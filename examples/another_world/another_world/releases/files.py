# File lookup shared by the releases.
from __future__ import annotations

import os


def find_file(data_dir: str, name: str) -> str:
    """The path of `name` in `data_dir`, matched case-insensitively as the
    DOS, Amiga and Windows file systems do, or "" if it is not there. A ""
    directory finds nothing, so lookups chain: find_file(find_file(d, a), b)."""
    if data_dir == "" or not os.path.isdir(data_dir):
        return ""
    want = name.lower()
    for entry in os.listdir(data_dir):
        if entry.lower() == want:
            return os.path.join(data_dir, entry)
    return ""
