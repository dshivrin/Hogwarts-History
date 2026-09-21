# Hogwarts History — Runtime Audit and Future Tooling Plan

Audit date: 2026-09-21  
Mode: read-only repository audit, followed by creation of this report only

No repository tooling, dependencies, runtime instructions, evidence, generated
artifacts, or chapter files were changed by the audit. Chapter 5 changed
concurrently during the audit; the final diff outside its chapter workspace and
`chapter-status.yaml` was empty before this report was created.

## 1. Current environment

- Root `.venv`: exists; `.venv/bin/python` is executable.
- Python: 3.9.6.
- PyYAML: 6.0.3, available in the project environment.
- pypdf: 6.13.1, available in the project environment.
- Installed root packages also include `yamllint 1.37.1`, `pathspec 1.1.1`,
  and `typing_extensions 4.15.0`.
- CLI tools:
  - `rg 15.1.0`: installed.
  - `jq 1.7.1`: installed.
  - `just 1.53.0`: installed.
  - GNU Make 3.81: installed.
  - Poppler tools: installed.
  - `yq`: absent, correctly optional.
- Separate environments are correctly used for fan-work tooling
  (`.fanfic-venv`, Python 3.12.13) and audiobook tooling
  (`authoring/audio/.venv`).

One important defect: although `.gitignore` excludes `.venv`, 746 root
virtual-environment files are already tracked by Git.

## 2. Why the repeated warning occurs

The warning is factually true about PATH Python but irrelevant to repository
health:

- `python` is unavailable.
- `/usr/bin/python3` is Python 3.9.6 and cannot import `yaml`.
- `.venv/bin/python` is also Python 3.9.6 but has PyYAML 6.0.3.

The maintained `Justfile` consistently invokes `.venv/bin/python`, so current
recipes are correct. The active runtime contract also routes routine work
through `just`.

The actual cause is an instruction gap: the root `AGENTS.md` defines the
audiobook interpreter but never states that general repository tooling must use
`.venv/bin/python`. When an agent performs an unsolicited
`python3 -c "import yaml"` check, it reaches system Python and emits the
warning. The `#!/usr/bin/env python3` script shebangs leave the same ambiguity
when scripts are executed directly.

No tracked file contains the quoted warning itself. Older planning material
contains some bare `python`/`python3` examples, but active root workflows do
not.

## 3. Dependency gaps

The root `requirements.txt` declares:

- Pinned and installed: PyYAML, yamllint, pypdf, pathspec, typing_extensions.
- Declared but not installed in `.venv`: pytest, ruff, jsonschema, Jinja2,
  rapidfuzz.
- Actually needed by maintained core scripts: PyYAML and pypdf.
- `pathspec` and `typing_extensions` are transitive dependencies of
  yamllint/pypdf under this Python version.
- `jsonschema` and pytest are used by the separate fan-work test suite and are
  already declared in `requirements-fanfic.txt`.
- No maintained root code imports Jinja2, rapidfuzz, or ruff.

Therefore there is no current PyYAML or pypdf runtime gap. The gap is
reproducibility and manifest hygiene:

- Python version is not declared.
- Five requirements are unpinned.
- The installed root environment does not match its manifest.
- A tracked platform-specific `.venv` masks reconstruction problems.

Future recommendation: retain `requirements.txt` as the canonical root tooling
manifest rather than introduce a competing packaging system. Pin only direct
root dependencies; move genuine developer-only tools into a small
`requirements-dev.txt` if retained. Do not use `pip freeze`.

## 4. Existing reusable tooling

Canonical and reusable:

- `scripts/query_entries.py`: tag, classification, reference type, confidence,
  source-unit, and output-YAML lookup.
- `scripts/query_duplicates.py`: ranked duplicate/corroboration candidates.
- `scripts/build_entry_index.py`: entry and source indexes.
- `scripts/build_tag_index.py`: tag index.
- `scripts/build_duplicate_index.py`: duplicate index.
- `scripts/validate_source_yaml.py`: canonical evidence and provenance
  validation.
