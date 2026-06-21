# Next Run

Generated display only. Source of truth: `project-control/processing-state.yaml`.

## Current Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-04`
- Book: `Harry Potter and the Goblet of Fire`
- Chapter: Chapter Eleven - Aboard the Hogwarts Express
- Page range: 1078-1088
- Extracted text: `.tmp/current-chapter.txt`
- Output YAML: `sources/book-04/chapter-11-aboard-the-hogwarts-express.yaml`

## Minimal Context

Read only:

- `docs/instructions/runtime-contract.md`
- `project-control/processing-state.yaml`
- `.tmp/current-chapter.txt`
- Current output YAML only if it exists

Use `just query-dupes <tag> <tag>` for duplicate and context lookup after candidate
tags are known. Open only referenced YAML files for likely matches.
Use `just search "pattern"` or targeted `rg` before opening broad files.

Do not read appendices, archives, old prompts, full indexes, all prior YAML files, or
`chapters-index.md` during normal runs.
