# External Completion Transaction and A02 Trial Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make external-source completion restore all generated artifacts after a handled failure, replace free-text duplicate gating with exact structured candidate reviews, and prove the result with one isolated A02 extraction.

**Architecture:** The queue controller will reuse the same pure candidate-query function as `just query-dupes`, then validate an ordered list of candidate dispositions against its latest ten results. A focused artifact-snapshot helper will capture the finite completion-owned output set before any builder writes and restore it byte-for-byte on failure. The accepted A01 evidence is migrated in place, while the A02 trial remains a separate commit.

**Tech Stack:** Python 3, PyYAML, `unittest`, `fcntl`, atomic `os.replace`, Markdown, YAML, `just`, and Git.

## Global Constraints

- Preserve all 63 acquired Markdown snapshots and their body hashes.
- Preserve A01 entry IDs, source claims, quotations, placement, provenance, and duplicate targets.
- Keep `notes` optional human context; never treat prose as a machine-verifiable gate.
- Use the exact ranked, limited results returned by the shared `query-dupes` implementation.
- Exclude every entry in the completing YAML from its own candidate results.
- Keep the existing four-claim concurrency limit and serialized completion lock.
- Restore handled completion failures byte-for-byte; durable crash and power-loss recovery remain out of scope.
- Run only A02 in the follow-up trial and commit it separately from controller changes.
- Do not modify the archived book-and-companion runtime.
- Rollback baseline before this follow-up: commit `786a9d7`.

## File Map

- `scripts/query_duplicates.py`: expose one pure ranked candidate-query API shared by the CLI and completion controller.
- `scripts/external_sources/queue.py`: validate structured candidate reviews and wrap all completion-owned artifacts in the rollback boundary.
- `scripts/external_sources/artifact_snapshot.py`: capture and atomically restore the fixed generated output set and direct generated appendices.
- `tests/test_refactor_support.py`: prove the shared query API retains CLI scoring, ranking, and limit behavior.
- `tests/test_external_source_automation.py`: exercise structured audit invariants and byte-exact rollback through the real queue controller.
- `docs/instructions/runtime-contract.md`: instruct workers to write candidate dispositions rather than relying on notes.
- `docs/instructions/schema-reference.md`: document the exact external duplicate-audit schema.
- `sources/external/official-rowling/a01-chamber-of-secrets.yaml`: migrate only the three duplicate audit records.
- `docs/superpowers/plans/2026-08-15-external-source-extraction-automation.md`: append the follow-up readiness result without deleting or rewriting the original plan.
- `sources/external/official-rowling/a02-the-sorting-hat.yaml`: canonical output created only by the isolated A02 trial after completion succeeds.

---

### Task 1: Share the exact duplicate-candidate query

**Status:** done

**Files:**
- Modify: `scripts/query_duplicates.py`
- Test: `tests/test_refactor_support.py`

**Interfaces:**
- Consumes: `project-control/tag-index.yaml`, `project-control/duplicate-index.yaml`, normalized tags, optional placement text, and a result limit.
- Produces: `query_candidates(root: Path, *, tags: list[str], candidate_chapter: str | None = None, candidate_section: str | None = None, limit: int = 10) -> dict`.
- Preserves: `query(root: Path, args: argparse.Namespace) -> dict` and the existing CLI output shape.

- [x] **Step 1: Add a failing test for the shared query API**

  In `RefactorSupportTests` in `tests/test_refactor_support.py`, construct literal tag and duplicate indexes whose scores force the order `exact-two`, `exact-one`, then `weak`, with an eleventh match excluded by `limit=10`. Call:

  ```python
  payload = query_duplicates.query_candidates(
      root,
      tags=["sorting-hat", "selection"],
      limit=10,
  )
  self.assertEqual(
      [row["entry_id"] for row in payload["matches"]],
      [
          "exact-two",
          "exact-one",
          "weak-01",
          "weak-02",
          "weak-03",
          "weak-04",
          "weak-05",
          "weak-06",
          "weak-07",
          "weak-08",
      ],
  )
  ```

  The fixture must use literal expected IDs; do not calculate the expected order with `score_entry()`.

