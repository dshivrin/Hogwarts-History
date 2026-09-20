from __future__ import annotations

import sys
from pathlib import Path
import unittest

import numpy as np


TASK_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TASK_DIR))
import run_full_chapter


class AssemblySelectionTests(unittest.TestCase):
    def test_selects_real_assembly_after_settings_validation_dummy_assembly(self):
        dummy_chunk = object()
        rendered_chunks = [object(), object()]
        real_assembly = {
            "sample_rate": 24000,
            "chunks": rendered_chunks,
            "audio": np.array([0.0], dtype=np.float32),
        }
        selector = getattr(run_full_chapter, "select_matching_assembly", None)
        selected = (
            selector(
                [
                    {"sample_rate": 1, "chunks": [dummy_chunk]},
                    real_assembly,
                ],
                rendered_chunks,
                24000,
            )
            if selector is not None
            else None
        )
        self.assertIs(
            selected,
            real_assembly,
            "The validation-only dummy assembly must not be mistaken for the chapter assembly",
        )


if __name__ == "__main__":
    unittest.main()
