#!/usr/bin/env python3
"""Byte snapshots for the finite artifacts owned by external completion."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import tempfile


FIXED_ARTIFACTS = (
    "project-control/duplicate-index.yaml",
    "project-control/entry-index.yaml",
    "project-control/source-index.yaml",
    "project-control/tag-index.yaml",
    "project-control/source-plan.yaml",
    "project-control/processing-state.yaml",
    "project-control/next-run.md",
    "book-seed/hogwarts-a-history-seed.md",
)
GENERATED_APPENDIX_DIR = "appendix/generated"


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


@dataclass(frozen=True)
class CompletionArtifactSnapshot:
    root: Path
    files: dict[str, bytes | None]
    original_appendix_files: frozenset[str]

    @classmethod
    def capture(cls, root: Path) -> "CompletionArtifactSnapshot":
        resolved = root.resolve()
        appendix_dir = resolved / GENERATED_APPENDIX_DIR
        appendix_files = (
            {
                path.relative_to(resolved).as_posix()
                for path in appendix_dir.iterdir()
                if path.is_file() and not path.is_symlink()
            }
            if appendix_dir.is_dir()
            else set()
        )
        names = set(FIXED_ARTIFACTS) | appendix_files
        files = {
            name: (resolved / name).read_bytes()
            if (resolved / name).is_file()
            else None
            for name in names
        }
        return cls(resolved, files, frozenset(appendix_files))

    def restore(self) -> None:
        for name, payload in self.files.items():
            path = self.root / name
            if payload is None:
                path.unlink(missing_ok=True)
            else:
                _atomic_write_bytes(path, payload)

        appendix_dir = self.root / GENERATED_APPENDIX_DIR
        if appendix_dir.is_dir():
            for path in appendix_dir.iterdir():
                name = path.relative_to(self.root).as_posix()
                if (
                    path.is_file()
                    and not path.is_symlink()
                    and name not in self.original_appendix_files
                ):
                    path.unlink()
