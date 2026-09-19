# Canonical Audiobook Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make full, opening-sample, and targeted-paragraph narration renders use configuration-driven voice and speed defaults while preserving one authoritative `narration.md` and one shared Kokoro rendering pipeline.

**Architecture:** Resolve optional CLI overrides against canonical settings before invoking concrete internal APIs. Read the complete narration manuscript once into an immutable snapshot, select sample blocks in memory, and route full and sample work through shared pronunciation, chunking, synthesis, assembly, artifact, manifest, and provenance helpers. Opening-sample retries remain in memory and load Kokoro only once.

**Tech Stack:** Python 3.12, standard-library `argparse`/`unittest`/`wave`, NumPy, PyYAML, MLX-Audio Kokoro, FFmpeg/ffprobe.

**Spec:** `authoring/audio/docs/superpowers/specs/2026-09-19-canonical-audiobook-generation-design.md`

## Global Constraints

- `narration.md` is the authoritative spoken manuscript and must never be rewritten, regenerated, or prepared implicitly by `render` or `sample`.
- Python receives explicit narration and output paths; chapter and edition discovery remain exclusively in Codex instructions.
- Canonical defaults exist only in `authoring/audio/narration-settings.yaml`: `voice: bm_george` and `speed: 0.96`.
- Voice and speed resolution is independently `explicit CLI override -> narration-settings.yaml`; overrides never mutate settings.
- Preserve the existing supported speed range of `0.90` through `1.05`; do not describe it as a new policy.
- Keep the fixed four-voice audition batch validation separate from normal render/sample voice validation.
- Normal render/sample voice validation is structural; the Kokoro backend remains authoritative for whether a non-empty explicit identifier exists.
- Preserve the public `run_render(..., voice: str, speed: float, ...)` contract for current tests and task-local callers.
- Use render kinds `full`, `opening_sample`, and `paragraph_sample`.
- Opening samples retain opening headings, contain complete prose sentences, and must be no longer than 30 seconds.
- Paragraph samples select exactly one one-based prose paragraph, excluding headings from numbering, and have no 30-second limit.
- Read and hash the complete narration once; sample provenance continues to identify that complete snapshot.
- Do not create derived Markdown narration sources, a second TTS pipeline, a parallel provenance schema, or Python chapter discovery.
- Preserve pre-existing working-tree edits. Inspect `git diff` before each task and stage only this plan's hunks with `git add -p` when a modified file also contains earlier user work.
- Do not add title effects, special title/section performance, MiniMax assets, music, ambience, mixing, crossfades, subtitle editorial rules, or mastering changes.

## Review Focus

- A voice-only or speed-only override must combine with the other canonical setting, never `None` or a stale hard-coded fallback; Task 1 tests each partial override.
- `sample --paragraph 0`, a negative number, and an index beyond available prose must fail before model loading or artifact writes; Task 2 tests invalid indices and Task 4 verifies early failure.
- A narration containing headings but no prose, or an opening whose shortest prose sentence still exceeds 30 seconds, must fail without ordinary outputs or a provenance update; Tasks 2 and 4 cover both conditions.
- A concurrent edit after the immutable narration read must not change selected text, hashes, or submitted chunks for that run; Task 3 preserves the existing full-render snapshot test and Task 4 adds the sample equivalent.
- An encoder, manifest, or provenance failure after synthesis may leave a partial final-run artifact under current renderer semantics, but rejected duration candidates must never do so; Task 4 distinguishes retry atomicity from existing finalization behavior.

---

### Task 1: Canonical defaults and CLI-boundary resolution

**Files:**
- Modify: `authoring/audio/narration-settings.yaml`
- Modify: `authoring/audio/scripts/narrate.py:632-673,1185-1264`
- Modify: `authoring/audio/tests/test_narrate.py:105-445,677-914`

**Interfaces:**
- Consumes: existing `SampleSpec`, `_validate_sample_specs`, `validate_settings`, `main`, and `run_render`.
- Produces: `validate_render_spec(voice: object, speed: object) -> SampleSpec` and `resolve_render_spec(settings: Mapping[str, object], voice: str | None, speed: float | None) -> SampleSpec`; later tasks use the same resolver for `sample`.

- [ ] **Step 1: Write failing settings and resolver tests**

Add `RenderConfigurationTests` to `authoring/audio/tests/test_narrate.py`. Use concrete canonical settings and pin independent fallback, explicit overrides, existing speed limits, and the voice-validation split:

