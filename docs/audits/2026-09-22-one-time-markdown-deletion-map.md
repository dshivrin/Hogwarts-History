# One-Time Markdown Deletion Map

Audit date: 2026-09-22
Mode: read-only classification; no Markdown candidate was deleted

## Result

The repository contains 244 Markdown files. Of those, 39 are completed,
superseded, or point-in-time working documents that can be removed without
losing an active runtime, authoring control, evidence source, or reproducibility
record.

- 20 files are safe to delete together now.
- 14 more are safe after updating stale inventory references in the repository
  handoff.
- 5 archived instructions are safe after updating their two active redirect
  references and the repository handoff.
- Approximate tracked space represented by all 39 files: 620 KB.

"Safe" here means operationally unnecessary and recoverable from Git history.
It does not mean that every file has no historical interest.

## How the map was produced

The audit:

1. enumerated every tracked Markdown path;
2. searched the repository for exact-path references;
3. checked the root, authoring, and audiobook runtime instructions;
4. distinguished active contracts, source snapshots, generated outputs,
   chapter artifacts, and provenance records from one-time plans and reports;
5. treated references inside the preserved 2026-09-16 audiobook filesystem
   snapshot as historical observations, not live dependencies; and
6. excluded any file named in a current control or hash record.

## Tier 1 — safe to delete as one group

These 20 files have no dependency outside this deletion group. Some plans and
specifications refer to one another, so they should be removed together.

### Consumed audit and stale implementation report

- `docs/audits/2026-09-21-runtime-audit-and-future-tooling-plan.md`
- `authoring/audio/current-audiobook-tts-implementation-report.md`

The runtime audit has now been implemented. The audiobook report describes a
generic-render defect and task-local workaround that the current audiobook
README and maintained renderer have superseded.

### Completed root implementation plans and designs

- `docs/superpowers/plans/2026-06-21-efficiency-and-book-seed.md`
- `docs/superpowers/plans/2026-06-22-finish-result-output-implementation.md`
- `docs/superpowers/plans/2026-06-27-token-usage-scale-up.md`
- `docs/superpowers/plans/2026-07-22-fanfic-hogwarts-history-dataset.md`
- `docs/superpowers/plans/2026-08-15-external-completion-transaction-and-a02-trial.md`
- `docs/superpowers/plans/2026-08-15-external-source-extraction-automation.md`
- `docs/superpowers/plans/2026-08-15-hogwarts-external-source-acquisition.md`
- `docs/superpowers/plans/2026-09-11-fantastic-beasts-remainder-automation.md`
- `docs/superpowers/plans/2026-09-18-open-questions-overlay-agent-instructions.md`
- `docs/superpowers/plans/2026-09-18-open-questions-overlay.md`
- `docs/superpowers/specs/2026-08-15-external-completion-transaction-and-duplicate-audit-design.md`
- `docs/superpowers/specs/2026-08-15-external-source-extraction-automation-design.md`
- `docs/superpowers/specs/2026-09-11-fantastic-beasts-remainder-automation-design.md`

These files are implementation history. Current behavior is represented by the
maintained scripts, tests, runtime contract, schemas, and data/control files.
Their remaining exact-path links are confined to this same group.

### Completed authoring and audiobook plans

- `authoring/docs/superpowers/plans/2026-09-20-evidence-synthesis-workflow-phase-1.md`
- `authoring/audio/docs/superpowers/plans/2026-09-19-canonical-audiobook-generation.md`
- `authoring/audio/docs/superpowers/specs/2026-09-19-canonical-audiobook-generation-design.md`

The authoring plan's rules now live in active policy, workflow, contract, and
template files. The audiobook plan and design are superseded by the maintained
README, agent instructions, settings, implementation, tests, and records.

### Superseded open-question working records

- `resources/external/open-questions-scapping/hogwarts-open-questions-codex-guide.pre-restructure-2026-09-18.md`
- `resources/external/open-questions-scapping/open-questions-integration-audit.md`

The current guide and structured overlay preserve the live result. The only
remaining references to these two files come from the completed overlay plan
listed above.

