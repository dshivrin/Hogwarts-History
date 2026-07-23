from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re
from typing import Awaitable, Callable, Protocol
from urllib.parse import urlsplit, urlunsplit

from playwright.async_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)
from pydantic import Field

from .discover import adapter_for
from .fanfiction_net import ExtractionError, STORY_SELECTORS
from .models import (
    CapturedPage,
    ChapterRef,
    SourceRecord,
    StrictModel,
    WorkDiscovery,
)
from .paths import CapturePaths, capture_paths
from .policy import PolicyDecision, evaluate_policy


Sleep = Callable[[float], Awaitable[None]]
_RETRY_BACKOFF_SECONDS = (2.0, 4.0)
_STORY_TIMEOUT_SECONDS = 30.0


class CaptureOptions(StrictModel):
    output_root: Path
    capture_id: str = Field(pattern=r"^\d{8}T\d{6}Z$")
    requested_delay_seconds: float = Field(default=5.0, ge=0)
    dry_run: bool = False
    resume: bool = False
    headed: bool = False


@dataclass(frozen=True)
class CaptureResult:
    discovery: WorkDiscovery
    policy: PolicyDecision
    pages: list[CapturedPage]
    paths: CapturePaths | None


class BrowserResponse(Protocol):
    status: int
    body: bytes
    final_url: str
    charset: str | None
    visible_text: str
    selector_results: dict[str, bool]


class BrowserGateway(Protocol):
    async def fetch(
        self,
        url: str,
        *,
        story_selectors: tuple[str, ...] = (),
        timeout_seconds: float = _STORY_TIMEOUT_SECONDS,
    ) -> BrowserResponse:
        """Return the raw main-document response and rendered-page checks."""

    async def screenshot(self, path: Path) -> None:
        """Capture the current rendered page to an ignored diagnostic path."""


class CaptureStopped(RuntimeError):
    """Raised when capture cannot continue safely."""


@dataclass(frozen=True)
class _GatewayResponse:
    status: int
    body: bytes
    final_url: str
    charset: str | None
    visible_text: str
    selector_results: dict[str, bool]


@dataclass(frozen=True)
class _CharsetDecision:
    declared: str | None
    used: str
    fallback: bool

    def as_dict(self) -> dict[str, str | bool | None]:
        return {
            "declared": self.declared,
            "used": self.used,
            "fallback": self.fallback,
        }


class _RetryExhausted(RuntimeError):
    def __init__(self, signature: str, detail: str) -> None:
        super().__init__(detail)
        self.signature = signature
        self.detail = detail


class _PlaywrightGateway:
    """Own exactly one unauthenticated browser context for one capture run."""

    def __init__(self, *, headed: bool) -> None:
        self._headed = headed
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    async def _start(self) -> None:
        if self._page is not None:
            return
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=not self._headed
        )
        # Passing no options keeps the browser's default user agent and creates
        # a clean context without cookies or storage state.
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()

    async def fetch(
        self,
        url: str,
        *,
        story_selectors: tuple[str, ...] = (),
        timeout_seconds: float = _STORY_TIMEOUT_SECONDS,
    ) -> _GatewayResponse:
        await self._start()
        assert self._page is not None
        try:
            main_response = await self._page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=int(timeout_seconds * 1000),
            )
        except PlaywrightTimeoutError as error:
            raise TimeoutError(str(error)) from error
        except PlaywrightError as error:
            if "ERR_CONNECTION_RESET" in str(error).upper():
                raise ConnectionResetError(str(error)) from error
            raise
        if main_response is None:
            raise PlaywrightError("navigation returned no main-document response")

        body = await main_response.body()
        selector_results = {
            selector: False for selector in story_selectors
        }
        if story_selectors and 200 <= main_response.status < 300:
            combined = self._page.locator(", ".join(story_selectors)).first
            try:
                await combined.wait_for(
                    state="attached", timeout=int(timeout_seconds * 1000)
                )
            except PlaywrightTimeoutError:
                pass
            for selector in story_selectors:
                locator = self._page.locator(selector)
                if await locator.count():
                    selector_results[selector] = bool(
                        (await locator.first.inner_text()).strip()
                    )

        body_locator = self._page.locator("body")
        visible_text = (
            await body_locator.inner_text() if await body_locator.count() else ""
        )
        return _GatewayResponse(
            status=main_response.status,
            body=body,
            final_url=self._page.url,
            charset=_response_charset(main_response.headers),
            visible_text=visible_text,
            selector_results=selector_results,
        )

    async def screenshot(self, path: Path) -> None:
        await self._start()
        assert self._page is not None
        path.parent.mkdir(parents=True, exist_ok=True)
        await self._page.screenshot(path=str(path), full_page=True)

    async def close(self) -> None:
        first_error: BaseException | None = None
        operations = (
            self._context.close if self._context is not None else None,
            self._browser.close if self._browser is not None else None,
            self._playwright.stop if self._playwright is not None else None,
        )
        for operation in operations:
            if operation is None:
                continue
            try:
                await operation()
            except BaseException as error:
                if first_error is None:
                    first_error = error
        if first_error is not None:
            raise first_error


