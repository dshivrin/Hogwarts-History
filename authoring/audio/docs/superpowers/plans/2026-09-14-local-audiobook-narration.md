# Local Audiobook Narration Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify a local MLX-Audio/Kokoro narration pipeline and generate only the approved British four-voice audition.

**Architecture:** A single Python entry point separates pure Markdown preparation and audio assembly from a lazily imported MLX-Audio adapter. The `audition` path loads one Kokoro model per process, reuses it across all requested samples, writes PCM WAV files, and records reproducibility plus MLX/Metal evidence in a YAML manifest.

**Tech Stack:** CPython 3.12, MLX-Audio 0.5.3, Kokoro-82M-bf16, Misaki 0.9.4 English G2P, PyYAML 6.0.2, NumPy/SciPy transitive runtime packages, standard-library `unittest`, and Homebrew ffmpeg.

**Spec:** `authoring/audio/docs/superpowers/specs/2026-09-14-local-audiobook-narration-design.md`

## Global Constraints

- Create or modify project files only under `authoring/audio/`; read all other repository paths without changing them.
- Do not modify `authoring/editions/1984/drafts/draft-01/chapters/01-before-hogwarts/draft-revision-01.md`.
- Do not modify `hogwarts-history-repository-handoff.md`; its baseline SHA-256 is `69008cbe38d9b2e3e6bb18d548637ed0ac4f559d3522d906b6b736665558880c`.
- Use `/opt/homebrew/bin/python3.12` and the isolated `authoring/audio/.venv`; do not touch the repository core environment.
- Keep `requirements.txt` as the portable top-level dependency contract and `requirements-lock.txt` as the successful M4 Pro environment snapshot.
- Use model `mlx-community/Kokoro-82M-bf16`, British `lang_code: b`, and only the four approved voices at initial speed `0.96`.
- Keep `voice: null` and `speed: null` in `narration-settings.yaml`.
- Load the model once per audition process.
- Record the resolved Hugging Face model revision when the cache path or API exposes it.
- Establish actual MLX/Metal execution from the selected device, successful MLX generation, MLX array output, and available runtime telemetry; do not depend on one exact memory delta.
- Generated audio and caches must remain ignored by Git.
- Do not render the full chapter.

---

### Task 1: Safe tooling skeleton and isolated runtime

**Files:**
- Create: `authoring/audio/.gitignore`
- Create: `authoring/audio/README.md`
- Create: `authoring/audio/narration-settings.yaml`
- Create: `authoring/audio/pronunciation-guide.yaml`
- Create: `authoring/audio/requirements.txt`
- Create: `authoring/audio/fixtures/audition-excerpt.txt`
- Create: `authoring/audio/output/.gitkeep`

**Interfaces:**
- Consumes: accepted design and the first five prose paragraphs of the Chapter 1 manuscript.
- Produces: canonical settings, an empty documented pronunciation map, exact 442-word fixture, ignored disposable paths, and the `.venv` used by later tasks.

- [ ] **Step 1: Add the ignore contract before creating disposable files**

```gitignore
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.cache/
huggingface/
models/
*.safetensors
*.npz
.DS_Store
output/*
!output/.gitkeep
samples/*.wav
samples/*.mp3
samples/*.m4a
samples/*.flac
samples/*.ogg
samples/*.opus
```

- [ ] **Step 2: Add the portable dependency contract**

```text
mlx-audio==0.5.3
misaki[en]==0.9.4
PyYAML==6.0.2
```

- [ ] **Step 3: Add canonical settings with unset narrator fields**

```yaml
engine: kokoro
model: mlx-community/Kokoro-82M-bf16
language: british-english
lang_code: b
voice: null
speed: null
chunking:
  max_words: 160
pauses:
  opening_ms: 120
  continuation_ms: 80
  paragraph_ms: 400
  section_ms: 1000
  chapter_ms: 1750
  closing_ms: 180
output:
  intermediate: wav
  listening_copy: mp3
```

- [ ] **Step 4: Add the versioned pronunciation guide without speculative substitutions**

```yaml
version: 1
substitutions: []
```

- [ ] **Step 5: Preserve the exact 442-word audition fixture**

