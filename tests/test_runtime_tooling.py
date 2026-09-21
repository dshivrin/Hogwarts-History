from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]


def import_required(name: str):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as exc:
        raise AssertionError(f"required module is missing: {name}") from exc


class ProjectDoctorTests(unittest.TestCase):
    def make_root(self, directory: str) -> Path:
        root = Path(directory)
        python = root / ".venv" / "bin" / "python"
        python.parent.mkdir(parents=True)
        python.write_text("#!/bin/sh\n", encoding="utf-8")
        python.chmod(0o755)
        for relative in (
            "AGENTS.md",
            "Justfile",
            "requirements.txt",
            "docs/instructions/runtime-contract.md",
            "authoring/AGENTS.md",
            "authoring/runtime/authoring-contract.md",
            "authoring/editions/1984/project-control/chapter-status.yaml",
            "scripts/query_entries.py",
            "scripts/query_duplicates.py",
        ):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n", encoding="utf-8")
        (root / "sources").mkdir()
        return root

    @staticmethod
    def healthy_probe(path: Path) -> dict[str, str]:
        return {"python": "3.9.6", "yaml": "6.0.3", "pypdf": "6.13.1"}

    @staticmethod
    def required_cli(name: str) -> str | None:
        return f"/fixture/{name}" if name in {"rg", "jq", "just"} else None

    def test_healthy_environment_passes_without_optional_yq(self) -> None:
        doctor = import_required("scripts.project_doctor")
        with tempfile.TemporaryDirectory() as directory:
            checks = doctor.run_checks(
                self.make_root(directory),
                which=self.required_cli,
                probe_python=self.healthy_probe,
            )

        self.assertFalse([check for check in checks if check.required and not check.ok])
        self.assertTrue(next(check for check in checks if check.label == "yq").ok is False)

    def test_missing_venv_fails(self) -> None:
        doctor = import_required("scripts.project_doctor")
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / ".venv" / "bin" / "python").unlink()
            checks = doctor.run_checks(
                root,
                which=self.required_cli,
                probe_python=self.healthy_probe,
            )

        self.assertFalse(next(check for check in checks if check.label == "Python environment").ok)

    def test_missing_required_import_fails(self) -> None:
        doctor = import_required("scripts.project_doctor")
        with tempfile.TemporaryDirectory() as directory:
            checks = doctor.run_checks(
                self.make_root(directory),
                which=self.required_cli,
                probe_python=lambda path: {"python": "3.9.6", "yaml": "6.0.3"},
            )

        self.assertFalse(next(check for check in checks if check.label == "pypdf").ok)

    def test_missing_required_cli_fails(self) -> None:
        doctor = import_required("scripts.project_doctor")
        with tempfile.TemporaryDirectory() as directory:
            checks = doctor.run_checks(
                self.make_root(directory),
                which=lambda name: None if name == "jq" else f"/fixture/{name}",
                probe_python=self.healthy_probe,
            )

        self.assertFalse(next(check for check in checks if check.label == "jq").ok)

    def test_missing_required_path_fails(self) -> None:
        doctor = import_required("scripts.project_doctor")
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / "authoring/runtime/authoring-contract.md").unlink()
            checks = doctor.run_checks(
                root,
                which=self.required_cli,
                probe_python=self.healthy_probe,
            )

        self.assertFalse(next(check for check in checks if check.label == "Authoring contract").ok)


