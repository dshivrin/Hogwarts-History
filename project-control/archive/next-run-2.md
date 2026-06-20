# Next Run

Use the automation control files instead of a custom chapter prompt:

- `project-control/source-plan.yaml`
- `project-control/processing-state.yaml`
- `project-control/next-run.md`

## Next Pending Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-02`
- Book: `Harry Potter and the Chamber of Secrets`
- Chapter: Chapter Four - At Flourish and Blotts
- Output file: `sources/book-02/chapter-04-at-flourish-and-blotts.yaml`

## Run Instructions

Process exactly one source unit: Book 2, Chapter Four - At Flourish and Blotts.

Use `chapters-index.md` for the chapter boundary:

- Book 2, Chapter 4 - At Flourish and Blotts: PDF pages 316-334.

Use the prior Book 2 Chapter Three boundary:

- Book 2, Chapter Three starts on PDF page 301.
- Book 2, Chapter Three ends on PDF page 315.
- Book 2, Chapter Four starts on PDF page 316.
- Book 2, Chapter Five starts on PDF page 335.

Do not scan the full collection PDF from page 1. Extract and search only the bounded Chapter Four range, PDF pages 316-334.

Use the reusable extraction script; do not write a one-off Python extractor for this run:

```bash
.venv/bin/python scripts/extract_pages.py \
  --pdf pdfs/harrypotter.pdf \
  --start-page 316 \
  --end-page 334 \
  --output .tmp/book-02-chapter-04-at-flourish-and-blotts.txt \
  --per-page-dir .tmp/book-02-chapter-04-at-flourish-and-blotts-pages
```

After processing:

1. Validate modified YAML files with `.venv/bin/python` and PyYAML.
2. If validation passes, mark Book 2 Chapter Four complete in `project-control/source-plan.yaml`.
3. Update `project-control/processing-state.yaml`.
4. Rewrite this file with the next pending source unit.
5. Always advance `next_pending` to the next chapter in the ordered plan. Do not set `next_pending: null` while another chapter in `pdfs/harrypotter.pdf` remains to be added or processed.
