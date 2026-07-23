"""Offline structural, content, integrity, and manual validation."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
from typing import Any
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
import fitz

from .merge_pdf import canonical_complete_pdf_name
from .models import (
    CapturedPage,
    CheckResult,
    ManifestRecord,
    SourceRecord,
    WorkDiscovery,
    WorkValidation,
)


DATASET_DIRECTORY = Path("data/fanfic-hogwarts-history")
RATIO_MINIMUM = 0.75
RATIO_MAXIMUM = 1.35
SUBSTANTIAL_PARAGRAPH_LENGTH = 40
ACCESS_DENIAL_TEXT = (
    "checking your browser",
    "access denied",
    "captcha",
    "page not found",
)
SITE_CHROME_SELECTORS = (
    "#content_wrapper",
    "#profile_top",
    "#storytext",
    "#review",
    ".xcontrast_txt",
    "nav",
    "footer",
    "form",
    "button",
    "input",
    "select",
    "textarea",
)
SITE_CHROME_TEXT = (
    "post review",
    "follow/favorite",
    "follow story",
    "favorite story",
)
HASH_FIELDS = {
    "raw_html_path": "raw_sha256",
    "clean_html_path": "clean_html_sha256",
    "text_path": "text_sha256",
    "chapter_pdf_path": "chapter_pdf_sha256",
    "complete_pdf_path": "complete_pdf_sha256",
}
AUTOMATED_CHECK_IDS = (
    "chapter_count",
    "chapter_sequence",
    "chapter_titles",
    "story_text",
    "access_denial",
    "site_chrome",
    "markdown_pdf_boundaries",
    "pdf_markdown_ratio",
    "pdf_semantic_html_ratio",
    "pdf_bookmarks",
    "artifact_hashes",
    "annotation_hashes",
)
_MANIFEST_CHECK_IDS = frozenset(AUTOMATED_CHECK_IDS)
_ARTIFACT_CHECK_IDS = frozenset(
    {
        "story_text",
        "access_denial",
        "site_chrome",
        "markdown_pdf_boundaries",
        "pdf_markdown_ratio",
        "pdf_semantic_html_ratio",
        "pdf_bookmarks",
        "artifact_hashes",
        "annotation_hashes",
    }
)
_SPACE = re.compile(r"\s+")
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_IMAGE = re.compile(r"!\[[^\]]*]\([^)]*\)")
_LINK = re.compile(r"\[([^\]]+)]\([^)]*\)")
_MARKDOWN_PUNCTUATION = re.compile(r"[`*_#>~|]")
_HASH = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class _CaptureMetadata:
    capture_id: str
    source: SourceRecord
    discovery: WorkDiscovery
    pages: list[CapturedPage]


@dataclass(frozen=True)
class _ValidationContext:
    capture_dir: Path
    dataset_root: Path
    source_id: str
    capture_id: str
    metadata: _CaptureMetadata | None
    manifest_records: list[ManifestRecord]
    artifact_bindings: list[dict[str, Path]]
    annotations: dict[str, Any]
    manual_reviews: dict[str, Any]
    input_errors: dict[str, str]

    def artifact_path(self, record: ManifestRecord, field: str) -> Path:
        for position, candidate in enumerate(self.manifest_records):
            if candidate is record:
                return self.artifact_bindings[position][field]
        raise ValueError("manifest record has no canonical artifact binding")


def validate_work(
    capture_dir: Path,
    *,
    manual_review_path: Path | None = None,
) -> WorkValidation:
    """Run every validation check and persist a deterministic result."""
    capture_dir = Path(capture_dir)
    dataset_root = capture_dir.parents[3]
    source_id = capture_dir.parents[1].name
    capture_id = capture_dir.name
    metadata, metadata_error = _load_or_error(
        lambda: _load_capture_metadata(capture_dir / "metadata.json"),
        empty=None,
    )
    all_records, manifest_error = _load_or_error(
        lambda: _load_manifest_records(dataset_root / "manifest.jsonl"),
        empty=[],
    )
    records = _select_manifest_records(
        all_records,
        source_id=source_id,
        capture_id=capture_id,
    )
    if manifest_error is None and not records:
        manifest_error = "manifest dependency invalid: no records for current capture"
    if metadata_error is not None:
        binding_error = (
            "metadata dependency invalid; canonical artifact binding unavailable"
        )
        bindings: list[dict[str, Path]] = []
    elif manifest_error is not None:
        binding_error = (
            "manifest dependency invalid; canonical artifact binding unavailable"
        )
        bindings = []
    else:
        bindings, binding_error = _load_or_error(
            lambda: _bind_artifact_paths(
                capture_dir=capture_dir,
                dataset_root=dataset_root,
                source_id=source_id,
                capture_id=capture_id,
                metadata=metadata,
                records=records,
            ),
            empty=[],
        )
    annotations, annotations_error = _load_or_error(
        lambda: _load_optional_json_object(capture_dir / "annotations.json"),
        empty={},
    )
    review_path = (
        Path(manual_review_path)
        if manual_review_path is not None
        else dataset_root / "reports/manual-review.json"
    )
    manual_reviews, manual_review_error = _load_or_error(
        lambda: _load_optional_json_object(review_path),
        empty={},
    )
    context = _ValidationContext(
        capture_dir=capture_dir,
        dataset_root=dataset_root,
        source_id=source_id,
        capture_id=capture_id,
        metadata=metadata,
        manifest_records=records,
        artifact_bindings=bindings,
        annotations=annotations,
        manual_reviews=manual_reviews,
        input_errors={
            key: error
            for key, error in (
                (
                    "metadata",
                    (
                        f"metadata dependency invalid: {metadata_error}"
                        if metadata_error is not None
                        else None
                    ),
                ),
                (
                    "manifest",
                    (
                        manifest_error
                        if manifest_error is None
                        or manifest_error.startswith("manifest dependency")
                        else f"manifest dependency invalid: {manifest_error}"
                    ),
                ),
                (
                    "artifact_binding",
                    (
                        binding_error
                        if binding_error is None
                        or "dependency" in binding_error
                        else (
                            "canonical artifact binding dependency invalid: "
                            f"{binding_error}"
                        )
                    ),
                ),
                ("annotations", annotations_error),
                ("manual_review", manual_review_error),
            )
            if error is not None
        },
    )

    functions: tuple[tuple[str, Callable[[_ValidationContext], tuple[bool, str]]], ...] = (
        ("chapter_count", _check_chapter_count),
        ("chapter_sequence", _check_chapter_sequence),
        ("chapter_titles", _check_chapter_titles),
        ("story_text", _check_story_text),
        ("access_denial", _check_access_denial),
        ("site_chrome", _check_site_chrome),
        ("markdown_pdf_boundaries", _check_markdown_pdf_boundaries),
        ("pdf_markdown_ratio", _check_pdf_markdown_ratio),
        ("pdf_semantic_html_ratio", _check_pdf_semantic_html_ratio),
        ("pdf_bookmarks", _check_pdf_bookmarks),
        ("artifact_hashes", _check_artifact_hashes),
        ("annotation_hashes", _check_annotation_hashes),
        ("manual_spot_checks", _check_manual_spot_checks),
    )
    checks = [_run_check(check_id, function, context) for check_id, function in functions]
    by_id = {check.check_id: check for check in checks}
    automated_failed = any(not by_id[check_id].passed for check_id in AUTOMATED_CHECK_IDS)
    if automated_failed:
        status = "fail"
    elif not by_id["manual_spot_checks"].passed:
        status = "manual-review-pending"
    else:
        status = "pass"
    result = WorkValidation(
        source_id=source_id,
        capture_id=capture_id,
        status=status,
        checks=checks,
    )
    _write_validation(capture_dir / "validation.json", result)
    return result


def validation_exit_status(validation: WorkValidation) -> int:
    """Return zero only for a fully passing validation."""
    return 0 if validation.status == "pass" else 1


def summarize_validations(
    validations: Iterable[WorkValidation],
) -> dict[str, int]:
    """Return deterministic counts suitable for CLI and report consumers."""
    items = list(validations)
    summary = {
        "total": len(items),
        "pass": sum(item.status == "pass" for item in items),
        "fail": sum(item.status == "fail" for item in items),
        "manual-review-pending": sum(
            item.status == "manual-review-pending" for item in items
        ),
    }
    summary["exit_status"] = (
        0 if summary["total"] > 0 and summary["pass"] == summary["total"] else 1
    )
    return summary


def _run_check(
    check_id: str,
    function: Callable[[_ValidationContext], tuple[bool, str]],
    context: _ValidationContext,
) -> CheckResult:
    dependencies = ["metadata"]
    if check_id in _MANIFEST_CHECK_IDS:
        dependencies.append("manifest")
    if check_id in _ARTIFACT_CHECK_IDS:
        dependencies.append("artifact_binding")
    failures = [
        context.input_errors[dependency]
        for dependency in dependencies
        if dependency in context.input_errors
    ]
    if failures:
        return CheckResult(
            check_id=check_id,
            passed=False,
            detail="dependency failure: " + "; ".join(failures),
        )
    try:
        passed, detail = function(context)
    except Exception as error:
        passed = False
        detail = f"check could not complete: {type(error).__name__}: {error}"
    return CheckResult(check_id=check_id, passed=passed, detail=detail)


def _check_chapter_count(context: _ValidationContext) -> tuple[bool, str]:
    metadata = _required_metadata(context)
    expected = metadata.source.expected_available_chapter_count
    artifact_counts = {
        "raw": len(list((context.capture_dir / "raw").glob("chapter-*.html"))),
        "clean": len(list((context.capture_dir / "clean").glob("chapter-*.html"))),
        "text": len(list((context.capture_dir / "text").glob("chapter-*.md"))),
        "chapter_pdf": len(
            list((context.capture_dir / "pdf").glob("chapter-*.pdf"))
        ),
    }
    observed = {
        "discovery": len(metadata.discovery.chapters),
        "captured": len(metadata.pages),
        "manifest": len(context.manifest_records),
        **artifact_counts,
    }
    manifest_expected = [
        record.expected_available_chapter_count
        for record in context.manifest_records
    ]
    passed = (
        all(count == expected for count in observed.values())
        and manifest_expected == [expected] * expected
    )
    detail = (
        f"displayed={expected!r}; observed={observed}; "
        f"manifest displayed counts={manifest_expected}"
    )
    return passed, detail


def _check_chapter_sequence(context: _ValidationContext) -> tuple[bool, str]:
    metadata = _required_metadata(context)
    chapter_groups = [
        ("discovery", metadata.discovery.chapters),
        ("captured", [page.chapter for page in metadata.pages]),
        ("manifest", context.manifest_records),
    ]
    failures: list[str] = []
    for label, chapters in chapter_groups:
        indexes = [chapter.chapter_index for chapter in chapters]
        urls = [str(chapter.chapter_url) for chapter in chapters]
        expected = list(range(1, len(chapters) + 1))
        if indexes != expected:
            failures.append(f"{label} indexes={indexes!r}, expected={expected!r}")
        if any(not url for url in urls) or len(urls) != len(set(urls)):
            failures.append(f"{label} URLs are empty or duplicated")
        for index, url in zip(indexes, urls, strict=True):
            if not _url_has_chapter_index(url, index):
                failures.append(f"{label} URL does not encode chapter {index!r}")
    for page in metadata.pages:
        if str(page.final_url) != str(page.chapter.chapter_url):
            failures.append("captured final URL differs from chapter URL")
    if metadata.capture_id != context.capture_id:
        failures.append("metadata capture_id differs from capture directory")
    if metadata.source.source_id != context.source_id:
        failures.append("source_id differs from capture directory")
    if metadata.discovery.source_id != metadata.source.source_id:
        failures.append("discovery source_id differs from source record")
    if metadata.source.work_title != metadata.discovery.work_title:
        failures.append("source and discovery work titles disagree")
    if metadata.source.author != metadata.discovery.author:
        failures.append("source and discovery authors disagree")
    if len(metadata.pages) == len(metadata.discovery.chapters):
        for position, (chapter, page) in enumerate(
            zip(metadata.discovery.chapters, metadata.pages, strict=True),
            start=1,
        ):
            if page.source_id != metadata.source.source_id:
                failures.append(f"captured page {position} source_id disagrees")
            if page.chapter != chapter:
                failures.append(
                    f"captured page {position} chapter differs from discovery"
                )
    if (
        len(metadata.pages)
        == len(metadata.discovery.chapters)
        == len(context.manifest_records)
    ):
        for position, (chapter, page, record) in enumerate(
            zip(
                metadata.discovery.chapters,
                metadata.pages,
                context.manifest_records,
                strict=True,
            ),
            start=1,
        ):
            disagreements = _manifest_provenance_disagreements(
                context,
                metadata,
                chapter,
                page,
                record,
            )
            if disagreements:
                failures.append(
                    f"manifest chapter {position} disagrees on "
                    + ", ".join(disagreements)
                )
    else:
        failures.append(
            "discovery, captured pages, and manifest chapter sequences "
            "have different lengths"
        )
    detail = (
        "; ".join(failures)
        if failures
        else (
            "discovery, captured pages, and manifest provenance agree in "
            "unique canonical chapter order"
        )
    )
    return not failures, detail


def _check_chapter_titles(context: _ValidationContext) -> tuple[bool, str]:
    metadata = _required_metadata(context)
    groups = [
        ("discovery", metadata.discovery.chapters),
        ("captured", [page.chapter for page in metadata.pages]),
        ("manifest", context.manifest_records),
    ]
    failures: list[str] = []
    for label, chapters in groups:
        for position, chapter in enumerate(chapters, start=1):
            title = chapter.chapter_title
            missing = chapter.title_missing is True
            has_title = isinstance(title, str) and bool(title.strip())
            if has_title == missing:
                failures.append(
                    f"{label} chapter {position} title/title_missing are inconsistent"
                )
    if (
        len(metadata.pages)
        == len(metadata.discovery.chapters)
        == len(context.manifest_records)
    ):
        for position, (chapter, page, record) in enumerate(
            zip(
                metadata.discovery.chapters,
                metadata.pages,
                context.manifest_records,
                strict=True,
            ),
            start=1,
        ):
            titles = {
                (chapter.chapter_title, chapter.title_missing),
                (page.chapter.chapter_title, page.chapter.title_missing),
                (record.chapter_title, record.title_missing),
            }
            if len(titles) != 1:
                failures.append(
                    f"chapter {position} title/title_missing representations disagree"
                )
    else:
        failures.append(
            "cannot compare chapter titles across differently sized representations"
        )
    detail = (
        "; ".join(failures)
        if failures
        else "every chapter has a title or an explicit title_missing record"
    )
    return not failures, detail


def _check_story_text(context: _ValidationContext) -> tuple[bool, str]:
    failures: list[str] = []
    for record in context.manifest_records:
        index = record.chapter_index
        clean_path = context.artifact_path(record, "clean_html_path")
        markdown_path = context.artifact_path(record, "text_path")
        story_text = _semantic_html_text(clean_path)
        markdown_text = _normalize_markdown(markdown_path.read_text("utf-8"))
        if not story_text:
            failures.append(f"chapter {index} semantic story text is empty")
        if not markdown_text:
            failures.append(f"chapter {index} Markdown story text is empty")
    detail = (
        "; ".join(failures)
        if failures
        else "all chapter story artifacts contain visible text"
    )
    return not failures, detail


def _check_access_denial(context: _ValidationContext) -> tuple[bool, str]:
    findings: list[str] = []
    for record in context.manifest_records:
        for field in ("raw_html_path", "clean_html_path"):
            path = context.artifact_path(record, field)
            content = path.read_bytes().lower()
            matches = [
                phrase
                for phrase in ACCESS_DENIAL_TEXT
                if phrase.encode("ascii") in content
            ]
            if matches:
                findings.append(
                    f"chapter {record.chapter_index} {field}: {matches}"
                )
    detail = (
        "; ".join(findings)
        if findings
        else "raw and clean HTML contain no access-denial response text"
    )
    return not findings, detail


def _check_site_chrome(context: _ValidationContext) -> tuple[bool, str]:
    findings: list[str] = []
    for record in context.manifest_records:
        path = context.artifact_path(record, "clean_html_path")
        soup = BeautifulSoup(path.read_text("utf-8"), "html.parser")
        selectors = [
            selector for selector in SITE_CHROME_SELECTORS if soup.select_one(selector)
        ]
        visible = _normalize_space(soup.get_text(" ", strip=True)).casefold()
        text_matches = [phrase for phrase in SITE_CHROME_TEXT if phrase in visible]
        if selectors or text_matches:
            findings.append(
                f"chapter {record.chapter_index} selectors={selectors} text={text_matches}"
            )
    detail = (
        "; ".join(findings)
        if findings
        else "clean HTML contains no known site chrome"
    )
    return not findings, detail


def _check_markdown_pdf_boundaries(
    context: _ValidationContext,
) -> tuple[bool, str]:
    failures: list[str] = []
    for record in context.manifest_records:
        index = record.chapter_index
        paragraphs = _substantial_markdown_paragraphs(
            context.artifact_path(record, "text_path").read_text("utf-8")
        )
        pdf_text = _pdf_text(context.artifact_path(record, "chapter_pdf_path"))
        if not paragraphs:
            failures.append(f"chapter {index} has no substantial Markdown paragraph")
            continue
        if paragraphs[0] not in pdf_text:
            failures.append(f"chapter {index} first substantial paragraph is absent")
        if paragraphs[-1] not in pdf_text:
            failures.append(f"chapter {index} last substantial paragraph is absent")
    detail = (
        "; ".join(failures)
        if failures
        else (
            "first and last substantial Markdown paragraphs appear in "
            "chapter PDFs"
        )
    )
    return not failures, detail


def _check_pdf_markdown_ratio(context: _ValidationContext) -> tuple[bool, str]:
    return _check_ratios(
        context,
        denominator=lambda record: _normalize_markdown(
            context.artifact_path(record, "text_path").read_text("utf-8")
        ),
        label="Markdown",
    )


def _check_pdf_semantic_html_ratio(
    context: _ValidationContext,
) -> tuple[bool, str]:
    return _check_ratios(
        context,
        denominator=lambda record: _semantic_html_text(
            context.artifact_path(record, "clean_html_path")
        ),
        label="semantic HTML",
    )


def _check_ratios(
    context: _ValidationContext,
    *,
    denominator: Callable[[ManifestRecord], str],
    label: str,
) -> tuple[bool, str]:
    ratios: list[str] = []
    failed = False
    for record in context.manifest_records:
        pdf = _pdf_text(context.artifact_path(record, "chapter_pdf_path"))
        reference = denominator(record)
        ratio = len(pdf) / len(reference) if reference else float("inf")
        ratios.append(f"chapter {record.chapter_index}={ratio:.3f}")
        if not RATIO_MINIMUM <= ratio <= RATIO_MAXIMUM:
            failed = True
    bounds = f"{RATIO_MINIMUM:.2f}..{RATIO_MAXIMUM:.2f}"
    return not failed, f"PDF/{label} ratios ({bounds}): {', '.join(ratios)}"


def _check_pdf_bookmarks(context: _ValidationContext) -> tuple[bool, str]:
    if not context.manifest_records:
        return False, "manifest has no complete PDF record"
    paths = {
        context.artifact_path(record, "complete_pdf_path")
        for record in context.manifest_records
    }
    if len(paths) != 1:
        return False, f"manifest references {len(paths)} complete PDFs"
    with fitz.open(next(iter(paths))) as document:
        bookmark_count = len(document.get_toc())
    expected = len(_required_metadata(context).discovery.chapters)
    return (
        bookmark_count == expected,
        f"complete PDF bookmarks={bookmark_count}; chapters={expected}",
    )


def _check_artifact_hashes(context: _ValidationContext) -> tuple[bool, str]:
    failures: list[str] = []
    if "manifest" in context.input_errors:
        failures.append(context.input_errors["manifest"])
    verified = 0
    for record in context.manifest_records:
        for path_field, hash_field in HASH_FIELDS.items():
            path = context.artifact_path(record, path_field)
            if path.is_symlink() or not path.is_file():
                failures.append(f"{path_field} is not a regular non-symlink file")
                continue
            stored = getattr(record, hash_field)
            current = _sha256_file(path)
            if stored != current:
                failures.append(
                    f"chapter {record.chapter_index} {hash_field} mismatch"
                )
            else:
                verified += 1
    if not context.manifest_records:
        failures.append("no manifest records were found for this capture")
    detail = (
        "; ".join(failures)
        if failures
        else f"verified {verified} stored artifact hashes"
    )
    return not failures, detail


def _check_annotation_hashes(context: _ValidationContext) -> tuple[bool, str]:
    failures: list[str] = []
    if "annotations" in context.input_errors:
        failures.append(context.input_errors["annotations"])
    checked = 0
    expected_keys = {
        f"chapter-{record.chapter_index:03d}"
        for record in context.manifest_records
    }
    unknown_records = set(context.annotations) - expected_keys
    if unknown_records:
        failures.append(
            f"annotations reference unknown chapters: {sorted(unknown_records)}"
        )
    for record in context.manifest_records:
        index = record.chapter_index
        key = f"chapter-{index:03d}"
        annotation = _mapping(context.annotations.get(key, {}))
        clean_path = context.artifact_path(record, "clean_html_path")
        soup = BeautifulSoup(clean_path.read_text("utf-8"), "html.parser")
        known = {
            str(node.get("data-sha256"))
            for node in soup.select("main[data-role='story'] [data-sha256]")
            if node.get("data-sha256")
        }
        author = _hash_values(annotation, "author_note_block_sha256", failures, key)
        missing = _hash_values(
            annotation,
            "missing_chapter_notice_block_sha256",
            failures,
            key,
        )
        unknown = (author | missing) - known
        if unknown:
            failures.append(f"{key} references unknown block hashes: {sorted(unknown)}")
        overlap = author & missing
        if overlap:
            failures.append(f"{key} assigns block hashes to multiple annotations")
        checked += len(author | missing)
    detail = (
        "; ".join(failures)
        if failures
        else f"validated {checked} annotation block hashes"
    )
    return not failures, detail


def _check_manual_spot_checks(context: _ValidationContext) -> tuple[bool, str]:
    key = f"{context.source_id}/{context.capture_id}"
    record = _mapping(context.manual_reviews.get(key, {}))
    failures: list[str] = []
    if "manual_review" in context.input_errors:
        failures.append(context.input_errors["manual_review"])
    for field in (
        "reviewed_by",
        "reviewed_at_utc",
        "notes",
    ):
        if not isinstance(record.get(field), str) or not record[field].strip():
            failures.append(f"{field} is unsigned")
    if isinstance(record.get("reviewed_at_utc"), str):
        try:
            reviewed_at = datetime.fromisoformat(
                record["reviewed_at_utc"].replace("Z", "+00:00")
            )
            if reviewed_at.utcoffset() != timezone.utc.utcoffset(reviewed_at):
                failures.append("reviewed_at_utc is not UTC")
        except ValueError:
            failures.append("reviewed_at_utc is invalid")
    for field in (
        "first_chapter",
        "final_chapter",
        "longest_chapter",
        "chapter_transitions",
    ):
        if record.get(field) is not True:
            failures.append(f"{field} is not signed true")
    actual_chapters = record.get("author_note_or_missing_notice_chapters")
    expected_chapters = _annotated_chapter_indexes(context.annotations)
    if (
        not isinstance(actual_chapters, list)
        or any(not isinstance(value, int) for value in actual_chapters)
        or sorted(set(actual_chapters)) != expected_chapters
    ):
        failures.append(
            "author_note_or_missing_notice_chapters does not match annotations"
        )
    detail = (
        "; ".join(failures)
        if failures
        else f"manual spot checks are signed for {key}"
    )
    return not failures, detail


def _substantial_markdown_paragraphs(markdown: str) -> list[str]:
    paragraphs = []
    for paragraph in re.split(r"\n\s*\n", _COMMENT.sub("", markdown)):
        visible = _normalize_markdown(paragraph)
        if len(visible) >= SUBSTANTIAL_PARAGRAPH_LENGTH:
            paragraphs.append(visible)
    return paragraphs


def _normalize_markdown(markdown: str) -> str:
    value = _COMMENT.sub(" ", markdown)
    value = _IMAGE.sub(" ", value)
    value = _LINK.sub(r"\1", value)
    value = _MARKDOWN_PUNCTUATION.sub("", value)
    value = value.replace("\\", "")
    return _normalize_space(value)


def _semantic_html_text(path: Path) -> str:
    soup = BeautifulSoup(path.read_text("utf-8"), "html.parser")
    story = soup.select_one("main[data-role='story']")
    return _normalize_space(story.get_text(" ", strip=True)) if story else ""


def _pdf_text(path: Path) -> str:
    with fitz.open(path) as document:
        return _normalize_space(" ".join(page.get_text() for page in document))


def _normalize_space(value: str) -> str:
    return _SPACE.sub(" ", value.replace("\xa0", " ")).strip()


def _url_has_chapter_index(url: str, index: int) -> bool:
    try:
        parts = [part for part in urlsplit(url).path.split("/") if part]
    except ValueError:
        return False
    return len(parts) >= 3 and parts[0] == "s" and parts[2] == str(index)


def _hash_values(
    annotation: dict[str, Any],
    field: str,
    failures: list[str],
    key: str,
) -> set[str]:
    values = annotation.get(field, [])
    if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
        failures.append(f"{key} {field} must be a list of hashes")
        return set()
    invalid = [value for value in values if _HASH.fullmatch(value) is None]
    if invalid:
        failures.append(f"{key} {field} contains invalid hashes")
    return {value for value in values if _HASH.fullmatch(value)}


def _annotated_chapter_indexes(annotations: dict[str, Any]) -> list[int]:
    result: list[int] = []
    for key, value in annotations.items():
        match = re.fullmatch(r"chapter-(\d{3})", key)
        record = _mapping(value)
        if match and (
            _list(record.get("author_note_block_sha256"))
            or _list(record.get("missing_chapter_notice_block_sha256"))
        ):
            result.append(int(match.group(1)))
    return sorted(set(result))


def _required_metadata(context: _ValidationContext) -> _CaptureMetadata:
    if context.metadata is None:
        raise ValueError("metadata dependency is unavailable")
    return context.metadata


def _manifest_provenance_disagreements(
    context: _ValidationContext,
    metadata: _CaptureMetadata,
    chapter: Any,
    page: CapturedPage,
    record: ManifestRecord,
) -> list[str]:
    comparisons = {
        "capture_id": (record.capture_id, context.capture_id),
        "source_id": (record.source_id, metadata.source.source_id),
        "work_title": (record.work_title, metadata.discovery.work_title),
        "author": (record.author, metadata.discovery.author),
        "platform": (record.platform, metadata.source.platform),
        "work_url": (str(record.work_url), str(metadata.source.work_url)),
        "chapter_index": (record.chapter_index, chapter.chapter_index),
        "chapter_url": (str(record.chapter_url), str(chapter.chapter_url)),
        "retrieved_at_utc": (record.retrieved_at_utc, page.retrieved_at_utc),
        "published_date_displayed": (
            record.published_date_displayed,
            metadata.discovery.published_date_displayed,
        ),
        "updated_date_displayed": (
            record.updated_date_displayed,
            metadata.discovery.updated_date_displayed,
        ),
        "expected_available_chapter_count": (
            record.expected_available_chapter_count,
            metadata.source.expected_available_chapter_count,
        ),
        "raw_html_path": (record.raw_html_path, page.raw_html_path),
    }
    return [
        field
        for field, (manifest_value, metadata_value) in comparisons.items()
        if manifest_value != metadata_value
    ]


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def _load_optional_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return _load_json_object(path)


def _load_capture_metadata(path: Path) -> _CaptureMetadata:
    value = _load_json_object(path)
    capture_id = value.get("capture_id")
    if not isinstance(capture_id, str) or not capture_id:
        raise ValueError("metadata capture_id must be a non-empty string")
    pages = value.get("pages")
    if not isinstance(pages, list):
        raise ValueError("metadata pages must be a JSON array")
    return _CaptureMetadata(
        capture_id=capture_id,
        source=SourceRecord.model_validate(value.get("source")),
        discovery=WorkDiscovery.model_validate(value.get("discovery")),
        pages=[CapturedPage.model_validate(page) for page in pages],
    )


def _load_or_error(
    loader: Callable[[], Any],
    *,
    empty: Any,
) -> tuple[Any, str | None]:
    try:
        return loader(), None
    except Exception as error:
        return empty, f"{type(error).__name__}: {error}"


def _load_manifest_records(
    path: Path,
) -> list[ManifestRecord]:
    records: list[ManifestRecord] = []
    for line in path.read_text("utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        records.append(ManifestRecord.model_validate(value))
    return records


def _select_manifest_records(
    records: list[ManifestRecord],
    *,
    source_id: str,
    capture_id: str,
) -> list[ManifestRecord]:
    capture_prefix = (
        DATASET_DIRECTORY
        / "works"
        / source_id
        / "captures"
        / capture_id
    )

    def belongs_to_capture(record: ManifestRecord) -> bool:
        if record.source_id == source_id and record.capture_id == capture_id:
            return True
        for field in HASH_FIELDS:
            value = getattr(record, field)
            if value.parts[: len(capture_prefix.parts)] == capture_prefix.parts:
                return True
        return False

    return [record for record in records if belongs_to_capture(record)]


def _bind_artifact_paths(
    *,
    capture_dir: Path,
    dataset_root: Path,
    source_id: str,
    capture_id: str,
    metadata: _CaptureMetadata | None,
    records: list[ManifestRecord],
) -> list[dict[str, Path]]:
    if metadata is None:
        raise ValueError("metadata dependency is unavailable")
    capture_relative = (
        DATASET_DIRECTORY
        / "works"
        / source_id
        / "captures"
        / capture_id
    )
    complete_name = canonical_complete_pdf_name(metadata.discovery)
    bindings: list[dict[str, Path]] = []
    for record in records:
        index = record.chapter_index
        expected = {
            "raw_html_path": (
                capture_relative / "raw" / f"chapter-{index:03d}.html"
            ),
            "clean_html_path": (
                capture_relative / "clean" / f"chapter-{index:03d}.html"
            ),
            "text_path": (
                capture_relative / "text" / f"chapter-{index:03d}.md"
            ),
            "chapter_pdf_path": (
                capture_relative / "pdf" / f"chapter-{index:03d}.pdf"
            ),
            "complete_pdf_path": capture_relative / "pdf" / complete_name,
        }
        bound: dict[str, Path] = {}
        for field, expected_relative in expected.items():
            manifest_relative = getattr(record, field)
            if manifest_relative != expected_relative:
                raise ValueError(
                    f"manifest {field} is not the canonical current-capture "
                    f"path for chapter {index}"
                )
            candidate = dataset_root.parents[1] / manifest_relative
            expected_absolute = capture_dir / expected_relative.relative_to(
                capture_relative
            )
            if candidate != expected_absolute:
                raise ValueError(
                    f"manifest {field} is not confined to the canonical capture"
                )
            _require_canonical_regular_file(
                candidate,
                capture_dir=capture_dir,
                dataset_root=dataset_root,
            )
            bound[field] = candidate
        bindings.append(bound)
    return bindings


def _require_canonical_regular_file(
    path: Path,
    *,
    capture_dir: Path,
    dataset_root: Path,
) -> None:
    try:
        dataset_resolved = dataset_root.resolve(strict=True)
        capture_resolved = capture_dir.resolve(strict=True)
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError(f"canonical artifact is unavailable: {path}") from error
    if dataset_resolved != dataset_root or capture_resolved != capture_dir:
        raise ValueError("dataset or capture path contains a symlink component")
    if resolved != path:
        raise ValueError(f"canonical artifact contains a symlink: {path}")
    if (
        not capture_resolved.is_relative_to(dataset_resolved)
        or not resolved.is_relative_to(capture_resolved)
    ):
        raise ValueError(f"canonical artifact escapes its capture: {path}")
    relative = path.relative_to(dataset_root)
    components = [dataset_root]
    current = dataset_root
    for part in relative.parts:
        current = current / part
        components.append(current)
    for position, component in enumerate(components):
        try:
            status = component.lstat()
        except OSError as error:
            raise ValueError(
                f"canonical artifact component is unavailable: {component}"
            ) from error
        if stat.S_ISLNK(status.st_mode):
            raise ValueError(
                f"canonical artifact contains a symlink component: {component}"
            )
        if position < len(components) - 1 and not stat.S_ISDIR(status.st_mode):
            raise ValueError(
                f"canonical artifact parent is not a directory: {component}"
            )
    if not stat.S_ISREG(components[-1].lstat().st_mode):
        raise ValueError(f"canonical artifact is not a regular file: {path}")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_validation(path: Path, validation: WorkValidation) -> None:
    payload = (
        json.dumps(
            validation.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
