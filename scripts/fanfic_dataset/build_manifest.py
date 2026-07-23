"""Build deterministic, hashed manifest records for captured fanfiction data."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat

from .merge_pdf import canonical_complete_pdf_name
from .models import CapturedPage, ManifestRecord, SourceRecord, WorkDiscovery, WorkValidation


DATASET_DIRECTORY = Path("data/fanfic-hogwarts-history")
TOOL_VERSION = "1.0.0"
SOURCE_ID = re.compile(r"^HAH-FAN-\d{3}$")
CAPTURE_ID = re.compile(r"^\d{8}T\d{6}Z$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(capture_dir: Path) -> list[ManifestRecord]:
    """Validate capture artifacts and write the dataset's sorted manifest."""
    capture_dir, dataset_root = _canonical_capture(capture_dir)
    captures = _included_captures(dataset_root)
    if capture_dir not in captures:
        raise ValueError("requested canonical capture is not included")
    records: list[ManifestRecord] = []
    for candidate in captures:
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
    if SOURCE_ID.fullmatch(work_validation.source_id) is None:
        raise ValueError("latest promotion requires a canonical source_id")
    if CAPTURE_ID.fullmatch(work_validation.capture_id) is None:
        raise ValueError("latest promotion requires a canonical capture_id")
    root = (dataset_root or _default_dataset_root()).resolve()
    work_root = _prepare_latest_parent(root, work_validation.source_id)
    latest_path = work_root / "latest.json"
    payload = (
        json.dumps(
            {
                "capture_id": work_validation.capture_id,
                "source_id": work_validation.source_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    _atomic_replace_bytes(
        work_root,
        "latest.json",
        payload,
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
    for page, chapter in zip(pages, discovery.chapters, strict=True):
        if page.source_id != source.source_id or page.chapter != chapter:
            raise ValueError("captured page does not match source discovery")
    complete_pdf = capture_dir / "pdf" / canonical_complete_pdf_name(discovery)
    _require_file(complete_pdf)
    result: list[ManifestRecord] = []
    for page in pages:
        index = page.chapter.chapter_index
        expected_raw = capture_dir / "raw" / f"chapter-{index:03d}.html"
        expected_metadata_raw = (
            DATASET_DIRECTORY / expected_raw.relative_to(dataset_root)
        )
        if page.raw_html_path != expected_metadata_raw:
            raise ValueError("captured page raw path is not canonical")
        raw = _metadata_artifact(page.raw_html_path, dataset_root)
        if raw != expected_raw:
            raise ValueError("captured page raw artifact is not in its capture")
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


def _canonical_capture(capture_dir: Path) -> tuple[Path, Path]:
    lexical = (
        capture_dir
        if capture_dir.is_absolute()
        else Path.cwd() / capture_dir
    )
    if ".." in lexical.parts:
        raise ValueError("argument must be an exact canonical capture path")
    try:
        resolved = lexical.resolve(strict=True)
    except (FileNotFoundError, OSError) as error:
        raise ValueError("argument must be an existing canonical capture") from error
    if lexical != resolved or not resolved.is_dir():
        raise ValueError("argument must be an exact canonical capture path")
    if (
        resolved.parent.name != "captures"
        or resolved.parents[2].name != "works"
        or resolved.parents[3].name != DATASET_DIRECTORY.name
        or resolved.parents[3].parent.name != DATASET_DIRECTORY.parent.name
        or SOURCE_ID.fullmatch(resolved.parents[1].name) is None
        or CAPTURE_ID.fullmatch(resolved.name) is None
    ):
        raise ValueError(
            "argument must be a canonical capture path at "
            "works/<source>/captures/<capture>"
        )
    return resolved, resolved.parents[3]


def _included_captures(dataset_root: Path) -> list[Path]:
    captures: list[Path] = []
    works_root = dataset_root / "works"
    for work_root in works_root.iterdir():
        if (
            work_root.is_symlink()
            or not work_root.is_dir()
            or SOURCE_ID.fullmatch(work_root.name) is None
        ):
            continue
        captures_root = work_root / "captures"
        if captures_root.is_symlink() or not captures_root.is_dir():
            continue
        for candidate in captures_root.iterdir():
            if (
                candidate.is_symlink()
                or not candidate.is_dir()
                or CAPTURE_ID.fullmatch(candidate.name) is None
            ):
                continue
            captures.append(candidate.resolve(strict=True))
    return sorted(captures)


def _default_dataset_root() -> Path:
    return Path(__file__).resolve().parents[2] / DATASET_DIRECTORY


def _prepare_latest_parent(dataset_root: Path, source_id: str) -> Path:
    dataset_root.mkdir(parents=True, exist_ok=True)
    if not dataset_root.is_dir():
        raise ValueError("dataset root is not a directory")
    current = dataset_root
    for component in ("works", source_id):
        candidate = current / component
        if candidate.is_symlink():
            raise ValueError(f"latest destination contains a symlink: {candidate}")
        candidate.mkdir(exist_ok=True)
        if candidate.is_symlink() or not candidate.is_dir():
            raise ValueError(f"latest destination contains a symlink: {candidate}")
        try:
            candidate.resolve(strict=True).relative_to(dataset_root)
        except ValueError as error:
            raise ValueError("latest destination is outside the dataset root") from error
        current = candidate
    return current


def _atomic_replace_bytes(parent: Path, name: str, payload: bytes) -> None:
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        directory = os.open(parent, directory_flags)
    except OSError as error:
        raise ValueError("latest destination parent is unsafe") from error
    temporary = f".{name}.{secrets.token_hex(12)}"
    created = False
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(temporary, flags, 0o600, dir_fd=directory)
        created = True
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
        try:
            existing = os.stat(name, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            if stat.S_ISLNK(existing.st_mode):
                raise ValueError("latest destination is a symlink")
        os.replace(
            temporary,
            name,
            src_dir_fd=directory,
            dst_dir_fd=directory,
        )
        created = False
    finally:
        if created:
            try:
                os.unlink(temporary, dir_fd=directory)
            except FileNotFoundError:
                pass
        os.close(directory)


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