async def capture_work(
    source: SourceRecord,
    options: CaptureOptions,
    *,
    gateway: BrowserGateway | None = None,
    sleep: Sleep = asyncio.sleep,
) -> CaptureResult:
    _validate_source_boundary(source)
    paths = capture_paths(
        options.output_root, source.source_id, options.capture_id
    )
    preexisting_root = paths.root.exists()
    resumed = _load_existing_capture(source, options, paths)
    if (
        resumed is not None
        and resumed[2] == "complete"
        and not options.dry_run
    ):
        discovery, pages, _ = resumed
        metadata = _read_json(paths.root / "metadata.json")
        return CaptureResult(
            discovery=discovery,
            policy=PolicyDecision.model_validate(metadata["policy"]),
            pages=pages,
            paths=paths,
        )

    owns_gateway = gateway is None
    active_gateway: BrowserGateway = gateway or _PlaywrightGateway(
        headed=options.headed
    )
    primary_error: BaseException | None = None
    try:
        robots_url = _robots_url(source)
        try:
            robots_response = await _fetch_robots(active_gateway, robots_url)
        except _RetryExhausted as error:
            if not options.dry_run:
                await _write_diagnostic(
                    gateway=active_gateway,
                    paths=paths,
                    chapter_index=1,
                    url=robots_url,
                    status=None,
                    selector_results={},
                    failure_signature=error.signature,
                    detail=error.detail,
                )
            raise CaptureStopped(
                f"robots fetch failed: {error.detail}"
            ) from error
        robots_text, _ = _decode_response(
            robots_response.body, robots_response.charset
        )
        robots_failure = _robots_failure(
            robots_response,
            expected_url=robots_url,
            decoded_body=robots_text,
        )
        if robots_failure is not None:
            if not options.dry_run:
                await _write_diagnostic(
                    gateway=active_gateway,
                    paths=paths,
                    chapter_index=1,
                    url=robots_url,
                    status=robots_response.status,
                    selector_results=robots_response.selector_results,
                    failure_signature=robots_failure,
                    detail=(
                        f"final URL: {robots_response.final_url}"
                        if robots_failure == "robots-unexpected-final-url"
                        else None
                    ),
                )
            raise CaptureStopped(
                f"robots access check failed: {robots_failure}"
            )
        policy = evaluate_policy(
            str(source.work_url),
            robots_text,
            options.requested_delay_seconds,
        ).model_copy(
            update={
                "robots_sha256": hashlib.sha256(
                    robots_response.body
                ).hexdigest()
            }
        )
        if resumed is not None:
            stored_policy = PolicyDecision.model_validate(
                _read_json(paths.root / "run-state.json")["policy"]
            )
            if policy != stored_policy:
                if not options.dry_run:
                    await _write_diagnostic(
                        gateway=active_gateway,
                        paths=paths,
                        chapter_index=1,
                        url=robots_url,
                        status=robots_response.status,
                        selector_results=robots_response.selector_results,
                        failure_signature="policy-changed",
                        detail=(
                            "current robots response and decision do not "
                            "match authoritative capture state"
                        ),
                    )
                raise CaptureStopped(
                    "capture policy changed during resume; "
                    "use a new capture_id"
                )
        if not options.dry_run:
            try:
                _persist_or_validate_policy_snapshot(
                    options, robots_response.body, policy
                )
            except CaptureStopped as error:
                await _write_diagnostic(
                    gateway=active_gateway,
                    paths=paths,
                    chapter_index=1,
                    url=robots_url,
                    status=robots_response.status,
                    selector_results=robots_response.selector_results,
                    failure_signature=(
                        "policy-changed"
                        if options.resume
                        else "policy-snapshot-collision"
                    ),
                    detail=str(error),
                )
                raise
        if not policy.allowed:
            if not options.dry_run:
                await _write_diagnostic(
                    gateway=active_gateway,
                    paths=paths,
                    chapter_index=1,
                    url=robots_url,
                    status=robots_response.status,
                    selector_results=robots_response.selector_results,
                    failure_signature="robots-disallowed",
                    detail=policy.reason,
                )
            raise CaptureStopped(f"robots policy blocked capture: {policy.reason}")

        if resumed is not None:
            discovery, pages, _ = resumed
            if options.dry_run:
                return CaptureResult(
                    discovery=discovery,
                    policy=policy,
                    pages=[],
                    paths=None,
                )
            return await _capture_remaining(
                source=source,
                options=options,
                paths=paths,
                discovery=discovery,
                policy=policy,
                pages=pages,
                gateway=active_gateway,
                sleep=sleep,
                first_response=None,
            )

        first_url = str(source.work_url)
        try:
            first_response = await _fetch_with_retries(
                active_gateway,
                first_url,
                story_selectors=STORY_SELECTORS,
                sleep=sleep,
            )
        except _RetryExhausted as error:
            if not options.dry_run:
                await _write_diagnostic(
                    gateway=active_gateway,
                    paths=paths,
                    chapter_index=1,
                    url=first_url,
                    status=None,
                    selector_results={},
                    failure_signature=error.signature,
                    detail=error.detail,
                )
            raise CaptureStopped(
                f"capture stopped at chapter 1: {error.signature}"
            ) from error

        first_text, _ = _decode_response(
            first_response.body, first_response.charset
        )
        failure = _chapter_failure(
            first_response, expected_url=first_url, decoded_body=first_text
        )
        if failure is not None:
            if not options.dry_run:
                await _write_diagnostic(
                    gateway=active_gateway,
                    paths=paths,
                    chapter_index=1,
                    url=first_url,
                    status=first_response.status,
                    selector_results=first_response.selector_results,
                    failure_signature=failure,
                )
            raise CaptureStopped(f"capture stopped at chapter 1: {failure}")

        try:
            discovery = adapter_for(source).discover(
                first_text, first_url, source
            )
        except ExtractionError as error:
            if not options.dry_run:
                await _write_diagnostic(
                    gateway=active_gateway,
                    paths=paths,
                    chapter_index=1,
                    url=first_url,
                    status=first_response.status,
                    selector_results=first_response.selector_results,
                    failure_signature="discovery-failed",
                    detail=str(error),
                )
            raise CaptureStopped(
                f"chapter 1 discovery failed: {error}"
            ) from error
        try:
            _validate_discovery_inventory(source, discovery)
        except CaptureStopped as error:
            if not options.dry_run:
                await _write_diagnostic(
                    gateway=active_gateway,
                    paths=paths,
                    chapter_index=1,
                    url=first_url,
                    status=first_response.status,
                    selector_results=first_response.selector_results,
                    failure_signature="chapter-inventory-mismatch",
                    detail=str(error),
                )
            raise
        if options.dry_run:
            return CaptureResult(
                discovery=discovery,
                policy=policy,
                pages=[],
                paths=None,
            )

        paths.root.mkdir(
            parents=True,
            exist_ok=options.resume and preexisting_root,
        )
        metadata = _new_metadata(source, options, discovery, policy)
        _atomic_write_json(
            paths.root / "run-state.json",
            _run_state(
                source=source,
                options=options,
                discovery=discovery,
                policy=policy,
                pages=[],
                charset_decisions={},
                status="running",
            ),
        )
        _atomic_write_json(paths.root / "metadata.json", metadata)
        return await _capture_remaining(
            source=source,
            options=options,
            paths=paths,
            discovery=discovery,
            policy=policy,
            pages=[],
            gateway=active_gateway,
            sleep=sleep,
            first_response=first_response,
        )
    except BaseException as error:
        primary_error = error
        raise
    finally:
        if owns_gateway:
            try:
                await _close_gateway(active_gateway)
            except BaseException as close_error:
                if primary_error is None:
                    raise
                primary_error.add_note(
                    "gateway cleanup also failed: "
                    f"{type(close_error).__name__}: {close_error}"
                )