```python
class RenderConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.settings = {
            "engine": "kokoro",
            "model": "mlx-community/Kokoro-82M-bf16",
            "language": "british-english",
            "lang_code": "b",
            "voice": "bm_george",
            "speed": 0.96,
            "chunking": {"max_words": 160},
            "pauses": {
                "opening_ms": 0,
                "continuation_ms": 0,
                "paragraph_ms": 0,
                "section_ms": 0,
                "chapter_ms": 0,
                "closing_ms": 0,
            },
            "output": {"intermediate": "wav", "listening_copy": "mp3"},
        }

    def test_resolve_render_spec_uses_canonical_defaults(self):
        self.assertEqual(
            narrate.resolve_render_spec(self.settings, None, None),
            SampleSpec("bm_george", 0.96),
        )

    def test_resolve_render_spec_applies_each_override_independently(self):
        self.assertEqual(
            narrate.resolve_render_spec(self.settings, "bm_lewis", None),
            SampleSpec("bm_lewis", 0.96),
        )
        self.assertEqual(
            narrate.resolve_render_spec(self.settings, None, 0.92),
            SampleSpec("bm_george", 0.92),
        )
        self.assertEqual(
            narrate.resolve_render_spec(self.settings, "bm_lewis", 1.0),
            SampleSpec("bm_lewis", 1.0),
        )

    def test_normal_render_accepts_non_batch_voice_but_preserves_speed_range(self):
        self.assertEqual(
            narrate.validate_render_spec("bm_lewis", 0.96),
            SampleSpec("bm_lewis", 0.96),
        )
        for speed in (0.89, 1.06):
            with self.subTest(speed=speed):
                with self.assertRaisesRegex(ValueError, "0.90 and 1.05"):
                    narrate.validate_render_spec("bm_george", speed)

    def test_audition_batch_still_rejects_non_batch_voice(self):
        with self.assertRaisesRegex(ValueError, "Unsupported British voice"):
            narrate._validate_sample_specs([SampleSpec("bm_lewis", 0.96)])
```

Update existing test settings fixtures from `voice: None, speed: None` to `voice: "bm_george", speed: 0.96`. Replace `test_settings_require_canonical_voice_and_speed_to_remain_null` with assertions that missing or invalid canonical values fail.

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
authoring/audio/.venv/bin/python -m unittest \
  authoring.audio.tests.test_narrate.RenderConfigurationTests -v
```

Expected: FAIL because `resolve_render_spec` and `validate_render_spec` do not exist and current settings validation requires `None`.

- [ ] **Step 3: Implement concrete configuration and validation split**

Change `authoring/audio/narration-settings.yaml`:

```yaml
voice: bm_george
speed: 0.96
```

Add normal render validation without altering `_validate_sample_specs`:

```python
def validate_render_spec(voice: object, speed: object) -> SampleSpec:
    if not isinstance(voice, str) or not voice.strip():
        raise ValueError("render voice must be a non-empty Kokoro voice identifier")
    if (
        not isinstance(speed, (int, float))
        or isinstance(speed, bool)
        or not 0.90 <= float(speed) <= 1.05
    ):
        raise ValueError("render speed must be between 0.90 and 1.05")
    return SampleSpec(voice.strip(), float(speed))


def resolve_render_spec(
    settings: Mapping[str, object],
    voice: str | None,
    speed: float | None,
) -> SampleSpec:
    return validate_render_spec(
        voice if voice is not None else settings.get("voice"),
        speed if speed is not None else settings.get("speed"),
    )
```

In `validate_settings`, replace the `voice must remain null` and `speed must remain null` checks with `validate_render_spec(settings.get("voice"), settings.get("speed"))`. In `run_render`, replace `_validate_sample_specs([SampleSpec(voice, speed)])` with `validate_render_spec(voice, speed)`.

- [ ] **Step 4: Make only render parser flags optional and resolve them in `main`**

Keep `run_render` unchanged. Change:

```python
render.add_argument("--voice")
render.add_argument("--speed", type=float)
```

Before calling `run_render`, resolve once:

```python
render_spec = resolve_render_spec(settings, args.voice, args.speed)
output = run_render(
    args.markdown,
    args.output,
    render_spec.voice,
    render_spec.speed,
    settings,
    args.pronunciations,
    args.listening_copy,
    manifest_path=args.manifest,
    chunk_manifest_path=args.chunk_manifest,
)
```

Add a CLI test that patches `run_render`, invokes `main` without flags and with each partial override, and asserts the concrete voice and speed passed to `run_render`.

- [ ] **Step 5: Run Task 1 tests and the current audio suite**

Run:

```bash
authoring/audio/.venv/bin/python -m unittest \
  authoring.audio.tests.test_narrate.RenderConfigurationTests \
  authoring.audio.tests.test_narrate.NarrationManuscriptTests \
  authoring.audio.tests.test_narrate.AuditionTests -v
