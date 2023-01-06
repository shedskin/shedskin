#!/usr/bin/env python3
"""clean_tests.py

A utility script to recursively remove detritus and residual artifacts 
from the `tests` directory.

Defaults can be configured by populating the following global variables:

SKIP_DIRS       directories to skip
DIR_SKIP_FUNCS  functions which match directories to skip
RM_DIRS         directories to remove
DIR_RM_FUNCS    functions which match directories to remove

SKIP_FILES      files to skip
FILE_SKIP_FUNCS functions which match files to skip
RM_FILES        files to remove
FILE_RM_FUNCS   functions which match files to remove

"""


import argparse
import os
import shutil


# ----------------------------------------------------------------
# colors

WHITE = "\x1b[97;20m"
GREY = "\x1b[38;20m"
GREEN = "\x1b[32;20m"
CYAN = "\x1b[36;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
RED_BOLD = "\x1b[31;1m"
RESET = "\x1b[0m"

# ----------------------------------------------------------------
# boolean functions

def mk_startswith(pattern):
    return lambda x: x.startswith(pattern)


def mk_endswith(pattern):
    return lambda x: x.endswith(pattern)


test_prefix = mk_startswith("test_")
skip_prefix = mk_startswith("skip_")

py_suffix = mk_endswith(".py")
pyc_suffix = mk_endswith(".pyc")
dsym_suffix = mk_endswith(".dSYM")



# ----------------------------------------------------------------
# configure dir functions

SKIP_DIRS = ["build", "scripts", "cmake", "testdata"]

DIR_SKIP_FUNCS = [
    test_prefix,
]

RM_DIRS = ["__pycache__"]

DIR_RM_FUNCS = [
    dsym_suffix,
]

# ----------------------------------------------------------------
# configure file functions

SKIP_FILES = [
    "CMakeLists.txt",
    "README.md",
    ".gitignore",
]

FILE_SKIP_FUNCS = [
    py_suffix,
    pyc_suffix, # skip pyc because __pycache__ are removed
    skip_prefix,
]

RM_FILES = []

FILE_RM_FUNCS = []
# ----------------------------------------------------------------
# cleaner class


class TestCleaner:
    """
    """
    def __init__(
        self,
        path=".",
        skip_dirs=SKIP_DIRS,
        dir_skip_funcs=DIR_SKIP_FUNCS,
        rm_dirs=RM_DIRS,
        dir_rm_funcs=DIR_RM_FUNCS,
        skip_files=SKIP_FILES,
        file_skip_funcs=FILE_SKIP_FUNCS,
        rm_files=RM_FILES,
        file_rm_funcs=FILE_RM_FUNCS,
        options=None,
    ):
        self.path = path

        self.skip_dirs = skip_dirs or []
        self.dir_skip_funcs = dir_skip_funcs or []
        self.rm_dirs = rm_dirs or []
        self.dir_rm_funcs = dir_rm_funcs or []

        self.skip_files = skip_files or []
        self.file_skip_funcs = file_skip_funcs or []
        self.rm_files = rm_files or []
        self.file_rm_funcs = file_rm_funcs or []

        self.options = options

        self.targets = []


    def remove(self, path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    def add_rm_targets(self, root, items, rm_list, rm_funcs):
        for i in items:
            if i in rm_list:
                target = os.path.join(root, i)
                self.targets.append(target)
                # print("added:", target)
                continue

            if any(match(i) for match in rm_funcs):
                target = os.path.join(root, i)
                self.targets.append(target)
                # print("added:", target)

    def process_dirs(self, root, dirs):
        self.add_rm_targets(root, dirs, self.rm_dirs, self.dir_rm_funcs)

        for d in self.skip_dirs:
            if d in dirs:
                dirs.remove(d)

        for d in dirs:
            if any(match(d) for match in self.dir_skip_funcs):
                dirs.remove(d)

    def process_files(self, root, files):
        self.add_rm_targets(root, files, self.rm_files, self.file_rm_funcs)

        for f in files:
            if f in self.skip_files:
                continue
            if any(match(f) for match in self.file_skip_funcs):
                continue
            target = os.path.join(root, f)
            self.targets.append(target)
            # print("added:", target)

    def process(self):
        for root, dirs, files in os.walk(self.path):
            self.process_dirs(root, dirs)
            self.process_files(root, files)

    def dump(self):
        for f in self.targets:
            if os.path.isfile(f):
                print(f"{YELLOW}file:{RESET}", f)
            else:
                print(f" {RED}dir:{RESET}", f)

    def clean(self):
        for f in self.targets:
            self.remove(f)
            print(f"{CYAN}removed:{RESET}", f)


    @classmethod
    def commandline(cls):
        """command line interace to clean_tests"""
        parser = argparse.ArgumentParser(
            prog = 'clean_tests',
            description = 'cleans detritus left over from building and running tests')
        arg = opt = parser.add_argument
        opt('-d', '--dryrun', help='run without removing anything', action='store_true')

        args = parser.parse_args()
        cleaner = cls(options=args)
        cleaner.process()
        if args.dryrun:
            cleaner.dump()
        else:
            cleaner.clean()

if __name__ == '__main__':
    TestCleaner.commandline()
