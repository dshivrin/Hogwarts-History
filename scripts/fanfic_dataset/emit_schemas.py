from __future__ import annotations

import json
from pathlib import Path

from .models import ManifestRecord, SourceRecord, WorkValidation


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "data/fanfic-hogwarts-history/schemas"


def schema_documents() -> dict[str, dict]:
    return {
        "manifest-record.schema.json": ManifestRecord.model_json_schema(),
        "source-record.schema.json": SourceRecord.model_json_schema(),
        "work-validation.schema.json": WorkValidation.model_json_schema(),
    }


def main() -> int:
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for name, document in schema_documents().items():
        (SCHEMA_DIR / name).write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