- [x] **Step 2: Run the focused test and verify RED**

  Run:

  ```bash
  .venv/bin/python -m unittest tests.test_refactor_support.RefactorSupportTests.test_query_duplicates_exposes_ranked_limited_candidate_api -v
  ```

  Expected: ERROR because `scripts.query_duplicates` has no `query_candidates` attribute.

- [x] **Step 3: Extract the existing query body into the pure API**

  Add the exact interface:

  ```python
  def query_candidates(
      root: Path,
      *,
      tags: list[str],
      candidate_chapter: str | None = None,
      candidate_section: str | None = None,
      limit: int = 10,
  ) -> dict:
      control = root / "project-control"
      tag_index = load_yaml(control / "tag-index.yaml")
      duplicate_index = load_yaml(control / "duplicate-index.yaml")
      requested_tags = {str(tag) for tag in tags}
      candidate_ids: set[str] = set()
      for tag in requested_tags:
          row = (tag_index.get("tags") or {}).get(tag) or {}
          candidate_ids.update(str(entry_id) for entry_id in row.get("entries") or [])

      matches: list[dict] = []
      for entry in duplicate_index.get("entries") or []:
          if not isinstance(entry, dict):
              continue
          entry_id = str(entry.get("entry_id") or "")
          score = score_entry(
              entry,
              requested_tags,
              candidate_chapter,
              candidate_section,
          )
          if requested_tags and entry_id not in candidate_ids and score == 0:
              continue
          if not requested_tags and score == 0 and (
              candidate_chapter or candidate_section
          ):
              continue
          if not requested_tags and not candidate_chapter and not candidate_section:
              continue
          if score == 0:
              continue
          matches.append(
              {
                  "entry_id": entry_id,
                  "score": score,
                  "title": title_from_topic(entry.get("canonical_topic")),
                  "tags": entry.get("tags") or [],
                  "source_note": entry.get("source_note"),
                  "output_yaml": entry.get("output_yaml"),
              }
          )
      matches.sort(key=lambda row: (-int(row["score"]), str(row["entry_id"])))
      return {
          "query": {
              "tags": sorted(requested_tags),
              "candidate_chapter": candidate_chapter,
              "candidate_section": candidate_section,
          },
          "matches": matches[: max(limit, 0)],
      }
  ```

  Reduce the existing adapter to:

  ```python
  def query(root: Path, args: argparse.Namespace) -> dict:
      return query_candidates(
          root,
          tags=list(args.tags or []),
          candidate_chapter=args.candidate_chapter,
          candidate_section=args.candidate_section,
          limit=args.limit,
      )
  ```

  Do not change score calculation, alphabetical tie-breaking, tag-index filtering, or CLI serialization.

- [x] **Step 4: Run focused and existing query tests and verify GREEN**

  Run:

  ```bash
  .venv/bin/python -m unittest tests.test_refactor_support.RefactorSupportTests.test_query_duplicates_exposes_ranked_limited_candidate_api tests.test_refactor_support.RefactorSupportTests.test_query_duplicates_returns_only_matching_tags -v
  ```

  Expected: all query-script tests pass with the existing CLI output unchanged.

- [x] **Step 5: Commit the shared query API**

  ```bash
  git add scripts/query_duplicates.py tests/test_refactor_support.py
  git commit -m "refactor: share duplicate candidate query"
  ```

### Task 2: Enforce structured duplicate candidate reviews

**Status:** done

**Files:**
- Modify: `scripts/external_sources/queue.py`
- Modify: `tests/test_external_source_automation.py`
- Modify: `docs/instructions/runtime-contract.md`
- Modify: `docs/instructions/schema-reference.md`
- Modify: `sources/external/official-rowling/a01-chamber-of-secrets.yaml`

**Interfaces:**
- Consumes: `query_candidates(root, tags=query_tags, limit=10)` from Task 1 and each entry's `duplicate_check.audit`.
- Produces: `QueueController._verify_duplicate_metadata(output: dict, output_path: Path) -> None` with exact ordered-candidate and disposition consistency checks.
- Schema: `audit: {query_tags: list[str], candidates: list[{id: str, disposition: str}]}`.

