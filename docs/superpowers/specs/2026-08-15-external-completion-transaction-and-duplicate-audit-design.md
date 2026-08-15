# External Completion Transaction and Duplicate Audit Design

**Date:** 2026-08-15
**Status:** Approved in conversation
**Scope:** Close the two remaining production-readiness gaps in the external-source completion controller, then process A02 as an isolated test run.

## Context

The A01 trial produced three accepted evidence entries and the external automation passes its current validation and test suite. A final review nevertheless reproduced two completion-path weaknesses:

1. When a generator fails after the staged YAML has been promoted, the controller restores the queue state and returns the YAML to staging but does not restore indexes, the book seed, or generated appendices that were already rewritten.
2. Duplicate candidate IDs are checked against the latest duplicate index, but `duplicate_check.notes` is accepted as arbitrary non-empty prose and therefore is not an enforceable audit record.

No other part of the acquisition corpus, A01 evidence claims, queue model, or four-worker claim limit is changed by this design.

## Goals

- A failed completion must restore every queue-owned and generated artifact to its exact pre-completion bytes.
- A duplicate audit must record a structured disposition for every candidate returned by the latest index query.
- Duplicate flags and targets must agree with those structured dispositions.
- Existing accepted A01 evidence must migrate without changing its source claims, placement, or provenance.
- After the fixes pass verification, A02 becomes the next isolated agent test.

## Non-goals

- Redesigning the index scoring algorithm.
- Proving that a worker's written rationale is factually correct through natural-language analysis.
- Making all repository writes globally atomic against operating-system or power loss.
- Processing more than A02 during the follow-up trial.
- Changing the 63-unit queue order or existing acquired source snapshots.

## Completion Transaction

### Artifact inventory

Immediately before the first completion command that can mutate canonical or generated state, the controller captures an in-memory byte snapshot of the fixed generated outputs:

- `project-control/duplicate-index.yaml`
- `project-control/entry-index.yaml`
- `project-control/source-index.yaml`
- `project-control/tag-index.yaml`
- `project-control/source-plan.yaml`
- `project-control/processing-state.yaml`
- `project-control/next-run.md`
- `book-seed/hogwarts-a-history-seed.md`
- every regular file directly under `appendix/generated/`

The snapshot records both the bytes and whether each path existed. It also records the original set of files in `appendix/generated/` so a failed generator cannot leave a newly created file behind.

### Success path

The existing serialized completion lock remains the transaction boundary:

1. Verify the claim and staged YAML.
2. Capture the artifact snapshot.
3. Rebuild the duplicate and tag indexes and verify the structured audit through the same query implementation exposed by `just query-dupes`.
4. Promote only the claimed staged YAML.
5. Rebuild canonical indexes and run full source validation.
6. Write the prospective `done` queue and processing state.
7. Generate the book seed and appendices from that state.
8. Return success only after all commands finish.

The byte snapshot is then discarded.

### Failure path

If any step after snapshot capture fails:

1. Move the promoted YAML back to its assigned staging path if promotion occurred.
2. Restore every snapshotted artifact atomically from its original bytes.
3. Remove only newly created files within the explicit generated-artifact inventory.
4. Leave the unit `in_progress` with the same claim token so the worker can correct or retry it.
5. Raise a gate-specific `QueueError`.

The controller does not attempt to regenerate the old state during rollback because the same failing generator could fail again. Restoration is byte-based and independent of generator behavior.

This transaction protects handled command failures and exceptions. Crash recovery across process termination or power loss is outside this bounded fix; adding a durable journal can be considered separately if operational experience requires it.

## Structured Duplicate Audit

### Schema

Each external entry uses:

```yaml
duplicate_check:
  possible_duplicate: true
  duplicate_of: cos-ch17-006
  notes: Optional human context.
  audit:
    query_tags:
      - chamber-of-secrets
      - basilisk
      - parselmouth
    candidates:
      - id: cos-ch17-006
        disposition: duplicate
```

