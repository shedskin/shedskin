# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Unit tests for core modules (`tests/unit/`, 74 tests total):
  - `test_config.py`: Tests for GlobalInfo and state objects
  - `test_graph.py`: Tests for constraint graph building
  - `test_infer.py`: Tests for type inference
  - `test_cpp.py`: Tests for C++ code generation config

### Changed

- Refactored `GlobalInfo` class into focused state objects for better code organization:
  - `FileSystemPaths`: Immutable paths for shedskin installation, resources, and libraries
  - `BuildConfiguration`: Build flags (bounds_checking, int32/64, nogc, etc.)
  - `NamingContext`: C++ keywords, prefix, and builtin type names
  - `EntityRegistry`: Functions, classes, variables, modules, and inheritance tracking
  - `GraphBuildingContext`: Temporary graph building state (loops, comprehensions, etc.)
  - `TypeInferenceState`: Core type inference data (cnode, types, constraints, etc.)
- Created new `shedskin/state/` package containing the focused state dataclasses
- Maintained 100% backwards compatibility via property delegation in `GlobalInfo`

### Security

- Replaced `os.system()` with `subprocess.run()` across all modules:
  - `cmake.py`: Conan install, shellcmd, cmake config/build/test, pytest
  - `makefile.py`: Command execution in `_execute()`
  - `__init__.py`: Executable running and Windows color output hack

### Fixed

- Resource leaks: Added context manager support to `MakefileWriter` class
- File handling: Use context managers for file operations in `config.py`

## [0.9.12]

### Added

- Initial tracked release