- `scripts/extract_pages.py`: text-PDF page-range extraction.
- `generate_book_seed.py`, `generate_appendices.py`,
  `open_questions_overlay.py`, and `source_files.py`: maintained
  generation/support tools.
- `complete_current_unit.py`, `update_next_run.py`, and
  `external_sources/queue.py`: well-tested but currently extraction-era
  machinery.
- `fanfic_dataset/`: substantial reusable library code, but unfinished as a
  command-line subsystem.

Superseded tracked copies:

- `scripts/query_entries 2.py`
- `scripts/query_duplicates 2.py`
- `scripts/generate_book_seed 2.py`

These are older, non-identical copies that omit later Cursed Child/timeline
behavior. Active recipes use the canonical filenames. They should eventually be
removed after a clean-history and reference check.

## 5. Disposable-script problems

No tracked heredoc-based Python or named `tmp_query.py`/`scratch.py` pattern was
found. The problem is mainly a tooling gap that encourages agents to improvise:

| Recurring operation | Current method | Reuse likelihood | Recommended home |
|---|---|---:|---|
| Exact entry lookup | Direct YAML or inline parsing | High | Extend `query_entries.py` with `--id` |
| Source lookup | Open/search `source-index.yaml` | High | Add source filters to `query_entries.py` |
| Chapter/topic evidence | Multiple tag calls and manual merging | High | Repeatable tags/chapter filter in `query_entries.py` |
| Approved-manuscript resolution | Manually parse `chapter-status.yaml` | High | New authoring status CLI |
| Chapter status | Manually inspect a large YAML file | High | Same authoring status CLI |
| Hash verification | `shasum` commands and temporary checksum files | High | `chapter hashes`/`chapter verify` subcommands |
| Research-brief orientation | Manual scans and searches | Medium/high | Read-only `chapter brief-context`; do not auto-write prose briefs |
| Image-only PDF range rendering | Raw `pdftoppm` invocation | Occasional | A `just render-pages` wrapper |
| Text-PDF extraction | Raw `extract_pages.py` invocation | Occasional | A `just extract-text` wrapper |

Hash and chapter-pointer operations are mandatory parts of the current
authoring workflow, so their recurrence is established even though disposable
Python files are not preserved in Git.

## 6. `Justfile` recommendations

There are currently 23 recipes. Useful read-only recipes include `tools`,
`next`, `status`, `brief`, `search`, `validate`, `validate-open-questions`,
`test`, `current-external`, `external-status`, `query-dupes`, and
`query-entries`.

Mutating recipes include `setup`, `indexes`, `generate`, `post`, `clean-cache`,
`advance-current`, and the external queue transitions.

Important limitations:

- `status`, `brief`, and `next` still describe extraction state, not current
  authoring state.
- `query-entries` exposes only the single-tag interface, although its
  underlying script supports more filters.
- No environment doctor, authoring status, pointer resolution, hash
  verification, or extraction wrapper exists.
- `tools` checks only CLI availability, not Python environments or imports.

Proposed later additions:

```text
just doctor
just status [chapter]
just next
just query <arguments...>
just hashes <chapter>
just verify-chapter <chapter>
just extract-text ...
just render-pages ...
```

Preserve `query-dupes` because duplicate ranking has distinct semantics. Avoid
hiding mutating behavior behind `status`, `next`, or `doctor`.

## 7. Runtime-instruction recommendations

After Chapter 5 is finished:

1. Add an exact top-level rule to `AGENTS.md`:

   > Repository Python tooling uses `.venv/bin/python`. Do not use `python` or
   > `python3` to determine whether repository dependencies are installed.
   > Prefer the root `Justfile` for supported workflows.

2. Update `authoring/shared/research-interface.md` to prefer the expanded
   stable query recipe and authoring status command.
3. Update the active authoring contract to name the status/hash command once
   implemented.
4. Keep the active extraction runtime's `just`-first routing; it is already
   correct.
