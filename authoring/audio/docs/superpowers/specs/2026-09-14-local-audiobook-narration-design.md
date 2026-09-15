# Local Audiobook Narration Prototype Design

## Purpose

Build a reproducible, entirely local audiobook narration prototype for the
1984 edition manuscript. The prototype uses Kokoro-82M through MLX-Audio on an
Apple Silicon M4 Pro and stops after a British-voice narrator audition. It must
not render the complete chapter or change manuscript prose.

## Scope and protection

All new project files, tests, fixtures, settings, manifests, generated audio,
and disposable runtime material belong under `authoring/audio/`. Existing
files elsewhere in the repository are read-only, including the source
manuscript and `hogwarts-history-repository-handoff.md`.

The current checkout is the execution workspace. A separate Git worktree is
not appropriate because the existing `authoring/` tree is untracked and would
not be present in a new worktree. Before implementation, record the Git status
and checksum the pre-existing outside-scope untracked handoff document. At the
end, compare status and checksum and inspect all tracked diffs outside
`authoring/audio/`.

The prototype will create this structure:

```text
authoring/audio/
├── .gitignore
├── README.md
├── narration-settings.yaml
├── pronunciation-guide.yaml
├── requirements.txt
├── requirements-lock.txt
├── docs/
│   └── superpowers/
│       ├── specs/
│       └── plans/
├── fixtures/
│   └── audition-excerpt.txt
├── scripts/
│   └── narrate.py
├── tests/
│   └── test_narrate.py
├── samples/
│   └── audition-manifest.yaml
└── output/
```

The `.gitignore` will ignore `.venv/`, Python caches, model and Hugging Face
caches, scratch files, all files under `output/`, and generated audio formats
under `samples/`. It will not ignore the source fixture, settings,
pronunciation guide, test suite, documentation, or sample manifest.

## Runtime and dependencies

Create an isolated CPython 3.12 virtual environment at
`authoring/audio/.venv`. Do not install anything into the repository's core
environment. Install the stable, exact top-level dependencies:

- `mlx-audio==0.5.3`
- `misaki[en]==0.9.4`
- `en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl#sha256=1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85`
- `PyYAML==6.0.2`

Use `pip freeze` after successful generation to record the complete resolved
environment in `requirements-lock.txt`. The short `requirements.txt` remains
the authoritative, human-maintained top-level dependency contract.

Use `espeakng-loader`, installed by the Misaki English extra, for the English
out-of-dictionary phonemization fallback. Do not install a separate Homebrew
`espeak-ng` unless runtime verification proves the bundled fallback unusable.
Install Homebrew `ffmpeg` because the machine currently lacks it and the
prototype needs reliable decoding checks and optional listening-copy
conversion.

Model weights and voice data are downloaded through the Hugging Face cache and
remain outside version control. After their first download, narration must run
locally without a paid API or subscription.

## Canonical configuration

`narration-settings.yaml` records:

- engine `kokoro`;
- model `mlx-community/Kokoro-82M-bf16`;
- language `british-english` and language code `b`;
- `voice: null` and `speed: null` until the user selects the narrator;
- configurable chapter, section, paragraph, opening, and closing pauses;
- WAV as the lossless intermediate and MP3 as the optional listening copy;
- a conservative semantic chunk target appropriate for Kokoro.

The audition command supplies voice and speed explicitly without writing them
back into canonical settings.

`pronunciation-guide.yaml` contains a versioned list of exact, documented
substitutions. A substitution identifies the manuscript term, the private
narration-layer replacement, and the reason it is required. The guide starts
empty unless listening proves that a term in the audition passage is
mispronounced. Candidate terms that are not present in the passage are not
claimed as tested and receive no speculative substitution.

## Manuscript preparation

The narration script exposes pure preprocessing functions that can be tested
without importing MLX-Audio. Processing occurs in this order:

1. Read UTF-8 Markdown.
2. Remove a leading YAML front-matter block.
3. Remove all HTML comments, including multiline evidence comments.
4. Recognize ATX headings and retain their visible text as typed chapter or
   section transitions rather than reading Markdown symbols.
5. Remove non-spoken Markdown formatting while preserving visible wording and
   punctuation.
6. Form paragraph-aware speech blocks.
7. Apply pronunciation substitutions only to the in-memory narration text.
8. Split an oversized paragraph at sentence boundaries. Never split inside a
   sentence; fail clearly if one sentence exceeds the safe model limit.

