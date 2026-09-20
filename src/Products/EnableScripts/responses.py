"""Small response helpers shared by the compatibility helpers."""

from urllib.parse import quote


def inline_filename(filename):
    filename = str(filename)
    if any(c in filename for c in "\r\n\x00"):
        raise ValueError("Invalid filename")
    filename = filename.replace("\\", "/").rsplit("/", 1)[-1]
    fallback = filename.encode("ascii", "replace").decode("ascii")
    fallback = fallback.replace('"', "_")
    return f'inline; filename="{fallback}"; filename*=UTF-8\'\'{quote(filename, safe="")}'
