# Codex Skill Instructions: Hogwarts: A History Seed Builder

## Purpose

Create the first structured, evidence-backed seed for a fan edition of **Hogwarts: A History**.

This skill is not meant to write the final book yet.
It is meant to read one bounded source unit at a time, extract canon-supported evidence, and use that evidence to grow a tentative structure for the future book.

The output should help answer:

- What topics should this book contain?
- What chapters or sections are emerging?
- Which facts are explicitly said to come from *Hogwarts: A History*?
- Which facts are only useful as supporting material?
- Which facts belong in the original pre-1984 book body, and which belong only as later editorial notes?
- Where exactly does every claim come from?

---

## Known Source Files

The current local PDF source files are expected to be:

```text
pdfs/
  Beedle The Bard_text.pdf
  Fantastic-Beasts-Where-to-Find-Them.pdf
  harrypotter.pdf
  quidditch-through-the-ages.pdf
```

Important notes:

- `harrypotter.pdf` is a complete-collection PDF containing all seven Harry Potter novels.
- The companion PDFs may have imperfect OCR or formatting.
- Always record the exact filename used.
- Never assume page numbers are stable across different PDF editions.

---

## Optional Future Sources To Consider

These are not currently local PDFs unless later added by the user. Do not process them unless files or explicit instructions are provided.

Potentially relevant additional Rowling/Wizarding World sources:

```text
Hogwarts: An Incomplete and Unreliable Guide
Short Stories from Hogwarts of Power, Politics and Pesky Poltergeists
Short Stories from Hogwarts of Heroism, Hardship and Dangerous Hobbies
From the Wizarding Archive: Volumes 1 and 2
Harry Potter prequel short story
Harry Potter and the Cursed Child
Wizarding World / HarryPotter.com writing by J.K. Rowling
```

Priority note:

- *Hogwarts: An Incomplete and Unreliable Guide* is especially relevant because it overlaps directly with Hogwarts institutions, secrets, locations, the Sorting Hat, ghosts, portraits, school subjects, the Hogwarts Express, the Great Lake, the Chamber of Secrets, and other structural topics.
- Treat later publications as external canon-support material, not as proof that the fictional in-universe *Hogwarts: A History* contained the same wording.

Future research task:

- Search for existing fanfiction or fan-made versions of *Hogwarts: A History*.
- Extract style observations and structural inspiration only.
- Do not copy prose.
- Keep a separate file for influence/style notes.

---

## Core Principle

This is an evidence-first indexing and structure-discovery skill.

Do not invent facts.
Do not write final prose as if it is canon.
Do not treat plausible inference as fact.
Do not include unsupported claims without a confidence note.
Do not copy long passages from source texts.

Each output item must be traceable to a source location.

---

## Historical Boundary Rule

Assume the original in-universe *Hogwarts: A History* was written before Harry Potter attended Hogwarts.

Working assumption:

```text
Original core book cutoff: before Harry's Hogwarts years
Approximate external planning cutoff: up to 1984, unless revised later
```

Implications:

- Ancient, medieval, early modern, nineteenth-century, and pre-Harry Hogwarts material may belong in the original book body.
- Harry-era events usually do not belong in the original book body.
- Harry-era scenes may still be evidence about older Hogwarts features.
- Harry-era events can be classified as later editorial notes, confirmations, or source context.

Example:

- The Great Hall ceiling enchantment predates Harry and can belong in the main book.
- Harry seeing it in 1991 is source context, not core book content.

---

## Input Per Run

Process exactly one bounded source unit.

A source unit is usually:

- one chapter from one of the seven novels,
- one chapter from a companion book,
- one article or essay from a web source,
- or one clearly bounded section of a source.

Expected task input:

```yaml
source_file: pdfs/harrypotter.pdf
book: Harry Potter and the Philosopher's Stone
chapter_or_section_title: Chapter Seven - The Sorting Hat
known_target_terms:
  - Hogwarts: A History
  - bewitched ceiling
  - Great Hall
```

---

## Required Process

### Step 1: Locate the Source Unit

1. Find the requested chapter or section title.
2. Find the next chapter or section title.
3. Treat the range between them as the processing boundary.
4. Search only inside that range.
5. For large collection PDFs, use the Chapter Boundary Performance Rule below before scanning.
6. Record:
   - `chapter_start_pdf_page`
   - `chapter_end_pdf_page`
   - `boundary_confidence`
   - `boundary_notes`

