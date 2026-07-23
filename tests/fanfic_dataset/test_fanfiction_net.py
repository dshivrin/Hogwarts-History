from __future__ import annotations

from pathlib import Path

import pytest

from scripts.fanfic_dataset.discover import adapter_for
from scripts.fanfic_dataset.fanfiction_net import (
    ExtractionError,
    FanFictionNetAdapter,
    parse_fanfiction_net,
)
from scripts.fanfic_dataset.models import SourceRecord


@pytest.fixture
def single_html() -> str:
    return _fixture("fanfiction-net-single.html")


@pytest.fixture
def multi_html() -> str:
    return _fixture("fanfiction-net-multi.html")


@pytest.fixture
def source() -> SourceRecord:
    return SourceRecord(
        source_id="HAH-FAN-001",
        work_title="Invented Multi Work",
        author="Synthetic Author",
        platform="fanfiction.net",
        work_url="https://www.fanfiction.net/s/1/1/invented-work",
        expected_available_chapter_count=3,
        status="core",
    )


def test_parser_discovers_chapters_in_numeric_order(multi_html, source):
    work = parse_fanfiction_net(multi_html, str(source.work_url), source)
    assert [chapter.chapter_index for chapter in work.chapters] == [1, 2, 3]
    assert [chapter.chapter_title for chapter in work.chapters] == [
        "Contents",
        "Founders",
        "Castle",
    ]


def test_parser_rejects_missing_story_container(single_html, source):
    html = single_html.replace('id="storytext"', 'id="missing"')
    with pytest.raises(ExtractionError, match="story container"):
        parse_fanfiction_net(html, str(source.work_url), source)


def test_parser_extracts_visible_label_metadata(multi_html, source) -> None:
    work = parse_fanfiction_net(multi_html, str(source.work_url), source)

    assert work.work_id == "1"
    assert work.work_title == "Invented Multi Work"
    assert work.author == "Synthetic Author"
    assert work.summary == "Another invented summary for deterministic parser tests."
    assert work.rating == "Fiction T"
    assert work.language == "English"
    assert work.displayed_word_count == 1234
    assert work.published_date_displayed == "Feb 2, 2020"
    assert work.updated_date_displayed == "Mar 3, 2020"


def test_parser_rejects_page_work_id_mismatch(multi_html, source) -> None:
    html = multi_html.replace("id: 1", "id: 999")
    with pytest.raises(ExtractionError, match="work ID"):
        parse_fanfiction_net(html, str(source.work_url), source)


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("<h1>Invented Single Work</h1>", "<h1>   </h1>", "work title"),
        (
            '<a href="/u/42/Synthetic-Author">Synthetic Author</a>',
            '<a href="/u/42/Synthetic-Author">   </a>',
            "author",
        ),
    ],
)
def test_parser_rejects_empty_required_identity_fields(
    single_html, source, old: str, new: str, message: str
) -> None:
    html = single_html.replace(old, new)
    with pytest.raises(ExtractionError, match=message):
        parse_fanfiction_net(html, str(source.work_url), source)


def test_parser_rejects_ambiguous_story_containers(single_html, source) -> None:
    html = single_html.replace(
        '<div id="storytext">',
        '<div id="storytext"><div class="storytext">'
        "<p>Second synthetic paragraph for parser testing.</p></div>",
    )
    with pytest.raises(ExtractionError, match="exactly one story container"):
        parse_fanfiction_net(html, str(source.work_url), source)


def test_parser_marks_only_empty_chapter_titles_missing(multi_html, source) -> None:
    html = multi_html.replace("2. Founders", "2.   ")
    work = parse_fanfiction_net(html, str(source.work_url), source)

    assert work.chapters[0].title_missing is False
    assert work.chapters[1].chapter_title is None
    assert work.chapters[1].title_missing is True
    assert work.chapters[2].title_missing is False


def test_parser_builds_single_chapter_from_canonical_url(single_html, source) -> None:
    work = parse_fanfiction_net(single_html, str(source.work_url), source)

    assert len(work.chapters) == 1
    assert work.chapters[0].chapter_index == 1
    assert work.chapters[0].chapter_title is None
    assert work.chapters[0].title_missing is True
    assert str(work.chapters[0].chapter_url) == str(source.work_url)


@pytest.mark.parametrize(
    "link",
    [
        '<a href="/tools/file.bin" aria-label="Download story">Get file</a>',
        '<a href="/tools/work.epub">Get file</a>',
        '<a href="/tools/file.bin" title="PDF export">Get file</a>',
    ],
)
def test_parser_returns_native_download_for_operator_review(
    single_html, source, link: str
) -> None:
    html = single_html.replace("</body>", f"{link}</body>")
    work = parse_fanfiction_net(html, str(source.work_url), source)
    assert work.native_download_url is not None
    assert str(work.native_download_url).startswith("https://www.fanfiction.net/tools/")


@pytest.mark.parametrize(
    ("options", "message"),
    [
        (
            '<option value="1">1. One</option>'
            '<option value="1">1. Duplicate</option>',
            "duplicate",
        ),
        (
            '<option value="one">1. One</option>',
            "non-numeric",
        ),
        (
            '<option value="1">1. One</option>'
            '<option value="3">3. Three</option>',
            "consecutive",
        ),
    ],
)
def test_parser_rejects_invalid_chapter_values(
    single_html, source, options: str, message: str
) -> None:
    html = single_html.replace(
        '<div id="storytext">',
        f'<select id="chap_select">{options}</select><div id="storytext">',
    )
    with pytest.raises(ExtractionError, match=message):
        parse_fanfiction_net(html, str(source.work_url), source)


def test_parser_tolerates_missing_optional_metadata(single_html, source) -> None:
    html = single_html.replace(
        "Rated: Fiction K+ · Language: English · Words: 321 ·\n"
        "        Published: Jan 1, 2020 · ",
        "",
    )
    work = parse_fanfiction_net(html, str(source.work_url), source)
    assert work.rating is None
    assert work.language is None
    assert work.displayed_word_count is None
    assert work.published_date_displayed is None
    assert work.updated_date_displayed is None


def test_platform_adapter_delegates_to_pure_parser(single_html, source) -> None:
    adapter = adapter_for(source)
    assert isinstance(adapter, FanFictionNetAdapter)
    assert adapter.discover(single_html, str(source.work_url), source).work_id == "1"


def _fixture(name: str) -> str:
    path = Path(__file__).with_name("fixtures") / name
    return path.read_text(encoding="utf-8")