Copy the first five prose paragraphs beginning with “The history of Hogwarts begins before Hogwarts had a history of its own.” and ending with “the routes by which it travelled have mostly disappeared.” Keep each word, punctuation mark, and paragraph boundary identical to the manuscript; omit headings and the evidence comment between paragraphs two and three.

- [ ] **Step 6: Document installation, commands, ignored outputs, configuration invariants, and offline reuse**

The README command contract is:

```bash
/opt/homebrew/bin/python3.12 -m venv authoring/audio/.venv
authoring/audio/.venv/bin/python -m pip install --upgrade pip
authoring/audio/.venv/bin/python -m pip install -r authoring/audio/requirements.txt
authoring/audio/.venv/bin/python -m unittest discover -s authoring/audio/tests -v
authoring/audio/.venv/bin/python authoring/audio/scripts/narrate.py audition \
  --fixture authoring/audio/fixtures/audition-excerpt.txt \
  --sample bm_daniel=0.96 --sample bm_george=0.96 \
  --sample bf_alice=0.96 --sample bf_emma=0.96
```

- [ ] **Step 7: Create the isolated environment and install exact top-level dependencies**

Run:

```bash
/opt/homebrew/bin/python3.12 -m venv authoring/audio/.venv
authoring/audio/.venv/bin/python -m pip install --upgrade pip
authoring/audio/.venv/bin/python -m pip install -r authoring/audio/requirements.txt
```

Expected: CPython reports 3.12.x and imports `mlx_audio`, `misaki`, and `yaml` from `authoring/audio/.venv`.

- [ ] **Step 8: Verify ignore coverage and commit only Task 1 project files**

```bash
git check-ignore -v authoring/audio/.venv/bin/python authoring/audio/output/probe.wav authoring/audio/samples/probe.wav
git add authoring/audio/.gitignore authoring/audio/README.md authoring/audio/narration-settings.yaml authoring/audio/pronunciation-guide.yaml authoring/audio/requirements.txt authoring/audio/fixtures/audition-excerpt.txt authoring/audio/output/.gitkeep
git diff --cached --check
git commit -m "feat: scaffold local narration tooling"
```

Expected: every disposable probe path matches `authoring/audio/.gitignore`, and the commit contains no path outside `authoring/audio/`.

---

### Task 2: Markdown preparation and exact fixture extraction

**Files:**
- Create: `authoring/audio/tests/test_narrate.py`
- Create: `authoring/audio/scripts/narrate.py`

**Interfaces:**
- Produces: `BlockKind`, `SpeechBlock`, `strip_front_matter(text: str) -> str`, `remove_html_comments(text: str) -> str`, `strip_inline_markdown(text: str) -> str`, `markdown_to_blocks(markdown: str) -> list[SpeechBlock]`, and `extract_prose_excerpt(markdown: str, min_words: int = 400, max_words: int = 500) -> str`.
- Consumes: the exact fixture and read-only Chapter 1 Markdown.

- [ ] **Step 1: Write failing tests for front matter, comments, headings, inline Markdown, and prose preservation**

```python
class MarkdownPreparationTests(unittest.TestCase):
    def test_markdown_to_blocks_removes_development_markup_and_keeps_spoken_text(self):
        source = """---\ndraft: true\n---\n# Chapter One\n\n## Before Hogwarts\n\nA *careful* [history](https://example.test) remains.\n\n<!-- evidence:\nsource-001\n-->\n"""
        self.assertEqual(
            markdown_to_blocks(source),
            [
                SpeechBlock(BlockKind.CHAPTER, "Chapter One"),
                SpeechBlock(BlockKind.SECTION, "Before Hogwarts"),
                SpeechBlock(BlockKind.PARAGRAPH, "A careful history remains."),
            ],
        )

    def test_extract_prose_excerpt_matches_preserved_fixture_exactly(self):
        manuscript = MANUSCRIPT_PATH.read_text(encoding="utf-8")
        fixture = FIXTURE_PATH.read_text(encoding="utf-8").strip()
        self.assertEqual(extract_prose_excerpt(manuscript), fixture)
        self.assertGreaterEqual(len(fixture.split()), 300)
        self.assertLessEqual(len(fixture.split()), 500)
```

