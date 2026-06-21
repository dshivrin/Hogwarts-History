# Hogwarts History Efficiency and Book Seed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve validation, lookup efficiency, and generated outputs while preserving the existing source-gathering mission: read the canon source chapter by chapter, extract all explicit `Hogwarts: A History` references, log duplicate/corroborating evidence, keep every source YAML, and eventually generate one human-readable book-like result.

**Architecture:** The source YAML files remain the archival evidence layer and stay self-contained. Runtime agents continue to process exactly one current source unit from `project-control/processing-state.yaml`; new tools only validate, query, and render that existing data. The final product becomes `book-seed/hogwarts-a-history-seed.md`; every other generated or control file is a helper, reference, audit trail, or source record.

**Tech Stack:** Python 3 with PyYAML, `unittest`, Markdown, YAML, existing scripts in `scripts/`, and existing project-control files.

---

## Non-Negotiable Process Invariants

- The project goal does not change: find every explicit reference to `Hogwarts: A History` and all strong supporting Hogwarts-history evidence by reading the source material chapter by chapter.
- A normal extraction run still processes one source unit: the `current_source_unit` in `project-control/processing-state.yaml`.
- The agent must not scan all prior YAML files or the whole PDF during normal extraction.
- Every extracted fact remains traceable to a source YAML entry with quote, page, anchor, duplicate check, confidence, and limitations.
- Duplicates are not deleted. Duplicate and corroborating evidence is logged in `duplicate_check`.
- `sources/book-*/*.yaml` files remain the permanent evidence archive.
- `book-seed/hogwarts-a-history-seed.md` becomes the only final human-readable result.
- `appendix/generated/*.md`, `project-control/*.yaml`, `.tmp/*`, and indexes remain helpers or references, not the end product.
- Schema compaction is deferred until validators and generators support both current and compact shapes.

## Planned File Responsibilities

- Create `scripts/validate_source_yaml.py`: parse and validate all source YAML, indexes, generated notices, enum values, duplicate references, quote lengths, and source-file naming.
- Create `scripts/query_duplicates.py`: return compact duplicate candidates from existing indexes and source YAML, without requiring agents to open full indexes.
- Create `scripts/query_entries.py`: return compact entry slices by tag, classification, reference type, confidence, source unit, or output YAML.
- Create `scripts/generate_book_seed.py`: generate the main human-readable book-like file from source YAML.
- Modify `scripts/generate_appendices.py`: keep appendices secondary and add `review-flags.md` plus `project-stats.md`.
- Modify `docs/instructions/runtime-contract.md`: preserve the same extraction procedure, but use validation and query scripts instead of manual full-index reads.
- Modify `docs/instructions/schema-reference.md`: document that source YAML is currently self-contained and that compact schema support is future/backward-compatible only.
- Modify `tests/test_refactor_support.py`: add focused tests for validation, query behavior, book generation, review flags, and stats.
- Create `book-seed/hogwarts-a-history-seed.md`: generated final result; do not edit manually.

## Desired End-State Repository Shape

```text
book-seed/
  hogwarts-a-history-seed.md

appendix/generated/
  explicit-hogwarts-a-history-references.md
  review-flags.md
  source-index.md
  project-stats.md
  open-questions.md
  book-structure-seed.md

docs/instructions/
  runtime-contract.md
  schema-reference.md
  background-guide.md
  archive/

project-control/
  processing-state.yaml
  next-run.md
  duplicate-index.yaml
  entry-index.yaml
  tag-index.yaml
  source-index.yaml
  source-plan.yaml
  structured-sources/open-questions.yaml

sources/
  book-01/
  book-02/
  book-03/
  book-04/

scripts/
  extract_pages.py
  validate_source_yaml.py
  build_duplicate_index.py
  build_entry_index.py
  build_tag_index.py
  query_duplicates.py
  query_entries.py
  generate_book_seed.py
  generate_appendices.py
  update_next_run.py
  cleanup_tmp.py
```

## Task 1: Add Source YAML Validator

**Files:**
- Create: `scripts/validate_source_yaml.py`
- Modify: `tests/test_refactor_support.py`

- [ ] **Step 1: Add failing tests for validator success and duplicate-reference failure**

Append tests that create temporary `sources/book-01/*.yaml` files, run `validate_source_yaml.main([...])`, and assert:

