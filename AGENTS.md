# Project instructions

`authoring/AGENTS.md` governs every task under `authoring/` and takes
precedence for authoring work. Do not modify the research/evidence layer
outside `authoring/` while preparing narration.

## Local audiobook narration

The local narration tooling is in `authoring/audio/`. Read
`authoring/audio/README.md` and the canonical settings before changing or
running it. Its current engine is `mlx-community/Kokoro-82M-bf16` through
MLX-Audio, using British English language code `b`.

### Available narrator choices

Use only these approved Kokoro voice identifiers:

- `bm_daniel`
- `bm_george`
- `bf_alice`
- `bf_emma`

Accepted speeds are from `0.90` through `1.05`. The initial shared audition
used all four voices at `0.96`; its files and measured facts are in
`authoring/audio/samples/`. Do not claim subjective voice differences without
listening to the complete files.

### When the user asks for a full chapter

Require the user to name the chapter source, voice, and speed explicitly. A
concise request such as this is sufficient:

> Render `<chapter markdown path>` with `<voice>` at `<speed>` using the local
> narration workflow.

For each requested chapter:

1. Treat the Markdown source as read-only. Never rewrite it for spoken
   delivery; report awkward wording separately.
2. Keep canonical `voice: null` and `speed: null` in
   `narration-settings.yaml` unless the user specifically asks to set their
   permanent selection. Pass the requested values only to the render command.
3. Render one chapter at a time to a new path under
   `authoring/audio/output/`, for example:

   ```bash
   HF_HUB_OFFLINE=1 authoring/audio/.venv/bin/python \
     authoring/audio/scripts/narrate.py render CHAPTER.md \
     --output authoring/audio/output/CHAPTER.wav \
     --voice VOICE --speed SPEED \
     --listening-copy authoring/audio/output/CHAPTER.mp3
   ```

   Omit `HF_HUB_OFFLINE=1` only when a required model/voice artifact has not
   yet been downloaded. Never substitute a CPU fallback for an MLX run.
4. Before reporting success, run the audio tests, verify the generated WAV
   with `ffprobe` and a full `ffmpeg` decode, and record the chapter source and
   output hashes, Python/package versions, model/revision, voice, language,
   speed, duration, and MLX/Metal runtime evidence in a versioned record under
   `authoring/audio/records/`. If the current renderer cannot capture a
   required runtime fact, add that auditable capability before treating the
   full render as complete.
5. Keep generated audio, model caches, and virtual environments out of version
   control. Commit only the reproducibility record and deliberate tooling or
   guide changes under `authoring/audio/`.
6. Do not render additional chapters, create speed variants, alter the
   pronunciation guide, or select a narrator unless the user asks. Apply a
   pronunciation substitution only after a human listener identifies and
   verifies the problem.
