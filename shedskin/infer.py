'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2011 Mark Dufour; License GNU GPL version 3 (See LICENSE)

infer.py: perform iterative type analysis

we combine two techniques from the literature, to analyze both parametric polymorphism and data polymorphism adaptively. these techniques are agesen's cartesian product algorithm and plevyak's iterative flow analysis (the data polymorphic part). for details about these algorithms, see ole agesen's excellent Phd thesis. for details about the Shed Skin implementation, see mark dufour's MsC thesis.

the cartesian product algorithm duplicates functions (or their graph counterpart), based on the cartesian product of possible argument types, whereas iterative flow analysis duplicates classes based on observed imprecisions at assignment points. the two integers mentioned in the graph.py description are used to keep track of duplicates along these dimensions (first class duplicate nr, then function duplicate nr).

the combined technique scales reasonably well, but can explode in many cases. there are many ways to improve this. some ideas:

-an iterative deepening approach, merging redundant duplicates after each deepening
-add and propagate filters across variables. e.g. 'a+1; a=b' implies that a and b must be of a type that implements '__add__'.

a complementary but very practical approach to (greatly) improve scalability would be to profile programs before compiling them, resulting in quite precise (lower bound) type information. type inference can then be used to 'fill in the gaps'.

iterative_dataflow_analysis():
    (FORWARD PHASE)
    -propagate types along constraint graph (propagate())
    -all the while creating function duplicates using the cartesian product algorithm(cpa())
    -when creating a function duplicate, fill in allocation points with correct type (ifa_seed_template())
    (BACKWARD PHASE)
    -determine classes to be duplicated, according to found imprecision points (ifa())
    -from imprecision points, follow the constraint graph (backwards) to find involved allocation points
    -duplicate classes, and spread them over these allocation points
    (CLEANUP)
    -quit if no further imprecision points (ifa() did not find anything)
    -otherwise, restore the constraint graph to its original state and restart
    -all the while maintaining types for each allocation point in getgx().alloc_info

update: we now analyze programs incrementally, adding several functions and redoing the full analysis each time. this seems to greatly help the CPA from exploding early on.