```python
def test_validate_source_yaml_accepts_valid_source_file(self) -> None:
    validate_source_yaml = importlib.import_module("scripts.validate_source_yaml")
    # Create one source YAML with source_unit, one valid entry, allowed enums,
    # quote_excerpt_short under 25 words, and duplicate_check.possible_duplicate false.
    # Expected: main(["--root", str(root)]) returns 0.

def test_validate_source_yaml_rejects_missing_duplicate_target(self) -> None:
    validate_source_yaml = importlib.import_module("scripts.validate_source_yaml")
    # Create one source YAML whose duplicate_check.duplicate_of points to "missing-id".
    # Expected: main(["--root", str(root)]) returns 1.
```

Run: `.venv/bin/python -m unittest tests/test_refactor_support.py`

Expected: FAIL because `scripts.validate_source_yaml` does not exist.

- [ ] **Step 2: Implement validator CLI**

Create `scripts/validate_source_yaml.py` with these concrete checks:

- All `sources/book-*/*.yaml` files parse as mappings.
- Top-level keys `source_unit` and `entries` exist.
- `entries` is a list.
- `source_unit` contains `source_file`, `book`, `chapter`, `chapter_start_pdf_page`, `chapter_end_pdf_page`, and `processed_date`.
- Every entry has `id`, `pdf_page`, `text_anchor`, `quote_excerpt_short`, `source_note`, `reference_type`, `era_classification`, `topic_tags`, `candidate_part`, `candidate_chapter`, `candidate_section`, `duplicate_check`, `confidence`, and `limitations`.
- `reference_type` is one of the values in `docs/instructions/schema-reference.md`.
- `era_classification` is one of the values in `docs/instructions/schema-reference.md`.
- `confidence` is `high`, `medium`, or `low`.
- `quote_excerpt_short` is under 25 words.
- Entry IDs are globally unique.
- Duplicate targets in `duplicate_check.duplicate_of` exist in another or same source YAML.
- Generated appendix files start with `# Generated File`.
- Index files parse as YAML when present.
- `--strict` additionally fails when `topic_tags` has fewer than 3 or more than 8 tags, `source_note` exceeds 60 words, or `possible_duplicate: true` has no `duplicate_of`.

The script must accept:

```bash
.venv/bin/python scripts/validate_source_yaml.py
.venv/bin/python scripts/validate_source_yaml.py --strict
.venv/bin/python scripts/validate_source_yaml.py --root /path/to/tmp/root
```

- [ ] **Step 3: Run validator tests**

Run: `.venv/bin/python -m unittest tests/test_refactor_support.py`

Expected: PASS.

- [ ] **Step 4: Run validator on current repo**

Run: `.venv/bin/python scripts/validate_source_yaml.py`

Expected: PASS or a concrete list of schema issues. If issues appear, fix only schema violations, not content judgment.

- [ ] **Step 5: Commit validator**

Run:

```bash
git add scripts/validate_source_yaml.py tests/test_refactor_support.py
git commit -m "Add source YAML validator"
```

## Task 2: Add Query Scripts for Duplicate and Entry Lookup

**Files:**
- Create: `scripts/query_duplicates.py`
- Create: `scripts/query_entries.py`
- Modify: `tests/test_refactor_support.py`

- [ ] **Step 1: Add failing query tests**

Add tests that create temporary source YAML plus `tag-index.yaml`, `duplicate-index.yaml`, and `entry-index.yaml`, then assert:

```python
def test_query_duplicates_returns_only_matching_tags(self) -> None:
    # Query tags ["great-hall", "enchanted-ceiling"].
    # Expected YAML output includes matching entry id and excludes unrelated tags.

def test_query_entries_filters_by_tag_and_classification(self) -> None:
    # Query --tag great-hall --classification original_book_core_candidate.
    # Expected YAML output includes only entries matching both filters.
```

Run: `.venv/bin/python -m unittest tests/test_refactor_support.py`

Expected: FAIL because query scripts do not exist.

- [ ] **Step 2: Implement `query_duplicates.py`**

The script must:

- Accept `--tags`, `--candidate-chapter`, `--candidate-section`, `--limit`, and `--root`.
- Read existing `project-control/tag-index.yaml` and `project-control/duplicate-index.yaml`.
- Score matches by shared tag count plus candidate chapter/section text overlap.
- Output YAML only, with this shape:

```yaml
query:
  tags:
  - great-hall
  candidate_chapter: The Great Hall
matches:
- entry_id: ps-ch07-001
  score: 5
  title: The Great Hall: The Enchanted Ceiling
  tags:
  - great-hall
  - enchanted-ceiling
  source_note: Hermione explains that the Great Hall ceiling is enchanted.
  output_yaml: sources/book-01/chapter-07-sorting-hat.yaml
```

- [ ] **Step 3: Implement `query_entries.py`**

The script must:

- Accept `--tag`, `--classification`, `--reference-type`, `--confidence`, `--source-unit`, `--output-yaml`, `--limit`, and `--root`.
- Read `project-control/entry-index.yaml`.
- Output YAML only, with `query` and `matches`.
- Return compact rows containing `entry_id`, `title`, `classification`, `confidence`, `tags`, `source_unit`, and `output_yaml`.

- [ ] **Step 4: Run query tests**

Run: `.venv/bin/python -m unittest tests/test_refactor_support.py`

Expected: PASS.

- [ ] **Step 5: Smoke-test against current repo**

Run:

```bash
.venv/bin/python scripts/query_duplicates.py --tags owl-post student-correspondence --limit 5
.venv/bin/python scripts/query_entries.py --tag owl-post --limit 5
```

Expected: Both commands output compact YAML and do not require opening full index files.

- [ ] **Step 6: Commit query scripts**

Run:

```bash
git add scripts/query_duplicates.py scripts/query_entries.py tests/test_refactor_support.py
git commit -m "Add compact source query scripts"
```

## Task 3: Generate the Final Human-Readable Book Seed

**Files:**
- Create: `scripts/generate_book_seed.py`
- Create: `book-seed/hogwarts-a-history-seed.md`
- Modify: `tests/test_refactor_support.py`

- [ ] **Step 1: Add failing book-seed generator test**

Add a test that creates two source entries with the same `candidate_part`, `candidate_chapter`, and `candidate_section`, then asserts the generated Markdown contains:

- `# Hogwarts: A History - Evidence-Backed Seed`
- A generated-file notice.
- One `## Part:` heading.
- One `### Chapter:` heading.
- One `#### Section:` heading.
- A fact/evidence/source block for each entry.
- Entry IDs and source YAML paths.

Run: `.venv/bin/python -m unittest tests/test_refactor_support.py`

Expected: FAIL because `scripts.generate_book_seed` does not exist.

- [ ] **Step 2: Implement `generate_book_seed.py`**

The generator must:

- Load all `sources/book-*/*.yaml`.
- Group entries by `candidate_part`, `candidate_chapter`, and `candidate_section`.
- Sort deterministically using explicit part order where available, then chapter/section names.
- Write `book-seed/hogwarts-a-history-seed.md`.
- Include every entry exactly once.
- Render readable blocks with these fields:

```markdown
**Fact:** <source_note>
**Evidence:** "<quote_excerpt_short>"
**Source:** <book>, <chapter>, PDF page <pdf_page>, entry `<id>`, `<output_yaml>`
**Classification:** <era_classification>
**Reference type:** <reference_type>
**Confidence:** <confidence>
**Duplicate / corroboration:** <duplicate_check summary>
**Notes:** <limitations>
```

- [ ] **Step 3: Run book-seed test**

Run: `.venv/bin/python -m unittest tests/test_refactor_support.py`

Expected: PASS.

- [ ] **Step 4: Generate current book seed**

Run: `.venv/bin/python scripts/generate_book_seed.py`

Expected: `book-seed/hogwarts-a-history-seed.md` exists and starts with a generated-file notice.

- [ ] **Step 5: Confirm the final-output hierarchy**

Check that `book-seed/hogwarts-a-history-seed.md` is the only file described as the final human-readable result. Appendices must be described as generated support files only.

- [ ] **Step 6: Commit book-seed generator**

Run:

```bash
git add scripts/generate_book_seed.py book-seed/hogwarts-a-history-seed.md tests/test_refactor_support.py
git commit -m "Generate evidence-backed book seed"
```

## Task 4: Add Review Flags and Project Stats Appendices

**Files:**
- Modify: `scripts/generate_appendices.py`
- Create: `appendix/generated/review-flags.md`
- Create: `appendix/generated/project-stats.md`
- Modify: `tests/test_refactor_support.py`

- [ ] **Step 1: Add failing tests for new appendices**

Add tests asserting:

- `review-flags.md` contains sections for low confidence, unknown era, possible duplicates, later editorial notes, off-campus context, limited evidence, and schema warnings.
- `project-stats.md` contains processed source units, entries by book, entries by era classification, entries by reference type, explicit `Hogwarts: A History` references, possible duplicates, latest processed unit, and next pending unit.

