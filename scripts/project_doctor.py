#!/usr/bin/env python3
"""Run read-only health checks for the maintained repository toolchain."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Callable, Optional


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Check:
    label: str
    ok: bool
    detail: str = ""
    required: bool = True


PythonProbe = Callable[[Path], dict[str, str]]
Which = Callable[[str], Optional[str]]


REQUIRED_PATHS = (
    ("Root instructions", "AGENTS.md"),
    ("Command menu", "Justfile"),
    ("Dependency manifest", "requirements.txt"),
    ("Runtime contract", "docs/instructions/runtime-contract.md"),
    ("Evidence store", "sources"),
    ("Authoring instructions", "authoring/AGENTS.md"),
    ("Authoring contract", "authoring/runtime/authoring-contract.md"),
    (
        "Authoring state",
        "authoring/editions/1984/project-control/chapter-status.yaml",
    ),
    ("Entry query", "scripts/query_entries.py"),
    ("Duplicate query", "scripts/query_duplicates.py"),
)


def probe_project_python(python: Path) -> dict[str, str]:
    code = """
import importlib
import json
import platform

payload = {"python": platform.python_version()}
for module_name in ("yaml", "pypdf"):
    try:
        module = importlib.import_module(module_name)
        payload[module_name] = str(getattr(module, "__version__", "installed"))
    except Exception as exc:
        payload[module_name + "_error"] = f"{type(exc).__name__}: {exc}"
print(json.dumps(payload, sort_keys=True))
""".strip()
    result = subprocess.run(
        [str(python), "-c", code],
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        return {"probe_error": result.stderr.strip() or f"exit {result.returncode}"}
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return {"probe_error": f"invalid probe output: {exc}"}
    return {str(key): str(value) for key, value in payload.items()}


def run_checks(
    root: Path,
    *,
    which: Which = shutil.which,
    probe_python: PythonProbe = probe_project_python,
) -> list[Check]:
    root = root.resolve()
    python = root / ".venv" / "bin" / "python"
    python_ok = python.is_file() and os.access(python, os.X_OK)
    checks = [
        Check("Python environment", python_ok, ".venv/bin/python"),
    ]

    probe = probe_python(python) if python_ok else {}
    checks.extend(
        [
            Check("Python", bool(probe.get("python")), probe.get("python", "unavailable")),
            Check(
                "PyYAML",
                bool(probe.get("yaml")),
                probe.get("yaml") or probe.get("yaml_error", "unavailable"),
            ),
            Check(
                "pypdf",
                bool(probe.get("pypdf")),
                probe.get("pypdf") or probe.get("pypdf_error", "unavailable"),
            ),
        ]
    )

    for name in ("rg", "jq", "just"):
        found = which(name)
        checks.append(Check(name, found is not None, found or "missing"))

    for name in ("make", "yq"):
        found = which(name)
        checks.append(Check(name, found is not None, found or "not installed", required=False))

    poppler = [which("pdftotext"), which("pdftoppm")]
    checks.append(
        Check(
            "Poppler",
            all(poppler),
            "pdftotext + pdftoppm" if all(poppler) else "not fully installed",
            required=False,
        )
    )

    for label, relative in REQUIRED_PATHS:
        path = root / relative
        checks.append(Check(label, path.exists(), relative if path.exists() else f"missing: {relative}"))
    return checks


def render(checks: list[Check]) -> str:
    lines = []
    width = max(len(check.label) for check in checks)
    for check in checks:
        state = "OK" if check.ok else ("FAIL" if check.required else "INFO")
        detail = f"  {check.detail}" if check.detail else ""
        lines.append(f"{check.label:<{width}}  {state}{detail}")
    failures = [check for check in checks if check.required and not check.ok]
    lines.append("")
    lines.append("Environment healthy." if not failures else f"Environment unhealthy: {len(failures)} required check(s) failed.")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    checks = run_checks(args.root)
    print(render(checks))
    return 1 if any(check.required and not check.ok for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
