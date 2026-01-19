# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Shared pytest fixtures for unit tests."""

import argparse

import pytest

from shedskin.config import GlobalInfo


@pytest.fixture
def default_options():
    """Create default argparse options namespace."""
    return argparse.Namespace()


@pytest.fixture
def gx(default_options):
    """Create a GlobalInfo instance with default options."""
    return GlobalInfo(default_options)
