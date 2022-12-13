#!/usr/bin/env python3

import argparse
import glob
import os
import subprocess
import time
import shutil
from pathlib import Path


white = "\x1b[97;20m"
GREY = "\x1b[38;20m"
GREEN = "\x1b[32;20m"
CYAN = "\x1b[36;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
RED_BOLD = "\x1b[31;1m"
RESET = "\x1b[0m"

class TestRunner:

    def __init__(self, options):
        self.options = options
        self.tests = sorted(glob.glob("test_*.py"))

    def check_output(self, args):
        return subprocess.check_output(args.split(), 
            stderr=subprocess.STDOUT
        )

    def run_step(self, cmd):
        try:
            self.check_output(cmd)
        except subprocess.CalledProcessError as e:
            print(f"\n{RED}ERROR{RESET}: '{cmd}' returns {e.returncode}")
            print(e.output.decode('utf8'))
            raise

    def validate(self, path):
        with open(path) as f:
            src = f.read()
        compile(src, path, 'exec')

    def run_test(self, path):
        print(f'testing {path:30s}', end='')
        path = Path(path)
        name = path.stem

        if self.options.validate:
            self.validate(path) # check python syntax

        try:
            self.run_step(f'shedskin {path}')
            self.run_step('make')
            self.run_step(f'./{name}')
        except:
            print(f"test: '{path}' terminated early")
            return

        print(f'{GREEN}OK{RESET}')

        files_to_clean = [f'{name}.cpp', f'{name}.hpp', f'{name}', 'Makefile']
        if self.options.exec:
            files_to_clean.remove(f'{name}')
        for f in files_to_clean:
            os.remove(f)

    def sequence(self, *cmds):
        cmd = " && ".join(cmds)
        os.system(cmd)

    def run_tests(self):
        st = time.time()

        if self.options.pytest:
            try:
                import pytest
                os.system('pytest')
            except ImportError:
                print('pytest not found')
                pass            
            print()

        if self.options.cmake:
            self.sequence(
                "rm -rf ./build",
                "mkdir -p build",
                "cd build",
                "cmake ..",
                "make",
                "make test"
            )
            os.system('rm -f Makefile')
        else:
            print(f'Running {CYAN}shedskin{RESET} tests:')
            if self.options.recent: # run only most recently modified test
                max_mtime = 0
                most_recent_test = None
                for test in self.tests:
                    mtime = os.stat(os.path.abspath(test)).st_mtime
                    if mtime > max_mtime:
                        max_mtime = mtime
                        most_recent_test = test
                self.run_test(most_recent_test)
            else:
                for test in self.tests:
                    self.run_test(test)
        et = time.time()
        elapsed_time = round(et - st, 1)
        print(f'Total time: {YELLOW}{elapsed_time}{RESET} seconds\n')

    @classmethod
    def commandline(cls):
        parser = argparse.ArgumentParser(
            prog = 'runtests',
            description = 'runs shedskin tests')
        arg = opt = parser.add_argument
        opt('-r', '--recent', help='run only most recently modified test', action='store_true')
        opt('-v', '--validate', help='validate each testfile before running', action='store_true')
        opt('-p', '--pytest', help='run pytest before each test run',  action='store_true')
        opt('-e', '--exec', help='retain test executable',  action='store_true')
        opt('-c', '--cmake', help='run tests using cmake',  action='store_true')

        args = parser.parse_args()
        runner = cls(args)
        runner.run_tests()

if __name__ == '__main__': TestRunner.commandline()

