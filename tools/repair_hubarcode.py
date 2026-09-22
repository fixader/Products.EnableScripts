"""Explicit Python 3 repair for hubarcode 1.0.0's DataMatrix API.

Never run automatically. Verifies original hashes and compiles changes before
writing. Saves originals and a manifest; preserves the upstream BSD notices.
"""

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import re
import shutil

MARKER = "# RestrictedPythonExtensions: hubarcode 1.0.0 DataMatrix Python 3 repair v1\n"
ORIGINAL_HASHES = {
    "__init__.py": "63d680ce49b15ae50a9bfc804de2ebad885f1fe421a4a076eec55ebb90270f64",
    "placement.py": "a25a1592de2417ce542d06e95db0954f1bea34d4f070ff90c440c3cae9016b82",
    "renderer.py": "92e4fb2bb855f0ef0d2c4a225dbc4265d9d7b9e5ecdd8f9cb37377ed4999b969",
    "textencoder.py": "726ab7c6b64b702bd026d2241bbdee2a839334b1b7147cb2f1c4819c73cca546",
}


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f"Unexpected source around {old[:60]!r}")
    return source.replace(old, new, 1)


def transform(name, source):
    if name == "__init__.py":
        for module in ("textencoder", "placement", "renderer"):
            source = replace_once(source, f"from {module} import", f"from .{module} import")
    elif name == "placement.py":
        for method in ("place_bit", "place_standard_shape"):
            pattern = rf'(    def {method}\(self, )\(posx, posy\)(, [^\n]+\n        """.*?"""\n)'
            source, count = re.subn(pattern, r'\1position\2        posx, posy = position\n', source, flags=re.S)
            if count != 1:
                raise ValueError(f"Unexpected tuple arguments in {method}")
    elif name == "renderer.py":
        source = replace_once(source, "from cStringIO import StringIO", "from io import BytesIO")
        source = replace_once(source, "def put_cell(self, (posx, posy), colour=1):", "def put_cell(self, position, colour=1):")
        source = replace_once(source, "        self.matrix[posy][posx] = colour", "        posx, posy = position\n        self.matrix[posy][posx] = colour")
        source = replace_once(source, "imagedata = StringIO()", "imagedata = BytesIO()")
        source = replace_once(source, "return chr(255)", "return b'\\xff'")
        source = replace_once(source, "return chr(0)", "return b'\\x00'")
        source = replace_once(source, '        buf = ""', '        buf = b""')
        source = replace_once(source, "bufrow = ''.join", "bufrow = b''.join")
        source = replace_once(source, "        # add the quiet zone (2 x cell width)",
                              "        if not isinstance(cellsize, int) or cellsize <= 0:\n"
                              "            raise ValueError('cellsize must be a positive integer')\n\n"
                              "        # add the quiet zone (2 x cell width)")
    elif name == "textencoder.py":
        source = replace_once(source, "from reedsolomon import", "from .reedsolomon import")
        source = replace_once(source, "        self.encode_text(text)",
                              "        if isinstance(text, bytes):\n"
                              "            text = text.decode('latin-1')\n"
                              "        if not isinstance(text, str) or any(ord(c) > 255 for c in text):\n"
                              "            raise ValueError('DataMatrix text must be Latin-1 or bytes')\n"
                              "        self.encode_text(text)")
        source = replace_once(source, "if char.isdigit():", "if '0' <= char <= '9':")
        source = replace_once(source, '            log.error("Data too big")\n            sys.exit(0)',
                              "            raise ValueError('Data too big: at most 44 encoded data codewords are supported')")
        source = replace_once(source, "        append = chr(ord(char) + 1)",
                              "        value = ord(char)\n"
                              "        if value >= 128:\n"
                              "            self.codewords += chr(235)  # ECC200 upper shift\n"
                              "            value -= 128\n"
                              "        append = chr(value + 1)")
    result = MARKER + source
    compile(result, name, "exec")
    return result.encode("utf-8")


def repair(folder, backup, apply=False):
    folder = Path(folder).resolve()
    originals = {name: (folder / name).read_bytes() for name in ORIGINAL_HASHES}
    if all(data.startswith(MARKER.encode()) for data in originals.values()):
        return "Repair already applied"
    for name, data in originals.items():
        if hashlib.sha256(data).hexdigest() != ORIGINAL_HASHES[name]:
            raise ValueError(f"{name} differs from the verified hubarcode 1.0.0 source; refusing to overwrite it")
    changes = {name: transform(name, data.decode("utf-8")) for name, data in originals.items()}
    if not apply:
        return "Verified: four DataMatrix files can be repaired; use --apply and --backup-dir"
    backup = Path(backup).resolve()
    if backup == folder or folder in backup.parents:
        raise ValueError("Backup must be outside the installed DataMatrix directory")
    backup.mkdir(parents=True, exist_ok=False)
    manifest = {"target": str(folder), "original_sha256": ORIGINAL_HASHES,
                "patched_sha256": {n: hashlib.sha256(v).hexdigest() for n, v in changes.items()}}
    for name in originals:
        shutil.copy2(folder / name, backup / name)
    (backup / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    try:
        for name, data in changes.items():
            (folder / name).write_bytes(data)
    except Exception:
        for name in originals:
            shutil.copy2(backup / name, folder / name)
        raise
    return f"Repaired DataMatrix. Originals and restore manifest: {backup}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--backup-dir", type=Path)
    args = parser.parse_args()
    if args.apply and args.backup_dir is None:
        parser.error("--apply requires --backup-dir")
    if importlib.metadata.version("hubarcode") != "1.0.0":
        parser.error("Only the verified hubarcode 1.0.0 source is supported")
    spec = importlib.util.find_spec("hubarcode")
    folder = Path(spec.origin).parent / "datamatrix"
    print(repair(folder, args.backup_dir, args.apply))


if __name__ == "__main__":
    main()
