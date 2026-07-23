"""Build deterministic, hashed manifest records for captured fanfiction data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .merge_pdf import canonical_complete_pdf_name
from .models import CapturedPage, ManifestRecord, SourceRecord, WorkDiscovery, WorkValidation


DATASET_DIRECTORY = Path("data/fanfic-hogwarts-history")
TOOL_VERSION = "1.0.0"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(capture_dir: Path) -> list[ManifestRecord]:
    """Validate capture artifacts and write the dataset's sorted manifest."""
    capture_dir = capture_dir.resolve(strict=True)
    dataset_root = _dataset_root(capture_dir)
    records: list[ManifestRecord] = []
    for candidate in sorted((dataset_root / "works").glob("*/captures/*")):
        if candidate.is_dir():
            records.extend(_records_for_capture(candidate, dataset_root))
    records.sort(key=lambda record: (record.source_id, record.capture_id, record.chapter_index))
    manifest_path = dataset_root / "manifest.jsonl"
    contents = "".join(
        json.dumps(
            record.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for record in records
    )
    manifest_path.write_text(contents, encoding="utf-8")
    return records


def promote_latest(work_validation: WorkValidation, *, dataset_root: Path | None = None) -> Path:
    """Advance a work's latest pointer after a passing validation only."""
    if work_validation.status != "pass":
        raise ValueError("latest may only be promoted after validation status pass")
    root = (dataset_root or _default_dataset_root()).resolve()
    latest_path = root / "works" / work_validation.source_id / "latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(
        json.dumps(
            {
                "capture_id": work_validation.capture_id,
                "source_id": work_validation.source_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )
    return latest_path


def _records_for_capture(capture_dir: Path, dataset_root: Path) -> list[ManifestRecord]:
    metadata_path = capture_dir / "metadata.json"
    if not metadata_path.is_file():
        raise ValueError(f"capture metadata is missing: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    source = SourceRecord.model_validate(metadata["source"])
    discovery = WorkDiscovery.model_validate(metadata["discovery"])
    pages = [CapturedPage.model_validate(page) for page in metadata["pages"]]
    if metadata.get("capture_id") != capture_dir.name:
        raise ValueError("capture metadata does not match capture directory")
    if source.source_id != capture_dir.parents[1].name or discovery.source_id != source.source_id:
        raise ValueError("capture metadata source does not match capture directory")
    _require_consecutive(pages, discovery)
    complete_pdf = capture_dir / "pdf" / canonical_complete_pdf_name(discovery)
    _require_file(complete_pdf)
    result: list[ManifestRecord] = []
    for page in pages:
        index = page.chapter.chapter_index
        raw = _metadata_artifact(page.raw_html_path, dataset_root)
        clean = capture_dir / "clean" / f"chapter-{index:03d}.html"
        text = capture_dir / "text" / f"chapter-{index:03d}.md"
        chapter_pdf = capture_dir / "pdf" / f"chapter-{index:03d}.pdf"
        for path in (raw, clean, text, chapter_pdf):
            _require_file(path)
        result.append(
            ManifestRecord(
                capture_id=capture_dir.name,
                source_id=source.source_id,
                work_title=discovery.work_title,
                author=discovery.author,
                platform=source.platform,
                work_url=source.work_url,
                chapter_index=index,
                chapter_title=page.chapter.chapter_title,
                title_missing=page.chapter.title_missing,
                chapter_url=page.chapter.chapter_url,
                retrieved_at_utc=page.retrieved_at_utc,
                published_date_displayed=discovery.published_date_displayed,
                updated_date_displayed=discovery.updated_date_displayed,
                expected_available_chapter_count=source.expected_available_chapter_count,
                raw_html_path=_relative_dataset_path(raw, dataset_root),
                clean_html_path=_relative_dataset_path(clean, dataset_root),
                text_path=_relative_dataset_path(text, dataset_root),
                chapter_pdf_path=_relative_dataset_path(chapter_pdf, dataset_root),
                complete_pdf_path=_relative_dataset_path(complete_pdf, dataset_root),
                raw_sha256=sha256_file(raw),
                clean_html_sha256=sha256_file(clean),
                text_sha256=sha256_file(text),
                chapter_pdf_sha256=sha256_file(chapter_pdf),
                complete_pdf_sha256=sha256_file(complete_pdf),
                tool_version=TOOL_VERSION,
            )
        )
    return result


def _dataset_root(capture_dir: Path) -> Path:
    for parent in (capture_dir, *capture_dir.parents):
        if parent.name == "fanfic-hogwarts-history" and parent.parent.name == "data":
            return parent
    raise ValueError("capture directory must be inside data/fanfic-hogwarts-history")


def _default_dataset_root() -> Path:
    return Path(__file__).resolve().parents[2] / DATASET_DIRECTORY


def _metadata_artifact(path: Path, dataset_root: Path) -> Path:
    if path.is_absolute():
        raise ValueError("artifact paths must be relative to the dataset root")
    project_root = dataset_root.parents[1]
    absolute = (project_root / path).resolve()
    if not absolute.is_relative_to(dataset_root):
        raise ValueError("artifact path is outside the dataset root")
    return absolute


def _relative_dataset_path(path: Path, dataset_root: Path) -> Path:
    try:
        return Path(DATASET_DIRECTORY) / path.resolve().relative_to(dataset_root)
    except ValueError as error:
        raise ValueError("artifact path is outside the dataset root") from error


def _require_file(path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"required artifact is missing: {path}")


def _require_consecutive(pages: list[CapturedPage], discovery: WorkDiscovery) -> None:
    indexes = [page.chapter.chapter_index for page in pages]
    expected = list(range(1, len(indexes) + 1))
    discovery_indexes = [chapter.chapter_index for chapter in discovery.chapters]
    if indexes != expected or discovery_indexes != expected:
        raise ValueError("chapters must be consecutive and ordered from one")
