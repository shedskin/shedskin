#!/usr/bin/env python3

import argparse
import os

def get_tree(path, options=None):
    parentdir = os.path.dirname(__file__)
    results = []
    # endings = ['.cpp', '.hpp']
    endings = ['.py']
    for root, dirs, files in os.walk(path):
        for f in files:
            if any(f.endswith(e) for e in endings):
                name = os.path.splitext(f)[0]
                results.append(os.path.join(root, name))
    return sorted(results)



def commandline():
    parser = argparse.ArgumentParser(
        prog = 'get_tree',
        description = 'get tree of translated dependencies (.hpp, .cpp)')
    arg = opt = parser.add_argument
    arg('path', help='path to root')

    args = parser.parse_args()
    if args.path:
        tree = get_tree(args.path, args)
        for elem in tree:
            print(elem)

commandline()
