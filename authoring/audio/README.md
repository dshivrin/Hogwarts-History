# Local narration prototype

This directory contains the local Kokoro audition tooling for the 1984 edition
manuscript. It is intentionally isolated from the manuscript and research
layers. The canonical narrator settings keep `voice` and `speed` unset; an
audition supplies those values for that run without rewriting the settings.

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
`mlx-community/Kokoro-82M-bf16`, and the four listed voices at speed `0.96`.
Do not render the complete chapter in this prototype.

## Files, outputs, and offline reuse

`narration-settings.yaml` is the canonical configuration: `engine`, `model`,
`language`, `lang_code`, pauses, chunk target, and WAV/MP3 output formats are
stable; `voice: null` and `speed: null` remain unset until selection. The
versioned pronunciation guide starts empty and must contain only tested,
documented narration-layer substitutions.

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

The four approved `0.96` WAVs have technical verification only. This execution
environment has no audio-return channel, so it has not established comparative
voice quality, pacing, artifacts, audible pronunciation of `Hogwarts`,
`Muggle`, or `Muggles`, or awkward spoken sentences. A human must listen to all
four complete samples before any speed variant, pronunciation substitution, or
narrator selection. Until then, leave `pronunciation-guide.yaml` empty and
keep canonical `voice: null` and `speed: null`.
