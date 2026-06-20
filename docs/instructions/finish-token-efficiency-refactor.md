# Finish Token-Efficiency Refactor Instructions

## Purpose

Finish the token-efficiency refactor before the next extraction run. The current cleanup made the workflow smaller, but it left several gaps that can cause either data loss or unnecessary token use.

This pass must make the minimal-context workflow reliable enough for the next extraction agent.

## Scope

Implement only refactor support work. Do not process a new chapter in this pass.

The next source-unit extraction has not been run yet after the cleanup. Current state still points at:

```yaml
current_source_unit:
  book_group: book-04
  book: Harry Potter and the Goblet of Fire
  chapter_number: 2
  chapter_title: Chapter Two - The Scar
```

Book 4 Chapter Three alignment is an expected state-transition target after Chapter Two is processed, not proof that Chapter Two has already been completed.

## Required Outcomes

1. Preserve curated appendix source material in structured data.
2. Create a compact index/tag system that agents can query without scanning large files.
3. Add the missing script that regenerates `project-control/next-run.md` and supports state advancement.
4. Make the post-Chapter-Two state align to Book 4 Chapter Three - The Invitation.
5. Ensure `.DS_Store` files are ignored and no longer tracked.

## Current Problems To Fix

### Curated Appendix Data Loss

The generated appendix flow replaced large curated files with compact generated files. This reduced token load, but it dropped the previous open-question backlog from the live tree.

The old open questions must be preserved as structured source data, not only in git history.

### Large Index Reads

`project-control/duplicate-index.yaml` and `project-control/entry-index.yaml` are useful, but they are large enough that reading both every run wastes tokens.

Routine agents should query compact indexes by tag, topic, or source unit. They should not load full index files into context unless debugging the index itself.

### Missing Next-Run Generator

`docs/instructions/runtime-contract.md` says to regenerate `project-control/next-run.md`, but no script exists for that. The next extraction agent would need to hand-edit state.

### State Alignment

The refactor should preserve this sequence:

1. Current unprocessed unit: Book 4 Chapter Two - The Scar, pages 961-968.
2. After Chapter Two is successfully processed, current unit advances to Book 4 Chapter Three - The Invitation, pages 969-978.

Do not mark Chapter Two complete unless `sources/book-04/chapter-02-the-scar.yaml` exists and validates.

## Implementation Plan

### 1. Add Structured Appendix Source

Create:

```text
project-control/structured-sources/
  open-questions.yaml
```

Optional later files:

```text
project-control/structured-sources/
  book-structure-overrides.yaml
  appendix-notes.yaml
```

`open-questions.yaml` should preserve the old curated open questions in structured form.

Suggested schema:

```yaml
version: 1
updated: '2026-06-21'
questions:
  - id: castle-navigation-001
    topic: Castle Navigation and Magical Architecture
    question: Does Hogwarts: A History explicitly describe castle navigation beyond the Great Hall ceiling?
    tags:
      - castle-navigation
      - magical-architecture
      - explicit-hogwarts-a-history
    status: open
    source: migrated-from-appendix-open-questions
    related_entries:
      - ps-ch07-001
```

Migration rule:

- Recover the old questions from git history or the archived source if present.
- Preserve the substance of each question.
- Normalize topic labels and tags.
- Do not place the full old markdown appendix back in the routine read path.

Update `scripts/generate_appendices.py` so generated `appendix/generated/open-questions.md` is built from this structured source plus any low-confidence/unknown-era entries.

### 2. Create Queryable Tag Indexes

Create a compact lookup file optimized for search:

```text
project-control/tag-index.yaml
```

Suggested shape:

```yaml
version: 1
updated: '2026-06-21'
tags:
  great-hall:
    entries:
      - ps-ch07-001
    output_yaml:
      - sources/book-01/chapter-07-sorting-hat.yaml
  hogwarts-security:
    entries:
      - poa-ch09-001
      - gof-ch01-004
    output_yaml:
      - sources/book-03/chapter-09-grim-defeat.yaml
      - sources/book-04/chapter-01-the-riddle-house.yaml
```

Add or update a script:

```text
scripts/build_tag_index.py
```

This script should read canonical source YAML files and write `project-control/tag-index.yaml`.

Runtime lookup rule:

- Use `rg "<tag-or-topic>" project-control/tag-index.yaml project-control/duplicate-index.yaml`.
- Open only referenced YAML files for likely matches.
- Do not read the entire duplicate index, entry index, or every source YAML file during routine extraction.

Update `docs/instructions/runtime-contract.md`:

- Required reads should not include full `duplicate-index.yaml` and `entry-index.yaml`.
- Required reads should include `processing-state.yaml` and current chapter text.
- Index files should be queried with `rg` by topic/tag.
- `entry-index.yaml` should become conditional, used only for browsing or appendix generation.

### 3. Add State And Next-Run Script

Create:

```text
scripts/update_next_run.py
```

Responsibilities:

1. Read `project-control/processing-state.yaml`.
2. Regenerate `project-control/next-run.md` from `current_source_unit`.
3. Optionally advance source state after a successful chapter run.
4. Keep `project-control/source-plan.yaml` synchronized or explicitly mark it deprecated.

Minimum CLI:

```bash
.venv/bin/python scripts/update_next_run.py
```

Optional advance CLI:

```bash
.venv/bin/python scripts/update_next_run.py --advance-after-success
```

The default mode must only regenerate `next-run.md`; it must not mark a chapter complete.

The advance mode must require:

- current output YAML exists
- current output YAML parses
- current output YAML has `source_unit` and `entries`
- next source unit is known

### 4. Align To Book 4 Chapter Three Correctly

Do not change current state to Chapter Three during this refactor-only pass unless Chapter Two output already exists and validates.

Instead, implement the transition logic so that after processing Book 4 Chapter Two:

```yaml
last_completed_source_unit:
  source_file: pdfs/harrypotter.pdf
  book_group: book-04
  book: Harry Potter and the Goblet of Fire
  chapter_number: 2
  chapter_title: Chapter Two - The Scar
  page_start: 961
  page_end: 968
  output_yaml: sources/book-04/chapter-02-the-scar.yaml

current_source_unit:
  source_file: pdfs/harrypotter.pdf
  book_group: book-04
  book: Harry Potter and the Goblet of Fire
  chapter_number: 3
  chapter_title: Chapter Three - The Invitation
  page_start: 969
  page_end: 978
  extracted_text_path: .tmp/current-chapter.txt
  output_yaml: sources/book-04/chapter-03-the-invitation.yaml
```

`next_source_unit` should then point to Book 4 Chapter Four - Back to the Burrow, pages 979-988.

Use existing `chapters-index.md` as source data while implementing this transition, but do not require routine agents to read `chapters-index.md`.

### 5. Update Git Ignore And Tracking

`.DS_Store` files must not be tracked.

Ensure `.gitignore` includes:

```text
*.DS_Store
**/.DS_Store
```

Remove already tracked `.DS_Store` files from the git index without deleting the local files:

```bash
git rm --cached .DS_Store docs/.DS_Store
```

Do not stage unrelated local cache files.

## Validation Requirements

Before committing this pass:

1. Compile Python scripts:

   ```bash
   PYTHONPYCACHEPREFIX=/tmp/hogwarts-pycache .venv/bin/python -m py_compile \
     scripts/extract_pages.py \
     scripts/build_duplicate_index.py \
     scripts/build_entry_index.py \
     scripts/build_tag_index.py \
     scripts/generate_appendices.py \
     scripts/cleanup_tmp.py \
     scripts/update_next_run.py
   ```

2. Parse YAML:

   ```bash
   .venv/bin/python -c "import pathlib, yaml; files=list(pathlib.Path('project-control').glob('*.yaml')) + list(pathlib.Path('project-control/structured-sources').glob('*.yaml')) + list(pathlib.Path('sources').glob('book-*/*.yaml')); [yaml.safe_load(p.read_text()) for p in files]; print(f'yaml ok: {len(files)} files')"
   ```

3. Regenerate indexes and appendices:

   ```bash
   .venv/bin/python scripts/build_duplicate_index.py
   .venv/bin/python scripts/build_entry_index.py
   .venv/bin/python scripts/build_tag_index.py
   .venv/bin/python scripts/generate_appendices.py
   .venv/bin/python scripts/update_next_run.py
   ```

4. Verify generated appendices start with the generated-file header.
5. Run `git diff --check`.
6. Confirm `git status --short` does not include tracked `.DS_Store` modifications.

## Commit And Push

Stage only the files changed by this refactor-completion pass.

Use a concise commit message:

```text
Finish token-efficiency refactor instructions
```

Push to:

```text
git@github.com:dshivrin/Hogwarts-History.git
```

## Definition Of Done

This pass is done when:

- curated open questions are preserved in structured source data
- generated open questions include structured curated questions
- agents can query tag/index files without reading all indexes
- `scripts/update_next_run.py` regenerates `next-run.md`
- state advancement from Book 4 Chapter Two to Book 4 Chapter Three is scripted and guarded
- `.DS_Store` files are ignored and untracked
- validation commands pass
- the scoped commit is pushed