async def _capture_remaining(
    *,
    source: SourceRecord,
    options: CaptureOptions,
    paths: CapturePaths,
    discovery: WorkDiscovery,
    policy: PolicyDecision,
    pages: list[CapturedPage],
    gateway: BrowserGateway,
    sleep: Sleep,
    first_response: BrowserResponse | None,
) -> CaptureResult:
    completed = {page.chapter.chapter_index for page in pages}
    remaining = [
        chapter
        for chapter in sorted(
            discovery.chapters, key=lambda chapter: chapter.chapter_index
        )
        if chapter.chapter_index not in completed
    ]
    metadata_path = paths.root / "metadata.json"
    metadata = _read_json(metadata_path)
    metadata["policy"] = policy.model_dump(mode="json")
    _atomic_write_json(metadata_path, metadata)

    for position, chapter in enumerate(remaining):
        _validate_chapter_boundary(source, chapter)
        chapter_url = str(chapter.chapter_url)
        try:
            if chapter.chapter_index == 1 and first_response is not None:
                response = first_response
            else:
                response = await _fetch_with_retries(
                    gateway,
                    chapter_url,
                    story_selectors=STORY_SELECTORS,
                    sleep=sleep,
                )
        except _RetryExhausted as error:
            await _stop_at_chapter(
                gateway=gateway,
                paths=paths,
                chapter_index=chapter.chapter_index,
                url=chapter_url,
                status=None,
                selector_results={},
                failure_signature=error.signature,
                detail=error.detail,
            )

        decoded_body, charset_decision = _decode_response(
            response.body, response.charset
        )
        failure = _chapter_failure(
            response,
            expected_url=chapter_url,
            decoded_body=decoded_body,
        )
        if failure is not None:
            await _stop_at_chapter(
                gateway=gateway,
                paths=paths,
                chapter_index=chapter.chapter_index,
                url=chapter_url,
                status=response.status,
                selector_results=response.selector_results,
                failure_signature=failure,
            )

        raw_path = paths.chapter(
            "raw", chapter.chapter_index, ".html"
        )
        _atomic_create_bytes(raw_path, response.body)
        captured = CapturedPage(
            source_id=source.source_id,
            chapter=chapter,
            retrieved_at_utc=datetime.now(timezone.utc),
            final_url=response.final_url,
            status=response.status,
            raw_html_path=raw_path,
        )
        pages.append(captured)
        completed.add(chapter.chapter_index)

        metadata["charset_decisions"][
            str(chapter.chapter_index)
        ] = charset_decision.as_dict()
        metadata["pages"] = [
            page.model_dump(mode="json") for page in pages
        ]
        _atomic_write_json(
            paths.root / "run-state.json",
            _run_state(
                source=source,
                options=options,
                discovery=discovery,
                policy=policy,
                pages=pages,
                charset_decisions=metadata["charset_decisions"],
                status=(
                    "complete"
                    if len(completed) == len(discovery.chapters)
                    else "running"
                ),
            ),
        )
        _atomic_write_json(metadata_path, metadata)

        if position < len(remaining) - 1:
            await sleep(
                policy.effective_delay_seconds + random.uniform(0.0, 1.0)
            )

    return CaptureResult(
        discovery=discovery,
        policy=policy,
        pages=pages,
        paths=paths,
    )


