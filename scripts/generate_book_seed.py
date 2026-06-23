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
ORDER_PATH = ROOT / "project-control" / "book-seed-order.yaml"

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


def load_book_seed_order(root: Path) -> dict:
    path = root / "project-control" / "book-seed-order.yaml"
    if not path.exists():
        return {"parts": []}
    data = load_yaml(path)
    parts = data.get("parts") or []
    if not isinstance(parts, list):
        raise ValueError(f"Expected parts list in {path}")
    return data


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


def configured_titles_first(available: list[str], configured: list[str]) -> list[str]:
    available_set = set(available)
    ordered = [title for title in configured if title in available_set]
    ordered.extend(sorted(title for title in available if title not in set(ordered)))
    return ordered


def configured_part_titles(order: dict) -> list[str]:
    return [
        str(part.get("title"))
        for part in order.get("parts") or []
        if isinstance(part, dict) and part.get("title")
    ]


def configured_chapter_titles(order: dict, part_title: str) -> list[str]:
    for part in order.get("parts") or []:
        if not isinstance(part, dict) or part.get("title") != part_title:
            continue
        return [
            str(chapter.get("title"))
            for chapter in part.get("chapters") or []
            if isinstance(chapter, dict) and chapter.get("title")
        ]
    return []


def configured_section_titles(order: dict, part_title: str, chapter_title: str) -> list[str]:
    for part in order.get("parts") or []:
        if not isinstance(part, dict) or part.get("title") != part_title:
            continue
        for chapter in part.get("chapters") or []:
            if not isinstance(chapter, dict) or chapter.get("title") != chapter_title:
                continue
            return [str(section) for section in chapter.get("sections") or [] if section]
    return []


def duplicate_targets(value: object) -> list[str]:
    if value in (None, "", False):
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    targets = []
    for raw in str(value).replace(",", ";").split(";"):
        target = raw.strip()
        if target:
            targets.append(target)
    return targets


def entry_evidence_label(entry: dict) -> str:
    duplicate_check = entry.get("duplicate_check")
    if isinstance(duplicate_check, dict) and duplicate_check.get("duplicate_of"):
        return "Corroboration"
    if entry.get("reference_type") == "explicit_hogwarts_a_history":
        return "Direct evidence"
    if entry.get("era_classification") in {
        "later_editorial_note",
        "post_1984_excluded_from_original",
        "unknown_or_uncertain",
    }:
        return "Context"
    return "Supporting evidence"


def format_source_line(entry: dict, source_path: Path | None = None) -> str:
    yaml_path = source_path.as_posix() if source_path else str(entry.get("_output_yaml") or "")
    return (
        f"Source: {entry.get('_book')}, {entry.get('_chapter')}, "
        f"PDF p. {entry.get('pdf_page')}, `{entry.get('id')}`, `{yaml_path}`"
    )


def format_corroboration(entry: dict) -> str | None:
    duplicate_check = entry.get("duplicate_check")
    if not isinstance(duplicate_check, dict):
        return None

    targets = duplicate_targets(duplicate_check.get("duplicate_of"))
    notes = str(duplicate_check.get("notes") or "").strip()
    possible = duplicate_check.get("possible_duplicate") is True

    if targets:
        target_text = ", ".join(f"`{target}`" for target in targets)
        if notes and notes.lower() not in {"no duplicate found.", "no duplicate found"}:
            return f"Corroborates: {target_text}. {notes}"
        return f"Corroborates: {target_text}."
    if possible and notes and notes.lower() not in {"no duplicate found.", "no duplicate found"}:
        return f"Possible corroboration: {notes}"
    return None


def summarize_section(entries: list[dict]) -> str:
    count = len(entries)
    first_note = next(
        (str(entry.get("source_note")).strip() for entry in entries if entry.get("source_note")),
        "",
    )
    if first_note:
        return (
            f"Summary: The available evidence includes {count} source "
            f"{'item' if count == 1 else 'items'}, led by: {first_note}"
        )
    return f"Summary: The available evidence includes {count} source {'item' if count == 1 else 'items'}."


def entry_sort_key(entry: dict) -> tuple[str, str, str, str]:
    return (
        str(entry.get("candidate_part") or "Unassigned"),
        str(entry.get("candidate_chapter") or "Unassigned"),
        str(entry.get("candidate_section") or "Unassigned"),
        str(entry.get("id") or ""),
    )


def render(entries: list[dict], order: dict | None = None) -> str:
    order = order or {"parts": []}
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
    for part in configured_titles_first(list(grouped), configured_part_titles(order)):
        lines.extend([f"## Part: {part}", ""])
        chapter_titles = configured_chapter_titles(order, part)
        for chapter in configured_titles_first(list(grouped[part]), chapter_titles):
            lines.extend([f"### Chapter: {chapter}", ""])
            section_titles = configured_section_titles(order, part, chapter)
            for section in configured_titles_first(list(grouped[part][chapter]), section_titles):
                section_entries = sorted(grouped[part][chapter][section], key=entry_sort_key)
                lines.extend([f"#### Section: {section}", "", summarize_section(section_entries), ""])
                for entry in section_entries:
                    note = str(entry.get("source_note") or "No source note recorded.").strip()
                    lines.append(f"- **{entry_evidence_label(entry)}:** {note}")
                    quote = str(entry.get("quote_excerpt_short") or "").strip()
                    if quote:
                        lines.append(f'  - Quote: "{quote}"')
                    lines.append(f"  - {format_source_line(entry)}")
                    classification = str(entry.get("era_classification") or "unclassified")
                    confidence = str(entry.get("confidence") or "unknown")
                    lines.append(f"  - Classification: {classification} | Confidence: {confidence}")
                    reference_type = str(entry.get("reference_type") or "").strip()
                    if reference_type:
                        lines.append(f"  - Reference type: {reference_type}")
                    corroboration = format_corroboration(entry)
                    if corroboration:
                        lines.append(f"  - {corroboration}")
                    limitations = str(entry.get("limitations") or "").strip()
                    if limitations:
                        lines.append(f"  - Notes: {limitations}")
                    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate(root: Path) -> Path:
    output_path = root / "book-seed" / "hogwarts-a-history-seed.md"
    entries = load_entries(root)
    order = load_book_seed_order(root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render(entries, order), encoding="utf-8")
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
