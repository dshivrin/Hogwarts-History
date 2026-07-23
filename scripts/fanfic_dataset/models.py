from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourceRecord(StrictModel):
    source_id: str = Field(pattern=r"^HAH-FAN-\d{3}$")
    work_title: str
    author: str
    platform: Literal["fanfiction.net"]
    work_url: HttpUrl = Field(
        json_schema_extra={"pattern": r"^[Hh][Tt][Tt][Pp][Ss]://"}
    )
    expected_available_chapter_count: int = Field(ge=1)
    status: Literal["core", "excluded", "candidate-needs-editorial-review"]
    priority: Literal["high", "medium", "low"] = "medium"
    known_limitations: list[str] = []
    promised_but_unavailable_chapters: list[str] = []

    @field_validator("work_url")
    @classmethod
    def require_https(cls, value: HttpUrl) -> HttpUrl:
        if value.scheme != "https":
            raise ValueError("work_url must use HTTPS")
        return value


class ChapterRef(StrictModel):
    chapter_index: int = Field(ge=1)
    chapter_title: str | None
    title_missing: bool = False
    chapter_url: HttpUrl


class WorkDiscovery(StrictModel):
    source_id: str
    work_id: str
    work_title: str
    author: str
    summary: str
    rating: str | None
    language: str | None
    displayed_word_count: int | None
    published_date_displayed: str | None
    updated_date_displayed: str | None
    native_download_url: HttpUrl | None = None
    chapters: list[ChapterRef]


class CapturedPage(StrictModel):
    source_id: str
    chapter: ChapterRef
    retrieved_at_utc: datetime
    final_url: HttpUrl
    status: int
    raw_html_path: Path


class ChapterArtifact(StrictModel):
    source_id: str
    capture_id: str
    chapter: ChapterRef
    raw_html_path: Path
    clean_html_path: Path
    text_path: Path
    chapter_pdf_path: Path


class ManifestRecord(StrictModel):
    dataset_version: str = "1.0"
    capture_id: str
    source_id: str
    work_title: str
    author: str
    platform: str
    work_url: HttpUrl
    chapter_index: int = Field(ge=1)
    chapter_title: str | None
    title_missing: bool = False
    chapter_url: HttpUrl
    retrieved_at_utc: datetime
    published_date_displayed: str | None
    updated_date_displayed: str | None
    expected_available_chapter_count: int
    raw_html_path: Path
    clean_html_path: Path
    text_path: Path
    chapter_pdf_path: Path
    complete_pdf_path: Path
    raw_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    clean_html_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    text_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    chapter_pdf_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    complete_pdf_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    fan_created: Literal[True] = True
    canon_status: Literal["non-canon fanfiction"] = "non-canon fanfiction"
    dataset_role: str = "style-and-coverage-reference"
    tool_version: str


class CheckResult(StrictModel):
    check_id: str
    passed: bool
    detail: str


class WorkValidation(StrictModel):
    source_id: str
    capture_id: str
    status: Literal["pass", "fail", "manual-review-pending"]
    checks: list[CheckResult]
