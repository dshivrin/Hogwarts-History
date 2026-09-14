import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from authoring.audio.scripts.narrate import (
    BlockKind,
    Pronunciation,
    SpeechBlock,
    apply_pronunciations,
    chunk_blocks,
    extract_prose_excerpt,
    load_pronunciations,
    markdown_to_blocks,
    split_sentences,
    strip_inline_markdown,
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
