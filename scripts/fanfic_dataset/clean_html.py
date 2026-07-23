"""Lossless, offline conversion of captured story containers to semantic HTML."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup, NavigableString, Tag

from .fanfiction_net import ExtractionError, STORY_SELECTORS
from .models import CapturedPage


_DROP_TAGS = frozenset({"script", "style", "button", "input", "select", "textarea", "option", "form"})
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
    text_parts: list[str] = []
    for child in container.children:
        if isinstance(child, NavigableString):
            text_parts.append(str(child))
            continue
        if not isinstance(child, Tag) or child.name in _DROP_TAGS:
            continue
        if text_parts:
            blocks.extend(_text_block("".join(text_parts)))
            text_parts.clear()
        copied = deepcopy(child)
        _sanitize_story_node(copied)
        text = _normalized_visible_text(copied)
        if text:
            blocks.append(StoryBlock(_sha(text), text, str(copied)))
    if text_parts:
        blocks.extend(_text_block("".join(text_parts)))
    return blocks


def _text_block(raw_text: str) -> list[StoryBlock]:
    text = _normalized_visible_text(raw_text)
    if not text:
        return []
    escaped = BeautifulSoup("", "html.parser").new_string(text)
    return [StoryBlock(_sha(text), text, f"<p>{escaped}</p>")]


def _sanitize_story_node(node: Tag) -> None:
    for descendant in list(node.find_all(True)):
        if descendant.name in _DROP_TAGS or descendant.name == "img":
            descendant.decompose()
            continue
        allowed = {"href", "title"} if descendant.name == "a" else set()
        for attribute in list(descendant.attrs):
            if attribute not in allowed:
                del descendant.attrs[attribute]


def _normalized_visible_text(node: Tag | str) -> str:
    if isinstance(node, Tag):
        # Joining text nodes without a synthetic separator preserves punctuation
        # adjacent to inline markup (for example, ``<strong>word</strong>.``).
        text = node.get_text("", strip=False)
    else:
        text = node
    return _TEXT_SPACE.sub(" ", text.replace("\xa0", " ")).strip()


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
            if value:
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
    profile = soup.select_one("#profile_top, div#profile_top")
    if profile is None:
        return {key: "" for key in ("work_title", "author", "summary", "rating", "language", "published", "updated")}
    title = profile.find(["h1", "h2"])
    author = profile.find("a", href=re.compile(r"/u/"))
    summary = profile.select_one("[data-role='summary']")
    profile_text = _normalized_visible_text(profile)
    return {
        "work_title": _normalized_visible_text(title) if title else "",
        "author": _normalized_visible_text(author) if author else "",
        "summary": _normalized_visible_text(summary) if summary else "",
        "rating": _label_value(profile_text, "Rated"),
        "language": _label_value(profile_text, "Language"),
        "published": _label_value(profile_text, "Published"),
        "updated": _label_value(profile_text, "Updated"),
    }


def _label_value(text: str, label: str) -> str:
    labels = "Rated|Language|Chapters|Words|Published|Updated|id"
    found = re.search(rf"\b{re.escape(label)}\s*:\s*(.*?)(?=\s*(?:·|\|)\s*(?:{labels})\s*:|$)", text, re.IGNORECASE)
    return found.group(1).strip() if found else ""


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