Allowed dispositions are:

- `duplicate`: the new entry repeats the indexed claim and `duplicate_of` should identify it.
- `corroborating`: the candidate overlaps, but the new carrier independently supports or extends it.
- `distinct`: the candidate was reviewed and does not represent the same claim.

`notes` remains optional human context. It is not used as a completion gate and cannot substitute for structured candidates.

### Verification rules

After rebuilding the duplicate and tag indexes, completion:

1. Normalizes `audit.query_tags` and calls the shared `query_duplicates` implementation with those tags, no placement filters, and the command's default limit of ten. This avoids a second, divergent interpretation of the indexes.
2. Excludes every entry in the completing YAML from the returned matches.
3. Requires `audit.candidates` to be a list of unique mappings with a returned `id` and an allowed `disposition`.
4. Requires the reviewed ID list to equal that latest, ranked, limited query result exactly. Missing, invented, duplicated, extra, or reordered IDs fail completion.
5. Requires `possible_duplicate` to be true exactly when at least one candidate has disposition `duplicate`.
6. Requires the normalized `duplicate_of` targets to equal the IDs whose disposition is `duplicate`.
7. Allows an empty candidate list only when the latest query returns no candidates; in that case `possible_duplicate` is false and `duplicate_of` is null.

These rules verify the completeness and internal consistency of the audit. They deliberately do not pretend to prove the semantics of a worker's prose.

## Compatibility and Migration

- Replace `audit.candidate_ids` with `audit.candidates` in A01's three entries.
- Preserve A01 entry IDs, quotations, source notes, placement, provenance, and duplicate targets.
- Map each existing A01 target to `disposition: duplicate`, because all three entries currently set `possible_duplicate: true` and name that target in `duplicate_of`.
- Update the runtime contract and schema reference so future workers produce the structured shape directly.
- Do not change the acquired A01 Markdown snapshot or any of the 62 pending snapshots.

## Tests

Follow test-driven development with two red-green cycles.

### Transaction tests

- Seed every generated artifact with distinctive bytes.
- Use a runner that mutates indexes, book seed, appendices, and creates an extra generated appendix before raising during generation.
- Verify the regression test fails against the current controller because those mutations survive.
- Implement snapshot restoration.
- Assert byte-for-byte equality for every pre-existing artifact, removal of the newly created generated file, return of canonical YAML to staging, unchanged claim token, and `in_progress` status.
- Retain a success-path test proving generated changes remain after successful completion.

### Duplicate-audit tests

- Verify the current candidate-ID-only shape fails the new schema test.
- Accept exact structured reviews with allowed dispositions.
- Verify completion and `just query-dupes` return the same ordered, limited candidate IDs for the same tags.
- Reject arbitrary notes without structured candidates.
- Reject missing, invented, duplicate, or extra candidate IDs.
- Reject unknown dispositions.
- Reject disagreements among `possible_duplicate`, `duplicate_of`, and duplicate dispositions.
- Cover the empty latest-index result.

### Full verification

Run the focused queue tests, canonical validation, index generation, appendix/book-seed generation, the complete unit-test suite, `git diff --check`, and a clean-worktree check after committing.

## A02 Test Run

After the fix commit passes verification:

1. Claim only A02 (`The Sorting Hat`) through the queue controller.
2. Give the test agent only the active runtime contract, compact claim data, A02 snapshot, and index-query access allowed by the runtime.
3. Require the new structured candidate audit in its staged output.
4. Complete A02 through the hardened controller.
5. Review the A02 evidence for anchor accuracy, quote length, placement, provenance, duplicate dispositions, and unintended broad reads.
6. Commit A02 separately from the controller fix so the trial can be reverted without losing the automation repair.

## Rollback Points

- `92884bd` remains the ready-for-first-trial automation checkpoint.
- `100ebd7` remains the isolated A01 trial commit.
- `786a9d7` remains the first completion-hardening checkpoint.
- The new controller fix and A02 trial will be separate commits.
