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
    for block in story.select(":scope > section[data-block-kind]"):
        converted = _normalize(markdownify(block.decode_contents(), heading_style="ATX"))
        if not converted:
            continue
        kind = str(block.get("data-block-kind"))
        if kind == "author-note":
            chunks.extend(("<!-- BEGIN AUTHOR NOTE -->", converted, "<!-- END AUTHOR NOTE -->"))
        elif kind == "missing-chapter-notice":
            chunks.extend(("<!-- BEGIN MISSING CHAPTER NOTICE -->", converted, "<!-- END MISSING CHAPTER NOTICE -->"))
        else:
            chunks.append(converted)
    text = "\n\n".join(("<!-- BEGIN CHAPTER TEXT -->", "\n\n".join(chunks), "<!-- END CHAPTER TEXT -->"))
    return _normalize(text).rstrip("\n") + "\n"


def _normalize(value: str) -> str:
    value = value.replace("\xa0", " ").replace("\r\n", "\n").replace("\r", "\n")
    value = "\n".join(line.rstrip() for line in value.split("\n"))
    return _BLANK_RUN.sub("\n\n", value).strip()
