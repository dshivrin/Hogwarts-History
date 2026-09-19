# Canonical Audiobook Generation Design

## Purpose

Make normal audiobook generation from a persistent `narration.md` concise and
configuration-driven. Codex resolves natural-language chapter references and
invokes the existing audio CLI; the Python audio pipeline continues to operate
on explicit narration-manuscript paths.

The normal configured narrator is `bm_george` at speed `0.96`. These values
live only in `narration-settings.yaml`. An explicit CLI or user-requested
override takes precedence without changing the canonical configuration.

## Scope

This change extends the existing implementation rather than adding a chapter
orchestration layer.

It will:

- make canonical voice and speed concrete values in
  `authoring/audio/narration-settings.yaml`;
- make `render --voice` and `render --speed` optional overrides;
- add a `sample NARRATION.md` command alongside `render`, supporting an
  opening sample by default and one prose paragraph through `--paragraph N`;
- share the existing Markdown parsing, pronunciation, chunking, Kokoro
  synthesis, semantic-pause assembly, WAV/MP3 output, provenance, manifest,
  and validation mechanisms;
- update project instructions so Codex maps short chapter requests to the
  persistent narration manuscript and chooses fresh output paths using the
  existing timestamped conventions.

It will not:

- add chapter-number, edition, manuscript, or output-directory discovery to
  Python;
- create a second full-chapter renderer or chapter orchestration workflow;
- automatically prepare a missing narration manuscript;
- rewrite, regenerate, truncate, or otherwise edit `narration.md`;
- create parallel provenance or reproducibility schemas.

This round also excludes special title or section performance, title sound
effects, MiniMax-generated assets, music, ambience, cue mixing, crossfades,
subtitle-removal editorial rules, and broader mastering changes. Those remain
future work after the narration manuscripts and targeted sample workflow are
comfortable to use.

## Responsibility boundary

### Codex project instructions

`AGENTS.md` owns natural-language interpretation and repository discovery.
For requests such as:

```text
generate chapter 3 audio
generate sample of chapter 3
regenerate chapter 3 audio
regenerate sample of chapter 3
generate paragraph 6 of chapter 3
regenerate paragraph 6 of chapter 3
```

Codex must:

1. resolve the referenced chapter directory under the active authoring
   structure;
2. require the persistent `narration.md` to exist;
3. select a new timestamped output directory under `authoring/audio/output/`;
4. invoke `render` for a full chapter, `sample` for an opening sample, or
   `sample --paragraph N` for a targeted prose paragraph;
5. omit voice and speed arguments for a normal run so configuration supplies
   them;
6. pass only user-requested voice or speed overrides;
7. run the existing verification and reproducibility steps appropriate to the
   output type.

`generate` and `regenerate` have the same runtime meaning: create fresh audio
from the current narration manuscript. Neither operation may call `prepare` or
replace an existing narration manuscript. Preparation remains a distinct,
explicit user operation.

### Python audio CLI

`authoring/audio/scripts/narrate.py` receives a concrete narration path and
output paths. It does not know about chapter numbers or editions.

The existing `render NARRATION.md` command remains the only full-chapter
rendering path. The new `sample NARRATION.md` command is a small sibling that
selects an opening excerpt by default or one prose paragraph when passed
`--paragraph N`, then delegates synthesis and output production to the same
internal rendering implementation.

## Canonical configuration and overrides

`narration-settings.yaml` will contain:

```yaml
voice: bm_george
speed: 0.96
```

For both `render` and `sample`, each setting resolves independently:

```text
explicit CLI value
-> otherwise narration-settings.yaml value
```

Thus a request may override only speed, only voice, or both. The resolved
values are recorded in the existing render manifest. Overrides never write
back to `narration-settings.yaml`.

The parser-level `--voice` and `--speed` arguments become optional. A shared
CLI-boundary resolver produces concrete values before calling the existing
internal rendering functions. `run_render` continues receiving a concrete
voice and speed so its current contract, tests, and task-local callers do not
change unnecessarily. The new sample path uses the same resolver.

