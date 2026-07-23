from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import fitz
import pytest

import scripts.fanfic_dataset.validate as validation_module
from scripts.fanfic_dataset.models import CheckResult, WorkValidation
from scripts.fanfic_dataset.validate import validate_work


DATASET_DIRECTORY = Path("data/fanfic-hogwarts-history")
CHECK_IDS = {
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
    "manual_spot_checks",
}
HASH_FIELDS = {
    "raw_html_path": "raw_sha256",
    "clean_html_path": "clean_html_sha256",
    "text_path": "text_sha256",
    "chapter_pdf_path": "chapter_pdf_sha256",
    "complete_pdf_path": "complete_pdf_sha256",
}
MANIFEST_DEPENDENT_CHECK_IDS = {
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
PROSE = {
    1: (
        "An invented brass compass rested beside the quiet ledger while "
        "careful researchers compared every synthetic entry.",
        "Beyond the imaginary window, a paper lantern marked the final line "
        "of this entirely fabricated opening chapter.",
    ),
    2: (
        "A fictional archivist arranged the harmless sample pages in order "
        "and checked each deliberately invented transition.",
        "At the close of the synthetic account, the empty reading room "
        "settled into a calm and wholly imaginary silence.",
    ),
}


def test_captured_count_must_match_displayed_count(tmp_path: Path) -> None:
    _, capture_dir, manual_review = _synthetic_capture(tmp_path)
    metadata = _read_json(capture_dir / "metadata.json")
    metadata["source"]["expected_available_chapter_count"] = 3
    _write_json(capture_dir / "metadata.json", metadata)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "chapter_count")


@pytest.mark.parametrize("problem", ["duplicate-index", "gap-index", "duplicate-url"])
def test_chapter_indexes_and_urls_must_be_unique_and_consecutive(
    tmp_path: Path,
    problem: str,
) -> None:
    _, capture_dir, manual_review = _synthetic_capture(tmp_path)
    metadata = _read_json(capture_dir / "metadata.json")
    if problem == "duplicate-index":
        replacement = 1
        metadata["discovery"]["chapters"][1]["chapter_index"] = replacement
        metadata["pages"][1]["chapter"]["chapter_index"] = replacement
    elif problem == "gap-index":
        replacement = 3
        metadata["discovery"]["chapters"][1]["chapter_index"] = replacement
        metadata["pages"][1]["chapter"]["chapter_index"] = replacement
    else:
        duplicate = metadata["discovery"]["chapters"][0]["chapter_url"]
        metadata["discovery"]["chapters"][1]["chapter_url"] = duplicate
        metadata["pages"][1]["chapter"]["chapter_url"] = duplicate
    _write_json(capture_dir / "metadata.json", metadata)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "chapter_sequence")


@pytest.mark.parametrize("missing_title", [None, "", "   "])
def test_missing_title_requires_explicit_title_missing_record(
    tmp_path: Path,
    missing_title: str | None,
) -> None:
    _, capture_dir, manual_review = _synthetic_capture(tmp_path)
    metadata = _read_json(capture_dir / "metadata.json")
    metadata["discovery"]["chapters"][0]["chapter_title"] = missing_title
    metadata["pages"][0]["chapter"]["chapter_title"] = missing_title
    _write_json(capture_dir / "metadata.json", metadata)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "chapter_titles")


def test_empty_story_text_fails_validation(tmp_path: Path) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    clean_path = capture_dir / "clean/chapter-001.html"
    clean_path.write_text(
        "<!doctype html><main data-role='story'>  </main>",
        encoding="utf-8",
    )
    _refresh_manifest(dataset_root)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "story_text")


@pytest.mark.parametrize("artifact", ["raw", "clean"])
@pytest.mark.parametrize(
    "denial_text",
    ["Checking your browser", "Access denied", "CAPTCHA", "Page not found"],
)
def test_raw_and_clean_html_reject_access_denial_responses(
    tmp_path: Path,
    artifact: str,
    denial_text: str,
) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    path = capture_dir / artifact / "chapter-001.html"
    path.write_text(
        path.read_text("utf-8") + f"<aside>{denial_text}</aside>",
        encoding="utf-8",
    )
    _refresh_manifest(dataset_root)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "access_denial")


