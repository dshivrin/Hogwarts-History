# External Source Extraction Automation Design

**Date:** 2026-08-15
**Status:** Design approved in conversation; awaiting written-spec review
**Scope:** Process all 63 acquired external source snapshots into the existing canonical Hogwarts evidence pipeline.

## Purpose

Replace the exhausted book-and-companion extraction runtime with a resumable, concurrency-safe automation workflow for the external corpus. The new workflow must process one acquired snapshot per unit, preserve provenance, perform indexed duplicate checks, write canonical evidence YAML, and update the same indexes and generated outputs used by the existing project.

This design does not draft final book prose, change the historical cutoff, collapse duplicate evidence, or acquire new source carriers.

## Existing State

- The book and companion queue in `project-control/source-plan.yaml` is complete.
- `project-control/processing-state.yaml` has no current or next unit.
- The canonical evidence pipeline reads `sources/book-*/*.yaml` and generates indexes, appendices, and `book-seed/hogwarts-a-history-seed.md`.
- The external corpus contains 63 Markdown snapshots registered in `resources/manifests/external-sources.yaml`:
  - A01-A37: 37 official HarryPotter.com Rowling originals.
  - B01-B26: 26 Accio Quote preservation transcripts.
- Existing compact lookup files already prevent broad dataset scans:
  - `project-control/entry-index.yaml`
  - `project-control/duplicate-index.yaml`
  - `project-control/tag-index.yaml`
  - `project-control/source-index.yaml`

## Chosen Architecture

Use one integrated automation controller rather than a parallel external-only controller.

1. Preserve the current active runtime contract byte-for-byte at:

   `docs/instructions/archive/runtime-contract-book-and-companion-extraction-2026-08-15.md`

2. Replace `docs/instructions/runtime-contract.md` with the external-source runtime contract.
3. Preserve all completed book history in `project-control/source-plan.yaml` and append an `external_sources` queue containing exactly 63 units.
4. Make `project-control/processing-state.yaml` point to the external phase while retaining the last completed companion unit as historical context.
5. Store external evidence YAML separately from acquired snapshots:

   ```text
   sources/external/
     official-rowling/
     interviews/
   ```

6. Extend the existing evidence discovery layer so every validator, index builder, query tool, appendix generator, and book-seed generator reads both:

   ```text
   sources/book-*/*.yaml
   sources/external/**/*.yaml
   ```

7. Centralize source-file discovery in one helper rather than duplicating glob rules across scripts.

## Unit Model

Each manifest record becomes one independently claimable work unit. A unit contains:

```yaml
id: A01
title: Chamber of Secrets
source_kind: external_markdown
source_class: official_rowling_original
authority: A
input_path: resources/external/official-rowling/harrypotter-com/a01-chamber-of-secrets.md
manifest_id: external-A01
output_file: sources/external/official-rowling/a01-chamber-of-secrets.yaml
status: pending
claimed_by: null
claim_token: null
claimed_at: null
completed_at: null
attempts: 0
validation_status: not_run
blocked_reason: null
update_profile: canonical_external_evidence
```

The queue order is A01-A37 followed by B01-B26. Ordering determines the default next claim but does not prevent safe parallel claims.

### Status values

- `pending`: available for an agent to claim.
- `in_progress`: owned by one active claim token.
- `done`: canonical YAML exists, validation passed, duplicate checks used the latest index, and generated outputs were refreshed.
- `blocked`: processing cannot continue without a source, provenance, schema, or human decision; `blocked_reason` is mandatory.

No unit is initially marked `in_progress`. A status becomes `in_progress` only through the claim command.

## Claim and Completion Protocol

Add a lock-aware queue command with four operations:

```text
claim [--agent AGENT_ID] [--unit UNIT_ID]
complete --unit UNIT_ID --claim-token TOKEN
release --unit UNIT_ID --claim-token TOKEN --reason REASON
block --unit UNIT_ID --claim-token TOKEN --reason REASON
```

### Claim

The claim command takes an exclusive filesystem lock, selects the requested pending unit or the first pending unit, writes `status: in_progress`, increments `attempts`, records claimant and UTC timestamp, generates a unique claim token, updates compact processing state, and releases the lock. It prints only the current unit’s required paths and commands.

At most four units may be `in_progress`. A fifth claim fails without changing state.

### Extraction

The worker reads only:

- `docs/instructions/runtime-contract.md`
- `project-control/processing-state.yaml`
- its manifest record
- its assigned Markdown snapshot
- `docs/instructions/schema-reference.md` only for schema uncertainty
- compact duplicate/tag indexes through query commands
- individual source YAML files returned as likely matches

