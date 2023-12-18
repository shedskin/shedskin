"""
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2023 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)

"""
import os
import sys
import pathlib


class GlobalInfo:  # XXX add comments, split up
    def __init__(self):
        self.constraints = set()
        self.allvars = set()
        self.allfuncs = set()
        self.allclasses = set()
        self.cnode = {}
        self.types = {}
        self.templates = 0
        self.modules = {}
        self.inheritance_relations = {}
        self.inheritance_temp_vars = {}
        self.parent_nodes = {}
        self.inherited = set()
        self.nrcltypes = 8
        self.empty_constructors = set()
        self.sig_nr = {}
        self.nameclasses = {}
        self.module = None
        self.module_path = None
        self.cwd = pathlib.Path.cwd()
        self.builtins = [
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
        self.assign_target = {}
        # allocation site type information across iterations
        self.alloc_info = {}
        self.iterations = 0
        self.total_iterations = 0
        self.lambdawrapper = {}
        self.init_directories()
        illegal_file = open(self.shedskin_illegal /  "illegal.txt")
        self.cpp_keywords = set(line.strip() for line in illegal_file)
        self.ss_prefix = "__ss_"
        self.list_types = {}
        self.loopstack = []  # track nested loops
        self.filterstack = []  # track 'if isinstance(..)'
        self.filters = {}  # syntax node filter determined using filterstack
        self.comments = {}
        self.import_order = 0  # module import order
        self.from_module = {}
        self.class_def_order = 0
        # command-line options
        self.wrap_around_check = True
        self.bounds_checking = True
        self.assertions = True
        self.executable_product = True
        self.pyextension_product = False
        self.longlong = False
        self.float = False
        self.flags = None
        self.silent = False
        self.nogc = False
        self.gcwarns = True
        self.backtrace = False
        self.makefile_name = "Makefile"
        self.debug_level = 0
        self.outputdir = None
        self.nomakefile = False

        # Others
        self.item_rvalue = {}
        self.genexp_to_lc = {}
        self.bool_test_only = set()
        self.tempcount = {}
        self.struct_unpack = {}
        self.maxhits = 0  # XXX amaze.py termination
        self.gc_cleanup = False
        self.terminal = None
        self.progressbar = None
        self.generate_cmakefile = False

    def init_directories(self):
        abspath = os.path.abspath(__file__) # sanitize mixed fwd/bwd slashes (mingw)
        shedskin_directory = os.sep.join(abspath.split(os.sep)[:-1])
        for dirname in sys.path:
            if os.path.exists(os.path.join(dirname, shedskin_directory)):
                shedskin_directory = os.path.join(dirname, shedskin_directory)
                break
        shedskin_libdir = os.path.join(shedskin_directory, "lib")
        self.shedskin_lib = pathlib.Path(shedskin_libdir)
        system_libdir = "/usr/share/shedskin/lib"
        self.sysdir = shedskin_directory
        # set resources subdirectors
        self.shedskin_resources = pathlib.Path(shedskin_directory) / "resources"
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
