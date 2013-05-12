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
import sys
from compiler.ast import Const, Node, AssAttr, Keyword, CallFunc, Getattr, Dict, List, Tuple, ListComp, Not, Compare, Name

import error
import graph
from config import getgx
from copy_ import determine_classes
from python import StaticClass, lookup_class_module, default_var, Function, \
    Variable, lookup_var, Class, lookup_implementor, def_class
from typestr import nodetypestr
from virtual import analyze_virtuals


def nrargs(node):
    if inode(node).lambdawrapper:
        return inode(node).lambdawrapper.largs
    return len(node.args)


def hmcpa(func):
    got_one = 0
    for dcpa, cpas in func.cp.items():
        if len(cpas) > 1:
            return len(cpas)
        if len(cpas) == 1:
            got_one = 1
    return got_one


def get_types(expr, node, merge):
    types = set()
    if merge:
        if expr.node in merge:
            types = merge[expr.node]
    elif node:
        node = (expr.node, node.dcpa, node.cpa)
        if node in getgx().cnode:
            types = getgx().cnode[node].types()
    return types


def is_anon_callable(expr, node, merge=None):
    types = get_types(expr, node, merge)
    anon = bool([t for t in types if isinstance(t[0], Function)])
    call = bool([t for t in types if isinstance(t[0], Class) and '__call__' in t[0].funcs])
    return anon, call


def parent_func(thing):
    parent = inode(thing).parent
    while parent:
        if not isinstance(parent, Function) or not parent.listcomp:
            if not isinstance(parent, StaticClass):
                return parent
        parent = parent.parent


def analyze_args(expr, func, node=None, skip_defaults=False, merge=None):
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analyze_callfunc(expr, node, merge)

    args = []
    kwdict = {}
    for a in expr.args:
        if isinstance(a, Keyword):
            kwdict[a.name] = a.expr
        else:
            args.append(a)
    formal_args = func.formals[:]
    if func.node.varargs:
        formal_args = formal_args[:-1]
    default_start = len(formal_args) - len(func.defaults)

    if ident in ['__getattr__', '__setattr__']:  # property?
        args = args[1:]

    if (method_call or constructor) and not (parent_constr or anon_func):  # XXX
        args = [None] + args

    argnr = 0
    actuals, formals, defaults = [], [], []
    missing = False
    for i, formal in enumerate(formal_args):
        if formal in kwdict:
            actuals.append(kwdict[formal])
            formals.append(formal)
        elif formal.startswith('__kw_') and formal[5:] in kwdict:
            actuals.insert(0, kwdict[formal[5:]])
            formals.insert(0, formal)
        elif argnr < len(args) and not formal.startswith('__kw_'):
            actuals.append(args[argnr])
            argnr += 1
            formals.append(formal)
        elif i >= default_start:
            if not skip_defaults:
                default = func.defaults[i - default_start]
                if formal.startswith('__kw_'):
                    actuals.insert(0, default)
                    formals.insert(0, formal)
                else:
                    actuals.append(default)
                    formals.append(formal)
                defaults.append(default)
        else:
            missing = True
    extra = args[argnr:]

    _error = (missing or extra) and not func.node.varargs and not func.node.kwargs and not expr.star_args and func.lambdanr is None and expr not in getgx().lambdawrapper  # XXX

    if func.node.varargs:
        for arg in extra:
            actuals.append(arg)
            formals.append(func.formals[-1])

    return actuals, formals, defaults, extra, _error


def connect_actual_formal(expr, func, parent_constr=False, merge=None):
    pairs = []

    actuals = [a for a in expr.args if not isinstance(a, Keyword)]
    if isinstance(func.parent, Class):
        formals = [f for f in func.formals if f != 'self']
    else:
        formals = [f for f in func.formals]

    if parent_constr:
        actuals = actuals[1:]

    skip_defaults = False  # XXX investigate and further narrow down cases where we want to skip
    if (func.mv.module.ident in ['time', 'string', 'collections', 'bisect', 'array', 'math', 'cStringIO', 'getopt']) or \
       (func.mv.module.ident == 'random' and func.ident == 'randrange') or\
       (func.mv.module.ident == 'builtin' and func.ident not in ('sort', 'sorted', 'min', 'max', '__print')):
        skip_defaults = True

    actuals, formals, _, extra, _error = analyze_args(expr, func, skip_defaults=skip_defaults, merge=merge)

    for (actual, formal) in zip(actuals, formals):
        if not (isinstance(func.parent, Class) and formal == 'self'):
            pairs.append((actual, func.vars[formal]))
    return pairs, len(extra), _error


