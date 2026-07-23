import hashlib
import json
import re
from pathlib import Path

import pytest

from scripts.fanfic_dataset.build_manifest import build_manifest, promote_latest
from scripts.fanfic_dataset.merge_pdf import canonical_complete_pdf_name
from scripts.fanfic_dataset.models import CheckResult, WorkDiscovery, WorkValidation


DATASET_DIRECTORY = Path("data/fanfic-hogwarts-history")
HASH_FIELDS = {
    "raw_html_path": "raw_sha256",
    "clean_html_path": "clean_html_sha256",
    "text_path": "text_sha256",
    "chapter_pdf_path": "chapter_pdf_sha256",
    "complete_pdf_path": "complete_pdf_sha256",
}


def test_build_manifest_is_global_sorted_hashed_and_byte_deterministic(
    tmp_path: Path,
) -> None:
    dataset_root, requested_capture = _synthetic_capture(
        tmp_path,
        source_id="HAH-FAN-002",
        capture_id="20260723T140000Z",
        chapter_count=1,
    )
    _synthetic_capture(
        tmp_path,
        source_id="HAH-FAN-001",
        capture_id="20260723T150000Z",
        chapter_count=2,
    )
    _synthetic_capture(
        tmp_path,
        source_id="HAH-FAN-002",
        capture_id="20260723T120000Z",
        chapter_count=2,
    )
    _synthetic_capture(
        tmp_path,
        source_id="HAH-FAN-001",
        capture_id="20260723T130000Z",
        chapter_count=1,
    )

    returned_records = build_manifest(requested_capture)
    manifest_path = dataset_root / "manifest.jsonl"
    first_payload = manifest_path.read_bytes()
    repeated_records = build_manifest(requested_capture)

    expected_order = [
        ("HAH-FAN-001", "20260723T130000Z", 1),
        ("HAH-FAN-001", "20260723T150000Z", 1),
        ("HAH-FAN-001", "20260723T150000Z", 2),
        ("HAH-FAN-002", "20260723T120000Z", 1),
        ("HAH-FAN-002", "20260723T120000Z", 2),
        ("HAH-FAN-002", "20260723T140000Z", 1),
    ]
    returned_order = [
        (record.source_id, record.capture_id, record.chapter_index)
        for record in returned_records
    ]
    assert returned_order == expected_order
    assert [
        (record.source_id, record.capture_id, record.chapter_index)
        for record in repeated_records
    ] == expected_order
    assert ("HAH-FAN-002", requested_capture.name, 1) in returned_order
    assert manifest_path.read_bytes() == first_payload
    assert first_payload.endswith(b"\n")

    records = [json.loads(line) for line in first_payload.splitlines()]
    assert len(records) == len(expected_order)
    for line, record in zip(first_payload.splitlines(), records, strict=True):
        assert line == json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        complete_paths = {
            candidate["complete_pdf_path"]
            for candidate in records
            if (
                candidate["source_id"],
                candidate["capture_id"],
            )
            == (record["source_id"], record["capture_id"])
        }
        assert len(complete_paths) == 1
        assert Path(record["complete_pdf_path"]).name == (
            f"{record['source_id']}__invented-history-"
            f"{record['source_id'].lower()}__invented-author-"
            f"{record['source_id'].lower()}.pdf"
        )
        for path_field, hash_field in HASH_FIELDS.items():
            relative_path = Path(record[path_field])
            artifact = tmp_path / relative_path
            assert not relative_path.is_absolute()
            assert str(relative_path).startswith(f"{DATASET_DIRECTORY}/")
            assert record[hash_field] == hashlib.sha256(
                artifact.read_bytes()
            ).hexdigest()
            assert re.fullmatch(r"[0-9a-f]{64}", record[hash_field])
        assert record["fan_created"] is True
        assert record["canon_status"] == "non-canon fanfiction"
    assert not list((dataset_root / "works").glob("*/latest.json"))


@pytest.mark.parametrize(
    "argument_kind",
    ["dataset-root", "captures-directory", "nested-directory", "dotdot-alias"],
)
def test_build_manifest_rejects_noncanonical_or_unincluded_argument(
    tmp_path: Path,
    argument_kind: str,
) -> None:
    dataset_root, capture_dir = _synthetic_capture(tmp_path)
    arguments = {
        "dataset-root": dataset_root,
        "captures-directory": capture_dir.parent,
        "nested-directory": capture_dir / "raw",
        "dotdot-alias": capture_dir / "raw" / "..",
    }

    with pytest.raises(ValueError, match="canonical capture"):
        build_manifest(arguments[argument_kind])

    assert not (dataset_root / "manifest.jsonl").exists()


