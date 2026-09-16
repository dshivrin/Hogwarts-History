# Fantastic Beasts Remainder Automation Design

**Date:** 2026-09-11
**Status:** Approved in conversation for implementation
**Scope:** Queue and process the locally available *Fantastic Beasts and Where to Find Them* PDF one bounded unit per automation run, while preserving completed work and keeping unacquired material visibly blocked.

## Purpose

The completed queue covers 217 book/companion PDF units and 63 acquired external-source units. It does not cover the local scanned PDF `pdfs/Fantastic-Beasts-Where-to-Find-Them.pdf`, and it must not represent unresolved acquisition candidates as readable sources.

This design reopens the PDF queue for ten bounded *Fantastic Beasts* units. It preserves the completed plan byte-for-byte, leaves every existing result unchanged, and reuses the project's canonical YAML, indexes, appendices, and generated book-seed pipeline.

## Preservation Rules

Before modifying active controls:

1. Copy `project-control/source-plan.yaml` byte-for-byte to `project-control/archive/source-plan-completed-2026-08-24.yaml`.
2. Copy the completed external runtime contract byte-for-byte to `docs/instructions/archive/runtime-contract-external-source-extraction-completed-2026-09-11.md`.
3. Verify both copies with `cmp` and SHA-256.

No existing source YAML, external snapshot, completed queue record, index history, or generated result is deleted or rewritten as source data.

## Ready Extraction Queue

Append one source family to the existing `sources` sequence:

| ID | Title | Inclusive PDF pages | Output |
|---|---|---:|---|
| FB00 | Front Matter, Contents, Author, and Foreword | 1–8 | `sources/book-fb/chapter-00-front-matter-contents-and-foreword.yaml` |
| FB01 | About This Book and What Is a Beast? | 9–13 | `sources/book-fb/chapter-01-about-this-book-and-what-is-a-beast.yaml` |
| FB02 | A Brief History of Muggle Awareness of Fantastic Beasts | 14–15 | `sources/book-fb/chapter-02-muggle-awareness-of-fantastic-beasts.yaml` |
| FB03 | Magical Beasts in Hiding | 16–20 | `sources/book-fb/chapter-03-magical-beasts-in-hiding.yaml` |
| FB04 | Why Magizoology Matters and Ministry Classifications | 21–22 | `sources/book-fb/chapter-04-magizoology-and-ministry-classifications.yaml` |
| FB05 | A–C Bestiary Entries | 23–30 | `sources/book-fb/chapter-05-bestiary-a-to-c.yaml` |
| FB06 | D–H Bestiary Entries | 31–43 | `sources/book-fb/chapter-06-bestiary-d-to-h.yaml` |
| FB07 | I–Q Bestiary Entries | 44–56 | `sources/book-fb/chapter-07-bestiary-i-to-q.yaml` |
| FB08 | R–Z Bestiary Entries | 57–64 | `sources/book-fb/chapter-08-bestiary-r-to-z.yaml` |
| FB09 | Back Matter | 65 | `sources/book-fb/chapter-09-back-matter.yaml` |

The unit IDs are stable plan identifiers. Canonical entry IDs use `fb-chNN-NNN`.

## State Model

The existing PDF state keys remain authoritative:

- `current_source_unit`: the only unit an automation run may process.
- `next_source_unit`: a preview of the next pending unit.
- `last_completed_source_unit`: the latest successfully advanced PDF unit.

At activation:

- FB00 is `in_progress` and is `current_source_unit`.
- FB01 is `pending` and is `next_source_unit`.
- FB02–FB09 are `pending`.
- all pre-existing 217 PDF and 63 external units remain `complete`/`done`.

Advancement validates the current canonical YAML before changing state, marks exactly the current plan row complete, promotes exactly the next pointer, computes one later preview from the ordered source plan, and stops. FB09 may complete with both current and next set to null.

## Scanned-PDF Reading Contract

The PDF has no useful embedded text layer. A routine worker must not treat an empty `pypdf` extraction as an empty source.

For the current unit only, the worker:

1. renders the inclusive page range to `.tmp/current-source-images/` with Poppler;
2. visually reads every rendered page in the range;
3. extracts all explicit *Hogwarts: A History* references plus the strongest three to seven relevant supporting entries, allowing zero supporting entries when a unit contains no relevant evidence;
4. uses `pdf_page` and a local `text_anchor` for locators;
5. runs indexed duplicate queries and opens only returned candidate YAML files;
6. writes only the assigned `sources/book-fb/...yaml` source result;
7. validates/regenerates the project, advances once, commits the completed unit, and ends the run.

The worker must never render or inspect pages outside the current range during a normal run.

## Runtime Dispatch

The active runtime contract becomes a small dispatcher:

- If `current_source_unit` is present, run the bounded PDF workflow.
- Otherwise, if the external queue has a pending unit, run the existing external claim workflow.
- Otherwise, report that no ready unit remains and list the structured acquisition backlog as blocked work.

The current project state selects the first branch. External results remain valid and untouched.

## Acquisition Backlog

Create `project-control/remaining-source-units.yaml` as a structured companion to `resources/external/unresolved/discovery-backlog.md`. It separates:

- ready extraction units (FB00–FB09), represented authoritatively in `source-plan.yaml`;
- original-carrier recovery for B01–B26;
- old J.K. Rowling website recovery;
- E01–E10 published/physical source acquisition;
- external-corpus completeness audits.

Every unacquired item is `blocked`, includes the exact unblock condition, and lists which manifest, carrier, queue, or provenance fields must be updated after lawful acquisition. Blocked acquisition work is not auto-promoted into the extraction queue.

## Automation Behavior

Update the existing `Hogwarts history` scheduled task rather than creating a duplicate. Preserve its project, local execution environment, cadence, model, and reasoning effort; replace only its instructions and set it active.

Each invocation must:

1. process no more than one ready unit;
2. stop on validation, rendering, schema, or duplicate uncertainty;
3. never skip the current pointer;
4. never begin the displayed next unit in the same invocation;
5. report source pages read, output path, entries created, validation, commit, and the next pointer.

## Verification

The implementation is acceptable when:

- both backups compare byte-for-byte with their pre-change originals;
- the ten FB units and their page ranges parse from YAML;
- the first state pointer is FB00 and the preview is FB01;
- the renderer prefers a current PDF unit over an exhausted external queue;
- plan-driven advancement supports `book-fb` and the final null-next transition;
- the validator and source index accept `book-fb` and produce `fb-chNN` identifiers;
- all tests and `just validate` pass;
- the existing automation is active with the one-unit stop rule.