def _load_existing_capture(
    source: SourceRecord,
    options: CaptureOptions,
    paths: CapturePaths,
) -> tuple[WorkDiscovery, list[CapturedPage], str] | None:
    if not paths.root.exists():
        return None
    if not options.resume:
        raise CaptureStopped(
            f"capture {options.capture_id} already exists; use resume"
        )
    state_path = paths.root / "run-state.json"
    metadata_path = paths.root / "metadata.json"
    if not state_path.exists() and not metadata_path.exists():
        if {entry.name for entry in paths.root.iterdir()} <= {"diagnostics"}:
            return None
        raise CaptureStopped("existing capture has no resumable state")
    if not state_path.exists():
        raise CaptureStopped("existing capture state is incomplete")
    state = _read_json(state_path)
    if state.get("capture_id") != options.capture_id:
        raise CaptureStopped("existing state has another capture_id")
    stored_source = SourceRecord.model_validate(state["source"])
    if stored_source != source:
        raise CaptureStopped("source record changed since capture began")
    discovery = WorkDiscovery.model_validate(state["discovery"])
    _validate_discovery_inventory(source, discovery)
    policy = PolicyDecision.model_validate(state["policy"])
    pages = [
        CapturedPage.model_validate(page)
        for page in state.get("pages", [])
    ]
    completed = [int(index) for index in state["completed_chapters"]]
    page_indexes = [page.chapter.chapter_index for page in pages]
    if completed != page_indexes or page_indexes != sorted(set(page_indexes)):
        raise CaptureStopped("authoritative capture state is inconsistent")
    discovered = {
        chapter.chapter_index: chapter for chapter in discovery.chapters
    }
    if any(
        index not in discovered
        or page.chapter != discovered[index]
        or page.source_id != source.source_id
        for index, page in zip(page_indexes, pages)
    ):
        raise CaptureStopped("capture pages do not match discovery")
    if page_indexes != sorted(discovered)[: len(page_indexes)]:
        raise CaptureStopped(
            "completed chapters must be an exact discovery prefix"
        )
    for page in pages:
        expected_path = paths.chapter(
            "raw", page.chapter.chapter_index, ".html"
        )
        if page.raw_html_path != expected_path:
            raise CaptureStopped("capture page has an unexpected raw path")
        if not expected_path.exists():
            raise CaptureStopped(
                f"completed chapter {page.chapter.chapter_index} is missing"
            )
    recorded_raw_paths = {page.raw_html_path for page in pages}
    existing_raw_paths = set((paths.root / "raw").glob("chapter-*.html"))
    unrecorded_raw_paths = existing_raw_paths - recorded_raw_paths
    if unrecorded_raw_paths:
        names = ", ".join(sorted(path.name for path in unrecorded_raw_paths))
        raise CaptureStopped(
            f"capture has unrecorded raw artifact(s): {names}; "
            "use a new capture_id"
        )
    status = str(state["status"])
    if status not in {"running", "stopped", "complete"}:
        raise CaptureStopped(f"invalid capture status: {status}")
    if status == "complete" and page_indexes != sorted(discovered):
        raise CaptureStopped("complete capture has an incomplete inventory")
    if status == "complete":
        _validate_persisted_policy_snapshot(options, policy)

    charset_decisions = state.get("charset_decisions", {})
    if set(charset_decisions) != {str(index) for index in completed}:
        raise CaptureStopped("capture charset state is inconsistent")
    repaired_metadata = _new_metadata(
        source, options, discovery, policy
    )
    repaired_metadata["pages"] = [
        page.model_dump(mode="json") for page in pages
    ]
    repaired_metadata["charset_decisions"] = charset_decisions
    try:
        metadata = _read_json(metadata_path)
    except (FileNotFoundError, json.JSONDecodeError):
        metadata = None
    if metadata != repaired_metadata and not options.dry_run:
        _atomic_write_json(metadata_path, repaired_metadata)
    return discovery, pages, status


