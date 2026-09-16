# Hogwarts: A History — Repository Handoff for Editorial Planning

Audit date: 2026-09-13  
Repository state: evidence extraction complete; editorial architecture and authoring not yet begun

This report is a read-only assessment of the repository as it stood on the audit date. No source data, instructions, indexes, or generated evidence were changed. The ordinary validator passed, all 66 core tests passed, regenerated artifacts matched the checked-in versions in an in-memory comparison, and the worktree was clean before this report was added.

## 1. Project overview

This repository is an evidence-first research system for producing a fan reconstruction or edition of the in-universe book *Hogwarts: A History*. It is not currently a manuscript repository. Its principal achievement is a traceable corpus of claims about Hogwarts, linked back to exact book chapters, PDF pages, or captured external sources and annotated for confidence, era, relevance, duplication, and tentative future placement.

Completed work includes:

- Chapter-by-chapter extraction of all seven Harry Potter novels: 198 chapters and 1,314 evidence entries.
- Section-level extraction of three companion books: *Quidditch Through the Ages*, *The Tales of Beedle the Bard*, and *Fantastic Beasts and Where to Find Them*: 29 source units and 127 entries.
- Acquisition and extraction of 63 external source snapshots: 37 official Rowling/HarryPotter.com documents and 26 preserved interview transcripts, yielding 242 entries.
- Creation of canonical YAML schemas, source and tag indexes, duplicate/corroboration metadata, validators, compact query tools, generated audit appendices, and a generated evidence seed.
- Preservation of 386 structured editorial/research questions.
- Partial construction of a separate non-canon fan-work reference pipeline. Its registry and several library modules exist, but no fan works have been captured into a local corpus.

The current extraction queues are exhausted: `project-control/processing-state.yaml` has no current or next PDF unit, and the external queue has 63 completed units with none pending, in progress, or blocked. `project-control/remaining-source-units.yaml` nevertheless preserves 15 blocked acquisition or audit items for sources that are unavailable, unverified, or not yet recovered.

The extraction system was designed to make every selected claim auditable, keep copyrighted quotations short, distinguish evidence from editorial interpretation, avoid silently double-counting repeated claims, and let later agents retrieve a small subject-specific evidence set instead of loading the whole corpus.

The intended eventual deliverable is a coherent fan-created book modeled on the in-universe *Hogwarts: A History*, potentially with later editorial apparatus. That deliverable does not yet exist. The current `book-seed/hogwarts-a-history-seed.md` is a generated evidence ledger, not drafted prose and not an approved outline.

### Encoded editorial assumptions

- `docs/instructions/background-guide.md` uses an approximate planning boundary of material known up to 1984, explicitly subject to revision.
- Older facts may be candidates for the reconstructed original body.
- Harry-era observations may confirm the persistence of older features, but normally do not prove when those features originated.
- Events clearly after the cutoff are excluded from the original reconstruction and may be retained only as later editorial context.
- Candidate part, chapter, and section labels are tentative extraction metadata, not accepted book architecture.
- Direct evidence, contextual evidence, confidence, era, and duplication are separate dimensions.

### Critical authorship/date correction

The repository does **not** establish that Bathilda Bagshot wrote *Hogwarts: A History*, and it does **not** establish 1984 as the book's publication date. Active material treats 1984 only as an approximate editorial cutoff. Bathilda Bagshot is associated with the different title *A History of Magic* in `sources/book-03/chapter-01-owl-post.yaml`. Some archived instructions and one classification explanation use the shorthand “Bathilda-era text,” but that wording is an unsupported working assumption, not canonical evidence. A future authoring system must not silently convert it into fact.

## 2. Repository map

```text
.
├── Justfile                              # Stable command surface for status, queries, validation, generation, and extraction transitions
├── chapters-index.md                     # PDF page-range map for the seven novels and three companion books
├── requirements.txt                      # Core Python dependencies
├── requirements-fanfic.txt               # Separate dependencies for the unfinished fan-work pipeline
├── pytest.ini                            # Pytest configuration for fan-work tests
├── pdfs/
│   ├── harrypotter.pdf                   # Combined carrier for all seven novels
│   ├── quidditch-through-the-ages.pdf    # Companion-book carrier
│   ├── Beedle The Bard_text.pdf          # Companion-book carrier
│   ├── Fantastic-Beasts-Where-to-Find-Them.pdf
│   ├── extracted image assets            # Auxiliary page/render assets, not independent evidence units
│   └── hogwarts-external-source-acquisition.md
│                                           # Historical acquisition contract and supplementary backlog
├── sources/
│   ├── book-01/ … book-07/               # Canonical YAML evidence for each novel chapter
│   ├── book-qtta/ book-beedle/ book-fb/  # Canonical YAML for the three companion books
│   └── external/
│       ├── official-rowling/             # Canonical YAML extracted from 37 official snapshots
│       └── interviews/                   # Canonical YAML extracted from 26 preservation transcripts
├── project-control/
│   ├── processing-state.yaml             # Authoritative live extraction state
│   ├── source-plan.yaml                  # Per-unit processing ledger and external queue data
│   ├── remaining-source-units.yaml       # Blocked acquisitions/audits and legacy ready-unit identifiers
│   ├── next-run.md                       # Generated compact status display
│   ├── entry-index.yaml                  # Compact entry lookup data
│   ├── source-index.yaml                 # Source-unit lookup data
│   ├── tag-index.yaml                    # Tag-to-entry lookup data
│   ├── duplicate-index.yaml              # Duplicate/corroboration search data
│   ├── book-seed-order.yaml              # Only deliberate current ordering seed; provisional and incomplete
│   ├── structured-sources/open-questions.yaml
│   │                                       # Canonical structured question backlog
│   └── archive/                           # Obsolete run displays and completed-plan snapshot
├── book-seed/
│   └── hogwarts-a-history-seed.md         # Generated 1,683-entry evidence ledger; not a manuscript
├── appendix/generated/
│   ├── book-structure-seed.md             # Alphabetical inventory of tentative placement labels
│   ├── explicit-hogwarts-a-history-references.md
│   ├── open-questions.md
│   ├── project-stats.md
│   ├── review-flags.md
│   └── source-index.md                    # Generated human-readable audit views
├── resources/
│   ├── external/                          # Local Markdown source snapshots and unresolved-source aids
│   └── manifests/                         # External provenance, authority, URL, and hash records
├── docs/
│   ├── instructions/                     # Active extraction contract, compact references, historical plans, and archives
│   └── superpowers/{plans,specs}/         # Implementation history; not current runtime input
├── scripts/
│   ├── core index/query/validation/generation scripts
│   ├── external_sources/                  # External acquisition and transactional queue tooling
│   └── fanfic_dataset/                    # Partially implemented non-canon reference pipeline
├── data/fanfic-hogwarts-history/          # Fan-work registry, schemas, candidate, and exclusion reports only
├── tests/                                 # Core unittest suite and separate pytest-oriented fan-work tests
├── work/external-staging/                 # Empty external extraction staging directory
├── .tmp/                                  # Extraction cache area
├── .venv/                                 # Core Python environment
├── .fanfic-venv/                          # Separate fan-work Python environment
└── .superpowers/sdd/                      # Development task ledgers/reviews, not project runtime
```

Two naming details matter:

- `chapters-index.md` calls Book 1 *Sorcerer's Stone*, while source metadata and `project-control/source-plan.yaml` use *Philosopher's Stone*. This is a label/edition inconsistency, not a coverage gap.
- `sources/` is the canonical evidence store. `book-seed/`, `appendix/generated/`, and most large files in `project-control/` are derived views and indexes.

## 3. Current instructions and agent runtime

### Repository-local automatic instructions

There is no repository `AGENTS.md`, `.agents/`, `.codex/`, or `SKILL.md`. Therefore no repository-local instruction is automatically injected by those conventions. A file historically titled as a Codex skill is ordinary archived Markdown, not an installed skill.

### Active and conditionally active files

