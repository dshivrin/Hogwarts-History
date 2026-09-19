import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
from importlib import metadata
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable, Mapping, Sequence
import wave

import numpy as np
import yaml


class BlockKind(str, Enum):
    CHAPTER = "chapter"
    SECTION = "section"
    PARAGRAPH = "paragraph"


@dataclass(frozen=True)
class SpeechBlock:
    kind: BlockKind
    text: str


@dataclass(frozen=True)
class Pronunciation:
    term: str
    replacement: str
    reason: str


@dataclass(frozen=True)
class SpeechChunk:
    kind: BlockKind
    text: str
    ends_block: bool


@dataclass(frozen=True)
class RenderedChunk:
    kind: BlockKind
    audio: np.ndarray
    ends_block: bool


@dataclass(frozen=True)
class SampleSpec:
    voice: str
    speed: float


@dataclass(frozen=True)
class RuntimeEvidence:
    device: str
    gpu_selected: bool
    metal_telemetry: dict[str, object]
    audio_array_type: str


@dataclass(frozen=True)
class NarrationSnapshot:
    path: Path
    sha256: str
    blocks: tuple[SpeechBlock, ...]
    provenance_report: dict[str, object]
    warnings: tuple[str, ...]
    provenance_path: Path | None
    provenance: dict[str, object] | None


@dataclass(frozen=True)
class SynthesisBundle:
    chunks: tuple[SpeechChunk, ...]
    audio: np.ndarray
    sample_rate: int
    synthesis_evidence: dict[str, object]


APPROVED_VOICES = frozenset({"bm_daniel", "bm_george", "bf_alice", "bf_emma"})
DEFAULT_AUDIO_ROOT = Path(__file__).resolve().parents[1]


def load_pronunciations(path: Path) -> list[Pronunciation]:
    with path.open(encoding="utf-8") as guide:
        contents = yaml.safe_load(guide)

    if not isinstance(contents, dict):
        raise ValueError("Pronunciation guide must be a mapping")
    if type(contents.get("version")) is not int or contents["version"] != 1:
        raise ValueError("Pronunciation guide must have version 1")
    substitutions = contents.get("substitutions")
    if not isinstance(substitutions, list):
        raise ValueError("Pronunciation guide substitutions must be a list")

    entries: list[Pronunciation] = []
    terms: set[str] = set()
    for substitution in substitutions:
        if not isinstance(substitution, dict):
            raise ValueError("Each pronunciation substitution must be a mapping")
        fields = ("term", "replacement", "reason")
        if any(
            not isinstance(substitution.get(field), str)
            or not substitution[field].strip()
            for field in fields
        ):
            raise ValueError("Pronunciation substitutions require non-empty strings")
        term = substitution["term"]
        if term in terms:
            raise ValueError(f"Duplicate pronunciation term: {term}")
        terms.add(term)
        entries.append(
            Pronunciation(
                term=term,
                replacement=substitution["replacement"],
                reason=substitution["reason"],
            )
        )
    return entries


def apply_pronunciations(text: str, entries: Sequence[Pronunciation]) -> str:
    for entry in entries:
        text = re.sub(
            rf"(?<!\w){re.escape(entry.term)}(?!\w)",
            lambda _match, replacement=entry.replacement: replacement,
            text,
        )
    return text


