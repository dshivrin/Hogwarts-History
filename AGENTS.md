# Project instructions

## Canonical repository runtime

Repository Python tooling uses `.venv/bin/python`. Do not use `python` or
`python3` to determine whether repository dependencies are installed. Prefer
supported root `just` recipes when available. The audiobook and fan-work
environments remain separate and keep their own interpreter rules.

Before writing a repository helper script:

1. inspect the root `Justfile`;
2. inspect the active tooling and runtime documentation;
3. search the existing `scripts/` tree.

Routine repository operations must use permanent tooling when it exists. Do not
create disposable Python files for supported queries, status inspection, hash
verification, validation, or extraction.

`authoring/AGENTS.md` governs every task under `authoring/` and takes
precedence for authoring work. Do not modify the research/evidence layer
outside `authoring/` while preparing narration.

## Local audiobook narration

The local narration tooling is in `authoring/audio/`. Read
`authoring/audio/README.md` and the canonical settings before changing or
running it. Its current engine is `mlx-community/Kokoro-82M-bf16` through
MLX-Audio, using British English language code `b`.

### Request routing and configured defaults

Codex, rather than the Python renderer, resolves natural-language chapter
references to the corresponding persistent `narration.md`. Treat these terms
as follows:

- **Normal render:** resolve the chapter's existing `narration.md`; omit
  `--voice` and `--speed` so `narration-settings.yaml` supplies the canonical
  values.
- **Override render:** pass only the voice and/or speed explicitly named by the
  user. Normal render validation accepts a non-empty identifier; the Kokoro
  backend is authoritative for whether that voice actually exists.
- **Opening sample:** invoke `sample NARRATION.md` with fresh output paths. It
  contains the opening headings and as much of the first one or two prose
  paragraphs as fits within approximately 30 seconds at sentence boundaries.
- **Paragraph sample:** invoke `sample NARRATION.md --paragraph N`; paragraph
  numbers count prose paragraphs only, not headings, and the complete selected
  paragraph is not subject to the opening-sample duration cap.

Map short requests directly:

```text
generate chapter 3 audio             -> render current narration.md
regenerate chapter 3 audio           -> fresh render of current narration.md
generate sample of chapter 3         -> opening sample
regenerate sample of chapter 3       -> fresh opening sample
generate paragraph 6 of chapter 3    -> paragraph sample --paragraph 6
regenerate paragraph 6 of chapter 3  -> fresh paragraph sample --paragraph 6
```

`generate` and `regenerate` both synthesize fresh audio from the current
`narration.md`; neither may create, replace, or refresh that manuscript. If it
is absent, stop cleanly and report that narration must be prepared first.

The fixed audition batch remains restricted to `bm_daniel`, `bm_george`,
`bf_alice`, and `bf_emma`. Normal explicit overrides may use another Kokoro
identifier, such as `bm_lewis`. Accepted speeds are from `0.90` through `1.05`.
Do not claim subjective voice differences without listening to complete files.

### When the user asks for chapter audio or a sample

For each requested chapter:

1. Keep the approved book manuscript and narration manuscript distinct. The
   approved manuscript is authoritative for the written book. The durable
   `narration.md` beside it is authoritative for speech and may be edited for
   performance without changing the book manuscript.
2. Preparation is a separate, explicit operation. Only when the user asks to
   prepare narration, create it from the approved manuscript with:

   ```bash
   authoring/audio/.venv/bin/python authoring/audio/scripts/narrate.py prepare \
     APPROVED_CHAPTER.md --output CHAPTER_DIRECTORY/narration.md
   ```

   Never delete or regenerate an existing narration manuscript merely to bring
   it back into equality with the approved manuscript.
3. Keep canonical voice and speed in `narration-settings.yaml`. Normal requests
   omit both CLI flags. Add only an explicitly requested `--voice` and/or
   `--speed` override; do not hard-code configured defaults in request routing.
4. Render or sample one chapter at a time to fresh timestamped paths under
   `authoring/audio/output/`, using the existing output conventions. A normal
   full render is:

   ```bash
   HF_HUB_OFFLINE=1 authoring/audio/.venv/bin/python \
     authoring/audio/scripts/narrate.py render CHAPTER_DIRECTORY/narration.md \
     --output authoring/audio/output/RUN/CHAPTER.wav \
     --listening-copy authoring/audio/output/RUN/CHAPTER.mp3 \
     --manifest authoring/audio/output/RUN/render-manifest.yaml \
     --chunk-manifest authoring/audio/output/RUN/chunks/chunk-manifest.yaml
   ```

   Omit `HF_HUB_OFFLINE=1` only when a required model/voice artifact has not
   yet been downloaded. Never substitute a CPU fallback for an MLX run.
   An opening sample uses the same output flags with `sample` instead of
   `render`; a paragraph sample additionally passes `--paragraph N`.
5. `narration-provenance.yaml` records the approved manuscript hash used for
   initial preparation, the immutable prepared narration hash, and the current
   narration hash. The current hash starts at the prepared baseline and is
   updated after each successful render. If the approved manuscript has changed,
   the renderer must warn and record the drift in its manifest, but it must not
   overwrite the narration manuscript or block rendering.
6. Before reporting success, run the audio tests, verify the generated WAV
   with `ffprobe` and a full `ffmpeg` decode, and record the chapter source and
   output hashes, Python/package versions, model/revision, voice, language,
   speed, duration, and MLX/Metal runtime evidence in a versioned record under
   `authoring/audio/records/`. If the current renderer cannot capture a
   required runtime fact, add that auditable capability before treating the
   render or sample as complete.
7. Keep generated audio, model caches, and virtual environments out of version
   control. Commit only the reproducibility record and deliberate tooling or
   guide changes under `authoring/audio/`. The chapter's `narration.md` and
   `narration-provenance.yaml` are durable authoring inputs and must be tracked.
8. Do not render additional chapters, create speed variants, alter the
   pronunciation guide, or select a narrator unless the user asks. Apply a
   pronunciation substitution only after a human listener identifies and
   verifies the problem.