- [x] **Step 1: Change the test fixture to express the desired structured schema**

  In `QueueTransitionTests.write_staged_output()`, replace:

  ```python
  "audit": {"query_tags": ["hogwarts"], "candidate_ids": []},
  ```

  with:

  ```python
  "audit": {"query_tags": ["hogwarts"], "candidates": []},
  ```

  Ensure the fixture writes both `project-control/tag-index.yaml` and `project-control/duplicate-index.yaml` when a test needs candidates.

- [x] **Step 2: Add failing tests for exact ordered reviews and consistency**

  Add these fixture helpers to `QueueTransitionTests`; they write real compact indexes and call the real controller helper:

  ```python
  def write_duplicate_query_fixture(self, rows: list[dict]) -> None:
      (self.root / "project-control/duplicate-index.yaml").write_text(
          yaml.safe_dump({"entries": rows}, sort_keys=False),
          encoding="utf-8",
      )
      tags: dict[str, dict[str, list[str]]] = {}
      for row in rows:
          for tag in row.get("tags") or []:
              tags.setdefault(str(tag), {"entries": []})["entries"].append(
                  str(row["entry_id"])
              )
      (self.root / "project-control/tag-index.yaml").write_text(
          yaml.safe_dump({"tags": tags}, sort_keys=False),
          encoding="utf-8",
      )

  def verify_duplicate(self, duplicate: dict, rows: list[dict]) -> None:
      self.write_duplicate_query_fixture(rows)
      payload = {
          "source_unit": {"source_kind": "external_markdown"},
          "entries": [{"id": "ext-a01-001", "duplicate_check": duplicate}],
      }
      self.controller._verify_duplicate_metadata(
          payload,
          self.root / "work/external-staging/a01.yaml",
      )

  def make_duplicate_check(
      self,
      *,
      audit: dict,
      possible_duplicate: bool = False,
      duplicate_of: str | list[str] | None = None,
      notes: str | None = None,
  ) -> dict:
      return {
          "possible_duplicate": possible_duplicate,
          "duplicate_of": duplicate_of,
          "notes": notes,
          "audit": audit,
      }
  ```

  Add these independent tests, using literal rows and expected decisions:

  ```python
  def test_duplicate_audit_rejects_notes_without_structured_candidates(self):
      duplicate = self.make_duplicate_check(
          notes="arbitrary text",
          audit={"query_tags": ["hogwarts"], "candidate_ids": ["book-001"]},
      )
      with self.assertRaisesRegex(self.queue.QueueError, "structured candidates"):
          self.verify_duplicate(
              duplicate,
              [{"entry_id": "book-001", "tags": ["hogwarts"]}],
          )

  def test_duplicate_audit_requires_exact_ranked_candidates(self):
      duplicate = self.make_duplicate_check(
          possible_duplicate=False,
          duplicate_of=None,
          audit={
              "query_tags": ["sorting-hat", "selection"],
              "candidates": [
                  {"id": "book-002", "disposition": "distinct"},
                  {"id": "book-001", "disposition": "corroborating"},
              ],
          },
      )
      with self.assertRaisesRegex(self.queue.QueueError, "ranked candidate list"):
          self.verify_duplicate(
              duplicate,
              [
                  {"entry_id": "book-001", "tags": ["sorting-hat", "selection"]},
                  {"entry_id": "book-002", "tags": ["sorting-hat"]},
              ],
          )

  def test_duplicate_audit_rejects_unknown_disposition(self):
      duplicate = self.make_duplicate_check(
          possible_duplicate=False,
          duplicate_of=None,
          audit={
              "query_tags": ["hogwarts"],
              "candidates": [{"id": "book-001", "disposition": "maybe"}],
          },
      )
      with self.assertRaisesRegex(self.queue.QueueError, "disposition"):
          self.verify_duplicate(
              duplicate,
              [{"entry_id": "book-001", "tags": ["hogwarts"]}],
          )
  ```

  Add these exact success and consistency cases:

  ```python
  def test_duplicate_audit_accepts_exact_ranked_nonduplicates(self):
      duplicate = self.make_duplicate_check(
          audit={
              "query_tags": ["sorting-hat", "selection"],
              "candidates": [
                  {"id": "book-001", "disposition": "corroborating"},
                  {"id": "book-002", "disposition": "distinct"},
              ],
          },
      )
      self.verify_duplicate(
          duplicate,
          [
              {"entry_id": "book-001", "tags": ["sorting-hat", "selection"]},
              {"entry_id": "book-002", "tags": ["sorting-hat"]},
          ],
      )

  def test_duplicate_audit_accepts_consistent_duplicate_target(self):
      duplicate = self.make_duplicate_check(
          possible_duplicate=True,
          duplicate_of="book-001",
          audit={
              "query_tags": ["sorting-hat"],
              "candidates": [{"id": "book-001", "disposition": "duplicate"}],
          },
      )
      self.verify_duplicate(
          duplicate,
          [{"entry_id": "book-001", "tags": ["sorting-hat"]}],
      )

  def test_duplicate_audit_accepts_empty_latest_result(self):
      duplicate = self.make_duplicate_check(
          audit={"query_tags": ["sorting-hat"], "candidates": []},
      )
      self.verify_duplicate(duplicate, [])

  def test_duplicate_audit_rejects_missing_invented_and_repeated_ids(self):
      rows = [
          {"entry_id": "book-001", "tags": ["sorting-hat", "selection"]},
          {"entry_id": "book-002", "tags": ["sorting-hat"]},
      ]
      cases = {
          "missing": [{"id": "book-001", "disposition": "distinct"}],
          "invented": [
              {"id": "book-001", "disposition": "distinct"},
              {"id": "invented", "disposition": "distinct"},
          ],
          "repeated": [
              {"id": "book-001", "disposition": "distinct"},
              {"id": "book-001", "disposition": "corroborating"},
          ],
      }
      for label, candidates in cases.items():
          with self.subTest(label=label):
              duplicate = self.make_duplicate_check(
                  audit={
                      "query_tags": ["sorting-hat", "selection"],
                      "candidates": candidates,
                  },
              )
              with self.assertRaises(self.queue.QueueError):
                  self.verify_duplicate(duplicate, rows)

  def test_duplicate_audit_rejects_flag_and_target_disagreement(self):
      rows = [{"entry_id": "book-001", "tags": ["sorting-hat"]}]
      cases = [
          self.make_duplicate_check(
              possible_duplicate=False,
              duplicate_of=None,
              audit={
                  "query_tags": ["sorting-hat"],
                  "candidates": [{"id": "book-001", "disposition": "duplicate"}],
              },
          ),
          self.make_duplicate_check(
              possible_duplicate=True,
              duplicate_of="book-002",
              audit={
                  "query_tags": ["sorting-hat"],
                  "candidates": [{"id": "book-001", "disposition": "duplicate"}],
              },
          ),
      ]
      for duplicate in cases:
          with self.subTest(duplicate=duplicate):
              with self.assertRaises(self.queue.QueueError):
                  self.verify_duplicate(duplicate, rows)
  ```

  Test helpers may write fixture indexes, but assertions must target controller behavior rather than mock call counts.

