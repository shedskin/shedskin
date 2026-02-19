# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Converted build system to uv, replacing pip/setuptools workflow with `uv` commands in Makefile (`f97db27a`)
- Applied mypy strict mode fixes across core modules (`__init__`, `cmake`, `config`, `cpp`, `graph`, `infer`, `makefile`, `stats`) (`635c2938`)
- Converted documentation from Sphinx/RST to MkDocs with Markdown (`23c5c338`)
  - Replaced `README.rst` with `README.md`
  - Removed generated Sphinx HTML/JS/CSS assets from `docs/`
  - Added `mkdocs.yml` configuration
- Updated `Makefile` test target to fix test invocation (`7cebb2ff`)
  - Refactored `graph.py` and `infer.py` to resolve type issues

### Removed

- Removed `requirements.txt` (dependencies now managed via `pyproject.toml` and uv) (`9602bf6b`)

## [0.9.12]

### Added

- Local dependency management (`--local-deps` flag) with bundled zip archives:
  - Builds bdwgc and pcre2 from compressed sources in `shedskin/ext/`
  - Extracts to platform-specific cache on first use:
    - macOS: `~/Library/Caches/shedskin/`
    - Linux: `~/.cache/shedskin/`
    - Windows: `%LOCALAPPDATA%/shedskin/Cache/`
  - Caches built static libraries for subsequent compilations
  - Works completely offline (no network required)
  - Cross-platform support (Linux, macOS, Windows)
- `LocalDependencyManager` class in `cmake.py` for zip-based dependency building
- CLI option `--local-deps` for both `translate` (Makefile) and `build` (CMake) commands
- Unit tests for core modules (`tests/unit/`, 74 tests total):
  - `test_config.py`: Tests for GlobalInfo and state objects
  - `test_graph.py`: Tests for constraint graph building
  - `test_infer.py`: Tests for type inference
  - `test_cpp.py`: Tests for C++ code generation config

- Initial tracked release

### Changed

- Made `--local-deps` the default dependency manager for `build`, `run`, and `runtests` subcommands
  - Dependencies are now automatically built from bundled `ext/` sources
  - No external package manager required out of the box
- Simplified CMake output directories to `${CMAKE_BINARY_DIR}` (executables in `build/`)
- Bundled bdwgc (v8.2.10) and pcre2 (pcre2-10.47) sources as compressed zip archives in `ext/`:
  - Reduced from 25MB (full sources) to 1.2MB (trimmed and compressed)
  - Removed documentation, tests, CI/CD files, autotools, legacy platform support
  - Removed SLJIT (JIT compiler) from pcre2 as shedskin doesn't use JIT features
- Refactored `GlobalInfo` class into focused state objects for better code organization:
  - `FileSystemPaths`: Immutable paths for shedskin installation, resources, and libraries
  - `BuildConfiguration`: Build flags (bounds_checking, int32/64, nogc, etc.)
  - `NamingContext`: C++ keywords, prefix, and builtin type names
  - `EntityRegistry`: Functions, classes, variables, modules, and inheritance tracking
  - `GraphBuildingContext`: Temporary graph building state (loops, comprehensions, etc.)
  - `TypeInferenceState`: Core type inference data (cnode, types, constraints, etc.)
- Created new `shedskin/state/` package containing the focused state dataclasses
- Maintained 100% backwards compatibility via property delegation in `GlobalInfo`
- Consolidated CLI argument definitions using argparse parent parsers:
  - Created `_create_shared_parsers()` method with reusable argument groups
  - Shared parsers: `stats`, `types`, `disable`, `compiler`, `cmake`
  - Reduced code duplication across `translate`, `build`, `run`, `runtests` subcommands

### Security

- Replaced `os.system()` with `subprocess.run()` across all modules:
  - `cmake.py`: shellcmd, cmake config/build/test, pytest
  - `makefile.py`: Command execution in `_execute()`
  - `__init__.py`: Executable running and Windows color output hack

### Documentation

- Documented type inference tuning constants in `infer.py`:
  - `INCREMENTAL`: Enable incremental analysis mode
  - `INCREMENTAL_FUNCS`: Functions to add per round (default: 5)
  - `INCREMENTAL_DATA`: Enable incremental allocation tracking
  - `INCREMENTAL_ALLOCS`: Allocations before restart (default: 1)
  - `MAXITERS`: Maximum iterations per round (default: 30)
  - `CPA_LIMIT`: Initial cartesian product limit (default: 10)
- Added `MAX_TYPE_DEPTH` constant in `typestr.py` for recursion limit (default: 10)

### Fixed

- Fixed CMake build failure when source file path is absolute (e.g., building from a different directory with `../examples/foo.py`). The issue occurred because absolute parent paths were being concatenated with build directories, creating invalid paths like `build/exe/C:/Users/.../file.cpp`.
- Resource leaks: Added context manager support to `MakefileWriter` class
- File handling: Use context managers for file operations in `config.py`

### Removed

- Removed Conan dependency manager support:
  - Removed `--conan` CLI option
  - Removed `ConanBDWGC`, `ConanPCRE`, and `ConanDependencyManager` classes
  - Removed `ENABLE_CONAN` CMake option
  - Removed `shedskin/resources/conan/` directory
  - Removed conan from `requirements.txt`