def test_access_denial_scan_accepts_lossless_non_utf8_raw_bytes(
    tmp_path: Path,
) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    raw_path = capture_dir / "raw/chapter-001.html"
    raw_path.write_bytes(raw_path.read_bytes() + b"<p>Invented price: \x80 7.</p>")
    _refresh_manifest(dataset_root)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    assert _check(result, "access_denial").passed


def test_clean_html_rejects_known_site_chrome(tmp_path: Path) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    clean_path = capture_dir / "clean/chapter-001.html"
    clean_path.write_text(
        clean_path.read_text("utf-8")
        + "<nav id='content_wrapper'><a>Post Review</a></nav>",
        encoding="utf-8",
    )
    _refresh_manifest(dataset_root)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "site_chrome")


def test_first_and_last_substantial_markdown_paragraphs_must_reach_pdf(
    tmp_path: Path,
) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    _write_pdf(capture_dir / "pdf/chapter-001.pdf", [PROSE[1][1]])
    _refresh_manifest(dataset_root)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "markdown_pdf_boundaries")


def test_pdf_markdown_visible_text_ratio_must_stay_within_bounds(
    tmp_path: Path,
) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    markdown = capture_dir / "text/chapter-001.md"
    markdown.write_text(
        markdown.read_text("utf-8")
        + "\n\n"
        + " ".join(["Invented expansion"] * 80)
        + "\n",
        encoding="utf-8",
    )
    _refresh_manifest(dataset_root)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "pdf_markdown_ratio")


def test_pdf_semantic_html_visible_text_ratio_must_stay_within_bounds(
    tmp_path: Path,
) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    clean = capture_dir / "clean/chapter-001.html"
    clean.write_text(
        clean.read_text("utf-8").replace(
            "</main>",
            "<section data-block-kind='chapter-text'><p>"
            + " ".join(["Fabricated appendix"] * 80)
            + "</p></section></main>",
        ),
        encoding="utf-8",
    )
    _refresh_manifest(dataset_root)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "pdf_semantic_html_ratio")


def test_complete_pdf_bookmark_count_must_match_chapter_count(
    tmp_path: Path,
) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    complete = _complete_pdf_path(capture_dir)
    _write_pdf(complete, [*PROSE[1], *PROSE[2]], toc_count=1)
    _refresh_manifest(dataset_root)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "pdf_bookmarks")


def test_stored_hashes_must_match_current_artifacts(tmp_path: Path) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    records = _manifest_records(dataset_root)
    records[0]["text_sha256"] = "0" * 64
    _write_manifest(dataset_root, records)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "artifact_hashes")


def test_annotations_must_reference_known_semantic_block_hashes(
    tmp_path: Path,
) -> None:
    _, capture_dir, manual_review = _synthetic_capture(tmp_path)
    annotations = _read_json(capture_dir / "annotations.json")
    annotations["chapter-001"]["author_note_block_sha256"] = ["f" * 64]
    _write_json(capture_dir / "annotations.json", annotations)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "annotation_hashes")


def test_annotation_for_unknown_chapter_cannot_hide_an_unknown_block_hash(
    tmp_path: Path,
) -> None:
    _, capture_dir, manual_review = _synthetic_capture(tmp_path)
    annotations = _read_json(capture_dir / "annotations.json")
    annotations["chapter-999"] = {
        "author_note_block_sha256": ["e" * 64],
        "missing_chapter_notice_block_sha256": [],
    }
    _write_json(capture_dir / "annotations.json", annotations)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "annotation_hashes")


def test_required_manual_spot_checks_must_be_signed(tmp_path: Path) -> None:
    _, capture_dir, manual_review = _synthetic_capture(tmp_path)
    _write_json(manual_review, {})

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "manual_spot_checks")
    assert result.status == "manual-review-pending"


def test_all_checks_run_and_automated_failure_overrides_manual_pending(
    tmp_path: Path,
) -> None:
    _, capture_dir, manual_review = _synthetic_capture(tmp_path)
    metadata = _read_json(capture_dir / "metadata.json")
    metadata["source"]["expected_available_chapter_count"] = 3
    metadata["discovery"]["chapters"][0]["chapter_title"] = ""
    metadata["pages"][0]["chapter"]["chapter_title"] = ""
    _write_json(capture_dir / "metadata.json", metadata)
    _write_json(manual_review, {})

    result = validate_work(capture_dir, manual_review_path=manual_review)

    assert {check.check_id for check in result.checks} == CHECK_IDS
    assert not _check(result, "chapter_count").passed
    assert not _check(result, "chapter_titles").passed
    assert not _check(result, "manual_spot_checks").passed
    assert result.status == "fail"