If the boundary cannot be found confidently, stop and report the limitation.

Do not process the whole PDF when only one chapter was requested.

---

## Chapter Boundary Performance Rule

For large collection PDFs such as `harrypotter.pdf`, do not scan the full PDF from page 1 for every chapter.

Use the cheapest available boundary method in this order:

1. Check existing source YAML files for nearby chapter boundaries.
2. Check `appendix/source-index.md` for known chapter/page anchors.
3. If a previous chapter has already been processed, begin scanning from that previous chapter's end page or the next nearby page, not from page 1.
4. If the requested chapter has a known approximate page from prior runs, begin scanning from a small page window around that page.
5. Only scan the full PDF if no prior anchors exist.

When scanning for a chapter title in a large collection PDF:

- Do not extract every page unless absolutely necessary.
- Prefer bounded page-window scans.
- Once the requested chapter start and the next chapter start are found, extract only that chapter range.
- Record the boundary method used in `boundary_notes`.

Example:

If Chapter Eight ended at PDF page 132 and the next task is Chapter Nine, start searching around page 132 or immediately after it. Do not restart from PDF page 1.

Good boundary note example:

```yaml
boundary_notes: Chapter Nine was located by scanning forward from the previously processed Chapter Eight boundary. Chapter Nine starts on PDF page 133; Chapter Ten starts on PDF page 150. Only pages 133-149 were extracted.
```

Bad boundary behavior:

```text
Looping over every page of the full collection PDF from page 1 for each new chapter.
```

This is allowed only if there are no prior anchors or source index entries.

---

### Step 2: Search For Explicit References

Search inside the source unit for direct references to:

- `Hogwarts: A History`
- phrases like “I read it in...”
- Hermione mentioning books or things she has read
- book/library/classroom/source mentions
- historical explanations given by characters
- institutional details about Hogwarts
- school traditions
- castle architecture
- magical protections
- founders
- ghosts
- portraits
- houses
- curriculum
- Quidditch at Hogwarts
- the library
- the grounds
- the lake
- school rules
- ceremonies
- old events that predate Harry

Explicit *Hogwarts: A History* references are the highest priority.

---

### Step 3: Extract Candidate Evidence Entries

Create an evidence entry when the source contains a detail that could plausibly help build *Hogwarts: A History*.

Include entries if they are one or more of the following:

1. Explicitly attributed to *Hogwarts: A History*
2. Explicitly attributed to a book, class, teacher, ghost, portrait, or school tradition
3. A concrete Hogwarts setting detail
4. A concrete historical or institutional detail about Hogwarts
5. A recurring practice, rule, custom, or magical system at Hogwarts
6. A detail that may support a future chapter of *Hogwarts: A History*

Exclude:

- general plot events with no institutional value
- character drama that does not reveal Hogwarts history or structure
- unsupported inference
- long copied passages
- film-only details unless explicitly requested later

Extraction volume rule:

- Always extract every explicit *Hogwarts: A History* reference in the source unit.
- For non-explicit supporting material, extract only the strongest 3-7 candidates per source unit unless the user asks for exhaustive extraction.
- Strong supporting candidates include school rules, ceremonies, House system details, castle architecture, magical protections, ghosts and portraits, curriculum, library/book references, old events predating Harry, and details likely to form a future chapter or section.
- Avoid weak supporting candidates that are only plot movement or atmosphere.

---

## Controlled Reference Types

Use only these values for `reference_type`:

```yaml
reference_type_values:
  - explicit_hogwarts_a_history
  - explicit_in_universe_source
  - direct_observed_setting
  - institutional_custom
  - historical_claim
  - magical_architecture
  - school_rule_or_policy
  - curriculum_or_subject
  - house_system
  - portrait_or_ghost_lore
  - security_or_protection
  - cross_reference_candidate
  - weak_context_only
```

---

## Controlled Era Classification

Use only these values for `era_classification`:

```yaml
era_classification_values:
  - original_book_core_candidate
  - pre_1984_historical_candidate
  - harry_era_confirmation
  - later_editorial_note
  - post_1984_excluded_from_original
  - unknown_or_uncertain
```

Guidance:

- Use `original_book_core_candidate` when the fact likely predates Harry and could plausibly be in the in-universe book.
- Use `harry_era_confirmation` when a Harry-era scene confirms an older feature.
- Use `later_editorial_note` when the fact is useful for the fan edition but likely not part of the original Bathilda-era text.
- Use `post_1984_excluded_from_original` when the event clearly happened too late for the original in-universe book.

