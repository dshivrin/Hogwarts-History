# Runtime Contract

Use this compact contract for one acquired external-source snapshot per work unit. The completed book-and-companion runtime is preserved at `docs/instructions/archive/runtime-contract-book-and-companion-extraction-2026-08-15.md`.

## CLI Workflow

- Start with `just brief`, `just next`, and `just external-status`.
- Claim the next unit with `just claim-external <agent>` or a specific unit with `just claim-external <agent> <unit>`.
- Recover active claim details with `just current-external` or `just current-external <unit>`.
- Use `just search "pattern"`, `just query-dupes <tag> <tag>`, and `just query-entries <tag>` for narrow lookup.
- Use `just validate` for canonical evidence; completion validates the assigned staged YAML before promotion.
- Submit a finished unit with `just complete-external <unit> <claim-token>`.
- Abandon an interrupted claim with `just release-external <unit> <claim-token> "<reason>"`.
- Record a source or decision blocker with `just block-external <unit> <claim-token> "<reason>"`.

Do not require `yq`; use the project commands for YAML state transitions.

## Required Reads

For a normal claimed unit, read only:

1. `docs/instructions/runtime-contract.md`.
2. `project-control/processing-state.yaml`.
3. The claim output for the assigned unit, token, input, manifest ID, and output paths.
4. The complete assigned Markdown snapshot, including its YAML front matter.
5. The assigned output YAML only if it already exists.

Read `docs/instructions/schema-reference.md` only for schema uncertainty or a validation failure. Read `docs/instructions/background-guide.md` only for canon, era, or classification ambiguity.

## Prohibited Broad Reads and Writes

Do not scan all canonical source YAML, all external snapshots, the full generated book seed, full appendices, archive directories, or old prompts. Do not open compact index YAML directly during normal extraction; use query commands.

Workers write only their assigned staged YAML path under `work/external-staging/`; staged drafts are deliberately excluded from canonical discovery. Workers must not edit canonical `sources/external/`, the manifest, `source-plan.yaml`, `processing-state.yaml`, `next-run.md`, indexes, appendices, or book seed. Queue completion atomically promotes only the claimed draft after every gate succeeds.

## External Extraction Procedure

1. Claim one `pending` unit and retain its claim token.
2. Read the assigned snapshot body completely.
3. Extract evidence useful to a future fan edition of *Hogwarts: A History*, preserving source authority and temporal limitations.
4. Write the exact assigned **staging** YAML path returned by the claim, with top-level `source_unit` and `entries` keys. Do not write the canonical output path.
5. Copy snapshot provenance into the external `source_unit`, including `source_id`, URLs, `capture_completeness`, and the snapshot body hash as `content_sha256`.
6. Use entry IDs `ext-<logical-id-lower>-NNN`, such as `ext-a01-001`.
7. Keep `pdf_page`, `printed_page`, and `extracted_text_lines` present and null. Locate evidence with `source_id`, `source_url`, optional `source_section`, and `text_anchor`.
8. Keep every `quote_excerpt_short` under 25 words. Paraphrase evidence in `source_note`.

## Index-First Duplicate Procedure

1. Normalize three to eight topic tags for each candidate entry.
2. Run `just query-dupes <tag> <tag>` with the strongest tags and placement terms.
3. Run `just query-entries <tag>` only when wider indexed context is needed.
4. Open only source YAML paths returned as likely matches.
5. Record the indexed comparison in `duplicate_check.notes`, plus `audit.query_tags` and the reviewed `audit.candidate_ids`; set `duplicate_of` when the same claim is already represented. Completion rebuilds the latest duplicate index, excludes the completing entry IDs, and rejects candidate IDs that are not returned by that index.
6. Do not delete corroborating evidence merely because it overlaps another source.

## Completion and Status Rules

- `pending` is claimable; `in_progress` is owned by one token; `done` has passed all gates; `blocked` requires a precise reason.
- Never edit a status or claim token manually.
- `just complete-external` verifies token ownership and staged output existence, binds the draft to its claimed carrier and snapshot provenance, validates anchors and tag counts, rebuilds/rechecks the latest duplicate index, atomically promotes only that draft, rebuilds canonical indexes, updates completion state, and regenerates the book seed and appendices before marking the unit `done`.
- A failed completion leaves the unit `in_progress`. Correct the assigned YAML and retry with the same token.
- Use release for interruption and block only for an actual source, provenance, schema, or human-decision blocker.

## Validation Checklist

- The assigned staged YAML parses with PyYAML and uses the external schema.
- Source ID, snapshot path, URLs, capture status, and body hash match the assigned carrier.
- Every entry has complete web locators, anchor phrases, short quote, paraphrase, placement, three to eight tags, classification, duplicate check, confidence, and limitations.
- Candidate anchor phrases can be found in the assigned snapshot.
- No generated or queue-owned file was edited by the worker.
- The completion command succeeds and reports the unit as `done`.

## Git Backup Rule

The coordinating agent stages only files belonging to the completed unit, reviews the staged diff, commits with a concise message, and pushes the current branch when requested. A worker must not commit unrelated shared-worktree changes.