5. Do not cosmetically update archived plans or historical runtime snapshots.
6. Add “inspect `Justfile`, maintained-tool index, then `scripts/`” before
   permitting new helper scripts.

## 8. Proposed permanent tooling architecture

Keep the architecture small:

- Environment: `scripts/project_doctor.py`, exposed as `just doctor`; strictly
  read-only, machine-detectable exit status, compact output.
- Evidence querying: extend `query_entries.py`; retain `query_duplicates.py`
  for ranked duplicate analysis.
- Extraction: retain `extract_pages.py`; expose text and image rendering
  separately because pypdf extraction and Poppler rendering solve different
  problems.
- Evidence validation: retain `validate_source_yaml.py` and
  `open_questions_overlay.py`.
- Authoring status: add one focused authoring CLI with `status`, `next`,
  `approved`, `brief-context`, `hashes`, and `verify` subcommands.
- Hash checking: integrate with authoring status so it validates recorded paths
  and SHA-256 values rather than becoming a generic hash utility.
- Brief generation: generate bounded context only; do not automatically create
  or overwrite editorial `brief.md`.

`just doctor` should check `.venv/bin/python`, Python version, PyYAML, pypdf,
maintained-tool imports, `rg`, `jq`, `just`, and required current paths. Make,
yq, Poppler, fan-work, and audiobook dependencies should be reported
conditionally.

## 9. Concurrency-safe implementation sequence

1. Finish, review, and commit Chapter 5 first.
2. Confirm a clean worktree and no active authoring agents.
3. Add tests and the read-only doctor. Shared `Justfile` and instruction changes
   are best done between authoring runs.
4. Normalize root dependency declarations and declare the supported Python
   version. Do this only with no concurrent agents.
5. Extend query tooling without removing old interfaces; run query regression
   tests.
6. Add the authoring status/hash/pointer CLI and test it against fixture copies
   of chapter control data.
7. Update `Justfile`, root instructions, and active authoring documentation
   together.
8. Remove superseded `* 2.py` copies only after proving no references remain.
9. Untrack `.venv` with `git rm --cached` in a dedicated maintenance commit; do
   not delete the local environment.
10. Run full validation and tests, then verify generated outputs have not
    changed unexpectedly.

Only read-only auditing is unconditionally safe during active authoring. Query
implementation, dependency files, `Justfile`, shared instructions,
chapter-status machinery, index generators, and `.venv` cleanup should wait
until no other agent is modifying the repository.

## 10. Suggested follow-up maintenance task

- [ ] Verify Chapter 5 is committed and the worktree is clean.
- [ ] Record the current root and fan-work interpreter/package baselines.
- [ ] Add failing tests for doctor success, missing `.venv`, missing imports,
      optional yq, and required CLI/path checks.
- [ ] Implement `scripts/project_doctor.py` and `just doctor`.
- [ ] Reduce and pin direct dependencies in `requirements.txt`; separate actual
      developer dependencies if needed.
- [ ] Declare the supported root Python version.
- [ ] Add `--id`, repeatable tags, source, and chapter-oriented filters to
      `query_entries.py`.
- [ ] Add regression tests preserving existing query output and `query-dupes`
      behavior.
- [ ] Implement the read-only authoring status/pointer/hash CLI with
      fixture-based tests.
- [ ] Add `just status`, `just next`, `just hashes`, and extraction wrappers
      with explicit read/write behavior.
- [ ] Update root `AGENTS.md` and active runtime documents; leave archives
      unchanged.
- [ ] Prove the three numbered script copies are unreferenced, then remove
      them.
- [ ] Untrack—but do not physically delete—the ignored root `.venv`.
- [ ] Run core tests, fan-work tests where applicable, validation, doctor, and a
      final clean-diff/generated-output check.

## Audit-end repository state

Before this report was created, the only working-tree changes were the
concurrent Chapter 5 work: one modification to
`authoring/editions/1984/project-control/chapter-status.yaml` and six untracked
Chapter 5 files. There were no staged files and no changes outside that
concurrent scope.
