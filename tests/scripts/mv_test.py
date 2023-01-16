#!/usr/bin/env python3

import ast
import argparse
import os
from pathlib import Path

SHEDSKIN_MODULES = [
    'array',
    'binascii',
    'bisect',
    'collections',
    'colorsys',
    'configparser',
    'copy',
    'csv',
    'datetime',
    'fnmatch',
    'functools',
    'gc',
    'getopt',
    'glob',
    'heapq',
    'io',
    'itertools',
    'math',
    'mmap',
    'os',
    'os.path',
    # 'pickle',
    'random',
    're',
    'select',
    'socket',
    'string',
    'struct',
    'sys',
    'time',
]

def get_imports(path):
    modules = set()
    with open(path) as fh:        
        root = ast.parse(fh.read(), path)
        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.Import):
                mods = []
            elif isinstance(node, ast.ImportFrom):  
                mods = node.module.split('.')
            else:
                continue
            for n in node.names:
                names = n.name.split('.')
                if not mods:
                    modules.add(names[0])
                else:
                    modules.add(mods[0])
    return sorted(list(modules))

def move_to_dir(testfile):
    modules = get_imports(testfile)
    path = Path(testfile)
    if path.exists() and path.is_file():
        os.makedirs(path.stem, exist_ok=True)
        testdir = Path(path.stem)
        with open(testdir / 'CMakeLists.txt', 'w') as f:
            f.write('set(sys_modules\n')
            for module in modules:
                if module in SHEDSKIN_MODULES:
                    f.write(f'    {module}\n')
            f.write(')\n')
            f.write('set(app_modules\n')
            for module in modules:
                if module not in SHEDSKIN_MODULES:
                    f.write(f'    {module}\n')
            f.write(')\n')
            if path.stem.startswith('test_ext'):
                f.write('add_shedskin_ext_test("${sys_modules}" "${app_modules}")\n')
            else:
                f.write('add_shedskin_test("${sys_modules}" "${app_modules}")\n')
        path.rename(testdir / path.name)

def commandline():
    parser = argparse.ArgumentParser(
        prog = 'mv_test',
        description = 'move test file to its own cmake subdirectory')
    arg = opt = parser.add_argument
    opt('-t', '--testfile', help='move single test to its own directory')
    opt('-a', '--all', help='move all tests to their own directory', action='store_true')
    opt('-d', '--dryrun', help='dryrun for `mv_test --all` option', action='store_true')

    options = parser.parse_args()
    if options.testfile:
        move_to_dir(options.testfile)
    elif options.all:
        for p in Path.cwd().iterdir():
            if p.is_file() and p.name.startswith('test_'):
                if options.dryrun:
                    print(p)
                else:
                    move_to_dir(p)
    else:
        parser.print_help()

if __name__ == '__main__': 
    commandline()
