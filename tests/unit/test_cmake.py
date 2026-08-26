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


def test_static_gc_lib_order_gccpp_before_gc():
    """Regression test for a static-link failure: gc_cpp.cc (bundled in
    libgccpp) calls GC_malloc_uncollectable()/GC_free(), which are only
    defined in libgc. Static archives are searched left-to-right by the
    linker, so libgccpp must be listed *before* libgc in LIB_DEPS, or the
    link fails with 'undefined reference to GC_malloc_uncollectable' (this
    is exactly what 'shedskin build --nogc' hit with ENABLE_LOCAL_DEPS).
    This only checks the raw-archive-path branches (ENABLE_SPM,
    ENABLE_LOCAL_DEPS); ENABLE_FETCH_CONTENT links CMake targets, whose
    inter-target dependency order CMake resolves itself.
    """
    cmake_module = (
        Path(__file__).parents[2]
        / "shedskin"
        / "resources"
        / "cmake"
        / "fn_add_shedskin_product.cmake"
    )
    text = cmake_module.read_text()

    for block_start in ("elseif(ENABLE_SPM)", "elseif(ENABLE_LOCAL_DEPS)"):
        start = text.index(block_start)
        # the LIB_DEPS assignment immediately follows within this branch
        lib_deps_start = text.index("set(LIB_DEPS", start)
        lib_deps_end = text.index(")", lib_deps_start)
        block = text[lib_deps_start:lib_deps_end]
        gccpp_pos = block.index("LIBGCCPP")
        gc_pos = block.index("LIBGC}")
        assert gccpp_pos < gc_pos, (
            f"{block_start}: LIBGCCPP must be listed before LIBGC in LIB_DEPS"
        )