```

Expected: PASS. The audition test still rejects `bm_lewis`; normal render resolution accepts it; the `run_render` positional contract remains unchanged.

- [ ] **Step 6: Commit only Task 1 hunks**

```bash
git add -p authoring/audio/narration-settings.yaml \
  authoring/audio/scripts/narrate.py \
  authoring/audio/tests/test_narrate.py
git diff --cached --check
git commit -m "feat: configure canonical narration defaults"
```

### Task 2: Pure opening and paragraph selectors

**Files:**
- Modify: `authoring/audio/scripts/narrate.py:19-163,579-630`
- Modify: `authoring/audio/tests/test_narrate.py:53-105`

**Interfaces:**
- Consumes: `SpeechBlock`, `BlockKind`, `split_sentences`, and `markdown_to_blocks`.
- Produces: `select_opening_sample_blocks(blocks: Sequence[SpeechBlock]) -> list[SpeechBlock]`, `remove_final_prose_sentence(blocks: Sequence[SpeechBlock]) -> list[SpeechBlock] | None`, and `select_prose_paragraph(blocks: Sequence[SpeechBlock], paragraph_number: int) -> list[SpeechBlock]`; Task 4 uses all three.

- [ ] **Step 1: Write failing selector tests**

Add `SampleSelectionTests` with explicit headings, prose blocks, and invalid cases:

```python
class SampleSelectionTests(unittest.TestCase):
    def setUp(self):
        self.blocks = [
            SpeechBlock(BlockKind.CHAPTER, "Chapter One"),
            SpeechBlock(BlockKind.SECTION, "Before Hogwarts"),
            SpeechBlock(BlockKind.PARAGRAPH, "First sentence. Second sentence."),
            SpeechBlock(BlockKind.SECTION, "Later Section"),
            SpeechBlock(BlockKind.PARAGRAPH, "Third sentence."),
        ]

    def test_opening_selection_keeps_only_opening_headings_and_first_paragraph(self):
        self.assertEqual(
            narrate.select_opening_sample_blocks(self.blocks),
            [self.blocks[0], self.blocks[1], self.blocks[2], self.blocks[4]],
        )

    def test_removing_final_sentence_preserves_headings_and_sentence_boundary(self):
        self.assertEqual(
            narrate.remove_final_prose_sentence(self.blocks[:3]),
            [
                self.blocks[0],
                self.blocks[1],
                SpeechBlock(BlockKind.PARAGRAPH, "First sentence."),
            ],
        )
        self.assertIsNone(
            narrate.remove_final_prose_sentence(
                [self.blocks[0], SpeechBlock(BlockKind.PARAGRAPH, "Only sentence.")]
            )
        )
        self.assertEqual(
            narrate.remove_final_prose_sentence(
                [self.blocks[0], self.blocks[2], self.blocks[4]]
            ),
            [self.blocks[0], self.blocks[2]],
        )

    def test_paragraph_numbering_ignores_headings(self):
        self.assertEqual(narrate.select_prose_paragraph(self.blocks, 1), [self.blocks[2]])
        self.assertEqual(narrate.select_prose_paragraph(self.blocks, 2), [self.blocks[4]])

    def test_invalid_paragraph_and_heading_only_narration_fail(self):
        for number in (0, -1, 3):
            with self.subTest(number=number):
                with self.assertRaisesRegex(ValueError, "prose paragraph"):
                    narrate.select_prose_paragraph(self.blocks, number)
        with self.assertRaisesRegex(ValueError, "prose"):
            narrate.select_opening_sample_blocks(self.blocks[:2])
```

- [ ] **Step 2: Run selector tests and verify RED**

Run:

```bash
authoring/audio/.venv/bin/python -m unittest \
  authoring.audio.tests.test_narrate.SampleSelectionTests -v
```

Expected: FAIL because the selector functions do not exist.

- [ ] **Step 3: Implement minimal pure selectors**

Add:

```python
def select_opening_sample_blocks(
    blocks: Sequence[SpeechBlock],
) -> list[SpeechBlock]:
    selected: list[SpeechBlock] = []
    prose_count = 0
    for block in blocks:
        if block.kind is BlockKind.PARAGRAPH:
            selected.append(block)
            prose_count += 1
            if prose_count == 2:
                break
        elif prose_count == 0:
            selected.append(block)
    if prose_count == 0:
        raise ValueError("Opening sample requires at least one prose paragraph")
    return selected


