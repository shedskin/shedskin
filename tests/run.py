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
from pathlib import Path


WHITE = "\x1b[97;20m"
GREY = "\x1b[38;20m"
GREEN = "\x1b[32;20m"
CYAN = "\x1b[36;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
RED_BOLD = "\x1b[31;1m"
RESET = "\x1b[0m"


class TestRunner:
    """shedskin test runner"""

    def __init__(self, options=None):
        self.options = options
        self.build_dir = Path('build')
        self.tests = sorted(glob.glob("./test_*/test_*.py", recursive=True))

    def check_output(self, args, cwd='.', nosplit=False):
        """run command and return output"""
        if not nosplit:
            args = args.split()
        return subprocess.check_output(args,
            stderr=subprocess.STDOUT,
            cwd=cwd,
        )

    def run_step(self, cmd, cwd='.', nosplit=False):
        """run command step in specified directory"""
        try:
            self.check_output(cmd, cwd, nosplit)
        except subprocess.CalledProcessError as e:
            print(f"\n{RED}ERROR{RESET}: '{cmd}' returns {e.returncode}")
            print(e.output.decode('utf8'))
            raise

    def check(self, path):
        """check file for syntax errors"""
        with open(path) as f:
            src = f.read()
        compile(src, path, 'exec')

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

    def run_test(self, path):
        """run test in path"""
        path = Path(path)
        name = path.stem

        if path.is_dir():
            file_path = path / f'{name}.py'
            self.run_test(file_path)

        else:
            is_nested = bool(path.parent.stem)

            print(f'testing {name:30s}', end='')

            if self.options.check:
                self.check(path) # check python syntax

            if self.options.extension:
                translation_step = f'shedskin -e {path.name}'
                compiled_product = f'{name}.so'
            else:
                translation_step = f'shedskin {path.name}'
                compiled_product = name

            try:
                if is_nested:
                    self.run_step(translation_step, cwd=path.parent)
                    self.run_step('make', cwd=path.parent)
                    if self.options.extension:
                        self.run_step(["python3", "-c",
                            repr(f'from {name} import test_all; test_all()')],
                            cwd=path.parent, nosplit=True)
                    else:
                        self.run_step(f'./{name}', cwd=path.parent)
                else:
                    self.run_step(translation_step)
                    self.run_step('make')
                    if self.options.extension:
                        self.run_step(["python3", "-c",
                            repr(f'from {name} import test_all; test_all()')],
                            nosplit=True)
                    else:
                        self.run_step(f'./{name}')
            except:
                print(f"{RED}ERROR{RESET}: '{path}' terminated early")
                return

            print(f'{GREEN}OK{RESET}')

            files_to_clean = [f'{name}.cpp', f'{name}.hpp', compiled_product, 'Makefile']
            folders_to_clean = [f'{name}.so.dSYM']

            if self.options.nocleanup:
                files_to_clean.remove(compiled_product)
            for f in files_to_clean:
                if not is_nested:
                    os.remove(f)
                else:
                    os.remove(path.parent / f)

            for f in folders_to_clean:
                if not is_nested:
                    if os.path.exists(f):
                        shutil.rmtree(f)
                else:
                    if os.path.exists(path.parent / f):
                        shutil.rmtree(path.parent / f)

    def sequence(self, *cmds):
        """run test steps in sequence"""
        cmd = " && ".join(cmds)
        print(f'{CYAN}cmd{RESET}: {cmd}')
        os.system(cmd)

    def run_tests(self):
        """build and run all tests"""
        st = time.time()

        if self.options.pytest:
            try:
                import pytest
                os.system('pytest')
            except ImportError:
                print('pytest not found')
            print()

        if self.options.cmake:
            cmake_config = "cmake .."
            cmake_build = "cmake --build ."
            cmake_test = "ctest --output-on-failure"

            if self.options.ccache:
                if shutil.which('ccache'):
                    cmake_config += " -DCMAKE_CXX_COMPILER_LAUNCHER=ccache"
                else:
                    print(f"\n{YELLOW}WARNING{RESET}: 'ccache' not found")

            if self.options.extension:
                cmake_config += " -DTEST_EXT=ON"

            if self.options.generator:
                cmake_config += f" -G{self.options.generator}"

            if self.options.include:
                cmake_test += f" --tests-regex {self.options.include}"

            if self.options.modified:
                most_recent_test = Path(self.get_most_recent_test()).stem
                cmake_build += f" --target {most_recent_test}"
                cmake_test += f" --tests-regex {most_recent_test}"                

            if self.options.parallel:
                cmake_build += f" --parallel {self.options.parallel}"
                cmake_test  += f" --parallel {self.options.parallel}"

            if self.options.progress:
                cmake_test += " --progress"

            if self.options.run:
                target_suffix = '-exe'
                if self.options.extension:
                    target_suffix = '-ext'
                cmake_build += f" --target {self.options.run}{target_suffix}"
                cmake_test += f" --tests-regex {self.options.run}"

            if self.options.stoponfail:
                cmake_test += " --stop-on-failure"

            if self.options.target:
                for target in self.options.target:
                    cmake_build += f" --target {target}"

            actions = [
                "cd build",
                cmake_config,
                cmake_build,
                cmake_test,
            ]
            if self.build_dir.exists() and self.options.reset:
                actions = ["rm -rf ./build", "mkdir -p build"] + actions

            else:
                if not self.build_dir.exists():
                    actions.insert(0, "mkdir -p build")

            self.sequence(*actions)
            if os.path.exists('Makefile'):
                os.remove('Makefile')
        else:
            print(f'Running {CYAN}shedskin{RESET} tests:')
            if self.options.modified: # run only most recently modified test
                most_recent_test = self.get_most_recent_test()
                self.run_test(most_recent_test)
            else:
                for test in self.tests:
                    self.run_test(test)
        et = time.time()
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(et - st))
        print(f'Total time: {YELLOW}{elapsed_time}{RESET}\n')

    def error_tests(self):
        """test error messages from tests in errs directory""" 
        failures = []
        os.chdir('errs')
        tests = sorted(os.path.basename(t) for t in glob.glob('[0-9][0-9].py'))
        for test in tests:
            print('*** test:', test)
            try:
                checks = []
                for line in open(test):                  
                    if line.startswith('#*'):
                        checks.append(line[1:].strip())
                cmd=f'{sys.executable} -m shedskin {test}'.split()
                output = subprocess.run(cmd, encoding='utf-8', 
                    capture_output=True, text=True).stdout
                assert not [l for l in output if 'Traceback' in l]
                for check in checks:
                    print(check)
                    assert [l for l in output.splitlines() if l.startswith(check)]
                print(f'*** {GREEN}SUCCESS{RESET}:', test)
            except AssertionError:
                print(f'*** {RED}FAILURE{RESET}:', test)
                failures.append(test)
        os.chdir('..')
        return failures

    @classmethod
    def commandline(cls):
        """command line interace to test runner"""
        parser = argparse.ArgumentParser(
            prog = 'runtests',
            description = 'runs shedskin tests')
        arg = opt = parser.add_argument
        opt('-c', '--cmake',      help='run tests using cmake', action='store_true')
        opt('-e', '--extension',  help='include python extension tests', action='store_true')
        opt('-g', '--generator',  help='specify a cmake build system generator')
        opt('-i', '--include',    help='provide regex of tests to include with cmake', metavar="PATTERN")        
        opt('-j', '--parallel',   help='build and run tests in parallel using N jobs', metavar="N", type=int)
        opt('-k', '--check',      help='check testfile py syntax before running', action='store_true')
        opt('-m', '--modified',   help='run only recently modified test', action='store_true')
        opt('-n', '--nocleanup',  help='do not cleanup built test', action='store_true')
        opt('-p', '--pytest',     help='run pytest before each test run', action='store_true')
        opt('-r', '--run',        help='run single test', metavar="TEST")
        opt('-s', '--stoponfail', help='stop when first failure happens in ctest', action='store_true')
        opt('-t', '--target',     help='build only specified targets', nargs="+")
        opt('-x', '--run-errs',   help='run error/warning message tests', action='store_true')
        opt('--ccache',           help='enable ccache with cmake', action='store_true')
        opt('--progress',         help='enable short progress output from ctest', action='store_true')
        opt('--reset',            help='reset cmake build', action='store_true')

        args = parser.parse_args()
        runner = cls(args)
        if args.cmake:
            runner.run_tests()
        else:
            if args.run:
                runner.run_test(args.run)
            elif args.run_errs:
                failures = runner.error_tests()
                if not failures:
                    print(f'==> {GREEN}NO FAILURES, yay!{RESET}')
                else:
                    print(f'==> {RED}TESTS FAILED:{RESET}', len(failures))
                    print(failures)
                    sys.exit()

if __name__ == '__main__':
    TestRunner.commandline()