The runtime's existing supported speed range of `0.90` through `1.05` remains
in effect for canonical settings and explicit overrides. This refactor does
not introduce or broaden that policy.

Voice validation is separated by purpose. The fixed four-voice audition
workflow retains its approved-combination validation. Normal render, opening
sample, and paragraph sample operations instead validate a non-empty Kokoro
voice identifier independently, so an explicit one-off override such as
`bm_lewis` is not rejected merely because it is outside the audition batch.

## Shared rendering architecture

The current `run_render` implementation already performs the canonical work:

```text
narration snapshot
-> provenance inspection
-> Markdown blocks
-> pronunciation substitutions
-> sentence-aware chunks
-> Kokoro synthesis
-> semantic-pause assembly
-> PCM16 WAV
-> optional MP3
-> render and exact-chunk manifests
-> provenance current-hash update
```

The implementation will extract only the smallest internal seams needed for
reuse. Full rendering will retain its existing public behavior and manifest
compatibility, with only the approved `render_kind` extension. Opening and
paragraph sampling will supply selected blocks to the same downstream
pronunciation, chunking, synthesis, assembly, output, and evidence code rather
than reimplementing those steps.

The input narration file must exist before either command starts. A missing
file fails cleanly through the CLI error path. No render or sample code calls
`prepare_narration`.

## Immutable narration snapshot and sample selection

Every render or sample reads `narration.md` once. Both sample modes operate on
parsed blocks derived in memory from that complete immutable snapshot. No
temporary or derived Markdown file becomes the apparent narration source.

The narration path and hash in provenance and manifests always identify the
complete authoritative narration manuscript. Separate sample-selection
metadata records the subset selected for speech.

### Opening sample

The initial candidate contains:

1. opening heading blocks before the first prose paragraph, including the
   chapter title and any opening subtitle or section heading;
2. complete sentences beginning with the first prose paragraph, preferably
   including that complete paragraph when it fits naturally;
3. further complete opening sentences only when they are useful and duration
   permits.

The selector uses complete sentence boundaries from the existing sentence
splitter. It never paraphrases text, cuts a sentence, edits the source file, or
truncates an already-rendered waveform.

Natural sentence and paragraph boundaries plus the 30-second maximum determine
observable sample content. A conservative text estimate may avoid an obviously
oversized first attempt, but no fixed word-count heuristic governs selection.

The pipeline loads Kokoro once, synthesizes and assembles the candidate in
memory, and measures duration from that assembled audio. If the candidate
exceeds 30 seconds, it removes the final selected prose sentence, then
resynthesizes and reassembles the reduced candidate with the already-loaded
model. Opening headings remain included. Reduction continues until duration is
at most 30 seconds or no prose sentence can be removed. If headings plus the
shortest usable opening prose sentence still exceed the target, the command
fails clearly rather than cutting speech mid-sentence.

No rejected candidate is written as an ordinary output. Only after a candidate
is accepted may the command write the final WAV, optional MP3, manifests,
provenance update, and other normal evidence. The implementation never
truncates rendered audio to satisfy the duration limit.

### Paragraph sample

`sample NARRATION.md --paragraph N` selects the one-based Nth
`BlockKind.PARAGRAPH` from the parsed narration snapshot. Chapter and section
headings do not count toward paragraph numbering. The selector includes exactly
that prose block and does not add neighboring headings or paragraphs.

Selection occurs before pronunciation substitution. The raw selected block is
not rewritten or paraphrased, then it passes through the normal pronunciation
guide, sentence-aware chunker, synthesis, and assembly path. Consequently the
exact strings submitted to Kokoro may differ from the raw paragraph when a
documented pronunciation substitution applies; the existing chunk manifest
continues recording those submitted strings.

A paragraph sample renders the complete selected prose paragraph. It has no
30-second duration limit, although the existing chunker may split it at
sentence boundaries under the configured chunk-size rule.

## Manifests, provenance, and records

