# Next Run

Generated display only. Source of truth: `project-control/processing-state.yaml`.

## Current Source Unit

- Source file: `pdfs/Fantastic-Beasts-Where-to-Find-Them.pdf`
- Book group: `book-fb`
- Book: `Fantastic Beasts and Where to Find Them`
- Chapter: R-Z Bestiary Entries
- Page range: 57-64
- Rendered images: `.tmp/current-source-images/`
- Output YAML: `sources/book-fb/chapter-08-bestiary-r-to-z.yaml`

## Minimal Context

Read only:

- `docs/instructions/runtime-contract.md`
- `project-control/processing-state.yaml`
- `.tmp/current-source-images/` after rendering only the current page range
- Current output YAML only if it exists

Use `just query-dupes <tag> <tag>` for duplicate and context lookup after candidate
tags are known. Open only referenced YAML files for likely matches.
Use `just search "pattern"` or targeted `rg` before opening broad files.

Do not read appendices, archives, old prompts, full indexes, all prior YAML files, or
`chapters-index.md` during normal runs.
