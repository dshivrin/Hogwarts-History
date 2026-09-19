import hashlib
import io
import shutil
import unittest
from contextlib import redirect_stderr
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from types import ModuleType
from unittest.mock import patch

import numpy as np
import yaml

import authoring.audio.scripts.narrate as narrate

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


class RenderConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.settings = {
            "engine": "kokoro",
            "model": "mlx-community/Kokoro-82M-bf16",
            "language": "british-english",
            "lang_code": "b",
            "voice": "bm_george",
            "speed": 0.96,
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

    def test_resolve_render_spec_uses_canonical_defaults(self):
        self.assertEqual(
            narrate.resolve_render_spec(self.settings, None, None),
            SampleSpec("bm_george", 0.96),
        )

    def test_resolve_render_spec_applies_each_override_independently(self):
        self.assertEqual(
            narrate.resolve_render_spec(self.settings, "bm_lewis", None),
            SampleSpec("bm_lewis", 0.96),
        )
        self.assertEqual(
            narrate.resolve_render_spec(self.settings, None, 0.92),
            SampleSpec("bm_george", 0.92),
        )
        self.assertEqual(
            narrate.resolve_render_spec(self.settings, "bm_lewis", 1.0),
            SampleSpec("bm_lewis", 1.0),
        )

    def test_normal_render_accepts_non_batch_voice_but_preserves_speed_range(self):
        self.assertEqual(
            narrate.validate_render_spec("bm_lewis", 0.96),
            SampleSpec("bm_lewis", 0.96),
        )
        for speed in (0.89, 1.06):
            with self.subTest(speed=speed):
                with self.assertRaisesRegex(ValueError, "0.90 and 1.05"):
                    narrate.validate_render_spec("bm_george", speed)

    def test_audition_batch_still_rejects_non_batch_voice(self):
        with self.assertRaisesRegex(ValueError, "Unsupported British voice"):
            narrate._validate_sample_specs([SampleSpec("bm_lewis", 0.96)])

