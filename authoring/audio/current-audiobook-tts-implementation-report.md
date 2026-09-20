# Current Audiobook/TTS Implementation Report

Investigation date: 2026-09-19

This is a read-only factual report of the audiobook/TTS implementation found in the repository. It summarizes the relevant files and behavior without reproducing the contents of the referenced files.

## Executive finding

The intended full-chapter interface is the `render` command in `authoring/audio/scripts/narrate.py`. That generic path is currently broken: its call to the WAV writer omits the required sample-rate argument. The latest verified Chapter One recording was therefore produced through a preserved task-local wrapper that supplies the missing argument in memory and adds reproducibility evidence.

No source manuscript is rewritten by the narration workflow.

## 1. Relevant project structure

```text
authoring/
├── AGENTS.md
├── editions/1984/drafts/draft-01/chapters/
│   └── 01-before-hogwarts/
│       ├── final-draft-candidate-revision-07.md  # Approved Chapter One source
│       └── narration-preflight-revision-07.md   # Narration-readiness record
└── audio/
    ├── README.md                    # Installation and audition documentation
    ├── .gitignore                   # Audio-specific ignore rules
    ├── requirements.txt             # Direct pinned dependencies
    ├── requirements-lock.txt        # Tested environment snapshot
    ├── narration-settings.yaml      # Canonical model, language, chunk, and pause settings
    ├── pronunciation-guide.yaml     # Versioned pronunciation substitutions
    ├── scripts/
    │   └── narrate.py               # Parser, chunker, renderer, and audio assembler
    ├── tests/
    │   └── test_narrate.py          # Narration implementation tests
    ├── fixtures/                    # Audition and calibration text fixtures
    ├── samples/                     # Audition audio and manifests
    ├── records/                     # Versioned render reproducibility records
    ├── output/
    │   ├── .gitkeep
    │   └── chapter-01-before-hogwarts-20260919-175431/
    │       ├── narration-input.md
    │       ├── tts-submission.txt
    │       ├── produce_chapter_one.py
    │       ├── test_production.py
    │       ├── chapter-01-before-hogwarts.wav
    │       ├── chapter-01-before-hogwarts.mp3
    │       ├── chunks/
    │       │   ├── chunk-001.wav ... chunk-042.wav
    │       │   └── chunk-manifest.yaml
    │       ├── render-manifest.yaml
    │       ├── full-render.log
    │       └── quality-control-report.md
    ├── chapter-01-full-20260916-215129/
    │   ├── run_full_chapter.py       # Earlier audit wrapper reused by current producer
    │   ├── test_run_full_chapter.py
    │   ├── chapter-01-full.wav/.mp3
    │   ├── chunks/
    │   └── generation-report.yaml
    └── docs/superpowers/             # Original design and implementation records
```

## 2. Exact entry point

### Intended normal workflow

The project-level instructions prescribe this interface:

```bash
HF_HUB_OFFLINE=1 authoring/audio/.venv/bin/python \
  authoring/audio/scripts/narrate.py render CHAPTER.md \
  --output authoring/audio/output/CHAPTER.wav \
  --voice VOICE --speed SPEED \
  --listening-copy authoring/audio/output/CHAPTER.mp3
```

The relative form is intended to be run from the repository root:

```text
/Users/dima/Documents/Hogwarts History
```

Global `--settings` and `--pronunciations` options are also supported and must appear before `render`. Their defaults are resolved relative to the narration script rather than the current working directory.

### Current generic-render defect

The generic renderer calls `write_pcm16_wav` without its required sample-rate argument. It therefore raises `TypeError` before writing the final WAV.

### Entry point that produced current Chapter One

The recorded production command was:

```bash
HF_HUB_OFFLINE=1 authoring/audio/.venv/bin/python \
  authoring/audio/output/chapter-01-before-hogwarts-20260919-175431/produce_chapter_one.py
```

That producer:

1. verifies the approved manuscript hash;
2. verifies that `narration-input.md` has the same parsed spoken blocks as the approved manuscript;
3. creates or verifies `tts-submission.txt`;
4. configures and imports the earlier audited wrapper;
5. patches the missing-sample-rate problem in memory;
6. invokes the ordinary renderer interface in-process;
7. captures chunk audio and runtime evidence; and
8. writes manifests and performs technical validation.

The task-local workflow refuses to overwrite an existing master WAV, listening-copy MP3, chunks directory, report, or log. The generic CLI has no equivalent guard: absent its current defect, it would overwrite the WAV and MP3 targets.

## 3. End-to-end Chapter One pipeline

