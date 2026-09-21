# Evidence Synthesis Workflow Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the project-wide evidence-synthesis and anti-repetition workflow, templates, naming rules, and verification checkpoint without modifying any existing chapter manuscript, outline, audit, or research artifact.

**Architecture:** Keep policy responsibilities layered: evidence consolidation rules in the shared evidence policy, stage and artifact rules in the chapter workflow, compact invariants in the runtime contract, prose checks in the style lock, and only routing or high-level authority in the AGENTS and editorial-policy files. Add one generic synthesis template and extend the existing outline and required audit templates. Preserve the current state enums and make synthesis plus validation mandatory gates within `evidence_reviewed`, avoiding a breaking state-schema migration.

**Tech Stack:** Markdown policy and templates, YAML project control, Git diff and checksum verification, repository text searches.

**Spec:** This checked-in plan is self-contained. The user-supplied attachment informed it but is not a runtime dependency.

## Global Constraints

- Work only under `authoring/`; the research/evidence layer remains read-only.
- Do not modify or overwrite any existing chapter manuscript, revision, final candidate, outline, audit, preparation package, evidence selection, or evidence-gaps file.
- Keep chapter workspaces under `authoring/editions/1984/drafts/draft-01/chapters/`.
- Preserve generic historical artifacts while introducing `evidence-synthesis-revision-NN.md` and `outline-revision-NN.md` for new work.
- Preserve Chapter 1 approved revision 07 and Chapter 2 approved revision 06, including their paths and SHA-256 values; Chapter 3 remains unapproved.
- Stop after policy/template implementation and verification; do not begin Chapter 1 revision 08 during this phase.

## Binding Functional Requirements

- Raw selected evidence must be consolidated into claims and validated before an outline may be created.
- A synthesis validates only when its filename and target revision match, its verdict is `PASS`, it has no unresolved blocking verification item, every claim has a permitted disposition, every selected evidence ID is accounted for, and every claim allowed into the outline is supported.
- Every selected evidence ID must occur in at least one consolidated claim, verification item, or deferred-evidence entry; multiple occurrences are allowed and orphaned IDs are forbidden.
- Verification scopes have deterministic effects: `blocking` stops the affected claim, `omittable` excludes the unsupported detail while permitting any independently supported remainder, and `deferable` moves the claim or material to deferred evidence and excludes it from the current outline and manuscript.
- For revision `NN`, exact matching revisioned artifacts are authoritative. Generic and embedded artifacts remain immutable historical inputs or baselines and never substitute for a missing matching artifact.
- Cross-chapter repetition checks must record each comparison baseline by chapter, revision, exact path, baseline kind (`approved` or `working`), and SHA-256.
- Phase 1 may modify only policy, runtime, template, style-contract, and plan infrastructure under `authoring/`; it may not create or change chapter revision artifacts.

## Review Focus

- Existing generic `draft.md` and `outline.md` artifacts must remain valid historical inputs rather than becoming invalid under the new naming rules.
- The unchanged status enum must still enforce synthesis and validation before `outlined` without implying that old chapters retroactively passed a nonexistent artifact gate.
- Source consolidation must preserve every evidence ID and source role, especially qualification, conflict, chronology, and independent corroboration.
- Reconciliation must detect every selected evidence ID that disappears between selection and synthesis.
- Claim-scoped verification must distinguish blocking, omittable, and deferable issues without allowing unsupported claims to proceed.
- Audit templates must cover paragraph, chapter, and cross-chapter repetition plus compression without duplicating the full evidence policy.

---

### Task 1: Shared evidence and chapter workflow

**Files:**
- Modify: `authoring/shared/evidence-policy.md`
- Modify: `authoring/shared/chapter-workflow.md`

**Interfaces:**
- Consumes: the existing evidence classifications, state names, generic artifact contract, and this plan's Binding Functional Requirements.
- Produces: the authoritative consolidation rules and workflow gates consumed by all runtime, editorial, template, and chapter work.

- [ ] **Step 1: Record an immutable chapter-artifact checksum baseline**

Run:

```bash
find authoring/editions/1984/drafts/draft-01/chapters/01-before-hogwarts authoring/editions/1984/drafts/draft-01/chapters/02-the-four-founders authoring/editions/1984/drafts/draft-01/chapters/03-the-founding-of-hogwarts -maxdepth 1 -type f -print0 | sort -z | xargs -0 shasum -a 256 > /tmp/hogwarts-authoring-phase1-before.sha256
shasum -a 256 authoring/editions/1984/project-control/chapter-status.yaml > /tmp/hogwarts-authoring-phase1-control-before.sha256
```