Run: `.venv/bin/python -m unittest tests/test_refactor_support.py`

Expected: FAIL because those files are not generated.

- [ ] **Step 2: Extend `generate_appendices.py`**

Add generation functions:

- `generate_review_flags(entries)` scans existing entry fields and groups review concerns.
- `generate_project_stats(entries)` counts entries by source book, era classification, reference type, explicit reference type, and duplicate status.
- `load_processing_state()` reads `project-control/processing-state.yaml` when available to identify latest completed and next pending source units.

- [ ] **Step 3: Preserve existing appendices**

Keep generating:

- `book-structure-seed.md`
- `explicit-hogwarts-a-history-references.md`
- `open-questions.md`
- `source-index.md`

Do not rename existing appendices in this task.

- [ ] **Step 4: Run appendix tests**

Run: `.venv/bin/python -m unittest tests/test_refactor_support.py`

Expected: PASS.

- [ ] **Step 5: Regenerate appendices**

Run: `.venv/bin/python scripts/generate_appendices.py`

Expected: Both new appendices exist and start with `# Generated File`.

- [ ] **Step 6: Commit appendix improvements**

Run:

```bash
git add scripts/generate_appendices.py appendix/generated/review-flags.md appendix/generated/project-stats.md tests/test_refactor_support.py
git commit -m "Add review flags and project stats appendices"
```

## Task 5: Update Runtime Contract Without Changing Extraction Goal

**Files:**
- Modify: `docs/instructions/runtime-contract.md`
- Modify: `docs/instructions/schema-reference.md`
- Modify: `scripts/update_next_run.py`
- Modify: `tests/test_refactor_support.py`

- [ ] **Step 1: Add failing runtime text test**

Update the existing `test_update_next_run_default_only_regenerates_prompt` to assert the generated prompt includes `scripts/query_duplicates.py` and excludes instructions to open full indexes.

Run: `.venv/bin/python -m unittest tests/test_refactor_support.py`

Expected: FAIL until runtime text is updated.

- [ ] **Step 2: Update `runtime-contract.md` required reads**

Keep the normal-run read list:

```text
1. docs/instructions/runtime-contract.md
2. project-control/processing-state.yaml
3. .tmp/current-chapter.txt after extraction
4. Current output YAML only if it exists
```

Do not add appendices, all indexes, prior YAML files, or `chapters-index.md` to required reads.

- [ ] **Step 3: Update duplicate procedure**

Replace manual index search wording with:

```text
Run scripts/query_duplicates.py with candidate tags and placement terms.
Open referenced YAML only when a likely duplicate appears.
Do not open full index files during normal extraction.
```

- [ ] **Step 4: Update output and validation steps**

Add:

```text
Run scripts/validate_source_yaml.py after changing source YAML or generated helper files.
Run scripts/generate_book_seed.py when appendices are regenerated or after each completed source unit.
```

- [ ] **Step 5: Update `schema-reference.md`**

Add a short note:

```text
Current source YAML is intentionally self-contained. Source metadata may repeat per entry so each entry remains portable and auditable. A compact inherited-location schema may be introduced later only after validators, index builders, query scripts, and generators support both shapes.
```

- [ ] **Step 6: Update `scripts/update_next_run.py` prompt text**

Generated `next-run.md` should instruct:

```text
Use scripts/query_duplicates.py for duplicate and context lookup.
Open only referenced YAML files for likely matches.
Do not read appendices, archives, old prompts, full indexes, all prior YAML files, or chapters-index.md during normal runs.
```

- [ ] **Step 7: Run tests and validation**

Run:

```bash
.venv/bin/python -m unittest tests/test_refactor_support.py
.venv/bin/python scripts/validate_source_yaml.py
```

Expected: PASS.

- [ ] **Step 8: Regenerate `next-run.md`**

Run: `.venv/bin/python scripts/update_next_run.py`

Expected: `project-control/next-run.md` still points to the same current source unit and includes query-script wording.

- [ ] **Step 9: Commit runtime updates**

Run:

```bash
git add docs/instructions/runtime-contract.md docs/instructions/schema-reference.md scripts/update_next_run.py project-control/next-run.md tests/test_refactor_support.py
git commit -m "Use query and validation scripts in runtime contract"
```

## Task 6: Wire Generators Into the Normal Post-Extraction Flow

