#!/usr/bin/env python3
"""Inspect authoring chapter state, approved pointers, and recorded hashes."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = Path("authoring/editions/1984/project-control/chapter-status.yaml")


def load_state(root: Path) -> dict:
    path = root / STATUS_PATH
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict) or not isinstance(loaded.get("chapters"), list):
        raise ValueError(f"Invalid chapter status data: {path}")
    return loaded


def chapter_for(state: dict, number: int) -> dict:
    for chapter in state["chapters"]:
        if isinstance(chapter, dict) and int(chapter.get("number", -1)) == number:
            return chapter
    raise ValueError(f"Unknown chapter: {number}")


def working_manuscript(chapter: dict) -> str | None:
    working = chapter.get("working_revision") or {}
    artifacts = working.get("artifacts") or {}
    manuscript = artifacts.get("manuscript") or {}
    return manuscript.get("path")


def chapter_summary(chapter: dict) -> dict:
    approved = chapter.get("approved_manuscript") or {}
    working = chapter.get("working_revision") or {}
    return {
        "number": chapter.get("number"),
        "slug": chapter.get("slug"),
        "title": chapter.get("title"),
        "status": chapter.get("status"),
        "draft": chapter.get("draft"),
        "working_revision": working.get("revision"),
        "working_status": working.get("status"),
        "working_manuscript": working_manuscript(chapter),
        "approved_revision": approved.get("revision"),
        "approved_manuscript": approved.get("path"),
    }


def controlled_artifacts(chapter: dict) -> list[dict]:
    records = []
    approved = chapter.get("approved_manuscript")
    if isinstance(approved, dict):
        records.append({"kind": "approved_manuscript", **approved})

    working = chapter.get("working_revision") or {}
    artifacts = working.get("artifacts") or {}
    if isinstance(artifacts, dict):
        for name, artifact in artifacts.items():
            if isinstance(artifact, dict):
                records.append({"kind": f"working_{name}", **artifact})

    baselines = working.get("comparison_baselines") or []
    if isinstance(baselines, list):
        for index, baseline in enumerate(baselines, start=1):
            if isinstance(baseline, dict):
                records.append(
                    {
                        **baseline,
                        "baseline_kind": baseline.get("kind"),
                        "kind": f"comparison_baseline_{index}",
                    }
                )
    return records


def resolve_controlled_path(root: Path, value: object) -> Path:
    relative = Path(str(value or ""))
    if not value or relative.is_absolute():
        raise ValueError("recorded path must be a non-empty repository-relative path")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("recorded path escapes the repository") from exc
    return resolved


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_artifacts(root: Path, chapter: dict) -> list[dict]:
    inspected = []
    for record in controlled_artifacts(chapter):
        row = {
            "kind": record.get("kind"),
            "path": record.get("path"),
            "recorded_sha256": record.get("sha256"),
        }
        if record.get("baseline_kind"):
            row["baseline_kind"] = record.get("baseline_kind")
        try:
            path = resolve_controlled_path(root, record.get("path"))
        except ValueError as exc:
            row.update({"current_sha256": None, "status": "INVALID_PATH", "detail": str(exc)})
        else:
            if not path.is_file():
                row.update({"current_sha256": None, "status": "MISSING"})
            else:
                current = file_sha256(path)
                row.update(
                    {
                        "current_sha256": current,
                        "status": "OK" if current == record.get("sha256") else "MISMATCH",
                    }
                )
        inspected.append(row)
    return inspected


def next_chapter(state: dict) -> dict | None:
    chapters = [chapter for chapter in state["chapters"] if isinstance(chapter, dict)]
    started = [
        int(chapter["number"])
        for chapter in chapters
        if chapter.get("status") != "planned"
        or chapter.get("working_revision")
        or chapter.get("approved_manuscript")
    ]
    highest_started = max(started, default=0)
    candidates = [
        chapter
        for chapter in chapters
        if int(chapter.get("number", 0)) > highest_started and chapter.get("status") == "planned"
    ]
    return min(candidates, key=lambda row: int(row["number"])) if candidates else None


def dump(payload: dict) -> None:
    yaml.safe_dump(payload, sys.stdout, sort_keys=False, allow_unicode=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "approved", "hashes", "verify", "brief-context"):
        command = commands.add_parser(name)
        command.add_argument("chapter", type=int)
    commands.add_parser("next")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    try:
        state = load_state(root)
        if args.command == "next":
            chapter = next_chapter(state)
            dump(
                {
                    "next": chapter_summary(chapter) if chapter else None,
                    "basis": "first planned chapter after highest started chapter",
                }
            )
            return 0

        chapter = chapter_for(state, args.chapter)
        if args.command == "status":
            dump({"chapter": chapter_summary(chapter)})
            return 0
        if args.command == "approved":
            approved = chapter.get("approved_manuscript")
            if not isinstance(approved, dict):
                raise ValueError(f"Chapter {args.chapter} has no approved manuscript")
            dump({"chapter": args.chapter, "approved": approved})
            return 0
        if args.command in {"hashes", "verify"}:
            rows = inspect_artifacts(root, chapter)
            key = "artifacts" if args.command == "hashes" else "verification"
            dump({"chapter": args.chapter, key: rows})
            if args.command == "verify" and any(row["status"] != "OK" for row in rows):
                return 1
            return 0
        if args.command == "brief-context":
            prior = [
                {
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "approved_manuscript": (item.get("approved_manuscript") or {}).get("path"),
                }
                for item in state["chapters"]
                if isinstance(item, dict)
                and int(item.get("number", 0)) < args.chapter
                and item.get("approved_manuscript")
            ]
            dump(
                {
                    "chapter": chapter_summary(chapter),
                    "governing_documents": [
                        "authoring/AGENTS.md",
                        "authoring/shared/evidence-policy.md",
                        "authoring/shared/chapter-workflow.md",
                        "authoring/runtime/authoring-contract.md",
                        "authoring/editions/1984/drafts/draft-01/style-lock.md",
                    ],
                    "approved_prior_chapters": prior,
                    "note": "Read-only context; no brief or chapter artifact was created.",
                }
            )
            return 0
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"authoring_status.py: error: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