def remove_final_prose_sentence(
    blocks: Sequence[SpeechBlock],
) -> list[SpeechBlock] | None:
    selected = list(blocks)
    paragraph_index = next(
        (index for index in range(len(selected) - 1, -1, -1)
         if selected[index].kind is BlockKind.PARAGRAPH),
        None,
    )
    if paragraph_index is None:
        return None
    sentences = split_sentences(selected[paragraph_index].text)
    prose_blocks = [block for block in selected if block.kind is BlockKind.PARAGRAPH]
    if len(sentences) == 1:
        if len(prose_blocks) <= 1:
            return None
        del selected[paragraph_index]
        return selected
    selected[paragraph_index] = SpeechBlock(
        BlockKind.PARAGRAPH, " ".join(sentences[:-1])
    )
    return selected


def select_prose_paragraph(
    blocks: Sequence[SpeechBlock], paragraph_number: int
) -> list[SpeechBlock]:
    if type(paragraph_number) is not int or paragraph_number < 1:
        raise ValueError("prose paragraph number must be a positive integer")
    paragraphs = [block for block in blocks if block.kind is BlockKind.PARAGRAPH]
    if paragraph_number > len(paragraphs):
        raise ValueError(
            f"prose paragraph {paragraph_number} does not exist; "
            f"narration contains {len(paragraphs)} prose paragraphs"
        )
    return [paragraphs[paragraph_number - 1]]
```

The opening selector collects opening headings plus the first two prose
paragraphs, skipping any later headings. This deterministic candidate matches
the title-plus-first-paragraph-or-two workflow without a word heuristic. The
reducer removes trailing sentences and may remove a one-sentence second
paragraph as a unit while retaining at least one earlier prose sentence.

- [ ] **Step 4: Run selector and Markdown tests**

Run:

```bash
authoring/audio/.venv/bin/python -m unittest \
  authoring.audio.tests.test_narrate.SampleSelectionTests \
  authoring.audio.tests.test_narrate.MarkdownPreparationTests -v
```

Expected: PASS, including headings excluded from paragraph numbering.

- [ ] **Step 5: Commit only Task 2 hunks**

```bash
git add -p authoring/audio/scripts/narrate.py \
  authoring/audio/tests/test_narrate.py
git diff --cached --check
git commit -m "feat: select narration sample blocks"
```

### Task 3: Extract shared snapshot, synthesis, and finalization seams

**Files:**
- Modify: `authoring/audio/scripts/narrate.py:25-64,1052-1165`
- Modify: `authoring/audio/tests/test_narrate.py:105-445`

**Interfaces:**
- Consumes: `inspect_narration_provenance`, `markdown_to_blocks`, `apply_pronunciations`, `chunk_blocks`, `synthesize_chunks`, `assemble_audio`, and current manifest/provenance behavior.
- Produces: `NarrationSnapshot`, `SynthesisBundle`, `read_narration_snapshot`, `synthesize_blocks`, and `write_render_result`; Task 4 composes these without calling output-writing `run_render` for retries.

- [ ] **Step 1: Add a failing full-render compatibility test**

Extend `NarrationManuscriptTests`:

```python
def test_full_render_manifest_identifies_full_kind(self):
    narrate.prepare_narration(self.source, self.narration)
    output = self.temp_dir / "full.wav"
    manifest = self.temp_dir / "full-manifest.yaml"
    narrate.run_render(
        self.narration,
        output,
        "bm_george",
        0.96,
        self.settings,
        self.pronunciations,
        manifest_path=manifest,
        model_loader=lambda _model_id: FakeKokoroModel(24000),
        evidence_provider=lambda: RuntimeEvidence(
            "Device(gpu, 0)", True, {}, "mlx.core.array"
        ),
    )
    self.assertEqual(yaml.safe_load(manifest.read_text())["render_kind"], "full")
```

Keep the existing immutable-snapshot, source-drift, exact-chunk, legacy-input,
WAV, and provenance assertions unchanged. They are the compatibility contract
for the extraction.

- [ ] **Step 2: Run the new compatibility test and verify RED**

Run:

```bash
authoring/audio/.venv/bin/python -m unittest \
  authoring.audio.tests.test_narrate.NarrationManuscriptTests.test_full_render_manifest_identifies_full_kind -v
