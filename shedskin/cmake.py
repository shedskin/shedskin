"""
# *** SHED SKIN Python-to-C++ Compiler ***
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
import textwrap
import time

from .utils import WHITE, CYAN, YELLOW, RESET

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
        # name=f'{main_module}_project',
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



class ConanDependency:
    """mixin for conand dependencies"""
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def __str__(self):
        return f"{self.name}/{self.version}"


class ConanBDWGC(ConanDependency):
    """boehm gc dependency'"""
    def __init__(
        self,
        name="bdwgc",
        version="8.2.2",
        cplusplus=True,
        cord=False,
        gcj_support=False,
        java_finalization=False,
        shared=False,
    ):
        self.name = name
        self.version = version
        self.cplusplus = cplusplus
        self.cord = cord
        self.gcj_support = gcj_support
        self.java_finalization = java_finalization
        self.shared = shared


class ConanPCRE(ConanDependency):
    """boehm gc dependency'"""
    def __init__(
        self,
        name="pcre",
        version="8.45",
        build_pcrecpp=True,
        build_pcregrep=False,
        shared=False,
        with_bzip2=False,
        with_zlib=False,
    ):
        self.name = name
        self.version = version
        self.build_pcrecpp = build_pcrecpp
        self.build_pcregrep = build_pcregrep
        self.shared = shared
        self.with_bzip2 = with_bzip2
        self.with_zlib = with_zlib


class ConanDependencyManager:
    """manages conan dependdncies"""
    def __init__(self, source_dir):
        self.source_dir = source_dir
        self.build_dir = self.source_dir / "build"
        self.bdwgc = ConanBDWGC()
        self.pcre = ConanPCRE()

    def generate_conanfile(self):
        """generate conanfile.txt"""
        bdwgc = self.bdwgc
        pcre = self.pcre
        content = textwrap.dedent(
            f"""
        [requires]
        {bdwgc}
        {pcre}

        [generators]
        cmake_find_package
        cmake_paths

        [options]
        bdwgc:cplusplus={bdwgc.cplusplus}
        bdwgc:cord={bdwgc.cord}
        bdwgc:gcj_support={bdwgc.gcj_support}
        bdwgc:java_finalization={bdwgc.java_finalization}
        bdwgc:shared={bdwgc.shared}
        pcre:build_pcrecpp={pcre.build_pcrecpp}
        pcre:build_pcregrep={pcre.build_pcregrep}
        pcre:shared={pcre.shared}
        pcre:with_bzip2={pcre.with_bzip2}
        pcre:with_zlib={pcre.with_zlib}
        """
        )
        conanfile = self.source_dir / "conanfile.txt"
        conanfile.write_text(content)

    def install(self):
        """install conan dependncies"""
        os.system(f"cd {self.build_dir} && conan install .. --build=missing")


def shellcmd(cmd, *args, **kwds):
    """generic shellcmd"""
    print("-" * 80)
    print(f"{WHITE}cmd{RESET}: {CYAN}{cmd}{RESET}")
    os.system(cmd.format(*args, **kwds))


def git_clone(repo, to_dir):
    """git clone in a function"""
    shellcmd(f"git clone --depth=1 {repo} {to_dir}")


def cmake_generate(src_dir, build_dir, prefix, **options):
    """generate cmake build system"""
    opts = " ".join(f"-D{k}={v}" for k, v in options.items())
    shellcmd(f"cmake -S {src_dir} -B {build_dir} --install-prefix {prefix} {opts}")


def cmake_build(build_dir):
    """start cmake build"""
    shellcmd(f"cmake --build {build_dir}")


def cmake_install(build_dir):
    """activate cmake install"""
    shellcmd(f"cmake --install {build_dir}")


def wget(url, output_dir):
    """retrieve file or package using wget"""
    shellcmd(f"wget -P {output_dir} {url}")


def tar(archive, output_dir):
    """untar archive"""
    shellcmd(f"tar -xvf {archive} -C {output_dir}")


