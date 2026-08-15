# Hogwarts: A History Fanfic Reference Dataset — Acquisition Plan

## Objective

Create a reproducible local dataset of publicly accessible fan-written works that imitate, reinterpret, or borrow the concept of *Hogwarts: A History*.

For every accepted source, produce:

1. One complete PDF per work.
2. One normalized text file per chapter.
3. The original captured HTML for traceability.
4. A machine-readable manifest containing source and chapter metadata.
5. A validation report proving that every available chapter was captured once and in the correct order.

The dataset will be used to compare styles, structures, topics, invented claims, and chapter coverage against chapters produced for the **Hogwarts: A History** project.

This dataset is **not canon evidence**. Every extracted claim must remain labeled as fan-created material.

---

## Confirmed source inventory

### HAH-FAN-001 — Primary reference

- **Title:** Hogwarts: A History
- **Author:** Unclebulgaria5
- **URL:** https://www.fanfiction.net/s/3626803/1/Hogwarts-A-History
- **Platform:** FanFiction.net
- **Published:** 2007
- **Available chapters:** 6
- **Displayed word count:** 9,703
- **Priority:** High
- **Why include it:** This is the closest discovered attempt to write the in-universe history book itself. It contains a contents page, introduction, historical periods, the founders, and a tour of the castle and grounds.
- **Known limitation:** Its contents page promises more chapters than are actually available, and the author notes that Chapter Four was lost. Capture only chapters that are publicly available; record missing promised chapters in the manifest.
- **Acquisition method:** Page-by-page capture, followed by PDF merge.

### HAH-FAN-002 — Textbook structure reference

- **Title:** Hogwarts: A History
- **Author:** Paperback Reitter
- **URL:** https://www.fanfiction.net/s/2905421/1/Hogwarts-A-History
- **Platform:** FanFiction.net
- **Published:** 2006
- **Available chapters:** 3
- **Displayed word count:** 1,239
- **Priority:** Medium
- **Why include it:** It explicitly describes itself as “textbook” fanfiction and provides a broad proposed table of contents covering the founders, construction, wards, disputes, headmasters, the Chamber of Secrets, and later Hogwarts.
- **Known limitation:** Very incomplete and contains out-of-character author notes. Preserve those notes but mark them as editorial material rather than in-universe prose.
- **Acquisition method:** Page-by-page capture, followed by PDF merge.

### HAH-FAN-003 — Alternative narrative voice reference

- **Title:** Hogwarts, A History Revised
- **Author:** Scutie-Naos
- **URL:** https://www.fanfiction.net/s/11672247/1/Hogwarts-A-History-Revised
- **Platform:** FanFiction.net
- **Published:** 2015
- **Last displayed update:** 2016
- **Available chapters:** 6
- **Displayed word count:** 25,338
- **Priority:** High for style; medium for factual comparison
- **Why include it:** The history is narrated by Hogwarts itself as a memoir. This provides a useful contrast to a conventional Bathilda Bagshot reference-book voice.
- **Known limitation:** It is character-driven fanfiction with framing scenes and invented metaphysics, not a neutral institutional history.
- **Acquisition method:** Page-by-page capture, followed by PDF merge.

### HAH-FAN-004 — Short foreword reference

- **Title:** Hogwarts: A History
- **Author:** manbigpog
- **URL:** https://www.fanfiction.net/s/13004712/1/Hogwarts-A-History
- **Platform:** FanFiction.net
- **Published:** 2018
- **Available chapters:** 1
- **Displayed word count:** 175
- **Priority:** Low
- **Why include it:** It is a concise in-universe Bathilda Bagshot introduction and may be useful when comparing forewords, tone, and opening conventions.
- **Known limitation:** It is only a short introduction, not a developed history.
- **Acquisition method:** Single-page capture and PDF generation.

---

## Discovered but excluded by default

### Hogwarts: A History (Hermione’s Version) — Lizzie_carlile

- **Discovery page:** https://www.tumblr.com/ao3feed-dramione/680116845121093632/hogwarts-a-history-hermiones-version
- **Original platform:** Archive of Our Own
- **Reason for exclusion:** The title refers to Hermione’s alternate life story. It is a Dramione alternate-universe narrative rather than a reconstruction or imitation of Bathilda Bagshot’s history book.
- **Action:** Do not ingest into the core historical-reference dataset. Optionally record it in a separate `title-collision-exclusions.json` file so future searches do not repeatedly rediscover it.
- **Important:** If later accepted for broader stylistic analysis, use AO3’s native download control instead of scraping chapter pages.

---

## Valid-source rules

A source is valid for the core dataset only when all of the following are true:

1. It is publicly accessible from the author’s posting page without bypassing login, payment, access controls, or a CAPTCHA.
2. The work presents itself as a history, textbook, chronicle, memoir of Hogwarts, or another direct reinterpretation of the fictional book.
3. The source page clearly identifies the work and author.
4. The text can be captured without copying reviews, advertisements, navigation menus, unrelated recommendations, or user-account data.
5. The capture is for private research and comparison; generated files must not be redistributed or presented as authorized editions.

Reject or quarantine:

- Ordinary stories that merely use *Hogwarts: A History* in the title.
- Reposts or mirrors with unclear provenance.
- Search-result snippets without an identifiable author page.
- Sold fanfiction copies.
- Sources requiring access-control circumvention.
- Pages blocked by the site’s terms, robots policy, or technical safeguards.

---

## Repository layout

Use the following structure relative to the project root:

```text
data/
  fanfic-hogwarts-history/
    README.md
    manifest.jsonl
    works/
      HAH-FAN-001/
        metadata.json
        raw/
          chapter-001.html
          chapter-002.html
        clean/
          chapter-001.html
          chapter-002.html
        text/
          chapter-001.md
          chapter-002.md
        pdf/
          chapter-001.pdf
          chapter-002.pdf
          HAH-FAN-001-complete.pdf
        validation.json
      HAH-FAN-002/
      HAH-FAN-003/
      HAH-FAN-004/
    reports/
      acquisition-report.md
      validation-report.md
      title-collision-exclusions.json
```

Do not place generated PDFs beside the canonical Rowling source PDFs. Fan-created material must remain in a clearly separate directory.

---

## Manifest schema

Store one JSON object per available chapter in `manifest.jsonl`.

Required fields:

```json
{
  "dataset_version": "1.0",
  "source_id": "HAH-FAN-001",
  "work_title": "Hogwarts: A History",
  "author": "Unclebulgaria5",
  "platform": "fanfiction.net",
  "work_url": "https://www.fanfiction.net/s/3626803/1/Hogwarts-A-History",
  "chapter_index": 1,
  "chapter_title": "Contents",
  "chapter_url": "https://www.fanfiction.net/s/3626803/1/Hogwarts-A-History",
  "retrieved_at_utc": "<ISO-8601 timestamp>",
  "published_date_displayed": "2007-06-30",
  "updated_date_displayed": "2007-07-05",
  "expected_available_chapter_count": 6,
  "raw_html_path": "works/HAH-FAN-001/raw/chapter-001.html",
  "clean_html_path": "works/HAH-FAN-001/clean/chapter-001.html",
  "text_path": "works/HAH-FAN-001/text/chapter-001.md",
  "chapter_pdf_path": "works/HAH-FAN-001/pdf/chapter-001.pdf",
  "complete_pdf_path": "works/HAH-FAN-001/pdf/HAH-FAN-001-complete.pdf",
  "raw_sha256": "<hash>",
  "text_sha256": "<hash>",
  "fan_created": true,
  "canon_status": "non-canon fanfiction",
  "dataset_role": "style-and-coverage-reference"
}
```

Optional analysis fields:

- `topic_tags`
- `narrative_voice`
- `in_universe_ratio`
- `contains_author_notes`
- `contains_missing_chapter_notice`
- `promised_but_unavailable_chapters`
- `style_notes`
- `possible_canon_conflicts`

---

## Acquisition strategy

### Rule 1 — Prefer an official download option

Before scraping, inspect the author’s original posting page for a native download or export option.

Preferred order:

1. Native PDF download.
2. Native EPUB download, retained as an original artifact and converted to PDF.
3. Native HTML download, retained and converted to PDF.
4. Browser print-to-PDF for the complete work.
5. Page-by-page capture when none of the above exists.

Never use third-party “fanfiction downloader” sites unless their provenance and compliance are explicitly reviewed and approved.

### Rule 2 — FanFiction.net page-by-page capture

The four confirmed core sources currently require chapter-by-chapter processing.

For each work:

1. Open Chapter 1 using Playwright.
2. Read work metadata from the page:
   - title;
   - author;
   - summary;
   - rating;
   - language;
   - displayed chapter count;
   - displayed word count;
   - published date;
   - updated date;
   - work ID.
3. Read the chapter selector and collect every available canonical chapter URL.
4. Visit each chapter URL in numeric order.
5. Wait for the story text and chapter heading to be visible.
6. Save the full response HTML unchanged under `raw/`.
7. Extract a clean document containing only:
   - work title;
   - author;
   - source URL;
   - chapter number and title;
   - summary and public metadata on the first chapter only;
   - author notes associated with that chapter;
   - chapter text.
8. Exclude:
   - menus;
   - site footer;
   - reviews;
   - recommended stories;
   - sign-in UI;
   - tracking scripts;
   - advertisements.
