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
`mlx-audio==0.5.3`, `misaki[en]==0.9.4`, and `PyYAML==6.0.2`. A later runtime
task may record the complete resolved environment in `requirements-lock.txt`.

## Test and audition commands

```bash
authoring/audio/.venv/bin/python -m unittest discover -s authoring/audio/tests -v
authoring/audio/.venv/bin/python authoring/audio/scripts/narrate.py audition \
  --fixture authoring/audio/fixtures/audition-excerpt.txt \
  --sample bm_daniel=0.96 --sample bm_george=0.96 \
  --sample bf_alice=0.96 --sample bf_emma=0.96
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
After the model and voice data have been downloaded once, reruns should use
the local Hugging Face/MLX cache and require no paid API or subscription. Keep
the virtual environment and caches under their documented paths, and never
rewrite the source manuscript as part of narration preparation.
