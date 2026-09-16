# Fanfic Hogwarts History Dataset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible, policy-aware local acquisition pipeline that captures the four approved fan works as versioned raw HTML, semantic HTML, normalized Markdown, chapter PDFs, one complete PDF per work, manifests, validation evidence, and a topic-comparison index.

**Architecture:** A Python 3.12 command package owns a typed source registry, policy preflight, FanFiction.net discovery/capture adapter, deterministic transformation pipeline, PDF assembler, manifest builder, and layered validator. Network access is isolated behind one Playwright client; all parsers and transforms are tested against synthetic local fixtures, while live acquisition remains an explicit, sequential operator action. Copyright-bearing artifacts are stored under ignored, timestamped capture directories; small registries, schemas, review metadata, and reports remain reviewable.

**Tech Stack:** Python 3.12+, Playwright/Chromium, BeautifulSoup4, markdownify, Pydantic 2, PyMuPDF, jsonschema, pytest, standard-library `urllib.robotparser`, SHA-256.

## Global Constraints

- The dataset is for private research and comparison; generated files must not be redistributed or presented as authorized editions.
- Every extracted claim remains labeled `fan_created: true` and `canon_status: "non-canon fanfiction"`.
- Never bypass login, payment, CAPTCHA, Cloudflare, robots policy, rate limiting, or any other technical safeguard.
- Use only the author's public posting page or a native download exposed by that page; do not use third-party downloader sites.
- Run chapter requests sequentially in one unauthenticated browser context.
- Use an effective delay of `max(5.0, robots_crawl_delay, --request-delay-seconds)` seconds with jitter from `0.0` through `1.0` seconds. The acquisition brief said at least 3 seconds, but FanFiction.net's public robots file advertised `crawl-delay: 5` during review on 2026-07-22.
- Stop the current work immediately on HTTP 429, access denial, CAPTCHA, Cloudflare challenge, policy disallowance, or a missing story container; write diagnostics and do not retry access-denial responses.
- Do not rewrite spelling, punctuation, capitalization, grammar, or factual claims.
- Do not add invented missing chapters, merge authors, or use Rowling/publisher branding.
- Preserve older captures; never overwrite a prior version when source content changes.
- Do not commit raw HTML, clean HTML, normalized fanfic text, or PDFs.
- Python 3.12+ is required for this package. The repository's current `.venv` is Python 3.9.6, so execution must create a separate `.fanfic-venv`; do not replace the existing environment.
- Live source facts observed during review are not test fixtures. Synthetic fixtures must contain invented, non-fanfic prose.

---

## Plan Review and Resolved Decisions

The acquisition brief is implementable, but these ambiguities must be resolved before code is written:

1. **Storage versioning:** The proposed `works/<id>/raw/` layout conflicts with the requirement to preserve older captures. Use `works/<id>/captures/<capture-id>/...` and a small `latest.json` pointer.
2. **PDF naming:** The example manifest used `HAH-FAN-001-complete.pdf`, while the PDF section required `<source-id>__<title>__<author>.pdf`. The latter is canonical everywhere.
3. **Policy cadence:** The proposed 3-second delay is below the five-second crawl delay visible on 2026-07-22. Enforce five seconds as the minimum and re-evaluate robots rules before each live run.
4. **Runtime mismatch:** The current local environment is Python 3.9.6 and has only `pypdf` from the proposed stack. Use an isolated Python 3.12 environment and a separate locked requirements file.
5. **Author-note classification:** HTML does not reliably identify author notes. Preserve all story-container blocks, then classify notes through hash-addressed human annotations. Never guess and remove prose.
6. **Raw capture meaning:** `raw/chapter-NNN.html` is the main document response body returned by Playwright, saved byte-for-byte after status/policy/failure-signature checks. It is not `page.content()` or another browser-serialized DOM snapshot.
7. **Dry-run boundary:** Dry-run may load Chapter 1, inspect native-download links, parse public metadata, and enumerate chapter URLs. It must not visit other chapter bodies or create capture directories.
8. **Validation truth:** Automated checks cannot prove visual inspection. Manual review gets a machine-readable checklist; a work is `complete` only after required checks are signed with timestamp and reviewer name.
9. **Core inventory stability:** The four approved sources remain pinned as core. A newer 2024 work with the same title was discovered during review and must be recorded as `candidate-needs-editorial-review`, not silently acquired.
10. **Copyright boundary:** Generated content artifacts remain local and ignored. The source registry, hashes, validation results, and topic labels may be tracked because they contain metadata rather than reproduced prose.

## Repository and Artifact Map

### Tracked implementation files

```text
.gitignore
Justfile
requirements-fanfic.txt
pytest.ini
scripts/fanfic_dataset/
  __init__.py              package version
  models.py                Pydantic contracts shared by every module
  emit_schemas.py          deterministic JSON Schema generation
  paths.py                 capture IDs and safe artifact paths
  registry.py              source/exclusion registry loader
  policy.py                robots/TOS snapshot and effective-delay gate
  discover.py              platform-neutral discovery protocol
  fanfiction_net.py        FanFiction.net metadata/chapter parser
  browser.py               the only Playwright/network boundary
  clean_html.py            story-block extraction and semantic HTML
  html_to_markdown.py      mechanical UTF-8 Markdown normalization
  render_pdf.py            chapter/provenance/TOC PDF rendering
  merge_pdf.py             merge, global page numbers, bookmarks
  build_manifest.py        deterministic JSONL and hash records
  validate.py              structural/content/integrity validation
  build_comparison_index.py topic/style suggestions and reviewed index
  report.py                human-readable acquisition/validation report
  cli.py                   argument parsing and orchestration
data/fanfic-hogwarts-history/
  README.md
  source-registry.json
  schemas/
    source-record.schema.json
    manifest-record.schema.json
    work-validation.schema.json
  reports/
    title-collision-exclusions.json
    source-candidates.json
tests/fanfic_dataset/
  __init__.py
  conftest.py
  fixtures/
    fanfiction-net-single.html
    fanfiction-net-multi.html
    access-denied.html
  test_models_registry.py
  test_policy.py
  test_fanfiction_net.py
  test_capture.py
  test_transform.py
  test_pdf.py
  test_manifest.py
  test_validate.py
  test_cli.py
  test_comparison_index.py
```

### Ignored local/generated files

```text
.fanfic-venv/
data/fanfic-hogwarts-history/manifest.jsonl
data/fanfic-hogwarts-history/chapter-comparison-index.jsonl
data/fanfic-hogwarts-history/works/
data/fanfic-hogwarts-history/reports/acquisition-report.md
data/fanfic-hogwarts-history/reports/validation-report.md
data/fanfic-hogwarts-history/reports/comparison-summary.md
data/fanfic-hogwarts-history/reports/manual-review.json
data/fanfic-hogwarts-history/reports/policy-snapshots/
```

