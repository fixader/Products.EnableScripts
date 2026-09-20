"""Repair a temporary copy, never the developer's installed package."""

import importlib.util
from pathlib import Path
import os
import shutil
import subprocess
import sys

import pytest


def test_hubarcode_python3_repair_and_decode(tmp_path):
    spec = importlib.util.find_spec("hubarcode")
    if spec is None or importlib.util.find_spec("zxingcpp") is None:
        pytest.skip("Install the test extras for the legacy Hubarcode round-trip test")
    package = tmp_path / "hubarcode"
    package.mkdir()
    (package / "__init__.py").write_text("")
    shutil.copytree(Path(spec.origin).parent / "datamatrix", package / "datamatrix")
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(tmp_path), str(root), str(root / "src")]))
    code = '''from pathlib import Path
import sys
from tools.repair_hubarcode import repair
from io import BytesIO
from PIL import Image
import zxingcpp
folder=Path(sys.argv[1])
print(repair(folder/'hubarcode/datamatrix', folder/'backup', apply=True))
from hubarcode.datamatrix import DataMatrixEncoder
from hubarcode.datamatrix.textencoder import TextEncoder
assert [ord(c) for c in TextEncoder().encode('hi')] == [105,106,129,74,235,130,61,159]
for value in ['banana', 'EnableScripts', '12345678901234567890', '\\u00c6\\u00d8\\u00c5', 'A'*44]:
    data=DataMatrixEncoder(value).get_imagedata()
    decoded=zxingcpp.read_barcode(Image.open(BytesIO(data)))
    assert decoded is not None and decoded.bytes == value.encode('latin-1')
for value in ['A'*45, '\\U0001f600']:
    try:
        DataMatrixEncoder(value)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid input was accepted')
from Products.EnableScripts.runtime import activate
from Products.PythonScripts.PythonScript import PythonScript
activate(('hubarcode',))
script=PythonScript('hubarcode_test')
script.write("from hubarcode.datamatrix import DataMatrixEncoder\\nreturn DataMatrixEncoder('restricted').get_imagedata()")
assert not script.errors
decoded=zxingcpp.read_barcode(Image.open(BytesIO(script._exec({},(),{}))))
assert decoded.text == 'restricted'
assert repair(folder/'hubarcode/datamatrix', folder/'backup', apply=True) == 'Repair already applied'
'''
    result = subprocess.run([sys.executable, "-c", code, str(tmp_path)], env=env,
                            capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stdout + result.stderr
