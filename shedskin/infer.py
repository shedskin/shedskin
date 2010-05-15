'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2009 Mark Dufour; License GNU GPL version 3 (See LICENSE)

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

'''

import gc, random
random.seed(42)

from shared import *
import graph, cpp

DEBUG = False

def class_copy(cl, dcpa):
    for var in cl.vars.values(): # XXX
        if not inode(var) in getgx().types: continue # XXX research later

        inode(var).copy(dcpa, 0)
        getgx().types[getgx().cnode[var, dcpa, 0]] = inode(var).types().copy()

        for n in inode(var).in_: # XXX
            if isinstance(n.thing, Const):
                addconstraint(n, getgx().cnode[var,dcpa,0])

    for func in cl.funcs.values():
        if cl.mv.module.ident == 'builtin' and cl.ident != '__iter' and func.ident == '__iter__': # XXX hack for __iter__:__iter()
            itercl = defclass('__iter')
            getgx().alloc_info[func.ident, ((cl,dcpa),), func.returnexpr[0]] = (itercl, itercl.dcpa)
            class_copy(itercl, dcpa)
            itercl.dcpa += 1

        func_copy(func, dcpa, 0)

# --- use dcpa=0,cpa=0 mold created by module visitor to duplicate function
def func_copy(func, dcpa, cpa, worklist=None, cart=None):
    #print 'funccopy', self, cart, dcpa, cpa

    # --- copy local end points of each constraint
    for (a,b) in func.constraints:
        if not (isinstance(a.thing, variable) and parent_func(a.thing) != func) and a.dcpa == 0:
            a = a.copy(dcpa, cpa, worklist)
        if not (isinstance(b.thing, variable) and parent_func(b.thing) != func) and b.dcpa == 0:
            b = b.copy(dcpa, cpa, worklist)

        addconstraint(a,b, worklist)

    # --- copy other nodes
    for node in func.nodes:
        newnode = node.copy(dcpa, cpa, worklist)

    # --- iterative flow analysis: seed allocation sites in new template
    ifa_seed_template(func, cart, dcpa, cpa, worklist)

def printtypeset(types):
    l = list(types.items())
    l.sort(lambda x, y: cmp(repr(x[0]),repr(y[0])))
    for uh in l:
        if not uh[0].mv.module.builtin:
            print repr(uh[0])+':', uh[1] #, uh[0].parent
    print

def printstate():
    #print 'state:'
    printtypeset(getgx().types)

def printconstraints():
    #print 'constraints:'
    l = list(getgx().constraints)
    l.sort(lambda x, y: cmp(repr(x[0]),repr(y[0])))
    for (a,b) in l:
        if not (a.mv.module.builtin and b.mv.module.builtin):
            print a, '->', b
            if not a in getgx().types or not b in getgx().types:
                print 'NOTYPE', a in getgx().types, b in getgx().types
    print

def seed_nodes(): # XXX redundant - can be removed?
    for node in getgx().types:
        if isinstance(node.thing, Name):
            if node.thing.name in ['True', 'False']:
                getgx().types[node] = set([(defclass('bool_'), 0)])
            elif node.thing.name == 'None':
                getgx().types[node] = set([(defclass('none'), 0)])

def init_worklist():
    worklist = []
    for node, types in getgx().types.items():
        if types:
            addtoworklist(worklist, node)
    return worklist

# --- iterative dataflow analysis

def propagate():
    #print 'propagate'
    seed_nodes()
    worklist = init_worklist()
    getgx().checkcallfunc = [] # XXX

    # --- check whether seeded nodes are object/argument to call
    changed = set()
    for w in worklist:
        for callfunc in w.callfuncs:
            changed.add(getgx().cnode[callfunc, w.dcpa, w.cpa])

    # --- statically bind calls without object/arguments
    for node in getgx().types:
        expr = node.thing
        if (isinstance(expr, CallFunc) and not expr.args) or expr in getgx().lambdawrapper: # XXX
            changed.add(node)

    for node in changed:
        cpa(node, worklist)

    # --- iterative dataflow analysis
    while worklist:
        a = worklist.pop(0)
        a.in_list = 0

        if not a.mv.module.builtin and a.changed: # XXX general mechanism for seeding/changes -> cpa
            for callfunc in a.callfuncs:
                cpa(getgx().cnode[callfunc, a.dcpa, a.cpa], worklist)
            a.changed = False

        for b in a.out.copy(): # XXX can change...?
            # for builtin types, the set of instance variables is known, so do not flow into non-existent ones # XXX ifa
            if isinstance(b.thing, variable) and isinstance(b.thing.parent, class_) and b.thing.parent.ident in getgx().builtins:
                if b.thing.parent.ident in ['int_', 'float_', 'str_', 'none', 'bool_']: continue
                elif b.thing.parent.ident in ['list', 'tuple', 'frozenset', 'set', 'file','__iter', 'deque'] and b.thing.name != 'unit': continue
                elif b.thing.parent.ident in ('dict', 'defaultdict') and b.thing.name not in ['unit', 'value']: continue
                elif b.thing.parent.ident == 'tuple2' and b.thing.name not in ['unit', 'first', 'second']: continue

                #print 'flow', a, b #, difference #, difference, getgx().types[b], b.callfunc

            difference = getgx().types[a] - getgx().types[b]
            if difference:
                getgx().types[b].update(difference)

                # --- check whether node corresponds to actual argument: if so, perform cartesian product algorithm
                for callfunc in b.callfuncs:
                    cpa(getgx().cnode[callfunc, b.dcpa, b.cpa], worklist)

                addtoworklist(worklist, b)

                while getgx().checkcallfunc: # XXX
                    b = getgx().checkcallfunc.pop()
                    for callfunc in b.callfuncs:
                        cpa(getgx().cnode[callfunc, b.dcpa, b.cpa], worklist)

# --- determine cartesian product of possible function and argument types
def possible_functions(node):
    expr = node.thing

    # --- determine possible target functions
    objexpr, ident, direct_call, method_call, constructor, parent_constr = analyze_callfunc(expr)
    funcs = []

    if is_anon_func(expr, node):
        # anonymous call
        types = getgx().cnode[expr.node, node.dcpa, node.cpa].types()
        types = [t for t in types if isinstance(t[0], function)] # XXX XXX analyse per t, sometimes class, sometimes function..

        if list(types)[0][0].parent: # method reference XXX merge below?
            funcs = [(f[0], f[1], (f[0].parent, f[1])) for f in types] # node.dcpa: connect to right dcpa duplicate version
        else: # function reference
            funcs = [(f[0], f[1], None) for f in types] # function call: only one version; no objtype

    elif constructor:
        funcs = [(t[0].funcs['__init__'], t[1], t) for t in node.types() if '__init__' in t[0].funcs]

    elif parent_constr:
        objtypes = getgx().cnode[lookupvar('self', node.parent), node.dcpa, node.cpa].types()
        funcs = [(t[0].funcs[ident], t[1], None) for t in objtypes if ident in t[0].funcs]

    elif direct_call:
        funcs = [(direct_call, 0, None)]

    elif method_call:
        objtypes = getgx().cnode[objexpr, node.dcpa, node.cpa].types()
        objtypes = [t for t in objtypes if not isinstance(t[0], function)] # XXX

        funcs = [(t[0].funcs[ident], t[1], t) for t in objtypes if ident in t[0].funcs]

    return funcs

def possible_argtypes(node, funcs, worklist):
    expr = node.thing
    objexpr, ident, direct_call, method_call, constructor, parent_constr = analyze_callfunc(expr)
    if funcs:
        func = funcs[0][0] # XXX

    args = []
    if expr.star_args: # XXX
        args = [expr.star_args]
    elif funcs and not func.node: # XXX getattr, setattr
        args = expr.args
    elif funcs:
        actuals, formals, used_defaults, varargs, error = analyze_args(expr, func, node)

        if not node.defnodes:
            for i, default in enumerate(used_defaults):
                defnode = cnode((inode(node.thing),i), node.dcpa, node.cpa, parent=func)
                getgx().types[defnode] = set()
                defnode.callfuncs.append(node.thing)
                addconstraint(getgx().cnode[default, 0, 0], defnode, worklist) # XXX bad place
        node.defnodes = True

        for act, form in zip(actuals, formals):
            if parent_constr or not (isinstance(func.parent, class_) and form == 'self'): # XXX merge
                args.append(act)

    argtypes = []
    for arg in args:
        if (arg, node.dcpa, node.cpa) in getgx().cnode:
            argtypes.append(getgx().cnode[arg,node.dcpa,node.cpa].types())
        else:
            argtypes.append(inode(arg).types()) # XXX def arg?

    # store arg count for wrappers to builtin refs
    if funcs and (func.lambdawrapper or node.thing in getgx().lambdawrapper):
        while argtypes and not argtypes[-1]:
            argtypes = argtypes[:-1]
        if func.lambdawrapper:
            if expr.star_args and node.parent and node.parent.node.varargs:
                func.largs = node.parent.xargs[node.dcpa,node.cpa]-len(node.parent.formals)+1
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

def cartesian_product(node, worklist):
    funcs = possible_functions(node)
    argtypes = possible_argtypes(node, funcs, worklist)
    return product(*([funcs]+argtypes))

def redirect(c, dcpa, func, callfunc, ident, callnode):
    # redirect based on number of arguments (__%s%d syntax in builtins)
    if func.mv.module.builtin:
        if isinstance(func.parent, class_): funcs = func.parent.funcs
        else: funcs = func.mv.funcs
        redir = '__%s%d' % (func.ident, len([kwarg for kwarg in callfunc.args if not isinstance(kwarg, Keyword)]))
        func = funcs.get(redir, func)

    # filter
    if ident == 'filter':
        clnames = [x[0].ident for x in c if isinstance(x[0], class_)]
        if 'str_' in clnames or 'tuple' in clnames or 'tuple2' in clnames:
            func = func.mv.funcs['__'+ident]

    # staticmethod
    if isinstance(func.parent, class_) and func.ident in func.parent.staticmethods:
        dcpa = 1

    # dict, defaultdict
    if (ident, nrargs(callfunc)) in (('dict', 1), ('defaultdict', 2)):
        clnames = [x[0].ident for x in c if isinstance(x[0], class_)]
        if 'dict' in clnames or 'defaultdict' in clnames:
            func = list(callnode.types())[0][0].funcs['__initdict__']
        else:
            func = list(callnode.types())[0][0].funcs['__inititer__']

    # list, tuple
    if ident in ('list', 'tuple', 'set', 'frozenset') and nrargs(callfunc) == 1:
        func = list(callnode.types())[0][0].funcs['__inititer__'] # XXX use __init__?

    # tuple2.__getitem__(0/1) -> __getfirst__/__getsecond__
    if (isinstance(callfunc.node, Getattr) and callfunc.node.attrname == '__getitem__' and \
        isinstance(callfunc.args[0], Const) and callfunc.args[0].value in (0,1) and \
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

    return c, dcpa, func

# --- cartesian product algorithm; adds interprocedural constraints
def cpa(callnode, worklist):
    cp = cartesian_product(callnode, worklist)
    objexpr, ident, direct_call, method_call, constructor, parent_constr = analyze_callfunc(callnode.thing)

    # --- iterate over argument type combinations
    for c in cp:
        (func, dcpa, objtype), c = c[0], c[1:]

        if objtype: objtype = (objtype,)
        else: objtype = ()

        # redirect in special cases
        callfunc = callnode.thing
        c, dcpa, func = redirect(c, dcpa, func, callfunc, ident, callnode)

        # already connected to template
        if (func,)+objtype+c in callnode.nodecp:
            continue
        callnode.nodecp.add((func,)+objtype+c)

        # create new template
        if not dcpa in func.cp or not c in func.cp[dcpa]:
            create_template(func, dcpa, c, worklist)
        cpa = func.cp[dcpa][c]
        func.xargs[dcpa, cpa] = len(c)

        # __getattr__, __setattr__
        if connect_getsetattr(func, callnode, callfunc, dcpa, worklist):
            continue

        # connect actuals and formals
        actuals_formals(callfunc, func, callnode, dcpa, cpa, objtype+c, worklist)

        # connect call and return expressions
        if func.retnode and not constructor:
            retnode = getgx().cnode[func.retnode.thing, dcpa, cpa]
            addconstraint(retnode, callnode, worklist)

def connect_getsetattr(func, callnode, callfunc, dcpa, worklist):
    if (isinstance(callfunc.node, Getattr) and callfunc.node.attrname in ['__setattr__', '__getattr__'] and \
        not (isinstance(func.parent, class_) and callfunc.args and callfunc.args[0].value in func.parent.properties)):
            varname = callfunc.args[0].value
            parent = func.parent

            var = defaultvar(varname, parent, worklist) # XXX always make new var??
            inode(var).copy(dcpa,0,worklist)

            if not getgx().cnode[var,dcpa,0] in getgx().types:
                getgx().types[getgx().cnode[var,dcpa,0]] = set()

            getgx().cnode[var,dcpa,0].mv = parent.module.mv # XXX move into defaultvar

            if callfunc.node.attrname == '__setattr__':
                addconstraint(getgx().cnode[callfunc.args[1],callnode.dcpa,callnode.cpa], getgx().cnode[var,dcpa,0], worklist)
            else:
                addconstraint(getgx().cnode[var,dcpa,0], callnode, worklist)
            return True
    return False

def create_template(func, dcpa, c, worklist):
    # --- unseen cartesian product: create new template

    if not dcpa in func.cp: func.cp[dcpa] = {}
    func.cp[dcpa][c] = cpa = len(func.cp[dcpa]) # XXX +1

    #if not func.mv.module.builtin and not func.ident in ['__getattr__', '__setattr__']:
    #    print 'template', (func, dcpa), c

    getgx().templates += 1
    func_copy(func, dcpa, cpa, worklist, c)

def actuals_formals(expr, func, node, dcpa, cpa, types, worklist):
    objexpr, ident, direct_call, method_call, constructor, parent_constr = analyze_callfunc(expr)

    if expr.star_args: # XXX only in lib/
        formals = func.formals
        actuals = len(formals)*[expr.star_args]
        types = len(formals)*types
    else:
        actuals, formals, _, varargs, error = analyze_args(expr, func, node)
        if error:
            return

    for (actual, formal, formaltype) in zip(actuals, formals, types):
        formalnode = getgx().cnode[func.vars[formal], dcpa, cpa]

        if formaltype[1] != 0: # ifa: remember dataflow information for non-simple types
            if actual == None:
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
        addtoworklist(worklist, formalnode)

# --- iterative flow analysis: after each iteration, detect imprecisions, and split involved contours
def ifa():
    split = [] # [(set of creation nodes, new type number), ..]
    for cl in ifa_classes_to_split():
        if DEBUG: print 'IFA: --- class %s ---' % cl.ident
        cl.newdcpa = cl.dcpa
        vars = [cl.vars[name] for name in cl.tvar_names() if name in cl.vars]
        classes_nr, nr_classes = ifa_class_types(cl, vars)
        for dcpa in range(1, cl.dcpa):
            if ifa_split_vars(cl, dcpa, vars, nr_classes, classes_nr, split) != None:
                if DEBUG: print 'IFA found splits, return'
                return split
    if DEBUG: print 'IFA final return'
    return split

def ifa_split_vars(cl, dcpa, vars, nr_classes, classes_nr, split):
    for (varnum, var) in enumerate(vars):
        if not (var, dcpa, 0) in getgx().cnode:
            continue
        node = getgx().cnode[var, dcpa, 0]
        creation_points, paths, assignsets, allnodes, csites, emptycsites = ifa_flow_graph(cl, dcpa, node)
        if DEBUG: print 'IFA visit var %s.%s, %d, csites %d' % (cl.ident, var.name, dcpa, len(csites))
        if len(csites)+len(emptycsites) == 1:
            continue
        if ((len(merge_simple_types(getgx().types[node])) > 1 and len(assignsets) > 1) or \
            (assignsets and emptycsites)): # XXX move to split_no_conf
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
            if DEBUG: print 'IFA normal split, remaining:', len(remaining)
            for splitsites in remaining[1:]:
                ifa_split_class(cl, dcpa, splitsites, split)
            return split
        # --- if all else fails, perform wholesale splitting
        # XXX assign sets should be different; len(paths) > 1?
        if len(paths) > 1 and 1 < len(csites) < 10:
            if DEBUG: print 'IFA wholesale splitting, csites:', len(csites)
            for csite in csites[1:]:
                ifa_split_class(cl, dcpa, [csite], split)
            return split

def ifa_split_no_confusion(cl, dcpa, varnum, classes_nr, nr_classes, csites, emptycsites, allnodes, split):
    '''creation sites on single path: split them off, possibly reusing contour'''
    attr_types = list(nr_classes[dcpa])
    noconf = set([n for n in csites if len(n.paths)==1]+emptycsites)
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
            try: subtype_csites[subtype].append(node)
            except KeyError: subtype_csites[subtype] = [node]
    items = subtype_csites.items()
    if not others:
        items = items[1:]
    for subtype, csites in subtype_csites.iteritems(): # XXX items?
        if subtype in classes_nr: # reuse contour
            nr = classes_nr[subtype]
            split.append((cl, dcpa, csites, nr))
            cl.splits[nr] = dcpa
        else: # create new contour
            classes_nr[subtype] = cl.newdcpa
            ifa_split_class(cl, dcpa, csites, split)
    if DEBUG and subtype_csites:
        print 'IFA found simple split', subtype_csites.keys()

def ifa_class_types(cl, vars):
    ''' create table for previously deduced types '''
    classes_nr, nr_classes = {}, {}
    for dcpa in range(1, cl.dcpa):
        attr_types = [] # XXX merge with ifa_merge_contours.. sep func?
        for var in vars:
            if (var,dcpa,0) in getgx().cnode:
                attr_types.append(merge_simple_types(getgx().cnode[var,dcpa,0].types()))
            else:
                attr_types.append(frozenset())
        attr_types = tuple(attr_types)
        if DEBUG and [x for x in attr_types if x]:
            print 'IFA', str(dcpa)+':', zip([var.name for var in vars], map(list, attr_types))
        nr_classes[dcpa] = attr_types
        classes_nr[attr_types] = dcpa
    return classes_nr, nr_classes

def ifa_determine_split(node, allnodes):
    ''' determine split along incoming dataflow edges '''
    remaining = [incoming.csites.copy() for incoming in node.in_ if incoming in allnodes]
    # --- try to clean out larger collections, if subsets are in smaller ones
    for (i, seti) in enumerate(remaining):
        for setj in remaining[i+1:]:
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
    for ident in ['list', 'tuple', 'tuple2', 'dict', 'set', 'frozenset', 'deque', 'defaultdict', '__iter']:
        for cl in getgx().allclasses:
            if cl.mv.module.builtin and cl.ident == ident:
                cl.splits = {}
                classes.append(cl)
                break
    random.shuffle(classes)
    return classes

def ifa_confluence_point(node, creation_points):
    ''' determine if node is confluence point '''
    if len(node.in_) > 1 and isinstance(node.thing, variable):
        for csite in node.csites:
            occ = [csite in crpoints for crpoints in creation_points.values()].count(True)
            if occ > 1:
                return True
    return False

def ifa_flow_graph(cl, dcpa, node):
    creation_points, paths, assignsets = {}, {}, {}
    allnodes = set()
    csites = []

    # --- determine assignment sets
    for a in node.in_:
        types = getgx().types[a]
        if types:
            if a.thing in getgx().assign_target: # XXX *args
                target = getgx().cnode[getgx().assign_target[a.thing], a.dcpa, a.cpa]
                #print 'target', a, target, types
                assignsets.setdefault(merge_simple_types(types), []).append(target)

    # --- determine backflow paths and creation points per assignment set
    for assign_set, targets in assignsets.iteritems():
        path = backflow_path(targets, (cl,dcpa))
        paths[assign_set] = path
        allnodes.update(path)
        alloc = [n for n in path if not n.in_]
        creation_points[assign_set] = alloc

    # --- per node, determine paths it is located on
    for n in allnodes: n.paths = []
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
    allcsites = set()
    for n, types in getgx().types.iteritems():
        if (cl, dcpa) in types and not n.in_:
            allcsites.add(n)
    emptycsites = list(allcsites-set(csites))
    for n in emptycsites:
        n.paths = []

    return creation_points, paths, assignsets, allnodes, csites, emptycsites

def ifa_split_class(cl, dcpa, things, split):
    split.append((cl, dcpa, things, cl.newdcpa))
    cl.splits[cl.newdcpa] = dcpa
    cl.newdcpa += 1

# --- cartesian product algorithm (cpa) & iterative flow analysis (ifa)
def iterative_dataflow_analysis():
    print '[iterative type analysis..]'
    backup = backup_network()

    while True:
        getgx().iterations += 1
        if getgx().iterations > 30:
            print '\n*WARNING* reached maximum number of iterations'
            break

        # --- propagate using cartesian product algorithm
        getgx().new_alloc_info = {}
        #print 'table'
        #print '\n'.join([repr(e)+': '+repr(l) for e,l in getgx().alloc_info.items()])
        #print 'propagate'
        propagate()
        getgx().alloc_info = getgx().new_alloc_info

        # --- ifa: detect conflicting assignments to instance variables, and split contours to resolve these
        if DEBUG: print '\n*** iteration ***'
        else: sys.stdout.write('*'); sys.stdout.flush()
        split = ifa()
        if DEBUG and split: print 'IFA splits', [(s[0], s[1], s[3]) for s in split]

        if not split: # nothing has changed
            print '\niterations:', getgx().iterations, 'templates:', getgx().templates
            return

        # --- update alloc info table for split contours
        for cl, dcpa, nodes, newnr in split:
            for n in nodes:
                parent = parent_func(n.thing)
                if parent:
                    if n.dcpa in parent.cp:
                        for cart, cpa in parent.cp[n.dcpa].items(): # XXX not very fast
                            if cpa == n.cpa:
                                if parent.parent and isinstance(parent.parent, class_): # self
                                    cart = ((parent.parent, n.dcpa),)+cart

                                getgx().alloc_info[parent.ident, cart, n.thing] = (cl, newnr)
                                break

        beforetypes = backup[0]

        # --- clean out constructor node types in functions, possibly to be seeded again
        for node in beforetypes:
            if isinstance(parent_func(node.thing), function):
                if node.constructor and isinstance(node.thing, (List,Dict,Tuple,ListComp,CallFunc)):
                    beforetypes[node] = set()

        # --- create new class types, and seed global nodes
        for cl, dcpa, nodes, newnr in split:
            if newnr == cl.dcpa:
                class_copy(cl, newnr)
                cl.dcpa += 1

            #print 'split off', nodes, newnr
            for n in nodes:
                if not parent_func(n.thing):
                    beforetypes[n] = set([(cl,newnr)])

        # --- restore network
        restore_network(backup)

# --- seed allocation sites in newly created templates (called by function.copy())
def ifa_seed_template(func, cart, dcpa, cpa, worklist):
    if cart != None: # (None means we are not in the process of propagation)
        #print 'funccopy', func.ident #, func.nodes
        if isinstance(func.parent, class_): # self
            cart = ((func.parent, dcpa),)+cart

        for node in func.nodes:
            if node.constructor and isinstance(node.thing, (List, Dict, Tuple, ListComp, CallFunc)):
                # --- contour is specified in alloc_info
                parent = node.parent
                while isinstance(parent.parent, function): parent = parent.parent

                alloc_id = (parent.ident, cart, node.thing) # XXX ident?
                alloc_node = getgx().cnode[node.thing, dcpa, cpa]

                if alloc_id in getgx().alloc_info:
                    pass # print 'specified', func.ident, cart, alloc_node, alloc_node.callfuncs, getgx().alloc_info[alloc_id]
                # --- contour is newly split: copy allocation type for 'mother' contour; modify alloc_info
                else:
                    mother_alloc_id = alloc_id

                    for (id, c, thing) in getgx().alloc_info:
                        if id ==  parent.ident and thing is node.thing:
                            for a, b in zip(cart, c):
                                if a != b and not (isinstance(a[0], class_) and a[0] is b[0] and a[1] in a[0].splits and a[0].splits[a[1]] == b[1]):
                                    break
                            else:
                                mother_alloc_id = (id, c, thing)
                                break

                    #print 'not specified.. mother id:', mother_alloc_id
                    if mother_alloc_id in getgx().alloc_info:
                        getgx().alloc_info[alloc_id] = getgx().alloc_info[mother_alloc_id]
                        #print 'mothered', alloc_node, getgx().alloc_info[mother_alloc_id]
                    elif getgx().types[node]: # empty constructors that do not flow to assignments have no type
                        #print 'no mother', func.ident, cart, mother_alloc_id, alloc_node, getgx().types[node]
                        getgx().alloc_info[alloc_id] = list(getgx().types[node])[0]
                    else:
                        #print 'oh boy'
                        for (id, c, thing) in getgx().alloc_info: # XXX vhy?
                            if id == parent.ident and thing is node.thing:
                                mother_alloc_id = (id, c, thing)
                                getgx().alloc_info[alloc_id] = getgx().alloc_info[mother_alloc_id]
                                break

                if alloc_id in getgx().alloc_info:
                    getgx().new_alloc_info[alloc_id] = getgx().alloc_info[alloc_id]
                    getgx().types[alloc_node] = set()
                    #print 'seeding..', alloc_node, getgx().alloc_info[alloc_id], alloc_node.thing in getgx().empty_constructors
                    getgx().types[alloc_node].add(getgx().alloc_info[alloc_id])
                    addtoworklist(worklist, alloc_node)

                    if alloc_node.callfuncs: # XXX
                        getgx().checkcallfunc.append(alloc_node)

# --- for a set of target nodes of a specific type of assignment (e.g. int to (list,7)), flow back to creation points
def backflow_path(worklist, t):
    path = set(worklist)
    while worklist:
        new = []
        for node in worklist:
            for incoming in node.in_:
                if t in getgx().types[incoming]:
                    incoming.fout.add(node)

                    if not incoming in path:
                        path.add(incoming)
                        new.append(incoming)
        worklist = new
    return path

def flow_creation_sites(worklist, allnodes):
    while worklist:
        new = []
        for node in worklist:
            for out in node.fout:
                if out in allnodes:
                    difference = node.csites - out.csites

                    if difference:
                        out.csites.update(difference)
                        if not out in new:
                            new.append(out)
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
        node.fout = set() # XXX ?

    for var in getgx().allvars: # XXX we have to restore some variable constraint nodes.. remove vars?
        if not (var, 0, 0) in getgx().cnode:
            newnode = cnode(var, parent=var.parent)

    # --- clear templates
    for func in getgx().allfuncs:
        func.cp = {}

    for cl in getgx().modules['builtin'].classes.values():
        for func in cl.funcs.values():
            func.cp = {}
    for func in getgx().modules['builtin'].funcs.values():
        func.cp = {}

def merge_simple_types(types):
    merge = types.copy()
    if len(types) > 1 and (defclass('none'),0) in types:
        if not (defclass('int_'),0) in types and not (defclass('float_'),0) in types and not (defclass('bool_'),0) in types:
            merge.remove((defclass('none'),0))

    return frozenset(merge)

def analyze(source, testing=False):
    gc.set_threshold(23456, 10, 10)

    if testing:
        setgx(newgx())
        ast = parse(source+'\n')
    else:
        ast = graph.parsefile(source)

    mv = None
    setmv(mv)

    # --- build dataflow graph from source code
    getgx().main_module = graph.parse_module(getgx().main_mod, ast)
    getgx().main_module.filename = getgx().main_mod+'.py'
    getgx().modules[getgx().main_mod] = getgx().main_module
    mv = getgx().main_module.mv
    setmv(mv)

    # --- seed class_.__name__ attributes..
    for cl in getgx().allclasses:
        if cl.ident == 'class_':
            var = defaultvar('__name__', cl)
            getgx().types[inode(var)] = set([(defclass('str_'), 0)])

    # --- number classes (-> constant-time subclass check)
    cpp.number_classes()

    # --- non-ifa: copy classes for each allocation site
    for cl in getgx().allclasses:
        if cl.ident in ['int_','float_','none', 'class_','str_', 'bool_']:
            continue
        if cl.ident == 'list':
            cl.dcpa = len(getgx().list_types)+2
        elif cl.ident != '__iter': # XXX huh
            cl.dcpa = 2

        for dcpa in range(1, cl.dcpa):
            class_copy(cl, dcpa)

    var = defaultvar('unit', defclass('str_'))
    getgx().types[inode(var)] = set([(defclass('str_'), 0)])

    # --- cartesian product algorithm & iterative flow analysis
    iterative_dataflow_analysis()

    for cl in getgx().allclasses:
        for name in cl.vars:
            if name in cl.parent.vars and not name.startswith('__'):
                error("instance variable '%s' of class '%s' shadows class variable" % (name, cl.ident))

    getgx().merged_all = merged(getgx().types) #, inheritance=True)
    getgx().merge_dcpa = merged(getgx().types, dcpa=True)

    mv = getgx().main_module.mv
    setmv(mv)
    propagate() # XXX remove

    getgx().merged_all = merged(getgx().types) #, inheritance=True)
    getgx().merged_inh = merged(getgx().types, inheritance=True)

    # --- detect inheritance stuff
    cpp.upgrade_variables()
    getgx().merged_all = merged(getgx().types)
    getgx().merged_inh = merged(getgx().types, inheritance=True)

    cpp.analyze_virtuals()

    # --- check some sources of confusion # XXX can we remove this
    confusion_misc()

    getgx().merge_dcpa = merged(getgx().types, dcpa=True)
    getgx().merged_all = merged(getgx().types) #, inheritance=True) # XXX

    # --- determine which classes need an __init__ method
    for node, types in getgx().merged_all.items():
        if isinstance(node, CallFunc):
            objexpr, ident, _ , method_call, _, _ = analyze_callfunc(node)
            if method_call and ident == '__init__':
                for t in getgx().merged_all[objexpr]:
                    t[0].has_init = True

    # --- determine which classes need copy, deepcopy methods
    if 'copy' in getgx().modules:
        func = getgx().modules['copy'].funcs['copy']
        var = func.vars[func.formals[0]]
        for cl in set([t[0] for t in getgx().merged_inh[var]]):
            cl.has_copy = True # XXX transitive, modeling

        func = getgx().modules['copy'].funcs['deepcopy']
        var = func.vars[func.formals[0]]
        for cl in set([t[0] for t in getgx().merged_inh[var]]):
            cl.has_deepcopy = True # XXX transitive, modeling

    # --- add inheritance relationships for non-original Nodes (and tempvars?); XXX register more, right solution?
    for func in getgx().allfuncs:
        #if not func.mv.module.builtin and func.ident == '__init__':
        if func in getgx().inheritance_relations:
            for inhfunc in getgx().inheritance_relations[func]:
                for a, b in zip(func.registered, inhfunc.registered):
                    graph.inherit_rec(a, b, func.mv)

                for a, b in zip(func.registered_tempvars, inhfunc.registered_tempvars): # XXX more general
                    getgx().inheritance_tempvars.setdefault(a, []).append(b)

    getgx().merged_inh = merged(getgx().types, inheritance=True) # XXX why X times

    # error for dynamic expression (XXX before codegen)
    for node in getgx().merged_all:
        if isinstance(node, Node) and not isinstance(node, AssAttr) and not inode(node).mv.module.builtin:
            cpp.typesetreprnew(node, inode(node).parent)

    return getgx()