---

## Candidate Book Structure

Every evidence entry must suggest where it may belong in the future fan edition.

Record:

- `candidate_part`
- `candidate_chapter`
- `candidate_section`
- `reason_for_placement`

Initial tentative structure:

```yaml
candidate_parts:
  - Origins of the School
  - The Castle and Its Grounds
  - Magical Architecture and Enchantments
  - The Four Houses
  - Ceremonies and School Traditions
  - Academic Life and Curriculum
  - Rules, Discipline, and Governance
  - Ghosts, Portraits, and Magical Residents
  - Protective Magic and Security
  - Quidditch and School Recreation
  - The Library, Books, and Scholarship
  - Notable Events Before 1984
  - Later Editorial Notes
  - Appendix: Explicit References to Hogwarts: A History
```

The structure may evolve, but every new proposed part/chapter must explain why it is needed.

---

## Quote Policy

This project is an index and research seed, not a source-text dump.

For each entry:

- Use short identifying excerpts only.
- Keep quote excerpts under 25 total words per entry.
- Always wrap `quote_excerpt_short` in YAML string quotes.
- Prefer paraphrase in `source_note`.
- Never copy long passages.
- Never reproduce full paragraphs.

Example:

```yaml
quote_excerpt_short: "bewitched to look like the sky outside"
```

---

## Text Anchors

PDF page numbers are useful for local work, but they may change across editions, extraction tools, or regenerated PDFs.

Every evidence entry must include a `text_anchor` block in addition to PDF page numbers.

Required format:

```yaml
text_anchor:
  start_phrase:
  end_phrase:
  local_occurrence_note:
```

Guidance:

- `start_phrase` should be a short phrase near the beginning of the relevant passage.
- `end_phrase` should be a short phrase near the end of the relevant passage.
- `local_occurrence_note` should explain how to relocate the passage if the same phrase appears more than once.
- Keep anchor phrases short. They are relocation markers, not quote dumps.

Example:

```yaml
text_anchor:
  start_phrase: "Harry had never even imagined such a strange and splendid place."
  end_phrase: "I read about it in Hogwarts: A History."
  local_occurrence_note: Great Hall ceiling passage, first-year arrival before the Sorting.
```

---

## Confidence

Use one of:

```yaml
confidence_values:
  - high
  - medium
  - low
```

Guidance:

- `high`: the source directly supports the entry.
- `medium`: the fact is clear, but its placement in the future book is interpretive.
- `low`: the entry is only a weak candidate or needs later confirmation.

Every `low` confidence entry must include a limitation note.

---

## Output Structure

Recommended repo structure:

```text
pdfs/
  Beedle The Bard_text.pdf
  Fantastic-Beasts-Where-to-Find-Them.pdf
  harrypotter.pdf
  quidditch-through-the-ages.pdf

sources/
  book-01/
    chapter-07-sorting-hat.yaml

appendix/
  book-structure-seed.md
  explicit-hogwarts-a-history-references.md
  source-index.md
  open-questions.md

docs/
  instructions/
    hogwarts-history-seed-builder.md
```

This file should usually live at:

```text
docs/instructions/hogwarts-history-seed-builder.md
```

---

## YAML Output Schema

Each processed source unit must produce one YAML file.

Example path:

```text
sources/book-01/chapter-07-sorting-hat.yaml
```

Required schema:

```yaml
source_unit:
  source_file:
  book:
  chapter:
  chapter_start_pdf_page:
  chapter_end_pdf_page:
  boundary_confidence:
  boundary_notes:
  processed_date:
  processor_notes:

entries:
  - id:
    source_file:
    book:
    chapter:
    chapter_start_pdf_page:
    chapter_end_pdf_page:
    pdf_page:
    printed_page:
    extracted_text_lines:
    text_anchor:
      start_phrase:
      end_phrase:
      local_occurrence_note:
    nearby_context:
    match_terms:
    quote_excerpt_short:
    source_note:
    reference_type:
    era_classification:
    topic_tags:
    candidate_part:
    candidate_chapter:
    candidate_section:
    reason_for_placement:
    relevance_to_hogwarts_a_history:
    duplicate_check:
      possible_duplicate:
      duplicate_of:
      notes:
    confidence:
    limitations:
```

---

## Required Field Guidance

### `text_anchor`

