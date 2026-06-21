# Hogwarts History Result Output Redesign Plan

Review date: 2026-06-21
Repository state: current workspace after validator, query scripts, generated appendices, stats, review flags, `book-seed/hogwarts-a-history-seed.md`, and CLI tooling support already exist.

Prerequisite status: `docs/instructions/cli-tooling-runtime-update-plan.md` has been implemented. This result-output plan assumes the root `Justfile` has real project recipes such as `just brief`, `just search`, `just validate`, `just test`, `just indexes`, `just generate`, `just post`, `just query-dupes`, and `just query-entries`.

## Purpose

This plan replaces the older efficiency-focused plan. The major efficiency work is already present: routine agents no longer need to read full historical YAML archives, validation exists, query scripts exist, generated review appendices exist, and the project now has a main generated human-readable file.

The next improvement should focus on result quality. The current main output is useful as an evidence ledger, but it is not yet easy to read as the seed of a future fan edition of `Hogwarts: A History`.

## Current State Summary

Already implemented:

- `scripts/validate_source_yaml.py`
- `scripts/query_duplicates.py`
- `scripts/query_entries.py`
- `scripts/build_tag_index.py`
- `scripts/generate_book_seed.py`
- enriched `scripts/generate_appendices.py`
- `appendix/generated/review-flags.md`
- `appendix/generated/project-stats.md`
- `book-seed/hogwarts-a-history-seed.md`
- runtime contract that prefers query scripts over full-index reading
- `scripts/check-cli-tools.sh`
- root-level `Justfile`
- `rg`, `jq`, `just`, and `make` are available locally

Tooling assumptions after the CLI tooling plan:

- Use `just` as the preferred command surface.
- Use `rg` or `just search "pattern"` before opening broad files.
- Use project Python scripts for YAML validation/query/generation.
- Do not require `yq`; it is optional and not installed.
- Use `jq` only for JSON output, not for current YAML workflows.

Verified current health:

```bash
just validate
```

Expected current result:

```text
Source YAML validation passed.
```

```bash
just test
```

Expected current result:

```text
Ran 13 tests
OK
```

`pytest` is not currently available in the virtual environment, so use `unittest` unless the test stack is intentionally changed later.

Before starting implementation, run:

```bash
just brief
just tools
just search "possible_duplicate=false"
just search "Fact:"
```

Use the search results to inspect narrow file ranges only. Do not read generated appendices, archives, or all source YAML files for orientation.

## Main Finding

The remaining bottleneck is not token efficiency. It is editorial structure.

The current `book-seed/hogwarts-a-history-seed.md` has the right data, but it renders every entry as a repeated block:

```markdown
**Fact:** ...
**Evidence:** ...
**Source:** ...
**Classification:** ...
**Reference type:** ...
**Confidence:** ...
**Duplicate / corroboration:** ...
**Notes:** ...
```

That is valuable for audit, but repetitive for human review. The next generator pass should preserve traceability while making the output read more like a structured evidence-backed book seed.

## Desired End State

The project should produce two different human-facing layers:

1. `book-seed/hogwarts-a-history-seed.md`
   - Main readable result.
   - Ordered by a deliberate book structure.
   - Contains section summaries and grouped evidence.
   - Hides low-value operational noise.

2. `appendix/generated/*.md`
   - Audit and debugging support.
   - Keeps detailed review flags, source index, explicit references, open questions, and stats.
   - Can remain more mechanical.

Agent helper files should stay compact and script-driven. Do not reintroduce a workflow where normal extraction agents read full generated appendices or all source YAML files.

## Redesign Principles

### 1. Explicit Book Order

Do not sort final parts, chapters, and sections alphabetically.

Use a deliberate ordering source. The simplest option is a new generated-or-maintained control file:

```text
project-control/book-seed-order.yaml
```

It should define:

```yaml
version: 1
parts:
  - name: Origins of the School
    chapters: []
  - name: The Castle and Its Grounds
    chapters: []
  - name: Magical Architecture and Enchantments
    chapters: []
  - name: The Four Houses
    chapters: []
  - name: Ceremonies and School Traditions
    chapters: []
  - name: Academic Life and Curriculum
    chapters: []
  - name: Rules, Discipline, and Governance
    chapters: []
  - name: Ghosts, Portraits, and Magical Residents
    chapters: []
  - name: Protective Magic and Security
    chapters: []
  - name: Quidditch and School Recreation
    chapters: []
  - name: The Library, Books, and Scholarship
    chapters: []
  - name: Notable Events Before 1984
    chapters: []
  - name: Later Editorial Notes
    chapters: []
```

Chapters or sections not listed should render after listed items under an `Unordered Additions` heading, not silently disappear.

### 2. Section Summaries Before Evidence

Each section should begin with a generated summary block assembled from the strongest entries in that section.