# --- return list of potential call targets
def callfunc_targets(node, merge):
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analyze_callfunc(node, merge=merge)
    funcs = []

    if node.node in merge and [t for t in merge[node.node] if isinstance(t[0], Function)]:  # anonymous function call
        funcs = [t[0] for t in merge[node.node] if isinstance(t[0], Function)]

    elif constructor:
        if ident in ('list', 'tuple', 'set', 'frozenset') and nrargs(node) == 1:
            funcs = [constructor.funcs['__inititer__']]
        elif (ident, nrargs(node)) in (('dict', 1), ('defaultdict', 2)):  # XXX merge infer.redirect
            funcs = [constructor.funcs['__initdict__']]  # XXX __inititer__?
        elif sys.platform == 'win32' and '__win32__init__' in constructor.funcs:
            funcs = [constructor.funcs['__win32__init__']]
        elif '__init__' in constructor.funcs:
            funcs = [constructor.funcs['__init__']]

    elif parent_constr:
        if ident != '__init__':
            cl = inode(node).parent.parent
            funcs = [cl.funcs[ident]]

    elif direct_call:
        funcs = [direct_call]

    elif method_call:
        classes = set(t[0] for t in merge[objexpr] if isinstance(t[0], Class))
        funcs = [cl.funcs[ident] for cl in classes if ident in cl.funcs]

    return funcs


# --- analyze call expression: namespace, method call, direct call/constructor..
def analyze_callfunc(node, node2=None, merge=None):  # XXX generate target list XXX uniform Variable system! XXX node2, merge?
    # print 'analyze callnode', node, inode(node).parent
    cnode = inode(node)
    mv = cnode.mv
    namespace, objexpr, method_call, parent_constr = mv.module, None, False, False
    constructor, direct_call, ident = None, None, None

    # anon func call XXX refactor as __call__ method call below
    anon_func, is_callable = is_anon_callable(node, node2, merge)
    if is_callable:
        method_call, objexpr, ident = True, node.node, '__call__'
        return objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func

    # method call
    if isinstance(node.node, Getattr):
        objexpr, ident = node.node.expr, node.node.attrname
        cl, module = lookup_class_module(objexpr, mv, cnode.parent)

        if cl:
            # staticmethod call
            if ident in cl.staticmethods:
                direct_call = cl.funcs[ident]
                return objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func

            # ancestor call
            elif ident not in ['__setattr__', '__getattr__'] and cnode.parent:
                thiscl = cnode.parent.parent
                if isinstance(thiscl, Class) and cl.ident in (x.ident for x in thiscl.ancestors_upto(None)):  # XXX
                    if lookup_implementor(cl, ident):
                        parent_constr = True
                        ident = ident + lookup_implementor(cl, ident) + '__'  # XXX change data structure
                        return objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func

        if module:  # XXX elif?
            namespace, objexpr = module, None
        else:
            method_call = True

    elif isinstance(node.node, Name):
        ident = node.node.name

    # direct [constructor] call
    if isinstance(node.node, Name) or namespace != mv.module:
        if isinstance(node.node, Name):
            if lookup_var(ident, cnode.parent, mv=mv):
                return objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func
        if ident in namespace.mv.classes:
            constructor = namespace.mv.classes[ident]
        elif ident in namespace.mv.funcs:
            direct_call = namespace.mv.funcs[ident]
        elif ident in namespace.mv.ext_classes:
            constructor = namespace.mv.ext_classes[ident]
        elif ident in namespace.mv.ext_funcs:
            direct_call = namespace.mv.ext_funcs[ident]
        else:
            if namespace != mv.module:
                return objexpr, ident, None, False, None, False, False

    return objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func


