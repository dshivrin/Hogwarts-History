# Task 6 audition report

## Execution record

Homebrew `ffmpeg` and `ffprobe` were installed at `/opt/homebrew/bin`; both
report version `9.0.1`. The isolated runtime is CPython `3.12.13` with
`mlx-audio 0.5.3`, `misaki 0.9.4`, and `PyYAML 6.0.2`. Misaki's `en_core_web_sm`
asset was installed in the isolated `.venv` because the package extra does not
include that spaCy model. The British G2P probe returned non-empty phonemes:
`hˈɒɡwɔːts, mˈʌɡᵊl, mˈʌɡᵊlz.`

One successful audition process was invoked with exactly:

```text
authoring/audio/.venv/bin/python authoring/audio/scripts/narrate.py audition \
  --fixture authoring/audio/fixtures/audition-excerpt.txt \
  --sample bm_daniel=0.96 --sample bm_george=0.96 \
  --sample bf_alice=0.96 --sample bf_emma=0.96
```

It used the fixture SHA-256
`cbe7773891b155bcc6c2f84cf36bed9c926fae1fac70ecc3574b0c401f7abbda`,
model `mlx-community/Kokoro-82M-bf16`, revision
`a71e4d38b236d968966a2002c4c895dbd12b1c3c`, and British language code `b`.
The manifest records the same fixture digest and the requested speed `0.96` for
all four samples. Canonical `voice` and `speed` remain null.

## Runtime evidence

Each manifest record reports `Device(gpu, 0)`, `gpu_selected: true`, and
`audio_array_type: mlx.core.array`. Metal telemetry identifies `Apple M4 Pro`
(`applegpu_g16s`), with `active_memory: 327774648`, `cache_memory: 9945780`,
and `peak_memory: 3341753400` bytes. This is an MLX GPU/Metal synthesis record,
not a CPU or NumPy fallback.

## Generated samples and decode checks

All files were fully decoded using `/opt/homebrew/bin/ffmpeg -v error -i FILE
-f null -` with zero decoder output. `ffprobe` reported mono `pcm_s16le` at
24,000 Hz for every file.

| Voice | Speed | File | Duration (s) | SHA-256 |
| --- | ---: | --- | ---: | --- |
| `bm_daniel` | 0.96 | `samples/bm-daniel-096.wav` | 152.675 | `4e32fe84234df1c9e454887236793579a7ffa471aaae1dec3766ab5d5b9cbe86` |
| `bm_george` | 0.96 | `samples/bm-george-096.wav` | 181.950 | `cb9d89a5941b05b2dca40d0762443dd62c6ea47d1943824996552c9f1e97ca17` |
| `bf_alice` | 0.96 | `samples/bf-alice-096.wav` | 162.750 | `6f477ac9ee8ebfbb8731334133b598ba90c36f9dc1b36dc696e394cb28798a98` |
| `bf_emma` | 0.96 | `samples/bf-emma-096.wav` | 165.700 | `e7d155cf33dd9ceaff6650d31dcc4366bb4fbdd23e8059d8a354e46134097a11` |

The manifest additionally records finite samples, non-silent content, peaks
from 0.4171 to 0.6689, and opening/closing silence for every WAV.

## Listening and pronunciation limitation

A sequential full-file local playback attempt was sent to the Mac audio device
using `afplay` for all four files. This execution environment provides no
audio-return channel to the agent, so no subjective listening claims about
warmth, clarity, pacing, artifacts, sentence awkwardness, or the audible forms
of `Hogwarts`, `Muggle`, and `Muggles` are asserted. The successful G2P probe
is only a phonemization fact, not an audible-quality judgment. Accordingly,
`pronunciation-guide.yaml` remains empty and no speed variants were rendered.

## Test result

`authoring/audio/.venv/bin/python -m unittest discover -s authoring/audio/tests
-v` completed with `Ran 28 tests` and `OK`.

## Protection audit

The baseline handoff-document SHA-256 remains
`69008cbe38d9b2e3e6bb18d548637ed0ac4f559d3522d906b6b736665558880c`.
The final audit runs `git diff -- . ':(exclude)authoring/audio/**'` and
`git diff --cached -- . ':(exclude)authoring/audio/**'`; both working-tree and
index comparisons must be empty outside `authoring/audio/`.

The narration-specific history starts at `fe08d84` and must be selected as
`fe08d84^..HEAD`. Do not mutate or rebase the unrelated commits before that
boundary. Known pre-existing untracked material outside `authoring/audio/` is
preserved: `authoring/AGENTS.md`, `authoring/README.md`, `authoring/editions/`,
`authoring/runtime/`, `authoring/shared/`, and
`hogwarts-history-repository-handoff.md`.