### Per-work local layout

```text
works/HAH-FAN-001/
  latest.json
  captures/20260722T120000Z/
    metadata.json
    run-state.json
    annotations.json
    raw/chapter-001.html
    clean/chapter-001.html
    text/chapter-001.md
    pdf/chapter-001.pdf
    pdf/HAH-FAN-001__hogwarts-a-history__unclebulgaria5.pdf
    diagnostics/
    validation.json
```

`capture_id` is the UTC retrieval start formatted as `%Y%m%dT%H%M%SZ`. A resumed run reuses its capture ID. A new run refuses to replace `latest.json` unless all validation passes.

## Shared Interfaces

These names are stable across all tasks:

```python
class SourceRecord(BaseModel): ...
class ChapterRef(BaseModel): ...
class WorkDiscovery(BaseModel): ...
class CapturePaths: ...
class CapturedPage(BaseModel): ...
class ChapterArtifact(BaseModel): ...
class ManifestRecord(BaseModel): ...
class CheckResult(BaseModel): ...
class WorkValidation(BaseModel): ...

def load_sources(path: Path) -> dict[str, SourceRecord]: ...
def evaluate_policy(url: str, robots_text: str, requested_delay: float) -> PolicyDecision: ...
def parse_fanfiction_net(html: str, canonical_url: str, source: SourceRecord) -> WorkDiscovery: ...
async def capture_work(source: SourceRecord, options: CaptureOptions) -> CaptureResult: ...
def build_clean_html(page: CapturedPage, annotations: ChapterAnnotations) -> str: ...
def html_to_markdown(clean_html: str) -> str: ...
async def render_chapter_pdf(clean_html_path: Path, output_path: Path) -> None: ...
def merge_work_pdf(discovery: WorkDiscovery, chapter_pdfs: list[Path], output_path: Path) -> None: ...
def build_manifest(capture_dir: Path) -> list[ManifestRecord]: ...
def validate_work(capture_dir: Path) -> WorkValidation: ...
```

## Task 1: Isolate the Runtime and Define the Data Contracts

**Files:**

- Modify: `.gitignore`
- Create: `requirements-fanfic.txt`
- Create: `pytest.ini`
- Create: `scripts/fanfic_dataset/__init__.py`
- Create: `scripts/fanfic_dataset/models.py`
- Create: `scripts/fanfic_dataset/emit_schemas.py`
- Create: `scripts/fanfic_dataset/paths.py`
- Create: `scripts/fanfic_dataset/registry.py`
- Create: `data/fanfic-hogwarts-history/source-registry.json`
- Create: `data/fanfic-hogwarts-history/schemas/source-record.schema.json`
- Create: `data/fanfic-hogwarts-history/schemas/manifest-record.schema.json`
- Create: `data/fanfic-hogwarts-history/schemas/work-validation.schema.json`
- Create: `data/fanfic-hogwarts-history/reports/title-collision-exclusions.json`
- Create: `data/fanfic-hogwarts-history/reports/source-candidates.json`
- Test: `tests/fanfic_dataset/test_models_registry.py`

**Interfaces:**

- Consumes: no earlier task.
- Produces: `SourceRecord`, `ChapterRef`, `WorkDiscovery`, `CapturePaths`, `ManifestRecord`, `WorkValidation`, `load_sources()`, `capture_paths()`.

- [ ] **Step 1: Verify the runtime prerequisite without changing the existing environment**

Run:

```bash
python3.12 --version
```

Expected today: command-not-found. Before implementation continues, install or otherwise provision Python 3.12+, then expect `Python 3.12.x` or newer. Do not rebuild `.venv`.

- [ ] **Step 2: Write the failing contract and registry tests**

Create `tests/fanfic_dataset/test_models_registry.py`:

```python
from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.fanfic_dataset.models import ManifestRecord, SourceRecord
from scripts.fanfic_dataset.emit_schemas import schema_documents
from scripts.fanfic_dataset.paths import capture_paths
from scripts.fanfic_dataset.registry import load_sources


def test_registry_contains_exact_approved_core_sources(tmp_path: Path) -> None:
    registry = tmp_path / "source-registry.json"
    registry.write_text(
        '[{"source_id":"HAH-FAN-001","work_title":"Hogwarts: A History",'
        '"author":"Example Author","platform":"fanfiction.net",'
        '"work_url":"https://www.fanfiction.net/s/1/1/example",'
        '"expected_available_chapter_count":6,"status":"core"}]',
        encoding="utf-8",
    )
    loaded = load_sources(registry)
    assert list(loaded) == ["HAH-FAN-001"]
    assert loaded["HAH-FAN-001"].expected_available_chapter_count == 6


def test_source_rejects_non_https_url() -> None:
    with pytest.raises(ValidationError):
        SourceRecord(
            source_id="HAH-FAN-001",
            work_title="Example",
            author="Example",
            platform="fanfiction.net",
            work_url="http://www.fanfiction.net/s/1/1/example",
            expected_available_chapter_count=1,
            status="core",
        )


def test_capture_paths_are_versioned_and_confined(tmp_path: Path) -> None:
    paths = capture_paths(tmp_path, "HAH-FAN-001", "20260722T120000Z")
    assert paths.root == tmp_path / "works/HAH-FAN-001/captures/20260722T120000Z"
    assert paths.chapter("raw", 2, ".html").name == "chapter-002.html"


def test_manifest_requires_non_canon_labels() -> None:
    fields = ManifestRecord.model_fields
    assert fields["fan_created"].default is True
    assert fields["canon_status"].default == "non-canon fanfiction"


def test_checked_in_schemas_match_models() -> None:
    root = Path(__file__).resolve().parents[2]
    for name, document in schema_documents().items():
        path = root / "data/fanfic-hogwarts-history/schemas" / name
        assert json.loads(path.read_text("utf-8")) == document
```

Add `import json` to the test module.

- [ ] **Step 3: Run the tests to prove the package does not exist**

Run:

```bash
.fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_models_registry.py -q
```

Expected: collection error for `scripts.fanfic_dataset.models`.

- [ ] **Step 4: Create the isolated environment and dependency lock**

Create `requirements-fanfic.txt` with compatible, exact versions selected and installed at execution time:

```text
beautifulsoup4==4.13.4
jsonschema==4.25.0
markdownify==1.1.0
playwright==1.54.0
pydantic==2.11.7
PyMuPDF==1.26.3
pytest==8.4.1
```

Run:

```bash
python3.12 -m venv .fanfic-venv
.fanfic-venv/bin/python -m pip install -r requirements-fanfic.txt
.fanfic-venv/bin/python -m playwright install chromium
```