# --- merge constraint network along combination of given dimensions (dcpa, cpa, inheritance)
# e.g. for annotation we merge everything; for code generation, we might want to create specialized code
def merged(nodes, inheritance=False):
    ggx = getgx()
    merge = {}
    if inheritance:  # XXX do we really need this crap
        mergeinh = merged([n for n in nodes if n.thing in ggx.inherited])
        mergenoinh = merged([n for n in nodes if not n.thing in ggx.inherited])

    for node in nodes:
        # --- merge node types
        sortdefault = merge.setdefault(node.thing, set())
        sortdefault.update(ggx.types[node])

        # --- merge inheritance nodes
        if inheritance:
            inh = ggx.inheritance_relations.get(node.thing, [])

            # merge function variables with their inherited versions (we don't customize!)
            if isinstance(node.thing, Variable) and isinstance(node.thing.parent, Function):
                var = node.thing
                for inhfunc in ggx.inheritance_relations.get(var.parent, []):
                    if var.name in inhfunc.vars:
                        if inhfunc.vars[var.name] in mergenoinh:
                            sortdefault.update(mergenoinh[inhfunc.vars[var.name]])
                for inhvar in ggx.inheritance_temp_vars.get(var, []):  # XXX more general
                    if inhvar in mergenoinh:
                        sortdefault.update(mergenoinh[inhvar])

            # node is not a function variable
            else:
                for n in inh:
                    if n in mergeinh:  # XXX ook mergenoinh?
                        sortdefault.update(mergeinh[n])
    return merge


def inode(node):
    return getgx().cnode[node, 0, 0]


def add_constraint(a, b, worklist=None):
    getgx().constraints.add((a, b))
    in_out(a, b)
    add_to_worklist(worklist, a)


def in_out(a, b):
    a.out.add(b)
    b.in_.add(a)


def add_to_worklist(worklist, node):  # XXX to infer.py
    if worklist is not None and not node.in_list:
        worklist.append(node)
        node.in_list = 1


class CNode:
    __slots__ = ['thing', 'dcpa', 'cpa', 'fakefunc', 'parent', 'defnodes', 'mv', 'constructor', 'copymetoo', 'fakert', 'in_', 'out', 'fout', 'in_list', 'callfuncs', 'nodecp']

    def __init__(self, thing, dcpa=0, cpa=0, parent=None):
        self.thing = thing
        self.dcpa = dcpa
        self.cpa = cpa
        self.fakefunc = None
        if isinstance(parent, Class):  # XXX
            parent = None
        self.parent = parent
        self.defnodes = False  # if callnode, notification nodes were made for default arguments
        self.mv = graph.getmv()
        self.constructor = False  # allocation site
        self.copymetoo = False
        self.fakert = False
        self.lambdawrapper = None

        getgx().cnode[self.thing, self.dcpa, self.cpa] = self

        # --- in, outgoing constraints

        self.in_ = set()        # incoming nodes
        self.out = set()        # outgoing nodes
        self.fout = set()       # unreal outgoing edges, used in ifa

        # --- iterative dataflow analysis

        self.in_list = 0        # node in work-list
        self.callfuncs = []    # callfuncs to which node is object/argument

        self.nodecp = set()        # already analyzed cp's # XXX kill!?

        # --- add node to surrounding non-listcomp function
        if parent:  # do this only once! (not when copying)
            while parent and isinstance(parent, Function) and parent.listcomp:
                parent = parent.parent
            if isinstance(parent, Function):
                if self not in parent.nodes:
                    parent.nodes.add(self)
                    parent.nodes_ordered.append(self)

    def copy(self, dcpa, cpa, worklist=None):  # XXX to infer.py
        # if not self.mv.module.builtin: print 'copy', self

        if (self.thing, dcpa, cpa) in getgx().cnode:
            return getgx().cnode[self.thing, dcpa, cpa]

        newnode = CNode(self.thing, dcpa, cpa)

        newnode.callfuncs = self.callfuncs[:]  # XXX no copy?
        newnode.constructor = self.constructor
        newnode.copymetoo = self.copymetoo
        newnode.parent = self.parent
        newnode.mv = self.mv

        add_to_worklist(worklist, newnode)

        if self.constructor or self.copymetoo or isinstance(self.thing, (Not, Compare)):  # XXX XXX
            getgx().types[newnode] = getgx().types[self].copy()
        else:
            getgx().types[newnode] = set()
        return newnode

    def types(self):
        if self in getgx().types:
            return getgx().types[self]
        else:
            return set()  # XXX

    def __repr__(self):
        return repr((self.thing, self.dcpa, self.cpa))