9. Save cleaned semantic HTML under `clean/`.
10. Save normalized UTF-8 Markdown under `text/`.
11. Print the clean HTML to a chapter PDF with Playwright.
12. Merge chapter PDFs in numeric order into one work-level PDF.
13. Record hashes and validation data.

Use resilient extraction based on page meaning rather than relying on a single brittle CSS class. Permit a small list of fallback selectors for the story body and chapter title. If none matches, stop that work and write a diagnostic artifact rather than saving an empty or incorrect file.

### Rule 3 — Rate limits and site protection

- Run sequentially, not concurrently.
- Wait at least 3 seconds between chapter requests, with small random jitter.
- Reuse one browser context.
- Identify the tool with a normal browser user agent; do not impersonate a crawler or rotate identities.
- Do not bypass Cloudflare, CAPTCHAs, login requirements, or blocked requests.
- On HTTP 429 or access denial, stop and record the failure.
- Cache completed chapters and never refetch an unchanged chapter during the same run.

---

## PDF specification

Produce **one final PDF per valid work**.

Each final PDF should contain:

1. A generated provenance page, clearly separate from the fanfic text:
   - title;
   - author;
   - original source URL;
   - platform;
   - retrieval timestamp;
   - statement: “Fan-created, non-canon material captured for private comparative research.”
2. A generated table of contents based on available chapter titles.
3. Every publicly available chapter in source order.
4. Chapter separators and stable bookmarks.
5. Page numbers.

Do not:

- rewrite the fanfic;
- silently correct grammar;
- remove author notes without recording that decision;
- add invented missing chapters;
- merge multiple authors into one PDF;
- use Rowling book branding, cover art, or publisher marks;
- describe the PDF as an official or authorized edition.

Suggested filename format:

```text
<source-id>__<slugified-title>__<slugified-author>.pdf
```

Examples:

```text
HAH-FAN-001__hogwarts-a-history__unclebulgaria5.pdf
HAH-FAN-003__hogwarts-a-history-revised__scutie-naos.pdf
```

---

## Text normalization

The normalized chapter text is intended for search and comparison, not presentation.

Apply only mechanical normalization:

- UTF-8 encoding;
- Unix line endings;
- normalize non-breaking spaces;
- preserve paragraph boundaries;
- preserve emphasis where detectable;
- preserve chapter and section headings;
- retain author notes with explicit markers;
- remove duplicated site header/footer text;
- remove review and navigation UI.

Do not alter spelling, punctuation, capitalization, factual claims, or grammar in the author’s prose.

Use visible markers:

```markdown
<!-- BEGIN AUTHOR NOTE -->
...
<!-- END AUTHOR NOTE -->

<!-- BEGIN CHAPTER TEXT -->
...
<!-- END CHAPTER TEXT -->
```

---

## Validation requirements

A work is complete only when all checks pass.

### Structural validation

- Number of captured chapter URLs equals the displayed available chapter count.
- Chapter indices are consecutive and unique.
- Every chapter has a non-empty title or an explicitly recorded missing title.
- Every chapter has non-empty story text.
- No chapter URL was captured twice.
- The merged PDF contains the same number of chapter bookmarks as captured chapters.

### Content validation

- Extract text from each generated chapter PDF.
- Confirm that the first and last substantial paragraph from normalized chapter text appear in the PDF text.
- Compare normalized HTML text length with PDF-extracted text length; investigate large differences.
- Search for failure signatures such as:
  - “Checking your browser”;
  - “Access denied”;
  - “CAPTCHA”;
  - “Page not found”;
  - empty story container.
- Confirm that navigation, reviews, and unrelated recommendations were not included.

### Integrity validation

- Generate SHA-256 hashes for raw HTML, normalized text, chapter PDF, and final merged PDF.
- Record retrieval timestamp and tool version.
- Make reruns idempotent.
- If a source changes later, preserve the older capture and create a new version instead of overwriting it.

### Manual spot checks

At minimum, manually inspect:

- first chapter of every work;
- final chapter of every work;
- the longest chapter of every work;
- all pages around chapter transitions in the merged PDF;
- any chapter containing a missing-chapter or author-note warning.

---

## Dataset use for project chapter checks

Create a separate chapter-comparison index after acquisition.

Suggested file:

```text
data/fanfic-hogwarts-history/chapter-comparison-index.jsonl
```

Each record should map a fanfic chapter or section to topics relevant to the main project:

```json
{
  "source_id": "HAH-FAN-001",
  "chapter_index": 6,
  "chapter_title": "Chapter Five: Exploring Hogwarts and its Grounds",
  "topic_tags": [
    "architecture",
    "castle-layout",
    "great-hall",
    "enchanted-ceiling",
    "common-rooms",
    "library",
    "secret-passages"
  ],
  "use_for": [
    "style comparison",
    "coverage-gap discovery",
    "fan-invention detection"
  ],
  "must_not_use_for": [
    "canon confirmation",
    "historical proof"
  ]
}
```

