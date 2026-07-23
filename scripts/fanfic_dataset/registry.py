from __future__ import annotations

import json
from pathlib import Path

from .models import SourceRecord


def load_sources(path: Path) -> dict[str, SourceRecord]:
    records = [SourceRecord.model_validate(item) for item in json.loads(path.read_text("utf-8"))]
    by_id = {record.source_id: record for record in records}
    if len(by_id) != len(records):
        raise ValueError("source registry contains duplicate source_id values")
    return by_id
