# Runtime Contract

Use this compact contract for routine extraction runs. Read full background or schema files only when this contract says to.

## CLI Workflow

Prefer short project recipes over repeated long shell commands.

- Start orientation with `just brief`.
- Use `just next` for the current next-run display.
- Use `just search "pattern"` or direct `rg "pattern" path/` before reading broad files.
- Use `just query-dupes <tag> <tag>` for duplicate lookup after candidate tags are known.
- Use `just validate` after source YAML changes.
- Use `just post` after a completed extraction or generator change.

Do not require `yq`; use project Python scripts for YAML.
Use `jq` only for JSON output.

## Required Reads

For a normal run, read only:

1. `docs/instructions/runtime-contract.md`
2. `project-control/processing-state.yaml`
3. `.tmp/current-chapter.txt` after extraction
4. The current output YAML only if it already exists

## Conditional Reads

Read these only when needed:

- `docs/instructions/schema-reference.md` for schema uncertainty or validation failure.
- `docs/instructions/background-guide.md` for canon, era, or classification ambiguity.
- `just query-dupes <tag> <tag>` for duplicate and context lookup after candidate tags are known.
- `just query-entries <tag>` for compact entry lookup by tag.
- Query script source files only when debugging the query tools themselves.
- Historical YAML files only when a query recipe identifies a likely duplicate.
- `appendix/generated/*.md` only for human-facing review, not routine extraction.

## Prohibited During Normal Runs

Do not read:

- `docs/instructions/archive/`
- `project-control/archive/`
- old `next-run N.md` prompts
- full appendices or non-generated appendix drafts
- all prior chapter YAML files
- `chapters-index.md` when page boundaries are present in `processing-state.yaml`

## Extraction Procedure

1. Read `processing-state.yaml`.
2. Extract the inclusive current page range with `scripts/extract_pages.py`.
3. Write combined text to `.tmp/current-chapter.txt`.
4. Identify evidence that supports a future fan edition of `Hogwarts: A History`.
5. Extract all explicit `Hogwarts: A History` references.
6. For supporting material, keep only the strongest 3-7 entries unless instructed otherwise.
7. Use short quotes only; keep `quote_excerpt_short` under 25 words.

## Duplicate Check Procedure

1. Normalize 3-8 topic tags for each candidate.
2. Run `just query-dupes <tag> <tag>` with candidate tags and placement terms.
3. If no likely match appears, mark `possible_duplicate: false`.
4. If a likely match appears, open only the referenced YAML file and compare evidence.
5. Do not open full index files during normal extraction.
6. Record the result in the entry `duplicate_check` block.

## Output Steps

1. Write or update the current chapter YAML path in `processing-state.yaml`.
2. Keep full chapter YAML self-contained and schema-compliant.
3. Run `just post`.
4. Keep `book-seed/hogwarts-a-history-seed.md` as the main human-readable result.
5. Keep `appendix/generated/*.md` as generated support/reference files.

## Validation Checklist

- YAML parses with PyYAML.
- Required top-level keys exist: `source_unit`, `entries`.
- Every entry has an `id`, source location, short quote, `source_note`, tags, classification, duplicate check, confidence, and limitations.
- `reference_type` and `era_classification` use values from `schema-reference.md`.
- Changed indexes parse as YAML.
- Generated appendices start with the generated-file notice.
- Run `just validate` after changing source YAML or generated helper files.
- Run `just post` when appendices are regenerated or after each completed source unit.

## Git Backup Rule

After every successful extraction or refactor iteration:

1. Stage only files that belong to the iteration.
2. Do not stage `.DS_Store`, caches, virtual environments, or unrelated user changes.
3. Run relevant validation.
4. Review `git status --short`.
5. Review the staged diff.
6. Commit with a concise message.
7. Push the current branch to `origin`.
