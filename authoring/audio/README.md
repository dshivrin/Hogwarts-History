# Local audiobook narration

This directory contains the local Kokoro narration and audition tooling for the
1984 edition manuscript. It is intentionally isolated from the manuscript and
research layers. `narration-settings.yaml` supplies the canonical voice, speed,
model, language, chunking, and pause settings for normal full and sample
renders; CLI voice and speed flags are optional per-run overrides.

## Install

Use the repository's Apple Silicon CPython 3.12 and install only into the
project virtual environment:

```bash
/opt/homebrew/bin/python3.12 -m venv authoring/audio/.venv
authoring/audio/.venv/bin/python -m pip install --upgrade pip
authoring/audio/.venv/bin/python -m pip install -r authoring/audio/requirements.txt
```

The top-level dependency contract is pinned in `requirements.txt`:
`mlx-audio==0.5.3`, `misaki[en]==0.9.4`, the exact `en_core_web_sm` wheel
needed for British G2P, and `PyYAML==6.0.2`. The G2P asset is installed by the
requirements command above; it is not an extra manual spaCy step.
`requirements-lock.txt` is the complete, tested M4 Pro environment snapshot;
it records the resolved packages from the successful audition rather than
replacing the portable top-level contract.

## Manuscript roles

The pipeline keeps three distinct text records:

- **Book manuscript:** the approved chapter Markdown is authoritative for the
  written book and remains read-only during narration work.
- **Narration manuscript:** the durable `narration.md` beside the chapter is
  authoritative for speech. A human may change punctuation, wording, headings,
  sentence boundaries, whitespace, or paragraphs for performance without
  changing the book manuscript.
- **Chunk manifest:** a per-render machine record of the exact strings submitted
  to Kokoro after Markdown parsing, pronunciation substitutions, and chunking.

## Prepare, edit, and render

Prepare a narration manuscript once:

```bash
authoring/audio/.venv/bin/python authoring/audio/scripts/narrate.py prepare \
  APPROVED_CHAPTER.md --output CHAPTER_DIRECTORY/narration.md
```

Preparation removes front matter and editorial HTML comments while preserving
readable headings, paragraphs, and inline Markdown. It also creates
`narration-provenance.yaml` beside the narration manuscript. Preparation refuses
to overwrite either existing file; there is intentionally no force option.

The provenance file retains the source-manuscript path and preparation hash,
the narration's immutable `prepared_sha256`, and a `current_sha256` initialized
to that baseline and updated after each successful render. Source-manuscript
drift is emitted as a warning and recorded in the render manifest. Drift never
blocks rendering and never rewrites the narration manuscript.

After preparation, edit `narration.md` directly and render that file. The
caller supplies the manuscript and every output path; Python does not discover
chapters or active editions:

```bash
HF_HUB_OFFLINE=1 authoring/audio/.venv/bin/python \
  authoring/audio/scripts/narrate.py render CHAPTER_DIRECTORY/narration.md \
  --output authoring/audio/output/RUN/chapter.wav \
  --listening-copy authoring/audio/output/RUN/chapter.mp3 \
  --manifest authoring/audio/output/RUN/render-manifest.yaml \
  --chunk-manifest authoring/audio/output/RUN/chunks/chunk-manifest.yaml
```

Omitting `--voice` and `--speed` uses the canonical configured defaults for a
normal render. Add only the values explicitly requested for an override, for
example `--voice bm_lewis`, `--speed 0.92`, or both. Normal render validation
requires a non-empty voice identifier and an in-range speed; the Kokoro backend
is authoritative for whether an explicit voice identifier actually exists.

Create an opening sample through the same synthesis and output path:

```bash
HF_HUB_OFFLINE=1 authoring/audio/.venv/bin/python \
  authoring/audio/scripts/narrate.py sample CHAPTER_DIRECTORY/narration.md \
  --output authoring/audio/output/RUN/sample.wav \
  --listening-copy authoring/audio/output/RUN/sample.mp3 \
  --manifest authoring/audio/output/RUN/render-manifest.yaml \
  --chunk-manifest authoring/audio/output/RUN/chunks/chunk-manifest.yaml
```

The opening candidate contains the opening headings plus the first two prose
paragraphs when present. If it exceeds approximately 30 seconds, complete
trailing prose sentences are removed and resynthesized until it fits. The
waveform is never cut mid-sentence and `narration.md` is never modified.

Select a complete prose paragraph by its one-based prose-only number:

```bash
HF_HUB_OFFLINE=1 authoring/audio/.venv/bin/python \
  authoring/audio/scripts/narrate.py sample CHAPTER_DIRECTORY/narration.md \
  --paragraph 6 \
  --output authoring/audio/output/RUN/paragraph-006.wav \
  --listening-copy authoring/audio/output/RUN/paragraph-006.mp3 \
  --manifest authoring/audio/output/RUN/render-manifest.yaml \
  --chunk-manifest authoring/audio/output/RUN/chunks/chunk-manifest.yaml
```

Headings do not count as paragraphs. Paragraph samples retain the complete
selected paragraph and are not limited by the opening-sample duration cap.
Use fresh timestamped output directories for both `generate` and `regenerate`.
Both operations synthesize from the current persistent narration manuscript.
If `narration.md` is absent, stop and run `prepare` only as a separate explicit
operation; generation never prepares or replaces it automatically.

The normal editorial loop is:

```text
approve book manuscript
→ prepare narration manuscript once
→ edit narration manuscript
→ render
→ listen
→ edit narration manuscript
→ render again to a new output directory
```

Pronunciation-guide substitutions remain an implementation-level step and are
not written into the prepared narration manuscript.

## Test and audition commands

```bash
authoring/audio/.venv/bin/python -m unittest discover -s authoring/audio/tests -v
authoring/audio/.venv/bin/python authoring/audio/scripts/narrate.py audition \
  --fixture authoring/audio/fixtures/audition-excerpt.txt \
  --sample bm_daniel=0.96 --sample bm_george=0.96 \
  --sample bf_alice=0.96 --sample bf_emma=0.96
```

The recorded run used CPython `3.12.13`, `mlx-audio 0.5.3`, `misaki 0.9.4`,
and `PyYAML 6.0.2`; `/opt/homebrew/bin/ffmpeg` and `ffprobe` were version
`9.0.1`. It used `mlx-community/Kokoro-82M-bf16` at revision
`a71e4d38b236d968966a2002c4c895dbd12b1c3c`. Verify an existing WAV without
regenerating it with:

```bash
/opt/homebrew/bin/ffprobe -v error -show_entries format=duration \
  -show_entries stream=codec_name,sample_rate,channels -of json SAMPLE.wav
/opt/homebrew/bin/ffmpeg -v error -i SAMPLE.wav -f null -
```

The audition fixture is the exact 442-word first-five-paragraph excerpt. Do
not edit it independently of the manuscript-extraction tests. The approved
first pass uses British language code `b`, the Kokoro model
`mlx-community/Kokoro-82M-bf16`, and the fixed audition whitelist
`bm_daniel`, `bm_george`, `bf_alice`, and `bf_emma` at speed `0.96`. That
whitelist applies to the audition batch, not to normal render overrides.

## Files, outputs, and offline reuse

`narration-settings.yaml` is the canonical configuration: `engine`, `model`,
`language`, `lang_code`, voice, speed, pauses, chunk target, and WAV/MP3 output
formats are shared by normal full and sample renders. The current configured
defaults are `bm_george` at `0.96`; change them only in that file so short
requests automatically follow future canonical selections. The versioned
pronunciation guide starts empty and must contain only tested, documented
narration-layer substitutions.

Generated output, model caches, Python caches, and generated sample audio are
ignored by `.gitignore`; `output/.gitkeep` preserves the output directory.
After the initial successful download has placed the model and requested voice
files in the local Hugging Face cache, the same audition can be rerun without
network access. To enforce that condition (and fail rather than download if a
required cached artifact is missing), prefix the normal CLI invocation with
`HF_HUB_OFFLINE=1`, for example:

```bash
HF_HUB_OFFLINE=1 authoring/audio/.venv/bin/python authoring/audio/scripts/narrate.py audition \
  --fixture authoring/audio/fixtures/audition-excerpt.txt \
  --sample bm_daniel=0.96 --sample bm_george=0.96 \
  --sample bf_alice=0.96 --sample bf_emma=0.96
```

The revision resolver first uses the loaded model/cache path; if it cannot
discover a revision locally, its best-effort Hub lookup fails harmlessly in
offline mode and does not prevent a cached render. Keep the virtual environment
and caches under their documented paths, and never rewrite the source
manuscript as part of narration preparation.

## Human listening gate

Technical validation does not establish subjective voice quality, pacing,
pronunciation, or the absence of audible artifacts. Listen to complete files
before making editorial or pronunciation-guide changes. Keep
`pronunciation-guide.yaml` limited to problems a human listener has identified
and verified.
