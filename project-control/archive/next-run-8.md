# Next Run

Use the automation control files instead of a custom chapter prompt:

- `project-control/source-plan.yaml`
- `project-control/processing-state.yaml`
- `project-control/next-run.md`

## Next Pending Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-03`
- Book: `Harry Potter and the Prisoner of Azkaban`
- Chapter: Chapter Thirteen - Gryffindor Versus Ravenclaw
- Output file: `sources/book-03/chapter-13-gryffindor-versus-ravenclaw.yaml`

## Run Instructions

Process exactly one source unit: Book 3, Chapter Thirteen - Gryffindor Versus Ravenclaw.

Use `chapters-index.md` for the chapter boundary:

- Book 3, Chapter 13 - Gryffindor Versus Ravenclaw: PDF pages 785-798.
- Book 3, Chapter 14 - Snape's Grudge: PDF pages 799-817.

Use the prior Book 3 Chapter Twelve boundary:

- Book 3 Chapter Twelve starts on PDF page 768.
- Book 3 Chapter Twelve ends on PDF page 784.
- Book 3 Chapter Thirteen starts on PDF page 785.
- Book 3 Chapter Fourteen starts on PDF page 799.

Do not scan the full collection PDF from page 1. Extract and search only the bounded Chapter Thirteen range, PDF pages 785-798.

Use the reusable extraction script; do not write a one-off Python extractor for this run:

```bash
.venv/bin/python scripts/extract_pages.py \
  --pdf pdfs/harrypotter.pdf \
  --start-page 785 \
  --end-page 798 \
  --output .tmp/book-03-chapter-13-gryffindor-versus-ravenclaw.txt \
  --per-page-dir .tmp/book-03-chapter-13-gryffindor-versus-ravenclaw-pages
```

After processing:

1. Validate modified YAML files with `.venv/bin/python` and PyYAML.
2. If validation passes, mark Book 3 Chapter Thirteen complete in `project-control/source-plan.yaml`.
3. Update `project-control/processing-state.yaml`.
4. Rewrite this file with the next pending source unit.
5. Always advance `next_pending` to the next chapter in the ordered plan. Do not set `next_pending: null` while another chapter in `pdfs/harrypotter.pdf` remains to be added or processed.
