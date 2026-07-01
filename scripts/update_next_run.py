#!/usr/bin/env python3
"""Regenerate next-run instructions and optionally advance source state."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROCESSING_STATE_PATH = ROOT / "project-control" / "processing-state.yaml"
NEXT_RUN_PATH = ROOT / "project-control" / "next-run.md"
CHAPTERS_INDEX_PATH = ROOT / "chapters-index.md"
SOURCE_PLAN_PATH = ROOT / "project-control" / "source-plan.yaml"

CHAPTER_WORDS = {
    1: "One",
    2: "Two",
    3: "Three",
    4: "Four",
    5: "Five",
    6: "Six",
    7: "Seven",
    8: "Eight",
    9: "Nine",
    10: "Ten",
    11: "Eleven",
    12: "Twelve",
    13: "Thirteen",
    14: "Fourteen",
    15: "Fifteen",
    16: "Sixteen",
    17: "Seventeen",
    18: "Eighteen",
    19: "Nineteen",
    20: "Twenty",
    21: "Twenty-One",
    22: "Twenty-Two",
    23: "Twenty-Three",
    24: "Twenty-Four",
    25: "Twenty-Five",
    26: "Twenty-Six",
    27: "Twenty-Seven",
    28: "Twenty-Eight",
    29: "Twenty-Nine",
    30: "Thirty",
    31: "Thirty-One",
    32: "Thirty-Two",
    33: "Thirty-Three",
    34: "Thirty-Four",
    35: "Thirty-Five",
    36: "Thirty-Six",
    37: "Thirty-Seven",
    38: "Thirty-Eight",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regenerate project-control/next-run.md from processing state."
    )
    parser.add_argument(
        "--advance-after-success",
        action="store_true",
        help="Advance current source unit after validating its output YAML.",
    )
    return parser.parse_args(argv)


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def write_yaml(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=False)


def validate_current_output(current: dict) -> None:
    output_path = ROOT / str(current.get("output_yaml") or "")
    if not output_path.exists():
        raise ValueError(f"Current output YAML does not exist: {output_path}")
    output = load_yaml(output_path)
    if not isinstance(output.get("source_unit"), dict):
        raise ValueError(f"Missing source_unit mapping in {output_path}")
    entries = output.get("entries")
    if not isinstance(entries, list):
        raise ValueError(f"Missing entries list in {output_path}")


def parse_chapters_index() -> dict[tuple[int, int], dict]:
    if not CHAPTERS_INDEX_PATH.exists():
        return {}

    chapters = {}
    current_book_title: str | None = None
    heading_pattern = re.compile(r"^## Book [^:]+:\s*(?P<title>.+)$")
    pattern = re.compile(
        r"book:\s*(?P<book>\d+),\s*chapter:\s*(?P<chapter>\d+),\s*"
        r"title:\s*(?P<title>.*?),\s*pages:\s*(?P<start>\d+)-(?P<end>\d+)"
    )
    for line in CHAPTERS_INDEX_PATH.read_text(encoding="utf-8").splitlines():
        heading_match = heading_pattern.search(line)
        if heading_match:
            current_book_title = heading_match.group("title").strip()
            continue

        match = pattern.search(line)
        if not match:
            continue
        book_number = int(match.group("book"))
        chapter_number = int(match.group("chapter"))
        chapters[(book_number, chapter_number)] = {
            "book_number": book_number,
            "book_group": f"book-{book_number:02d}",
            "book": current_book_title,
            "chapter_number": chapter_number,
            "short_title": match.group("title").strip(),
            "page_start": int(match.group("start")),
            "page_end": int(match.group("end")),
        }
    return chapters


def book_number_from_group(book_group: str) -> int:
    match = re.search(r"(\d+)$", book_group)
    if not match:
        raise ValueError(f"Cannot determine book number from {book_group}")
    return int(match.group(1))


def slugify(value: str) -> str:
    text = value.lower().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "untitled"


def chapter_title(chapter_number: int, short_title: str) -> str:
    if short_title.lower().startswith("chapter "):
        return short_title
    word = CHAPTER_WORDS.get(chapter_number, str(chapter_number))
    return f"Chapter {word} - {short_title}"


def output_yaml_for(unit: dict, source_plan: dict | None) -> str:
    planned = find_planned_chapter(source_plan, unit)
    if planned and planned.get("output_file"):
        return str(planned["output_file"])

    title = unit["chapter_title"].split(" - ", 1)[-1]
    return (
        f"sources/{unit['book_group']}/"
        f"chapter-{unit['chapter_number']:02d}-{slugify(title)}.yaml"
    )


def build_unit(base: dict, chapter_info: dict, source_plan: dict | None) -> dict:
    unit = {
        "source_file": base.get("source_file"),
        "book_group": chapter_info.get("book_group") or base.get("book_group"),
        "book": chapter_info.get("book") or base.get("book"),
        "chapter_number": chapter_info["chapter_number"],
        "chapter_title": chapter_title(
            chapter_info["chapter_number"],
            str(chapter_info["short_title"]),
        ),
        "page_start": chapter_info["page_start"],
        "page_end": chapter_info["page_end"],
    }
    unit["output_yaml"] = output_yaml_for(unit, source_plan)
    return unit


def following_chapter_info(
    chapters: dict[tuple[int, int], dict],
    book_number: int,
    chapter_number: int,
) -> dict | None:
    same_book = chapters.get((book_number, chapter_number + 1))
    if same_book:
        return same_book
    return chapters.get((book_number + 1, 1))


def find_planned_chapter(source_plan: dict | None, unit: dict) -> dict | None:
    if not source_plan:
        return None
    for source in source_plan.get("sources") or []:
        if source.get("book_group") != unit.get("book_group"):
            continue
        for chapter in source.get("chapters") or []:
            if chapter.get("number") == unit.get("chapter_number"):
                return chapter
    return None


def update_source_plan_completed(source_plan: dict, completed_unit: dict) -> bool:
    chapter = find_planned_chapter(source_plan, completed_unit)
    if not chapter:
        source_plan["status_note"] = (
            "Processing state is authoritative; source-plan chapter row was not found."
        )
        return False
    chapter["status"] = "complete"
    chapter["output_file"] = completed_unit.get("output_yaml")
    return True


def advance_state(state: dict) -> dict:
    current = state.get("current_source_unit")
    next_unit = state.get("next_source_unit")
    if not isinstance(current, dict) or not isinstance(next_unit, dict):
        raise ValueError("processing-state.yaml must define current and next source units")

    validate_current_output(current)
    source_plan = load_yaml(SOURCE_PLAN_PATH) if SOURCE_PLAN_PATH.exists() else None
    chapters = parse_chapters_index()
    next_book_number = book_number_from_group(str(next_unit.get("book_group")))

    next_chapter_number = int(next_unit.get("chapter_number") or 0)
    following_info = following_chapter_info(
        chapters,
        next_book_number,
        next_chapter_number,
    )
    if not following_info:
        raise ValueError(
            f"Next source unit after chapter {next_chapter_number} is not known"
        )

    advanced = deepcopy(state)
    completed = deepcopy(current)
    completed.pop("extracted_text_path", None)
    advanced["last_completed_source_unit"] = completed

    new_current = deepcopy(next_unit)
    new_current.setdefault(
        "extracted_text_path",
        current.get("extracted_text_path") or ".tmp/current-chapter.txt",
    )
    advanced["current_source_unit"] = new_current
    advanced["next_source_unit"] = build_unit(new_current, following_info, source_plan)

    if source_plan is not None:
        update_source_plan_completed(source_plan, completed)
        write_yaml(SOURCE_PLAN_PATH, source_plan)

    return advanced


def render_next_run(state: dict) -> str:
    current = state.get("current_source_unit") or {}
    return f"""# Next Run

