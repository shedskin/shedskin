'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

'''
import logging
import sys


ERRORS = set()


def error(msg, gx, node=None, warning=False, mv=None):
    from . import infer

    if warning:
        kind = logging.WARNING
    else:
        kind = logging.ERROR
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
        print_error(result)
        sys.exit(1)


def print_error(error):
    (kind, filename, lineno, msg) = error
    result = ''
    if filename:
        result += filename + ':'
        if lineno is not None:
            result += str(lineno) + ':'
        result += ' '
    logging.log(kind, result + msg)


def print_errors():
    for error in sorted(ERRORS):
        print_error(error)