| Path | Approximate size | Purpose and dependencies | Current status | Writing-phase suitability |
|---|---:|---|---|---|
| `docs/instructions/runtime-contract.md` | 113 lines / 7.5 KB | Canonical one-unit extraction dispatcher; depends on `Justfile`, processing state, remaining units, the current carrier/output, and conditional schema/background references. | Active | Extraction-specific; unsuitable as an authoring contract. |
| `project-control/processing-state.yaml` | 85 lines / 3.1 KB | Authoritative live state; names the runtime, schema, background guide, indexes, generator, cache, and external queue. | Active | Useful for status, but its extraction task is exhausted. |
| `project-control/next-run.md` | 19 lines / 357 B | Generated display of the next work item and queue totals; produced by `scripts/update_next_run.py`. | Active/generated | Status only. |
| `project-control/source-plan.yaml` | 2,526 lines / 88.5 KB | Per-unit completion ledger for book, companion, and external extraction. | Active record | Coverage reference; mostly extraction history. |
| `project-control/remaining-source-units.yaml` | 126 lines / 6.8 KB | Records blocked acquisitions/audits plus legacy identifiers for the Fantastic Beasts units. | Active record | Useful as a source-gap bibliography. |
| `docs/instructions/schema-reference.md` | 167 lines / 6.2 KB | Defines source-unit and entry fields plus controlled reference, era, and confidence values; parsed by the validator. | Active/conditional | Still essential for interpreting evidence. |
| `docs/instructions/background-guide.md` | 49 lines / 1.7 KB | States project purpose, evidence standards, approximate cutoff, inclusion rules, and common tentative parts. | Active/conditional | Editorially useful, but retains an extraction-era “do not draft prose” scope. |
| `docs/instructions/hogwarts-history-seed-builder.md` | 5 lines / 371 B | Redirects old entry points to the runtime and `Justfile`; points to the archived full instruction. | Active redirect | Extraction legacy. |
| `Justfile` | 101 lines / 3.1 KB | Stable command interface for status, querying, validation, generation, and state transitions. | Active | Query/validation recipes remain useful; transition recipes do not. |

### Starting flow expected today

An extraction agent is currently expected to:

1. Read `docs/instructions/runtime-contract.md`.
2. Run `just brief`, `just next`, and `just external-status`.
3. Inspect `project-control/processing-state.yaml`.
4. Give a non-null `current_source_unit` precedence over the external queue.
5. Read `docs/instructions/schema-reference.md` only for schema uncertainty or validation failures.
6. Read `docs/instructions/background-guide.md` only for canon, era, or classification ambiguity.
7. Avoid archives and broad index loads during routine extraction.

Today that flow ends without extraction: `current_source_unit` and `next_source_unit` are null, and every external unit is done. The contract directs the agent to summarize the blockers in `project-control/remaining-source-units.yaml`.

There is no equivalent writing-phase runtime. The active contract deliberately prohibits drafting and optimizes for processing one bounded source unit, so it should be treated as extraction machinery rather than as instructions for composing chapters.

### Historical, superseded, or planning-only instructions

The following files remain valuable as implementation history but are not loaded by the current dispatcher:

| Path | Approximate size | Status/purpose |
|---|---:|---|
| `docs/instructions/cli-tooling-runtime-update-plan.md` | 479 lines | Historical plan that introduced the current `just`/`rg`-first runtime approach; substantially implemented. |
| `docs/instructions/finish-cli-tooling-implementation-plan.md` | 303 lines | Follow-up cleanup plan; substantially implemented. |
| `docs/instructions/token-efficiency-refactor-instructions.md` | 497 lines | Original minimal-context/indexing refactor instructions. |
| `docs/instructions/finish-token-efficiency-refactor.md` | 310 lines | Follow-up for structured questions, compact queries, and state advancement. |
| `docs/instructions/result-output-redesign-plan.md` | 445 lines | Proposed ordered, cleaner seed and appendix rendering; only partly realized. |
| `docs/instructions/fanfic-hogwarts-history-dataset-plan.md` | 609 lines | Specification for a four-work non-canon reference corpus; implementation incomplete. |
| `docs/instructions/implement-fanfic-dataset-subagent-driven-prompt.md` | 220 lines | Copyable implementation-session prompt; not automatic. |
| `pdfs/hogwarts-external-source-acquisition.md` | 1,948 lines / 54.9 KB | Completed acquisition contract plus an append-only supplementary backlog. |

Superseded variants are under:

- `docs/instructions/archive/hogwarts-history-seed-builder-first.md` — 751 lines.
- `docs/instructions/archive/hogwarts-history-seed-builder-updated.md` — 891 lines.
- `docs/instructions/archive/hogwarts-history-seed-builder.md` — 1,304 lines.
- `docs/instructions/archive/runtime-contract-book-and-companion-extraction-2026-08-15.md` — 99 lines.
- `docs/instructions/archive/runtime-contract-external-source-extraction-completed-2026-09-11.md` — 76 lines.
- `project-control/archive/next-run-2.md` through `next-run-9.md` — obsolete Book 2/3 run snapshots.
- `project-control/archive/source-plan-completed-2026-08-24.yaml` — historical completed-plan snapshot.

`docs/superpowers/` contains eight dated implementation plans and three design specifications. `.superpowers/sdd/` contains development briefs, reviews, and ledgers. Neither directory is part of the active project runtime.

### Instruction and state disagreements

- `project-control/next-run.md` calls `project-control/source-plan.yaml` the “Source of truth,” while the source plan names `project-control/processing-state.yaml` as `authoritative_state`; the runtime also tells agents to inspect processing state first. Operationally, processing state is authoritative.
- `project-control/source-plan.yaml` still reports `current_phase: fantastic-beasts-remainder-extraction` even though every Fantastic Beasts unit is complete and no current/next unit remains.
- `project-control/remaining-source-units.yaml` retains ten Fantastic Beasts “ready extraction” identifiers, but the authoritative plan marks all ten complete. They are not live work.
- `appendix/generated/project-stats.md` calls B26 the latest processed unit because the generator favors the last external item; `project-control/processing-state.yaml` records FB09 as the later completed PDF unit. These are different concepts under an ambiguous label.
- `docs/instructions/schema-reference.md` correctly models external duplicate reviews as `duplicate_check.audit.candidates`, but later prose calls the field `candidate_ids`. Current YAML and queue code use `candidates`.
- `resources/manifests/external-source-acquisition-report.md` says the snapshots were added without extracted claims and cites the older 1,314-entry seed. That was historically accurate at acquisition time; all 63 snapshots have since yielded 242 entries, bringing the total to 1,683.
- Fan-work plans describe `python -m scripts.fanfic_dataset.cli`, but no `scripts/fanfic_dataset/cli.py` exists.

## 4. Evidence dataset

### Corpus totals

| Corpus | Source units | Entries |
|---|---:|---:|
| Seven novels | 198 chapters | 1,314 |
| *Quidditch Through the Ages* | 12 units | 37 |
| *The Tales of Beedle the Bard* | 7 units | 29 |
| *Fantastic Beasts and Where to Find Them* | 10 units | 61 |
| Official Rowling/HarryPotter.com snapshots | 37 documents | 161 |
| Preserved interview transcripts | 26 documents | 81 |
| **Total** | **290** | **1,683** |

All 1,683 evidence IDs are nonempty and globally unique. All 290 source-unit IDs are unique. Of the 290 source YAML files, 289 contain at least one entry. The sole valid empty unit is `sources/book-beedle/chapter-06-back-matter.yaml`, whose material is real-world production/charity information rather than in-universe Hogwarts evidence.

Novel breakdown:

| Directory | Units | Entries |
|---|---:|---:|
| `sources/book-01/` | 17 | 104 |
| `sources/book-02/` | 18 | 115 |
| `sources/book-03/` | 22 | 145 |
| `sources/book-04/` | 37 | 235 |
| `sources/book-05/` | 38 | 261 |
| `sources/book-06/` | 30 | 209 |
| `sources/book-07/` | 36 | 245 |

### Confidence

| Value | Entries | Share |
|---|---:|---:|
| `high` | 1,361 | 80.9% |
| `medium` | 299 | 17.8% |
| `low` | 23 | 1.4% |

The extraction instructions define high confidence as direct source support, medium as a clear fact whose future-book placement is interpretive, and low as a weak candidate or item needing confirmation. All 81 interview-derived entries are medium or low; the 37 official-source units produce 158 high- and 3 medium-confidence entries.

### Era classification

| Exact value | Entries |
|---|---:|
| `original_book_core_candidate` | 13 |
| `pre_1984_historical_candidate` | 346 |
| `harry_era_confirmation` | 554 |
| `later_editorial_note` | 706 |
| `post_1984_excluded_from_original` | 42 |
| `unknown_or_uncertain` | 22 |

