from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from scripts.fanfic_dataset.clean_html import (
    AnnotationError,
    ChapterAnnotations,
    build_clean_html,
    extract_chapter,
)
from scripts.fanfic_dataset.html_to_markdown import html_to_markdown
from scripts.fanfic_dataset.fanfiction_net import ExtractionError
from scripts.fanfic_dataset.models import CapturedPage, ChapterRef


_VALID_PROFILE_HTML = (
    "<div id='profile_top'><h1>Invented Work</h1>"
    "<a href='/u/7'>Synthetic Author</a></div>"
)


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
        _VALID_PROFILE_HTML
        + """<div id='storytext'><p>First <strong>block</strong>.</p>
        <p>Second <button>ignored control</button> block.</p></div>""",
        captured_page,
    )

    assert [block.text for block in result.blocks] == ["First block.", "Second block."]
    assert result.html.index("First") < result.html.index("Second")
    assert "button" not in result.html


def test_clean_html_hash_text_separates_nested_blocks_without_spacing_inline_punctuation(
    captured_page: CapturedPage,
) -> None:
    result = extract_chapter(
        _VALID_PROFILE_HTML
        + (
            "<div id='storytext'><div><p>Alpha.</p><p>Beta.</p>"
            "<p>With <em>emphasis</em>.</p></div></div>"
        ),
        captured_page,
    )

    assert result.blocks[0].text == "Alpha. Beta. With emphasis."
    assert result.blocks[0].sha256 == hashlib.sha256(
        b"Alpha. Beta. With emphasis."
    ).hexdigest()
    assert result.blocks[0].html == (
        "<div><p>Alpha.</p><p>Beta.</p><p>With <em>emphasis</em>.</p></div>"
    )


def test_clean_html_ignores_direct_story_comments(
    captured_page: CapturedPage,
) -> None:
    result = extract_chapter(
        (
            "<div id='profile_top'><h1>Invented Work</h1>"
            "<a href='/u/7'>Synthetic Author</a></div>"
            "<div id='storytext'>Alpha<!-- invisible comment -->Beta"
            "<p>Gamma.</p></div>"
        ),
        captured_page,
    )

    assert [block.text for block in result.blocks] == ["AlphaBeta", "Gamma."]
    assert result.blocks[0].sha256 == hashlib.sha256(b"AlphaBeta").hexdigest()
    assert result.blocks[0].html == "<p>AlphaBeta</p>"
    assert "invisible comment" not in result.html


def test_markdown_groups_direct_inline_content_in_one_paragraph(
    captured_page: CapturedPage,
) -> None:
    result = extract_chapter(
        _VALID_PROFILE_HTML
        + (
            "<div id='storytext'>Hello <em>world</em>!"
            "<strong> Still together.</strong><p>Separate block.</p></div>"
        ),
        captured_page,
    )

    assert [block.text for block in result.blocks] == [
        "Hello world! Still together.",
        "Separate block.",
    ]
    assert result.blocks[0].html == (
        "<p>Hello <em>world</em>!<strong> Still together.</strong></p>"
    )
    assert html_to_markdown(result.html) == """<!-- BEGIN CHAPTER TEXT -->

Hello *world*! **Still together.**

Separate block.

<!-- END CHAPTER TEXT -->
"""


def test_markdown_groups_direct_br_with_surrounding_inline_content(
    captured_page: CapturedPage,
) -> None:
    result = extract_chapter(
        _VALID_PROFILE_HTML
        + "<div id='storytext'>First line.<br>Second <em>line</em>.</div>",
        captured_page,
    )

    assert [block.text for block in result.blocks] == ["First line. Second line."]
    assert result.blocks[0].html == (
        "<p>First line.<br/>Second <em>line</em>.</p>"
    )
    assert html_to_markdown(result.html) == """<!-- BEGIN CHAPTER TEXT -->

First line.
Second *line*.

<!-- END CHAPTER TEXT -->
"""


def test_clean_html_removes_nested_comments_without_separating_visible_text(
    captured_page: CapturedPage,
) -> None:
    result = extract_chapter(
        _VALID_PROFILE_HTML
        + (
            "<div id='storytext'><p>Before "
            "<em>visible<!-- nested comment -->text</em> after.</p></div>"
        ),
        captured_page,
    )

    assert [block.text for block in result.blocks] == ["Before visibletext after."]
    assert result.blocks[0].html == (
        "<p>Before <em>visibletext</em> after.</p>"
    )
    assert "nested comment" not in result.html
    assert "*visibletext*" in html_to_markdown(result.html)