def test_missing_manifest_does_not_hide_later_validation_checks(
    tmp_path: Path,
) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    (dataset_root / "manifest.jsonl").unlink()

    result = validate_work(capture_dir, manual_review_path=manual_review)

    assert {check.check_id for check in result.checks} == CHECK_IDS
    _assert_dependency_failures(
        result,
        MANIFEST_DEPENDENT_CHECK_IDS,
        "manifest",
    )
    assert result.status == "fail"


def test_manifest_loader_rejects_records_that_are_not_full_manifest_records(
    tmp_path: Path,
) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    records = _manifest_records(dataset_root)
    del records[0]["tool_version"]
    _write_manifest(dataset_root, records)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_dependency_failures(
        result,
        MANIFEST_DEPENDENT_CHECK_IDS,
        "manifest",
    )
    _assert_failed(result, "chapter_count")
    _assert_failed(result, "chapter_sequence")
    _assert_failed(result, "chapter_titles")


@pytest.mark.parametrize(
    ("field", "value", "check_id"),
    [
        ("source_id", "HAH-FAN-099", "chapter_sequence"),
        ("capture_id", "20260723T130000Z", "chapter_sequence"),
        (
            "chapter_url",
            "https://www.fanfiction.net/s/700/9/invented-history",
            "chapter_sequence",
        ),
        ("chapter_title", "Tampered Invented Title", "chapter_titles"),
        ("title_missing", True, "chapter_titles"),
        ("expected_available_chapter_count", 9, "chapter_count"),
        ("author", "Different Synthetic Author", "chapter_sequence"),
        ("retrieved_at_utc", "2026-07-23T13:00:00Z", "chapter_sequence"),
    ],
)
def test_manifest_must_exactly_agree_with_capture_metadata(
    tmp_path: Path,
    field: str,
    value: object,
    check_id: str,
) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    records = _manifest_records(dataset_root)
    records[0][field] = value
    _write_manifest(dataset_root, records)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, check_id)


def test_manifest_order_and_indexes_are_not_repaired_by_the_loader(
    tmp_path: Path,
) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    records = list(reversed(_manifest_records(dataset_root)))
    _write_manifest(dataset_root, records)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "chapter_sequence")


@pytest.mark.parametrize("second_index", [1, 3])
def test_manifest_duplicate_or_gapped_indexes_fail_sequence_validation(
    tmp_path: Path,
    second_index: int,
) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    records = _manifest_records(dataset_root)
    records[1]["chapter_index"] = second_index
    _write_manifest(dataset_root, records)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "chapter_sequence")


@pytest.mark.parametrize(
    "problem",
    [
        "cross-chapter",
        "cross-capture",
        "traversal",
        "noncanonical-complete",
    ],
)
def test_manifest_artifact_paths_must_bind_to_current_canonical_capture_paths(
    tmp_path: Path,
    problem: str,
) -> None:
    dataset_root, capture_dir, manual_review = _synthetic_capture(tmp_path)
    records = _manifest_records(dataset_root)
    if problem == "cross-chapter":
        for path_field, hash_field in HASH_FIELDS.items():
            if path_field != "complete_pdf_path":
                records[0][path_field] = records[1][path_field]
                records[0][hash_field] = records[1][hash_field]
    elif problem == "cross-capture":
        alternate_capture = capture_dir.with_name("20260723T130000Z")
        shutil.copytree(capture_dir, alternate_capture)
        for path_field, hash_field in HASH_FIELDS.items():
            if path_field != "complete_pdf_path":
                path = alternate_capture / {
                    "raw_html_path": "raw/chapter-001.html",
                    "clean_html_path": "clean/chapter-001.html",
                    "text_path": "text/chapter-001.md",
                    "chapter_pdf_path": "pdf/chapter-001.pdf",
                }[path_field]
                records[0][path_field] = str(
                    DATASET_DIRECTORY / path.relative_to(dataset_root)
                )
                records[0][hash_field] = _sha256(path)
    elif problem == "traversal":
        records[0]["raw_html_path"] = str(
            DATASET_DIRECTORY
            / "works"
            / "HAH-FAN-001"
            / "captures"
            / "20260723T130000Z"
            / ".."
            / "20260723T120000Z"
            / "raw"
            / "chapter-001.html"
        )
    else:
        canonical = _complete_pdf_path(capture_dir)
        alternate = canonical.with_name("invented-complete.pdf")
        shutil.copyfile(canonical, alternate)
        records[0]["complete_pdf_path"] = str(
            DATASET_DIRECTORY / alternate.relative_to(dataset_root)
        )
        records[0]["complete_pdf_sha256"] = _sha256(alternate)
    _write_manifest(dataset_root, records)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_dependency_failures(
        result,
        MANIFEST_DEPENDENT_CHECK_IDS,
        "canonical",
    )


