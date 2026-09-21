# Chapter Workflow

The long-term goal is an automated authoring task that handles one chapter at a
time while preserving a consistent voice and a traceable path from evidence to
prose. Automation is not implemented yet.

## Intended state machine

The persisted state names remain backward-compatible. Evidence synthesis and
validation are mandatory internal gates within `evidence_reviewed`; they do not
add new values to `chapter-status.yaml`.

```text
PLANNED
↓
EVIDENCE_SELECTED
↓
EVIDENCE_REVIEWED
  evidence reviewed and synthesized
  ↓
  synthesis validated
↓
OUTLINED
↓
OUTLINE_APPROVED
↓
DRAFTED
↓
AUDITED
↓
EDITOR_APPROVED
```

Persisted project-control values use the corresponding lowercase forms. State
transitions must be explicit, and no stage may be skipped simply because material
already appears persuasive.

## Chapter workspace

When a chapter enters preparation, its draft workspace will contain:

```text
brief.md
evidence-selection.yaml
evidence-gaps.md
outline.md
draft.md
fact-audit.md
style-audit.md
continuity-audit.md
```

Do not pre-create workspaces for chapters that remain merely planned.

The generic names above remain valid historical artifacts and initial-workspace
conventions. For every new numbered manuscript revision `NN`, create a matching
`evidence-synthesis-revision-NN.md` and `outline-revision-NN.md`. The synthesis
belongs only to that manuscript revision and must not be silently reused for a
later revision.

When work targets revision `NN`, the exact matching revisioned artifacts are
authoritative for that revision. Generic `outline.md`, generic `draft.md`, and
outline material embedded in a historical preparation package remain valid
historical inputs or baselines, but none may substitute for a missing matching
revisioned synthesis or outline.

## Required order of work

The evidence-selection stage precedes outlining. An approved outline precedes
prose. The workflow must not begin with a request equivalent to “Write a chapter
about X.” Its intended logic is:

```text
research evidence
↓
curated evidence
↓
consolidated historical claims
↓
validated evidence synthesis
↓
chapter argument
↓
approved outline
↓
prose
↓
independent audits
```

This order prevents a narrative from being invented first and supported by a
selective search afterward. Fact, style, and continuity audits are separate
checks. Human editorial approval remains a required gate, and completion of one
chapter must not automatically start the next.

## Synthesis validation gate

Creating a synthesis file does not validate it. A new revision remains at
`evidence_selected` until all of the following are true:

1. `evidence-synthesis-revision-NN.md` exists and records target revision `NN`;
2. its synthesis verdict is exactly `PASS`;
3. it contains no unresolved `blocking` verification item;
4. every consolidated claim has exactly one disposition defined in
   `authoring/shared/evidence-policy.md`;
5. every evidence ID in the matching evidence selection is reconciled to at
   least one consolidated claim, verification item, or deferred-evidence entry;
6. every `advance_to_outline` claim has named supporting evidence, or is
   explicitly classified as a bounded editorial inference supported by named
   evidence; and
7. no `blocked_pending_verification` claim advances to the outline.

Only after all seven conditions pass may the working revision be recorded as
`evidence_reviewed` and advance toward `outlined`. An `omittable` verification
item permits only the independently supported remainder to advance. A
`deferable` item must be represented in deferred evidence and excluded from the
current outline and manuscript.

## From claims to outline and prose

Build the outline from consolidated claims, not by walking evidence IDs. Give
each section one explicit purpose—“The purpose of this section is to show
_____”—and compare every section with every other section before approval.
Merge sections that primarily answer the same historical question.

Each claim normally has one primary section. A later section may recall it to
develop a new consequence, distinction, contradiction, or chronological stage,
but may not re-prove it. Every outlined claim must exist in the matching passing
synthesis. Drafting then proceeds from the chapter purpose, matching synthesis,
matching outline, evidence references, active style lock, and the exact earlier
chapter baselines used for comparison.

After drafting, perform a dedicated compression pass and record three separate
repetition checks: sentence and paragraph repetition, chapter-level conceptual
repetition, and cross-chapter repetition. Compression follows redundancy, not
an arbitrary percentage target, and preserves concrete historical detail and
meaningful distinctions.

## Unified-edition planning fields

Evidence dossiers must classify event chronology independently from knowledge
access. Outlines must label each proposed passage as reconstructed Bagshot
narrative or later editorial addition. An addendum is appropriate only when an
addition would disrupt chronology, the reconstructed author's perspective, or
the main chapter's reading flow.

## Draft-wide style authority

Before outlining or drafting, load the active draft's `style-lock.md`. Apply it
through revision and check the completed chapter against it before delivery.
Chapter-local instructions may narrow subject matter and chapter boundaries,
but they may not silently override the draft-wide narrator, chronology,
evidence, or prose rules. Any proposed book-wide change must be resolved in the
style lock rather than introduced in one chapter alone.

## Approved and working baselines

An approved manuscript remains authoritative until explicit editorial approval
replaces it. A later unapproved revision may be used as a working comparison
baseline after it passes its required audits, but that use does not promote it
or change the approved manuscript pointer.

Every synthesis, style audit, or continuity audit that performs a cross-chapter
comparison must record each baseline's chapter number, revision, exact
repository-relative path, baseline kind (`approved` or `working`), and SHA-256.
“Earlier chapters” without those identifiers is not a reproducible baseline.

## Optional working-revision control record

The existing top-level chapter `status` and `approved_manuscript` fields remain
unchanged. When a new revision actually exists, project control may add this
optional sibling mapping. Uppercase values below are field-type tokens, not
literal values:

```yaml
working_revision:
  revision: REVISION_NUMBER
  status: evidence_reviewed
  artifacts:
    evidence_synthesis:
      path: REPOSITORY_RELATIVE_PATH
      sha256: SHA256_HEX
    outline:
      path: REPOSITORY_RELATIVE_PATH
      sha256: SHA256_HEX
    manuscript:
      path: REPOSITORY_RELATIVE_PATH
      sha256: SHA256_HEX
  comparison_baselines:
    - chapter: CHAPTER_NUMBER
      revision: REVISION_NUMBER
      kind: approved_or_working
      path: REPOSITORY_RELATIVE_PATH
      sha256: SHA256_HEX
```

`working_revision.status` uses an existing `allowed_statuses` value and advances
independently of the top-level chapter status. It remains `evidence_selected`
until synthesis validation passes, then becomes `evidence_reviewed`. Add an
artifact key only after that artifact exists, and never replace or overload
`approved_manuscript` with an unapproved revision.
