#!/usr/bin/env python3

import argparse
import ast
import os
import sys
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

def add_deps(imported_modules, module, *dependent_modules):
    for dep in dependent_modules:
        if module in imported_modules and dep not in imported_modules:
            imported_modules.append(dep)
    return imported_modules

def move_to_dir(egfile):
    modules = get_imports(egfile)
    modules = add_deps(modules, 'getopt', 'os') # order is important
    modules = add_deps(modules, 'os', 'os.path', 'stat')
    modules = add_deps(modules, 'random', 'math', 'time')
    modules = add_deps(modules, 'fnmatch', 're')
    path = Path(egfile)
    if path.exists() and path.is_file():
        os.makedirs(path.stem, exist_ok=True)
        egdir = Path(path.stem)
        with open(egdir / 'CMakeLists.txt', 'w') as f:
            f.write('set(modules\n')
            for module in modules:
                f.write(f'    {module}\n')
            f.write(')\n')
            f.write('add_shedskin_example("${modules}")\n')
        path.rename(egdir / path.name)

def move_all_from_dir(path):
    path = Path(path)

    with open('cmake/subdirs.cmake', 'a') as cmake_script:
        for f in sorted(path.iterdir()):
            if f.is_file() and f.suffix == '.py':
                try:
                    move_to_dir(f)
                    cmake_script.write(f'add_subdirectory({f.stem})\n')
                except:
                    print(f'skipped: {f}')

def commandline():
    parser = argparse.ArgumentParser(
        prog = 'mv_eg',
        description = 'move example file to its own cmake subdirectory')
    arg = opt = parser.add_argument
    opt('-e', '--example',  help='move example to its own directory')
    opt('-a', '--all-from-dir', help='move all examples from a directory to its own directory')


    args = parser.parse_args()
    if args.example:
        move_to_dir(args.example)
    elif args.all_from_dir:
        move_all_from_dir(args.all_from_dir)
    else:
        parser.print_help(sys.stderr)
        sys.exit()


if __name__ == '__main__': 
    commandline()
