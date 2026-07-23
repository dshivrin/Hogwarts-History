"""Lossless, offline conversion of captured story containers to semantic HTML."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

from .fanfiction_net import (
    PROFILE_SELECTORS,
    STORY_SELECTORS,
    ExtractionError,
    _author,
    _first_match,
    _label_value,
    _language,
    _summary,
    _work_title,
)
from .models import CapturedPage


_DROP_TAGS = frozenset({"script", "style", "button", "input", "select", "textarea", "option", "form"})
_VISIBLE_BLOCK_TAGS = frozenset({
    "address", "article", "aside", "blockquote", "br", "dd", "details", "dialog",
    "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer", "h1", "h2",
    "h3", "h4", "h5", "h6", "header", "hgroup", "hr", "li", "main", "nav",
    "ol", "p", "pre", "search", "section", "table", "tbody", "td", "tfoot", "th",
    "thead", "tr", "ul", "caption", "colgroup", "legend", "menu", "summary",
})
_TEXT_BOUNDARY_TAGS = _VISIBLE_BLOCK_TAGS
_DIRECT_BLOCK_TAGS = _VISIBLE_BLOCK_TAGS - {"br"}
_TEXT_SPACE = re.compile(r"\s+")
_HASH = re.compile(r"^[0-9a-f]{64}$")


class AnnotationError(ValueError):
    """Raised when manual block annotations do not describe this chapter."""


@dataclass(frozen=True)
class ChapterAnnotations:
    author_note_block_sha256: list[str] = field(default_factory=list)
    missing_chapter_notice_block_sha256: list[str] = field(default_factory=list)
    reviewed_by: str | None = None
    reviewed_at_utc: str | None = None


@dataclass(frozen=True)
class StoryBlock:
    sha256: str
    text: str
    html: str


@dataclass(frozen=True)
class ExtractedChapter:
    html: str
    blocks: list[StoryBlock]


def extract_chapter(raw_html: str | bytes, page: CapturedPage) -> ExtractedChapter:
    """Extract all direct story-container blocks and render unannotated semantic HTML."""
    soup = BeautifulSoup(_decode_html(raw_html), "html.parser")
    blocks = _story_blocks(_story_container(soup))
    return ExtractedChapter(
        html=_render_semantic_html(soup, page, blocks, ChapterAnnotations()),
        blocks=blocks,
    )


def build_clean_html(page: CapturedPage, annotations: ChapterAnnotations) -> str:
    """Build annotated semantic HTML from a persisted raw main-document response."""
    raw_html = page.raw_html_path.read_bytes()
    soup = BeautifulSoup(_decode_html(raw_html), "html.parser")
    blocks = _story_blocks(_story_container(soup))
    _validate_annotations(blocks, annotations)
    return _render_semantic_html(soup, page, blocks, annotations)


def load_chapter_annotations(path: Path, chapter_index: int) -> ChapterAnnotations:
    """Load the exact hash-addressed annotations.json record for one chapter."""
    data = json.loads(path.read_text("utf-8"))
    key = f"chapter-{chapter_index:03d}"
    record = data.get(key, {})
    if not isinstance(record, dict):
        raise AnnotationError(f"annotation record {key} must be an object")
    permitted = {
        "author_note_block_sha256",
        "missing_chapter_notice_block_sha256",
        "reviewed_by",
        "reviewed_at_utc",
    }
    unknown = set(record) - permitted
    if unknown:
        raise AnnotationError(f"unknown annotation fields: {sorted(unknown)}")
    return ChapterAnnotations(
        author_note_block_sha256=_hash_list(record, "author_note_block_sha256"),
        missing_chapter_notice_block_sha256=_hash_list(
            record, "missing_chapter_notice_block_sha256"
        ),
        reviewed_by=_optional_string(record, "reviewed_by"),
        reviewed_at_utc=_optional_string(record, "reviewed_at_utc"),
    )


def _decode_html(raw_html: str | bytes) -> str:
    return raw_html if isinstance(raw_html, str) else raw_html.decode("utf-8", errors="replace")


def _story_container(soup: BeautifulSoup) -> Tag:
    matches: dict[int, Tag] = {}
    for selector in STORY_SELECTORS:
        for node in soup.select(selector):
            matches[id(node)] = node
    if len(matches) != 1:
        raise ExtractionError("missing supported story container" if not matches else "expected exactly one story container")
    return next(iter(matches.values()))


def _story_blocks(container: Tag) -> list[StoryBlock]:
    blocks: list[StoryBlock] = []
    phrasing_parts: list[NavigableString | Tag] = []
    for child in container.children:
        if isinstance(child, Comment):
            continue
        if isinstance(child, NavigableString):
            phrasing_parts.append(child)
            continue
        if not isinstance(child, Tag) or child.name in _DROP_TAGS:
            continue
        if _is_remote_image(child):
            continue
        if child.name not in _DIRECT_BLOCK_TAGS:
            phrasing_parts.append(child)
            continue
        if phrasing_parts:
            blocks.extend(_phrasing_block(phrasing_parts))
            phrasing_parts.clear()
        copied = deepcopy(child)
        _sanitize_story_node(copied)
        text = _normalized_visible_text(copied)
        blocks.append(StoryBlock(_sha(text), text, str(copied)))
    if phrasing_parts:
        blocks.extend(_phrasing_block(phrasing_parts))
    return blocks


def _phrasing_block(parts: list[NavigableString | Tag]) -> list[StoryBlock]:
    if not any(isinstance(part, Tag) for part in parts) and not _normalized_visible_text(
        "".join(str(part) for part in parts)
    ):
        return []
    fragment = BeautifulSoup("", "html.parser")
    paragraph = fragment.new_tag("p")
    for part in parts:
        paragraph.append(deepcopy(part))
    _sanitize_story_node(paragraph)
    text = _normalized_visible_text(paragraph)
    return [StoryBlock(_sha(text), text, str(paragraph))]


def _sanitize_story_node(node: Tag) -> None:
    for comment in node.find_all(string=lambda value: isinstance(value, Comment)):
        comment.extract()
    for descendant in reversed(node.find_all(True)):
        if descendant.name in _DROP_TAGS or _is_remote_image(descendant):
            descendant.decompose()
    for descendant in [node, *node.find_all(True)]:
        allowed = {"href", "title"} if descendant.name == "a" else set()
        if descendant.name == "img":
            allowed = {"src", "alt", "title"}
        for attribute in list(descendant.attrs):
            if attribute not in allowed:
                del descendant.attrs[attribute]


def _is_remote_image(node: Tag) -> bool:
    if node.name != "img":
        return False
    source_attributes = (
        node.get("src", ""),
        node.get("srcset", ""),
        node.get("data-src", ""),
        node.get("data-original", ""),
        node.get("data-lazy-src", ""),
    )
    return any(
        re.search(r"(?:https?:)?//", str(source), re.IGNORECASE)
        for source in source_attributes
    )


def _normalized_visible_text(node: Tag | str) -> str:
    if isinstance(node, Tag):
        text = "".join(_visible_text_parts(node))
    else:
        text = node
    return _TEXT_SPACE.sub(" ", text.replace("\xa0", " ")).strip()


def _visible_text_parts(node: Tag):
    for child in node.children:
        if isinstance(child, Comment):
            continue
        if isinstance(child, NavigableString):
            yield str(child)
            continue
        if not isinstance(child, Tag):
            continue
        is_boundary = child.name in _TEXT_BOUNDARY_TAGS
        if is_boundary:
            yield " "
        yield from _visible_text_parts(child)
        if is_boundary:
            yield " "


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_annotations(blocks: list[StoryBlock], annotations: ChapterAnnotations) -> None:
    known = {block.sha256 for block in blocks}
    author = set(annotations.author_note_block_sha256)
    missing = set(annotations.missing_chapter_notice_block_sha256)
    for value in author | missing:
        if not _HASH.fullmatch(value):
            raise AnnotationError(f"invalid block hash: {value!r}")
        if value not in known:
            raise AnnotationError(f"unknown block hash: {value}")
    overlap = author & missing
    if overlap:
        raise AnnotationError(f"block hashes have multiple annotations: {sorted(overlap)}")


def _render_semantic_html(
    source_soup: BeautifulSoup,
    page: CapturedPage,
    blocks: list[StoryBlock],
    annotations: ChapterAnnotations,
) -> str:
    metadata = _profile_metadata(source_soup)
    output = BeautifulSoup("<!doctype html><html><head><meta charset='utf-8'></head><body></body></html>", "html.parser")
    head = output.head
    assert head is not None
    title = output.new_tag("title")
    title.string = f"{metadata['work_title']} — {page.chapter.chapter_title or 'Chapter ' + str(page.chapter.chapter_index)}"
    head.append(title)
    body = output.body
    assert body is not None
    provenance = output.new_tag("header", attrs={"data-role": "provenance"})
    _append_text_tag(output, provenance, "h1", metadata["work_title"])
    _append_text_tag(output, provenance, "p", f"Author: {metadata['author']}")
    _append_text_tag(output, provenance, "p", f"Canonical source URL: {page.final_url}")
    _append_text_tag(output, provenance, "h2", f"Chapter {page.chapter.chapter_index}: {page.chapter.chapter_title or 'Untitled'}")
    if page.chapter.chapter_index == 1:
        for label, value in (
            ("Summary", metadata["summary"]), ("Rating", metadata["rating"]),
            ("Language", metadata["language"]), ("Published", metadata["published"]),
            ("Updated", metadata["updated"]),
        ):
            _append_text_tag(output, provenance, "p", f"{label}: {value}")
    body.append(provenance)
    story = output.new_tag("main", attrs={"data-role": "story"})
    author_hashes = set(annotations.author_note_block_sha256)
    missing_hashes = set(annotations.missing_chapter_notice_block_sha256)
    for block in blocks:
        kind = "author-note" if block.sha256 in author_hashes else "missing-chapter-notice" if block.sha256 in missing_hashes else "chapter-text"
        wrapper = output.new_tag("section", attrs={"data-block-kind": kind, "data-sha256": block.sha256})
        fragment = BeautifulSoup(block.html, "html.parser")
        for child in list(fragment.contents):
            wrapper.append(child)
        story.append(wrapper)
    body.append(story)
    return str(output)


def _append_text_tag(soup: BeautifulSoup, parent: Tag, name: str, value: str) -> None:
    tag = soup.new_tag(name)
    tag.string = value
    parent.append(tag)


def _profile_metadata(soup: BeautifulSoup) -> dict[str, str]:
    profile = _first_match(soup, PROFILE_SELECTORS)
    if profile is None:
        raise ExtractionError("missing profile container")
    work_title = _work_title(profile)
    if not work_title:
        raise ExtractionError("parsed work title is empty")
    author = _author(profile)
    if not author:
        raise ExtractionError("parsed author is empty")
    profile_text = " ".join(profile.stripped_strings)
    return {
        "work_title": work_title,
        "author": author,
        "summary": _summary(profile),
        "rating": _label_value(profile_text, "Rated") or "",
        "language": _language(profile_text) or "",
        "published": _label_value(profile_text, "Published") or "",
        "updated": _label_value(profile_text, "Updated") or "",
    }


def _hash_list(record: dict[str, object], name: str) -> list[str]:
    value = record.get(name, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise AnnotationError(f"{name} must be a list of hashes")
    return value


def _optional_string(record: dict[str, object], name: str) -> str | None:
    value = record.get(name)
    if value is not None and not isinstance(value, str):
        raise AnnotationError(f"{name} must be a string")
    return value
