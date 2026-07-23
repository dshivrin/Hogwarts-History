import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from scripts.fanfic_dataset.emit_schemas import schema_documents
from scripts.fanfic_dataset.models import ManifestRecord, SourceRecord
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


def test_capture_paths_reject_traversal_suffix(tmp_path: Path) -> None:
    paths = capture_paths(tmp_path, "HAH-FAN-001", "20260722T120000Z")
    with pytest.raises(ValueError, match="unsupported suffix"):
        paths.chapter("raw", 2, "/../../outside.html")


def test_manifest_requires_non_canon_labels() -> None:
    fields = ManifestRecord.model_fields
    assert fields["fan_created"].default is True
    assert fields["canon_status"].default == "non-canon fanfiction"


@pytest.mark.parametrize(
    ("field", "value"),
    [("fan_created", False), ("canon_status", "canon")],
)
def test_manifest_rejects_alternative_policy_labels(field: str, value: object) -> None:
    payload = _manifest_payload()
    payload[field] = value
    with pytest.raises(ValidationError):
        ManifestRecord(**payload)


def test_source_schema_rejects_non_https_url() -> None:
    schema = schema_documents()["source-record.schema.json"]
    invalid = {
        "source_id": "HAH-FAN-001",
        "work_title": "Example",
        "author": "Example",
        "platform": "fanfiction.net",
        "work_url": "http://www.fanfiction.net/s/1/1/example",
        "expected_available_chapter_count": 1,
        "status": "core",
    }
    assert list(Draft202012Validator(schema).iter_errors(invalid))


def test_checked_in_schemas_match_models() -> None:
    root = Path(__file__).resolve().parents[2]
    for name, document in schema_documents().items():
        path = root / "data/fanfic-hogwarts-history/schemas" / name
        assert json.loads(path.read_text("utf-8")) == document


def _manifest_payload() -> dict[str, object]:
    return {
        "capture_id": "20260722T120000Z",
        "source_id": "HAH-FAN-001",
        "work_title": "Example",
        "author": "Example",
        "platform": "fanfiction.net",
        "work_url": "https://www.fanfiction.net/s/1/1/example",
        "chapter_index": 1,
        "chapter_title": "One",
        "chapter_url": "https://www.fanfiction.net/s/1/1/example/1/",
        "retrieved_at_utc": "2026-07-22T12:00:00Z",
        "published_date_displayed": None,
        "updated_date_displayed": None,
        "expected_available_chapter_count": 1,
        "raw_html_path": "raw/chapter-001.html",
        "clean_html_path": "clean/chapter-001.html",
        "text_path": "text/chapter-001.txt",
        "chapter_pdf_path": "pdf/chapter-001.pdf",
        "complete_pdf_path": "complete.pdf",
        "raw_sha256": "0" * 64,
        "clean_html_sha256": "0" * 64,
        "text_sha256": "0" * 64,
        "chapter_pdf_sha256": "0" * 64,
        "complete_pdf_sha256": "0" * 64,
        "tool_version": "1.0.0",
    }
