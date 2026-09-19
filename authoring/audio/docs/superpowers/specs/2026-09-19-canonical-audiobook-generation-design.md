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
- add a `sample NARRATION.md` command alongside `render`;
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

## Responsibility boundary

### Codex project instructions

`AGENTS.md` owns natural-language interpretation and repository discovery.
For requests such as:

```text
generate chapter 3 audio
generate sample of chapter 3
regenerate chapter 3 audio
regenerate sample of chapter 3
```

Codex must:

1. resolve the referenced chapter directory under the active authoring
   structure;
2. require the persistent `narration.md` to exist;
3. select a new timestamped output directory under `authoring/audio/output/`;
4. invoke `render` for a full chapter or `sample` for an opening sample;
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
selects an opening excerpt, then delegates synthesis and output production to
the same internal rendering path.

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

Canonical configuration validation will require a non-empty voice identifier
and a numeric speed in the supported `0.90` through `1.05` range. Explicit
render/sample overrides use the same range. The fixed four-voice audition
workflow retains its own approved-combination validation, while direct
render/sample overrides accept a valid Kokoro voice identifier such as the
user-approved `bm_lewis`. This prevents the audition batch policy from
incorrectly constraining an explicit one-off render.

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
shape. Sampling will supply selected opening blocks to the same downstream
chunking, synthesis, assembly, output, and evidence code rather than
reimplementing those steps.

The input narration file must exist before either command starts. A missing
file fails cleanly through the CLI error path. No render or sample code calls
`prepare_narration`.

## Sample selection

A sample is derived in memory from the single immutable snapshot read from
`narration.md`. Selection preserves original spoken text and block kinds.

The initial candidate contains:

1. opening heading blocks before the first prose paragraph, including the
   chapter title and any opening subtitle or section heading;
2. complete sentences from the beginning prose;
3. normally the complete first paragraph when it fits the target, with
   additional complete sentences considered only when useful.

The selector uses complete sentence boundaries from the existing sentence
splitter. It never paraphrases text, cuts a sentence, edits the source file, or
truncates an already-rendered waveform.

The first pass uses a conservative opening prose budget consistent with the
requested roughly 50–70-word guidance. After synthesis and assembly, the WAV
duration is inspected. If it exceeds 30 seconds, the final selected prose
sentence is removed and the sample is synthesized again. Opening heading
content is retained. Reduction continues until the duration is at most 30
seconds or no prose sentence can be removed. If headings plus the shortest
opening prose sentence still exceed the target, the command fails clearly
rather than cutting speech mid-sentence.

Retry artifacts remain within the newly selected output location and do not
alter historical runs. Only the successful final WAV, optional MP3, and final
metadata are reported as outputs.

## Manifests, provenance, and records

Full renders continue using the existing narration provenance, render
manifest, exact submitted chunk manifest, WAV/MP3 handling, runtime evidence,
and reproducibility-record workflow.

Samples use those same mechanisms. The existing render manifest gains only a
render-kind field with values `full` or `sample`, plus sample-selection facts
needed to audit the result, such as selected sentence count and final duration.
The chunk manifest continues to contain the exact strings submitted to Kokoro.
The narration entry continues to identify and hash the complete authoritative
`narration.md`, while the sample-selection metadata identifies the derived
subset. No sample-specific provenance sidecar is created.

Source-manuscript drift remains a warning recorded in metadata and never
causes narration replacement. A successful sample may update the existing
provenance `current_sha256` to the hash of the narration snapshot it used, just
as a full render does.

Timestamped directory naming remains an agent-level choice following existing
`authoring/audio/output/` conventions. The Python commands continue accepting
explicit output, listening-copy, render-manifest, and chunk-manifest paths.

## Error handling

Both commands fail before model loading when:

- the narration path is absent or unreadable;
- configured voice or speed is absent or invalid;
- an explicit override is invalid;
- the narration has no usable spoken blocks;
- a valid sentence-boundary sample cannot satisfy the duration contract.

Existing source-drift warnings remain non-fatal. Synthesis, audio encoding,
manifest, and provenance errors continue through the existing CLI error
handling rather than being hidden by a new orchestration layer.

## Documentation changes

The root `AGENTS.md` will distinguish:

- **normal audiobook render:** Codex resolves the narration manuscript and
  output paths, while voice and speed come from canonical configuration;
- **explicit override/audition render:** user-specified voice and/or speed are
  passed for that run and replace the corresponding configured value.

It will also state that missing narration stops generation and requires the
separate preparation operation. The audio README will document optional
render overrides and the new sample command without presenting natural-language
chapter discovery as a Python feature.

## Tests

Tests will cover only the new behavior:

- canonical configured voice and speed are used when render flags are absent;
- voice-only, speed-only, and combined CLI overrides take precedence;
- sample selection retains opening headings and only complete prose sentences;
- an over-duration sample removes whole trailing sentences and regenerates;
- no waveform truncation is used to meet the duration target;
- sample and full rendering use the same pronunciation, chunking, synthesis,
  assembly, output, provenance, and manifest path;
- missing `narration.md` fails and never invokes preparation;
- existing full-render output and manifest behavior remains compatible;
- sample manifests identify the render kind and exact selected/submitted text.

Tests will use the existing fake Kokoro model and temporary files. They will
not add Python chapter-discovery tests or require a real model download.

## Success criteria

The change is complete when:

- normal full and sample CLI invocations work without `--voice` or `--speed`;
- changing canonical configuration changes subsequent normal runs without code
  or instruction edits;
- explicit overrides affect only the requested run;
- full renders still use the existing canonical path;
- samples are produced through shared rendering code and contain only complete
  opening sentences at no more than approximately 30 seconds;
- missing narration never causes implicit preparation;
- the focused tests and existing audio test suite pass;
- documentation and governing instructions accurately describe the resulting
  behavior.
