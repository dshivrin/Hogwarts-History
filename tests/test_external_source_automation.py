from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib
from pathlib import Path
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "resources" / "manifests" / "external-sources.yaml"
RUNTIME_ARCHIVE_PATH = (
    ROOT
    / "docs"
    / "instructions"
    / "archive"
    / "runtime-contract-book-and-companion-extraction-2026-08-15.md"
)
PRE_REPLACEMENT_RUNTIME_SHA256 = (
    "915e08fd144c21a850b7c4998a13dbb8868a4022aa0c6cc0fb813d35c2517e67"
)


def load_yaml(path: Path) -> dict:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise AssertionError(f"expected YAML mapping in {path}")
    return loaded


def snapshot_parts(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"missing front matter in {path}")
    _, header, body = text.split("---\n", 2)
    metadata = yaml.safe_load(header) or {}
    return metadata, body.lstrip("\n")


def queue_module():
    try:
        return importlib.import_module("scripts.external_sources.queue")
    except ModuleNotFoundError as exc:
        raise AssertionError("external queue controller must be implemented") from exc


def write_test_manifest(root: Path, count: int = 5) -> Path:
    records = []
    for number in range(1, count + 1):
        logical_id = f"A{number:02d}"
        records.append(
            {
                "id": f"external-{logical_id}",
                "logical_id": logical_id,
                "title": f"Source {logical_id}",
                "source_class": "official_rowling_original",
                "authority": "A",
                "local_path": f"resources/external/{logical_id.lower()}.md",
            }
        )
    manifest_path = root / "resources/manifests/external-sources.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        yaml.safe_dump({"schema_version": 1, "sources": records}, sort_keys=False),
        encoding="utf-8",
    )
    return manifest_path


class RuntimeBackupAndManifestTests(unittest.TestCase):
    def test_runtime_archive_preserves_pre_replacement_contract(self) -> None:
        self.assertTrue(RUNTIME_ARCHIVE_PATH.is_file())
        archive_hash = hashlib.sha256(RUNTIME_ARCHIVE_PATH.read_bytes()).hexdigest()
        self.assertEqual(archive_hash, PRE_REPLACEMENT_RUNTIME_SHA256)

    def test_capture_completeness_replaces_ambiguous_key_without_body_changes(self) -> None:
        manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
        manifest = load_yaml(MANIFEST_PATH)
        records = manifest["sources"]

        self.assertEqual(len(records), 63)
        self.assertNotIn("\n    completeness:", manifest_text)
        expected_ids = {f"A{number:02d}" for number in range(1, 38)} | {
            f"B{number:02d}" for number in range(1, 27)
        }
        self.assertEqual({record["logical_id"] for record in records}, expected_ids)

        for record in records:
            self.assertEqual(record["capture_completeness"], "complete")
            snapshot_path = ROOT / record["local_path"]
            metadata, body = snapshot_parts(snapshot_path)
            body_without_title = body.split("\n\n", 1)[1].rstrip("\n")
            self.assertEqual(metadata["capture_completeness"], "complete")
            self.assertNotIn("completeness", metadata)
            self.assertEqual(
                hashlib.sha256(body_without_title.encode("utf-8")).hexdigest(),
                record["sha256"],
                record["logical_id"],
            )