- [ ] **Step 2: Run the tests and verify the expected missing-module failure**

```bash
authoring/audio/.venv/bin/python -m unittest authoring.audio.tests.test_narrate.MarkdownPreparationTests -v
```

Expected: FAIL because `authoring/audio/scripts/narrate.py` does not exist.

- [ ] **Step 3: Implement typed blocks and the minimal preprocessing pipeline**

```text
BlockKind values: chapter, section, paragraph.
SpeechBlock fields: kind: BlockKind; text: str. The dataclass is frozen.
strip_front_matter: if the first line is exactly `---`, discard through the next exact `---` line; otherwise return the input.
remove_html_comments: replace every `<!--` through `-->` span with an empty string using DOTALL matching.
strip_inline_markdown: keep alt text and link labels; remove backticks, emphasis delimiters, and leading blockquote markers; collapse whitespace without changing punctuation.
markdown_to_blocks: preprocess front matter and comments, flush accumulated prose at blank lines or headings, classify level-one headings as chapter and all deeper headings as section, and join manuscript line wraps with one space.
extract_prose_excerpt: keep paragraph blocks only, append complete paragraphs until at least 400 words, reject a next paragraph that would exceed 500 after the minimum is satisfied, and raise if 400 words cannot be collected.
```

- [ ] **Step 4: Run the focused tests and then the complete suite**

```bash
authoring/audio/.venv/bin/python -m unittest authoring.audio.tests.test_narrate.MarkdownPreparationTests -v
authoring/audio/.venv/bin/python -m unittest discover -s authoring/audio/tests -v
```

Expected: all Markdown-preparation tests PASS and the fixture comparison is exact.

- [ ] **Step 5: Commit the preprocessing behavior**

```bash
git add authoring/audio/scripts/narrate.py authoring/audio/tests/test_narrate.py
git diff --cached --check
git commit -m "feat: prepare manuscripts for narration"
```

---

### Task 3: Pronunciation substitutions and sentence-safe chunking

**Files:**
- Modify: `authoring/audio/tests/test_narrate.py`
- Modify: `authoring/audio/scripts/narrate.py`

**Interfaces:**
- Produces: `Pronunciation`, `load_pronunciations(path: Path) -> list[Pronunciation]`, `apply_pronunciations(text: str, entries: Sequence[Pronunciation]) -> str`, `split_sentences(text: str) -> list[str]`, and `chunk_blocks(blocks: Sequence[SpeechBlock], max_words: int) -> list[SpeechChunk]`.
- Consumes: `SpeechBlock` and `BlockKind` from Task 2.

- [ ] **Step 1: Write failing tests for exact substitutions and non-mutating source behavior**

```python
def test_pronunciation_substitutions_are_boundary_aware(self):
    entries = [Pronunciation(term="Hogwarts", replacement="Hog-warts", reason="audition correction")]
    self.assertEqual(apply_pronunciations("Hogwarts and Hogwartsian", entries), "Hog-warts and Hogwartsian")

def test_applying_pronunciations_does_not_change_the_manuscript(self):
    before = MANUSCRIPT_PATH.read_bytes()
    apply_pronunciations("Hogwarts", [Pronunciation("Hogwarts", "Hog-warts", "test")])
    self.assertEqual(MANUSCRIPT_PATH.read_bytes(), before)
```

- [ ] **Step 2: Write failing tests for complete-sentence chunking and overlong-sentence rejection**

```python
def test_chunk_blocks_splits_only_between_sentences(self):
    block = SpeechBlock(BlockKind.PARAGRAPH, "One short sentence. Another complete sentence. Final words.")
    self.assertEqual(
        [chunk.text for chunk in chunk_blocks([block], max_words=5)],
        ["One short sentence.", "Another complete sentence.", "Final words."],
    )

def test_chunk_blocks_rejects_a_single_sentence_over_the_limit(self):
    with self.assertRaisesRegex(ValueError, "single sentence"):
        chunk_blocks([SpeechBlock(BlockKind.PARAGRAPH, "one two three four five six.")], max_words=5)
```

