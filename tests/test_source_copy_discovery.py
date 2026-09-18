"""Identical filesystem copies must not become independent evidence."""
from pathlib import Path
import tempfile
import unittest
from scripts.source_files import discover_source_yaml

class SourceCopyDiscoveryTests(unittest.TestCase):
    def test_identical_numbered_copy_is_preserved_but_not_counted(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            folder = root / 'sources/book-04'
            folder.mkdir(parents=True)
            original = folder / 'chapter-02-the-scar.yaml'
            copy = folder / 'chapter-02-the-scar 2.yaml'
            original.write_text('entries: []\n')
            copy.write_bytes(original.read_bytes())
            self.assertEqual(discover_source_yaml(root), [original])
            self.assertTrue(copy.exists())

    def test_different_or_orphaned_copy_stays_visible_for_validation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            folder = root / 'sources/book-04'
            folder.mkdir(parents=True)
            original = folder / 'chapter-02-the-scar.yaml'
            copy = folder / 'chapter-02-the-scar 2.yaml'
            original.write_text('entries: []\n')
            copy.write_text('entries: [different]\n')
            self.assertEqual(set(discover_source_yaml(root)), {original, copy})
            original.unlink()
            self.assertEqual(discover_source_yaml(root), [copy])
