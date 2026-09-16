# Hogwarts: A History — External Source Acquisition Plan

**Purpose:** Give a Codex agent a concrete, reproducible plan for locating, validating, preserving, and registering external Harry Potter canon / author-commentary sources as project resources.

**Status:** Source acquisition only.  
**Do not draft the book and do not perform the taxonomy/structure refactor during this task.**

**Verified:** 2026-08-15

---

## 1. Goal

Build a durable external-source corpus for the *Hogwarts: A History* project from publicly accessible sources outside the seven main novels.

The corpus should prioritize:

1. J.K. Rowling-authored official material.
2. Primary transcripts of J.K. Rowling interviews, live chats, Q&As, and press conferences.
3. Archived material from J.K. Rowling's former official website.
4. Reliable preservation copies of primary material when the original is no longer available.
5. Secondary indexes only as discovery tools, not as evidence when a primary source can be recovered.

The immediate objective is to **add the sources to the project as resources with strong provenance**, not yet to merge claims into the 1,314-entry evidence seed.

---

## 2. Hard Rules

### 2.1 Preserve provenance

Every saved resource must retain:

- canonical/source title
- author or speaker
- publication/interview date when known
- original publisher/site
- original URL
- retrieval URL if different
- retrieval date
- source class
- whether the saved page is original, mirror, transcript, archive, or secondary summary
- local file path
- content hash if practical
- notes about completeness or missing material

Never save an extracted statement without preserving enough metadata to trace it back to the source.

### 2.2 Primary beats secondary

Use this precedence:

1. **Official J.K. Rowling / HarryPotter.com original writing**
2. **Original publisher/interviewer transcript**
3. **Faithful contemporary transcript/mirror of a primary interview**
4. **Archived J.K. Rowling website material**
5. **Reliable preservation transcription of a lost primary page**
6. **Secondary reference/index**
7. **Fan wiki / forum discussion**

If an Accio Quote, HP Lexicon, Leaky Cauldron, or other index points to a surviving primary source, acquire the primary source and use that as evidence.

### 2.3 Discovery pages are not automatically evidence

Examples:

- Accio Quote thematic pages are excellent indexes.
- HP Lexicon source pages are excellent indexes.
- Fan wikis can expose missing topics.

But a summary on one of those pages must not become a canonical evidence record when the underlying Rowling statement is available.

### 2.4 Do not bypass access controls

Use only publicly accessible pages and archives.

Do not:

- bypass paywalls
- defeat anti-bot systems
- circumvent authentication
- scrape a source that explicitly requires restricted access
- invent missing text

If a source is inaccessible, record it as unresolved and look for a lawful preservation copy.

### 2.5 Do not change the book seed during acquisition

For this run:

- do not rewrite `book-seed/hogwarts-a-history-seed.md`
- do not modify the controlled outline
- do not merge candidate labels
- do not resolve the 1,314-entry taxonomy
- do not remove open questions

This phase produces **resources + manifests + acquisition report only**.

---

## 3. Suggested Project Layout

Use existing project conventions if an equivalent resources tree already exists. Do not create duplicates.

Suggested structure:

```text
resources/
  external/
    official-rowling/
      harrypotter-com/
    interviews/
      accio-quote/
      leaky-cauldron/
      original-publisher/
    jkr-website-archive/
    indexes/
      accio-quote/
      hp-lexicon/
    unresolved/

  manifests/
    external-sources.yaml
    external-source-acquisition-report.md
```

If the repository already has `sources/`, `corpus/`, or another canonical resource directory, adapt this plan to that existing structure.

Do not reorganize unrelated existing resources merely to match this example.

---

## 4. Preferred Saved Formats

For each web resource, preserve at minimum:

1. source metadata / manifest entry
2. readable text snapshot
3. original URL

Preferred local representation:

```text
<slug>.md
```

The Markdown snapshot should contain a metadata header followed by the relevant page text.

If the current project tooling already preserves raw HTML, it is also acceptable to retain:

```text
<slug>.html
<slug>.md
```

Do not rely solely on HTML if the current evidence-extraction scripts cannot read it reliably.

### Recommended header

```yaml
---
title:
author:
source_site:
source_class:
publication_date:
original_url:
retrieval_url:
retrieved_at:
archive_url:
is_primary:
is_official:
completeness:
sha256:
notes:
---
```

Suggested `source_class` values:

```text
official_rowling_original
primary_interview_transcript
primary_live_chat_transcript
primary_press_conference_transcript
archived_official_website
preservation_transcription
secondary_index
secondary_reference
```

---

# 5. Corpus A — Official J.K. Rowling Originals

## 5.1 Root discovery page

Start here and enumerate the available J.K. Rowling Originals:

https://www.harrypotter.com/writing-by-jk-rowling

Treat pages explicitly presented as original writing by J.K. Rowling as **highest-priority external evidence**.

Do not stop after the seed list below. Crawl/discover the complete accessible collection and test every article for relevance to:

- Hogwarts history
- castle architecture
- school governance
- founders
- admission
- transport
- staff
- curriculum
- school customs
- student life
- ghosts
- portraits
- houses
- relics
- magical protections
- grounds
- school records
- historical students
- historical incidents
- pre-1984 institutional history

## 5.2 Verified high-priority seed pages

Acquire these first.

### A01 — Chamber of Secrets

https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets

High value for:

- founders
- Salazar Slytherin
- construction history
- founder disagreements
- Chamber access
- castle plumbing history
- Gaunt family
- historical attempts to locate the Chamber
- headmasters/headmistresses
- Hogwarts historians

### A02 — The Sorting Hat

https://www.harrypotter.com/writing-by-jk-rowling/the-sorting-hat

High value for:

- four founders
- creation of the Sorting Hat
- Sorting criteria
- institutional continuity
- House selection

### A03 — Quill of Acceptance and Book of Admittance

https://www.harrypotter.com/writing-by-jk-rowling/the-quill-of-acceptance-and-the-book-of-admittance

High value for:

- Hogwarts admissions
- identification of magical children
- founder-era institutional machinery
- admissions records
- school administration

### A04 — The Hogwarts Express

https://www.harrypotter.com/writing-by-jk-rowling/the-hogwarts-express

High value for:

- historical student transport
- Statute of Secrecy effects on Hogwarts
- Portkeys
- hospital wing
- Ministry relations
- headmaster security policy
- creation/adoption of the Hogwarts Express
- pure-blood opposition

### A05 — Hogwarts Portraits

https://www.harrypotter.com/writing-by-jk-rowling/hogwarts-portraits

High value for:

- institutional memory
- headmaster/headmistress portraits
- preservation of knowledge across administrations
- portrait mechanics

### A06 — Hogwarts Ghosts

https://www.harrypotter.com/writing-by-jk-rowling/hogwarts-ghosts

High value for:

- House ghosts
- Nearly Headless Nick
- Fat Friar
- Grey Lady
- Bloody Baron
- Moaning Myrtle
- Professor Binns
- historical Hogwarts residents

### A07 — Hufflepuff Common Room

https://www.harrypotter.com/writing-by-jk-rowling/hufflepuff-common-room

