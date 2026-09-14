import unittest
from pathlib import Path

from authoring.audio.scripts.narrate import (
    BlockKind,
    SpeechBlock,
    extract_prose_excerpt,
    markdown_to_blocks,
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
