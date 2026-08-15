#!/usr/bin/env python3
"""Lock-safe work queue for canonical external-source evidence extraction."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import fcntl
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import threading
from typing import Callable, Iterator

import yaml

IMPORT_ROOT = Path(__file__).resolve().parents[2]
if str(IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(IMPORT_ROOT))

try:
    from scripts import query_duplicates, validate_source_yaml
    from scripts.external_sources.artifact_snapshot import CompletionArtifactSnapshot
except ModuleNotFoundError:  # Direct script execution.
    from artifact_snapshot import CompletionArtifactSnapshot
    import query_duplicates
    import validate_source_yaml


ROOT = IMPORT_ROOT
MAX_IN_PROGRESS = 4
_THREAD_LOCK = threading.Lock()


class QueueError(RuntimeError):
    """Raised when a queue command cannot make the requested transition."""


CommandRunner = Callable[[list[list[str]], Path], None]


def load_yaml(path: Path) -> dict:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError as exc:
        raise QueueError(f"required YAML does not exist: {path}") from exc
    if not isinstance(loaded, dict):
        raise QueueError(f"expected YAML mapping in {path}")
    return loaded


def atomic_write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _unit_sort_key(record: dict) -> tuple[str, int]:
    logical_id = str(record.get("logical_id") or "")
    if len(logical_id) != 3 or logical_id[0] not in {"A", "B"}:
        raise QueueError(f"invalid external logical_id: {logical_id!r}")
    try:
        number = int(logical_id[1:])
    except ValueError as exc:
        raise QueueError(f"invalid external logical_id: {logical_id!r}") from exc
    return logical_id[0], number


def build_units(manifest: dict) -> list[dict]:
    records = manifest.get("sources") or []
    if not isinstance(records, list):
        raise QueueError("external manifest sources must be a list")
    units: list[dict] = []
    seen_ids: set[str] = set()
    seen_inputs: set[str] = set()
    seen_outputs: set[str] = set()
    seen_manifest_ids: set[str] = set()

    for record in sorted(records, key=_unit_sort_key):
        if not isinstance(record, dict):
            raise QueueError("external manifest records must be mappings")
        logical_id = str(record.get("logical_id") or "")
        manifest_id = str(record.get("id") or "")
        input_path = str(record.get("local_path") or "")
        if not manifest_id or not input_path:
            raise QueueError(f"manifest record {logical_id} lacks id or local_path")
        source_class = str(record.get("source_class") or "")
        output_group = (
            "official-rowling"
            if source_class == "official_rowling_original"
            else "interviews"
        )
        output_file = (
            Path("sources/external") / output_group / f"{Path(input_path).stem}.yaml"
        ).as_posix()
        staging_file = (Path("work/external-staging") / f"{logical_id.lower()}.yaml").as_posix()
        unit = {
            "id": logical_id,
            "title": record.get("title"),
            "source_kind": "external_markdown",
            "source_class": source_class,
            "authority": record.get("authority"),
            "input_path": input_path,
            "manifest_id": manifest_id,
            "output_file": output_file,
            "staging_file": staging_file,
            "status": "pending",
            "claimed_by": None,
            "claim_token": None,
            "claimed_at": None,
            "completed_at": None,
            "attempts": 0,
            "validation_status": "not_run",
            "blocked_reason": None,
            "update_profile": "canonical_external_evidence",
            "history": [],
        }
        if logical_id in seen_ids:
            raise QueueError(f"duplicate queue unit id: {logical_id}")
        if input_path in seen_inputs:
            raise QueueError(f"duplicate queue input_path: {input_path}")
        if output_file in seen_outputs:
            raise QueueError(f"duplicate queue output_file: {output_file}")
        if manifest_id in seen_manifest_ids:
            raise QueueError(f"duplicate queue manifest_id: {manifest_id}")
        seen_ids.add(logical_id)
        seen_inputs.add(input_path)
        seen_outputs.add(output_file)
        seen_manifest_ids.add(manifest_id)
        units.append(unit)
    return units


def unit_summary(unit: dict, *, include_token: bool = False) -> dict:
    keys = [
        "id",
        "title",
        "status",
        "input_path",
        "output_file",
        "staging_file",
        "manifest_id",
        "claimed_by",
        "claimed_at",
    ]
    if include_token:
        keys.append("claim_token")
    return {key: unit.get(key) for key in keys}


def derive_external_state(units: list[dict]) -> dict:
    counts = {status: 0 for status in ("pending", "in_progress", "done", "blocked")}
    for unit in units:
        status = str(unit.get("status") or "")
        if status not in counts:
            raise QueueError(f"unit {unit.get('id')} has invalid status {status!r}")
        counts[status] += 1
    active = [unit_summary(unit) for unit in units if unit.get("status") == "in_progress"]
    next_pending = next((unit for unit in units if unit.get("status") == "pending"), None)
    completed = [unit for unit in units if unit.get("status") == "done"]
    last_completed = max(
        completed,
        key=lambda unit: (str(unit.get("completed_at") or ""), str(unit.get("id") or "")),
        default=None,
    )
    return {
        "total_units": len(units),
        "counts": counts,
        "active_units": active,
        "next_pending_unit": unit_summary(next_pending) if next_pending else None,
        "last_completed_unit": unit_summary(last_completed) if last_completed else None,
    }


def render_external_next_run(status: dict) -> str:
    counts = status["counts"]
    next_unit = status.get("next_pending_unit")
    active_units = status.get("active_units") or []
    lines = [
        "# Next Run",
        "",
        "Generated display only. Source of truth: `project-control/source-plan.yaml`.",
        "",
        "## External Source Queue",
        "",
        f"- Total: {status['total_units']}",
        f"- Pending: {counts['pending']}",
        f"- In progress: {counts['in_progress']}",
        f"- Done: {counts['done']}",
        f"- Blocked: {counts['blocked']}",
        "",
    ]
    if active_units:
        lines.extend(["## Active Claims", ""])
        for unit in active_units:
            lines.append(f"- `{unit['id']}` claimed by `{unit.get('claimed_by')}`")
        lines.append("")
    lines.extend(["## Next Pending Unit", ""])
    if next_unit:
        lines.extend(
            [
                f"- Unit: `{next_unit['id']}` — {next_unit.get('title')}",
                f"- Input: `{next_unit.get('input_path')}`",
                f"- Output: `{next_unit.get('output_file')}`",
                "",
                "Claim it with `just claim-external <agent> <unit>`.",
            ]
        )
    else:
        lines.append("No pending external source remains.")
    lines.extend(
        [
            "",
            "## Minimal Context",
            "",
            "Use the active runtime contract and compact query commands. Do not scan all source YAML files.",
            "",
        ]
    )
    return "\n".join(lines)


def default_runner(commands: list[list[str]], root: Path) -> None:
    for command in commands:
        result = subprocess.run(command, cwd=root, text=True)
        if result.returncode:
            raise QueueError(
                f"completion command failed ({result.returncode}): {' '.join(command)}"
            )


class QueueController:
    def __init__(self, root: Path = ROOT) -> None:
        self.root = Path(root).resolve()
        self.plan_path = self.root / "project-control/source-plan.yaml"
        self.state_path = self.root / "project-control/processing-state.yaml"
        self.next_run_path = self.root / "project-control/next-run.md"
        self.manifest_path = self.root / "resources/manifests/external-sources.yaml"
        self.lock_path = self.root / "project-control/.external-queue.lock"

    @contextmanager
    def _lock(self) -> Iterator[None]:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with _THREAD_LOCK:
            with self.lock_path.open("a+", encoding="utf-8") as handle:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    @staticmethod
    def _units(plan: dict) -> list[dict]:
        external = plan.get("external_sources")
        if not isinstance(external, dict):
            raise QueueError("source plan has no external_sources queue; run init")
        units = external.get("units")
        if not isinstance(units, list):
            raise QueueError("external_sources.units must be a list")
        return units

    @staticmethod
    def _find_unit(units: list[dict], unit_id: str) -> dict:
        normalized = unit_id.upper()
        for unit in units:
            if unit.get("id") == normalized:
                return unit
        raise QueueError(f"unknown external unit: {unit_id}")

    @staticmethod
    def _verify_claim(unit: dict, token: str) -> None:
        if unit.get("status") != "in_progress":
            raise QueueError(f"unit {unit.get('id')} is not in progress")
        if not token or not secrets.compare_digest(str(unit.get("claim_token") or ""), token):
            raise QueueError(f"claim token does not own unit {unit.get('id')}")

    def _sync_state(self, plan: dict) -> dict:
        units = self._units(plan)
        status = derive_external_state(units)
        state = load_yaml(self.state_path) if self.state_path.exists() else {}
        state["external_processing"] = {
            "phase": "external-source-extraction",
            "manifest": "resources/manifests/external-sources.yaml",
            "max_in_progress": int(
                plan["external_sources"].get("max_in_progress") or MAX_IN_PROGRESS
            ),
            **deepcopy(status),
        }
        state["current_source_unit"] = (
            deepcopy(status["active_units"][0]) if status["active_units"] else None
        )
        state["next_source_unit"] = deepcopy(status["next_pending_unit"])
        if status["last_completed_unit"]:
            state["last_completed_external_source_unit"] = status["last_completed_unit"]
        rules = state.setdefault("automation_rules", {})
        rules.update(
            {
                "process_one_unit_per_run": True,
                "max_external_units_in_progress": MAX_IN_PROGRESS,
                "index_first_duplicate_lookup": True,
                "workers_write_assigned_yaml_only": True,
                "completion_updates_generated_outputs": True,
            }
        )
        atomic_write_yaml(self.state_path, state)
        atomic_write_text(self.next_run_path, render_external_next_run(status))
        return status

    def initialize(self) -> dict:
        with self._lock():
            plan = load_yaml(self.plan_path)
            manifest = load_yaml(self.manifest_path)
            generated_units = build_units(manifest)
            existing = plan.get("external_sources")
            if isinstance(existing, dict) and isinstance(existing.get("units"), list):
                existing_ids = [unit.get("id") for unit in existing["units"]]
                generated_ids = [unit.get("id") for unit in generated_units]
                if existing_ids != generated_ids:
                    raise QueueError("existing external queue does not match manifest IDs")
                units = existing["units"]
                for unit, generated in zip(units, generated_units):
                    unit.setdefault("staging_file", generated["staging_file"])
            else:
                units = generated_units
            plan["current_phase"] = "external-source-extraction"
            plan["external_sources"] = {
                "schema_version": 1,
                "generated_from": "resources/manifests/external-sources.yaml",
                "max_in_progress": MAX_IN_PROGRESS,
                "update_profiles": {
                    "canonical_external_evidence": {
                        "rebuild_indexes": True,
                        "regenerate_book_seed": True,
                        "regenerate_appendices": True,
                        "update_next_run": True,
                    }
                },
                "units": units,
            }
            atomic_write_yaml(self.plan_path, plan)
            self._sync_state(plan)
            return deepcopy(plan["external_sources"])

    def unit(self, unit_id: str) -> dict:
        with self._lock():
            plan = load_yaml(self.plan_path)
            return deepcopy(self._find_unit(self._units(plan), unit_id))

    def status(self) -> dict:
        with self._lock():
            plan = load_yaml(self.plan_path)
            return derive_external_state(self._units(plan))

    def current(self, unit_id: str | None = None) -> dict | list[dict] | None:
        with self._lock():
            plan = load_yaml(self.plan_path)
            units = self._units(plan)
            if unit_id:
                return unit_summary(self._find_unit(units, unit_id), include_token=True)
            active = [
                unit_summary(unit, include_token=True)
                for unit in units
                if unit.get("status") == "in_progress"
            ]
            if active:
                return active
            pending = next((unit for unit in units if unit.get("status") == "pending"), None)
            return unit_summary(pending) if pending else None

    def claim(self, agent: str, unit_id: str | None = None) -> dict:
        if not agent.strip():
            raise QueueError("agent identifier must be non-empty")
        with self._lock():
            plan = load_yaml(self.plan_path)
            units = self._units(plan)
            maximum = int(plan["external_sources"].get("max_in_progress") or MAX_IN_PROGRESS)
            active_count = sum(unit.get("status") == "in_progress" for unit in units)
            if active_count >= maximum:
                raise QueueError(f"four units are already in progress (limit {maximum})")
            if unit_id:
                unit = self._find_unit(units, unit_id)
                if unit.get("status") != "pending":
                    raise QueueError(f"unit {unit.get('id')} is not pending")
            else:
                unit = next((row for row in units if row.get("status") == "pending"), None)
                if unit is None:
                    raise QueueError("no pending external unit remains")
            timestamp = now_utc()
            unit.update(
                {
                    "status": "in_progress",
                    "claimed_by": agent.strip(),
                    "claim_token": secrets.token_urlsafe(24),
                    "claimed_at": timestamp,
                    "completed_at": None,
                    "blocked_reason": None,
                    "attempts": int(unit.get("attempts") or 0) + 1,
                    "validation_status": "not_run",
                }
            )
            unit.setdefault("history", []).append(
                {"event": "claimed", "at": timestamp, "agent": agent.strip()}
            )
            atomic_write_yaml(self.plan_path, plan)
            self._sync_state(plan)
            return deepcopy(unit)

    def release(self, unit_id: str, token: str, reason: str) -> dict:
        if not reason.strip():
            raise QueueError("release requires a non-empty reason")
        with self._lock():
            plan = load_yaml(self.plan_path)
            unit = self._find_unit(self._units(plan), unit_id)
            self._verify_claim(unit, token)
            timestamp = now_utc()
            unit.setdefault("history", []).append(
                {"event": "released", "at": timestamp, "reason": reason.strip()}
            )
            unit.update(
                {
                    "status": "pending",
                    "claimed_by": None,
                    "claim_token": None,
                    "claimed_at": None,
                    "validation_status": "not_run",
                    "blocked_reason": None,
                }
            )
            atomic_write_yaml(self.plan_path, plan)
            self._sync_state(plan)
            return deepcopy(unit)

    def block(self, unit_id: str, token: str, reason: str) -> dict:
        if not reason.strip():
            raise QueueError("block requires a non-empty reason")
        with self._lock():
            plan = load_yaml(self.plan_path)
            unit = self._find_unit(self._units(plan), unit_id)
            self._verify_claim(unit, token)
            timestamp = now_utc()
            unit.setdefault("history", []).append(
                {"event": "blocked", "at": timestamp, "reason": reason.strip()}
            )
            unit.update(
                {
                    "status": "blocked",
                    "claimed_by": None,
                    "claim_token": None,
                    "claimed_at": None,
                    "validation_status": "not_run",
                    "blocked_reason": reason.strip(),
                }
            )
            atomic_write_yaml(self.plan_path, plan)
            self._sync_state(plan)
            return deepcopy(unit)

    def _verify_duplicate_metadata(
        self, output: dict, output_path: Path
    ) -> None:
        source_unit = output.get("source_unit")
        entries = output.get("entries")
        if not isinstance(source_unit, dict) or not isinstance(entries, list):
            raise QueueError(f"invalid source YAML structure: {output_path}")
        completing_ids = {
            str(entry.get("id") or "") for entry in entries if isinstance(entry, dict)
        }
        for index, entry in enumerate(entries, start=1):
            if not isinstance(entry, dict):
                raise QueueError(f"entry {index} is not a mapping in {output_path}")
            duplicate = entry.get("duplicate_check")
            if not isinstance(duplicate, dict):
                raise QueueError(
                    f"entry {entry.get('id') or index} lacks duplicate-check metadata"
                )
            audit = duplicate.get("audit")
            if not isinstance(audit, dict):
                raise QueueError(
                    f"entry {entry.get('id') or index} lacks structured duplicate audit"
                )
            query_tags = audit.get("query_tags")
            reviews = audit.get("candidates")
            if (
                not isinstance(query_tags, list)
                or not query_tags
                or not all(isinstance(tag, str) and tag.strip() for tag in query_tags)
            ):
                raise QueueError(
                    f"entry {entry.get('id') or index} has invalid duplicate audit query_tags"
                )
            if not isinstance(reviews, list):
                raise QueueError(
                    f"entry {entry.get('id') or index} lacks structured candidates"
                )
            reviewed_ids: list[str] = []
            dispositions: list[str] = []
            allowed_dispositions = {"duplicate", "corroborating", "distinct"}
            for review in reviews:
                if not isinstance(review, dict):
                    raise QueueError(
                        f"entry {entry.get('id') or index} candidate review must be a mapping"
                    )
                candidate_id = str(review.get("id") or "").strip()
                disposition = str(review.get("disposition") or "").strip()
                if not candidate_id:
                    raise QueueError(
                        f"entry {entry.get('id') or index} candidate review lacks id"
                    )
                if disposition not in allowed_dispositions:
                    raise QueueError(
                        f"entry {entry.get('id') or index} has invalid candidate disposition"
                    )
                reviewed_ids.append(candidate_id)
                dispositions.append(disposition)
            if len(reviewed_ids) != len(set(reviewed_ids)):
                raise QueueError(
                    f"entry {entry.get('id') or index} candidate review IDs must be unique"
                )
            query_result = query_duplicates.query_candidates(
                self.root,
                tags=[tag.strip() for tag in query_tags],
                limit=10,
            )
            expected_ids = [
                str(row.get("entry_id") or "")
                for row in query_result.get("matches") or []
                if str(row.get("entry_id") or "") not in completing_ids
            ]
            if reviewed_ids != expected_ids:
                raise QueueError(
                    f"entry {entry.get('id') or index} audit does not match latest "
                    "ranked candidate list"
                )
            duplicate_ids = [
                candidate_id
                for candidate_id, disposition in zip(reviewed_ids, dispositions)
                if disposition == "duplicate"
            ]
            possible_duplicate = duplicate.get("possible_duplicate")
            if not isinstance(possible_duplicate, bool):
                raise QueueError(
                    f"entry {entry.get('id') or index} possible_duplicate must be boolean"
                )
            if possible_duplicate is not bool(duplicate_ids):
                raise QueueError(
                    f"entry {entry.get('id') or index} possible_duplicate disagrees "
                    "with duplicate dispositions"
                )
            targets = validate_source_yaml.duplicate_targets(duplicate.get("duplicate_of"))
            if targets != duplicate_ids:
                raise QueueError(
                    f"entry {entry.get('id') or index} duplicate_of disagrees "
                    "with duplicate dispositions"
                )

    def _manifest_record(self, unit: dict) -> dict:
        manifest = load_yaml(self.manifest_path)
        matches = [
            record
            for record in manifest.get("sources") or []
            if isinstance(record, dict)
            and record.get("logical_id") == unit.get("id")
            and record.get("id") == unit.get("manifest_id")
        ]
        if len(matches) != 1:
            raise QueueError(f"manifest has no unique record for unit {unit.get('id')}")
        return matches[0]

    def _verify_assigned_output(self, unit: dict, output: dict, output_path: Path) -> None:
        source_unit = output.get("source_unit")
        entries = output.get("entries")
        if not isinstance(source_unit, dict) or not isinstance(entries, list):
            raise QueueError(f"invalid source YAML structure: {output_path}")
        record = self._manifest_record(unit)
        expected = {
            "source_kind": "external_markdown",
            "source_id": unit.get("id"),
            "source_file": record.get("local_path"),
            "title": record.get("title"),
            "author": record.get("author"),
            "source_site": record.get("source_site"),
            "source_class": record.get("source_class"),
            "authority": record.get("authority"),
            "publication_date": record.get("publication_date"),
            "original_url": record.get("original_url"),
            "retrieval_url": record.get("retrieval_url"),
            "capture_completeness": record.get("capture_completeness"),
            "content_sha256": record.get("sha256"),
        }
        for key, value in expected.items():
            if source_unit.get(key) != value:
                raise QueueError(
                    f"{output_path}: source_unit {key} does not match claimed carrier"
                )
        allowed_urls = {str(record.get("original_url") or ""), str(record.get("retrieval_url") or "")}
        for index, entry in enumerate(entries, start=1):
            if not isinstance(entry, dict):
                raise QueueError(f"{output_path}: entry {index} is not a mapping")
            if entry.get("source_id") != unit.get("id"):
                raise QueueError(f"{output_path}: entry {index} source_id does not match claimed unit")
            if entry.get("source_file") != record.get("local_path"):
                raise QueueError(f"{output_path}: entry {index} source_file does not match claimed carrier")
            if str(entry.get("source_url") or "") not in allowed_urls:
                raise QueueError(f"{output_path}: entry {index} source_url does not match claimed carrier")

    def _validate_staged_output(self, output: dict, output_path: Path) -> None:
        source_unit = output.get("source_unit") or {}
        entries = output.get("entries") or []
        rel_path = output_path.relative_to(self.root).as_posix()
        errors = validate_source_yaml.validate_external_source_unit(
            self.root, rel_path, source_unit, entries
        )
        for index, entry in enumerate(entries, start=1):
            if not isinstance(entry, dict):
                continue
            label = f"{rel_path}: entry {index}"
            missing = sorted(validate_source_yaml.ENTRY_REQUIRED - set(entry))
            if missing:
                errors.append(f"{label}: missing {', '.join(missing)}")
            if entry.get("confidence") not in validate_source_yaml.CONFIDENCE_VALUES:
                errors.append(f"{label}: invalid confidence {entry.get('confidence')!r}")
            if validate_source_yaml.word_count(entry.get("quote_excerpt_short")) >= 25:
                errors.append(f"{label}: quote_excerpt_short must be under 25 words")
            tag_count = len(entry.get("topic_tags") or []) if isinstance(entry.get("topic_tags"), list) else 0
            if tag_count < 3 or tag_count > 8:
                errors.append(f"{label}: strict topic_tags count must be 3-8")
        if errors:
            raise QueueError("staged output validation failed: " + "; ".join(errors))

    def complete(
        self,
        unit_id: str,
        token: str,
        *,
        runner: CommandRunner = default_runner,
    ) -> dict:
        with self._lock():
            plan = load_yaml(self.plan_path)
            unit = self._find_unit(self._units(plan), unit_id)
            self._verify_claim(unit, token)
            output_path = self.root / str(unit.get("output_file") or "")
            staging_path = self.root / str(unit.get("staging_file") or "")
            if not staging_path.is_file():
                raise QueueError(f"staged output YAML does not exist: {staging_path}")
            if output_path.exists():
                raise QueueError(f"canonical output path already exists: {output_path}")
            promoted = False
            completed_successfully = False
            artifact_snapshot: CompletionArtifactSnapshot | None = None
            try:
                output = load_yaml(staging_path)
                self._verify_assigned_output(unit, output, staging_path)
                self._validate_staged_output(output, staging_path)
                artifact_snapshot = CompletionArtifactSnapshot.capture(self.root)
                python = (
                    str(self.root / ".venv/bin/python")
                    if (self.root / ".venv/bin/python").exists()
                    else sys.executable
                )
                runner([[python, "scripts/validate_source_yaml.py"]], self.root)
                runner(
                    [
                        [python, "scripts/build_duplicate_index.py"],
                        [python, "scripts/build_tag_index.py"],
                    ],
                    self.root,
                )
                self._verify_duplicate_metadata(output, staging_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                os.replace(staging_path, output_path)
                promoted = True
                runner(
                    [
                        [python, "scripts/build_duplicate_index.py"],
                        [python, "scripts/build_entry_index.py"],
                        [python, "scripts/build_tag_index.py"],
                        [python, "scripts/validate_source_yaml.py"],
                    ],
                    self.root,
                )
                timestamp = now_utc()
                unit.setdefault("history", []).append(
                    {"event": "completed", "at": timestamp}
                )
                unit.update(
                    {
                        "status": "done",
                        "claimed_by": None,
                        "claim_token": None,
                        "claimed_at": None,
                        "completed_at": timestamp,
                        "validation_status": "passed",
                        "blocked_reason": None,
                    }
                )
                atomic_write_yaml(self.plan_path, plan)
                self._sync_state(plan)
                runner(
                    [
                        [python, "scripts/generate_book_seed.py"],
                        [python, "scripts/generate_appendices.py"],
                    ],
                    self.root,
                )
                completed_successfully = True
                return deepcopy(unit)
            except QueueError:
                raise
            except Exception as exc:
                raise QueueError(f"completion gate failed: {exc}") from exc
            finally:
                if artifact_snapshot is not None and not completed_successfully:
                    if promoted:
                        os.replace(output_path, staging_path)
                    artifact_snapshot.restore()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init")

    claim = subparsers.add_parser("claim")
    claim.add_argument("--agent", required=True)
    claim.add_argument("--unit")

    current = subparsers.add_parser("current")
    current.add_argument("--unit")

    for name in ("complete", "release", "block"):
        command = subparsers.add_parser(name)
        command.add_argument("--unit", required=True)
        command.add_argument("--claim-token", required=True)
        if name in {"release", "block"}:
            command.add_argument("--reason", required=True)
    subparsers.add_parser("status")
    return parser


def print_yaml(payload: object) -> None:
    print(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).rstrip())


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    controller = QueueController(args.root)
    try:
        if args.command == "init":
            payload = controller.initialize()
            print_yaml({"units": len(payload["units"]), "status": "initialized"})
        elif args.command == "claim":
            print_yaml(controller.claim(args.agent, args.unit))
        elif args.command == "current":
            print_yaml(controller.current(args.unit))
        elif args.command == "complete":
            print_yaml(controller.complete(args.unit, args.claim_token))
        elif args.command == "release":
            print_yaml(controller.release(args.unit, args.claim_token, args.reason))
        elif args.command == "block":
            print_yaml(controller.block(args.unit, args.claim_token, args.reason))
        else:
            print_yaml(controller.status())
    except QueueError as exc:
        print(f"external queue: error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
