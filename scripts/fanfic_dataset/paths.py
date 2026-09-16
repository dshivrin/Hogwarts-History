from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


SAFE_ID = re.compile(r"^[A-Z0-9-]+$")
CAPTURE_ID = re.compile(r"^\d{8}T\d{6}Z$")
CHAPTER_SUFFIXES = {
    "raw": ".html",
    "clean": ".html",
    "text": ".md",
    "pdf": ".pdf",
}


@dataclass(frozen=True)
class CapturePaths:
    root: Path

    def chapter(self, kind: str, index: int, suffix: str) -> Path:
        if kind not in CHAPTER_SUFFIXES:
            raise ValueError(f"unsupported artifact kind: {kind}")
        if index < 1:
            raise ValueError("chapter index must be positive")
        if suffix != CHAPTER_SUFFIXES[kind]:
            raise ValueError(f"unsupported suffix for {kind}: {suffix}")
        return self.root / kind / f"chapter-{index:03d}{suffix}"


def capture_paths(output_root: Path, source_id: str, capture_id: str) -> CapturePaths:
    if not SAFE_ID.fullmatch(source_id) or not CAPTURE_ID.fullmatch(capture_id):
        raise ValueError("unsafe source_id or capture_id")
    return CapturePaths(output_root / "works" / source_id / "captures" / capture_id)