Expected: dependencies and the Playwright Chromium build install successfully. If a selected pin is unavailable for the provisioned Python, update the pin to the newest compatible stable release, record the resolved version in the plan execution notes, and rerun the full suite.

- [ ] **Step 5: Implement the shared models**

Create `scripts/fanfic_dataset/__init__.py`:

```python
"""Private fanfic reference dataset tooling."""

__version__ = "1.0.0"
```

Create `scripts/fanfic_dataset/models.py` with strict Pydantic models. Required fields and exact invariants:

```python
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourceRecord(StrictModel):
    source_id: str = Field(pattern=r"^HAH-FAN-\d{3}$")
    work_title: str
    author: str
    platform: Literal["fanfiction.net"]
    work_url: HttpUrl
    expected_available_chapter_count: int = Field(ge=1)
    status: Literal["core", "excluded", "candidate-needs-editorial-review"]
    priority: Literal["high", "medium", "low"] = "medium"
    known_limitations: list[str] = []
    promised_but_unavailable_chapters: list[str] = []

    @field_validator("work_url")
    @classmethod
    def require_https(cls, value: HttpUrl) -> HttpUrl:
        if value.scheme != "https":
            raise ValueError("work_url must use HTTPS")
        return value


class ChapterRef(StrictModel):
    chapter_index: int = Field(ge=1)
    chapter_title: str | None
    title_missing: bool = False
    chapter_url: HttpUrl


class WorkDiscovery(StrictModel):
    source_id: str
    work_id: str
    work_title: str
    author: str
    summary: str
    rating: str | None
    language: str | None
    displayed_word_count: int | None
    published_date_displayed: str | None
    updated_date_displayed: str | None
    native_download_url: HttpUrl | None = None
    chapters: list[ChapterRef]


class CapturedPage(StrictModel):
    source_id: str
    chapter: ChapterRef
    retrieved_at_utc: datetime
    final_url: HttpUrl
    status: int
    raw_html_path: Path


class ChapterArtifact(StrictModel):
    source_id: str
    capture_id: str
    chapter: ChapterRef
    raw_html_path: Path
    clean_html_path: Path
    text_path: Path
    chapter_pdf_path: Path


class ManifestRecord(StrictModel):
    dataset_version: str = "1.0"
    capture_id: str
    source_id: str
    work_title: str
    author: str
    platform: str
    work_url: HttpUrl
    chapter_index: int = Field(ge=1)
    chapter_title: str | None
    title_missing: bool = False
    chapter_url: HttpUrl
    retrieved_at_utc: datetime
    published_date_displayed: str | None
    updated_date_displayed: str | None
    expected_available_chapter_count: int
    raw_html_path: Path
    clean_html_path: Path
    text_path: Path
    chapter_pdf_path: Path
    complete_pdf_path: Path
    raw_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    clean_html_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    text_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    chapter_pdf_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    complete_pdf_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    fan_created: bool = True
    canon_status: str = "non-canon fanfiction"
    dataset_role: str = "style-and-coverage-reference"
    tool_version: str


class CheckResult(StrictModel):
    check_id: str
    passed: bool
    detail: str


class WorkValidation(StrictModel):
    source_id: str
    capture_id: str
    status: Literal["pass", "fail", "manual-review-pending"]
    checks: list[CheckResult]
```

- [ ] **Step 6: Implement safe versioned paths and registry loading**

Create `scripts/fanfic_dataset/paths.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


SAFE_ID = re.compile(r"^[A-Z0-9-]+$")
CAPTURE_ID = re.compile(r"^\d{8}T\d{6}Z$")


@dataclass(frozen=True)
class CapturePaths:
    root: Path

    def chapter(self, kind: str, index: int, suffix: str) -> Path:
        if kind not in {"raw", "clean", "text", "pdf"}:
            raise ValueError(f"unsupported artifact kind: {kind}")
        if index < 1:
            raise ValueError("chapter index must be positive")
        return self.root / kind / f"chapter-{index:03d}{suffix}"


def capture_paths(output_root: Path, source_id: str, capture_id: str) -> CapturePaths:
    if not SAFE_ID.fullmatch(source_id) or not CAPTURE_ID.fullmatch(capture_id):
        raise ValueError("unsafe source_id or capture_id")
    return CapturePaths(output_root / "works" / source_id / "captures" / capture_id)
```

Create `scripts/fanfic_dataset/registry.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

from .models import SourceRecord


def load_sources(path: Path) -> dict[str, SourceRecord]:
    records = [SourceRecord.model_validate(item) for item in json.loads(path.read_text("utf-8"))]
    by_id = {record.source_id: record for record in records}
    if len(by_id) != len(records):
        raise ValueError("source registry contains duplicate source_id values")
    return by_id
```

Create `scripts/fanfic_dataset/emit_schemas.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

from .models import ManifestRecord, SourceRecord, WorkValidation


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "data/fanfic-hogwarts-history/schemas"


def schema_documents() -> dict[str, dict]:
    return {
        "manifest-record.schema.json": ManifestRecord.model_json_schema(),
        "source-record.schema.json": SourceRecord.model_json_schema(),
        "work-validation.schema.json": WorkValidation.model_json_schema(),
    }


def main() -> int:
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for name, document in schema_documents().items():
        (SCHEMA_DIR / name).write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Run it once to create the checked-in schema files:

```bash
.fanfic-venv/bin/python -m scripts.fanfic_dataset.emit_schemas
```

Expected: the three files under `data/fanfic-hogwarts-history/schemas/` are created, and rerunning the command makes no diff.

- [ ] **Step 7: Seed the registries and ignore rules**

Create `source-registry.json` with the four exact source records from the acquisition brief and counts `6`, `3`, `6`, `1`. Set all four to `status: "core"`. Record HAH-FAN-001's lost/promised chapter description in `promised_but_unavailable_chapters`.

Create `title-collision-exclusions.json` with Lizzie_carlile's Hermione AU, its discovery/original URLs, exclusion reason, and `status: "excluded"`.

Create `source-candidates.json` with FanFiction.net work `14387130`, author `Wizardry.101`, publication date `2024-08-28`, and reason `Title and founder-history framing may qualify, but the public first page reads as a dramatic screenplay rather than an imitation of Bathilda Bagshot's reference book; editorial review required.`

Append these exact patterns to `.gitignore`:

```gitignore
.fanfic-venv/
data/fanfic-hogwarts-history/manifest.jsonl
data/fanfic-hogwarts-history/chapter-comparison-index.jsonl
data/fanfic-hogwarts-history/works/
data/fanfic-hogwarts-history/reports/acquisition-report.md
data/fanfic-hogwarts-history/reports/validation-report.md
data/fanfic-hogwarts-history/reports/comparison-summary.md
data/fanfic-hogwarts-history/reports/manual-review.json
data/fanfic-hogwarts-history/reports/policy-snapshots/
```