```

Expected: FAIL with missing `render_kind`.

- [ ] **Step 3: Introduce explicit immutable data carriers**

Add:

```python
@dataclass(frozen=True)
class NarrationSnapshot:
    path: Path
    sha256: str
    blocks: tuple[SpeechBlock, ...]
    provenance_report: dict[str, object]
    warnings: tuple[str, ...]
    provenance_path: Path | None
    provenance: dict[str, object] | None


@dataclass(frozen=True)
class SynthesisBundle:
    chunks: tuple[SpeechChunk, ...]
    audio: np.ndarray
    sample_rate: int
    synthesis_evidence: dict[str, object]
```

Implement the single-read snapshot helper:

```python
def read_narration_snapshot(markdown_path: Path) -> NarrationSnapshot:
    narration_bytes = markdown_path.read_bytes()
    narration_hash = hashlib.sha256(narration_bytes).hexdigest()
    report, warnings, provenance_path, provenance = inspect_narration_provenance(
        markdown_path, narration_hash
    )
    return NarrationSnapshot(
        markdown_path,
        narration_hash,
        tuple(markdown_to_blocks(narration_bytes.decode("utf-8"))),
        report,
        tuple(warnings),
        provenance_path,
        provenance,
    )
```

- [ ] **Step 4: Extract shared synthesis without writing**

Add a helper which receives already-selected raw blocks and applies the canonical downstream path:

```python
def synthesize_blocks(
    blocks: Sequence[SpeechBlock],
    pronunciations: Sequence[Pronunciation],
    settings: Mapping[str, object],
    model: object,
    voice: str,
    speed: float,
) -> SynthesisBundle:
    spoken_blocks = [
        SpeechBlock(block.kind, apply_pronunciations(block.text, pronunciations))
        for block in blocks
    ]
    chunks = chunk_blocks(spoken_blocks, settings["chunking"]["max_words"])  # type: ignore[index]
    rendered, sample_rate, evidence = synthesize_chunks(
        model, chunks, voice, speed, str(settings["lang_code"])
    )
    audio = assemble_audio(rendered, sample_rate, settings["pauses"])  # type: ignore[arg-type]
    return SynthesisBundle(tuple(chunks), audio, sample_rate, evidence)
```

- [ ] **Step 5: Extract final artifact/manifest/provenance writing**

Move the existing WAV, MP3, chunk-manifest, render-manifest, runtime-evidence, and provenance-update code into:

```python
def write_render_result(
    snapshot: NarrationSnapshot,
    bundle: SynthesisBundle,
    output_path: Path,
    voice: str,
    speed: float,
    settings: Mapping[str, object],
    model: object,
    listening_copy: Path | None,
    manifest_path: Path | None,
    chunk_manifest_path: Path | None,
    evidence_provider: Callable[[], RuntimeEvidence],
    *,
    render_kind: str,
    selection: Mapping[str, object] | None = None,
) -> Path:
```

The helper rejects unknown render kinds, writes `bundle.audio`, builds chunk records from `bundle.chunks`, preserves current manifest keys, and adds:

```python
manifest["render_kind"] = render_kind
if selection is not None:
    manifest["sample_selection"] = dict(selection)
```

It updates `snapshot.provenance["narration"]["current_sha256"]` only after
accepted artifacts and manifests have been written, using `snapshot.sha256`
as the authoritative immutable narration hash.

- [ ] **Step 6: Rewrite `run_render` as a thin composition without changing its signature**

The body becomes:

```python
validate_settings(settings)
render_spec = validate_render_spec(voice, speed)
snapshot = read_narration_snapshot(markdown_path)
for warning in snapshot.warnings:
    print(f"WARNING: {warning}", file=sys.stderr)
pronunciations = load_pronunciations(pronunciation_path)
model = (model_loader or _default_model_loader)(str(settings["model"]))
bundle = synthesize_blocks(
    snapshot.blocks, pronunciations, settings, model,
    render_spec.voice, render_spec.speed,
)
return write_render_result(
    snapshot, bundle, output_path, render_spec.voice, render_spec.speed,
    settings, model, listening_copy, manifest_path, chunk_manifest_path,
    evidence_provider or collect_runtime_evidence,
    render_kind="full",
)
```

- [ ] **Step 7: Run the full existing audio suite**

Run:

```bash
authoring/audio/.venv/bin/python -m unittest discover \
  -s authoring/audio/tests -v
