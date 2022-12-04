'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

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
    -all the while maintaining types for each allocation point in gx.alloc_info

update: we now analyze programs incrementally, adding several functions and redoing the full analysis each time. this seems to greatly help the CPA from exploding early on.

'''
import ast
import itertools
import logging
import random
import sys

from . import ast_utils 
from . import error
from . import python

logger = logging.getLogger('infer')
ifa_logger = logging.getLogger('infer.ifa')


INCREMENTAL = True
INCREMENTAL_FUNCS = 5
INCREMENTAL_DATA = True
INCREMENTAL_ALLOCS = 20
MAXITERS = 30
CPA_LIMIT = 10


class CNode:
    __slots__ = ['gx', 'thing', 'dcpa', 'cpa', 'fakefunc', 'parent', 'defnodes', 'mv', 'constructor', 'copymetoo', 'fakert', 'lambdawrapper', 'in_', 'out', 'fout', 'in_list', 'callfuncs', 'nodecp', 'paths', 'csites', 'assignhop', 'temp1', 'temp2', 'subs']

    def __init__(self, gx, thing, dcpa=0, cpa=0, parent=None, mv=None):
        self.gx = gx
        self.thing = thing
        self.dcpa = dcpa
        self.cpa = cpa
        self.fakefunc = None
        if isinstance(parent, python.Class):  # XXX
            parent = None
        self.parent = parent
        self.defnodes = False  # if callnode, notification nodes were made for default arguments
        self.mv = mv
        self.constructor = False  # allocation site
        self.copymetoo = False
        self.fakert = False
        self.lambdawrapper = None

        self.gx.cnode[self.thing, self.dcpa, self.cpa] = self

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
            while parent and isinstance(parent, python.Function) and parent.listcomp:
                parent = parent.parent
            if isinstance(parent, python.Function):
                if self not in parent.nodes:
                    parent.nodes.add(self)
                    parent.nodes_ordered.append(self)

    def copy(self, dcpa, cpa, worklist=None):  # XXX to infer.py
        # if not self.mv.module.builtin: print 'copy', self

        if (self.thing, dcpa, cpa) in self.gx.cnode:
            return self.gx.cnode[self.thing, dcpa, cpa]

        newnode = CNode(self.gx, self.thing, dcpa, cpa, mv=self.mv)

        newnode.callfuncs = self.callfuncs[:]  # XXX no copy?
        newnode.constructor = self.constructor
        newnode.copymetoo = self.copymetoo
        newnode.parent = self.parent

        add_to_worklist(worklist, newnode)

        if self.constructor or self.copymetoo or isinstance(self.thing, (ast.Not, ast.Compare)):  # XXX XXX
            self.gx.types[newnode] = self.gx.types[self].copy()
        else:
            self.gx.types[newnode] = set()
        return newnode

    def types(self):
        if self in self.gx.types:
            return self.gx.types[self]
        else:
            return set()  # XXX

    def __repr__(self):
        return repr((self.thing, self.dcpa, self.cpa))


def DEBUG(gx, level):
    return gx.debug_level >= level


def nrargs(gx, node):
    if inode(gx, node).lambdawrapper:
        return inode(gx, node).lambdawrapper.largs
    return len(node.args)


def called(func):
    return bool([cpas for cpas in func.cp.values() if cpas])


def get_types(gx, expr, node, merge):
    types = set()
    if merge:
        if expr.func in merge:
            types = merge[expr.func]
    elif node:
        node = (expr.func, node.dcpa, node.cpa)
        if node in gx.cnode:
            types = gx.cnode[node].types()
    return types


def is_anon_callable(gx, expr, node, merge=None):
    types = get_types(gx, expr, node, merge)
    anon = bool([t for t in types if isinstance(t[0], python.Function)])
    call = bool([t for t in types if isinstance(t[0], python.Class) and '__call__' in t[0].funcs])
    return anon, call


def parent_func(gx, thing):
    parent = inode(gx, thing).parent
    while parent:
        if not isinstance(parent, python.Function) or not parent.listcomp:
            if not isinstance(parent, python.StaticClass):
                return parent
        parent = parent.parent


def analyze_args(gx, expr, func, node=None, skip_defaults=False, merge=None):
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analyze_callfunc(gx, expr, node, merge)

    args = []
    kwdict = {}
    for a in expr.args:
        args.append(a)
    for a in expr.keywords:
        kwdict[a.arg] = a.value
    formal_args = func.formals[:]
    if func.node.args.vararg:
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

    _error = (missing or extra) and not func.node.args.vararg and not func.node.args.kwarg and not ast_utils.get_starargs(expr) and func.lambdanr is None and expr not in gx.lambdawrapper  # XXX

    if func.node.args.vararg:
        for arg in extra:
            actuals.append(arg)
            formals.append(func.formals[-1])

    return actuals, formals, defaults, extra, _error


def connect_actual_formal(gx, expr, func, parent_constr=False, merge=None):
    pairs = []

    actuals = [a for a in expr.args if not isinstance(a, ast.keyword)]
    if isinstance(func.parent, python.Class):
        formals = [f for f in func.formals if f != 'self']
    else:
        formals = [f for f in func.formals]

    if parent_constr:
        actuals = actuals[1:]

    skip_defaults = False  # XXX investigate and further narrow down cases where we want to skip
    if (func.mv.module.ident in ['time', 'string', 'collections', 'bisect', 'array', 'math', 'cStringIO', 'getopt']) or \
       (func.mv.module.ident == 'random' and func.ident == 'randrange') or \
       (func.mv.module.ident == 'builtin' and func.ident not in ('sort', 'sorted', 'min', 'max', '__print')):
        skip_defaults = True

    actuals, formals, _, extra, _error = analyze_args(gx, expr, func, skip_defaults=skip_defaults, merge=merge)

    for (actual, formal) in zip(actuals, formals):
        if not (isinstance(func.parent, python.Class) and formal == 'self'):
            pairs.append((actual, func.vars[formal]))
    return pairs, len(extra), _error


# --- return list of potential call targets
def callfunc_targets(gx, node, merge):
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analyze_callfunc(gx, node, merge=merge)
    funcs = []

    if node.func in merge and [t for t in merge[node.func] if isinstance(t[0], python.Function)]:  # anonymous function call
        funcs = [t[0] for t in merge[node.func] if isinstance(t[0], python.Function)]

    elif constructor:
        if ident in ('list', 'tuple', 'set', 'frozenset') and nrargs(gx, node) == 1:
            funcs = [constructor.funcs['__inititer__']]
        elif (ident, nrargs(gx, node)) in (('dict', 1), ('defaultdict', 2)):  # XXX merge infer.redirect
            funcs = [constructor.funcs['__initdict__']]  # XXX __inititer__?
        elif sys.platform == 'win32' and '__win32__init__' in constructor.funcs:
            funcs = [constructor.funcs['__win32__init__']]
        elif '__init__' in constructor.funcs:
            funcs = [constructor.funcs['__init__']]

    elif parent_constr:
        if ident != '__init__':
            cl = inode(gx, node).parent.parent
            funcs = [cl.funcs[ident]]

    elif direct_call:
        funcs = [direct_call]

    elif method_call:
        classes = set(t[0] for t in merge[objexpr] if isinstance(t[0], python.Class))
        funcs = [cl.funcs[ident] for cl in classes if ident in cl.funcs]

    return funcs


# --- analyze call expression: namespace, method call, direct call/constructor..
def analyze_callfunc(gx, node, node2=None, merge=None):  # XXX generate target list XXX uniform python.Variable system! XXX node2, merge?
    # print 'analyze callnode', ast.dump(node), inode(gx, node).parent
    cnode = inode(gx, node)
    mv = cnode.mv
    namespace, objexpr, method_call, parent_constr = mv.module, None, False, False
    constructor, direct_call, ident = None, None, None

    # anon func call XXX refactor as __call__ method call below
    anon_func, is_callable = is_anon_callable(gx, node, node2, merge)
    if is_callable:
        method_call, objexpr, ident = True, node.func, '__call__'
        return objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func

    # method call
    if isinstance(node.func, ast.Attribute):
        objexpr, ident = node.func.value, node.func.attr
        cl, module = python.lookup_class_module(objexpr, mv, cnode.parent)

        if cl:
            # staticmethod call
            if ident in cl.staticmethods:
                direct_call = cl.funcs[ident]
                return objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func

            # ancestor call
            elif ident not in ['__setattr__', '__getattr__'] and cnode.parent:
                thiscl = cnode.parent.parent
                if isinstance(thiscl, python.Class) and cl.ident in (x.ident for x in thiscl.ancestors_upto(None)):  # XXX
                    if python.lookup_implementor(cl, ident):
                        parent_constr = True
                        ident = ident + python.lookup_implementor(cl, ident) + '__'  # XXX change data structure
                        return objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func

        if module:  # XXX elif?
            namespace, objexpr = module, None
        else:
            method_call = True

    elif isinstance(node.func, ast.Name):
        ident = node.func.id

    # direct [constructor] call
    if isinstance(node.func, ast.Name) or namespace != mv.module:
        if isinstance(node.func, ast.Name):
            if python.lookup_var(ident, cnode.parent, mv=mv):
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
def merged(gx, nodes, inheritance=False):
    merge = {}
    if inheritance:  # XXX do we really need this crap
        mergeinh = merged(gx, [n for n in nodes if n.thing in gx.inherited])
        mergenoinh = merged(gx, [n for n in nodes if not n.thing in gx.inherited])

    for node in nodes:
        # --- merge node types
        sortdefault = merge.setdefault(node.thing, set())
        sortdefault.update(gx.types[node])

        # --- merge inheritance nodes
        if inheritance:
            inh = gx.inheritance_relations.get(node.thing, [])

            # merge function variables with their inherited versions (we don't customize!)
            if isinstance(node.thing, python.Variable) and isinstance(node.thing.parent, python.Function):
                var = node.thing
                for inhfunc in gx.inheritance_relations.get(var.parent, []):
                    if var.name in inhfunc.vars:
                        if inhfunc.vars[var.name] in mergenoinh:
                            sortdefault.update(mergenoinh[inhfunc.vars[var.name]])
                for inhvar in gx.inheritance_temp_vars.get(var, []):  # XXX more general
                    if inhvar in mergenoinh:
                        sortdefault.update(mergenoinh[inhvar])

            # node is not a function variable
            else:
                for n in inh:
                    if n in mergeinh:  # XXX ook mergenoinh?
                        sortdefault.update(mergeinh[n])
    return merge


def inode(gx, node):
    return gx.cnode[node, 0, 0]


def add_constraint(gx, a, b, worklist=None):
    gx.constraints.add((a, b))
    in_out(a, b)
    add_to_worklist(worklist, a)


def in_out(a, b):
    a.out.add(b)
    b.in_.add(a)


def add_to_worklist(worklist, node):  # XXX to infer.py
    if worklist is not None and not node.in_list:
        worklist.append(node)
        node.in_list = 1


def class_copy(gx, cl, dcpa):
    for var in cl.vars.values():  # XXX
        if not inode(gx, var) in gx.types:
            continue  # XXX research later

        inode(gx, var).copy(dcpa, 0)
        gx.types[gx.cnode[var, dcpa, 0]] = inode(gx, var).types().copy()

        for n in inode(gx, var).in_:  # XXX
            if isinstance(n.thing, (ast.Num, ast.Str)):
                add_constraint(gx, n, gx.cnode[var, dcpa, 0])

    for func in cl.funcs.values():
        if cl.mv.module.ident == 'builtin' and cl.ident != '__iter' and func.ident == '__iter__':  # XXX hack for __iter__:__iter()
            itercl = python.def_class(gx, '__iter')
            gx.alloc_info[func.ident, ((cl, dcpa),), func.returnexpr[0]] = (itercl, itercl.dcpa)
            class_copy(gx, itercl, dcpa)
            itercl.dcpa += 1

        func_copy(gx, func, dcpa, 0)

# --- use dcpa=0,cpa=0 mold created by module visitor to duplicate function


def func_copy(gx, func, dcpa, cpa, worklist=None, cart=None):
    # print 'funccopy', func, cart, dcpa, cpa

    # --- copy local end points of each constraint
    for (a, b) in func.constraints:
        if not (isinstance(a.thing, python.Variable) and parent_func(gx, a.thing) != func) and a.dcpa == 0:
            a = a.copy(dcpa, cpa, worklist)
        if not (isinstance(b.thing, python.Variable) and parent_func(gx, b.thing) != func) and b.dcpa == 0:
            b = b.copy(dcpa, cpa, worklist)

        add_constraint(gx, a, b, worklist)

    # --- copy other nodes
    for node in func.nodes:
        node.copy(dcpa, cpa, worklist)

    # --- iterative flow analysis: seed allocation sites in new template
    ifa_seed_template(gx, func, cart, dcpa, cpa, worklist)


def print_typeset(types):
    l = list(types.items())
    l.sort(lambda x, y: cmp(repr(x[0]), repr(y[0])))
    for uh in l:
        if not uh[0].mv.module.builtin:
            logger.info('%r: %s', uh[0], uh[1])
    logger.info('')


def print_state(gx):
    # print 'state:'
    print_typeset(gx.types)


def print_constraints(gx):
    # print 'constraints:'
    l = list(gx.constraints)
    l.sort(lambda x, y: cmp(repr(x[0]), repr(y[0])))
    for (a, b) in l:
        if not (a.mv.module.builtin and b.mv.module.builtin):
            logger.info('%s -> %s', a, b)
            if not a in gx.types or not b in gx.types:
                logger.info('NOTYPE %s %s', a in gx.types, b in gx.types)
    logger.info('')


# --- iterative dataflow analysis
def propagate(gx):
    logger.debug('propagate')

    # --- initialize working sets
    worklist = []
    changed = set()
    for node in gx.types:
        if gx.types[node]:
            add_to_worklist(worklist, node)
        expr = node.thing
        if (isinstance(expr, ast.Call) and not expr.args) or expr in gx.lambdawrapper:  # XXX
            changed.add(node)

    for node in changed:
        cpa(gx, node, worklist)

    builtins = set(gx.builtins)
    types = gx.types

    # --- iterative dataflow analysis
    while worklist:
        callnodes = set()
        while worklist:
            a = worklist.pop(0)
            a.in_list = 0

            for callfunc in a.callfuncs:
                t = (callfunc, a.dcpa, a.cpa)
                if t in gx.cnode:
                    callnodes.add(gx.cnode[t])

            for b in a.out.copy():  # XXX can change...?
                # for builtin types, the set of instance variables is known, so do not flow into non-existent ones # XXX ifa
                if isinstance(b.thing, python.Variable) and isinstance(b.thing.parent, python.Class):
                    parent_ident = b.thing.parent.ident
                    if parent_ident in builtins:
                        if parent_ident in ['int_', 'float_', 'str_', 'none', 'bool_', 'bytes_']:
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

                if b.thing in gx.filters:
                    typesa = set([t for t in typesa if t[0] == gx.filters[b.thing]])

                typesb.update(typesa)
                if len(typesb) > oldsize:
                    add_to_worklist(worklist, b)

        for callnode in callnodes:
            cpa(gx, callnode, worklist)


# --- determine cartesian product of possible function and argument types
def possible_functions(gx, node, analysis):
    expr = node.thing

    # --- determine possible target functions
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analysis
    funcs = []

    if anon_func:
        # anonymous call
        types = gx.cnode[expr.func, node.dcpa, node.cpa].types()
        types = [t for t in types if isinstance(t[0], python.Function)]  # XXX XXX analyse per t, sometimes class, sometimes function..

        if list(types)[0][0].parent:  # method reference XXX merge below?
            funcs = [(f[0], f[1], (f[0].parent, f[1])) for f in types]  # node.dcpa: connect to right dcpa duplicate version
        else:  # function reference
            funcs = [(f[0], f[1], None) for f in types]  # function call: only one version; no objtype

    elif constructor:
        funcs = [(t[0].funcs['__init__'], t[1], t) for t in node.types() if '__init__' in t[0].funcs]

    elif parent_constr:
        objtypes = gx.cnode[python.lookup_var('self', node.parent, mv=node.mv), node.dcpa, node.cpa].types()
        funcs = [(t[0].funcs[ident], t[1], None) for t in objtypes if ident in t[0].funcs]

    elif direct_call:
        funcs = [(direct_call, 0, None)]

    elif method_call:
        objtypes = gx.cnode[objexpr, node.dcpa, node.cpa].types()
        objtypes = [t for t in objtypes if not isinstance(t[0], python.Function)]  # XXX

        funcs = [(t[0].funcs[ident], t[1], t) for t in objtypes if ident in t[0].funcs and not (isinstance(t[0], python.Class) and ident in t[0].staticmethods)]

    return funcs


def possible_argtypes(gx, node, funcs, analysis, worklist):
    expr = node.thing
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analysis
    if funcs:
        func = funcs[0][0]  # XXX

    args = []
    starargs = ast_utils.get_starargs(expr)
    if starargs:  # XXX
        args = [starargs]
    elif funcs and not func.node:  # XXX getattr, setattr
        args = expr.args
    elif funcs:
        actuals, formals, used_defaults, varargs, _ = analyze_args(gx, expr, func, node)

        if not node.defnodes:
            for i, default in enumerate(used_defaults):
                defnode = CNode(gx, (inode(gx, node.thing), i), node.dcpa, node.cpa, parent=func, mv=node.mv)
                gx.types[defnode] = set()
                defnode.callfuncs.append(node.thing)
                add_constraint(gx, gx.cnode[default, 0, 0], defnode, worklist)  # XXX bad place
        node.defnodes = True

        for act, form in zip(actuals, formals):
            if parent_constr or not (isinstance(func.parent, python.Class) and form == 'self'):  # XXX merge
                args.append(act)

    argtypes = []
    for arg in args:
        if (arg, node.dcpa, node.cpa) in gx.cnode:
            argtypes.append(gx.cnode[arg, node.dcpa, node.cpa].types())
        else:
            argtypes.append(inode(gx, arg).types())  # XXX def arg?

    # store arg count for wrappers to builtin refs
    if funcs and (func.lambdawrapper or node.thing in gx.lambdawrapper):
        while argtypes and not argtypes[-1]:
            argtypes = argtypes[:-1]
        if func.lambdawrapper:
            if starargs and node.parent and node.parent.node.args.vararg:
                func.largs = node.parent.xargs[node.dcpa, node.cpa] - len(node.parent.formals) + 1
            else:
                func.largs = len(argtypes)

    return argtypes


def cartesian_product(gx, node, analysis, worklist):
    funcs = possible_functions(gx, node, analysis)
    if not funcs:
        return []
    argtypes = possible_argtypes(gx, node, funcs, analysis, worklist)
    alltypes = [funcs] + argtypes
    return list(itertools.product(*alltypes))


def redirect(gx, c, dcpa, func, callfunc, ident, callnode, direct_call, constructor):
    # redirect based on number of arguments (__%s%d syntax in builtins)
    if func.mv.module.builtin:
        if isinstance(func.parent, python.Class):
            funcs = func.parent.funcs
        else:
            funcs = func.mv.funcs
        redir = '__%s%d' % (func.ident, len([kwarg for kwarg in callfunc.args if not isinstance(kwarg, ast.keyword)]))
        func = funcs.get(redir, func)

    # staticmethod
    if isinstance(func.parent, python.Class) and func.ident in func.parent.staticmethods:
        dcpa = 1

    # dict.__init__
    if constructor and (ident, nrargs(gx, callfunc)) in (('dict', 1), ('defaultdict', 2)):
        clnames = [x[0].ident for x in c if isinstance(x[0], python.Class)]
        if 'dict' in clnames or 'defaultdict' in clnames:
            func = list(callnode.types())[0][0].funcs['__initdict__']
        else:
            func = list(callnode.types())[0][0].funcs['__inititer__']

    # dict.update
    if func.ident == 'update' and isinstance(func.parent, python.Class) and func.parent.ident in ('dict', 'defaultdict'):
        clnames = [x[0].ident for x in c if isinstance(x[0], python.Class)]
        if not ('dict' in clnames or 'defaultdict' in clnames):
            func = func.parent.funcs['updateiter']

    # list, tuple
    if constructor and ident in ('list', 'tuple', 'set', 'frozenset') and nrargs(gx, callfunc) == 1:
        func = list(callnode.types())[0][0].funcs['__inititer__']  # XXX use __init__?

    # array
    if constructor and ident == 'array' and isinstance(callfunc.args[0], ast.Str):
        typecode = callfunc.args[0].s
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
    if (isinstance(callfunc.func, ast.Attribute) and callfunc.func.attr == '__getitem__' and
        isinstance(callfunc.args[0], ast.Num) and callfunc.args[0].n in (0, 1) and
            func.parent.mv.module.builtin and func.parent.ident == 'tuple2'):
        if callfunc.args[0].n == 0:
            func = func.parent.funcs['__getfirst__']
        else:
            func = func.parent.funcs['__getsecond__']

    # property
    if isinstance(callfunc.func, ast.Attribute) and callfunc.func.attr in ['__setattr__', '__getattr__']:
        if isinstance(func.parent, python.Class) and callfunc.args and callfunc.args[0].s in func.parent.properties:
            arg = callfunc.args[0].s
            if callfunc.func.attr == '__setattr__':
                func = func.parent.funcs[func.parent.properties[arg][1]]
            else:
                func = func.parent.funcs[func.parent.properties[arg][0]]
            c = c[1:]

    # win32
    if sys.platform == 'win32' and func.mv.module.builtin and isinstance(func.parent, python.Class) and '__win32' + func.ident in func.parent.funcs:
        func = func.parent.funcs['__win32' + func.ident]

    return c, dcpa, func

# --- cartesian product algorithm; adds interprocedural constraints


def cpa(gx, callnode, worklist):
    analysis = analyze_callfunc(gx, callnode.thing, callnode)
    cp = cartesian_product(gx, callnode, analysis, worklist)
    if not cp:
        return
    if len(cp) > gx.cpa_limit and not gx.cpa_clean:
        gx.cpa_limited = True
        return []
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analysis

    # --- iterate over argument type combinations
    for c in cp:
        (func, dcpa, objtype), c = c[0], c[1:]

        if INCREMENTAL:
            if not func.mv.module.builtin and func not in gx.added_funcs_set and not func.ident in ['__getattr__', '__setattr__']:
                if INCREMENTAL_DATA:
                    if gx.added_allocs >= INCREMENTAL_ALLOCS:
                        continue
                else:
                    if gx.added_funcs >= INCREMENTAL_FUNCS:
                        continue
                gx.added_funcs += 1
                gx.added_funcs_set.add(func)
                logger.debug('adding %s', func)

        if objtype:
            objtype = (objtype,)
        else:
            objtype = ()

        # redirect in special cases
        callfunc = callnode.thing
        c, dcpa, func = redirect(gx, c, dcpa, func, callfunc, ident, callnode, direct_call, constructor)

        # already connected to template
        if (func,) + objtype + c in callnode.nodecp:
            continue
        callnode.nodecp.add((func,) + objtype + c)

        # create new template
        if not dcpa in func.cp or not c in func.cp[dcpa]:
            create_template(gx, func, dcpa, c, worklist)
        cpa = func.cp[dcpa][c]
        func.xargs[dcpa, cpa] = len(c)

        # __getattr__, __setattr__
        if connect_getsetattr(gx, func, callnode, callfunc, dcpa, worklist):
            continue

        # connect actuals and formals
        actuals_formals(gx, callfunc, func, callnode, dcpa, cpa, objtype + c, analysis, worklist)

        # connect call and return expressions
        if func.retnode and not constructor:
            retnode = gx.cnode[func.retnode.thing, dcpa, cpa]
            add_constraint(gx, retnode, callnode, worklist)


def connect_getsetattr(gx, func, callnode, callfunc, dcpa, worklist):
    if (isinstance(callfunc.func, ast.Attribute) and callfunc.func.attr in ['__setattr__', '__getattr__'] and
            not (isinstance(func.parent, python.Class) and callfunc.args and callfunc.args[0].s in func.parent.properties)):
        varname = callfunc.args[0].s
        parent = func.parent

        var = default_var(gx, varname, parent, worklist, mv=parent.module.mv)  # XXX always make new var??
        inode(gx, var).copy(dcpa, 0, worklist)

        if not gx.cnode[var, dcpa, 0] in gx.types:
            gx.types[gx.cnode[var, dcpa, 0]] = set()

        gx.cnode[var, dcpa, 0].mv = parent.module.mv  # XXX move into default_var

        if callfunc.func.attr == '__setattr__':
            add_constraint(gx, gx.cnode[callfunc.args[1], callnode.dcpa, callnode.cpa], gx.cnode[var, dcpa, 0], worklist)
        else:
            add_constraint(gx, gx.cnode[var, dcpa, 0], callnode, worklist)
        return True
    return False


def create_template(gx, func, dcpa, c, worklist):
    # --- unseen cartesian product: create new template
    if not dcpa in func.cp:
        func.cp[dcpa] = {}
    func.cp[dcpa][c] = cpa = len(func.cp[dcpa])  # XXX +1

    if not func.mv.module.builtin and not func.ident in ['__getattr__', '__setattr__']:
        logger.debug('template (%s, %s) %s', func, dcpa, c)

    gx.templates += 1
    func_copy(gx, func, dcpa, cpa, worklist, c)


def actuals_formals(gx, expr, func, node, dcpa, cpa, types, analysis, worklist):
    objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analysis

    starargs = ast_utils.get_starargs(expr)
    if starargs:  # XXX only in lib/
        formals = func.formals
        actuals = len(formals) * [starargs]
        types = len(formals) * types
    else:
        actuals, formals, _, varargs, _error = analyze_args(gx, expr, func, node)
        if _error:
            return

    for (actual, formal, formaltype) in zip(actuals, formals, types):
        formalnode = gx.cnode[func.vars[formal], dcpa, cpa]

        if formaltype[1] != 0:  # ifa: remember dataflow information for non-simple types
            if actual is None:
                if constructor:
                    objexpr = node.thing

                if method_call or constructor:
                    formalnode.in_.add(gx.cnode[objexpr, node.dcpa, node.cpa])
            else:
                if actual in func.defaults:
                    formalnode.in_.add(gx.cnode[actual, 0, 0])
                else:
                    formalnode.in_.add(gx.cnode[actual, node.dcpa, node.cpa])

        gx.types[formalnode].add(formaltype)
        add_to_worklist(worklist, formalnode)

# --- iterative flow analysis: after each iteration, detect imprecisions, and split involved contours


def ifa(gx):
    logger.debug('ifa')
    split = []  # [(set of creation nodes, new type number), ..]

    allcsites = {}
    for n, types in gx.types.items():
        if not n.in_:
            for (cl, dcpa) in types:
                allcsites.setdefault((cl, dcpa), set()).add(n)

    for cl in ifa_classes_to_split(gx):
        ifa_logger.debug('IFA: --- class %s ---', cl.ident)
        cl.newdcpa = cl.dcpa
        vars = [cl.vars[name] for name in cl.tvar_names() if name in cl.vars]
        classes_nr, nr_classes = ifa_class_types(gx, cl, vars)
        for dcpa in range(1, cl.dcpa):
            if ifa_split_vars(gx, cl, dcpa, vars, nr_classes, classes_nr, split, allcsites) is not None:
                ifa_logger.debug('IFA found splits, return')
                return split
    ifa_logger.debug('IFA final return')
    return split


def ifa_split_vars(gx, cl, dcpa, vars, nr_classes, classes_nr, split, allcsites):
    for (varnum, var) in enumerate(vars):
        if not (var, dcpa, 0) in gx.cnode:
            continue
        node = gx.cnode[var, dcpa, 0]
        creation_points, paths, assignsets, allnodes, csites, emptycsites = ifa_flow_graph(gx, cl, dcpa, node, allcsites)
        ifa_logger.debug('IFA visit var %s.%s, %d, csites %d', cl.ident, var.name, dcpa, len(csites))
        if len(csites) + len(emptycsites) == 1:
            continue
        if ((len(merge_simple_types(gx, gx.types[node])) > 1 and len(assignsets) > 1) or
                (assignsets and emptycsites)):  # XXX move to split_no_conf
            ifa_split_no_confusion(gx, cl, dcpa, varnum, classes_nr, nr_classes, csites, emptycsites, allnodes, split)
        if split:
            break
        for node in allnodes:
            if not ifa_confluence_point(node, creation_points):
                continue
            if not node.thing.formal_arg and not isinstance(node.thing.parent, python.Class):
                continue
            remaining = ifa_determine_split(node, allnodes)
            if len(remaining) < 2 or len(remaining) >= 10:
                continue
            # --- if it exists, perform actual splitting
            ifa_logger.debug('IFA normal split, remaining:', len(remaining))
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
            ifa_logger.debug('IFA partition csites: %s', list(prt.values())[0])
            ifa_split_class(cl, dcpa, list(prt.values())[0], split)

        # --- if all else fails, perform wholesale splitting
        elif len(paths) > 1 and 1 < len(csites) < 10:
            ifa_logger.debug('IFA wholesale splitting, csites: %d', len(csites))
            for csite in csites[1:]:
                ifa_split_class(cl, dcpa, [csite], split)
            return split


def ifa_split_no_confusion(gx, cl, dcpa, varnum, classes_nr, nr_classes, csites, emptycsites, allnodes, split):
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
    for subtype, csites in subtype_csites.items():
        if subtype in classes_nr:  # reuse contour
            nr = classes_nr[subtype]
            split.append((cl, dcpa, csites, nr))
            cl.splits[nr] = dcpa
        else:  # create new contour
            classes_nr[subtype] = cl.newdcpa
            ifa_split_class(cl, dcpa, csites, split)
    if subtype_csites:
        ifa_logger.debug('IFA found simple split: %s', subtype_csites.keys())


def ifa_class_types(gx, cl, vars):
    ''' create table for previously deduced types '''
    classes_nr, nr_classes = {}, {}
    for dcpa in range(1, cl.dcpa):
        attr_types = []  # XXX merge with ifa_merge_contours.. sep func?
        for var in vars:
            if (var, dcpa, 0) in gx.cnode:
                attr_types.append(merge_simple_types(gx, gx.cnode[var, dcpa, 0].types()))
            else:
                attr_types.append(frozenset())
        attr_types = tuple(attr_types)
        if all(attr_types):
            ifa_logger.debug('IFA %s: %s %s', dcpa, zip([var.name for var in vars], map(list, attr_types)))
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


def ifa_classes_to_split(gx):
    ''' setup classes to perform splitting on '''
    classes = []
    for ident in ['list', 'tuple', 'tuple2', 'dict', 'set', 'frozenset', 'deque', 'defaultdict', '__iter', 'array']:
        for cl in gx.allclasses:
            if cl.mv.module.builtin and cl.ident == ident:
                cl.splits = {}
                classes.append(cl)
                break
    random.shuffle(classes)
    return classes


def ifa_confluence_point(node, creation_points):
    ''' determine if node is confluence point '''
    if len(node.in_) > 1 and isinstance(node.thing, python.Variable):
        for csite in node.csites:
            occ = [csite in crpoints for crpoints in creation_points.values()].count(True)
            if occ > 1:
                return True
    return False


def ifa_flow_graph(gx, cl, dcpa, node, allcsites):
    creation_points, paths, assignsets = {}, {}, {}
    allnodes = set()
    csites = []

    # --- determine assignment sets
    for a in node.in_:
        types = gx.types[a]
        if types:
            if a.thing in gx.assign_target:  # XXX *args
                target = gx.cnode[gx.assign_target[a.thing], a.dcpa, a.cpa]
                # print 'target', a, target, types
                assignsets.setdefault(merge_simple_types(gx, types), []).append(target)

    # --- determine backflow paths and creation points per assignment set
    for assign_set, targets in assignsets.items():
        path = backflow_path(gx, targets, (cl, dcpa))
        paths[assign_set] = path
        allnodes.update(path)
        alloc = [n for n in path if not n.in_]
        creation_points[assign_set] = alloc

    # --- per node, determine paths it is located on
    for n in allnodes:
        n.paths = []
    for assign_set, path in paths.items():
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


def update_progressbar(gx, perc):
#    if not logger.isEnabledFor(logging.INFO):
#        return
    if gx.progressbar is None:
        import progressbar
        widgets = progressbar.widgets
        gx.progressbar = progressbar.ProgressBar(
            widgets=[widgets.Bar(marker='*'), widgets.Percentage()],
            maxval=1,
            term_width=33
        )
        gx.progressbar.start()

    with gx.terminal.location(x=0):
        gx.progressbar.update(perc)
    if perc == 1:
        # Finished, so add a new line.
        sys.stdout.write('\n')

# --- cartesian product algorithm (cpa) & iterative flow analysis (ifa)


def iterative_dataflow_analysis(gx):
    logger.info('[analyzing types..]')
    backup = backup_network(gx)

    gx.orig_types = {}
    for n, t in gx.types.items():
        gx.orig_types[n] = t

    if INCREMENTAL:
        update_progressbar(gx, 0)

    gx.added_funcs = INCREMENTAL_FUNCS  # analyze root of callgraph in first round
    gx.added_funcs_set = set()
    gx.added_allocs = 0
    gx.added_allocs_set = set()
    gx.cpa_limit = CPA_LIMIT
    gx.cpa_clean = False

    while True:
        gx.iterations += 1
        gx.total_iterations += 1
        maxiter = (gx.iterations == MAXITERS)
        logger.debug('*** iteration %d ***', gx.iterations)

        # --- propagate using cartesian product algorithm
        gx.new_alloc_info = {}
#        print 'table'
#        print '\n'.join([repr(e)+': '+repr(l) for e,l in gx.alloc_info.items()])
        gx.cpa_limited = False
        propagate(gx)
        gx.alloc_info = gx.new_alloc_info

        if gx.cpa_limited:
            logger.debug('CPA limit %d reached!', gx.cpa_limit)
        else:
            gx.cpa_clean = True

        # --- ifa: detect conflicting assignments to instance variables, and split contours to resolve these
        split = ifa(gx)
        if split:
            logger.debug('%d splits', len(split))
            if ifa_logger.isEnabledFor(logging.DEBUG):
                ifa_logger.debug('IFA splits: %s', [(s[0], s[1], s[3]) for s in split])

        if not split or maxiter:
            if not maxiter:
                logger.debug('no splits')
            if INCREMENTAL:
                allfuncs = len([f for f in gx.allfuncs if not f.mv.module.builtin and not [start for start in ('__iadd__', '__imul__', '__str__', '__hash__') if f.ident.startswith(start)]])
                perc = 1.0
                if allfuncs:
                    perc = min(len(gx.added_funcs_set) / float(allfuncs), 1.0)
                update_progressbar(gx, perc)
            if maxiter:
                logger.warning('reached maximum number of iterations')
                gx.maxhits += 1
                if gx.maxhits == 3:
                    return

            gx.cpa_clean = False
            if INCREMENTAL and (gx.added_funcs or gx.added_allocs):
                gx.added_funcs = 0
                gx.added_allocs = 0
                gx.iterations = 0
            elif gx.cpa_limited:
                gx.cpa_limit *= 2
                gx.iterations = 0
            else:
                if INCREMENTAL:
                    update_progressbar(gx, 1.0)
                logger.debug('iterations: %s templates: %s', gx.total_iterations, gx.templates)
                return

        if not INCREMENTAL and not logger.isEnabledFor(logging.DEBUG):
            sys.stdout.write('*')
            sys.stdout.flush()

        # --- update alloc info table for split contours
        for cl, dcpa, nodes, newnr in split:
            for n in nodes:
                parent = parent_func(gx, n.thing)
                if parent:
                    if n.dcpa in parent.cp:
                        for cart, cpa in parent.cp[n.dcpa].items():  # XXX not very fast
                            if cpa == n.cpa:
                                if parent.parent and isinstance(parent.parent, python.Class):  # self
                                    cart = ((parent.parent, n.dcpa),) + cart

                                gx.alloc_info[parent.ident, cart, n.thing] = (cl, newnr)
                                break

        beforetypes = backup[0]

        # --- clean out constructor node types in functions, possibly to be seeded again
        for node in beforetypes:
            func = parent_func(gx, node.thing)
            if isinstance(func, python.Function):
                if node.constructor and isinstance(node.thing, (ast.List, ast.Dict, ast.Tuple, ast.ListComp, ast.Call)):
                    beforetypes[node] = set()

        # --- create new class types, and seed global nodes
        for cl, dcpa, nodes, newnr in split:
            if newnr == cl.dcpa:
                class_copy(gx, cl, newnr)
                cl.dcpa += 1

            # print 'split off', nodes, newnr
            for n in nodes:
                if not parent_func(gx, n.thing):
                    beforetypes[n] = set([(cl, newnr)])

        # --- restore network
        restore_network(gx, backup)

# --- seed allocation sites in newly created templates (called by function.copy())


def ifa_seed_template(gx, func, cart, dcpa, cpa, worklist):
    if cart is not None:  # (None means we are not in the process of propagation)
        # print 'funccopy', func.ident #, func.nodes
        if isinstance(func.parent, python.Class):  # self
            cart = ((func.parent, dcpa),) + cart

        added = gx.added_allocs_set
        added_new = 0

        for node in func.nodes_ordered:
            if node.constructor and isinstance(node.thing, (ast.List, ast.Dict, ast.Tuple, ast.ListComp, ast.Call)):
                if node.thing not in added:
                    if INCREMENTAL_DATA and not func.mv.module.builtin:
                        if gx.added_allocs >= INCREMENTAL_ALLOCS:
                            continue
                        added_new += 1
                        gx.added_allocs += 1
                    added.add(node.thing)

                # --- contour is specified in alloc_info
                parent = node.parent
                while isinstance(parent.parent, python.Function):
                    parent = parent.parent

                alloc_id = (parent.ident, cart, node.thing)  # XXX ident?
                alloc_node = gx.cnode[node.thing, dcpa, cpa]

                if alloc_id in gx.alloc_info:
                    pass
#                    print 'specified' # print 'specified', func.ident, cart, alloc_node, alloc_node.callfuncs, gx.alloc_info[alloc_id]
                # --- contour is newly split: copy allocation type for 'mother' contour; modify alloc_info
                else:
                    mother_alloc_id = alloc_id

                    for (id, c, thing) in gx.alloc_info:
                        if id == parent.ident and thing is node.thing:
                            for a, b in zip(cart, c):
                                if a != b and not (isinstance(a[0], python.Class) and a[0] is b[0] and a[1] in a[0].splits and a[0].splits[a[1]] == b[1]):
                                    break
                            else:
                                mother_alloc_id = (id, c, thing)
                                break

                    # print 'not specified.. mother id:', mother_alloc_id
                    if mother_alloc_id in gx.alloc_info:
                        gx.alloc_info[alloc_id] = gx.alloc_info[mother_alloc_id]
                        # print 'mothered', alloc_node, gx.alloc_info[mother_alloc_id]
                    elif gx.orig_types[node]:  # empty constructors that do not flow to assignments have no type
                        # print 'no mother', func.ident, cart, mother_alloc_id, alloc_node, gx.types[node]
                        gx.alloc_info[alloc_id] = list(gx.orig_types[node])[0]
                    else:
                        # print 'oh boy'
                        for (id, c, thing) in gx.alloc_info:  # XXX vhy?
                            if id == parent.ident and thing is node.thing:
                                mother_alloc_id = (id, c, thing)
                                gx.alloc_info[alloc_id] = gx.alloc_info[mother_alloc_id]
                                break

                if alloc_id in gx.alloc_info:
                    gx.new_alloc_info[alloc_id] = gx.alloc_info[alloc_id]
                    gx.types[alloc_node] = set()
                    # print 'seeding..', alloc_node, gx.alloc_info[alloc_id], alloc_node.thing in gx.empty_constructors
                    gx.types[alloc_node].add(gx.alloc_info[alloc_id])
                    add_to_worklist(worklist, alloc_node)

        if added_new and not func.mv.module.builtin:
            logger.debug('%d seed(s): %s', added_new, func)

# --- for a set of target nodes of a specific type of assignment (e.g. int to (list,7)), flow back to creation points


def backflow_path(gx, worklist, t):
    path = set(worklist)
    while worklist:
        new = set()
        for node in worklist:
            for incoming in node.in_:
                if t in gx.types[incoming]:
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
def backup_network(gx):
    beforetypes = {}
    for node, typeset in gx.types.items():
        beforetypes[node] = typeset.copy()

    beforeconstr = gx.constraints.copy()

    beforeinout = {}
    for node in gx.types:
        beforeinout[node] = (node.in_.copy(), node.out.copy())

    beforecnode = gx.cnode.copy()

    return (beforetypes, beforeconstr, beforeinout, beforecnode)


# --- restore constraint network, introducing new types
def restore_network(gx, backup):
    beforetypes, beforeconstr, beforeinout, beforecnode = backup

    gx.types = {}
    for node, typeset in beforetypes.items():
        gx.types[node] = typeset.copy()

    gx.constraints = beforeconstr.copy()
    gx.cnode = beforecnode.copy()

    for node, typeset in gx.types.items():
        node.nodecp = set()
        node.defnodes = False
        befinout = beforeinout[node]
        node.in_, node.out = befinout[0].copy(), befinout[1].copy()
        node.fout = set()  # XXX ?

    for var in gx.allvars:  # XXX we have to restore some variable constraint nodes.. remove vars?
        if not (var, 0, 0) in gx.cnode:
            CNode(gx, var, parent=var.parent)

    for func in gx.allfuncs:
        func.cp = {}


def merge_simple_types(gx, types):
    merge = types.copy()
    if len(types) > 1 and (python.def_class(gx, 'none'), 0) in types:
        if not (python.def_class(gx, 'int_'), 0) in types and not (python.def_class(gx, 'float_'), 0) in types and not (python.def_class(gx, 'bool_'), 0) in types:
            merge.remove((python.def_class(gx, 'none'), 0))

    return frozenset(merge)


def get_classes(gx, var):
    return set(t[0] for t in gx.merged_inh[var]
               if isinstance(t[0], python.Class) and not t[0].mv.module.builtin)


def deepcopy_classes(gx, classes):
    changed = True
    while changed:
        changed = False
        for cl in classes.copy():
            for var in cl.vars.values():
                if var not in gx.merged_inh:
                    continue
                newcl = get_classes(gx, var)
                if newcl - classes:
                    changed = True
                    classes.update(newcl)
    return classes


def determine_classes(gx):  # XXX modeling..?
    if 'copy' not in gx.modules:
        return
    func = gx.modules['copy'].mv.funcs['copy']
    var = func.vars[func.formals[0]]
    for cl in get_classes(gx, var):
        cl.has_copy = True
    func = gx.modules['copy'].mv.funcs['deepcopy']
    var = func.vars[func.formals[0]]
    for cl in deepcopy_classes(gx, get_classes(gx, var)):
        cl.has_deepcopy = True


def analyze(gx, module_name):
    from . import graph  # TODO improve separation to avoid circular imports..
    from .typestr import nodetypestr
    from .virtual import analyze_virtuals

    # --- build dataflow graph from source code
    gx.main_module = graph.parse_module(module_name, gx)

    # --- seed class_.__name__ attributes..
    for cl in gx.allclasses:
        if cl.ident == 'class_':
            var = default_var(gx, '__name__', cl)
            gx.types[inode(gx, var)] = set([(python.def_class(gx, 'str_'), 0)])

    # --- non-ifa: copy classes for each allocation site
    for cl in gx.allclasses:
        if cl.ident in ['int_', 'float_', 'none', 'class_', 'str_', 'bool_', 'bytes_']:
            continue
        if cl.ident == 'list':
            cl.dcpa = len(gx.list_types) + 2
        elif cl.ident != '__iter':  # XXX huh
            cl.dcpa = 2

        for dcpa in range(1, cl.dcpa):
            class_copy(gx, cl, dcpa)

    # --- seed str/bytes unit
    cl = python.def_class(gx, 'str_')
    var = default_var(gx, 'unit', cl)
    gx.types[inode(gx, var)] = set([(cl, 0)])

    cl = python.def_class(gx, 'bytes_')
    var = default_var(gx, 'unit', cl)
    gx.types[inode(gx, var)] = set([(python.def_class(gx, 'int_'), 0)])

    # --- cartesian product algorithm & iterative flow analysis
    iterative_dataflow_analysis(gx)

    logger.info('[generating c++ code..]')

    for cl in gx.allclasses:
        for name in cl.vars:
            if name in cl.parent.vars and not name.startswith('__'):
                error.error("instance variable '%s' of class '%s' shadows class variable" % (name, cl.ident), gx, warning=True)

    gx.merged_inh = merged(gx, gx.types, inheritance=True)
    analyze_virtuals(gx)
    determine_classes(gx)

    # --- add inheritance relationships for non-original Nodes (and temp_vars?); XXX register more, right solution?
    for func in gx.allfuncs:
        if func in gx.inheritance_relations:
            for inhfunc in gx.inheritance_relations[func]:
                for a, b in zip(func.registered, inhfunc.registered):
                    graph.inherit_rec(gx, a, b, func.mv)

                for a, b in zip(func.registered_temp_vars, inhfunc.registered_temp_vars):  # XXX more general
                    gx.inheritance_temp_vars.setdefault(a, []).append(b)

    gx.merged_inh = merged(gx, gx.types, inheritance=True)

    # error for dynamic expression without explicit type declaration
    for node in gx.merged_inh:
        if isinstance(node, ast.AST) and not ast_utils.is_assign_attribute(node) and not inode(gx, node).mv.module.builtin:
            nodetypestr(gx, node, inode(gx, node).parent, mv=inode(gx, node).mv)

    return gx


def register_temp_var(var, parent):
    if isinstance(parent, python.Function):
        parent.registered_temp_vars.append(var)


def default_var(gx, name, parent, worklist=None, mv=None, exc_name=False):
    if parent:
        mv = parent.mv
    var = python.lookup_var(name, parent, local=True, mv=mv)
    if not var:
        var = python.Variable(name, parent)
        if parent:  # XXX move to python.Variable?
            parent.vars[name] = var
        elif exc_name:
            mv.exc_names[name] = var
        else:
            mv.globals[name] = var
        gx.allvars.add(var)

    if (var, 0, 0) not in gx.cnode:
        newnode = CNode(gx, var, parent=parent, mv=mv)
        if parent:
            newnode.mv = parent.mv
        else:
            newnode.mv = mv
        add_to_worklist(worklist, newnode)
        gx.types[newnode] = set()

    if isinstance(parent, python.Function) and parent.listcomp and not var.registered:
        while isinstance(parent, python.Function) and parent.listcomp:  # XXX
            parent = parent.parent
        register_temp_var(var, parent)

    return var


def var_types(gx, var):
    return inode(gx, var).types()
