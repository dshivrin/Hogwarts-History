# Next Run

Generated display only. Source of truth: `project-control/processing-state.yaml`.

## Current Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-04`
- Book: `Harry Potter and the Goblet of Fire`
- Chapter: Chapter Seven - Bagman and Crouch
- Page range: 1009-1025
- Extracted text: `.tmp/current-chapter.txt`
- Output YAML: `sources/book-04/chapter-07-bagman-and-crouch.yaml`

## Minimal Context

Read only:

- `docs/instructions/runtime-contract.md`
- `project-control/processing-state.yaml`
- `.tmp/current-chapter.txt`
- Current output YAML only if it exists

Use `scripts/query_duplicates.py` for duplicate and context lookup. Open only referenced
YAML files for likely matches.

Do not read appendices, archives, old prompts, full indexes, all prior YAML files, or
`chapters-index.md` during normal runs.
