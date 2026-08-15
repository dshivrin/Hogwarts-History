from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "resources" / "manifests" / "external-sources.yaml"
RUNTIME_ARCHIVE_PATH = (
    ROOT
    / "docs"
    / "instructions"
    / "archive"
    / "runtime-contract-book-and-companion-extraction-2026-08-15.md"
)
PRE_REPLACEMENT_RUNTIME_SHA256 = (
    "915e08fd144c21a850b7c4998a13dbb8868a4022aa0c6cc0fb813d35c2517e67"
)


def load_yaml(path: Path) -> dict:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise AssertionError(f"expected YAML mapping in {path}")
    return loaded


def snapshot_parts(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"missing front matter in {path}")
    _, header, body = text.split("---\n", 2)
    metadata = yaml.safe_load(header) or {}
    return metadata, body.lstrip("\n")


class RuntimeBackupAndManifestTests(unittest.TestCase):
    def test_runtime_archive_preserves_pre_replacement_contract(self) -> None:
        self.assertTrue(RUNTIME_ARCHIVE_PATH.is_file())
        archive_hash = hashlib.sha256(RUNTIME_ARCHIVE_PATH.read_bytes()).hexdigest()
        self.assertEqual(archive_hash, PRE_REPLACEMENT_RUNTIME_SHA256)

    def test_capture_completeness_replaces_ambiguous_key_without_body_changes(self) -> None:
        manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
        manifest = load_yaml(MANIFEST_PATH)
        records = manifest["sources"]

        self.assertEqual(len(records), 63)
        self.assertNotIn("\n    completeness:", manifest_text)
        expected_ids = {f"A{number:02d}" for number in range(1, 38)} | {
            f"B{number:02d}" for number in range(1, 27)
        }
        self.assertEqual({record["logical_id"] for record in records}, expected_ids)

        for record in records:
            self.assertEqual(record["capture_completeness"], "complete")
            snapshot_path = ROOT / record["local_path"]
            metadata, body = snapshot_parts(snapshot_path)
            body_without_title = body.split("\n\n", 1)[1].rstrip("\n")
            self.assertEqual(metadata["capture_completeness"], "complete")
            self.assertNotIn("completeness", metadata)
            self.assertEqual(
                hashlib.sha256(body_without_title.encode("utf-8")).hexdigest(),
                record["sha256"],
                record["logical_id"],
            )


if __name__ == "__main__":
    unittest.main()
