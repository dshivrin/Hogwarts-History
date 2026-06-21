#!/usr/bin/env python3
"""Build compact entry and source indexes from canonical source YAML files."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = ROOT / "sources"
ENTRY_INDEX_PATH = ROOT / "project-control" / "entry-index.yaml"
SOURCE_INDEX_PATH = ROOT / "project-control" / "source-index.yaml"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def chapter_number_from_path(path: Path) -> int | None:
    match = re.search(r"chapter-(\d+)-", path.name)
    return int(match.group(1)) if match else None


def source_unit_id(path: Path, chapter_number: int | None) -> str:
    book_prefixes = {
        "book-01": "ps",
        "book-02": "cos",
        "book-03": "poa",
        "book-04": "gof",
        "book-05": "ootp",
        "book-06": "hbp",
        "book-07": "dh",
    }
    book_group = path.parent.name
    prefix = book_prefixes.get(book_group, book_group.replace("book-", "book"))
    if chapter_number is None:
        return path.stem
    return f"{prefix}-ch{chapter_number:02d}"


def title_for(entry: dict) -> str:
    section = entry.get("candidate_section")
    chapter = entry.get("candidate_chapter")
    if section and chapter:
        return f"{chapter}: {section}"
    return str(section or chapter or entry.get("id") or "Untitled entry")


def build_indexes() -> tuple[dict, dict]:
    by_entry: dict[str, dict] = {}
    by_tag: dict[str, list[str]] = defaultdict(list)
    processed_units: list[dict] = []

    for path in sorted(SOURCES_DIR.glob("book-*/*.yaml")):
        data = load_yaml(path)
        source_unit = data.get("source_unit") or {}
        entries = data.get("entries") or []
        if not isinstance(entries, list):
            raise ValueError(f"Expected entries list in {path}")

        chapter_number = chapter_number_from_path(path)
        rel_path = path.relative_to(ROOT).as_posix()
        source_id = source_unit_id(path, chapter_number)
        explicit_count = sum(
            1
            for entry in entries
            if isinstance(entry, dict)
            and entry.get("reference_type") == "explicit_hogwarts_a_history"
        )
        processed_units.append(
            {
                "source_unit_id": source_id,
                "source_file": source_unit.get("source_file"),
                "book": source_unit.get("book"),
                "chapter_number": chapter_number,
                "chapter_title": source_unit.get("chapter"),
                "page_start": source_unit.get("chapter_start_pdf_page"),
                "page_end": source_unit.get("chapter_end_pdf_page"),
                "output_yaml": rel_path,
                "processed_at": str(source_unit.get("processed_date") or ""),
                "explicit_reference_count": explicit_count,
                "candidate_entry_count": len(entries),
                "boundary_summary": (
                    f"Used indexed page range; extracted only pages "
                    f"{source_unit.get('chapter_start_pdf_page')}-"
                    f"{source_unit.get('chapter_end_pdf_page')}."
                ),
            }
        )

        for entry in entries:
            if not isinstance(entry, dict) or not entry.get("id"):
                continue
            entry_id = str(entry["id"])
            tags = sorted({str(tag) for tag in entry.get("topic_tags") or []})
            by_entry[entry_id] = {
                "title": title_for(entry),
                "classification": entry.get("era_classification"),
                "reference_type": entry.get("reference_type"),
                "confidence": entry.get("confidence"),
                "tags": tags,
                "source_unit": source_id,
                "output_yaml": rel_path,
            }
            for tag in tags:
                by_tag[tag].append(entry_id)

    entry_index = {
        "version": 1,
        "updated": date.today().isoformat(),
        "by_entry": by_entry,
        "by_tag": dict(sorted((tag, sorted(ids)) for tag, ids in by_tag.items())),
    }
    source_index = {
        "version": 1,
        "updated": date.today().isoformat(),
        "processed_units": processed_units,
    }
    return entry_index, source_index


def main() -> int:
    ENTRY_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry_index, source_index = build_indexes()
    with ENTRY_INDEX_PATH.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(entry_index, handle, sort_keys=False, allow_unicode=False)
    with SOURCE_INDEX_PATH.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(source_index, handle, sort_keys=False, allow_unicode=False)
    print(f"Wrote {ENTRY_INDEX_PATH.relative_to(ROOT)}")
    print(f"Wrote {SOURCE_INDEX_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
