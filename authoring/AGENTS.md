# Authoring Scope Instructions

These instructions apply to every agent working anywhere under `authoring/`.
The repository outside this directory is the canonical research/evidence layer.
Authoring work consumes that layer; it does not rewrite it.

## Allowed work

An authoring agent may:

- read any existing repository research or evidence file;
- run existing read-only evidence queries and searches;
- inspect canonical source YAML;
- inspect PDFs and external snapshots when necessary;
- inspect generated appendices, open questions, and duplicate or corroboration data;
- create or modify files inside `authoring/` when the assigned authoring task permits it.

## Protected scope

Unless a task explicitly overrides this protection, an authoring agent must not
modify anything outside `authoring/`. This restriction includes, but is not
limited to:

```text
sources/
pdfs/
resources/
project-control/
book-seed/
appendix/
docs/
scripts/
tests/
Justfile
requirements.txt
requirements-fanfic.txt
```

All other existing repository infrastructure outside `authoring/` is protected
as well. Do not run generators, formatters, or completion workflows that may
rewrite protected files unless a task explicitly authorizes those changes.

## Narration editing

Before preparing, creating, improving, or editing narration, making a chapter
TTS-ready, or editing `narration.md`, read and follow
`authoring/audio/AGENT-NARRATION-EDITING.md`. If a persistent `narration.md`
already exists, preparation must never overwrite or replace it.

## Research problems found during authoring

If authoring work reveals bad or contradictory evidence, a likely extraction
error, stale metadata, missing provenance, or a research gap, record it in the
relevant authoring chapter workspace or audit output. Do not silently repair,
normalize, or otherwise alter the research layer.

A future controlled process may accept research-correction submissions. Until
then, preserve the boundary: research is read-only; authoring observations stay
inside `authoring/`.
