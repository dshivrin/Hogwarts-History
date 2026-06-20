# Next Run

Use the automation control files instead of a custom chapter prompt:

- `project-control/source-plan.yaml`
- `project-control/processing-state.yaml`
- `project-control/next-run.md`

## Next Pending Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-02`
- Book: `Harry Potter and the Chamber of Secrets`
- Chapter: Chapter Nine - The Writing on the Wall
- Output file: `sources/book-02/chapter-09-the-writing-on-the-wall.yaml`

## Run Instructions

Process exactly one source unit: Book 2, Chapter Nine - The Writing on the Wall.

Use `chapters-index.md` for the chapter boundary:

- Book 2, Chapter 9 - The Writing on the Wall: PDF pages 399-416.

Use the prior Book 2 Chapter Eight boundary:

- Book 2, Chapter Eight starts on PDF page 383.
- Book 2, Chapter Eight ends on PDF page 398.
- Book 2, Chapter Nine starts on PDF page 399.
- Book 2, Chapter Ten starts on PDF page 417.

Do not scan the full collection PDF from page 1. Extract and search only the bounded Chapter Nine range, PDF pages 399-416.

Use the reusable extraction script; do not write a one-off Python extractor for this run:

```bash
.venv/bin/python scripts/extract_pages.py \
  --pdf pdfs/harrypotter.pdf \
  --start-page 399 \
  --end-page 416 \
  --output .tmp/book-02-chapter-09-the-writing-on-the-wall.txt \
  --per-page-dir .tmp/book-02-chapter-09-the-writing-on-the-wall-pages
```

After processing:

1. Validate modified YAML files with `.venv/bin/python` and PyYAML.
2. If validation passes, mark Book 2 Chapter Nine complete in `project-control/source-plan.yaml`.
3. Update `project-control/processing-state.yaml`.
4. Rewrite this file with the next pending source unit.
5. Always advance `next_pending` to the next chapter in the ordered plan. Do not set `next_pending: null` while another chapter in `pdfs/harrypotter.pdf` remains to be added or processed.