## Tier 2 — safe after updating the repository handoff

These 14 files are no longer operational, but
`hogwarts-history-repository-handoff.md` still inventories them. Remove or
rewrite those handoff rows in the same deletion commit so the handoff does not
contain dead links.

### Superseded implementation prompts and plans

- `docs/instructions/cli-tooling-runtime-update-plan.md`
- `docs/instructions/fanfic-hogwarts-history-dataset-plan.md`
- `docs/instructions/finish-cli-tooling-implementation-plan.md`
- `docs/instructions/finish-token-efficiency-refactor.md`
- `docs/instructions/implement-fanfic-dataset-subagent-driven-prompt.md`
- `docs/instructions/token-efficiency-refactor-instructions.md`

Do not include `docs/instructions/result-output-redesign-plan.md` in this
deletion: its own handoff assessment says the proposal is only partly realized.

### Obsolete generated run snapshots

- `project-control/archive/next-run-2.md`
- `project-control/archive/next-run-3.md`
- `project-control/archive/next-run-4.md`
- `project-control/archive/next-run-5.md`
- `project-control/archive/next-run-6.md`
- `project-control/archive/next-run-7.md`
- `project-control/archive/next-run-8.md`
- `project-control/archive/next-run-9.md`

These are obsolete Book 2/3 generated displays. Current state lives in YAML and
`project-control/next-run.md`. Their appearance in the preserved audiobook
filesystem inventory is historical and should not be edited.

## Tier 3 — safe after repairing active redirects

These five archived instructions are not loaded by current workflows, but two
active documents still link to them. Before deletion:

1. remove the legacy-archive sentence from
   `docs/instructions/hogwarts-history-seed-builder.md`;
2. remove the archive pointer in the opening paragraph of
   `docs/instructions/runtime-contract.md`; and
3. remove their inventory rows from `hogwarts-history-repository-handoff.md`.

Then delete:

- `docs/instructions/archive/hogwarts-history-seed-builder-first.md`
- `docs/instructions/archive/hogwarts-history-seed-builder-updated.md`
- `docs/instructions/archive/hogwarts-history-seed-builder.md`
- `docs/instructions/archive/runtime-contract-book-and-companion-extraction-2026-08-15.md`
- `docs/instructions/archive/runtime-contract-external-source-extraction-completed-2026-09-11.md`

## Reviewed but not safe to delete

The following one-time-looking files were deliberately excluded:

- `hogwarts-history-repository-handoff.md`: still contains unique repository
  topology, known disagreements, and unresolved assessments. Review and migrate
  that information before considering deletion.
- `docs/instructions/result-output-redesign-plan.md`: partially implemented;
  it remains the only consolidated description of unfinished output redesign.
- `pdfs/hogwarts-external-source-acquisition.md`: still used as the corpus
  catalog/contract by the external-resource README and acquisition command.
- `authoring/audio/docs/superpowers/plans/2026-09-14-local-audiobook-narration.md`,
  its design specification, and its Task 6 report: their hashes are recorded in
  `resources/manifests/cursed-child-research-record.yaml`.
- `resources/manifests/*.md`: acquisition/research provenance, not disposable
  implementation notes.
- chapter briefs, outlines, audits, synthesis files, drafts, and narration
  manuscripts: durable authoring artifacts, with several paths and hashes in
  chapter control data.
- `appendix/generated/*.md`, `book-seed/*.md`, and
  `project-control/next-run.md`: generated current outputs, not one-time notes.
- `resources/external/**/*.md`: source snapshots and live research guidance,
  not repository-maintenance documents.
- active READMEs, AGENTS files, policies, templates, contracts, style guides,
  and schema/background references.

## Safe execution order

If deletion is authorized later, use three commits or three clearly separated
stages:

1. delete Tier 1 and run all validation;
2. update the handoff and delete Tier 2; and
3. repair the two active redirects, update the handoff, and delete Tier 3.

After each stage, run `just doctor`, `just validate`, `just test`, and an
exact-path search for every deleted file. Do not rewrite historical audiobook
filesystem inventories merely because they list files that existed at capture
time.