```

Expected: PASS. Existing exact chunks, hashes, warnings, WAV facts, CLI output, and provenance assertions remain green, and full manifests contain `render_kind: full`.

- [ ] **Step 8: Commit only Task 3 hunks**

```bash
git add -p authoring/audio/scripts/narrate.py \
  authoring/audio/tests/test_narrate.py
git diff --cached --check
git commit -m "refactor: share narration rendering stages"
```

### Task 4: Opening and paragraph sample execution

**Files:**
- Modify: `authoring/audio/scripts/narrate.py:1052-1264`
- Modify: `authoring/audio/tests/test_narrate.py`

**Interfaces:**
- Consumes: Task 1 `resolve_render_spec`; Task 2 sample selectors; Task 3 `read_narration_snapshot`, `synthesize_blocks`, and `write_render_result`.
- Produces: `run_sample(..., paragraph: int | None = None, max_duration_seconds: float = 30.0, ...) -> Path` and the `sample NARRATION.md` CLI command.

- [ ] **Step 1: Add a duration-controllable fake model**

In the test file add:

```python
class DurationKokoroModel(FakeKokoroModel):
    def __init__(self, durations_by_text, sample_rate=10):
        super().__init__(sample_rate)
        self.durations_by_text = durations_by_text

    def generate(self, *, text, voice, speed, lang_code):
        if lang_code != "b":
            raise AssertionError("British language code was not passed")
        self.requests.append((text, voice, speed, lang_code))
        seconds = self.durations_by_text[text]
        audio = np.full(round(seconds * self.sample_rate), 0.25, dtype=np.float32)
        yield FakeGeneration(FakeMlxArray(audio), self.sample_rate)
```

Use test settings with zero pauses so requested durations directly control the assembled result.

- [ ] **Step 2: Write failing opening-sample retry and provenance tests**

Add `SampleRenderingTests` with a prepared narration containing two headings and two first-paragraph sentences. Configure the fake first candidate above 30 seconds and the reduced candidate below 30 seconds. Patch `write_pcm16_wav` with `wraps=narrate.write_pcm16_wav` and assert:

```python
self.assertEqual(load_count, 1)
self.assertEqual(wav_writer.call_count, 1)
self.assertLessEqual(inspect_wav(output)["duration_seconds"], 30.0)
self.assertEqual(manifest["render_kind"], "opening_sample")
self.assertEqual(manifest["narration"]["current_sha256"], full_narration_hash)
self.assertEqual(
    [chunk["text"] for chunk in chunk_manifest["chunks"]],
    ["Chapter One", "Before Hogwarts", "First sentence."],
)
self.assertFalse(any(output.parent.glob("*rejected*.wav")))
```

Assert that the model request log contains the longer first attempt and the reduced retry, proving resynthesis rather than waveform truncation.

- [ ] **Step 3: Write failing paragraph-sample tests**

Use a narration with headings and at least three prose paragraphs plus a pronunciation entry. Invoke paragraph 2 and assert:

```python
self.assertEqual(manifest["render_kind"], "paragraph_sample")
self.assertEqual(manifest["sample_selection"]["paragraph_number"], 2)
self.assertEqual(manifest["narration"]["current_sha256"], full_narration_hash)
self.assertEqual([request[0] for request in model.requests], ["Hog-warts remains."])
self.assertGreater(inspect_wav(output)["duration_seconds"], 30.0)
```

The final assertion pins that paragraph samples do not inherit the opening limit.

- [ ] **Step 4: Write failing early-error and immutable-snapshot tests**

Cover a missing narration path, paragraph `0`, a negative paragraph, a paragraph beyond the available count, headings-only narration, and an opening whose one prose sentence renders longer than 30 seconds. For every pre-synthesis selection error assert model load count is zero and no WAV, MP3, manifest, or chunk manifest exists. For the over-duration single-sentence case assert no final artifact exists and the provenance `current_sha256` is unchanged.

Use the existing `RacingPath` pattern to replace the manuscript after `read_bytes`; assert the sample manifest hash and submitted chunks still match the first snapshot.

- [ ] **Step 5: Run sample tests and verify RED**

Run:

```bash
authoring/audio/.venv/bin/python -m unittest \
  authoring.audio.tests.test_narrate.SampleRenderingTests -v
