# Finish Result Output Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to execute this plan.

**Goal:** Finish the result-output refactor so generated project outputs are ordered, compact, traceable, and validated against the redesigned format.

**Architecture:** Keep source YAML as the durable extraction record. Update the generation scripts so `book-seed/hogwarts-a-history-seed.md` and generated appendices become the readable output layer. Add validation and tests that lock the new output contract in place.

**Tech Stack:** Python standard library, PyYAML, `unittest`, `just`, `rg`, `jq` only for JSON inspection when needed.

---

## Current State Snapshot

The CLI tooling plan has already been implemented. Use `just` recipes for orientation and validation:

```bash
just status
just next
just test
just generate
just validate
just post
```

Current automation state in `project-control/processing-state.yaml`:

- Last completed source unit: Book 4, Chapter 12, `Chapter Twelve - The Triwizard Tournament`, pages 1089-1106.
- Current source unit: Book 4, Chapter 13, `Chapter Thirteen - Mad-Eye Moody`, pages 1107-1120.
- Next source unit: Book 4, Chapter 14, `Chapter Fourteen - The Unforgivable Curses`, pages 1121-1136.

Current generated output status:

- `book-seed/hogwarts-a-history-seed.md` is still in the old ledger format.
- `scripts/generate_book_seed.py` still sorts parts, chapters, and sections alphabetically.
- `project-control/book-seed-order.yaml` does not exist yet.
- `scripts/generate_appendices.py` still renders explicit references as a thin single-line list.
- `appendix/generated/explicit-hogwarts-a-history-references.md` now includes four explicit references, including `gof-ch11-005`.
- `scripts/validate_source_yaml.py` validates generated appendices but does not validate the main book seed output contract.
- `tests/test_refactor_support.py` still contains tests that preserve the old ledger output, including `**Fact:**`.

Do not change extraction state or add new source entries while implementing this plan. The source corpus should remain processed through Book 4 Chapter 12 unless a separate extraction task is explicitly requested.

---

## Desired Output Contract

The main generated seed should be reader-first but still auditable:

- Use configured narrative order, not alphabetical order.
- Render part, chapter, and section headings according to `project-control/book-seed-order.yaml`.
- Add a short generated section summary before compact evidence bullets.
- Replace old ledger fields such as `**Fact:**` with prose-oriented bullets.
- Preserve traceability in every evidence item:
  - source book
  - source chapter
  - PDF page
  - source entry id
  - source YAML path
  - classification
  - confidence
  - quote or evidence note
- Suppress negative duplicate noise. Never emit `possible_duplicate=false`.
- Render only meaningful duplicate or corroboration data, such as `Corroborates: \`ps-ch07-001\`.`.

The explicit references appendix should become useful for review:

- Include each explicit `Hogwarts: A History` reference.
- Include source entry id, source book, chapter, PDF page, quote, classification, destination section, and source YAML path.
- Include the new current reference `gof-ch11-005`.

Validation should fail if generated output regresses to the old format.

---

## Task 1: Add Configured Book Seed Ordering

Create `project-control/book-seed-order.yaml`.

Use the project's intended `Hogwarts: A History` structure from `docs/instructions/background-guide.md` as the initial order. The file should define ordered parts, chapters, and sections in a simple YAML shape:

```yaml
parts:
  - title: Origins of the School
    chapters:
      - title: Founding and Early Purpose
        sections:
          - The Four Founders
          - The Founding Era
  - title: Academic Life and Curriculum
    chapters:
      - title: Houses and Sorting
        sections:
          - The Sorting Hat
          - House Identity and Rivalry
```

The exact chapter and section names must match existing `candidate_part`, `candidate_chapter`, and `candidate_section` values where possible.

Update `scripts/generate_book_seed.py`:

- Add `ORDER_PATH = ROOT / "project-control" / "book-seed-order.yaml"`.
- Add `load_book_seed_order(root: Path) -> dict`.
- Add an ordering helper that returns configured titles first and unknown titles afterward in stable alphabetical order.
- Use the helper for part, chapter, and section rendering.
- Keep generation functional if the order file is absent, but tests should cover the configured path.

Add or update tests in `tests/test_refactor_support.py`:

- Build two or three sample entries whose alphabetical order differs from configured order.
- Assert rendered part/chapter/section order follows `book-seed-order.yaml`.
- Assert unknown sections are still rendered after configured sections.

Verification for this task:

```bash
just test
```

---

## Task 2: Redesign Main Book Seed Rendering

Update `scripts/generate_book_seed.py` so the generated seed is no longer a raw ledger.

Recommended helper functions:

```python
def entry_evidence_label(entry: dict) -> str:
    """Return a compact label such as Direct evidence, Context, or Corroboration."""


def format_source_line(entry: dict, source_path: Path | None = None) -> str:
    """Return source book, chapter, page, id, and YAML path in one traceable line."""


def format_corroboration(entry: dict) -> str | None:
    """Return a corroboration line only for positive duplicate/corroboration data."""


def summarize_section(entries: list[dict]) -> str:
    """Return a short generated summary for the section."""
```

The output for a section should look like this shape:

```markdown
### Section: The Sorting Hat

Summary: The available evidence presents the Sorting Hat as both a selection mechanism and a carrier of founder-era continuity.

- **Direct evidence:** The Sorting Hat sings about the founders and their house criteria.
  - Quote: "..."
  - Source: Book 1, Chapter 7, PDF p. 125, `ps-ch07-001`, `sources/book-01/chapter-07-sorting-hat.yaml`
  - Classification: direct | Confidence: high
  - Notes: Explicitly identifies the Sorting Hat as historically connected to the founders.
```

