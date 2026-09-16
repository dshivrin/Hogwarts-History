"""Mechanical Markdown normalization for semantic chapter HTML."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag
from markdownify import markdownify


_BLANK_RUN = re.compile(r"\n{3,}")


def html_to_markdown(clean_html: str) -> str:
    """Convert only semantic story blocks and add visible classification markers."""
    soup = BeautifulSoup(clean_html, "html.parser")
    story = soup.select_one("main[data-role='story']")
    if story is None:
        raise ValueError("clean HTML has no semantic story section")
    chunks: list[str] = []
    chapter_blocks: list[str] = []
    chapter_block_seen = False

    def close_chapter_text() -> None:
        nonlocal chapter_block_seen
        if not chapter_block_seen:
            return
        chunks.append(
            "\n\n".join(
                (
                    "<!-- BEGIN CHAPTER TEXT -->",
                    "\n\n".join(chapter_blocks),
                    "<!-- END CHAPTER TEXT -->",
                )
            )
        )
        chapter_blocks.clear()
        chapter_block_seen = False

    for block in story.select(":scope > section[data-block-kind]"):
        converted = _normalize(markdownify(block.decode_contents(), heading_style="ATX"))
        kind = str(block.get("data-block-kind"))
        if kind == "chapter-text":
            chapter_block_seen = True
            if converted:
                chapter_blocks.append(converted)
            continue
        close_chapter_text()
        if kind == "author-note":
            markers = ("<!-- BEGIN AUTHOR NOTE -->", "<!-- END AUTHOR NOTE -->")
        elif kind == "missing-chapter-notice":
            markers = (
                "<!-- BEGIN MISSING CHAPTER NOTICE -->",
                "<!-- END MISSING CHAPTER NOTICE -->",
            )
        else:
            raise ValueError(f"unknown semantic story block kind: {kind}")
        chunks.append("\n\n".join((markers[0], converted, markers[1])))
    close_chapter_text()
    if not chunks:
        chunks.append(
            "\n\n".join(
                ("<!-- BEGIN CHAPTER TEXT -->", "<!-- END CHAPTER TEXT -->")
            )
        )
    text = "\n\n".join(chunks)
    return _normalize(text).rstrip("\n") + "\n"


def _normalize(value: str) -> str:
    value = value.replace("\xa0", " ").replace("\r\n", "\n").replace("\r", "\n")
    value = "\n".join(line.rstrip() for line in value.split("\n"))
    return _BLANK_RUN.sub("\n\n", value).strip()