High value for:

- castle layout
- common-room access
- security systems
- dormitories
- House traditions
- Helga Hufflepuff
- relationship to kitchens

### A08 — The Sword of Gryffindor

https://www.harrypotter.com/writing-by-jk-rowling/the-sword-of-gryffindor

High value for:

- Godric Gryffindor
- founder relics
- goblin-made artefacts
- Hogwarts institutional symbolism

### A09 — The Great Lake

https://www.harrypotter.com/writing-by-jk-rowling/the-great-lake

High value for:

- Hogwarts grounds
- magical creatures
- ecological role of the estate
- lake inhabitants

### A10 — Remus Lupin

https://www.harrypotter.com/writing-by-jk-rowling/remus-lupin

High value for:

- Dumbledore-era admissions policy
- student welfare
- Whomping Willow
- secret passage accommodation
- 1970s Hogwarts
- staffing history

### A11 — The Marauder's Map

https://www.harrypotter.com/writing-by-jk-rowling/the-marauders-map

High value for:

- castle exploration
- secret passages
- 1970s Hogwarts
- Filch
- student rule-breaking
- school security

### A12 — Professor McGonagall

https://www.harrypotter.com/writing-by-jk-rowling/professor-mcgonagall

High value for:

- faculty history
- McGonagall's education
- Hogwarts employment
- staff life
- headship

### A13 — Professor Kettleburn

https://www.harrypotter.com/writing-by-jk-rowling/professor-kettleburn

High value for:

- Care of Magical Creatures
- historical staffing
- disciplinary/probation history
- Dippet and Dumbledore administrations

### A14 — The Mirror of Erised

https://www.harrypotter.com/writing-by-jk-rowling/the-mirror-of-erised

Potential value for:

- Hogwarts artefacts
- castle storage/history
- Room of Requirement context

### A15 — The Original Forty

https://www.harrypotter.com/writing-by-jk-rowling/the-original-forty

Potential value for:

- Hogwarts student planning
- names and demographics
- authorial development

Mark author-development notes separately from in-universe facts.

---

# 6. Corpus B — J.K. Rowling Interview / Q&A / Chat Transcripts

These are primary spoken/written statements by Rowling preserved as transcripts.

The main discovery tool is:

https://www.accio-quote.org/themes/hogwarts.htm

**Important:** the thematic page is an index. Follow its links to the underlying transcript wherever possible.

Also inspect Accio Quote year indexes and interview indexes for additional Hogwarts-relevant transcripts.

## 6.1 Verified seed transcripts

### B01 — Scholastic.com live chat — 3 February 2000

https://www.accio-quote.org/articles/2000/0200-scholastic-chat.htm

Important Hogwarts material includes:

- Hogwarts floor plan / moving architecture
- visual conception of Hogwarts
- magical student identification
- admissions book/quill
- education
- ghosts
- school structure

The Accio copy identifies the original Scholastic transcript source. If the original Scholastic page is still retrievable, prefer it and retain Accio as a preservation copy.

### B02 — Scholastic live chat — 16 October 2000

Discover and acquire via Accio Quote / HP Lexicon.

Search terms:

```text
site:accio-quote.org Rowling Scholastic October 16 2000 chat
```

Validate date and provenance before saving.

### B03 — AOL Live chat — 19 October 2000

https://www.accio-quote.org/articles/2000/1000-aol-chat.htm

Important Hogwarts material includes:

- no fixed conventional blueprint
- moving staircases/rooms
- Rowling's floor notebook
- houses
- school organization

### B04 — World Book Day live chat — 4 March 2004

https://www.accio-quote.org/articles/2004/0304-wbd.htm

Also look for the original / contemporary publisher copy.

High-value topics include:

- what Muggles see at Hogwarts
- Hogwarts location/concealment
- Muggle-born family contact
- pre-Hogwarts education
- Houses
- Sorting
- school organization
- examinations

### B05 — MuggleNet / The Leaky Cauldron interview — July 2005, Part 1

https://www.accio-quote.org/articles/2005/0705-tlc_mugglenet-anelli-1.htm

### B06 — MuggleNet / The Leaky Cauldron interview — July 2005, Part 2

https://www.accio-quote.org/articles/2005/0705-tlc_mugglenet-anelli-2.htm

### B07 — MuggleNet / The Leaky Cauldron interview — July 2005, Part 3

https://www.accio-quote.org/articles/2005/0705-tlc_mugglenet-anelli-3.htm

Acquire all three parts as one logical interview set.

Potentially useful material includes:

- Houses
- founders
- House symbolism
- Sorting Hat
- Peeves
- student population
- Keeper of the Keys
- institutional organization

Also locate the Leaky Cauldron versions where available and record both URLs.

### B08 — Edinburgh "cub reporter" press conference — July 2005

https://www.accio-quote.org/articles/2005/0705-edinburgh-ITVcubreporters.htm

Acquire and scan for Hogwarts institutional/history material.

### B09 — Bloomsbury post-Deathly Hallows web chat — 30 July 2007

https://www.accio-quote.org/articles/2007/0730-bloomsbury-chat.html

Contemporary Leaky Cauldron preservation copy:

https://www.the-leaky-cauldron.org/2007/07/30/j-k-rowling-web-chat-transcript/

High-value topics may include:

- Hogwarts staff
- Headmaster portraits
- Peeves
- Houses/common rooms
- institutional aftermath
- school roles

Many answers are post-1984. Keep the source anyway; later extraction must distinguish **when Rowling answered** from **the in-universe date of the claim**.

### B10 — PotterCast J.K. Rowling interview — December 2007 / January 2008

Accio preservation:

https://www.accio-quote.org/articles/2007/1217-pottercast-anelli.html

Leaky Cauldron Part 1 transcript:

https://www.the-leaky-cauldron.org/2007/12/23/transcript-of-part-1-of-pottercast-s-jk-rowling-interview/

Discover and acquire all subsequent transcript parts belonging to the same interview.

---

# 7. Corpus C — J.K. Rowling's Former Official Website

Rowling's older official site contained:

- FAQ answers
- "Extra Stuff"
- diary entries
- rumours
- hidden/scrapbook material
- direct answers to fan questions

Some material may not have been republished in the later Pottermore/HarryPotter.com archive.

## 7.1 Discovery indexes

Harry Potter Lexicon — Sources Archive:

https://www.hp-lexicon.org/source/

Guide to Rowling's original website:

https://www.hp-lexicon.org/source/guide-to-rowling-website/

JKR website archive/index:

https://www.hp-lexicon.org/source/other-canon/jkr/

Use these pages to discover titles, dates, and original URLs.

## 7.2 Retrieval strategy

For each relevant old JKR page:

1. identify the original URL
2. try the original URL if it still resolves
3. check HarryPotter.com for a republished Rowling Original
4. if not republished, search the Internet Archive / Wayback Machine
5. if a readable archived original exists, preserve the archived original
6. if no archived original survives, preserve the HP Lexicon transcription with explicit `source_class: preservation_transcription`
7. never silently upgrade a transcription or summary to "official original"

