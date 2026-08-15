# Prompt: Implement the Fanfic Dataset Plan with Subagent-Driven Development

Copy the prompt below into a new Codex task rooted at:

```text
/Users/dima/Documents/Hogwarts History
```

---

You are the primary controller responsible for implementing this plan:

```text
/Users/dima/Documents/Hogwarts History/docs/superpowers/plans/2026-07-22-fanfic-hogwarts-history-dataset.md
```

Implement the complete plan using **Subagent-Driven Development**. Continue through all eleven tasks without asking whether to proceed between tasks.

## Required Skills

Before taking implementation actions:

1. Read and follow `superpowers:using-superpowers`.
2. Read and follow `superpowers:subagent-driven-development`.
3. Use `superpowers:test-driven-development` for every implementation task.
4. Use `superpowers:systematic-debugging` whenever a test fails unexpectedly.
5. Use `superpowers:verification-before-completion` before claiming success.
6. Use `superpowers:requesting-code-review` for the final whole-branch review.
7. Use `superpowers:finishing-a-development-branch` only after implementation, validation, and final review are clean.

The saved implementation plan is the source of truth for scope, exact values, interfaces, commands, and acceptance criteria.

## Preflight

1. Read the implementation plan completely.
2. Read the original acquisition brief only when a requirement needs clarification:

   ```text
   /Users/dima/Documents/Hogwarts History/docs/instructions/fanfic-hogwarts-history-dataset-plan.md
   ```

3. Inspect:

   ```bash
   git status --short
   git branch --show-current
   git log -5 --oneline
   ```

4. Preserve all pre-existing worktree changes. In particular, do not discard, overwrite, stage, or commit unrelated modifications or previously untracked plans.
5. Scan the implementation plan once for internal conflicts. If genuine conflicts exist, present them to the user as one batched question before Task 1. If the scan is clean, proceed immediately.
6. Check for a durable progress ledger:

   ```text
   /Users/dima/Documents/Hogwarts History/.superpowers/sdd/progress.md
   ```

   Trust completed entries and their commit ranges. Resume at the first unfinished task; never repeat a reviewed task.
7. Record the branch starting commit as `MERGE_BASE` for the final review.

Work in the current checkout. Do not create another worktree unless the user explicitly requests one; the requirements plan and other workspace state may be untracked.

## Git Safety

- Stage only files belonging to the current task.
- Never use `git reset --hard`, destructive checkout, broad cleanup, or commands that could erase user work.
- Do not stage generated fanfic prose, raw/clean HTML, Markdown chapters, PDFs, screenshots, policy snapshots, local manifests, or other paths the plan requires to remain ignored.
- Before every commit, run the task’s verification, inspect `git status --short`, and inspect the staged diff.
- Use the commit messages specified by the plan when present.
- Record the exact base commit before dispatching each implementer. Never assume `HEAD~1`, because an implementer may create multiple commits.

## Runtime Prerequisite

The existing `.venv` uses Python 3.9.6 and must remain untouched. The fanfic pipeline requires an isolated `.fanfic-venv` running Python 3.12 or newer.

Check for an already available compatible interpreter before Task 1. Do not silently weaken the version requirement. If Python 3.12+ is unavailable and provisioning it requires external installation or new authority, stop once, explain the exact blocker, and request the required approval. Resume from Task 1 after the prerequisite is available.

## Durable Task Loop

For each plan task, sequentially:

1. Generate a task brief with the `subagent-driven-development` skill’s `scripts/task-brief` helper. The brief must contain the plan task’s complete text.
2. Derive the report path from the brief path by replacing `brief` with `report`.
3. Record `BASE_SHA=$(git rev-parse HEAD)`.
4. Dispatch a **fresh implementer subagent** with:

   - `fork_turns: "none"` so it receives only the curated task context;
   - an explicitly selected model;
   - the task brief path as its requirements;
   - the repository path;
   - only the interfaces and decisions from earlier tasks that this task consumes;
   - the report file path and required status contract.

5. Require the implementer to:

   - ask questions before guessing;
   - follow RED → GREEN → REFACTOR;
   - run focused tests while iterating and the relevant complete suite before committing;
   - commit only task files;
   - self-review;
   - write its full report to the report file, including commands and RED/GREEN evidence;
   - return only `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`, commit SHAs, a one-line test result, concerns, and the report path.

6. Handle status exactly as required by `subagent-driven-development`:

   - `DONE`: proceed to review.
   - `DONE_WITH_CONCERNS`: resolve correctness or scope concerns before review.
   - `NEEDS_CONTEXT`: supply only the missing context and redispatch.
   - `BLOCKED`: change context, model capability, or task decomposition; escalate to the user only when the plan or authority is the blocker.

7. Generate the review package with:

   ```bash
   scripts/review-package BASE_SHA HEAD
   ```

   Use the helper from the `subagent-driven-development` skill directory and pass the unique output file to the reviewer.

