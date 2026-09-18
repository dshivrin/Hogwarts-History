#!/usr/bin/env python3
"""Discover canonical evidence YAML without scanning unrelated project files."""

from __future__ import annotations

from pathlib import Path
import re


def discover_source_yaml(root: Path) -> list[Path]:
    """Return book and external evidence YAML in deterministic path order."""
    sources = Path(root) / "sources"
    paths = set(sources.glob("book-*/*.yaml"))
    paths.update(sources.glob("external/**/*.yaml"))
    result = []
    for path in sorted(paths):
        if not path.is_file():
            continue
        # Preserve numbered filesystem copies on disk, but do not count an
        # exactly identical copy as a second source. Divergent copies remain
        # visible so the canonical validator rejects them for human review.
        match = re.fullmatch(r"(chapter-\d{2}-[a-z0-9-]+) (\d+)\.yaml", path.name)
        if match and int(match[2]) >= 2:
            original = path.with_name(match[1] + ".yaml")
            if original.is_file() and original.read_bytes() == path.read_bytes():
                continue
        result.append(path)
    return result
