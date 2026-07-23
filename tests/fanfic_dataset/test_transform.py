from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.fanfic_dataset.clean_html import (
    AnnotationError,
    ChapterAnnotations,
    build_clean_html,
    extract_chapter,
)
from scripts.fanfic_dataset.html_to_markdown import html_to_markdown
from scripts.fanfic_dataset.models import CapturedPage, ChapterRef


@pytest.fixture
def raw_html() -> str:
    return """<!doctype html><html><body>
    <div id=\"profile_top\"><h1>Invented Work</h1><a href=\"/u/7\">Synthetic Author</a>
    <p data-role=\"summary\">An invented summary.</p><div>Rated: Fiction T · Language: English · Published: Jan 1, 2020 · Updated: Jan 2, 2020</div></div>
    <nav>Post Review</nav><div id=\"storytext\">
      <p>Synthetic paragraph with <em>emphasized</em> words.</p>
      <p>Author's entirely invented note.</p><script>alert('no')</script><style>.x { color: red }</style><input value=\"Post Review\">
    </div><footer>Post Review</footer></body></html>"""


@pytest.fixture
def captured_page(tmp_path: Path, raw_html: str) -> CapturedPage:
    raw_path = tmp_path / "chapter-001.html"
    raw_path.write_text(raw_html, encoding="utf-8")
    return CapturedPage(
        source_id="HAH-FAN-001",
        chapter=ChapterRef(
            chapter_index=1,
            chapter_title="Invented Beginning",
            chapter_url="https://www.fanfiction.net/s/1/1/invented-work",
        ),
        retrieved_at_utc=datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc),
        final_url="https://www.fanfiction.net/s/1/1/invented-work",
        status=200,
        raw_html_path=raw_path,
    )


def test_clean_html_keeps_only_provenance_and_story_blocks(
    raw_html: str, captured_page: CapturedPage
) -> None:
    result = extract_chapter(raw_html, captured_page)

    assert "Synthetic paragraph" in result.html
    assert "Author's entirely invented note." in result.html
    assert "Post Review" not in result.html
    assert "<script" not in result.html
    assert result.blocks[0].sha256
    assert "Invented Work" in result.html
    assert "Synthetic Author" in result.html
    assert "An invented summary." in result.html


def test_markdown_preserves_emphasis_and_required_markers(
    captured_page: CapturedPage,
) -> None:
    clean_html = build_clean_html(captured_page, ChapterAnnotations())

    text = html_to_markdown(clean_html)

    assert "*emphasized*" in text
    assert "<!-- BEGIN CHAPTER TEXT -->" in text
    assert text.endswith("<!-- END CHAPTER TEXT -->\n")


def test_author_note_annotation_wraps_only_matching_block(
    raw_html: str, captured_page: CapturedPage
) -> None:
    first_block_hash = hashlib.sha256(
        "Synthetic paragraph with emphasized words.".encode("utf-8")
    ).hexdigest()
    annotations = ChapterAnnotations(author_note_block_sha256=[first_block_hash])

    text = html_to_markdown(build_clean_html(captured_page, annotations))

    assert text.count("<!-- BEGIN AUTHOR NOTE -->") == 1
    assert text.count("<!-- BEGIN CHAPTER TEXT -->") == 1


def test_annotations_reject_hashes_not_in_the_chapter(
    captured_page: CapturedPage,
) -> None:
    annotations = ChapterAnnotations(author_note_block_sha256=["a" * 64])

    with pytest.raises(AnnotationError, match="unknown block hash"):
        build_clean_html(captured_page, annotations)


def test_clean_html_preserves_source_order_and_drops_nested_controls(
    captured_page: CapturedPage,
) -> None:
    result = extract_chapter(
        """<div id='storytext'><p>First <strong>block</strong>.</p>
        <p>Second <button>ignored control</button> block.</p></div>""",
        captured_page,
    )

    assert [block.text for block in result.blocks] == ["First block.", "Second block."]
    assert result.html.index("First") < result.html.index("Second")
    assert "button" not in result.html


def test_only_first_chapter_includes_work_metadata(
    captured_page: CapturedPage,
) -> None:
    later_page = captured_page.model_copy(
        update={
            "chapter": captured_page.chapter.model_copy(
                update={"chapter_index": 2, "chapter_title": "Later"}
            )
        }
    )

    clean_html = build_clean_html(later_page, ChapterAnnotations())

    assert "Summary: An invented summary." not in clean_html
    assert "Rating: Fiction T" not in clean_html
    assert "Canonical source URL:" in clean_html


def test_markdown_normalizes_line_endings_nbsp_and_blank_runs() -> None:
    clean_html = """<main data-role='story'><section data-block-kind='chapter-text'>
    <p>One&nbsp;two</p>\r\n\r\n\r\n<p>Three</p></section></main>"""

    text = html_to_markdown(clean_html)

    assert "One two" in text
    assert "\r" not in text
    assert "\n\n\n" not in text