@pytest.mark.parametrize(
    ("profile_html", "message"),
    [
        ("", "missing profile container"),
        (
            "<div id='profile_top'><h1>   </h1>"
            "<a href='/u/7'>Synthetic Author</a></div>",
            "parsed work title is empty",
        ),
        (
            "<div id='profile_top'><h1>Invented Work</h1>"
            "<a href='/u/7'>   </a></div>",
            "parsed author is empty",
        ),
    ],
)
def test_clean_html_rejects_missing_required_provenance(
    captured_page: CapturedPage,
    profile_html: str,
    message: str,
) -> None:
    with pytest.raises(ExtractionError, match=message):
        extract_chapter(
            f"{profile_html}<div id='storytext'><p>Invented chapter.</p></div>",
            captured_page,
        )


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


def test_chapter_one_emits_all_optional_metadata_labels_when_values_are_missing(
    captured_page: CapturedPage,
) -> None:
    raw = (
        _VALID_PROFILE_HTML
        + "<div id='storytext'><p>Invented chapter.</p></div>"
    )

    chapter_one = extract_chapter(raw, captured_page)
    provenance = BeautifulSoup(chapter_one.html, "html.parser").select_one(
        "header[data-role='provenance']"
    )

    assert provenance is not None
    assert [tag.get_text() for tag in provenance.select("p")] == [
        "Author: Synthetic Author",
        "Canonical source URL: https://www.fanfiction.net/s/1/1/invented-work",
        "Summary: ",
        "Rating: ",
        "Language: ",
        "Published: ",
        "Updated: ",
    ]

    chapter_two = extract_chapter(
        raw,
        captured_page.model_copy(
            update={
                "chapter": captured_page.chapter.model_copy(
                    update={"chapter_index": 2, "chapter_title": "Later"}
                )
            }
        ),
    )

    assert all(
        f"{label}:" not in chapter_two.html
        for label in ("Summary", "Rating", "Language", "Published", "Updated")
    )


def test_markdown_normalizes_line_endings_nbsp_and_blank_runs() -> None:
    clean_html = """<main data-role='story'><section data-block-kind='chapter-text'>
    <p>One&nbsp;two</p>\r\n\r\n\r\n<p>Three</p></section></main>"""

    text = html_to_markdown(clean_html)

    assert "One two" in text
    assert "\r" not in text
    assert "\n\n\n" not in text


def test_markdown_emits_empty_chapter_range_when_story_has_no_blocks() -> None:
    clean_html = "<main data-role='story'></main>"

    assert html_to_markdown(clean_html) == """<!-- BEGIN CHAPTER TEXT -->

<!-- END CHAPTER TEXT -->
"""


@pytest.mark.parametrize("tag", ("summary", "legend", "menu", "caption"))
def test_block_like_nested_siblings_are_separated_in_visible_text(
    captured_page: CapturedPage, tag: str
) -> None:
    result = extract_chapter(
        _VALID_PROFILE_HTML
        + (
            "<div id='storytext'><p>"
            f"<{tag}>Alpha.</{tag}><{tag}>Beta.</{tag}>"
            "<em>Gamma.</em><strong>Delta.</strong>"
            "</p></div>"
        ),
        captured_page,
    )

    assert result.blocks[0].text == "Alpha. Beta. Gamma.Delta."


def test_clean_html_preserves_allowed_empty_and_image_blocks_and_original_text(
    captured_page: CapturedPage,
) -> None:
    result = extract_chapter(
        _VALID_PROFILE_HTML
        + (
            "<div id='storytext'>"
            "Alpha  &lt;literal&gt;"
            "<hr data-tracking='discard'>"
            "<div class='empty'></div>"
            "<p id='also-empty'></p>"
            "<figure style='discard'><img src='/images/invented.png' "
            "alt='Invented diagram' onload='discard'></figure>"
            "<img src='https://tracker.invalid/pixel.png'>"
            "<img srcset='https://tracker.invalid/pixel-2x.png 2x'>"
            "<script src='https://tracker.invalid/story.js'></script>"
            "</div>"
        ),
        captured_page,
    )

    assert len(result.blocks) == 5
    assert [block.text for block in result.blocks] == [
        "Alpha <literal>",
        "",
        "",
        "",
        "",
    ]
    assert [block.sha256 for block in result.blocks[1:]] == [
        hashlib.sha256(b"").hexdigest()
    ] * 4
    story = BeautifulSoup(result.html, "html.parser").select_one(
        "main[data-role='story']"
    )
    assert story is not None
    rendered = story.select(":scope > section")
    assert rendered[0].decode_contents() == "<p>Alpha  &lt;literal&gt;</p>"
    assert [section.find().name for section in rendered[1:]] == [
        "hr",
        "div",
        "p",
        "figure",
    ]
    assert rendered[4].img is not None
    assert rendered[4].img["src"] == "/images/invented.png"
    assert "tracker.invalid" not in result.html


