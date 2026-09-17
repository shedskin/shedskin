# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

import os, os.path, fnmatch, re

def iglob(pathname, recursive=False, include_hidden=False, root_dir=None, dir_fd=-1):
    return __iter('')

def glob(pathname, recursive=False, include_hidden=False, root_dir=None, dir_fd=-1):
    return ['']

def has_magic(s):
    return True

def escape(pathname):
    return pathname

def translate(pat, recursive=False, include_hidden=False, seps=None):
    return ''
