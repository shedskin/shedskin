'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2011 Mark Dufour; License GNU GPL version 3 (See LICENSE)

annotate.py: annotate source code with inferred types, as *.ss.py (shedskin -a)

'''
import re
from compiler.ast import Const, AssTuple, AssList, Assign, AugAssign, \
    Getattr, Dict, Print, Return, Printnl, Name, List, Tuple, ListComp

from graph import setmv
from config import getgx
from infer import inode
from python import assign_rec
from typestr import nodetypestr

RE_COMMENT = re.compile(r'#[^\"\']*$')

def paste(source, expr, text, mv):
    if not expr.lineno:
        return
    if (expr, 0, 0) not in getgx().cnode or inode(expr).mv != mv:
        return  # XXX
    line = source[expr.lineno - 1]
    match = RE_COMMENT.search(line)
    if match:
        line = line[:match.start()]
    if text:
        text = '# ' + text
    line = line.rstrip()
    if text and len(line) < 40:
        line += (40 - len(line)) * ' '
    source[expr.lineno - 1] = line
    if text:
        source[expr.lineno - 1] += ' ' + text
    source[expr.lineno - 1] += '\n'

def annotate():
    if not getgx().annotation:
        return

    for module in getgx().modules.values():
        if module.builtin:
            continue
        mv = module.mv
        merge = dict((k,v) for k,v in getgx().merged_inh.items() if (k,0,0) in getgx().cnode and inode(k).mv == mv)
        source = open(module.filename).readlines()

        # --- constants/names/attributes
        for expr in merge:
            if isinstance(expr, (Const, Name)):
                paste(source, expr, nodetypestr(expr, inode(expr).parent, False, mv=mv), mv)

        for expr in merge:
            if isinstance(expr, Getattr):
                paste(source, expr, nodetypestr(expr, inode(expr).parent, False, mv=mv), mv)

        for expr in merge:
            if isinstance(expr, (Tuple, List, Dict)):
                paste(source, expr, nodetypestr(expr, inode(expr).parent, False, mv=mv), mv)

        # --- instance variables
        funcs = mv.funcs.values()
        for cl in mv.classes.values():
            labels = [var.name + ': ' + nodetypestr(var, cl, False, mv=mv) for var in cl.vars.values() if var in merge and merge[var] and not var.name.startswith('__')]
            if labels:
                paste(source, cl.node, ', '.join(labels), mv)
            funcs += cl.funcs.values()

        # --- function variables
        for func in funcs:
            if not func.node or func.node in getgx().inherited:
                continue
            vars = [func.vars[f] for f in func.formals]
            labels = [var.name + ': ' + nodetypestr(var, func, False, mv=mv) for var in vars if not var.name.startswith('__')]
            paste(source, func.node, ', '.join(labels), mv)

        # --- callfuncs
        for callfunc, _ in mv.callfuncs:
            if isinstance(callfunc.node, Getattr):
                if not callfunc.node.__class__.__name__.startswith('FakeGetattr'): # XXX
                    paste(source, callfunc.node.expr, nodetypestr(callfunc, inode(callfunc).parent, False, mv=mv), mv)
            else:
                paste(source, callfunc.node, nodetypestr(callfunc, inode(callfunc).parent, False, mv=mv), mv)

        # --- higher-level crap (listcomps, returns, assignments, prints)
        for expr in merge:
            if isinstance(expr, ListComp):
                paste(source, expr, nodetypestr(expr, inode(expr).parent, False, mv=mv), mv)
            elif isinstance(expr, Return):
                paste(source, expr, nodetypestr(expr.value, inode(expr).parent, False, mv=mv), mv)
            elif isinstance(expr, (AssTuple, AssList)):
                paste(source, expr, nodetypestr(expr, inode(expr).parent, False, mv=mv), mv)
            elif isinstance(expr, (Print, Printnl)):
                paste(source, expr, ', '.join(nodetypestr(child, inode(child).parent, False, mv=mv) for child in expr.nodes), mv)

        # --- assignments
        for expr in merge:
            if isinstance(expr, Assign):
                pairs = assign_rec(expr.nodes[0], expr.expr)
                paste(source, expr, ', '.join(nodetypestr(r, inode(r).parent, False, mv=mv) for (l, r) in pairs), mv)
            elif isinstance(expr, AugAssign):
                paste(source, expr, nodetypestr(expr.expr, inode(expr).parent, False, mv=mv), mv)

        # --- output annotated file (skip if no write permission)
        try:
            out = open(module.filename[:-3] + '.ss.py', 'w')
            out.write(''.join(source))
            out.close()
        except IOError:
            pass
