#!/usr/bin/env python3
"""Extract an inclusive PDF page range to reusable text files."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from pypdf import PdfReader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract 1-based inclusive PDF pages into a combined text file, "
            "optionally also writing one text file per page."
        )
    )
    parser.add_argument("--pdf", required=True, type=Path, help="Source PDF path.")
    parser.add_argument(
        "--start-page",
        required=True,
        type=int,
        help="First PDF page to extract, using 1-based numbering.",
    )
    parser.add_argument(
        "--end-page",
        required=True,
        type=int,
        help="Last PDF page to extract, using 1-based numbering.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Combined text output path.",
    )
    parser.add_argument(
        "--per-page-dir",
        type=Path,
        help="Optional directory for page-N.txt files.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.start_page < 1:
        raise ValueError("--start-page must be 1 or greater.")
    if args.end_page < args.start_page:
        raise ValueError("--end-page must be greater than or equal to --start-page.")
    if not args.pdf.is_file():
        raise ValueError(f"PDF does not exist: {args.pdf}")


def extract_pages(
    pdf_path: Path,
    start_page: int,
    end_page: int,
    output_path: Path,
    per_page_dir: Path | None = None,
) -> int:
    reader = PdfReader(str(pdf_path))
    page_count = len(reader.pages)

    if end_page > page_count:
        raise ValueError(
            f"Requested page {end_page}, but PDF has only {page_count} pages."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if per_page_dir is not None:
        per_page_dir.mkdir(parents=True, exist_ok=True)

    combined_blocks: list[str] = []

    for page_number in range(start_page, end_page + 1):
        page = reader.pages[page_number - 1]
        text = page.extract_text() or ""
        block = f"=== PDF page {page_number} ===\n{text.strip()}\n"
        combined_blocks.append(block)

        if per_page_dir is not None:
            page_path = per_page_dir / f"page-{page_number}.txt"
            page_path.write_text(block, encoding="utf-8")

    output_path.write_text("\n".join(combined_blocks), encoding="utf-8")
    return end_page - start_page + 1


def main() -> int:
    args = parse_args()

    try:
        validate_args(args)
        extracted_count = extract_pages(
            args.pdf,
            args.start_page,
            args.end_page,
            args.output,
            args.per_page_dir,
        )
    except Exception as exc:
        print(f"extract_pages.py: error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Extracted {extracted_count} page(s) from {args.pdf} "
        f"to {args.output}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