A relocation aid for future searches and cross-edition checking.

Example:

```yaml
text_anchor:
  start_phrase: "Harry had never even imagined such a strange and splendid place."
  end_phrase: "I read about it in Hogwarts: A History."
  local_occurrence_note: Great Hall ceiling passage, first-year arrival before the Sorting.
```

### `quote_excerpt_short`

A short identifying quote only. Always wrap this value in YAML string quotes.

Example:

```yaml
quote_excerpt_short: "bewitched to look like the sky outside"
```

### `source_note`

A paraphrased description of what the source says.

Example:

```yaml
source_note: Hermione explains that the Great Hall ceiling is enchanted to resemble the outside sky and says she read this in Hogwarts: A History.
```

### `relevance_to_hogwarts_a_history`

Explain why this entry belongs in the project.

Example:

```yaml
relevance_to_hogwarts_a_history: This is an explicit in-universe reference to information Hermione says comes from Hogwarts: A History, making it a direct candidate for the fan edition.
```

### `candidate_part`, `candidate_chapter`, `candidate_section`

These are not final. They are seed-structure suggestions.

Example:

```yaml
candidate_part: Magical Architecture and Enchantments
candidate_chapter: The Great Hall
candidate_section: The Enchanted Ceiling
```

---

## Example Entry

```yaml
source_unit:
  source_file: pdfs/harrypotter.pdf
  book: Harry Potter and the Philosopher's Stone
  chapter: Chapter Seven - The Sorting Hat
  chapter_start_pdf_page: 107
  chapter_end_pdf_page: 116
  boundary_confidence: high
  boundary_notes: Chapter boundary identified from Chapter Seven title to Chapter Eight title.
  processed_date: 2026-06-09
  processor_notes: Processed only Chapter Seven.

entries:
  - id: ps-ch07-001
    source_file: pdfs/harrypotter.pdf
    book: Harry Potter and the Philosopher's Stone
    chapter: Chapter Seven - The Sorting Hat
    chapter_start_pdf_page: 107
    chapter_end_pdf_page: 116
    pdf_page: 110
    printed_page: not available
    extracted_text_lines: "11-14"
    text_anchor:
      start_phrase: "Harry had never even imagined such a strange and splendid place."
      end_phrase: "I read about it in Hogwarts: A History."
      local_occurrence_note: Great Hall ceiling passage, first-year arrival before the Sorting.
    nearby_context: First-years enter the Great Hall before the Sorting ceremony; Harry notices the ceiling and Hermione explains its enchantment.
    match_terms:
      - Hogwarts: A History
      - bewitched
      - sky outside
      - Great Hall
    quote_excerpt_short: "bewitched to look like the sky outside"
    source_note: Hermione explains that the Great Hall ceiling is enchanted to resemble the outside sky and says she read this in Hogwarts: A History.
    reference_type: explicit_hogwarts_a_history
    era_classification: original_book_core_candidate
    topic_tags:
      - great-hall
      - enchanted-ceiling
      - magical-architecture
      - hermione-source
      - explicit-reference
    candidate_part: Magical Architecture and Enchantments
    candidate_chapter: The Great Hall
    candidate_section: The Enchanted Ceiling
    reason_for_placement: The fact describes a permanent magical feature of the castle and is explicitly attributed to Hogwarts: A History.
    relevance_to_hogwarts_a_history: This is a direct in-universe confirmation that the ceiling enchantment is covered by Hogwarts: A History.
    duplicate_check:
      possible_duplicate: false
      duplicate_of: null
      notes: No duplicate found in the current seed.
    confidence: high
    limitations: Only this chapter was checked in this run; later books may contain additional Great Hall ceiling references.
```

---

## Markdown Seed Summary

After processing the source unit, update:

```text
appendix/book-structure-seed.md
```

The summary should contain:

```markdown
# Hogwarts: A History — Book Structure Seed

## Emerging Parts

### Magical Architecture and Enchantments

Possible chapters:
- The Great Hall
  - The Enchanted Ceiling
  - Ceremonial Use of the Hall

Evidence:
- PS, Chapter Seven, page 110: Hermione says the Great Hall ceiling is bewitched to look like the sky outside and that she read this in Hogwarts: A History.

Confidence:
- Strong explicit support for the enchanted ceiling.
- Chapter placement is tentative but likely.

## Explicit Hogwarts: A History References

- PS, Chapter Seven — The Sorting Hat — Great Hall ceiling enchantment.

## Open Questions

- Does the ceiling enchantment appear elsewhere?
- Is the Great Hall described in other books with additional magical architecture?
- Are there later references to other features Hermione says she read about?
```

