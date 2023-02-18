#!/usr/bin/env python3

import argparse
import glob
import os
import re
import shutil
import sys
from collections import defaultdict
from modulefinder import ModuleFinder
from pathlib import Path

# from pprint import pprint

dep_graph = {
    "array": [],
    "binascii": [],
    "bisect": [],
    "collections": [],
    "colorsys": [],
    "configparser": ["re"],
    "copy": [],
    "csv": [],
    "datetime": ["time", "string"],
    "deque": [],
    "fnmatch": ["os", "re", "os.path"],
    "functools": [],
    "gc": [],
    "getopt": ["os", "sys"],
    "glob": ["os", "os.path", "re", "fnmatch"],
    "heapq": [],
    "io": [],
    "itertools": [],
    "math": [],
    "mmap": [],
    "os": ["os.path"],
    "os.path": ["os", "stat"],
    "random": ["math", "time"],
    "re": [],
    "select": [],
    "signal": [],
    "socket": [],
    "stat": [],
    "string": [],
    "struct": [],
    "sys": [],
    "time": [],
}


def add_shedskin_product(
    sys_modules=None,
    app_modules=None,
    data=None,
    options=None,
    name=None,
    include=None,
    libdir=None,
    build_executable=False,
    build_extension=False,
    build_test=False,
    disable_executable=False,
    disable_extension=False,
    disable_test=False,
    enable_externalproject=False,
    enable_conan=False,
    enable_spm=False,
    debug=False,
):
    """populates a cmake function with the same name

    boolean options:
        DEBUG

    boolean option pairs (setting one unsets the other)
        BUILD_EXECUTABLE BUILD_EXTENSION BUILD_TEST
        DISABLE_EXECUTABLE DISABLE_EXTENSION DISABLE_TEST

    radio options (mutually exclusive):
        ENABLE_CONAN ENABLE_SPM ENABLE_EXTERNALPROJECT

    single_value options:
        NAME INCLUDE LIBDIR

    multiple value options:
        SYS_MODULES APP_MODULES DATA OPTIONS
    """

    def mk_add(lines, spaces=4):
        def _append(level, txt):
            indentation = " " * spaces * level
            lines.append(f"{indentation}{txt}")

        return _append

    f = ["add_shedskin_product("]
    add = mk_add(f)

    if build_executable:
        add(1, "BUILD_EXECUTABLE")
    if disable_executable:
        add(1, "DISABLE_EXECUTABLE")

    if build_extension:
        add(1, "BUILD_EXTENSION")
    if disable_extension:
        add(1, "DISABLE_EXTENSION")

    if build_test:
        add(1, "BUILD_TEST")
    if disable_test:
        add(1, "DISABLE_TEST")

    if enable_externalproject:
        add(1, "ENABLE_EXTERNALPROJECT")
    elif enable_conan:
        add(1, "ENABLE_CONAN")
    elif enable_spm:
        add(1, "ENABLE_SPM")

    if name:
        add(1, f"NAME {name}")
    if include:
        add(1, f"INCLUDE {include}")
    if libdir:
        add(1, f"LIBDIR {libdir}")

    if sys_modules:
        add(1, "SYS_MODULES")
        for m in sorted(sys_modules):
            add(2, m)
    if app_modules:
        add(1, "APP_MODULES")
        for m in sorted(app_modules):
            add(2, m)
    add(0, ")")
    return "\n".join(f)


def update_folders(write_cmakefile=False):
    for p in Path.cwd().iterdir():
        if p.is_dir():
            if p.name in ["scripts", "testdata", "cmake"]:
                continue
            # print(p)
            try:
                update_folder(p, write_cmakefile)
            except:
                print(f"ERROR: {p}")


def generate_cmakefile(pyfile, write_cmakefile=False):
    p = Path(pyfile)
    clfile = p.parent / "CMakeLists.txt"

    def add_sys_deps(sys_mods):
        count = 0
        for m in sys_mods.copy():
            for dep in dep_graph[m]:
                if dep not in sys_mods:
                    count += 1
                    sys_mods.add(dep)
        if count > 0:
            add_sys_deps(sys_mods)

    finder = ModuleFinder(path=[p.name])
    finder.run_script(str(p))
    modules = {}
    modules.update(finder.modules)  # imported and used
    modules.update(finder.badmodules)  # imported but not used
    if len(modules) > 1:  # i.e. there are imports
        sys_mods = set()
        app_mods = set()
        app_mods_paths = set()
        for m in modules:
            if m in dep_graph:
                sys_mods.add(m)
            else:
                app_mods.add(m)
                relpath = os.path.relpath(modules[m].__file__, str(p.parent))
                add_mod_path = relpath[:-3]
                if add_mod_path == p.stem:
                    continue
                app_mods_paths.add(add_mod_path)
        add_sys_deps(sys_mods)
        if write_cmakefile:
            clfile.write_text(add_shedskin_product(sys_mods, app_mods_paths))
    else:
        if write_cmakefile:
            clfile.write_text("add_shedskin_product()\n")