@pytest.mark.parametrize("problem", ["missing", "absolute", "outside", "gap"])
def test_build_manifest_rejects_invalid_capture_inputs(
    tmp_path: Path, problem: str
) -> None:
    _, capture_dir = _synthetic_capture(tmp_path)
    metadata_path = capture_dir / "metadata.json"
    if problem == "missing":
        (capture_dir / "text/chapter-002.md").unlink()
    elif problem == "absolute":
        metadata = json.loads(metadata_path.read_text("utf-8"))
        metadata["pages"][0]["raw_html_path"] = "/tmp/chapter-001.html"
        metadata_path.write_text(json.dumps(metadata), "utf-8")
    elif problem == "outside":
        metadata = json.loads(metadata_path.read_text("utf-8"))
        metadata["pages"][0]["raw_html_path"] = "../other/chapter-001.html"
        metadata_path.write_text(json.dumps(metadata), "utf-8")
    else:
        metadata = json.loads(metadata_path.read_text("utf-8"))
        metadata["pages"][1]["chapter"]["chapter_index"] = 3
        metadata_path.write_text(json.dumps(metadata), "utf-8")

    with pytest.raises(ValueError):
        build_manifest(capture_dir)


@pytest.mark.parametrize(
    "problem",
    [
        "page-source",
        "chapter-title",
        "chapter-url",
        "wrong-chapter-raw",
        "noncanonical-current-raw",
    ],
)
def test_build_manifest_binds_each_page_and_raw_artifact_to_current_capture(
    tmp_path: Path,
    problem: str,
) -> None:
    _, capture_dir = _synthetic_capture(tmp_path)
    metadata_path = capture_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text("utf-8"))
    page = metadata["pages"][0]
    if problem == "page-source":
        page["source_id"] = "HAH-FAN-999"
    elif problem == "chapter-title":
        page["chapter"]["chapter_title"] = "Invented mismatched title"
    elif problem == "chapter-url":
        page["chapter"]["chapter_url"] = (
            "https://www.fanfiction.net/s/999/1/synthetic"
        )
    elif problem == "wrong-chapter-raw":
        page["raw_html_path"] = str(
            DATASET_DIRECTORY
            / "works"
            / "HAH-FAN-001"
            / "captures"
            / capture_dir.name
            / "raw"
            / "chapter-002.html"
        )
    else:
        page["raw_html_path"] = str(
            DATASET_DIRECTORY
            / "works"
            / "HAH-FAN-001"
            / "captures"
            / capture_dir.name
            / "raw"
            / ".."
            / "raw"
            / "chapter-001.html"
        )
    metadata_path.write_text(json.dumps(metadata), "utf-8")

    with pytest.raises(ValueError, match="page|raw"):
        build_manifest(capture_dir)


def test_promote_latest_rejects_non_passing_validation(tmp_path: Path) -> None:
    validation = _validation(status="fail")

    with pytest.raises(ValueError, match="pass"):
        promote_latest(validation, dataset_root=tmp_path)


@pytest.mark.parametrize("source_id", ["../../escaped", "FAN-001"])
def test_promote_latest_rejects_traversal_and_noncanonical_source_ids(
    tmp_path: Path,
    source_id: str,
) -> None:
    dataset_root = tmp_path / "data/fanfic-hogwarts-history"

    with pytest.raises(ValueError, match="source_id"):
        promote_latest(
            _validation(source_id=source_id),
            dataset_root=dataset_root,
        )

    assert not (dataset_root.parent / "escaped/latest.json").exists()
    assert not (dataset_root / "works/FAN-001/latest.json").exists()


@pytest.mark.parametrize("symlink_kind", ["work-parent", "latest"])
def test_promote_latest_rejects_symlinked_write_destinations(
    tmp_path: Path,
    symlink_kind: str,
) -> None:
    dataset_root = tmp_path / "data/fanfic-hogwarts-history"
    works_root = dataset_root / "works"
    external = tmp_path / "external"
    external.mkdir(parents=True)
    works_root.mkdir(parents=True)
    external_latest = external / "latest.json"
    external_latest.write_bytes(b"preserve-external-bytes")
    work_root = works_root / "HAH-FAN-001"
    if symlink_kind == "work-parent":
        work_root.symlink_to(external, target_is_directory=True)
    else:
        work_root.mkdir()
        (work_root / "latest.json").symlink_to(external_latest)

    with pytest.raises(ValueError, match="symlink"):
        promote_latest(_validation(), dataset_root=dataset_root)

    assert external_latest.read_bytes() == b"preserve-external-bytes"
    if symlink_kind == "latest":
        assert (work_root / "latest.json").is_symlink()


