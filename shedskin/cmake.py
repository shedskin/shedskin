"""
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour and constributors
cmake support contributed by Shakeeb Alireza
License GNU GPL version 3 (See LICENSE)

shedskin cmake builder

api:

    shedskin build pkg/app.py

"""
import modulefinder
import os
import pathlib
import shutil
import subprocess
import sys
import time
import logging
import glob


from .utils import RED, GREEN, YELLOW, RESET
from .depend import ShedskinDependencyManager, ConanDependencyManager


DEPENDENCY_GRAPH = {
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


def get_pkg_path():
    """return shedskin package path"""
    _pkg_path = pathlib.Path(__file__).parent
    assert _pkg_path.name == "shedskin"
    return _pkg_path


def pkg_path():
    """used by cmake to get package path automatically"""
    sys.stdout.write(str(get_pkg_path()))


def check_output(cmd):
    """returns output of shell command"""
    try:
        return subprocess.check_output(cmd.split(), encoding="utf8").strip()
    except FileNotFoundError:
        return None


def add_shedskin_product(
    main_module=None,
    sys_modules=None,
    app_modules=None,
    data=None,
    include_dirs=None,
    link_libs=None,
    link_dirs=None,
    compile_options=None,
    link_options=None,
    cmdline_options=None,
    build_executable=False,
    build_extension=False,
    build_test=False,
    disable_executable=False,
    disable_extension=False,
    disable_test=False,
    has_lib=False,
    enble_conan=False,
    enable_externalproject=False,
    enable_spm=False,
    debug=False,
    name=None,
):
    """populates a cmake function with the same name

    boolean options:
        HAS_LIB
        DEBUG

    boolean option pairs (setting one unsets the other)
        BUILD_EXECUTABLE BUILD_EXTENSION BUILD_TEST
        DISABLE_EXECUTABLE DISABLE_EXTENSION DISABLE_TEST

    radio options (mutually exclusive):
        ENABLE_CONAN ENABLE_SPM ENABLE_EXTERNALPROJECT

    single_value options:
        NAME MAIN_MODULE

    multiple value options:
        SYS_MODULES APP_MODULES DATA
        INCLUDE_DIRS LINK_LIBS LINK_DIRS
        COMPILE_OPTIONS LINK_OPTIONS CMDLINE_OPTIONS
    """

    def mk_add(lines, spaces=4):
        def _append(level, txt):
            indentation = " " * spaces * level
            lines.append(f"{indentation}{txt}")

        return _append

    flist = ["add_shedskin_product("]
    add = mk_add(flist)

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
    elif enble_conan:
        add(1, "ENABLE_CONAN")
    elif enable_spm:
        add(1, "ENABLE_SPM")

    if has_lib:
        add(1, "HAS_LIB")

    if debug:
        add(1, "DEBUG")

    if name:
        add(1, f"NAME {name}")

    if main_module:
        add(1, f"MAIN_MODULE {main_module}")

    if include_dirs:
        add(1, f"INCLUDE_DIRS {include_dirs}")

    if link_libs:
        add(1, f"LINK_LIBS {link_libs}")

    if link_dirs:
        add(1, f"LINK_DIRS {link_dirs}")

    if compile_options:
        add(1, f"COMPILE_OPTIONS {compile_options}")

    if link_options:
        add(1, f"LINK_OPTIONS {link_options}")

    if cmdline_options:
        add(1, f"CMDLINE_OPTIONS {cmdline_options}")

    if sys_modules:
        add(1, "SYS_MODULES")
        for sys_mod in sorted(sys_modules):
            add(2, sys_mod)

    if app_modules:
        add(1, "APP_MODULES")
        for app_mod in sorted(app_modules):
            add(2, app_mod)
    if data:
        add(1, "DATA")
        for elem in sorted(data):
            add(2, elem)

    add(0, ")")
    return "\n".join(flist)


def get_cmakefile_template(name, subdir, section="modular"):
    """returns a cmake template"""
    pkg_path = get_pkg_path()
    cmakelists_tmpl = pkg_path / "resources" / "cmake" / section / "CMakeLists.txt"
    tmpl = cmakelists_tmpl.read_text()
    return tmpl % {"project_name": name, "subdir": subdir}


def generate_cmakefile_0(gx):
    """iniitial generation algorithm (not used)"""
    p = pathlib.Path(gx.main_module.filename)

    src_clfile = p.parent / "CMakeLists.txt"

    def add_sys_deps(sys_mods):
        count = 0
        for m in sys_mods.copy():
            for dep in DEPENDENCY_GRAPH[m]:
                if dep not in sys_mods:
                    count += 1
                    sys_mods.add(dep)
        if count > 0:
            add_sys_deps(sys_mods)

    sys_path = sys.path[:]
    sys_path[0] = str(p.parent)
    finder = modulefinder.ModuleFinder(path=sys_path)
    finder.run_script(str(p))
    modules = {}
    modules.update(finder.modules)  # imported and used
    # modules.update(finder.badmodules)  # imported but not used
    if len(modules) > 1:  # i.e. there are imports
        sys_mods = set()
        app_mods = set()
        app_mods_paths = set()
        for m in modules:
            if m in DEPENDENCY_GRAPH:
                sys_mods.add(m)
            else:
                app_mods.add(m)
                relpath = os.path.relpath(modules[m].__file__, str(p.parent))
                add_mod_path = relpath[:-3]
                if add_mod_path == p.stem:
                    continue
                app_mods_paths.add(add_mod_path)
        add_sys_deps(sys_mods)
        content = add_shedskin_product(p.name, sys_mods, app_mods_paths)
    else:
        content = "add_shedskin_product()\n"

    src_clfile.write_text(content)

    master_clfile = src_clfile.parent.parent / "CMakeLists.txt"
    master_clfile_content = get_cmakefile_template(
        name=f"{gx.main_module.ident}_project",
        subdir=p.parent.name,
    )
    master_clfile.write_text(master_clfile_content)


def generate_cmakefile(gx):
    """improved generator using built-in machinery"""
    p = pathlib.Path(gx.main_module.filename)
    src_clfile = p.parent / "CMakeLists.txt"

    modules = gx.modules.values()
    # filenames = [f'{m.filename.parent / m.filename.stem}' for m in modules]

    sys_mods = set()
    app_mods = set()

    for module in modules:
        if module.builtin:
            entry = module.filename.relative_to(gx.shedskin_lib)
            entry = entry.parent / entry.stem
            if entry.name == 'builtin': # don't include 'builtin' module
                continue
            sys_mods.add(entry)
        else:
            entry = module.filename.relative_to(gx.main_module.filename.parent)
            entry = entry.parent / entry.stem
            if entry.name == p.stem: # don't include main_module
                continue
            app_mods.add(entry)

    src_clfile.write_text(add_shedskin_product(p.name, sys_mods, app_mods))

    master_clfile = src_clfile.parent.parent / "CMakeLists.txt"
    master_clfile_content = get_cmakefile_template(
        name=f"{gx.main_module.ident}_project",
        subdir=p.parent.name,
    )
    master_clfile.write_text(master_clfile_content)



class CMakeBuilder:
    """shedskin cmake builder"""

    def __init__(self, options):
        self.options = options
        self.source_dir = pathlib.Path.cwd().parent
        self.build_dir = self.source_dir / "build"
        self.tests = sorted(glob.glob("./test_*/test_*.py", recursive=True))
        self.log = logging.getLogger(self.__class__.__name__)

    def check(self, path):
        """check file for syntax errors"""
        with open(path, encoding='utf8') as fopen:
            src = fopen.read()
        compile(src, path, "exec")

    def get_most_recent_test(self):
        """returns name of recently modified test"""
        max_mtime = 0
        most_recent_test = None
        for test in self.tests:
            mtime = os.stat(os.path.abspath(test)).st_mtime
            if mtime > max_mtime:
                max_mtime = mtime
                most_recent_test = test
        return most_recent_test

    def error_tests(self):
        """test error messages from tests in errs directory"""
        failures = []
        os.chdir("errs")
        tests = sorted(os.path.basename(t) for t in glob.glob("[0-9][0-9].py"))
        for test in tests:
            print("*** test:", test)
            try:
                checks = []
                for line in open(test):
                    if line.startswith("#*"):
                        checks.append(line[1:].strip())
                cmd = f"{sys.executable} -m shedskin {test}".split()
                output = subprocess.run(
                    cmd, encoding="utf-8", capture_output=True, text=True
                ).stdout
                assert not [l for l in output if "Traceback" in l]
                for check in checks:
                    print(check)
                    assert [l for l in output.splitlines() if l.startswith(check)]
                print(f"*** {GREEN}SUCCESS{RESET}:", test)
            except AssertionError:
                print(f"*** {RED}FAILURE{RESET}:", test)
                failures.append(test)
        os.chdir("..")
        return failures

    def rm_build(self):
        """remove build directory"""
        shutil.rmtree(self.build_dir)

    def mkdir_build(self):
        """create build directory"""
        os.makedirs(self.build_dir, exist_ok=True)

    def cmake_config(self, options):
        """cmake configuration phase"""
        options = " ".join(options)
        cfg_cmd = f"cmake {options} -S {self.source_dir} -B {self.build_dir}"
        self.log.info(cfg_cmd)
        os.system(cfg_cmd)

    def cmake_build(self, options):
        """activate cmake build"""
        options = " ".join(options)
        bld_cmd = f"cmake {options} --build {self.build_dir}"
        self.log.info(bld_cmd)
        os.system(bld_cmd)

    def cmake_test(self, options):
        options = " ".join(options)
        tst_cmd = f"ctest --output-on-failure {options} --test-dir {self.build_dir}"
        print('tst_cmd:', tst_cmd)
        os.system(tst_cmd)

    def run_tests(self):
        self.process(run_tests=True)

    def build(self):
        self.process(run_tests=False)

    def process(self, run_tests=False):
        """build shedskin program"""
        start_time = time.time()

        cfg_options = []
        bld_options = []
        tst_options = []

        # -------------------------------------------------------------------------
        # cfg and bld options

        cfg_options.append("-DBUILD_EXECUTABLE=ON")
        if self.options.extmod:
            cfg_options.append("-DBUILD_EXTENSION=ON")

        if self.options.debug:
            cfg_options.append("-DDEBUG=ON")

        if self.options.generator:
            cfg_options.append(f"-G{self.options.generator}")

        if self.options.build_type:
            cfg_options.append(f" -DCMAKE_BUILD_TYPE={self.options.build_type}")

        if self.options.jobs:
            bld_options.append(f"--parallel {self.options.jobs}")
            tst_options.append(f"--parallel {self.options.jobs}")

        if self.options.ccache:
            if shutil.which("ccache"):
                cfg_options.append("-DCMAKE_CXX_COMPILER_LAUNCHER=ccache")
            else:
                print(f"\n{YELLOW}WARNING{RESET}: 'ccache' not found")

        if self.options.conan:
            cfg_options.append("-DENABLE_CONAN=ON")

        elif self.options.spm:
            cfg_options.append("-DENABLE_SPM=ON")

        elif self.options.extproject:
            cfg_options.append("-DENABLE_EXTERNAL_PROJECT=ON")

        if not cfg_options:
            print(f"{YELLOW}no configuration options selected{RESET}")
            return

        if self.build_dir.exists() and self.options.reset:
            self.rm_build()

        if not self.build_dir.exists():
            self.mkdir_build()

        if self.options.conan:
            dpm = ConanDependencyManager(self.source_dir)
            dpm.generate_conanfile()
            dpm.install()

        elif self.options.spm:
            dpm = ShedskinDependencyManager(self.source_dir)
            dpm.install_all()

        if self.options.target:
            target_suffix = "-exe"
            for target in self.options.target:
                bld_options.append(f"--target {target}{target_suffix}")
                tst_options.append(f"--tests-regex {target}{target_suffix}")

        # -------------------------------------------------------------------------
        # test options

        if run_tests:

            if self.options.include:
                self.tst_options.append(f"--tests-regex {self.options.include}")

            if self.options.check:
                self.check(self.options.name) # check python syntax

            if self.options.modified:
                most_recent_test = pathlib.Path(self.get_most_recent_test()).stem
                bld_options.append(f"--target {most_recent_test}")
                tst_options.append(f"--tests-regex {most_recent_test}")

            #nocleanup

            if self.options.pytest:
                try:
                    import pytest
                    os.system('pytest')
                except ImportError:
                    print('pytest not found')
                print()

            if self.options.run:
                target_suffix = '-exe'
                if self.options.extmod:
                    target_suffix = '-ext'
                bld_options.append(f"--target {self.options.run}{target_suffix}")
                tst_options.append(f"--tests-regex {self.options.run}")

            if self.options.stoponfail:
                self.tst_options.append("--stop-on-failure")

            if self.options.progress:
                self.tst_options.append("--progress")

        self.cmake_config(cfg_options)

        self.cmake_build(bld_options)

        if run_tests:
            self.cmake_test(tst_options)

        if run_tests:
            if self.options.run_errs:
                failures = self.error_tests()
                if not failures:
                    print(f'==> {GREEN}NO FAILURES, yay!{RESET}')
                else:
                    print(f'==> {RED}TESTS FAILED:{RESET}', len(failures))
                    print(failures)
                    sys.exit()

        end_time = time.time()
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))
        print(f"Total time: {elapsed_time}\n")

