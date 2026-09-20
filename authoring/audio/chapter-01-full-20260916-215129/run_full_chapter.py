#!/usr/bin/env python3
"""One-run, non-invasive orchestration for the user-requested Chapter One render.

This script imports the repository's existing narration implementation, invokes
its supported ``render`` command, and captures the already-produced synthesis
chunks and runtime facts without changing the implementation itself.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import traceback
import wave

import numpy as np
import yaml


OUTPUT_DIR = Path(__file__).resolve().parent
REPO_ROOT = OUTPUT_DIR.parents[2]
AUDIO_ROOT = REPO_ROOT / "authoring/audio"
NARRATE_PATH = AUDIO_ROOT / "scripts/narrate.py"
SOURCE_PATH = (
    REPO_ROOT
    / "authoring/editions/1984/drafts/draft-01/chapters/01-before-hogwarts/draft-revision-04.md"
)
SETTINGS_PATH = AUDIO_ROOT / "narration-settings.yaml"
PRONUNCIATIONS_PATH = AUDIO_ROOT / "pronunciation-guide.yaml"
MASTER_PATH = OUTPUT_DIR / "chapter-01-full.wav"
LISTENING_PATH = OUTPUT_DIR / "chapter-01-full.mp3"
CHUNKS_DIR = OUTPUT_DIR / "chunks"
CHUNK_MANIFEST_PATH = CHUNKS_DIR / "chunk-manifest.yaml"
REPORT_PATH = OUTPUT_DIR / "generation-report.yaml"
LOG_PATH = OUTPUT_DIR / "run.log"
VOICE = "bm_george"
SPEED = 0.96


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as input_file:
        for block in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_narrate_module():
    spec = importlib.util.spec_from_file_location("chapter_one_narrate", NARRATE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import narration implementation: {NARRATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def require_new_targets() -> None:
    for path in (MASTER_PATH, LISTENING_PATH, CHUNKS_DIR, REPORT_PATH, LOG_PATH):
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite task output: {path}")


def ffprobe(path: Path) -> dict[str, object]:
    result = subprocess.run(
        [
            "/opt/homebrew/bin/ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,format_name,size,bit_rate",
            "-show_entries",
            "stream=index,codec_name,sample_fmt,sample_rate,channels,channel_layout,bit_rate",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def full_decode(path: Path) -> dict[str, object]:
    result = subprocess.run(
        [
            "/opt/homebrew/bin/ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-f",
            "null",
            "-",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "exit_code": result.returncode,
        "stderr": result.stderr,
        "passed": result.returncode == 0,
    }


def pcm16_from_float(audio: np.ndarray) -> np.ndarray:
    samples = np.asarray(audio, dtype=np.float32).reshape(-1)
    peak = float(np.max(np.abs(samples)))
    if peak > 0.95:
        samples = samples * (0.95 / peak)
    return np.rint(samples * 32767).astype("<i2")


def read_pcm16(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as input_file:
        if input_file.getnchannels() != 1 or input_file.getsampwidth() != 2:
            raise RuntimeError("Expected a mono, 16-bit PCM WAV")
        sample_rate = input_file.getframerate()
        frames = input_file.readframes(input_file.getnframes())
    return np.frombuffer(frames, dtype="<i2"), sample_rate


def select_matching_assembly(assemblies, rendered, sample_rate):
    """Return the chapter assembly, excluding validation-only dummy calls."""
    matches = [
        assembly
        for assembly in assemblies
        if assembly["sample_rate"] == sample_rate
        and len(assembly["chunks"]) == len(rendered)
        and all(
            actual is expected
            for actual, expected in zip(
                assembly["chunks"], rendered, strict=True
            )
        )
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one chapter assembly, found {len(matches)}"
        )
    return matches[0]


def zero_prefix(samples: np.ndarray) -> int:
    nonzero = np.flatnonzero(samples)
    return int(nonzero[0]) if nonzero.size else int(samples.size)


def zero_suffix(samples: np.ndarray) -> int:
    return zero_prefix(samples[::-1])


def verify_text_sequence(blocks, chunks) -> dict[str, object]:
    rebuilt: list[tuple[object, str]] = []
    current: list[str] = []
    current_kind = None
    for chunk in chunks:
        if current_kind is None:
            current_kind = chunk.kind
        if chunk.kind != current_kind:
            raise RuntimeError("Chunk kind changed before its source block ended")
        current.append(chunk.text)
        if chunk.ends_block:
            rebuilt.append((current_kind, " ".join(current)))
            current = []
            current_kind = None
    if current:
        raise RuntimeError("Final source block lacks an ends_block chunk")
    expected = [(block.kind, block.text) for block in blocks]
    return {
        "passed": rebuilt == expected,
        "expected_block_count": len(expected),
        "rebuilt_block_count": len(rebuilt),
    }


def inspect_joins(rendered, sample_rate: int, pauses: dict[str, int]) -> dict[str, object]:
    opening = int(sample_rate * pauses["opening_ms"] / 1000)
    closing = int(sample_rate * pauses["closing_ms"] / 1000)
    ending_pause_keys = {
        "paragraph": "paragraph_ms",
        "section": "section_ms",
        "chapter": "chapter_ms",
    }
    cursor = opening
    joins: list[dict[str, object]] = []
    max_extra_silence_ms = 0.0
    for index, chunk in enumerate(rendered):
        audio_pcm = pcm16_from_float(chunk.audio)
        cursor += len(audio_pcm)
        pause_key = (
            ending_pause_keys[chunk.kind.value]
            if chunk.ends_block
            else "continuation_ms"
        )
        pause_samples = int(sample_rate * pauses[pause_key] / 1000)
        if index + 1 < len(rendered):
            next_pcm = pcm16_from_float(rendered[index + 1].audio)
            trailing = zero_suffix(audio_pcm)
            leading = zero_prefix(next_pcm)
            extra_ms = (trailing + leading) * 1000 / sample_rate
            max_extra_silence_ms = max(max_extra_silence_ms, extra_ms)
            joins.append(
                {
                    "after_chunk": index + 1,
                    "before_chunk": index + 2,
                    "configured_pause_ms": pauses[pause_key],
                    "rendered_trailing_zero_ms": round(trailing * 1000 / sample_rate, 3),
                    "next_rendered_leading_zero_ms": round(leading * 1000 / sample_rate, 3),
                    "effective_zero_gap_ms": round(
                        pauses[pause_key] + extra_ms, 3
                    ),
                    "outgoing_edge_abs_pcm16": int(abs(int(audio_pcm[-1]))),
                    "incoming_edge_abs_pcm16": int(abs(int(next_pcm[0]))),
                }
            )
        cursor += pause_samples
    expected_total = cursor + closing
    return {
        "join_count": len(joins),
        "joins": joins,
        "max_rendered_extra_silence_ms": round(max_extra_silence_ms, 3),
        "expected_total_samples": expected_total,
    }


def render() -> dict[str, object]:
    narrate = load_narrate_module()
    settings = narrate._read_settings(SETTINGS_PATH)
    narrate.validate_settings(settings)
    pronunciations = narrate.load_pronunciations(PRONUNCIATIONS_PATH)
    source_markdown = SOURCE_PATH.read_text(encoding="utf-8")
    provenance_report, provenance_warnings, _provenance_path, _provenance = (
        narrate.inspect_narration_provenance(SOURCE_PATH)
    )
    unsupported = [
        line
        for line in source_markdown.splitlines()
        if re.match(r"^(?:```|~~~|>|[-*+] |[0-9]+[.)] |\|)", line)
    ]
    if unsupported:
        raise RuntimeError(f"Unsupported Markdown constructs: {unsupported}")
    source_blocks = narrate.markdown_to_blocks(source_markdown)
    prepared_blocks = [
        narrate.SpeechBlock(
            block.kind, narrate.apply_pronunciations(block.text, pronunciations)
        )
        for block in source_blocks
    ]
    expected_chunks = narrate.chunk_blocks(
        prepared_blocks, settings["chunking"]["max_words"]
    )
    text_sequence = verify_text_sequence(prepared_blocks, expected_chunks)
    if not text_sequence["passed"]:
        raise RuntimeError("Preprocessing/chunking did not preserve the source block sequence")

    captured: dict[str, object] = {
        "models": [],
        "syntheses": [],
        "assemblies": [],
    }
    original_loader = narrate._default_model_loader
    original_synthesize = narrate.synthesize_chunks
    original_assemble = narrate.assemble_audio

    def capturing_loader(model_id: str):
        model = original_loader(model_id)
        captured["models"].append((model_id, model))
        return model

    def capturing_synthesize(model, chunks, voice, speed, lang_code):
        result = original_synthesize(model, chunks, voice, speed, lang_code)
        captured["syntheses"].append(
            {
                "chunks": list(chunks),
                "voice": voice,
                "speed": speed,
                "lang_code": lang_code,
                "result": result,
            }
        )
        return result

    def capturing_assemble(chunks, sample_rate, pause_settings):
        assembled = original_assemble(chunks, sample_rate, pause_settings)
        captured["assemblies"].append(
            {
                "chunks": list(chunks),
                "sample_rate": sample_rate,
                "pauses": dict(pause_settings),
                "audio": np.asarray(assembled, dtype=np.float32).copy(),
            }
        )
        return assembled

    narrate._default_model_loader = capturing_loader
    narrate.synthesize_chunks = capturing_synthesize
    narrate.assemble_audio = capturing_assemble
    cli_exit = narrate.main(
        [
            "--settings",
            str(SETTINGS_PATH),
            "--pronunciations",
            str(PRONUNCIATIONS_PATH),
            "render",
            str(SOURCE_PATH),
            "--output",
            str(MASTER_PATH),
            "--voice",
            VOICE,
            "--speed",
            str(SPEED),
            "--listening-copy",
            str(LISTENING_PATH),
        ]
    )
    if cli_exit != 0:
        raise RuntimeError(f"Renderer returned nonzero status: {cli_exit}")
    if len(captured["models"]) != 1:
        raise RuntimeError("Expected exactly one model load")
    if len(captured["syntheses"]) != 1:
        raise RuntimeError("Expected exactly one synthesis pass")

    synthesis = captured["syntheses"][0]
    rendered, sample_rate, synthesis_evidence = synthesis["result"]
    assembly = select_matching_assembly(
        captured["assemblies"], rendered, sample_rate
    )
    if synthesis["chunks"] != expected_chunks:
        raise RuntimeError("Synthesis chunk sequence differs from the expected sequence")
    assembly_sequence_verified = (
        len(assembly["chunks"]) == len(rendered)
        and all(
            actual is expected
            for actual, expected in zip(assembly["chunks"], rendered, strict=True)
        )
    )
    if not assembly_sequence_verified:
        raise RuntimeError("Assembly did not receive each rendered chunk once and in order")
    if sample_rate != 24000 or assembly["sample_rate"] != sample_rate:
        raise RuntimeError(f"Unexpected sample rate: {sample_rate}")
    if not str(synthesis_evidence["audio_array_type"]).startswith("mlx."):
        raise RuntimeError(
            f"Synthesis did not return MLX audio arrays: {synthesis_evidence}"
        )

    runtime = narrate.collect_runtime_evidence()
    if not runtime.gpu_selected:
        raise RuntimeError(f"MLX GPU was not selected: {runtime}")
    model_id, model = captured["models"][0]
    model_revision = narrate.resolve_model_revision(model, model_id)

    CHUNKS_DIR.mkdir(parents=False, exist_ok=False)
    chunk_records: list[dict[str, object]] = []
    for index, (speech_chunk, rendered_chunk) in enumerate(
        zip(expected_chunks, rendered, strict=True), start=1
    ):
        chunk_path = CHUNKS_DIR / f"chunk-{index:03d}.wav"
        narrate.write_pcm16_wav(chunk_path, rendered_chunk.audio, sample_rate)
        audio = narrate.inspect_wav(chunk_path)
        chunk_records.append(
            {
                "index": index,
                "path": str(chunk_path.relative_to(OUTPUT_DIR)),
                "sha256": sha256_path(chunk_path),
                "size_bytes": chunk_path.stat().st_size,
                "kind": speech_chunk.kind.value,
                "ends_block": speech_chunk.ends_block,
                "word_count": len(speech_chunk.text.split()),
                "text": speech_chunk.text,
                "audio": audio,
            }
        )
    actual_chunk_paths = sorted(CHUNKS_DIR.glob("chunk-*.wav"))
    chunk_count_verified = len(actual_chunk_paths) == len(expected_chunks)
    if not chunk_count_verified:
        raise RuntimeError("Generated chunk count does not match expected chunk count")

    master_pcm, master_sample_rate = read_pcm16(MASTER_PATH)
    expected_pcm = pcm16_from_float(assembly["audio"])
    master_matches_assembly = (
        master_sample_rate == sample_rate
        and master_pcm.shape == expected_pcm.shape
        and np.array_equal(master_pcm, expected_pcm)
    )
    if not master_matches_assembly:
        raise RuntimeError("WAV master is not the exact assembled PCM sequence")

    join_inspection = inspect_joins(
        rendered, sample_rate, dict(settings["pauses"])
    )
    if join_inspection["expected_total_samples"] != len(master_pcm):
        raise RuntimeError("Expected boundary accounting does not match WAV length")
    master_facts = narrate.inspect_wav(MASTER_PATH)
    wav_probe = ffprobe(MASTER_PATH)
    mp3_probe = ffprobe(LISTENING_PATH)
    wav_decode = full_decode(MASTER_PATH)
    mp3_decode = full_decode(LISTENING_PATH)
    if not wav_decode["passed"] or not mp3_decode["passed"]:
        raise RuntimeError("A complete ffmpeg decode failed")

    chunk_manifest = {
        "source_path": str(SOURCE_PATH),
        "source_sha256": sha256_path(SOURCE_PATH),
        "expected_chunk_count": len(expected_chunks),
        "actual_chunk_count": len(actual_chunk_paths),
        "sample_rate": sample_rate,
        "chunks": chunk_records,
    }
    CHUNK_MANIFEST_PATH.write_text(
        yaml.safe_dump(chunk_manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    warnings: list[str] = list(provenance_warnings)
    if max(
        (join["effective_zero_gap_ms"] for join in join_inspection["joins"]),
        default=0,
    ) > 2500:
        warnings.append(
            "At least one measured inter-chunk zero gap exceeds 2500 ms; see join_inspection."
        )

    report = {
        "status": "rendered_pending_final_repository_audit",
        **provenance_report,
        "source": {
            "path": str(SOURCE_PATH),
            "sha256": sha256_path(SOURCE_PATH),
            "size_bytes": SOURCE_PATH.stat().st_size,
            "designation": "Exact manuscript path supplied by the user as the finalized Chapter One draft.",
            "raw_word_count": len(source_markdown.split()),
            "spoken_block_count": len(prepared_blocks),
            "spoken_word_count": sum(len(block.text.split()) for block in prepared_blocks),
            "opening_text": expected_chunks[0].text,
            "closing_text": expected_chunks[-1].text,
        },
        "implementation": {
            "narrate_path": str(NARRATE_PATH),
            "narrate_sha256": sha256_path(NARRATE_PATH),
            "settings_path": str(SETTINGS_PATH),
            "settings_sha256": sha256_path(SETTINGS_PATH),
            "pronunciations_path": str(PRONUNCIATIONS_PATH),
            "pronunciations_sha256": sha256_path(PRONUNCIATIONS_PATH),
            "pronunciation_entry_count": len(pronunciations),
            "cli_command": [
                str(AUDIO_ROOT / ".venv/bin/python"),
                str(NARRATE_PATH),
                "render",
                str(SOURCE_PATH),
                "--output",
                str(MASTER_PATH),
                "--voice",
                VOICE,
                "--speed",
                str(SPEED),
                "--listening-copy",
                str(LISTENING_PATH),
            ],
            "cli_exit_code": cli_exit,
        },
        "configuration": {
            "engine": settings["engine"],
            "model": model_id,
            "model_revision": model_revision,
            "voice": VOICE,
            "language": settings["language"],
            "lang_code": settings["lang_code"],
            "speed": SPEED,
            "chunking": dict(settings["chunking"]),
            "pauses": dict(settings["pauses"]),
            "output": dict(settings["output"]),
        },
        "versions": {
            "python": sys.version.split()[0],
            "mlx_audio": narrate._package_version("mlx-audio"),
            "mlx": narrate._package_version("mlx"),
            "misaki": narrate._package_version("misaki"),
            "pyyaml": narrate._package_version("PyYAML"),
            "numpy": narrate._package_version("numpy"),
        },
        "runtime_evidence": {
            "device": runtime.device,
            "gpu_selected": runtime.gpu_selected,
            "metal_telemetry": runtime.metal_telemetry,
            "audio_array_type": synthesis_evidence["audio_array_type"],
        },
        "chunks": {
            "expected_count": len(expected_chunks),
            "actual_count": len(actual_chunk_paths),
            "directory": str(CHUNKS_DIR),
            "manifest": str(CHUNK_MANIFEST_PATH),
        },
        "outputs": {
            "wav": {
                "path": str(MASTER_PATH),
                "sha256": sha256_path(MASTER_PATH),
                "size_bytes": MASTER_PATH.stat().st_size,
                "audio": master_facts,
                "ffprobe": wav_probe,
                "full_decode": wav_decode,
            },
            "mp3": {
                "path": str(LISTENING_PATH),
                "sha256": sha256_path(LISTENING_PATH),
                "size_bytes": LISTENING_PATH.stat().st_size,
                "ffprobe": mp3_probe,
                "full_decode": mp3_decode,
            },
        },
        "validation": {
            "markdown_construct_check": "passed",
            "text_sequence": text_sequence,
            "chunk_count_verified": chunk_count_verified,
            "assembly_sequence_verified": assembly_sequence_verified,
            "master_matches_assembled_pcm": master_matches_assembly,
            "sample_rate_verified_24000_hz": sample_rate == 24000,
            "mlx_audio_array_verified": str(
                synthesis_evidence["audio_array_type"]
            ).startswith("mlx."),
            "mlx_gpu_verified": runtime.gpu_selected,
            "final_wav_full_decode": wav_decode["passed"],
            "final_mp3_full_decode": mp3_decode["passed"],
            "join_inspection": join_inspection,
            "audio_tests": "pending",
            "preexisting_file_hash_audit": "pending",
            "git_status_comparison": "pending",
            "human_full_listen": False,
        },
        "warnings": warnings,
        "deviations": [
            "This task-local wrapper captures in-memory chunks, detailed join evidence, independent probes, and full-decode results beyond the canonical render manifest."
        ],
    }
    REPORT_PATH.write_text(
        yaml.safe_dump(report, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return report


def main() -> int:
    require_new_targets()
    with LOG_PATH.open("x", encoding="utf-8") as log_file:
        with contextlib.redirect_stdout(log_file), contextlib.redirect_stderr(log_file):
            print("Starting Chapter One production render", flush=True)
            print(f"Source: {SOURCE_PATH}", flush=True)
            print(f"Output directory: {OUTPUT_DIR}", flush=True)
            try:
                report = render()
            except BaseException:
                traceback.print_exc()
                raise
            print(
                f"Rendered {report['chunks']['actual_count']} chunks; "
                f"duration={report['outputs']['wav']['audio']['duration_seconds']:.3f}s",
                flush=True,
            )
    print(
        json.dumps(
            {
                "report": str(REPORT_PATH),
                "chunks": report["chunks"]["actual_count"],
                "duration_seconds": report["outputs"]["wav"]["audio"][
                    "duration_seconds"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
