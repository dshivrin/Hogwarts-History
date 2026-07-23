from __future__ import annotations

import asyncio
import ast
from collections import defaultdict
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

import scripts.fanfic_dataset.browser as browser_module
from scripts.fanfic_dataset.browser import (
    CaptureOptions,
    CaptureStopped,
    capture_work,
)
from scripts.fanfic_dataset.models import SourceRecord
from scripts.fanfic_dataset.paths import capture_paths


FIXTURES = Path(__file__).parent / "fixtures"
ROBOTS = b"User-agent: *\nAllow: /\nCrawl-delay: 5\n"
BLOCKED_ROBOTS = b"User-agent: *\nDisallow: /s/\n"


@dataclass
class FakeResponse:
    status: int
    body: bytes
    final_url: str | None = None
    charset: str | None = "utf-8"
    visible_text: str | None = None
    selector_results: dict[str, bool] | None = None


@dataclass
class FakeSleep:
    calls: list[float] = field(default_factory=list)

    async def __call__(self, seconds: float) -> None:
        self.calls.append(seconds)


class FakeGateway:
    def __init__(
        self,
        responses: dict[str, FakeResponse | list[FakeResponse | BaseException]],
    ) -> None:
        self.responses = responses
        self.calls: list[str] = []
        self.events: list[str] = []
        self.in_flight = 0
        self.max_in_flight = 0
        self.attempts: defaultdict[str, int] = defaultdict(int)
        self.screenshots: list[Path] = []
        self.required_before_story: tuple[Path, ...] = ()

    async def fetch(
        self,
        url: str,
        *,
        story_selectors: tuple[str, ...] = (),
        timeout_seconds: float = 30.0,
    ) -> FakeResponse:
        del timeout_seconds
        self.calls.append(url)
        self.events.append(f"fetch:{url}")
        if story_selectors:
            assert all(path.exists() for path in self.required_before_story)
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        await asyncio.sleep(0)
        try:
            response: FakeResponse | BaseException
            configured = self.responses[url]
            if isinstance(configured, list):
                attempt = self.attempts[url]
                self.attempts[url] += 1
                response = configured[attempt]
            else:
                response = configured
            if isinstance(response, BaseException):
                raise response
            if response.final_url is None:
                response.final_url = url
            if response.visible_text is None:
                response.visible_text = response.body.decode(
                    response.charset or "utf-8", errors="replace"
                )
            if response.selector_results is None:
                response.selector_results = {
                    selector: selector == "#storytext"
                    and b'id="storytext"' in response.body
                    for selector in story_selectors
                }
            return response
        finally:
            self.in_flight -= 1

    async def screenshot(self, path: Path) -> None:
        self.events.append(f"screenshot:{path.name}")
        self.screenshots.append(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"synthetic screenshot")


@pytest.fixture
def source() -> SourceRecord:
    return SourceRecord(
        source_id="HAH-FAN-001",
        work_title="Invented Multi Work",
        author="Synthetic Author",
        platform="fanfiction.net",
        work_url="https://www.fanfiction.net/s/1/1/invented-work",
        expected_available_chapter_count=3,
        status="core",
    )


@pytest.fixture
def chapter_urls() -> list[str]:
    return [
        f"https://www.fanfiction.net/s/1/{index}/invented-work"
        for index in range(1, 4)
    ]


@pytest.fixture
def multi_html() -> bytes:
    return (FIXTURES / "fanfiction-net-multi.html").read_bytes()


@pytest.fixture
def access_denied_html() -> bytes:
    return (FIXTURES / "access-denied.html").read_bytes()


@pytest.fixture
def options(tmp_path: Path) -> CaptureOptions:
    return CaptureOptions(
        output_root=tmp_path / "dataset",
        capture_id="20260723T120000Z",
        requested_delay_seconds=3.0,
    )


def _gateway(
    source: SourceRecord,
    chapter_urls: list[str],
    multi_html: bytes,
    *,
    robots: bytes = ROBOTS,
) -> FakeGateway:
    robots_url = "https://www.fanfiction.net/robots.txt"
    return FakeGateway(
        {
            robots_url: FakeResponse(200, robots),
            **{
                url: FakeResponse(
                    200,
                    multi_html.replace(
                        b"Synthetic chapter text for parser testing.",
                        f"Synthetic chapter {index} text.".encode(),
                    ),
                )
                for index, url in enumerate(chapter_urls, start=1)
            },
        }
    )


def _run(
    source: SourceRecord,
    options: CaptureOptions,
    gateway: FakeGateway,
    sleep: FakeSleep | None = None,
):
    kwargs: dict[str, Any] = {"gateway": gateway}
    if sleep is not None:
        kwargs["sleep"] = sleep
    return asyncio.run(capture_work(source, options, **kwargs))


