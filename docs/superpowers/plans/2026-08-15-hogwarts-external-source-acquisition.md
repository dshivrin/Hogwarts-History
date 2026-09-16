# Hogwarts External Source Acquisition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a traceable local corpus of accessible Rowling-authored and Rowling-spoken Hogwarts sources without changing the existing evidence seed, generated appendices, outline, or structured source YAML.

**Architecture:** Treat `pdfs/hogwarts-external-source-acquisition.md` as the source catalog and contract. Fetch each public carrier into a temporary cache, transform only the article/transcript body into a provenance-headed Markdown snapshot, and emit one YAML manifest plus acquisition and unresolved-source reports. Keep the acquisition tooling isolated from the existing extraction pipeline.

**Tech Stack:** Python 3 standard library, `curl`, pytest, Markdown, YAML output.

## Global Constraints

- Do not rewrite `book-seed/hogwarts-a-history-seed.md`.
- Do not modify the controlled outline, generated appendices, taxonomy, or existing source YAML.
- Use only public pages; do not bypass paywalls, authentication, or anti-bot controls.
- Preserve title, author/speaker, source site, dates, original and retrieval URLs, carrier type, local path, content hash, completeness, authority, and relevance tags.
- Prefer a primary carrier; preserve mirrors without counting them as independent corroboration.
- Do not acquire pirated copies of published books.

---

### Task 1: Catalog and extraction contracts

**Files:**
- Create: `tests/external_sources/test_build_external_corpus.py`
- Create: `scripts/external_sources/build_external_corpus.py`

**Interfaces:**
- Consumes: the acquisition-plan Markdown and cached HTML files named by source ID.
- Produces: `parse_plan(path) -> list[dict]`, `extract_official(html) -> dict`, and `extract_transcript(html) -> dict`.

- [ ] **Step 1: Write failing parser tests**

  Add literal fixtures proving that A/B source headings and their first carrier URL become unique catalog records, including a supplied URL override for B02.

- [ ] **Step 2: Run the focused tests and verify RED**

  Run: `python3 -m pytest tests/external_sources/test_build_external_corpus.py -q`
  Expected: import failure because `scripts.external_sources.build_external_corpus` does not exist.

- [ ] **Step 3: Implement the minimal catalog parser**

  Parse only `### Axx` and `### Bxx` headings, stop URL association at the next heading, normalize titles, reject duplicate IDs, and apply explicit carrier overrides.

- [ ] **Step 4: Add failing extraction tests**

  Use compact HarryPotter.com `__NEXT_DATA__` and Accio `<div id="content">` fixtures. Assert the exact title/date/body and prove navigation text is excluded.

- [ ] **Step 5: Implement extraction and rerun GREEN**

  Extract official article fields from the embedded JSON; use `html.parser.HTMLParser` for transcript content; normalize whitespace without paraphrasing source text.

### Task 2: Fetch the accessible carriers

**Files:**
- Create: temporary HTML files under `/tmp/hogwarts-external-source-cache/`

**Interfaces:**
- Consumes: catalog URLs printed by the acquisition tool.
- Produces: one cached HTML carrier for every successful public request and a status JSON for every attempt.

- [ ] **Step 1: Emit and inspect the fetch queue**

  Run: `python3 scripts/external_sources/build_external_corpus.py catalog --plan pdfs/hogwarts-external-source-acquisition.md`
  Expected: A01-A37 and B01-B26, with no duplicate logical IDs.

- [ ] **Step 2: Fetch with direct public requests**

  Use `curl -L --fail --silent --show-error` for each URL. Record HTTP failures; do not retry restricted sources through alternate access methods.

- [ ] **Step 3: Validate cached carriers**

  Confirm each successful file is non-empty and contains the expected official JSON article body or Accio content container.

### Task 3: Build snapshots and the manifest

**Files:**
- Create: `resources/external/official-rowling/harrypotter-com/*.md`
- Create: `resources/external/interviews/accio-quote/*.md`
- Create: `resources/manifests/external-sources.yaml`

**Interfaces:**
- Consumes: the catalog and validated HTML cache.
- Produces: UTF-8 Markdown snapshots and an authority-ranked manifest with content hashes.

- [ ] **Step 1: Add failing output tests**

  Assert a generated snapshot has complete YAML metadata, faithful body text, a 64-character SHA-256 body hash, and no navigation text. Assert the manifest references an existing snapshot and preserves logical IDs.

- [ ] **Step 2: Implement snapshot and manifest generation**

  Generate files only below `resources/external/` and `resources/manifests/`; classify official Rowling pages as authority A and Accio preservation transcripts as authority D with their named original outlet retained.

- [ ] **Step 3: Run focused tests and build the corpus**

  Run the focused pytest file, then run the tool against the real cache. Expected: all cached carriers generate non-empty Markdown snapshots and manifest records.

### Task 4: Report unresolved and preservation-only sources

**Files:**
- Create: `resources/manifests/external-source-acquisition-report.md`
- Create: `resources/external/unresolved/discovery-backlog.md`
- Create: `resources/external/indexes/*.md`

**Interfaces:**
- Consumes: fetch status, manifest records, known old-site/archive indexes, and the supplementary source queue.
- Produces: counts by authority/class, acquired/skipped lists, unresolved provenance, archive-recovery work, and the recommended next extraction batch.

- [ ] **Step 1: Save discovery-index metadata snapshots**

  Register the Accio Hogwarts index, HP Lexicon source index, old-JKR-site indexes, Famous Wizard Cards index, and Daily Prophet newsletter index as discovery-only resources.

- [ ] **Step 2: Write the acquisition report**

  Report exact acquired and unavailable counts, multi-part interview relationships, duplicate carriers, authority/source-class totals, and sources deliberately not copied because they require a legitimate local edition.

- [ ] **Step 3: Write the recovery backlog**

  Record old `jkrowling.com` material, lawful broadcaster audio/transcripts, published ebooks/screenplays, cards/newsletters, and any HTTP failures without inventing content.

### Task 5: Integrity verification

**Files:**
- Verify: all files created by Tasks 1-4
- Verify unchanged: `book-seed/`, `appendix/generated/`, `project-control/structured-sources/`, and the pre-existing prefix of `pdfs/hogwarts-external-source-acquisition.md`

**Interfaces:**
- Consumes: completed corpus and a pre-edit checksum/baseline.
- Produces: reproducible verification evidence for the final handoff.

- [ ] **Step 1: Run focused and existing tests**

  Run: `python3 -m pytest tests/external_sources/test_build_external_corpus.py -q`
  Then run the repository's relevant existing test command if the focused suite passes.

- [ ] **Step 2: Validate every manifest record**

  Verify each local path exists, text is UTF-8 and non-empty, required metadata is populated, the body hash matches, IDs are unique, and the snapshot contains no obvious page chrome.

- [ ] **Step 3: Prove append-only/no-result mutation**

  Compare the saved pre-edit acquisition-plan prefix byte-for-byte and inspect `git status --short` limited to the intended new resource, script, test, plan, and report paths. Confirm no protected result path changed during this run.