@pytest.mark.parametrize("symlink_kind", ["parent", "leaf"])
def test_manifest_artifact_binding_rejects_symlink_components_and_leaves(
    tmp_path: Path,
    symlink_kind: str,
) -> None:
    _, capture_dir, manual_review = _synthetic_capture(tmp_path)
    if symlink_kind == "parent":
        raw = capture_dir / "raw"
        real_raw = capture_dir / "raw-real"
        raw.rename(real_raw)
        raw.symlink_to(real_raw, target_is_directory=True)
    else:
        text = capture_dir / "text/chapter-001.md"
        real_text = capture_dir / "text/chapter-001-real.md"
        text.rename(real_text)
        text.symlink_to(real_text)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_dependency_failures(
        result,
        MANIFEST_DEPENDENT_CHECK_IDS,
        "symlink",
    )


@pytest.mark.parametrize("problem", ["missing", "malformed"])
def test_missing_or_malformed_metadata_fails_every_dependent_check(
    tmp_path: Path,
    problem: str,
) -> None:
    _, capture_dir, manual_review = _synthetic_capture(tmp_path)
    metadata_path = capture_dir / "metadata.json"
    if problem == "missing":
        metadata_path.unlink()
    else:
        _write_json(metadata_path, {"capture_id": "not-a-capture"})

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_dependency_failures(result, CHECK_IDS, "metadata")
    assert result.status == "fail"


def test_source_discovery_provenance_disagreement_is_not_vacuously_valid(
    tmp_path: Path,
) -> None:
    _, capture_dir, manual_review = _synthetic_capture(tmp_path)
    metadata = _read_json(capture_dir / "metadata.json")
    metadata["discovery"]["author"] = "Contradictory Synthetic Author"
    _write_json(capture_dir / "metadata.json", metadata)

    result = validate_work(capture_dir, manual_review_path=manual_review)

    _assert_failed(result, "chapter_sequence")


def test_signed_valid_capture_passes_and_persists_deterministically(
    tmp_path: Path,
) -> None:
    _, capture_dir, manual_review = _synthetic_capture(tmp_path)

    first = validate_work(capture_dir, manual_review_path=manual_review)
    first_bytes = (capture_dir / "validation.json").read_bytes()
    second = validate_work(capture_dir, manual_review_path=manual_review)

    assert first.status == "pass"
    assert all(check.passed for check in first.checks)
    assert second == first
    assert (capture_dir / "validation.json").read_bytes() == first_bytes
    assert first_bytes.endswith(b"\n")
    assert json.loads(first_bytes) == first.model_dump(mode="json")


def test_dataset_summary_and_exit_status_are_ready_for_cli_consumers(
    tmp_path: Path,
) -> None:
    _, capture_dir, manual_review = _synthetic_capture(tmp_path)
    passed = validate_work(capture_dir, manual_review_path=manual_review)
    pending = passed.model_copy(update={"status": "manual-review-pending"})
    failed = passed.model_copy(update={"status": "fail"})
    summarize = getattr(validation_module, "summarize_validations", None)
    exit_status = getattr(validation_module, "validation_exit_status", None)

    assert callable(summarize)
    assert callable(exit_status)
    assert summarize([failed, passed, pending]) == {
        "total": 3,
        "pass": 1,
        "fail": 1,
        "manual-review-pending": 1,
        "exit_status": 1,
    }
    assert summarize([])["exit_status"] == 1
    assert exit_status(passed) == 0
    assert exit_status(pending) == 1
    assert exit_status(failed) == 1


def _assert_failed(result: WorkValidation, check_id: str) -> None:
    check = next(
        (candidate for candidate in result.checks if candidate.check_id == check_id),
        None,
    )
    assert check is not None, f"missing validation check {check_id!r}"
    assert not check.passed
    assert check.detail
    assert result.status != "pass"


