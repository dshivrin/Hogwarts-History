# Hogwarts: A History — Authoring Layer

This directory is the isolated workspace for constructing editions of
*Hogwarts: A History*. It sits on top of the existing research corpus without
copying or rewriting it.

```text
RESEARCH / EVIDENCE LAYER (existing repository; read-only to authoring)
                               ↓
AUTHORING LAYER (`authoring/`; editorial and manuscript work)
```

## Layer 1 — Research

The existing repository stores evidence, provenance, sources, validation,
extraction logic, generated reference views, and query infrastructure. It is
the canonical source of research records and is considered read-only by the
authoring system.

## Layer 2 — Authoring

`authoring/` stores editorial decisions, book architecture, evidence selection,
accepted chronology and continuity, chapter briefs and outlines, prose, audits,
and edition-specific project state. Authoring files may cite evidence IDs and
repository-relative source paths; they should not duplicate canonical evidence
records wholesale.

## Edition

The project now produces one unified, expanded edition. The reconstructed 1984
edition remains its historical and literary foundation, but all canonical
evidence may be considered. Later discoveries and later events are added through
clearly attributable editorial material rather than being retroactively placed
within Bathilda Bagshot's knowledge.

`authoring/editorial-policy.md` is the project-wide authority for this model.
The existing `authoring/editions/1984/` directory is retained as a legacy path
for continuity; its name no longer denotes an evidence or publication cutoff.

## Drafts

`authoring/editions/1984/drafts/draft-01/` is the first manuscript and style
attempt. Substantially different voices or editorial approaches should become
sibling drafts such as `draft-02/` or `draft-03/`; a completed draft should not
be silently overwritten to try a different approach.

Chapter workspaces are created only when a chapter enters preparation. Existing
workspaces remain in the legacy path and are governed by the unified policy.
