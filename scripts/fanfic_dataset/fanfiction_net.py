from __future__ import annotations

import re
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup, Tag

from .models import ChapterRef, SourceRecord, WorkDiscovery

STORY_SELECTORS = ("#storytext", "div.storytext")
PROFILE_SELECTORS = ("#profile_top", "div#profile_top")
CHAPTER_SELECTORS = (
    "select#chap_select option",
    "select[name='chapter'] option",
)

_METADATA_LABELS = (
    "Rated",
    "Language",
    "Chapters",
    "Words",
    "Published",
    "Updated",
    "id",
)
_METADATA_PREFIX = re.compile(
    r"^(?:Rated|Language|Chapters|Words|Published|Updated|id)\s*:",
    re.IGNORECASE,
)
_NATIVE_DOWNLOAD_TERMS = ("download", "epub", "pdf", "export")


class ExtractionError(ValueError):
    """Raised when public work metadata cannot be parsed unambiguously."""


class FanFictionNetAdapter:
    def discover(
        self, html: str, canonical_url: str, source: SourceRecord
    ) -> WorkDiscovery:
        return parse_fanfiction_net(html, canonical_url, source)


def parse_fanfiction_net(
    html: str, canonical_url: str, source: SourceRecord
) -> WorkDiscovery:
    soup = BeautifulSoup(html, "html.parser")
    _story_container(soup)
    profile = _first_match(soup, PROFILE_SELECTORS)
    if profile is None:
        raise ExtractionError("missing profile container")

    title = _work_title(profile)
    if not title:
        raise ExtractionError("parsed work title is empty")
    author = _author(profile)
    if not author:
        raise ExtractionError("parsed author is empty")

    source_work_id = _source_work_id(source)
    profile_text = " ".join(profile.stripped_strings)
    page_work_id = _label_value(profile_text, "id")
    if page_work_id is None or not page_work_id.isdigit():
        raise ExtractionError("page work ID is missing or non-numeric")
    if page_work_id != source_work_id:
        raise ExtractionError(
            f"page work ID {page_work_id} does not match source work ID "
            f"{source_work_id}"
        )

    displayed_chapter_count = _visible_chapter_count(profile_text)
    options = _first_matches(soup, CHAPTER_SELECTORS)
    if options:
        chapters = _chapters_from_options(options, canonical_url, source_work_id)
        if (
            displayed_chapter_count is not None
            and displayed_chapter_count != len(chapters)
        ):
            raise ExtractionError(
                "visible chapter count does not match selector inventory: "
                f"{displayed_chapter_count} != {len(chapters)}"
            )
    else:
        if displayed_chapter_count is not None and displayed_chapter_count > 1:
            raise ExtractionError(
                "missing chapter selector for multiple chapters: "
                f"{displayed_chapter_count}"
            )
        chapters = [
            ChapterRef(
                chapter_index=1,
                chapter_title=None,
                title_missing=True,
                chapter_url=canonical_url,
            )
        ]

    return WorkDiscovery(
        source_id=source.source_id,
        work_id=page_work_id,
        work_title=title,
        author=author,
        summary=_summary(profile),
        rating=_label_value(profile_text, "Rated"),
        language=_language(profile_text),
        displayed_word_count=_word_count(profile_text),
        published_date_displayed=_label_value(profile_text, "Published"),
        updated_date_displayed=_label_value(profile_text, "Updated"),
        native_download_url=_native_download_url(soup, canonical_url),
        chapters=chapters,
    )


def _story_container(soup: BeautifulSoup) -> Tag:
    matches: dict[int, Tag] = {}
    for selector in STORY_SELECTORS:
        for match in soup.select(selector):
            matches[id(match)] = match
    if len(matches) != 1:
        if not matches:
            raise ExtractionError("missing supported story container")
        raise ExtractionError("expected exactly one story container")
    return next(iter(matches.values()))


def _first_match(soup: BeautifulSoup, selectors: tuple[str, ...]) -> Tag | None:
    for selector in selectors:
        match = soup.select_one(selector)
        if match is not None:
            return match
    return None


def _first_matches(soup: BeautifulSoup, selectors: tuple[str, ...]) -> list[Tag]:
    for selector in selectors:
        matches = soup.select(selector)
        if matches:
            return matches
    return []


def _source_work_id(source: SourceRecord) -> str:
    match = re.match(r"^/s/(\d+)(?:/|$)", urlsplit(str(source.work_url)).path)
    if match is None:
        raise ExtractionError("source work URL has no numeric work ID")
    return match.group(1)


def _work_title(profile: Tag) -> str:
    heading = profile.find(["h1", "h2"])
    if heading is not None:
        return heading.get_text(" ", strip=True)

    for candidate in profile.find_all("b"):
        text = candidate.get_text(" ", strip=True)
        if text and not _METADATA_PREFIX.match(text):
            return text
    return ""


