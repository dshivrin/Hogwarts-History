# Next Run

Use the automation control files instead of a custom chapter prompt:

- `project-control/source-plan.yaml`
- `project-control/processing-state.yaml`
- `project-control/next-run.md`

## Next Pending Source Unit

- Source file: `pdfs/harrypotter.pdf`
- Book group: `book-02`
- Book: `Harry Potter and the Chamber of Secrets`
- Chapter: Chapter Five - The Whomping Willow
- Output file: `sources/book-02/chapter-05-whomping-willow.yaml`

## Run Instructions

Process exactly one source unit: Book 2, Chapter Five - The Whomping Willow.

Use `chapters-index.md` for the chapter boundary:

- Book 2, Chapter 5 - The Whomping Willow: PDF pages 335-352.

Use the prior Book 2 Chapter Four boundary:

- Book 2, Chapter Four starts on PDF page 316.
- Book 2, Chapter Four ends on PDF page 334.
- Book 2, Chapter Five starts on PDF page 335.
- Book 2, Chapter Six starts on PDF page 353.

Do not scan the full collection PDF from page 1. Extract and search only the bounded Chapter Five range, PDF pages 335-352.

Use the reusable extraction script; do not write a one-off Python extractor for this run:

```bash
.venv/bin/python scripts/extract_pages.py \
  --pdf pdfs/harrypotter.pdf \
  --start-page 335 \
  --end-page 352 \
  --output .tmp/book-02-chapter-05-whomping-willow.txt \
  --per-page-dir .tmp/book-02-chapter-05-whomping-willow-pages
```

After processing:

1. Validate modified YAML files with `.venv/bin/python` and PyYAML.
2. If validation passes, mark Book 2 Chapter Five complete in `project-control/source-plan.yaml`.
3. Update `project-control/processing-state.yaml`.
4. Rewrite this file with the next pending source unit.
5. Always advance `next_pending` to the next chapter in the ordered plan. Do not set `next_pending: null` while another chapter in `pdfs/harrypotter.pdf` remains to be added or processed.
