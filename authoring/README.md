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

## Editions

The current target is `authoring/editions/1984/`, a reconstructed edition whose
editorial knowledge cutoff is approximately 1984. A future edition such as
`authoring/editions/2026/` may use the same research corpus while applying a
different historical scope, chronology, annotation scheme, and set of editorial
decisions. No 2026 edition has been created yet.

## Drafts

`authoring/editions/1984/drafts/draft-01/` is the first manuscript and style
attempt. Substantially different voices or editorial approaches should become
sibling drafts such as `draft-02/` or `draft-03/`; a completed draft should not
be silently overwritten to try a different approach.

Chapter workspaces are created only when a chapter enters preparation. The
current draft therefore has an empty `chapters/` directory.