class ShedskinDependencyManager:
    """shedskin local dependency manager (SPM) class"""

    def __init__(self, source_dir, reset_on_run=False):
        self.reset_on_run = reset_on_run
        self.source_dir = source_dir
        self.build_dir = self.source_dir / "build"
        self.deps_dir = self.build_dir / "deps"
        self.include_dir = self.deps_dir / "include"
        self.lib_dir = self.deps_dir / "lib"
        self.downloads_dir = self.deps_dir / "downloads"
        self.src_dir = self.deps_dir / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.lib_suffix = ".lib" if sys.platform == "win32" else ".a"

        if self.reset_on_run:
            shutil.rmtree(self.deps_dir)

    def targets_exist(self) -> bool:
        """assert that all targets exist"""
        libgc = self.lib_dir / f"libgc{self.lib_suffix}"
        libgccpp = self.lib_dir / f"libgccpp{self.lib_suffix}"
        libpcre = self.lib_dir / f"libgccpp{self.lib_suffix}"
        gc_h = self.include_dir / "gc.h"
        pcre_h = self.include_dir / "pcre.h"

        targets = [libgc, libgccpp, libpcre, gc_h, pcre_h]
        return all(t.exists() for t in targets)

    def install_all(self):
        """install all dependencies"""
        if not self.targets_exist():
            self.install_bdwgc()
            self.install_pcre()
        else:
            print(f"{WHITE}SPM:{RESET} targets exist, no need to run.")

    def install_bdwgc(self):
        """download / build / install bdwgc"""
        bdwgc_repo = "https://github.com/ivmai/bdwgc"
        bdwgc_src = self.src_dir / "bdwgc"
        bdwgc_build = bdwgc_src / "build"

        print("download / build / install bdwgc")
        git_clone(bdwgc_repo, bdwgc_src)
        bdwgc_build.mkdir(exist_ok=True)
        cmake_generate(
            bdwgc_src,
            bdwgc_build,
            prefix=self.deps_dir,
            BUILD_SHARED_LIBS=False,
            enable_cplusplus=True,
            build_cord=False,
            enable_docs=False,
            enable_gcj_support=False,
            enable_java_finalization=False,
        )
        cmake_build(bdwgc_build)
        cmake_install(bdwgc_build)

    def install_pcre(self):
        """download / build / install pcre"""
        pcre_url = (
            "https://sourceforge.net/projects/pcre/files/pcre/8.45/pcre-8.45.tar.gz"
        )
        pcre_archive = self.downloads_dir / "pcre-8.45.tar.gz"
        pcre_src = self.src_dir / "pcre-8.45"
        pcre_build = pcre_src / "build"

        print("download / build / install pcre")
        wget(pcre_url, self.downloads_dir)
        tar(pcre_archive, self.src_dir)
        # pcre_archive.unlink()
        pcre_build.mkdir(parents=True, exist_ok=True)
        cmake_generate(
            pcre_src,
            pcre_build,
            prefix=self.deps_dir,
            BUILD_SHARED_LIBS=False,
            PCRE_BUILD_PCREGREP=False,
            PCRE_BUILD_PCRECPP=True,
            PCRE_SUPPORT_LIBREADLINE=False,
            PCRE_SUPPORT_LIBEDIT=False,
            PCRE_SUPPORT_LIBZ=False,
            PCRE_SUPPORT_LIBBZ2=False,
            PCRE_BUILD_TESTS=False,
            PCRE_SHOW_REPORT=False,
        )
        cmake_build(pcre_build)
        cmake_install(pcre_build)


class CmakeOptions:
    """class to capture cmake options"""
    def __init__(self):
        self.options = {}

    def enable(self, key):
        """enable options"""
        self.options[key] = True

    def disable(self, key):
        """disable option"""
        self.options[key] = False

    def __str__(self):
        return " ".join(f"-D{key}={self.options[key]}" for key in self.options)


class CMakeBuilder:
    """shedskin cmake builder"""

    def __init__(self, options):
        self.options = options
        self.source_dir = pathlib.Path.cwd().parent
        self.build_dir = self.source_dir / "build"

    def check(self, path):
        """check file for syntax errors"""
        with open(path, encoding='utf8') as fopen:
            src = fopen.read()
        compile(src, path, "exec")

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
        print(cfg_cmd)
        os.system(cfg_cmd)

    def cmake_build(self, options):
        """activte cmake build"""
        options = " ".join(options)
        os.system(f"cmake {options} --build {self.build_dir}")

    def build(self):
        """build shedskin program"""
        start_time = time.time()

        cfg_options = []
        bld_options = []

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

        self.cmake_config(cfg_options)

        self.cmake_build(bld_options)

        end_time = time.time()
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))
        print(f"Total time: {YELLOW}{elapsed_time}{RESET}\n")
