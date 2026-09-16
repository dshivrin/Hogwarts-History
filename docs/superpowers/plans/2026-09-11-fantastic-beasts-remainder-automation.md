# Fantastic Beasts Remainder Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Do not delegate this sequential, shared-state queue migration.

**Goal:** Activate a backed-up, one-unit-per-run automation queue for the ten locally available *Fantastic Beasts and Where to Find Them* PDF units without modifying any completed result.

**Architecture:** Preserve the completed active plan and external runtime as byte-identical archive files, append a `book-fb` source family to the existing plan, and make the current/next PDF pointers take precedence over the exhausted external queue. Advancement remains state-driven but uses the ordered source plan for nonnumeric companion groups and final-queue exhaustion. Unacquired carriers remain blocked in a separate structured backlog.

**Tech Stack:** Python 3, PyYAML, `unittest`, Poppler `pdftoppm`, Markdown, YAML, `just`, Git, and the Codex local scheduled-task runtime.

---

### Task 1: Preserve completed controls and document the approved design

**Status:** done

**Files:**
- Create: `project-control/archive/source-plan-completed-2026-08-24.yaml`
- Create: `docs/instructions/archive/runtime-contract-external-source-extraction-completed-2026-09-11.md`
- Create: `docs/superpowers/specs/2026-09-11-fantastic-beasts-remainder-automation-design.md`
- Create: `docs/superpowers/plans/2026-09-11-fantastic-beasts-remainder-automation.md`

- [x] **Step 1: Record the approved ten-unit boundary and blocked-acquisition policy in the design spec**
- [x] **Step 2: Record an executable implementation plan with explicit files, tests, and verification commands**
- [x] **Step 3: Copy the active source plan and external runtime without transformations**
- [x] **Step 4: Verify each backup with `cmp` and matching SHA-256 output**

### Task 2: Specify PDF queue behavior with failing tests

**Status:** done

**Files:**
- Modify: `tests/test_refactor_support.py`

- [x] **Step 1: Add a test proving a current PDF unit renders instead of an exhausted external queue**
- [x] **Step 2: Run the focused test and observe the external-queue rendering failure**
- [x] **Step 3: Add a test proving `book-fb` advances through ordered plan rows**
- [x] **Step 4: Run the focused test and observe the nonnumeric-group failure**
- [x] **Step 5: Add a test proving a final unit advances to null current/next pointers**
- [x] **Step 6: Run the focused test and observe the missing-next failure**
- [x] **Step 7: Add validator and source-index tests for `book-fb` and `fb-chNN`**
- [x] **Step 8: Run the focused tests and observe the unsupported-name/prefix failures**

### Task 3: Implement plan-driven one-unit PDF advancement

**Status:** done

**Files:**
- Modify: `scripts/update_next_run.py`
- Modify: `scripts/validate_source_yaml.py`
- Modify: `scripts/build_entry_index.py`
- Modify: `tests/test_refactor_support.py`

- [x] **Step 1: Prefer `current_source_unit` before external queue rendering**
- [x] **Step 2: Resolve following units from ordered `source-plan.yaml` rows, including page boundaries and output paths**
- [x] **Step 3: Allow a current unit with null next pointer to complete the queue**
- [x] **Step 4: Mark the promoted row `in_progress` while marking only the completed row `complete`**
- [x] **Step 5: Accept `book-fb/chapter-NN-...yaml` and assign the `fb-chNN` source-unit prefix**
- [x] **Step 6: Run all focused tests and confirm green**

### Task 4: Queue the ready units and structure blocked work

**Status:** done

**Files:**
- Modify: `project-control/source-plan.yaml`
- Modify: `project-control/processing-state.yaml`
- Create: `project-control/remaining-source-units.yaml`
- Modify: `project-control/next-run.md` (generated)

- [x] **Step 1: Append FB00–FB09 with exact inclusive page ranges and output paths**
- [x] **Step 2: Set FB00/current to `in_progress`, FB01/next to `pending`, and FB02–FB09 to `pending`**
- [x] **Step 3: Keep all 280 existing completed rows unchanged**
- [x] **Step 4: Add blocked acquisition/recovery units with precise unblock conditions and update targets**
- [x] **Step 5: Regenerate `project-control/next-run.md` and inspect the rendered FB00 task**

### Task 5: Replace the active worker instructions

**Status:** done

**Files:**
- Modify: `docs/instructions/runtime-contract.md`
- Modify: `docs/instructions/schema-reference.md`
- Modify: `Justfile`
- Create: `scripts/complete_current_unit.py`
- Modify: `tests/test_refactor_support.py`

- [x] **Step 1: Add the PDF/external/no-ready dispatcher and scanned-page visual procedure**
- [x] **Step 2: State the exact one-unit stop boundary and current/next ownership rules**
- [x] **Step 3: Document `book-fb`, `fb-chNN-NNN`, and rendered-image locators**
- [x] **Step 4: Add an `advance-current` recipe whose completion transaction restores control/generated artifacts after any downstream failure**
- [x] **Step 5: Update runtime/Justfile behavior tests and run them**

### Task 6: Verify and activate the existing automation

**Status:** done

**Files:**
- Modify externally: existing Codex automation `hogwarts-history`

- [x] **Step 1: Run focused unit tests for advancement, validation, indexing, runtime, and command surface**
- [x] **Step 2: Run `just test`, `just validate`, and YAML consistency checks**
- [x] **Step 3: Confirm backups still compare byte-for-byte and no completed source result changed**
- [x] **Step 4: Inspect the existing automation and preserve its cadence, project, model, and reasoning effort**
- [x] **Step 5: Replace its prompt with the one-unit dispatcher instructions and set it active**
- [x] **Step 6: Verify the automation view reports active status and the updated prompt**
- [x] **Step 7: Commit only the remainder-queue implementation files after reviewing staged diff**
