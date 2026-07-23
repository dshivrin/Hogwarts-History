import json
import re
from pathlib import Path

import pytest

from scripts.fanfic_dataset.build_manifest import build_manifest, promote_latest
from scripts.fanfic_dataset.merge_pdf import canonical_complete_pdf_name
from scripts.fanfic_dataset.models import CheckResult, WorkDiscovery, WorkValidation


def test_build_manifest_writes_sorted_hashed_relative_records(tmp_path: Path) -> None:
    dataset_root, capture_dir = _synthetic_capture(tmp_path)

    returned_records = build_manifest(capture_dir)
    manifest_path = dataset_root / "manifest.jsonl"

    assert [record.chapter_index for record in returned_records] == [1, 2]
    payload = manifest_path.read_text(encoding="utf-8")
    assert payload.endswith("\n")
    records = [json.loads(line) for line in payload.splitlines()]
    assert [record["chapter_index"] for record in records] == [1, 2]
    assert records == sorted(
        records,
        key=lambda record: (
            record["source_id"],
            record["capture_id"],
            record["chapter_index"],
        ),
    )
    assert records[0]["complete_pdf_path"] == records[1]["complete_pdf_path"]
    assert records[0]["complete_pdf_path"] == str(
        Path("data/fanfic-hogwarts-history")
        / "works/HAH-FAN-001/captures/20260723T120000Z/pdf"
        / canonical_complete_pdf_name(
            WorkDiscovery.model_validate(
                json.loads((capture_dir / "metadata.json").read_text("utf-8"))["discovery"]
            )
        )
    )
    for record in records:
        for field in (
            "raw_html_path",
            "clean_html_path",
            "text_path",
            "chapter_pdf_path",
            "complete_pdf_path",
        ):
            path = Path(record[field])
            assert not path.is_absolute()
            assert str(path).startswith("data/fanfic-hogwarts-history/")
        for field in (
            "raw_sha256",
            "clean_html_sha256",
            "text_sha256",
            "chapter_pdf_sha256",
            "complete_pdf_sha256",
        ):
            assert re.fullmatch(r"[0-9a-f]{64}", record[field])
        assert record["fan_created"] is True
        assert record["canon_status"] == "non-canon fanfiction"
    assert not (dataset_root / "works/HAH-FAN-001/latest.json").exists()


@pytest.mark.parametrize("problem", ["missing", "absolute", "outside", "gap"])
def test_build_manifest_rejects_invalid_capture_inputs(
    tmp_path: Path, problem: str
) -> None:
    _, capture_dir = _synthetic_capture(tmp_path)
    if problem == "missing":
        (capture_dir / "text/chapter-002.md").unlink()
    elif problem == "absolute":
        metadata = json.loads((capture_dir / "metadata.json").read_text("utf-8"))
        metadata["pages"][0]["raw_html_path"] = "/tmp/chapter-001.html"
        (capture_dir / "metadata.json").write_text(json.dumps(metadata), "utf-8")
    elif problem == "outside":
        metadata = json.loads((capture_dir / "metadata.json").read_text("utf-8"))
        metadata["pages"][0]["raw_html_path"] = "../other/chapter-001.html"
        (capture_dir / "metadata.json").write_text(json.dumps(metadata), "utf-8")
    else:
        metadata = json.loads((capture_dir / "metadata.json").read_text("utf-8"))
        metadata["pages"][1]["chapter"]["chapter_index"] = 3
        (capture_dir / "metadata.json").write_text(json.dumps(metadata), "utf-8")

    with pytest.raises(ValueError):
        build_manifest(capture_dir)


def test_promote_latest_rejects_non_passing_validation(tmp_path: Path) -> None:
    validation = WorkValidation(
        source_id="HAH-FAN-001",
        capture_id="20260723T120000Z",
        status="fail",
        checks=[CheckResult(check_id="synthetic", passed=False, detail="synthetic")],
    )

    with pytest.raises(ValueError, match="pass"):
        promote_latest(validation, dataset_root=tmp_path)


def _synthetic_capture(tmp_path: Path) -> tuple[Path, Path]:
    dataset_root = tmp_path / "data/fanfic-hogwarts-history"
    capture_dir = dataset_root / "works/HAH-FAN-001/captures/20260723T120000Z"
    for directory in ("raw", "clean", "text", "pdf"):
        (capture_dir / directory).mkdir(parents=True, exist_ok=True)
    for chapter in (1, 2):
        stem = f"chapter-{chapter:03d}"
        (capture_dir / f"raw/{stem}.html").write_text(
            f"<p>Synthetic chapter {chapter}.</p>", encoding="utf-8"
        )
        (capture_dir / f"clean/{stem}.html").write_text(
            f"<article>Synthetic chapter {chapter}.</article>", encoding="utf-8"
        )
        (capture_dir / f"text/{stem}.md").write_text(
            f"# Synthetic {chapter}\n", encoding="utf-8"
        )
        (capture_dir / f"pdf/{stem}.pdf").write_bytes(f"synthetic-{chapter}".encode())
    metadata = {
        "capture_id": "20260723T120000Z",
        "source": {
            "source_id": "HAH-FAN-001",
            "work_title": "Synthetic Hogwarts History",
            "author": "Synthetic Author",
            "platform": "fanfiction.net",
            "work_url": "https://www.fanfiction.net/s/1/1/synthetic",
            "expected_available_chapter_count": 2,
            "status": "core",
        },
        "discovery": {
            "source_id": "HAH-FAN-001",
            "work_id": "1",
            "work_title": "Synthetic Hogwarts History",
            "author": "Synthetic Author",
            "summary": "Synthetic prose only.",
            "rating": None,
            "language": "English",
            "displayed_word_count": 2,
            "published_date_displayed": None,
            "updated_date_displayed": None,
            "chapters": [
                {
                    "chapter_index": chapter,
                    "chapter_title": f"Synthetic {chapter}",
                    "chapter_url": f"https://www.fanfiction.net/s/1/1/{chapter}/",
                }
                for chapter in (1, 2)
            ],
        },
        "pages": [
            {
                "source_id": "HAH-FAN-001",
                "chapter": {
                    "chapter_index": chapter,
                    "chapter_title": f"Synthetic {chapter}",
                    "chapter_url": f"https://www.fanfiction.net/s/1/1/{chapter}/",
                },
                "retrieved_at_utc": "2026-07-23T12:00:00Z",
                "final_url": f"https://www.fanfiction.net/s/1/1/{chapter}/",
                "status": 200,
                "raw_html_path": (
                    "data/fanfic-hogwarts-history/works/HAH-FAN-001/captures/"
                    f"20260723T120000Z/raw/chapter-{chapter:03d}.html"
                ),
            }
            for chapter in (1, 2)
        ],
    }
    (capture_dir / "metadata.json").write_text(
        json.dumps(metadata), encoding="utf-8"
    )
    complete_pdf = capture_dir / "pdf" / canonical_complete_pdf_name(
        WorkDiscovery.model_validate(metadata["discovery"])
    )
    complete_pdf.write_bytes(b"synthetic-complete")
    return dataset_root, capture_dir