class SourceDiscoveryAndRenderingTests(unittest.TestCase):
    def test_discovery_returns_book_and_external_yaml_in_stable_order(self) -> None:
        try:
            source_files = importlib.import_module("scripts.source_files")
        except ModuleNotFoundError:
            self.fail("scripts.source_files must provide canonical source discovery")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            relative_paths = [
                "sources/external/official-rowling/a01-example.yaml",
                "sources/book-01/chapter-01-example.yaml",
                "sources/external/interviews/b01-example.yaml",
                "sources/ignored/example.yaml",
            ]
            for relative_path in relative_paths:
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("source_unit: {}\nentries: []\n", encoding="utf-8")

            discovered = [
                path.relative_to(root).as_posix()
                for path in source_files.discover_source_yaml(root)
            ]

        self.assertEqual(
            discovered,
            [
                "sources/book-01/chapter-01-example.yaml",
                "sources/external/interviews/b01-example.yaml",
                "sources/external/official-rowling/a01-example.yaml",
            ],
        )

    def test_book_seed_renders_web_provenance_without_pdf_none(self) -> None:
        generate_book_seed = importlib.import_module("scripts.generate_book_seed")
        entry = {
            "id": "ext-a01-001",
            "source_id": "A01",
            "source_url": "https://example.test/a01",
            "_output_yaml": "sources/external/official-rowling/a01-example.yaml",
            "_book": None,
            "_chapter": None,
            "pdf_page": None,
        }

        rendered = generate_book_seed.format_source_line(entry)

        self.assertEqual(
            rendered,
            "Source: A01, https://example.test/a01, "
            "`sources/external/official-rowling/a01-example.yaml`",
        )
        self.assertNotIn("PDF p. None", rendered)

    def test_appendix_explicit_reference_renders_web_provenance(self) -> None:
        appendices = importlib.import_module("scripts.generate_appendices")
        entry = {
            "id": "ext-a01-001",
            "source_id": "A01",
            "source_url": "https://example.test/a01",
            "_output_yaml": "sources/external/official-rowling/a01-example.yaml",
            "_book": None,
            "_chapter": None,
            "reference_type": "explicit_hogwarts_a_history",
            "pdf_page": None,
            "era_classification": "pre_1984_historical_candidate",
            "confidence": "high",
        }

        rendered = appendices.generate_explicit_references([entry])

        self.assertIn("Source: A01, https://example.test/a01", rendered)
        self.assertNotIn("PDF p. None", rendered)

    def test_appendix_review_label_uses_external_source_metadata(self) -> None:
        appendices = importlib.import_module("scripts.generate_appendices")
        entry = {
            "id": "ext-a01-001",
            "source_id": "A01",
            "source_note": "Founder-era Chamber evidence.",
            "_book": None,
            "_chapter": None,
            "_source_title": "Chamber of Secrets",
        }

        rendered = appendices.entry_label(entry)

        self.assertEqual(
            rendered,
            "`ext-a01-001` (A01, Chamber of Secrets): Founder-era Chamber evidence.",
        )
        self.assertNotIn("(None, None)", rendered)

    def test_appendix_loader_preserves_external_source_title(self) -> None:
        appendices = importlib.import_module("scripts.generate_appendices")

        entries = appendices.load_entries()
        a01_entry = next(entry for entry in entries if entry.get("id") == "ext-a01-001")

        self.assertEqual(a01_entry.get("_source_title"), "Chamber of Secrets")

    def test_project_stats_renders_external_queue_unit_without_page_placeholders(self) -> None:
        appendices = importlib.import_module("scripts.generate_appendices")
        source_index = {"processed_units": []}
        state = {
            "external_processing": {
                "last_completed_unit": {
                    "id": "A01",
                    "title": "Chamber of Secrets",
                    "input_path": "resources/external/a01.md",
                    "output_file": "sources/external/a01.yaml",
                },
                "next_pending_unit": {
                    "id": "A02",
                    "title": "The Sorting Hat",
                    "input_path": "resources/external/a02.md",
                    "output_file": "sources/external/a02.yaml",
                },
            },
            "last_completed_source_unit": {"book": "The Tales of Beedle the Bard"},
            "current_source_unit": None,
        }

        original_load_yaml = appendices.load_yaml
        original_load_processing_state = appendices.load_processing_state
        appendices.load_yaml = lambda path: source_index
        appendices.load_processing_state = lambda: state
        try:
            rendered = appendices.generate_project_stats(
                [
                    {
                        "id": "ext-a01-001",
                        "source_id": "A01",
                        "source_url": "https://example.test/a01",
                        "_book": None,
                        "_chapter": None,
                        "_source_title": "Chamber of Secrets",
                        "era_classification": "pre_1984_historical_candidate",
                        "reference_type": "historical_claim",
                        "duplicate_check": {"possible_duplicate": False},
                    }
                ]
            )
        finally:
            appendices.load_yaml = original_load_yaml
            appendices.load_processing_state = original_load_processing_state

        self.assertIn(
            "- `A02` — The Sorting Hat, input `resources/external/a02.md`, "
            "output `sources/external/a02.yaml`",
            rendered,
        )
        self.assertIn("- A01 — Chamber of Secrets: 1", rendered)
        self.assertNotIn("Unknown", rendered)
        self.assertNotIn("pages None-None", rendered)