def test_capture_is_sequential_and_sleeps_between_chapters(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake_sleep = FakeSleep()

    result = _run(source, options, fake, fake_sleep)

    assert fake.max_in_flight == 1
    assert fake_sleep.calls == [pytest.approx(5.0, abs=1.0)] * 2
    assert [page.chapter.chapter_index for page in result.pages] == [1, 2, 3]


def test_policy_snapshots_exist_before_story_navigation(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    policy_root = (
        options.output_root
        / "reports"
        / "policy-snapshots"
        / options.capture_id
    )
    robots_path = policy_root / "robots.txt"
    decision_path = policy_root / "policy-decision.json"
    fake.required_before_story = (robots_path, decision_path)

    result = _run(source, options, fake, FakeSleep())

    assert robots_path.read_bytes() == ROBOTS
    assert json.loads(decision_path.read_text("utf-8")) == result.policy.model_dump(
        mode="json"
    )
    assert fake.calls[0] == "https://www.fanfiction.net/robots.txt"


def test_policy_digest_hashes_exact_persisted_robots_bytes(
    source, options, chapter_urls, multi_html
) -> None:
    robots = (
        "User-agent: *\nAllow: /\n# synthetic café\n"
    ).encode("windows-1252")
    fake = _gateway(source, chapter_urls, multi_html, robots=robots)
    fake.responses["https://www.fanfiction.net/robots.txt"].charset = (
        "windows-1252"
    )

    result = _run(source, options, fake, FakeSleep())

    assert result.policy.robots_sha256 == hashlib.sha256(robots).hexdigest()
    snapshot = (
        options.output_root
        / "reports"
        / "policy-snapshots"
        / options.capture_id
        / "robots.txt"
    )
    assert snapshot.read_bytes() == robots


def test_robots_disallowance_blocks_story_navigation(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(
        source, chapter_urls, multi_html, robots=BLOCKED_ROBOTS
    )

    with pytest.raises(CaptureStopped, match="robots"):
        _run(source, options, fake)

    assert fake.calls == ["https://www.fanfiction.net/robots.txt"]
    policy_root = (
        options.output_root
        / "reports"
        / "policy-snapshots"
        / options.capture_id
    )
    assert (policy_root / "robots.txt").read_bytes() == BLOCKED_ROBOTS
    assert json.loads(
        (policy_root / "policy-decision.json").read_text("utf-8")
    )["allowed"] is False
    diagnostic = json.loads(
        (
            capture_paths(
                options.output_root, source.source_id, options.capture_id
            ).root
            / "diagnostics"
            / "chapter-001.json"
        ).read_text("utf-8")
    )
    assert diagnostic["status"] == 200
    assert diagnostic["failure_signature"] == "robots-disallowed"


@pytest.mark.parametrize(
    ("robots_body", "visible_text", "signature"),
    [
        (
            b"<html><title>CAPTCHA</title></html>",
            "User-agent: *\nAllow: /",
            "captcha",
        ),
        (
            ROBOTS,
            "Checking your browser before accessing Cloudflare",
            "cloudflare",
        ),
        (
            b"<html><h1>Access denied</h1></html>",
            "User-agent: *\nAllow: /",
            "access-denied",
        ),
    ],
)
def test_robots_200_safeguard_pages_stop_before_story_navigation(
    source,
    options,
    chapter_urls,
    multi_html,
    robots_body,
    visible_text,
    signature,
) -> None:
    fake = _gateway(source, chapter_urls, multi_html, robots=robots_body)
    fake.responses["https://www.fanfiction.net/robots.txt"].visible_text = (
        visible_text
    )
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )

    with pytest.raises(CaptureStopped, match=signature):
        _run(source, options, fake)

    assert fake.calls == ["https://www.fanfiction.net/robots.txt"]
    diagnostic = json.loads(
        (paths.root / "diagnostics" / "chapter-001.json").read_text("utf-8")
    )
    assert diagnostic["status"] == 200
    assert diagnostic["failure_signature"] == signature


@pytest.mark.parametrize(
    ("robots_response", "signature"),
    [
        (FakeResponse(503, b"synthetic unavailable"), "robots-http-503"),
        (
            FakeResponse(
                200,
                ROBOTS,
                final_url="https://www.fanfiction.net/challenge",
            ),
            "robots-unexpected-final-url",
        ),
    ],
)
def test_robots_transport_stops_write_chapter_one_diagnostic(
    source,
    options,
    chapter_urls,
    multi_html,
    robots_response,
    signature,
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses["https://www.fanfiction.net/robots.txt"] = robots_response
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )

    with pytest.raises(CaptureStopped):
        _run(source, options, fake)

    diagnostic = json.loads(
        (paths.root / "diagnostics" / "chapter-001.json").read_text("utf-8")
    )
    assert diagnostic["url"] == "https://www.fanfiction.net/robots.txt"
    assert diagnostic["status"] == robots_response.status
    assert diagnostic["failure_signature"] == signature
    assert fake.calls == ["https://www.fanfiction.net/robots.txt"]


def test_dry_run_robots_failure_preserves_no_write_contract(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses["https://www.fanfiction.net/robots.txt"] = FakeResponse(
        503, b"synthetic unavailable"
    )

    with pytest.raises(CaptureStopped):
        _run(source, options.model_copy(update={"dry_run": True}), fake)

    assert not options.output_root.exists()


def test_dry_run_does_not_create_capture_directory(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)

    result = _run(
        source, options.model_copy(update={"dry_run": True}), fake
    )

    assert result.discovery.chapters
    assert result.pages == []
    assert not options.output_root.exists()
    assert fake.calls == [
        "https://www.fanfiction.net/robots.txt",
        chapter_urls[0],
    ]


def test_access_denial_writes_diagnostic_and_stops(
    source, options, chapter_urls, multi_html, access_denied_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses[chapter_urls[1]] = FakeResponse(403, access_denied_html)
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )

    with pytest.raises(CaptureStopped, match="chapter 2"):
        _run(source, options, fake, FakeSleep())

    diagnostic_path = paths.root / "diagnostics" / "chapter-002.json"
    diagnostic = json.loads(diagnostic_path.read_text("utf-8"))
    assert diagnostic["status"] == 403
    assert diagnostic["failure_signature"] == "http-403-access-denied"
    assert Path(diagnostic["screenshot_path"]).exists()
    assert not paths.chapter("raw", 3, ".html").exists()
    assert fake.calls.count(chapter_urls[1]) == 1


def test_capture_preserves_raw_response_bytes_and_records_charset(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    encoded = (
        multi_html.decode("utf-8")
        .replace(
            "Synthetic paragraph for parser testing.",
            "Synthetic chapter with café.",
        )
        .replace(
            '<meta charset="utf-8">',
            '<meta charset="windows-1252">',
        )
        .encode("windows-1252")
    )
    fake.responses[chapter_urls[0]] = FakeResponse(
        200, encoded, charset="windows-1252"
    )
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )

    _run(source, options, fake, FakeSleep())

    assert paths.chapter("raw", 1, ".html").read_bytes() == encoded
    metadata = json.loads((paths.root / "metadata.json").read_text("utf-8"))
    assert metadata["charset_decisions"]["1"] == {
        "declared": "windows-1252",
        "used": "windows-1252",
        "fallback": False,
    }


def test_missing_story_content_writes_diagnostic_without_raw_artifact(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses[chapter_urls[1]] = FakeResponse(
        200,
        multi_html,
        selector_results={"#storytext": False, "div.storytext": False},
    )
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )

    with pytest.raises(CaptureStopped, match="chapter 2"):
        _run(source, options, fake, FakeSleep())

    diagnostic = json.loads(
        (paths.root / "diagnostics" / "chapter-002.json").read_text("utf-8")
    )
    assert diagnostic["failure_signature"] == "missing-story-content"
    assert not paths.chapter("raw", 2, ".html").exists()


def test_discovery_inventory_failure_writes_chapter_one_diagnostic(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    source = source.model_copy(
        update={"expected_available_chapter_count": 4}
    )
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )

    with pytest.raises(CaptureStopped, match="inventory"):
        _run(source, options, fake, FakeSleep())

    diagnostic = json.loads(
        (paths.root / "diagnostics" / "chapter-001.json").read_text("utf-8")
    )
    assert diagnostic["failure_signature"] == "chapter-inventory-mismatch"
    assert not paths.chapter("raw", 1, ".html").exists()


def test_discovery_extraction_failure_is_diagnostic_stop(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses[chapter_urls[0]] = FakeResponse(
        200, multi_html.replace(b"id: 1", b"id: synthetic")
    )
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )

    with pytest.raises(CaptureStopped, match="discovery"):
        _run(source, options, fake, FakeSleep())

    diagnostic = json.loads(
        (paths.root / "diagnostics" / "chapter-001.json").read_text("utf-8")
    )
    assert diagnostic["failure_signature"] == "discovery-failed"
    assert not paths.chapter("raw", 1, ".html").exists()


@pytest.mark.parametrize(
    ("status", "visible_text", "signature"),
    [
        (429, "", "http-429-rate-limited"),
        (200, "Please complete the CAPTCHA", "captcha"),
        (200, "Checking your browser before accessing Cloudflare", "cloudflare"),
    ],
)
def test_non_retryable_access_failures_stop_after_one_attempt(
    source,
    options,
    chapter_urls,
    multi_html,
    status,
    visible_text,
    signature,
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses[chapter_urls[1]] = FakeResponse(
        status, multi_html, visible_text=visible_text
    )
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )

    with pytest.raises(CaptureStopped):
        _run(source, options, fake, FakeSleep())

    diagnostic = json.loads(
        (paths.root / "diagnostics" / "chapter-002.json").read_text("utf-8")
    )
    assert diagnostic["failure_signature"] == signature
    assert fake.calls.count(chapter_urls[1]) == 1


def test_connection_failures_get_only_two_backoff_retries(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses[chapter_urls[0]] = [
        TimeoutError("synthetic timeout"),
        ConnectionResetError("synthetic reset"),
        FakeResponse(200, multi_html),
    ]
    fake_sleep = FakeSleep()

    result = _run(source, options, fake, fake_sleep)

    assert len(result.pages) == 3
    assert fake.calls.count(chapter_urls[0]) == 3
    assert fake_sleep.calls[:2] == [2.0, 4.0]


def test_run_state_is_atomic_and_updated_after_each_chapter(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )

    _run(source, options, fake, FakeSleep())

    state = json.loads((paths.root / "run-state.json").read_text("utf-8"))
    assert state["completed_chapters"] == [1, 2, 3]
    assert state["status"] == "complete"
    assert not list(options.output_root.rglob("*.tmp"))


def test_capture_rejects_symlinked_capture_root_before_network_or_writes(
    tmp_path, source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    external_root = tmp_path / "external-capture"
    external_root.mkdir()
    paths.root.parent.mkdir(parents=True)
    paths.root.symlink_to(external_root, target_is_directory=True)

    with pytest.raises(CaptureStopped, match="symlink"):
        _run(
            source,
            options.model_copy(update={"resume": True}),
            fake,
            FakeSleep(),
        )

    assert fake.calls == []
    assert list(external_root.iterdir()) == []


def test_capture_rejects_symlinked_raw_parent_without_external_write(
    monkeypatch, tmp_path, source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    external_raw = tmp_path / "external-raw"
    external_raw.mkdir()
    original = browser_module._atomic_write_json

    def install_raw_symlink(path, value):
        original(path, value)
        raw_root = paths.root / "raw"
        if path == paths.root / "metadata.json" and not raw_root.exists():
            raw_root.symlink_to(external_raw, target_is_directory=True)

    monkeypatch.setattr(
        browser_module, "_atomic_write_json", install_raw_symlink
    )

    with pytest.raises(CaptureStopped, match="symlink"):
        _run(source, options, fake, FakeSleep())

    assert list(external_raw.iterdir()) == []


def test_capture_rejects_html_temp_symlink_without_overwriting_target(
    monkeypatch, tmp_path, source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    external_target = tmp_path / "older-capture.html"
    external_target.write_bytes(b"preserve older capture")
    original = browser_module._atomic_write_json
    installed = False

    def install_html_temp_symlink(path, value):
        nonlocal installed
        original(path, value)
        raw_root = paths.root / "raw"
        temporary = raw_root / "chapter-001.html.tmp"
        if path == paths.root / "metadata.json" and not installed:
            raw_root.mkdir()
            temporary.symlink_to(external_target)
            installed = True

    monkeypatch.setattr(
        browser_module, "_atomic_write_json", install_html_temp_symlink
    )

    with pytest.raises(CaptureStopped, match="temporary|symlink"):
        _run(source, options, fake, FakeSleep())

    assert external_target.read_bytes() == b"preserve older capture"
    assert (paths.root / "raw" / "chapter-001.html.tmp").is_symlink()


def test_capture_rejects_json_temp_symlink_without_overwriting_target(
    tmp_path, source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    policy_root = (
        options.output_root
        / "reports"
        / "policy-snapshots"
        / options.capture_id
    )
    policy_root.mkdir(parents=True)
    external_target = tmp_path / "older-policy.json"
    external_target.write_bytes(b'{"preserve": true}\n')
    temporary = policy_root / "policy-decision.json.tmp"
    temporary.symlink_to(external_target)

    with pytest.raises(CaptureStopped, match="temporary|symlink"):
        _run(source, options, fake, FakeSleep())

    assert external_target.read_bytes() == b'{"preserve": true}\n'
    assert temporary.is_symlink()
    assert fake.calls == ["https://www.fanfiction.net/robots.txt"]


def test_authoritative_state_is_initialized_before_derived_metadata(
    monkeypatch, source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    writes = []
    original = browser_module._atomic_write_json

    def recording_write(path, value):
        if path.parent == paths.root:
            writes.append(path.name)
        original(path, value)

    monkeypatch.setattr(browser_module, "_atomic_write_json", recording_write)

    _run(source, options, fake, FakeSleep())

    assert writes[:2] == ["run-state.json", "metadata.json"]


def test_resume_refuses_raw_artifact_not_recorded_in_authoritative_state(
    monkeypatch, source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    original = browser_module._atomic_write_json

    def crash_before_first_completion(path, value):
        if (
            path == paths.root / "run-state.json"
            and value.get("completed_chapters") == [1]
        ):
            raise RuntimeError("synthetic crash before state completion")
        original(path, value)

    monkeypatch.setattr(
        browser_module, "_atomic_write_json", crash_before_first_completion
    )
    with pytest.raises(RuntimeError, match="synthetic crash"):
        _run(source, options, fake, FakeSleep())
    monkeypatch.setattr(browser_module, "_atomic_write_json", original)
    assert paths.chapter("raw", 1, ".html").exists()
    fake.calls.clear()

    with pytest.raises(CaptureStopped, match="unrecorded raw artifact"):
        _run(
            source,
            options.model_copy(update={"resume": True}),
            fake,
            FakeSleep(),
        )

    assert fake.calls == []


def test_dry_run_resume_never_repairs_or_captures_existing_state(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses[chapter_urls[1]] = [
        TimeoutError("synthetic timeout"),
        TimeoutError("synthetic timeout"),
        TimeoutError("synthetic timeout"),
    ]
    with pytest.raises(CaptureStopped, match="network-timeout"):
        _run(source, options, fake, FakeSleep())
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    metadata_path = paths.root / "metadata.json"
    metadata_path.write_bytes(b'{"synthetic": "do not repair"}\n')
    before = {
        path.relative_to(options.output_root): path.read_bytes()
        for path in options.output_root.rglob("*")
        if path.is_file()
    }
    fake.responses[chapter_urls[1]] = FakeResponse(200, multi_html)
    fake.calls.clear()

    result = _run(
        source,
        options.model_copy(update={"resume": True, "dry_run": True}),
        fake,
        FakeSleep(),
    )

    after = {
        path.relative_to(options.output_root): path.read_bytes()
        for path in options.output_root.rglob("*")
        if path.is_file()
    }
    assert result.discovery.chapters
    assert result.pages == []
    assert result.paths is None
    assert fake.calls == ["https://www.fanfiction.net/robots.txt"]
    assert after == before
    assert not paths.chapter("raw", 2, ".html").exists()


def test_resume_never_refetches_completed_chapter(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake_sleep = FakeSleep()

    first = _run(source, options, fake, fake_sleep)
    fake.calls.clear()
    second = _run(
        source, options.model_copy(update={"resume": True}), fake
    )

    assert fake.calls == []
    assert second.discovery == first.discovery
    assert second.pages == first.pages


@pytest.mark.parametrize(
    "snapshot_change",
    [
        "missing-robots",
        "missing-decision",
        "modified-robots",
        "noncanonical-decision",
    ],
)
def test_complete_resume_rejects_missing_or_modified_policy_snapshot_before_gateway(
    monkeypatch,
    source,
    options,
    chapter_urls,
    multi_html,
    snapshot_change,
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    _run(source, options, fake, FakeSleep())
    policy_root = (
        options.output_root
        / "reports"
        / "policy-snapshots"
        / options.capture_id
    )
    robots_path = policy_root / "robots.txt"
    decision_path = policy_root / "policy-decision.json"
    if snapshot_change == "missing-robots":
        robots_path.unlink()
    elif snapshot_change == "missing-decision":
        decision_path.unlink()
    elif snapshot_change == "modified-robots":
        robots_path.write_bytes(ROBOTS + b"# modified\n")
    else:
        decision = json.loads(decision_path.read_text("utf-8"))
        decision_path.write_text(json.dumps(decision), encoding="utf-8")
    fake.calls.clear()

    def unexpected_gateway_creation(*, headed):
        del headed
        raise AssertionError("gateway was created")

    monkeypatch.setattr(
        browser_module, "_PlaywrightGateway", unexpected_gateway_creation
    )

    with pytest.raises(CaptureStopped, match="persisted policy snapshot"):
        asyncio.run(
            capture_work(
                source,
                options.model_copy(update={"resume": True}),
            )
        )

    assert fake.calls == []


def test_resume_rejects_non_prefix_completed_inventory_before_gateway_creation(
    monkeypatch,
    source,
    options,
    chapter_urls,
    multi_html,
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    _run(source, options, fake, FakeSleep())
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    state_path = paths.root / "run-state.json"
    state = json.loads(state_path.read_text("utf-8"))
    state["status"] = "running"
    state["completed_chapters"] = [1, 3]
    state["pages"] = [state["pages"][0], state["pages"][2]]
    state["charset_decisions"].pop("2")
    state_path.write_text(json.dumps(state), encoding="utf-8")
    paths.chapter("raw", 2, ".html").unlink()
    fake.calls.clear()

    def unexpected_gateway_creation(*, headed):
        del headed
        raise AssertionError("gateway was created")

    monkeypatch.setattr(
        browser_module, "_PlaywrightGateway", unexpected_gateway_creation
    )

    with pytest.raises(CaptureStopped, match="exact discovery prefix"):
        asyncio.run(
            capture_work(
                source,
                options.model_copy(update={"resume": True}),
            )
        )

    assert fake.calls == []


def test_resume_repairs_derived_metadata_from_authoritative_state(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    first = _run(source, options, fake, FakeSleep())
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    metadata_path = paths.root / "metadata.json"
    metadata = json.loads(metadata_path.read_text("utf-8"))
    metadata["pages"] = []
    metadata["charset_decisions"] = {}
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    fake.calls.clear()

    resumed = _run(
        source, options.model_copy(update={"resume": True}), fake
    )

    assert fake.calls == []
    assert resumed.pages == first.pages
    repaired = json.loads(metadata_path.read_text("utf-8"))
    assert len(repaired["pages"]) == 3
    assert set(repaired["charset_decisions"]) == {"1", "2", "3"}


def test_resume_rejects_non_retryable_diagnostic_only_chapter_one_state(
    monkeypatch, source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses[chapter_urls[0]] = FakeResponse(
        200, multi_html.replace(b"id: 1", b"id: synthetic")
    )
    with pytest.raises(CaptureStopped, match="discovery"):
        _run(source, options, fake, FakeSleep())
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    assert (paths.root / "diagnostics" / "chapter-001.json").exists()

    def unexpected_gateway_creation(*, headed):
        del headed
        raise AssertionError("gateway was created")

    monkeypatch.setattr(
        browser_module, "_PlaywrightGateway", unexpected_gateway_creation
    )

    with pytest.raises(CaptureStopped, match="non-retryable"):
        asyncio.run(
            capture_work(
                source,
                options.model_copy(update={"resume": True}),
            )
        )


@pytest.mark.parametrize("failure_chapter", [1, 2])
@pytest.mark.parametrize(
    ("status", "visible_text", "signature"),
    [
        (403, None, "http-403-access-denied"),
        (429, None, "http-429-rate-limited"),
        (500, None, "http-500"),
        (200, "Please complete the CAPTCHA", "captcha"),
        (200, "Checking your browser", "challenge"),
        (200, "Cloudflare access check", "cloudflare"),
        (200, "Access denied", "access-denied"),
    ],
)
def test_resume_rejects_recorded_non_retryable_stop_before_gateway_creation(
    monkeypatch,
    source,
    options,
    chapter_urls,
    multi_html,
    failure_chapter,
    status,
    visible_text,
    signature,
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses[chapter_urls[failure_chapter - 1]] = FakeResponse(
        status,
        multi_html,
        visible_text=visible_text,
    )
    with pytest.raises(CaptureStopped, match=signature):
        _run(source, options, fake, FakeSleep())

    def unexpected_gateway_creation(*, headed):
        del headed
        raise AssertionError("gateway was created")

    monkeypatch.setattr(
        browser_module, "_PlaywrightGateway", unexpected_gateway_creation
    )

    with pytest.raises(CaptureStopped, match="non-retryable"):
        asyncio.run(
            capture_work(
                source,
                options.model_copy(update={"resume": True}),
            )
        )


@pytest.mark.parametrize("failure_chapter", [1, 2])
def test_resume_preserves_retryable_network_interruption_recovery(
    source,
    options,
    chapter_urls,
    multi_html,
    failure_chapter,
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    failed_url = chapter_urls[failure_chapter - 1]
    fake.responses[failed_url] = [
        TimeoutError("synthetic timeout"),
        ConnectionResetError("synthetic reset"),
        TimeoutError("synthetic timeout"),
    ]
    with pytest.raises(CaptureStopped, match="network-timeout"):
        _run(source, options, fake, FakeSleep())

    fake.responses[failed_url] = FakeResponse(200, multi_html)
    fake.calls.clear()

    result = _run(
        source,
        options.model_copy(update={"resume": True}),
        fake,
        FakeSleep(),
    )

    assert [page.chapter.chapter_index for page in result.pages] == [1, 2, 3]
    assert fake.calls == [
        "https://www.fanfiction.net/robots.txt",
        *chapter_urls[failure_chapter - 1 :],
    ]


def test_partial_resume_refuses_changed_robots_without_overwriting_snapshot(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses[chapter_urls[1]] = [
        TimeoutError("synthetic timeout"),
        TimeoutError("synthetic timeout"),
        TimeoutError("synthetic timeout"),
    ]
    with pytest.raises(CaptureStopped, match="network-timeout"):
        _run(source, options, fake, FakeSleep())
    policy_root = (
        options.output_root
        / "reports"
        / "policy-snapshots"
        / options.capture_id
    )
    original_decision = (policy_root / "policy-decision.json").read_bytes()
    changed_robots = b"User-agent: *\nAllow: /\nCrawl-delay: 7\n"
    fake.responses["https://www.fanfiction.net/robots.txt"] = FakeResponse(
        200, changed_robots
    )
    fake.calls.clear()

    with pytest.raises(CaptureStopped, match="policy changed"):
        _run(
            source,
            options.model_copy(update={"resume": True}),
            fake,
            FakeSleep(),
        )

    assert fake.calls == ["https://www.fanfiction.net/robots.txt"]
    assert (policy_root / "robots.txt").read_bytes() == ROBOTS
    assert (policy_root / "policy-decision.json").read_bytes() == original_decision
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    diagnostic = json.loads(
        (paths.root / "diagnostics" / "chapter-001.json").read_text("utf-8")
    )
    assert diagnostic["status"] == 200
    assert diagnostic["failure_signature"] == "policy-changed"


def test_resume_compares_policy_to_state_when_snapshots_are_missing(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses[chapter_urls[1]] = [
        TimeoutError("synthetic timeout"),
        TimeoutError("synthetic timeout"),
        TimeoutError("synthetic timeout"),
    ]
    with pytest.raises(CaptureStopped, match="network-timeout"):
        _run(source, options, fake, FakeSleep())
    policy_root = (
        options.output_root
        / "reports"
        / "policy-snapshots"
        / options.capture_id
    )
    (policy_root / "robots.txt").unlink()
    (policy_root / "policy-decision.json").unlink()
    fake.responses["https://www.fanfiction.net/robots.txt"] = FakeResponse(
        200, b"User-agent: *\nAllow: /\nCrawl-delay: 9\n"
    )
    fake.calls.clear()

    with pytest.raises(CaptureStopped, match="policy changed"):
        _run(
            source,
            options.model_copy(update={"resume": True}),
            fake,
            FakeSleep(),
        )

    assert fake.calls == ["https://www.fanfiction.net/robots.txt"]
    assert not (policy_root / "robots.txt").exists()
    assert not (policy_root / "policy-decision.json").exists()


def test_resume_rejects_same_id_source_registry_changes(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    _run(source, options, fake, FakeSleep())
    changed_source = source.model_copy(
        update={"work_title": "Changed Registry Title"}
    )
    fake.calls.clear()

    with pytest.raises(CaptureStopped, match="source record changed"):
        _run(
            changed_source,
            options.model_copy(update={"resume": True}),
            fake,
        )

    assert fake.calls == []


@pytest.mark.parametrize(
    "corrupt_url",
    [
        "https://evil.example/s/1/2/invented-work",
        "https://www.fanfiction.net/s/999/2/invented-work",
        "https://www.fanfiction.net/s/1/3/invented-work",
    ],
)
def test_resume_rejects_corrupt_discovery_before_gateway_creation(
    monkeypatch,
    source,
    options,
    chapter_urls,
    multi_html,
    access_denied_html,
    corrupt_url,
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    fake.responses[chapter_urls[1]] = FakeResponse(403, access_denied_html)
    with pytest.raises(CaptureStopped, match="chapter 2"):
        _run(source, options, fake, FakeSleep())
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    state_path = paths.root / "run-state.json"
    state = json.loads(state_path.read_text("utf-8"))
    state["discovery"]["chapters"][1]["chapter_url"] = corrupt_url
    state_path.write_text(json.dumps(state), encoding="utf-8")

    def unexpected_gateway_creation(*, headed):
        del headed
        raise AssertionError("gateway was created")

    monkeypatch.setattr(
        browser_module, "_PlaywrightGateway", unexpected_gateway_creation
    )

    with pytest.raises(CaptureStopped, match="discovery"):
        asyncio.run(
            capture_work(
                source,
                options.model_copy(update={"resume": True}),
            )
        )


def test_existing_capture_requires_explicit_resume(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    _run(source, options, fake, FakeSleep())
    fake.calls.clear()

    with pytest.raises(CaptureStopped, match="already exists"):
        _run(source, options, fake)

    assert fake.calls == []


@pytest.mark.parametrize(
    "work_url",
    [
        "https://fanfiction.net/s/1/1/invented-work",
        "https://www.fanfiction.net.evil.example/s/1/1/invented-work",
        "https://www.fanfiction.net:444/s/1/1/invented-work",
        "https://www.fanfiction.net/u/1/synthetic-author",
        "https://www.fanfiction.net/s/not-numeric/1/invented-work",
    ],
)
def test_unsupported_source_boundary_is_rejected_before_gateway_call(
    source, options, chapter_urls, multi_html, work_url
) -> None:
    invalid_source = SourceRecord.model_validate(
        {**source.model_dump(mode="json"), "work_url": work_url}
    )
    fake = _gateway(source, chapter_urls, multi_html)

    with pytest.raises(CaptureStopped, match="unsupported source URL"):
        _run(invalid_source, options, fake)

    assert fake.calls == []
    assert not options.output_root.exists()


def test_non_resume_policy_snapshot_collision_is_immutable(
    source, options, chapter_urls, multi_html
) -> None:
    fake = _gateway(source, chapter_urls, multi_html)
    policy_root = (
        options.output_root
        / "reports"
        / "policy-snapshots"
        / options.capture_id
    )
    policy_root.mkdir(parents=True)
    robots_path = policy_root / "robots.txt"
    decision_path = policy_root / "policy-decision.json"
    robots_path.write_bytes(b"preexisting synthetic evidence")
    decision_path.write_bytes(b'{"preexisting": true}\n')

    with pytest.raises(CaptureStopped, match="snapshot collision"):
        _run(source, options, fake, FakeSleep())

    assert fake.calls == ["https://www.fanfiction.net/robots.txt"]
    assert robots_path.read_bytes() == b"preexisting synthetic evidence"
    assert decision_path.read_bytes() == b'{"preexisting": true}\n'
    assert not any(call in chapter_urls for call in fake.calls)
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    diagnostic = json.loads(
        (paths.root / "diagnostics" / "chapter-001.json").read_text("utf-8")
    )
    assert diagnostic["status"] == 200
    assert diagnostic["failure_signature"] == "policy-snapshot-collision"


def test_playwright_close_attempts_every_owned_layer_after_failure() -> None:
    events = []

    class FailingContext:
        async def close(self):
            events.append("context")
            raise RuntimeError("context close failed")

    class FakeBrowser:
        async def close(self):
            events.append("browser")

    class FakePlaywright:
        async def stop(self):
            events.append("playwright")

    gateway = browser_module._PlaywrightGateway(headed=False)
    gateway._context = FailingContext()
    gateway._browser = FakeBrowser()
    gateway._playwright = FakePlaywright()

    with pytest.raises(RuntimeError, match="context close failed"):
        asyncio.run(gateway.close())

    assert events == ["context", "browser", "playwright"]


def test_playwright_gateway_forces_png_for_temporary_screenshot_path(
    tmp_path,
) -> None:
    calls = []

    class FakePage:
        async def screenshot(self, **kwargs):
            calls.append(kwargs)

    gateway = browser_module._PlaywrightGateway(headed=False)
    gateway._page = FakePage()
    temporary = tmp_path / "chapter-001.png.tmp"

    asyncio.run(gateway.screenshot(temporary))

    assert calls == [
        {
            "path": str(temporary),
            "full_page": True,
            "type": "png",
        }
    ]


def test_owned_gateway_close_error_does_not_replace_capture_stop(
    monkeypatch, source, options
) -> None:
    class FailingOwnedGateway:
        async def fetch(self, url, **kwargs):
            del url, kwargs
            raise TimeoutError("synthetic robots timeout")

        async def close(self):
            raise RuntimeError("synthetic close failure")

    monkeypatch.setattr(
        browser_module,
        "_PlaywrightGateway",
        lambda *, headed: FailingOwnedGateway(),
    )

    with pytest.raises(CaptureStopped, match="robots fetch failed"):
        asyncio.run(capture_work(source, options))


def test_browser_is_the_only_playwright_import_boundary() -> None:
    scripts_root = Path(__file__).parents[2] / "scripts" / "fanfic_dataset"
    importers = []
    for path in scripts_root.rglob("*.py"):
        tree = ast.parse(path.read_text("utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "playwright.async_api":
                importers.append(path.name)
            if isinstance(node, ast.Import) and any(
                name.name == "playwright.async_api" for name in node.names
            ):
                importers.append(path.name)

    assert importers == ["browser.py"]