def test_clean_html_sanitizes_root_and_nested_subtrees_safely(
    captured_page: CapturedPage,
) -> None:
    result = extract_chapter(
        _VALID_PROFILE_HTML
        + """<div id="storytext"><p id="root-track" class="styled"
        style="color:red" onclick="discard()">Before
        <span data-track="discard" onmouseover="discard()">middle
        <form><div><label>control<input value="secret"></label></div></form>
        after <img src="https://tracker.invalid/pixel.png">
        <img src="/images/kept.png" alt="Kept" onload="discard()"></span></p></div>""",
        captured_page,
    )

    story_html = result.blocks[0].html
    assert "Before" in story_html
    assert "middle" in story_html
    assert "after" in story_html
    assert "control" not in story_html
    assert "<form" not in story_html
    assert "<input" not in story_html
    assert "tracker.invalid" not in story_html
    assert 'src="/images/kept.png"' in story_html
    assert 'alt="Kept"' in story_html
    for unsafe in ("root-track", "styled", "style=", "onclick=", "data-track", "onmouseover=", "onload="):
        assert unsafe not in story_html


def test_markdown_annotation_ranges_are_disjoint_and_keep_source_order(
    captured_page: CapturedPage,
) -> None:
    raw = (
        _VALID_PROFILE_HTML
        + "<div id='storytext'><p>Chapter before.</p><p>Invented note.</p>"
        "<p>Invented missing notice.</p><p>Chapter after.</p></div>"
    )
    captured_page.raw_html_path.write_text(raw, encoding="utf-8")
    annotations = ChapterAnnotations(
        author_note_block_sha256=[
            hashlib.sha256(b"Invented note.").hexdigest()
        ],
        missing_chapter_notice_block_sha256=[
            hashlib.sha256(b"Invented missing notice.").hexdigest()
        ],
    )

    text = html_to_markdown(build_clean_html(captured_page, annotations))

    assert text == """<!-- BEGIN CHAPTER TEXT -->

Chapter before.

<!-- END CHAPTER TEXT -->

<!-- BEGIN AUTHOR NOTE -->

Invented note.

<!-- END AUTHOR NOTE -->

<!-- BEGIN MISSING CHAPTER NOTICE -->

Invented missing notice.

<!-- END MISSING CHAPTER NOTICE -->

<!-- BEGIN CHAPTER TEXT -->

Chapter after.

<!-- END CHAPTER TEXT -->
"""


def test_chapter_one_metadata_uses_visible_fanfiction_net_variants(
    captured_page: CapturedPage,
) -> None:
    raw = """<div id="profile_top">
    <b>Invented Fallback Work</b>
    <a href="/u/7/synthetic-author">Synthetic Author</a>
    <div class="xcontrast_txt">An invented fallback summary.</div>
    <span>Rated: Fiction M - Spanish - Words: 1,234 -
    Published: Apr 4, 2020 - Updated: May 5, 2020 - id: 1</span>
    </div><div id="storytext"><p>Invented chapter.</p></div>"""

    result = extract_chapter(raw, captured_page)

    assert "Invented Fallback Work" in result.html
    assert "Summary: An invented fallback summary." in result.html
    assert "Rating: Fiction M" in result.html
    assert "Language: Spanish" in result.html
    assert "Published: Apr 4, 2020" in result.html
    assert "Updated: May 5, 2020" in result.html
    assert "Rating: Fiction M - Spanish" not in result.html

    adjacent_metadata = """<div id="profile_top">
    <h1>Invented Adjacent Metadata</h1>
    <a href="/u/7/synthetic-author">Synthetic Author</a>
    <p data-role="summary">Another invented summary.</p>
    <span>Rated: Fiction K+</span><span>Language: French</span>
    <span>Published: Jun 6, 2020</span><span>Updated: Jul 7, 2020</span>
    </div><div id="storytext"><p>Invented chapter.</p></div>"""

    adjacent_result = extract_chapter(adjacent_metadata, captured_page)

    assert "Rating: Fiction K+" in adjacent_result.html
    assert "Language: French" in adjacent_result.html
    assert "Published: Jun 6, 2020" in adjacent_result.html
    assert "Updated: Jul 7, 2020" in adjacent_result.html
    assert "Rating: Fiction K+Language" not in adjacent_result.html
