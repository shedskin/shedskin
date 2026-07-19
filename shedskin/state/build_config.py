# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.state.build_config: Build configuration settings."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class BuildConfiguration:
    """Build configuration settings.

    These settings are determined at configuration time via the
    Shedskin.configure() method.

    Attributes:
        wrap_around_check: Enable wrap-around checking for integers.
        bounds_checking: Enable bounds checking for sequences.
        assertions: Enable assertion checking.
        executable_product: Build an executable.
        pyextension_product: Build a Python extension module.
        int32: Use 32-bit integers.
        int64: Use 64-bit integers.
        int128: Use 128-bit integers.
        float32: Use 32-bit floats.
        float64: Use 64-bit floats.
        flags: Optional path to custom compiler flags file.
        silent: Suppress output messages.
        nogc: Disable garbage collection.
        backtrace: Enable backtrace on errors.
        makefile_name: Name of the generated makefile.
        debug_level: Debug verbosity level.
        nomakefile: Skip makefile generation.
        generate_cmakefile: Generate CMakeLists.txt.
    """

    wrap_around_check: bool = True
    bounds_checking: bool = True
    assertions: bool = True
    executable_product: bool = True
    pyextension_product: bool = False
    int32: bool = False
    int64: bool = False
    int128: bool = False
    float32: bool = False
    float64: bool = False
    flags: Optional[Path] = None
    silent: bool = False
    nogc: bool = False
    backtrace: bool = False
    makefile_name: str = "Makefile"
    debug_level: int = 0
    nomakefile: bool = False
    generate_cmakefile: bool = False
