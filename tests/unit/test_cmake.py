# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.cmake module.

'shedskin build' generates a CMake project whose build step shells out to a
separate 'shedskin translate ... ${opts} <file>' subprocess -- that
subprocess (not the outer 'build' process) is where type-inference-time-only
flags like --retry actually take effect. These tests guard against such
flags silently failing to be forwarded into CMDLINE_OPTIONS.
"""

import argparse
from pathlib import Path

from shedskin import cmake, graph, infer
from shedskin.config import GlobalInfo


def _generate_cmakelists(tmp_path, monkeypatch, **gx_attrs):
    """Parse+analyze demo_program1.py and generate its CMakeLists.txt,
    returning the generated file's contents as a string."""
    demo_path = Path(__file__).parent / "fixtures" / "demo_program1.py"
    monkeypatch.chdir(tmp_path)

    options = argparse.Namespace(
        collect_stats=False,
        include_dirs=[],
        link_dirs=[],
        link_libs=[],
        extra_lib=None,
    )
    gx = GlobalInfo(options)
    gx.silent = True
    gx.source_root = demo_path.parent
    gx.module_path = demo_path
    gx.outputdir = str(tmp_path)
    for name, value in gx_attrs.items():
        setattr(gx, name, value)

    module_name = demo_path.stem
    gx.main_module = graph.parse_module(module_name, gx)
    infer.analyze(gx, module_name)

    cmake.generate_cmakefile(gx)
    return (tmp_path / "CMakeLists.txt").read_text()


def test_retry_forwarded_to_cmdline_options(tmp_path, monkeypatch):
    """--retry only affects the internal translate subprocess's own
    type-inference loop, so it must be forwarded via CMDLINE_OPTIONS."""
    cmakelists = _generate_cmakelists(tmp_path, monkeypatch, retry_maxiters=True)
    assert "--retry" in cmakelists


def test_no_retry_by_default(tmp_path, monkeypatch):
    """Without --retry, CMDLINE_OPTIONS must not mention it."""
    cmakelists = _generate_cmakelists(tmp_path, monkeypatch, retry_maxiters=False)
    assert "--retry" not in cmakelists


def test_silent_forwarded_to_cmdline_options(tmp_path, monkeypatch):
    """--silent must reach the internal 'translate' subprocess too, since
    that's where the per-module 'analyzing types'/'generating C++' progress
    output actually gets printed -- not the outer 'build' process."""
    cmakelists = _generate_cmakelists(tmp_path, monkeypatch, silent=True)
    assert "--silent" in cmakelists


def test_no_silent_by_default(tmp_path, monkeypatch):
    """Without --silent, CMDLINE_OPTIONS must not mention it."""
    cmakelists = _generate_cmakelists(tmp_path, monkeypatch, silent=False)
    assert "--silent" not in cmakelists