## 7.3 High-priority categories

Search the old website archive for material on:

- Hogwarts
- founders
- houses
- Sorting Hat
- school population
- admissions
- castle
- classrooms
- staff
- headmasters
- prefects
- ghosts
- Peeves
- Hogsmeade
- school subjects
- examinations
- school rules
- common rooms
- Quidditch
- Hogwarts Express
- Ministry relations
- historical students
- magical education

---

# 8. Corpus D — Discovery / Preservation Indexes

These are useful for finding missing primary material.

## D01 — Accio Quote Hogwarts topic index

https://www.accio-quote.org/themes/hogwarts.htm

Use as:

```text
topic index -> cited interview -> transcript -> local resource
```

Do not use as:

```text
topic index -> evidence claim
```

unless the underlying primary source truly cannot be recovered, and then mark the claim as secondary/preservation-only.

## D02 — Harry Potter Lexicon Sources Archive

https://www.hp-lexicon.org/source/

Use to enumerate interviews, chats, websites, and Rowling commentary.

## D03 — HP Lexicon archive of old JKR website

https://www.hp-lexicon.org/source/other-canon/jkr/

Use primarily for locating material that is otherwise difficult to recover.

## D04 — The Leaky Cauldron interview archive

Seed page:

https://www.the-leaky-cauldron.org/2007/09/10/interviews/

Use to find original/contemporary interview copies and missing transcript parts.

## D05 — MuggleNet

Search MuggleNet specifically for original interviews or jointly conducted interviews with Rowling.

Do not ingest modern editorial articles merely because they discuss canon.

---

# 9. Additional Discovery Pass

After all seed sources above are acquired, perform a systematic discovery sweep.

## 9.1 Accio Quote

Enumerate all Rowling interviews/chats that contain one or more of:

```text
Hogwarts
castle
school
founder
Gryffindor
Hufflepuff
Ravenclaw
Slytherin
Sorting Hat
headmaster
headmistress
prefect
teacher
professor
ghost
Peeves
Hogsmeade
Quidditch
OWL
NEWT
curriculum
classroom
dormitory
common room
Great Hall
Forbidden Forest
lake
library
Restricted Section
Ministry
governor
admission
student
train
Hogwarts Express
```

Do not reject a transcript solely because it is mainly about another topic.

## 9.2 HP Lexicon

Use the Sources Archive to identify primary sources absent from Accio Quote.

For every candidate:

- record title
- date
- source/publisher
- original link
- preservation link
- whether full transcript is available

## 9.3 Leaky Cauldron / MuggleNet

Look specifically for:

- publication-day interviews
- press conferences
- live chats
- fan Q&As
- PotterCast interviews
- transcripts reproducing publisher events

## 9.4 Wayback Machine

Use only to recover publicly published pages that have disappeared.

Prioritize:

- JKRowling.com
- Bloomsbury Q&A/chat pages
- Scholastic Rowling chat pages
- publisher interviews
- official Harry Potter / Pottermore material no longer live

Record both the original URL and archive URL.

---

# 10. Source Authority Model

Assign every acquired resource an authority level.

## Level A — Official primary

Examples:

- HarryPotter.com J.K. Rowling Original
- live J.K. Rowling official website page
- original Bloomsbury transcript
- original Scholastic transcript

Suggested field:

```yaml
authority: A
```

## Level B — Contemporary primary transcript / faithful mirror

Examples:

- Accio Quote transcript that identifies the original interview/chat
- Leaky Cauldron transcript of its own Rowling interview
- MuggleNet transcript of its own Rowling interview

```yaml
authority: B
```

## Level C — Archived official material

Example:

- Wayback capture of JKRowling.com

```yaml
authority: C
```

This is still strong evidence, but preserve archive provenance.

## Level D — Preservation transcription

Example:

- HP Lexicon transcription of a lost JKR website page for which no original/archive copy is recoverable

```yaml
authority: D
```

## Level E — Secondary discovery

Examples:

- Accio topic summary
- HP Lexicon encyclopedia page
- fan wiki

```yaml
authority: E
```

Level E should normally **not feed factual evidence directly**.

---

# 11. Relevance Classification

Each resource should receive one or more relevance tags.

Suggested tags:

```text
founding
founders
castle_architecture
castle_magic
grounds
admissions
transport
houses
sorting
curriculum
examinations
staff
headmasters
governance
ministry_relations
discipline
student_welfare
student_life
seasonal_customs
library
archives
portraits
ghosts
peeves
quidditch
competitions
hogsmeade
secret_passages
security
protective_magic
relics
historical_students
historical_incidents
first_wizarding_war
pre_1984
post_1984
authorial_process
possible_non_hogwarts_context
```

A source can have multiple tags.

---

# 12. Temporal Rules

The reconstructed *Hogwarts: A History* is being treated as an in-universe work whose main historical content stops around **1984**.

However, source publication date is not the same thing as claim date.

For example:

- Rowling may state something in 2007 about a Hogwarts practice established centuries earlier.
- That claim can still be relevant to the pre-1984 book.
- A 2007 statement about events in 1997 belongs to later editorial notes, not the 1984 body.

Therefore preserve:

```yaml
source_date:
claim_era:
```

Do not exclude post-1984 publications merely because of publication date.

---

# 13. Special Handling of Contradictions

Do not "fix" Rowling statements when they conflict with:

- novels
- later Rowling writing
- other interviews
- dates
- population figures
- geography
- school mechanics

Instead record the source independently.

Future claim clustering should be able to see:

```text
claim A
supported by source X
contradicted/qualified by source Y
```

Never silently reconcile conflicting evidence during acquisition.

---

# 14. Fan Wikis and Forums

Fan resources may be used for **discovery only**.

Useful purpose:

```text
fan page -> citation/source hint -> primary source search
```

They may identify obscure Rowling answers, old interviews, old website extras, or statements whose original page has disappeared.

Do not bulk-import fan-written Hogwarts history as evidence.

For every useful fan-page statement, search for its cited primary source.

If no primary/preservation source can be found, place it in:

```text
resources/external/unresolved/
```

with a note explaining what remains unverified.

---

# 15. Existing Companion Books

These are separate from the web acquisition task but should be recognized as high-authority book sources already available / being processed in the project.

Expected companion-book corpus includes:

- *Quidditch Through the Ages*
- *Fantastic Beasts and Where to Find Them*
- *The Tales of Beedle the Bard*

Do not replace these with web transcriptions if local editions already exist.

In particular, *The Tales of Beedle the Bard* contains Dumbledore commentary with substantial Hogwarts institutional material, including:

- Armando Dippet
- Silvanus Kettleburn
- Hogwarts Christmas pantomime
- Great Hall damage
- hospital wing
- probation/discipline
- Board of Governors
- Hogwarts library
- Lucius Malfoy
- headmaster authority

Treat the local book as the source of record.

---

# 16. Acquisition Workflow

Perform the work in this order.

## Step 1 — Inspect repository conventions

Before writing anything:

- locate existing resource/source directories
- inspect manifests
- inspect naming conventions
- inspect any source-ingestion scripts
- reuse established conventions where sensible