The source manuscript is never rewritten. The first 300–500 prose words used
for the audition are copied verbatim, with original paragraph boundaries, into
`fixtures/audition-excerpt.txt`. Headings, comments, and development metadata
are omitted from that fixture. A test derives the same passage from the
manuscript preprocessing path and requires exact equality with the fixture,
so every voice receives identical source text.

## Synthesis and audio assembly

`scripts/narrate.py` provides two command paths:

- `render` reads a Markdown manuscript and produces one configured narration.
- `audition` reads the preserved plain-text fixture and renders multiple
  voice/speed combinations in one process.

Both paths share preprocessing, chunking, synthesis, and assembly code. The
audition path loads `mlx-community/Kokoro-82M-bf16` exactly once, then reuses
the loaded model for every voice and chunk. Every call uses `lang_code="b"`
and the explicit sample speed. No stochastic setting is varied between voices.

The script concatenates generated chunk waveforms in memory. It inserts no
extra pause between ordinary model-generated sentences. It inserts a short
continuation gap only when a long paragraph had to be split, and configurable
silence after paragraph, section-heading, and chapter-heading blocks. The file
begins and ends with explicit silence so speech cannot be clipped at its
boundaries. It writes mono PCM WAV at the model's native sample rate and can
ask `ffmpeg` for an MP3 listening copy.

## Audition procedure

The approved first pass consists of exactly these four samples, all at speed
`0.96` and British language code `b`:

- `bm_daniel`
- `bm_george`
- `bf_alice`
- `bf_emma`

Listen to all four before deciding whether another speed is useful. Generate
at most two additional variants, using `0.92` or `1.00`, only for voices where
the comparison would materially help the narrator decision. Do not render all
voice/speed combinations.

Each WAV filename encodes voice and speed. `samples/audition-manifest.yaml`
records, for every file:

- fixture path and SHA-256;
- Python version;
- exact `mlx-audio` and `misaki` versions;
- model identifier;
- voice;
- language code;
- speed;
- sample rate, channel count, sample count, duration, and file SHA-256;
- measured MLX device and Metal-memory evidence from the run.

## Testing and verification

Use the standard-library `unittest` runner so test tooling adds no runtime
dependency. Follow test-driven development for the script: each production
behavior begins with a focused failing test, then the smallest implementation
that passes it.

Tests cover:

- YAML front matter and multiline HTML evidence comments are absent;
- headings become correctly typed spoken transitions;
- inline Markdown symbols are not present in spoken output;
- punctuation and visible prose remain intact;
- substitutions affect narration text but not the source file;
- paragraphs split only between complete sentences;
- an overlong single sentence fails instead of being cut;
- configured pauses produce the expected sample counts;
- beginning and ending silence are present;
- audition fixture extraction exactly matches the preserved fixture;
- all audition requests share one fixture payload and one loaded model.

Integration verification must establish facts rather than infer them from an
installation:

1. Import MLX and record `mlx.core.default_device()`.
2. Load the exact Kokoro model successfully.
3. Run real synthesis and record Metal peak or active memory before and after
   generation, demonstrating that the MLX Metal backend performed work.
4. Confirm each WAV with `ffprobe` and decode it fully with `ffmpeg` using an
   error-only null output.
5. Inspect waveform duration, finite samples, non-silent content, peak level,
   opening silence, and closing silence.
6. Confirm every manifest entry has the same fixture hash and language code.
7. Run the full unit-test suite.
8. Run `git status --short`, inspect diffs outside `authoring/audio/`, and
   verify the pre-existing handoff-document checksum is unchanged.

## Human-quality review

Listen to the generated audition files rather than assigning voice traits from
their names or published grades. Report concise, comparative observations
about warmth, formality, clarity, pacing, artifacts, and suitability for calm
historical narration without selecting a final narrator.

Listen specifically for `Hogwarts`, `Muggle`, and `Muggles`, the candidate
terms present in the fixture. Report any issue and document any successful
narration-layer correction. Do not make claims about untested project terms.

Report sentences in the audition passage that sound awkward aloud. This is an
editorial observation only: do not edit the source manuscript or silently
alter the fixture.

## Stopping condition

Stop after the tested script, configuration, preserved fixture, four to six
audition WAV files, metadata manifest, verification evidence, and final report
are complete. Leave canonical `voice` and `speed` unset. Do not render the full
chapter until the user selects a narrator.
