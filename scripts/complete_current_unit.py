#!/usr/bin/env python3
"""Complete one current PDF unit with rollback-safe generated artifacts."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Callable

import yaml

try:
    from scripts.external_sources.artifact_snapshot import CompletionArtifactSnapshot
except ModuleNotFoundError:  # Direct script execution.
    from external_sources.artifact_snapshot import CompletionArtifactSnapshot


ROOT = Path(__file__).resolve().parents[1]
CommandRunner = Callable[[list[list[str]], Path], None]


class CompletionError(RuntimeError):
    """Raised when the current unit cannot pass every completion gate."""


def load_mapping(path: Path) -> dict:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError as exc:
        raise CompletionError(f"required file does not exist: {path}") from exc
    if not isinstance(loaded, dict):
        raise CompletionError(f"expected YAML mapping in {path}")
    return loaded


def default_runner(commands: list[list[str]], root: Path) -> None:
    for command in commands:
        subprocess.run(command, cwd=root, check=True, text=True)


def completion_commands(root: Path) -> list[list[str]]:
    python = (
        str(root / ".venv/bin/python")
        if (root / ".venv/bin/python").is_file()
        else sys.executable
    )
    return [
        [python, "scripts/build_duplicate_index.py"],
        [python, "scripts/build_entry_index.py"],
        [python, "scripts/build_tag_index.py"],
        [python, "scripts/validate_source_yaml.py"],
        [python, "scripts/update_next_run.py", "--advance-after-success"],
        [python, "scripts/generate_book_seed.py"],
        [python, "scripts/generate_appendices.py"],
        [python, "scripts/update_next_run.py"],
        [python, "scripts/cleanup_tmp.py"],
        [python, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
    ]


def validate_assigned_output(current: dict, output: dict, output_path: Path) -> None:
    source_unit = output.get("source_unit") or {}
    expected = {
        "source_file": current.get("source_file"),
        "book": current.get("book"),
        "chapter": current.get("chapter_title"),
        "chapter_start_pdf_page": current.get("page_start"),
        "chapter_end_pdf_page": current.get("page_end"),
    }
    for key, value in expected.items():
        if source_unit.get(key) != value:
            raise CompletionError(
                f"current output {key} does not match assigned unit in {output_path}"
            )


def complete(root: Path = ROOT, *, runner: CommandRunner = default_runner) -> dict:
    resolved = root.resolve()
    state_path = resolved / "project-control" / "processing-state.yaml"
    state = load_mapping(state_path)
    current = state.get("current_source_unit")
    if not isinstance(current, dict):
        raise CompletionError("processing-state.yaml has no current source unit")

    output_value = str(current.get("output_yaml") or "")
    output_path = resolved / output_value
    if not output_value or not output_path.is_file():
        raise CompletionError(f"current output YAML does not exist: {output_path}")
    output = load_mapping(output_path)
    if not isinstance(output.get("source_unit"), dict):
        raise CompletionError(f"current output lacks source_unit mapping: {output_path}")
    if not isinstance(output.get("entries"), list):
        raise CompletionError(f"current output lacks entries list: {output_path}")
    validate_assigned_output(current, output, output_path)

    snapshot = CompletionArtifactSnapshot.capture(resolved)
    try:
        runner(completion_commands(resolved), resolved)
    except Exception as exc:
        snapshot.restore()
        raise CompletionError(f"completion gate failed; controls restored: {exc}") from exc
    return current


def main() -> int:
    try:
        completed = complete()
    except CompletionError as exc:
        print(f"complete_current_unit.py: error: {exc}", file=sys.stderr)
        return 1
    print(
        "Completed exactly one source unit: "
        f"{completed.get('unit_id') or completed.get('chapter_title')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
