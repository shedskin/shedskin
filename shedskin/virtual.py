'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

virtual.py: virtual methods and variables

'''

import ast

from . import infer
from . import python
from . import typestr


def virtuals(self, cl, declare):
    if not cl.virtuals:
        return
    for ident, subclasses in cl.virtuals.items():
        if not subclasses:
            continue
        if ident in cl.funcs and infer.called(cl.funcs[ident]):
            subclasses = subclasses.copy()
            subclasses.add(cl)

        # --- merge arg/return types
        formals = []
        retexpr = False

        for subcl in subclasses:
            if ident not in subcl.funcs:
                continue

            func = subcl.funcs[ident]
            sig_types = []

            if func.returnexpr:
                retexpr = True
                if func.retnode.thing in self.mergeinh:
                    sig_types.append(self.mergeinh[func.retnode.thing])  # XXX mult returns; some targets with return some without..
                else:
                    sig_types.append(set())  # XXX

            for name in func.formals[1:]:
                var = func.vars[name]
                sig_types.append(self.mergeinh[var])
            formals.append(sig_types)

        merged = []
        for z in zip(*formals):
            merge = set()
            for _types in z:
                merge.update(_types)
            merged.append(merge)

        formals = []
        subcl0 = list(subclasses)[0]
        if ident in subcl0.funcs:
            formals = list(subclasses)[0].funcs[ident].formals[1:]

        ftypes = []
        for m in merged:
            ts = typestr.typestr(self.gx, m, mv=self.mv)
            if not ts.endswith('*'):
                ftypes.append(ts + ' ')
            else:
                ftypes.append(ts)

        # --- prepare for having to cast back arguments (virtual function call means multiple targets)
        for subcl in subclasses:
            if ident in subcl.funcs:
                subcl.funcs[ident].ftypes = ftypes

        # --- virtual function declaration
        if declare:
            self.start('virtual ')
            if retexpr and ftypes:
                self.append(ftypes[0])
                ftypes = ftypes[1:]
            else:
                self.append('void ')
            self.append(self.cpp_name(ident) + '(')

            self.append(', '.join(t + f for (t, f) in zip(ftypes, formals)))

            if ident in cl.funcs and self.inhcpa(cl.funcs[ident]):
                self.eol(')')
            else:
                if merged:
                    self.eol(') { return %s; }' % self.nothing(merged[0]))  # XXX msvc needs return statement
                else:
                    self.eol(') { }')  # XXX merged may be empty because of dynamic typing

            if ident in cl.funcs:
                cl.funcs[ident].declared = True


# --- determine virtual methods and variables
def analyze_virtuals(gx):
    for node in gx.merged_inh:
        # --- for every message
        if isinstance(node, ast.Call) and not infer.inode(gx, node).mv.module.builtin:  # ident == 'builtin':
            objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = infer.analyze_callfunc(gx, node, merge=gx.merged_inh)
            if not method_call or objexpr not in gx.merged_inh:
                continue  # XXX

            # --- determine abstract receiver class
            classes = typestr.polymorphic_t(gx, gx.merged_inh[objexpr])
            classes = [cl for cl in classes if isinstance(cl, python.Class)]
            if not classes:
                continue

            if isinstance(objexpr, ast.Name) and objexpr.id == 'self' and infer.inode(gx, objexpr).parent:
                abstract_cl = infer.inode(gx, objexpr).parent.parent
                upgrade_cl(gx, abstract_cl, node, ident, classes)

            lcp = typestr.lowest_common_parents(classes)
            if lcp:
                upgrade_cl(gx, lcp[0], node, ident, classes)


def upgrade_cl(gx, abstract_cl, node, ident, classes):
    if not abstract_cl or not isinstance(abstract_cl, python.Class):
        return
    subclasses = [cl for cl in classes if python.subclass(cl, abstract_cl)]

    # --- register virtual method
    if not ident.startswith('__'):
        redefined = False
        for concrete_cl in classes:
            if [cl for cl in concrete_cl.ancestors_upto(abstract_cl) if ident in cl.funcs and not cl.funcs[ident].inherited]:
                redefined = True
        if redefined:
            abstract_cl.virtuals.setdefault(ident, set()).update(subclasses)

    # --- register virtual var
    elif ident in ['__getattr__', '__setattr__'] and subclasses:
        var = infer.default_var(gx, node.args[0].s, abstract_cl)
        for subcl in subclasses:
            if var.name in subcl.vars and subcl.vars[var.name] in gx.merged_inh:
                gx.types.setdefault(gx.cnode[var, 0, 0], set()).update(gx.merged_inh[subcl.vars[var.name]])  # XXX shouldn't this be merged automatically already?
        abstract_cl.virtualvars.setdefault(node.args[0].s, set()).update(subclasses)