def test_promote_latest_atomically_writes_deterministic_pointer(
    tmp_path: Path,
) -> None:
    dataset_root = tmp_path / "data/fanfic-hogwarts-history"
    validation = _validation()
    expected = (
        b'{"capture_id":"20260723T120000Z","source_id":"HAH-FAN-001"}\n'
    )

    latest_path = promote_latest(validation, dataset_root=dataset_root)
    first_bytes = latest_path.read_bytes()
    returned_again = promote_latest(validation, dataset_root=dataset_root)

    assert latest_path == (
        dataset_root / "works/HAH-FAN-001/latest.json"
    )
    assert returned_again == latest_path
    assert first_bytes == expected
    assert latest_path.read_bytes() == expected
    assert not list(latest_path.parent.glob(".latest.json.*"))


def _validation(
    *,
    source_id: str = "HAH-FAN-001",
    capture_id: str = "20260723T120000Z",
    status: str = "pass",
) -> WorkValidation:
    return WorkValidation(
        source_id=source_id,
        capture_id=capture_id,
        status=status,
        checks=[
            CheckResult(
                check_id="synthetic",
                passed=status == "pass",
                detail="Invented validation evidence.",
            )
        ],
    )


def _synthetic_capture(
    tmp_path: Path,
    *,
    source_id: str = "HAH-FAN-001",
    capture_id: str = "20260723T120000Z",
    chapter_count: int = 2,
) -> tuple[Path, Path]:
    dataset_root = tmp_path / DATASET_DIRECTORY
    capture_dir = (
        dataset_root / "works" / source_id / "captures" / capture_id
    )
    for directory in ("raw", "clean", "text", "pdf"):
        (capture_dir / directory).mkdir(parents=True, exist_ok=True)
    for chapter in range(1, chapter_count + 1):
        stem = f"chapter-{chapter:03d}"
        identity = f"{source_id}-{capture_id}-{chapter}"
        (capture_dir / f"raw/{stem}.html").write_bytes(
            f"<p>Invented raw {identity}.</p>".encode()
        )
        (capture_dir / f"clean/{stem}.html").write_bytes(
            f"<article>Invented clean {identity}.</article>".encode()
        )
        (capture_dir / f"text/{stem}.md").write_bytes(
            f"# Invented text {identity}\n".encode()
        )
        (capture_dir / f"pdf/{stem}.pdf").write_bytes(
            f"invented-pdf-{identity}".encode()
        )
    work_number = int(source_id.rsplit("-", 1)[1])
    metadata = {
        "capture_id": capture_id,
        "source": {
            "source_id": source_id,
            "work_title": f"Invented History {source_id}",
            "author": f"Invented Author {source_id}",
            "platform": "fanfiction.net",
            "work_url": (
                f"https://www.fanfiction.net/s/{work_number}/1/synthetic"
            ),
            "expected_available_chapter_count": chapter_count,
            "status": "core",
        },
        "discovery": {
            "source_id": source_id,
            "work_id": str(work_number),
            "work_title": f"Invented History {source_id}",
            "author": f"Invented Author {source_id}",
            "summary": "Invented synthetic prose only.",
            "rating": None,
            "language": "English",
            "displayed_word_count": chapter_count,
            "published_date_displayed": None,
            "updated_date_displayed": None,
            "chapters": [
                {
                    "chapter_index": chapter,
                    "chapter_title": f"Invented Chapter {chapter}",
                    "chapter_url": (
                        f"https://www.fanfiction.net/s/{work_number}/"
                        f"{chapter}/synthetic"
                    ),
                }
                for chapter in range(1, chapter_count + 1)
            ],
        },
        "pages": [
            {
                "source_id": source_id,
                "chapter": {
                    "chapter_index": chapter,
                    "chapter_title": f"Invented Chapter {chapter}",
                    "chapter_url": (
                        f"https://www.fanfiction.net/s/{work_number}/"
                        f"{chapter}/synthetic"
                    ),
                },
                "retrieved_at_utc": "2026-07-23T12:00:00Z",
                "final_url": (
                    f"https://www.fanfiction.net/s/{work_number}/"
                    f"{chapter}/synthetic"
                ),
                "status": 200,
                "raw_html_path": str(
                    DATASET_DIRECTORY
                    / "works"
                    / source_id
                    / "captures"
                    / capture_id
                    / "raw"
                    / f"chapter-{chapter:03d}.html"
                ),
            }
            for chapter in range(1, chapter_count + 1)
        ],
    }
    (capture_dir / "metadata.json").write_text(
        json.dumps(metadata), encoding="utf-8"
    )
    complete_pdf = capture_dir / "pdf" / canonical_complete_pdf_name(
        WorkDiscovery.model_validate(metadata["discovery"])
    )
    complete_pdf.write_bytes(
        f"invented-complete-{source_id}-{capture_id}".encode()
    )
    return dataset_root, capture_dir
