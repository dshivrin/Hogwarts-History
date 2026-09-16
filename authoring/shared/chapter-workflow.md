# Chapter Workflow

The long-term goal is an automated authoring task that handles one chapter at a
time while preserving a consistent voice and a traceable path from evidence to
prose. Automation is not implemented yet.

## Intended state machine

```text
PLANNED
↓
EVIDENCE_SELECTED
↓
EVIDENCE_REVIEWED
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

## Required order of work

The evidence-selection stage precedes outlining. An approved outline precedes
prose. The workflow must not begin with a request equivalent to “Write a chapter
about X.” Its intended logic is:

```text
research evidence
↓
curated evidence
↓
historical interpretation
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
