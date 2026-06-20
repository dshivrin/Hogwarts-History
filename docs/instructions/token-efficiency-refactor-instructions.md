# Hogwarts History Token-Efficiency Refactor Instructions

## Goal

Reduce tokens consumed per extraction iteration so the automation can process more chapters per day while preserving extraction quality, source traceability, and repeatability.

Routine extraction runs should read only the smallest useful context:

1. A short runtime contract.
2. The current extracted source-unit text.
3. The current output YAML, if it already exists.
4. Compact indexes for duplicate and state checks.
5. Full schema or background references only when validation fails or classification is ambiguous.

## Git Backup Rule

The project remote is:

```text
git@github.com:dshivrin/Hogwarts-History.git
```

After every successful extraction or refactor iteration, commit and push the scoped changes to this private repository.

For chapter extraction iterations, use the book name and chapter number plus chapter name in the commit message:

```text
<Book Name> Chapter <number> - <Chapter Name>
```

Example:

```text
Harry Potter and the Goblet of Fire Chapter 2 - The Scar
```

For non-chapter maintenance or refactor iterations, use a concise descriptive commit message:

```text
Refactor token-efficiency runtime instructions
```

Stage only files that belong to the current iteration. Do not stage unrelated generated files, local cache files, virtual environments, `.DS_Store`, or unrelated user changes.

Before pushing:

1. Run the relevant validation for the files changed.
2. Review `git status --short`.
3. Review the staged diff.
4. Commit only the intended scope.
5. Push the current branch to `origin`.

## Current Problems To Fix

The workflow is correct but context-heavy. Agents can discover and read too much history before processing one chapter:

- full 1,300-line instruction file
- stale instruction variants
- old `next-run N.md` prompts
- long appendices
- all prior chapter YAML files
- verbose source-index boundary notes
- accumulated `.tmp/` extraction artifacts

The refactor should separate runtime instructions, schema reference, background guidance, compact state, generated appendices, and archived history.

## Guiding Rules

1. Keep one source of truth per concept.
2. Keep default runtime context small and predictable.
3. Use compact indexes before historical YAML files.
4. Treat appendices as generated outputs, not routine inputs.
5. Archive stale prompts and stale instruction variants outside active discovery paths.
6. Keep YAML schema validation strict.
7. Preserve existing `sources/book-*/*.yaml` paths unless a later migration explicitly requires moving them.
8. Preserve existing source-file paths such as `pdfs/harrypotter.pdf`.

## Target Layout

The exact folder names can stay close to the current repo. The important change is the role of each file.

```text
docs/
  instructions/
    runtime-contract.md
    schema-reference.md
    background-guide.md
    archive/

project-control/
  processing-state.yaml
  duplicate-index.yaml
  entry-index.yaml
  source-index.yaml
  next-run.md
  archive/

sources/
  book-01/
  book-02/
  book-03/
  book-04/

appendix/
  generated/

scripts/
  extract_pages.py
  build_duplicate_index.py
  build_entry_index.py
  generate_appendices.py
  cleanup_tmp.py
```

## Phase 1: Canonicalize Runtime Instructions

Create a short `docs/instructions/runtime-contract.md` under 150 lines.

It should include:

- required files to read
- files prohibited during normal runs
- extraction procedure
- duplicate-check procedure using compact indexes
- output and state update steps
- validation checklist
- git backup rule

Move stale instruction variants into `docs/instructions/archive/`:

- `hogwarts-history-seed-builder-first.md`
- `hogwarts-history-seed-builder-updated.md`

Move the current full instruction file into archive only if a tiny redirect remains at the old path:

```md
# Archived Runtime Redirect

Routine agents must use `docs/instructions/runtime-contract.md`.
The legacy full instruction file is retained in `docs/instructions/archive/`.
```

## Phase 2: Shrink `next-run.md`

Move old run prompts into `project-control/archive/`:

- `next-run 2.md`
- `next-run 3.md`
- `next-run 4.md`
- `next-run 5.md`
- `next-run 6.md`
- `next-run 7.md`
- `next-run 8.md`
- `next-run 9.md`

Keep only `project-control/next-run.md` active. It should be a small generated display, not a second source of truth.

Target size: under 40 lines.

It should summarize:

- current source unit
- source file
- page range
- output YAML
- minimal-context read list
- reminder not to read appendices or archives during normal runs

If `next-run.md` is deleted, automation should still be able to run from `processing-state.yaml`.

## Phase 3: Consolidate Runtime State

Make `project-control/processing-state.yaml` the compact source of truth for the current and next run.

It should include:

```yaml
project:
  mode: minimal_context
  canonical_runtime_contract: docs/instructions/runtime-contract.md
  schema_reference: docs/instructions/schema-reference.md
  background_guide: docs/instructions/background-guide.md

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

indexes:
  duplicate_index: project-control/duplicate-index.yaml
  entry_index: project-control/entry-index.yaml
  source_index: project-control/source-index.yaml

appendices:
  generated_only: true
  generator_script: scripts/generate_appendices.py

cache:
  current_text: .tmp/current-chapter.txt
  keep_last_n_chapters: 3
```

Routine agents should not need `chapters-index.md` when current and next page ranges are already in state.

## Phase 4: Add Compact Duplicate Index

Create `project-control/duplicate-index.yaml` from existing `sources/book-*/*.yaml` files.

Use it to avoid scanning all previous YAML files during duplicate checks.

Suggested shape:

```yaml
version: 1
updated: '2026-06-20'
entries:
  - entry_id: ps-ch07-001
    canonical_topic: great_hall_enchanted_ceiling
    tags:
      - magical-architecture
      - great-hall
      - enchanted-ceiling
      - explicit-reference
    book: Harry Potter and the Philosopher's Stone
    chapter_number: 7
    chapter_title: Chapter Seven - The Sorting Hat
    source_note: Hermione says the ceiling is bewitched to look like the sky outside and that she read about it in Hogwarts: A History.
    output_yaml: sources/book-01/chapter-07-sorting-hat.yaml
```

Duplicate lookup procedure:

1. Generate 3-8 normalized topic tags for each candidate entry.
2. Search only `duplicate-index.yaml` for overlapping tags or canonical topic.
3. If no match appears, treat the entry as new.
4. If a match appears, open only the referenced YAML file and compare evidence.
5. Update the current entry's `duplicate_check` block.

The duplicate index must be rebuildable from canonical YAML outputs.

## Phase 5: Add Compact Entry Index

Create `project-control/entry-index.yaml` for broad browsing and appendix generation.

Suggested shape:

```yaml
version: 1
updated: '2026-06-20'
by_entry:
  ps-ch07-001:
    title: Great Hall enchanted ceiling
    classification: original_book_core_candidate
    confidence: high
    tags:
      - great-hall
      - enchanted-ceiling
      - magical-architecture
    source_unit: ps-ch07
    output_yaml: sources/book-01/chapter-07-sorting-hat.yaml
by_tag:
  great-hall:
    - ps-ch07-001
  enchanted-ceiling:
    - ps-ch07-001
```

Agents should use this index to answer "what already exists around this topic?" without reading all chapter YAML files.

## Phase 6: Treat Appendices As Generated Outputs

Move generated human-facing outputs to `appendix/generated/` or mark them clearly as generated.

Generate these files from YAML and indexes:

- `appendix/generated/book-structure-seed.md`
- `appendix/generated/explicit-hogwarts-a-history-references.md`
- `appendix/generated/open-questions.md`
- `appendix/generated/source-index.md`

Generated files should start with:

```md
# Generated File

Do not edit manually.
Regenerate with `scripts/generate_appendices.py`.
Source data: sources YAML + project-control indexes.
```

For chapters with no explicit references, use compact rows instead of long negative search notes.

## Phase 7: Refactor Source Index

Create `project-control/source-index.yaml` and stop growing narrative boundary notes in `appendix/source-index.md`.

Suggested shape:

```yaml
version: 1
updated: '2026-06-20'
processed_units:
  - source_unit_id: gof-ch01
    source_file: pdfs/harrypotter.pdf
    book: Harry Potter and the Goblet of Fire
    chapter_number: 1
    chapter_title: Chapter One - The Riddle House
    page_start: 949
    page_end: 960
    output_yaml: sources/book-04/chapter-01-the-riddle-house.yaml
    processed_at: '2026-06-20'
    explicit_reference_count: 0
    candidate_entry_count: 5
    boundary_summary: Used indexed page range; extracted only pages 949-960.
```

## Phase 8: Keep Full YAML Self-Contained But Avoid Broad Scans

Full chapter YAML files remain canonical and self-contained.

Open full historical YAML files only when:

- `duplicate-index.yaml` identifies a likely duplicate
- schema repair is required
- a human asks for source details

Do not scan all prior chapter YAML files during a normal run.

## Phase 9: Add Cache Cleanup Policy

Use deterministic temporary paths:

```text
.tmp/current-chapter.txt
.tmp/previous-chapter-1.txt
.tmp/previous-chapter-2.txt
.tmp/previous-chapter-3.txt
```

Add `scripts/cleanup_tmp.py` to keep only:

- current chapter text
- last 3 extracted chapter texts
- current run extraction log

The cache cleanup must not delete canonical YAML, appendices, control files, PDFs, scripts, or instruction files.

## Phase 10: Minimal Context Runtime Procedure

Normal runs should read only:

1. `docs/instructions/runtime-contract.md`
2. `project-control/processing-state.yaml`
3. `project-control/duplicate-index.yaml`
4. `project-control/entry-index.yaml`
5. current extracted chapter text
6. current output YAML, if it already exists

Conditional reads:

- `docs/instructions/schema-reference.md` for schema uncertainty or validation failure
- `docs/instructions/background-guide.md` for canon/date-boundary ambiguity
- referenced historical YAML files only for likely duplicate comparison
- generated appendices only for human-facing review

Prohibited during normal runs:

- archived instruction variants
- old `next-run N.md` files
- full appendices
- all previous YAML files
- full `chapters-index.md` when page boundaries are already in state

Runtime steps:

1. Read minimal required files.
2. Extract or refresh current chapter text with `scripts/extract_pages.py`.
3. Identify candidate institutional or history entries.
4. Normalize tags for each candidate.
5. Check duplicates through `duplicate-index.yaml`.
6. Open referenced YAML files only for likely duplicate candidates.
7. Write or update current chapter YAML.
8. Update compact indexes.
9. Update `processing-state.yaml` to the next chapter.
10. Regenerate `next-run.md`.
11. Regenerate appendices only if configured for that run.
12. Clean `.tmp/` according to cache policy.
13. Validate changed YAML.
14. Commit and push the scoped iteration.
15. Emit a short run summary.

## Scripts To Add

### `scripts/build_duplicate_index.py`

Read canonical source YAML files and write `project-control/duplicate-index.yaml`.

### `scripts/build_entry_index.py`

Read canonical source YAML files and write `project-control/entry-index.yaml`.

### `scripts/generate_appendices.py`

Generate appendix markdown files from source YAML and indexes.

### `scripts/cleanup_tmp.py`

Remove old extraction artifacts while preserving current and recent chapter text.

## Migration Order

### Pass 1: Immediate Cleanup

1. Archive stale instruction variants.
2. Archive old `next-run N.md` files.
3. Create `runtime-contract.md`.
4. Shrink `next-run.md`.
5. Add current and next boundaries to `processing-state.yaml`.
6. Keep a redirect at the legacy instruction path if it is moved.
7. Commit and push the scoped changes.

### Pass 2: Index-Based Duplicate Checks

1. Add `scripts/build_duplicate_index.py`.
2. Generate `project-control/duplicate-index.yaml`.
3. Update runtime instructions to use the duplicate index only.
4. Add the "open full YAML only on candidate match" rule.
5. Commit and push the scoped changes.

### Pass 3: Generated Outputs

1. Add `scripts/build_entry_index.py`.
2. Generate `project-control/entry-index.yaml`.
3. Add `scripts/generate_appendices.py`.
4. Mark appendices as generated.
5. Remove long zero-reference notes from generated output.
6. Commit and push the scoped changes.

### Pass 4: State And Cache Hardening

1. Convert source index to compact YAML.
2. Add cache cleanup script.
3. Make `next-run.md` generated from state.
4. Add validation checks for minimal context mode.
5. Commit and push the scoped changes.

## Success Metrics

| Metric | Current problem | Target |
| --- | --- | --- |
| Files read per normal run | Many, unpredictable | 5-7 predictable files |
| Instruction tokens per run | Full legacy instruction | Short runtime contract |
| Duplicate-check cost | Grows with all YAML files | Compact index plus 0-3 target YAMLs |
| Appendix maintenance | Manual edits | Generated from data |
| Old prompt discovery | Multiple stale files | Archived outside active path |
| Temporary files | Hundreds of artifacts | Current plus last 3 chapters |
| Backup safety | Local-only iteration state | Commit and push every iteration |

## Definition Of Done

The refactor is complete when a normal extraction run can be performed with this read pattern:

```text
docs/instructions/runtime-contract.md
project-control/processing-state.yaml
project-control/duplicate-index.yaml
project-control/entry-index.yaml
.tmp/current-chapter.txt
current output YAML, if it exists
0-3 referenced historical YAML files, only when duplicate candidates exist
```

And when:

- old instruction variants are archived
- old next-run files are archived
- appendices are generated or clearly treated as generated
- duplicate checks use compact indexes
- chapter boundaries are available in `processing-state.yaml`
- `.tmp/` cleanup is deterministic
- every successful iteration is committed and pushed to GitHub