Do not create a parallel source system if one already exists.

## Step 2 — Acquire Corpus A

Acquire the verified HarryPotter.com Rowling Originals listed above.

Then enumerate the rest of the Rowling Originals archive and acquire every Hogwarts-relevant article.

## Step 3 — Acquire Corpus B

Acquire the verified interview/Q&A transcripts.

For each Accio transcript:

- inspect attribution
- identify original publisher/interviewer
- search for original transcript
- save original where accessible
- retain Accio URL as preservation/discovery metadata

## Step 4 — Acquire Corpus C

Recover relevant old JKRowling.com material.

Prefer archived original captures.

## Step 5 — Expand through discovery indexes

Search Accio Quote, HP Lexicon, Leaky Cauldron, and MuggleNet for additional Rowling material.

## Step 6 — Create/update manifest

Every local resource gets a manifest record.

## Step 7 — Validate files

Check:

- file exists
- text is non-empty
- metadata header exists
- original URL exists
- source class exists
- title/date are populated when known
- text extraction did not capture navigation junk instead of source content
- encoding is UTF-8

## Step 8 — Report

Produce:

```text
resources/manifests/external-source-acquisition-report.md
```

or the repository-equivalent location.

Report:

- sources discovered
- sources acquired
- sources skipped
- inaccessible sources
- sources requiring archive recovery
- duplicate mirrors
- unresolved provenance
- count by authority level
- count by source class
- count by relevance tag
- recommended next extraction batch

---

# 17. Suggested Manifest Schema

If the project does not already define one, use something close to:

```yaml
- id: external-A01
  title: "Chamber of Secrets"
  author: "J.K. Rowling"
  source_site: "HarryPotter.com"
  source_class: official_rowling_original
  authority: A
  publication_date: null
  original_url: "https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets"
  retrieval_url: "https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets"
  archive_url: null
  retrieved_at: "2026-08-15"
  local_path: "resources/external/official-rowling/harrypotter-com/chamber-of-secrets.md"
  sha256: null
  completeness: complete
  relevance:
    - founding
    - founders
    - castle_architecture
    - historical_incidents
    - pre_1984
  evidence_use: primary
  notes: null
```

Do not force this schema if an existing project schema already covers these fields.

---

# 18. Deduplication Rules

The same Rowling statement may appear on:

- original publisher site
- Accio Quote
- Leaky Cauldron
- HP Lexicon
- archived snapshots

Do not create five independent logical sources for one interview.

Instead model:

```text
logical source
  ├── preferred primary URL
  ├── preservation mirror URL
  └── archive URL
```

A mirror is useful provenance and resilience, but it should not inflate evidence weight later.

---

# 19. Text Normalization

When saving readable snapshots:

Remove:

- navigation
- cookie notices
- ads
- unrelated recommendation widgets
- footer boilerplate
- unrelated site chrome

Preserve:

- title
- date
- interviewer
- question labels
- Rowling answers
- section headings
- footnotes
- context needed to understand the answer

Do not paraphrase the source during acquisition.

The local snapshot should be a faithful, readable representation of the publicly available source text.

---

# 20. Copyright / Storage Discipline

This is a private research corpus used for source analysis.

Prefer storing:

- source metadata
- faithful text needed for analysis
- URL provenance

Do not publish the acquired corpus externally.

Do not retrieve pirated copies of published books.

For published companion books, use the legitimate local project copies already available.

---

# 21. Acceptance Criteria

The acquisition pass is complete when all of the following are true:

- [ ] Existing repository source conventions were inspected first.
- [ ] All verified Corpus A seed pages were acquired or explicitly reported unavailable.
- [ ] The full HarryPotter.com Rowling Originals archive was searched for additional Hogwarts-relevant pages.
- [ ] All verified Corpus B transcripts were acquired or explicitly reported unavailable.
- [ ] All parts of multi-part interviews were discovered and linked together.
- [ ] Accio Quote Hogwarts topic index was exhausted as a discovery queue.
- [ ] HP Lexicon Sources Archive was checked for additional Rowling primary sources.
- [ ] Old JKRowling.com material relevant to Hogwarts was searched and recovered where possible.
- [ ] Original/primary URLs were preferred over summaries.
- [ ] Mirrors were not counted as independent corroborating evidence.
- [ ] Every acquired resource has provenance metadata.
- [ ] Every acquired resource has an authority classification.
- [ ] Every acquired resource has relevance tags.
- [ ] Inaccessible/unverified items were recorded instead of guessed.
- [ ] No book drafting was performed.
- [ ] No structural/taxonomy refactor was performed.
- [ ] No existing evidence records were deleted.
- [ ] An acquisition report was produced.

---

# 22. Deliverables

At the end of the run, provide:

1. **Local source files** for all acquired resources.
2. **External source manifest** containing provenance and authority.
3. **Acquisition report** listing what was found and what remains unresolved.
4. **Discovery backlog** for sources that need manual/archive recovery.
5. **Suggested extraction order** for the next phase.

Do not begin extraction into the main evidence seed unless separately instructed.

---

# 23. Recommended Extraction Order After Acquisition

Once acquisition is complete, the next extraction run should probably proceed in this order:

1. *Quidditch Through the Ages* — if current processing is not yet complete
2. *The Tales of Beedle the Bard*
3. *Fantastic Beasts and Where to Find Them* — Hogwarts-relevant material only
4. HarryPotter.com J.K. Rowling Originals
5. Rowling Q&A/interview corpus
6. Archived JKRowling.com material
7. Only then use secondary indexes to identify remaining gaps

Do not start the structural consolidation pass until these high-authority sources have been extracted, because they are likely to provide strong anchor claims for the later claim-clustering/taxonomy phase.

---

# 24. Seed URLs — Machine-Friendly List

