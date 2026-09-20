# Agent Narration Editing Guide

## Purpose

Use this guide whenever preparing, creating, improving, or editing a chapter's
durable `narration.md`, including requests to make a chapter TTS-ready. The goal
is the strongest reasonable first-pass narration manuscript before a human
listener begins paragraph-by-paragraph tuning.

The written chapter manuscript is authoritative for the book. `narration.md`
is authoritative for spoken delivery. Narration may differ when natural speech
requires it, but it must preserve factual claims, qualifications, chronology,
quotations, argument, tone, and meaning. Narration editing is not permission to
rewrite the chapter.

## Protect existing narration

Before preparing narration:

1. Locate the chapter.
2. Check whether its persistent `narration.md` already exists.

If it exists, do not run preparation again and do not overwrite it. Edit the
existing durable narration manuscript.

If it does not exist, identify the approved or final chapter manuscript and run
the canonical preparation workflow once:

```bash
authoring/audio/.venv/bin/python authoring/audio/scripts/narrate.py prepare \
  APPROVED_CHAPTER.md --output CHAPTER_DIRECTORY/narration.md
```

Then edit the resulting persistent `narration.md`. Manual narration work must
survive every later `render` or `sample` operation.

## Editing philosophy

Treat punctuation and structure as performance controls. Prefer the smallest
change that improves speech, in this order:

```text
punctuation
→ sentence boundary
→ paragraph boundary
→ minor word-order change
→ small narration-only rewrite
```

Do not jump directly to rewriting prose.

### Punctuation

- `.` creates a normal sentence stop and delivery reset.
- `,` creates a short natural pause.
- `;` creates a stronger internal pause while keeping ideas connected.
- `:` creates a deliberate pause before an explanation, definition, or list.
- `—` creates a noticeable rhetorical break or emphasis.
- A paragraph break creates stronger separation and a delivery reset.

These are tendencies, not guaranteed timing instructions. Final judgment comes
from listening.

### Sentence length

Long written sentences may sound flat, rushed, or choose poor breathing points.
Split a sentence when it contains several distinct ideas or dependent clauses,
or when a clear conceptual boundary offers a natural reset. Prefer semantic
splits over arbitrary cuts. Do not turn elegant prose into tiny, robotic
sentences.

### Paragraph boundaries

Split or join narration paragraphs when it improves spoken structure. A change
of period or topic, movement from evidence to interpretation, major contrast,
important conclusion, or deliberate rhetorical emphasis may justify a stronger
paragraph reset. Do not add excessive paragraph breaks merely to force silence.

### Headings

Every heading in `narration.md` becomes spoken audio. Retain headings that help
a listener; remove headings that interrupt narration without helping
comprehension; consolidate redundant adjacent headings; and simplify spoken
heading structure when useful. Never remove the chapter title. Do not change
the written manuscript when changing narration headings. Minor subsection
headings should not automatically survive merely because they help visual
navigation on the page.

### Lists

Make spoken list structure unambiguous through punctuation and sentence
structure. A colon may help introduce a list, and commas should clearly divide
its items. Do not unnecessarily rewrite list content.

### Spoken syntax and emphasis

If punctuation does not correct emphasis, a minor word-order change is allowed.
For example, moving the key idea toward the end of a clause may improve natural
stress. Preserve the original meaning and tone.

### Quotations

Preserve genuine quotations accurately. Do not alter quoted wording merely to
improve TTS. Surrounding punctuation, paragraph placement, or attribution
placement may be adjusted for clearer spoken delivery.

### Pronunciation

Do not clutter `narration.md` with phonetic spellings. Prefer the project's
pronunciation guide for predictable substitutions. Use narration edits for
rhythm, punctuation, sentence and paragraph structure, headings, and deliberate
spoken phrasing. Do not make speculative pronunciation changes.

Inspect dates, centuries, Roman numerals, abbreviations, initials, unusual
names, invented magical terms, Latin, and symbols that may sound awkward. Do
not automatically rewrite them; first decide whether the pronunciation guide
is the correct solution.

### Repetition

Repeated language can be much more obvious aloud. Preserve deliberate
rhetorical repetition. If repetition appears accidental and likely to sound
robotic, make only conservative narration-specific adjustments.

## Editorial boundary

Good narration edits include punctuation changes, splitting one long sentence,
joining artificially short sentences, changing paragraph boundaries, removing
or consolidating redundant spoken headings, minor word-order changes, and small
spoken-language adjustments that preserve meaning.

Do not add evidence, change claims, remove qualifications, change chronology,
substantially change tone, rewrite whole arguments, alter quotations, or invent
factual transitions. If an edit changes meaning rather than delivery, it
belongs in the written manuscript first.

## Required preparation workflow

When asked to prepare narration for a chapter:

1. Locate the approved chapter manuscript.
2. Locate the existing `narration.md`, if any.
3. If narration does not exist, run canonical `prepare` once.
4. Read the written manuscript and narration side by side.
5. Perform a conservative, TTS-focused editorial pass.
6. Optimize punctuation, sentence length, paragraph structure, headings, lists,
   and spoken syntax.
7. Preserve meaning, claims, qualifications, quotations, chronology, and tone.
8. Keep pronunciation hacks in the pronunciation guide rather than the
   narration manuscript.
9. Perform a semantic and editorial safety review against the written
   manuscript.
10. Leave the persistent `narration.md` ready for listening.

The safety review is not an equality check. Different punctuation, sentence
boundaries, paragraph boundaries, and spoken heading structure are expected.
Its purpose is only to catch accidental changes in meaning.

## Listening is a separate loop

Produce a strong first narration version, then stop. Do not repeatedly render
every paragraph in pursuit of subjective intonation unless explicitly asked.
The later listening loop uses focused requests such as:

```text
generate sample of chapter 1
generate paragraph 6 of chapter 1
regenerate paragraph 6 of chapter 1
```

A human may then refine `narration.md`; future generation must continue using
that edited persistent manuscript.