Rules:

- Do not emit `**Fact:**`.
- Do not emit `**Duplicate / corroboration:**`.
- Do not emit `possible_duplicate=false`.
- Do not emit empty notes, empty quotes, or empty duplicate lines.
- Preserve all meaningful existing data. This is a rendering refactor, not a source rewrite.
- If an entry has `duplicate_check.duplicate_of`, render `Corroborates:` with ids.
- If an entry has `duplicate_check.possible_duplicate: true`, render that only when it includes useful target ids or notes.

Add or update tests:

- Assert the rendered seed contains a `Summary:` line for populated sections.
- Assert no old ledger labels appear.
- Assert `possible_duplicate=false` is absent.
- Assert source traceability contains entry id, PDF page, classification, confidence, and YAML source path.
- Assert positive duplicate/corroboration data renders clearly.

Verification for this task:

```bash
just test
```

---

## Task 3: Enrich Explicit Reference Appendix

Update `scripts/generate_appendices.py`, especially `generate_explicit_references()`.

Render each explicit reference as a compact review block:

```markdown
## Book 4, Chapter 11 - Aboard the Hogwarts Express

- `gof-ch11-005`
  - Quote: "..."
  - Evidence note: Hermione cites Hogwarts: A History as the source for Hogwarts being hidden from outsiders.
  - Destination: Magical Protections / Concealment from Muggles / Muggle-Repelling Effects
  - Source: PDF p. 1081, `sources/book-04/chapter-11-aboard-the-hogwarts-express.yaml`
  - Classification: direct | Confidence: high
```

Rules:

- Keep the `# Generated File` header.
- Group entries by source book and chapter in source order.
- Include all explicit `Hogwarts: A History` references currently in source YAML.
- Include `gof-ch11-005` after regeneration.
- Do not depend on a fixed total count in tests unless the fixture owns the complete source set.

Add or update tests:

- Use a fixture entry with `reference_type: explicit` or the project's current equivalent.
- Assert quote, page, destination, classification, and source YAML path render.
- Assert output remains valid when an entry lacks an optional quote or notes field.

Verification for this task:

```bash
just test
```

---

## Task 4: Validate the Main Generated Seed

Update `scripts/validate_source_yaml.py` to validate the generated seed contract as part of `just validate`.

Add a function such as:

```python
def validate_book_seed(root: Path, source_entry_count: int) -> list[str]:
    """Return validation errors for the generated book seed output."""
```

Checks:

- If source entries exist, `book-seed/hogwarts-a-history-seed.md` must exist.
- The file must start with `# Generated File`.
- The file must contain `# Hogwarts: A History - Evidence-Backed Seed`.
- The file must contain at least one rendered part heading.
- The file must not contain `**Fact:**`.
- The file must not contain `**Duplicate / corroboration:**`.
- The file must not contain `possible_duplicate=false`.
- The explicit references appendix must still start with `# Generated File`.

Add tests:

- A valid generated seed passes.
- A generated seed containing `**Fact:**` fails validation.
- A generated seed containing `possible_duplicate=false` fails validation.

Verification for this task:

```bash
just test
just validate
```

---

## Task 5: Regenerate Current Outputs

After tests pass, regenerate outputs from the current source corpus:

```bash
just generate
just validate
just post
```

Inspect the regenerated files:

```bash
rg "possible_duplicate=false|\\*\\*Fact:\\*\\*|\\*\\*Duplicate / corroboration:\\*\\*" book-seed/hogwarts-a-history-seed.md
rg "gof-ch11-005|Hogwarts hidden from outsiders|Muggle-facing ruin" appendix/generated/explicit-hogwarts-a-history-references.md book-seed/hogwarts-a-history-seed.md
rg "^## Part:" book-seed/hogwarts-a-history-seed.md
```

Expected results:

- First `rg` returns no matches.
- Second `rg` finds the Book 4 Chapter 11 explicit reference.
- Third `rg` shows parts in configured order, with the first rendered part being the first configured part that has source entries.

Then run the full local verification:

```bash
just test
just validate
just post
git diff --stat
```

Expected known test behavior:

- `just test` may print an intentional negative validator message for a fixture with a missing duplicate target.
- The command still passes only if the final test result is `OK`.

---

## Acceptance Criteria

The implementation is complete when all of these are true:

- `project-control/book-seed-order.yaml` exists and controls generated seed order.
- `book-seed/hogwarts-a-history-seed.md` no longer uses old ledger labels.
- `book-seed/hogwarts-a-history-seed.md` contains compact evidence bullets with section summaries.
- Negative duplicate noise is absent from generated output.
- Positive corroboration or duplicate information remains visible.
- `appendix/generated/explicit-hogwarts-a-history-references.md` includes enriched review blocks.
- `gof-ch11-005` appears in the explicit references appendix after regeneration.
- `just test`, `just validate`, and `just post` pass.
- The automation extraction state remains processed through Book 4 Chapter 12 unless a separate extraction task was explicitly run.

---

## Final Review Checklist

Before handing off, record the exact verification commands and results in the final response:

```bash
just test
just validate
just post
rg "possible_duplicate=false|\\*\\*Fact:\\*\\*|\\*\\*Duplicate / corroboration:\\*\\*" book-seed/hogwarts-a-history-seed.md
rg "gof-ch11-005" appendix/generated/explicit-hogwarts-a-history-references.md
git status --short
```

The first three commands must pass. The old-format `rg` command must return no matches. The `gof-ch11-005` search must return at least one match. `git status --short` should show only the intended implementation files and regenerated outputs.
