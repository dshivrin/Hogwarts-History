"""Assemble rendered chapters into a canonical complete-work PDF."""

from __future__ import annotations

from html import escape
import os
from pathlib import Path
import re
import tempfile
import unicodedata

import fitz

from .models import WorkDiscovery
from .render_pdf import _render_local_html_sync


def canonical_complete_pdf_name(discovery: WorkDiscovery) -> str:
    """Return the required stable complete-work PDF filename."""
    title_slug = _ascii_slug(discovery.work_title, fallback="untitled")
    author_slug = _ascii_slug(discovery.author, fallback="unknown-author")
    return f"{discovery.source_id}__{title_slug}__{author_slug}.pdf"


def merge_work_pdf(
    discovery: WorkDiscovery,
    chapter_pdfs: list[Path],
    output_path: Path,
) -> None:
    """Merge front matter and ordered chapters, then validate and replace."""
    _validate_inputs(discovery, chapter_pdfs, output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chapter_page_counts = [_page_count(path) for path in chapter_pdfs]

    front_html = _temporary_path(output_path.parent, ".front-matter-", ".html")
    front_pdf = _temporary_path(output_path.parent, ".front-matter-", ".pdf")
    merged_pdf = _temporary_path(
        output_path.parent,
        f".{output_path.name}.",
        ".tmp.pdf",
    )
    try:
        front_page_count = _render_front_matter(
            discovery,
            chapter_page_counts,
            front_html,
            front_pdf,
        )
        expected_page_count = front_page_count + sum(chapter_page_counts)
        bookmarks: list[list[int | str]] = []
        with fitz.open() as complete:
            with fitz.open(front_pdf) as front:
                complete.insert_pdf(front)
            for chapter, chapter_pdf in zip(
                discovery.chapters,
                chapter_pdfs,
                strict=True,
            ):
                chapter_start = complete.page_count + 1
                title = _chapter_title(
                    chapter.chapter_index,
                    chapter.chapter_title,
                )
                bookmarks.append([1, title, chapter_start])
                with fitz.open(chapter_pdf) as rendered_chapter:
                    complete.insert_pdf(rendered_chapter)
            complete.set_toc(bookmarks)
            _add_global_page_numbers(complete)
            complete.set_metadata(
                {
                    "title": discovery.work_title,
                    "author": discovery.author,
                    "subject": (
                        "Fan-created, non-canon material captured for private "
                        "comparative research."
                    ),
                }
            )
            complete.save(
                merged_pdf,
                garbage=4,
                deflate=True,
                no_new_id=True,
            )

        _validate_complete_pdf(
            merged_pdf,
            expected_page_count=expected_page_count,
            expected_bookmarks=bookmarks,
        )
        os.replace(merged_pdf, output_path)
    finally:
        front_html.unlink(missing_ok=True)
        front_pdf.unlink(missing_ok=True)
        merged_pdf.unlink(missing_ok=True)


def _ascii_slug(value: str, *, fallback: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return slug or fallback


def _validate_inputs(
    discovery: WorkDiscovery,
    chapter_pdfs: list[Path],
    output_path: Path,
) -> None:
    if output_path.name != canonical_complete_pdf_name(discovery):
        raise ValueError(
            "complete PDF output must use canonical filename "
            f"{canonical_complete_pdf_name(discovery)!r}"
        )
    if len(chapter_pdfs) != len(discovery.chapters):
        raise ValueError("chapter PDF count does not match discovery")
    indexes = [chapter.chapter_index for chapter in discovery.chapters]
    if indexes != sorted(indexes) or len(indexes) != len(set(indexes)):
        raise ValueError("discovery chapters must be in unique numeric order")
    for path in chapter_pdfs:
        if path.suffix.lower() != ".pdf" or not path.is_file():
            raise ValueError(f"chapter PDF does not exist: {path}")


def _page_count(path: Path) -> int:
    try:
        with fitz.open(path) as document:
            if document.page_count < 1:
                raise ValueError(f"chapter PDF has no pages: {path}")
            return document.page_count
    except fitz.FileDataError as error:
        raise ValueError(f"chapter PDF is invalid: {path}") from error


def _render_front_matter(
    discovery: WorkDiscovery,
    chapter_page_counts: list[int],
    html_path: Path,
    pdf_path: Path,
) -> int:
    assumed_front_pages = 2
    for _ in range(4):
        starts = _chapter_start_pages(assumed_front_pages, chapter_page_counts)
        html_path.write_text(
            _front_matter_html(discovery, starts),
            encoding="utf-8",
        )
        _render_local_html_sync(html_path, pdf_path)
        actual_front_pages = _page_count(pdf_path)
        if actual_front_pages == assumed_front_pages:
            return actual_front_pages
        assumed_front_pages = actual_front_pages
    raise ValueError("front-matter pagination did not stabilize")


def _chapter_start_pages(
    front_page_count: int,
    chapter_page_counts: list[int],
) -> list[int]:
    starts: list[int] = []
    next_page = front_page_count + 1
    for page_count in chapter_page_counts:
        starts.append(next_page)
        next_page += page_count
    return starts


def _front_matter_html(
    discovery: WorkDiscovery,
    chapter_start_pages: list[int],
) -> str:
    metadata = [
        ("Source ID", discovery.source_id),
        ("Work ID", discovery.work_id),
        ("Author", discovery.author),
        ("Rating", discovery.rating or "Not displayed"),
        ("Language", discovery.language or "Not displayed"),
        (
            "Displayed word count",
            str(discovery.displayed_word_count)
            if discovery.displayed_word_count is not None
            else "Not displayed",
        ),
        ("Published", discovery.published_date_displayed or "Not displayed"),
        ("Updated", discovery.updated_date_displayed or "Not displayed"),
    ]
    metadata_html = "".join(
        f"<dt>{escape(label)}</dt><dd>{escape(value)}</dd>"
        for label, value in metadata
    )
    toc_html = "".join(
        (
            "<li><span>"
            f"{escape(_chapter_title(chapter.chapter_index, chapter.chapter_title))}"
            "</span><span class=\"leader\"></span>"
            f"<span class=\"page-number\">{page_number}</span></li>"
        )
        for chapter, page_number in zip(
            discovery.chapters,
            chapter_start_pages,
            strict=True,
        )
    )
    summary = escape(discovery.summary or "No summary displayed.")
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{escape(discovery.work_title)} - Complete Work</title>
  <style>
    @page {{ size: A4; }}
    body {{ font-family: Georgia, "Times New Roman", Times, serif; }}
    .provenance {{ min-height: 225mm; }}
    .eyebrow {{ font-size: 9pt; letter-spacing: .12em; text-transform: uppercase; }}
    h1 {{ font-size: 28pt; margin: 24mm 0 5mm; }}
    .notice {{ border-top: 1px solid #777; border-bottom: 1px solid #777;
               margin: 10mm 0; padding: 5mm 0; }}
    dl {{ display: grid; grid-template-columns: 42mm 1fr; gap: 2mm 5mm; }}
    dt {{ font-weight: bold; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    .summary {{ margin-top: 8mm; }}
    .toc {{ break-before: page; }}
    .toc h2 {{ font-size: 22pt; margin: 0 0 10mm; }}
    .toc ol {{ list-style: none; margin: 0; padding: 0; }}
    .toc li {{ align-items: baseline; break-inside: avoid; display: flex;
               gap: 3mm; margin: 0 0 4mm; }}
    .leader {{ border-bottom: 1px dotted #777; flex: 1; }}
    .page-number {{ min-width: 10mm; text-align: right; }}
  </style>
</head>
<body>
  <section class="provenance">
    <p class="eyebrow">Research reference copy</p>
    <h1>{escape(discovery.work_title)}</h1>
    <p class="notice">Fan-created, non-canon material captured for private comparative research.</p>
    <dl>{metadata_html}</dl>
    <div class="summary"><h2>Summary</h2><p>{summary}</p></div>
  </section>
  <section class="toc">
    <h2>Contents</h2>
    <ol>{toc_html}</ol>
  </section>
</body>
</html>
"""


def _chapter_title(index: int, title: str | None) -> str:
    return title or f"Chapter {index}"


def _add_global_page_numbers(document: fitz.Document) -> None:
    for number, page in enumerate(document, start=1):
        footer = fitz.Rect(
            0,
            page.rect.height - 42,
            page.rect.width,
            page.rect.height - 18,
        )
        available = page.insert_textbox(
            footer,
            str(number),
            fontsize=9,
            fontname="tiro",
            align=fitz.TEXT_ALIGN_CENTER,
            overlay=True,
        )
        if available < 0:
            raise ValueError(f"page number did not fit on page {number}")


def _validate_complete_pdf(
    path: Path,
    *,
    expected_page_count: int,
    expected_bookmarks: list[list[int | str]],
) -> None:
    with fitz.open(path) as document:
        if document.page_count != expected_page_count:
            raise ValueError(
                "complete PDF page count mismatch: "
                f"expected {expected_page_count}, got {document.page_count}"
            )
        toc = document.get_toc()
        if len(toc) != len(expected_bookmarks):
            raise ValueError(
                "complete PDF bookmark count mismatch: "
                f"expected {len(expected_bookmarks)}, got {len(toc)}"
            )
        if [item[:3] for item in toc] != expected_bookmarks:
            raise ValueError("complete PDF bookmarks do not match chapter inventory")


def _temporary_path(directory: Path, prefix: str, suffix: str) -> Path:
    descriptor, name = tempfile.mkstemp(
        prefix=prefix,
        suffix=suffix,
        dir=directory,
    )
    os.close(descriptor)
    path = Path(name)
    path.unlink()
    return path