```text
https://www.harrypotter.com/writing-by-jk-rowling
https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets
https://www.harrypotter.com/writing-by-jk-rowling/the-sorting-hat
https://www.harrypotter.com/writing-by-jk-rowling/the-quill-of-acceptance-and-the-book-of-admittance
https://www.harrypotter.com/writing-by-jk-rowling/the-hogwarts-express
https://www.harrypotter.com/writing-by-jk-rowling/hogwarts-portraits
https://www.harrypotter.com/writing-by-jk-rowling/hogwarts-ghosts
https://www.harrypotter.com/writing-by-jk-rowling/hufflepuff-common-room
https://www.harrypotter.com/writing-by-jk-rowling/the-sword-of-gryffindor
https://www.harrypotter.com/writing-by-jk-rowling/the-great-lake
https://www.harrypotter.com/writing-by-jk-rowling/remus-lupin
https://www.harrypotter.com/writing-by-jk-rowling/the-marauders-map
https://www.harrypotter.com/writing-by-jk-rowling/professor-mcgonagall
https://www.harrypotter.com/writing-by-jk-rowling/professor-kettleburn
https://www.harrypotter.com/writing-by-jk-rowling/the-mirror-of-erised
https://www.harrypotter.com/writing-by-jk-rowling/the-original-forty

https://www.accio-quote.org/themes/hogwarts.htm
https://www.accio-quote.org/articles/2000/0200-scholastic-chat.htm
https://www.accio-quote.org/articles/2000/1000-aol-chat.htm
https://www.accio-quote.org/articles/2004/0304-wbd.htm
https://www.accio-quote.org/articles/2005/0705-tlc_mugglenet-anelli-1.htm
https://www.accio-quote.org/articles/2005/0705-tlc_mugglenet-anelli-2.htm
https://www.accio-quote.org/articles/2005/0705-tlc_mugglenet-anelli-3.htm
https://www.accio-quote.org/articles/2005/0705-edinburgh-ITVcubreporters.htm
https://www.accio-quote.org/articles/2007/0730-bloomsbury-chat.html
https://www.accio-quote.org/articles/2007/1217-pottercast-anelli.html

https://www.hp-lexicon.org/source/
https://www.hp-lexicon.org/source/guide-to-rowling-website/
https://www.hp-lexicon.org/source/other-canon/jkr/

https://www.the-leaky-cauldron.org/2007/09/10/interviews/
https://www.the-leaky-cauldron.org/2007/07/30/j-k-rowling-web-chat-transcript/
https://www.the-leaky-cauldron.org/2007/12/23/transcript-of-part-1-of-pottercast-s-jk-rowling-interview/
```

---

## Final instruction to the agent

Treat this file as a **seed and acquisition contract, not an exhaustive bibliography**.

The successful result is not merely "download the listed pages."

The successful result is:

> Build a traceable, authority-ranked, machine-readable collection of accessible Rowling-authored and Rowling-spoken material relevant to Hogwarts, discover additional primary sources through the listed indexes, preserve the best available version of each logical source, and add the corpus to the project without altering the existing evidence seed or book structure.

---

# 25. Supplementary Source Queue — Append-Only Discovery Pass

**Added:** 2026-08-15  
**Scope:** Additional sources discovered after the seed plan above was written.  
**Preservation rule:** This section supplements the existing results; it does not replace, renumber, or revise any source already listed.

The entries below are acquisition candidates. Their short relevance notes are routing metadata, not evidence claims and not substitutes for the source text. Validate authorship, date, completeness, and the best available original or archive copy during acquisition.

## 25.1 Additional HarryPotter.com J.K. Rowling Originals

These pages are explicitly presented by HarryPotter.com as original writing by J.K. Rowling. Treat the direct page as `authority: A` while it remains accessible.

### A16 — Peeves

https://www.harrypotter.com/writing-by-jk-rowling/peeves

**Priority:** very high

High value for:

- an inhabitant present since the founding era
- the first Hogwarts caretaker
- named later caretakers and headmistresses
- the 1876 evacuation and negotiated settlement
- institutional discipline and limits of headmaster authority

### A17 — Pensieve

https://www.harrypotter.com/writing-by-jk-rowling/pensieve

**Priority:** very high

High value for:

- the school-owned Pensieve
- headmaster and headmistress institutional memory
- an artefact predating Hogwarts
- a possible founder-era discovery tradition
- school archives and succession

### A18 — Hogwarts School Subjects

https://www.harrypotter.com/writing-by-jk-rowling/hogwarts-school-subjects

**Priority:** very high

High value for:

- compulsory first-year curriculum
- elective subjects
- advanced Alchemy provision
- historical curriculum development

Keep the author-development note distinct from settled in-universe curriculum.

### A19 — King's Cross Station

https://www.harrypotter.com/writing-by-jk-rowling/kings-cross-station

**Priority:** high

High value for:

- construction of Hogsmeade station
- creation of Platform Nine and Three-Quarters
- Ministers Ottaline Gambol and Evangeline Orpington
- Ministry staffing at the start and end of school terms
- transport security and Statute of Secrecy procedures

Acquire as a logical companion to A04, not as duplicate corroboration of the same statement.

### A20 — Hatstall

https://www.harrypotter.com/writing-by-jk-rowling/hatstall

**Priority:** high

High value for:

- rare Sorting outcomes
- institutional terminology
- historical students and staff
- the Sorting Hat's decision practice

### A21 — Toads

https://www.harrypotter.com/writing-by-jk-rowling/toads

**Priority:** high

High value for:

- permitted school pets
- older Potions and Charms practices
- Ministry animal-welfare regulation
- changing student customs
- the grounds and lake

### A22 — Familiars

https://www.harrypotter.com/writing-by-jk-rowling/familiars

**Priority:** medium

High value for:

- the status of student animals as pets rather than familiars
- school pet policy
- Argus Filch and Mrs Norris
- the role of owls as an organized postal service

### A23 — Owls

https://www.harrypotter.com/writing-by-jk-rowling/owls

**Priority:** medium

High value for:

- wizarding correspondence
- student and family communication
- postal-owl ownership and access
- protective magic against correspondence

### A24 — The Floo Network

https://www.harrypotter.com/writing-by-jk-rowling/the-floo-network

**Priority:** high

High value for:

- the general exclusion of Hogwarts fireplaces from the network
- school security policy
- Ministry regulation of magical transport
- exceptional or illicit connections

### A25 — Time-Turner

https://www.harrypotter.com/writing-by-jk-rowling/time-turner

**Priority:** medium

High value for:

- Ministry permission for exceptional student use
- timetable administration
- the sole Time-Turner known to have entered Hogwarts in the relevant account

Most explicit events are post-1984; tag them accordingly.

### A26 — Colours

https://www.harrypotter.com/writing-by-jk-rowling/colours

**Priority:** high

High value for:

- House colours
- the four Houses' elemental associations
- authorial symbolism versus in-universe fact

Separate symbolic author commentary from claims a Hogwarts historian could know in-universe.

### A27 — Werewolves

https://www.harrypotter.com/writing-by-jk-rowling/werewolves

**Priority:** high

High value for:

- a secret population released into the Forbidden Forest
- Dumbledore-era grounds policy
- staff use of rumours to discourage entry to the Forest
- institutional handling of lycanthropy

Deduplicate overlapping Remus Lupin material against A10.

### A28 — Wizarding Schools

https://www.harrypotter.com/writing-by-jk-rowling/wizarding-schools

**Priority:** high

High value for:

- Hogwarts in the international school system
- International Confederation registration
- concealment and defensive siting of magical schools
- home-schooling as an alternative to institutional education

### A29 — Beauxbatons Academy of Magic

https://www.harrypotter.com/writing-by-jk-rowling/beauxbatons-academy-of-magic

**Priority:** medium

High value for:

- comparative school population
- long-term Hogwarts-Beauxbatons relations
- historical Triwizard results
- international school rivalry and exchange

### A30 — Ilvermorny School of Witchcraft and Wizardry

https://www.harrypotter.com/writing-by-jk-rowling/ilvermorny

**Priority:** medium

High value for:

- Salazar Slytherin's descendants
- Hogwarts admissions refused by a guardian
- Hogwarts as a model for another school's four-House system
- comparative Sorting and governance

Keep second-hand descriptions of Hogwarts attributed to their in-universe speakers.