- [x] **Step 3: Run the structured-audit tests and verify RED**

  Run:

  ```bash
  .venv/bin/python -m unittest \
    tests.test_external_source_automation.QueueTransitionTests.test_duplicate_audit_rejects_notes_without_structured_candidates \
    tests.test_external_source_automation.QueueTransitionTests.test_duplicate_audit_requires_exact_ranked_candidates \
    tests.test_external_source_automation.QueueTransitionTests.test_duplicate_audit_rejects_unknown_disposition -v
  ```

  Expected: failures because the current controller accepts `candidate_ids`, ignores disposition, and does not compare ranked query output.

- [x] **Step 4: Implement exact candidate and disposition verification**

  Import the shared module beside the validator import:

  ```python
  try:
      from scripts import query_duplicates, validate_source_yaml
  except ModuleNotFoundError:
      import query_duplicates
      import validate_source_yaml
  ```

  Change the helper to an instance method and implement these invariants:

  ```python
  ALLOWED_DUPLICATE_DISPOSITIONS = {"duplicate", "corroborating", "distinct"}

  def _verify_duplicate_metadata(self, output: dict, output_path: Path) -> None:
      entries = output.get("entries") or []
      completing_ids = {str(entry["id"]) for entry in entries}
      for index, entry in enumerate(entries, start=1):
          duplicate = entry.get("duplicate_check")
          audit = duplicate.get("audit") if isinstance(duplicate, dict) else None
          query_tags = audit.get("query_tags") if isinstance(audit, dict) else None
          reviews = audit.get("candidates") if isinstance(audit, dict) else None
          if not isinstance(reviews, list):
              raise QueueError(f"entry {entry.get('id') or index} lacks structured candidates")
          result = query_duplicates.query_candidates(
              self.root,
              tags=query_tags,
              limit=10,
          )
          expected_ids = [
              str(row["entry_id"])
              for row in result["matches"]
              if str(row["entry_id"]) not in completing_ids
          ]
          reviewed_ids = [str(review.get("id") or "") for review in reviews]
          if reviewed_ids != expected_ids:
              raise QueueError(
                  f"entry {entry.get('id') or index} audit does not match latest ranked candidate list"
              )
  ```

  Validate every review is a mapping, IDs are non-empty and unique, and dispositions belong to `ALLOWED_DUPLICATE_DISPOSITIONS`. Derive the ordered duplicate IDs and require:

  ```python
  duplicate_ids = [
      str(review["id"])
      for review in reviews
      if review["disposition"] == "duplicate"
  ]
  targets = validate_source_yaml.duplicate_targets(duplicate.get("duplicate_of"))
  if duplicate.get("possible_duplicate") is not bool(duplicate_ids):
      raise QueueError("possible_duplicate disagrees with duplicate dispositions")
  if targets != duplicate_ids:
      raise QueueError("duplicate_of disagrees with duplicate dispositions")
  ```

  Remove the non-empty `notes` requirement. In `complete()`, rebuild both `build_duplicate_index.py` and `build_tag_index.py` before invoking this helper.

