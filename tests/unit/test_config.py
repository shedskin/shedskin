# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.config module."""

import argparse
from pathlib import Path

import pytest

from shedskin.config import GlobalInfo, get_pkg_path
from shedskin.state import (
    BuildConfiguration,
    EntityRegistry,
    FileSystemPaths,
    GraphBuildingContext,
    NamingContext,
    TypeInferenceState,
)


class TestGlobalInfo:
    """Tests for GlobalInfo class."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_init_creates_state_objects(self, gx):
        """GlobalInfo should initialize all state objects."""
        assert hasattr(gx, "_paths")
        assert hasattr(gx, "_naming")
        assert hasattr(gx, "_registry")
        assert hasattr(gx, "_graph_context")
        assert hasattr(gx, "_type_inference")
        assert hasattr(gx, "_build_config")

    def test_filesystem_paths_property_delegation(self, gx):
        """FileSystemPaths properties should be accessible via gx."""
        assert isinstance(gx.cwd, Path)
        assert isinstance(gx.sysdir, str)
        assert isinstance(gx.shedskin_lib, Path)
        assert gx.shedskin_lib.exists()

    def test_naming_context_property_delegation(self, gx):
        """NamingContext properties should be accessible via gx."""
        assert isinstance(gx.cpp_keywords, set)
        assert len(gx.cpp_keywords) > 0
        assert "int" in gx.cpp_keywords  # C++ keyword
        assert gx.ss_prefix == "__ss_"
        assert isinstance(gx.builtins, list)
        assert "str_" in gx.builtins

    def test_build_config_property_delegation(self, gx):
        """BuildConfiguration properties should be accessible via gx."""
        assert gx.bounds_checking is True
        assert gx.wrap_around_check is True
        assert gx.executable_product is True
        assert gx.pyextension_product is False

    def test_build_config_setters(self, gx):
        """BuildConfiguration properties should be settable."""
        gx.bounds_checking = False
        assert gx.bounds_checking is False

        gx.int64 = True
        assert gx.int64 is True

        gx.makefile_name = "CustomMakefile"
        assert gx.makefile_name == "CustomMakefile"

    def test_entity_registry_property_delegation(self, gx):
        """EntityRegistry properties should be accessible via gx."""
        assert isinstance(gx.allfuncs, set)
        assert isinstance(gx.allclasses, set)
        assert isinstance(gx.allvars, set)
        assert isinstance(gx.modules, dict)

    def test_entity_registry_mutable(self, gx):
        """EntityRegistry collections should be mutable."""
        # These are mutable collections, test we can add to them
        initial_len = len(gx.allfuncs)
        gx.allfuncs.add("test_func")  # type: ignore
        assert len(gx.allfuncs) == initial_len + 1

    def test_graph_context_property_delegation(self, gx):
        """GraphBuildingContext properties should be accessible via gx."""
        assert isinstance(gx.tempcount, dict)
        assert isinstance(gx.loopstack, list)
        assert isinstance(gx.genexp_to_lc, dict)

    def test_type_inference_property_delegation(self, gx):
        """TypeInferenceState properties should be accessible via gx."""
        assert isinstance(gx.constraints, set)
        assert isinstance(gx.cnode, dict)
        assert isinstance(gx.types, dict)
        assert gx.iterations == 0

    def test_type_inference_setters(self, gx):
        """TypeInferenceState properties should be settable."""
        gx.iterations = 5
        assert gx.iterations == 5

        gx.cpa_limit = 20
        assert gx.cpa_limit == 20

    def test_libdirs_mutable(self, gx):
        """libdirs should be mutable for --extra-lib support."""
        original = gx.libdirs.copy()
        gx.libdirs = ["/test/path"] + gx.libdirs
        assert gx.libdirs[0] == "/test/path"
        assert len(gx.libdirs) == len(original) + 1

    def test_module_state(self, gx):
        """Module state attributes should be accessible."""
        assert gx.module is None
        assert gx.module_path is None
        assert gx.outputdir is None


class TestStateObjects:
    """Tests for individual state object classes."""

    def test_filesystem_paths_frozen(self):
        """FileSystemPaths should be immutable."""
        paths = FileSystemPaths(
            cwd=Path.cwd(),
            sysdir="/test",
            shedskin_lib=Path("/test/lib"),
            libdirs=("/test/lib",),
            shedskin_resources=Path("/test/resources"),
            shedskin_cmake=Path("/test/cmake"),
            shedskin_flags=Path("/test/flags"),
            shedskin_illegal=Path("/test/illegal"),
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            paths.cwd = Path("/other")  # type: ignore

    def test_build_configuration_mutable(self):
        """BuildConfiguration should be mutable."""
        config = BuildConfiguration()
        config.bounds_checking = False
        assert config.bounds_checking is False

    def test_naming_context_defaults(self):
        """NamingContext should have correct defaults."""
        naming = NamingContext()
        assert naming.ss_prefix == "__ss_"
        assert "str_" in naming.builtins
        assert len(naming.builtins) == 13

    def test_entity_registry_counters(self):
        """EntityRegistry should track ordering counters."""
        registry = EntityRegistry()
        assert registry.class_def_order == 0
        assert registry.import_order == 0

        registry.class_def_order = 5
        assert registry.class_def_order == 5

    def test_graph_building_context_collections(self):
        """GraphBuildingContext should have empty collections by default."""
        ctx = GraphBuildingContext()
        assert len(ctx.tempcount) == 0
        assert len(ctx.loopstack) == 0
        assert len(ctx.genexp_to_lc) == 0

    def test_type_inference_state_defaults(self):
        """TypeInferenceState should have correct defaults."""
        state = TypeInferenceState()
        assert state.iterations == 0
        assert state.cpa_limit == 0
        assert state.cpa_clean is False
        assert len(state.constraints) == 0


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_get_pkg_path(self):
        """get_pkg_path should return shedskin package path."""
        pkg_path = get_pkg_path()
        assert pkg_path.name == "shedskin"
        assert pkg_path.is_dir()
        assert (pkg_path / "__init__.py").exists()


def test_all():
    """Run all tests in this module."""
    pytest.main([__file__, "-v"])
