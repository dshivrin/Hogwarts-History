#!/usr/bin/env python3
"""Query compact entry index rows by common extraction filters."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--tag")
    parser.add_argument("--classification")
    parser.add_argument("--reference-type")
    parser.add_argument("--confidence")
    parser.add_argument("--source-unit")
    parser.add_argument("--output-yaml")
    parser.add_argument("--limit", type=int, default=20)
    return parser.parse_args(argv)


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def matches(row: dict, args: argparse.Namespace) -> bool:
    tags = {str(tag) for tag in row.get("tags") or []}
    checks = [
        args.tag is None or args.tag in tags,
        args.classification is None or row.get("classification") == args.classification,
        args.reference_type is None or row.get("reference_type") == args.reference_type,
        args.confidence is None or row.get("confidence") == args.confidence,
        args.source_unit is None or row.get("source_unit") == args.source_unit,
        args.output_yaml is None or row.get("output_yaml") == args.output_yaml,
    ]
    return all(checks)


def query(root: Path, args: argparse.Namespace) -> dict:
    entry_index = load_yaml(root / "project-control" / "entry-index.yaml")
    rows = []
    for entry_id, row in sorted((entry_index.get("by_entry") or {}).items()):
        if not isinstance(row, dict) or not matches(row, args):
            continue
        rows.append(
            {
                "entry_id": entry_id,
                "title": row.get("title"),
                "classification": row.get("classification"),
                "confidence": row.get("confidence"),
                "tags": row.get("tags") or [],
                "source_unit": row.get("source_unit"),
                "output_yaml": row.get("output_yaml"),
            }
        )
    return {
        "query": {
            "tag": args.tag,
            "classification": args.classification,
            "reference_type": args.reference_type,
            "confidence": args.confidence,
            "source_unit": args.source_unit,
            "output_yaml": args.output_yaml,
        },
        "matches": rows[: max(args.limit, 0)],
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = query(args.root.resolve(), args)
    except Exception as exc:
        print(f"query_entries.py: error: {exc}", file=sys.stderr)
        return 1
    yaml.safe_dump(payload, sys.stdout, sort_keys=False, allow_unicode=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