- [x] **Step 5: Run all queue transition tests and verify GREEN**

  Run:

  ```bash
  .venv/bin/python -m unittest tests.test_external_source_automation.QueueTransitionTests -v
  ```

  Expected: every transition and structured-audit test passes.

- [x] **Step 6: Migrate A01 and worker documentation**

  Replace the three A01 `candidate_ids` fields with the exact ranked query results observed during execution:

  - `ext-a01-001`: `cos-ch16-003`, `cos-ch17-006`, `cos-ch02-002`, `cos-ch07-006`, `cos-ch08-006`, `cos-ch09-001`, `cos-ch09-002`, `cos-ch09-003`; retain `cos-ch17-006` as `duplicate` and mark the others `distinct`.
  - `ext-a01-002`: `cos-ch16-006`, `cos-ch16-007`, `cos-ch02-002`, `cos-ch07-006`, `cos-ch08-006`, `cos-ch09-001`, `cos-ch09-002`, `cos-ch09-005`, `cos-ch09-006`; retain `cos-ch16-007` as `duplicate` and mark the others `distinct`.
  - `ext-a01-003`: `cos-ch09-006`, `cos-ch02-002`, `cos-ch07-006`, `cos-ch08-006`, `cos-ch09-001`, `cos-ch09-002`, `cos-ch09-005`, `cos-ch10-006`, `cos-ch11-006`; retain `cos-ch09-006` as `duplicate` and mark the others `distinct`.

  Keep the existing notes as optional context. Update `runtime-contract.md` and the external example in `schema-reference.md` to name the three allowed dispositions, exact ranked result requirement, and optional status of `notes`.

- [x] **Step 7: Validate the migration and commit**

  Run:

  ```bash
  .venv/bin/python scripts/validate_source_yaml.py
  .venv/bin/python -m unittest tests.test_external_source_automation.QueueTransitionTests tests.test_refactor_support.RefactorSupportTests.test_query_duplicates_exposes_ranked_limited_candidate_api tests.test_refactor_support.RefactorSupportTests.test_query_duplicates_returns_only_matching_tags -v
  git diff --check
  ```

  Expected: source validation and focused tests pass, with no whitespace errors.

  Commit:

  ```bash
  git add scripts/external_sources/queue.py tests/test_external_source_automation.py docs/instructions/runtime-contract.md docs/instructions/schema-reference.md sources/external/official-rowling/a01-chamber-of-secrets.yaml
  git commit -m "fix: enforce structured duplicate reviews"
  ```

### Task 3: Restore all generated artifacts after completion failure

**Status:** done

**Files:**
- Create: `scripts/external_sources/artifact_snapshot.py`
- Modify: `scripts/external_sources/queue.py`
- Modify: `tests/test_external_source_automation.py`
- Modify: `docs/superpowers/plans/2026-08-15-external-source-extraction-automation.md`

