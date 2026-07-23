import json
from pathlib import Path

import pytest
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


def test_manifest_requires_non_canon_labels() -> None:
    fields = ManifestRecord.model_fields
    assert fields["fan_created"].default is True
    assert fields["canon_status"].default == "non-canon fanfiction"


def test_checked_in_schemas_match_models() -> None:
    root = Path(__file__).resolve().parents[2]
    for name, document in schema_documents().items():
        path = root / "data/fanfic-hogwarts-history/schemas" / name
        assert json.loads(path.read_text("utf-8")) == document