- [ ] **Step 3: Run the new test classes and verify failures name missing behavior**

```bash
authoring/audio/.venv/bin/python -m unittest authoring.audio.tests.test_narrate.PronunciationTests authoring.audio.tests.test_narrate.ChunkingTests -v
```

Expected: FAIL because the new types and functions are absent.

- [ ] **Step 4: Implement validated pronunciation loading and chunk metadata**

```text
Pronunciation fields: term: str; replacement: str; reason: str. The dataclass is frozen.
SpeechChunk fields: kind: BlockKind; text: str; ends_block: bool. The dataclass is frozen.
load_pronunciations: safe-load YAML, require version 1 and a list under substitutions, require non-empty term/replacement/reason strings, and reject duplicate terms.
apply_pronunciations: for each entry, replace only case-sensitive matches bounded on both sides by non-word characters.
split_sentences: normalize internal whitespace and capture the shortest spans ending in `.`, `?`, or `!` plus optional closing quotes; retain a final punctuation-free span.
chunk_blocks: reject max_words below one, sentence-split each block, reject any single sentence over the limit, greedily pack adjacent complete sentences, preserve kind, and set ends_block only on the final emitted chunk for each source block.
```

- [ ] **Step 5: Verify all tests and commit**

```bash
authoring/audio/.venv/bin/python -m unittest discover -s authoring/audio/tests -v
git add authoring/audio/scripts/narrate.py authoring/audio/tests/test_narrate.py
git diff --cached --check
git commit -m "feat: add safe narration chunking"
```

Expected: all tests PASS.

---

### Task 4: Deterministic audio assembly and WAV output

**Files:**
- Modify: `authoring/audio/tests/test_narrate.py`
- Modify: `authoring/audio/scripts/narrate.py`

**Interfaces:**
- Produces: `RenderedChunk`, `assemble_audio(chunks: Sequence[RenderedChunk], sample_rate: int, pauses: Mapping[str, int]) -> numpy.ndarray`, `write_pcm16_wav(path: Path, audio: numpy.ndarray, sample_rate: int) -> None`, `inspect_wav(path: Path) -> dict[str, int | float | bool]`, and `encode_listening_copy(wav_path: Path, output_path: Path, ffmpeg: str = "ffmpeg") -> None`.
- Consumes: `SpeechChunk` from Task 3 and NumPy supplied by MLX-Audio.

- [ ] **Step 1: Write failing tests for pause lengths and boundary padding**

```python
def test_assemble_audio_uses_semantic_pauses_and_boundary_silence(self):
    chunks = [
        RenderedChunk(BlockKind.PARAGRAPH, np.ones(4, dtype=np.float32), False),
        RenderedChunk(BlockKind.PARAGRAPH, np.ones(3, dtype=np.float32), True),
        RenderedChunk(BlockKind.SECTION, np.ones(2, dtype=np.float32), True),
    ]
    pauses = {"opening_ms": 100, "continuation_ms": 50, "paragraph_ms": 200,
              "section_ms": 300, "chapter_ms": 400, "closing_ms": 100}
    audio = assemble_audio(chunks, sample_rate=1000, pauses=pauses)
    self.assertEqual(len(audio), 100 + 4 + 50 + 3 + 200 + 2 + 300 + 100)
    self.assertTrue(np.all(audio[:100] == 0))
    self.assertTrue(np.all(audio[-100:] == 0))
```

- [ ] **Step 2: Write a failing round-trip test for finite mono PCM WAV output**

```python
def test_write_pcm16_wav_round_trips_without_clipping(self):
    path = self.temp_dir / "sample.wav"
    write_pcm16_wav(path, np.array([0.0, -0.5, 0.5, 0.0], dtype=np.float32), 24000)
    facts = inspect_wav(path)
    self.assertEqual(facts["sample_rate"], 24000)
    self.assertEqual(facts["channels"], 1)
    self.assertEqual(facts["sample_count"], 4)
    self.assertLessEqual(facts["peak"], 0.951)
```

- [ ] **Step 3: Run the audio tests and verify the missing-behavior failures**

```bash
authoring/audio/.venv/bin/python -m unittest authoring.audio.tests.test_narrate.AudioAssemblyTests -v
```