When checking a project chapter:

1. Identify its topic tags.
2. Retrieve matching fanfic chapters from the index.
3. Compare:
   - chapter organization;
   - narrative voice;
   - level of detail;
   - historical framing;
   - use of anecdotes;
   - use of invented names and dates;
   - claims absent from canonical sources.
4. Produce a comparison report with three sections:
   - `Useful stylistic ideas`;
   - `Possible coverage gaps`;
   - `Fan-created claims that must not enter the seed without canon support`.
5. Never promote a repeated fanfic claim to canon merely because multiple fanfics contain it.

---

## Implementation modules

Suggested Python modules:

```text
scripts/fanfic_dataset/
  discover.py
  fetch_fanfiction_net.py
  clean_html.py
  html_to_markdown.py
  render_pdf.py
  merge_pdf.py
  validate.py
  build_manifest.py
  build_comparison_index.py
  cli.py
```

Suggested dependencies:

- Python 3.12+
- Playwright
- BeautifulSoup4 or selectolax
- html2text or markdownify
- pypdf or PyMuPDF
- Pydantic
- tenacity, used only for limited transient retries

Do not introduce Selenium if Playwright is already available.

---

## CLI design

Examples:

```bash
python -m scripts.fanfic_dataset.cli acquire --source HAH-FAN-001
python -m scripts.fanfic_dataset.cli acquire --all
python -m scripts.fanfic_dataset.cli validate --all
python -m scripts.fanfic_dataset.cli build-index
python -m scripts.fanfic_dataset.cli report
```

Useful flags:

```text
--resume
--force-new-version
--headed
--dry-run
--output-root <path>
--request-delay-seconds 3
```

`--dry-run` must discover metadata and chapter URLs without saving story text or PDFs.

---

## Execution phases

### Phase 1 — Scaffold and source registry

- Create directories and schemas.
- Add the four confirmed sources to a static registry.
- Add the title-collision exclusion.
- Implement dry-run discovery.

**Exit criterion:** Dry run reports the expected available chapter counts of 6, 3, 6, and 1 without downloading chapter bodies.

### Phase 2 — Single-source proof of concept

Use `HAH-FAN-004` because it has one short page.

- Capture raw HTML.
- Produce clean HTML and Markdown.
- Render one PDF.
- Run all validations.

**Exit criterion:** The final PDF and manifest are correct and contain no site chrome.

### Phase 3 — Multi-chapter acquisition

Use `HAH-FAN-001`.

- Discover all six available chapters.
- Capture sequentially.
- Generate chapter PDFs.
- Merge to one final PDF.
- Record the missing promised Chapter Four note.

**Exit criterion:** Six chapter artifacts and one validated merged PDF exist.

### Phase 4 — Remaining sources

Acquire `HAH-FAN-002` and `HAH-FAN-003` using the same pipeline.

**Exit criterion:** All four valid works pass structural, content, and integrity validation.

### Phase 5 — Comparison index

- Tag chapters by topic and narrative style.
- Generate `chapter-comparison-index.jsonl`.
- Produce a human-readable summary report.

**Exit criterion:** A project chapter can be matched to relevant fanfic sections without searching all PDFs manually.

---

## Acceptance criteria

The task is complete when:

- [ ] Four work-level PDFs exist, one for each confirmed valid source.
- [ ] Every currently available chapter is represented exactly once.
- [ ] Raw HTML, clean HTML, normalized Markdown, and chapter PDFs are retained.
- [ ] All outputs have SHA-256 hashes.
- [ ] The manifest identifies every artifact and original URL.
- [ ] Validation proves that no error page, review section, or navigation UI was captured as story text.
- [ ] Missing or promised-but-unavailable chapters are explicitly recorded.
- [ ] Fan-created material is visibly labeled non-canon.
- [ ] The excluded Hermione AU is recorded as a title collision but not added to the core dataset.
- [ ] The comparison index supports topic-based retrieval for future project chapters.
- [ ] No access controls, CAPTCHAs, paywalls, or technical restrictions were bypassed.

---

## Final Codex report format

After execution, Codex should return:

```markdown
# Fanfic Dataset Acquisition Report

## Completed sources
- HAH-FAN-001: <chapter count>, <PDF path>, <validation status>
- HAH-FAN-002: ...
- HAH-FAN-003: ...
- HAH-FAN-004: ...

## Excluded sources
- <source>: <reason>

## Validation summary
- Expected chapters:
- Captured chapters:
- PDFs generated:
- Failed checks:

## Files created or updated
- <paths>

## Open issues
- <missing chapters, source changes, blocked pages, or extraction uncertainty>
```

Do not claim completion unless the validation commands were actually run and their output was reviewed.
