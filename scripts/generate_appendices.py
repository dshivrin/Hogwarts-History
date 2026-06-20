#!/usr/bin/env python3
"""Generate human-facing appendix markdown from source YAML and indexes."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = ROOT / "sources"
GENERATED_DIR = ROOT / "appendix" / "generated"
ENTRY_INDEX_PATH = ROOT / "project-control" / "entry-index.yaml"
SOURCE_INDEX_PATH = ROOT / "project-control" / "source-index.yaml"
STRUCTURED_OPEN_QUESTIONS_PATH = (
    ROOT / "project-control" / "structured-sources" / "open-questions.yaml"
)

HEADER = """# Generated File

Do not edit manually.
Regenerate with `scripts/generate_appendices.py`.
Source data: sources YAML + project-control indexes + structured source data.
"""


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def source_yaml_files() -> list[Path]:
    return sorted(SOURCES_DIR.glob("book-*/*.yaml"))


def load_entries() -> list[dict]:
    rows: list[dict] = []
    for path in source_yaml_files():
        data = load_yaml(path)
        source_unit = data.get("source_unit") or {}
        for entry in data.get("entries") or []:
            if not isinstance(entry, dict):
                continue
            row = dict(entry)
            row["_output_yaml"] = path.relative_to(ROOT).as_posix()
            row["_chapter"] = source_unit.get("chapter")
            row["_book"] = source_unit.get("book")
            rows.append(row)
    return rows


def write(path: Path, body: str) -> None:
    path.write_text(f"{HEADER}\n{body.rstrip()}\n", encoding="utf-8")


def generate_book_structure(entries: list[dict]) -> str:
    grouped: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for entry in entries:
        part = str(entry.get("candidate_part") or "Unassigned")
        chapter = str(entry.get("candidate_chapter") or "Unassigned")
        section = str(entry.get("candidate_section") or "Unassigned")
        grouped[part][chapter].add(section)

    lines = ["# Book Structure Seed", ""]
    for part in sorted(grouped):
        lines.extend([f"## {part}", ""])
        for chapter in sorted(grouped[part]):
            lines.append(f"- {chapter}")
            for section in sorted(grouped[part][chapter]):
                lines.append(f"  - {section}")
        lines.append("")
    return "\n".join(lines)


def generate_explicit_references(entries: list[dict]) -> str:
    lines = ["# Explicit Hogwarts: A History References", ""]
    explicit = [
        entry
        for entry in entries
        if entry.get("reference_type") == "explicit_hogwarts_a_history"
    ]
    if not explicit:
        lines.append("No explicit references have been indexed yet.")
        return "\n".join(lines)

    for entry in explicit:
        lines.append(
            "- "
            f"{entry.get('_book')}, {entry.get('_chapter')}, "
            f"entry `{entry.get('id')}`: {entry.get('source_note')}"
        )
    return "\n".join(lines)


def generate_open_questions(entries: list[dict]) -> str:
    structured_questions = load_structured_open_questions()
    uncertain = [
        entry
        for entry in entries
        if entry.get("confidence") == "low"
        or entry.get("era_classification") == "unknown_or_uncertain"
    ]
    lines = ["# Open Questions", ""]
    if structured_questions:
        current_topic = None
        for question in structured_questions:
            topic = str(question.get("topic") or "Unassigned")
            if topic != current_topic:
                if current_topic is not None:
                    lines.append("")
                lines.extend([f"## {topic}", ""])
                current_topic = topic
            suffix_parts = []
            tags = question.get("tags") or []
            related_entries = question.get("related_entries") or []
            if tags:
                suffix_parts.append("tags: " + ", ".join(f"`{tag}`" for tag in tags))
            if related_entries:
                suffix_parts.append(
                    "related: " + ", ".join(f"`{entry}`" for entry in related_entries)
                )
            suffix = f" ({'; '.join(suffix_parts)})" if suffix_parts else ""
            lines.append(f"- {question.get('question')}{suffix}")
        lines.append("")

    if not uncertain and not structured_questions:
        lines.append("No low-confidence or unknown-era entries are currently indexed.")
        return "\n".join(lines)

    if uncertain:
        lines.extend(["## Generated From Low-Confidence Entries", ""])
    for entry in uncertain:
        lines.append(
            "- "
            f"`{entry.get('id')}` ({entry.get('_chapter')}): "
            f"{entry.get('limitations')}"
        )
    return "\n".join(lines)


def load_structured_open_questions() -> list[dict]:
    if not STRUCTURED_OPEN_QUESTIONS_PATH.exists():
        return []
    data = load_yaml(STRUCTURED_OPEN_QUESTIONS_PATH)
    questions = data.get("questions") or []
    if not isinstance(questions, list):
        raise ValueError(f"Expected questions list in {STRUCTURED_OPEN_QUESTIONS_PATH}")
    return [question for question in questions if isinstance(question, dict)]


def generate_source_index() -> str:
    source_index = load_yaml(SOURCE_INDEX_PATH)
    lines = ["# Source Index", ""]
    for unit in source_index.get("processed_units") or []:
        lines.append(
            "- "
            f"`{unit.get('source_unit_id')}`: {unit.get('book')}, "
            f"{unit.get('chapter_title')}, pages "
            f"{unit.get('page_start')}-{unit.get('page_end')}, "
            f"{unit.get('candidate_entry_count')} entries, "
            f"{unit.get('explicit_reference_count')} explicit references."
        )
    return "\n".join(lines)


def main() -> int:
    if not ENTRY_INDEX_PATH.exists() or not SOURCE_INDEX_PATH.exists():
        raise SystemExit("Run build_entry_index.py before generate_appendices.py.")

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    entries = load_entries()
    write(GENERATED_DIR / "book-structure-seed.md", generate_book_structure(entries))
    write(
        GENERATED_DIR / "explicit-hogwarts-a-history-references.md",
        generate_explicit_references(entries),
    )
    write(GENERATED_DIR / "open-questions.md", generate_open_questions(entries))
    write(GENERATED_DIR / "source-index.md", generate_source_index())
    print(f"Wrote generated appendices to {GENERATED_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
