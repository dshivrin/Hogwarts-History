#!/usr/bin/env python3
"""Build a compact tag lookup index from canonical source YAML files."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = ROOT / "sources"
OUTPUT_PATH = ROOT / "project-control" / "tag-index.yaml"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def build_index() -> dict:
    grouped: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {
            "entries": set(),
            "output_yaml": set(),
        }
    )

    for path in sorted(SOURCES_DIR.glob("book-*/*.yaml")):
        data = load_yaml(path)
        entries = data.get("entries") or []
        if not isinstance(entries, list):
            raise ValueError(f"Expected entries list in {path}")

        rel_path = path.relative_to(ROOT).as_posix()
        for entry in entries:
            if not isinstance(entry, dict) or not entry.get("id"):
                continue
            entry_id = str(entry["id"])
            for tag in sorted({str(tag) for tag in entry.get("topic_tags") or []}):
                row = grouped[tag]
                row["entries"].add(entry_id)  # type: ignore[union-attr]
                row["output_yaml"].add(rel_path)  # type: ignore[union-attr]

    tags = {}
    for tag, row in sorted(grouped.items()):
        tags[tag] = {
            "entries": sorted(row["entries"]),  # type: ignore[arg-type]
            "output_yaml": sorted(row["output_yaml"]),  # type: ignore[arg-type]
        }

    return {
        "version": 1,
        "updated": date.today().isoformat(),
        "tags": tags,
    }


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(build_index(), handle, sort_keys=False, allow_unicode=False)
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
