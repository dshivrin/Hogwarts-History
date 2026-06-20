# Next Run

Use the automation control files instead of a custom chapter prompt:

- `project-control/source-plan.yaml`
- `project-control/processing-state.yaml`
- `project-control/next-run.md`

## Next Pending Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-02`
- Book: `Harry Potter and the Chamber of Secrets`
- Chapter: Chapter Seventeen - The Heir of Slytherin
- Output file: `sources/book-02/chapter-17-the-heir-of-slytherin.yaml`

## Run Instructions

Process exactly one source unit: Book 2, Chapter Seventeen - The Heir of Slytherin.

Use `chapters-index.md` for the chapter boundary:

- Book 2, Chapter 17 - The Heir of Slytherin: PDF pages 536-552.

Use the prior Book 2 Chapter Sixteen boundary:

- Book 2, Chapter Sixteen starts on PDF page 517.
- Book 2, Chapter Sixteen ends on PDF page 535.
- Book 2, Chapter Seventeen starts on PDF page 536.
- Book 2, Chapter Eighteen starts on PDF page 553.

Do not scan the full collection PDF from page 1. Extract and search only the bounded Chapter Seventeen range, PDF pages 536-552.

Use the reusable extraction script; do not write a one-off Python extractor for this run:

```bash
.venv/bin/python scripts/extract_pages.py \
  --pdf pdfs/harrypotter.pdf \
  --start-page 536 \
  --end-page 552 \
  --output .tmp/book-02-chapter-17-the-heir-of-slytherin.txt \
  --per-page-dir .tmp/book-02-chapter-17-the-heir-of-slytherin-pages
```

After processing:

1. Validate modified YAML files with `.venv/bin/python` and PyYAML.
2. If validation passes, mark Book 2 Chapter Seventeen complete in `project-control/source-plan.yaml`.
3. Update `project-control/processing-state.yaml`.
4. Rewrite this file with the next pending source unit.
5. Always advance `next_pending` to the next chapter in the ordered plan. Do not set `next_pending: null` while another chapter in `pdfs/harrypotter.pdf` remains to be added or processed.
