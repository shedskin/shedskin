#!/usr/bin/env python3

import ast
import argparse
import os
from pathlib import Path


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
            f.write('set(modules\n')
            for module in modules:
                f.write(f'    {module}\n')
            f.write(')\n')
            if path.stem.startswith('test_ext'):
                f.write('add_shedskin_ext_test("${modules}")\n')
            else:
                f.write('add_shedskin_test("${modules}")\n')
        path.rename(testdir / path.name)

def commandline():
    parser = argparse.ArgumentParser(
        prog = 'mv_test',
        description = 'move test file to its own cmake subdirectory')
    arg = opt = parser.add_argument
    arg('testfile', help='move test to its own directory')

    args = parser.parse_args()
    move_to_dir(args.testfile)

if __name__ == '__main__': 
    commandline()
