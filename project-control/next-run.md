# Next Run

Use the automation control files instead of a custom chapter prompt:

- `project-control/source-plan.yaml`
- `project-control/processing-state.yaml`
- `project-control/next-run.md`

## Next Pending Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-04`
- Book: `Harry Potter and the Goblet of Fire`
- Chapter: Chapter Two - The Scar
- Output file: `sources/book-04/chapter-02-the-scar.yaml`

## Run Instructions

Process exactly one source unit: Book 4, Chapter Two - The Scar.

Use `chapters-index.md` for the chapter boundary:

- Book 4, Chapter 2 - The Scar: PDF pages 961-968.
- Book 4, Chapter 3 - The Invitation starts on PDF page 969.

Use the prior Book 4 Chapter One boundary:

- Book 4 Chapter One starts on PDF page 949.
- Book 4 Chapter One ends on PDF page 960.
- Book 4 Chapter Two starts on PDF page 961.

Do not scan the full collection PDF from page 1. Extract and search only the bounded Chapter Two range, PDF pages 961-968.

Use the reusable extraction script; do not write a one-off Python extractor for this run:

```bash
.venv/bin/python scripts/extract_pages.py \
  --pdf pdfs/harrypotter.pdf \
  --start-page 961 \
  --end-page 968 \
  --output .tmp/book-04-chapter-02-the-scar.txt \
  --per-page-dir .tmp/book-04-chapter-02-the-scar-pages
```

After processing:

1. Validate modified YAML files with `.venv/bin/python` and PyYAML.
2. If validation passes, mark Book 4 Chapter Two complete in `project-control/source-plan.yaml`.
3. Update `project-control/processing-state.yaml`.
4. Rewrite this file with the next pending source unit.
5. Always advance `next_pending` to the next chapter in the ordered plan. Do not set `next_pending: null` while another chapter in `pdfs/harrypotter.pdf` remains to be added or processed.