The worker must not read every source YAML, the generated book seed, full appendices, or unrelated external snapshots.

### Completion

Completion takes the queue lock and verifies the claim token. While holding the serialized completion lock it:

1. Confirms the assigned output YAML exists.
2. Validates its source-unit and entry schema.
3. Rebuilds compact indexes so concurrently completed YAML is visible.
4. Repeats duplicate-candidate queries against the latest indexes.
5. Requires the worker’s duplicate-check metadata to reflect those results.
6. Runs the complete validation and generation workflow.
7. Marks the unit `done`, clears claim fields, records `completed_at`, and selects the next pending unit for the display state.

If any gate fails, the unit remains `in_progress` and the command reports the exact failing gate. It must never mark a unit done first and validate later.

### Release and block

- `release` returns an abandoned or interrupted claim to `pending`, clears ownership fields, and records a release note.
- `block` changes the unit to `blocked`, retains its attempt history, and requires a precise reason.
- A stale or mismatched token cannot release, block, or complete another worker’s unit.

## Canonical External Evidence Schema

External YAML uses the existing `source_unit` and `entries` structure, with web-specific provenance added.

```yaml
source_unit:
  source_kind: external_markdown
  source_id: A01
  source_file: resources/external/official-rowling/harrypotter-com/a01-chamber-of-secrets.md
  title: Chamber of Secrets
  author: J.K. Rowling
  source_site: HarryPotter.com
  source_class: official_rowling_original
  authority: A
  publication_date: '2015-08-10'
  original_url: https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets
  retrieval_url: https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets
  capture_completeness: complete
  content_sha256: 64-character-sha256
  processed_date: '2026-08-15'
  processor_notes: Source body read completely and evidence extracted under the external runtime contract.

entries:
  - id: ext-a01-001
    source_file: resources/external/official-rowling/harrypotter-com/a01-chamber-of-secrets.md
    source_id: A01
    source_url: https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets
    source_section: null
    pdf_page: null
    printed_page: null
    extracted_text_lines: null
    text_anchor:
      start_phrase: short local start phrase
      end_phrase: short local end phrase
      local_occurrence_note: where the passage occurs in the snapshot
    nearby_context: concise context
    match_terms:
      - normalized search term
    quote_excerpt_short: fewer than 25 words
    source_note: concise paraphrase of the evidence
    reference_type: historical_claim
    era_classification: pre_1984_historical_candidate
    topic_tags:
      - normalized-tag
    candidate_part: existing candidate part
    candidate_chapter: existing candidate chapter
    candidate_section: specific candidate section
    reason_for_placement: placement rationale
    relevance_to_hogwarts_a_history: intended use and temporal qualification
    duplicate_check:
      possible_duplicate: false
      duplicate_of: null
      notes: indexed lookup result
    confidence: high
    limitations: source and interpretation limits
```

The existing reference types, era classifications, quote limit, placement model, and duplicate semantics remain unchanged.

For external entries, `pdf_page`, `printed_page`, and `extracted_text_lines` remain present and null for compatibility. `source_id`, `source_url`, `source_section`, and `text_anchor` provide the actual locator.

## Manifest Field Migration

Rename `completeness` to `capture_completeness` in:

- `resources/manifests/external-sources.yaml`
- all 63 external snapshot headers
- `scripts/external_sources/build_external_corpus.py`
- acquisition tests
- corpus README and acquisition report where the field is described
- all new external validators and queue-generation code

The field means the complete readable content exposed by the retrieval carrier was captured. It does not mean evidence extraction, corpus discovery, or primary-carrier verification is complete.

Evidence-processing progress is represented only by queue `status`.

## Update Profile

Every external unit references `update_profile: canonical_external_evidence`. The profile defines what a completed unit changes.

### Directly written by the worker

- Its assigned `sources/external/...yaml` file.
- Nothing else.

### Updated by queue commands

- Unit status, claim metadata, attempts, validation status, and blocker/release history in `project-control/source-plan.yaml`.
- Current/next/last-completed external pointers and aggregate counts in `project-control/processing-state.yaml`.
- The generated `project-control/next-run.md` display.

### Regenerated after successful completion

- `project-control/duplicate-index.yaml`
- `project-control/entry-index.yaml`
- `project-control/source-index.yaml`
- `project-control/tag-index.yaml`
- `book-seed/hogwarts-a-history-seed.md`
- `appendix/generated/*.md`

