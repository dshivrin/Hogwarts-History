# Next Run

Use the automation control files instead of a custom chapter prompt:

- `project-control/source-plan.yaml`
- `project-control/processing-state.yaml`
- `project-control/next-run.md`

## Next Pending Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-02`
- Book: `Harry Potter and the Chamber of Secrets`
- Chapter: Chapter Fourteen - Cornelius Fudge
- Output file: `sources/book-02/chapter-14-cornelius-fudge.yaml`

## Run Instructions

Process exactly one source unit: Book 2, Chapter Fourteen - Cornelius Fudge.

Use `chapters-index.md` for the chapter boundary:

- Book 2, Chapter 14 - Cornelius Fudge: PDF pages 489-501.

Use the prior Book 2 Chapter Thirteen boundary:

- Book 2, Chapter Thirteen starts on PDF page 471.
- Book 2, Chapter Thirteen ends on PDF page 488.
- Book 2, Chapter Fourteen starts on PDF page 489.
- Book 2, Chapter Fifteen starts on PDF page 502.

Do not scan the full collection PDF from page 1. Extract and search only the bounded Chapter Fourteen range, PDF pages 489-501.

Use the reusable extraction script; do not write a one-off Python extractor for this run:

```bash
.venv/bin/python scripts/extract_pages.py \
  --pdf pdfs/harrypotter.pdf \
  --start-page 489 \
  --end-page 501 \
  --output .tmp/book-02-chapter-14-cornelius-fudge.txt \
  --per-page-dir .tmp/book-02-chapter-14-cornelius-fudge-pages
```

After processing:

1. Validate modified YAML files with `.venv/bin/python` and PyYAML.
2. If validation passes, mark Book 2 Chapter Fourteen complete in `project-control/source-plan.yaml`.
3. Update `project-control/processing-state.yaml`.
4. Rewrite this file with the next pending source unit.
5. Always advance `next_pending` to the next chapter in the ordered plan. Do not set `next_pending: null` while another chapter in `pdfs/harrypotter.pdf` remains to be added or processed.