def _author(profile: Tag) -> str:
    author_link = profile.find("a", href=re.compile(r"/u/"))
    return author_link.get_text(" ", strip=True) if author_link is not None else ""


def _summary(profile: Tag) -> str:
    explicit = profile.select_one("[data-role='summary']")
    if explicit is not None:
        return explicit.get_text(" ", strip=True)

    for candidate in profile.find_all(["div", "p"]):
        classes = set(candidate.get("class", []))
        if "xcontrast_txt" not in classes:
            continue
        text = candidate.get_text(" ", strip=True)
        if text and not any(
            re.search(rf"\b{label}\s*:", text, re.IGNORECASE)
            for label in _METADATA_LABELS
        ):
            return text
    return ""


def _metadata_segments(text: str) -> list[str]:
    return [
        segment.strip()
        for segment in re.split(r"\s+(?:·|\||-)\s+", text)
        if segment.strip()
    ]


def _label_value(text: str, label: str) -> str | None:
    label_pattern = re.compile(rf"\b{re.escape(label)}\s*:\s*(.*)", re.IGNORECASE)
    for segment in _metadata_segments(text):
        match = label_pattern.search(segment)
        if match is not None:
            value = match.group(1).strip()
            return value or None

    following_label = "|".join(re.escape(item) for item in _METADATA_LABELS)
    fallback = re.search(
        rf"\b{re.escape(label)}\s*:\s*(.*?)"
        rf"(?=\s+\b(?:{following_label})\s*:|$)",
        text,
        re.IGNORECASE,
    )
    if fallback is None:
        return None
    value = fallback.group(1).strip(" ·|-")
    return value or None


def _language(text: str) -> str | None:
    explicit = _label_value(text, "Language")
    if explicit is not None:
        return explicit

    segments = _metadata_segments(text)
    for index, segment in enumerate(segments[:-1]):
        if re.search(r"\bRated\s*:", segment, re.IGNORECASE):
            candidate = segments[index + 1]
            if not _METADATA_PREFIX.match(candidate):
                return candidate
    return None


def _word_count(text: str) -> int | None:
    displayed = _label_value(text, "Words")
    if displayed is None:
        return None
    digits = displayed.replace(",", "").replace(" ", "")
    return int(digits) if digits.isdigit() else None


def _visible_chapter_count(text: str) -> int | None:
    displayed = _label_value(text, "Chapters")
    if displayed is None:
        return None
    digits = displayed.replace(",", "").replace(" ", "")
    if not digits.isdigit() or int(digits) < 1:
        raise ExtractionError(f"invalid visible chapter count: {displayed!r}")
    return int(digits)


def _chapters_from_options(
    options: list[Tag], canonical_url: str, work_id: str
) -> list[ChapterRef]:
    discovered: dict[int, ChapterRef] = {}
    for option in options:
        raw_value = str(option.get("value", "")).strip()
        if not raw_value.isdigit():
            raise ExtractionError(f"non-numeric chapter value: {raw_value!r}")
        chapter_index = int(raw_value)
        if chapter_index in discovered:
            raise ExtractionError(f"duplicate chapter value: {chapter_index}")

        chapter_title = _chapter_title(option.get_text(" ", strip=True), chapter_index)
        discovered[chapter_index] = ChapterRef(
            chapter_index=chapter_index,
            chapter_title=chapter_title,
            title_missing=chapter_title is None,
            chapter_url=_chapter_url(canonical_url, work_id, chapter_index),
        )

    indexes = sorted(discovered)
    if indexes != list(range(1, len(discovered) + 1)):
        raise ExtractionError(
            f"chapter values must be unique and consecutive from 1: {indexes}"
        )
    return [discovered[index] for index in indexes]


def _chapter_title(option_text: str, chapter_index: int) -> str | None:
    if option_text.strip() == str(chapter_index):
        return None
    title = re.sub(
        rf"^\s*{chapter_index}\.\s*",
        "",
        option_text,
        count=1,
    ).strip()
    return title or None


def _chapter_url(canonical_url: str, work_id: str, chapter_index: int) -> str:
    parsed = urlsplit(canonical_url)
    path_parts = [part for part in parsed.path.split("/") if part]
    slug = "/".join(path_parts[3:]) if len(path_parts) > 3 else ""
    path = f"/s/{work_id}/{chapter_index}"
    if slug:
        path = f"{path}/{slug}"
    return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def _native_download_url(soup: BeautifulSoup, canonical_url: str) -> str | None:
    for link in soup.find_all("a", href=True):
        accessible_parts = [
            link.get_text(" ", strip=True),
            str(link.get("href", "")),
            str(link.get("aria-label", "")),
            str(link.get("title", "")),
        ]
        for image in link.find_all("img"):
            accessible_parts.append(str(image.get("alt", "")))
        accessible = " ".join(accessible_parts).casefold()
        if any(term in accessible for term in _NATIVE_DOWNLOAD_TERMS):
            return urljoin(canonical_url, str(link["href"]))
    return None
