from __future__ import annotations

import sys
import tempfile
from pathlib import Path
import unittest
import wave

import numpy as np


TASK_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TASK_DIR))
import run_full_chapter


class WriteCompatibilityTests(unittest.TestCase):
    def test_missing_renderer_sample_rate_uses_immediately_preceding_assembly_rate(self):
        narrate = run_full_chapter.load_narrate_module()
        adapter = getattr(run_full_chapter, "write_pcm16_compat", None)
        wrote = False
        with tempfile.TemporaryDirectory(dir=TASK_DIR / "tmp") as directory:
            output = Path(directory) / "probe.wav"
            if adapter is not None:
                adapter(
                    narrate.write_pcm16_wav,
                    {"assemblies": [{"sample_rate": 24000}]},
                    output,
                    np.array([0.0, 0.25, 0.0], dtype=np.float32),
                )
                with wave.open(str(output), "rb") as input_file:
                    wrote = (
                        input_file.getframerate() == 24000
                        and input_file.getnframes() == 3
                    )
        self.assertTrue(
            wrote,
            "The task-local adapter must supply the captured assembly sample rate",
        )

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