def _check(result: WorkValidation, check_id: str) -> CheckResult:
    return next(check for check in result.checks if check.check_id == check_id)


def _assert_dependency_failures(
    result: WorkValidation,
    check_ids: set[str],
    dependency: str,
) -> None:
    for check_id in check_ids:
        check = _check(result, check_id)
        assert not check.passed, check_id
        assert dependency in check.detail.casefold(), (check_id, check.detail)


def _synthetic_capture(tmp_path: Path) -> tuple[Path, Path, Path]:
    source_id = "HAH-FAN-001"
    capture_id = "20260723T120000Z"
    dataset_root = tmp_path / DATASET_DIRECTORY
    capture_dir = (
        dataset_root / "works" / source_id / "captures" / capture_id
    )
    for directory in ("raw", "clean", "text", "pdf"):
        (capture_dir / directory).mkdir(parents=True, exist_ok=True)

    chapters = []
    pages = []
    for index in (1, 2):
        title = f"Invented Chapter {index}"
        url = f"https://www.fanfiction.net/s/700/{index}/invented-history"
        chapters.append(
            {
                "chapter_index": index,
                "chapter_title": title,
                "title_missing": False,
                "chapter_url": url,
            }
        )
        pages.append(
            {
                "source_id": source_id,
                "chapter": chapters[-1],
                "retrieved_at_utc": "2026-07-23T12:00:00Z",
                "final_url": url,
                "status": 200,
                "raw_html_path": str(
                    DATASET_DIRECTORY
                    / "works"
                    / source_id
                    / "captures"
                    / capture_id
                    / "raw"
                    / f"chapter-{index:03d}.html"
                ),
            }
        )
        block_text = " ".join(PROSE[index])
        block_hash = hashlib.sha256(block_text.encode("utf-8")).hexdigest()
        (capture_dir / f"raw/chapter-{index:03d}.html").write_text(
            "<!doctype html><html><body><div id='storytext'>"
            + "".join(f"<p>{paragraph}</p>" for paragraph in PROSE[index])
            + "</div></body></html>",
            encoding="utf-8",
        )
        (capture_dir / f"clean/chapter-{index:03d}.html").write_text(
            "<!doctype html><html><body><main data-role='story'>"
            f"<section data-block-kind='chapter-text' data-sha256='{block_hash}'>"
            + "".join(f"<p>{paragraph}</p>" for paragraph in PROSE[index])
            + "</section></main></body></html>",
            encoding="utf-8",
        )
        (capture_dir / f"text/chapter-{index:03d}.md").write_text(
            "<!-- BEGIN CHAPTER TEXT -->\n\n"
            + "\n\n".join(PROSE[index])
            + "\n\n<!-- END CHAPTER TEXT -->\n",
            encoding="utf-8",
        )
        _write_pdf(
            capture_dir / f"pdf/chapter-{index:03d}.pdf",
            list(PROSE[index]),
        )

    metadata = {
        "capture_id": capture_id,
        "source": {
            "source_id": source_id,
            "work_title": "Invented Archive History",
            "author": "Synthetic Researcher",
            "platform": "fanfiction.net",
            "work_url": "https://www.fanfiction.net/s/700/1/invented-history",
            "expected_available_chapter_count": 2,
            "status": "core",
        },
        "discovery": {
            "source_id": source_id,
            "work_id": "700",
            "work_title": "Invented Archive History",
            "author": "Synthetic Researcher",
            "summary": "Entirely invented material for local validation tests.",
            "rating": None,
            "language": "English",
            "displayed_word_count": 88,
            "published_date_displayed": None,
            "updated_date_displayed": None,
            "chapters": chapters,
        },
        "pages": pages,
    }
    _write_json(capture_dir / "metadata.json", metadata)
    _write_json(
        capture_dir / "annotations.json",
        {
            "chapter-001": {
                "author_note_block_sha256": [],
                "missing_chapter_notice_block_sha256": [],
                "reviewed_by": "Synthetic Operator",
                "reviewed_at_utc": "2026-07-23T12:30:00Z",
            },
            "chapter-002": {
                "author_note_block_sha256": [],
                "missing_chapter_notice_block_sha256": [],
                "reviewed_by": "Synthetic Operator",
                "reviewed_at_utc": "2026-07-23T12:30:00Z",
            },
        },
    )
    complete = capture_dir / "pdf/HAH-FAN-001__invented-archive-history__synthetic-researcher.pdf"
    _write_pdf(complete, [*PROSE[1], *PROSE[2]], toc_count=2)
    _write_manifest_from_capture(dataset_root, capture_dir, complete)

    manual_review = dataset_root / "reports/manual-review.json"
    manual_review.parent.mkdir(parents=True)
    _write_json(
        manual_review,
        {
            f"{source_id}/{capture_id}": {
                "reviewed_by": "Synthetic Operator",
                "reviewed_at_utc": "2026-07-23T12:45:00Z",
                "first_chapter": True,
                "final_chapter": True,
                "longest_chapter": True,
                "chapter_transitions": True,
                "author_note_or_missing_notice_chapters": [],
                "notes": "Compared the invented rendered pages with the synthetic fixture.",
            }
        },
    )
    return dataset_root, capture_dir, manual_review


