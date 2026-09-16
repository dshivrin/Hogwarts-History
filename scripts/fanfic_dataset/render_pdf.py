"""Render self-contained semantic chapter HTML to PDF."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
import fitz
from playwright.sync_api import Route, sync_playwright


_SYSTEM_SERIF_CSS = """
html, body, body * {
  font-family: Georgia, "Times New Roman", Times, serif !important;
}
html {
  color: #161616;
  font-size: 11.5pt;
  line-height: 1.55;
}
body {
  margin: 0;
}
h1, h2, h3 {
  line-height: 1.2;
  break-after: avoid;
}
p {
  orphans: 3;
  widows: 3;
}
img {
  max-width: 100%;
}
"""
_REMOTE_SCHEMES = frozenset({"http", "https"})
_CHROMIUM_PDF_DATE = re.compile(
    rb"/(CreationDate|ModDate) \(D:\d{14}\+00'00'\)"
)
_FETCHING_ATTRIBUTES = {
    "audio": ("src",),
    "embed": ("src",),
    "iframe": ("src",),
    "img": ("src", "srcset"),
    "input": ("src",),
    "link": ("href",),
    "object": ("data",),
    "script": ("src",),
    "source": ("src", "srcset"),
    "track": ("src",),
    "video": ("poster", "src"),
}


async def render_chapter_pdf(clean_html_path: Path, output_path: Path) -> None:
    """Render one local semantic HTML chapter to an atomically replaced PDF."""
    html_path = clean_html_path.resolve(strict=True)
    if html_path.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("clean HTML path must have an HTML suffix")
    if output_path.suffix.lower() != ".pdf":
        raise ValueError("chapter PDF output must have a .pdf suffix")
    _validate_self_contained_html(html_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(_render_atomically, html_path, output_path)


def _render_atomically(html_path: Path, output_path: Path) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.",
        suffix=".tmp.pdf",
        dir=output_path.parent,
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        _render_local_html_sync(html_path, temporary_path)
        with fitz.open(temporary_path) as document:
            if document.page_count < 1:
                raise ValueError("rendered chapter PDF has no pages")
        os.replace(temporary_path, output_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _render_local_html_sync(html_path: Path, output_path: Path) -> None:
    """Render validated local HTML with the synchronous Playwright boundary."""
    _validate_self_contained_html(html_path)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.route("**/*", _local_resources_only)
            page.goto(
                html_path.resolve(strict=True).as_uri(),
                wait_until="load",
            )
            page.add_style_tag(content=_SYSTEM_SERIF_CSS)
            page.evaluate("document.fonts.ready")
            page.emulate_media(media="print")
            page.pdf(
                path=str(output_path),
                format="A4",
                tagged=True,
                print_background=True,
                margin={
                    "top": "20mm",
                    "right": "20mm",
                    "bottom": "20mm",
                    "left": "20mm",
                },
                display_header_footer=False,
            )
            _normalize_chromium_metadata(output_path)
        finally:
            browser.close()


def _local_resources_only(route: Route) -> None:
    scheme = urlsplit(route.request.url).scheme.lower()
    if scheme in {"file", "data", "about"}:
        route.continue_()
    else:
        route.abort()


def _normalize_chromium_metadata(output_path: Path) -> None:
    source = output_path.read_bytes()

    def fixed_date(match: re.Match[bytes]) -> bytes:
        return (
            b"/"
            + match.group(1)
            + b" (D:20000101000000+00'00')"
        )

    normalized, replacements = _CHROMIUM_PDF_DATE.subn(fixed_date, source)
    if replacements != 2:
        raise ValueError(
            "rendered PDF did not contain Chromium creation and modification dates"
        )
    output_path.write_bytes(normalized)


def _validate_self_contained_html(html_path: Path) -> None:
    try:
        source = html_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("clean HTML must be valid UTF-8") from error
    soup = BeautifulSoup(source, "html.parser")
    if soup.find("script") is not None:
        raise ValueError("clean HTML must not contain scripts")
    style_text = "\n".join(node.get_text() for node in soup.find_all("style"))
    if re.search(r"@font-face|@import|url\s*\(", style_text, re.IGNORECASE):
        raise ValueError("clean HTML must use system fonts and local inline CSS only")
    for tag_name, attributes in _FETCHING_ATTRIBUTES.items():
        for node in soup.find_all(tag_name):
            for attribute in attributes:
                value = node.get(attribute)
                if value is None:
                    continue
                values = (
                    str(value).split(",")
                    if attribute == "srcset"
                    else [str(value)]
                )
                for candidate in values:
                    url = candidate.strip().split()[0] if candidate.strip() else ""
                    parsed = urlsplit(url)
                    if (
                        parsed.scheme.lower() in _REMOTE_SCHEMES
                        or url.startswith("//")
                    ):
                        raise ValueError(
                            f"clean HTML contains a remote resource: {url}"
                        )