def update_folder(folder, write_cmakefile=False):
    def add_sys_deps(sys_mods):
        count = 0
        for m in sys_mods.copy():
            for dep in dep_graph[m]:
                if dep not in sys_mods:
                    count += 1
                    sys_mods.add(dep)
        if count > 0:
            add_sys_deps(sys_mods)

    p = Path(folder)
    name = p.stem
    # assert p.name.startswith("test_"), f"{folder} is not a test folder"
    testfile = p / f"{name}.py"
    assert testfile.exists(), f"{testfile} does not exist"
    clfile = p / "CMakeLists.txt"
    if write_cmakefile and clfile.exists():
        shutil.copy(clfile, f"{clfile.parent}/{clfile.stem}.bak.txt")
    # check for imports
    finder = ModuleFinder(path=[p.name])
    finder.run_script(str(testfile))
    modules = {}
    modules.update(finder.modules)  # imported and used
    modules.update(finder.badmodules)  # imported but not used
    if len(modules) > 1:  # i.e. there are imports
        sys_mods = set()
        app_mods = set()
        app_mods_paths = set()
        for m in modules:
            if m in dep_graph:
                sys_mods.add(m)
            else:
                app_mods.add(m)
                relpath = os.path.relpath(modules[m].__file__, folder)
                add_mod_path = relpath[:-3]
                if add_mod_path == testfile.stem:
                    continue
                # print('add_mod_path:', add_mod_path)
                app_mods_paths.add(add_mod_path)
        add_sys_deps(sys_mods)
        # print(name, "sys_mods:", sys_mods, "app_mods:", app_mods, "app_paths:", app_mods_paths)
        print(name, add_shedskin_product(sys_mods, app_mods_paths))
        if write_cmakefile:
            clfile.write_text(add_shedskin_product(sys_mods, app_mods_paths))
    else:
        # print(f"{folder} has no imports")
        print(f"{name:.<30}", "add_shedskin_product()")
        if write_cmakefile:
            clfile.write_text("add_shedskin_product()\n")


def move_to_dir(pyfile):
    path = Path(pyfile)
    if path.exists() and path.is_file():
        os.makedirs(path.stem, exist_ok=True)
        targetdir = Path(path.stem)
        targetfile = targetdir / path.name
        path.rename(targetfile)
        generate_cmakefile(targetfile, write_cmakefile=True)


def test_add_shedskin_product():
    print(
        add_shedskin_product(
            name="mymod",
            sys_modules=[
                "random",
                "math",
                "time",
                "sys",
                "re",
            ],
            app_modules=[
                "ml/__init__",
                "ml/camera",
                "ml/image",
                "ml/minilight",
                "ml/raytracer",
                "ml/scene",
                "ml/spatialindex",
                "ml/surfacepoint",
                "ml/triangle",
                "ml/vector3f",
            ],
        )
    )


def get_deps_from_glob_patten(glob_pattern, deps=None, no_builtin=False):
    pattern = re.compile(r'^#include "(\w.+)\.[ch]pp"')
    if not deps:
        deps = defaultdict(set)
    files = sorted(glob.glob(str(glob_pattern)))
    for fpath in files:
        p = Path(fpath)
        if p.stem == "builtin":
            continue
        with open(fpath) as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                match = pattern.match(line)
                if match:
                    matched = match.group(1)
                    if matched in ["__init__"]:
                        continue
                    if matched == "os/__init__":
                        matched = "os"
                    if matched in ["os/path", "path"]:
                        matched = "os.path"
                    if p.parent.name == "lib":
                        name = p.stem
                    else:
                        if p.stem == "__init__":
                            name = p.parent.name
                        else:
                            name = f"{p.parent.name}.{p.stem}"
                    if name in [matched]:
                        continue
                    deps[name].add(matched)
                    if matched == "builtin" and no_builtin:
                        deps[name].remove(matched)
    return deps


def get_shedskin_deps(dump=False, no_builtin=False):
    from shedskin import get_pkg_path

    pkg = get_pkg_path()
    deps = get_deps_from_glob_patten(pkg / "lib/*.[ch]pp", no_builtin=no_builtin)
    deps = get_deps_from_glob_patten(
        pkg / "lib/**/*.[ch]pp", deps, no_builtin=no_builtin
    )
    d = dict(deps)
    # adjustments
    d["datetime"].add("string")
    if dump:
        from pprint import pprint

        pprint(d)
    return d


def gen_graph(deps, title="graph", view=False):
    import graphviz

    # g = graphviz.Digraph(comment='Shedskin Dependencies', engine='sfdp', node_attr={'shape': 'plaintext'})
    g = graphviz.Digraph(
        comment="Shedskin Dependencies",
        engine="dot",
        node_attr={"shape": "record", "height": ".1"},
    )
    # g = graphviz.Digraph(comment='Shedskin Dependencies', engine='sfdp')
    g.attr(rankdir="LR", size="8,5")
    # g.attr(fontsize='10')
    for k, v in deps.items():
        g.node(k)
        for t in v:
            g.edge(k, t)
    # g.unflatten(stagger=3)
    g.render(f"{title}", view=view)
    print(f"{title}.pdf generated")


def gen_shedskin_graph(title="graph"):
    d = get_shedskin_deps()
    gen_graph(d, title, view=True)


def commandline():
    parser = argparse.ArgumentParser(prog="mv_eg", description="utilities")
    arg = opt = parser.add_argument
    opt("-ua", "--update-all", help="update all test directories", action="store_true")
    opt("-u", "--update", help="update specified test directory")
    opt("-w", "--write", help="write cmakefile during update", action="store_true")
    opt("-m", "--move", help="move pyfile to its own cmake subdirectory")
    opt("-d", "--deps", help="print shedskin dependencies", action="store_true")
    opt("-g", "--graph", help="generate graph of shedskin local dependencies", action="store_true")

    args = parser.parse_args()
    if args.update:
        update_folder(args.update, write_cmakefile=args.write)
    elif args.update_all:
        update_folders(write_cmakefile=args.write)
    elif args.move:
        move_to_dir(args.move)
    elif args.deps:
        get_shedskin_deps(dump=True, no_builtin=True)
    elif args.graph:
        gen_shedskin_graph(title="graph")
    else:
        parser.print_help(sys.stderr)
        sys.exit()


if __name__ == "__main__":
    commandline()