The summary should answer:

- What does the evidence establish?
- Is it likely original-book material, historical candidate material, Harry-era confirmation, or later editorial material?
- What remains uncertain?

This can be deterministic. It does not need AI prose generation. Use the strongest high-confidence `source_note` values, explicit references first, then historical candidates, then confirmations.

### 3. Cleaner Evidence Rendering

The final book seed should use compact evidence bullets instead of full repeated field blocks.

Recommended final format:

```markdown
- **Claim:** The Great Hall ceiling is enchanted to mirror the sky outside.
  Evidence: "bewitched to look like the sky outside" (Philosopher's Stone, Chapter Seven, PDF p. 113, `ps-ch07-001`)
  Classification: original book core candidate; confidence: high.
  Note: Explicitly attributed to `Hogwarts: A History`.
```

Only show duplicate/corroboration text when it adds value.

Suppress:

```text
possible_duplicate=false
```

Replace:

```text
possible_duplicate=true; duplicate_of=ps-ch07-001
```

With:

```text
Corroborates: `ps-ch07-001`.
```

### 4. Separate Claims From Source Notes

The current generator treats `source_note` as the final `Fact`. That is workable but imprecise.

Prefer one of these two approaches:

Option A, no schema change:

- Keep source YAML as-is.
- In `generate_book_seed.py`, label the field as `Evidence note` instead of `Fact`.
- Generate section-level summaries from grouped `source_note` values.

Option B, schema enhancement:

- Add an optional entry field named `claim`.
- Keep `source_note` as the extraction note.
- Render `claim` in the final book seed when present.
- Fall back to `source_note` only when `claim` is absent.

Recommended: start with Option A because it avoids changing all historical YAML files. Add Option B only after the renderer is stable.

### 5. Richer Explicit References Appendix

`appendix/generated/explicit-hogwarts-a-history-references.md` should become the quick audit file for every explicit `Hogwarts: A History` reference.

Each item should include:

- destination part/chapter/section
- short quote
- book/chapter/page
- entry id
- source YAML path
- classification
- whether it is original-book core, confirmation, or later editorial context

This file should remain generated and secondary. The main book seed should still be the primary human result.

### 6. Validate the Main Generated Result

Extend validation so `scripts/validate_source_yaml.py` also checks:

- `book-seed/hogwarts-a-history-seed.md` exists
- it starts with `# Generated File`
- it contains `# Hogwarts: A History - Evidence-Backed Seed`
- it contains at least one `## Part:` heading when source entries exist
- no raw `possible_duplicate=false` appears in the final book seed after the rendering cleanup

This keeps the final result from drifting back into an overly mechanical format.

## Implementation Plan

All tasks should use the post-CLI-tooling recipes. Prefer:

```bash
just test
just validate
just generate
just post
```

over direct repeated `.venv/bin/python ...` command chains. Direct script commands are still acceptable inside tests or when debugging one specific script.

### Task 1: Add Explicit Book Seed Ordering

Files:

- Create: `project-control/book-seed-order.yaml`
- Modify: `scripts/generate_book_seed.py`
- Modify: `tests/test_refactor_support.py`

Steps:

- Run `just brief` for orientation.
- Use `just search "Candidate Parts"` and `just search "Origins of the School"` to locate the canonical part list without reading broad archives.
- Add a focused test that creates entries in two parts whose alphabetical order differs from the desired order.
- Add `book-seed-order.yaml` with the part order from `docs/instructions/background-guide.md`.
- Update `generate_book_seed.py` to load the order file when present.
- Render unknown parts, chapters, or sections after known ordered items.
- Run `just test`.
- Run `just generate`.

Acceptance criteria:

- The generated book seed follows deliberate part order.
- Missing order entries do not cause data loss.
- Existing source YAML does not need to change.
- `just test` passes.
- `just validate` passes.

### Task 2: Redesign Main Book Seed Rendering

Files:

- Modify: `scripts/generate_book_seed.py`
- Modify: `tests/test_refactor_support.py`

Steps:

- Use `just search "possible_duplicate=false"` and `just search "Duplicate / corroboration"` to locate the current raw rendering behavior.
- Use `just search "source_note"` to locate the current source-note rendering path.
- Add tests for section summaries and compact evidence bullets.
- Replace repeated full blocks with section summaries plus compact bullets.
- Rename entry-level `Fact` rendering to `Evidence note` or use a compact `Claim` label only when a future `claim` field exists.
- Suppress `possible_duplicate=false`.
- Render positive duplicate links as `Corroborates: ...`.
- Run `just test`.
- Run `just generate`.

Acceptance criteria:

- The final seed is shorter and easier to scan.
- Entry ids, source paths, page references, confidence, and classifications remain visible.
- No evidence traceability is lost.
- `rg "possible_duplicate=false" book-seed/hogwarts-a-history-seed.md` returns no matches after regeneration.