async def _fetch_robots(
    gateway: BrowserGateway, robots_url: str
) -> BrowserResponse:
    try:
        return await gateway.fetch(robots_url)
    except (TimeoutError, ConnectionResetError, PlaywrightError) as error:
        raise _RetryExhausted("robots-fetch-failed", str(error)) from error


def _robots_failure(
    response: BrowserResponse,
    *,
    expected_url: str,
    decoded_body: str,
) -> str | None:
    if response.status != 200:
        return f"robots-http-{response.status}"
    if _normalized_url(response.final_url) != _normalized_url(expected_url):
        return "robots-unexpected-final-url"
    return _safeguard_failure(decoded_body, response.visible_text)


async def _fetch_with_retries(
    gateway: BrowserGateway,
    url: str,
    *,
    story_selectors: tuple[str, ...],
    sleep: Sleep,
) -> BrowserResponse:
    for attempt in range(len(_RETRY_BACKOFF_SECONDS) + 1):
        try:
            return await gateway.fetch(
                url,
                story_selectors=story_selectors,
                timeout_seconds=_STORY_TIMEOUT_SECONDS,
            )
        except (TimeoutError, ConnectionResetError) as error:
            if attempt == len(_RETRY_BACKOFF_SECONDS):
                signature = (
                    "network-timeout"
                    if isinstance(error, TimeoutError)
                    else "connection-reset"
                )
                raise _RetryExhausted(signature, str(error)) from error
            await sleep(_RETRY_BACKOFF_SECONDS[attempt])
        except PlaywrightError as error:
            raise _RetryExhausted(
                "network-error", str(error)
            ) from error
    raise AssertionError("unreachable retry state")