Expected: FAIL because `RenderedChunk` and audio helpers are absent.

- [ ] **Step 4: Implement semantic concatenation, PCM conversion, inspection, and optional ffmpeg conversion**

```text
assemble_audio: validate non-empty finite mono arrays; append opening silence; append each rendered chunk; use continuation silence only when ends_block is false; otherwise choose paragraph, section, or chapter silence from the chunk kind; append closing silence.
write_pcm16_wav: flatten to float32; reject empty or non-finite input; scale peaks above 0.95 down to 0.95; round after multiplying by 32767; write one-channel, 16-bit PCM through wave.open.
inspect_wav: require one-channel, 16-bit PCM; decode frames as little-endian int16; report `sample_rate`, `channels`, `sample_count`, `duration_seconds`, `peak`, `non_silent_samples`, `finite`, `opening_silence_samples`, and `closing_silence_samples`.
encode_listening_copy: create the parent directory and execute [ffmpeg, -y, -v, error, -i, wav_path, output_path] with check=True.
```

- [ ] **Step 5: Run the complete suite and commit**

```bash
authoring/audio/.venv/bin/python -m unittest discover -s authoring/audio/tests -v
git add authoring/audio/scripts/narrate.py authoring/audio/tests/test_narrate.py
git diff --cached --check
git commit -m "feat: assemble narration audio safely"
```

Expected: all tests PASS.

---

### Task 5: MLX adapter, one-load audition orchestration, manifest, and CLI

**Files:**
- Modify: `authoring/audio/tests/test_narrate.py`
- Modify: `authoring/audio/scripts/narrate.py`

**Interfaces:**
- Produces: `SampleSpec`, `RuntimeEvidence`, `collect_runtime_evidence() -> RuntimeEvidence`, `resolve_model_revision(model: object, model_id: str) -> str | None`, `synthesize_chunks(model: object, chunks: Sequence[SpeechChunk], voice: str, speed: float, lang_code: str) -> tuple[list[RenderedChunk], int, dict[str, str]]`, the `run_audition` and `run_render` signatures listed in Step 5, `build_parser() -> argparse.ArgumentParser`, and `main(argv: Sequence[str] | None = None) -> int`.
- Consumes: all pure preparation and audio functions from Tasks 2–4 and `mlx_audio.tts.utils.load_model` imported only inside the default loader.

- [ ] **Step 1: Write a failing behavioral test that makes a second model load fatal**

```python
def test_run_audition_reuses_one_model_for_multiple_samples(self):
    loads = 0
    def loader(model_id):
        nonlocal loads
        loads += 1
        if loads > 1:
            raise AssertionError("model loaded more than once")
        return FakeKokoroModel(sample_rate=24000)

    records = run_audition(
        fixture_path=self.fixture,
        sample_specs=[SampleSpec("bm_daniel", 0.96), SampleSpec("bf_emma", 0.96)],
        settings=self.settings,
        pronunciation_path=self.pronunciations,
        output_dir=self.output_dir,
        manifest_path=self.manifest,
        model_loader=loader,
        evidence_provider=lambda: RuntimeEvidence("Device(gpu, 0)", True, {}, "test"),
    )
    self.assertEqual([record["voice"] for record in records], ["bm_daniel", "bf_emma"])
    self.assertTrue(all(Path(record["path"]).is_file() for record in records))
```

`FakeKokoroModel.generate()` yields a complete result object with a real NumPy `audio` array and `sample_rate`, and rejects any language code other than `b` so the test exercises the production boundary.

- [ ] **Step 2: Write failing tests for manifest invariants and canonical-null enforcement**

```python
def test_manifest_records_identical_fixture_and_exact_sample_settings(self):
    records = self.run_two_sample_audition()
    self.assertEqual(len({r["fixture_sha256"] for r in records}), 1)
    self.assertEqual({r["lang_code"] for r in records}, {"b"})
    self.assertEqual({r["speed"] for r in records}, {0.96})
    self.assertEqual({r["model"] for r in records}, {"mlx-community/Kokoro-82M-bf16"})

def test_settings_require_canonical_voice_and_speed_to_remain_null(self):
    settings = dict(self.settings, voice="bm_george")
    with self.assertRaisesRegex(ValueError, "voice.*null"):
        validate_settings(settings)
```

