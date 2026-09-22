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
    gx.infer_v2 = True
    gx.infer_v2_codegen = True
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

def test_backtrace_rdynamic_forwarded_to_link_options(tmp_path, monkeypatch):
    """-rdynamic is a linker flag, not a compiler flag: target_compile_options()
    never passes it to the actual link step, so backtrace_symbols() can't
    resolve the program's own symbols at runtime and --traceback prints a
    useless backtrace. It must be forwarded via LINK_OPTIONS instead."""
    cmakelists = _generate_cmakelists(tmp_path, monkeypatch, backtrace=True)
    assert "LINK_OPTIONS -rdynamic" in cmakelists
    assert "-rdynamic" not in cmakelists.split("COMPILE_OPTIONS")[1].split("\n")[0]
    # guard against the flag block being accidentally duplicated again
    assert cmakelists.count("-D__SS_BACKTRACE") == 1


def test_no_backtrace_by_default(tmp_path, monkeypatch):
    """Without --traceback, neither flag should be forwarded at all."""
    cmakelists = _generate_cmakelists(tmp_path, monkeypatch, backtrace=False)
    assert "-rdynamic" not in cmakelists
    assert "-D__SS_BACKTRACE" not in cmakelists


def test_nogc_forwarded_to_compile_options(tmp_path, monkeypatch):
    """--nogc must reach the compiler as -D__SS_NOGC so the generated C++
    avoids libgc types/allocators."""
    cmakelists = _generate_cmakelists(tmp_path, monkeypatch, nogc=True)
    assert "-D__SS_NOGC" in cmakelists


def test_no_nogc_by_default(tmp_path, monkeypatch):
    """Without --nogc, -D__SS_NOGC must not be forwarded."""
    cmakelists = _generate_cmakelists(tmp_path, monkeypatch, nogc=False)
    assert "-D__SS_NOGC" not in cmakelists


def test_no_gccpp_linked():
    """libgccpp (bdwgc's replacement of the global operator new/delete) must
    not be linked. In extension modules its symbols are kept local (hidden
    visibility, --exclude-libs), so libstdc++ keeps its own operator new while
    shedskin code binds to gccpp's: std::stable_sort's temporary buffer is then
    allocated via libstdc++'s nothrow new (malloc), but released via gccpp's
    sized delete (GC_free), crashing. shedskin allocates everything it traces
    via gc/gc_allocator, so it does not need gccpp (nor libgctba, as builtin.hpp
    defines GC_INCLUDE_NEW).
    """
    root = Path(__file__).parents[2] / "shedskin"
    sources = [
        root / "makefile.py",
        root / "resources" / "cmake" / "fn_add_shedskin_product.cmake",
        root / "resources" / "cmake" / "install_deps.cmake",
        root / "resources" / "cmake" / "shedskin_deps.cmake",
        root / "resources" / "flags" / "FLAGS",
        root / "resources" / "flags" / "FLAGS.osx",
        root / "resources" / "flags" / "FLAGS.mingw",
    ]
    for source in sources:
        for line in source.read_text().splitlines():
            if line.lstrip().startswith("#"):
                continue
            for name in ("gccpp", "GCCPP", "gctba"):
                assert name not in line, f"{source.name}: links {name}: {line.strip()}"
