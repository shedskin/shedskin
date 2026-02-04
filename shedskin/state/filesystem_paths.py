# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.state.filesystem_paths: File system path configuration."""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


@dataclass(frozen=True)
class FileSystemPaths:
    """Immutable file system paths used during compilation.

    These paths are determined at startup and remain constant throughout
    the compilation process.

    Attributes:
        cwd: Current working directory at startup.
        sysdir: Shedskin installation directory.
        shedskin_lib: Path to shedskin library directory.
        libdirs: Tuple of library directories to search.
        shedskin_resources: Path to resources directory.
        shedskin_cmake: Path to cmake resources.
        shedskin_flags: Path to compiler flags resources.
        shedskin_illegal: Path to illegal keywords file directory.
    """

    cwd: Path
    sysdir: str
    shedskin_lib: Path
    libdirs: Tuple[str, ...]
    shedskin_resources: Path
    shedskin_cmake: Path
    shedskin_flags: Path
    shedskin_illegal: Path