INCREMENTAL = True
INCREMENTAL_FUNCS = 5
INCREMENTAL_DATA = True
INCREMENTAL_ALLOCS = 20
MAXITERS = 30
CPA_LIMIT = 10


def DEBUG(level):
    return getgx().debug_level >= level


def class_copy(cl, dcpa):
    for var in cl.vars.values():  # XXX
        if not inode(var) in getgx().types:
            continue  # XXX research later

        inode(var).copy(dcpa, 0)
        getgx().types[getgx().cnode[var, dcpa, 0]] = inode(var).types().copy()

        for n in inode(var).in_:  # XXX
            if isinstance(n.thing, Const):
                add_constraint(n, getgx().cnode[var, dcpa, 0])

    for func in cl.funcs.values():
        if cl.mv.module.ident == 'builtin' and cl.ident != '__iter' and func.ident == '__iter__':  # XXX hack for __iter__:__iter()
            itercl = def_class('__iter')
            getgx().alloc_info[func.ident, ((cl, dcpa),), func.returnexpr[0]] = (itercl, itercl.dcpa)
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
    print_typeset(getgx().types)


def print_constraints():
    # print 'constraints:'
    l = list(getgx().constraints)
    l.sort(lambda x, y: cmp(repr(x[0]), repr(y[0])))
    for (a, b) in l:
        if not (a.mv.module.builtin and b.mv.module.builtin):
            print a, '->', b
            if not a in getgx().types or not b in getgx().types:
                print 'NOTYPE', a in getgx().types, b in getgx().types
    print

# --- iterative dataflow analysis


def propagate():
    if DEBUG(1):
        print 'propagate'
    ggx = getgx()

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
                if isinstance(b.thing, Variable) and isinstance(b.thing.parent, Class):
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
        types = getgx().cnode[expr.node, node.dcpa, node.cpa].types()
        types = [t for t in types if isinstance(t[0], Function)]  # XXX XXX analyse per t, sometimes class, sometimes function..

        if list(types)[0][0].parent:  # method reference XXX merge below?
            funcs = [(f[0], f[1], (f[0].parent, f[1])) for f in types]  # node.dcpa: connect to right dcpa duplicate version
        else:  # function reference
            funcs = [(f[0], f[1], None) for f in types]  # function call: only one version; no objtype

    elif constructor:
        funcs = [(t[0].funcs['__init__'], t[1], t) for t in node.types() if '__init__' in t[0].funcs]

    elif parent_constr:
        objtypes = getgx().cnode[lookup_var('self', node.parent), node.dcpa, node.cpa].types()
        funcs = [(t[0].funcs[ident], t[1], None) for t in objtypes if ident in t[0].funcs]

    elif direct_call:
        funcs = [(direct_call, 0, None)]

    elif method_call:
        objtypes = getgx().cnode[objexpr, node.dcpa, node.cpa].types()
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
                getgx().types[defnode] = set()
                defnode.callfuncs.append(node.thing)
                add_constraint(getgx().cnode[default, 0, 0], defnode, worklist)  # XXX bad place
        node.defnodes = True

        for act, form in zip(actuals, formals):
            if parent_constr or not (isinstance(func.parent, Class) and form == 'self'):  # XXX merge
                args.append(act)

    argtypes = []
    for arg in args:
        if (arg, node.dcpa, node.cpa) in getgx().cnode:
            argtypes.append(getgx().cnode[arg, node.dcpa, node.cpa].types())
        else:
            argtypes.append(inode(arg).types())  # XXX def arg?

    # store arg count for wrappers to builtin refs
    if funcs and (func.lambdawrapper or node.thing in getgx().lambdawrapper):
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
        if isinstance(func.parent, Class):
            funcs = func.parent.funcs
        else:
            funcs = func.mv.funcs
        redir = '__%s%d' % (func.ident, len([kwarg for kwarg in callfunc.args if not isinstance(kwarg, Keyword)]))
        func = funcs.get(redir, func)

    # filter
    if direct_call and ident == 'filter':
        clnames = [x[0].ident for x in c if isinstance(x[0], Class)]
        if 'str_' in clnames or 'tuple' in clnames or 'tuple2' in clnames:
            func = func.mv.funcs['__' + ident]

    # staticmethod
    if isinstance(func.parent, Class) and func.ident in func.parent.staticmethods:
        dcpa = 1

    # dict.__init__
    if constructor and (ident, nrargs(callfunc)) in (('dict', 1), ('defaultdict', 2)):
        clnames = [x[0].ident for x in c if isinstance(x[0], Class)]
        if 'dict' in clnames or 'defaultdict' in clnames:
            func = list(callnode.types())[0][0].funcs['__initdict__']
        else:
            func = list(callnode.types())[0][0].funcs['__inititer__']

    # dict.update
    if func.ident == 'update' and isinstance(func.parent, Class) and func.parent.ident in ('dict', 'defaultdict'):
        clnames = [x[0].ident for x in c if isinstance(x[0], Class)]
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
        if isinstance(func.parent, Class) and callfunc.args and callfunc.args[0].value in func.parent.properties:
            arg = callfunc.args[0].value
            if callfunc.node.attrname == '__setattr__':
                func = func.parent.funcs[func.parent.properties[arg][1]]
            else:
                func = func.parent.funcs[func.parent.properties[arg][0]]
            c = c[1:]

    # win32
    if sys.platform == 'win32' and func.mv.module.builtin and isinstance(func.parent, Class) and '__win32' + func.ident in func.parent.funcs:
        func = func.parent.funcs['__win32' + func.ident]

    return c, dcpa, func