8. Dispatch a **fresh task reviewer subagent** with `fork_turns: "none"` and an explicit model. Give it:

   - the same task brief;
   - the implementer report;
   - the review-package path;
   - `BASE_SHA` and current `HEAD_SHA`;
   - the plan’s Global Constraints copied verbatim.

9. Require two independent verdicts:

   - specification compliance;
   - code quality.

   The reviewer is read-only and must not mutate the checkout or rerun tests already evidenced by the implementer unless it identifies a specific unanswered doubt.

10. If the reviewer reports Critical or Important findings, dispatch one fresh fixer with the complete task finding list. The fixer must:

    - make the minimum compliant correction;
    - rerun the named covering tests;
    - append fix evidence to the existing report;
    - commit the fix.

11. Generate a new review package from the original task `BASE_SHA` to the new `HEAD`, then redispatch a fresh reviewer. Repeat until both verdicts are clean.
12. Resolve every reviewer `Cannot verify from diff` item yourself before marking the task complete.
13. Record Minor findings in the ledger for final-review triage.
14. Append:

    ```text
    Task N: complete (commits <base7>..<head7>, review clean)
    ```

    to `.superpowers/sdd/progress.md`.
15. Continue immediately to the next task.

Do not run multiple implementers concurrently. They share one working tree and the tasks have sequential interfaces.

## Model Selection

Always specify the subagent model explicitly and use `fork_turns: "none"`.

- Use `gpt-5.6-terra` with medium reasoning for narrowly mechanical tasks whose plan contains exact code and tests.
- Use `gpt-5.6-sol` with high reasoning for network boundaries, parsing, PDF assembly, validation, CLI orchestration, cross-task integration, difficult fixes, and reviews of consequential changes.
- Use `gpt-5.6-sol` with high or xhigh reasoning for the final whole-branch review.
- If a lower-capability implementer reports that it is blocked by reasoning complexity, redispatch with the stronger model and explain what changed.

## Project-Specific Non-Negotiable Rules

- Keep all network access inside `scripts/fanfic_dataset/browser.py`.
- Use synthetic fixtures only; never copy live fanfic prose into tests.
- Keep browser requests sequential, unauthenticated, policy-checked, and at the effective minimum delay defined by the plan.
- Never bypass login, CAPTCHA, Cloudflare, robots restrictions, rate limits, or access denial.
- Recheck `robots.txt` and the live chapter inventory immediately before Task 9.
- Stop acquisition and create diagnostics on any policy/access failure; do not treat blocked acquisition as successful.
- Preserve response bodies byte-for-byte for raw capture as specified by the plan.
- Keep author-note classification hash-addressed and human-reviewed; never guess and remove prose.
- Keep fan-created claims labeled non-canon and isolated from canonical `sources/`, `book-seed/`, and `project-control/` data.
- Preserve older captures and promote `latest.json` only after passing validation.
- Generated copyrighted artifacts remain local and ignored.
- Do not claim live acquisition success from mocked or offline tests.

## Manual and Visual Review

Task 9 requires genuine manual inspection. The primary controller—not a task implementer—must inspect the source page and rendered artifacts for every required first, final, longest, transition, author-note, and missing-chapter case.

Use the available PDF/image rendering tools for visual verification. Record the actual reviewer identity as `Codex`, the real UTC timestamp, and concrete notes. Never fabricate a review checkbox or validation result.

If a public page changes, a count differs, or access becomes blocked, preserve diagnostics and report the open issue. Do not force stale expectations or bypass safeguards.

## Final Whole-Branch Gate

After all eleven task reviews are clean:

1. Run every verification command required by Task 11 and `superpowers:verification-before-completion`.
2. Confirm ignored copyright-bearing artifacts are not staged.
3. Generate a final review package from `MERGE_BASE` to `HEAD`.
4. Dispatch one fresh, high-capability final reviewer using `superpowers:requesting-code-review`. Give it:

   - the complete implementation plan path;
   - the final review-package path;
   - the full test/validation report paths;
   - all unresolved Minor findings from the ledger;
   - the exact Global Constraints.

5. If the final reviewer reports findings, dispatch **one** fixer with the complete list, run covering tests plus the full required suite, commit, regenerate the package, and re-review.
6. Do not finish until the final reviewer says the branch is ready and all required validation is genuinely passing.
7. Use `superpowers:finishing-a-development-branch` to present the user with integration choices. Do not merge, push, or open a pull request unless the user authorizes that outcome.

## Final Response

Lead with the verified outcome. Include:

- implementation status for all eleven tasks;
- offline test command and result;
- live acquisition/validation status for each approved source;
- complete-PDF and report paths when generated;
- comparison-index status;
- commit range;
- any policy, source-change, manual-review, or environment issues;
- confirmation that copyright-bearing artifacts remain ignored and unstaged;
- final reviewer verdict.

Do not claim completion unless the commands were run and their outputs were reviewed.
