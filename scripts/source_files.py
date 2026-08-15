#!/usr/bin/env python3
"""Discover canonical evidence YAML without scanning unrelated project files."""

from __future__ import annotations

from pathlib import Path


def discover_source_yaml(root: Path) -> list[Path]:
    """Return book and external evidence YAML in deterministic path order."""
    sources = Path(root) / "sources"
    paths = set(sources.glob("book-*/*.yaml"))
    paths.update(sources.glob("external/**/*.yaml"))
    return sorted(path for path in paths if path.is_file())
