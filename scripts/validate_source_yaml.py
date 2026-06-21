#!/usr/bin/env python3
"""Validate canonical source YAML, compact indexes, and generated support files."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]

SOURCE_UNIT_REQUIRED = {
    "source_file",
    "book",
    "chapter",
    "chapter_start_pdf_page",
    "chapter_end_pdf_page",
    "processed_date",
}
ENTRY_REQUIRED = {
    "id",
    "pdf_page",
    "text_anchor",
    "quote_excerpt_short",
    "source_note",
    "reference_type",
    "era_classification",
    "topic_tags",
    "candidate_part",
    "candidate_chapter",
    "candidate_section",
    "duplicate_check",
    "confidence",
    "limitations",
}
CONFIDENCE_VALUES = {"high", "medium", "low"}
SOURCE_NAME_RE = re.compile(r"^book-\d{2}/chapter-\d{2}-[a-z0-9-]+\.yaml$")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def load_yaml(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def word_count(value: object) -> int:
    return len(re.findall(r"\b[\w'-]+\b", str(value or "")))


def schema_values(root: Path, heading: str) -> set[str]:
    path = root / "docs" / "instructions" / "schema-reference.md"
    if not path.exists():
        return set()
    values: set[str] = set()
    in_section = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_section = line.strip() == f"## {heading}"
            continue
        if not in_section:
            continue
        match = re.match(r"- `([^`]+)`", line.strip())
        if match:
            values.add(match.group(1))
    return values


def duplicate_targets(value: object) -> list[str]:
    if value in (None, "", False):
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    return [
        target.strip()
        for target in re.split(r"[;,]", str(value))
        if target.strip()
    ]


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def validate_source_files(
    root: Path,
    strict: bool,
    reference_types: set[str],
    era_classifications: set[str],
) -> list[str]:
    errors: list[str] = []
    seen_ids: dict[str, Path] = {}
    duplicate_refs: list[tuple[Path, str, str]] = []

    for path in sorted((root / "sources").glob("book-*/*.yaml")):
        rel_path = rel(path, root)
        source_name = path.relative_to(root / "sources").as_posix()
        if not SOURCE_NAME_RE.match(source_name):
            errors.append(f"{rel_path}: source YAML filename must be book-XX/chapter-XX-slug.yaml")
        try:
            data = load_yaml(path)
        except Exception as exc:
            errors.append(f"{rel_path}: YAML parse error: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{rel_path}: top-level YAML must be a mapping")
            continue

        source_unit = data.get("source_unit")
        entries = data.get("entries")
        if not isinstance(source_unit, dict):
            errors.append(f"{rel_path}: missing source_unit mapping")
            source_unit = {}
        else:
            missing = sorted(SOURCE_UNIT_REQUIRED - set(source_unit))
            if missing:
                errors.append(f"{rel_path}: source_unit missing {', '.join(missing)}")
        if not isinstance(entries, list):
            errors.append(f"{rel_path}: entries must be a list")
            continue

        for index, entry in enumerate(entries, start=1):
            label = f"{rel_path}: entry {index}"
            if not isinstance(entry, dict):
                errors.append(f"{label}: entry must be a mapping")
                continue
            entry_id = str(entry.get("id") or "")
            if not entry_id:
                errors.append(f"{label}: missing id")
            elif entry_id in seen_ids:
                errors.append(
                    f"{label}: duplicate id {entry_id} also in {rel(seen_ids[entry_id], root)}"
                )
            else:
                seen_ids[entry_id] = path

            missing = sorted(ENTRY_REQUIRED - set(entry))
            if missing:
                errors.append(f"{label}: missing {', '.join(missing)}")
            if reference_types and entry.get("reference_type") not in reference_types:
                errors.append(f"{label}: invalid reference_type {entry.get('reference_type')!r}")
            if era_classifications and entry.get("era_classification") not in era_classifications:
                errors.append(
                    f"{label}: invalid era_classification {entry.get('era_classification')!r}"
                )
            if entry.get("confidence") not in CONFIDENCE_VALUES:
                errors.append(f"{label}: invalid confidence {entry.get('confidence')!r}")
            if word_count(entry.get("quote_excerpt_short")) >= 25:
                errors.append(f"{label}: quote_excerpt_short must be under 25 words")

            duplicate_check = entry.get("duplicate_check")
            if not isinstance(duplicate_check, dict):
                errors.append(f"{label}: duplicate_check must be a mapping")
                duplicate_check = {}
            for target in duplicate_targets(duplicate_check.get("duplicate_of")):
                duplicate_refs.append((path, entry_id or f"entry-{index}", target))

            if strict:
                tags = entry.get("topic_tags")
                tag_count = len(tags) if isinstance(tags, list) else 0
                if tag_count < 3 or tag_count > 8:
                    errors.append(f"{label}: strict topic_tags count must be 3-8")
                if word_count(entry.get("source_note")) > 60:
                    errors.append(f"{label}: strict source_note must be 60 words or fewer")
                if duplicate_check.get("possible_duplicate") is True and not duplicate_targets(
                    duplicate_check.get("duplicate_of")
                ):
                    errors.append(
                        f"{label}: strict possible_duplicate true requires duplicate_of"
                    )

    for path, entry_id, target in duplicate_refs:
        if target not in seen_ids:
            errors.append(
                f"{rel(path, root)}: entry {entry_id} duplicate_of target {target!r} not found"
            )
    return errors


def validate_generated_files(root: Path) -> list[str]:
    errors: list[str] = []
    generated = root / "appendix" / "generated"
    if not generated.exists():
        return errors
    for path in sorted(generated.glob("*.md")):
        if not path.read_text(encoding="utf-8").startswith("# Generated File"):
            errors.append(f"{rel(path, root)}: generated appendix must start with # Generated File")
    return errors


def validate_index_files(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((root / "project-control").glob("*index.yaml")):
        try:
            load_yaml(path)
        except Exception as exc:
            errors.append(f"{rel(path, root)}: YAML parse error: {exc}")
    return errors


def validate(root: Path, strict: bool) -> list[str]:
    reference_types = schema_values(root, "Reference Types")
    era_classifications = schema_values(root, "Era Classifications")
    errors: list[str] = []
    errors.extend(validate_source_files(root, strict, reference_types, era_classifications))
    errors.extend(validate_generated_files(root))
    errors.extend(validate_index_files(root))
    return errors


def print_errors(errors: Iterable[str]) -> None:
    print("Source YAML validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    errors = validate(root, args.strict)
    if errors:
        print_errors(errors)
        return 1
    print("Source YAML validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