---

## Duplicate Handling

Before adding a new entry, compare against previous YAML files if available.

A duplicate means the same fact appears again.

If duplicate:

```yaml
duplicate_check:
  possible_duplicate: true
  duplicate_of: ps-ch07-001
  notes: Same Great Hall ceiling enchantment appears again, but this occurrence may provide different context.
```

Do not delete duplicates automatically. Repeated references may show importance.

---

## First Recommended Run

Use the already validated target:

```yaml
source_file: pdfs/harrypotter.pdf
book: Harry Potter and the Philosopher's Stone
chapter_or_section_title: Chapter Seven - The Sorting Hat
known_target_terms:
  - Hogwarts: A History
  - Great Hall
  - bewitched
  - ceiling
  - Sorting Hat
```

Expected output should include at least:

```yaml
candidate_part: Magical Architecture and Enchantments
candidate_chapter: The Great Hall
candidate_section: The Enchanted Ceiling
reference_type: explicit_hogwarts_a_history
era_classification: original_book_core_candidate
confidence: high
```

It may also include a weaker seed for:

```yaml
candidate_part: Ceremonies and School Traditions
candidate_chapter: The Sorting Ceremony
candidate_section: Arrival of First-Year Students
reference_type: institutional_custom
era_classification: harry_era_confirmation
confidence: medium
```

Do not over-extract from this first run. The point is to validate the schema.

---

## Second Recommended Run

After the first run has been reviewed, process Book 1, Chapter Eight to test academic-life and curriculum extraction.

Recommended task:

```yaml
source_file: pdfs/harrypotter.pdf
book: Harry Potter and the Philosopher's Stone
chapter_or_section_title: Chapter Eight - The Potions Master
known_target_terms:
  - Hogwarts: A History
  - Potions
  - Snape
  - ghosts
  - Peeves
  - classes
  - History of Magic
  - Defence Against the Dark Arts
  - Transfiguration
  - Charms
  - Herbology
  - House points
  - Slytherin
  - Gryffindor
```

Expected output path:

```text
sources/book-01/chapter-08-potions-master.yaml
```

For this run:

- Process only Chapter Eight.
- Locate Chapter Eight and the next chapter title, Chapter Nine.
- Check previous YAML files for duplicate candidates.
- Extract all explicit *Hogwarts: A History* references if any appear.
- Limit non-explicit supporting material to the strongest 3-7 candidates.

---

## Third Recommended Run

After Chapter Eight has been reviewed, process Book 1, Chapter Nine to test rules, discipline, restricted areas, flying lessons, and security extraction.

Recommended task:

```yaml
source_file: pdfs/harrypotter.pdf
book: Harry Potter and the Philosopher's Stone
chapter_or_section_title: Chapter Nine - The Midnight Duel
known_target_terms:
  - Hogwarts: A History
  - Midnight Duel
  - flying lessons
  - broomsticks
  - Madam Hooch
  - House points
  - detention
  - trophy room
  - forbidden corridor
  - third-floor corridor
  - Fluffy
  - trapdoor
  - Filch
  - Mrs. Norris
  - curfew
  - rules
  - restricted areas
  - magical security
```

Expected output path:

```text
sources/book-01/chapter-09-midnight-duel.yaml
```

For this run:

- Process only Chapter Nine.
- Locate Chapter Nine and the next chapter title, Chapter Ten.
- Use prior chapter/page anchors before scanning the PDF.
- Do not scan the full collection PDF from page 1 unless no prior anchors exist.
- Check previous YAML files for duplicate candidates.
- Extract all explicit *Hogwarts: A History* references if any appear.
- Limit non-explicit supporting material to the strongest 3-7 candidates.
- Treat 1991-1992-specific restrictions cautiously as later editorial notes unless they clearly indicate a standing institutional practice.

---

## Fourth Recommended Run

After Chapter Nine has been reviewed, process Book 1, Chapter Ten to test classroom instruction, feasts, emergencies, and student-safety extraction.

Recommended task:

```yaml
source_file: pdfs/harrypotter.pdf
book: Harry Potter and the Philosopher's Stone
chapter_or_section_title: Chapter Ten - Halloween
known_target_terms:
  - Hogwarts: A History
  - Halloween
  - Charms
  - Wingardium Leviosa
  - Flitwick
  - troll
  - dungeon
  - feast
  - Great Hall
  - House points
  - Gryffindor
  - teachers
  - Quirrell
  - Snape
  - rules
  - students
```

Expected output path:

```text
sources/book-01/chapter-10-halloween.yaml
```

For this run:

- Process only Chapter Ten.
- Locate Chapter Ten and the next chapter title, Chapter Eleven.
- Use prior chapter/page anchors before scanning the PDF.
- Do not scan the full collection PDF from page 1 unless no prior anchors exist.
- Check previous YAML files for duplicate candidates.
- Extract all explicit *Hogwarts: A History* references if any appear.
- Limit non-explicit supporting material to the strongest 3-7 candidates.

---

## Report Format Per Run

At the end of each run, report:

```markdown
## Run Summary

Source unit processed:
Entries created:
Explicit Hogwarts: A History references:
Tentative structure seeds added:
Duplicate candidates:
Open questions:
Confidence summary:
Files created or updated:
Limitations:
```

---

## What Not To Do

Do not write final chapters yet.

Do not create smooth encyclopedia prose as if it is canon.

Do not infer dates unless the source gives them.

Do not include post-1984 events as if they appeared in the original *Hogwarts: A History*.

Do not treat Harry-era plot events as original book content.

Do not treat film-only details as book canon.

Do not copy fanfiction prose.

Do not overwrite previous source files without preserving earlier entries.

Do not silently change the schema. If a schema change seems necessary, propose it first in a notes section.

---

## How To Use This Skill In Codex

1. Create a repo or folder for the project.
2. Put the PDFs in the `pdfs/` folder using the exact filenames listed above.
3. Put this Markdown file at:

```text
docs/instructions/hogwarts-history-seed-builder.md
```

4. Give Codex a task like:

```text
Read docs/instructions/hogwarts-history-seed-builder.md.

Run the first recommended source-unit extraction:
- source_file: pdfs/harrypotter.pdf
- book: Harry Potter and the Philosopher's Stone
- chapter_or_section_title: Chapter Seven - The Sorting Hat

Create the YAML source file and update the Markdown seed summary.
Use prior chapter/page anchors before scanning large collection PDFs.
Do not process other chapters.
Do not write final prose.
```

5. Review the generated YAML before processing the next chapter.

## Automated Iteration Mode

The project should support repeated automated runs without requiring a custom prompt for each chapter.

When the user asks to “run the next pending source-unit extraction,” the agent must use the project-control files to determine the next task.

Required control files:

```text
project-control/
  source-plan.yaml
  processing-state.yaml
  next-run.md
```

If these files do not exist yet, the agent should create them before processing the next source unit.

---

### `source-plan.yaml`

This file contains the ordered list of source units to process.

Each source unit should include:

```yaml
source_file:
book_group:
book:
chapter_number:
chapter_title:
status:
output_file:
```

Allowed `status` values:

```yaml
status_values:
  - pending
  - in_progress
  - complete
  - skipped
  - needs_review
  - failed
```

For the current phase, initialize Book 1 using the already completed chapters and continue from Chapter Eleven:

```yaml
project:
  name: Hogwarts: A History Seed Builder

current_phase: automated-book-01

sources:
  - source_file: pdfs/harrypotter.pdf
    book_group: book-01
    book: Harry Potter and the Philosopher's Stone
    chapters:
      - number: 1
        title: Chapter One - The Boy Who Lived
        status: pending
        output_file: sources/book-01/chapter-01-boy-who-lived.yaml
      - number: 2
        title: Chapter Two - The Vanishing Glass
        status: pending
        output_file: sources/book-01/chapter-02-vanishing-glass.yaml
      - number: 3
        title: Chapter Three - The Letters from No One
        status: pending
        output_file: sources/book-01/chapter-03-letters-from-no-one.yaml
      - number: 4
        title: Chapter Four - The Keeper of the Keys
        status: pending
        output_file: sources/book-01/chapter-04-keeper-of-the-keys.yaml
      - number: 5
        title: Chapter Five - Diagon Alley
        status: pending
        output_file: sources/book-01/chapter-05-diagon-alley.yaml
      - number: 6
        title: Chapter Six - The Journey from Platform Nine and Three-quarters
        status: pending
        output_file: sources/book-01/chapter-06-journey-from-platform-nine-and-three-quarters.yaml
      - number: 7
        title: Chapter Seven - The Sorting Hat
        status: complete
        output_file: sources/book-01/chapter-07-sorting-hat.yaml
      - number: 8
        title: Chapter Eight - The Potions Master
        status: complete
        output_file: sources/book-01/chapter-08-potions-master.yaml
      - number: 9
        title: Chapter Nine - The Midnight Duel
        status: complete
        output_file: sources/book-01/chapter-09-midnight-duel.yaml
      - number: 10
        title: Chapter Ten - Halloween
        status: complete
        output_file: sources/book-01/chapter-10-halloween.yaml
      - number: 11
        title: Chapter Eleven - Quidditch
        status: pending
        output_file: sources/book-01/chapter-11-quidditch.yaml
      - number: 12
        title: Chapter Twelve - The Mirror of Erised
        status: pending
        output_file: sources/book-01/chapter-12-mirror-of-erised.yaml
      - number: 13
        title: Chapter Thirteen - Nicolas Flamel
        status: pending
        output_file: sources/book-01/chapter-13-nicolas-flamel.yaml
      - number: 14
        title: Chapter Fourteen - Norbert the Norwegian Ridgeback
        status: pending
        output_file: sources/book-01/chapter-14-norbert-the-norwegian-ridgeback.yaml
      - number: 15
        title: Chapter Fifteen - The Forbidden Forest
        status: pending
        output_file: sources/book-01/chapter-15-forbidden-forest.yaml
      - number: 16
        title: Chapter Sixteen - Through the Trapdoor
        status: pending
        output_file: sources/book-01/chapter-16-through-the-trapdoor.yaml
      - number: 17
        title: Chapter Seventeen - The Man with Two Faces
        status: pending
        output_file: sources/book-01/chapter-17-man-with-two-faces.yaml
```

Backfill note:

- Chapters 1-6 are marked pending because they have not yet been processed in this workflow.
- The next automated run should continue with Chapter Eleven unless the user explicitly asks to backfill earlier chapters first.
- After Book 1 is complete, the source plan can be extended to Books 2-7 and companion sources.

---

### `processing-state.yaml`

This file records the last completed source unit and the next pending unit.

Recommended initial state after completing Chapter Ten:

```yaml
last_completed:
  source_file: pdfs/harrypotter.pdf
  book_group: book-01
  chapter_number: 10
  chapter_title: Chapter Ten - Halloween
  output_file: sources/book-01/chapter-10-halloween.yaml
  chapter_start_pdf_page: 150
  chapter_end_pdf_page: 163
  next_chapter_start_pdf_page: 164

next_pending:
  source_file: pdfs/harrypotter.pdf
  book_group: book-01
  book: Harry Potter and the Philosopher's Stone
  chapter_number: 11
  chapter_title: Chapter Eleven - Quidditch
  output_file: sources/book-01/chapter-11-quidditch.yaml

automation_rules:
  process_one_unit_per_run: true
  never_scan_full_pdf_if_anchor_exists: true
  update_next_run_file: true
  stop_on_schema_error: true
```

The agent must update this file after every successful run.

After every successful run, `next_pending` must point to the next chapter in the ordered source plan. If the completed source unit is the last listed chapter of a book but the same source file continues into another book, extend `source-plan.yaml` with the next book's next chapter and set `next_pending` to that chapter. Only set `next_pending: null` when the full planned source sequence is intentionally exhausted and no next chapter should be processed.

---

### `next-run.md`

This file is a human-readable summary of the next task. It replaces one-off prompts.

Recommended initial file after completing Chapter Ten:

```markdown
# Next Run

Process the next pending source unit from:

- `project-control/source-plan.yaml`
- `project-control/processing-state.yaml`

Current next unit:

- source_file: `pdfs/harrypotter.pdf`
- book: `Harry Potter and the Philosopher's Stone`
- chapter: `Chapter Eleven - Quidditch`
- output_file: `sources/book-01/chapter-11-quidditch.yaml`

Use prior chapter/page anchors. Do not scan the full PDF from page 1.

After processing:

1. Create or update the chapter YAML.
2. Update appendix files.
3. Mark this chapter complete in `source-plan.yaml`.
4. Update `processing-state.yaml`.
5. Rewrite this file with the next pending source unit.
```

The agent must rewrite this file after every successful run.

---

### Automated Run Procedure

For each automated iteration:

1. Read `docs/instructions/hogwarts-history-seed-builder.md`.
2. Read `project-control/source-plan.yaml`.
3. Read `project-control/processing-state.yaml`.
4. Read `project-control/next-run.md`.
5. Identify the next source unit to process:
   - Prefer `processing-state.yaml` `next_pending`.
   - If that is missing or stale, use the first `pending` unit in `source-plan.yaml` after `last_completed`.
   - Do not jump backward to pending backfill chapters unless the user explicitly asks.
6. Mark the selected unit as `in_progress` in `source-plan.yaml`.
7. Locate the chapter boundary using prior anchors and the Chapter Boundary Performance Rule.
8. Extract the bounded page range with the reusable extractor script:

   ```bash
   .venv/bin/python scripts/extract_pages.py \
     --pdf <source-pdf> \
     --start-page <first-page> \
     --end-page <last-page> \
     --output .tmp/<book-and-chapter>.txt \
     --per-page-dir .tmp/<book-and-chapter>-pages
   ```

   Do not write one-off Python extraction snippets for normal PDF source-unit runs. If the script fails, report the failure or fix the reusable script; do not silently replace it with ad hoc extraction code.
9. Process exactly one source unit using the extracted bounded text.
10. Create or update the source YAML file.
11. Update appendix files.
12. Validate YAML output with PyYAML.
13. Mark the source unit as `complete`.
14. Update `processing-state.yaml`, setting `next_pending` to the next chapter in the ordered plan.
15. If the next chapter is not yet listed but the same source file continues, extend `source-plan.yaml` with that next chapter before writing `next_pending`.
16. Rewrite `project-control/next-run.md` with the next pending source unit.
17. Print the standard Run Summary.

---

### Failure Handling

If the run fails:

1. Do not mark the unit as `complete`.
2. Mark the unit as `failed` or `needs_review`.
3. Record the reason in `processing-state.yaml`.
4. Record the issue in `project-control/next-run.md`.
5. Preserve any partial files for review only if they are clearly marked as partial.
6. Stop after reporting the failure.

---

### Automation Safety Rules

- Process only one source unit per run unless explicitly instructed otherwise.
- Do not scan the full collection PDF from page 1 if prior anchors exist.
- Do not overwrite curated files without preserving existing content.
- Do not silently change the schema.
- Do not write final book prose.
- Do not mix fanfiction/style research with canon evidence extraction.
- Do not process companion PDFs until they are present locally and added to `source-plan.yaml`.
- Do not process web sources in automated iteration mode unless the user explicitly enables web-source processing.

---

### Permanent Prompt For Automated Runs

Once the control files exist, the user should only need this prompt:

```text
Read and follow docs/instructions/hogwarts-history-seed-builder.md.

Run the next pending source-unit extraction using:

project-control/source-plan.yaml
project-control/processing-state.yaml
project-control/next-run.md

Process exactly one source unit.
Update the control files at the end so the next run can continue automatically.
```

---


## Optional Tooling

No special plugin is required by these instructions themselves.

PDF text extraction for normal source-unit runs must use the reusable script:

```bash
.venv/bin/python scripts/extract_pages.py \
  --pdf <source-pdf> \
  --start-page <first-page> \
  --end-page <last-page> \
  --output .tmp/<book-and-chapter>.txt \
  --per-page-dir .tmp/<book-and-chapter>-pages
```

The agent may use other local tools for searching, validation, and formatting, including:

```text
python
ripgrep
yaml formatter or linter
markdown formatter
```

If the reusable extractor cannot run because dependencies are missing, the agent should either:

- ask to add one,
- fix the reusable script or its environment,
- or report that the PDF cannot be processed reliably.

Recommended Python packages:

```text
pypdf
PyYAML
```

Do not require heavy OCR unless the PDF text layer is unusable.

---

## Future Skill: Fanfiction and Style Research

This is a separate future task, not part of the source extraction run.

Purpose:

- Search the web for existing fan-made versions of *Hogwarts: A History*.
- Identify common structures, tones, chapter ideas, and gaps.
- Record inspiration only.
- Do not copy text.
- Keep this research separate from canon evidence.

Suggested output file:

```text
appendix/fanfic-style-research.md
```

Suggested fields:

```yaml
source_title:
source_url:
author_or_site:
summary:
structure_observations:
style_observations:
ideas_worth_considering:
things_to_avoid:
copyright_or_ethics_notes:
```
