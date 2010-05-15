'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2009 Mark Dufour; License GNU GPL version 3 (See LICENSE)

annotate.py: annotate source code with inferred types, as *.ss.py (shedskin -a)

'''

import re, string

from compiler import *
from compiler.ast import *
from compiler.visitor import *

from shared import *
from cpp import typesetreprnew

def annotate():
    if not getgx().annotation:
        return
    re_comment = re.compile(r'#[^\"\']*$')
    def paste(expr, text):
        if not expr.lineno: return
        if (expr,0,0) in getgx().cnode and inode(expr).mv != mv: return # XXX
        line = source[expr.lineno-1][:-1]
        match = re_comment.search(line)
        if match:
            line = line[:match.start()]
        if text:
            text = '# '+text
        line = string.rstrip(line)
        if text and len(line) < 40: line += (40-len(line))*' '
        source[expr.lineno-1] = line
        if text: source[expr.lineno-1] += ' ' + text
        source[expr.lineno-1] += '\n'

    for module in getgx().modules.values():
        if module.builtin:
            continue

        mv = module.mv
        setmv(mv)

        # merge type information for nodes in module XXX inheritance across modules?
        merge = merged([n for n in getgx().types if n.mv == mv], inheritance=True)

        source = open(module.filename).readlines()

        # --- constants/names/attributes
        for expr in merge:
            if isinstance(expr, (Const, Name)):
                paste(expr, typesetreprnew(expr, inode(expr).parent, False))
        for expr in merge:
            if isinstance(expr, Getattr):
                paste(expr, typesetreprnew(expr, inode(expr).parent, False))
        for expr in merge:
            if isinstance(expr, (Tuple,List,Dict)):
                paste(expr, typesetreprnew(expr, inode(expr).parent, False))

        # --- instance variables
        funcs = getmv().funcs.values()
        for cl in getmv().classes.values():
            labels = [var.name+': '+typesetreprnew(var, cl, False) for var in cl.vars.values() if var in merge and merge[var] and not var.name.startswith('__')]
            if labels: paste(cl.node, ', '.join(labels))
            funcs += cl.funcs.values()

        # --- function variables
        for func in funcs:
            if not func.node or func.node in getgx().inherited: continue
            vars = [func.vars[f] for f in func.formals]
            labels = [var.name+': '+typesetreprnew(var, func, False) for var in vars if not var.name.startswith('__')]
            paste(func.node, ', '.join(labels))

        # --- callfuncs
        for callfunc, _ in getmv().callfuncs:
            if isinstance(callfunc.node, Getattr):
                if not isinstance(callfunc.node, (fakeGetattr, fakeGetattr2, fakeGetattr3)):
                    paste(callfunc.node.expr, typesetreprnew(callfunc, inode(callfunc).parent, False))
            else:
                paste(callfunc.node, typesetreprnew(callfunc, inode(callfunc).parent, False))

        # --- higher-level crap (listcomps, returns, assignments, prints)
        for expr in merge:
            if isinstance(expr, ListComp):
                paste(expr, typesetreprnew(expr, inode(expr).parent, False))
            elif isinstance(expr, Return):
                paste(expr, typesetreprnew(expr.value, inode(expr).parent, False))
            elif isinstance(expr, (AssTuple, AssList)):
                paste(expr, typesetreprnew(expr, inode(expr).parent, False))
            elif isinstance(expr, (Print,Printnl)):
                paste(expr, ', '.join([typesetreprnew(child, inode(child).parent, False) for child in expr.nodes]))

        # --- assignments
        for expr in merge:
            if isinstance(expr, Assign):
                pairs = assign_rec(expr.nodes[0], expr.expr)
                paste(expr, ', '.join([typesetreprnew(r, inode(r).parent, False) for (l,r) in pairs]))
            elif isinstance(expr, AugAssign):
                paste(expr, typesetreprnew(expr.expr, inode(expr).parent, False))

        # --- output annotated file (skip if no write permission)
        try:
            out = open(os.path.join(getgx().output_dir, module.filename[:-3]+'.ss.py'),'w')
            out.write(''.join(source))
            out.close()
        except IOError:
            pass
