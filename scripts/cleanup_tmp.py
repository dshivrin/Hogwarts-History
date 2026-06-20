#!/usr/bin/env python3
"""Clean extraction cache while preserving deterministic current/recent files."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
TMP_DIR = ROOT / ".tmp"
DEFAULT_KEEP = {
    "current-chapter.txt",
    "previous-chapter-1.txt",
    "previous-chapter-2.txt",
    "previous-chapter-3.txt",
    "current-run.log",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove old .tmp extraction artifacts, keeping deterministic files."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print paths that would be removed without deleting them.",
    )
    return parser.parse_args()


def clean(dry_run: bool) -> list[Path]:
    removed: list[Path] = []
    if not TMP_DIR.exists():
        return removed

    for path in sorted(TMP_DIR.iterdir()):
        if path.name in DEFAULT_KEEP:
            continue
        removed.append(path)
        if dry_run:
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    return removed


def main() -> int:
    args = parse_args()
    removed = clean(args.dry_run)
    action = "Would remove" if args.dry_run else "Removed"
    for path in removed:
        print(f"{action}: {path.relative_to(ROOT)}")
    print(f"{action} {len(removed)} .tmp artifact(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