### Reference type

| Exact value | Entries |
|---|---:|
| `historical_claim` | 345 |
| `security_or_protection` | 249 |
| `institutional_custom` | 231 |
| `curriculum_or_subject` | 173 |
| `school_rule_or_policy` | 165 |
| `cross_reference_candidate` | 121 |
| `magical_architecture` | 116 |
| `explicit_in_universe_source` | 114 |
| `direct_observed_setting` | 70 |
| `house_system` | 42 |
| `portrait_or_ghost_lore` | 36 |
| `weak_context_only` | 11 |
| `explicit_hogwarts_a_history` | 10 |

There is no separate boolean or enum named `inference`, and no `institutional_history` entry field. Interpretive content lives in the placement reason, relevance explanation, limitations, confidence, and era fields. `institutional_custom` and `historical_claim` are reference types.

### Storage and field model

Canonical evidence lives in `sources/**/*.yaml`. A book/companion source file has a `source_unit` mapping with source PDF, title, chapter/unit name, page range, boundary confidence/notes, processing date, and processing notes. Each entry repeats enough source metadata to be useful independently and includes:

- Identity: `id`.
- Provenance and locators: `source_file`, book, chapter, chapter range, `pdf_page`, `printed_page`, `extracted_text_lines`, and `text_anchor`.
- Evidence summary: `nearby_context`, `match_terms`, `quote_excerpt_short`, and `source_note`.
- Classification: `reference_type`, `era_classification`, and `topic_tags`.
- Tentative structure: `candidate_part`, `candidate_chapter`, `candidate_section`, and `reason_for_placement`.
- Editorial interpretation: `relevance_to_hogwarts_a_history`.
- Overlap: `duplicate_check`, including `possible_duplicate`, optional `duplicate_of`, and—in external records—a structured audit.
- Caution: `confidence` and `limitations`.

External source units instead record a `source_id`, snapshot path, title, author, source site/class/authority, publication date, original and retrieval URLs, completeness, SHA-256 body hash, and processing details. Their entries use `source_id`, `source_url`, optional `source_section`, and text anchors; PDF locators are null.

Locator coverage is complete by carrier type:

- 1,441 PDF-backed entries have a non-null `pdf_page`.
- 242 external entries use snapshot/URL/section locators and null PDF fields.
- `extracted_text_lines` is present for 1,380 entries; it is null for the 242 external entries and the 61 visually extracted, image-only Fantastic Beasts entries.
- Every evidence PDF page falls inside its source unit's page range.

### Tags and tentative placement

The corpus uses 3,205 distinct normalized free-form topic tags, with 3–9 tags per entry. The expected range is 3–8; four entries have nine tags. Candidate placement is also free-form: 197 distinct part labels, 617 distinct chapter labels, 711 distinct part/chapter pairs, 1,524 distinct section labels, and 1,536 exact part/chapter/section triples. This high cardinality is evidence of extraction drift, not a hidden finished outline.

### Representative abbreviated records

Book/PDF example:

```yaml
id: ps-ch07-001
source_file: pdfs/harrypotter.pdf
book: Harry Potter and the Philosopher's Stone
chapter: Chapter Seven - The Sorting Hat
pdf_page: 110
text_anchor:
  start_phrase: It was lit by thousands...
  end_phrase: bewitched to look like the sky outside
source_note: Hermione attributes the enchanted ceiling to Hogwarts: A History.
reference_type: explicit_hogwarts_a_history
era_classification: original_book_core_candidate
topic_tags: [great-hall, enchanted-ceiling, magical-architecture, ...]
candidate_part: Magical Architecture and Enchantments
confidence: high
limitations: Later books may contain additional references.
```

External example:

```yaml
id: ext-a01-002
source_file: resources/external/official-rowling/harrypotter-com/a01-chamber-of-secrets.md
source_id: A01
source_url: https://www.harrypotter.com/...
source_section: Chamber of Secrets
pdf_page: null
text_anchor:
  start_phrase: the entrance to the Chamber was threatened
  end_phrase: newfangled plumbing had been placed on top of it
source_note: Eighteenth-century plumbing changes altered Chamber access.
reference_type: magical_architecture
era_classification: pre_1984_historical_candidate
duplicate_check:
  audit:
    query_tags: [...]
    candidates: [...]
confidence: high
```

### Subject retrieval for an authoring agent

Use the query layer to find candidate IDs and paths, then open only the returned source YAML and, where wording matters, the cited PDF page or snapshot.

```bash
just query-entries founders
just query-entries magical-architecture
just query-entries school-governance
just query-entries quidditch
just query-entries library
just query-entries hogwarts-library
```

Useful exact-tag counts include `founders` 10, `magical-architecture` 45, `school-governance` 22, `quidditch` 48, `library` 22, and `hogwarts-library` 9. The plain tag `governance` has no matches, so synonym awareness is necessary.

`just query-entries` defaults to 20 results. Exhaustive and filtered retrieval uses the underlying script:

```bash
.venv/bin/python scripts/query_entries.py --tag library --limit 10000
.venv/bin/python scripts/query_entries.py \
  --classification pre_1984_historical_candidate --limit 10000
.venv/bin/python scripts/query_entries.py \
  --reference-type magical_architecture --limit 10000
```

The script also supports confidence, source-unit/path, and YAML-output filters. `just query-dupes <tags...>` ranks likely duplicates/corroborations and defaults to ten results; it is not exhaustive subject retrieval.

## 5. Evidence provenance and validation

### Traceability chain

For novels and companion books:

```text
evidence ID
→ sources/book-*/chapter-or-unit.yaml
→ source_unit.source_file
→ book + chapter/unit + inclusive PDF range
→ entry.pdf_page
→ optional printed page and extracted text lines
→ text_anchor start phrase, end phrase, and occurrence note
→ local PDF under pdfs/
```

`chapters-index.md` and `project-control/source-plan.yaml` provide additional range and completion mappings.

For external evidence:

```text
evidence ID
→ sources/external/**/*.yaml
→ source_unit source ID and snapshot path
→ local Markdown snapshot under resources/external/
→ source section and local start/end anchor
→ snapshot front matter and normalized-body SHA-256
→ original/retrieval URL and resources/manifests/external-sources.yaml
```

Official snapshots retain direct HarryPotter.com carriers and authority A. Interview snapshots retain Accio Quote preservation carriers and authority D; where the original publisher or broadcaster carrier was not verified, the transcript is not treated as independent original corroboration.

### Validator

`just validate` runs `scripts/validate_source_yaml.py` in ordinary mode. It currently passes.

It checks:

- Supported source-YAML paths and top-level YAML shape.
- Required source-unit and entry keys.
- Globally unique, nonempty evidence IDs.
- Controlled `reference_type`, `era_classification`, and confidence values.
- Short quotation length: fewer than 25 words.
- Existence of every populated `duplicate_of` target.
- Minimal generated-file markers and parseability of generated indexes.
- For external sources: source-ID and entry-ID forms, completeness, snapshot existence, source/snapshot metadata agreement, 64-character hash form, actual body hash, null PDF locators, required URL/section/anchor fields, and occurrence of both anchor phrases in the snapshot.

It does **not** check:

- Whether book anchors or quotations occur in the underlying PDF.
- PDF hashes or carrier integrity.
- Semantic truth, canon correctness, source-note interpretation, or editorial placement.
- Repeated entry-level book/chapter/range metadata against its enclosing `source_unit`.
- General PDF page/range consistency.
- Chronological consistency or exact event dates.
- Candidate-part/chapter/section vocabulary.
- Freshness or semantic equivalence of indexes and generated appendices; their ordinary validation is mainly structural.
- Current external URL availability.
- Whether a saved duplicate-audit ranking is still the current top-ten ranking after later corpus additions.

Strict mode adds a 3–8 tag count, a maximum 60-word source note, and a requirement that `possible_duplicate: true` have a populated target. It currently fails on seven legacy entries:

- Nine tags: `ps-ch09-005`, `cos-ch07-001`, `poa-ch08-007`, and `hbp-ch12-007`.
- `possible_duplicate: true` but `duplicate_of: null`: `dh-ch02-005`, `dh-ch08-002`, and `dh-ch08-003`.