# --- cartesian product algorithm; adds interprocedural constraints


def cpa(callnode, worklist):
    analysis = analyze_callfunc(callnode.thing, callnode)
    cp = cartesian_product(callnode, analysis, worklist)
    if not cp:
        return
    if len(cp) > getgx().cpa_limit and not getgx().cpa_clean:
        getgx().cpa_limited = True
        return []
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analysis

    # --- iterate over argument type combinations
    for c in cp:
        (func, dcpa, objtype), c = c[0], c[1:]

        if INCREMENTAL:
            if not func.mv.module.builtin and func not in getgx().added_funcs_set and not func.ident in ['__getattr__', '__setattr__']:
                if INCREMENTAL_DATA:
                    if getgx().added_allocs >= INCREMENTAL_ALLOCS:
                        continue
                else:
                    if getgx().added_funcs >= INCREMENTAL_FUNCS:
                        continue
                getgx().added_funcs += 1
                getgx().added_funcs_set.add(func)
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
            retnode = getgx().cnode[func.retnode.thing, dcpa, cpa]
            add_constraint(retnode, callnode, worklist)


def connect_getsetattr(func, callnode, callfunc, dcpa, worklist):
    if (isinstance(callfunc.node, Getattr) and callfunc.node.attrname in ['__setattr__', '__getattr__'] and
            not (isinstance(func.parent, Class) and callfunc.args and callfunc.args[0].value in func.parent.properties)):
        varname = callfunc.args[0].value
        parent = func.parent

        var = default_var(varname, parent, worklist)  # XXX always make new var??
        inode(var).copy(dcpa, 0, worklist)

        if not getgx().cnode[var, dcpa, 0] in getgx().types:
            getgx().types[getgx().cnode[var, dcpa, 0]] = set()

        getgx().cnode[var, dcpa, 0].mv = parent.module.mv  # XXX move into default_var

        if callfunc.node.attrname == '__setattr__':
            add_constraint(getgx().cnode[callfunc.args[1], callnode.dcpa, callnode.cpa], getgx().cnode[var, dcpa, 0], worklist)
        else:
            add_constraint(getgx().cnode[var, dcpa, 0], callnode, worklist)
        return True
    return False


