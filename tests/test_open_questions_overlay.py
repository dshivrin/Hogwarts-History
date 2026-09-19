from __future__ import annotations

from copy import deepcopy
from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest

import yaml

from scripts.open_questions_overlay import (
    DEFAULT_OVERLAY_PATH,
    load_yaml,
    main,
    query_payload,
    sha256,
    build_overlay,
    questions_for_chapter,
    validate_overlay,
)


ROOT = Path(__file__).resolve().parents[1]
LEGACY = (
    ROOT
    / "resources"
    / "external"
    / "open-questions-scapping"
    / "hogwarts-open-questions-enriched.pre-restructure-2026-09-18.yaml"
)


class OpenQuestionsOverlayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.legacy = yaml.safe_load(LEGACY.read_text(encoding="utf-8"))
        cls.overlay = build_overlay(ROOT, cls.legacy)
        cls.by_id = cls.overlay["questions"]

    def test_build_preserves_every_canonical_question_id_once(self) -> None:
        canonical = yaml.safe_load(
            (ROOT / "project-control/structured-sources/open-questions.yaml").read_text(
                encoding="utf-8"
            )
        )["questions"]
        expected = [row["id"] for row in canonical]
        actual = list(self.overlay["questions"])

        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 386)
        self.assertEqual(len(set(actual)), 386)

    def test_overlay_separates_evidence_inference_and_creative_use(self) -> None:
        for row in self.overlay["questions"].values():
            self.assertEqual(
                set(row),
                {
                    "research",
                    "gap",
                    "placement",
                    "interpretation",
                },
            )
            self.assertIsInstance(row["research"]["verified_facts"], list)
            self.assertIn("historical_inference", row["interpretation"])
            self.assertIn("creative_reconstruction", row["interpretation"])

    def test_partial_answer_keeps_verified_fact_and_residual_question(self) -> None:
        row = self.by_id["sorting-ceremony-001"]

        self.assertEqual(row["research"]["status"], "partially_answered")
        self.assertEqual(
            row["research"]["verified_facts"][0]["evidence_ids"],
            ["ext-a02-001"],
        )
        self.assertIn("when", row["gap"]["residual_question"].lower())
        self.assertEqual(row["placement"]["primary_chapter_id"], 4)
        self.assertIn(13, row["placement"]["secondary_chapter_ids"])

    def test_decisive_later_evidence_is_not_left_research_pending(self) -> None:
        expected = {
            "protective-magic-and-security-115": "ootp-ch37-005",
            "protective-magic-and-security-116": "ootp-ch06-007",
            "protective-magic-and-security-117": "ootp-ch32-007",
        }
        for question_id, evidence_id in expected.items():
            row = self.by_id[question_id]
            self.assertEqual(row["research"]["status"], "answered_later_context")
            evidence_ids = {
                item
                for fact in row["research"]["verified_facts"]
                for item in fact["evidence_ids"]
            }
            self.assertIn(evidence_id, evidence_ids)
            self.assertEqual(row["interpretation"]["body_eligibility"], "later_context_only")

    def test_unreviewed_questions_assert_no_facts_or_creative_solution(self) -> None:
        row = self.by_id["great-hall-ceiling-001"]

        self.assertEqual(row["research"]["status"], "local_search_required")
        self.assertEqual(row["research"]["verified_facts"], [])
        self.assertEqual(
            row["interpretation"]["creative_reconstruction"],
            "prohibited_until_research_review",
        )

    def test_source_catalog_distinguishes_local_and_unverified_sources(self) -> None:
        sources = self.overlay["source_catalog"]

        self.assertEqual(sources["A11"]["availability"], "already_extracted")
        self.assertEqual(sources["A11"]["authority"], "A")
        self.assertEqual(sources["W-HALL"]["availability"], "candidate_unverified")
        self.assertIsNone(sources["W-HALL"]["canonical_source_id"])

    def test_every_question_uses_an_authoritative_chapter_id(self) -> None:
        chapter_ids = {
            chapter["id"]
            for chapter in yaml.safe_load(
                (ROOT / "authoring/editions/1984/table-of-contents.yaml").read_text(
                    encoding="utf-8"
                )
            )["chapters"]
        }
        self.assertEqual(chapter_ids, set(range(1, 21)))
        for row in self.overlay["questions"].values():
            self.assertIn(row["placement"]["primary_chapter_id"], chapter_ids)
            self.assertTrue(
                set(row["placement"]["secondary_chapter_ids"]).issubset(chapter_ids)
            )

    def test_validator_accepts_built_overlay(self) -> None:
        self.assertEqual(validate_overlay(ROOT, self.overlay), [])

    def test_checked_in_overlay_matches_builder_output(self) -> None:
        checked_in = yaml.safe_load(
            (ROOT / DEFAULT_OVERLAY_PATH).read_text(encoding="utf-8")
        )

        self.assertEqual(checked_in, self.overlay)

    def test_chapter_query_includes_primary_and_secondary_destinations(self) -> None:
        rows = questions_for_chapter(self.overlay, 13)
        ids = set(rows)

        self.assertIn("sorting-ceremony-001", ids)
        self.assertIn("feasts-and-school-traditions-006", ids)
        self.assertNotIn("source-processing-001", ids)

    def test_validator_rejects_invalid_records(self):
        # Each mutation breaks a consumer-facing integrity guarantee.
        cases = [
            (("canonical_questions", "sha256"), "wrong"),
            (("canonical_questions", "version"), -1),
            (("questions", "sorting-ceremony-001", "question"), "duplicated wording"),
            (("questions", "sorting-ceremony-001", "research", "verified_facts"), []),
            (("questions", "sorting-ceremony-001", "research", "verified_facts"), [{"statement": "claim", "evidence_ids": ["missing"]}]),
            (("questions", "sorting-ceremony-001", "research", "local_source_ids"), ["W-HALL"]),
            (("questions", "sorting-ceremony-001", "research", "external_candidate_ids"), ["A02"]),
            (("questions", "sorting-ceremony-001", "research", "query_tags"), []),
            (("questions", "sorting-ceremony-001", "research", "next_action"), " "),
            (("questions", "sorting-ceremony-001", "gap", "residual_question"), " "),
            (("questions", "sorting-ceremony-001", "gap", "status"), "invented"),
            (("questions", "sorting-ceremony-001", "placement", "primary_chapter_id"), 21),
            (("questions", "sorting-ceremony-001", "placement", "secondary_chapter_ids"), [21]),
            (("questions", "sorting-ceremony-001", "interpretation", "author_question"), "invented"),
            (("questions", "protective-magic-and-security-115", "interpretation", "body_eligibility"), "requires_access_review"),
            (("questions", "house-elves-and-hogwarts-001", "interpretation", "body_eligibility"), "requires_access_review"),
            (("questions", "source-processing-001", "interpretation", "body_eligibility"), "requires_access_review"),
            (("source_catalog", "P-NOVELS", "local_paths"), ["missing.pdf"]),
            (("source_catalog", "A02", "canonical_source_id"), "A03"),
            (("source_catalog", "A02", "evidence_yaml"), "AGENTS.md"),
            (("source_catalog", "A02", "snapshot_path"), "AGENTS.md"),
        ]
        for keys, value in cases:
            with self.subTest(keys=keys):
                overlay = deepcopy(self.overlay)
                target = overlay
                for key in keys[:-1]:
                    target = target[key]
                target[keys[-1]] = value
                self.assertTrue(validate_overlay(ROOT, overlay))

    def test_validator_rejects_reordered_and_missing_ids(self):
        overlay = deepcopy(self.overlay)
        first = next(iter(overlay["questions"]))
        row = overlay["questions"].pop(first)
        self.assertTrue(validate_overlay(ROOT, overlay))
        overlay["questions"][first] = row
        self.assertTrue(validate_overlay(ROOT, overlay))

    def test_malformed_sections_return_diagnostics(self):
        for section in ("research", "gap", "placement", "interpretation"):
            with self.subTest(section=section):
                overlay = deepcopy(self.overlay)
                overlay["questions"]["sorting-ceremony-001"][section] = ["bad"]
                self.assertTrue(validate_overlay(ROOT, overlay))

    def test_duplicate_yaml_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.yaml"
            path.write_text("questions:\n  same: {}\n  same: {}\n")
            with self.assertRaises(ValueError):
                load_yaml(path)

    def test_migrate_accepts_an_absolute_output_path(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "overlay.yaml"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = main(
                    [
                        "--root",
                        str(ROOT),
                        "migrate",
                        "--legacy",
                        str(LEGACY),
                        "--output",
                        str(output),
                    ]
                )

            self.assertEqual(result, 0)
            self.assertTrue(output.exists())
            self.assertIn(str(output), stdout.getvalue())

    def test_rebuild_uses_canonical_wording_for_unreviewed_gap(self):
        legacy = deepcopy(self.legacy)
        row = next(row for row in legacy["questions"] if row["id"] == "great-hall-ceiling-001")
        row["question"] = "Stale legacy wording"
        built = build_overlay(ROOT, legacy)
        self.assertEqual(built["questions"][row["id"]]["gap"]["residual_question"], self.by_id[row["id"]]["gap"]["residual_question"])

    def test_query_joins_canonical_wording(self):
        payload = query_payload(ROOT, self.overlay, 13)
        row = next(row for row in payload["questions"] if row["id"] == "sorting-ceremony-001")
        canonical = load_yaml(ROOT / "project-control/structured-sources/open-questions.yaml")
        original = next(row for row in canonical["questions"] if row["id"] == "sorting-ceremony-001")
        self.assertEqual(row["question"], original["question"])
        self.assertEqual(payload["question_count"], len(payload["questions"]))

    def test_backup_hashes_match_pre_restructure_originals(self):
        self.assertEqual(sha256(LEGACY), "96424a5640b3e22ba03672d5dd28f52eb867e9d905f86ebd604a7229d2d6cb3a")
        guide = LEGACY.with_name("hogwarts-open-questions-codex-guide.pre-restructure-2026-09-18.md")
        self.assertEqual(sha256(guide), "5b29d22d711b0b9934e35c0a49e017de1868e97374085258bafe05b1557227d5")

    def test_reviewed_admissions_preserves_known_registration_answer(self):
        row = self.by_id["pre-hogwarts-historical-context-017"]
        ids = {item for fact in row["research"]["verified_facts"] for item in fact["evidence_ids"]}
        self.assertTrue({"ext-a03-004", "ext-a03-005"}.issubset(ids))
        self.assertNotIn("birth-time", row["gap"]["residual_question"])

    def test_world_cup_security_is_not_misclassified_as_triwizard(self):
        row = self.by_id["protective-magic-and-security-113"]
        self.assertEqual(row["placement"]["primary_chapter_id"], 15)
        self.assertIn(17, row["placement"]["secondary_chapter_ids"])

    def test_mirror_mechanism_remains_partial_later_context(self):
        row = self.by_id["protective-magic-and-security-033"]

        self.assertEqual(row["research"]["status"], "partially_answered")
        self.assertTrue(row["gap"]["residual_question"])
        self.assertEqual(
            row["interpretation"]["body_eligibility"], "later_context_only"
        )
        self.assertEqual(
            row["interpretation"]["creative_reconstruction"], "prohibited"
        )

    def test_every_question_has_local_sources_to_inspect(self):
        for question_id, row in self.by_id.items():
            self.assertTrue(row["research"]["local_source_ids"], question_id)


if __name__ == "__main__":
    unittest.main()
