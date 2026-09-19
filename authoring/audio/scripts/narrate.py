import argparse
from dataclasses import asdict, dataclass
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
    for match in re.finditer(r"[.!?](?:[\"'\u201d\u2019]+)?", normalized):
        sentence = normalized[start : match.end()].strip()
        if sentence:
            sentences.append(sentence)
        start = match.end()
    tail = normalized[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


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


def run_render(
    markdown_path: Path, output_path: Path, voice: str, speed: float,
    settings: Mapping[str, object], pronunciation_path: Path, listening_copy: Path | None = None,
) -> Path:
    validate_settings(settings)
    validate_render_spec(voice, speed)
    pronunciations = load_pronunciations(pronunciation_path)
    blocks = [SpeechBlock(block.kind, apply_pronunciations(block.text, pronunciations)) for block in markdown_to_blocks(markdown_path.read_text(encoding="utf-8"))]
    chunks = chunk_blocks(blocks, settings["chunking"]["max_words"])  # type: ignore[index]
    model = _default_model_loader(str(settings["model"]))
    rendered, sample_rate, _ = synthesize_chunks(model, chunks, voice, float(speed), str(settings["lang_code"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_pcm16_wav(output_path, assemble_audio(rendered, sample_rate, settings["pauses"]))  # type: ignore[arg-type]
    if listening_copy is not None:
        encode_listening_copy(output_path, listening_copy)
    return output_path


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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
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
            )
            print(output)
    except Exception as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