Workers must not edit generated outputs manually.

## Index-First Lookup Rules

Agents never scan the entire evidence dataset.

1. Normalize three to eight topic tags for a candidate entry.
2. Run `just query-dupes <tag> <tag>`.
3. Run `just query-entries <tag>` when wider context is needed.
4. Open only the source YAML files named by compact query results.
5. Record the comparison in `duplicate_check`.

The source-discovery helper makes external entries visible to the existing indexes. The external manifest remains the source-corpus provenance catalog; the evidence indexes remain the lookup layer for extracted claims.

## Runtime Contract Replacement

The new active runtime contract will contain:

- orientation commands;
- claim, current-unit, completion, release, and block commands;
- minimal required reads;
- prohibited broad reads;
- the external evidence extraction procedure;
- index-first duplicate procedure;
- status transition rules;
- direct-versus-generated update rules;
- validation and completion gates;
- the Git backup rule already used by the project.

The archive backup is created and verified before the active contract is replaced. The existing redirect at `docs/instructions/hogwarts-history-seed-builder.md` continues to point to the active runtime contract.

## Command Surface

Extend the root `Justfile` with compact recipes:

```text
just claim-external [agent] [unit]
just current-external
just complete-external unit token
just release-external unit token reason
just block-external unit token reason
just external-status
```

Existing recipes remain valid:

```text
just query-dupes <tags>
just query-entries <tag>
just validate
just indexes
just generate
just post
```

`just brief` and `just next` switch to the external queue once the replacement runtime is activated.

## Error Handling

- Missing snapshot or manifest record: claim fails and the unit is marked `blocked` only through an explicit block command.
- Hash mismatch: validation fails; no evidence output is accepted as complete.
- Invalid source YAML: completion fails and unit remains `in_progress`.
- Duplicate entry ID: completion fails.
- Stale claim token: command fails without state mutation.
- Four active claims: further claims fail without state mutation.
- Index or generator failure: unit remains `in_progress`; generated outputs are never treated as proof of completion.
- Process interruption during state mutation: write state to a temporary sibling and atomically replace the target while holding the lock.

## Testing Strategy

Add test-first coverage for:

1. Manifest-to-queue generation produces exactly A01-A37 and B01-B26 in deterministic order.
2. All units start `pending` with unique IDs, inputs, outputs, and manifest references.
3. Two simultaneous claims cannot receive the same unit.
4. A fifth claim is rejected when four claims are active.
5. Claim tokens gate completion, release, and block transitions.
6. Completion refuses missing or invalid YAML.
7. Successful completion changes only the claimed unit to `done` and advances compact state.
8. External YAML validates with null PDF locators and required web locators.
9. All index builders discover both book and external YAML.
10. Duplicate and entry queries return external entries without broad reads.
11. Book-seed and appendix source lines render web provenance without `PDF p. None`.
12. `completeness` is absent from the manifest and all snapshots after migration.
13. `capture_completeness` is present and preserved through corpus regeneration.
14. The runtime-contract archive hash equals the pre-replacement active contract hash.
15. Existing book-source tests continue to pass unchanged.

## Rollout Order

1. Back up and hash-verify the existing runtime contract.
2. Migrate `capture_completeness` and regenerate the acquisition corpus.
3. Add unified canonical source discovery and web-aware schema validation.
4. Update indexes, queries, book-seed generation, and appendices for external YAML.
5. Add the lock-aware external queue controller and tests.
6. Generate the 63-unit queue from the manifest while retaining completed book history.
7. Activate external processing state and regenerate `next-run.md`.
8. Replace the active runtime contract and extend the `Justfile`.
9. Run focused tests, full validation, generation, and the complete repository test suite.
10. Verify no unit is falsely marked `in_progress` or `done`; the first unit remains pending until claimed.

## Acceptance Criteria

- The previous runtime contract exists unchanged in the dated archive file.
- The active runtime contract describes only the external-source phase while retaining shared project rules.
- Exactly 63 external units exist, one per manifest logical ID.
- Every unit has an explicit input, output, status, update profile, and validation state.
- No unit is initially marked `in_progress` or `done`.
- Claims are lock-safe and capped at four concurrent units.
- Completion is validation-gated and token-gated.
- External evidence enters the existing canonical indexes and generated book seed.
- Agents use compact indexes rather than scanning all canonical YAML.
- The manifest and snapshots use `capture_completeness`; the ambiguous `completeness` field is gone.
- Existing book evidence files and completed source-plan history are preserved.
- The full repository test suite passes after activation.
