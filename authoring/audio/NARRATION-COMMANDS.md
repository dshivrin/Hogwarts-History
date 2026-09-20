# Narration Commands

```text
prepare narration for chapter 1

generate sample of chapter 1
regenerate sample of chapter 1

generate paragraph 6 of chapter 1
regenerate paragraph 6 of chapter 1

generate chapter 1 audio
regenerate chapter 1 audio
```

Optional overrides:

```text
generate paragraph 6 of chapter 1 at 0.92
generate sample of chapter 1 with bm_lewis
```

- `prepare narration` creates the persistent `narration.md` only when it does
  not already exist.
- `generate` and `regenerate` always use the current existing `narration.md`.
  They never recreate, overwrite, or replace it.
- An opening sample is a short title-and-opening audition.
- A paragraph sample renders one prose paragraph for focused tuning.
- Full generation renders the entire current narration manuscript.
