# Agent instructions: implement the open-questions editorial overlay

Work in the repository root and implement the plan in:

`docs/superpowers/plans/2026-09-18-open-questions-overlay.md`

The plan may have been partially or fully attempted already. Inspect the current worktree and verify every requirement against repository sources before editing. Do not trust completion checkboxes or generated claims without evidence. Preserve correct existing work and make only the changes needed to reach the acceptance criteria below.

## Objective

Replace the legacy enriched open-questions proposal with a compact, ID-keyed editorial overlay that remains traceable to all 386 canonical questions. The result must help a drafting agent retrieve questions for one chapter, see verified findings and remaining research, and distinguish canonical evidence from historical inference and creative reconstruction.

This task is research infrastructure only. Do not edit existing manuscript chapters or draft new prose.

## Repository authorities

Treat these files as authoritative:

- Canonical questions: `project-control/structured-sources/open-questions.yaml`
- Twenty-chapter outline: `authoring/editions/1984/table-of-contents.yaml`
- Evidence ID index: `project-control/entry-index.yaml`
- External-source manifest: `resources/manifests/external-sources.yaml`
- Legacy enriched proposal and guide: `resources/external/open-questions-scapping/`
- Detailed implementation plan: `docs/superpowers/plans/2026-09-18-open-questions-overlay.md`

Read applicable `AGENTS.md` files before making changes. Do not modify the canonical questions, source evidence, chapter outline, generated indexes, or manuscript files as part of this task.

## Non-negotiable requirements

1. Preserve all 386 canonical question IDs exactly once and in canonical order. Do not delete, merge, or silently rename answered, duplicated, excluded, or repository-only questions.
2. Keep canonical facts separate from interpretation. Every verified factual statement must cite one or more exact evidence IDs that resolve through `project-control/entry-index.yaml`.
3. Keep historical inference and creative reconstruction in separate, explicitly non-canonical fields. Never present either as verified evidence.
4. Preserve partial answers. Record the supported portion and retain a narrower residual question for everything still unresolved.
5. Use only chapter IDs from the authoritative 20-chapter outline. Give every question one primary chapter and optional secondary chapter references.
6. Search existing indexed evidence, canonical YAML, local snapshots, and local PDFs before identifying external research. Do not download or re-extract material already present locally.
7. Treat unverified URLs only as research candidates. They cannot support verified facts until ingested through the normal evidence pipeline and assigned evidence IDs.
8. Preserve the pre-restructure enriched YAML and guide as dated, byte-identical backups before replacing the live files.
9. Keep house-elf questions traceable but excluded from manuscript use. Keep `source-processing-001` as repository control work rather than narrative material.
10. Do not modify or draft manuscript chapters. Do not commit unless the user explicitly asks.

## Required implementation

Create or complete `scripts/open_questions_overlay.py` with three capabilities:

- Build the overlay from the canonical questions and dated legacy backup.
- Validate the checked-in overlay against canonical IDs, evidence IDs, source IDs, the source inventory, and chapter IDs.
- Query all questions relevant to one chapter, including secondary destinations, while joining canonical question wording for readable output.

The live YAML must use an ID-keyed mapping under `questions`. Each value should contain only the editorial overlay fields:

- `research`
- `gap`
- `placement`
- `interpretation`

Do not duplicate canonical question text, topic, original status, source notes, or related-entry fields in the overlay.

The source catalog must map legacy source leads to canonical local source IDs where possible and mark absent external targets as `candidate_unverified`. Each question must identify local sources to inspect first, external candidates only when applicable, useful query tags, and a concrete next action.

Rewrite `resources/external/open-questions-scapping/hogwarts-open-questions-codex-guide.md` around this model. It must explain:

- Which files are authoritative.
- How to retrieve questions for one chapter.
- The local-first research order.
- How partial answers and residual gaps work.
- How event date, witness date, and narrator-access date differ.
- The boundary between evidence, inference, authorial open questions, and creative reconstruction.
- How to update and validate one overlay record without editing the canonical questions.

Add focused unit tests in `tests/test_open_questions_overlay.py`. Tests must cover all 386 IDs, ID-keyed schema shape, exact canonical order, evidence/source/chapter validation, partial-answer preservation, later-context treatment, excluded items, chapter retrieval, and deterministic rebuild equivalence.

Expose a `just validate-open-questions` command and include the overlay validator in `just validate`.

## Working method

1. Inspect `git status` and preserve unrelated user changes.
2. Audit the legacy proposal against the repository authorities before trusting its source leads or thematic destinations.
3. Confirm the dated backups exist and match the original pre-restructure hashes. If they do not exist, create them before changing the live files.
4. Use test-driven development: add or confirm a failing focused test before changing behavior, then make the smallest implementation that passes.
5. Generate the live overlay only from the dated legacy backup plus current canonical repository data.
6. Query representative chapters 2, 5, 10, and 17 and inspect their results.
7. Run every validation gate below.
8. Review the final diff and confirm no canonical research data or manuscript file changed.

## Acceptance criteria

The task is complete only when all of the following are true:

- The overlay contains exactly 386 unique keys matching canonical IDs in canonical order.
- The canonical question-file hash recorded by the overlay matches the current canonical file.
- Every verified fact has valid evidence IDs; no inference or creative statement appears in verified facts.
- Every partial answer has a non-empty residual question.
- Every local source reference resolves to a locally available catalog entry.
- Every external source reference resolves to a catalog entry explicitly marked unverified.
- Every primary and secondary chapter ID exists in the authoritative 20-chapter outline.
- A chapter query returns both primary and secondary matches with canonical wording.
- The checked-in overlay exactly matches a deterministic rebuild from the dated legacy backup.
- `just validate-open-questions` passes.
- `just validate` passes.
- `just test` passes. An expected validator error printed by a negative-path test is not a suite failure when the final test result is `OK`.
- `git diff --check` passes.
- Backup hashes are verified.
- No manuscript chapter, canonical open-question record, source evidence record, or chapter outline was modified.

## Final report

Report:

- Files created or changed.
- Confirmation that all 386 IDs were preserved.
- Counts by research and gap status.
- How many sources are locally available versus external candidates.
- Results of representative chapter queries.
- Exact validation and test results.
- Confirmation that canonical data and manuscripts were untouched.
- Any unresolved limitation that still requires human editorial judgment.

Do not claim completion from inspection alone. Run the required commands and cite their fresh results.
