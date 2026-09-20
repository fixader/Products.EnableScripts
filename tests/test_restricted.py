import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize("scenario", ["disabled", "bytesio", "granular", "object_off", "media", "helpers", "platypus", "xml", "barcodes", "http"])
def test_real_restricted_scripts(scenario):
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=str(root / "src"))
    result = subprocess.run([sys.executable, str(root / "tests" / "scenario.py"), scenario],
                            env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
