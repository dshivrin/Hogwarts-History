# Next Run

Generated display only. Source of truth: `project-control/processing-state.yaml`.

## Current Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-04`
- Book: `Harry Potter and the Goblet of Fire`
- Chapter: Chapter Two - The Scar
- Page range: 961-968
- Extracted text: `.tmp/current-chapter.txt`
- Output YAML: `sources/book-04/chapter-02-the-scar.yaml`

## Minimal Context

Read only:

- `docs/instructions/runtime-contract.md`
- `project-control/processing-state.yaml`
- `.tmp/current-chapter.txt`
- Current output YAML only if it exists

Use `rg "<tag-or-topic>" project-control/tag-index.yaml project-control/duplicate-index.yaml`
for duplicate and context lookup. Open only referenced YAML files for likely matches.

Do not read appendices, archives, old prompts, full indexes, all prior YAML files, or
`chapters-index.md` during normal runs.