Expected: exit 0, a checksum row for every existing Chapter 1–3 artifact, and a checksum for the current working contents of `chapter-status.yaml`.

- [ ] **Step 2: Extend the evidence policy**

Add focused sections establishing:

- raw evidence must be consolidated into the smallest faithful claim set before outlining;
- similarity alone is insufficient to merge evidence;
- per-source roles include establishment, independent confirmation, detail, chronology, limitation, retrospective confirmation, tradition, and conflict;
- provenance and evidence IDs survive conceptual consolidation;
- `VERIFY_SOURCE_RELATIONSHIP` and `VERIFY_SOURCE` entries carry identifiers, question, consequence, and blocking/omittable/deferable scope;
- `blocking` prevents the affected claim from entering an outline or manuscript until resolved;
- `omittable` excludes the unsupported detail and permits only an independently supported remainder to proceed;
- `deferable` moves the affected claim or material to deferred evidence and excludes it from the current outline and manuscript;
- unsupported relationships are never resolved from memory, inference, wiki material, or assumed canon;
- every selected evidence ID is reconciled to at least one claim, verification item, or deferred-evidence entry, with no orphaned selected IDs;
- unused but relevant material is recorded as deferred evidence rather than forced into prose or discarded.

- [ ] **Step 3: Extend the chapter workflow without changing existing state enums**

Keep the persisted state list compatible and define the internal gates as:

```text
evidence_selected
→ evidence reviewed and synthesized
→ synthesis validated
→ outlined
→ outline_approved
→ drafted
→ audited
→ editor_approved
```

Document that merely creating a synthesis does not validate it. `evidence_reviewed` is incomplete for a new revision until all of these conditions hold:

1. `evidence-synthesis-revision-NN.md` exists and its recorded target revision is `NN`;
2. its synthesis verdict is exactly `PASS`;
3. it contains no unresolved `blocking` verification item;
4. every consolidated claim has exactly one disposition: `advance_to_outline`, `omit_from_revision`, `defer`, or `blocked_pending_verification`;
5. every evidence ID in the matching evidence selection is present in at least one consolidated claim, verification item, or deferred-evidence entry;
6. every `advance_to_outline` claim has supporting evidence or is explicitly classified as a bounded editorial inference supported by named evidence; and
7. no `blocked_pending_verification` claim advances to the outline.

Add revisioned synthesis and outline conventions for new revisions while retaining generic historical artifacts. For revision `NN`, the exact matching revisioned synthesis and outline are authoritative; generic or embedded artifacts remain historical inputs and cannot substitute when a matching artifact is absent. Require claim-to-section mapping, section-purpose and overlap checks, claim-scoped verification handling, a dedicated compression pass, and three-level repetition review.

Define approved and working comparison baselines separately. Every synthesis and continuity/style audit that performs a cross-chapter check must record the compared chapter number, revision, exact path, baseline kind (`approved` or `working`), and SHA-256.

Document this future optional `chapter-status.yaml` extension without instantiating it during Phase 1. In the schema illustration below, uppercase values are field-type tokens, not values to copy into project control:

```yaml
working_revision:
  revision: REVISION_NUMBER
  status: evidence_reviewed
  artifacts:
    evidence_synthesis:
      path: REPOSITORY_RELATIVE_PATH
      sha256: SHA256_HEX
    outline:
      path: REPOSITORY_RELATIVE_PATH
      sha256: SHA256_HEX
    manuscript:
      path: REPOSITORY_RELATIVE_PATH
      sha256: SHA256_HEX
  comparison_baselines:
    - chapter: CHAPTER_NUMBER
      revision: REVISION_NUMBER
      kind: approved_or_working
      path: REPOSITORY_RELATIVE_PATH
      sha256: SHA256_HEX
```

`working_revision.status` uses the existing `allowed_statuses`; it is `evidence_selected` until synthesis validation passes, then `evidence_reviewed`, and advances independently of the chapter's existing top-level status. Omit nonexistent artifact keys rather than pointing to future files. Never replace or overload `approved_manuscript`.

- [ ] **Step 4: Verify policy coverage**

Run:

```bash
rg -n "evidence-synthesis-revision-NN|outline-revision-NN|VERIFY_SOURCE_RELATIONSHIP|VERIFY_SOURCE|blocking|omittable|deferable|working comparison baseline|compression|cross-chapter" authoring/shared/evidence-policy.md authoring/shared/chapter-workflow.md
```

Expected: every required concept appears in its designated authority, while existing lowercase state names remain unchanged.

- [ ] **Step 5: Perform a semantic diff review for Task 1**

Run:

```bash
git diff -- authoring/shared/evidence-policy.md authoring/shared/chapter-workflow.md
```

Read the complete diff and confirm that evidence relationships, source roles, verification semantics, and coverage reconciliation live in `evidence-policy.md`; stage gates, artifact precedence, comparison-baseline recording, and the future control shape live in `chapter-workflow.md`; and neither file contradicts the existing state enum.

### Task 2: Editorial routing and runtime contract

**Files:**
- Modify: `authoring/editorial-policy.md`
- Modify: `authoring/editions/1984/editorial-policy.md`
- Modify: `authoring/runtime/authoring-contract.md`
- Modify: `authoring/AGENTS.md`

**Interfaces:**
- Consumes: the shared evidence and workflow rules from Task 1.
- Produces: project-wide authority, legacy-path recognition, compact runtime invariants, and agent routing to the canonical rules.

- [ ] **Step 1: Add only project-level editorial rules**

In `authoring/editorial-policy.md`, require synthesis before outline or prose, preservation of historical and approved artifacts, and an explicit distinction between approved manuscripts and unapproved working comparison baselines.

- [ ] **Step 2: Recognize revisioned artifacts in the legacy-path policy**

In `authoring/editions/1984/editorial-policy.md`, retain support for generic and embedded historical outlines while requiring future revision work to pair `evidence-synthesis-revision-NN.md`, `outline-revision-NN.md`, and the corresponding manuscript revision.

- [ ] **Step 3: Add compact runtime invariants**

Update `authoring/runtime/authoring-contract.md` to prohibit outlining from raw evidence, require synthesis and claim-scoped verification, require drafting from claims and sections, require three-level repetition and compression checks, and prohibit overwriting approved artifacts.

- [ ] **Step 4: Route agents to the new mandatory authorities**

Update `authoring/AGENTS.md` with a concise instruction to read the evidence policy, chapter workflow, runtime contract, and active style lock before evidence selection, synthesis, outlining, drafting, revision, or audit work. Do not reproduce the operational rules there.

- [ ] **Step 5: Verify authority layering**

Run:

```bash
rg -n "synthes|working comparison|approved manuscript|shared/evidence-policy|shared/chapter-workflow|runtime/authoring-contract" authoring/AGENTS.md authoring/editorial-policy.md authoring/editions/1984/editorial-policy.md authoring/runtime/authoring-contract.md
```

Expected: high-level rules appear in editorial policy, operational rules remain referenced rather than copied into AGENTS, and the runtime contract stays compact.

- [ ] **Step 6: Perform a semantic diff review for Task 2**

Run:

```bash
git diff -- authoring/AGENTS.md authoring/editorial-policy.md authoring/editions/1984/editorial-policy.md authoring/runtime/authoring-contract.md
```

Read the complete diff and confirm that AGENTS only routes work, project editorial policy contains only project-wide rules, the legacy-path policy covers compatibility and precedence, and the runtime contract contains compact invariants rather than duplicated evidence mechanics.

### Task 3: Synthesis, outline, and audit templates

**Files:**
- Create: `authoring/editions/1984/templates/evidence-synthesis.md`
- Modify: `authoring/editions/1984/templates/outline.md`
- Modify: `authoring/editions/1984/templates/fact-audit.md`
- Modify: `authoring/editions/1984/templates/style-audit.md`
- Modify: `authoring/editions/1984/templates/continuity-audit.md`

**Interfaces:**
- Consumes: the synthesis structure and workflow gates established by Tasks 1–2.
- Produces: reusable artifacts for claim consolidation, revisioned outlines, and the currently required fact/style/continuity audit classes.

- [ ] **Step 1: Add the synthesis template**

