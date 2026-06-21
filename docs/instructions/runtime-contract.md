# Runtime Contract

Use this compact contract for routine extraction runs. Read full background or schema files only when this contract says to.

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
- `scripts/query_duplicates.py` for duplicate and context lookup.
- `scripts/query_entries.py` for compact entry lookup by tag, classification, source unit, or output YAML.
- Historical YAML files only when a query script identifies a likely duplicate.
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
2. Run `scripts/query_duplicates.py` with candidate tags and placement terms.
3. If no likely match appears, mark `possible_duplicate: false`.
4. If a likely match appears, open only the referenced YAML file and compare evidence.
5. Do not open full index files during normal extraction.
6. Record the result in the entry `duplicate_check` block.

## Output Steps

1. Write or update the current chapter YAML path in `processing-state.yaml`.
2. Keep full chapter YAML self-contained and schema-compliant.
3. Rebuild compact indexes:
   - `scripts/build_duplicate_index.py`
   - `scripts/build_entry_index.py`
   - `scripts/build_tag_index.py`
4. Run `scripts/validate_source_yaml.py` after changing source YAML or generated helper files.
5. Run `scripts/generate_book_seed.py` when appendices are regenerated or after each completed source unit.
6. Regenerate `project-control/next-run.md` from `processing-state.yaml`.
7. Regenerate appendices only when needed with `scripts/generate_appendices.py`.
8. Run `scripts/cleanup_tmp.py` after extraction artifacts are no longer needed.

## Validation Checklist

- YAML parses with PyYAML.
- Required top-level keys exist: `source_unit`, `entries`.
- Every entry has an `id`, source location, short quote, `source_note`, tags, classification, duplicate check, confidence, and limitations.
- `reference_type` and `era_classification` use values from `schema-reference.md`.
- Changed indexes parse as YAML.
- Generated appendices start with the generated-file notice.
- Run `scripts/validate_source_yaml.py` after changing source YAML or generated helper files.
- Run `scripts/generate_book_seed.py` when appendices are regenerated or after each completed source unit.

## Git Backup Rule

After every successful extraction or refactor iteration:

1. Stage only files that belong to the iteration.
2. Do not stage `.DS_Store`, caches, virtual environments, or unrelated user changes.
3. Run relevant validation.
4. Review `git status --short`.
5. Review the staged diff.
6. Commit with a concise message.
7. Push the current branch to `origin`.