- [ ] **Step 8: Run the focused tests and commit**

Run:

```bash
.fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_models_registry.py -q
```

Expected: `5 passed`.

Commit:

```bash
git add .gitignore requirements-fanfic.txt pytest.ini scripts/fanfic_dataset data/fanfic-hogwarts-history tests/fanfic_dataset
git commit -m "feat: scaffold fanfic dataset contracts"
```

## Task 2: Add Policy Preflight and Deterministic Discovery

**Files:**

- Create: `scripts/fanfic_dataset/policy.py`
- Create: `scripts/fanfic_dataset/discover.py`
- Create: `scripts/fanfic_dataset/fanfiction_net.py`
- Create: `tests/fanfic_dataset/fixtures/fanfiction-net-single.html`
- Create: `tests/fanfic_dataset/fixtures/fanfiction-net-multi.html`
- Create: `tests/fanfic_dataset/test_policy.py`
- Create: `tests/fanfic_dataset/test_fanfiction_net.py`

**Interfaces:**

- Consumes: `SourceRecord`, `ChapterRef`, `WorkDiscovery`.
- Produces: `PolicyDecision`, `evaluate_policy()`, `parse_fanfiction_net()`, and `PlatformAdapter` protocol.

- [ ] **Step 1: Write failing policy and parser tests**

Test these exact behaviors:

```python
def test_policy_raises_effective_delay_to_robots_value():
    robots = "User-agent: *\nAllow: /\nCrawl-delay: 5\n"
    decision = evaluate_policy("https://www.fanfiction.net/s/1/1/x", robots, 3.0)
    assert decision.allowed is True
    assert decision.effective_delay_seconds == 5.0


def test_policy_rejects_disallowed_story_path():
    robots = "User-agent: *\nDisallow: /s/\n"
    decision = evaluate_policy("https://www.fanfiction.net/s/1/1/x", robots, 5.0)
    assert decision.allowed is False


def test_parser_discovers_chapters_in_numeric_order(multi_html, source):
    work = parse_fanfiction_net(multi_html, str(source.work_url), source)
    assert [chapter.chapter_index for chapter in work.chapters] == [1, 2, 3]
    assert [chapter.chapter_title for chapter in work.chapters] == ["Contents", "Founders", "Castle"]


def test_parser_rejects_missing_story_container(single_html, source):
    html = single_html.replace('id="storytext"', 'id="missing"')
    with pytest.raises(ExtractionError, match="story container"):
        parse_fanfiction_net(html, str(source.work_url), source)
```

The fixtures must include only invented sentences such as `Synthetic paragraph for parser testing.` They must model `#profile_top`, `#chap_select`, selected options, and `#storytext`, but contain no copied fanfic prose.

- [ ] **Step 2: Run tests and confirm missing imports**

Run:

```bash
.fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_policy.py tests/fanfic_dataset/test_fanfiction_net.py -q
```

Expected: collection errors for the new modules.

- [ ] **Step 3: Implement policy evaluation**

`PolicyDecision` contains `allowed`, `reason`, `robots_url`, `robots_sha256`, and `effective_delay_seconds`. `evaluate_policy()` must:

1. Parse with `RobotFileParser` using user-agent `*`.
2. Check `can_fetch("*", url)`.
3. Read `crawl_delay("*")` when numeric.
4. Set delay to `max(5.0, requested_delay, robots_delay or 0.0)`.
5. Hash the exact robots body.
6. Return a decision; it must never silently convert a disallowance to allowance.

The live browser task writes the robots body and decision JSON to `reports/policy-snapshots/<capture-id>/` before visiting a story.

- [ ] **Step 4: Implement semantic FanFiction.net parsing**

Use these ordered fallback selectors:

```python
STORY_SELECTORS = ("#storytext", "div.storytext")
PROFILE_SELECTORS = ("#profile_top", "div#profile_top")
CHAPTER_SELECTORS = ("select#chap_select option", "select[name='chapter'] option")
```

`parse_fanfiction_net()` must validate that:

- page work ID equals the numeric ID in `SourceRecord.work_url`;
- parsed title and author are non-empty;
- exactly one supported story selector is used;
- selector options become unique, consecutive `ChapterRef` values;
- an empty chapter title sets `title_missing: true`, while a non-empty title must keep it `false`;
- a one-chapter page without a selector yields Chapter 1 from the canonical URL;
- any discovered native link with `download`, `epub`, `pdf`, or `export` in its accessible text/URL is returned for operator review rather than followed automatically;
- duplicate or non-numeric chapter values raise `ExtractionError`.

Metadata parsing must use visible labels (`Rated:`, `Language`, `Chapters:`, `Words:`, `Published:`, `Updated:`, `id:`) and tolerate missing optional fields. Do not bind correctness to one complete CSS class string.

Create `discover.py` with this complete platform boundary:

```python
from __future__ import annotations

from typing import Protocol

from .models import SourceRecord, WorkDiscovery


class PlatformAdapter(Protocol):
    def discover(self, html: str, canonical_url: str, source: SourceRecord) -> WorkDiscovery:
        """Parse public work metadata and canonical chapter URLs without I/O."""
        ...


def adapter_for(source: SourceRecord) -> PlatformAdapter:
    if source.platform == "fanfiction.net":
        from .fanfiction_net import FanFictionNetAdapter

        return FanFictionNetAdapter()
    raise ValueError(f"unsupported platform: {source.platform}")
```

- [ ] **Step 5: Run focused tests and commit**

Run:

```bash
.fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_policy.py tests/fanfic_dataset/test_fanfiction_net.py -q
```

Expected: all tests pass.

Commit:

```bash
git add scripts/fanfic_dataset tests/fanfic_dataset
git commit -m "feat: add policy-aware fanfic discovery"
```

## Task 3: Implement the Single Network Boundary and Versioned Capture State

**Files:**

- Create: `scripts/fanfic_dataset/browser.py`
- Create: `tests/fanfic_dataset/fixtures/access-denied.html`
- Create: `tests/fanfic_dataset/test_capture.py`

**Interfaces:**

- Consumes: `PolicyDecision`, `SourceRecord`, `WorkDiscovery`, `CapturePaths`.
- Produces: `CaptureOptions`, `CaptureResult`, `BrowserGateway` protocol, `capture_work()`.

- [ ] **Step 1: Write failing tests with a fake browser**

The fake gateway records calls and returns fixture HTML. Cover:

```python
async def test_capture_is_sequential_and_sleeps_between_chapters(...):
    result = await capture_work(source, options, gateway=fake, sleep=fake_sleep)
    assert fake.max_in_flight == 1
    assert fake_sleep.calls == [pytest.approx(5.0, abs=1.0)] * 2
    assert len(result.pages) == 3


async def test_dry_run_does_not_create_capture_directory(...):
    result = await capture_work(source, options.model_copy(update={"dry_run": True}), gateway=fake)
    assert result.discovery.chapters
    assert not output_root.exists()


async def test_access_denial_writes_diagnostic_and_stops(...):
    fake.responses[chapter_2_url] = FakeResponse(403, access_denied_html)
    with pytest.raises(CaptureStopped):
        await capture_work(source, options, gateway=fake, sleep=fake_sleep)
    assert diagnostic_path.exists()
    assert not chapter_3_raw_path.exists()


async def test_resume_never_refetches_completed_chapter(...):
    await capture_work(source, options, gateway=fake, sleep=fake_sleep)
    fake.calls.clear()
    await capture_work(source, options.model_copy(update={"resume": True}), gateway=fake)
    assert fake.calls == []
```

- [ ] **Step 2: Implement capture rules**

`browser.py` must be the only module importing `playwright.async_api`. It must:

1. Launch Chromium headed only when `--headed` is set.
2. Create one new, unauthenticated context with default browser user agent and no storage state.
3. Fetch and snapshot `robots.txt` before story navigation.
4. Load Chapter 1 and wait for one story selector using a bounded 30-second timeout.
5. For dry-run, return discovery immediately without writing story HTML or capture directories.
6. Otherwise create the versioned capture root and atomically write `metadata.json` plus `run-state.json`.
7. Visit chapters in numeric order, checking main-document response status and final URL.
8. Save `await main_response.body()` byte-for-byte as the raw main-document response only after checking status, final URL, non-empty story selector in the rendered page, and failure signatures in both the response body and rendered visible text. Decode a separate in-memory copy using the declared response charset, falling back to UTF-8 with replacement, for checks and parsing; record the charset decision in capture metadata. Never use `page.content()` for the raw artifact.
9. Sleep after a successful chapter only when another request remains. Use `effective_delay + random.uniform(0, 1)`.
10. Update `run-state.json` atomically after every completed chapter.
11. On stop conditions, write `diagnostics/chapter-NNN.json` with URL, status, selector results, failure signature, and screenshot path. A screenshot may contain copyrighted text and stays inside the ignored capture directory.
12. Allow only two retries for connection reset/timeouts, with 2 and 4 second backoff. Never retry 403, 429, CAPTCHA, challenge, or robots failures.

Use atomic writes through `path.with_suffix(path.suffix + ".tmp")` followed by `replace()`; cleanup may delete only that exact temporary file.

- [ ] **Step 3: Run focused tests and commit**

Run:

```bash
.fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_capture.py -q
```

Expected: all capture tests pass without network access.

Commit:

```bash
git add scripts/fanfic_dataset/browser.py tests/fanfic_dataset
git commit -m "feat: add sequential versioned fanfic capture"
```

## Task 4: Build Lossless Clean HTML and Normalized Markdown

**Files:**

- Create: `scripts/fanfic_dataset/clean_html.py`
- Create: `scripts/fanfic_dataset/html_to_markdown.py`
- Create: `tests/fanfic_dataset/test_transform.py`

**Interfaces:**

- Consumes: raw HTML, `CapturedPage`, and optional `annotations.json` keyed by paragraph SHA-256.
- Produces: semantic chapter HTML, normalized Markdown, block inventory for manual annotations.

- [ ] **Step 1: Write failing transform tests**

Cover exact output invariants:

```python
def test_clean_html_contains_only_provenance_and_story_blocks(single_html, captured_page):
    result = extract_chapter(single_html, captured_page)
    assert "Synthetic paragraph" in result.html
    assert "Post Review" not in result.html
    assert "<script" not in result.html
    assert result.blocks[0].sha256


def test_markdown_preserves_emphasis_and_markers(clean_html):
    text = html_to_markdown(clean_html)
    assert "*emphasized*" in text
    assert "<!-- BEGIN CHAPTER TEXT -->" in text
    assert text.endswith("<!-- END CHAPTER TEXT -->\n")


def test_author_note_annotation_wraps_only_matching_block(...):
    annotations = ChapterAnnotations(author_note_block_sha256=[first_block_hash])
    text = html_to_markdown(build_clean_html(page, annotations))
    assert text.count("<!-- BEGIN AUTHOR NOTE -->") == 1
    assert text.count("<!-- BEGIN CHAPTER TEXT -->") == 1
```

- [ ] **Step 2: Implement block extraction and annotation**

`extract_chapter()` must copy child blocks from the selected story container in source order, drop only `script`, `style`, form controls, and nodes explicitly outside that container, and compute SHA-256 from each block's normalized visible text. It must never delete a story block because its prose resembles an author note.

The semantic HTML template must contain, in order: work title; author; canonical source URL; chapter number and title; summary/rating/language/published/updated metadata on Chapter 1 only; then annotated story blocks. It must contain no review controls, navigation, recommendation, advertisement, account, tracking, remote image, or remote script nodes.

`annotations.json` has this exact form:

```json
{
  "chapter-001": {
    "author_note_block_sha256": ["<64 lowercase hex characters>"],
    "missing_chapter_notice_block_sha256": [],
    "reviewed_by": "operator name",
    "reviewed_at_utc": "2026-07-22T12:00:00Z"
  }
}
```

Unknown hashes are validation failures. Unannotated blocks default to chapter text and remain preserved.

- [ ] **Step 3: Implement mechanical Markdown normalization**

Use `markdownify` only on the semantic story section. Normalize NBSP to space, CRLF/CR to LF, trailing spaces away, and runs of more than two blank lines to two. Preserve headings, paragraph boundaries, `em`, `strong`, and links. Emit the exact visible markers required by the acquisition brief. Always end with one newline.

- [ ] **Step 4: Run tests and commit**

Run:

```bash
.fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_transform.py -q
```

Expected: all transform tests pass.

Commit:

```bash
git add scripts/fanfic_dataset/clean_html.py scripts/fanfic_dataset/html_to_markdown.py tests/fanfic_dataset/test_transform.py
git commit -m "feat: normalize captured fanfic chapters"
```

## Task 5: Render Chapter PDFs and Assemble the Complete Work PDF

**Files:**

- Create: `scripts/fanfic_dataset/render_pdf.py`
- Create: `scripts/fanfic_dataset/merge_pdf.py`
- Create: `tests/fanfic_dataset/test_pdf.py`

**Interfaces:**

- Consumes: clean HTML, work metadata, ordered chapter PDF paths.
- Produces: one chapter PDF per chapter and canonical complete PDF with provenance page, TOC, bookmarks, and global page numbers.

- [ ] **Step 1: Write failing PDF tests**