class EvidenceQueryExtensionTests(unittest.TestCase):
    def write_index(self, root: Path) -> None:
        control = root / "project-control"
        control.mkdir(parents=True)
        (control / "entry-index.yaml").write_text(
            yaml.safe_dump(
                {
                    "by_entry": {
                        "ext-a17-001": {
                            "title": "Pensieve",
                            "classification": "pre_1984_historical_candidate",
                            "reference_type": "historical_claim",
                            "confidence": "high",
                            "tags": ["founders", "memory"],
                            "source_unit": "A17",
                            "output_yaml": "sources/external/official-rowling/a17-pensieve.yaml",
                        },
                        "ps-ch07-001": {
                            "title": "The Sorting Hat: Founders",
                            "classification": "original_book_core_candidate",
                            "reference_type": "historical_claim",
                            "confidence": "high",
                            "tags": ["founders", "sorting-hat"],
                            "source_unit": "ps-ch07",
                            "output_yaml": "sources/book-01/chapter-07-sorting-hat.yaml",
                        },
                        "ps-ch01-999": {
                            "title": "Sorting Hat Mention",
                            "classification": "harry_era_confirmation",
                            "reference_type": "institutional_custom",
                            "confidence": "medium",
                            "tags": ["sorting-hat"],
                            "source_unit": "ps-ch01",
                            "output_yaml": "sources/book-01/chapter-01-boy-who-lived.yaml",
                        },
                    }
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

    def query(self, *arguments: str) -> dict:
        query_entries = import_required("scripts.query_entries")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_index(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                result = query_entries.main(["--root", str(root), *arguments])
            self.assertEqual(result, 0)
            return yaml.safe_load(stdout.getvalue())

    def test_query_by_exact_id(self) -> None:
        payload = self.query("--id", "ext-a17-001")
        self.assertEqual([row["entry_id"] for row in payload["matches"]], ["ext-a17-001"])

    def test_query_by_source(self) -> None:
        payload = self.query("--source", "A17")
        self.assertEqual([row["entry_id"] for row in payload["matches"]], ["ext-a17-001"])
        self.assertEqual(payload["query"]["source"], "A17")

    def test_query_by_chapter_or_source_unit(self) -> None:
        payload = self.query("--chapter", "chapter-07")
        self.assertEqual([row["entry_id"] for row in payload["matches"]], ["ps-ch07-001"])

    def test_repeated_tags_require_all_tags(self) -> None:
        payload = self.query("--tag", "founders", "--tag", "sorting-hat")
        self.assertEqual([row["entry_id"] for row in payload["matches"]], ["ps-ch07-001"])
        self.assertEqual(payload["query"]["tags"], ["founders", "sorting-hat"])


class AuthoringStatusTests(unittest.TestCase):
    def write_state(self, root: Path) -> None:
        chapter_root = root / "authoring/editions/1984/drafts/draft-01/chapters"
        approved = chapter_root / "01-before-hogwarts/draft-revision-01.md"
        working = chapter_root / "05-slytherin/draft-revision-01.md"
        approved.parent.mkdir(parents=True)
        working.parent.mkdir(parents=True)
        approved.write_text("approved\n", encoding="utf-8")
        working.write_text("working\n", encoding="utf-8")
        import hashlib

        approved_hash = hashlib.sha256(approved.read_bytes()).hexdigest()
        working_hash = hashlib.sha256(working.read_bytes()).hexdigest()
        state = {
            "allowed_statuses": ["planned", "drafted", "editor_approved"],
            "chapters": [
                {
                    "id": 1,
                    "number": 1,
                    "slug": "before-hogwarts",
                    "title": "Before Hogwarts",
                    "status": "editor_approved",
                    "draft": "draft-01",
                    "approved_manuscript": {
                        "revision": 1,
                        "path": approved.relative_to(root).as_posix(),
                        "sha256": approved_hash,
                    },
                },
                {
                    "id": 5,
                    "number": 5,
                    "slug": "slytherin",
                    "title": "Slytherin",
                    "status": "drafted",
                    "draft": "draft-01",
                    "working_revision": {
                        "revision": 1,
                        "status": "drafted",
                        "artifacts": {
                            "manuscript": {
                                "path": working.relative_to(root).as_posix(),
                                "sha256": working_hash,
                            }
                        },
                        "comparison_baselines": [
                            {
                                "chapter": 1,
                                "revision": 1,
                                "kind": "approved",
                                "path": approved.relative_to(root).as_posix(),
                                "sha256": approved_hash,
                            }
                        ],
                    },
                },
                {
                    "id": 6,
                    "number": 6,
                    "slug": "castle",
                    "title": "Castle",
                    "status": "planned",
                    "draft": "draft-01",
                },
            ],
        }
        path = root / "authoring/editions/1984/project-control/chapter-status.yaml"
        path.parent.mkdir(parents=True)
        path.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")

    def run_cli(self, root: Path, *arguments: str) -> tuple[int, str, str]:
        authoring = import_required("scripts.authoring_status")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = authoring.main(["--root", str(root), *arguments])
        return result, stdout.getvalue(), stderr.getvalue()

    def test_status_reports_working_and_approved_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_state(root)
            result, output, _ = self.run_cli(root, "status", "5")
        payload = yaml.safe_load(output)
        self.assertEqual(result, 0)
        self.assertEqual(payload["chapter"]["status"], "drafted")
        self.assertTrue(payload["chapter"]["working_manuscript"].endswith("draft-revision-01.md"))
        self.assertIsNone(payload["chapter"]["approved_manuscript"])

    def test_next_reports_first_planned_chapter_after_started_work(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_state(root)
            result, output, _ = self.run_cli(root, "next")
        payload = yaml.safe_load(output)
        self.assertEqual(result, 0)
        self.assertEqual(payload["next"]["number"], 6)
        self.assertEqual(payload["basis"], "first planned chapter after highest started chapter")

    def test_approved_resolves_authoritative_manuscript(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_state(root)
            result, output, _ = self.run_cli(root, "approved", "1")
        payload = yaml.safe_load(output)
        self.assertEqual(result, 0)
        self.assertTrue(payload["approved"]["path"].endswith("draft-revision-01.md"))

    def test_approved_fails_when_chapter_has_no_approved_manuscript(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_state(root)
            result, _, error = self.run_cli(root, "approved", "5")
        self.assertEqual(result, 1)
        self.assertIn("no approved manuscript", error.lower())

    def test_verify_detects_hash_mismatch_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_state(root)
            manuscript = root / "authoring/editions/1984/drafts/draft-01/chapters/05-slytherin/draft-revision-01.md"
            manuscript.write_text("changed\n", encoding="utf-8")
            before = manuscript.read_bytes()
            result, output, _ = self.run_cli(root, "verify", "5")
            after = manuscript.read_bytes()
        payload = yaml.safe_load(output)
        self.assertEqual(result, 1)
        self.assertEqual(payload["verification"][0]["status"], "MISMATCH")
        self.assertEqual(before, after)

    def test_hashes_and_brief_context_are_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_state(root)
            state_path = root / "authoring/editions/1984/project-control/chapter-status.yaml"
            before = state_path.read_bytes()
            hashes_result, hashes_output, _ = self.run_cli(root, "hashes", "5")
            brief_result, brief_output, _ = self.run_cli(root, "brief-context", "6")
            after = state_path.read_bytes()
        self.assertEqual(hashes_result, 0)
        self.assertEqual(brief_result, 0)
        artifacts = yaml.safe_load(hashes_output)["artifacts"]
        self.assertEqual(artifacts[0]["status"], "OK")
        self.assertEqual(artifacts[1]["kind"], "comparison_baseline_1")
        self.assertEqual(artifacts[1]["baseline_kind"], "approved")
        self.assertEqual(yaml.safe_load(brief_output)["chapter"]["number"], 6)
        self.assertEqual(before, after)


class JustRecipeTests(unittest.TestCase):
    def dry_run(self, *arguments: str) -> str:
        result = subprocess.run(
            ["just", "--dry-run", *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout + result.stderr

    def test_new_read_only_recipes_route_to_permanent_tools(self) -> None:
        self.assertIn("scripts/project_doctor.py", self.dry_run("doctor"))
        self.assertIn("scripts/query_entries.py", self.dry_run("query", "--id", "ext-a17-001"))
        self.assertIn("authoring_status.py", self.dry_run("author-status", "5"))
        self.assertIn("authoring_status.py", self.dry_run("author-next"))
        self.assertIn("authoring_status.py", self.dry_run("chapter-approved", "1"))
        self.assertIn("authoring_status.py", self.dry_run("chapter-hashes", "5"))
        self.assertIn("authoring_status.py", self.dry_run("verify-chapter", "5"))

    def test_extraction_wrappers_keep_text_and_image_operations_separate(self) -> None:
        text_command = self.dry_run("extract-text", "book.pdf", "2", "4", "out.txt")
        image_command = self.dry_run("render-pages", "book.pdf", "2", "4", "page")
        self.assertIn("scripts/extract_pages.py", text_command)
        self.assertNotIn("pdftoppm", text_command)
        self.assertIn("pdftoppm", image_command)
        self.assertNotIn("scripts/extract_pages.py", image_command)


if __name__ == "__main__":
    unittest.main()