Create `evidence-synthesis.md` with these headings and structured prompts: target revision, chapter purpose, consolidated claims, duplicate or overlapping evidence, source roles, evidence requiring verification, evidence-coverage reconciliation, deferred evidence, cross-chapter dependencies, comparison baselines, proposed section purposes, repetition risks, and synthesis verdict. Each claim records claim ID, claim, existing-compatible classification, supporting evidence and per-source roles, limitations, primary section, cross-chapter status, and exactly one permitted disposition. Verification entries record their deterministic scope and effect. The reconciliation section lists every selected evidence ID with at least one destination. The verdict field accepts `PASS` or `BLOCKED` and states that only `PASS` permits outlining.

- [ ] **Step 2: Extend the outline template**

Add target manuscript revision and matching synthesis revision, and for every section require title, the literal purpose formulation, primary and supporting claims, evidence IDs, deferred material, internal overlap risk, and earlier-chapter overlap risk. Require exact recorded cross-chapter baseline path, revision, kind, and SHA-256. State that every outlined claim must exist in the matching passing synthesis. Preserve the existing authorship-layer and uncertainty fields.

- [ ] **Step 3: Extend the current required audit templates**

Add evidence-synthesis, target-revision, passing-verdict, evidence-reconciliation, and outlined-claim support checks to the fact audit. Add paragraph-purpose labels, sentence/paragraph repetition, chapter-level conceptual repetition, caveat restraint, and compression checks to the style audit. Add section overlap, exact comparison-baseline identifiers, and cross-chapter repetition checks to the continuity audit.

- [ ] **Step 4: Verify template completeness**

Run:

```bash
rg -n "Target Revision|Chapter Purpose|Consolidated Claims|Duplicate or Overlapping Evidence|Source Roles|Evidence Requiring Verification|Evidence-Coverage Reconciliation|Deferred Evidence|Cross-Chapter Dependencies|Comparison Baselines|Proposed Section Purposes|Repetition Risks|Synthesis Verdict|PASS|BLOCKED" authoring/editions/1984/templates/evidence-synthesis.md
rg -n "Target manuscript revision|Matching synthesis|purpose of this section|Primary claims|Supporting claims|Overlap risk|earlier chapters|SHA-256" authoring/editions/1984/templates/outline.md
rg -n "synthesis|paragraph|conceptual repetition|cross-chapter|caveat|compression|overlap" authoring/editions/1984/templates/fact-audit.md authoring/editions/1984/templates/style-audit.md authoring/editions/1984/templates/continuity-audit.md
```

Expected: all mandated synthesis headings and all three repetition levels are represented in the appropriate templates.

- [ ] **Step 5: Perform a semantic diff review for Task 3**

Run:

```bash
sed -n '1,320p' authoring/editions/1984/templates/evidence-synthesis.md
git diff -- authoring/editions/1984/templates/outline.md authoring/editions/1984/templates/fact-audit.md authoring/editions/1984/templates/style-audit.md authoring/editions/1984/templates/continuity-audit.md
```

Read the complete new synthesis template and the complete diff of the tracked templates. Confirm that they require usable fields and deterministic values rather than merely mentioning keywords; selected-evidence reconciliation is auditable; and comparison baselines are reproducible. The explicit `sed` is required because ordinary `git diff` does not display an untracked new template.

### Task 4: Draft-wide prose contract

**Files:**
- Modify: `authoring/editions/1984/drafts/draft-01/style-lock.md`

**Interfaces:**
- Consumes: the shared evidence policy and workflow plus the existing anti-repetition rules.
- Produces: an explicit prose-stage distinction among local repetition, chapter-level conceptual repetition, cross-chapter repetition, over-qualification, and compression.

- [ ] **Step 1: Strengthen rather than duplicate the style rules**

Cross-reference the shared evidence and workflow authorities. Preserve existing paragraph uniqueness and redundancy language, then explicitly require paragraph-purpose labels during review, a separate compression pass, positive history before limitations, one meaningful qualification per point unless the evidence requires more, and omission of manufactured speculation.

- [ ] **Step 2: Verify the prose contract**

Run:

```bash
rg -n "paragraph-purpose|sentence|conceptual repetition|cross-chapter|positive history|qualification|compression|shared/evidence-policy|shared/chapter-workflow" authoring/editions/1984/drafts/draft-01/style-lock.md
```

Expected: the file explicitly distinguishes all repetition levels and points to the shared authorities without reproducing their full rules.

- [ ] **Step 3: Perform a semantic diff review for Task 4**

Run:

```bash
git diff -- authoring/editions/1984/drafts/draft-01/style-lock.md
```