Generate two tiny synthetic HTML chapters in a temporary directory and assert:

```python
with fitz.open(complete_pdf) as document:
    text = "\n".join(page.get_text() for page in document)
    assert "Fan-created, non-canon material captured for private comparative research." in text
    assert "Synthetic Chapter One" in text
    assert "Synthetic Chapter Two" in text
    assert [item[1] for item in document.get_toc()] == [
        "Synthetic Chapter One",
        "Synthetic Chapter Two",
    ]
    assert document[-1].get_text().strip().endswith(str(document.page_count))
```

- [ ] **Step 2: Render deterministic chapter PDFs**

`render_chapter_pdf()` opens the local `file://` clean HTML with Playwright, waits for fonts, and calls `page.pdf()` with A4, tagged PDF, background printing, fixed 20mm margins, and no header/footer. The clean HTML template must use system serif fonts only and must not fetch remote fonts/images/scripts.

- [ ] **Step 3: Assemble and number the complete PDF**

`merge_work_pdf()` must:

1. Generate provenance and TOC pages from local HTML and render them first.
2. Insert each chapter PDF with PyMuPDF in numeric order.
3. Add one level-1 TOC/bookmark entry at the first page of each chapter.
4. Add global page numbers at bottom center after all pages are inserted.
5. Save to a temporary PDF, reopen it, confirm page count and TOC count, then atomically replace the destination.
6. Use canonical name `<source-id>__<slugified-title>__<slugified-author>.pdf`; slugs are lowercase ASCII alphanumerics separated by single hyphens.

- [ ] **Step 4: Run PDF tests and commit**

Run:

```bash
.fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_pdf.py -q
```

Expected: PDF text, page-number, and bookmark assertions pass.

Commit:

```bash
git add scripts/fanfic_dataset/render_pdf.py scripts/fanfic_dataset/merge_pdf.py tests/fanfic_dataset/test_pdf.py
git commit -m "feat: render complete fanfic reference PDFs"
```

## Task 6: Build Deterministic Manifest Records and Latest Pointers

**Files:**

- Create: `scripts/fanfic_dataset/build_manifest.py`
- Create: `tests/fanfic_dataset/test_manifest.py`

**Interfaces:**

- Consumes: validated capture metadata and artifacts.
- Produces: sorted `manifest.jsonl`, per-work `latest.json`, SHA-256 values for every artifact.

- [ ] **Step 1: Write failing manifest tests**

Assert that two synthetic chapters yield two newline-terminated JSONL records sorted by `(source_id, capture_id, chapter_index)`, all paths are relative to `data/fanfic-hogwarts-history`, all five hashes are lowercase SHA-256, and `complete_pdf_path` is identical across a work's records.

- [ ] **Step 2: Implement hashing and manifest construction**

Use this exact helper:

```python
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
```

`build_manifest(capture_dir)` refuses missing files, absolute output paths, paths outside the dataset root, and non-consecutive chapters. Serialize each `ManifestRecord` with `model_dump(mode="json")`, `sort_keys=True`, and compact separators.

Do not update `latest.json` in this task. Expose `promote_latest(work_validation)` and allow it only when status is `pass`; the CLI calls it after Task 7 validation.

- [ ] **Step 3: Run tests and commit**

Run:

```bash
.fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_manifest.py -q
```

Expected: all manifest tests pass.

Commit:

```bash
git add scripts/fanfic_dataset/build_manifest.py tests/fanfic_dataset/test_manifest.py
git commit -m "feat: build hashed fanfic dataset manifest"
```

## Task 7: Implement Structural, Content, Integrity, and Manual Validation

**Files:**

- Create: `scripts/fanfic_dataset/validate.py`
- Create: `tests/fanfic_dataset/test_validate.py`

**Interfaces:**

- Consumes: capture metadata, raw/clean/text/PDF artifacts, annotations, manual review file.
- Produces: `validation.json`, dataset validation summary, process exit status `0` only for pass.

- [ ] **Step 1: Write one failing test per validation family**

Tests must prove failure for:

- captured count differs from displayed count;
- duplicate/nonconsecutive URL or index;
- empty/missing title without an explicit `title_missing: true` record;
- empty story text;
- raw or clean HTML contains `Checking your browser`, `Access denied`, `CAPTCHA`, or `Page not found`;
- clean HTML contains known site-chrome selectors/text;
- first or last substantial Markdown paragraph is absent from PDF text;
- PDF/Markdown normalized length ratio is outside `0.75 <= ratio <= 1.35`;
- PDF/semantic-HTML visible-text ratio is outside `0.75 <= ratio <= 1.35`;
- bookmark count differs from chapter count;
- stored hashes differ from current files;
- an annotation references an unknown block hash;
- required manual spot checks are unsigned.

- [ ] **Step 2: Implement the validation pipeline**

Each check returns `CheckResult(check_id, passed, detail)`. `validate_work()` runs all checks so one failure does not hide others. A substantial paragraph is at least 40 visible characters after markers and Markdown punctuation are removed.

Manual review records use:

```json
{
  "HAH-FAN-001/20260722T120000Z": {
    "reviewed_by": "operator name",
    "reviewed_at_utc": "2026-07-22T12:00:00Z",
    "first_chapter": true,
    "final_chapter": true,
    "longest_chapter": true,
    "chapter_transitions": true,
    "author_note_or_missing_notice_chapters": [1, 4],
    "notes": "Compared rendered pages with the public source; no site chrome observed."
  }
}
```

Before manual review is signed, otherwise-valid work status is `manual-review-pending`, not `pass`. Hash mismatches or automated failures always produce `fail`.

- [ ] **Step 3: Run tests and commit**

Run:

```bash
.fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_validate.py -q
```

Expected: all validation tests pass.

Commit:

```bash
git add scripts/fanfic_dataset/validate.py tests/fanfic_dataset/test_validate.py
git commit -m "feat: validate fanfic dataset artifacts"
```

## Task 8: Wire the CLI, Recipes, and Reports

**Files:**

- Create: `scripts/fanfic_dataset/report.py`
- Create: `scripts/fanfic_dataset/cli.py`
- Modify: `Justfile`
- Create: `data/fanfic-hogwarts-history/README.md`
- Create: `tests/fanfic_dataset/test_cli.py`

**Interfaces:**

- Consumes: all preceding module APIs.
- Produces: requested CLI commands, exit codes, dry-run output, acquisition/validation reports.

- [ ] **Step 1: Write failing CLI tests**

Invoke `main([...])` with fakes and assert:

- `acquire --source HAH-FAN-004 --dry-run` makes discovery calls only and prints count/status;
- `acquire --all` selects exactly core sources in source-ID order;
- `--request-delay-seconds 4` prints/evaluates an effective five-second minimum;
- unknown/excluded source IDs return exit code `2`;
- `validate --all` returns `1` if any work fails or is pending manual review;
- `report` includes all four source IDs, exclusions, counts, failures, paths, and open issues;
- mutually exclusive `--resume` and `--force-new-version` are rejected by argparse.

- [ ] **Step 2: Implement the CLI commands**

Support exactly:

```text
acquire --source ID | --all [--resume | --force-new-version] [--headed]
        [--dry-run] [--output-root PATH] [--request-delay-seconds FLOAT]
validate --source ID | --all [--output-root PATH]
build-index [--output-root PATH]
report [--output-root PATH]
```

Defaults:

```text
output-root = data/fanfic-hogwarts-history
request-delay-seconds = 5.0
headed = false
resume = false
force-new-version = false
dry-run = false
```

The acquisition orchestrator executes discovery/capture, transform, chapter PDF render, work PDF merge, manifest build, validation, and report refresh. It does not promote `latest.json` until validation status is `pass`.

- [ ] **Step 3: Add short `just` recipes without changing existing recipes**

Append:

```just
# Run fanfic dataset unit tests without live network access
fanfic-test:
    .fanfic-venv/bin/python -m pytest tests/fanfic_dataset -q

# Discover all approved works without saving story bodies
fanfic-dry-run:
    .fanfic-venv/bin/python -m scripts.fanfic_dataset.cli acquire --all --dry-run

# Validate all locally captured works
fanfic-validate:
    .fanfic-venv/bin/python -m scripts.fanfic_dataset.cli validate --all

# Rebuild the local comparison index
fanfic-index:
    .fanfic-venv/bin/python -m scripts.fanfic_dataset.cli build-index

# Rebuild human-readable fanfic dataset reports
fanfic-report:
    .fanfic-venv/bin/python -m scripts.fanfic_dataset.cli report
```

- [ ] **Step 4: Document the private-use and execution boundary**

`data/fanfic-hogwarts-history/README.md` must state:

- the dataset is fan-created, non-canon, private research material;
- generated prose/PDF artifacts are ignored and must not be committed or redistributed;
- the four approved IDs and exclusion/candidate report locations;
- environment creation and browser installation commands;
- dry-run, one-source, resume, validate, index, and report commands;
- manual review requirement;
- no access-control bypass and immediate-stop rules;
- how versioned captures and `latest.json` work.

- [ ] **Step 5: Run CLI tests and commit**

Run:

```bash
.fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_cli.py -q
just fanfic-test
```

Expected: focused and complete offline suites pass with no external requests.

Commit:

```bash
git add Justfile scripts/fanfic_dataset data/fanfic-hogwarts-history/README.md tests/fanfic_dataset/test_cli.py
git commit -m "feat: expose fanfic dataset workflow"
```

## Task 9: Run the Four Acquisition Phases with Review Gates

**Files:**

- Generate locally: `data/fanfic-hogwarts-history/works/**`
- Generate locally: `data/fanfic-hogwarts-history/manifest.jsonl`
- Generate locally: `data/fanfic-hogwarts-history/reports/policy-snapshots/**`
- Update locally: `data/fanfic-hogwarts-history/reports/manual-review.json`

**Interfaces:**

- Consumes: completed CLI and live public pages.
- Produces: validated, versioned local captures for the four approved sources.

- [ ] **Step 1: Recheck policy and source counts with dry-run**

Run:

```bash
just fanfic-dry-run
```

Expected: the policy check allows normal public page access, effective delay is at least five seconds, and source counts are reported. The expected current counts are 6, 3, 6, and 1; any mismatch stops acquisition and becomes an open issue rather than being forced through.

- [ ] **Step 2: Acquire the one-page proof of concept**

Run:

```bash
.fanfic-venv/bin/python -m scripts.fanfic_dataset.cli acquire --source HAH-FAN-004 --headed
```

Expected before manual review: one raw HTML, clean HTML, Markdown, chapter PDF, complete PDF, and `validation.json` with status `manual-review-pending`.

- [ ] **Step 3: Manually review HAH-FAN-004 and validate**

Inspect the source page, raw/clean/text artifacts, chapter PDF, complete PDF, provenance, page number, and absence of site chrome. Record the exact capture ID, operator name, UTC time, required booleans, and notes in `manual-review.json`.

Run:

```bash
.fanfic-venv/bin/python -m scripts.fanfic_dataset.cli validate --source HAH-FAN-004
```

Expected: status `pass`, exit `0`, and `latest.json` points to the reviewed capture.

- [ ] **Step 4: Acquire and review HAH-FAN-001**

Run:

```bash
.fanfic-venv/bin/python -m scripts.fanfic_dataset.cli acquire --source HAH-FAN-001 --headed
```

Expected: six chapter artifact sets and one complete PDF. Use the block-hash annotation workflow to mark the available missing-chapter notice; record promised-but-unavailable material only in metadata, never as a fabricated chapter. Review first, last, longest, all transitions, and notice/note pages, then rerun validation to `pass`.

- [ ] **Step 5: Acquire and review HAH-FAN-002 and HAH-FAN-003 separately**

Run:

```bash
.fanfic-venv/bin/python -m scripts.fanfic_dataset.cli acquire --source HAH-FAN-002 --headed
.fanfic-venv/bin/python -m scripts.fanfic_dataset.cli acquire --source HAH-FAN-003 --headed
```

Expected: 3 and 6 chapter artifact sets. Annotate actual author-note blocks by hash after comparing the public page, perform every manual spot check, then validate each work to `pass`.

- [ ] **Step 6: Validate all and verify counts**

Run:

```bash
just fanfic-validate
wc -l data/fanfic-hogwarts-history/manifest.jsonl
```

Expected: four passing works and `16` manifest lines if live source counts remain 6+3+6+1. Any source change must be reported with the live count; do not hard-code success around stale inventory.

Do not commit the generated artifacts.

## Task 10: Build and Review the Chapter Comparison Index

**Files:**

- Create: `scripts/fanfic_dataset/build_comparison_index.py`
- Create: `tests/fanfic_dataset/test_comparison_index.py`
- Generate locally: `data/fanfic-hogwarts-history/chapter-comparison-index.jsonl`
- Generate locally: `data/fanfic-hogwarts-history/reports/comparison-summary.md`

**Interfaces:**

- Consumes: latest passing manifests and normalized chapter Markdown.
- Produces: one reviewed comparison record per available chapter.

- [ ] **Step 1: Write failing comparison-index tests**

Assert that:

- only latest captures with validation `pass` are indexed;
- each manifest chapter yields exactly one record;
- all records include `use_for` and `must_not_use_for` exact constants;
- keyword suggestions are deterministic and case-insensitive;
- unreviewed records carry `review_status: "pending"` and make `build-index` exit `1`;
- reviewed records require at least one `topic_tag`, one `narrative_voice`, and reviewer/timestamp.

