#!/usr/bin/env python3

"""shedskin example runner

There are currently two ways to run tests:

(1) the builtin way and
(2) the cmake way.

## Builtin Method

To build and run a single example in cpp-executable mode:

    ./run -r <name>.py

To build and run a single example in python-extension mode:

    ./run -er <name>.py

To build and run all examples in cpp-executable mode:

    ./run.py

To build and run all examples in python-extension mode:

    ./run.py -e

To build and run the most recently modified example (useful during example dev):

    ./run.py -m

    or

    ./run.py -me


## CMake Method

To build and run all examples as executables using cmake:

    ./run.py -c

If the above command is run for the first time, it will run the equivalent of the following:

    mkdir build && cd build && cmake .. && cmake --build .

If it is run subsequently, it will run the equivalent of the following:

    cd build && cmake .. && cmake --build .

This is useful during example development and has the benefit of only picking up
changes to modified examples and will not re-translate or re-compile unchanged examples.

To reset or remove the cmake `build` directory and run cmake:

    ./run.py --reset -c

To build and run all cmake examples as executables **and** python extensions using cmake:

    ./run.py -ce

This will build/run an executable and python extension example for each example in the directory,
basically the equivalent of the following (if it is run the first time):

    mkdir build && cd build && cmake .. -DTEST_EXT=ON && cmake --build .

If it is run subsequently, it will run the equivalent of the following:

    cd build && cmake .. && cmake --build .
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


class ExampleRunner:
    """shedskin example runner"""

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



    def run_step(self, cmd, cwd='.', nosplit=False, run=False):
        """run command step in specified directory"""
        if run:
            try:
                subprocess.run(cmd.split(), cwd=cwd)
            except subprocess.CalledProcessError as e:
                print(f"\n{RED}ERROR{RESET}: '{cmd}' returns {e.returncode}")
                print(e.output.decode('utf8'))
                raise
        else:
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

    def run_example(self, path):
        """run example in path"""
        path = Path(path)
        name = path.stem

        if path.is_dir():
            file_path = path / f'{name}.py'
            self.run_example(file_path)

        else:
            is_nested = bool(path.parent.stem)

            print(f'building {name:30s}', end='')

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
                    print(f'{GREEN}OK{RESET}')
                    if self.options.extension:
                        self.run_step(f'python {name}_main.py', cwd=path.parent, run=True)
                    else:
                        self.run_step(f'./{name}', cwd=path.parent, run=True)
                else:
                    self.run_step(translation_step)
                    self.run_step('make')
                    print(f'{GREEN}OK{RESET}')
                    if self.options.extension:
                        self.run_step(f'python {name}_main.py', run=True)
                    else:
                        self.run_step(f'./{name}', run=True)
            except:
                print(f"{RED}ERROR{RESET}: '{path}' terminated early")
                return

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

    def run_examples(self):
        """build and run all examples"""
        st = time.time()

        if self.options.cmake:
            if self.options.extension:
                cmake_cmd = "cmake .. -DAS_EXT=ON"
            else:
                cmake_cmd = "cmake .."
            actions = [
                "cd build",
                cmake_cmd,
                "cmake --build .",
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
                max_mtime = 0
                most_recent_test = None
                for test in self.tests:
                    mtime = os.stat(os.path.abspath(test)).st_mtime
                    if mtime > max_mtime:
                        max_mtime = mtime
                        most_recent_test = test
                self.run_example(most_recent_test)
            else:
                for test in self.tests:
                    self.run_example(test)
        et = time.time()
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(et - st))
        print(f'Total time: {YELLOW}{elapsed_time}{RESET}\n')

    @classmethod
    def commandline(cls):
        """command line interace to test runner"""
        parser = argparse.ArgumentParser(
            prog = 'run',
            description = 'runs shedskin examples')
        arg = opt = parser.add_argument
        opt('-c', '--cmake',     help='run examples using cmake', action='store_true')
        opt('-e', '--extension', help='include python extensions', action='store_true')
        opt('-k', '--check',     help='check file.py syntax before running', action='store_true')
        opt('-m', '--modified',  help='run only recently modified example', action='store_true')
        opt('-n', '--nocleanup', help='do not cleanup built example', action='store_true')
        opt('-r', '--run',       help='run single example', metavar="EXAMPLE")
        opt('-s', '--reset',     help='reset cmake build', action='store_true')

        args = parser.parse_args()
        runner = cls(args)
        if args.run:
            runner.run_example(args.run)
        else:
            runner.run_examples()

if __name__ == '__main__':
    ExampleRunner.commandline()