def _chapter_failure(
    response: BrowserResponse,
    *,
    expected_url: str,
    decoded_body: str,
) -> str | None:
    if response.status == 403:
        return "http-403-access-denied"
    if response.status == 429:
        return "http-429-rate-limited"
    if not 200 <= response.status < 300:
        return f"http-{response.status}"
    if _normalized_url(response.final_url) != _normalized_url(expected_url):
        return "unexpected-final-url"

    safeguard_failure = _safeguard_failure(
        decoded_body, response.visible_text
    )
    if safeguard_failure is not None:
        return safeguard_failure
    if not any(response.selector_results.values()):
        return "missing-story-content"
    return None


def _safeguard_failure(
    decoded_body: str, visible_text: str
) -> str | None:
    inspected_text = f"{decoded_body}\n{visible_text}".casefold()
    if "captcha" in inspected_text:
        return "captcha"
    if "cloudflare" in inspected_text:
        return "cloudflare"
    if any(
        signature in inspected_text
        for signature in (
            "checking your browser",
            "security challenge",
            "verify you are human",
        )
    ):
        return "challenge"
    if any(
        signature in inspected_text
        for signature in (
            "access denied",
            "request blocked",
            "temporarily blocked",
        )
    ):
        return "access-denied"
    return None


async def _stop_at_chapter(
    *,
    gateway: BrowserGateway,
    paths: CapturePaths,
    chapter_index: int,
    url: str,
    status: int | None,
    selector_results: dict[str, bool],
    failure_signature: str,
    detail: str | None = None,
) -> None:
    await _write_diagnostic(
        gateway=gateway,
        paths=paths,
        chapter_index=chapter_index,
        url=url,
        status=status,
        selector_results=selector_results,
        failure_signature=failure_signature,
        detail=detail,
    )
    state_path = paths.root / "run-state.json"
    state = _read_json(state_path)
    state["status"] = "stopped"
    state["stopped_chapter"] = chapter_index
    state["failure_signature"] = failure_signature
    _atomic_write_json(state_path, state)
    raise CaptureStopped(
        f"capture stopped at chapter {chapter_index}: {failure_signature}"
    )


