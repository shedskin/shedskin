# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.config: contains the main shedskin global configuration class

`GlobalInfo` which is referred to in shedskin as `gx`.
"""

import argparse
import os
import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, TypeAlias, Union

from .state import (
    BuildConfiguration,
    EntityRegistry,
    FileSystemPaths,
    GraphBuildingContext,
    NamingContext,
    TypeInferenceState,
)

if TYPE_CHECKING:
    import ast

    from . import infer, python
    from .utils import ProgressBar

# types aliases
CartesianProduct: TypeAlias = Tuple[Tuple["python.Class", int], ...]

# constants
PLATFORM = platform.system()


# classes
class GlobalInfo:
    """Global configuration and state for the shedskin compiler.

    This class uses focused state objects internally while maintaining
    backwards-compatible attribute access via property delegation.
    """

    def __init__(self, options: argparse.Namespace):
        self.options = options

        # Initialize filesystem paths first (needed for cpp_keywords)
        self._paths = self._init_directories()

        # Load C++ keywords from illegal.txt
        illegal_file = open(self._paths.shedskin_illegal / "illegal.txt")
        cpp_keywords = set(line.strip() for line in illegal_file)
        illegal_file.close()

        # Initialize focused state objects
        self._naming = NamingContext(cpp_keywords=cpp_keywords)
        self._registry = EntityRegistry()
        self._graph_context = GraphBuildingContext()
        self._type_inference = TypeInferenceState()

        # Build configuration - defaults, updated by Shedskin.configure()
        self._build_config = BuildConfiguration()

        # Mutable copy of libdirs (can be modified via --extra-lib)
        self._libdirs: List[str] = list(self._paths.libdirs)

        # Mutable module state (not in state objects)
        self.main_module: "python.Module"
        self.module: Optional["python.Module"] = None
        self.module_path: Optional[Path] = None
        self.outputdir: Optional[str] = None

        # UI/terminal state
        self.terminal = None
        self.progressbar: Optional["ProgressBar"] = None

    def _init_directories(self) -> FileSystemPaths:
        """Initialize and return filesystem paths."""
        abspath = os.path.abspath(__file__)  # sanitize mixed fwd/bwd slashes (mingw)
        shedskin_directory = os.sep.join(abspath.split(os.sep)[:-1])
        for dirname in sys.path:
            if os.path.exists(os.path.join(dirname, shedskin_directory)):
                shedskin_directory = os.path.join(dirname, shedskin_directory)
                break
        shedskin_libdir = os.path.join(shedskin_directory, "lib")
        shedskin_lib = Path(shedskin_libdir)
        system_libdir = "/usr/share/shedskin/lib"

        shedskin_resources = Path(shedskin_directory) / "resources"

        if os.path.isdir(shedskin_libdir):
            libdirs = (shedskin_libdir,)
        elif os.path.isdir(system_libdir):
            libdirs = (system_libdir,)
        else:
            print(
                "*ERROR* Could not find lib directory in %s or %s.\n"
                % (shedskin_libdir, system_libdir)
            )
            sys.exit(1)

        return FileSystemPaths(
            cwd=Path.cwd(),
            sysdir=shedskin_directory,
            shedskin_lib=shedskin_lib,
            libdirs=libdirs,
            shedskin_resources=shedskin_resources,
            shedskin_cmake=shedskin_resources / "cmake" / "modular",
            shedskin_conan=shedskin_resources / "conan",
            shedskin_flags=shedskin_resources / "flags",
            shedskin_illegal=shedskin_resources / "illegal",
        )

    def set_build_config(self, config: BuildConfiguration) -> None:
        """Set the build configuration (called after Shedskin.configure())."""
        self._build_config = config

    # -------------------------------------------------------------------------
    # Property delegation for backwards compatibility
    # -------------------------------------------------------------------------

    # FileSystemPaths delegation
    @property
    def cwd(self) -> Path:
        return self._paths.cwd

    @property
    def sysdir(self) -> str:
        return self._paths.sysdir

    @property
    def shedskin_lib(self) -> Path:
        return self._paths.shedskin_lib

    @property
    def libdirs(self) -> List[str]:
        return self._libdirs

    @libdirs.setter
    def libdirs(self, value: List[str]) -> None:
        self._libdirs = value

    @property
    def shedskin_resources(self) -> Path:
        return self._paths.shedskin_resources

    @property
    def shedskin_cmake(self) -> Path:
        return self._paths.shedskin_cmake

    @property
    def shedskin_conan(self) -> Path:
        return self._paths.shedskin_conan

    @property
    def shedskin_flags(self) -> Path:
        return self._paths.shedskin_flags

    @property
    def shedskin_illegal(self) -> Path:
        return self._paths.shedskin_illegal

    # NamingContext delegation
    @property
    def cpp_keywords(self) -> set[str]:
        return self._naming.cpp_keywords

    @property
    def ss_prefix(self) -> str:
        return self._naming.ss_prefix

    @property
    def builtins(self) -> list[str]:
        return self._naming.builtins

    # BuildConfiguration delegation
    @property
    def wrap_around_check(self) -> bool:
        return self._build_config.wrap_around_check

    @wrap_around_check.setter
    def wrap_around_check(self, value: bool) -> None:
        self._build_config.wrap_around_check = value

    @property
    def bounds_checking(self) -> bool:
        return self._build_config.bounds_checking

    @bounds_checking.setter
    def bounds_checking(self, value: bool) -> None:
        self._build_config.bounds_checking = value

    @property
    def assertions(self) -> bool:
        return self._build_config.assertions

    @assertions.setter
    def assertions(self, value: bool) -> None:
        self._build_config.assertions = value

    @property
    def executable_product(self) -> bool:
        return self._build_config.executable_product

    @executable_product.setter
    def executable_product(self, value: bool) -> None:
        self._build_config.executable_product = value

    @property
    def pyextension_product(self) -> bool:
        return self._build_config.pyextension_product

    @pyextension_product.setter
    def pyextension_product(self, value: bool) -> None:
        self._build_config.pyextension_product = value

    @property
    def int32(self) -> bool:
        return self._build_config.int32

    @int32.setter
    def int32(self, value: bool) -> None:
        self._build_config.int32 = value

    @property
    def int64(self) -> bool:
        return self._build_config.int64

    @int64.setter
    def int64(self, value: bool) -> None:
        self._build_config.int64 = value

    @property
    def int128(self) -> bool:
        return self._build_config.int128

    @int128.setter
    def int128(self, value: bool) -> None:
        self._build_config.int128 = value

    @property
    def float32(self) -> bool:
        return self._build_config.float32

    @float32.setter
    def float32(self, value: bool) -> None:
        self._build_config.float32 = value

    @property
    def float64(self) -> bool:
        return self._build_config.float64

    @float64.setter
    def float64(self, value: bool) -> None:
        self._build_config.float64 = value

    @property
    def flags(self) -> Optional[Path]:
        return self._build_config.flags

    @flags.setter
    def flags(self, value: Optional[Path]) -> None:
        self._build_config.flags = value

    @property
    def silent(self) -> bool:
        return self._build_config.silent

    @silent.setter
    def silent(self, value: bool) -> None:
        self._build_config.silent = value

    @property
    def nogc(self) -> bool:
        return self._build_config.nogc

    @nogc.setter
    def nogc(self, value: bool) -> None:
        self._build_config.nogc = value

    @property
    def backtrace(self) -> bool:
        return self._build_config.backtrace

    @backtrace.setter
    def backtrace(self, value: bool) -> None:
        self._build_config.backtrace = value

    @property
    def makefile_name(self) -> str:
        return self._build_config.makefile_name

    @makefile_name.setter
    def makefile_name(self, value: str) -> None:
        self._build_config.makefile_name = value

    @property
    def debug_level(self) -> int:
        return self._build_config.debug_level

    @debug_level.setter
    def debug_level(self, value: int) -> None:
        self._build_config.debug_level = value

    @property
    def nomakefile(self) -> bool:
        return self._build_config.nomakefile

    @nomakefile.setter
    def nomakefile(self, value: bool) -> None:
        self._build_config.nomakefile = value

    @property
    def generate_cmakefile(self) -> bool:
        return self._build_config.generate_cmakefile

    @generate_cmakefile.setter
    def generate_cmakefile(self, value: bool) -> None:
        self._build_config.generate_cmakefile = value

    # EntityRegistry delegation
    @property
    def allfuncs(self) -> set["python.Function"]:
        return self._registry.allfuncs

    @property
    def allclasses(self) -> set["python.Class"]:
        return self._registry.allclasses

    @property
    def allvars(self) -> set["python.Variable"]:
        return self._registry.allvars

    @property
    def modules(self) -> dict[str, "python.Module"]:
        return self._registry.modules

    @property
    def inheritance_relations(self) -> dict[
        Union["python.Function", "ast.AST"],
        List[Union["python.Function", "ast.AST"]],
    ]:
        return self._registry.inheritance_relations

    @property
    def inheritance_temp_vars(self) -> dict[
        "python.Variable", List["python.Variable"]
    ]:
        return self._registry.inheritance_temp_vars

    @property
    def inherited(self) -> set["ast.AST"]:
        return self._registry.inherited

    @property
    def lambdawrapper(self) -> dict[Any, str]:
        return self._registry.lambdawrapper

    @property
    def class_def_order(self) -> int:
        return self._registry.class_def_order

    @class_def_order.setter
    def class_def_order(self, value: int) -> None:
        self._registry.class_def_order = value

    @property
    def import_order(self) -> int:
        return self._registry.import_order

    @import_order.setter
    def import_order(self, value: int) -> None:
        self._registry.import_order = value

    # GraphBuildingContext delegation
    @property
    def tempcount(self) -> dict[Any, str]:
        return self._graph_context.tempcount

    @property
    def loopstack(self) -> List[Union["ast.While", "ast.For"]]:
        return self._graph_context.loopstack

    @property
    def genexp_to_lc(self) -> dict["ast.GeneratorExp", "ast.ListComp"]:
        return self._graph_context.genexp_to_lc

    @property
    def setcomp_to_lc(self) -> dict["ast.SetComp", "ast.ListComp"]:
        return self._graph_context.setcomp_to_lc

    @property
    def dictcomp_to_lc(self) -> dict["ast.DictComp", "ast.ListComp"]:
        return self._graph_context.dictcomp_to_lc

    @property
    def bool_test_only(self) -> set["ast.AST"]:
        return self._graph_context.bool_test_only

    @property
    def called(self) -> set["ast.Attribute"]:
        return self._graph_context.called

    @property
    def item_rvalue(self) -> dict["ast.AST", "ast.AST"]:
        return self._graph_context.item_rvalue

    @property
    def assign_target(self) -> dict["ast.AST", "ast.AST"]:
        return self._graph_context.assign_target

    @property
    def struct_unpack(self) -> dict[
        "ast.Assign", Tuple[List[Tuple[str, str, str, int]], str, str]
    ]:
        return self._graph_context.struct_unpack

    @property
    def augment(self) -> set["ast.AST"]:
        return self._graph_context.augment

    @property
    def parent_nodes(self) -> dict["ast.AST", "ast.AST"]:
        return self._graph_context.parent_nodes

    @property
    def from_module(self) -> dict["ast.AST", "python.Module"]:
        return self._graph_context.from_module

    @property
    def list_types(self) -> dict[Tuple[int, "ast.AST"], int]:
        return self._graph_context.list_types

    # TypeInferenceState delegation
    @property
    def constraints(self) -> set[tuple["infer.CNode", "infer.CNode"]]:
        return self._type_inference.constraints

    @constraints.setter
    def constraints(self, value: set[tuple["infer.CNode", "infer.CNode"]]) -> None:
        self._type_inference.constraints = value

    @property
    def cnode(self) -> dict[Tuple[Any, int, int], "infer.CNode"]:
        return self._type_inference.cnode

    @cnode.setter
    def cnode(self, value: dict[Tuple[Any, int, int], "infer.CNode"]) -> None:
        self._type_inference.cnode = value

    @property
    def types(self) -> dict["infer.CNode", set[Tuple[Any, int]]]:
        return self._type_inference.types

    @types.setter
    def types(self, value: dict["infer.CNode", set[Tuple[Any, int]]]) -> None:
        self._type_inference.types = value

    @property
    def orig_types(self) -> dict["infer.CNode", set[Tuple[Any, int]]]:
        return self._type_inference.orig_types

    @orig_types.setter
    def orig_types(self, value: dict["infer.CNode", set[Tuple[Any, int]]]) -> None:
        self._type_inference.orig_types = value

    @property
    def alloc_info(self) -> dict[
        Tuple[str, CartesianProduct, "ast.AST"], Tuple["python.Class", int]
    ]:
        return self._type_inference.alloc_info

    @alloc_info.setter
    def alloc_info(self, value: dict[
        Tuple[str, CartesianProduct, "ast.AST"], Tuple["python.Class", int]
    ]) -> None:
        self._type_inference.alloc_info = value

    @property
    def new_alloc_info(self) -> dict[
        Tuple[str, CartesianProduct, "ast.AST"], Tuple["python.Class", int]
    ]:
        return self._type_inference.new_alloc_info

    @new_alloc_info.setter
    def new_alloc_info(self, value: dict[
        Tuple[str, CartesianProduct, "ast.AST"], Tuple["python.Class", int]
    ]) -> None:
        self._type_inference.new_alloc_info = value

    @property
    def iterations(self) -> int:
        return self._type_inference.iterations

    @iterations.setter
    def iterations(self, value: int) -> None:
        self._type_inference.iterations = value

    @property
    def total_iterations(self) -> int:
        return self._type_inference.total_iterations

    @total_iterations.setter
    def total_iterations(self, value: int) -> None:
        self._type_inference.total_iterations = value

    @property
    def templates(self) -> int:
        return self._type_inference.templates

    @templates.setter
    def templates(self, value: int) -> None:
        self._type_inference.templates = value

    @property
    def added_allocs(self) -> int:
        return self._type_inference.added_allocs

    @added_allocs.setter
    def added_allocs(self, value: int) -> None:
        self._type_inference.added_allocs = value

    @property
    def added_allocs_set(self) -> set[Any]:
        return self._type_inference.added_allocs_set

    @added_allocs_set.setter
    def added_allocs_set(self, value: set[Any]) -> None:
        self._type_inference.added_allocs_set = value

    @property
    def added_funcs(self) -> int:
        return self._type_inference.added_funcs

    @added_funcs.setter
    def added_funcs(self, value: int) -> None:
        self._type_inference.added_funcs = value

    @property
    def added_funcs_set(self) -> set["python.Function"]:
        return self._type_inference.added_funcs_set

    @added_funcs_set.setter
    def added_funcs_set(self, value: set["python.Function"]) -> None:
        self._type_inference.added_funcs_set = value

    @property
    def cpa_clean(self) -> bool:
        return self._type_inference.cpa_clean

    @cpa_clean.setter
    def cpa_clean(self, value: bool) -> None:
        self._type_inference.cpa_clean = value

    @property
    def cpa_limit(self) -> int:
        return self._type_inference.cpa_limit

    @cpa_limit.setter
    def cpa_limit(self, value: int) -> None:
        self._type_inference.cpa_limit = value

    @property
    def cpa_limited(self) -> bool:
        return self._type_inference.cpa_limited

    @cpa_limited.setter
    def cpa_limited(self, value: bool) -> None:
        self._type_inference.cpa_limited = value

    @property
    def merged_inh(self) -> dict[Any, set[Tuple[Any, int]]]:
        return self._type_inference.merged_inh

    @merged_inh.setter
    def merged_inh(self, value: dict[Any, set[Tuple[Any, int]]]) -> None:
        self._type_inference.merged_inh = value

    @property
    def maxhits(self) -> int:
        return self._type_inference.maxhits

    @maxhits.setter
    def maxhits(self, value: int) -> None:
        self._type_inference.maxhits = value

    def get_stats(self) -> dict[str, Any]:
        pyfile = Path(self.module_path)
        return {
            "name": pyfile.stem,
            "filename": str(pyfile),
            "n_words": 0,
            "sloc": 0,
            "prebuild_secs": 0.0,
            "build_secs": 0.0,
            "run_secs": 0.0,
            "n_constraints": len(self.constraints),
            "n_vars": len(self.allvars),
            "n_funcs": len(self.allfuncs),
            "n_classes": len(self.allclasses),
            "n_cnodes": len(self.cnode.keys()),
            "n_types": len(self.types.keys()),
            "n_orig_types": len(self.orig_types.keys()),
            "n_modules": len(self.modules.keys()),
            "n_templates": self.templates,
            "n_inheritance_relations": len(self.inheritance_relations.keys()),
            "n_inheritance_temp_vars": len(self.inheritance_temp_vars.keys()),
            "n_parent_nodes": len(self.parent_nodes.keys()),
            "n_inherited": len(self.inherited),
            "n_assign_target": len(self.assign_target.keys()),
            "n_alloc_info": len(self.alloc_info.keys()),
            "n_new_alloc_info": len(self.new_alloc_info.keys()),
            "n_iterations": self.iterations,
            "total_iterations": self.total_iterations,
            "n_called": len(self.called),
            "added_allocs": self.added_allocs,
            "added_funcs": self.added_funcs,
            "cpa_limit": self.cpa_limit,
            # commandline-options
            "wrap_around_check": self.wrap_around_check,
            "bounds_checking": self.bounds_checking,
            "assertions": self.assertions,
            "executable_product": self.executable_product,
            "pyextension_product": self.pyextension_product,
            "int32": self.int32,
            "int64": self.int64,
            "int128": self.int128,
            "float32": self.float32,
            "float64": self.float64,
            "silent": self.silent,
            "nogc": self.nogc,
            "backtrace": self.backtrace,
        }


# utility functions


def get_pkg_path() -> Path:
    """Return the path to the shedskin package"""
    _pkg_path = Path(__file__).parent
    assert _pkg_path.name == "shedskin"
    return _pkg_path


def get_user_cache_dir() -> Path:
    """Get user cache directory depending on platform"""
    if PLATFORM == "Darwin":
        return Path("~/Library/Caches/shedskin").expanduser()
    if PLATFORM == "Linux":
        return Path("~/.cache/shedskin").expanduser()
    if PLATFORM == "Windows":
        profile = os.getenv("USERPROFILE")
        if not profile:
            raise SystemExit("USERPROFILE environment variable not set on windows")
        user_dir = Path(profile)
        return user_dir / "AppData" / "Local" / "shedskin" / "Cache"
    raise SystemExit(f"{PLATFORM} os not supported")