Generated display only. Source of truth: `project-control/processing-state.yaml`.

## Current Source Unit

- Source file: `{current.get('source_file')}`
- Book group: `{current.get('book_group')}`
- Book: `{current.get('book')}`
- Chapter: {current.get('chapter_title')}
- Page range: {current.get('page_start')}-{current.get('page_end')}
- Extracted text: `{current.get('extracted_text_path', '.tmp/current-chapter.txt')}`
- Output YAML: `{current.get('output_yaml')}`

## Minimal Context

Read only:

- `docs/instructions/runtime-contract.md`
- `project-control/processing-state.yaml`
- `.tmp/current-chapter.txt`
- Current output YAML only if it exists

Use `just query-dupes <tag> <tag>` for duplicate and context lookup after candidate
tags are known. Open only referenced YAML files for likely matches.
Use `just search "pattern"` or targeted `rg` before opening broad files.

Do not read appendices, archives, old prompts, full indexes, all prior YAML files, or
`chapters-index.md` during normal runs.
"""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        state = load_yaml(PROCESSING_STATE_PATH)
        if args.advance_after_success:
            state = advance_state(state)
            write_yaml(PROCESSING_STATE_PATH, state)
        NEXT_RUN_PATH.write_text(render_next_run(state), encoding="utf-8")
    except Exception as exc:
        print(f"update_next_run.py: error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {NEXT_RUN_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
