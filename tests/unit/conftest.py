# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Shared pytest fixtures for unit tests."""

import argparse
from pathlib import Path

import pytest

from shedskin.config import GlobalInfo
from shedskin import cpp, graph, infer


@pytest.fixture
def default_options():
    """Create default argparse options namespace."""
    return argparse.Namespace()


@pytest.fixture
def gx(default_options):
    """Create a GlobalInfo instance with default options."""
    return GlobalInfo(default_options)


@pytest.fixture(scope="session")
def analyzed_demo():
    """Run the full shedskin pipeline (parse + infer) on demo_program.py.

    Returns the GlobalInfo object after analysis, with all type inference
    and virtual analysis complete. This is a session-scoped fixture so the
    expensive analysis runs only once.
    """
    demo_path = Path(__file__).parent / "fixtures" / "demo_program1.py"

    options = argparse.Namespace()
    gx = GlobalInfo(options)
    gx.silent = True
    gx.source_root = demo_path.parent
    gx.module_path = demo_path

    module_name = demo_path.stem
    gx.main_module = graph.parse_module(module_name, gx)
    infer.analyze(gx, module_name)

    return gx


@pytest.fixture(scope="session")
def generated_demo(analyzed_demo, tmp_path_factory):
    """Run C++ code generation on the analyzed demo program.

    Returns (gx, output_dir) after generate_code has written .cpp/.hpp files.
    """
    gx = analyzed_demo
    output_dir = tmp_path_factory.mktemp("demo_output")
    gx.outputdir = str(output_dir)

    cpp.generate_code(gx)

    return gx, output_dir