- [ ] **Step 3: Run orchestration tests and verify expected missing-behavior failures**

```bash
authoring/audio/.venv/bin/python -m unittest authoring.audio.tests.test_narrate.AuditionTests -v
```

Expected: FAIL because the orchestration API is absent.

- [ ] **Step 4: Implement MLX synthesis and robust runtime evidence collection**

```text
SampleSpec fields: voice: str; speed: float. The dataclass is frozen.
RuntimeEvidence fields: device: str; gpu_selected: bool; metal_telemetry: dict[str, object]; audio_array_type: str. The dataclass is frozen.
collect_runtime_evidence: import mlx.core lazily, stringify default_device, compare it with mx.gpu, call each available Metal telemetry function independently under exception handling, and return the accumulated facts.
resolve_model_revision: inspect config.model_path and model.model_path for a `snapshots/<revision>` pair; otherwise scan the Hugging Face cache for the matching repo; otherwise request model_info.sha; return None only after all three sources are unavailable.
synthesize_chunks: call model.generate(text=chunk.text, voice=voice, speed=speed, lang_code=lang_code) for each semantic chunk; evaluate each MLX audio result, flatten it to float32 NumPy, require a single consistent result.sample_rate, preserve kind/ends_block, and record the module-qualified source array type.
```

Collect `mlx.core.default_device()`, compare it with `mlx.core.gpu`, and record whichever of `mlx.core.metal.device_info()`, `get_active_memory()`, `get_cache_memory()`, and `get_peak_memory()` exist and succeed. Record the module-qualified output array type from real generation. Treat telemetry fields as supporting evidence, not pass/fail deltas; actual success requires a GPU default device, a loaded MLX model, non-empty MLX-generated audio, and a valid WAV.

Resolve the model revision first from a model/config cache path containing `snapshots/<revision>`, then from `huggingface_hub.scan_cache_dir()`, then from `HfApi().model_info(model_id).sha` when network access is available. Return `None` without failing offline generation if all sources are unavailable.

- [ ] **Step 5: Implement audition/render orchestration and manifest writing**

```text
run_audition(fixture_path: Path, sample_specs: Sequence[SampleSpec], settings: Mapping[str, object], pronunciation_path: Path, output_dir: Path, manifest_path: Path, model_loader: Callable[[str], object] | None = None, evidence_provider: Callable[[], RuntimeEvidence] | None = None) -> list[dict[str, object]]
run_render(markdown_path: Path, output_path: Path, voice: str, speed: float, settings: Mapping[str, object], pronunciation_path: Path, listening_copy: Path | None = None) -> Path

run_audition sequence: validate settings and unique sample requests; read and hash the fixture once; build and pronunciation-adjust blocks once; load the model once; resolve the revision once; for each SampleSpec synthesize, assemble, write, inspect, and hash one WAV; collect post-generation runtime evidence; safe-dump one manifest; return its sample records.
run_render sequence: validate settings and explicit narrator arguments; preprocess the read-only Markdown into blocks; load the model; synthesize and assemble one WAV; optionally call encode_listening_copy; return the WAV path without changing the manuscript or canonical settings.
```

Validate model, language, null canonical narrator fields, approved British voice names, speed range, and duplicate requests before model loading. Name samples `bm-daniel-096.wav`, `bm-george-096.wav`, `bf-alice-096.wav`, and `bf-emma-096.wav`. Write global run metadata and repeat the exact fixture path/hash, Python version, `mlx-audio` version, `misaki` version, model identifier/revision, voice, language code, speed, audio facts, MLX/Metal evidence, and file SHA-256 in every per-sample record with `yaml.safe_dump(sort_keys=False)`.

- [ ] **Step 6: Implement the command-line contract and errors**

```text
narrate.py audition --fixture PATH --sample VOICE=SPEED [--sample VOICE=SPEED, repeatable]
narrate.py render MANUSCRIPT --output PATH --voice VOICE --speed SPEED [--listening-copy PATH]
```