```

Expected: FAIL because `run_sample` and the `sample` command do not exist.

- [ ] **Step 6: Implement `run_sample` with one model load and in-memory retries**

Add this concrete interface:

```python
def run_sample(
    markdown_path: Path,
    output_path: Path,
    voice: str,
    speed: float,
    settings: Mapping[str, object],
    pronunciation_path: Path,
    listening_copy: Path | None = None,
    *,
    paragraph: int | None = None,
    max_duration_seconds: float = 30.0,
    manifest_path: Path | None = None,
    chunk_manifest_path: Path | None = None,
    model_loader: Callable[[str], object] | None = None,
    evidence_provider: Callable[[], RuntimeEvidence] | None = None,
) -> Path:
```

Validate settings and the concrete render selection, read the immutable snapshot, perform paragraph/opening selection before model loading, print source-drift warnings once, load pronunciations, then load the model exactly once.

For a paragraph, synthesize once and set:

```python
render_kind = "paragraph_sample"
selection = {"paragraph_number": paragraph}
```

For an opening, loop without writing:

```python
while True:
    bundle = synthesize_blocks(
        selected, pronunciations, settings, model,
        render_spec.voice, render_spec.speed,
    )
    duration = len(bundle.audio) / bundle.sample_rate
    if duration <= max_duration_seconds:
        break
    reduced = remove_final_prose_sentence(selected)
    if reduced is None:
        raise ValueError(
            "Opening headings and shortest prose sentence exceed 30 seconds"
        )
    selected = reduced
render_kind = "opening_sample"
selection = {
    "selected_sentences": [
        sentence
        for block in selected if block.kind is BlockKind.PARAGRAPH
        for sentence in split_sentences(block.text)
    ],
    "duration_seconds": duration,
}
```

Call `write_render_result` exactly once after acceptance. Add duration to the paragraph selection from `len(bundle.audio) / bundle.sample_rate`.

- [ ] **Step 7: Add the `sample` parser and CLI routing**

Add:

```python
sample = commands.add_parser("sample")
sample.add_argument("markdown", type=Path)
sample.add_argument("--output", type=Path, required=True)
sample.add_argument("--voice")
sample.add_argument("--speed", type=float)
sample.add_argument("--paragraph", type=int)
sample.add_argument("--listening-copy", type=Path)
sample.add_argument("--manifest", type=Path)
sample.add_argument("--chunk-manifest", type=Path)
```

In `main`, resolve settings exactly once and pass concrete values:

```python
elif args.command == "sample":
    render_spec = resolve_render_spec(settings, args.voice, args.speed)
    output = run_sample(
        args.markdown,
        args.output,
        render_spec.voice,
        render_spec.speed,
        settings,
        args.pronunciations,
        args.listening_copy,
        paragraph=args.paragraph,
        manifest_path=args.manifest,
        chunk_manifest_path=args.chunk_manifest,
    )
    print(output)
```

Add CLI tests for configured defaults, voice-only, speed-only, combined overrides, and `--paragraph 3`, patching `run_sample` so no real model loads.

- [ ] **Step 8: Run Task 4 and full audio tests**

Run:

```bash
authoring/audio/.venv/bin/python -m unittest \
  authoring.audio.tests.test_narrate.SampleSelectionTests \
  authoring.audio.tests.test_narrate.SampleRenderingTests \
  authoring.audio.tests.test_narrate.NarrationManuscriptTests -v
authoring/audio/.venv/bin/python -m unittest discover \
  -s authoring/audio/tests -v
```

Expected: both commands exit 0 with no failures. Tests show one model load per sample run, no rejected candidate artifacts, full-manuscript provenance, and all existing full-render behavior intact.

- [ ] **Step 9: Commit only Task 4 hunks**

```bash
git add -p authoring/audio/scripts/narrate.py \
  authoring/audio/tests/test_narrate.py
git diff --cached --check
git commit -m "feat: add canonical narration samples"
```

### Task 5: Codex routing instructions and operator documentation

**Files:**
- Modify: `AGENTS.md:7-91`
- Modify: `authoring/audio/README.md:1-145`
- Test: `authoring/audio/tests/test_narrate.py`

**Interfaces:**
- Consumes: final CLI forms `render NARRATION.md` and `sample NARRATION.md [--paragraph N]`, optional `--voice`/`--speed`, explicit output paths, manifests, and chunk manifests.
- Produces: unambiguous agent-level routing for short natural-language requests and operator-facing CLI examples.

- [ ] **Step 1: Update governing instructions**

Replace the current full-chapter restriction with four explicit terms:

```markdown
- **Normal render:** resolve the chapter's existing `narration.md`; omit
  `--voice` and `--speed` so canonical settings apply.
- **Override render:** pass only the voice and/or speed named by the user.
- **Opening sample:** invoke `sample NARRATION.md` with fresh output paths.
- **Paragraph sample:** invoke `sample NARRATION.md --paragraph N`; paragraph
  numbers count prose paragraphs only, not headings.
