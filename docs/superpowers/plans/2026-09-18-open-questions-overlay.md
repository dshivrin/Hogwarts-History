# Open Questions Editorial Overlay Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the duplicated enriched-question proposal with a validated, chapter-queryable editorial overlay covering all 386 canonical open questions.

**Architecture:** The canonical open-question YAML remains unchanged. A migration/validation/query module joins canonical questions with a compact overlay keyed by question ID, validates evidence against the compact entry index, validates sources against the overlay catalog and repository inventory, and validates chapter IDs against the authoritative 20-chapter table of contents. The rewritten guide documents a local-first research and drafting workflow.

**Tech Stack:** Python 3, PyYAML, `unittest`, existing compact YAML indexes and `Justfile` command surface.

**Spec:** Approved in-chat design on 2026-09-18, informed by `resources/external/open-questions-scapping/open-questions-integration-audit.md`.

## Global Constraints

- Preserve all 386 canonical question IDs without merging or deletion.
- Do not modify canonical open questions, source YAML, generated indexes, chapter plans, or manuscript files.
- Verified facts require exact evidence IDs; interpretation and creative reconstruction remain separate fields.
- Every question uses an existing chapter ID from 1 through 20.
- Existing local evidence is searched before any unavailable external candidate.
- Back up the two proposal files byte-for-byte before replacement.
- Do not commit.

---

### Task 1: Backups and Overlay Contract

**Files:**
- Create: `resources/external/open-questions-scapping/hogwarts-open-questions-enriched.pre-restructure-2026-09-18.yaml`
- Create: `resources/external/open-questions-scapping/hogwarts-open-questions-codex-guide.pre-restructure-2026-09-18.md`
- Create: `tests/test_open_questions_overlay.py`

**Interfaces:**
- Consumes: canonical questions, legacy proposal, current TOC, entry index, external manifest.
- Produces: executable expectations for `build_overlay`, `validate_overlay`, and `questions_for_chapter`.

- [x] Copy both proposal files to dated backup paths and verify SHA-256 equality.
- [x] Write tests requiring 386 unique IDs, exact canonical coverage, valid evidence/source/chapter references, separation of facts/inference/creative fields, and chapter-filtered retrieval.
- [x] Run the focused test and confirm it fails because `scripts.open_questions_overlay` does not exist.

### Task 2: Migration, Validation, and Query Module

**Files:**
- Create: `scripts/open_questions_overlay.py`
- Modify: `tests/test_open_questions_overlay.py`

**Interfaces:**
- Produces: `build_overlay(root: Path, legacy: dict) -> dict`, `validate_overlay(root: Path, overlay: dict) -> list[str]`, and an ID-keyed result from `questions_for_chapter(overlay: dict, chapter_id: int)`.

- [x] Implement the minimal source-catalog migration with canonical manifest IDs for local sources and explicit `candidate_unverified` records for absent URLs.
- [x] Implement stable chapter mapping to IDs 1–20, including question-specific overrides identified by the audit.
- [x] Implement reviewed partial answers with exact evidence IDs and retain residual questions.
- [x] Implement default unreviewed records with no asserted facts and no creative eligibility before research review.
- [x] Implement validation and chapter query output.
- [x] Run the focused tests and confirm they pass.

### Task 3: Generate the Compact Overlay and Rewrite the Guide

**Files:**
- Modify: `resources/external/open-questions-scapping/hogwarts-open-questions-enriched.yaml`
- Modify: `resources/external/open-questions-scapping/hogwarts-open-questions-codex-guide.md`

**Interfaces:**
- Consumes: the backed-up legacy proposal and canonical repository data.
- Produces: schema-versioned compact overlay and drafting/research guide.

- [x] Run the migration command against the dated legacy backup.
- [x] Rewrite the guide to document authority, schema, local-first search stages, partial-answer handling, chronology, inference/creative boundaries, chapter retrieval, and update rules.
- [x] Query representative chapters 2, 5, 10, and 17 and inspect returned records.

### Task 4: Repository Command Integration and Full Verification

**Files:**
- Modify: `Justfile`

**Interfaces:**
- Produces: `just validate-open-questions` and inclusion in `just validate`.

- [x] Add the read-only overlay validator command.
- [x] Run the focused overlay tests.
- [x] Run `just validate` and `just test`.
- [x] Verify backup hashes, all 386 IDs, evidence references, source references, chapter IDs, and zero tracked changes outside the authorized files.
- [x] Inspect the final working-tree diff and report results without committing.