Default all settings, guide, sample, and manifest paths relative to `authoring/audio/`, regardless of the caller's current directory. Print each created path and duration. Return a nonzero exit through `argparse.error` for bad sample syntax and through a concise caught exception for runtime failures.

- [ ] **Step 7: Run focused tests, the complete suite, and commit**

```bash
authoring/audio/.venv/bin/python -m unittest authoring.audio.tests.test_narrate.AuditionTests -v
authoring/audio/.venv/bin/python -m unittest discover -s authoring/audio/tests -v
git add authoring/audio/scripts/narrate.py authoring/audio/tests/test_narrate.py
git diff --cached --check
git commit -m "feat: orchestrate reproducible Kokoro auditions"
```

Expected: all tests PASS without downloading or loading the real model.

---

### Task 6: Install ffmpeg and generate the approved four-voice audition

**Files:**
- Create: `authoring/audio/samples/bm-daniel-096.wav` (ignored)
- Create: `authoring/audio/samples/bm-george-096.wav` (ignored)
- Create: `authoring/audio/samples/bf-alice-096.wav` (ignored)
- Create: `authoring/audio/samples/bf-emma-096.wav` (ignored)
- Create: `authoring/audio/samples/audition-manifest.yaml`
- Create: `authoring/audio/requirements-lock.txt`
- Modify: `authoring/audio/pronunciation-guide.yaml` only if actual listening proves a correction necessary.

**Interfaces:**
- Consumes: the `audition` CLI, exact fixture, canonical settings, empty or evidence-based pronunciation guide, and Hugging Face model cache/API.
- Produces: four initial playable WAV files, manifest, environment snapshot, and actual MLX/Metal evidence.

- [ ] **Step 1: Install Homebrew ffmpeg and verify its binaries**

```bash
/opt/homebrew/bin/brew install ffmpeg
/opt/homebrew/bin/ffmpeg -version
/opt/homebrew/bin/ffprobe -version
```

Expected: both tools report versions and arm64-compatible Homebrew paths.

- [ ] **Step 2: Verify exact Python packages and probe British G2P before synthesis**

```bash
authoring/audio/.venv/bin/python -c "import importlib.metadata as m, platform; print(platform.python_version()); print(m.version('mlx-audio')); print(m.version('misaki')); print(m.version('PyYAML'))"
authoring/audio/.venv/bin/python -c "from misaki import en, espeak; g=en.G2P(trf=False,british=True,fallback=espeak.EspeakFallback(british=True)); print(g('Hogwarts, Muggle, Muggles.')[0])"
```

Expected: Python 3.12.x, exact top-level versions, and non-empty British phonemes without a fallback-loading warning.

- [ ] **Step 3: Run one process containing exactly the four approved initial samples**

```bash
authoring/audio/.venv/bin/python authoring/audio/scripts/narrate.py audition \
  --fixture authoring/audio/fixtures/audition-excerpt.txt \
  --sample bm_daniel=0.96 \
  --sample bm_george=0.96 \
  --sample bf_alice=0.96 \
  --sample bf_emma=0.96
```

Expected: the log reports one model load, `Device(gpu, 0)` or equivalent MLX GPU evidence, four non-empty WAV paths, and one manifest.

- [ ] **Step 4: Listen to all four complete samples before any additional generation**

Compare intelligibility, pacing, warmth, formality, sentence endings, joins, artifacts, and the spoken forms of `Hogwarts`, `Muggle`, and `Muggles`. Record observations for the final report without naming a winner.

- [ ] **Step 5: Apply and document a pronunciation correction only if listening proves it necessary**

If a present candidate term is wrong, add exactly one entry per affected term:

```yaml
substitutions:
  - term: Hogwarts
    replacement: Hog-warts
    reason: "Corrects the pronunciation heard in the four-voice 0.96 audition."
```

Choose the replacement by a short isolated pronunciation probe, then rerun the same four-sample command so every delivered sample uses the same corrected fixture payload. Do not add untested terms.

- [ ] **Step 6: Generate at most two measured-speed variants only when listening establishes a useful comparison**

