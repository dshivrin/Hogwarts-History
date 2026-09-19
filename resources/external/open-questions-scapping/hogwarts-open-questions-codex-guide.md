# Open-questions editorial overlay

The live `hogwarts-open-questions-enriched.yaml` is an ID-keyed editorial overlay for all 386 canonical questions. It does not replace the canonical question store or authorize manuscript changes.

## Authorities

Paths below are relative to the repository root:

- `project-control/structured-sources/open-questions.yaml`: authoritative IDs, wording, topics, original status, tags, source notes, and related entries. Read-only for overlay work.
- `authoring/editions/1984/table-of-contents.yaml`: authoritative twenty-chapter destinations, purposes, and boundaries.
- `project-control/entry-index.yaml`: evidence-ID discovery and pointers to exact canonical `sources/**/*.yaml` records. Read the records and their limitations before asserting a fact.
- `resources/manifests/external-sources.yaml`: external-source identity, authority, original URLs, and local snapshots.
- `project-control/source-index.yaml`: processed local PDF units and their evidence paths.
- `authoring/editions/1984/` and `authoring/shared/`: edition policy and chapter workflow. Read applicable authoring instructions before drafting.

The dated legacy backups are migration inputs, not evidence. Their source leads and old thematic destinations are not authorities.

## Retrieve one chapter

From the repository root:

```bash
.venv/bin/python scripts/open_questions_overlay.py query --chapter 5
```

The query returns primary **and secondary** matches, joins canonical question wording and topic, and includes research, gap, placement, and interpretation fields. A destination supports retrieval; it does not grant body eligibility. Excluded items remain visible for omission awareness. Avoid repeating the same material in every matching chapter.

## Actual record shape

`questions` maps each unchanged canonical ID to exactly four fields:

- `research`: `status`, `verified_facts` (each with `statement` and exact `evidence_ids`), `local_source_ids`, `external_candidate_ids`, `query_tags`, and a concrete `next_action`.
- `gap`: `status` and `residual_question`.
- `placement`: `primary_chapter_id` and `secondary_chapter_ids`, using only outline IDs 1–20.
- `interpretation`: `body_eligibility`, `author_question`, `historical_inference`, `creative_reconstruction`, and a cautionary `note`.

`local_source_ids` are sources to inspect first, **not a log of completed searches**. The P-prefixed catalog keys are corpus aliases whose actual paths resolve through the local inventory; A-prefixed keys are canonical external manifest logical IDs. External candidates have `availability: candidate_unverified` and no canonical source ID. Their URLs cannot support a verified fact until normal ingestion assigns an evidence ID.

Supported research statuses are `local_search_required`, `partially_answered`, `answered_with_access_gap`, `answered_later_context`, `excluded`, and `repository_only_resolved`. Gap statuses respectively distinguish `not_yet_reviewed`, `actual_gap`, `no_residual_gap`, `excluded_from_manuscript`, and `repository_only`. Do not introduce an unsupported status in a hand edit; extend the builder, validator, and tests deliberately when a new disposition is needed.

## Local-first research

1. Read the canonical question and related entries, overlay facts, residual question, and cited evidence limitations.
2. Search the compact entry index with `query_tags`, using `just query-entries TAG` and `just query-dupes TAGS`.
3. Follow exact evidence IDs to canonical YAML and inspect `local_source_ids`.
4. Check the corresponding existing snapshots and PDFs. Do not download or re-extract already available material.
5. Investigate `external_candidate_ids` only if that local review leaves a specific residual gap. An unverified URL is a lead, never an inspected source.
6. Ingest usable external evidence through the normal evidence pipeline before referencing its new ID here.

Record reproducible negative searches and editorial outcomes in the existing chapter `evidence-gaps.md` or `evidence-selection.yaml` workflow when conducting authoring work. A quick failed search does not establish absence from the corpus. This overlay implementation does not modify those artifacts.

## Partial answers and interpretation

Preserve the supported portion as a verified fact with exact evidence IDs. Narrow `gap.residual_question` to what remains unresolved; every partial answer must retain a non-empty residual. Do not merge or delete duplicates, answered questions, excluded questions, or repository-control questions.

For example, the Sorting Hat's founder-era origin is supported by `ext-a02-001`; the beginning of its later ceremonial form remains a separate question. For admissions, `ext-a03-004/005` explain the Book's evidentiary threshold and Neville's delayed acceptance; addresses and first-contact logistics remain unresolved.

Verified facts contain only supported assertions, with attribution where the evidence is testimony or tradition. `historical_inference` and `creative_reconstruction` are separate **non-canonical eligibility assessments**, not established conclusions. `author_question: eligible` permits consideration of explicit uncertainty after access review; it does not turn an unanswered question into a fact.

Creative reconstruction is restricted to rhetorical framing and bounded interpretation under edition policy. Never invent an event, actor, custom, procedure, motive, source, quotation, date, office, law, school rule, spell, or witness to fill a gap. `candidate_after_editorial_review` still requires a human editorial decision. Questions may remain unanswered.

House-elf IDs remain excluded from manuscript use. `source-processing-001` is repository control work and must never become narrative material.

## Three different dates

An **event date** locates what happened. A **witness date** locates when someone described it. A **narrator-access date** concerns when the circa-1984 historian could plausibly know it. These are separate research questions: later testimony about an earlier event does not prove earlier narrator access. Modern authorial commentary can settle editorial facts without making them available to the in-world historian.

The overlay records conservative body eligibility, not invented date values. Before drafting, establish the three dates or their uncertainty from the cited evidence in the existing chapter evidence-selection workflow. `requires_access_review` is not body approval. `later_context_only` material cannot be imported into the original body merely because its event predates 1984. The Mirror's modification is documented without asserting an exact year absent from the cited record.

## Update one record reproducibly

The live overlay is generated. To update a reviewed question, edit its ID-specific entry in `REVIEWED` in `scripts/open_questions_overlay.py`, keeping assertions and evidence IDs separate from its residual question. Placement corrections belong in `CHAPTER_OVERRIDES`; source mappings belong in the source-catalog builder. Add a focused regression test before changing behavior. Do not change canonical question wording or edit the dated backups.

Rebuild from the immutable dated input:

```bash
.venv/bin/python scripts/open_questions_overlay.py migrate \
  --legacy resources/external/open-questions-scapping/hogwarts-open-questions-enriched.pre-restructure-2026-09-18.yaml
just validate-open-questions
just validate
just test
git diff --check
```

Review the generated change for the intended ID and any deliberate source-catalog correction. A direct edit to the generated YAML is temporary and will fail deterministic rebuild tests. A record requiring a new disposition must receive a deliberate builder/validator/test extension first.

Validation rejects missing/reordered IDs, duplicate YAML keys, stale canonical metadata, invalid evidence/source/chapter references, unsupported statuses, empty partial residuals, and violations of exclusion controls. The suite verifies equivalent rebuild data and backup hashes. Machines check references and structure; human review must still judge whether the cited passage supports the precise assertion and whether the narrator could know it.

## Preserved inputs

The backups match the pre-restructure originals byte for byte:

| Backup | SHA-256 |
|---|---|
| `hogwarts-open-questions-enriched.pre-restructure-2026-09-18.yaml` | `96424a5640b3e22ba03672d5dd28f52eb867e9d905f86ebd604a7229d2d6cb3a` |
| `hogwarts-open-questions-codex-guide.pre-restructure-2026-09-18.md` | `5b29d22d711b0b9934e35c0a49e017de1868e97374085258bafe05b1557227d5` |
