#!/usr/bin/env python3
"""Generate human-facing appendix markdown from source YAML and indexes."""

from __future__ import annotations

from collections import Counter, defaultdict
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
PROCESSING_STATE_PATH = ROOT / "project-control" / "processing-state.yaml"

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

    grouped: dict[tuple[str, str], list[dict]] = {}
    for entry in explicit:
        key = (str(entry.get("_book") or "Unknown book"), str(entry.get("_chapter") or "Unknown chapter"))
        grouped.setdefault(key, []).append(entry)

    for (book, chapter), group_entries in grouped.items():
        lines.extend([f"## {book}, {chapter}", ""])
        for entry in group_entries:
            lines.append(f"- `{entry.get('id')}`")
            quote = str(entry.get("quote_excerpt_short") or "").strip()
            if quote:
                lines.append(f'  - Quote: "{quote}"')
            note = str(entry.get("source_note") or "").strip()
            if note:
                lines.append(f"  - Evidence note: {note}")
            destination = " / ".join(
                str(value)
                for value in [
                    entry.get("candidate_part"),
                    entry.get("candidate_chapter"),
                    entry.get("candidate_section"),
                ]
                if value
            )
            if destination:
                lines.append(f"  - Destination: {destination}")
            lines.append(
                f"  - Source: PDF p. {entry.get('pdf_page')}, `{entry.get('_output_yaml')}`"
            )
            lines.append(
                "  - "
                f"Classification: {entry.get('era_classification')} | "
                f"Confidence: {entry.get('confidence')}"
            )
        lines.append("")
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


def entry_label(entry: dict) -> str:
    return (
        f"`{entry.get('id')}` ({entry.get('_book')}, {entry.get('_chapter')}): "
        f"{entry.get('source_note') or entry.get('limitations') or 'No note recorded.'}"
    )


def matching_entries(entries: list[dict], predicate) -> list[dict]:
    return [entry for entry in entries if predicate(entry)]


def add_entry_section(lines: list[str], heading: str, entries: list[dict]) -> None:
    lines.extend([f"## {heading}", ""])
    if not entries:
        lines.extend(["No entries currently flagged.", ""])
        return
    for entry in sorted(entries, key=lambda item: str(item.get("id") or "")):
        lines.append(f"- {entry_label(entry)}")
    lines.append("")


def has_limited_evidence(entry: dict) -> bool:
    text = f"{entry.get('limitations') or ''} {entry.get('source_note') or ''}".lower()
    markers = ["limited", "uncertain", "not stated", "does not", "may", "only"]
    return any(marker in text for marker in markers)


def has_off_campus_context(entry: dict) -> bool:
    tags = " ".join(str(tag) for tag in entry.get("topic_tags") or []).lower()
    text = f"{tags} {entry.get('candidate_part') or ''} {entry.get('source_note') or ''}".lower()
    return any(marker in text for marker in ["off-campus", "holiday", "muggle", "privet"])


def schema_warnings(entry: dict) -> list[str]:
    warnings = []
    tags = entry.get("topic_tags")
    if not isinstance(tags, list) or len(tags) < 3 or len(tags) > 8:
        warnings.append("topic tag count outside recommended 3-8 range")
    if not entry.get("text_anchor"):
        warnings.append("missing text_anchor relocation aid")
    if not entry.get("quote_excerpt_short"):
        warnings.append("missing quote excerpt")
    return warnings


def generate_review_flags(entries: list[dict]) -> str:
    lines = ["# Review Flags", ""]
    add_entry_section(
        lines,
        "Low Confidence",
        matching_entries(entries, lambda entry: entry.get("confidence") == "low"),
    )
    add_entry_section(
        lines,
        "Unknown Era",
        matching_entries(entries, lambda entry: entry.get("era_classification") == "unknown_or_uncertain"),
    )
    add_entry_section(
        lines,
        "Possible Duplicates",
        matching_entries(
            entries,
            lambda entry: isinstance(entry.get("duplicate_check"), dict)
            and entry["duplicate_check"].get("possible_duplicate") is True,
        ),
    )
    add_entry_section(
        lines,
        "Later Editorial Notes",
        matching_entries(
            entries,
            lambda entry: entry.get("era_classification")
            in {"later_editorial_note", "post_1984_excluded_from_original"},
        ),
    )
    add_entry_section(lines, "Off-Campus Context", matching_entries(entries, has_off_campus_context))
    add_entry_section(lines, "Limited Evidence", matching_entries(entries, has_limited_evidence))

    lines.extend(["## Schema Warnings", ""])
    warning_rows = []
    for entry in entries:
        for warning in schema_warnings(entry):
            warning_rows.append(f"- `{entry.get('id')}`: {warning}")
    if warning_rows:
        lines.extend(sorted(warning_rows))
    else:
        lines.append("No schema warnings from appendix review.")
    return "\n".join(lines)


def load_processing_state() -> dict:
    if not PROCESSING_STATE_PATH.exists():
        return {}
    return load_yaml(PROCESSING_STATE_PATH)


def counter_lines(counter: Counter) -> list[str]:
    if not counter:
        return ["- None recorded."]
    return [f"- {key}: {counter[key]}" for key in sorted(counter)]


def unit_summary(unit: dict) -> str:
    if not unit:
        return "Not recorded."
    return (
        f"{unit.get('book')}, {unit.get('chapter_title')}, "
        f"pages {unit.get('page_start')}-{unit.get('page_end')}, "
        f"`{unit.get('output_yaml')}`"
    )


def generate_project_stats(entries: list[dict]) -> str:
    source_index = load_yaml(SOURCE_INDEX_PATH)
    state = load_processing_state()
    processed_units = source_index.get("processed_units") or []
    by_book = Counter(str(entry.get("_book") or "Unknown") for entry in entries)
    by_era = Counter(str(entry.get("era_classification") or "unknown") for entry in entries)
    by_reference = Counter(str(entry.get("reference_type") or "unknown") for entry in entries)
    explicit_count = by_reference.get("explicit_hogwarts_a_history", 0)
    duplicate_count = sum(
        1
        for entry in entries
        if isinstance(entry.get("duplicate_check"), dict)
        and entry["duplicate_check"].get("possible_duplicate") is True
    )

    lines = ["# Project Stats", ""]
    lines.extend(["## Processed Source Units", "", f"- Total: {len(processed_units)}", ""])
    lines.extend(["## Entries by Book", "", *counter_lines(by_book), ""])
    lines.extend(["## Entries by Era Classification", "", *counter_lines(by_era), ""])
    lines.extend(["## Entries by Reference Type", "", *counter_lines(by_reference), ""])
    lines.extend(["## Explicit `Hogwarts: A History` References", "", f"- Total: {explicit_count}", ""])
    lines.extend(["## Possible Duplicates", "", f"- Total: {duplicate_count}", ""])
    lines.extend(
        [
            "## Latest Processed Unit",
            "",
            f"- {unit_summary(state.get('last_completed_source_unit') or {})}",
            "",
            "## Next Pending Unit",
            "",
            f"- {unit_summary(state.get('current_source_unit') or {})}",
        ]
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
    write(GENERATED_DIR / "review-flags.md", generate_review_flags(entries))
    write(GENERATED_DIR / "project-stats.md", generate_project_stats(entries))
    print(f"Wrote generated appendices to {GENERATED_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