**Interfaces:**
- Consumes: a repository root and the finite completion-owned generated paths.
- Produces: `CompletionArtifactSnapshot.capture(root: Path) -> CompletionArtifactSnapshot` and `.restore() -> None`.
- Queue integration: capture before the pre-promotion index rebuild; restore inside the existing unsuccessful-completion `finally` block.

- [x] **Step 1: Add a failing controller regression test for stale generated artifacts**

  Add `test_generation_failure_restores_every_generated_artifact`. Keep `source-plan.yaml`, `processing-state.yaml`, and `next-run.md` valid, seed distinctive valid contents into the other generated artifacts, and record every path without using production snapshot code:

  ```python
  tracked = [
      "project-control/duplicate-index.yaml",
      "project-control/entry-index.yaml",
      "project-control/source-index.yaml",
      "project-control/tag-index.yaml",
      "project-control/source-plan.yaml",
      "project-control/processing-state.yaml",
      "project-control/next-run.md",
      "book-seed/hogwarts-a-history-seed.md",
      "appendix/generated/book-structure-seed.md",
      "appendix/generated/explicit-hogwarts-a-history-references.md",
      "appendix/generated/open-questions.md",
      "appendix/generated/project-stats.md",
      "appendix/generated/review-flags.md",
      "appendix/generated/source-index.md",
  ]
  seeded = {
      "project-control/duplicate-index.yaml": "entries: []\n",
      "project-control/entry-index.yaml": "entries: []\n",
      "project-control/source-index.yaml": "sources: []\n",
      "project-control/tag-index.yaml": "tags: {}\n",
      "book-seed/hogwarts-a-history-seed.md": "# Original book seed\n",
      "appendix/generated/book-structure-seed.md": "# Original structure\n",
      "appendix/generated/explicit-hogwarts-a-history-references.md": "# Original references\n",
      "appendix/generated/open-questions.md": "# Original questions\n",
      "appendix/generated/project-stats.md": "# Original stats\n",
      "appendix/generated/review-flags.md": "# Original flags\n",
      "appendix/generated/source-index.md": "# Original sources\n",
  }
  for name, text in seeded.items():
      path = self.root / name
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(text, encoding="utf-8")
  before = {name: (self.root / name).read_bytes() for name in tracked}
  ```

  Use this runner to overwrite every tracked artifact, create a new appendix, and fail after promotion:

  ```python
  def failing_runner(commands, root):
      if any(command[-1] == "scripts/generate_appendices.py" for command in commands):
          for name in tracked:
              path = root / name
              path.parent.mkdir(parents=True, exist_ok=True)
              path.write_bytes(f"mutated:{name}".encode("utf-8"))
          (root / "appendix/generated/unexpected.md").write_text(
              "unexpected\n",
              encoding="utf-8",
          )
          raise RuntimeError("appendix generation failed")
  ```

  After `complete()` raises, assert:

  ```python
  self.assertEqual(
      {name: (self.root / name).read_bytes() for name in tracked},
      before,
  )
  self.assertFalse((self.root / "appendix/generated/unexpected.md").exists())
  self.assertTrue(draft.is_file())
  self.assertFalse((self.root / claimed["output_file"]).exists())
  self.assertEqual(self.controller.unit("A01")["claim_token"], claimed["claim_token"])
  self.assertEqual(self.controller.unit("A01")["status"], "in_progress")
  ```

- [x] **Step 2: Run the rollback regression test and verify RED**

  Run:

  ```bash
  .venv/bin/python -m unittest tests.test_external_source_automation.QueueTransitionTests.test_generation_failure_restores_every_generated_artifact -v
  ```

  Expected: FAIL because one or more indexes, book-seed files, appendices, or the new appendix remain changed.