```text
final-draft-candidate-revision-07.md
→ comment-free narration-input.md
→ approved-hash and spoken-block equivalence checks
→ strip_front_matter()
→ remove_html_comments()
→ markdown_to_blocks() and strip_inline_markdown()
→ SpeechBlock objects
→ apply_pronunciations()
→ chunk_blocks(max_words=160)
→ 42 SpeechChunk objects
→ Kokoro model.generate() for each chunk
→ in-memory audio arrays
→ assemble_audio() with semantic silence
→ mono 24 kHz PCM16 WAV
→ FFmpeg MP3 conversion
→ chunk, manifest, probe, and full-decode audit
```

The final text passed to Kokoro is constructed by `markdown_to_blocks`, `apply_pronunciations`, `split_sentences`, and `chunk_blocks`. Each resulting `SpeechChunk.text` value is passed directly to `model.generate` with the selected voice, speed, and language code.

## 4. Narration text generation

The generic renderer keeps its parsed and chunked narration text only in memory. It does not persist a narration script.

The current verified Chapter One output contains three local text representations:

- `narration-input.md`: source prose with editorial HTML comments removed and Markdown headings retained.
- `tts-submission.txt`: the 40 parsed spoken blocks, without Markdown syntax, in order.
- `chunks/chunk-manifest.yaml`: all 42 exact chunk strings supplied to individual Kokoro calls.

The repository contains a `prepare_markdown` helper that removes comments and collapses excessive blank lines. The production entry point, however, reads an already-existing `narration-input.md`; it does not call that helper to create the file. The exact external action that originally wrote the current narration input cannot be determined from the repository.

Spoken edits to `narration-input.md` cause the producer's equivalence check against the approved manuscript to fail. `tts-submission.txt` is created only if absent and is accepted only when its existing content matches exactly. The chunk manifest is an output record rather than an input.

The producer also refuses to rerun over its existing render targets.

## 5. Heading handling

Heading markers are stripped before speech. The current mapping is:

| Markdown source | Internal kind | Exact spoken text |
| --- | --- | --- |
| `# Chapter One` | `chapter` | `Chapter One` |
| `## Before Hogwarts` | `section` | `Before Hogwarts` |
| `### Before the School` | `section` | `Before the School` |

Every heading is a separate source block and normally a separate TTS chunk. Only a level-one heading receives the `chapter` kind; all levels from two through six receive the same `section` kind.

Heading hierarchy does not change model, voice, speed, or language. It affects only the semantic pause after the completed block:

- chapter heading: 1,750 ms;
- section heading: 1,000 ms.

Blank lines terminate prose blocks. They do not directly create arbitrary pauses; the completed block's kind selects the pause duration.

The latest Chapter One chunk manifest confirms that its first three Kokoro calls used `Chapter One`, `Before Hogwarts`, and `Before the School`.

## 6. Kokoro configuration

Actual settings recorded for current Chapter One:

- Engine: `kokoro`
- Package/backend: `mlx-audio==0.5.3`
- Model loader: `mlx_audio.tts.utils.load_model`
- Model: `mlx-community/Kokoro-82M-bf16`
- Model revision: `a71e4d38b236d968966a2002c4c895dbd12b1c3c`
- Voice: `bm_george`
- Language: `british-english`
- Language code: `b`
- Speed: `0.96`
- Generated sample rate: 24,000 Hz
- Output channels: mono
- Master encoding: signed 16-bit PCM WAV
- Verified runtime: Apple M4 Pro MLX GPU/Metal
- Generated array type: `mlx.core.array`
- Python: `3.12.13`
- MLX: `0.32.2`
- Misaki: `0.9.4`
- PyYAML: `6.0.2`
- NumPy: `2.5.3`

Canonical `voice` and `speed` remain unset in `narration-settings.yaml`; they are supplied for an individual render.

Only text, voice, speed, and language code are explicitly passed to Kokoro. The repository defines no custom sampling, pitch, temperature, phoneme, SSML, or prosody parameters.

British G2P support comes from `misaki[en]` and the pinned `en_core_web_sm` dependency. There is no repository-level custom G2P configuration.

There is no model or voice fallback. The recorded command used offline Hugging Face mode, so missing cached artifacts would fail rather than download. The generic render path uses MLX-Audio but does not independently assert that MLX selected a GPU; the audit wrapper does perform that check.

## 7. Chunking and segmentation

- Maximum size: 160 whitespace-delimited words.
- Blocks never merge with neighboring blocks.
- Sentences end at `.`, `!`, or `?`, optionally followed by closing straight or curly quotes.
- Whole sentences accumulate until adding the next sentence would exceed the maximum.
- A single sentence longer than 160 words causes an error instead of being forcibly split.
- Each heading is a separate block.
- Paragraphs are separated by blank lines or headings.
- Whitespace is collapsed before chunking.
- Punctuation is otherwise retained.
- Every chunk is rendered independently.
- Multiple model results returned for one chunk are concatenated into that chunk.

