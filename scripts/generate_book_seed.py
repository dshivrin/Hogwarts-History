#!/usr/bin/env python3
"""Generate the main human-readable Hogwarts: A History seed."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "book-seed" / "hogwarts-a-history-seed.md"

HEADER = """# Generated File

Do not edit manually.
Regenerate with `scripts/generate_book_seed.py`.
Source data: sources YAML.
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser.parse_args(argv)


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def load_entries(root: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted((root / "sources").glob("book-*/*.yaml")):
        data = load_yaml(path)
        source_unit = data.get("source_unit") or {}
        entries = data.get("entries") or []
        if not isinstance(entries, list):
            raise ValueError(f"Expected entries list in {path}")
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            row = dict(entry)
            row["_book"] = source_unit.get("book")
            row["_chapter"] = source_unit.get("chapter")
            row["_output_yaml"] = path.relative_to(root).as_posix()
            rows.append(row)
    return rows


def duplicate_summary(duplicate_check: object) -> str:
    if not isinstance(duplicate_check, dict):
        return "Not recorded."
    possible = duplicate_check.get("possible_duplicate")
    duplicate_of = duplicate_check.get("duplicate_of")
    notes = duplicate_check.get("notes")
    parts = [f"possible_duplicate={str(possible).lower()}"]
    if duplicate_of:
        parts.append(f"duplicate_of={duplicate_of}")
    if notes:
        parts.append(str(notes))
    return "; ".join(parts)


def entry_sort_key(entry: dict) -> tuple[str, str, str, str]:
    return (
        str(entry.get("candidate_part") or "Unassigned"),
        str(entry.get("candidate_chapter") or "Unassigned"),
        str(entry.get("candidate_section") or "Unassigned"),
        str(entry.get("id") or ""),
    )


def render(entries: list[dict]) -> str:
    grouped: dict[str, dict[str, dict[str, list[dict]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    for entry in entries:
        grouped[str(entry.get("candidate_part") or "Unassigned")][
            str(entry.get("candidate_chapter") or "Unassigned")
        ][str(entry.get("candidate_section") or "Unassigned")].append(entry)

    lines = [
        HEADER.rstrip(),
        "",
        "# Hogwarts: A History - Evidence-Backed Seed",
        "",
        "This generated seed arranges archived source evidence into a readable draft structure.",
        "",
    ]
    for part in sorted(grouped):
        lines.extend([f"## Part: {part}", ""])
        for chapter in sorted(grouped[part]):
            lines.extend([f"### Chapter: {chapter}", ""])
            for section in sorted(grouped[part][chapter]):
                lines.extend([f"#### Section: {section}", ""])
                for entry in sorted(grouped[part][chapter][section], key=entry_sort_key):
                    quote = str(entry.get("quote_excerpt_short") or "")
                    lines.extend(
                        [
                            f"**Fact:** {entry.get('source_note')}",
                            f'**Evidence:** "{quote}"',
                            (
                                f"**Source:** {entry.get('_book')}, {entry.get('_chapter')}, "
                                f"PDF page {entry.get('pdf_page')}, entry `{entry.get('id')}`, "
                                f"`{entry.get('_output_yaml')}`"
                            ),
                            f"**Classification:** {entry.get('era_classification')}",
                            f"**Reference type:** {entry.get('reference_type')}",
                            f"**Confidence:** {entry.get('confidence')}",
                            (
                                "**Duplicate / corroboration:** "
                                f"{duplicate_summary(entry.get('duplicate_check'))}"
                            ),
                            f"**Notes:** {entry.get('limitations')}",
                            "",
                        ]
                    )
    return "\n".join(lines).rstrip() + "\n"


def generate(root: Path) -> Path:
    output_path = root / "book-seed" / "hogwarts-a-history-seed.md"
    entries = load_entries(root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render(entries), encoding="utf-8")
    return output_path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        output_path = generate(args.root.resolve())
    except Exception as exc:
        print(f"generate_book_seed.py: error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {output_path.relative_to(args.root.resolve())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
