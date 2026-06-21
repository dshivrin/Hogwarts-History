# CLI Tooling Runtime Instruction Update Plan

Review date: 2026-06-21
Repository path: `/Users/dima/Documents/Hogwarts History`

## Purpose

This plan instructs an agent to update the project's runtime instructions so future agents use the available CLI tooling instead of repeatedly reading large files or copying long command sequences.

This is not a content-extraction plan and not a result-output redesign plan. It is a workflow-instruction cleanup plan.

## Current Tooling State

Available and confirmed:

- `rg` / ripgrep: installed and working.
  - Checked version: `ripgrep 15.1.0`
  - Use for fast repository search.
- `jq`: installed and working.
  - Checked version: `jq-1.7.1-apple`
  - Use only for JSON inspection.
- `just`: installed and working.
  - Checked version: `just 1.53.0`
  - Use as the preferred project command runner.
- `make`: available.
  - Checked version: `GNU Make 3.81`
  - Keep as fallback only.

Not installed:

- `yq`
  - Optional future tool only.
  - Do not make runtime instructions depend on it.
  - Use Python project scripts for YAML work instead.

Current project helper files:

- `scripts/check-cli-tools.sh`
- root-level `Justfile`

Current `Justfile` recipes:

```text
default        # Show available commands
tools          # Check installed CLI tools
next           # Show current next-run instructions
status         # Compact project status
search pattern # Search the repo
validate       # Placeholder until real validation is wired
```

Important current gap:

```text
just validate
```

currently prints a placeholder instead of running the real validator. Do not update runtime instructions to rely on `just validate` until the recipe is wired to:

```bash
.venv/bin/python scripts/validate_source_yaml.py
```

## Desired End State

Future agents should orient and work through compact commands:

```bash
just brief
just next
just status
just search "Hogwarts: A History"
just validate
just post
```

The runtime instructions should mention short command patterns only. Keep detailed CLI explanations in supporting instruction files, not in the hot runtime prompt.

## Instruction Update Principles

### 1. Prefer `just` For Repeated Workflows

Use `just` as the stable interface for common project operations.

The runtime contract should not list long repeated post-extraction command chains when a `just` recipe can express the same workflow.

Preferred style:

```text
After changing source YAML or generated helper scripts, run `just post`.
```

Avoid this in the hot runtime prompt:

```text
.venv/bin/python scripts/build_duplicate_index.py
.venv/bin/python scripts/build_entry_index.py
.venv/bin/python scripts/build_tag_index.py
.venv/bin/python scripts/validate_source_yaml.py
.venv/bin/python scripts/generate_book_seed.py
.venv/bin/python scripts/generate_appendices.py
.venv/bin/python scripts/update_next_run.py
.venv/bin/python scripts/cleanup_tmp.py
```

The long command sequence can remain in a support plan or recipe implementation, but not in the routine agent read path.

### 2. Use `rg` For Search Before File Reading

Agents should search first, then open narrow file ranges.

Recommended runtime wording:

```text
Use `just search "pattern"` or direct `rg "pattern" path/` before reading broad files.
Prefer targeted search results plus narrow `sed -n` reads over opening large appendices, archives, or source collections.
```

### 3. Use Python Scripts For YAML

Do not require `yq`.

Recommended runtime wording:

```text
Use project Python scripts for YAML validation, query, and generation.
Do not depend on `yq`; it is optional and not installed.
```

### 4. Keep `jq` Narrowly Scoped

`jq` is useful, but current core project state is YAML and Markdown.

Recommended runtime wording:

```text
Use `jq` only for structured JSON output if future scripts emit JSON.
Do not convert YAML workflows to JSON just to use `jq`.
```

### 5. Keep The Runtime Contract Small

The runtime contract is a hot prompt file. It should contain only:

- required reads
- prohibited broad reads
- short command recipes
- extraction rules
- validation expectations

Move detailed tool rationale into this file or a future tooling guide, not into `runtime-contract.md`.

## Recommended `Justfile` Recipe Expansion

Before updating runtime instructions to rely on these recipes, wire them into `Justfile`.

Recommended recipes:

```just
# Install Python dependencies into the existing virtual environment
setup:
    .venv/bin/python -m pip install -r requirements.txt

# Run the source/index/generated-file validator
validate:
    .venv/bin/python scripts/validate_source_yaml.py

# Run the current test suite
test:
    .venv/bin/python -m unittest tests/test_refactor_support.py

# Rebuild compact indexes
indexes:
    .venv/bin/python scripts/build_duplicate_index.py
    .venv/bin/python scripts/build_entry_index.py
    .venv/bin/python scripts/build_tag_index.py

# Regenerate human-facing outputs and next-run display
generate:
    .venv/bin/python scripts/generate_book_seed.py
    .venv/bin/python scripts/generate_appendices.py
    .venv/bin/python scripts/update_next_run.py

# Full normal post-change workflow
post:
    just indexes
    just validate
    just generate
    .venv/bin/python scripts/cleanup_tmp.py
    just test

# Compact orientation for routine agents
brief:
    just status

# Query possible duplicate or corroborating entries by tags
query-dupes *tags:
    .venv/bin/python scripts/query_duplicates.py --tags {{tags}}

# Query indexed entries by one tag
query-entries tag:
    .venv/bin/python scripts/query_entries.py --tag "{{tag}}"
```

Optional future recipes:

```just
# Extract the current source unit listed in processing-state.yaml
extract-current:
    # Implement only if a small wrapper script exists to read current_source_unit.

# Open compact generated output preview
seed-head:
    sed -n '1,180p' book-seed/hogwarts-a-history-seed.md
```

Do not add recipes that require parsing YAML in shell with fragile `grep` or `awk`. If a recipe needs structured YAML state, add a small Python script first.

## Files To Update

### 1. `Justfile`

Goal:

Wire real project-specific recipes and remove the placeholder validator.

Required changes:

- Replace placeholder `validate` recipe with the real validator command.
- Add `test`, `indexes`, `generate`, `post`, `brief`, `query-dupes`, and `query-entries`.
- Keep `tools`, `next`, `status`, and `search`.
- Keep recipe names short and stable.

Acceptance criteria:

```bash
just --list
just tools
just brief
just validate
just test
```

all run successfully, except `just tools` may report optional `yq` missing without failing.

### 2. `docs/instructions/runtime-contract.md`

Goal:

Update the hot runtime instructions to use `just` recipes without increasing prompt size.

Required changes:

- Add a short `CLI Workflow` section near the top.
- Mention:
  - `just brief` for orientation.
  - `just next` for current next-run instructions.
  - `just search "pattern"` or `rg` for targeted search.
  - `just query-dupes ...` for duplicate lookup after tags are known.
  - `just validate` after source YAML changes.
  - `just post` after completed extraction or generator changes.
- Replace the long post-extraction command sequence with `just post`.
- Keep the existing rule against reading full archives, appendices, and all prior YAML files.
- Explicitly say not to require `yq`.

Suggested compact wording:

```markdown
## CLI Workflow

Prefer short project recipes over repeated long shell commands.

- Start orientation with `just brief`.
- Use `just next` for the current next-run display.
- Use `just search "pattern"` or direct `rg "pattern" path/` before reading broad files.
- Use `just query-dupes <tag> <tag>` for duplicate lookup after candidate tags are known.
- Use `just validate` after source YAML changes.
- Use `just post` after a completed extraction or generator change.

Do not require `yq`; use project Python scripts for YAML.
Use `jq` only for JSON output.
```

### 3. `tests/test_refactor_support.py`

Goal:

Keep the unittest suite aligned with the new command-contract behavior.

Required changes:

- Remove or replace the obsolete `test_runtime_contract_lists_post_extraction_flow_order` test. It currently asserts that `runtime-contract.md` contains the expanded post-extraction script sequence, which is exactly what this plan removes from the hot runtime prompt.
- Add a focused runtime-contract test that asserts:
  - the `CLI Workflow` section exists.
  - the contract includes `just brief`, `just next`, `just search`, `just query-dupes`, `just validate`, and `just post`.
  - the output steps say to run `just post`.
  - the old expanded command sequence is not present in `runtime-contract.md`.
  - the contract explicitly says not to require `yq`.
- Add a focused Justfile test that asserts the root `Justfile` exposes the intended recipe names:
  - `brief`
  - `test`
  - `indexes`
  - `generate`
  - `post`
  - `query-dupes`
  - `query-entries`
- Do not keep a test that requires the hot runtime prompt to spell out `build_duplicate_index.py`, `build_entry_index.py`, `build_tag_index.py`, `validate_source_yaml.py`, `generate_book_seed.py`, `generate_appendices.py`, `update_next_run.py`, and `cleanup_tmp.py` in order.

Suggested replacement test shape:

```python
def test_runtime_contract_uses_compact_cli_workflow(self) -> None:
    contract = Path("docs/instructions/runtime-contract.md").read_text(encoding="utf-8")

    self.assertIn("## CLI Workflow", contract)
    for text in [
        "just brief",
        "just next",
        "just search",
        "just query-dupes",
        "just validate",
        "just post",
        "Do not require `yq`",
    ]:
        self.assertIn(text, contract)

    self.assertNotIn(".venv/bin/python scripts/build_duplicate_index.py", contract)
    self.assertNotIn(".venv/bin/python scripts/build_entry_index.py", contract)
    self.assertNotIn(".venv/bin/python scripts/build_tag_index.py", contract)
    self.assertNotIn(".venv/bin/python scripts/validate_source_yaml.py", contract)
    self.assertNotIn(".venv/bin/python scripts/generate_book_seed.py", contract)
    self.assertNotIn(".venv/bin/python scripts/generate_appendices.py", contract)
    self.assertNotIn(".venv/bin/python scripts/update_next_run.py", contract)
    self.assertNotIn(".venv/bin/python scripts/cleanup_tmp.py", contract)


def test_justfile_exposes_compact_workflow_recipes(self) -> None:
    justfile = Path("Justfile").read_text(encoding="utf-8")

    for recipe in [
        "brief:",
        "test:",
        "indexes:",
        "generate:",
        "post:",
        "query-dupes *tags:",
        "query-entries tag:",
    ]:
        self.assertIn(recipe, justfile)
```

### 4. `docs/instructions/result-output-redesign-plan.md`

Goal:

Keep the result-output plan aligned with the command workflow.

Required changes:

- In the implementation plan's regenerate/review step, replace the long command sequence with:

```bash
just post
```

- Keep the detailed command list only if it is clearly labeled as the expanded implementation of `just post`.

### 5. `docs/instructions/hogwarts-history-seed-builder.md`

Goal:

If this file remains the human entrypoint, make it point routine agents to the compact runtime contract and short recipes.

Required changes:

- Do not add a long tool tutorial.
- Add one sentence:

```text
Routine agents should follow `docs/instructions/runtime-contract.md` and use the root `Justfile` recipes for orientation, validation, search, and post-run generation.
```

## Recommended Runtime Contract Shape After Update

The top of `runtime-contract.md` should roughly be:

```markdown
# Runtime Contract

Use this compact contract for routine extraction runs. Read full background or schema files only when this contract says to.

## CLI Workflow

Prefer short project recipes over repeated long shell commands.

- Start orientation with `just brief`.
- Use `just next` for the current next-run display.
- Use `just search "pattern"` or direct `rg "pattern" path/` before reading broad files.
- Use `just query-dupes <tag> <tag>` for duplicate lookup after candidate tags are known.
- Use `just validate` after source YAML changes.
- Use `just post` after a completed extraction or generator change.

Do not require `yq`; use project Python scripts for YAML.
Use `jq` only for JSON output.

## Required Reads
...
```

The output steps should become:

```markdown
## Output Steps

1. Write or update the current chapter YAML path in `processing-state.yaml`.
2. Keep full chapter YAML self-contained and schema-compliant.
3. Run `just post`.
4. Keep `book-seed/hogwarts-a-history-seed.md` as the main human-readable result.
5. Keep `appendix/generated/*.md` as generated support/reference files.
```

## Test And Verification Plan

After implementing the test, instruction, and recipe updates, run:

```bash
just --list
just tools
just brief
just validate
just test
```

Then run:

```bash
just post
```

Expected:

- `just --list` shows the new recipes.
- `just tools` succeeds when required tools are available.
- `just brief` prints compact orientation.
- `just validate` runs the Python validator, not a placeholder.
- `just test` runs `unittest`, including the replacement tests for compact runtime CLI wording and Justfile recipe coverage.
- `just post` rebuilds indexes, validates, regenerates outputs, cleans temporary files, and runs tests.
- The obsolete runtime-contract test for the expanded long command sequence is removed or replaced, so no test requires the hot runtime prompt to contain that sequence.

If `just post` changes generated files, review:

```bash
git diff --stat
git diff -- book-seed/hogwarts-a-history-seed.md appendix/generated/
```

## What Not To Do

- Do not require `yq`.
- Do not replace Python YAML scripts with shell parsing.
- Do not expand `runtime-contract.md` into a full tool manual.
- Do not remove direct script commands from developer plans where exact expansion is useful.
- Do not make `make` the primary runner; keep `just` primary and `make` fallback only.
- Do not add `pytest` as the official test command unless the dependency is added intentionally.
- Do not make normal agents read large appendices, archives, or all source YAML files for orientation.

## Summary

The project now has enough CLI tooling to reduce routine agent context load further. The next step is to make the root `Justfile` the stable command surface, then update the runtime instructions to reference only short recipes and targeted search patterns.

The intended behavioral change is:

```text
Before:
Agent reads instructions, scans files, and copies long command chains.

After:
Agent starts with `just brief`, searches with `rg`/`just search`, queries duplicates with project scripts, and finishes with `just post`.
```
