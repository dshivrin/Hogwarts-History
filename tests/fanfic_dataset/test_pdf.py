from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
import time

import fitz
import pytest

from scripts.fanfic_dataset.merge_pdf import (
    canonical_complete_pdf_name,
    merge_work_pdf,
)
from scripts.fanfic_dataset.models import ChapterRef, WorkDiscovery
from scripts.fanfic_dataset.render_pdf import render_chapter_pdf


def _write_chapter(path: Path, title: str, prose: str) -> None:
    path.write_text(
        f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>{title}</title></head>
<body>
  <header data-role="provenance"><h1>{title}</h1></header>
  <main data-role="story">
    <section data-block-kind="chapter-text"><p>{prose}</p></section>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def _synthetic_discovery() -> WorkDiscovery:
    return WorkDiscovery(
        source_id="HAH-FAN-999",
        work_id="999",
        work_title="Synthetic Complete Work",
        author="Invented Researcher",
        summary="An entirely invented work used to verify local PDF assembly.",
        rating="Fiction T",
        language="English",
        displayed_word_count=18,
        published_date_displayed="Jan 1, 2020",
        updated_date_displayed="Jan 2, 2020",
        chapters=[
            ChapterRef(
                chapter_index=1,
                chapter_title="Synthetic Chapter One",
                chapter_url="https://example.invalid/s/999/1/synthetic",
            ),
            ChapterRef(
                chapter_index=2,
                chapter_title="Synthetic Chapter Two",
                chapter_url="https://example.invalid/s/999/2/synthetic",
            ),
        ],
    )


def test_renders_and_assembles_complete_pdf_with_provenance_toc_and_global_numbers(
    tmp_path: Path,
) -> None:
    discovery = _synthetic_discovery()
    chapter_pdfs: list[Path] = []
    for index, (title, prose) in enumerate(
        (
            ("Synthetic Chapter One", "A paper owl crossed the invented archive."),
            ("Synthetic Chapter Two", "The imaginary shelves settled into silence."),
        ),
        start=1,
    ):
        html_path = tmp_path / f"chapter-{index:03d}.html"
        pdf_path = tmp_path / f"chapter-{index:03d}.pdf"
        _write_chapter(html_path, title, prose)
        asyncio.run(render_chapter_pdf(html_path, pdf_path))
        chapter_pdfs.append(pdf_path)

    complete_pdf = tmp_path / canonical_complete_pdf_name(discovery)
    merge_work_pdf(discovery, chapter_pdfs, complete_pdf)

    with fitz.open(complete_pdf) as document:
        text = "\n".join(page.get_text() for page in document)
        assert (
            "Fan-created, non-canon material captured for private comparative research."
            in text
        )
        assert "Synthetic Chapter One" in text
        assert "Synthetic Chapter Two" in text
        assert [item[1] for item in document.get_toc()] == [
            "Synthetic Chapter One",
            "Synthetic Chapter Two",
        ]
        assert document[-1].get_text().strip().endswith(str(document.page_count))


def test_canonical_complete_pdf_name_uses_ascii_single_hyphen_slugs() -> None:
    discovery = _synthetic_discovery().model_copy(
        update={
            "work_title": "  Éclairs & Tea: A Tale!  ",
            "author": "Anne O’Doe",
        }
    )

    assert canonical_complete_pdf_name(discovery) == (
        "HAH-FAN-999__eclairs-tea-a-tale__anne-odoe.pdf"
    )


def test_render_chapter_pdf_rejects_remote_resources_before_launch(
    tmp_path: Path,
) -> None:
    html_path = tmp_path / "chapter-001.html"
    html_path.write_text(
        """<!doctype html><html><body>
        <main data-role="story"><p>Invented prose.</p>
        <img src="https://example.invalid/remote.png"></main>
        </body></html>""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="remote resource"):
        asyncio.run(render_chapter_pdf(html_path, tmp_path / "chapter-001.pdf"))

    assert not (tmp_path / "chapter-001.pdf").exists()


def test_render_chapter_pdf_is_byte_stable_across_render_times(
    tmp_path: Path,
) -> None:
    html_path = tmp_path / "chapter-001.html"
    _write_chapter(
        html_path,
        "Synthetic Stable Chapter",
        "An invented clock remained perfectly still.",
    )
    first_pdf = tmp_path / "first.pdf"
    second_pdf = tmp_path / "second.pdf"

    asyncio.run(render_chapter_pdf(html_path, first_pdf))
    time.sleep(1.1)
    asyncio.run(render_chapter_pdf(html_path, second_pdf))

    assert hashlib.sha256(first_pdf.read_bytes()).digest() == hashlib.sha256(
        second_pdf.read_bytes()
    ).digest()