'''
import random
from compiler.ast import Const, Node, AssAttr, Keyword, CallFunc, \
    Getattr, Dict, List, Tuple, ListComp

import graph
import virtual
import copy_
import typestr
from shared import analyze_callfunc, parent_func, Variable, setmv, inode, merged, Function, add_to_worklist, default_var, analyze_args, add_constraint, def_class, CNode, nrargs, sys, class_, lookup_var
import config
from error import error


INCREMENTAL = True
INCREMENTAL_FUNCS = 5
INCREMENTAL_DATA = True
INCREMENTAL_ALLOCS = 20
MAXITERS = 30
CPA_LIMIT = 10


def DEBUG(level):
    return config.getgx().debug_level >= level


def class_copy(cl, dcpa):
    for var in cl.vars.values():  # XXX
        if not inode(var) in config.getgx().types:
            continue  # XXX research later

        inode(var).copy(dcpa, 0)
        config.getgx().types[config.getgx().cnode[var, dcpa, 0]] = inode(var).types().copy()

        for n in inode(var).in_:  # XXX
            if isinstance(n.thing, Const):
                add_constraint(n, config.getgx().cnode[var, dcpa, 0])

    for func in cl.funcs.values():
        if cl.mv.module.ident == 'builtin' and cl.ident != '__iter' and func.ident == '__iter__':  # XXX hack for __iter__:__iter()
            itercl = def_class('__iter')
            config.getgx().alloc_info[func.ident, ((cl, dcpa),), func.returnexpr[0]] = (itercl, itercl.dcpa)
            class_copy(itercl, dcpa)
            itercl.dcpa += 1

        func_copy(func, dcpa, 0)

# --- use dcpa=0,cpa=0 mold created by module visitor to duplicate function


def func_copy(func, dcpa, cpa, worklist=None, cart=None):
    # print 'funccopy', func, cart, dcpa, cpa

    # --- copy local end points of each constraint
    for (a, b) in func.constraints:
        if not (isinstance(a.thing, Variable) and parent_func(a.thing) != func) and a.dcpa == 0:
            a = a.copy(dcpa, cpa, worklist)
        if not (isinstance(b.thing, Variable) and parent_func(b.thing) != func) and b.dcpa == 0:
            b = b.copy(dcpa, cpa, worklist)

        add_constraint(a, b, worklist)

    # --- copy other nodes
    for node in func.nodes:
        node.copy(dcpa, cpa, worklist)

    # --- iterative flow analysis: seed allocation sites in new template
    ifa_seed_template(func, cart, dcpa, cpa, worklist)


def print_typeset(types):
    l = list(types.items())
    l.sort(lambda x, y: cmp(repr(x[0]), repr(y[0])))
    for uh in l:
        if not uh[0].mv.module.builtin:
            print repr(uh[0]) + ':', uh[1]  # , uh[0].parent
    print


def print_state():
    # print 'state:'
    print_typeset(config.getgx().types)


def print_constraints():
    # print 'constraints:'
    l = list(config.getgx().constraints)
    l.sort(lambda x, y: cmp(repr(x[0]), repr(y[0])))
    for (a, b) in l:
        if not (a.mv.module.builtin and b.mv.module.builtin):
            print a, '->', b
            if not a in config.getgx().types or not b in config.getgx().types:
                print 'NOTYPE', a in config.getgx().types, b in config.getgx().types
    print

# --- iterative dataflow analysis


def propagate():
    if DEBUG(1):
        print 'propagate'
    ggx = config.getgx()

    # --- initialize working sets
    worklist = []
    changed = set()
    for node in ggx.types:
        if ggx.types[node]:
            add_to_worklist(worklist, node)
        expr = node.thing
        if (isinstance(expr, CallFunc) and not expr.args) or expr in ggx.lambdawrapper:  # XXX
            changed.add(node)

    for node in changed:
        cpa(node, worklist)

    builtins = set(ggx.builtins)
    types = ggx.types

    # --- iterative dataflow analysis
    while worklist:
        callnodes = set()
        while worklist:
            a = worklist.pop(0)
            a.in_list = 0

            for callfunc in a.callfuncs:
                t = (callfunc, a.dcpa, a.cpa)
                if t in ggx.cnode:
                    callnodes.add(ggx.cnode[t])

            for b in a.out.copy():  # XXX can change...?
                # for builtin types, the set of instance variables is known, so do not flow into non-existent ones # XXX ifa
                if isinstance(b.thing, Variable) and isinstance(b.thing.parent, class_):
                    parent_ident = b.thing.parent.ident
                    if parent_ident in builtins:
                        if parent_ident in ['int_', 'float_', 'str_', 'none', 'bool_']:
                            continue
                        elif parent_ident in ['list', 'tuple', 'frozenset', 'set', 'file', '__iter', 'deque', 'array'] and b.thing.name != 'unit':
                            continue
                        elif parent_ident in ('dict', 'defaultdict') and b.thing.name not in ['unit', 'value']:
                            continue
                        elif parent_ident == 'tuple2' and b.thing.name not in ['unit', 'first', 'second']:
                            continue

                typesa = types[a]
                typesb = types[b]
                oldsize = len(typesb)
                typesb.update(typesa)
                if len(typesb) > oldsize:
                    add_to_worklist(worklist, b)

        for callnode in callnodes:
            cpa(callnode, worklist)

# --- determine cartesian product of possible function and argument types


def possible_functions(node, analysis):
    expr = node.thing

    # --- determine possible target functions
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analysis
    funcs = []

    if anon_func:
        # anonymous call
        types = config.getgx().cnode[expr.node, node.dcpa, node.cpa].types()
        types = [t for t in types if isinstance(t[0], Function)]  # XXX XXX analyse per t, sometimes class, sometimes function..

        if list(types)[0][0].parent:  # method reference XXX merge below?
            funcs = [(f[0], f[1], (f[0].parent, f[1])) for f in types]  # node.dcpa: connect to right dcpa duplicate version
        else:  # function reference
            funcs = [(f[0], f[1], None) for f in types]  # function call: only one version; no objtype

    elif constructor:
        funcs = [(t[0].funcs['__init__'], t[1], t) for t in node.types() if '__init__' in t[0].funcs]

    elif parent_constr:
        objtypes = config.getgx().cnode[lookup_var('self', node.parent), node.dcpa, node.cpa].types()
        funcs = [(t[0].funcs[ident], t[1], None) for t in objtypes if ident in t[0].funcs]

    elif direct_call:
        funcs = [(direct_call, 0, None)]

    elif method_call:
        objtypes = config.getgx().cnode[objexpr, node.dcpa, node.cpa].types()
        objtypes = [t for t in objtypes if not isinstance(t[0], Function)]  # XXX

        funcs = [(t[0].funcs[ident], t[1], t) for t in objtypes if ident in t[0].funcs]

    return funcs


def possible_argtypes(node, funcs, analysis, worklist):
    expr = node.thing
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analysis
    if funcs:
        func = funcs[0][0]  # XXX

    args = []
    if expr.star_args:  # XXX
        args = [expr.star_args]
    elif funcs and not func.node:  # XXX getattr, setattr
        args = expr.args
    elif funcs:
        actuals, formals, used_defaults, varargs, _ = analyze_args(expr, func, node)

        if not node.defnodes:
            for i, default in enumerate(used_defaults):
                defnode = CNode((inode(node.thing), i), node.dcpa, node.cpa, parent=func)
                config.getgx().types[defnode] = set()
                defnode.callfuncs.append(node.thing)
                add_constraint(config.getgx().cnode[default, 0, 0], defnode, worklist)  # XXX bad place
        node.defnodes = True

        for act, form in zip(actuals, formals):
            if parent_constr or not (isinstance(func.parent, class_) and form == 'self'):  # XXX merge
                args.append(act)

    argtypes = []
    for arg in args:
        if (arg, node.dcpa, node.cpa) in config.getgx().cnode:
            argtypes.append(config.getgx().cnode[arg, node.dcpa, node.cpa].types())
        else:
            argtypes.append(inode(arg).types())  # XXX def arg?

    # store arg count for wrappers to builtin refs
    if funcs and (func.lambdawrapper or node.thing in config.getgx().lambdawrapper):
        while argtypes and not argtypes[-1]:
            argtypes = argtypes[:-1]
        if func.lambdawrapper:
            if expr.star_args and node.parent and node.parent.node.varargs:
                func.largs = node.parent.xargs[node.dcpa, node.cpa] - len(node.parent.formals) + 1
            else:
                func.largs = len(argtypes)

    return argtypes


def product(*lists):
    if not lists:
        return [()]
    result = []
    prod = product(*lists[:-1])
    for x in prod:
        for y in lists[-1]:
            result.append(x + (y,))
    return result


def cartesian_product(node, analysis, worklist):
    funcs = possible_functions(node, analysis)
    if not funcs:
        return []
    argtypes = possible_argtypes(node, funcs, analysis, worklist)
    alltypes = [funcs] + argtypes
    return product(*alltypes)


def redirect(c, dcpa, func, callfunc, ident, callnode, direct_call, constructor):
    # redirect based on number of arguments (__%s%d syntax in builtins)
    if func.mv.module.builtin:
        if isinstance(func.parent, class_):
            funcs = func.parent.funcs
        else:
            funcs = func.mv.funcs
        redir = '__%s%d' % (func.ident, len([kwarg for kwarg in callfunc.args if not isinstance(kwarg, Keyword)]))
        func = funcs.get(redir, func)

    # filter
    if direct_call and ident == 'filter':
        clnames = [x[0].ident for x in c if isinstance(x[0], class_)]
        if 'str_' in clnames or 'tuple' in clnames or 'tuple2' in clnames:
            func = func.mv.funcs['__' + ident]

    # staticmethod
    if isinstance(func.parent, class_) and func.ident in func.parent.staticmethods:
        dcpa = 1

    # dict.__init__
    if constructor and (ident, nrargs(callfunc)) in (('dict', 1), ('defaultdict', 2)):
        clnames = [x[0].ident for x in c if isinstance(x[0], class_)]
        if 'dict' in clnames or 'defaultdict' in clnames:
            func = list(callnode.types())[0][0].funcs['__initdict__']
        else:
            func = list(callnode.types())[0][0].funcs['__inititer__']

    # dict.update
    if func.ident == 'update' and isinstance(func.parent, class_) and func.parent.ident in ('dict', 'defaultdict'):
        clnames = [x[0].ident for x in c if isinstance(x[0], class_)]
        if not ('dict' in clnames or 'defaultdict' in clnames):
            func = func.parent.funcs['updateiter']

    # list, tuple
    if constructor and ident in ('list', 'tuple', 'set', 'frozenset') and nrargs(callfunc) == 1:
        func = list(callnode.types())[0][0].funcs['__inititer__']  # XXX use __init__?

    # array
    if constructor and ident == 'array' and isinstance(callfunc.args[0], Const):
        typecode = callfunc.args[0].value
        array_type = None
        if typecode in 'bBhHiIlL':
            array_type = 'int'
        elif typecode == 'c':
            array_type = 'str'
        elif typecode in 'fd':
            array_type = 'float'
        if array_type is not None:
            func = list(callnode.types())[0][0].funcs['__init_%s__' % array_type]

    # tuple2.__getitem__(0/1) -> __getfirst__/__getsecond__
    if (isinstance(callfunc.node, Getattr) and callfunc.node.attrname == '__getitem__' and
        isinstance(callfunc.args[0], Const) and callfunc.args[0].value in (0, 1) and
            func.parent.mv.module.builtin and func.parent.ident == 'tuple2'):
        if callfunc.args[0].value == 0:
            func = func.parent.funcs['__getfirst__']
        else:
            func = func.parent.funcs['__getsecond__']

    # property
    if isinstance(callfunc.node, Getattr) and callfunc.node.attrname in ['__setattr__', '__getattr__']:
        if isinstance(func.parent, class_) and callfunc.args and callfunc.args[0].value in func.parent.properties:
            arg = callfunc.args[0].value
            if callfunc.node.attrname == '__setattr__':
                func = func.parent.funcs[func.parent.properties[arg][1]]
            else:
                func = func.parent.funcs[func.parent.properties[arg][0]]
            c = c[1:]

    # win32
    if sys.platform == 'win32' and func.mv.module.builtin and isinstance(func.parent, class_) and '__win32' + func.ident in func.parent.funcs:
        func = func.parent.funcs['__win32' + func.ident]

    return c, dcpa, func

# --- cartesian product algorithm; adds interprocedural constraints


def cpa(callnode, worklist):
    analysis = analyze_callfunc(callnode.thing, callnode)
    cp = cartesian_product(callnode, analysis, worklist)
    if not cp:
        return
    if len(cp) > config.getgx().cpa_limit and not config.getgx().cpa_clean:
        config.getgx().cpa_limited = True
        return []
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analysis

    # --- iterate over argument type combinations
    for c in cp:
        (func, dcpa, objtype), c = c[0], c[1:]

        if INCREMENTAL:
            if not func.mv.module.builtin and func not in config.getgx().added_funcs_set and not func.ident in ['__getattr__', '__setattr__']:
                if INCREMENTAL_DATA:
                    if config.getgx().added_allocs >= INCREMENTAL_ALLOCS:
                        continue
                else:
                    if config.getgx().added_funcs >= INCREMENTAL_FUNCS:
                        continue
                config.getgx().added_funcs += 1
                config.getgx().added_funcs_set.add(func)
                if DEBUG(1):
                    print 'adding', func

        if objtype:
            objtype = (objtype,)
        else:
            objtype = ()

        # redirect in special cases
        callfunc = callnode.thing
        c, dcpa, func = redirect(c, dcpa, func, callfunc, ident, callnode, direct_call, constructor)

        # already connected to template
        if (func,) + objtype + c in callnode.nodecp:
            continue
        callnode.nodecp.add((func,) + objtype + c)

        # create new template
        if not dcpa in func.cp or not c in func.cp[dcpa]:
            create_template(func, dcpa, c, worklist)
        cpa = func.cp[dcpa][c]
        func.xargs[dcpa, cpa] = len(c)

        # __getattr__, __setattr__
        if connect_getsetattr(func, callnode, callfunc, dcpa, worklist):
            continue

        # connect actuals and formals
        actuals_formals(callfunc, func, callnode, dcpa, cpa, objtype + c, analysis, worklist)

        # connect call and return expressions
        if func.retnode and not constructor:
            retnode = config.getgx().cnode[func.retnode.thing, dcpa, cpa]
            add_constraint(retnode, callnode, worklist)


def connect_getsetattr(func, callnode, callfunc, dcpa, worklist):
    if (isinstance(callfunc.node, Getattr) and callfunc.node.attrname in ['__setattr__', '__getattr__'] and
            not (isinstance(func.parent, class_) and callfunc.args and callfunc.args[0].value in func.parent.properties)):
        varname = callfunc.args[0].value
        parent = func.parent

        var = default_var(varname, parent, worklist)  # XXX always make new var??
        inode(var).copy(dcpa, 0, worklist)

        if not config.getgx().cnode[var, dcpa, 0] in config.getgx().types:
            config.getgx().types[config.getgx().cnode[var, dcpa, 0]] = set()

        config.getgx().cnode[var, dcpa, 0].mv = parent.module.mv  # XXX move into default_var

        if callfunc.node.attrname == '__setattr__':
            add_constraint(config.getgx().cnode[callfunc.args[1], callnode.dcpa, callnode.cpa], config.getgx().cnode[var, dcpa, 0], worklist)
        else:
            add_constraint(config.getgx().cnode[var, dcpa, 0], callnode, worklist)
        return True
    return False


def create_template(func, dcpa, c, worklist):
    # --- unseen cartesian product: create new template
    if not dcpa in func.cp:
        func.cp[dcpa] = {}
    func.cp[dcpa][c] = cpa = len(func.cp[dcpa])  # XXX +1

    if DEBUG(2) and not func.mv.module.builtin and not func.ident in ['__getattr__', '__setattr__']:
        print 'template', (func, dcpa), c

    config.getgx().templates += 1
    func_copy(func, dcpa, cpa, worklist, c)


def actuals_formals(expr, func, node, dcpa, cpa, types, analysis, worklist):
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analysis

    if expr.star_args:  # XXX only in lib/
        formals = func.formals
        actuals = len(formals) * [expr.star_args]
        types = len(formals) * types
    else:
        actuals, formals, _, varargs, _error = analyze_args(expr, func, node)
        if _error:
            return

    for (actual, formal, formaltype) in zip(actuals, formals, types):
        formalnode = config.getgx().cnode[func.vars[formal], dcpa, cpa]

        if formaltype[1] != 0:  # ifa: remember dataflow information for non-simple types
            if actual is None:
                if constructor:
                    objexpr = node.thing

                if method_call or constructor:
                    formalnode.in_.add(config.getgx().cnode[objexpr, node.dcpa, node.cpa])
            else:
                if actual in func.defaults:
                    formalnode.in_.add(config.getgx().cnode[actual, 0, 0])
                else:
                    formalnode.in_.add(config.getgx().cnode[actual, node.dcpa, node.cpa])

        config.getgx().types[formalnode].add(formaltype)
        add_to_worklist(worklist, formalnode)

# --- iterative flow analysis: after each iteration, detect imprecisions, and split involved contours


def ifa():
    if DEBUG(1):
        print 'ifa'
    split = []  # [(set of creation nodes, new type number), ..]

    allcsites = {}
    for n, types in config.getgx().types.iteritems():
        if not n.in_:
            for (cl, dcpa) in types:
                allcsites.setdefault((cl, dcpa), set()).add(n)

    for cl in ifa_classes_to_split():
        if DEBUG(3):
            print 'IFA: --- class %s ---' % cl.ident
        cl.newdcpa = cl.dcpa
        vars = [cl.vars[name] for name in cl.tvar_names() if name in cl.vars]
        classes_nr, nr_classes = ifa_class_types(cl, vars)
        for dcpa in range(1, cl.dcpa):
            if ifa_split_vars(cl, dcpa, vars, nr_classes, classes_nr, split, allcsites) is not None:
                if DEBUG(3):
                    print 'IFA found splits, return'
                return split
    if DEBUG(3):
        print 'IFA final return'
    return split


def ifa_split_vars(cl, dcpa, vars, nr_classes, classes_nr, split, allcsites):
    for (varnum, var) in enumerate(vars):
        if not (var, dcpa, 0) in config.getgx().cnode:
            continue
        node = config.getgx().cnode[var, dcpa, 0]
        creation_points, paths, assignsets, allnodes, csites, emptycsites = ifa_flow_graph(cl, dcpa, node, allcsites)
        if DEBUG(3):
            print 'IFA visit var %s.%s, %d, csites %d' % (cl.ident, var.name, dcpa, len(csites))
        if len(csites) + len(emptycsites) == 1:
            continue
        if ((len(merge_simple_types(config.getgx().types[node])) > 1 and len(assignsets) > 1) or
                (assignsets and emptycsites)):  # XXX move to split_no_conf
            ifa_split_no_confusion(cl, dcpa, varnum, classes_nr, nr_classes, csites, emptycsites, allnodes, split)
        if split:
            break
        for node in allnodes:
            if not ifa_confluence_point(node, creation_points):
                continue
            if not node.thing.formal_arg and not isinstance(node.thing.parent, class_):
                continue
            remaining = ifa_determine_split(node, allnodes)
            if len(remaining) < 2 or len(remaining) >= 10:
                continue
            # --- if it exists, perform actual splitting
            if DEBUG(3):
                print 'IFA normal split, remaining:', len(remaining)
            for splitsites in remaining[1:]:
                ifa_split_class(cl, dcpa, splitsites, split)
            return split

        # --- try to partition csites across paths
        prt = {}
        for c in csites:
            ts = set()
            for p in c.paths:
                ts.update(p)
            ts = frozenset(ts)
            if ts not in prt:
                prt[ts] = []
            prt[ts].append(c)
        if len(prt) > 1:
            if DEBUG(3):
                print 'IFA partition csites:', prt.values()[0]
            ifa_split_class(cl, dcpa, prt.values()[0], split)

        # --- if all else fails, perform wholesale splitting
        elif len(paths) > 1 and 1 < len(csites) < 10:
            if DEBUG(3):
                print 'IFA wholesale splitting, csites:', len(csites)
            for csite in csites[1:]:
                ifa_split_class(cl, dcpa, [csite], split)
            return split

def ifa_split_no_confusion(cl, dcpa, varnum, classes_nr, nr_classes, csites, emptycsites, allnodes, split):
    '''creation sites on single path: split them off, possibly reusing contour'''
    attr_types = list(nr_classes[dcpa])
    noconf = set([n for n in csites if len(n.paths) == 1] + emptycsites)
    others = len(csites) + len(emptycsites) - len(noconf)
    subtype_csites = {}
    for node in noconf:
        if node.paths:
            assign_set = node.paths[0]
        else:
            assign_set = frozenset()
        if attr_types[varnum] == assign_set:
            others += 1
        else:
            subtype = attr_types[:]
            subtype[varnum] = assign_set
            subtype = tuple(subtype)
            try:
                subtype_csites[subtype].append(node)
            except KeyError:
                subtype_csites[subtype] = [node]
    items = subtype_csites.items()
    if not others:
        items = items[1:]
    for subtype, csites in subtype_csites.iteritems():  # XXX items?
        if subtype in classes_nr:  # reuse contour
            nr = classes_nr[subtype]
            split.append((cl, dcpa, csites, nr))
            cl.splits[nr] = dcpa
        else:  # create new contour
            classes_nr[subtype] = cl.newdcpa
            ifa_split_class(cl, dcpa, csites, split)
    if DEBUG(3) and subtype_csites:
        print 'IFA found simple split', subtype_csites.keys()


def ifa_class_types(cl, vars):
    ''' create table for previously deduced types '''
    classes_nr, nr_classes = {}, {}
    for dcpa in range(1, cl.dcpa):
        attr_types = []  # XXX merge with ifa_merge_contours.. sep func?
        for var in vars:
            if (var, dcpa, 0) in config.getgx().cnode:
                attr_types.append(merge_simple_types(config.getgx().cnode[var, dcpa, 0].types()))
            else:
                attr_types.append(frozenset())
        attr_types = tuple(attr_types)
        if DEBUG(3) and [x for x in attr_types if x]:
            print 'IFA', str(dcpa) + ':', zip([var.name for var in vars], map(list, attr_types))
        nr_classes[dcpa] = attr_types
        classes_nr[attr_types] = dcpa
    return classes_nr, nr_classes


def ifa_determine_split(node, allnodes):
    ''' determine split along incoming dataflow edges '''
    remaining = [incoming.csites.copy() for incoming in node.in_ if incoming in allnodes]
    # --- try to clean out larger collections, if subsets are in smaller ones
    for (i, seti) in enumerate(remaining):
        for setj in remaining[i + 1:]:
            in_both = seti.intersection(setj)
            if in_both:
                if len(seti) > len(setj):
                    seti -= in_both
                else:
                    setj -= in_both
    remaining = [setx for setx in remaining if setx]
    return remaining


def ifa_classes_to_split():
    ''' setup classes to perform splitting on '''
    classes = []
    for ident in ['list', 'tuple', 'tuple2', 'dict', 'set', 'frozenset', 'deque', 'defaultdict', '__iter', 'array']:
        for cl in config.getgx().allclasses:
            if cl.mv.module.builtin and cl.ident == ident:
                cl.splits = {}
                classes.append(cl)
                break
    random.shuffle(classes)
    return classes


def ifa_confluence_point(node, creation_points):
    ''' determine if node is confluence point '''
    if len(node.in_) > 1 and isinstance(node.thing, Variable):
        for csite in node.csites:
            occ = [csite in crpoints for crpoints in creation_points.values()].count(True)
            if occ > 1:
                return True
    return False


def ifa_flow_graph(cl, dcpa, node, allcsites):
    creation_points, paths, assignsets = {}, {}, {}
    allnodes = set()
    csites = []

    # --- determine assignment sets
    for a in node.in_:
        types = config.getgx().types[a]
        if types:
            if a.thing in config.getgx().assign_target:  # XXX *args
                target = config.getgx().cnode[config.getgx().assign_target[a.thing], a.dcpa, a.cpa]
                # print 'target', a, target, types
                assignsets.setdefault(merge_simple_types(types), []).append(target)

    # --- determine backflow paths and creation points per assignment set
    for assign_set, targets in assignsets.iteritems():
        path = backflow_path(targets, (cl, dcpa))
        paths[assign_set] = path
        allnodes.update(path)
        alloc = [n for n in path if not n.in_]
        creation_points[assign_set] = alloc

    # --- per node, determine paths it is located on
    for n in allnodes:
        n.paths = []
    for assign_set, path in paths.iteritems():
        for n in path:
            n.paths.append(assign_set)

    # --- for each node, determine creation points that 'flow' through it
    for n in allnodes:
        n.csites = set()
        if not n.in_:
            n.csites.add(n)
            csites.append(n)
    flow_creation_sites(csites, allnodes)

    # csites not flowing to any assignment
    allcsites2 = allcsites.get((cl, dcpa), set())
    emptycsites = list(allcsites2 - set(csites))
    for n in emptycsites:
        n.paths = []

    return creation_points, paths, assignsets, allnodes, csites, emptycsites


def ifa_split_class(cl, dcpa, things, split):
    split.append((cl, dcpa, things, cl.newdcpa))
    cl.splits[cl.newdcpa] = dcpa
    cl.newdcpa += 1


def update_progressbar(perc):
    if not config.getgx().silent:
        print '\r%s%d%%' % (int(perc * 32) * '*', 100 * perc),
        if DEBUG(1):
            print
        else:
            sys.stdout.flush()

# --- cartesian product algorithm (cpa) & iterative flow analysis (ifa)


def iterative_dataflow_analysis():
    if not config.getgx().silent:
        print '[analyzing types..]'
    backup = backup_network()

    config.getgx().orig_types = {}
    for n, t in config.getgx().types.iteritems():
        config.getgx().orig_types[n] = t

    if INCREMENTAL:
        update_progressbar(0)

    config.getgx().added_funcs = INCREMENTAL_FUNCS  # analyze root of callgraph in first round
    config.getgx().added_funcs_set = set()
    config.getgx().added_allocs = 0
    config.getgx().added_allocs_set = set()
    config.getgx().cpa_limit = CPA_LIMIT
    config.getgx().cpa_clean = False

    while True:
        config.getgx().iterations += 1
        config.getgx().total_iterations += 1
        maxiter = (config.getgx().iterations == MAXITERS)
        if DEBUG(1):
            print '\n*** iteration %d ***' % config.getgx().iterations

        # --- propagate using cartesian product algorithm
        config.getgx().new_alloc_info = {}
#        print 'table'
#        print '\n'.join([repr(e)+': '+repr(l) for e,l in getgx().alloc_info.items()])
        config.getgx().cpa_limited = False
        propagate()
        config.getgx().alloc_info = config.getgx().new_alloc_info

        if config.getgx().cpa_limited:
            if DEBUG(1):
                print 'CPA limit %d reached!' % config.getgx().cpa_limit
        else:
            config.getgx().cpa_clean = True

        # --- ifa: detect conflicting assignments to instance variables, and split contours to resolve these
        split = ifa()
        if split:
            if DEBUG(1):
                print '%d splits' % len(split)
            elif DEBUG(3):
                print 'IFA splits', [(s[0], s[1], s[3]) for s in split]

        if not split or maxiter:
            if DEBUG(1) and not maxiter:
                print 'no splits'
            if INCREMENTAL:
                allfuncs = len([f for f in config.getgx().allfuncs if not f.mv.module.builtin and not [start for start in ('__iadd__', '__imul__', '__str__', '__hash__') if f.ident.startswith(start)]])
                perc = 1.0
                if allfuncs:
                    perc = min(len(config.getgx().added_funcs_set) / float(allfuncs), 1.0)
                update_progressbar(perc)
            if maxiter:
                print '\n*WARNING* reached maximum number of iterations'
                config.getgx().maxhits += 1
                if config.getgx().maxhits == 3:
                    return

            config.getgx().cpa_clean = False
            if INCREMENTAL and (config.getgx().added_funcs or config.getgx().added_allocs):
                config.getgx().added_funcs = 0
                config.getgx().added_allocs = 0
                config.getgx().iterations = 0
            elif config.getgx().cpa_limited:
                config.getgx().cpa_limit *= 2
                config.getgx().iterations = 0
            else:
                if INCREMENTAL:
                    update_progressbar(1.0)
                if DEBUG(1):
                    print '\niterations:', config.getgx().total_iterations, 'templates:', config.getgx().templates
                elif not config.getgx().silent:
                    print
                return

        if not INCREMENTAL and not DEBUG(1):
            sys.stdout.write('*')
            sys.stdout.flush()

        # --- update alloc info table for split contours
        for cl, dcpa, nodes, newnr in split:
            for n in nodes:
                parent = parent_func(n.thing)
                if parent:
                    if n.dcpa in parent.cp:
                        for cart, cpa in parent.cp[n.dcpa].items():  # XXX not very fast
                            if cpa == n.cpa:
                                if parent.parent and isinstance(parent.parent, class_):  # self
                                    cart = ((parent.parent, n.dcpa),) + cart

                                config.getgx().alloc_info[parent.ident, cart, n.thing] = (cl, newnr)
                                break

        beforetypes = backup[0]

        # --- clean out constructor node types in functions, possibly to be seeded again
        for node in beforetypes:
            func = parent_func(node.thing)
            if isinstance(func, Function):
                if node.constructor and isinstance(node.thing, (List, Dict, Tuple, ListComp, CallFunc)):
                    beforetypes[node] = set()

        # --- create new class types, and seed global nodes
        for cl, dcpa, nodes, newnr in split:
            if newnr == cl.dcpa:
                class_copy(cl, newnr)
                cl.dcpa += 1

            # print 'split off', nodes, newnr
            for n in nodes:
                if not parent_func(n.thing):
                    beforetypes[n] = set([(cl, newnr)])

        # --- restore network
        restore_network(backup)

# --- seed allocation sites in newly created templates (called by function.copy())


def ifa_seed_template(func, cart, dcpa, cpa, worklist):
    if cart is not None:  # (None means we are not in the process of propagation)
        # print 'funccopy', func.ident #, func.nodes
        if isinstance(func.parent, class_):  # self
            cart = ((func.parent, dcpa),) + cart

        added = config.getgx().added_allocs_set
        added_new = 0

        for node in func.nodes_ordered:
            if node.constructor and isinstance(node.thing, (List, Dict, Tuple, ListComp, CallFunc)):
                if node.thing not in added:
                    if INCREMENTAL_DATA and not func.mv.module.builtin:
                        if config.getgx().added_allocs >= INCREMENTAL_ALLOCS:
                            continue
                        added_new += 1
                        config.getgx().added_allocs += 1
                    added.add(node.thing)

                # --- contour is specified in alloc_info
                parent = node.parent
                while isinstance(parent.parent, Function):
                    parent = parent.parent

                alloc_id = (parent.ident, cart, node.thing)  # XXX ident?
                alloc_node = config.getgx().cnode[node.thing, dcpa, cpa]

                if alloc_id in config.getgx().alloc_info:
                    pass
#                    print 'specified' # print 'specified', func.ident, cart, alloc_node, alloc_node.callfuncs, getgx().alloc_info[alloc_id]
                # --- contour is newly split: copy allocation type for 'mother' contour; modify alloc_info
                else:
                    mother_alloc_id = alloc_id

                    for (id, c, thing) in config.getgx().alloc_info:
                        if id == parent.ident and thing is node.thing:
                            for a, b in zip(cart, c):
                                if a != b and not (isinstance(a[0], class_) and a[0] is b[0] and a[1] in a[0].splits and a[0].splits[a[1]] == b[1]):
                                    break
                            else:
                                mother_alloc_id = (id, c, thing)
                                break

                    # print 'not specified.. mother id:', mother_alloc_id
                    if mother_alloc_id in config.getgx().alloc_info:
                        config.getgx().alloc_info[alloc_id] = config.getgx().alloc_info[mother_alloc_id]
                        # print 'mothered', alloc_node, getgx().alloc_info[mother_alloc_id]
                    elif config.getgx().orig_types[node]:  # empty constructors that do not flow to assignments have no type
                        # print 'no mother', func.ident, cart, mother_alloc_id, alloc_node, getgx().types[node]
                        config.getgx().alloc_info[alloc_id] = list(config.getgx().orig_types[node])[0]
                    else:
                        # print 'oh boy'
                        for (id, c, thing) in config.getgx().alloc_info:  # XXX vhy?
                            if id == parent.ident and thing is node.thing:
                                mother_alloc_id = (id, c, thing)
                                config.getgx().alloc_info[alloc_id] = config.getgx().alloc_info[mother_alloc_id]
                                break

                if alloc_id in config.getgx().alloc_info:
                    config.getgx().new_alloc_info[alloc_id] = config.getgx().alloc_info[alloc_id]
                    config.getgx().types[alloc_node] = set()
                    # print 'seeding..', alloc_node, getgx().alloc_info[alloc_id], alloc_node.thing in getgx().empty_constructors
                    config.getgx().types[alloc_node].add(config.getgx().alloc_info[alloc_id])
                    add_to_worklist(worklist, alloc_node)

        if DEBUG(1) and added_new and not func.mv.module.builtin:
            print '%d seed(s)' % added_new, func

# --- for a set of target nodes of a specific type of assignment (e.g. int to (list,7)), flow back to creation points


def backflow_path(worklist, t):
    path = set(worklist)
    while worklist:
        new = set()
        for node in worklist:
            for incoming in node.in_:
                if t in config.getgx().types[incoming]:
                    incoming.fout.add(node)
                    if not incoming in path:
                        path.add(incoming)
                        new.add(incoming)
        worklist = new
    return path


def flow_creation_sites(worklist, allnodes):
    while worklist:
        new = set()
        for node in worklist:
            for out in node.fout:
                if out in allnodes:
                    oldsize = len(out.csites)
                    out.csites.update(node.csites)
                    if len(out.csites) > oldsize:
                        new.add(out)
        worklist = new

# --- backup constraint network


def backup_network():
    beforetypes = {}
    for node, typeset in config.getgx().types.items():
        beforetypes[node] = typeset.copy()

    beforeconstr = config.getgx().constraints.copy()

    beforeinout = {}
    for node in config.getgx().types:
        beforeinout[node] = (node.in_.copy(), node.out.copy())

    beforecnode = config.getgx().cnode.copy()

    return (beforetypes, beforeconstr, beforeinout, beforecnode)

# --- restore constraint network, introducing new types


def restore_network(backup):
    beforetypes, beforeconstr, beforeinout, beforecnode = backup

    config.getgx().types = {}
    for node, typeset in beforetypes.items():
        config.getgx().types[node] = typeset.copy()

    config.getgx().constraints = beforeconstr.copy()
    config.getgx().cnode = beforecnode.copy()

    for node, typeset in config.getgx().types.items():
        node.nodecp = set()
        node.defnodes = False
        befinout = beforeinout[node]
        node.in_, node.out = befinout[0].copy(), befinout[1].copy()
        node.fout = set()  # XXX ?

    for var in config.getgx().allvars:  # XXX we have to restore some variable constraint nodes.. remove vars?
        if not (var, 0, 0) in config.getgx().cnode:
            CNode(var, parent=var.parent)

    for func in config.getgx().allfuncs:
        func.cp = {}


def merge_simple_types(types):
    merge = types.copy()
    if len(types) > 1 and (def_class('none'), 0) in types:
        if not (def_class('int_'), 0) in types and not (def_class('float_'), 0) in types and not (def_class('bool_'), 0) in types:
            merge.remove((def_class('none'), 0))

    return frozenset(merge)


def analyze(module_name):
    mv = None
    setmv(mv)

    # --- build dataflow graph from source code
    config.getgx().main_module = graph.parse_module(module_name)
    mv = config.getgx().main_module.mv
    setmv(mv)

    # --- seed class_.__name__ attributes..
    for cl in config.getgx().allclasses:
        if cl.ident == 'class_':
            var = default_var('__name__', cl)
            config.getgx().types[inode(var)] = set([(def_class('str_'), 0)])

    # --- non-ifa: copy classes for each allocation site
    for cl in config.getgx().allclasses:
        if cl.ident in ['int_', 'float_', 'none', 'class_', 'str_', 'bool_']:
            continue
        if cl.ident == 'list':
            cl.dcpa = len(config.getgx().list_types) + 2
        elif cl.ident != '__iter':  # XXX huh
            cl.dcpa = 2

        for dcpa in range(1, cl.dcpa):
            class_copy(cl, dcpa)

    var = default_var('unit', def_class('str_'))
    config.getgx().types[inode(var)] = set([(def_class('str_'), 0)])

    # --- cartesian product algorithm & iterative flow analysis
    iterative_dataflow_analysis()

    if not config.getgx().silent:
        print '[generating c++ code..]'

    for cl in config.getgx().allclasses:
        for name in cl.vars:
            if name in cl.parent.vars and not name.startswith('__'):
                error("instance variable '%s' of class '%s' shadows class variable" % (name, cl.ident))

    mv = config.getgx().main_module.mv
    setmv(mv)

    config.getgx().merged_inh = merged(config.getgx().types, inheritance=True)
    virtual.analyze_virtuals()
    copy_.determine_classes()

    # --- add inheritance relationships for non-original Nodes (and temp_vars?); XXX register more, right solution?
    for func in config.getgx().allfuncs:
        if func in config.getgx().inheritance_relations:
            for inhfunc in config.getgx().inheritance_relations[func]:
                for a, b in zip(func.registered, inhfunc.registered):
                    graph.inherit_rec(a, b, func.mv)

                for a, b in zip(func.registered_temp_vars, inhfunc.registered_temp_vars):  # XXX more general
                    config.getgx().inheritance_temp_vars.setdefault(a, []).append(b)

    config.getgx().merged_inh = merged(config.getgx().types, inheritance=True)

    # error for dynamic expression without explicit type declaration
    for node in config.getgx().merged_inh:
        if isinstance(node, Node) and not isinstance(node, AssAttr) and not inode(node).mv.module.builtin:
            typestr.nodetypestr(node, inode(node).parent)

    return config.getgx()
