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

if TYPE_CHECKING:
    import ast

    from . import infer, python
    from .utils import ProgressBar

# types aliases
CartesianProduct: TypeAlias = Tuple[Tuple["python.Class", int], ...]

# constants
PLATFORM = platform.system()


# classes
class GlobalInfo:  # XXX add comments, split up
    """Global configuration and state for the shedskin compiler"""

    def __init__(self, options: argparse.Namespace):
        self.options = options
        self.constraints: set[tuple["infer.CNode", "infer.CNode"]] = set()
        self.allvars: set["python.Variable"] = set()
        self.allfuncs: set["python.Function"] = set()
        self.allclasses: set["python.Class"] = set()
        self.cnode: dict[Tuple[Any, int, int], "infer.CNode"] = {}
        self.types: dict["infer.CNode", set[Tuple[Any, int]]] = {}
        self.orig_types: dict["infer.CNode", set[Tuple[Any, int]]] = {}
        self.templates: int = 0
        self.modules: dict[str, "python.Module"] = {}
        self.inheritance_relations: dict[
            Union["python.Function", "ast.AST"],
            List[Union["python.Function", "ast.AST"]],
        ] = {}
        self.inheritance_temp_vars: dict[
            "python.Variable", List["python.Variable"]
        ] = {}
        self.parent_nodes: dict[ast.AST, ast.AST] = {}
        self.inherited: set[ast.AST] = set()
        self.main_module: "python.Module"
        self.module: Optional["python.Module"] = None
        self.module_path: Optional[Path] = None
        self.cwd: Path = Path.cwd()
        self.builtins: list[str] = [
            "none",
            "str_",
            "bytes_",
            "float_",
            "int_",
            "class_",
            "list",
            "tuple",
            "tuple2",
            "dict",
            "set",
            "frozenset",
            "bool_",
        ]
        # instance node for instance Variable assignment
        self.assign_target: dict[ast.AST, ast.AST] = {}
        # allocation site type information across iterations
        self.alloc_info: dict[
            Tuple[str, CartesianProduct, ast.AST], Tuple["python.Class", int]
        ] = {}
        self.new_alloc_info: dict[
            Tuple[str, CartesianProduct, ast.AST], Tuple["python.Class", int]
        ] = {}
        self.iterations: int = 0
        self.total_iterations: int = 0
        self.lambdawrapper: dict[Any, str] = {}
        self.init_directories()
        illegal_file = open(self.shedskin_illegal / "illegal.txt")
        self.cpp_keywords = set(line.strip() for line in illegal_file)
        self.ss_prefix: str = "__ss_"
        self.list_types: dict[Tuple[int, ast.AST], int] = {}
        self.loopstack: List[Union[ast.While, ast.For]] = []  # track nested loops
        #        self.comments = {}  # TODO not filled anymore?
        self.import_order: int = 0  # module import order
        self.from_module: dict[ast.AST, "python.Module"] = {}
        self.class_def_order: int = 0
        # command-line options
        self.wrap_around_check: bool = True
        self.bounds_checking: bool = True
        self.assertions: bool = True
        self.executable_product: bool = True
        self.pyextension_product: bool = False
        self.int32: bool = False
        self.int64: bool = False
        self.int128: bool = False
        self.float32: bool = False
        self.float64: bool = False
        self.flags: Optional[Path] = None
        self.silent: bool = False
        self.nogc: bool = False
        self.backtrace: bool = False
        self.makefile_name: str = "Makefile"
        self.debug_level: int = 0
        self.outputdir: Optional[str] = None
        self.nomakefile: bool = False

        # Others
        self.item_rvalue: dict[ast.AST, ast.AST] = {}
        self.genexp_to_lc: dict[ast.GeneratorExp, ast.ListComp] = {}
        self.setcomp_to_lc: dict[ast.SetComp, ast.ListComp] = {}
        self.dictcomp_to_lc: dict[ast.DictComp, ast.ListComp] = {}
        self.bool_test_only: set[ast.AST] = set()
        self.called: set[ast.Attribute] = set()
        self.tempcount: dict[Any, str] = {}
        self.struct_unpack: dict[
            ast.Assign, Tuple[List[Tuple[str, str, str, int]], str, str]
        ] = {}
        self.augment: set[ast.AST] = set()

        self.maxhits = 0  # XXX amaze.py termination
        self.terminal = None
        self.progressbar: Optional["ProgressBar"] = None
        self.generate_cmakefile: bool = False

        # from infer.py
        self.added_allocs: int = 0
        self.added_allocs_set: set[Any] = set()
        self.added_funcs: int = 0
        self.added_funcs_set: set["python.Function"] = set()
        self.cpa_clean: bool = False
        self.cpa_limit: int = 0
        self.cpa_limited: bool = False
        self.merged_inh: dict[Any, set[Tuple[Any, int]]] = {}

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

    def init_directories(self) -> None:
        """Initialize directory paths"""
        abspath = os.path.abspath(__file__)  # sanitize mixed fwd/bwd slashes (mingw)
        shedskin_directory = os.sep.join(abspath.split(os.sep)[:-1])
        for dirname in sys.path:
            if os.path.exists(os.path.join(dirname, shedskin_directory)):
                shedskin_directory = os.path.join(dirname, shedskin_directory)
                break
        shedskin_libdir = os.path.join(shedskin_directory, "lib")
        self.shedskin_lib = Path(shedskin_libdir)
        system_libdir = "/usr/share/shedskin/lib"
        self.sysdir = shedskin_directory
        # set resources subdirectors
        self.shedskin_resources = Path(shedskin_directory) / "resources"
        self.shedskin_cmake = self.shedskin_resources / "cmake" / "modular"
        self.shedskin_conan = self.shedskin_resources / "conan"
        self.shedskin_flags = self.shedskin_resources / "flags"
        self.shedskin_illegal = self.shedskin_resources / "illegal"

        if os.path.isdir(shedskin_libdir):
            self.libdirs = [shedskin_libdir]
        elif os.path.isdir(system_libdir):
            self.libdirs = [system_libdir]
        else:
            print(
                "*ERROR* Could not find lib directory in %s or %s.\n"
                % (shedskin_libdir, system_libdir)
            )
            sys.exit(1)


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
