'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

'''
import sys

import infer


ERRORS = set()


def error(msg, gx, node=None, warning=False, mv=None):
    if warning:
        kind = '*WARNING*'
    else:
        kind = '*ERROR*'
    if not mv and node and (node, 0, 0) in gx.cnode:
        mv = infer.inode(gx, node).mv
    filename = lineno = None
    if mv:
        filename = mv.module.relative_filename
        if node and hasattr(node, 'lineno'):
            lineno = node.lineno
    result = (kind, filename, lineno, msg)
    if result not in ERRORS:
        ERRORS.add(result)
    if not warning:
        print format_error(result)
        sys.exit(1)


def format_error(error):
    (kind, filename, lineno, msg) = error
    result = kind
    if filename:
        result += ' %s:' % filename
        if lineno is not None:
            result += '%d:' % lineno
    return result + ' ' + msg


def print_errors():
    for error in sorted(ERRORS):
        print format_error(error)