- [ ] **Step 2: Implement deterministic suggestions**

Use a checked-in vocabulary mapping, not an AI call. Initial exact mappings:

```python
TOPIC_KEYWORDS = {
    "architecture": ("castle", "tower", "corridor", "staircase"),
    "castle-layout": ("floor", "room", "passage", "dungeon"),
    "founders": ("gryffindor", "hufflepuff", "ravenclaw", "slytherin"),
    "great-hall": ("great hall", "enchanted ceiling"),
    "library": ("library", "books", "restricted section"),
    "school-governance": ("headmaster", "headmistress", "governor"),
    "student-life": ("student", "lesson", "class", "house"),
    "wards-and-security": ("ward", "protect", "secret passage"),
}
USE_FOR = ["style comparison", "coverage-gap discovery", "fan-invention detection"]
MUST_NOT_USE_FOR = ["canon confirmation", "historical proof"]
```

Suggestions initialize a review file; they are not accepted labels until a human confirms them against the normalized text. Narrative-voice choices are `reference-book`, `memoir-first-person`, `framed-narrative`, `mixed`, and `other`.

`comparison-summary.md` accepts a project chapter's topic tags and renders matching fanfic records under these exact headings:

```markdown
## Useful stylistic ideas
## Possible coverage gaps
## Fan-created claims that must not enter the seed without canon support
```

The third section is always present, even when no claims are recorded. The generator must never write a fanfic-derived fact to `sources/`, `book-seed/`, or `project-control/`.

- [ ] **Step 3: Review all 16 expected records**

For each record, confirm/remove suggested tags, select narrative voice, set `in_universe_ratio` from `0.0` through `1.0`, set `contains_author_notes`, record concise style notes without copying prose, and add reviewer/timestamp. The tool must preserve previous reviewed records when rerun and add only new capture IDs.

- [ ] **Step 4: Build and verify the final index**

Run:

```bash
just fanfic-index
wc -l data/fanfic-hogwarts-history/chapter-comparison-index.jsonl
```

Expected: exit `0` and the index line count equals the latest manifest's chapter count, currently expected to be `16`.

- [ ] **Step 5: Commit implementation only**

Run:

```bash
git add scripts/fanfic_dataset/build_comparison_index.py tests/fanfic_dataset/test_comparison_index.py
git commit -m "feat: build fanfic comparison index"
```

## Task 11: Final Verification and Acquisition Report

**Files:**

- Generate locally: `data/fanfic-hogwarts-history/reports/acquisition-report.md`
- Generate locally: `data/fanfic-hogwarts-history/reports/validation-report.md`
- Verify: all tracked implementation and local dataset artifacts.

**Interfaces:**

- Consumes: all tasks.
- Produces: evidence-backed final report without committing fanfic content.

- [ ] **Step 1: Run the complete offline implementation suite**

Run:

```bash
just fanfic-test
```

Expected: all tests pass and no live network calls occur.

- [ ] **Step 2: Run all local artifact validation and rebuild reports**

Run:

```bash
just fanfic-validate
just fanfic-index
just fanfic-report
```

Expected: all four core works pass; index has no pending records; both reports are regenerated.

- [ ] **Step 3: Verify no copyright-bearing artifact is staged**

Run:

```bash
git status --short
git check-ignore data/fanfic-hogwarts-history/works/HAH-FAN-001/captures/*/raw/chapter-001.html
git check-ignore data/fanfic-hogwarts-history/works/HAH-FAN-001/captures/*/pdf/*.pdf
```

Expected: both generated paths are ignored. Review every staged path; unstage any capture, text, or PDF before committing.

- [ ] **Step 4: Inspect final reports and artifact counts**

The acquisition report must use the exact requested headings:

```markdown
# Fanfic Dataset Acquisition Report

## Completed sources
## Excluded sources
## Validation summary
## Files created or updated
## Open issues
```

It must list each source's current chapter count, canonical complete-PDF path, and validation status; exclusions and candidates; expected/captured/PDF/failure totals; implementation paths; and any source changes, missing promised chapters, blocked pages, or extraction uncertainty.

- [ ] **Step 5: Commit final tracked documentation and tests**

Run:

```bash
git add .gitignore Justfile requirements-fanfic.txt pytest.ini scripts/fanfic_dataset tests/fanfic_dataset data/fanfic-hogwarts-history/README.md data/fanfic-hogwarts-history/source-registry.json data/fanfic-hogwarts-history/reports/title-collision-exclusions.json data/fanfic-hogwarts-history/reports/source-candidates.json
git diff --cached --check
git status --short
git commit -m "feat: complete fanfic reference dataset pipeline"
```

Expected: diff check passes, only implementation/metadata files are staged, and the commit succeeds.

## Requirement-to-Task Traceability

| Acquisition requirement | Implemented and verified in |
|---|---|
| Four approved sources and title collision | Tasks 1, 9 |
| Native-download-first inspection | Tasks 2, 8, 9 |
| Page-by-page sequential capture | Tasks 3, 9 |
| Raw HTML, clean HTML, Markdown, chapter PDFs | Tasks 3-5 |
| One complete PDF per work | Task 5 |
| Provenance, TOC, separators, bookmarks, page numbers | Task 5 |
| Mechanical text normalization and note markers | Task 4 |
| Manifest schema and all artifact hashes | Task 6 |
| Structural/content/integrity validation | Task 7 |
| Manual first/final/longest/transition/note review | Tasks 7, 9 |
| Idempotent resume and preserved versions | Tasks 1, 3, 6 |
| Topic/style comparison index | Task 10 |
| No access-control or policy bypass | Tasks 2, 3, 9 |
| Non-canon labeling and private-use boundary | Tasks 1, 5, 8, 11 |
| Final Codex report format | Tasks 8, 11 |

## Self-Review Result

- **Spec coverage:** Every acceptance criterion maps to at least one implementation and verification task. Native download inspection, manual review evidence, versioning, and source-change handling are now explicit.
- **Placeholder scan:** No prohibited placeholder or generic implementation steps remain. Angle-bracket values appear only where execution must supply an actual computed hash or person/timestamp in generated local data.
- **Type consistency:** The shared interfaces use the same `SourceRecord`, `ChapterRef`, `WorkDiscovery`, `CapturePaths`, `ManifestRecord`, and `WorkValidation` names throughout. PDF assembly consumes `WorkDiscovery`, and `complete_pdf_path` always refers to the canonical slugged filename.
- **Known prerequisite:** Python 3.12+ is not currently installed in the workspace environment. Execution cannot begin dependency installation until it is provisioned; the current Python 3.9 `.venv` is intentionally preserved.
