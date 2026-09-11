# Runtime Contract

Use this dispatcher for exactly one ready source unit per automation invocation. The completed external-only contract is preserved at `docs/instructions/archive/runtime-contract-external-source-extraction-completed-2026-09-11.md`.

## Dispatch Rule

Start with `just brief` and inspect `project-control/processing-state.yaml`.

1. If `current_source_unit` is a mapping, process only that bounded PDF unit with the PDF procedure below.
2. Otherwise, if `external_processing.next_pending_unit` is present, use the external claim procedure below.
3. Otherwise, perform no extraction. Report that no ready unit remains and summarize blockers from `project-control/remaining-source-units.yaml`.

Never let an exhausted external queue hide a populated `current_source_unit`.

## CLI Workflow

- Start with `just brief`, `just next`, and `just external-status`.
- Use `just search "pattern"`, `just query-dupes <tag> <tag>`, and `just query-entries <tag>` for narrow lookup.
- Use `just validate` for canonical evidence validation.
- Finish a PDF unit with `just advance-current`; this validates, advances once, regenerates, tests, and restores control/generated artifacts if any completion gate fails.
- Claim an external unit with `just claim-external <agent>` or `just claim-external <agent> <unit>`.
- Recover an external claim with `just current-external` or `just current-external <unit>`.
- Finish an external unit with `just complete-external <unit> <claim-token>`.
- Abandon or block an external claim with `just release-external` or `just block-external` and the required token/reason.

Do not require `yq`; use project commands for YAML state transitions.

## Required Reads for a PDF Unit

Read only:

1. `docs/instructions/runtime-contract.md`.
2. `project-control/processing-state.yaml`.
3. Every rendered page image for the inclusive current range.
4. The current output YAML only if it already exists.
5. Individual historical YAML files only when compact query results identify them as candidates.

Read `docs/instructions/schema-reference.md` only for schema uncertainty or validation failure. Read `docs/instructions/background-guide.md` only for canon, era, or classification ambiguity.

## Scanned PDF Procedure

The current `Fantastic Beasts and Where to Find Them` carrier is image-only. Empty output from `scripts/extract_pages.py` is not evidence that its pages are empty.

1. Read `source_file`, `page_start`, and `page_end` from `current_source_unit`.
2. Clear old disposable cache files with `just clean-cache`.
3. Create `.tmp/current-source-images/`.
4. Render only the inclusive current range as rendered page images:

   ```bash
   pdftoppm -f PAGE_START -l PAGE_END -jpeg -r 180 SOURCE_PDF .tmp/current-source-images/page
   ```

5. Visually inspect every rendered page image in that directory. Do not use OCR alone and do not render pages outside the current range.
6. Extract every explicit *Hogwarts: A History* reference. For other material, keep the strongest three to seven relevant entries; `entries: []` is valid when the bounded unit has no relevant evidence.
7. Write only the exact `output_yaml` path assigned by `current_source_unit`, using top-level `source_unit` and `entries` keys.
8. Use entry IDs `fb-chNN-NNN`. Preserve the inclusive range in `source_unit`; locate each entry with its exact `pdf_page`, optional printed page, and a local `text_anchor` visible on that page.
9. Keep each `quote_excerpt_short` under 25 words and paraphrase the evidence in `source_note`.
10. Run the index-first duplicate procedure below.
11. Run `just advance-current`. If it fails, correct the current output and retry; the current/next controls are restored automatically.
12. Review and commit only files belonging to this completed unit.
13. Stop the invocation after the completion report. Do not begin `next_source_unit`, even if it is now displayed as current.

## Index-First Duplicate Procedure

1. Normalize three to eight topic tags for each candidate entry.
2. Run `just query-dupes <tag> <tag>` with the strongest tags and placement terms.
3. Run `just query-entries <tag>` only when wider indexed context is needed.
4. Open only source YAML paths returned as likely matches.
5. Record the comparison in `duplicate_check`; keep corroborating evidence when it independently supports or extends a claim.
6. Do not open full compact index files during normal extraction.

## External Claim Procedure

Use this only when no PDF `current_source_unit` exists and the external queue has a pending unit.

1. Claim one pending unit and retain its token.
2. Read the complete assigned Markdown snapshot and write only its assigned staging YAML under `work/external-staging/`.
3. Workers write only their assigned staged YAML path. Do not write the canonical output path.
4. Preserve snapshot provenance, URLs, `capture_completeness`, source ID, and body hash.
5. Use `ext-<logical-id-lower>-NNN` IDs and null PDF locators.
6. Record `audit.query_tags` and every candidate from the exact ranked `just query-dupes` result, in returned order. Give each candidate one disposition: `duplicate`, `corroborating`, or `distinct`. Make `possible_duplicate` and `duplicate_of` agree exactly with candidates marked `duplicate`; free-text notes are optional context, not the audit.
7. Complete, release, or block the single claim with the project command.
8. Stop after one external unit.

## Prohibited Broad Reads and Writes

Do not scan all canonical source YAML, all external snapshots, the full generated book seed, full appendices, archive directories, old prompts, or the full PDF. Use the assigned source range and compact query commands.

For PDF units, do not manually edit `source-plan.yaml`, `processing-state.yaml`, `next-run.md`, indexes, appendices, or book seed. For external units, do not manually edit queue-owned or generated files.

## Validation and Completion Rules

- A PDF output must parse, contain `source_unit` and `entries`, use its assigned carrier/range, and pass the canonical validator before state advances.
- `just advance-current` snapshots control and generated artifacts, rebuilds indexes, validates, advances exactly once, regenerates outputs, runs tests, and restores the snapshot after any failure.
- The current PDF output remains available for correction if a completion gate fails.
- External completion rebuilds the latest indexes, reruns the recorded ranked duplicate query, and rejects missing, invented, repeated, reordered, or inconsistent candidate reviews.
- `pending` external units are claimable; `in_progress` external units are token-owned; `done` units passed all gates; `blocked` units require a precise reason.
- Blocked acquisition rows in `project-control/remaining-source-units.yaml` are not readable extraction units and must never be auto-promoted.

## Run Summary

Report:

- source unit ID and inclusive pages read;
- source PDF/snapshot and canonical output path as links;
- entries created and explicit *Hogwarts: A History* reference count;
- duplicate candidates and open questions;
- validation/test result and commit ID;
- exactly one next current unit, or no ready unit plus blocked backlog count.

## Git Backup Rule

After every successful unit, stage only files belonging to that unit, review the staged diff, commit with a concise message, and push only when requested. Never stage `.DS_Store`, caches, virtual environments, rendered page images, or unrelated user changes.