### A31 — Professor Quirrell

https://www.harrypotter.com/writing-by-jk-rowling/professor-quirrell

**Priority:** medium

High value for:

- Defence Against the Dark Arts staffing
- a staff member's pre-employment travels
- a Hogwarts appointment exploited by Voldemort

### A32 — Gilderoy Lockhart

https://www.harrypotter.com/writing-by-jk-rowling/gilderoy-lockhart

**Priority:** high

High value for:

- historical student discipline and school-wide incidents
- staff recollections of a former student
- Defence Against the Dark Arts recruitment
- Dumbledore's hiring strategy

### A33 — Sybill Trelawney

https://www.harrypotter.com/writing-by-jk-rowling/sybill-trelawney

**Priority:** high

High value for:

- Divination staffing
- recruitment and sanctuary policy
- staff accommodation and staff relationships

### A34 — Dolores Umbridge

https://www.harrypotter.com/writing-by-jk-rowling/dolores-umbridge

**Priority:** medium

High value for:

- a historical student's experience of Hogwarts
- Ministry interference in school governance
- the Inquisitor role and abuse of disciplinary authority

Most governance events are post-1984 and must not enter the main historical body unqualified.

### A35 — Draco Malfoy

https://www.harrypotter.com/writing-by-jk-rowling/draco-malfoy

**Priority:** medium

High value for:

- pre-arranged student social networks
- prefect selection
- House and faculty favoritism
- student use of the Room of Requirement and school security failures

Most material is post-1984; preserve only as later editorial evidence unless a claim clearly concerns an earlier practice.

### A36 — Scottish Rugby

https://www.harrypotter.com/writing-by-jk-rowling/scottish-rugby

**Priority:** high

High value for:

- a nineteenth-century wizarding family whose children attended Hogwarts
- a Squib's attempted entry into the school
- the Sorting Hat's rejection of a non-magical child
- an exceptional admissions and Sorting incident

### A37 — Extension Charms

https://www.harrypotter.com/writing-by-jk-rowling/extension-charms

**Priority:** medium

High value for:

- standard Hogwarts school trunks
- Ministry-approved manufacture of school equipment
- the Ford Anglia in the Forbidden Forest

## 25.2 Additional Rowling Interview, Chat, and Broadcast Transcripts

Unless an original publisher or broadcaster copy is recovered, classify these Accio Quote pages as `authority: B` preservation transcripts. Retain the named original outlet in provenance metadata.

### B11 — The Herald interview — 24 June 1997

https://www.accio-quote.org/articles/1997/0697-herald-johnstone.html

Useful for the earliest published statement that Rowling imagined Hogwarts in Scotland.

### B12 — Guardian Unlimited interview — 16 February 1999

https://www.accio-quote.org/articles/1999/0299-guardian-carey.htm

Useful for:

- Hogwarts as a boarding school
- nighttime student life
- the school's role as security and surrogate family
- the contrast between strict rules and institutional danger

### B13 — Salon interview — 1999

https://www.accio-quote.org/articles/1999/0399-salon-weir.htm

Useful for Hogwarts as sanctuary, boarding-school autonomy, castle spaces, portraits, ghosts, and grounds. Confirm the exact publication date before populating the manifest.

### B14 — Barnes & Noble interview — 19 March 1999

https://www.accio-quote.org/articles/1999/0399-barnesandnoble.html

Useful for Muggle-born magical ability, early school-world planning, Quidditch, and Rowling's research versus invention.

### B15 — Barnes & Noble live chat — 8 September 1999

https://www.accio-quote.org/articles/1999/0999-barnesnoble-staff.htm

Useful for:

- Hogwarts' Scottish location
- King's Cross routing
- school planning and the size of the cast
- early statements about staff and students

### B16 — Boston Globe / Student NewsLine interview — 18 October 1999

https://www.accio-quote.org/articles/1999/1099-bostonglobe-loer.html

Useful for the Sorting Hat, the purpose and dangers of Quidditch, Hogwarts' distinct school culture, and authorial design.

### B17 — The Connection, WBUR Radio — 12 October 1999

https://www.accio-quote.org/articles/1999/1099-connectiontransc2.htm

Useful for school architecture and secret passages, staff, and the statement that one of Harry's classmates later teaches at Hogwarts. Preserve the transcript's own note that it is a courtesy transcription and look for surviving WBUR audio.

### B18 — The Diane Rehm Show, WAMU — December 1999

https://www.accio-quote.org/articles/1999/1299-wamu-rehm.htm

Useful for folklore behind Hogwarts ghosts and Rowling's research methods. Verify the broadcast date from the transcript or broadcaster archive.

### B19 — South West News Service interview — July 2000

https://www.accio-quote.org/articles/2000/0700-swns-alfie.htm

Useful for:

- Hogwarts serving Britain and Ireland
- concealment from Muggles
- staff residence during holidays
- Filch's continuing presence
- kitchens and dietary accommodation
- common-room access

### B20 — Barnes & Noble / Yahoo! chat — 20 October 2000

https://www.accio-quote.org/articles/2000/1000-livechat-barnesnoble.html

Useful for:

- Filius Flitwick as Head of Ravenclaw
- Hagrid's House
- staff discipline and Dumbledore's tolerance of harsh teaching
- historical students and House affiliation

### B21 — Raincoast Books interview — March 2001

https://www.accio-quote.org/articles/2001/0301-raincoast-interview.html

Useful for:

- *Quidditch Through the Ages* as a Hogwarts library book
- *Fantastic Beasts and Where to Find Them* as a school textbook
- schoolbook graffiti and student use
- Quidditch history

Treat this as contextual provenance for the local companion books, not as an independent duplicate of their contents.

### B22 — BBC Blue Peter interview — March 2001

https://www.accio-quote.org/articles/2001/0301-bluepeter.htm

Useful for the Forbidden Forest, dangerous-creature policy, and Fluffy's disposition after the first school year.

### B23 — BBC Red Nose Day chat — 12 March 2001

https://www.accio-quote.org/articles/2001/0301-bbc-rednose.htm

Useful for Hogwarts staff family life, magical instruction, and school-era character chronology.

### B24 — BBC *Harry Potter and Me* — 28 December 2001

https://www.accio-quote.org/articles/2001/1201-bbc-hpandme.htm

Useful for:

- Rowling's chart of Hogwarts students
- House, ability, parentage, and allegiance metadata
- early planning of school organization
- visual evidence of notebooks and planning documents

Where the transcript describes a document visible on screen, preserve a lawful still or timestamped visual reference rather than treating the transcript's description as the document itself.

### B25 — BBC Radio 4, *Living with Harry Potter* — 10 December 2005

https://www.accio-quote.org/articles/2005/1205-bbc-fry.html

Useful for:

- why Hogwarts is a boarding school
- remoteness and concealment
- the institutional setting as a contained magical community
- Gilderoy Lockhart and staff conception

Prefer surviving BBC audio as the primary carrier and retain the Accio transcript as an access copy.

### B26 — Radio City Music Hall reading and Q&A, Part 2 — 2 August 2006