Configured silence:

| Position | Duration |
| --- | ---: |
| Opening | 120 ms |
| Between chunks belonging to one block | 80 ms |
| After paragraph | 400 ms |
| After section | 1,000 ms |
| After chapter heading | 1,750 ms |
| Closing | 180 ms |

Kokoro's own leading and trailing silence is not trimmed. The Chapter One audit measured effective gaps of 469.25–2,114.125 ms after model-produced edge silence was included.

## 8. Pronunciation and preprocessing

The transformation order is:

1. Task-local comment removal and excessive-blank-line reduction in the derived clean copy.
2. Removal of an opening YAML front-matter region, when present.
3. Removal of HTML comments.
4. Division into headings and blank-line-separated paragraphs.
5. Inline Markdown cleanup:
   - code-span contents are preserved;
   - images become their alternative text;
   - links become their visible label;
   - leading blockquote markers are removed;
   - backticks and supported bold/italic delimiters are removed;
   - whitespace is collapsed.
6. Pronunciation substitutions are applied in guide order.
7. Whitespace is normalized again for sentence splitting.
8. Sentences are combined into final chunks.

Pronunciation entries contain a term, replacement, and documented reason. Replacement is case-sensitive and constrained by non-word boundaries around the configured term.

The current guide contains no substitutions, so Chapter One received no custom pronunciation changes.

The repository does not explicitly normalize em dashes or quotation marks, expand abbreviations, rewrite numbers or dates, insert SSML, or provide special proper-name handling. Those values pass to the underlying TTS/G2P stack after ordinary Markdown and whitespace cleanup.

## 9. Audio post-processing

After synthesis:

1. Rendered arrays remain in memory.
2. `assemble_audio` concatenates opening silence, rendered chunks, semantic pauses, and closing silence.
3. `write_pcm16_wav` validates the signal, applies a whole-file peak guard only when the absolute peak exceeds 0.95, and quantizes to signed 16-bit PCM.
4. The listening-copy encoder invokes FFmpeg with the input WAV and output MP3 path, allowing FFmpeg to choose its default MP3 encoding parameters.

The full-chapter path applies no fades, crossfades, dynamic compression, explicit resampling, loudness normalization, noise processing, or authored chapter metadata.

The current master's peak was approximately 0.4793, so the peak guard did not rescale it.

A separate two-pass spoken-word loudness-normalization implementation exists for George calibration samples. It targets -19 LUFS, -1 dBTP, LRA 7, mono, and 128 kbps. That implementation is not used by the full-chapter renderer.

The current MP3 was produced with FFmpeg defaults and is mono, 24 kHz, and 32 kbps. It has an FFmpeg encoder tag but no repository-authored chapter metadata.

The audited chunk WAVs were written from captured in-memory arrays after synthesis. The final master was assembled directly from the arrays rather than by reopening and joining the chunk files.

No runtime cleanup or deletion stage exists.

## 10. Current Chapter One artifacts

The latest verified output is under:

`authoring/audio/output/chapter-01-before-hogwarts-20260919-175431/`

| Artifact | Status |
| --- | --- |
| `narration-input.md` | Derived narration input; ignored |
| `tts-submission.txt` | Parsed spoken-block record; ignored |
| `produce_chapter_one.py` | Task-local producer; ignored |
| `test_production.py` | Task-local tests; ignored |
| `chunks/chunk-001.wav` ... `chunk-042.wav` | Generated intermediate audio; ignored |
| `chunks/chunk-manifest.yaml` | Exact chunk and audio manifest; ignored |
| `chapter-01-before-hogwarts.wav` | Generated master; ignored |
| `chapter-01-before-hogwarts.mp3` | Generated listening copy; ignored |
| `render-manifest.yaml` | Detailed generated audit; ignored |
| `full-render.log` | Generated log; ignored |
| `quality-control-report.md` | Generated local report; ignored |
| `records/2026-09-19-chapter-01-before-hogwarts-revision-07.yaml` | Tracked reproducibility record |

Current media facts verified directly:

- WAV: 50,458,124 bytes, 1,051.210 seconds, mono 24 kHz PCM s16le.
- MP3: 4,205,324 bytes, 1,051.210 seconds, mono 24 kHz, 32 kbps.
- Both current hashes match the tracked reproducibility record.
- Both files passed direct probing and complete decode during the investigation.

The current manifest names a `performance-cue-sheet.md`, but that file is absent from the current output directory.

An older Chapter One directory, `authoring/audio/chapter-01-full-20260916-215129/`, is tracked, including its audio and chunk files. Current ignore rules do not retroactively untrack those earlier artifacts. It is not the latest Revision 07 output.

## 11. Relevant configuration and documentation

Current defining or documenting files include:

- root `AGENTS.md`;
- `authoring/AGENTS.md`;
- `authoring/audio/README.md`;
- `authoring/audio/narration-settings.yaml`;
- `authoring/audio/pronunciation-guide.yaml`;
- `authoring/audio/requirements.txt`;
- `authoring/audio/requirements-lock.txt`;
- `authoring/audio/tests/test_narrate.py`;
- the Chapter One reproducibility record;
- the task-local production script, manifest, and quality-control report; and
- the original design and implementation records under `authoring/audio/docs/superpowers/`.

Documentation differences:

- Root `AGENTS.md` permits an explicitly requested full-chapter render and supplies the generic command.
- The audio README and original prototype design still state that a complete chapter should not be rendered.
- The README documents auditioning but not the later task-local chapter-production wrappers.
- The generic command documented by the project instructions currently fails because of the missing sample-rate argument.
- The latest manifest records a performance cue sheet that does not exist in the output directory.
- The tracked record says the shared and task-local tests passed during production; they were not rerun for the investigation.

## 12. Current implementation summary

### Current flow

```text
approved Chapter One Revision 07 Markdown
→ locally persisted comment-free narration input
→ regex Markdown parsing and inline-markup removal
→ empty pronunciation-substitution pass
→ per-block sentence chunking at no more than 160 words
→ Kokoro-82M-bf16 through MLX-Audio using bm_george, b, and 0.96
→ in-memory concatenation with semantic zero pauses
→ mono 24 kHz PCM16 WAV
→ default FFmpeg MP3 conversion
→ task-local chunk, manifest, probe, and decode audit
```

### Important files

| File | Role |
| --- | --- |
| `authoring/audio/scripts/narrate.py` | Canonical parser, chunker, renderer, and assembler |
| `authoring/audio/narration-settings.yaml` | Canonical settings |
| `authoring/audio/pronunciation-guide.yaml` | Pronunciation substitutions |
| `authoring/editions/1984/drafts/draft-01/chapters/01-before-hogwarts/final-draft-candidate-revision-07.md` | Approved Chapter One manuscript |
| `authoring/audio/output/chapter-01-before-hogwarts-20260919-175431/narration-input.md` | Markdown input used for the latest render |
| `authoring/audio/output/chapter-01-before-hogwarts-20260919-175431/chunks/chunk-manifest.yaml` | Exact per-call Kokoro strings |
| `authoring/audio/output/chapter-01-before-hogwarts-20260919-175431/produce_chapter_one.py` | Latest Chapter One entry point |
| `authoring/audio/chapter-01-full-20260916-215129/run_full_chapter.py` | Compatibility and audit wrapper |
| `authoring/audio/records/2026-09-19-chapter-01-before-hogwarts-revision-07.yaml` | Tracked reproducibility record |

### Current TTS settings

```text
engine: kokoro
backend: mlx-audio 0.5.3 / MLX Metal
model: mlx-community/Kokoro-82M-bf16
revision: a71e4d38b236d968966a2002c4c895dbd12b1c3c
voice: bm_george
language: british-english
lang_code: b
speed: 0.96
chunk maximum: 160 words
sample rate: 24000 Hz
master: mono PCM16 WAV
listening copy: mono MP3, observed 32 kbps
pronunciation substitutions: none
```

### Narration-text finding

**YES, for the current persisted Chapter One render.**

A human can open `chunks/chunk-manifest.yaml` and see every exact text string passed to Kokoro, including call boundaries. `tts-submission.txt` provides the same spoken content as a cleaner 40-block reading copy, but does not show the two additional chunk splits.

Neither file is currently a durable manual-override mechanism: the directory is ignored, the chunk manifest is output-only, and the producer rejects narration input whose spoken blocks diverge from the approved manuscript.

For an ordinary generic `narrate.py render` run, the answer is **NO** because the renderer constructs the narration strings only in memory.

### Likely modification points

1. **Combine chapter number and title:** update `markdown_to_blocks` or add preprocessing that combines the initial level-one and level-two heading blocks.
2. **Different chapter-title delivery:** make `synthesize_chunks` select synthesis parameters according to `BlockKind.CHAPTER`.
3. **Different section cadence:** extend section-specific synthesis behavior; `assemble_audio` already provides a distinct section pause.
4. **Reduce spoken section headings:** filter or classify headings during Markdown-to-block conversion, preferably through explicit configuration.
5. **Add an opening sound:** mix or prepend a sample-rate-compatible asset during assembly before narration begins.
6. **Persist final narration text:** make `run_render` write the post-pronunciation `SpeechChunk` sequence before model loading, following the existing wrapper manifest pattern.
7. **Preserve manual narration edits:** introduce a versioned narration-script input with explicit precedence over generated Markdown and stop treating every spoken difference from the manuscript as an error.