Run it with:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python scripts/validate_source_yaml.py --strict
```

One additional metadata inconsistency is not caught by the validator: `gof-ch25-005` in `sources/book-04/chapter-25-the-egg-and-the-eye.yaml` repeats `chapter_start_pdf_page: 1337`, whereas its source unit and neighboring entries use 1330. The evidence page is 1337 and is inside the correct 1330–1347 range, so traceability remains possible.

### Duplicate state

- 1,050 entries have `possible_duplicate: true`.
- 1,047 have a populated `duplicate_of`.
- All 242 external entries contain structured duplicate audits, and their saved dispositions are internally consistent.
- Re-running the saved audit tags against the final complete corpus reproduces the exact saved ranking for 143 external entries but changes it for 99. Those 99 are valid historical snapshots of the corpus at completion time, not current top-ten results.

Possible-duplicate flags indicate repeated or corroborating claims needing review; they do not mean 1,050 entries are disposable.

### ID stability and regeneration

IDs are stored in canonical YAML and copied unchanged by index and report generators. Regeneration does not renumber them. Uniqueness is enforced, and external/Fantastic Beasts naming receives some pattern validation, but ordinary novel and companion IDs are not protected by an immutable registry or content-derived scheme. Manual renaming could therefore break cross-references.

An in-memory regeneration comparison confirmed that all four indexes, the main book seed, and all six generated appendices match current canonical inputs byte-for-byte on the audit date. No raw/generated count discrepancy exists. Some generators include date metadata, so byte identity across future dates is not guaranteed even when the evidence is semantically unchanged.

After canonical source changes, the supported sequence is:

```bash
just indexes
just validate
just generate
```

or the combined:

```bash
just post
```

`just generate` alone does not rebuild indexes first, even though some appendices depend on them. The canonical source YAML, local carriers, snapshots, manifests, and IDs should be preserved; generated indexes, seed, and appendices are reproducible views.

## 6. Existing book structure material

### The only deliberate current ordering seed

`project-control/book-seed-order.yaml` is the sole current file that deliberately orders proposed book material. It defines:

- 14 ordered parts.
- 42 part/chapter pairs.
- 70 exact part/chapter/section slots.

The broad parts cover origins, castle and grounds, magical architecture, houses, ceremonies, academic life, governance, residents, protection, Quidditch, scholarship, pre-1984 events, later notes, and an explicit-reference appendix.

This is genuine editorial seed material, but it is incomplete and unapproved:

- All 14 configured part labels occur somewhere in the data.
- Only 37 of 42 configured part/chapter pairs occur.
- Only 57 of 70 configured exact triples occur.
- Only 359 of 1,683 entries use a configured chapter pair.
- Only 133 entries use an exact configured triple.
- 1,075 entries sit under a configured part; 608 use one of 183 unconfigured part labels.

Examples of placement drift:

- The configured `The Four Houses / The Sorting Ceremony` pair is absent; 13 relevant entries use `Ceremonies and School Traditions / The Sorting Ceremony`.
- The configured `Protective Magic and Security / The Castle and Its Concealments` pair is absent; the explicit concealment record sits under `Original Book Core`.
- The configured explicit-reference appendix chapter `Named Sources About Hogwarts` is absent; its relevant entry uses `Chamber of Secrets References`.
- Other configured pairs, including `Origins of the School / The Four Houses`, have no exact match.

### Main seed

`book-seed/hogwarts-a-history-seed.md` is current and generated from source YAML plus `project-control/book-seed-order.yaml`. It is approximately 20,800 lines and 1.87 MB.

It is an evidence ledger, not a manuscript or reliable outline:

- The 14 configured part headings appear first.
- Every unconfigured part label is then appended alphabetically without an explicit boundary identifying it as unordered material.
- “Section summaries” are deterministic counts plus the first source note, not editorial synthesis.
- The file mixes original-core candidates, older history, Harry-era confirmation, post-cutoff context, exclusions, low-confidence material, and duplicates.
- Its header says its source is source YAML, although the ordering file is also a generator dependency.

### Structure appendix

`appendix/generated/book-structure-seed.md` is approximately 2,845 lines and 107 KB. It groups all free-form `candidate_part`, `candidate_chapter`, and `candidate_section` values alphabetically. It contains no accepted narrative order, category consolidation, evidence weighting, contradiction resolution, or claim selection. Labels such as `Hogwarts: A History`, `Hogwarts, a History as a Source`, `Original Book Core`, several unrelated `Part I/II/III/IV` schemes, and `Editorial apparatus` coexist.

It only looks like an outline because extraction destinations were grouped. It should be read as a category inventory.

### “Emerging Parts” and other historical structure work

“Emerging Parts” exists only in three archived seed-builder instructions:

- `docs/instructions/archive/hogwarts-history-seed-builder-first.md`
- `docs/instructions/archive/hogwarts-history-seed-builder-updated.md`
- `docs/instructions/archive/hogwarts-history-seed-builder.md`

Those files describe a former/manual appendix path and sample heading. No current generated file contains an active `Emerging Parts` section.

`docs/instructions/result-output-redesign-plan.md` correctly identified structural consolidation as a bottleneck and proposed a clear unordered-additions boundary and richer synthesized summaries. Current code realized ordered known parts and deterministic generation, but unknown labels are still appended alphabetically and summaries remain mechanical. The plan is therefore historical and only partially realized.

### Other structure-adjacent material

- `docs/instructions/background-guide.md`: compact scope and common-part suggestions.
- `docs/instructions/schema-reference.md`: says candidate placement is tentative.
- `project-control/structured-sources/open-questions.yaml`: unresolved editorial/research issues.
- `appendix/generated/open-questions.md`: human view of those questions plus dynamic low-confidence/unknown-era rows.
- `appendix/generated/review-flags.md`: large filter-oriented quality review.
- `appendix/generated/explicit-hogwarts-a-history-references.md`: compact constraints from explicit title mentions.
- `appendix/generated/project-stats.md`: current distributions.
- `chapters-index.md`: source-carrier chapter boundaries, not proposed chapters for the reconstructed book.

The repository therefore contains a useful provisional ordering seed and extensive grouped evidence, but no approved book architecture.

## 7. Explicit references to *Hogwarts: A History*

`appendix/generated/explicit-hogwarts-a-history-references.md` contains ten records selected by `reference_type: explicit_hogwarts_a_history`. Nine are in-universe novel references; one is an extradiegetic Rowling interview record carried by an authority-D preservation transcript. Nine are high confidence and one is medium. Seven are classified `original_book_core_candidate`, one `pre_1984_historical_candidate`, and two `later_editorial_note`.

| ID and canonical YAML | What the reference establishes |
|---|---|
| `ps-ch07-001` — `sources/book-01/chapter-07-sorting-hat.yaml` | The book describes the Great Hall's enchanted ceiling. |
| `cos-ch09-001` — `sources/book-02/chapter-09-the-writing-on-the-wall.yaml` | Students expect the book to help with the Chamber legend; library copies are in demand, there is a two-week wait, and Hermione owns a copy at home. It does not prove the book's exact Chamber contents. |
| `poa-ch09-001` — `sources/book-03/chapter-09-grim-defeat.yaml` | The book is cited for broad protective enchantments, including anti-intrusion and anti-Apparition protections. |
| `gof-ch11-005` — `sources/book-04/chapter-11-aboard-the-hogwarts-express.yaml` | It describes Hogwarts's concealment from Muggles and the ruin-like appearance presented to them. |
| `gof-ch15-003` — `sources/book-04/chapter-15-beauxbatons-and-durmstrang.yaml` | It covers the 1792 Triwizard judging disaster involving a cockatrice, but omits Hogwarts house-elf servitude. This is the clearest evidence of institutional blind spot or bias. |
| `gof-ch28-003` — `sources/book-04/chapter-28-the-madness-of-mr-crouch.yaml` | It explains that Muggle electrical/technical devices fail around Hogwarts because of the magical environment. |
| `ootp-ch17-002` — `sources/book-05/chapter-17-educational-decree-number-twenty-four.yaml` | It records a founders-era gendered dormitory rule, reinforced by the enchanted staircase. |
| `ootp-ch23-001` — `sources/book-05/chapter-23-christmas-on-the-closed-ward.yaml` | It is cited for the impossibility of Apparition or Disapparition inside Hogwarts. |
| `dh-ch06-004` — `sources/book-07/chapter-06-the-ghoul-in-pajamas.yaml` | Hermione takes her copy on the Horcrux hunt, showing personal reliance and portability; this says little about physical dimensions because enchanted luggage is involved. |
| `ext-b07-004` — `sources/external/interviews/b07-mugglenet-the-leaky-cauldron-interview.yaml` | Rowling describes Hermione as the character who reads the book and delivers exposition, unlike Harry and Ron. This is narrative-construction commentary, not in-universe content evidence. |

These references do **not** establish the author, publication year, number of editions, page count, exact length, or physical dimensions. The generated appendix displays B07 under “Unknown book, Unknown chapter” because it groups on book/chapter fields absent from external entries; the source identity itself is known.

Four of the ten explicit references render as `Corroboration` rather than `Direct evidence` in the main seed because the generated display label gives a populated `duplicate_of` higher precedence than explicit-reference type. Counts of explicit references must therefore use raw `reference_type`, not the presentation label.

## 8. Source corpus

### Primary canon and first-party sources

| Carrier/corpus | Availability and coverage | Current authority treatment |
|---|---|---|
| `pdfs/harrypotter.pdf` | 3,623 pages; all 198 chapters across seven novels processed into 1,314 entries. | Primary canonical narrative carrier. |
| `pdfs/quidditch-through-the-ages.pdf` | 65 pages; all 12 planned units processed into 37 entries. | Primary companion source, used where relevant to Hogwarts history and Quidditch. |
| `pdfs/Beedle The Bard_text.pdf` | 65 pages; all 7 planned units processed into 29 entries; one intentionally empty back-matter unit. | Primary companion source, selectively relevant. |
| `pdfs/Fantastic-Beasts-Where-to-Find-Them.pdf` | 65 pages, image-only; all 10 planned units visually processed into 61 entries. | Primary companion source; strong relevant material retained per bounded unit. |
| `resources/external/official-rowling/harrypotter-com/` | 37 complete Markdown snapshots, all processed into 161 entries. | Authority A, `official_rowling_original`; first-party authorial web material. |

All seven novels and all three locally available companion books are complete at their planned chapter/section granularity. The shorter companions naturally have fewer units and entries; Fantastic Beasts required visual rather than extracted-text review.

`pdfs/` also contains 20 extracted image assets from the companion books. They are auxiliary render/source aids, not independent evidence units.

### Preserved interviews and secondary/discovery sources

`resources/external/interviews/accio-quote/` contains 26 complete local transcript snapshots, all processed into 81 entries under `sources/external/interviews/`. They preserve Rowling statements but are assigned authority D, `preservation_transcription`, because the original broadcaster/publisher carrier was not verified. B05–B07 are three parts of one interview; B10 is a multi-page PotterCast interview. These snapshots must not be counted as independent corroboration of their missing originals.

Discovery sources—including Accio indexes, HP Lexicon, The Rowling Library, Leaky Cauldron, MuggleNet, and Wayback results—are treated as authority E discovery aids unless an actual primary or archival carrier is recovered. They normally do not contribute factual evidence directly.

Fifteen acquisition/audit items remain blocked in `project-control/remaining-source-units.yaml`, covering:

- Original publisher/broadcaster carriers for B01–B26.
- Old `jkrowling.com` captures.
- Three *Pottermore Presents* ebooks.
- Two later screenplays.
- Famous Wizard Cards and *Daily Prophet* newsletters.
- The 2008 prequel.
- A Lindsey Fraser interview book and a Rowling documentary.
- Archive completeness, date, and audio audits.

These are bibliography/backlog records, not incorporated evidence unless a corresponding current source YAML already exists from a lower-authority preservation carrier.

### Fan works and reconstruction references

`data/fanfic-hogwarts-history/source-registry.json` registers four approved non-canon references:

| Registry ID | Work/author | Available chapters | Priority/caution |
|---|---|---:|---|
| `HAH-FAN-001` | Unclebulgaria5 | 6 | High priority. |
| `HAH-FAN-002` | Paperback Reitter | 3 | Medium priority. |
| `HAH-FAN-003` | Scutie-Naos | 6 | High priority; narrative and invented-metaphysics warning. |
| `HAH-FAN-004` | manbigpog | 1 | Low priority. |

There is also one candidate requiring editorial review and one Hermione AU title-collision exclusion. The governing plan treats fan works only as style, structure, and coverage references. Repeated fan-created claims may never be promoted to canon without primary support.

No fan work has actually been captured into the local dataset: there are no work HTML snapshots, normalized chapters, rendered work PDFs, `manifest.jsonl`, validation report, or comparison index. Fan works are not part of the 1,683 canonical evidence entries.

## 9. Scripts and tooling

### Core evidence, query, validation, and generation tools

| Path | Input → output | Function | Writing-phase relevance |
|---|---|---|---|
| `scripts/source_files.py` | Repository tree → canonical source-file list | Shared discovery of book and external YAML. | Foundational. |
| `scripts/build_entry_index.py` | Canonical YAML → `entry-index.yaml`, `source-index.yaml` | Builds compact entry/source lookup data. | High. |
| `scripts/build_tag_index.py` | Canonical YAML → `tag-index.yaml` | Maps exact tags to entries and paths. | High. |
| `scripts/build_duplicate_index.py` | Canonical YAML → `duplicate-index.yaml` | Builds normalized duplicate/corroboration search data. | High. |
| `scripts/query_entries.py` | Entry index + filters → compact YAML results | Retrieves subject-, class-, source-, reference-, and confidence-filtered evidence. | Primary authoring-time locator. |
| `scripts/query_duplicates.py` | Duplicate index + tags/placement filters → ranked YAML | Finds likely repeated or corroborating claims. | Useful during synthesis. |
| `scripts/validate_source_yaml.py` | Sources, snapshots, schema values, generated files → pass/fail | Enforces structural integrity and external snapshot provenance. | Essential safeguard. |
| `scripts/generate_book_seed.py` | Canonical YAML + `book-seed-order.yaml` → main seed | Renders the full grouped evidence ledger. | Reference only; not prose generation. |
| `scripts/generate_appendices.py` | Sources, indexes, state, questions → six Markdown reports | Produces structure, explicit-reference, question, source, review, and statistics views. | Useful audit/report layer. |

### Extraction and runtime tools

| Path | Input → output | Function | Writing-phase relevance |
|---|---|---|---|
| `scripts/extract_pages.py` | Inclusive PDF range → combined/per-page text | Extracts text with `pypdf`; not useful for image-only pages. | Extraction legacy. |
| `scripts/update_next_run.py` | State, plan, chapter index, queue → updated state/plan/display | Advances PDF extraction and regenerates `next-run.md`. | Extraction legacy. |
| `scripts/complete_current_unit.py` | Current YAML + state → validated promotion/regeneration | Transactionally completes a PDF unit; restores finite artifacts on failure. | Extraction legacy. |
| `scripts/cleanup_tmp.py` | `.tmp/` → cleaned cache | Removes non-whitelisted temporary artifacts; supports dry-run. | Housekeeping only. |
| `scripts/check-cli-tools.sh` | Local PATH → tool/version report | Checks `rg` as required and `jq`/`just` as recommended. | General diagnostic. |

### External-source automation

| Path | Input → output | Function | Status |
|---|---|---|---|
| `scripts/external_sources/build_external_corpus.py` | Acquisition plan + HTML cache → snapshots + manifest | Builds provenance-preserving local external corpus. | Acquisition-only unless sources are refreshed/recovered. |
| `scripts/external_sources/queue.py` | Manifest, plan, staged YAML → queue transitions and canonical promotion | Lock-safe claim/current/release/block/complete workflow with regeneration. | Extraction legacy; queue exhausted. |
| `scripts/external_sources/artifact_snapshot.py` | Finite artifact set → byte snapshot/rollback | Transaction helper. | Runtime support only. |

### Partial fan-work tooling

Implemented modules under `scripts/fanfic_dataset/` include:

- `browser.py`: policy-aware Playwright capture with resume and diagnostics.
- `fanfiction_net.py` and `discover.py`: metadata/chapter discovery and adapter dispatch.
- `policy.py`: robots/crawl-delay decisions.
- `clean_html.py` and `html_to_markdown.py`: story extraction and normalized Markdown.
- `render_pdf.py` and `merge_pdf.py`: chapter rendering and complete reference-work PDF assembly.
- `models.py`, `paths.py`, and `registry.py`: strict contracts and paths.
- `build_manifest.py`: deterministic manifest/latest-pointer construction.
- `validate.py`: structural, integrity, content, and manual-review checks.
- `emit_schemas.py`: Pydantic-to-JSON-schema generation.

The durable development ledger records only tasks 1–6 complete; validation command integration, acquisition, comparison, and final reporting remain unfinished. There is no root fan-work `just` recipe and no promised `scripts/fanfic_dataset/cli.py`.

There is also no compiler for a final *Hogwarts: A History* manuscript, PDF, or EPUB. The fan-work `merge_pdf.py` compiles captured reference works only.

### Dependencies and environment

Core `requirements.txt` pins PyYAML 6.0.3, yamllint 1.37.1, pypdf 6.13.1, pathspec 1.1.1, and typing_extensions 4.15.0, and lists pytest, ruff, jsonschema, Jinja2, and rapidfuzz without pins. The observed `.venv` uses Python 3.9.6 and contains the first five; several of the unpinned packages were not installed there.

`requirements-fanfic.txt` and `.fanfic-venv` use Python 3.12 with BeautifulSoup, jsonschema, markdownify, Playwright, Pydantic, PyMuPDF, and pytest. Playwright Chromium is present. Repository workflows also use ripgrep, jq, just, Git, and Poppler. `yq` is absent by design.

`scripts/check-cli-tools.sh` does not check Python environments, Git, Poppler, Playwright, or Chromium even though the wider workflows use them. `just setup` installs only core requirements. `just test` runs the core unittest discovery path, not the pytest-oriented fan-work suite.

### Supported `just` recipes

There are 22 recipes:

| Recipe | Function | State effect |
|---|---|---|
| `default` | Lists recipes. | Read-only. |
| `tools` | Reports CLI availability/versions. | Read-only. |
| `setup` | Installs `requirements.txt` into `.venv`. | Mutating environment setup. |
| `next` | Prints `project-control/next-run.md`. | Read-only. |
| `status` | Shows repository root and current task display. | Read-only. |
| `search PATTERN` | Searches the repository with `rg`. | Read-only. |
| `validate` | Runs ordinary canonical validation. | Read-oriented. |
| `test` | Runs core `unittest` discovery. | Test run. |
| `indexes` | Rebuilds duplicate, entry/source, and tag indexes. | Regenerates files. |
| `generate` | Regenerates the book seed, appendices, and next-run display. | Regenerates files. |
| `post` | Indexes, validates, generates, cleans cache, and tests. | Mutating/regenerating. |
| `brief` | Compact status alias. | Read-only. |
| `clean-cache` | Removes disposable `.tmp` artifacts. | Mutating cleanup. |
| `advance-current` | Transactionally completes the current PDF unit. | Extraction state mutation. |
| `claim-external [agent] [unit]` | Claims the next or named external unit. | Queue mutation. |
| `current-external [unit]` | Shows active claims or one named unit. | Read-only. |
| `complete-external UNIT TOKEN` | Token-gated external completion/promotion. | Queue/source mutation. |
| `release-external UNIT TOKEN REASON` | Returns an interrupted claim to pending. | Queue mutation. |
| `block-external UNIT TOKEN REASON` | Marks a claimed unit blocked. | Queue mutation. |
| `external-status` | Prints compact queue counts and pointers. | Read-only. |
| `query-dupes TAGS...` | Returns ranked duplicate/corroboration candidates. | Read-only. |
| `query-entries TAG` | Returns compact evidence matches. | Read-only. |

## 10. Current editorial classifications

### Exact era values

- `original_book_core_candidate`: likely predates Harry and is plausibly part of the reconstructed original book. “Candidate” is important; it is not accepted prose.
- `pre_1984_historical_candidate`: older historical material that falls before the project's approximate cutoff. The repository does not define a sufficiently sharp conceptual boundary between this and `original_book_core_candidate`.
- `harry_era_confirmation`: a Harry-era observation that confirms an older feature or institution. It does not by itself date the feature's origin.
- `later_editorial_note`: useful in a fan edition but likely not part of the reconstructed original text.
- `post_1984_excluded_from_original`: an event clearly too late for the original-body cutoff.
- `unknown_or_uncertain`: unresolved era requiring review.

The exact stored field is `era_classification`. Values such as `original_book_candidate` and `pre_1984_institutional_history` do not occur as controlled values.

The schema's explanation of `later_editorial_note` uses “Bathilda-era text,” but the evidence does not establish Bathilda's authorship. Future writing should interpret the value operationally as “outside the reconstructed pre-cutoff original body,” pending an explicit authorship/edition decision.

### Other independent axes

- `reference_type` describes the kind of evidence: historical claim, architecture, institution, rule, explicit source mention, direct observation, weak context, and so on.
- `confidence` describes support and placement certainty.
- `duplicate_check` describes overlap/corroboration.
- `candidate_part`, `candidate_chapter`, and `candidate_section` describe tentative destinations.
- `limitations` records local caution.
- External `authority` describes carrier/source reliability.

These axes must not be collapsed. A high-confidence Harry-era observation can still be unsuitable for the original body; a duplicate can be valuable corroboration; an official external source can still be later than the cutoff.

### Generated presentation labels

The main seed derives four display labels with this precedence:

1. A populated `duplicate_of` → `Corroboration`.
2. Otherwise `explicit_hogwarts_a_history` → `Direct evidence`.
3. Otherwise later/post-cutoff/unknown era → `Context`.
4. Everything else → `Supporting evidence`.

Current rendered totals are 1,047 Corroboration, 371 Supporting evidence, 259 Context, and 6 Direct evidence. These are display labels, not canonical entry types. There are ten raw explicit-title references; four display as Corroboration because duplicate status wins.

### Effect on future writing

- Original-core and pre-1984 candidates may feed the reconstructed body only after editorial selection and chronology review.
- Harry-era confirmations support continuity but should not be voiced as original historical knowledge without older support.
- Later editorial notes belong in clearly differentiated later apparatus if that edition model is selected.
- Post-1984 exclusions must not enter the original voice.
- Unknown-era and low-confidence material requires explicit disposition.
- Authority-D transcripts need source-critical treatment and should not outweigh primary carriers merely because the statement is convenient.
- Possible duplicates should be synthesized or used as corroboration, not copied as multiple independent claims.

There is no separate master exclusion list. Exclusion-like status is distributed across era, `weak_context_only`, authority, limitations, and local notes.

## 11. Chronology

There is no master timeline and no structured event-date schema.

The only universal chronological field is the coarse six-value `era_classification`. Exact years, centuries, ranges, and uncertain dates appear opportunistically inside `source_note`, `limitations`, candidate labels, or free-form tags such as `1689`, `1792`, `eighteenth-century`, or named historical periods. They are not normalized.

`processed_date` is the extraction date, not the date of the event. An external `publication_date` is the carrier's publication date, not necessarily the event date or the date the information became true.

Uncertainty is handled through:

- `unknown_or_uncertain` era classification: 22 entries.
- `low` confidence: 23 entries.
- Entry-level `limitations` and source notes.
- The structured question backlog.
- Generated review flags.

The 22 unknown-era and 23 low-confidence sets do not overlap, so the generated question view adds 45 dynamic data-quality rows beyond the 386 structured questions.

There is no chronology validator, exact-date query index, consistency checker, or compiled contradiction register. Some source-critical conflicts are recorded locally—for example Binns's denial versus the Chamber's reality, Riddle's self-interested diary testimony, and Doge's memorial account versus Skeeter's biography—but they are not normalized into a system-wide chronology model.

This creates several authoring hazards:

- A repeated Harry-era observation may be mistaken for proof that a feature existed before 1984.
- Search by exact date requires free-text/tag discovery and may miss synonyms or unlabeled dates.
- Historical candidates have no standardized start/end range or uncertainty precision.
- `original_book_core_candidate` and `pre_1984_historical_candidate` lack a fully explicit boundary.
- 706 later editorial notes and 42 post-cutoff exclusions substantially outnumber the 359 original-core plus pre-1984 candidates; an unfiltered seed will therefore distort the original-body voice.
- Carrier publication dates can be confused with in-universe event dates.
- Contradictions must currently be recognized and adjudicated manually.

## 12. Current open questions and unresolved issues

The canonical question store is `project-control/structured-sources/open-questions.yaml`; `appendix/generated/open-questions.md` is its human-readable view plus dynamic review rows.

There are 386 unique structured questions, all still `open`, across 16 topic values. Of these, 382 were migrated from a former appendix and only four were created directly from source processing. Only four questions have `related_entries`, totaling eight links, so most questions are not machine-linked to the evidence that motivated them.

Grouped counts:

| Group | Questions | Main unresolved themes |
|---|---:|---|
| Founding and Sorting | 11 | Exact founding date, founder-source reliability, Chamber legend status, early house/sorting practice. |
| Great Hall, castle architecture, and rooms | 45 | Dating stairs, doors, portraits, rooms, concealments, routes, and architectural changes. |
| Ghosts and house-elves | 17 | Resident histories, institutional labor, whether private-family elf rules apply to Hogwarts, and the book's omission. |
| Curriculum and staffing | 35 | Curriculum stability, teacher-specific practices, exams, appointments, accommodations, and date ranges. |
| Quidditch | 18 | Season structure, equipment, refereeing, rule history, and institutional operation. |
| Library and named sources | 18 | Provenance, restricted access, copy availability, and source reliability. |
| Rules and discipline | 32 | Authority, enforcement, permanence, exceptions, and historical development. |
| Pre-Hogwarts historical context | 54 | Date reliability, relevance, source bias, and boundary between world history and school history. |
| Feasts and traditions | 38 | Origins, continuity, exact dates, and special events. |
| Protective magic, security, and governance | 117 | Apparition/entry protections versus known breaches, authority relationships, Chamber testimony, concealment, and policy changes. |
| Source processing | 1 | Stability of PDF locators. |

High-value specific issues include:

- Whether the Chamber legend is actually covered in *Hogwarts: A History* or students merely expect it to be.
- Exact founding date and the reliability of later accounts.
- Which secret-route and Marauder's Map facts existed before the cutoff versus being later discoveries.
- Dating moving staircases, vanishing steps, doors, portraits, armor, rooms, and concealment mechanisms.
- Reconciling broad anti-Apparition/anti-intrusion descriptions with secret passages and Animagus entry.
- Reconciling Binns's denial of the Chamber with its demonstrated existence.
- Treating Riddle's diary as self-interested magical testimony rather than neutral history.
- The omission of house-elf servitude and what it implies about institutional perspective.
- Curriculum stability, staffing dates, and the line between general policy and one teacher's practice.
- Quidditch operations and historical rule development.
- Named-source and restricted-library provenance.
- Dating the Mirror of Erised before the cutoff.
- Allocation of authority among headmaster, governors, Ministry, families, and outside committees.
- The date of the banned Dippet-era pantomime.
- Long-term stability of PDF page locators.

The generated appendix adds 45 low-confidence/unknown-era rows not present in canonical question YAML. Conversely, it omits structured IDs, statuses, and source fields, repeats one heading because it preserves YAML order, and is less suitable for precise tracking. Use the YAML for status work and the generated file for browsing.

Additional unresolved corpus issues include the 15 blocked acquisitions, the 1,050 possible-duplicate flags, 99 external duplicate rankings that became stale as the corpus grew, four tag-count strict failures, three incomplete duplicate targets, the one repeated chapter-range inconsistency, and the lack of any master contradiction register.

## 13. Readiness for writing

### What is ready

- A complete planned corpus of 290 structured source units and 1,683 uniquely identified entries.
- Full planned coverage of all seven novels and the three local companion books.
- Full extraction of all 63 acquired external snapshots.
- Precise source paths and PDF/snapshot locators, plus strong external hash provenance.
- Controlled reference, era, and confidence values.
- Queryable tag, source, entry, and duplicate indexes.
- Normal validation that passes and a core test suite with 66 passing tests.
- Checked-in derived files that currently match canonical inputs.
- A compact explicit-reference appendix that constrains known contents, omissions, reputation, and use of the in-universe book.
- A preserved structured backlog of 386 open questions.
- Transactional extraction completion workflows if source processing resumes.

### What is missing

- An approved final book outline. The current ordering file is provisional and covers only a minority of exact placements.
- A writing-specific runtime or authoring contract. The current runtime is extraction-only and prohibits drafting.
- A resolved edition model: pre-1984 reconstruction, later annotated edition, or both.
- An explicit decision about authorship and narrator voice; Bathilda authorship is not established.
- A chapter-brief format and a claim-selection/synthesis policy.
- Rules for citations, notes, attribution, source authority, and handling authority-D interview material.
- A contradiction-resolution and historiographical policy.
- Consolidation of 197 candidate part labels and the wider chapter/section taxonomy.
- A normalized chronology or timeline.
- Editorial disposition of 386 questions, 1,050 possible duplicates, 748 later/post-cutoff records, and the small strict-validation backlog.
- Per-chapter completeness criteria and a method for declaring evidence gaps.
- Voice/style guidance separated from canon evidence.
- A final manuscript/PDF/EPUB compiler.

### What should be preserved

- All canonical `sources/**/*.yaml` files and evidence IDs.
- All local PDFs, external snapshots, and `resources/manifests/external-sources.yaml`.
- The six era classifications and the separation among reference type, confidence, authority, placement, and duplication.
- Exact locators, text anchors, limitations, and source notes.
- `project-control/structured-sources/open-questions.yaml`.
- `project-control/book-seed-order.yaml` as prior editorial work, clearly labeled provisional.
- Index builders, compact query tools, validators, and report generators.
- Generated audit appendices, especially the explicit-reference appendix and review flags.
- The house-elf omission and other evidence about the in-universe book's limitations.
- Compact background and schema references.

### Extraction-era baggage

The following should remain available for provenance or renewed extraction, but should not be loaded into every future authoring run:

- `docs/instructions/runtime-contract.md`.
- `project-control/processing-state.yaml`, `source-plan.yaml`, `next-run.md`, and queue-transition instructions.
- `scripts/extract_pages.py`, state advancement, queue claim/complete/release/block workflows, and `.tmp` procedures.
- Archived seed-builder prompts and obsolete next-run snapshots.
- Historical implementation plans/specifications and `.superpowers/sdd/` ledgers.
- The obsolete “Emerging Parts” model.
- The 1.87 MB main seed and 107 KB alphabetical structure seed as whole-context inputs.
- Historical acquisition reports with pre-extraction counts.
- Treating all 197 extraction-era part labels as real architecture.

This is a loading recommendation, not a recommendation to delete those files.

## 14. Recommended context package for a chapter-writing agent

### Always load

| Path | Why |
|---|---|
| `docs/instructions/background-guide.md` | Compact project scope, evidence rules, cutoff, and inclusion logic. Its extraction-era no-drafting statement would need to be explicitly superseded by a future authoring task. |
| `docs/instructions/schema-reference.md` | Required to interpret classifications, confidence, duplicate metadata, and tentative placement correctly. |
| `project-control/book-seed-order.yaml` | The only deliberate current ordering seed; load with an explicit “provisional, incomplete” warning. |
| `appendix/generated/explicit-hogwarts-a-history-references.md` | Small hard-constraint set for known content, omissions, reputation, use, and uncertainty. |

These four files total roughly 21 KB and provide the best compact common baseline available today.

### Load as needed

- Exact `sources/...yaml` files returned by a subject query.
- The cited PDF page or external Markdown snapshot when wording/provenance matters.
- `appendix/generated/project-stats.md` for corpus-wide orientation.
- `chapters-index.md` when checking PDF boundaries.
- `project-control/structured-sources/open-questions.yaml`, filtered to the relevant topic or IDs.
- `project-control/remaining-source-units.yaml` and `resources/external/unresolved/discovery-backlog.md` when discussing corpus completeness.
- `resources/manifests/external-sources.yaml` when evaluating external authority or carrier provenance.
- `docs/instructions/runtime-contract.md` only if renewed extraction is part of the task.
- `data/fanfic-hogwarts-history/source-registry.json` and the fan-work plan only for explicit non-canon style/structure study.

### Query; do not load wholesale

- `project-control/entry-index.yaml` — approximately 996 KB.
- `project-control/tag-index.yaml` — approximately 876 KB.
- `project-control/duplicate-index.yaml` — approximately 1.07 MB.
- `project-control/source-index.yaml` — approximately 140 KB.
- `book-seed/hogwarts-a-history-seed.md` — approximately 1.87 MB.
- `appendix/generated/book-structure-seed.md` — approximately 107 KB.
- `appendix/generated/open-questions.md` — approximately 104 KB.
- `appendix/generated/review-flags.md` — approximately 804 KB.
- The complete `sources/` tree, source PDFs, and external snapshots.

Use `query_entries.py` and `query_duplicates.py` to narrow evidence first. There is no dedicated open-question query command, so questions must currently be filtered by targeted YAML/text search.

## 15. Machine-readable inventory

| Path | Type | Purpose | Active? | Writing-phase relevance |
|---|---|---|---|---|
| `docs/instructions/background-guide.md` | Markdown reference | Scope, cutoff, inclusion rules, common tentative parts | Conditional | Critical |
| `docs/instructions/schema-reference.md` | Markdown schema reference | Defines source/entry fields and controlled values | Conditional; validator dependency | Critical |
| `docs/instructions/runtime-contract.md` | Markdown runtime | One-unit extraction dispatcher | Yes | Extraction legacy |
| `docs/instructions/hogwarts-history-seed-builder.md` | Markdown redirect | Redirects legacy entry point to runtime | Yes | Extraction legacy |
| `project-control/processing-state.yaml` | YAML state | Authoritative extraction pointers and runtime references | Yes; exhausted | Extraction legacy |
| `project-control/source-plan.yaml` | YAML ledger | Per-unit completion and external queue record | Yes; stale phase label | Useful |
| `project-control/remaining-source-units.yaml` | YAML backlog | Blocked acquisitions/audits and legacy unit identifiers | Yes | Useful |
| `project-control/next-run.md` | Generated Markdown | Compact next-work display | Yes/generated | Extraction legacy |
| `chapters-index.md` | Markdown index | Source-PDF chapter/unit page ranges | Yes | Useful |
| `sources/book-*/*.yaml` | Canonical YAML evidence | Book and companion source units and entries | Yes | Critical |
| `sources/external/**/*.yaml` | Canonical YAML evidence | External entries linked to snapshots | Yes | Critical |
| `resources/external/**` | Markdown source corpus | Local official/interview snapshots and unresolved aids | Yes | Critical when cited |
| `resources/manifests/external-sources.yaml` | YAML manifest | External authority, provenance, URLs, and hashes | Yes | Critical for external claims |
| `project-control/entry-index.yaml` | Generated YAML index | Compact entry metadata for filtered lookup | Yes/generated | Useful |
| `project-control/tag-index.yaml` | Generated YAML index | Exact tag-to-entry lookup | Yes/generated | Useful |
| `project-control/duplicate-index.yaml` | Generated YAML index | Duplicate/corroboration candidate lookup | Yes/generated | Useful |
| `project-control/source-index.yaml` | Generated YAML index | Source-unit metadata lookup | Yes/generated | Useful |
| `project-control/book-seed-order.yaml` | YAML editorial seed | Provisional ordered parts/chapters/sections | Yes | Critical but provisional |
| `project-control/structured-sources/open-questions.yaml` | Canonical YAML backlog | 386 unresolved editorial/research questions | Yes | Critical |
| `book-seed/hogwarts-a-history-seed.md` | Generated Markdown | Full grouped evidence ledger | Yes/generated | Reference only |
| `appendix/generated/book-structure-seed.md` | Generated Markdown | Alphabetical inventory of tentative destinations | Yes/generated | Reference only |
| `appendix/generated/explicit-hogwarts-a-history-references.md` | Generated Markdown | Ten explicit title references | Yes/generated | Critical |
| `appendix/generated/open-questions.md` | Generated Markdown | Browsable question and review view | Yes/generated | Useful |
| `appendix/generated/review-flags.md` | Generated Markdown | Quality, era, duplicate, and heuristic review filters | Yes/generated | Useful; query selectively |
| `appendix/generated/project-stats.md` | Generated Markdown | Corpus distributions and status summary | Yes/generated | Useful |
| `scripts/query_entries.py` | Python CLI | Filtered evidence retrieval | Yes | Critical |
| `scripts/query_duplicates.py` | Python CLI | Ranked overlap/corroboration retrieval | Yes | Useful |
| `scripts/validate_source_yaml.py` | Python validator | Structural and external-provenance validation | Yes | Critical |
| `scripts/build_*_index.py` | Python generators | Rebuild derived indexes | Yes | Useful |
| `scripts/generate_book_seed.py` | Python generator | Rebuild full evidence seed | Yes | Generated/reference only |
| `scripts/generate_appendices.py` | Python generator | Rebuild six audit appendices | Yes | Useful |
| `scripts/extract_pages.py` | Python extraction tool | Extracts text from PDF ranges | Yes | Extraction legacy |
| `scripts/external_sources/queue.py` | Python runtime | Transactional external queue/promotion | Yes; queue exhausted | Extraction legacy |
| `docs/instructions/archive/**` | Archived Markdown | Superseded extraction contracts and seed builders | No | Extraction legacy |
| `docs/superpowers/**` | Plans/specifications | Implementation history | No | Reference only |
| `data/fanfic-hogwarts-history/source-registry.json` | JSON registry | Approved non-canon reference works | Partial | Reference only |
| `scripts/fanfic_dataset/**` | Python library | Partial capture/normalization/render/validation pipeline | Partial | Reference only |

## 16. Final handoff summary

# What another model needs to know before designing the authoring system

1. The repository contains 1,683 uniquely identified evidence entries across 290 source units; canonical truth lives in `sources/**/*.yaml`.
2. All seven novels, all three local companion books, and all 63 acquired external snapshots are processed at their planned granularity.
3. Ordinary validation passes and 66 core tests pass, but strict validation has seven known legacy failures: four tag-count and three incomplete duplicate-target records.
4. The four generated indexes, main seed, and six generated appendices currently match canonical inputs; they are reproducible views, not sources of truth.
5. Provenance is strong: entries point to exact PDF pages/anchors or hashed local external snapshots with manifest URLs and authority metadata.
6. External authority is not uniform: 37 official documents are authority A; 26 Accio Quote preservation transcripts are authority D and are not verified original carriers.
7. The extraction queue is complete, but 15 unavailable or unverified source acquisitions/audits remain recorded as blocked.
8. The repository has no approved book outline. `project-control/book-seed-order.yaml` is a real but incomplete 14-part ordering seed; most exact entry placements fall outside it.
9. `book-seed/hogwarts-a-history-seed.md` is a 1.87 MB evidence ledger, not prose. `appendix/generated/book-structure-seed.md` is an alphabetical category inventory, not narrative architecture.
10. Candidate placement vocabulary has drifted to 197 part labels, 711 part/chapter pairs, and 1,536 exact triples; taxonomy consolidation is a prerequisite for dependable chapter assembly.
11. Ten explicit title references constrain known book contents and use. They establish several subjects, student demand/reliance, and a major omission—house-elf servitude—but not author, publication year, size, or edition history.
12. Bathilda Bagshot's authorship of *Hogwarts: A History* is not established. Active material uses 1984 only as an approximate editorial cutoff, not a publication fact.
13. Era, reference type, confidence, source authority, tentative placement, and duplication are separate axes and must remain separate in any authoring pipeline.
14. The corpus contains 706 later editorial notes, 42 post-1984 exclusions, 554 Harry-era confirmations, and only 359 original-core/pre-1984 candidates. Unfiltered generation would badly blur the intended historical voice.
15. There is no master timeline, normalized event-date field, chronology validator, or contradiction register. Chronological coherence currently requires manual source-critical work.
16. There are 386 open structured questions, 1,050 possible-duplicate flags, 45 low-confidence/unknown-era review items, and a small set of validation/provenance discrepancies needing editorial disposition.
17. Compact subject retrieval already exists through `just query-entries`, `query_entries.py`, and `just query-dupes`; a writing agent should query first and load only cited YAML/carrier excerpts.
18. The active runtime is extraction-only and expressly avoids drafting. A future writing system will need its own authority, edition, chapter-brief, citation, contradiction, voice, and completeness rules.
19. The current source data, IDs, locators, manifests, classifications, questions, validators, queries, and audit appendices are valuable infrastructure and should be preserved rather than rebuilt casually.
20. Fan-work support is partial and non-canonical: a registry and library modules exist, but no fan works have been captured or incorporated into the evidence corpus.
