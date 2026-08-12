# Next Run

Generated display only. Source of truth: `project-control/processing-state.yaml`.

## Current Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-07`
- Book: `Harry Potter and the Deathly Hallows`
- Chapter: Chapter Thirty-Six - The Flaw in the Plan
- Page range: 3594-3615
- Extracted text: `.tmp/current-chapter.txt`
- Output YAML: `sources/book-07/chapter-36-the-flaw-in-the-plan.yaml`

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