- [x] **Step 3: Implement the focused artifact snapshot helper**

  Create `scripts/external_sources/artifact_snapshot.py` with:

  ```python
  from dataclasses import dataclass
  import os
  from pathlib import Path
  import tempfile

  FIXED_ARTIFACTS = (
      "project-control/duplicate-index.yaml",
      "project-control/entry-index.yaml",
      "project-control/source-index.yaml",
      "project-control/tag-index.yaml",
      "project-control/source-plan.yaml",
      "project-control/processing-state.yaml",
      "project-control/next-run.md",
      "book-seed/hogwarts-a-history-seed.md",
  )
  GENERATED_APPENDIX_DIR = "appendix/generated"

  def _atomic_write_bytes(path: Path, payload: bytes) -> None:
      path.parent.mkdir(parents=True, exist_ok=True)
      temporary_path: Path | None = None
      try:
          with tempfile.NamedTemporaryFile(
              mode="wb",
              dir=path.parent,
              prefix=f".{path.name}.",
              suffix=".tmp",
              delete=False,
          ) as handle:
              temporary_path = Path(handle.name)
              handle.write(payload)
              handle.flush()
              os.fsync(handle.fileno())
          os.replace(temporary_path, path)
      finally:
          if temporary_path is not None and temporary_path.exists():
              temporary_path.unlink()

  @dataclass(frozen=True)
  class CompletionArtifactSnapshot:
      root: Path
      files: dict[str, bytes | None]
      original_appendix_files: frozenset[str]

      @classmethod
      def capture(cls, root: Path) -> "CompletionArtifactSnapshot":
          resolved = root.resolve()
          appendix_dir = resolved / GENERATED_APPENDIX_DIR
          appendix_files = {
              path.relative_to(resolved).as_posix()
              for path in appendix_dir.iterdir()
              if path.is_file() and not path.is_symlink()
          } if appendix_dir.is_dir() else set()
          names = set(FIXED_ARTIFACTS) | appendix_files
          files = {
              name: (resolved / name).read_bytes() if (resolved / name).is_file() else None
              for name in names
          }
          return cls(resolved, files, frozenset(appendix_files))

      def restore(self) -> None:
          for name, payload in self.files.items():
              path = self.root / name
              if payload is None:
                  path.unlink(missing_ok=True)
              else:
                  _atomic_write_bytes(path, payload)

          appendix_dir = self.root / GENERATED_APPENDIX_DIR
          if appendix_dir.is_dir():
              for path in appendix_dir.iterdir():
                  name = path.relative_to(self.root).as_posix()
                  if (
                      path.is_file()
                      and not path.is_symlink()
                      and name not in self.original_appendix_files
                  ):
                      path.unlink()
  ```

  Do not recurse outside `appendix/generated`, follow directory symlinks, or delete untracked files elsewhere.

- [x] **Step 4: Integrate the snapshot into completion**

  Import `CompletionArtifactSnapshot` with the same package/direct-script fallback pattern as other imports. In `complete()`:

  ```python
  artifact_snapshot = CompletionArtifactSnapshot.capture(self.root)
  try:
      # Existing validation, index, promotion, state, and generation workflow.
      completed_successfully = True
      return deepcopy(unit)
  finally:
      if not completed_successfully:
          if promoted:
              os.replace(output_path, staging_path)
          artifact_snapshot.restore()
  ```

  Remove the separate `original_plan`, `original_state`, and `original_next_run` byte variables because they are now inside the complete artifact snapshot. Capture must occur before the first `build_duplicate_index.py`/`build_tag_index.py` call.

- [x] **Step 5: Run rollback and success-path tests and verify GREEN**

  Run:

  ```bash
  .venv/bin/python -m unittest \
    tests.test_external_source_automation.QueueTransitionTests.test_generation_failure_restores_every_generated_artifact \
    tests.test_external_source_automation.QueueTransitionTests.test_successful_completion_marks_only_claimed_unit_done \
    tests.test_external_source_automation.QueueTransitionTests.test_completion_generates_reports_from_prospective_done_state -v
  ```

  Expected: all three pass; the failure test proves exact restoration, and success tests prove final artifacts are retained.

- [x] **Step 6: Record the fixed readiness gates in the original plan**

  Preserve every original task and checkbox in `2026-08-15-external-source-extraction-automation.md`. Append this dated section:

  ```markdown
  ## Production-readiness follow-up — 2026-08-15

  - [x] Structured candidate dispositions replace free-text duplicate gating.
  - [x] Completion reuses the exact ranked `query-dupes` implementation.
  - [x] Handled post-promotion failures restore all completion-owned artifacts byte-for-byte.
  - [ ] A02 isolated trial accepted.
  ```