async def _write_diagnostic(
    *,
    gateway: BrowserGateway,
    paths: CapturePaths,
    chapter_index: int,
    url: str,
    status: int | None,
    selector_results: dict[str, bool],
    failure_signature: str,
    detail: str | None = None,
) -> None:
    diagnostic_root = paths.root / "diagnostics"
    screenshot_path = diagnostic_root / f"chapter-{chapter_index:03d}.png"
    screenshot_error = None
    try:
        await gateway.screenshot(screenshot_path)
    except Exception as error:  # diagnostics must survive screenshot failures
        screenshot_error = f"{type(error).__name__}: {error}"
    diagnostic = {
        "url": url,
        "status": status,
        "selector_results": selector_results,
        "failure_signature": failure_signature,
        "screenshot_path": str(screenshot_path),
    }
    if detail is not None:
        diagnostic["detail"] = detail
    if screenshot_error is not None:
        diagnostic["screenshot_error"] = screenshot_error
    _atomic_write_json(
        diagnostic_root / f"chapter-{chapter_index:03d}.json",
        diagnostic,
    )


def _new_metadata(
    source: SourceRecord,
    options: CaptureOptions,
    discovery: WorkDiscovery,
    policy: PolicyDecision,
) -> dict[str, object]:
    return {
        "capture_id": options.capture_id,
        "source": source.model_dump(mode="json"),
        "discovery": discovery.model_dump(mode="json"),
        "policy": policy.model_dump(mode="json"),
        "charset_decisions": {},
        "pages": [],
    }


def _run_state(
    *,
    source: SourceRecord,
    options: CaptureOptions,
    discovery: WorkDiscovery,
    policy: PolicyDecision,
    pages: list[CapturedPage],
    charset_decisions: dict,
    status: str,
) -> dict[str, object]:
    return {
        "capture_id": options.capture_id,
        "source": source.model_dump(mode="json"),
        "discovery": discovery.model_dump(mode="json"),
        "policy": policy.model_dump(mode="json"),
        "status": status,
        "completed_chapters": [
            page.chapter.chapter_index for page in pages
        ],
        "pages": [page.model_dump(mode="json") for page in pages],
        "charset_decisions": charset_decisions,
    }


def _persist_or_validate_policy_snapshot(
    options: CaptureOptions,
    robots_body: bytes,
    policy: PolicyDecision,
) -> None:
    policy_root = (
        options.output_root
        / "reports"
        / "policy-snapshots"
        / options.capture_id
    )
    robots_path = policy_root / "robots.txt"
    decision_path = policy_root / "policy-decision.json"
    if robots_path.exists() or decision_path.exists():
        if (
            not robots_path.exists()
            or not decision_path.exists()
            or robots_path.read_bytes() != robots_body
            or decision_path.read_bytes()
            != _json_bytes(policy.model_dump(mode="json"))
        ):
            if not options.resume:
                raise CaptureStopped(
                    "policy snapshot collision for capture_id; "
                    "use a new capture_id"
                )
            raise CaptureStopped(
                "capture policy changed during resume; use a new capture_id"
            )
        return
    _atomic_write_bytes(robots_path, robots_body)
    _atomic_write_json(
        decision_path,
        policy.model_dump(mode="json"),
    )


def _validate_persisted_policy_snapshot(
    options: CaptureOptions,
    policy: PolicyDecision,
) -> None:
    policy_root = (
        options.output_root
        / "reports"
        / "policy-snapshots"
        / options.capture_id
    )
    robots_path = policy_root / "robots.txt"
    decision_path = policy_root / "policy-decision.json"
    if not robots_path.exists() or not decision_path.exists():
        raise CaptureStopped("persisted policy snapshot is incomplete")
    robots_body = robots_path.read_bytes()
    if hashlib.sha256(robots_body).hexdigest() != policy.robots_sha256:
        raise CaptureStopped("persisted policy snapshot robots hash changed")
    if decision_path.read_bytes() != _json_bytes(
        policy.model_dump(mode="json")
    ):
        raise CaptureStopped(
            "persisted policy snapshot decision bytes changed"
        )