```

Document the natural-language mappings:

```text
generate chapter 3 audio             -> render current narration.md
regenerate chapter 3 audio           -> fresh render of current narration.md
generate sample of chapter 3         -> opening sample
regenerate sample of chapter 3       -> fresh opening sample
generate paragraph 6 of chapter 3    -> paragraph sample --paragraph 6
regenerate paragraph 6 of chapter 3  -> fresh paragraph sample --paragraph 6
```

State that all generation stops cleanly when `narration.md` is absent and never calls `prepare`. Retain the explicit preparation command as a separate operation. Replace the blanket four-voice restriction with a distinction: the four identifiers constrain only the fixed audition batch; normal explicit overrides may use another valid Kokoro identifier such as `bm_lewis`.

- [ ] **Step 2: Update README command examples and semantics**

Document normal configuration-driven full rendering:

```bash
HF_HUB_OFFLINE=1 authoring/audio/.venv/bin/python \
  authoring/audio/scripts/narrate.py render CHAPTER_DIRECTORY/narration.md \
  --output authoring/audio/output/RUN/CHAPTER.wav \
  --listening-copy authoring/audio/output/RUN/CHAPTER.mp3 \
  --manifest authoring/audio/output/RUN/render-manifest.yaml \
  --chunk-manifest authoring/audio/output/RUN/chunks/chunk-manifest.yaml
```

Add opening and paragraph examples using the same output flags:

```bash
authoring/audio/.venv/bin/python authoring/audio/scripts/narrate.py sample \
  CHAPTER_DIRECTORY/narration.md --output authoring/audio/output/RUN/sample.wav

authoring/audio/.venv/bin/python authoring/audio/scripts/narrate.py sample \
  CHAPTER_DIRECTORY/narration.md --paragraph 6 \
  --output authoring/audio/output/RUN/paragraph-006.wav
```

Explain that only explicit overrides add `--voice` and/or `--speed`, opening samples are at most 30 seconds, paragraph samples are complete and unlimited by the opening cap, and all paths are supplied by the caller rather than discovered by Python.

Document that normal voice validation checks only for a non-empty identifier;
the Kokoro backend reports whether an explicit identifier exists. The fixed
four-voice audition batch retains its whitelist.

- [ ] **Step 3: Run documentation consistency checks**

Run:

```bash
rg -n "voice: null|speed: null|Require the user to name|override/audition|prepare it once" \
  AGENTS.md authoring/audio/README.md \
  authoring/audio/docs/superpowers/specs/2026-09-19-canonical-audiobook-generation-design.md
rg -n "generate paragraph|opening sample|paragraph sample|bm_lewis|--paragraph" \
  AGENTS.md authoring/audio/README.md
```

Expected: the first command returns no stale policy matches; the second finds the new routing and examples in both documents.

- [ ] **Step 4: Run final verification**

Run:

```bash
authoring/audio/.venv/bin/python -m unittest discover \
  -s authoring/audio/tests -v
authoring/audio/.venv/bin/python -m unittest discover \
  -s authoring/audio/chapter-01-full-20260916-215129 -v
git diff --check
git status --short
```

Expected: all audio and preserved chapter-wrapper tests pass; `git diff --check` exits 0; status shows only deliberate task changes plus the known pre-existing working-tree edits.

- [ ] **Step 5: Run the real cached/offline opening-sample smoke test**

Use the existing Chapter One `narration.md`, omit voice and speed overrides,
and write a fresh ignored directory under `authoring/audio/output/`. Prefix the
command with `HF_HUB_OFFLINE=1`. Do not invoke `render` or synthesize a full
chapter. Verify the WAV with `ffprobe` and a full `ffmpeg` decode; inspect the
MP3, duration, `opening_sample` render kind, narration SHA-256, and exact chunk
manifest; listen to the complete sample for basic intelligibility and obvious
artifacts. Leave generated output ignored and untracked.

- [ ] **Step 6: Commit only documentation and any final focused test hunk**

```bash
git add -p AGENTS.md authoring/audio/README.md \
  authoring/audio/tests/test_narrate.py
git diff --cached --check
git commit -m "docs: define canonical audiobook requests"
```

## Final branch review

After all five tasks pass, use the execution skill's whole-branch review flow. The reviewer must compare the implementation to the specification, inspect every ledger ruling, and explicitly check the five Review Focus cases above. Do not render real audio as part of automated verification; fake Kokoro models and temporary files are the approved test mechanism for this implementation.