def create_template(func, dcpa, c, worklist):
    # --- unseen cartesian product: create new template
    if not dcpa in func.cp:
        func.cp[dcpa] = {}
    func.cp[dcpa][c] = cpa = len(func.cp[dcpa])  # XXX +1

    if DEBUG(2) and not func.mv.module.builtin and not func.ident in ['__getattr__', '__setattr__']:
        print 'template', (func, dcpa), c

    getgx().templates += 1
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
        formalnode = getgx().cnode[func.vars[formal], dcpa, cpa]

        if formaltype[1] != 0:  # ifa: remember dataflow information for non-simple types
            if actual is None:
                if constructor:
                    objexpr = node.thing

                if method_call or constructor:
                    formalnode.in_.add(getgx().cnode[objexpr, node.dcpa, node.cpa])
            else:
                if actual in func.defaults:
                    formalnode.in_.add(getgx().cnode[actual, 0, 0])
                else:
                    formalnode.in_.add(getgx().cnode[actual, node.dcpa, node.cpa])

        getgx().types[formalnode].add(formaltype)
        add_to_worklist(worklist, formalnode)

# --- iterative flow analysis: after each iteration, detect imprecisions, and split involved contours


def ifa():
    if DEBUG(1):
        print 'ifa'
    split = []  # [(set of creation nodes, new type number), ..]

    allcsites = {}
    for n, types in getgx().types.iteritems():
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
        if not (var, dcpa, 0) in getgx().cnode:
            continue
        node = getgx().cnode[var, dcpa, 0]
        creation_points, paths, assignsets, allnodes, csites, emptycsites = ifa_flow_graph(cl, dcpa, node, allcsites)
        if DEBUG(3):
            print 'IFA visit var %s.%s, %d, csites %d' % (cl.ident, var.name, dcpa, len(csites))
        if len(csites) + len(emptycsites) == 1:
            continue
        if ((len(merge_simple_types(getgx().types[node])) > 1 and len(assignsets) > 1) or
                (assignsets and emptycsites)):  # XXX move to split_no_conf
            ifa_split_no_confusion(cl, dcpa, varnum, classes_nr, nr_classes, csites, emptycsites, allnodes, split)
        if split:
            break
        for node in allnodes:
            if not ifa_confluence_point(node, creation_points):
                continue
            if not node.thing.formal_arg and not isinstance(node.thing.parent, Class):
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
            if (var, dcpa, 0) in getgx().cnode:
                attr_types.append(merge_simple_types(getgx().cnode[var, dcpa, 0].types()))
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
        for cl in getgx().allclasses:
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
        types = getgx().types[a]
        if types:
            if a.thing in getgx().assign_target:  # XXX *args
                target = getgx().cnode[getgx().assign_target[a.thing], a.dcpa, a.cpa]
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
    if not getgx().silent:
        print '\r%s%d%%' % (int(perc * 32) * '*', 100 * perc),
        if DEBUG(1):
            print
        else:
            sys.stdout.flush()

# --- cartesian product algorithm (cpa) & iterative flow analysis (ifa)


def iterative_dataflow_analysis():
    if not getgx().silent:
        print '[analyzing types..]'
    backup = backup_network()

    getgx().orig_types = {}
    for n, t in getgx().types.iteritems():
        getgx().orig_types[n] = t

    if INCREMENTAL:
        update_progressbar(0)

    getgx().added_funcs = INCREMENTAL_FUNCS  # analyze root of callgraph in first round
    getgx().added_funcs_set = set()
    getgx().added_allocs = 0
    getgx().added_allocs_set = set()
    getgx().cpa_limit = CPA_LIMIT
    getgx().cpa_clean = False

    while True:
        getgx().iterations += 1
        getgx().total_iterations += 1
        maxiter = (getgx().iterations == MAXITERS)
        if DEBUG(1):
            print '\n*** iteration %d ***' % getgx().iterations

        # --- propagate using cartesian product algorithm
        getgx().new_alloc_info = {}
