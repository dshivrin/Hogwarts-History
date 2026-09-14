import hashlib
import io
import unittest
from contextlib import redirect_stderr
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from types import ModuleType
from unittest.mock import patch

import numpy as np
import yaml

from authoring.audio.scripts.narrate import (
    BlockKind,
    Pronunciation,
    SpeechBlock,
    SpeechChunk,
    RenderedChunk,
    RuntimeEvidence,
    SampleSpec,
    apply_pronunciations,
    assemble_audio,
    chunk_blocks,
    encode_listening_copy,
    extract_prose_excerpt,
    inspect_wav,
    load_pronunciations,
    markdown_to_blocks,
    resolve_model_revision,
    run_audition,
    main,
    split_sentences,
    strip_inline_markdown,
    synthesize_chunks,
    validate_settings,
    write_pcm16_wav,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
MANUSCRIPT_PATH = (
    REPOSITORY_ROOT
    / "authoring/editions/1984/drafts/draft-01/chapters/01-before-hogwarts"
    / "draft-revision-01.md"
)
FIXTURE_PATH = REPOSITORY_ROOT / "authoring/audio/fixtures/audition-excerpt.txt"


class MarkdownPreparationTests(unittest.TestCase):
    def test_markdown_preparation_preserves_code_spans_and_strips_emphasis(self):
        self.assertEqual(
            strip_inline_markdown(
                "`__init__` `__future__` `__annotations__` `__builtins__` `__spec__`"
            ),
            "__init__ __future__ __annotations__ __builtins__ __spec__",
        )
        self.assertEqual(strip_inline_markdown("__careful__"), "careful")
        self.assertEqual(strip_inline_markdown("**careful**"), "careful")
        self.assertEqual(
            markdown_to_blocks("Import `__future__` before use.\n"),
            [SpeechBlock(BlockKind.PARAGRAPH, "Import __future__ before use.")],
        )

    def test_markdown_to_blocks_removes_blockquote_markers_from_every_line(self):
        self.assertEqual(
            markdown_to_blocks("> First line\n> Second line\n"),
            [SpeechBlock(BlockKind.PARAGRAPH, "First line Second line")],
        )

    def test_markdown_to_blocks_preserves_literal_underscore_characters(self):
        self.assertEqual(
            markdown_to_blocks("A snake_case name and *careful* prose.\n"),
            [SpeechBlock(BlockKind.PARAGRAPH, "A snake_case name and careful prose.")],
        )

    def test_markdown_to_blocks_removes_closing_atx_heading_markers(self):
        self.assertEqual(
            markdown_to_blocks("# A heading #\n"),
            [SpeechBlock(BlockKind.CHAPTER, "A heading")],
        )

    def test_markdown_to_blocks_removes_development_markup_and_keeps_spoken_text(self):
        source = """---\ndraft: true\n---\n# Chapter One\n\n## Before Hogwarts\n\nA *careful* [history](https://example.test) remains.\n\n<!-- evidence:\nsource-001\n-->\n"""
        self.assertEqual(
            markdown_to_blocks(source),
            [
                SpeechBlock(BlockKind.CHAPTER, "Chapter One"),
                SpeechBlock(BlockKind.SECTION, "Before Hogwarts"),
                SpeechBlock(BlockKind.PARAGRAPH, "A careful history remains."),
            ],
        )

    def test_extract_prose_excerpt_matches_preserved_fixture_exactly(self):
        manuscript = MANUSCRIPT_PATH.read_text(encoding="utf-8")
        fixture = FIXTURE_PATH.read_text(encoding="utf-8").strip()
        self.assertEqual(extract_prose_excerpt(manuscript), fixture)
        self.assertGreaterEqual(len(fixture.split()), 300)
        self.assertLessEqual(len(fixture.split()), 500)


class PronunciationTests(unittest.TestCase):
    def test_pronunciation_substitutions_are_boundary_aware(self):
        entries = [
            Pronunciation(
                term="Hogwarts",
                replacement="Hog-warts",
                reason="audition correction",
            )
        ]
        self.assertEqual(
            apply_pronunciations("Hogwarts and Hogwartsian", entries),
            "Hog-warts and Hogwartsian",
        )

    def test_applying_pronunciations_does_not_change_the_manuscript(self):
        before = MANUSCRIPT_PATH.read_bytes()
        apply_pronunciations(
            "Hogwarts", [Pronunciation("Hogwarts", "Hog-warts", "test")]
        )
        self.assertEqual(MANUSCRIPT_PATH.read_bytes(), before)

    def test_load_pronunciations_accepts_a_valid_versioned_guide(self):
        with TemporaryDirectory() as directory:
            guide = Path(directory) / "pronunciations.yaml"
            guide.write_text(
                "version: 1\nsubstitutions:\n  - term: Muggle\n"
                "    replacement: Mug-gull\n    reason: audition correction\n",
                encoding="utf-8",
            )
            self.assertEqual(
                load_pronunciations(guide),
                [Pronunciation("Muggle", "Mug-gull", "audition correction")],
            )

    def test_load_pronunciations_rejects_duplicate_or_incomplete_entries(self):
        for content in (
            "version: 1\nsubstitutions:\n  - term: Muggle\n"
            "    replacement: Mug-gull\n    reason: first\n  - term: Muggle\n"
            "    replacement: Mug-gull\n    reason: second\n",
            "version: 1\nsubstitutions:\n  - term: Muggle\n"
            "    replacement: ''\n    reason: audition correction\n",
        ):
            with self.subTest(content=content), TemporaryDirectory() as directory:
                guide = Path(directory) / "pronunciations.yaml"
                guide.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_pronunciations(guide)


class ChunkingTests(unittest.TestCase):
    def test_chunk_blocks_keeps_sentences_that_total_the_word_limit_together(self):
        chunks = chunk_blocks(
            [SpeechBlock(BlockKind.PARAGRAPH, "One two. Three.")], max_words=3
        )
        self.assertEqual([chunk.text for chunk in chunks], ["One two. Three."])

    def test_chunk_blocks_splits_only_between_sentences(self):
        block = SpeechBlock(
            BlockKind.PARAGRAPH,
            "One short sentence. Another complete sentence. Final words.",
        )
        self.assertEqual(
            [chunk.text for chunk in chunk_blocks([block], max_words=5)],
            ["One short sentence.", "Another complete sentence. Final words."],
        )

    def test_chunk_blocks_rejects_a_single_sentence_over_the_limit(self):
        with self.assertRaisesRegex(ValueError, "single sentence"):
            chunk_blocks(
                [SpeechBlock(BlockKind.PARAGRAPH, "one two three four five six.")],
                max_words=5,
            )

    def test_chunk_blocks_marks_only_the_final_chunk_as_ending_its_block(self):
        chunks = chunk_blocks(
            [SpeechBlock(BlockKind.SECTION, "One two. Three four.")], max_words=2
        )
        self.assertEqual(
            [(chunk.kind, chunk.text, chunk.ends_block) for chunk in chunks],
            [
                (BlockKind.SECTION, "One two.", False),
                (BlockKind.SECTION, "Three four.", True),
            ],
        )

    def test_split_sentences_normalizes_whitespace_and_keeps_unpunctuated_tail(self):
        self.assertEqual(
            split_sentences('  First sentence.  "Second question?" Final tail  '),
            ["First sentence.", '"Second question?"', "Final tail"],
        )

    def test_chunk_blocks_rejects_a_non_positive_word_limit(self):
        with self.assertRaisesRegex(ValueError, "max_words"):
            chunk_blocks([SpeechBlock(BlockKind.PARAGRAPH, "One sentence.")], 0)


class AudioAssemblyTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        self.temp_dir = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_assemble_audio_uses_semantic_pauses_and_boundary_silence(self):
        chunks = [
            RenderedChunk(BlockKind.PARAGRAPH, np.ones(4, dtype=np.float32), False),
            RenderedChunk(BlockKind.PARAGRAPH, np.ones(3, dtype=np.float32), True),
            RenderedChunk(BlockKind.SECTION, np.ones(2, dtype=np.float32), True),
        ]
        pauses = {
            "opening_ms": 100,
            "continuation_ms": 50,
            "paragraph_ms": 200,
            "section_ms": 300,
            "chapter_ms": 400,
            "closing_ms": 100,
        }

        audio = assemble_audio(chunks, sample_rate=1000, pauses=pauses)

        self.assertEqual(len(audio), 100 + 4 + 50 + 3 + 200 + 2 + 300 + 100)
        self.assertTrue(np.all(audio[:100] == 0))
        self.assertTrue(np.all(audio[-100:] == 0))

    def test_write_pcm16_wav_round_trips_without_clipping(self):
        path = self.temp_dir / "sample.wav"

        write_pcm16_wav(
            path, np.array([0.0, -0.5, 0.5, 0.0], dtype=np.float32), 24000
        )

        facts = inspect_wav(path)
        self.assertEqual(facts["sample_rate"], 24000)
        self.assertEqual(facts["channels"], 1)
        self.assertEqual(facts["sample_count"], 4)
        self.assertTrue(facts["finite"])
        self.assertEqual(facts["duration_seconds"], 4 / 24000)
        self.assertEqual(facts["non_silent_samples"], 2)
        self.assertEqual(facts["opening_silence_samples"], 1)
        self.assertEqual(facts["closing_silence_samples"], 1)
        self.assertLessEqual(facts["peak"], 0.951)

    def test_encode_listening_copy_surfaces_ffmpeg_failure_with_the_real_command(self):
        failing_ffmpeg = self.temp_dir / "failing-ffmpeg"
        failing_ffmpeg.write_text("#!/bin/sh\nexit 23\n", encoding="utf-8")
        failing_ffmpeg.chmod(0o755)
        wav_path = self.temp_dir / "input.wav"
        output_path = self.temp_dir / "nested" / "listening.m4a"

        with self.assertRaises(subprocess.CalledProcessError) as raised:
            encode_listening_copy(wav_path, output_path, ffmpeg=str(failing_ffmpeg))

        self.assertEqual(
            raised.exception.cmd,
            [
                str(failing_ffmpeg),
                "-y",
                "-v",
                "error",
                "-i",
                str(wav_path),
                str(output_path),
            ],
        )
        self.assertEqual(raised.exception.returncode, 23)
        self.assertTrue(output_path.parent.is_dir())


class FakeGeneration:
    def __init__(self, audio, sample_rate):
        self.audio = audio
        self.sample_rate = sample_rate


class FakeMlxArray:
    __module__ = "mlx.core"

    def __init__(self, values):
        self.values = values

    def eval(self):
        return self.values


class FakeKokoroModel:
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.model_path = "/cache/models--mlx-community--Kokoro-82M-bf16/snapshots/test-revision"
        self.requests = []

    def generate(self, *, text, voice, speed, lang_code):
        if lang_code != "b":
            raise AssertionError("British language code was not passed to the model")
        self.requests.append((text, voice, speed, lang_code))
        yield FakeGeneration(FakeMlxArray(np.array([0.0, 0.25, -0.25], dtype=np.float32)), self.sample_rate)


class FakeNumpyKokoroModel(FakeKokoroModel):
    def generate(self, *, text, voice, speed, lang_code):
        if lang_code != "b":
            raise AssertionError("British language code was not passed to the model")
        self.requests.append((text, voice, speed, lang_code))
        yield FakeGeneration(np.array([0.0, 0.25, -0.25], dtype=np.float32), self.sample_rate)


class AuditionTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        self.temp_dir = Path(self.temporary_directory.name)
        self.fixture = self.temp_dir / "fixture.txt"
        self.fixture.write_text("First sentence.\n\nSecond sentence.", encoding="utf-8")
        self.pronunciations = self.temp_dir / "pronunciations.yaml"
        self.pronunciations.write_text("version: 1\nsubstitutions: []\n", encoding="utf-8")
        self.output_dir = self.temp_dir / "samples"
        self.manifest = self.output_dir / "audition-manifest.yaml"
        self.settings = {
            "engine": "kokoro",
            "model": "mlx-community/Kokoro-82M-bf16",
            "language": "british-english",
            "lang_code": "b",
            "voice": None,
            "speed": None,
            "chunking": {"max_words": 160},
            "pauses": {
                "opening_ms": 0,
                "continuation_ms": 0,
                "paragraph_ms": 0,
                "section_ms": 0,
                "chapter_ms": 0,
                "closing_ms": 0,
            },
            "output": {"intermediate": "wav", "listening_copy": "mp3"},
        }

    def tearDown(self):
        self.temporary_directory.cleanup()

    def _evidence(self):
        return RuntimeEvidence("Device(gpu, 0)", True, {"active_memory": 1}, "mlx.core.array")

    def _run_two_sample_audition(self):
        return run_audition(
            fixture_path=self.fixture,
            sample_specs=[SampleSpec("bm_daniel", 0.96), SampleSpec("bf_emma", 0.96)],
            settings=self.settings,
            pronunciation_path=self.pronunciations,
            output_dir=self.output_dir,
            manifest_path=self.manifest,
            model_loader=lambda _model_id: FakeKokoroModel(sample_rate=24000),
            evidence_provider=self._evidence,
        )

    def test_run_audition_reuses_one_model_for_multiple_samples(self):
        loads = 0

        def loader(model_id):
            nonlocal loads
            self.assertEqual(model_id, "mlx-community/Kokoro-82M-bf16")
            loads += 1
            if loads > 1:
                raise AssertionError("model loaded more than once")
            return FakeKokoroModel(sample_rate=24000)

        records = run_audition(
            fixture_path=self.fixture,
            sample_specs=[SampleSpec("bm_daniel", 0.96), SampleSpec("bf_emma", 0.96)],
            settings=self.settings,
            pronunciation_path=self.pronunciations,
            output_dir=self.output_dir,
            manifest_path=self.manifest,
            model_loader=loader,
            evidence_provider=self._evidence,
        )

        self.assertEqual(loads, 1)
        self.assertEqual([record["voice"] for record in records], ["bm_daniel", "bf_emma"])
        self.assertTrue(all(Path(record["path"]).is_file() for record in records))

    def test_manifest_records_identical_fixture_and_exact_sample_settings(self):
        records = self._run_two_sample_audition()
        manifest = yaml.safe_load(self.manifest.read_text(encoding="utf-8"))

        self.assertEqual(len({record["fixture_sha256"] for record in records}), 1)
        self.assertEqual({record["lang_code"] for record in records}, {"b"})
        self.assertEqual({record["speed"] for record in records}, {0.96})
        self.assertEqual({record["model"] for record in records}, {"mlx-community/Kokoro-82M-bf16"})
        self.assertEqual(records[0]["fixture_sha256"], hashlib.sha256(self.fixture.read_bytes()).hexdigest())
        self.assertEqual(manifest["model_revision"], "test-revision")
        self.assertEqual(manifest["fixture_sha256"], records[0]["fixture_sha256"])

    def test_settings_require_canonical_voice_and_speed_to_remain_null(self):
        with self.assertRaisesRegex(ValueError, "voice.*null"):
            validate_settings(dict(self.settings, voice="bm_george"))
        with self.assertRaisesRegex(ValueError, "speed.*null"):
            validate_settings(dict(self.settings, speed=0.96))

    def test_run_audition_merges_compatible_existing_manifest_by_output_path(self):
        initial = self._run_two_sample_audition()
        refreshed = run_audition(
            fixture_path=self.fixture,
            sample_specs=[SampleSpec("bm_daniel", 1.0)],
            settings=self.settings,
            pronunciation_path=self.pronunciations,
            output_dir=self.output_dir,
            manifest_path=self.manifest,
            model_loader=lambda _model_id: FakeKokoroModel(sample_rate=24000),
            evidence_provider=self._evidence,
        )

        self.assertEqual([record["path"] for record in refreshed], [
            initial[0]["path"],
            initial[1]["path"],
            str((self.output_dir / "bm-daniel-100.wav").resolve()),
        ])
        manifest_records = yaml.safe_load(self.manifest.read_text(encoding="utf-8"))["samples"]
        self.assertEqual([record["path"] for record in manifest_records], [record["path"] for record in refreshed])

    def test_synthesize_chunks_preserves_semantic_boundaries_and_array_evidence(self):
        chunks = [SpeechChunk(BlockKind.PARAGRAPH, "One sentence.", True)]

        rendered, sample_rate, evidence = synthesize_chunks(
            FakeKokoroModel(24000), chunks, "bm_daniel", 0.96, "b"
        )

        self.assertEqual(sample_rate, 24000)
        self.assertEqual([(item.kind, item.ends_block) for item in rendered], [(BlockKind.PARAGRAPH, True)])
        self.assertEqual(evidence, {"audio_array_type": "mlx.core.FakeMlxArray"})

    def test_resolve_model_revision_reads_snapshot_path_without_network(self):
        model = type("Model", (), {"model_path": "/cache/models--org--repo/snapshots/abc123"})()

        self.assertEqual(resolve_model_revision(model, "org/repo"), "abc123")

    def test_resolve_model_revision_falls_back_to_hub_when_cache_scan_fails(self):
        hub = ModuleType("huggingface_hub")
        hub.scan_cache_dir = lambda: (_ for _ in ()).throw(RuntimeError("bad cache"))

        class FakeApi:
            def model_info(self, model_id):
                self.model_id = model_id
                return type("ModelInfo", (), {"sha": "hub-revision"})()

        hub.HfApi = FakeApi
        with patch.dict("sys.modules", {"huggingface_hub": hub}):
            self.assertEqual(resolve_model_revision(object(), "org/repo"), "hub-revision")

    def test_main_reports_model_load_errors_without_a_traceback(self):
        settings_path = self.temp_dir / "settings.yaml"
        settings_path.write_text(yaml.safe_dump(self.settings), encoding="utf-8")
        error_output = io.StringIO()
        with patch("authoring.audio.scripts.narrate.run_audition", side_effect=ModuleNotFoundError("mlx missing")), redirect_stderr(error_output):
            with self.assertRaises(SystemExit) as raised:
                main(["--settings", str(settings_path), "audition", "--sample", "bm_daniel=0.96"])

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("error: mlx missing", error_output.getvalue())
        self.assertNotIn("Traceback", error_output.getvalue())

    def test_run_audition_rejects_non_gpu_or_non_mlx_evidence_before_artifacts(self):
        for model, evidence in (
            (FakeKokoroModel(24000), RuntimeEvidence("Device(cpu, 0)", False, {}, "mlx.core.array")),
            (FakeNumpyKokoroModel(24000), RuntimeEvidence("Device(gpu, 0)", True, {}, "mlx.core.array")),
        ):
            with self.subTest(evidence=evidence, model=type(model).__name__):
                with self.assertRaisesRegex(RuntimeError, "MLX.*GPU|MLX-generated"):
                    run_audition(
                        fixture_path=self.fixture,
                        sample_specs=[SampleSpec("bm_daniel", 0.96)],
                        settings=self.settings,
                        pronunciation_path=self.pronunciations,
                        output_dir=self.output_dir,
                        manifest_path=self.manifest,
                        model_loader=lambda _model_id, model=model: model,
                        evidence_provider=lambda evidence=evidence: evidence,
                    )
                self.assertFalse(self.manifest.exists())
                self.assertEqual(list(self.output_dir.glob("*.wav")) if self.output_dir.exists() else [], [])
