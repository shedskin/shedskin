'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

annotate.py: annotate source code with inferred types, as *.ss.py (shedskin -a)

'''
import ast
import re

from . import ast_utils
from . import infer
from . import python
from . import typestr

RE_COMMENT = re.compile(r'#[^\"\']*$')


def paste(gx, source, expr, text, mv):
    if not expr.lineno:
        return
    if (expr, 0, 0) not in gx.cnode or infer.inode(gx, expr).mv != mv:
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


def annotate(gx):
    if not gx.annotation:
        return

    for module in gx.modules.values():
        if module.builtin:
            continue
        mv = module.mv
        merge = dict((k, v) for k, v in gx.merged_inh.items() if (k, 0, 0) in gx.cnode and infer.inode(gx, k).mv == mv)
        source = open(module.filename).readlines()

        # --- constants/names/attributes
        for expr in merge:
            if isinstance(expr, (ast.Num, ast.Str, ast.Name)):
                paste(gx, source, expr, typestr.nodetypestr(gx, expr, infer.inode(gx, expr).parent, False, mv=mv), mv)

        for expr in merge:
            if isinstance(expr, ast.Attribute):
                paste(gx, source, expr, typestr.nodetypestr(gx, expr, infer.inode(gx, expr).parent, False, mv=mv), mv)

        for expr in merge:
            if isinstance(expr, (ast.Tuple, ast.List, ast.Dict)):
                paste(gx, source, expr, typestr.nodetypestr(gx, expr, infer.inode(gx, expr).parent, False, mv=mv), mv)

        # --- instance variables
        funcs = mv.funcs.values()
        for cl in mv.classes.values():
            labels = [var.name + ': ' + typestr.nodetypestr(gx, var, cl, False, mv=mv) for var in cl.vars.values() if var in merge and merge[var] and not var.name.startswith('__')]
            if labels:
                paste(gx, source, cl.node, ', '.join(labels), mv)
            funcs += cl.funcs.values()

        # --- function variables
        for func in funcs:
            if not func.node or func.node in gx.inherited:
                continue
            vars = [func.vars[f] for f in func.formals]
            labels = [var.name + ': ' + typestr.nodetypestr(gx, var, func, False, mv=mv) for var in vars if not var.name.startswith('__')]
            paste(gx, source, func.node, ', '.join(labels), mv)

        # --- callfuncs
        for callfunc, _ in mv.callfuncs:
            if isinstance(callfunc.node, ast.Attribute):
                if not callfunc.node.__class__.__name__.startswith('FakeGetattr'):  # XXX
                    paste(gx, source, callfunc.node.expr, typestr.nodetypestr(gx, callfunc, infer.inode(gx, callfunc).parent, False, mv=mv), mv)
            else:
                paste(gx, source, callfunc.node, typestr.nodetypestr(gx, callfunc, infer.inode(gx, callfunc).parent, False, mv=mv), mv)

        # --- higher-level crap (listcomps, returns, assignments, prints)
        for expr in merge:
            if isinstance(expr, ast.ListComp):
                paste(gx, source, expr, typestr.nodetypestr(gx, expr, infer.inode(gx, expr).parent, False, mv=mv), mv)
            elif isinstance(expr, ast.Return):
                paste(gx, source, expr, typestr.nodetypestr(gx, expr.value, infer.inode(gx, expr).parent, False, mv=mv), mv)
            elif ast_utils.is_assign_list_or_tuple(expr):
                paste(gx, source, expr, typestr.nodetypestr(gx, expr, infer.inode(gx, expr).parent, False, mv=mv), mv)
            elif isinstance(expr, ast.Print):
                paste(gx, source, expr, ', '.join(typestr.nodetypestr(gx, child, infer.inode(gx, child).parent, False, mv=mv) for child in expr.nodes), mv)

        # --- assignments
        for expr in merge:
            if isinstance(expr, ast.Assign):
                pairs = python.assign_rec(expr.nodes[0], expr.expr)
                paste(gx, source, expr, ', '.join(typestr.nodetypestr(gx, r, infer.inode(gx, r).parent, False, mv=mv) for (l, r) in pairs), mv)
            elif isinstance(expr, ast.AugAssign):
                paste(gx, source, expr, typestr.nodetypestr(gx, expr.expr, infer.inode(gx, expr).parent, False, mv=mv), mv)

        # --- output annotated file (skip if no write permission)
        try:
            out = open(module.filename[:-3] + '.ss.py', 'w')
            out.write(''.join(source))
            out.close()
        except OSError:
            pass