#        print 'table'
#        print '\n'.join([repr(e)+': '+repr(l) for e,l in getgx().alloc_info.items()])
        getgx().cpa_limited = False
        propagate()
        getgx().alloc_info = getgx().new_alloc_info

        if getgx().cpa_limited:
            if DEBUG(1):
                print 'CPA limit %d reached!' % getgx().cpa_limit
        else:
            getgx().cpa_clean = True

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
                allfuncs = len([f for f in getgx().allfuncs if not f.mv.module.builtin and not [start for start in ('__iadd__', '__imul__', '__str__', '__hash__') if f.ident.startswith(start)]])
                perc = 1.0
                if allfuncs:
                    perc = min(len(getgx().added_funcs_set) / float(allfuncs), 1.0)
                update_progressbar(perc)
            if maxiter:
                print '\n*WARNING* reached maximum number of iterations'
                getgx().maxhits += 1
                if getgx().maxhits == 3:
                    return

            getgx().cpa_clean = False
            if INCREMENTAL and (getgx().added_funcs or getgx().added_allocs):
                getgx().added_funcs = 0
                getgx().added_allocs = 0
                getgx().iterations = 0
            elif getgx().cpa_limited:
                getgx().cpa_limit *= 2
                getgx().iterations = 0
            else:
                if INCREMENTAL:
                    update_progressbar(1.0)
                if DEBUG(1):
                    print '\niterations:', getgx().total_iterations, 'templates:', getgx().templates
                elif not getgx().silent:
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
                                if parent.parent and isinstance(parent.parent, Class):  # self
                                    cart = ((parent.parent, n.dcpa),) + cart

                                getgx().alloc_info[parent.ident, cart, n.thing] = (cl, newnr)
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
        if isinstance(func.parent, Class):  # self
            cart = ((func.parent, dcpa),) + cart

        added = getgx().added_allocs_set
        added_new = 0

        for node in func.nodes_ordered:
            if node.constructor and isinstance(node.thing, (List, Dict, Tuple, ListComp, CallFunc)):
                if node.thing not in added:
                    if INCREMENTAL_DATA and not func.mv.module.builtin:
                        if getgx().added_allocs >= INCREMENTAL_ALLOCS:
                            continue
                        added_new += 1
                        getgx().added_allocs += 1
                    added.add(node.thing)

                # --- contour is specified in alloc_info
                parent = node.parent
                while isinstance(parent.parent, Function):
                    parent = parent.parent

                alloc_id = (parent.ident, cart, node.thing)  # XXX ident?
                alloc_node = getgx().cnode[node.thing, dcpa, cpa]

                if alloc_id in getgx().alloc_info:
                    pass
#                    print 'specified' # print 'specified', func.ident, cart, alloc_node, alloc_node.callfuncs, getgx().alloc_info[alloc_id]
                # --- contour is newly split: copy allocation type for 'mother' contour; modify alloc_info
                else:
                    mother_alloc_id = alloc_id

                    for (id, c, thing) in getgx().alloc_info:
                        if id == parent.ident and thing is node.thing:
                            for a, b in zip(cart, c):
                                if a != b and not (isinstance(a[0], Class) and a[0] is b[0] and a[1] in a[0].splits and a[0].splits[a[1]] == b[1]):
                                    break
                            else:
                                mother_alloc_id = (id, c, thing)
                                break

                    # print 'not specified.. mother id:', mother_alloc_id
                    if mother_alloc_id in getgx().alloc_info:
                        getgx().alloc_info[alloc_id] = getgx().alloc_info[mother_alloc_id]
                        # print 'mothered', alloc_node, getgx().alloc_info[mother_alloc_id]
                    elif getgx().orig_types[node]:  # empty constructors that do not flow to assignments have no type
                        # print 'no mother', func.ident, cart, mother_alloc_id, alloc_node, getgx().types[node]
                        getgx().alloc_info[alloc_id] = list(getgx().orig_types[node])[0]
                    else:
                        # print 'oh boy'
                        for (id, c, thing) in getgx().alloc_info:  # XXX vhy?
                            if id == parent.ident and thing is node.thing:
                                mother_alloc_id = (id, c, thing)
                                getgx().alloc_info[alloc_id] = getgx().alloc_info[mother_alloc_id]
                                break

                if alloc_id in getgx().alloc_info:
                    getgx().new_alloc_info[alloc_id] = getgx().alloc_info[alloc_id]
                    getgx().types[alloc_node] = set()
                    # print 'seeding..', alloc_node, getgx().alloc_info[alloc_id], alloc_node.thing in getgx().empty_constructors
                    getgx().types[alloc_node].add(getgx().alloc_info[alloc_id])
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
                if t in getgx().types[incoming]:
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
    for node, typeset in getgx().types.items():
        beforetypes[node] = typeset.copy()

    beforeconstr = getgx().constraints.copy()

    beforeinout = {}
    for node in getgx().types:
        beforeinout[node] = (node.in_.copy(), node.out.copy())

    beforecnode = getgx().cnode.copy()

    return (beforetypes, beforeconstr, beforeinout, beforecnode)

