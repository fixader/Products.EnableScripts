import os
from pathlib import Path
import subprocess
import sys


def test_custom_policy_across_restarts(tmp_path):
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=str(root / 'src'))
    for phase in ('initial', 'enabled', 'edited', 'removed'):
        result = subprocess.run([sys.executable, str(root/'tests/custom_web_scenario.py'), str(tmp_path), phase],
                                env=env, capture_output=True, text=True, timeout=90)
        assert result.returncode == 0, result.stdout + result.stderr


def test_unavailable_custom_library_does_not_break_startup():
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=str(root / 'src'))
    code = '''from Products.RestrictedPythonExtensions import runtime
record = ('restrictedpythonextensions_missing_library', ('public',), ())
runtime.activate(custom=(record,), custom_enabled=('restrictedpythonextensions_missing_library',))
assert 'custom:restrictedpythonextensions_missing_library' in runtime.ERRORS
assert not runtime.ACTIVE
'''
    result = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
