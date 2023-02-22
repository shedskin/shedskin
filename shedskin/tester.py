"""shedskin testrunner
"""
import glob
import os
import subprocess
import time
import shutil
import sys
import pathlib


from .utils import RED, GREEN, YELLOW, CYAN, RESET
from .depend import ShedskinDependencyManager, ConanDependencyManager


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