https://www.accio-quote.org/articles/2006/0802-radiocityreading2.html

Useful for Madam Pince, the Hogwarts library as a plot and research environment, and selected staff or House questions. Acquire the complete event set if other parts survive.

## 25.3 Rowling-Authored Published and Legacy Source Families

These sources do not fit cleanly into Corpora A-C but are important omissions from an external-Hogwarts bibliography.

### E01 — *Hogwarts: An Incomplete and Unreliable Guide* — 2016

Official Pottermore Presents ebook by J.K. Rowling.

**Priority:** very high

Acquire a legitimate edition and use it as a stable published carrier for Rowling material on Hogwarts. It substantially overlaps HarryPotter.com originals, so map chapter/section-to-web-page equivalence and avoid counting both carriers as independent corroboration.

### E02 — *Short Stories from Hogwarts of Heroism, Hardship and Dangerous Hobbies* — 2016

Official Pottermore Presents ebook by J.K. Rowling.

**Priority:** high

Useful for staff and historical students, including McGonagall, Lupin, Trelawney, and Kettleburn. Deduplicate against the corresponding HarryPotter.com originals.

### E03 — *Short Stories from Hogwarts of Power, Politics and Pesky Poltergeists* — 2016

Official Pottermore Presents ebook by J.K. Rowling.

**Priority:** high

Useful for Peeves, Quirrell, Lockhart, Umbridge, school governance, and institutional power. Deduplicate against the corresponding HarryPotter.com originals.

### E04 — *Fantastic Beasts: The Crimes of Grindelwald — The Original Screenplay* — 2018

Published screenplay by J.K. Rowling.

**Priority:** high

Useful for 1910s and 1927 Hogwarts, Dumbledore's teaching career, staff intervention, classroom practice, and school architecture. Treat screenplay text as the source of record; do not silently substitute film-only visual additions.

### E05 — *Fantastic Beasts: The Secrets of Dumbledore — The Complete Screenplay* — 2022

Published screenplay by J.K. Rowling and Steve Kloves.

**Priority:** high

Useful for 1930s Hogwarts, Dumbledore's teaching environment, the Great Hall, the Room of Requirement, staff, and international wizarding politics touching the school. Preserve joint authorship and distinguish screenplay directions from spoken in-universe testimony.

### E06 — Original Famous Wizard Cards

Discovery and provenance index:

https://www.hp-lexicon.org/source/other-canon/fw/

**Priority:** very high

Rowling stated that she wrote the original Famous Wizard Card information. This source family is valuable for:

- Hogwarts founders
- former headmasters and headmistresses
- Hogsmeade's founder
- historical witches and wizards connected to school subjects
- institutional chronology

Do not assume that every trading card or every later game-card variant contains Rowling-authored text. Recover the original card set and record platform/edition differences.

### E07 — Official Harry Potter Fan Club *Daily Prophet* newsletters — 1998-1999

Discovery and provenance index:

https://www.hp-lexicon.org/source/other-canon/dp/

Issue records:

- https://www.hp-lexicon.org/source/other-canon/dp/dp1/
- https://www.hp-lexicon.org/source/other-canon/dp/dp2/
- https://www.hp-lexicon.org/source/other-canon/dp/dp3/
- https://www.hp-lexicon.org/source/other-canon/dp/dp4/

**Priority:** medium

Bloomsbury confirmed that Rowling wrote these four newsletters. They are useful for school-adjacent institutions, Quidditch, Hogwarts supplies, and later editorial context. Their internal dates and some terminology conflict with later canon; preserve each issue independently and flag contradictions rather than reconciling them.

### E08 — The 2008 Harry Potter prequel

Published in the charity anthology *What's Your Story?* from Waterstones; written by J.K. Rowling.

**Priority:** medium

Useful for James Potter and Sirius Black as recently graduated historical students and for the pre-1984 First Wizarding War context. Acquire only a legitimate published or officially released copy; do not use unauthorized scans.

### E09 — *Conversations with J.K. Rowling* by Lindsey Fraser — 2001

**Priority:** high

This published interview is repeatedly cited by the Accio Hogwarts index for Hogwarts' institutional conception, the original subject list, and school organization. Acquire a legitimate copy and classify Rowling's answers as primary interview material while preserving Fraser's editorial text separately.

### E10 — ITV, *J.K. Rowling: A Year in the Life* — 2007

**Priority:** medium

The documentary includes primary Rowling commentary and visual access to authorial planning material. Acquire a lawful recording or broadcaster transcript and preserve timestamps. Mark planning notes and family-tree material as authorial-process evidence unless Rowling explicitly presents them as in-universe facts.

## 25.4 Additional Preservation and Enumeration Tools

### D06 — The Rowling Library archive of J.K. Rowling's original website

https://www.therowlinglibrary.com/j-k-rowling/official-website/

Use as a discovery and preservation aid only. Record original `jkrowling.com` URLs and prefer a readable Wayback capture of the official page when one survives.

### D07 — Accio Quote chronological indexes

```text
https://www.accio-quote.org/articles/list1997.html
https://www.accio-quote.org/articles/list1998.html
https://www.accio-quote.org/articles/list1999.html
https://www.accio-quote.org/articles/list2000.html
https://www.accio-quote.org/articles/list2001.html
https://www.accio-quote.org/articles/list2004.html
https://www.accio-quote.org/articles/list2005.html
https://www.accio-quote.org/articles/list2006.html
https://www.accio-quote.org/articles/list2007.html
```

Use these to catch Hogwarts-relevant material not linked from the thematic index. Apply the same rule as D01: index to transcript to best surviving primary carrier.

### D08 — Harry Potter Lexicon Famous Wizard Cards source index

https://www.hp-lexicon.org/source/other-canon/fw/

Use to enumerate card variants and locate provenance. Do not treat the Lexicon's merged presentation as proof that every line came from a single Rowling-authored card.

### D09 — Harry Potter Lexicon Daily Prophet newsletter source index

https://www.hp-lexicon.org/source/other-canon/dp/

Use to enumerate the four issues, publication dates, and known continuity cautions before seeking scans or physical copies.

## 25.5 Suggested Acquisition Order for This Supplement

Acquire this supplementary queue in the following order:

1. A16-A19: Peeves, Pensieve, Hogwarts School Subjects, and King's Cross Station.
2. A20-A28: Sorting, student life, communications, security, grounds, and international-school context.
3. E01-E03: the three stable Pottermore Presents editions, with explicit carrier-level deduplication.
4. E04-E06: pre-1984 screenplay scenes and the original Famous Wizard Cards.
5. B11-B26: interview and broadcast transcripts, preferring original audio/publisher carriers.
6. E07-E10: newsletters, prequel, published interview, and documentary.
7. D06-D09: preservation recovery and completeness audit.

This supplement expands the acquisition queue only. It does not authorize changes to the current book seed, generated appendices, structured source YAML, taxonomy, outline, or processing state.

## 25.6 Supplementary URLs — Machine-Friendly List