- [x] **Step 7: Run the full suite and commit the transaction**

  Run:

  ```bash
  just indexes
  just validate
  just generate
  just test
  git diff --check
  ```

  Expected: all commands exit zero. The unittest suite still prints the established negative-fixture validator message but ends with `OK`.

  Commit:

  ```bash
  git add scripts/external_sources/artifact_snapshot.py scripts/external_sources/queue.py tests/test_external_source_automation.py docs/superpowers/plans/2026-08-15-external-source-extraction-automation.md project-control appendix/generated book-seed/hogwarts-a-history-seed.md
  git commit -m "fix: rollback external completion artifacts"
  ```

### Task 4: Record readiness and run isolated A02

**Status:** in progress

**Files:**
- Modify: `docs/superpowers/plans/2026-08-15-external-source-extraction-automation.md`
- Modify: `project-control/source-plan.yaml`
- Modify: `project-control/processing-state.yaml`
- Modify: `project-control/next-run.md`
- Modify: generated indexes, appendices, and book seed through queue completion
- Create: `sources/external/official-rowling/a02-the-sorting-hat.yaml`

**Interfaces:**
- Consumes: the hardened queue controller, active runtime contract, compact query commands, and A02 snapshot.
- Produces: one reviewed A02 canonical evidence YAML, queue status with A01/A02 done and A03 next, and a separate trial commit.

- [x] **Step 1: Run the pre-trial readiness gate**

  Run:

  ```bash
  just indexes
  just validate
  just generate
  just test
  just external-status
  git diff --check
  git status --short
  ```

  Expected: tests pass, source validation passes, the worktree is clean, queue counts are `pending: 62`, `in_progress: 0`, `done: 1`, `blocked: 0`, and A02 is next.

- [ ] **Step 2: Dispatch only the A02 test agent**

  The coordinating agent claims A02 and supplies the returned token and paths. The test-agent prompt must say:

  ```text
  Process only claimed unit A02 under docs/instructions/runtime-contract.md.
  Read the entire assigned A02 snapshot and only the compact query-selected evidence allowed by the runtime.
  Write only the assigned work/external-staging/a02.yaml file.
  For every entry, record audit.query_tags and the exact ordered audit.candidates returned by just query-dupes, assigning duplicate, corroborating, or distinct to each.
  Do not commit, edit queue state, edit canonical sources, or read unrelated snapshots.
  Report every file read, every query run, extracted entry count, and unresolved limitation.
  ```

- [ ] **Step 3: Complete A02 through the controller**

  Copy the runtime-generated `claim_token` returned by the A02 claim into the second argument of `just complete-external`, and record the fully concrete command in the execution ledger before running it. Do not store the token in the plan.

  Expected: completion validates the carrier and anchors, verifies the exact structured duplicate audit, promotes only A02, regenerates outputs, and reports A02 as `done`.

- [ ] **Step 4: Review A02 evidence and queue effects**

  Check each A02 entry against the snapshot text and assert:

  - both anchor phrases occur in A02;
  - every short quote is under 25 words;
  - provenance matches manifest A02 exactly;
  - all tags, placement fields, and temporal limitations are defensible;
  - candidate reviews match fresh `just query-dupes` output in exact order;
  - the agent read no unrelated snapshot or broad source corpus;
  - queue counts are `pending: 61`, `in_progress: 0`, `done: 2`, `blocked: 0`, with A03 next.

  If evidence review fails, revert only the A02 trial through a normal Git revert and leave the controller fixes intact.

- [ ] **Step 5: Run final verification and commit A02 separately**

  Run:

  ```bash
  just indexes
  just validate
  just generate
  just test
  just external-status
  git diff --check
  ```

  Expected: all commands exit zero and A02 remains the only new canonical source in this trial.

  Mark `A02 isolated trial accepted` checked in the appended follow-up section, then commit:

  ```bash
  git add sources/external/official-rowling/a02-the-sorting-hat.yaml project-control appendix/generated book-seed/hogwarts-a-history-seed.md docs/superpowers/plans/2026-08-15-external-source-extraction-automation.md
  git commit -m "extract: process external source A02"
  ```

  Record the controller-fix commit and A02-trial commit as separate rollback points in the handoff.
