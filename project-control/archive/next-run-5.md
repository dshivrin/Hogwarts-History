# Next Run

Use the automation control files instead of a custom chapter prompt:

- `project-control/source-plan.yaml`
- `project-control/processing-state.yaml`
- `project-control/next-run.md`

## Next Pending Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-02`
- Book: `Harry Potter and the Chamber of Secrets`
- Chapter: Chapter Twelve - The Polyjuice Potion
- Output file: `sources/book-02/chapter-12-the-polyjuice-potion.yaml`

## Run Instructions

Process exactly one source unit: Book 2, Chapter Twelve - The Polyjuice Potion.

Use `chapters-index.md` for the chapter boundary:

- Book 2, Chapter 12 - The Polyjuice Potion: PDF pages 453-470.

Use the prior Book 2 Chapter Eleven boundary:

- Book 2, Chapter Eleven starts on PDF page 434.
- Book 2, Chapter Eleven ends on PDF page 452.
- Book 2, Chapter Twelve starts on PDF page 453.
- Book 2, Chapter Thirteen starts on PDF page 471.

Do not scan the full collection PDF from page 1. Extract and search only the bounded Chapter Twelve range, PDF pages 453-470.

Use the reusable extraction script; do not write a one-off Python extractor for this run:

```bash
.venv/bin/python scripts/extract_pages.py \
  --pdf pdfs/harrypotter.pdf \
  --start-page 453 \
  --end-page 470 \
  --output .tmp/book-02-chapter-12-the-polyjuice-potion.txt \
  --per-page-dir .tmp/book-02-chapter-12-the-polyjuice-potion-pages
```

After processing:

1. Validate modified YAML files with `.venv/bin/python` and PyYAML.
2. If validation passes, mark Book 2 Chapter Twelve complete in `project-control/source-plan.yaml`.
3. Update `project-control/processing-state.yaml`.
4. Rewrite this file with the next pending source unit.
5. Always advance `next_pending` to the next chapter in the ordered plan. Do not set `next_pending: null` while another chapter in `pdfs/harrypotter.pdf` remains to be added or processed.
