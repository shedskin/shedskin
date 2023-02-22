#!/usr/bin/env python3
"""shedskin testrunner
"""
import argparse
import glob
import os
import subprocess
import time
import shutil
import sys
import textwrap
import pathlib


WHITE = "\x1b[97;20m"
GREY = "\x1b[38;20m"
GREEN = "\x1b[32;20m"
CYAN = "\x1b[36;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
RED_BOLD = "\x1b[31;1m"
RESET = "\x1b[0m"


class ConanDependency:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def __str__(self):
        return f"{self.name}/{self.version}"


class ConanBDWGC(ConanDependency):
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
    def __init__(self, source_dir):
        self.source_dir = source_dir
        self.build_dir = self.source_dir / "build"
        self.bdwgc = ConanBDWGC()
        self.pcre = ConanPCRE()

    def generate_conanfile(self):
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
        # with open("conanfile.txt", "w") as cfile:
        #     cfile.write(content)

    def install(self):
        # os.system("cd build && conan install .. --build=missing")
        os.system(f"cd {self.build_dir} && conan install .. --build=missing")


def shellcmd(cmd, *args, **kwds):
    print("-" * 80)
    print(f"{WHITE}cmd{RESET}: {CYAN}{cmd}{RESET}")
    os.system(cmd.format(*args, **kwds))


def git_clone(repo, to_dir):
    shellcmd(f"git clone --depth=1 {repo} {to_dir}")


def cmake_generate(src_dir, build_dir, prefix, **options):
    opts = " ".join(f"-D{k}={v}" for k, v in options.items())
    shellcmd(f"cmake -S {src_dir} -B {build_dir} --install-prefix {prefix} {opts}")


def cmake_build(build_dir):
    shellcmd(f"cmake --build {build_dir}")


def cmake_install(build_dir):
    shellcmd(f"cmake --install {build_dir}")


def wget(url, output_dir):
    shellcmd(f"wget -P {output_dir} {url}")


def tar(archive, output_dir):
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

    def targets_exist(self):
        libgc = self.lib_dir / f"libgc{self.lib_suffix}"
        libgccpp = self.lib_dir / f"libgccpp{self.lib_suffix}"
        libpcre = self.lib_dir / f"libgccpp{self.lib_suffix}"
        gc_h = self.include_dir / "gc.h"
        pcre_h = self.include_dir / "pcre.h"

        targets = [libgc, libgccpp, libpcre, gc_h, pcre_h]
        return all(t.exists() for t in targets)

    def install_all(self):
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


class TestRunner:
    """shedskin test builder / runner"""

    def __init__(self, options):
        self.options = options
        self.build_dir = pathlib.Path("build")
        self.source_dir = pathlib.Path.cwd()
        self.tests = sorted(glob.glob("./test_*/test_*.py", recursive=True))

    def check(self, path):
        """check file for syntax errors"""
        with open(path) as f:
            src = f.read()
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

    def sequence(self, *cmds):
        """run build steps in sequence"""
        cmd = " && ".join(cmds)
        print(f"{CYAN}cmd{RESET}: {cmd}")
        os.system(cmd)

    def rm_build(self):
        shutil.rmtree(self.build_dir)

    def mkdir_build(self):
        os.makedirs(self.build_dir, exist_ok=True)

    def cmake_config(self, options):
        options = " ".join(options)
        cfg_cmd = f"cmake {options} -S {self.source_dir} -B {self.build_dir}"
        print('cfg_cmd:', cfg_cmd)
        os.system(cfg_cmd)

    def cmake_build(self, options):
        options = " ".join(options)
        bld_cmd = f"cmake {options} --build {self.build_dir}"
        print('bld_cmd:', bld_cmd)
        os.system(bld_cmd)

    def cmake_test(self, options):
        options = " ".join(options)
        tst_cmd = f"ctest --output-on-failure {options} --test-dir {self.build_dir}"
        print('tst_cmd:', tst_cmd)
        os.system(tst_cmd)

    def run_tests(self):
        """tests shedskin program"""
        st = time.time()

        cfg_options = []
        bld_options = []
        tst_options = []

        # if self.options.executable:
        #     cfg_options.append("-DBUILD_EXECUTABLE=ON")
        # if self.options.pyextension:
        #     cfg_options.append("-DBUILD_EXTENSION=ON")

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

        self.cmake_test(tst_options)

        et = time.time()
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(et - st))
        print(f"Total time: {YELLOW}{elapsed_time}{RESET}\n")

        if self.options.run_errs:
            failures = self.error_tests()
            if not failures:
                print(f'==> {GREEN}NO FAILURES, yay!{RESET}')
            else:
                print(f'==> {RED}TESTS FAILED:{RESET}', len(failures))
                print(failures)
                sys.exit()