If one or two otherwise suitable voices sound consistently rushed, run one audition process with only those voices at `0.92`. If a suitable voice sounds consistently slow, use `1.00` instead. If the initial pacing is already useful, generate no variant. The delivered total must remain between four and six audio files.

- [ ] **Step 7: Snapshot the successful environment and commit reproducibility metadata**

```bash
authoring/audio/.venv/bin/python -m pip freeze > /tmp/hogwarts-audio-requirements-lock.txt
```

Copy the snapshot into `authoring/audio/requirements-lock.txt` with `apply_patch`, preserving it as an environment record rather than replacing the portable `requirements.txt`. Then run:

```bash
git add authoring/audio/requirements-lock.txt authoring/audio/samples/audition-manifest.yaml authoring/audio/pronunciation-guide.yaml
git diff --cached --check
git commit -m "feat: record Kokoro audition environment"
```

Expected: generated audio remains ignored; only the lock snapshot, manifest, and any evidence-based guide change are committed.

---

### Task 7: End-to-end verification, documentation, and protection audit

**Files:**
- Modify: `authoring/audio/README.md`
- Modify: `authoring/audio/samples/audition-manifest.yaml` only if verification adds measured facts.

**Interfaces:**
- Consumes: all audition artifacts and the baseline protection evidence.
- Produces: verified commands and the factual data needed for the final report.

- [ ] **Step 1: Run the full unit-test suite from the documented environment**

```bash
authoring/audio/.venv/bin/python -m unittest discover -s authoring/audio/tests -v
```

Expected: all tests PASS with no warnings or errors.

- [ ] **Step 2: Probe and fully decode every audition WAV**

For each `authoring/audio/samples/*.wav`, run:

```bash
/opt/homebrew/bin/ffprobe -v error -show_entries format=duration -show_entries stream=codec_name,sample_rate,channels -of json SAMPLE.wav
/opt/homebrew/bin/ffmpeg -v error -i SAMPLE.wav -f null -
```

Expected: PCM audio, 24000 Hz unless the model reports another native rate, one channel, positive duration, and zero decode errors.

- [ ] **Step 3: Validate the manifest as the shared-source and execution record**

Check that every sample record has the same fixture path and SHA-256, exact Python/package/model/voice/language/speed values, non-empty file SHA-256, matching WAV facts, a GPU-selected MLX device, MLX output array type, available Metal telemetry, and the resolved model revision when discoverable.

- [ ] **Step 4: Confirm unclipped boundaries and non-silent content**

Use each manifest record's `opening_silence_samples`, `closing_silence_samples`, `finite`, `peak`, and `non_silent_samples` facts. Require finite data, positive non-silent samples, peak at or below `0.951`, and at least the configured opening and closing silence within one sample of rounding.

- [ ] **Step 5: Update README with the tested versions and exact successful commands**

Keep canonical narrator fields unset. Document that the model and voice files can be reused offline after download, that the lock is an M4 Pro snapshot, and that generated audio is intentionally ignored.

- [ ] **Step 6: Re-run tests after documentation-adjacent changes and commit**

```bash
authoring/audio/.venv/bin/python -m unittest discover -s authoring/audio/tests -v
git add authoring/audio/README.md authoring/audio/samples/audition-manifest.yaml
git diff --cached --check
git commit -m "docs: record verified narration workflow"
```

- [ ] **Step 7: Perform the final repository protection audit**

```bash
shasum -a 256 hogwarts-history-repository-handoff.md
git diff -- . ':(exclude)authoring/audio/**'
git diff --cached -- . ':(exclude)authoring/audio/**'
git status --short
```

Expected: the handoff checksum remains `69008cbe38d9b2e3e6bb18d548637ed0ac4f559d3522d906b6b736665558880c`; both outside-scope diffs are empty; all new task paths are under `authoring/audio/`; the pre-existing untracked authoring/research material and handoff document remain untouched.

- [ ] **Step 8: Prepare the final report and stop**

Report installation location and versions, exact model and revision, every sample's voice/speed/duration/path, comparative listening observations, pronunciation issues, awkward spoken sentences from the audition passage, MLX/Metal evidence, test/audio verification, and protection status. Do not select a narrator and do not render the chapter.
