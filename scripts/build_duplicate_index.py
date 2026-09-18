#!/usr/bin/env python3
"""Build the compact duplicate index from canonical source YAML files."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import re

import yaml

try:
    from scripts.source_files import discover_source_yaml
except ModuleNotFoundError:  # Direct script execution.
    from source_files import discover_source_yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = ROOT / "sources"
OUTPUT_PATH = ROOT / "project-control" / "duplicate-index.yaml"


def slugify(value: object) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "untitled"


def chapter_number_from_path(path: Path) -> int | None:
    match = re.search(r"chapter-(\d+)-", path.name)
    return int(match.group(1)) if match else None


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def build_entries() -> list[dict]:
    rows: list[dict] = []
    for path in discover_source_yaml(ROOT):
        data = load_yaml(path)
        source_unit = data.get("source_unit") or {}
        entries = data.get("entries") or []
        if not isinstance(entries, list):
            raise ValueError(f"Expected entries list in {path}")

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            tags = sorted({str(tag) for tag in entry.get("topic_tags") or []})
            canonical_parts = [
                entry.get("candidate_chapter"),
                entry.get("candidate_section"),
            ]
            canonical_topic = slugify(" ".join(str(p) for p in canonical_parts if p))
            row = {
                    "entry_id": entry.get("id"),
                    "canonical_topic": canonical_topic,
                    "tags": tags,
                    "book": entry.get("book") or source_unit.get("book"),
                    "chapter_number": chapter_number_from_path(path),
                    "chapter_title": entry.get("chapter") or source_unit.get("chapter"),
                    "source_note": entry.get("source_note"),
                    "output_yaml": path.relative_to(ROOT).as_posix(),
                }
            source_id = entry.get("source_id") or source_unit.get("source_id")
            source_url = (
                entry.get("source_url")
                or source_unit.get("original_url")
                or source_unit.get("retrieval_url")
            )
            if source_id:
                row["source_id"] = source_id
            if source_url:
                row["source_url"] = source_url
            if entry.get("scene_id"):
                for key in ("scene_id", "pdf_page", "timeline", "timeline_detail", "evidence_mode"):
                    row[key] = entry.get(key)
            rows.append(row)
    return rows


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "updated": date.today().isoformat(),
        "entries": build_entries(),
    }
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=False)
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