```text
https://www.harrypotter.com/writing-by-jk-rowling/peeves
https://www.harrypotter.com/writing-by-jk-rowling/pensieve
https://www.harrypotter.com/writing-by-jk-rowling/hogwarts-school-subjects
https://www.harrypotter.com/writing-by-jk-rowling/kings-cross-station
https://www.harrypotter.com/writing-by-jk-rowling/hatstall
https://www.harrypotter.com/writing-by-jk-rowling/toads
https://www.harrypotter.com/writing-by-jk-rowling/familiars
https://www.harrypotter.com/writing-by-jk-rowling/owls
https://www.harrypotter.com/writing-by-jk-rowling/the-floo-network
https://www.harrypotter.com/writing-by-jk-rowling/time-turner
https://www.harrypotter.com/writing-by-jk-rowling/colours
https://www.harrypotter.com/writing-by-jk-rowling/werewolves
https://www.harrypotter.com/writing-by-jk-rowling/wizarding-schools
https://www.harrypotter.com/writing-by-jk-rowling/beauxbatons-academy-of-magic
https://www.harrypotter.com/writing-by-jk-rowling/ilvermorny
https://www.harrypotter.com/writing-by-jk-rowling/professor-quirrell
https://www.harrypotter.com/writing-by-jk-rowling/gilderoy-lockhart
https://www.harrypotter.com/writing-by-jk-rowling/sybill-trelawney
https://www.harrypotter.com/writing-by-jk-rowling/dolores-umbridge
https://www.harrypotter.com/writing-by-jk-rowling/draco-malfoy
https://www.harrypotter.com/writing-by-jk-rowling/scottish-rugby
https://www.harrypotter.com/writing-by-jk-rowling/extension-charms

https://www.accio-quote.org/articles/1997/0697-herald-johnstone.html
https://www.accio-quote.org/articles/1999/0299-guardian-carey.htm
https://www.accio-quote.org/articles/1999/0399-salon-weir.htm
https://www.accio-quote.org/articles/1999/0399-barnesandnoble.html
https://www.accio-quote.org/articles/1999/0999-barnesnoble-staff.htm
https://www.accio-quote.org/articles/1999/1099-bostonglobe-loer.html
https://www.accio-quote.org/articles/1999/1099-connectiontransc2.htm
https://www.accio-quote.org/articles/1999/1299-wamu-rehm.htm
https://www.accio-quote.org/articles/2000/0700-swns-alfie.htm
https://www.accio-quote.org/articles/2000/1000-livechat-barnesnoble.html
https://www.accio-quote.org/articles/2001/0301-raincoast-interview.html
https://www.accio-quote.org/articles/2001/0301-bluepeter.htm
https://www.accio-quote.org/articles/2001/0301-bbc-rednose.htm
https://www.accio-quote.org/articles/2001/1201-bbc-hpandme.htm
https://www.accio-quote.org/articles/2005/1205-bbc-fry.html
https://www.accio-quote.org/articles/2006/0802-radiocityreading2.html

https://www.hp-lexicon.org/source/other-canon/fw/
https://www.hp-lexicon.org/source/other-canon/dp/
https://www.hp-lexicon.org/source/other-canon/dp/dp1/
https://www.hp-lexicon.org/source/other-canon/dp/dp2/
https://www.hp-lexicon.org/source/other-canon/dp/dp3/
https://www.hp-lexicon.org/source/other-canon/dp/dp4/
https://www.therowlinglibrary.com/j-k-rowling/official-website/
```

---

# 26. Runes, Potions, Plants, and Early Magical Culture Supplement

**Authorized:** 2026-09-15
**Scope:** Acquire only sources absent from the existing external corpus, extract historically meaningful evidence through the canonical queue, and leave manuscript prose untouched.

The pre-acquisition audit found `A17` — Pensieve already captured and fully extracted. The source and its existing structured entries distinguish its pre-Hogwarts carved-stone and modified-Saxon-rune description from the explicitly unsubstantiated founders legend. It must not be acquired again.

## 26.1 Missing J.K. Rowling Originals

### A38 — The Potter Family

https://www.harrypotter.com/writing-by-jk-rowling/the-potter-family

Preserve Linfred of Stinchcombe as twelfth-century, post-foundation comparative evidence for household experimentation, medicinal service to Muggle neighbours, garden plants, developing remedies, and sales to witches and wizards. Do not backdate his practice to pre-Hogwarts Britain.

### A39 — Potions

https://www.harrypotter.com/writing-by-jk-rowling/potions

Separate in-universe propositions about wandwork, potion effects, and skilled potioneering from the author's real-world commentary about dittany and bezoars.

### A40 — Cauldrons

https://www.harrypotter.com/writing-by-jk-rowling/cauldrons

Separate wizarding-world material history and potion practice from the author's real-world folklore commentary.

### A41 — Mr Ollivander

https://www.harrypotter.com/writing-by-jk-rowling/mr-ollivander

Preserve older wandmaking practice, inherited or personally significant core materials, historical craft innovation, and resistance from established practitioners. Do not date illustrative examples unless the source does.

### A42 — Wand Woods

https://www.harrypotter.com/writing-by-jk-rowling/wand-woods

Extract only historically useful craft traditions, named older wandmakers, inherited knowledge, and relevant plant/creature material relationships; do not reproduce the modern personality catalogue.

### A43 — Fourteenth Century – Seventeenth Century

https://www.harrypotter.com/writing-by-jk-rowling/fourteenth-century-to-seventeenth-century-en

Treat Native American plant magic, potion sophistication, healing, and wandless practice as later, non-British comparative evidence, not direct evidence of pre-Hogwarts British practice.

### A44 — Seventeenth Century and Beyond

https://www.harrypotter.com/writing-by-jk-rowling/seventeenth-century-and-beyond-en

Treat apothecary supply and foraging among unfamiliar magical plants as later comparative evidence. Do not backdate a seventeenth-century supply network into the tenth century.

### A45 — Technology

https://www.harrypotter.com/writing-by-jk-rowling/technology

Preserve the broad pre-Statute sharing of ordinary transport and material technologies while avoiding claims about a precise tenth-century decade.

## 26.2 Official Editorial Context

### F01 — The Hogwarts classes that you might have forgotten about

https://www.harrypotter.com/features/hogwarts-classes-that-you-might-have-forgotten-about

Classify this official editorial carrier as `secondary_reference`, authority `E`. Extract only the source-critical Ancient Runes passage, using `weak_context_only`, low confidence, and explicit limitations preserving the article's phrases “it can be presumed” and “perhaps”. It cannot establish Bronze/Iron Age wizarding runes and cannot override `A17`.

## 26.3 Retrieval and Processing

Fetch only `A38`–`A45` and `F01` by direct public HTTPS request to the catalog URLs above. Store raw HTML in a disposable cache, build normalized Markdown snapshots through `scripts/external_sources/build_external_corpus.py --append --ids ...`, and let `scripts/external_sources/queue.py init` append pending units without resetting existing completion history.

Process each new unit through claim, staging, structured duplicate review, and completion. Rebuild and validate the canonical indexes and generated evidence artifacts after extraction. Do not modify `authoring/`.