Full renders continue using the existing narration provenance, render
manifest, exact submitted chunk manifest, WAV/MP3 handling, runtime evidence,
and reproducibility-record workflow.

Samples use those same mechanisms. The existing render manifest gains a stable
`render_kind` field with values `full`, `opening_sample`, or
`paragraph_sample`, plus the sample-selection facts needed to audit the result.
An opening sample records its selected sentences and final duration. A
paragraph sample records its one-based prose paragraph number and duration.
The chunk manifest continues to contain the exact strings submitted to Kokoro.
The narration entry continues to identify and hash the complete authoritative
`narration.md`, while the sample-selection metadata identifies the derived
subset. No sample-specific provenance sidecar is created.

Source-manuscript drift remains a warning recorded in metadata and never
causes narration replacement. A successful sample updates the existing
provenance `current_sha256` to the hash of the narration snapshot it used, just
as a full render does. Rejected opening-sample candidates do not update
provenance.

Timestamped directory naming remains an agent-level choice following existing
`authoring/audio/output/` conventions. The Python commands continue accepting
explicit output, listening-copy, render-manifest, and chunk-manifest paths.

## Error handling

Both commands fail before model loading when:

- the narration path is absent or unreadable;
- configured voice or speed is absent or invalid;
- an explicit override is invalid;
- the narration has no usable spoken blocks;
- a requested prose paragraph number is outside the available range;
- an opening sample cannot satisfy the duration contract at a complete-sentence
  boundary.

Existing source-drift warnings remain non-fatal. Synthesis, audio encoding,
manifest, and provenance errors continue through the existing CLI error
handling rather than being hidden by a new orchestration layer.

## Documentation changes

The root `AGENTS.md` will distinguish:

- **normal audiobook render:** Codex resolves the narration manuscript and
  output paths, while voice and speed come from canonical configuration;
- **override render:** user-specified voice and/or speed are
  passed for that run and replace the corresponding configured value.

It will also state that missing narration stops generation and requires the
separate preparation operation, distinguish the four-voice audition batch from
normal one-off voice overrides, and route paragraph requests to
`sample --paragraph N`. The audio README will document optional render
overrides, opening samples, and paragraph samples without presenting
natural-language chapter discovery as a Python feature.

## Tests

Tests will cover only the new behavior:

- canonical configured voice and speed are used when render flags are absent;
- voice-only, speed-only, and combined CLI overrides take precedence;
- sample selection retains opening headings and only complete prose sentences;
- an over-duration sample removes whole trailing sentences and regenerates;
- no waveform truncation is used to meet the duration target;
- rejected opening-sample attempts do not write ordinary output artifacts and
  reuse one loaded model;
- prose paragraph numbering ignores headings;
- a requested paragraph selects exactly the corresponding prose block;
- paragraph samples render the complete paragraph without the opening-sample
  duration limit;
- paragraph selection precedes canonical pronunciation substitution;
- sample and full rendering use the same pronunciation, chunking, synthesis,
  assembly, output, provenance, and manifest path;
- missing `narration.md` fails and never invokes preparation;
- existing full-render output and manifest behavior remains compatible;
- manifests identify all three render kinds and record the applicable sample
  selection alongside the exact submitted chunks.

Tests will use the existing fake Kokoro model and temporary files. They will
not add Python chapter-discovery tests or require a real model download.

## Success criteria

The change is complete when:

- normal full and sample CLI invocations work without `--voice` or `--speed`;
- changing canonical configuration changes subsequent normal runs without code
  or instruction edits;
- explicit overrides affect only the requested run;
- full renders still use the existing canonical path;
- opening samples are produced through shared rendering code, retain opening
  headings, contain only complete prose sentences, and last no more than 30
  seconds;
- paragraph samples select exactly one prose paragraph before pronunciation,
  render it completely, and have no opening-sample duration limit;
- missing narration never causes implicit preparation;
- the focused tests and existing audio test suite pass;
- documentation and governing instructions accurately describe the resulting
  behavior.
