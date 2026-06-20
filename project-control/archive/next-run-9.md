# Next Run

Use the automation control files instead of a custom chapter prompt:

- `project-control/source-plan.yaml`
- `project-control/processing-state.yaml`
- `project-control/next-run.md`

## Next Pending Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-03`
- Book: `Harry Potter and the Prisoner of Azkaban`
- Chapter: Chapter Nineteen - The Servant of Lord Voldemort
- Output file: `sources/book-03/chapter-19-the-servant-of-lord-voldemort.yaml`

## Run Instructions

Process exactly one source unit: Book 3, Chapter Nineteen - The Servant of Lord Voldemort.

Use `chapters-index.md` for the chapter boundary:

- Book 3, Chapter 19 - The Servant of Lord Voldemort: PDF pages 874-890.
- Book 3, Chapter 20 - The Dementor's Kiss: PDF pages 891-897.

Use the prior Book 3 Chapter Eighteen boundary:

- Book 3 Chapter Eighteen starts on PDF page 867.
- Book 3 Chapter Eighteen ends on PDF page 873.
- Book 3 Chapter Nineteen starts on PDF page 874.
- Book 3 Chapter Twenty starts on PDF page 891.

Do not scan the full collection PDF from page 1. Extract and search only the bounded Chapter Nineteen range, PDF pages 874-890.

Use the reusable extraction script; do not write a one-off Python extractor for this run:

```bash
.venv/bin/python scripts/extract_pages.py \
  --pdf pdfs/harrypotter.pdf \
  --start-page 874 \
  --end-page 890 \
  --output .tmp/book-03-chapter-19-the-servant-of-lord-voldemort.txt \
  --per-page-dir .tmp/book-03-chapter-19-the-servant-of-lord-voldemort-pages
```

After processing:

1. Validate modified YAML files with `.venv/bin/python` and PyYAML.
2. If validation passes, mark Book 3 Chapter Nineteen complete in `project-control/source-plan.yaml`.
3. Update `project-control/processing-state.yaml`.
4. Rewrite this file with the next pending source unit.
5. Always advance `next_pending` to the next chapter in the ordered plan. Do not set `next_pending: null` while another chapter in `pdfs/harrypotter.pdf` remains to be added or processed.
