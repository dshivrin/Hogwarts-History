from __future__ import annotations

import importlib
import io
from pathlib import Path
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout

import yaml


class RefactorSupportTests(unittest.TestCase):
    def test_validate_source_yaml_accepts_valid_source_file(self) -> None:
        validate_source_yaml = importlib.import_module("scripts.validate_source_yaml")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_schema_reference(root)
            source_dir = root / "sources" / "book-01"
            source_dir.mkdir(parents=True)
            (source_dir / "chapter-07-sorting-hat.yaml").write_text(
                self._source_yaml("ps-ch07-001"),
                encoding="utf-8",
            )

            self.assertEqual(validate_source_yaml.main(["--root", str(root)]), 0)

    def test_validate_source_yaml_rejects_missing_duplicate_target(self) -> None:
        validate_source_yaml = importlib.import_module("scripts.validate_source_yaml")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_schema_reference(root)
            source_dir = root / "sources" / "book-01"
            source_dir.mkdir(parents=True)
            (source_dir / "chapter-07-sorting-hat.yaml").write_text(
                self._source_yaml(
                    "ps-ch07-001",
                    duplicate_check=(
                        "    possible_duplicate: true\n"
                        "    duplicate_of: missing-id\n"
                        "    notes: Missing duplicate target.\n"
                    ),
                ),
                encoding="utf-8",
            )

            self.assertEqual(validate_source_yaml.main(["--root", str(root)]), 1)

    def test_build_tag_index_groups_entries_by_tag_with_output_paths(self) -> None:
        build_tag_index = importlib.import_module("scripts.build_tag_index")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_dir = root / "sources" / "book-01"
            source_dir.mkdir(parents=True)
            (source_dir / "chapter-07-sorting-hat.yaml").write_text(
                textwrap.dedent(
                    """
                    source_unit:
                      source_file: pdfs/harrypotter.pdf
                      book: Harry Potter and the Philosopher's Stone
                      chapter: Chapter Seven - The Sorting Hat
                    entries:
                    - id: ps-ch07-001
                      topic_tags:
                      - great-hall
                      - sorting-ceremony
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            build_tag_index.ROOT = root
            build_tag_index.SOURCES_DIR = root / "sources"
            build_tag_index.OUTPUT_PATH = root / "project-control" / "tag-index.yaml"

            self.assertEqual(build_tag_index.main(), 0)
            tag_index = yaml.safe_load(build_tag_index.OUTPUT_PATH.read_text())

        self.assertEqual(tag_index["tags"]["great-hall"]["entries"], ["ps-ch07-001"])
        self.assertEqual(
            tag_index["tags"]["great-hall"]["output_yaml"],
            ["sources/book-01/chapter-07-sorting-hat.yaml"],
        )

    def test_build_entry_index_includes_reference_type_for_queries(self) -> None:
        build_entry_index = importlib.import_module("scripts.build_entry_index")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_dir = root / "sources" / "book-01"
            source_dir.mkdir(parents=True)
            (source_dir / "chapter-07-sorting-hat.yaml").write_text(
                textwrap.dedent(
                    """
                    source_unit:
                      source_file: pdfs/harrypotter.pdf
                      book: Harry Potter and the Philosopher's Stone
                      chapter: Chapter Seven - The Sorting Hat
                    entries:
                    - id: ps-ch07-001
                      reference_type: explicit_hogwarts_a_history
                      topic_tags:
                      - great-hall
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            build_entry_index.ROOT = root
            build_entry_index.SOURCES_DIR = root / "sources"
            build_entry_index.ENTRY_INDEX_PATH = root / "project-control" / "entry-index.yaml"
            build_entry_index.SOURCE_INDEX_PATH = root / "project-control" / "source-index.yaml"

            self.assertEqual(build_entry_index.main(), 0)
            entry_index = yaml.safe_load(build_entry_index.ENTRY_INDEX_PATH.read_text())

        self.assertEqual(
            entry_index["by_entry"]["ps-ch07-001"]["reference_type"],
            "explicit_hogwarts_a_history",
        )

    def test_query_duplicates_returns_only_matching_tags(self) -> None:
        query_duplicates = importlib.import_module("scripts.query_duplicates")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_query_indexes(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(
                    query_duplicates.main(
                        [
                            "--root",
                            str(root),
                            "--tags",
                            "great-hall",
                            "enchanted-ceiling",
                        ]
                    ),
                    0,
                )
            payload = yaml.safe_load(stdout.getvalue())

        match_ids = [match["entry_id"] for match in payload["matches"]]
        self.assertIn("ps-ch07-001", match_ids)
        self.assertNotIn("ps-ch03-001", match_ids)

    def test_query_entries_filters_by_tag_and_classification(self) -> None:
        query_entries = importlib.import_module("scripts.query_entries")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_query_indexes(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(
                    query_entries.main(
                        [
                            "--root",
                            str(root),
                            "--tag",
                            "great-hall",
                            "--classification",
                            "original_book_core_candidate",
                        ]
                    ),
                    0,
                )
            payload = yaml.safe_load(stdout.getvalue())

        self.assertEqual([match["entry_id"] for match in payload["matches"]], ["ps-ch07-001"])

    def test_generate_book_seed_groups_entries_with_sources(self) -> None:
        generate_book_seed = importlib.import_module("scripts.generate_book_seed")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_dir = root / "sources" / "book-01"
            source_dir.mkdir(parents=True)
            (source_dir / "chapter-07-sorting-hat.yaml").write_text(
                self._book_seed_source_yaml(),
                encoding="utf-8",
            )

            self.assertEqual(generate_book_seed.main(["--root", str(root)]), 0)
            book_seed = (root / "book-seed" / "hogwarts-a-history-seed.md").read_text()

        self.assertIn("# Generated File", book_seed)
        self.assertIn("# Hogwarts: A History - Evidence-Backed Seed", book_seed)
        self.assertEqual(book_seed.count("## Part:"), 1)
        self.assertEqual(book_seed.count("### Chapter:"), 1)
        self.assertEqual(book_seed.count("#### Section:"), 1)
        self.assertEqual(book_seed.count("**Fact:**"), 2)
        self.assertIn("entry `ps-ch07-001`", book_seed)
        self.assertIn("`sources/book-01/chapter-07-sorting-hat.yaml`", book_seed)

    def test_generate_appendices_includes_structured_open_questions(self) -> None:
        appendices = importlib.import_module("scripts.generate_appendices")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "project-control" / "structured-sources").mkdir(parents=True)
            source_dir = root / "sources" / "book-01"
            source_dir.mkdir(parents=True)
            generated_dir = root / "appendix" / "generated"

            (root / "project-control" / "entry-index.yaml").write_text(
                "version: 1\nby_entry: {}\n", encoding="utf-8"
            )
            (root / "project-control" / "source-index.yaml").write_text(
                "version: 1\nprocessed_units: []\n", encoding="utf-8"
            )
            (root / "project-control" / "structured-sources" / "open-questions.yaml").write_text(
                textwrap.dedent(
                    """
                    version: 1
                    updated: '2026-06-21'
                    questions:
                    - id: castle-navigation-001
                      topic: Castle Navigation and Magical Architecture
                      question: 'Does Hogwarts: A History explicitly describe castle navigation beyond the Great Hall ceiling?'
                      tags:
                      - castle-navigation
                      status: open
                      source: migrated-from-appendix-open-questions
                      related_entries:
                      - ps-ch07-001
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (source_dir / "chapter-07-sorting-hat.yaml").write_text(
                textwrap.dedent(
                    """
                    source_unit:
                      book: Harry Potter and the Philosopher's Stone
                      chapter: Chapter Seven - The Sorting Hat
                    entries:
                    - id: ps-ch07-999
                      confidence: low
                      limitations: Needs corroboration.
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            appendices.ROOT = root
            appendices.SOURCES_DIR = root / "sources"
            appendices.GENERATED_DIR = generated_dir
            appendices.ENTRY_INDEX_PATH = root / "project-control" / "entry-index.yaml"
            appendices.SOURCE_INDEX_PATH = root / "project-control" / "source-index.yaml"
            appendices.STRUCTURED_OPEN_QUESTIONS_PATH = (
                root / "project-control" / "structured-sources" / "open-questions.yaml"
            )

            self.assertEqual(appendices.main(), 0)
            open_questions = (generated_dir / "open-questions.md").read_text()

        self.assertIn("Castle Navigation and Magical Architecture", open_questions)
        self.assertIn("Does Hogwarts: A History explicitly describe", open_questions)
        self.assertIn("ps-ch07-999", open_questions)

    def test_generate_appendices_includes_review_flags_and_project_stats(self) -> None:
        appendices = importlib.import_module("scripts.generate_appendices")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            generated_dir = root / "appendix" / "generated"
            source_dir = root / "sources" / "book-01"
            source_dir.mkdir(parents=True)
            (root / "project-control" / "structured-sources").mkdir(parents=True)
            (source_dir / "chapter-07-sorting-hat.yaml").write_text(
                self._appendix_flags_source_yaml(),
                encoding="utf-8",
            )
            (root / "project-control" / "entry-index.yaml").write_text(
                "version: 1\nby_entry: {}\n", encoding="utf-8"
            )
            (root / "project-control" / "source-index.yaml").write_text(
                textwrap.dedent(
                    """
                    version: 1
                    processed_units:
                    - source_unit_id: ps-ch07
                      book: Harry Potter and the Philosopher's Stone
                      chapter_title: Chapter Seven - The Sorting Hat
                      candidate_entry_count: 1
                      explicit_reference_count: 1
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (root / "project-control" / "processing-state.yaml").write_text(
                self._state_yaml(),
                encoding="utf-8",
            )
            (root / "project-control" / "structured-sources" / "open-questions.yaml").write_text(
                "version: 1\nquestions: []\n",
                encoding="utf-8",
            )

            appendices.ROOT = root
            appendices.SOURCES_DIR = root / "sources"
            appendices.GENERATED_DIR = generated_dir
            appendices.ENTRY_INDEX_PATH = root / "project-control" / "entry-index.yaml"
            appendices.SOURCE_INDEX_PATH = root / "project-control" / "source-index.yaml"
            appendices.PROCESSING_STATE_PATH = root / "project-control" / "processing-state.yaml"
            appendices.STRUCTURED_OPEN_QUESTIONS_PATH = (
                root / "project-control" / "structured-sources" / "open-questions.yaml"
            )

            self.assertEqual(appendices.main(), 0)
            review_flags = (generated_dir / "review-flags.md").read_text()
            project_stats = (generated_dir / "project-stats.md").read_text()

        for heading in [
            "## Low Confidence",
            "## Unknown Era",
            "## Possible Duplicates",
            "## Later Editorial Notes",
            "## Off-Campus Context",
            "## Limited Evidence",
            "## Schema Warnings",
        ]:
            self.assertIn(heading, review_flags)
        for text in [
            "## Processed Source Units",
            "## Entries by Book",
            "## Entries by Era Classification",
            "## Entries by Reference Type",
            "## Explicit `Hogwarts: A History` References",
            "## Possible Duplicates",
            "## Latest Processed Unit",
            "## Next Pending Unit",
            "Chapter One - The Riddle House",
            "Chapter Two - The Scar",
        ]:
            self.assertIn(text, project_stats)

    def test_update_next_run_default_only_regenerates_prompt(self) -> None:
        update_next_run = importlib.import_module("scripts.update_next_run")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            control_dir = root / "project-control"
            control_dir.mkdir()
            state_path = control_dir / "processing-state.yaml"
            next_run_path = control_dir / "next-run.md"
            state_path.write_text(self._state_yaml(), encoding="utf-8")

            update_next_run.ROOT = root
            update_next_run.PROCESSING_STATE_PATH = state_path
            update_next_run.NEXT_RUN_PATH = next_run_path
            update_next_run.CHAPTERS_INDEX_PATH = root / "chapters-index.md"
            update_next_run.SOURCE_PLAN_PATH = control_dir / "source-plan.yaml"

            self.assertEqual(update_next_run.main([]), 0)
            state = yaml.safe_load(state_path.read_text())
            next_run = next_run_path.read_text()

        self.assertEqual(state["current_source_unit"]["chapter_number"], 2)
        self.assertIn("Chapter Two - The Scar", next_run)
        self.assertIn("just query-dupes", next_run)
        self.assertNotIn("scripts/query_duplicates.py", next_run)
        self.assertNotIn("Open full index files", next_run)
        self.assertNotIn("project-control/entry-index.yaml`", next_run)

    def test_update_next_run_advances_after_valid_current_output(self) -> None:
        update_next_run = importlib.import_module("scripts.update_next_run")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            control_dir = root / "project-control"
            control_dir.mkdir()
            state_path = control_dir / "processing-state.yaml"
            next_run_path = control_dir / "next-run.md"
            state_path.write_text(self._state_yaml(), encoding="utf-8")
            output_yaml = root / "sources" / "book-04" / "chapter-02-the-scar.yaml"
            output_yaml.parent.mkdir(parents=True)
            output_yaml.write_text(
                textwrap.dedent(
                    """
                    source_unit:
                      book: Harry Potter and the Goblet of Fire
                      chapter: Chapter Two - The Scar
                    entries:
                    - id: gof-ch02-001
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (root / "chapters-index.md").write_text(
                textwrap.dedent(
                    """
                    - book: 4, chapter: 2, title: The Scar, pages: 961-968
                    - book: 4, chapter: 3, title: The Invitation, pages: 969-978
                    - book: 4, chapter: 4, title: Back to the Burrow, pages: 979-988
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (control_dir / "source-plan.yaml").write_text(
                textwrap.dedent(
                    """
                    sources:
                    - book_group: book-04
                      book: Harry Potter and the Goblet of Fire
                      chapters:
                      - number: 2
                        title: Chapter Two - The Scar
                        status: pending
                        output_file: sources/book-04/chapter-02-the-scar.yaml
                      - number: 3
                        title: Chapter Three - The Invitation
                        status: pending
                        output_file: sources/book-04/chapter-03-the-invitation.yaml
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            update_next_run.ROOT = root
            update_next_run.PROCESSING_STATE_PATH = state_path
            update_next_run.NEXT_RUN_PATH = next_run_path
            update_next_run.CHAPTERS_INDEX_PATH = root / "chapters-index.md"
            update_next_run.SOURCE_PLAN_PATH = control_dir / "source-plan.yaml"

            self.assertEqual(update_next_run.main(["--advance-after-success"]), 0)
            state = yaml.safe_load(state_path.read_text())
            source_plan = yaml.safe_load((control_dir / "source-plan.yaml").read_text())

        self.assertEqual(state["last_completed_source_unit"]["chapter_number"], 2)
        self.assertEqual(state["current_source_unit"]["chapter_number"], 3)
        self.assertEqual(state["next_source_unit"]["chapter_number"], 4)
        self.assertEqual(source_plan["sources"][0]["chapters"][0]["status"], "complete")

    def test_runtime_contract_uses_compact_cli_workflow(self) -> None:
        contract = Path("docs/instructions/runtime-contract.md").read_text(encoding="utf-8")

        self.assertIn("## CLI Workflow", contract)
        for text in [
            "just brief",
            "just next",
            "just search",
            "just query-dupes",
            "just query-entries",
            "just validate",
            "just post",
            "Do not require `yq`",
        ]:
            self.assertIn(text, contract)

        self.assertIn("3. Run `just post`.", contract)
        self.assertNotIn("`scripts/query_duplicates.py` for duplicate and context lookup", contract)
        self.assertNotIn("`scripts/query_entries.py` for " "compact entry lookup", contract)
        for text in [
            ".venv/bin/python scripts/build_duplicate_index.py",
            ".venv/bin/python scripts/build_entry_index.py",
            ".venv/bin/python scripts/build_tag_index.py",
            ".venv/bin/python scripts/validate_source_yaml.py",
            ".venv/bin/python scripts/generate_book_seed.py",
            ".venv/bin/python scripts/generate_appendices.py",
            ".venv/bin/python scripts/update_next_run.py",
            ".venv/bin/python scripts/cleanup_tmp.py",
        ]:
            self.assertNotIn(text, contract)

    def test_justfile_exposes_compact_workflow_recipes(self) -> None:
        justfile = Path("Justfile").read_text(encoding="utf-8")

        for recipe in [
            "brief:",
            "test:",
            "indexes:",
            "generate:",
            "post:",
            "query-dupes *tags:",
            "query-entries tag:",
        ]:
            self.assertIn(recipe, justfile)

    def _state_yaml(self) -> str:
        return (
            textwrap.dedent(
                """
                project:
                  mode: minimal_context
                last_completed_source_unit:
                  source_file: pdfs/harrypotter.pdf
                  book_group: book-04
                  book: Harry Potter and the Goblet of Fire
                  chapter_number: 1
                  chapter_title: Chapter One - The Riddle House
                  page_start: 949
                  page_end: 960
                  output_yaml: sources/book-04/chapter-01-the-riddle-house.yaml
                current_source_unit:
                  source_file: pdfs/harrypotter.pdf
                  book_group: book-04
                  book: Harry Potter and the Goblet of Fire
                  chapter_number: 2
                  chapter_title: Chapter Two - The Scar
                  page_start: 961
                  page_end: 968
                  extracted_text_path: .tmp/current-chapter.txt
                  output_yaml: sources/book-04/chapter-02-the-scar.yaml
                next_source_unit:
                  source_file: pdfs/harrypotter.pdf
                  book_group: book-04
                  book: Harry Potter and the Goblet of Fire
                  chapter_number: 3
                  chapter_title: Chapter Three - The Invitation
                  page_start: 969
                  page_end: 978
                  output_yaml: sources/book-04/chapter-03-the-invitation.yaml
                """
            ).strip()
            + "\n"
        )

    def _write_schema_reference(self, root: Path) -> None:
        instructions = root / "docs" / "instructions"
        instructions.mkdir(parents=True)
        (instructions / "schema-reference.md").write_text(
            textwrap.dedent(
                """
                # Schema Reference

                ## Reference Types

                Use only:

                - `explicit_hogwarts_a_history`
                - `institutional_custom`

                ## Era Classifications

                Use only:

                - `original_book_core_candidate`
                - `harry_era_confirmation`
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )

    def _source_yaml(self, entry_id: str, duplicate_check: str | None = None) -> str:
        duplicate_check = duplicate_check or (
            "    possible_duplicate: false\n"
            "    duplicate_of: null\n"
            "    notes: No duplicate found.\n"
        )
        return (
            textwrap.dedent(
                f"""
                source_unit:
                  source_file: pdfs/harrypotter.pdf
                  book: Harry Potter and the Philosopher's Stone
                  chapter: Chapter Seven - The Sorting Hat
                  chapter_start_pdf_page: 107
                  chapter_end_pdf_page: 122
                  processed_date: '2026-06-21'
                entries:
                - id: {entry_id}
                  pdf_page: 110
                  text_anchor:
                    start_phrase: First-years enter the Great Hall
                    end_phrase: bewitched to look like the sky outside
                    local_occurrence_note: One occurrence.
                  quote_excerpt_short: bewitched to look like the sky outside
                  source_note: Hermione identifies the Great Hall ceiling enchantment.
                  reference_type: explicit_hogwarts_a_history
                  era_classification: original_book_core_candidate
                  topic_tags:
                  - great-hall
                  - enchanted-ceiling
                  - magical-architecture
                  candidate_part: Magical Architecture and Enchantments
                  candidate_chapter: The Great Hall
                  candidate_section: The Enchanted Ceiling
                  duplicate_check:
                __DUPLICATE_CHECK__
                  confidence: high
                  limitations: Later books may add corroborating references.
                """
            ).strip()
            .replace("__DUPLICATE_CHECK__", duplicate_check.rstrip())
            + "\n"
        )

    def _write_query_indexes(self, root: Path) -> None:
        control = root / "project-control"
        control.mkdir(parents=True)
        (control / "tag-index.yaml").write_text(
            textwrap.dedent(
                """
                version: 1
                tags:
                  great-hall:
                    entries:
                    - ps-ch07-001
                    output_yaml:
                    - sources/book-01/chapter-07-sorting-hat.yaml
                  enchanted-ceiling:
                    entries:
                    - ps-ch07-001
                    output_yaml:
                    - sources/book-01/chapter-07-sorting-hat.yaml
                  admissions:
                    entries:
                    - ps-ch03-001
                    output_yaml:
                    - sources/book-01/chapter-03-letters-from-no-one.yaml
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )
        (control / "duplicate-index.yaml").write_text(
            textwrap.dedent(
                """
                version: 1
                entries:
                - entry_id: ps-ch07-001
                  canonical_topic: the-great-hall-the-enchanted-ceiling
                  tags:
                  - great-hall
                  - enchanted-ceiling
                  source_note: Hermione explains the Great Hall ceiling enchantment.
                  output_yaml: sources/book-01/chapter-07-sorting-hat.yaml
                - entry_id: ps-ch03-001
                  canonical_topic: admissions-acceptance-letters
                  tags:
                  - admissions
                  source_note: The first Hogwarts letter arrives.
                  output_yaml: sources/book-01/chapter-03-letters-from-no-one.yaml
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )
        (control / "entry-index.yaml").write_text(
            textwrap.dedent(
                """
                version: 1
                by_entry:
                  ps-ch07-001:
                    title: 'The Great Hall: The Enchanted Ceiling'
                    classification: original_book_core_candidate
                    reference_type: explicit_hogwarts_a_history
                    confidence: high
                    tags:
                    - great-hall
                    - enchanted-ceiling
                    source_unit: ps-ch07
                    output_yaml: sources/book-01/chapter-07-sorting-hat.yaml
                  ps-ch03-001:
                    title: 'Admissions: Acceptance Letters'
                    classification: harry_era_confirmation
                    reference_type: institutional_custom
                    confidence: medium
                    tags:
                    - admissions
                    source_unit: ps-ch03
                    output_yaml: sources/book-01/chapter-03-letters-from-no-one.yaml
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )

    def _book_seed_source_yaml(self) -> str:
        return (
            textwrap.dedent(
                """
                source_unit:
                  source_file: pdfs/harrypotter.pdf
                  book: Harry Potter and the Philosopher's Stone
                  chapter: Chapter Seven - The Sorting Hat
                  chapter_start_pdf_page: 107
                  chapter_end_pdf_page: 122
                  processed_date: '2026-06-21'
                entries:
                - id: ps-ch07-001
                  pdf_page: 110
                  text_anchor:
                    start_phrase: First-years enter the Great Hall
                    end_phrase: bewitched to look like the sky outside
                    local_occurrence_note: One occurrence.
                  quote_excerpt_short: bewitched to look like the sky outside
                  source_note: Hermione identifies the Great Hall ceiling enchantment.
                  reference_type: explicit_hogwarts_a_history
                  era_classification: original_book_core_candidate
                  topic_tags:
                  - great-hall
                  - enchanted-ceiling
                  candidate_part: Magical Architecture and Enchantments
                  candidate_chapter: The Great Hall
                  candidate_section: The Enchanted Ceiling
                  duplicate_check:
                    possible_duplicate: false
                    duplicate_of: null
                    notes: No duplicate found.
                  confidence: high
                  limitations: Later books may add corroborating references.
                - id: ps-ch07-002
                  pdf_page: 108
                  text_anchor:
                    start_phrase: The Sorting Ceremony will take place
                    end_phrase: earn your House points
                    local_occurrence_note: One occurrence.
                  quote_excerpt_short: The Sorting Ceremony will take place
                  source_note: McGonagall describes the Sorting Ceremony.
                  reference_type: institutional_custom
                  era_classification: harry_era_confirmation
                  topic_tags:
                  - sorting-ceremony
                  - house-system
                  candidate_part: Magical Architecture and Enchantments
                  candidate_chapter: The Great Hall
                  candidate_section: The Enchanted Ceiling
                  duplicate_check:
                    possible_duplicate: true
                    duplicate_of: ps-ch07-001
                    notes: Corroborates Great Hall context.
                  confidence: medium
                  limitations: Ceremony origin is not stated.
                """
            ).strip()
            + "\n"
        )

    def _appendix_flags_source_yaml(self) -> str:
        return (
            textwrap.dedent(
                """
                source_unit:
                  source_file: pdfs/harrypotter.pdf
                  book: Harry Potter and the Philosopher's Stone
                  chapter: Chapter Seven - The Sorting Hat
                  chapter_start_pdf_page: 107
                  chapter_end_pdf_page: 122
                  processed_date: '2026-06-21'
                entries:
                - id: ps-ch07-flag
                  pdf_page: 110
                  quote_excerpt_short: bewitched to look like the sky outside
                  source_note: Hermione identifies an off-campus later note with limited corroboration.
                  reference_type: explicit_hogwarts_a_history
                  era_classification: later_editorial_note
                  topic_tags:
                  - off-campus-context
                  candidate_part: Magical Architecture and Enchantments
                  candidate_chapter: The Great Hall
                  candidate_section: The Enchanted Ceiling
                  duplicate_check:
                    possible_duplicate: true
                    duplicate_of: ps-ch07-001
                    notes: Needs comparison.
                  confidence: low
                  limitations: Limited evidence; origin is not stated.
                """
            ).strip()
            + "\n"
        )


if __name__ == "__main__":
    unittest.main()