    def test_render_cli_resolves_defaults_and_partial_overrides(self):
        cases = (
            ([], "bm_george", 0.96),
            (["--voice", "bm_lewis"], "bm_lewis", 0.96),
            (["--speed", "0.92"], "bm_george", 0.92),
            (["--voice", "bm_lewis", "--speed", "1.0"], "bm_lewis", 1.0),
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            settings_path = root / "settings.yaml"
            settings_path.write_text(yaml.safe_dump(self.settings), encoding="utf-8")
            narration_path = root / "narration.md"
            narration_path.write_text("# Chapter\n\nOpening prose.\n", encoding="utf-8")
            output_path = root / "output.wav"
            for overrides, expected_voice, expected_speed in cases:
                with self.subTest(overrides=overrides):
                    with patch.object(narrate, "run_render", return_value=output_path) as render:
                        exit_code = main(
                            [
                                "--settings", str(settings_path),
                                "render", str(narration_path),
                                "--output", str(output_path),
                                *overrides,
                            ]
                        )
                    self.assertEqual(exit_code, 0)
                    self.assertEqual(render.call_args.args[2:4], (expected_voice, expected_speed))

    def test_sample_cli_resolves_defaults_overrides_and_paragraph(self):
        cases = (
            ([], "bm_george", 0.96, None),
            (["--voice", "bm_lewis"], "bm_lewis", 0.96, None),
            (["--speed", "0.92"], "bm_george", 0.92, None),
            (
                ["--voice", "bm_lewis", "--speed", "1.0", "--paragraph", "3"],
                "bm_lewis",
                1.0,
                3,
            ),
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            settings_path = root / "settings.yaml"
            settings_path.write_text(yaml.safe_dump(self.settings), encoding="utf-8")
            narration_path = root / "narration.md"
            narration_path.write_text("# Chapter\n\nOpening prose.\n", encoding="utf-8")
            output_path = root / "sample.wav"
            for overrides, expected_voice, expected_speed, paragraph in cases:
                with self.subTest(overrides=overrides):
                    with patch.object(
                        narrate, "run_sample", return_value=output_path, create=True
                    ) as sample:
                        exit_code = main(
                            [
                                "--settings", str(settings_path),
                                "sample", str(narration_path),
                                "--output", str(output_path),
                                *overrides,
                            ]
                        )
                    self.assertEqual(exit_code, 0)
                    self.assertEqual(
                        sample.call_args.args[2:4],
                        (expected_voice, expected_speed),
                    )
                    self.assertEqual(sample.call_args.kwargs["paragraph"], paragraph)


class SampleSelectionTests(unittest.TestCase):
    def setUp(self):
        self.blocks = [
            SpeechBlock(BlockKind.CHAPTER, "Chapter One"),
            SpeechBlock(BlockKind.SECTION, "Before Hogwarts"),
            SpeechBlock(BlockKind.PARAGRAPH, "First sentence. Second sentence."),
            SpeechBlock(BlockKind.SECTION, "Later Section"),
            SpeechBlock(BlockKind.PARAGRAPH, "Third sentence."),
        ]

    def test_opening_selection_keeps_opening_headings_and_first_two_paragraphs(self):
        self.assertEqual(
            narrate.select_opening_sample_blocks(self.blocks),
            [self.blocks[0], self.blocks[1], self.blocks[2], self.blocks[4]],
        )

    def test_removing_final_sentence_preserves_headings_and_sentence_boundary(self):
        self.assertEqual(
            narrate.remove_final_prose_sentence(self.blocks[:3]),
            [
                self.blocks[0],
                self.blocks[1],
                SpeechBlock(BlockKind.PARAGRAPH, "First sentence."),
            ],
        )
        self.assertIsNone(
            narrate.remove_final_prose_sentence(
                [self.blocks[0], SpeechBlock(BlockKind.PARAGRAPH, "Only sentence.")]
            )
        )
        self.assertEqual(
            narrate.remove_final_prose_sentence(
                [self.blocks[0], self.blocks[2], self.blocks[4]]
            ),
            [self.blocks[0], self.blocks[2]],
        )

    def test_removing_final_sentence_does_not_split_after_abbreviation(self):
        self.assertIsNone(
            narrate.remove_final_prose_sentence(
                [
                    SpeechBlock(BlockKind.CHAPTER, "Chapter One"),
                    SpeechBlock(
                        BlockKind.PARAGRAPH,
                        "Mr. Smith arrived.",
                    ),
                ]
            )
        )

    def test_paragraph_numbering_ignores_headings(self):
        self.assertEqual(narrate.select_prose_paragraph(self.blocks, 1), [self.blocks[2]])
        self.assertEqual(narrate.select_prose_paragraph(self.blocks, 2), [self.blocks[4]])

    def test_invalid_paragraph_and_heading_only_narration_fail(self):
        for number in (0, -1, 3):
            with self.subTest(number=number):
                with self.assertRaisesRegex(ValueError, "prose paragraph"):
                    narrate.select_prose_paragraph(self.blocks, number)
        with self.assertRaisesRegex(ValueError, "prose"):
            narrate.select_opening_sample_blocks(self.blocks[:2])


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


class NarrationManuscriptTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        self.temp_dir = Path(self.temporary_directory.name)
        self.source = self.temp_dir / "chapter.md"
        self.narration = self.temp_dir / "narration.md"
        self.source.write_text(
            "---\nrevision: 7\n---\n\n"
            "# Chapter One\n\n"
            "## Before Hogwarts\n\n"
            "<!-- evidence: source-1 -->\n\n"
            "Spoken *words* remain.\n",
            encoding="utf-8",
        )
        self.pronunciations = self.temp_dir / "pronunciations.yaml"
        self.pronunciations.write_text(
            "version: 1\nsubstitutions: []\n", encoding="utf-8"
        )
        self.settings = {
            "engine": "kokoro",
            "model": "mlx-community/Kokoro-82M-bf16",
            "language": "british-english",
            "lang_code": "b",
            "voice": "bm_george",
            "speed": 0.96,
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

    def test_prepare_creates_readable_narration_and_provenance(self):
        prepare = getattr(narrate, "prepare_narration", None)
        self.assertTrue(callable(prepare), "narration preparation is missing")

        provenance_path = prepare(
            self.source,
            self.narration,
            prepared_at="2026-09-19T12:00:00+00:00",
        )

        self.assertEqual(
            self.narration.read_text(encoding="utf-8"),
            "# Chapter One\n\n## Before Hogwarts\n\nSpoken *words* remain.\n",
        )
        provenance = yaml.safe_load(provenance_path.read_text(encoding="utf-8"))
        narration_hash = hashlib.sha256(self.narration.read_bytes()).hexdigest()
        self.assertEqual(
            provenance["source_manuscript"]["sha256"],
            hashlib.sha256(self.source.read_bytes()).hexdigest(),
        )
        self.assertEqual(provenance["narration"]["prepared_sha256"], narration_hash)
        self.assertEqual(provenance["narration"]["current_sha256"], narration_hash)
        self.assertEqual(provenance["prepared_at"], "2026-09-19T12:00:00+00:00")

    def test_prepare_hashes_the_same_immutable_source_snapshot_it_reads(self):
        original_bytes = self.source.read_bytes()
        original_hash = hashlib.sha256(original_bytes).hexdigest()
        path_type = type(self.source)

        class RacingSourcePath(path_type):
            def read_text(path_self, *args, **kwargs):
                snapshot = super().read_text(*args, **kwargs)
                super().write_text("# Concurrent revision\n", encoding="utf-8")
                return snapshot

            def read_bytes(path_self):
                snapshot = super().read_bytes()
                super().write_text("# Concurrent revision\n", encoding="utf-8")
                return snapshot

        provenance_path = narrate.prepare_narration(
            RacingSourcePath(self.source), self.narration
        )

        provenance = yaml.safe_load(provenance_path.read_text(encoding="utf-8"))
        report, warnings, _, _ = narrate.inspect_narration_provenance(
            self.narration
        )
        self.assertIn("# Chapter One", self.narration.read_text(encoding="utf-8"))
        self.assertEqual(provenance["source_manuscript"]["sha256"], original_hash)
        self.assertEqual(report["source_manuscript"]["status"], "drifted")
        self.assertEqual(len(warnings), 1)

    def test_prepare_refuses_to_overwrite_existing_narration(self):
        self.narration.write_text("Human performance edit.\n", encoding="utf-8")

        with self.assertRaisesRegex(FileExistsError, "Refusing to overwrite"):
            narrate.prepare_narration(self.source, self.narration)

        self.assertEqual(
            self.narration.read_text(encoding="utf-8"),
            "Human performance edit.\n",
        )

    def test_prepare_uses_exclusive_creation_after_preflight_check(self):
        self.narration.write_text("Human performance edit.\n", encoding="utf-8")

        with patch.object(Path, "exists", return_value=False):
            with self.assertRaises(FileExistsError) as raised:
                narrate.prepare_narration(self.source, self.narration)

        self.assertEqual(Path(raised.exception.filename), self.narration)
        self.assertEqual(
            self.narration.read_text(encoding="utf-8"),
            "Human performance edit.\n",
        )

    def test_prepare_preserves_new_narration_if_sidecar_creation_races(self):
        provenance_path = narrate.narration_provenance_path(self.narration)
        provenance_path.write_text("human: provenance\n", encoding="utf-8")

        with patch.object(Path, "exists", return_value=False):
            with self.assertRaises(FileExistsError):
                narrate.prepare_narration(self.source, self.narration)

        self.assertTrue(self.narration.is_file())
        self.assertIn(
            "# Chapter One",
            self.narration.read_text(encoding="utf-8"),
        )
        self.assertEqual(
            provenance_path.read_text(encoding="utf-8"),
            "human: provenance\n",
        )

    def test_prepare_does_not_delete_a_replacement_after_sidecar_failure(self):
        provenance_path = narrate.narration_provenance_path(self.narration)
        provenance_path.write_text("human: provenance\n", encoding="utf-8")
        path_type = type(self.narration)

        class ReplacingPath(path_type):
            def open(path_self, mode="r", *args, **kwargs):
                opened = super().open(mode, *args, **kwargs)
                if path_self.name != "narration.md" or mode != "x":
                    return opened

                class ReplaceOnClose:
                    def __enter__(wrapper_self):
                        return opened.__enter__()

                    def __exit__(wrapper_self, *exception):
                        result = opened.__exit__(*exception)
                        Path(path_self).unlink()
                        Path(path_self).write_text(
                            "Concurrent human narration.\n", encoding="utf-8"
                        )
                        return result

                return ReplaceOnClose()

        racing_narration = ReplacingPath(self.narration)
        with patch.object(Path, "exists", return_value=False):
            with self.assertRaises(FileExistsError):
                narrate.prepare_narration(self.source, racing_narration)

        self.assertEqual(
            self.narration.read_text(encoding="utf-8"),
            "Concurrent human narration.\n",
        )

    def test_prepare_command_creates_narration_without_loading_tts_settings(self):
        exit_code = main(
            ["prepare", str(self.source), "--output", str(self.narration)]
        )

        self.assertEqual(exit_code, 0)
        self.assertTrue(self.narration.is_file())
        self.assertTrue(narrate.narration_provenance_path(self.narration).is_file())

    def test_render_uses_edited_narration_and_records_exact_chunks(self):
        provenance_path = narrate.prepare_narration(
            self.source,
            self.narration,
            prepared_at="2026-09-19T12:00:00+00:00",
        )
        prepared_hash = hashlib.sha256(self.narration.read_bytes()).hexdigest()
        self.narration.write_text(
            "# Spoken Title\n\nA narration-only sentence!\n",
            encoding="utf-8",
        )
        current_hash = hashlib.sha256(self.narration.read_bytes()).hexdigest()
        output = self.temp_dir / "chapter.wav"
        render_manifest = self.temp_dir / "render-manifest.yaml"
        chunk_manifest = self.temp_dir / "chunks" / "chunk-manifest.yaml"
        model = FakeKokoroModel(sample_rate=24000)

        narrate.run_render(
            self.narration,
            output,
            "bm_george",
            0.96,
            self.settings,
            self.pronunciations,
            manifest_path=render_manifest,
            chunk_manifest_path=chunk_manifest,
            model_loader=lambda _model_id: model,
            evidence_provider=lambda: RuntimeEvidence(
                "Device(gpu, 0)", True, {"active_memory": 1}, "mlx.core.array"
            ),
        )

        self.assertEqual(
            [request[0] for request in model.requests],
            ["Spoken Title", "A narration-only sentence!"],
        )
        self.assertEqual(inspect_wav(output)["sample_rate"], 24000)
        chunks = yaml.safe_load(chunk_manifest.read_text(encoding="utf-8"))
        self.assertEqual(
            [chunk["text"] for chunk in chunks["chunks"]],
            ["Spoken Title", "A narration-only sentence!"],
        )
        manifest = yaml.safe_load(render_manifest.read_text(encoding="utf-8"))
        self.assertEqual(manifest["narration"]["prepared_sha256"], prepared_hash)
        self.assertEqual(manifest["narration"]["current_sha256"], current_hash)
        provenance = yaml.safe_load(provenance_path.read_text(encoding="utf-8"))
        self.assertEqual(provenance["narration"]["prepared_sha256"], prepared_hash)
        self.assertEqual(provenance["narration"]["current_sha256"], current_hash)

    def test_source_drift_warns_and_is_recorded_without_blocking_render(self):
        narrate.prepare_narration(self.source, self.narration)
        self.source.write_text("# Revised print manuscript\n", encoding="utf-8")
        output = self.temp_dir / "chapter.wav"
        render_manifest = self.temp_dir / "render-manifest.yaml"
        warning_output = io.StringIO()

        with redirect_stderr(warning_output):
            narrate.run_render(
                self.narration,
                output,
                "bm_george",
                0.96,
                self.settings,
                self.pronunciations,
                manifest_path=render_manifest,
                model_loader=lambda _model_id: FakeKokoroModel(24000),
                evidence_provider=lambda: RuntimeEvidence(
                    "Device(gpu, 0)", True, {}, "mlx.core.array"
                ),
            )

        self.assertTrue(output.is_file())
        self.assertIn("WARNING: Source manuscript has changed", warning_output.getvalue())
        manifest = yaml.safe_load(render_manifest.read_text(encoding="utf-8"))
        self.assertEqual(manifest["source_manuscript"]["status"], "drifted")
        self.assertEqual(len(manifest["warnings"]), 1)
        self.assertIn("has changed", manifest["warnings"][0])

    def test_render_command_writes_requested_manifests_next_to_output(self):
        narrate.prepare_narration(self.source, self.narration)
        settings_path = self.temp_dir / "settings.yaml"
        settings_path.write_text(yaml.safe_dump(self.settings), encoding="utf-8")
        output_dir = self.temp_dir / "render"
        output = output_dir / "chapter.wav"

        with (
            patch(
                "authoring.audio.scripts.narrate._default_model_loader",
                return_value=FakeKokoroModel(24000),
            ),
            patch(
                "authoring.audio.scripts.narrate.collect_runtime_evidence",
                return_value=RuntimeEvidence(
                    "Device(gpu, 0)", True, {}, "mlx.core.array"
                ),
            ),
        ):
            exit_code = main(
                [
                    "--settings",
                    str(settings_path),
                    "--pronunciations",
                    str(self.pronunciations),
                    "render",
                    str(self.narration),
                    "--output",
                    str(output),
                    "--voice",
                    "bm_george",
                    "--speed",
                    "0.96",
                    "--manifest",
                    str(output_dir / "render-manifest.yaml"),
                    "--chunk-manifest",
                    str(output_dir / "chunks" / "chunk-manifest.yaml"),
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertTrue((output_dir / "render-manifest.yaml").is_file())
        self.assertTrue((output_dir / "chunks" / "chunk-manifest.yaml").is_file())

    def test_legacy_markdown_without_provenance_has_consistent_manifest_shape(self):
        legacy_input = self.temp_dir / "legacy-input.md"
        legacy_input.write_text("# Legacy narration\n", encoding="utf-8")
        output = self.temp_dir / "legacy.wav"
        manifest_path = self.temp_dir / "legacy-manifest.yaml"

        narrate.run_render(
            legacy_input,
            output,
            "bm_george",
            0.96,
            self.settings,
            self.pronunciations,
            manifest_path=manifest_path,
            model_loader=lambda _model_id: FakeKokoroModel(24000),
            evidence_provider=lambda: RuntimeEvidence(
                "Device(gpu, 0)", True, {}, "mlx.core.array"
            ),
        )

        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["narration"]["path"], str(legacy_input.resolve()))
        self.assertIsNone(manifest["narration"]["prepared_sha256"])

    def test_render_hash_and_chunks_use_one_immutable_narration_snapshot(self):
        narrate.prepare_narration(self.source, self.narration)
        original_bytes = self.narration.read_bytes()
        original_hash = hashlib.sha256(original_bytes).hexdigest()
        path_type = type(self.narration)

        class RacingPath(path_type):
            def read_bytes(path_self):
                snapshot = super().read_bytes()
                super().write_text(
                    "# Concurrent performance edit\n", encoding="utf-8"
                )
                return snapshot

            def read_text(path_self, *args, **kwargs):
                if path_self.name == "narration.md":
                    super().write_text(
                        "# Concurrent performance edit\n", encoding="utf-8"
                    )
                return super().read_text(*args, **kwargs)

        racing_narration = RacingPath(self.narration)
        output = self.temp_dir / "snapshot.wav"
        manifest_path = self.temp_dir / "snapshot-manifest.yaml"
        model = FakeKokoroModel(24000)

        narrate.run_render(
            racing_narration,
            output,
            "bm_george",
            0.96,
            self.settings,
            self.pronunciations,
            manifest_path=manifest_path,
            model_loader=lambda _model_id: model,
            evidence_provider=lambda: RuntimeEvidence(
                "Device(gpu, 0)", True, {}, "mlx.core.array"
            ),
        )

        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(model.requests[0][0], "Chapter One")
        self.assertEqual(manifest["narration"]["current_sha256"], original_hash)

    def test_full_render_manifest_identifies_full_kind(self):
        narrate.prepare_narration(self.source, self.narration)
        output = self.temp_dir / "full.wav"
        manifest = self.temp_dir / "full-manifest.yaml"

        narrate.run_render(
            self.narration,
            output,
            "bm_george",
            0.96,
            self.settings,
            self.pronunciations,
            manifest_path=manifest,
            model_loader=lambda _model_id: FakeKokoroModel(24000),
            evidence_provider=lambda: RuntimeEvidence(
                "Device(gpu, 0)", True, {}, "mlx.core.array"
            ),
        )

        self.assertEqual(
            yaml.safe_load(manifest.read_text(encoding="utf-8"))["render_kind"],
            "full",
        )

    def test_empty_full_narration_fails_before_model_loading(self):
        empty_narration = self.temp_dir / "empty-narration.md"
        empty_narration.write_text("<!-- editorial only -->\n", encoding="utf-8")
        load_count = 0

        def load(_model_id):
            nonlocal load_count
            load_count += 1
            return FakeKokoroModel(24000)

        with self.assertRaisesRegex(ValueError, "spoken content"):
            narrate.run_render(
                empty_narration,
                self.temp_dir / "empty.wav",
                "bm_george",
                0.96,
                self.settings,
                self.pronunciations,
                model_loader=load,
                evidence_provider=lambda: RuntimeEvidence(
                    "Device(gpu, 0)", True, {}, "mlx.core.array"
                ),
            )

        self.assertEqual(load_count, 0)
        self.assertFalse((self.temp_dir / "empty.wav").exists())


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

    def test_pronunciation_replacements_treat_backslashes_as_literal_text(self):
        entries = [Pronunciation("Hogwarts", r"Hog\warts", "literal test")]

        self.assertEqual(apply_pronunciations("Hogwarts", entries), r"Hog\warts")

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
    def test_split_sentences_is_conservative_for_common_non_boundaries(self):
        self.assertEqual(
            split_sentences(
                "Dr. A. N. Smith measured 3.5 metres... Then left. Next sentence."
            ),
            [
                "Dr. A. N. Smith measured 3.5 metres... Then left.",
                "Next sentence.",
            ],
        )

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
            RenderedChunk(BlockKind.CHAPTER, np.ones(1, dtype=np.float32), True),
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

        self.assertEqual(len(audio), 100 + 4 + 50 + 3 + 200 + 2 + 300 + 1 + 400 + 100)
        self.assertTrue(np.all(audio[:100] == 0))
        self.assertTrue(np.all(audio[104:154] == 0))
        self.assertTrue(np.all(audio[157:357] == 0))
        self.assertTrue(np.all(audio[359:659] == 0))
        self.assertTrue(np.all(audio[660:1060] == 0))
        self.assertTrue(np.all(audio[-100:] == 0))

    def test_assemble_audio_normalizes_non_numeric_audio_to_value_error(self):
        with self.assertRaisesRegex(ValueError, "Rendered chunk audio"):
            assemble_audio(
                [RenderedChunk(BlockKind.PARAGRAPH, np.array(["not audio"]), True)],
                sample_rate=24000,
                pauses={
                    "opening_ms": 0,
                    "continuation_ms": 0,
                    "paragraph_ms": 0,
                    "section_ms": 0,
                    "chapter_ms": 0,
                    "closing_ms": 0,
                },
            )

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


class DurationKokoroModel(FakeKokoroModel):
    def __init__(self, durations_by_text, sample_rate=10):
        super().__init__(sample_rate)
        self.durations_by_text = durations_by_text

    def generate(self, *, text, voice, speed, lang_code):
        if lang_code != "b":
            raise AssertionError("British language code was not passed")
        self.requests.append((text, voice, speed, lang_code))
        seconds = self.durations_by_text[text]
        audio = np.full(
            round(seconds * self.sample_rate), 0.25, dtype=np.float32
        )
        yield FakeGeneration(FakeMlxArray(audio), self.sample_rate)


class FakeNumpyKokoroModel(FakeKokoroModel):
    def generate(self, *, text, voice, speed, lang_code):
        if lang_code != "b":
            raise AssertionError("British language code was not passed to the model")
        self.requests.append((text, voice, speed, lang_code))
        yield FakeGeneration(np.array([0.0, 0.25, -0.25], dtype=np.float32), self.sample_rate)


class SampleRenderingTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        self.temp_dir = Path(self.temporary_directory.name)
        self.source = self.temp_dir / "chapter.md"
        self.source.write_text(
            "# Chapter One\n\n## Before Hogwarts\n\n"
            "First sentence. Second sentence.\n\nThird sentence.\n\n"
            "Fourth paragraph.\n",
            encoding="utf-8",
        )
        self.narration = self.temp_dir / "narration.md"
        narrate.prepare_narration(self.source, self.narration)
        self.pronunciations = self.temp_dir / "pronunciations.yaml"
        self.pronunciations.write_text(
            "version: 1\nsubstitutions: []\n", encoding="utf-8"
        )
        self.settings = {
            "engine": "kokoro",
            "model": "mlx-community/Kokoro-82M-bf16",
            "language": "british-english",
            "lang_code": "b",
            "voice": "bm_george",
            "speed": 0.96,
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
        self.output = self.temp_dir / "sample.wav"
        self.mp3 = self.temp_dir / "sample.mp3"
        self.manifest_path = self.temp_dir / "render-manifest.yaml"
        self.chunk_manifest_path = self.temp_dir / "chunks" / "chunk-manifest.yaml"

    def tearDown(self):
        self.temporary_directory.cleanup()

    @staticmethod
    def _evidence():
        return RuntimeEvidence("Device(gpu, 0)", True, {}, "mlx.core.array")

    def test_opening_retries_in_memory_and_finalizes_only_accepted_candidate(self):
        model = DurationKokoroModel(
            {
                "Chapter One": 2,
                "Before Hogwarts": 2,
                "First sentence. Second sentence.": 31,
                "Third sentence.": 5,
                "First sentence.": 20,
            }
        )
        load_count = 0

        def load(_model_id):
            nonlocal load_count
            load_count += 1
            return model

        with patch.object(
            narrate, "write_pcm16_wav", wraps=narrate.write_pcm16_wav
        ) as wav_writer:
            narrate.run_sample(
                self.narration,
                self.output,
                "bm_george",
                0.96,
                self.settings,
                self.pronunciations,
                manifest_path=self.manifest_path,
                chunk_manifest_path=self.chunk_manifest_path,
                model_loader=load,
                evidence_provider=self._evidence,
            )

        manifest = yaml.safe_load(self.manifest_path.read_text(encoding="utf-8"))
        chunks = yaml.safe_load(
            self.chunk_manifest_path.read_text(encoding="utf-8")
        )
        narration_hash = hashlib.sha256(self.narration.read_bytes()).hexdigest()
        self.assertEqual(load_count, 1)
        self.assertEqual(wav_writer.call_count, 1)
        self.assertLessEqual(inspect_wav(self.output)["duration_seconds"], 30.0)
        self.assertEqual(manifest["render_kind"], "opening_sample")
        self.assertEqual(manifest["narration"]["current_sha256"], narration_hash)
        self.assertEqual(
            [chunk["text"] for chunk in chunks["chunks"]],
            ["Chapter One", "Before Hogwarts", "First sentence."],
        )
        requested_text = [request[0] for request in model.requests]
        self.assertIn("First sentence. Second sentence.", requested_text)
        self.assertIn("Third sentence.", requested_text)
        self.assertEqual(requested_text[-1], "First sentence.")
        self.assertFalse(any(self.output.parent.glob("*rejected*.wav")))

    def test_paragraph_sample_uses_pronunciation_and_has_no_duration_limit(self):
        self.pronunciations.write_text(
            "version: 1\nsubstitutions:\n"
            "  - term: Hogwarts\n"
            "    replacement: Hog-warts\n"
            "    reason: test\n",
            encoding="utf-8",
        )
        self.narration.write_text(
            "# Chapter One\n\nFirst paragraph.\n\nHogwarts remains.\n\nThird paragraph.\n",
            encoding="utf-8",
        )
        full_hash = hashlib.sha256(self.narration.read_bytes()).hexdigest()
        model = DurationKokoroModel({"Hog-warts remains.": 35})

        narrate.run_sample(
            self.narration,
            self.output,
            "bm_george",
            0.96,
            self.settings,
            self.pronunciations,
            paragraph=2,
            manifest_path=self.manifest_path,
            chunk_manifest_path=self.chunk_manifest_path,
            model_loader=lambda _model_id: model,
            evidence_provider=self._evidence,
        )

        manifest = yaml.safe_load(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["render_kind"], "paragraph_sample")
        self.assertEqual(manifest["sample_selection"]["paragraph_number"], 2)
        self.assertEqual(manifest["narration"]["current_sha256"], full_hash)
        self.assertEqual([request[0] for request in model.requests], ["Hog-warts remains."])
        self.assertGreater(inspect_wav(self.output)["duration_seconds"], 30.0)

    def test_selection_errors_happen_before_model_loading_or_artifacts(self):
        headings_only = self.temp_dir / "headings.md"
        headings_only.write_text("# Chapter\n\n## Section\n", encoding="utf-8")
        cases = (
            (self.temp_dir / "missing.md", None),
            (self.narration, 0),
            (self.narration, -1),
            (self.narration, 99),
            (headings_only, None),
        )
        for markdown, paragraph in cases:
            with self.subTest(markdown=markdown.name, paragraph=paragraph):
                load_count = 0

                def load(_model_id):
                    nonlocal load_count
                    load_count += 1
                    return FakeKokoroModel(10)

                with self.assertRaises((FileNotFoundError, ValueError)):
                    narrate.run_sample(
                        markdown,
                        self.output,
                        "bm_george",
                        0.96,
                        self.settings,
                        self.pronunciations,
                        self.mp3,
                        paragraph=paragraph,
                        manifest_path=self.manifest_path,
                        chunk_manifest_path=self.chunk_manifest_path,
                        model_loader=load,
                        evidence_provider=self._evidence,
                    )
                self.assertEqual(load_count, 0)
                for path in (
                    self.output,
                    self.mp3,
                    self.manifest_path,
                    self.chunk_manifest_path,
                ):
                    self.assertFalse(path.exists())

    def test_unshortenable_opening_writes_nothing_and_preserves_provenance(self):
        provenance_path = narrate.narration_provenance_path(self.narration)
        before = yaml.safe_load(provenance_path.read_text(encoding="utf-8"))
        self.narration.write_text(
            "# Chapter One\n\nOne exceptionally long sentence.\n", encoding="utf-8"
        )
        model = DurationKokoroModel(
            {"Chapter One": 2, "One exceptionally long sentence.": 31}
        )

        with self.assertRaisesRegex(ValueError, "exceed 30 seconds"):
            narrate.run_sample(
                self.narration,
                self.output,
                "bm_george",
                0.96,
                self.settings,
                self.pronunciations,
                self.mp3,
                manifest_path=self.manifest_path,
                chunk_manifest_path=self.chunk_manifest_path,
                model_loader=lambda _model_id: model,
                evidence_provider=self._evidence,
            )

        for path in (
            self.output,
            self.mp3,
            self.manifest_path,
            self.chunk_manifest_path,
        ):
            self.assertFalse(path.exists())
        after = yaml.safe_load(provenance_path.read_text(encoding="utf-8"))
        self.assertEqual(
            after["narration"]["current_sha256"],
            before["narration"]["current_sha256"],
        )

    def test_sample_uses_one_immutable_narration_snapshot(self):
        original_hash = hashlib.sha256(self.narration.read_bytes()).hexdigest()
        path_type = type(self.narration)

        class RacingPath(path_type):
            def read_bytes(path_self):
                snapshot = super().read_bytes()
                super().write_text("# Replacement\n\nChanged prose.\n", encoding="utf-8")
                return snapshot

        model = DurationKokoroModel(
            {
                "Chapter One": 1,
                "Before Hogwarts": 1,
                "First sentence. Second sentence.": 2,
                "Third sentence.": 1,
            }
        )
        narrate.run_sample(
            RacingPath(self.narration),
            self.output,
            "bm_george",
            0.96,
            self.settings,
            self.pronunciations,
            manifest_path=self.manifest_path,
            chunk_manifest_path=self.chunk_manifest_path,
            model_loader=lambda _model_id: model,
            evidence_provider=self._evidence,
        )

        manifest = yaml.safe_load(self.manifest_path.read_text(encoding="utf-8"))
        chunks = yaml.safe_load(
            self.chunk_manifest_path.read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["narration"]["current_sha256"], original_hash)
        self.assertEqual(chunks["chunks"][0]["text"], "Chapter One")


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
            "voice": "bm_george",
            "speed": 0.96,
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

    def test_run_audition_rejects_colliding_output_names_before_model_loading(self):
        with self.assertRaisesRegex(ValueError, "output filename"):
            run_audition(
                fixture_path=self.fixture,
                sample_specs=[SampleSpec("bm_daniel", 0.955), SampleSpec("bm_daniel", 0.956)],
                settings=self.settings,
                pronunciation_path=self.pronunciations,
                output_dir=self.output_dir,
                manifest_path=self.manifest,
                model_loader=lambda _model_id: (_ for _ in ()).throw(AssertionError("model must not load")),
                evidence_provider=self._evidence,
            )

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

    def test_settings_require_valid_canonical_voice_and_speed(self):
        for changes, message in (
            ({"voice": None}, "voice"),
            ({"voice": ""}, "voice"),
            ({"speed": None}, "speed"),
            ({"speed": 0.89}, "0.90 and 1.05"),
        ):
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(ValueError, message):
                    validate_settings(dict(self.settings, **changes))

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

    def test_relative_manifest_merges_after_project_relocation(self):
        original_root = self.temp_dir / "original-audio"
        relocated_root = self.temp_dir / "relocated-audio"
        original_fixture = original_root / "fixtures/audition-excerpt.txt"
        original_guide = original_root / "pronunciations.yaml"
        original_fixture.parent.mkdir(parents=True)
        original_fixture.write_bytes(self.fixture.read_bytes())
        original_guide.write_text(self.pronunciations.read_text(encoding="utf-8"), encoding="utf-8")
        original_manifest = original_root / "samples/audition-manifest.yaml"
        with patch("authoring.audio.scripts.narrate.DEFAULT_AUDIO_ROOT", original_root):
            initial = run_audition(
                original_fixture,
                [SampleSpec("bm_daniel", 0.96), SampleSpec("bf_emma", 0.96)],
                self.settings,
                original_guide,
                original_root / "samples",
                original_manifest,
                lambda _model_id: FakeKokoroModel(24000),
                self._evidence,
            )
        manifest_data = yaml.safe_load(original_manifest.read_text(encoding="utf-8"))
        self.assertEqual(manifest_data["fixture_path"], "fixtures/audition-excerpt.txt")
        self.assertEqual({record["path"] for record in initial}, {"samples/bm-daniel-096.wav", "samples/bf-emma-096.wav"})
        relocated_fixture = relocated_root / "fixtures/audition-excerpt.txt"
        relocated_fixture.parent.mkdir(parents=True)
        relocated_fixture.write_bytes(original_fixture.read_bytes())
        relocated_guide = relocated_root / "pronunciations.yaml"
        relocated_guide.write_text(original_guide.read_text(encoding="utf-8"), encoding="utf-8")
        relocated_manifest = relocated_root / "samples/audition-manifest.yaml"
        relocated_manifest.parent.mkdir(parents=True)
        manifest_data["fixture_path"] = "fixtures/../fixtures/audition-excerpt.txt"
        relocated_manifest.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")

        with patch("authoring.audio.scripts.narrate.DEFAULT_AUDIO_ROOT", relocated_root):
            records = run_audition(
                relocated_fixture,
                [SampleSpec("bm_daniel", 1.0)],
                self.settings,
                relocated_guide,
                relocated_root / "samples",
                relocated_manifest,
                lambda _model_id: FakeKokoroModel(24000),
                self._evidence,
            )

        self.assertEqual(
            [record["path"] for record in records],
            ["samples/bm-daniel-096.wav", "samples/bf-emma-096.wav", "samples/bm-daniel-100.wav"],
        )

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


class GeorgeCalibrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        self.temp_dir = Path(self.temporary_directory.name)
        self.fixture = self.temp_dir / "george-calibration-excerpt.txt"
        self.fixture.write_text(
            "First literary sentence; it has two clauses.\n\n"
            "The secure outline is spare.",
            encoding="utf-8",
        )
        self.pronunciations = self.temp_dir / "pronunciations.yaml"
        self.pronunciations.write_text(
            "version: 1\nsubstitutions: []\n", encoding="utf-8"
        )
        self.output_dir = self.temp_dir / "samples"
        self.manifest = self.output_dir / "george-calibration-manifest.yaml"
        self.settings = {
            "engine": "kokoro",
            "model": "mlx-community/Kokoro-82M-bf16",
            "language": "british-english",
            "lang_code": "b",
            "voice": "bm_george",
            "speed": 0.96,
            "chunking": {"max_words": 160},
            "pauses": {
                "opening_ms": 120,
                "continuation_ms": 80,
                "paragraph_ms": 400,
                "section_ms": 1000,
                "chapter_ms": 1750,
                "closing_ms": 180,
            },
            "output": {"intermediate": "wav", "listening_copy": "mp3"},
        }

    def tearDown(self):
        self.temporary_directory.cleanup()

    @staticmethod
    def _evidence():
        return RuntimeEvidence(
            "Device(gpu, 0)", True, {"active_memory": 1}, "mlx.core.array"
        )

    @staticmethod
    def _fake_normalizer(wav_path, mp3_path, sample_rate, ffmpeg):
        mp3_path.write_bytes(b"normalised listening copy")
        return {
            "settings": {
                "integrated_lufs": -19.0,
                "true_peak_dbtp": -1.0,
                "loudness_range_lu": 7.0,
                "channels": 1,
                "sample_rate": sample_rate,
                "codec": "libmp3lame",
                "bitrate": "128k",
            },
            "commands": {
                "analysis": [ffmpeg, "analysis", str(wav_path)],
                "normalise": [ffmpeg, "normalise", str(mp3_path)],
                "measurement": [ffmpeg, "measurement", str(mp3_path)],
            },
            "measured_output": {
                "integrated_lufs": -19.0,
                "true_peak_dbtp": -1.1,
                "loudness_range_lu": 0.0,
            },
        }

    def test_calibration_reuses_one_model_and_records_exact_variants(self):
        loads = 0
        model = FakeKokoroModel(sample_rate=24000)

        def loader(model_id):
            nonlocal loads
            self.assertEqual(model_id, "mlx-community/Kokoro-82M-bf16")
            loads += 1
            return model

        runner = getattr(narrate, "run_george_calibration", None)
        self.assertTrue(callable(runner), "calibration runner is missing")
        records = runner(
            fixture_path=self.fixture,
            settings=self.settings,
            pronunciation_path=self.pronunciations,
            output_dir=self.output_dir,
            manifest_path=self.manifest,
            ffmpeg="/opt/homebrew/bin/ffmpeg",
            model_loader=loader,
            evidence_provider=self._evidence,
            listening_copy_encoder=self._fake_normalizer,
        )

        self.assertEqual(loads, 1)
        self.assertEqual([record["variant"] for record in records], ["A", "B", "C"])
        self.assertEqual([record["speed"] for record in records], [0.96, 0.98, 0.96])
        self.assertEqual(
            [record["paragraph_pause_ms"] for record in records], [400, 400, 275]
        )
        self.assertEqual(
            [Path(record["wav_path"]).name for record in records],
            [
                "bm-george-calibration-a-096.wav",
                "bm-george-calibration-b-098.wav",
                "bm-george-calibration-c-096-shorter-pauses.wav",
            ],
        )
        self.assertEqual(
            [Path(record["mp3_path"]).name for record in records],
            [
                "bm-george-calibration-a-096.mp3",
                "bm-george-calibration-b-098.mp3",
                "bm-george-calibration-c-096-shorter-pauses.mp3",
            ],
        )
        fixture_hash = hashlib.sha256(self.fixture.read_bytes()).hexdigest()
        self.assertEqual({record["fixture_sha256"] for record in records}, {fixture_hash})
        self.assertEqual({record["voice"] for record in records}, {"bm_george"})
        self.assertEqual({record["lang_code"] for record in records}, {"b"})
        self.assertTrue(all(record["raw_wav_unnormalised"] for record in records))
        self.assertTrue(all(Path(record["wav_path"]).is_file() for record in records))
        self.assertTrue(all(Path(record["mp3_path"]).is_file() for record in records))
        self.assertTrue(
            all(
                record["wav_sha256"]
                == hashlib.sha256(Path(record["wav_path"]).read_bytes()).hexdigest()
                for record in records
            )
        )
        manifest = yaml.safe_load(self.manifest.read_text(encoding="utf-8"))
        self.assertEqual(manifest["model_load_count"], 1)
        self.assertEqual(manifest["human_selection"], "pending")
        self.assertEqual(manifest["variants"], records)
        self.assertEqual(len(model.requests), 4)
        self.assertEqual(
            [request[2] for request in model.requests],
            [0.96, 0.96, 0.98, 0.98],
        )

    def test_parser_exposes_the_fixed_george_calibration_workflow(self):
        args = narrate.build_parser().parse_args(["george-calibration"])

        self.assertEqual(args.command, "george-calibration")
        self.assertEqual(
            args.fixture,
            narrate.DEFAULT_AUDIO_ROOT
            / "fixtures/george-calibration-excerpt.txt",
        )
        self.assertEqual(args.output_dir, narrate.DEFAULT_AUDIO_ROOT / "samples")
        self.assertEqual(
            args.manifest,
            narrate.DEFAULT_AUDIO_ROOT
            / "samples/george-calibration-manifest.yaml",
        )
        self.assertEqual(args.ffmpeg, "ffmpeg")

    def test_calibration_detects_a_listening_encoder_that_alters_the_raw_wav(self):
        def destructive_encoder(wav_path, mp3_path, sample_rate, ffmpeg):
            wav_path.write_bytes(b"changed")
            mp3_path.write_bytes(b"copy")
            return self._fake_normalizer(wav_path, mp3_path, sample_rate, ffmpeg)

        runner = getattr(narrate, "run_george_calibration", None)
        self.assertTrue(callable(runner), "calibration runner is missing")
        with self.assertRaisesRegex(RuntimeError, "raw WAV"):
            runner(
                fixture_path=self.fixture,
                settings=self.settings,
                pronunciation_path=self.pronunciations,
                output_dir=self.output_dir,
                manifest_path=self.manifest,
                ffmpeg="ffmpeg",
                model_loader=lambda _model_id: FakeKokoroModel(sample_rate=24000),
                evidence_provider=self._evidence,
                listening_copy_encoder=destructive_encoder,
            )

    def test_spoken_word_normalisation_creates_a_measured_mono_mp3(self):
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg is None:
            self.skipTest("ffmpeg is required for loudness-normalisation integration")
        sample_rate = 24000
        seconds = np.arange(sample_rate * 2, dtype=np.float32) / sample_rate
        wav_path = self.temp_dir / "tone.wav"
        mp3_path = self.temp_dir / "tone.mp3"
        write_pcm16_wav(
            wav_path,
            0.08 * np.sin(2 * np.pi * 220 * seconds),
            sample_rate,
        )

        normalizer = getattr(narrate, "normalize_spoken_word_mp3", None)
        self.assertTrue(callable(normalizer), "spoken-word normalizer is missing")
        evidence = normalizer(wav_path, mp3_path, sample_rate, ffmpeg)

        self.assertTrue(mp3_path.is_file())
        self.assertGreater(mp3_path.stat().st_size, 0)
        self.assertEqual(
            evidence["settings"],
            {
                "integrated_lufs": -19.0,
                "true_peak_dbtp": -1.0,
                "loudness_range_lu": 7.0,
                "channels": 1,
                "sample_rate": 24000,
                "codec": "libmp3lame",
                "bitrate": "128k",
            },
        )
        self.assertAlmostEqual(
            evidence["measured_output"]["integrated_lufs"], -19.0, delta=0.6
        )
        self.assertLessEqual(evidence["measured_output"]["true_peak_dbtp"], -1.0)
        self.assertEqual(set(evidence["commands"]), {"analysis", "normalise", "measurement"})