### Task 3: Enrich Explicit References Appendix

Files:

- Modify: `scripts/generate_appendices.py`
- Modify: `tests/test_refactor_support.py`

Steps:

- Use `just search "generate_explicit_references"` to locate the appendix generator.
- Use `just query-entries great-hall` or `just query-entries "hogwarts-a-history"` only if a compact index lookup is useful; do not open all source YAML files.
- Add a test for explicit reference appendix rows with destination, quote, page, id, and source path.
- Update `generate_explicit_references()` to include those fields.
- Keep the appendix generated-file notice.
- Run `just test`.
- Run `just generate`.

Acceptance criteria:

- Every explicit `Hogwarts: A History` reference is easy to audit without opening source YAML.
- The appendix remains secondary to the main book seed.
- `just validate` passes.

### Task 4: Add Main Output Validation

Files:

- Modify: `scripts/validate_source_yaml.py`
- Modify: `tests/test_refactor_support.py`

Steps:

- Use `just search "validate_generated_files"` to locate the current generated-file validation logic.
- Add validation tests for a valid generated book seed and a malformed generated book seed.
- Validate the generated file header and expected title.
- Validate that source entries imply at least one rendered part heading.
- After Task 2, reject raw `possible_duplicate=false` in the final book seed.
- Run `just test`.
- Run `just validate`.

Acceptance criteria:

- Validation catches missing or malformed main output.
- Validation still passes on the current source YAML.
- `just validate` runs the Python validator through the `Justfile`, not a placeholder.

### Task 5: Regenerate and Review

Files:

- Generated: `book-seed/hogwarts-a-history-seed.md`
- Generated: `appendix/generated/explicit-hogwarts-a-history-references.md`
- Generated: any other appendices touched by `generate_appendices.py`

Steps:

Run the compact normal post-generation recipe; the root `Justfile` contains its expanded implementation:

```bash
just post
```

Review:

- `rg "## Part:" book-seed/hogwarts-a-history-seed.md`
- top 200 lines of `book-seed/hogwarts-a-history-seed.md`
- explicit references appendix
- review flags appendix
- `git diff --stat`

Acceptance criteria:

- The generated book seed reads as a structured human-facing seed.
- The generated appendices remain audit-focused.
- Tests and validation pass.
- No normal extraction workflow regression is introduced.
- `just --list` still shows the expected workflow recipes.

## Short Expected Output Example

After this plan is implemented, a section in `book-seed/hogwarts-a-history-seed.md` should look closer to this:

```markdown
## Part: Magical Architecture and Enchantments

### Chapter: The Great Hall

#### Section: The Enchanted Ceiling

The current evidence establishes the Great Hall ceiling as a stable Hogwarts enchantment and an explicit topic recorded in `Hogwarts: A History`. The strongest source is Hermione's first-year explanation, with later feast scenes serving as confirmation rather than new original-book material.

- **Claim:** The Great Hall ceiling is bewitched to resemble the sky outside.
  Evidence: "bewitched to look like the sky outside" (Philosopher's Stone, Chapter Seven, PDF p. 113, `ps-ch07-001`)
  Classification: original book core candidate; confidence: high.
  Note: Explicitly attributed to `Hogwarts: A History`.

- **Confirmation:** Later Great Hall scenes continue to show the enchanted ceiling functioning during ordinary school meals and ceremonies.
  Evidence: "enchanted ceiling" (Chamber of Secrets, Chapter Five, PDF p. 343, `cos-ch05-004`)
  Classification: Harry-era confirmation; confidence: medium.
  Corroborates: `ps-ch07-001`.
```

The explicit references appendix should look closer to this:

```markdown
## Magical Architecture and Enchantments / The Great Hall / The Enchanted Ceiling

- `ps-ch07-001` - Philosopher's Stone, Chapter Seven, PDF p. 113
  Quote: "bewitched to look like the sky outside"
  Classification: original book core candidate
  Source YAML: `sources/book-01/chapter-07-sorting-hat.yaml`
```

## What Not To Do

- Do not manually edit generated files as the source of truth.
- Do not remove duplicate or corroborating source entries.
- Do not require normal extraction agents to read all prior YAML files.
- Do not change the source-gathering mission.
- Do not compact the source YAML schema until generators, validators, and index builders support both current and compact shapes.
- Do not require `yq`; use project Python scripts for YAML.
- Do not use shell `grep`/`awk` parsing for structured YAML state.
- Do not replace the `just` workflow with long repeated command chains in runtime instructions.

## Bottom Line

The project now has the efficiency foundation and CLI command surface it needed. The next pass should use `just` and `rg` to stay compact while making the final generated result easier to read, deliberately ordered, and less mechanical without weakening the evidence trail.