def _write_manifest_from_capture(
    dataset_root: Path,
    capture_dir: Path,
    complete: Path,
) -> None:
    metadata = _read_json(capture_dir / "metadata.json")
    records = []
    for page in metadata["pages"]:
        index = page["chapter"]["chapter_index"]
        paths = {
            "raw_html_path": capture_dir / f"raw/chapter-{index:03d}.html",
            "clean_html_path": capture_dir / f"clean/chapter-{index:03d}.html",
            "text_path": capture_dir / f"text/chapter-{index:03d}.md",
            "chapter_pdf_path": capture_dir / f"pdf/chapter-{index:03d}.pdf",
            "complete_pdf_path": complete,
        }
        record = {
            "dataset_version": "1.0",
            "source_id": metadata["source"]["source_id"],
            "capture_id": metadata["capture_id"],
            "work_title": metadata["discovery"]["work_title"],
            "author": metadata["discovery"]["author"],
            "platform": metadata["source"]["platform"],
            "work_url": metadata["source"]["work_url"],
            "chapter_index": index,
            "chapter_title": page["chapter"]["chapter_title"],
            "title_missing": page["chapter"]["title_missing"],
            "chapter_url": page["chapter"]["chapter_url"],
            "retrieved_at_utc": page["retrieved_at_utc"],
            "published_date_displayed": metadata["discovery"][
                "published_date_displayed"
            ],
            "updated_date_displayed": metadata["discovery"][
                "updated_date_displayed"
            ],
            "expected_available_chapter_count": metadata["source"][
                "expected_available_chapter_count"
            ],
            "fan_created": True,
            "canon_status": "non-canon fanfiction",
            "dataset_role": "style-and-coverage-reference",
            "tool_version": "1.0.0",
        }
        for path_field, hash_field in HASH_FIELDS.items():
            path = paths[path_field]
            record[path_field] = str(
                DATASET_DIRECTORY / path.relative_to(dataset_root)
            )
            record[hash_field] = _sha256(path)
        records.append(record)
    _write_manifest(dataset_root, records)


def _refresh_manifest(dataset_root: Path) -> None:
    records = _manifest_records(dataset_root)
    project_root = dataset_root.parents[1]
    for record in records:
        for path_field, hash_field in HASH_FIELDS.items():
            record[hash_field] = _sha256(project_root / record[path_field])
    _write_manifest(dataset_root, records)


def _manifest_records(dataset_root: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in (dataset_root / "manifest.jsonl").read_text("utf-8").splitlines()
    ]


def _write_manifest(dataset_root: Path, records: list[dict[str, object]]) -> None:
    payload = "".join(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    )
    (dataset_root / "manifest.jsonl").write_text(payload, encoding="utf-8")


def _write_pdf(path: Path, paragraphs: list[str], toc_count: int | None = None) -> None:
    with fitz.open() as document:
        for paragraph in paragraphs:
            page = document.new_page()
            page.insert_textbox(
                fitz.Rect(50, 50, 545, 790),
                paragraph,
                fontsize=11,
                fontname="tiro",
            )
        if toc_count is not None:
            document.set_toc(
                [
                    [1, f"Invented Chapter {index}", min(index, len(paragraphs))]
                    for index in range(1, toc_count + 1)
                ]
            )
        document.save(path)


def _complete_pdf_path(capture_dir: Path) -> Path:
    return next(
        path
        for path in (capture_dir / "pdf").glob("*.pdf")
        if not path.name.startswith("chapter-")
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text("utf-8"))


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
