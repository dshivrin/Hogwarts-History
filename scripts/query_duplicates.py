#!/usr/bin/env python3
"""Query compact duplicate candidates without opening full source archives."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--tags", nargs="*", default=[])
    parser.add_argument("--candidate-chapter")
    parser.add_argument("--candidate-section")
    parser.add_argument("--limit", type=int, default=10)
    return parser.parse_args(argv)


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def words(value: str | None) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", str(value or "").lower()))


def title_from_topic(value: object) -> str:
    text = str(value or "Untitled entry").replace("-", " ")
    return " ".join(word.capitalize() for word in text.split())


def score_entry(entry: dict, tags: set[str], chapter: str | None, section: str | None) -> int:
    entry_tags = {str(tag) for tag in entry.get("tags") or []}
    score = len(tags & entry_tags)
    topic_words = words(str(entry.get("canonical_topic") or ""))
    score += len(words(chapter) & topic_words)
    score += len(words(section) & topic_words)
    return score


def query(root: Path, args: argparse.Namespace) -> dict:
    control = root / "project-control"
    tag_index = load_yaml(control / "tag-index.yaml")
    duplicate_index = load_yaml(control / "duplicate-index.yaml")
    requested_tags = {str(tag) for tag in args.tags or []}

    candidate_ids: set[str] = set()
    if requested_tags:
        for tag in requested_tags:
            row = (tag_index.get("tags") or {}).get(tag) or {}
            candidate_ids.update(str(entry_id) for entry_id in row.get("entries") or [])

    matches = []
    for entry in duplicate_index.get("entries") or []:
        if not isinstance(entry, dict):
            continue
        entry_id = str(entry.get("entry_id") or "")
        score = score_entry(entry, requested_tags, args.candidate_chapter, args.candidate_section)
        if requested_tags and entry_id not in candidate_ids and score == 0:
            continue
        if not requested_tags and score == 0 and (args.candidate_chapter or args.candidate_section):
            continue
        if not requested_tags and not args.candidate_chapter and not args.candidate_section:
            continue
        if score == 0:
            continue
        matches.append(
            {
                "entry_id": entry_id,
                "score": score,
                "title": title_from_topic(entry.get("canonical_topic")),
                "tags": entry.get("tags") or [],
                "source_note": entry.get("source_note"),
                "output_yaml": entry.get("output_yaml"),
            }
        )

    matches.sort(key=lambda row: (-int(row["score"]), str(row["entry_id"])))
    return {
        "query": {
            "tags": sorted(requested_tags),
            "candidate_chapter": args.candidate_chapter,
            "candidate_section": args.candidate_section,
        },
        "matches": matches[: max(args.limit, 0)],
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = query(args.root.resolve(), args)
    except Exception as exc:
        print(f"query_duplicates.py: error: {exc}", file=sys.stderr)
        return 1
    yaml.safe_dump(payload, sys.stdout, sort_keys=False, allow_unicode=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