class ExternalValidationTests(unittest.TestCase):
    def write_external_fixture(
        self,
        root: Path,
        *,
        content_sha256: str | None = None,
        pdf_page: int | None = None,
    ) -> Path:
        body = "Evidence body."
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        snapshot_relative = "resources/external/a01-example.md"
        snapshot = root / snapshot_relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_text(
            "---\n"
            "id: A01\n"
            "capture_completeness: complete\n"
            f"sha256: {digest}\n"
            "---\n\n"
            "# Example\n\n"
            f"{body}\n",
            encoding="utf-8",
        )
        output = root / "sources/external/official-rowling/a01-example.yaml"
        output.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "source_unit": {
                "source_kind": "external_markdown",
                "source_id": "A01",
                "source_file": snapshot_relative,
                "title": "Example",
                "author": "J.K. Rowling",
                "source_site": "Example",
                "source_class": "official_rowling_original",
                "authority": "A",
                "publication_date": "2015-08-10",
                "original_url": "https://example.test/a01",
                "retrieval_url": "https://example.test/a01",
                "capture_completeness": "complete",
                "content_sha256": content_sha256 or digest,
                "processed_date": "2026-08-15",
                "processor_notes": "Complete snapshot read.",
            },
            "entries": [
                {
                    "id": "ext-a01-001",
                    "source_file": snapshot_relative,
                    "source_id": "A01",
                    "source_url": "https://example.test/a01",
                    "source_section": None,
                    "pdf_page": pdf_page,
                    "printed_page": None,
                    "extracted_text_lines": None,
                    "text_anchor": {
                        "start_phrase": "Evidence",
                        "end_phrase": "body.",
                        "local_occurrence_note": "Only body paragraph.",
                    },
                    "nearby_context": "Example context.",
                    "match_terms": ["evidence"],
                    "quote_excerpt_short": "Evidence body.",
                    "source_note": "The source contains evidence.",
                    "reference_type": "historical_claim",
                    "era_classification": "pre_1984_historical_candidate",
                    "topic_tags": ["hogwarts", "history", "example"],
                    "candidate_part": "Origins",
                    "candidate_chapter": "Example chapter",
                    "candidate_section": "Example section",
                    "reason_for_placement": "It is historical evidence.",
                    "relevance_to_hogwarts_a_history": "Supports the example section.",
                    "duplicate_check": {
                        "possible_duplicate": False,
                        "duplicate_of": None,
                        "notes": "Indexed lookup found no match.",
                    },
                    "confidence": "high",
                    "limitations": "Test carrier only.",
                }
            ],
        }
        output.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return output

    def validate_fixture(self, root: Path) -> list[str]:
        validator = importlib.import_module("scripts.validate_source_yaml")
        return validator.validate_source_files(
            root,
            False,
            {"historical_claim"},
            {"pre_1984_historical_candidate"},
        )

    def test_valid_external_yaml_with_web_locators_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_external_fixture(root)
            errors = self.validate_fixture(root)

        self.assertEqual(errors, [])

    def test_external_hash_mismatch_and_pdf_locator_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_external_fixture(root, content_sha256="0" * 64, pdf_page=7)
            errors = self.validate_fixture(root)

        joined = "\n".join(errors)
        self.assertIn("content_sha256 does not match snapshot body", joined)
        self.assertIn("pdf_page must be null for external evidence", joined)

    def test_external_entries_are_counted_with_book_entries(self) -> None:
        validator = importlib.import_module("scripts.validate_source_yaml")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_external_fixture(root)
            count = validator.count_source_entries(root)

        self.assertEqual(count, 1)


class QueueGenerationTests(unittest.TestCase):
    def test_manifest_builds_exact_deterministic_63_unit_queue(self) -> None:
        queue = queue_module()
        manifest = load_yaml(MANIFEST_PATH)

        units = queue.build_units(manifest)

        expected_ids = [f"A{number:02d}" for number in range(1, 38)] + [
            f"B{number:02d}" for number in range(1, 27)
        ]
        self.assertEqual([unit["id"] for unit in units], expected_ids)
        self.assertEqual(len({unit["input_path"] for unit in units}), 63)
        self.assertEqual(len({unit["output_file"] for unit in units}), 63)
        self.assertEqual(len({unit["manifest_id"] for unit in units}), 63)
        for unit in units:
            self.assertEqual(unit["status"], "pending")
            self.assertEqual(unit["attempts"], 0)
            self.assertIsNone(unit["claimed_by"])
            self.assertIsNone(unit["claim_token"])
            self.assertIsNone(unit["claimed_at"])
            self.assertIsNone(unit["completed_at"])
            self.assertIsNone(unit["blocked_reason"])
            self.assertEqual(unit["validation_status"], "not_run")
            self.assertEqual(unit["update_profile"], "canonical_external_evidence")


class QueueTransitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        control = self.root / "project-control"
        control.mkdir(parents=True)
        (control / "source-plan.yaml").write_text(
            yaml.safe_dump(
                {
                    "project": {"name": "test"},
                    "current_phase": "book-complete",
                    "sources": [{"book_group": "book-01", "chapters": []}],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        (control / "processing-state.yaml").write_text(
            yaml.safe_dump(
                {"last_completed_source_unit": {"book_group": "book-01"}},
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        write_test_manifest(self.root)
        self.queue = queue_module()
        self.controller = self.queue.QueueController(self.root)
        self.controller.initialize()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_simultaneous_claims_are_unique_and_fifth_claim_is_rejected(self) -> None:
        with ThreadPoolExecutor(max_workers=2) as executor:
            first, second = list(
                executor.map(
                    lambda agent: self.queue.QueueController(self.root).claim(agent),
                    ["worker-one", "worker-two"],
                )
            )
        self.assertNotEqual(first["id"], second["id"])

        self.controller.claim("worker-three")
        self.controller.claim("worker-four")
        before = (self.root / "project-control/source-plan.yaml").read_bytes()
        with self.assertRaisesRegex(self.queue.QueueError, "four units are already in progress"):
            self.controller.claim("worker-five")
        after = (self.root / "project-control/source-plan.yaml").read_bytes()
        self.assertEqual(before, after)

    def test_claim_tokens_gate_release_and_block_transitions(self) -> None:
        claimed = self.controller.claim("worker", unit_id="A01")
        with self.assertRaisesRegex(self.queue.QueueError, "claim token"):
            self.controller.release("A01", "stale-token", "interrupted")

        released = self.controller.release(
            "A01", claimed["claim_token"], "worker interrupted"
        )
        self.assertEqual(released["status"], "pending")
        self.assertEqual(released["history"][-1]["event"], "released")

        claimed_again = self.controller.claim("worker", unit_id="A01")
        with self.assertRaisesRegex(self.queue.QueueError, "non-empty reason"):
            self.controller.block("A01", claimed_again["claim_token"], " ")
        blocked = self.controller.block(
            "A01", claimed_again["claim_token"], "snapshot provenance is ambiguous"
        )
        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(blocked["blocked_reason"], "snapshot provenance is ambiguous")

    def test_completion_failure_leaves_unit_in_progress(self) -> None:
        claimed = self.controller.claim("worker", unit_id="A01")

        with self.assertRaisesRegex(self.queue.QueueError, "output YAML does not exist"):
            self.controller.complete(
                "A01", claimed["claim_token"], runner=lambda commands, root: None
            )

        unit = self.controller.unit("A01")
        self.assertEqual(unit["status"], "in_progress")
        self.assertEqual(unit["validation_status"], "not_run")

    def test_successful_completion_marks_only_claimed_unit_done(self) -> None:
        claimed = self.controller.claim("worker", unit_id="A01")
        output = self.root / claimed["output_file"]
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            yaml.safe_dump(
                {
                    "source_unit": {"source_kind": "external_markdown"},
                    "entries": [
                        {
                            "id": "ext-a01-001",
                            "topic_tags": ["hogwarts", "history", "example"],
                            "duplicate_check": {
                                "possible_duplicate": False,
                                "duplicate_of": None,
                                "notes": "Indexed lookup found no match.",
                            },
                        }
                    ],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

        completed = self.controller.complete(
            "A01", claimed["claim_token"], runner=lambda commands, root: None
        )

        self.assertEqual(completed["status"], "done")
        self.assertEqual(completed["validation_status"], "passed")
        self.assertIsNone(completed["claim_token"])
        self.assertEqual(self.controller.unit("A02")["status"], "pending")
        status = self.controller.status()
        self.assertEqual(status["counts"], {"pending": 4, "in_progress": 0, "done": 1, "blocked": 0})
        self.assertEqual(status["next_pending_unit"]["id"], "A02")


class ExternalQueueDisplayTests(unittest.TestCase):
    def test_next_run_renders_external_counts_and_next_unit(self) -> None:
        update_next_run = importlib.import_module("scripts.update_next_run")
        state = {
            "external_processing": {
                "total_units": 63,
                "counts": {
                    "pending": 63,
                    "in_progress": 0,
                    "done": 0,
                    "blocked": 0,
                },
                "active_units": [],
                "next_pending_unit": {
                    "id": "A01",
                    "title": "Chamber of Secrets",
                    "input_path": "resources/external/a01.md",
                    "output_file": "sources/external/official-rowling/a01.yaml",
                },
                "last_completed_unit": None,
            },
            "last_completed_source_unit": {"book": "The Tales of Beedle the Bard"},
            "current_source_unit": None,
        }

        rendered = update_next_run.render_next_run(state)

        self.assertIn("## External Source Queue", rendered)
        self.assertIn("- Pending: 63", rendered)
        self.assertIn("`A01` — Chamber of Secrets", rendered)
        self.assertNotIn("No pending source unit remains", rendered)


if __name__ == "__main__":
    unittest.main()