def split_sentences(text: str) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []

    sentences: list[str] = []
    start = 0
    non_terminal_abbreviations = {
        "dr",
        "etc",
        "jr",
        "miss",
        "mr",
        "mrs",
        "ms",
        "no",
        "prof",
        "sr",
        "st",
        "vs",
    }
    for match in re.finditer(r"[.!?](?:[\"'\u201d\u2019]+)?", normalized):
        punctuation_index = match.start()
        if normalized[punctuation_index] == ".":
            previous_character = (
                normalized[punctuation_index - 1]
                if punctuation_index > 0
                else ""
            )
            next_character = (
                normalized[punctuation_index + 1]
                if punctuation_index + 1 < len(normalized)
                else ""
            )
            word_match = re.search(
                r"([A-Za-z]+)$", normalized[:punctuation_index]
            )
            preceding_word = word_match.group(1) if word_match else ""
            if (
                previous_character == "."
                or next_character == "."
                or (previous_character.isdigit() and next_character.isdigit())
                or preceding_word.lower() in non_terminal_abbreviations
                or (len(preceding_word) == 1 and bool(normalized[match.end() :].strip()))
            ):
                continue
        sentence = normalized[start : match.end()].strip()
        if sentence:
            sentences.append(sentence)
        start = match.end()
    tail = normalized[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def select_opening_sample_blocks(
    blocks: Sequence[SpeechBlock],
) -> list[SpeechBlock]:
    selected: list[SpeechBlock] = []
    prose_count = 0
    for block in blocks:
        if block.kind is BlockKind.PARAGRAPH:
            selected.append(block)
            prose_count += 1
            if prose_count == 2:
                break
        elif prose_count == 0:
            selected.append(block)
    if prose_count == 0:
        raise ValueError("Opening sample requires at least one prose paragraph")
    return selected


def remove_final_prose_sentence(
    blocks: Sequence[SpeechBlock],
) -> list[SpeechBlock] | None:
    selected = list(blocks)
    paragraph_index = next(
        (
            index
            for index in range(len(selected) - 1, -1, -1)
            if selected[index].kind is BlockKind.PARAGRAPH
        ),
        None,
    )
    if paragraph_index is None:
        return None
    sentences = split_sentences(selected[paragraph_index].text)
    prose_count = sum(
        block.kind is BlockKind.PARAGRAPH for block in selected
    )
    if len(sentences) == 1:
        if prose_count <= 1:
            return None
        del selected[paragraph_index]
        return selected
    selected[paragraph_index] = SpeechBlock(
        BlockKind.PARAGRAPH, " ".join(sentences[:-1])
    )
    return selected


def select_prose_paragraph(
    blocks: Sequence[SpeechBlock], paragraph_number: int
) -> list[SpeechBlock]:
    if type(paragraph_number) is not int or paragraph_number < 1:
        raise ValueError("prose paragraph number must be a positive integer")
    paragraphs = [
        block for block in blocks if block.kind is BlockKind.PARAGRAPH
    ]
    if paragraph_number > len(paragraphs):
        raise ValueError(
            f"prose paragraph {paragraph_number} does not exist; "
            f"narration contains {len(paragraphs)} prose paragraphs"
        )
    return [paragraphs[paragraph_number - 1]]


def chunk_blocks(
    blocks: Sequence[SpeechBlock], max_words: int
) -> list[SpeechChunk]:
    if max_words < 1:
        raise ValueError("max_words must be at least 1")

    chunks: list[SpeechChunk] = []
    for block in blocks:
        block_chunks: list[str] = []
        current_sentences: list[str] = []
        current_word_count = 0
        for sentence in split_sentences(block.text):
            sentence_word_count = len(sentence.split())
            if sentence_word_count > max_words:
                raise ValueError("A single sentence exceeds the word limit")
            if current_sentences and current_word_count + sentence_word_count > max_words:
                block_chunks.append(" ".join(current_sentences))
                current_sentences = []
                current_word_count = 0
            current_sentences.append(sentence)
            current_word_count += sentence_word_count
        if current_sentences:
            block_chunks.append(" ".join(current_sentences))
        chunks.extend(
            SpeechChunk(block.kind, text, index == len(block_chunks) - 1)
            for index, text in enumerate(block_chunks)
        )
    return chunks


def assemble_audio(
    chunks: Sequence[RenderedChunk], sample_rate: int, pauses: Mapping[str, int]
) -> np.ndarray:
    if not chunks:
        raise ValueError("At least one rendered chunk is required")
    if sample_rate < 1:
        raise ValueError("sample_rate must be positive")

    pause_keys = {
        "opening_ms",
        "continuation_ms",
        "paragraph_ms",
        "section_ms",
        "chapter_ms",
        "closing_ms",
    }
    if set(pauses) != pause_keys or any(
        type(pauses[key]) is not int or pauses[key] < 0 for key in pause_keys
    ):
        raise ValueError("pauses must contain non-negative integer millisecond values")

    def silence(milliseconds: int) -> np.ndarray:
        samples = round(sample_rate * milliseconds / 1000)
        return np.zeros(samples, dtype=np.float32)

    parts = [silence(pauses["opening_ms"])]
    ending_pause_keys = {
        BlockKind.PARAGRAPH: "paragraph_ms",
        BlockKind.SECTION: "section_ms",
        BlockKind.CHAPTER: "chapter_ms",
    }
    for chunk in chunks:
        try:
            audio = np.asarray(chunk.audio, dtype=np.float32)
            valid_audio = audio.ndim == 1 and audio.size > 0 and np.isfinite(audio).all()
        except (TypeError, ValueError):
            valid_audio = False
        if not valid_audio:
            raise ValueError("Rendered chunk audio must be a non-empty finite mono array")
        parts.append(audio)
        pause_key = (
            ending_pause_keys[chunk.kind]
            if chunk.ends_block
            else "continuation_ms"
        )
        parts.append(silence(pauses[pause_key]))
    parts.append(silence(pauses["closing_ms"]))
    return np.concatenate(parts)


def write_pcm16_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    if sample_rate < 1:
        raise ValueError("sample_rate must be positive")
    samples = np.asarray(audio, dtype=np.float32).reshape(-1)
    if samples.size == 0 or not np.isfinite(samples).all():
        raise ValueError("audio must be non-empty and finite")
    peak = float(np.max(np.abs(samples)))
    if peak > 0.95:
        samples = samples * (0.95 / peak)
    pcm = np.rint(samples * 32767).astype("<i2")
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(pcm.tobytes())


def inspect_wav(path: Path) -> dict[str, int | float | bool]:
    with wave.open(str(path), "rb") as input_file:
        channels = input_file.getnchannels()
        sample_width = input_file.getsampwidth()
        sample_rate = input_file.getframerate()
        sample_count = input_file.getnframes()
        frames = input_file.readframes(sample_count)
    if channels != 1 or sample_width != 2:
        raise ValueError("WAV must be one-channel 16-bit PCM")

    samples = np.frombuffer(frames, dtype="<i2")
    normalized = samples.astype(np.float32) / 32767
    non_silent = normalized != 0
    opening_silence = int(np.argmax(non_silent)) if non_silent.any() else len(samples)
    closing_silence = (
        int(np.argmax(non_silent[::-1])) if non_silent.any() else len(samples)
    )
    return {
        "sample_rate": sample_rate,
        "channels": channels,
        "sample_count": sample_count,
        "duration_seconds": sample_count / sample_rate,
        "peak": float(np.max(np.abs(normalized))) if sample_count else 0.0,
        "non_silent_samples": int(np.count_nonzero(non_silent)),
        "finite": bool(np.isfinite(normalized).all()),
        "opening_silence_samples": opening_silence,
        "closing_silence_samples": closing_silence,
    }


def encode_listening_copy(
    wav_path: Path, output_path: Path, ffmpeg: str = "ffmpeg"
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [ffmpeg, "-y", "-v", "error", "-i", str(wav_path), str(output_path)],
        check=True,
    )


def _loudnorm_measurement(output: str) -> dict[str, object]:
    for candidate in reversed(re.findall(r"\{[^{}]+\}", output, flags=re.DOTALL)):
        try:
            measurement = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(measurement, dict) and "input_i" in measurement:
            return measurement
    raise ValueError("ffmpeg loudnorm output did not contain a measurement")


def _run_loudnorm_command(command: list[str]) -> dict[str, object]:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return _loudnorm_measurement(result.stderr)


def normalize_spoken_word_mp3(
    wav_path: Path,
    output_path: Path,
    sample_rate: int,
    ffmpeg: str = "ffmpeg",
) -> dict[str, object]:
    """Create and measure a two-pass, mono spoken-word listening copy."""
    target_i = -19.0
    target_tp = -1.0
    target_lra = 7.0
    base_filter = f"loudnorm=I={target_i}:TP={target_tp}:LRA={target_lra}"
    analysis_command = [
        ffmpeg,
        "-hide_banner",
        "-nostats",
        "-i",
        str(wav_path),
        "-af",
        f"{base_filter}:print_format=json",
        "-f",
        "null",
        "-",
    ]
    analysis = _run_loudnorm_command(analysis_command)
    normalise_filter = (
        f"{base_filter}:measured_I={analysis['input_i']}"
        f":measured_TP={analysis['input_tp']}"
        f":measured_LRA={analysis['input_lra']}"
        f":measured_thresh={analysis['input_thresh']}"
        f":offset={analysis['target_offset']}:linear=true:print_format=json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    normalise_command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-nostats",
        "-i",
        str(wav_path),
        "-af",
        normalise_filter,
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "128k",
        str(output_path),
    ]
    normalised = _run_loudnorm_command(normalise_command)
    measurement_command = [
        ffmpeg,
        "-hide_banner",
        "-nostats",
        "-i",
        str(output_path),
        "-af",
        f"{base_filter}:print_format=json",
        "-f",
        "null",
        "-",
    ]
    measured_output = _run_loudnorm_command(measurement_command)
    return {
        "settings": {
            "integrated_lufs": target_i,
            "true_peak_dbtp": target_tp,
            "loudness_range_lu": target_lra,
            "channels": 1,
            "sample_rate": sample_rate,
            "codec": "libmp3lame",
            "bitrate": "128k",
        },
        "commands": {
            "analysis": analysis_command,
            "normalise": normalise_command,
            "measurement": measurement_command,
        },
        "measured_input": {
            "integrated_lufs": float(analysis["input_i"]),
            "true_peak_dbtp": float(analysis["input_tp"]),
            "loudness_range_lu": float(analysis["input_lra"]),
            "threshold_lufs": float(analysis["input_thresh"]),
        },
        "normalisation_output": {
            "integrated_lufs": float(normalised["output_i"]),
            "true_peak_dbtp": float(normalised["output_tp"]),
            "loudness_range_lu": float(normalised["output_lra"]),
            "threshold_lufs": float(normalised["output_thresh"]),
            "normalisation_type": normalised.get("normalization_type"),
            "target_offset_lu": float(normalised["target_offset"]),
        },
        "measured_output": {
            "integrated_lufs": float(measured_output["input_i"]),
            "true_peak_dbtp": float(measured_output["input_tp"]),
            "loudness_range_lu": float(measured_output["input_lra"]),
            "threshold_lufs": float(measured_output["input_thresh"]),
        },
    }


def strip_front_matter(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return text

    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == "---":
            return "".join(lines[index + 1 :])
    return text


def remove_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as input_file:
        for block in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def narration_provenance_path(narration_path: Path) -> Path:
    return narration_path.with_name(f"{narration_path.stem}-provenance.yaml")


def _portable_project_path(path: Path) -> str:
    resolved = path.resolve()
    repository_root = DEFAULT_AUDIO_ROOT.parents[1].resolve()
    try:
        return resolved.relative_to(repository_root).as_posix()
    except ValueError:
        return str(resolved)


def prepare_narration(
    source_path: Path,
    narration_path: Path,
    *,
    prepared_at: str | None = None,
) -> Path:
    provenance_path = narration_provenance_path(narration_path)
    if narration_path.exists():
        raise FileExistsError(f"Refusing to overwrite narration manuscript: {narration_path}")
    if provenance_path.exists():
        raise FileExistsError(f"Refusing to overwrite narration provenance: {provenance_path}")

    source_bytes = source_path.read_bytes()
    source_text = source_bytes.decode("utf-8")
    prepared = remove_html_comments(strip_front_matter(source_text))
    prepared = re.sub(r"\n{3,}", "\n\n", prepared).strip() + "\n"
    narration_hash = hashlib.sha256(prepared.encode("utf-8")).hexdigest()
    narration_path.parent.mkdir(parents=True, exist_ok=True)
    provenance = {
        "schema_version": 1,
        "prepared_at": prepared_at or datetime.now(timezone.utc).isoformat(),
        "preparation_tool": _portable_project_path(Path(__file__)),
        "source_manuscript": {
            "path": _portable_project_path(source_path),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
        },
        "narration": {
            "path": _portable_project_path(narration_path),
            "prepared_sha256": narration_hash,
            "current_sha256": narration_hash,
        },
    }
    with narration_path.open("x", encoding="utf-8") as narration_file:
        narration_file.write(prepared)
    with provenance_path.open("x", encoding="utf-8") as provenance_file:
        yaml.safe_dump(
            provenance,
            provenance_file,
            sort_keys=False,
            allow_unicode=True,
        )
    return provenance_path


def _resolve_project_path(path: str) -> Path:
    value = Path(path)
    if value.is_absolute():
        return value
    return DEFAULT_AUDIO_ROOT.parents[1] / value


def inspect_narration_provenance(
    narration_path: Path,
    current_narration_hash: str | None = None,
) -> tuple[dict[str, object], list[str], Path | None, dict[str, object] | None]:
    if current_narration_hash is None:
        current_narration_hash = sha256_path(narration_path)
    provenance_path = narration_provenance_path(narration_path)
    if not provenance_path.exists():
        return (
            {
                "narration": {
                    "path": _portable_project_path(narration_path),
                    "prepared_sha256": None,
                    "current_sha256": current_narration_hash,
                }
            },
            [],
            None,
            None,
        )

    provenance = yaml.safe_load(provenance_path.read_text(encoding="utf-8"))
    if not isinstance(provenance, dict):
        raise ValueError("Narration provenance must be a mapping")
    source = provenance.get("source_manuscript")
    narration = provenance.get("narration")
    if not isinstance(source, dict) or not isinstance(narration, dict):
        raise ValueError("Narration provenance requires source_manuscript and narration mappings")
    if not isinstance(source.get("path"), str) or not isinstance(source.get("sha256"), str):
        raise ValueError("Narration provenance source manuscript is incomplete")
    if not isinstance(narration.get("prepared_sha256"), str):
        raise ValueError("Narration provenance prepared hash is missing")

    source_path = _resolve_project_path(source["path"])
    warnings: list[str] = []
    current_source_hash: str | None = None
    if source_path.exists():
        current_source_hash = sha256_path(source_path)
        source_status = (
            "current" if current_source_hash == source["sha256"] else "drifted"
        )
    else:
        source_status = "missing"
    if source_status == "drifted":
        warnings.append(
            "Source manuscript has changed since this narration manuscript was prepared: "
            f"{source['path']}"
        )
    elif source_status == "missing":
        warnings.append(
            "Source manuscript recorded by narration provenance is missing: "
            f"{source['path']}"
        )

    report = {
        "source_manuscript": {
            "path": source["path"],
            "sha256": source["sha256"],
            "current_sha256": current_source_hash,
            "status": source_status,
        },
        "narration": {
            "path": _portable_project_path(narration_path),
            "prepared_sha256": narration["prepared_sha256"],
            "current_sha256": current_narration_hash,
        },
    }
    return report, warnings, provenance_path, provenance


def read_narration_snapshot(markdown_path: Path) -> NarrationSnapshot:
    narration_bytes = markdown_path.read_bytes()
    narration_hash = hashlib.sha256(narration_bytes).hexdigest()
    report, warnings, provenance_path, provenance = inspect_narration_provenance(
        markdown_path, narration_hash
    )
    return NarrationSnapshot(
        markdown_path,
        narration_hash,
        tuple(markdown_to_blocks(narration_bytes.decode("utf-8"))),
        report,
        tuple(warnings),
        provenance_path,
        provenance,
    )


def strip_inline_markdown(text: str) -> str:
    code_spans: list[str] = []
    sentinel = "\0"
    while sentinel in text:
        sentinel += "\0"

    def protect_code_span(match: re.Match[str]) -> str:
        code_spans.append(match.group("content"))
        return f"{sentinel}{len(code_spans) - 1}{sentinel}"

    text = re.sub(
        r"(?P<delimiter>`+)(?P<content>.+?)(?P=delimiter)",
        protect_code_span,
        text,
    )
    text = re.sub(r"!\[([^]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    text = text.replace("`", "")
    text = re.sub(r"(?<!\w)\*\*(?=\S)(.+?)(?<=\S)\*\*(?!\w)", r"\1", text)
    text = re.sub(r"(?<!\w)__(?=\S)(.+?)(?<=\S)__(?!\w)", r"\1", text)
    text = re.sub(
        r"(?<![\w_])([*_])(?!_)(?=\S)(.+?)(?<=\S)\1(?![\w_])",
        r"\2",
        text,
    )
    for index, code_span in enumerate(code_spans):
        text = text.replace(f"{sentinel}{index}{sentinel}", code_span)
    return " ".join(text.split())


def markdown_to_blocks(markdown: str) -> list[SpeechBlock]:
    blocks: list[SpeechBlock] = []
    prose_lines: list[str] = []

    def flush_prose() -> None:
        if prose_lines:
            text = strip_inline_markdown("\n".join(prose_lines))
            if text:
                blocks.append(SpeechBlock(BlockKind.PARAGRAPH, text))
            prose_lines.clear()

    prepared = remove_html_comments(strip_front_matter(markdown))
    for line in prepared.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush_prose()
            kind = BlockKind.CHAPTER if len(heading.group(1)) == 1 else BlockKind.SECTION
            heading_text = re.sub(r"\s+#+\s*$", "", heading.group(2))
            text = strip_inline_markdown(heading_text)
            if text:
                blocks.append(SpeechBlock(kind, text))
        elif not line.strip():
            flush_prose()
        else:
            prose_lines.append(line.strip())
    flush_prose()
    return blocks


def extract_prose_excerpt(
    markdown: str, min_words: int = 400, max_words: int = 500
) -> str:
    selected: list[str] = []
    word_count = 0

    for block in markdown_to_blocks(markdown):
        if block.kind is not BlockKind.PARAGRAPH:
            continue
        paragraph_words = len(block.text.split())
        if word_count + paragraph_words > max_words:
            if word_count >= min_words:
                break
            raise ValueError("Cannot collect the minimum excerpt length within the maximum")
        selected.append(block.text)
        word_count += paragraph_words
        if word_count >= min_words:
            break

    if word_count < min_words:
        raise ValueError("Cannot collect the minimum excerpt length")
    return "\n\n".join(selected)


def validate_settings(settings: Mapping[str, object]) -> None:
    if settings.get("engine") != "kokoro":
        raise ValueError("engine must be kokoro")
    if settings.get("model") != "mlx-community/Kokoro-82M-bf16":
        raise ValueError("model must be mlx-community/Kokoro-82M-bf16")
    if settings.get("language") != "british-english" or settings.get("lang_code") != "b":
        raise ValueError("language must be british-english with lang_code b")
    validate_render_spec(settings.get("voice"), settings.get("speed"))
    chunking = settings.get("chunking")
    if not isinstance(chunking, Mapping) or type(chunking.get("max_words")) is not int or chunking["max_words"] < 1:
        raise ValueError("chunking.max_words must be a positive integer")
    pauses = settings.get("pauses")
    if not isinstance(pauses, Mapping):
        raise ValueError("pauses must be a mapping")
    # Keep the validation shared with assembly, but fail before model loading.
    assemble_audio([RenderedChunk(BlockKind.PARAGRAPH, np.array([0.0]), True)], 1, pauses)


def validate_render_spec(voice: object, speed: object) -> SampleSpec:
    if not isinstance(voice, str) or not voice.strip():
        raise ValueError("render voice must be a non-empty Kokoro voice identifier")
    if (
        not isinstance(speed, (int, float))
        or isinstance(speed, bool)
        or not 0.90 <= float(speed) <= 1.05
    ):
        raise ValueError("render speed must be between 0.90 and 1.05")
    return SampleSpec(voice.strip(), float(speed))


def resolve_render_spec(
    settings: Mapping[str, object],
    voice: str | None,
    speed: float | None,
) -> SampleSpec:
    return validate_render_spec(
        voice if voice is not None else settings.get("voice"),
        speed if speed is not None else settings.get("speed"),
    )


def _validate_sample_specs(sample_specs: Sequence[SampleSpec]) -> None:
    if not sample_specs:
        raise ValueError("At least one audition sample is required")
    seen: set[tuple[str, float]] = set()
    filenames: set[str] = set()
    for sample in sample_specs:
        if sample.voice not in APPROVED_VOICES:
            raise ValueError(f"Unsupported British voice: {sample.voice}")
        if not isinstance(sample.speed, (int, float)) or isinstance(sample.speed, bool) or not 0.9 <= sample.speed <= 1.05:
            raise ValueError("sample speed must be between 0.90 and 1.05")
        request = (sample.voice, float(sample.speed))
        if request in seen:
            raise ValueError("Duplicate audition voice and speed request")
        seen.add(request)
        filename = _sample_filename(sample)
        if filename in filenames:
            raise ValueError("Duplicate audition output filename")
        filenames.add(filename)


def _module_qualified_type(value: object) -> str:
    value_type = type(value)
    return f"{value_type.__module__}.{value_type.__qualname__}"


def collect_runtime_evidence() -> RuntimeEvidence:
    """Read MLX device/Metal facts without making MLX a module import dependency."""
    try:
        import mlx.core as mx
    except ImportError:
        return RuntimeEvidence("unavailable", False, {}, "unavailable")

    device = mx.default_device()
    try:
        gpu_selected = device == mx.gpu
    except Exception:
        gpu_selected = "gpu" in str(device).lower()
    telemetry: dict[str, object] = {}
    metal = getattr(mx, "metal", None)
    for name in ("device_info", "get_active_memory", "get_cache_memory", "get_peak_memory"):
        operation = getattr(metal, name, None)
        if callable(operation):
            try:
                telemetry[name.removeprefix("get_")] = operation()
            except Exception:
                pass
    return RuntimeEvidence(str(device), bool(gpu_selected), telemetry, "unavailable")


def _revision_from_path(path: object) -> str | None:
    if not isinstance(path, (str, Path)):
        return None
    match = re.search(r"(?:^|[\\/])snapshots[\\/]([^\\/]+)", str(path))
    return match.group(1) if match else None


def resolve_model_revision(model: object, model_id: str) -> str | None:
    for owner in (getattr(model, "config", None), model):
        if owner is not None:
            revision = _revision_from_path(getattr(owner, "model_path", None))
            if revision:
                return revision
    try:
        from huggingface_hub import HfApi, scan_cache_dir
    except Exception:
        return None

    try:
        cache = scan_cache_dir()
        for repository in cache.repos:
            if repository.repo_id == model_id:
                revisions = list(repository.revisions)
                if revisions:
                    return revisions[0].commit_hash
    except Exception:
        pass
    try:
        # This is intentionally best effort: an offline model can still render.
        revision = HfApi().model_info(model_id).sha
        return revision if isinstance(revision, str) else None
    except Exception:
        return None


def _generation_results(generated: object) -> list[object]:
    if hasattr(generated, "audio"):
        return [generated]
    try:
        return list(generated)  # type: ignore[arg-type]
    except TypeError as error:
        raise ValueError("model.generate() returned no audio result") from error


def synthesize_chunks(
    model: object,
    chunks: Sequence[SpeechChunk],
    voice: str,
    speed: float,
    lang_code: str,
) -> tuple[list[RenderedChunk], int, dict[str, str]]:
    rendered: list[RenderedChunk] = []
    sample_rate: int | None = None
    array_types: set[str] = set()
    for chunk in chunks:
        generated = model.generate(text=chunk.text, voice=voice, speed=speed, lang_code=lang_code)  # type: ignore[attr-defined]
        results = _generation_results(generated)
        if not results:
            raise ValueError("model.generate() returned no audio result")
        arrays: list[np.ndarray] = []
        for result in results:
            audio = getattr(result, "audio", None)
            result_rate = getattr(result, "sample_rate", None)
            if type(result_rate) is not int or result_rate < 1:
                raise ValueError("generated audio requires a positive sample_rate")
            if sample_rate is None:
                sample_rate = result_rate
            elif sample_rate != result_rate:
                raise ValueError("generated chunks must use one sample rate")
            array_types.add(_module_qualified_type(audio))
            evaluate = getattr(audio, "eval", None)
            if callable(evaluate):
                audio = evaluate()
            array = np.asarray(audio, dtype=np.float32).reshape(-1)
            if not array.size or not np.isfinite(array).all():
                raise ValueError("generated audio must be non-empty and finite")
            arrays.append(array)
        rendered.append(RenderedChunk(chunk.kind, np.concatenate(arrays), chunk.ends_block))
    if sample_rate is None:
        raise ValueError("At least one speech chunk is required")
    return rendered, sample_rate, {"audio_array_type": ",".join(sorted(array_types))}


def _default_model_loader(model_id: str) -> object:
    from mlx_audio.tts.utils import load_model

    return load_model(model_id)


def _package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def _sample_filename(sample: SampleSpec) -> str:
    return f"{sample.voice.replace('_', '-')}-{round(sample.speed * 100):03d}.wav"


def _manifest_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(DEFAULT_AUDIO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _normalize_manifest_path(path: object) -> str | None:
    if not isinstance(path, str):
        return None
    value = Path(path)
    if value.is_absolute():
        return _manifest_path(value)
    return _manifest_path(DEFAULT_AUDIO_ROOT / value)


def _load_compatible_manifest(
    manifest_path: Path, model: str, fixture_path: Path, fixture_hash: str
) -> list[dict[str, object]]:
    if not manifest_path.exists():
        return []
    content = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(content, Mapping):
        raise ValueError("Existing manifest must be a mapping")
    if (
        content.get("model") != model
        or _normalize_manifest_path(content.get("fixture_path"))
        != _manifest_path(fixture_path)
        or content.get("fixture_sha256") != fixture_hash
    ):
        raise ValueError("Existing manifest is incompatible with this audition")
    records = content.get("samples")
    if not isinstance(records, list) or not all(isinstance(record, dict) and isinstance(record.get("path"), str) for record in records):
        raise ValueError("Existing manifest samples are invalid")
    return [dict(record) for record in records]


def run_audition(
    fixture_path: Path,
    sample_specs: Sequence[SampleSpec],
    settings: Mapping[str, object],
    pronunciation_path: Path,
    output_dir: Path,
    manifest_path: Path,
    model_loader: Callable[[str], object] | None = None,
    evidence_provider: Callable[[], RuntimeEvidence] | None = None,
) -> list[dict[str, object]]:
    validate_settings(settings)
    _validate_sample_specs(sample_specs)
    fixture_path = fixture_path.resolve()
    fixture_bytes = fixture_path.read_bytes()
    fixture_hash = hashlib.sha256(fixture_bytes).hexdigest()
    pronunciations = load_pronunciations(pronunciation_path)
    blocks = [SpeechBlock(BlockKind.PARAGRAPH, paragraph) for paragraph in fixture_bytes.decode("utf-8").split("\n\n") if paragraph.strip()]
    prepared = [SpeechBlock(block.kind, apply_pronunciations(block.text, pronunciations)) for block in blocks]
    chunks = chunk_blocks(prepared, settings["chunking"]["max_words"])  # type: ignore[index]
    model_id = str(settings["model"])
    existing = _load_compatible_manifest(manifest_path, model_id, fixture_path, fixture_hash)
    loader = model_loader or _default_model_loader
    model = loader(model_id)
    revision = resolve_model_revision(model, model_id)
    synthesized: list[tuple[SampleSpec, list[RenderedChunk], int]] = []
    source_array_types: set[str] = set()
    for sample in sample_specs:
        rendered, sample_rate, synthesis_evidence = synthesize_chunks(model, chunks, sample.voice, float(sample.speed), str(settings["lang_code"]))
        source_array_types.update(synthesis_evidence["audio_array_type"].split(","))
        synthesized.append((sample, rendered, sample_rate))
    source_array_type = ",".join(sorted(source_array_types))
    runtime = (evidence_provider or collect_runtime_evidence)()
    runtime = RuntimeEvidence(runtime.device, runtime.gpu_selected, runtime.metal_telemetry, source_array_type)
    if not runtime.gpu_selected:
        raise RuntimeError("MLX default device must select a GPU")
    if not all(array_type.startswith("mlx.") for array_type in source_array_types):
        raise RuntimeError("MLX-generated audio is required for a successful audition")

    output_dir.mkdir(parents=True, exist_ok=True)
    generated_records: list[dict[str, object]] = []
    for sample, rendered, sample_rate in synthesized:
        output_path = (output_dir / _sample_filename(sample)).resolve()
        audio = assemble_audio(rendered, sample_rate, settings["pauses"])  # type: ignore[arg-type]
        write_pcm16_wav(output_path, audio, sample_rate)
        facts = inspect_wav(output_path)
        generated_records.append({
            "fixture_path": _manifest_path(fixture_path), "fixture_sha256": fixture_hash,
            "python_version": sys.version.split()[0], "mlx_audio_version": _package_version("mlx-audio"),
            "misaki_version": _package_version("misaki"), "model": model_id,
            "model_revision": revision, "voice": sample.voice, "lang_code": settings["lang_code"],
            "speed": float(sample.speed), "path": _manifest_path(output_path), "audio": facts,
            "file_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
        })
    for record in generated_records:
        record["runtime_evidence"] = asdict(runtime)
    replacements = {record["path"]: record for record in generated_records}
    records = [replacements.pop(record["path"], record) for record in existing]
    records.extend(replacements.values())
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "fixture_path": _manifest_path(fixture_path),
                "fixture_sha256": fixture_hash,
                "python_version": sys.version.split()[0],
                "mlx_audio_version": _package_version("mlx-audio"),
                "misaki_version": _package_version("misaki"),
                "model": model_id,
                "model_revision": revision,
                "samples": records,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return records


def run_george_calibration(
    fixture_path: Path,
    settings: Mapping[str, object],
    pronunciation_path: Path,
    output_dir: Path,
    manifest_path: Path,
    ffmpeg: str = "ffmpeg",
    model_loader: Callable[[str], object] | None = None,
    evidence_provider: Callable[[], RuntimeEvidence] | None = None,
    listening_copy_encoder: Callable[
        [Path, Path, int, str], dict[str, object]
    ] = normalize_spoken_word_mp3,
) -> list[dict[str, object]]:
    validate_settings(settings)
    fixture_path = fixture_path.resolve()
    fixture_bytes = fixture_path.read_bytes()
    fixture_hash = hashlib.sha256(fixture_bytes).hexdigest()
    pronunciations = load_pronunciations(pronunciation_path)
    blocks = [
        SpeechBlock(BlockKind.PARAGRAPH, paragraph)
        for paragraph in fixture_bytes.decode("utf-8").split("\n\n")
        if paragraph.strip()
    ]
    prepared = [
        SpeechBlock(block.kind, apply_pronunciations(block.text, pronunciations))
        for block in blocks
    ]
    chunks = chunk_blocks(prepared, settings["chunking"]["max_words"])  # type: ignore[index]

    configured_pauses = settings["pauses"]
    current_paragraph_pause = configured_pauses["paragraph_ms"]  # type: ignore[index]
    if type(current_paragraph_pause) is not int or current_paragraph_pause < 125:
        raise ValueError("pauses.paragraph_ms must be at least 125 for calibration")
    variants = (
        ("A", 0.96, current_paragraph_pause, "bm-george-calibration-a-096"),
        ("B", 0.98, current_paragraph_pause, "bm-george-calibration-b-098"),
        (
            "C",
            0.96,
            current_paragraph_pause - 125,
            "bm-george-calibration-c-096-shorter-pauses",
        ),
    )

    model_id = str(settings["model"])
    model = (model_loader or _default_model_loader)(model_id)
    revision = resolve_model_revision(model, model_id)
    rendered_by_speed: dict[float, tuple[list[RenderedChunk], int]] = {}
    source_array_types: set[str] = set()
    for speed in (0.96, 0.98):
        rendered, sample_rate, synthesis_evidence = synthesize_chunks(
            model, chunks, "bm_george", speed, str(settings["lang_code"])
        )
        rendered_by_speed[speed] = (rendered, sample_rate)
        source_array_types.update(synthesis_evidence["audio_array_type"].split(","))

    source_array_type = ",".join(sorted(source_array_types))
    runtime = (evidence_provider or collect_runtime_evidence)()
    runtime = RuntimeEvidence(
        runtime.device,
        runtime.gpu_selected,
        runtime.metal_telemetry,
        source_array_type,
    )
    if not runtime.gpu_selected:
        raise RuntimeError("MLX default device must select a GPU")
    if not all(array_type.startswith("mlx.") for array_type in source_array_types):
        raise RuntimeError("MLX-generated audio is required for a successful calibration")

    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for variant, speed, paragraph_pause, basename in variants:
        rendered, sample_rate = rendered_by_speed[speed]
        pauses = dict(configured_pauses)  # type: ignore[arg-type]
        pauses["paragraph_ms"] = paragraph_pause
        wav_path = (output_dir / f"{basename}.wav").resolve()
        mp3_path = (output_dir / f"{basename}.mp3").resolve()
        write_pcm16_wav(
            wav_path,
            assemble_audio(rendered, sample_rate, pauses),
            sample_rate,
        )
        wav_hash = hashlib.sha256(wav_path.read_bytes()).hexdigest()
        audio = inspect_wav(wav_path)
        loudness = listening_copy_encoder(wav_path, mp3_path, sample_rate, ffmpeg)
        if hashlib.sha256(wav_path.read_bytes()).hexdigest() != wav_hash:
            raise RuntimeError("Listening-copy processing altered the raw WAV")
        records.append(
            {
                "variant": variant,
                "fixture_path": _manifest_path(fixture_path),
                "fixture_sha256": fixture_hash,
                "model": model_id,
                "model_revision": revision,
                "voice": "bm_george",
                "language": settings["language"],
                "lang_code": settings["lang_code"],
                "speed": speed,
                "paragraph_pause_ms": paragraph_pause,
                "wav_path": _manifest_path(wav_path),
                "wav_sha256": wav_hash,
                "mp3_path": _manifest_path(mp3_path),
                "mp3_sha256": hashlib.sha256(mp3_path.read_bytes()).hexdigest(),
                "duration_seconds": audio["duration_seconds"],
                "sample_rate": audio["sample_rate"],
                "audio": audio,
                "raw_wav_unnormalised": True,
                "loudness_normalisation": loudness,
                "runtime_evidence": asdict(runtime),
            }
        )

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "fixture_path": _manifest_path(fixture_path),
                "fixture_sha256": fixture_hash,
                "python_version": sys.version.split()[0],
                "mlx_audio_version": _package_version("mlx-audio"),
                "misaki_version": _package_version("misaki"),
                "model": model_id,
                "model_revision": revision,
                "model_load_count": 1,
                "human_selection": "pending",
                "variants": records,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return records


def synthesize_blocks(
    blocks: Sequence[SpeechBlock],
    pronunciations: Sequence[Pronunciation],
    settings: Mapping[str, object],
    model: object,
    voice: str,
    speed: float,
) -> SynthesisBundle:
    spoken_blocks = [
        SpeechBlock(block.kind, apply_pronunciations(block.text, pronunciations))
        for block in blocks
    ]
    chunks = chunk_blocks(
        spoken_blocks, settings["chunking"]["max_words"]  # type: ignore[index]
    )
    rendered, sample_rate, evidence = synthesize_chunks(
        model, chunks, voice, speed, str(settings["lang_code"])
    )
    audio = assemble_audio(
        rendered, sample_rate, settings["pauses"]  # type: ignore[arg-type]
    )
    return SynthesisBundle(tuple(chunks), audio, sample_rate, evidence)


def write_render_result(
    snapshot: NarrationSnapshot,
    bundle: SynthesisBundle,
    output_path: Path,
    voice: str,
    speed: float,
    settings: Mapping[str, object],
    model: object,
    listening_copy: Path | None,
    manifest_path: Path | None,
    chunk_manifest_path: Path | None,
    evidence_provider: Callable[[], RuntimeEvidence],
    *,
    render_kind: str,
    selection: Mapping[str, object] | None = None,
) -> Path:
    if render_kind not in {"full", "opening_sample", "paragraph_sample"}:
        raise ValueError(f"Unknown render kind: {render_kind}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_pcm16_wav(output_path, bundle.audio, bundle.sample_rate)
    if listening_copy is not None:
        encode_listening_copy(output_path, listening_copy)

    chunk_records = [
        {
            "index": index,
            "kind": chunk.kind.value,
            "ends_block": chunk.ends_block,
            "word_count": len(chunk.text.split()),
            "text": chunk.text,
        }
        for index, chunk in enumerate(bundle.chunks, start=1)
    ]
    if chunk_manifest_path is not None:
        chunk_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        chunk_manifest_path.write_text(
            yaml.safe_dump(
                {
                    "narration": snapshot.provenance_report["narration"],
                    "chunk_count": len(chunk_records),
                    "chunks": chunk_records,
                },
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )

    runtime_evidence = asdict(evidence_provider())
    runtime_evidence["audio_array_type"] = bundle.synthesis_evidence[
        "audio_array_type"
    ]
    if manifest_path is not None:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        outputs: dict[str, object] = {
            "wav": {
                "path": _portable_project_path(output_path),
                "sha256": sha256_path(output_path),
                "audio": inspect_wav(output_path),
            }
        }
        if listening_copy is not None:
            outputs["mp3"] = {
                "path": _portable_project_path(listening_copy),
                "sha256": sha256_path(listening_copy),
            }
        manifest: dict[str, object] = {
            "schema_version": 1,
            "status": "rendered",
            "render_kind": render_kind,
            **snapshot.provenance_report,
            "warnings": list(snapshot.warnings),
            "configuration": {
                "engine": settings["engine"],
                "model": settings["model"],
                "model_revision": resolve_model_revision(
                    model, str(settings["model"])
                ),
                "voice": voice,
                "language": settings["language"],
                "lang_code": settings["lang_code"],
                "speed": speed,
                "chunking": dict(settings["chunking"]),  # type: ignore[arg-type]
                "pauses": dict(settings["pauses"]),  # type: ignore[arg-type]
            },
            "runtime_evidence": runtime_evidence,
            "chunks": {
                "count": len(chunk_records),
                "manifest": (
                    _portable_project_path(chunk_manifest_path)
                    if chunk_manifest_path is not None
                    else None
                ),
                "submitted_text": chunk_records,
            },
            "outputs": outputs,
        }
        if selection is not None:
            manifest["sample_selection"] = dict(selection)
        manifest_path.write_text(
            yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    if snapshot.provenance_path is not None and snapshot.provenance is not None:
        narration = snapshot.provenance["narration"]
        if not isinstance(narration, dict):
            raise ValueError("Narration provenance narration mapping is invalid")
        narration["current_sha256"] = snapshot.sha256
        snapshot.provenance_path.write_text(
            yaml.safe_dump(
                snapshot.provenance, sort_keys=False, allow_unicode=True
            ),
            encoding="utf-8",
        )
    return output_path


def run_render(
    markdown_path: Path, output_path: Path, voice: str, speed: float,
    settings: Mapping[str, object], pronunciation_path: Path, listening_copy: Path | None = None,
    *,
    manifest_path: Path | None = None,
    chunk_manifest_path: Path | None = None,
    model_loader: Callable[[str], object] | None = None,
    evidence_provider: Callable[[], RuntimeEvidence] | None = None,
) -> Path:
    validate_settings(settings)
    render_spec = validate_render_spec(voice, speed)
    snapshot = read_narration_snapshot(markdown_path)
    if not snapshot.blocks:
        raise ValueError("Narration manuscript contains no spoken content")
    for warning in snapshot.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    pronunciations = load_pronunciations(pronunciation_path)
    model = (model_loader or _default_model_loader)(str(settings["model"]))
    bundle = synthesize_blocks(
        snapshot.blocks,
        pronunciations,
        settings,
        model,
        render_spec.voice,
        render_spec.speed,
    )
    return write_render_result(
        snapshot,
        bundle,
        output_path,
        render_spec.voice,
        render_spec.speed,
        settings,
        model,
        listening_copy,
        manifest_path,
        chunk_manifest_path,
        evidence_provider or collect_runtime_evidence,
        render_kind="full",
    )


def run_sample(
    markdown_path: Path,
    output_path: Path,
    voice: str,
    speed: float,
    settings: Mapping[str, object],
    pronunciation_path: Path,
    listening_copy: Path | None = None,
    *,
    paragraph: int | None = None,
    max_duration_seconds: float = 30.0,
    manifest_path: Path | None = None,
    chunk_manifest_path: Path | None = None,
    model_loader: Callable[[str], object] | None = None,
    evidence_provider: Callable[[], RuntimeEvidence] | None = None,
) -> Path:
    validate_settings(settings)
    render_spec = validate_render_spec(voice, speed)
    if not np.isfinite(max_duration_seconds) or max_duration_seconds <= 0:
        raise ValueError("max sample duration must be positive and finite")

    snapshot = read_narration_snapshot(markdown_path)
    if paragraph is None:
        selected = select_opening_sample_blocks(snapshot.blocks)
    else:
        selected = select_prose_paragraph(snapshot.blocks, paragraph)

    for warning in snapshot.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    pronunciations = load_pronunciations(pronunciation_path)
    model = (model_loader or _default_model_loader)(str(settings["model"]))

    if paragraph is not None:
        bundle = synthesize_blocks(
            selected,
            pronunciations,
            settings,
            model,
            render_spec.voice,
            render_spec.speed,
        )
        duration = len(bundle.audio) / bundle.sample_rate
        render_kind = "paragraph_sample"
        selection: dict[str, object] = {
            "paragraph_number": paragraph,
            "duration_seconds": duration,
        }
    else:
        while True:
            bundle = synthesize_blocks(
                selected,
                pronunciations,
                settings,
                model,
                render_spec.voice,
                render_spec.speed,
            )
            duration = len(bundle.audio) / bundle.sample_rate
            if duration <= max_duration_seconds:
                break
            reduced = remove_final_prose_sentence(selected)
            if reduced is None:
                raise ValueError(
                    "Opening headings and shortest prose sentence exceed "
                    f"{max_duration_seconds:g} seconds"
                )
            selected = reduced
        render_kind = "opening_sample"
        selection = {
            "selected_sentences": [
                sentence
                for block in selected
                if block.kind is BlockKind.PARAGRAPH
                for sentence in split_sentences(block.text)
            ],
            "duration_seconds": duration,
        }

    return write_render_result(
        snapshot,
        bundle,
        output_path,
        render_spec.voice,
        render_spec.speed,
        settings,
        model,
        listening_copy,
        manifest_path,
        chunk_manifest_path,
        evidence_provider or collect_runtime_evidence,
        render_kind=render_kind,
        selection=selection,
    )


def _read_settings(path: Path) -> Mapping[str, object]:
    settings = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(settings, Mapping):
        raise ValueError("settings must be a mapping")
    return settings


def _parse_sample(value: str) -> SampleSpec:
    voice, separator, speed = value.partition("=")
    if not separator:
        raise argparse.ArgumentTypeError("sample must use VOICE=SPEED")
    try:
        return SampleSpec(voice, float(speed))
    except ValueError as error:
        raise argparse.ArgumentTypeError("sample speed must be numeric") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render local Kokoro narration")
    parser.add_argument("--settings", type=Path, default=DEFAULT_AUDIO_ROOT / "narration-settings.yaml")
    parser.add_argument("--pronunciations", type=Path, default=DEFAULT_AUDIO_ROOT / "pronunciation-guide.yaml")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("source", type=Path)
    prepare.add_argument("--output", type=Path, required=True)
    audition = commands.add_parser("audition")
    audition.add_argument("--fixture", type=Path, default=DEFAULT_AUDIO_ROOT / "fixtures/audition-excerpt.txt")
    audition.add_argument("--sample", type=_parse_sample, action="append", required=True)
    audition.add_argument("--output-dir", type=Path, default=DEFAULT_AUDIO_ROOT / "samples")
    audition.add_argument("--manifest", type=Path, default=DEFAULT_AUDIO_ROOT / "samples/audition-manifest.yaml")
    calibration = commands.add_parser("george-calibration")
    calibration.add_argument(
        "--fixture",
        type=Path,
        default=DEFAULT_AUDIO_ROOT / "fixtures/george-calibration-excerpt.txt",
    )
    calibration.add_argument(
        "--output-dir", type=Path, default=DEFAULT_AUDIO_ROOT / "samples"
    )
    calibration.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_AUDIO_ROOT / "samples/george-calibration-manifest.yaml",
    )
    calibration.add_argument("--ffmpeg", default="ffmpeg")
    render = commands.add_parser("render")
    render.add_argument("markdown", type=Path)
    render.add_argument("--output", type=Path, required=True)
    render.add_argument("--voice")
    render.add_argument("--speed", type=float)
    render.add_argument("--listening-copy", type=Path)
    render.add_argument("--manifest", type=Path)
    render.add_argument("--chunk-manifest", type=Path)
    sample = commands.add_parser("sample")
    sample.add_argument("markdown", type=Path)
    sample.add_argument("--output", type=Path, required=True)
    sample.add_argument("--voice")
    sample.add_argument("--speed", type=float)
    sample.add_argument("--paragraph", type=int)
    sample.add_argument("--listening-copy", type=Path)
    sample.add_argument("--manifest", type=Path)
    sample.add_argument("--chunk-manifest", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            provenance = prepare_narration(args.source, args.output)
            print(args.output)
            print(provenance)
            return 0
        settings = _read_settings(args.settings)
        if args.command == "audition":
            records = run_audition(args.fixture, args.sample, settings, args.pronunciations, args.output_dir, args.manifest)
            for record in records:
                print(f"{record['path']} ({record['audio']['duration_seconds']:.2f}s)")
        elif args.command == "george-calibration":
            records = run_george_calibration(
                args.fixture,
                settings,
                args.pronunciations,
                args.output_dir,
                args.manifest,
                args.ffmpeg,
            )
            for record in records:
                print(f"{record['wav_path']} ({record['duration_seconds']:.2f}s)")
        elif args.command == "sample":
            render_spec = resolve_render_spec(settings, args.voice, args.speed)
            output = run_sample(
                args.markdown,
                args.output,
                render_spec.voice,
                render_spec.speed,
                settings,
                args.pronunciations,
                args.listening_copy,
                paragraph=args.paragraph,
                manifest_path=args.manifest,
                chunk_manifest_path=args.chunk_manifest,
            )
            print(output)
        else:
            render_spec = resolve_render_spec(settings, args.voice, args.speed)
            output = run_render(
                args.markdown,
                args.output,
                render_spec.voice,
                render_spec.speed,
                settings,
                args.pronunciations,
                args.listening_copy,
                manifest_path=args.manifest,
                chunk_manifest_path=args.chunk_manifest,
            )
            print(output)
    except Exception as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
