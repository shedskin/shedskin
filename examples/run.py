#!/usr/bin/env python3
"""shedskin example runner
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


skiplist = [
    'c64',
    'gs',
    'mastermind',
    'minilight',
    'msp_ss',
    'pylot',
    'rsync',
    'sha',
    'tarsalzp',
    'tonyjpegdecoder',
    'webserver',

    'testdata',
]



class ExampleRunner:
    """shedskin example runner"""

    def __init__(self, options=None):
        self.options = options
        self.build_dir = Path('build')
        self.examples = self.get_examples()

    def get_examples(self):
        return [d for d in Path.cwd().iterdir() if all([
            d.is_dir(), 
            d.stem not in skiplist, 
            not d.stem.startswith('_')
        ])]

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
            cmake_config = "cmake .."
            cmake_build  = "cmake --build ."

            if self.options.extension:
                cmake_config += " -DAS_EXT=ON"

            if self.options.ccache:
                if shutil.which('ccache'):
                    cmake_config += " -DCMAKE_CXX_COMPILER_LAUNCHER=ccache"
                else:
                    print(f"\n{YELLOW}WARNING{RESET}: 'ccache' not found")

            if self.options.generator:
                cmake_config += f" -G{self.options.generator}"

            if self.options.parallel:
                cmake_build += f" --parallel {self.options.parallel}"

            if self.options.run:
                cmake_build += f" --target {self.options.run}-exe"
                # os.system(f'./build/{self.options.run}/{self.options.run}')

            if self.options.target:
                for target in self.options.target:
                    cmake_build += f" --target {target}-exe"

            actions = [
                "cd build",
                cmake_config,
                cmake_build,
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
            print(f'Running {CYAN}shedskin{RESET} examples:')
            for example in self.examples:
                self.run_example(example)
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
        opt('-g', '--generator', help='specify a cmake build system generator')
        opt('-j', '--parallel',  help='build and run examples in parallel using N jobs', metavar="N", type=int)
        opt('-k', '--check',     help='check file.py syntax before running', action='store_true')
        opt('-n', '--nocleanup', help='do not cleanup built example', action='store_true')
        opt('-r', '--run',       help='run single example', metavar="EXAMPLE")
        opt('-s', '--reset',     help='reset cmake build', action='store_true')
        opt('-t', '--target',    help='build only specified targets', nargs="+")
        opt('--ccache',          help='enable ccache with cmake', action='store_true')

        args = parser.parse_args()
        runner = cls(args)
        if args.cmake:
            runner.run_examples()
        else:
            if args.run:
                runner.run_example(args.run)
            else:
                runner.run_examples()

if __name__ == '__main__':
    ExampleRunner.commandline()
