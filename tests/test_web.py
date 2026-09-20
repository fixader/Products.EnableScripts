import os
from pathlib import Path
import subprocess
import sys


def test_wsgi_security_and_restart_persistence(tmp_path):
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=str(root / "src"))
    for phase in ("initial", "restart", "disabled_again"):
        result = subprocess.run([sys.executable, str(root / "tests" / "web_scenario.py"),
                                 str(tmp_path), phase],
                                env=env, capture_output=True, text=True, timeout=90)
        assert result.returncode == 0, result.stdout + result.stderr