Read the complete diff and confirm that the style lock contains prose-stage rules only, cross-references the shared authorities, and does not duplicate evidence consolidation or workflow mechanics.

### Task 5: Compatibility, preservation, and checkpoint report

**Files:**
- Inspect only: `authoring/editions/1984/project-control/chapter-status.yaml`
- Inspect only: all existing Chapter 1–3 artifacts

**Interfaces:**
- Consumes: every Phase 1 change.
- Produces: verified compatibility evidence and the required pre-rewrite checkpoint report.

- [ ] **Step 1: Decide and document project-control compatibility**

Confirm that the current control file has no active-WIP field. Verify that Task 1 documented the optional `working_revision` mapping exactly, with an independent status drawn from the existing enum, artifact paths and hashes added only as files come into existence, and exact comparison baselines. Do not instantiate the mapping or add pointers to nonexistent revision artifacts during Phase 1. The later chapter-rewrite phase must use this documented shape while preserving `approved_manuscript` and the top-level chapter status.

- [ ] **Step 2: Verify immutable chapter artifacts**

Run:

```bash
find authoring/editions/1984/drafts/draft-01/chapters/01-before-hogwarts authoring/editions/1984/drafts/draft-01/chapters/02-the-four-founders authoring/editions/1984/drafts/draft-01/chapters/03-the-founding-of-hogwarts -maxdepth 1 -type f -print0 | sort -z | xargs -0 shasum -a 256 > /tmp/hogwarts-authoring-phase1-after.sha256
diff -u /tmp/hogwarts-authoring-phase1-before.sha256 /tmp/hogwarts-authoring-phase1-after.sha256
```

Expected: exit 0 with no diff. Because Phase 1 may not create files in these chapter directories, the identical before/after commands prove that no pre-existing file was added, removed, renamed, or modified.

- [ ] **Step 3: Verify project-control preservation**

Run:

```bash
shasum -a 256 authoring/editions/1984/project-control/chapter-status.yaml > /tmp/hogwarts-authoring-phase1-control-after.sha256
diff -u /tmp/hogwarts-authoring-phase1-control-before.sha256 /tmp/hogwarts-authoring-phase1-control-after.sha256
rg -n "revision: 7|final-draft-candidate-revision-07.md|471ee8304bfd81c4c538b8ce74c8762448a197b1c7d33e7584b83ef1c6e855ed|revision: 6|final-draft-candidate-revision-06.md|b4b8c8cfc5a94169545ff7d159c02821f05723877ba8051fa28224ca83c30e43|status: drafted" authoring/editions/1984/project-control/chapter-status.yaml
```

Expected: the control-file checksum is unchanged from the Phase 1 baseline, both approved pointers and hashes remain present, and Chapter 3 remains drafted rather than approved.

- [ ] **Step 4: Run repository checks**

Run:

```bash
git diff --check
if rg -n '[[:blank:]]+$' authoring/editions/1984/templates/evidence-synthesis.md authoring/docs/superpowers/plans/2026-09-20-evidence-synthesis-workflow-phase-1.md; then echo 'trailing whitespace found'; exit 1; fi
git status --short
```

Expected: `git diff --check` succeeds, the trailing-whitespace search prints no matches, and status contains only pre-existing Chapter 3 work plus Phase 1 policy, runtime, plan, and template changes.

- [ ] **Step 5: Review the complete Phase 1 diff semantically**

Run:

```bash
git diff -- authoring/AGENTS.md authoring/editorial-policy.md authoring/editions/1984/editorial-policy.md authoring/shared/evidence-policy.md authoring/shared/chapter-workflow.md authoring/runtime/authoring-contract.md authoring/editions/1984/drafts/draft-01/style-lock.md authoring/editions/1984/templates
sed -n '1,320p' authoring/editions/1984/templates/evidence-synthesis.md
```

Read the complete diff and the complete untracked synthesis template against the Binding Functional Requirements. Confirm responsibility layering, deterministic validation, artifact precedence, selected-evidence coverage, comparison-baseline reproducibility, and backward compatibility. Confirm that no chapter artifact appears in the diff.

- [ ] **Step 6: Deliver the mandatory checkpoint**

Report files changed, files added, the exact synthesis gate, new filename conventions, continued generic-artifact support, the project-control schema decision, and any verification issues or repository contradictions. Stop without creating any Chapter 1 revision-08 artifact.