**Files:**
- Modify: `docs/instructions/runtime-contract.md`
- Modify: `tests/test_refactor_support.py`

- [ ] **Step 1: Add a documentation assertion test**

Add a test that reads `docs/instructions/runtime-contract.md` and asserts the post-extraction flow contains this order:

```text
build_duplicate_index.py
build_entry_index.py
build_tag_index.py
validate_source_yaml.py
generate_book_seed.py
generate_appendices.py
update_next_run.py
cleanup_tmp.py
```

Run: `.venv/bin/python -m unittest tests/test_refactor_support.py`

Expected: FAIL until the contract lists this order.

- [ ] **Step 2: Update output steps**

The normal post-extraction command sequence should be:

```bash
.venv/bin/python scripts/build_duplicate_index.py
.venv/bin/python scripts/build_entry_index.py
.venv/bin/python scripts/build_tag_index.py
.venv/bin/python scripts/validate_source_yaml.py
.venv/bin/python scripts/generate_book_seed.py
.venv/bin/python scripts/generate_appendices.py
.venv/bin/python scripts/update_next_run.py
.venv/bin/python scripts/cleanup_tmp.py
```

Keep `generate_appendices.py` as support output. Keep `generate_book_seed.py` as the main human-result output.

- [ ] **Step 3: Run tests**

Run: `.venv/bin/python -m unittest tests/test_refactor_support.py`

Expected: PASS.

- [ ] **Step 4: Commit flow documentation**

Run:

```bash
git add docs/instructions/runtime-contract.md tests/test_refactor_support.py
git commit -m "Document post-extraction generation flow"
```

## Task 7: Optional Future Schema Compaction

**Files:**
- Modify only after Tasks 1-6 are complete and passing.

- [ ] **Step 1: Confirm compaction is still needed**

Measure current source YAML size and index size:

```bash
wc -l sources/book-*/*.yaml project-control/*index.yaml
```

Expected: Use this only to decide whether compaction is worth the risk.

- [ ] **Step 2: Add backward-compatible loader tests**

Before changing any source files, add tests that prove loaders accept:

- Current self-contained entries.
- Future compact entries with inherited `source_unit` metadata and per-entry `loc`.

- [ ] **Step 3: Update loaders before data**

Update validators, index builders, query scripts, appendix generator, and book generator to normalize both shapes internally.

- [ ] **Step 4: Convert one source YAML only**

Convert exactly one small source YAML file and run:

```bash
.venv/bin/python -m unittest tests/test_refactor_support.py
.venv/bin/python scripts/validate_source_yaml.py
.venv/bin/python scripts/build_duplicate_index.py
.venv/bin/python scripts/build_entry_index.py
.venv/bin/python scripts/build_tag_index.py
.venv/bin/python scripts/generate_book_seed.py
.venv/bin/python scripts/generate_appendices.py
```

Expected: PASS and no lost entries.

- [ ] **Step 5: Stop unless the benefit is clear**

Do not bulk-convert source YAML unless the one-file trial shows meaningful size reduction with no loss of readability or auditability.

## Final Verification

Run:

```bash
git status --short
.venv/bin/python -m unittest tests/test_refactor_support.py
.venv/bin/python scripts/validate_source_yaml.py
.venv/bin/python scripts/query_duplicates.py --tags hogwarts-history great-hall --limit 5
.venv/bin/python scripts/query_entries.py --tag owl-post --limit 5
.venv/bin/python scripts/generate_book_seed.py
.venv/bin/python scripts/generate_appendices.py
.venv/bin/python scripts/update_next_run.py
git status --short
```

Expected:

- Tests pass.
- Validator passes.
- Query scripts output compact YAML.
- `book-seed/hogwarts-a-history-seed.md` exists and includes all source entries exactly once.
- Appendices exist and are clearly support/reference files.
- `project-control/processing-state.yaml` still controls the next chapter-by-chapter extraction run.
- No `.DS_Store`, `.tmp/`, `.venv/`, or unrelated files are staged.

## Self-Review Notes

- Spec coverage: This plan preserves the chapter-by-chapter extraction goal, duplicate logging, source retention, helper/reference separation, and single final human-readable book output.
- Placeholder scan: The plan intentionally contains no unfinished marker text or unspecified implementation phases.
- Scope control: Query scripts, validation, final book generation, and appendix improvements are separable tasks with independent commits.
- Risk control: Schema compaction is explicitly optional and deferred until the validation/query/generation path is stable.