# --- restore constraint network, introducing new types


def restore_network(backup):
    beforetypes, beforeconstr, beforeinout, beforecnode = backup

    getgx().types = {}
    for node, typeset in beforetypes.items():
        getgx().types[node] = typeset.copy()

    getgx().constraints = beforeconstr.copy()
    getgx().cnode = beforecnode.copy()

    for node, typeset in getgx().types.items():
        node.nodecp = set()
        node.defnodes = False
        befinout = beforeinout[node]
        node.in_, node.out = befinout[0].copy(), befinout[1].copy()
        node.fout = set()  # XXX ?

    for var in getgx().allvars:  # XXX we have to restore some variable constraint nodes.. remove vars?
        if not (var, 0, 0) in getgx().cnode:
            CNode(var, parent=var.parent)

    for func in getgx().allfuncs:
        func.cp = {}


def merge_simple_types(types):
    merge = types.copy()
    if len(types) > 1 and (def_class('none'), 0) in types:
        if not (def_class('int_'), 0) in types and not (def_class('float_'), 0) in types and not (def_class('bool_'), 0) in types:
            merge.remove((def_class('none'), 0))

    return frozenset(merge)


def analyze(module_name):
    mv = None
    graph.setmv(mv)

    # --- build dataflow graph from source code
    getgx().main_module = graph.parse_module(module_name)
    mv = getgx().main_module.mv
    graph.setmv(mv)

    # --- seed class_.__name__ attributes..
    for cl in getgx().allclasses:
        if cl.ident == 'class_':
            var = default_var('__name__', cl)
            getgx().types[inode(var)] = set([(def_class('str_'), 0)])

    # --- non-ifa: copy classes for each allocation site
    for cl in getgx().allclasses:
        if cl.ident in ['int_', 'float_', 'none', 'class_', 'str_', 'bool_']:
            continue
        if cl.ident == 'list':
            cl.dcpa = len(getgx().list_types) + 2
        elif cl.ident != '__iter':  # XXX huh
            cl.dcpa = 2

        for dcpa in range(1, cl.dcpa):
            class_copy(cl, dcpa)

    var = default_var('unit', def_class('str_'))
    getgx().types[inode(var)] = set([(def_class('str_'), 0)])

    # --- cartesian product algorithm & iterative flow analysis
    iterative_dataflow_analysis()

    if not getgx().silent:
        print '[generating c++ code..]'

    for cl in getgx().allclasses:
        for name in cl.vars:
            if name in cl.parent.vars and not name.startswith('__'):
                error.error("instance variable '%s' of class '%s' shadows class variable" % (name, cl.ident))

    mv = getgx().main_module.mv
    graph.setmv(mv)

    getgx().merged_inh = merged(getgx().types, inheritance=True)
    analyze_virtuals()
    determine_classes()

    # --- add inheritance relationships for non-original Nodes (and temp_vars?); XXX register more, right solution?
    for func in getgx().allfuncs:
        if func in getgx().inheritance_relations:
            for inhfunc in getgx().inheritance_relations[func]:
                for a, b in zip(func.registered, inhfunc.registered):
                    graph.inherit_rec(a, b, func.mv)

                for a, b in zip(func.registered_temp_vars, inhfunc.registered_temp_vars):  # XXX more general
                    getgx().inheritance_temp_vars.setdefault(a, []).append(b)

    getgx().merged_inh = merged(getgx().types, inheritance=True)

    # error for dynamic expression without explicit type declaration
    for node in getgx().merged_inh:
        if isinstance(node, Node) and not isinstance(node, AssAttr) and not inode(node).mv.module.builtin:
            nodetypestr(node, inode(node).parent)

    return getgx()