def _decode_response(
    body: bytes, declared_charset: str | None
) -> tuple[str, _CharsetDecision]:
    if declared_charset:
        try:
            return body.decode(declared_charset), _CharsetDecision(
                declared=declared_charset,
                used=declared_charset,
                fallback=False,
            )
        except (LookupError, UnicodeDecodeError):
            pass
    return body.decode("utf-8", errors="replace"), _CharsetDecision(
        declared=declared_charset,
        used="utf-8",
        fallback=True,
    )


def _response_charset(headers: dict[str, str]) -> str | None:
    content_type = headers.get("content-type", "")
    match = re.search(
        r"(?:^|;)\s*charset\s*=\s*[\"']?([^;\"'\s]+)",
        content_type,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def _normalized_url(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit(
        (
            parsed.scheme.casefold(),
            parsed.netloc.casefold(),
            parsed.path.rstrip("/") or "/",
            parsed.query,
            "",
        )
    )


def _validate_source_boundary(source: SourceRecord) -> None:
    parsed = urlsplit(str(source.work_url))
    if (
        source.platform != "fanfiction.net"
        or parsed.scheme != "https"
        or parsed.hostname != "www.fanfiction.net"
        or parsed.port not in (None, 443)
        or parsed.username is not None
        or parsed.password is not None
        or re.fullmatch(r"/s/\d+(?:/.*)?", parsed.path) is None
    ):
        raise CaptureStopped(
            "unsupported source URL; expected "
            "https://www.fanfiction.net[:443]/s/<numeric-id>/..."
        )


def _validate_discovery_inventory(
    source: SourceRecord, discovery: WorkDiscovery
) -> None:
    source_work_id = _source_work_id(source)
    if (
        discovery.source_id != source.source_id
        or not discovery.work_id.isdigit()
        or discovery.work_id != source_work_id
    ):
        raise CaptureStopped("discovery belongs to another source or work")
    expected_indexes = list(
        range(1, source.expected_available_chapter_count + 1)
    )
    indexes = [chapter.chapter_index for chapter in discovery.chapters]
    if (
        len(indexes) != len(expected_indexes)
        or sorted(indexes) != expected_indexes
    ):
        raise CaptureStopped(
            "discovery chapter inventory must have the expected count and "
            "unique consecutive indexes"
        )
    for chapter in discovery.chapters:
        _validate_chapter_boundary(source, chapter)


def _validate_chapter_boundary(
    source: SourceRecord, chapter: ChapterRef
) -> None:
    parsed = urlsplit(str(chapter.chapter_url))
    try:
        allowed_port = parsed.port in (None, 443)
    except ValueError:
        allowed_port = False
    expected_path = re.compile(
        rf"/s/{re.escape(_source_work_id(source))}/"
        rf"{chapter.chapter_index}(?:/.*)?"
    )
    if (
        parsed.scheme != "https"
        or parsed.hostname != "www.fanfiction.net"
        or not allowed_port
        or parsed.username is not None
        or parsed.password is not None
        or expected_path.fullmatch(parsed.path) is None
    ):
        raise CaptureStopped(
            f"discovery chapter {chapter.chapter_index} has an unsupported URL"
        )


def _source_work_id(source: SourceRecord) -> str:
    match = re.match(r"^/s/(\d+)(?:/|$)", urlsplit(str(source.work_url)).path)
    if match is None:
        raise CaptureStopped("source URL has no numeric work ID")
    return match.group(1)


def _robots_url(source: SourceRecord) -> str:
    parsed = urlsplit(str(source.work_url))
    return urlunsplit(
        (parsed.scheme, parsed.netloc, "/robots.txt", "", "")
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text("utf-8"))


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _atomic_write_json(path: Path, value: object) -> None:
    _atomic_write_bytes(path, _json_bytes(value))


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_bytes(payload)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_create_bytes(path: Path, payload: bytes) -> None:
    if path.exists():
        raise CaptureStopped(
            f"refusing to overwrite existing raw artifact: {path}"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_bytes(payload)
        if path.exists():
            raise CaptureStopped(
                f"refusing to overwrite existing raw artifact: {path}"
            )
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


async def _close_gateway(gateway: BrowserGateway) -> None:
    close = getattr(gateway, "close", None)
    if close is not None:
        await close()
