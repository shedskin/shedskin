#!/usr/bin/env python

# *** SHED SKIN Python-to-C++ Compiler 0.0.26 ***
# Copyright 2005-2008 Mark Dufour; License GNU GPL version 3 (See LICENSE)

from compiler import *
from compiler.ast import *
from compiler.visitor import *

from shared import *
from graph import *
from cpp import *

import sys, string, copy, getopt, os.path, textwrap, traceback

# python2.3 compatibility
try: enumerate
except NameError:
    def enumerate(collection):
        i = 0
        it = iter(collection)
        while 1:
            yield (i, it.next())
            i += 1
try: set
except NameError:
    from sets import Set, ImmutableSet
    set = Set; frozenset = ImmutableSet

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

            #print 'itercopy', itercl.dcpa

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

    # --- copy tuple seed for varargs
    if func.varargs:
        var = func.vars[func.varargs]
        getgx().types[getgx().cnode[var,dcpa,cpa]] = getgx().types[inode(var)].copy()

    # --- iterative flow analysis: seed allocation sites in new template
    ifa_seed_template(func, cart, dcpa, cpa, worklist)



def singletype2(node, ident):
    return [t for t in inode(node).types() if t[0].ident == ident]


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

def cartesian(*lists):
    if not lists:
        return [()]
    result = []
    prod = cartesian(*lists[:-1])
    for x in prod:
        for y in lists[-1]:
            result.append(x + (y,))
    return result
  
def seed_nodes():
    for node in getgx().types:
        if isinstance(node.thing, Name):
            if node.thing.name in ['True', 'False']:
                getgx().types[node] = set([(defclass('int_'), 0)])
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
    #print 'worklist', worklist

    getgx().checkcallfunc = [] # XXX 

    # --- check whether seeded nodes are object/argument to call  
    changed = set()
    for w in worklist:
        for callfunc in w.callfuncs:
            #print 'seed changed', w.callfunc, w.dcpa, w.cpa
            changed.add(getgx().cnode[callfunc, w.dcpa, w.cpa])

    # --- statically bind calls without object/arguments 
    for node in getgx().types:
        expr = node.thing
        if isinstance(expr, CallFunc) and not expr.args:
            changed.add(node)

    for node in changed:
        cpa(node, worklist)

    # --- iterative dataflow analysis
    while worklist:
        a = worklist.pop(0)
        a.in_list = 0
         
        for b in a.out.copy(): # XXX kan veranderen...?
            # for builtin types, the set of instance variables is known, so do not flow into non-existent ones # XXX ifa
            if isinstance(b.thing, variable) and isinstance(b.thing.parent, class_) and b.thing.parent.ident in getgx().builtins:
                if b.thing.parent.ident in ['int_', 'float_', 'str_', 'none']: continue
                elif b.thing.parent.ident in ['list', 'tuple', 'frozenset', 'set', 'file','__iter'] and b.thing.name != 'unit': continue 
                elif b.thing.parent.ident == 'dict' and b.thing.name not in ['unit', 'value']: continue
                elif b.thing.parent.ident == 'tuple2' and b.thing.name not in ['unit', 'first', 'second']: continue

                #print 'flow', a, b #, difference #, difference, getgx().types[b], b.callfunc

            difference = getgx().types[a] - getgx().types[b]

            if difference:
                if isinstance(b.thing, variable) and b.thing.filter: # apply filter
                    #print 'aha', b.thing.filter, difference, [d for d in difference if d[0] in b.thing.filter] 
                    difference = set([d for d in difference if d[0] in b.thing.filter])

                getgx().types[b].update(difference)

                # --- flow may be constrained by run-time checks, e.g. isinstance(..) # XXX and by method calls
                #if (b.thing, 0, 0) in getgx().cnode: # XXX
                #    filters = getgx().cnode[b.thing, 0, 0].filters
                #    if filters:
                #        print 'filter', b.thing, filters
                #        getgx().types[b] = set([t for t in getgx().types[b] if t[0] in filters]) # XXX efficiency, inheritance

                # --- check whether node corresponds to actual argument: if so, perform cartesian product algorithm
                for callfunc in b.callfuncs:
                    #print 'id changed', b.callfunc, b.dcpa, b.cpa, getgx().types[b], a
                    cpa(getgx().cnode[callfunc, b.dcpa, b.cpa], worklist)

                addtoworklist(worklist, b)

                while getgx().checkcallfunc: # XXX
                    b = getgx().checkcallfunc.pop()
                    for callfunc in b.callfuncs:
                        cpa(getgx().cnode[callfunc, b.dcpa, b.cpa], worklist)


        
# --- determine cartesian product of possible function and argument types
def cartesian_product(node, worklist):
    expr = node.thing

    # --- determine possible target functions
    objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(expr, True)
    anon_func = False
    funcs = []

    if not node.mv.module.builtin or node.mv.module.ident == 'path': # XXX to analyze_callfunc
        subnode = expr.node, node.dcpa, node.cpa
        if subnode in getgx().cnode:
            stypes = getgx().cnode[subnode].types() 
            if [t for t in stypes if isinstance(t[0], function)]:
                anon_func = True

    if anon_func:
        # anonymous call 
        types = getgx().cnode[expr.node, node.dcpa, node.cpa].types()

        if types:
            if list(types)[0][0].parent: # method reference XXX merge below?
                funcs = [(f[0], f[1], (f[0].parent, f[1])) for f in types] # node.dcpa: connect to right dcpa duplicate version 
            else: # function reference
                funcs = [(f[0], f[1], None) for f in types] # function call: only one version; no objtype
        else:
            funcs = []

    elif constructor:
        funcs = [(t[0].funcs['__init__'], t[1], t) for t in node.types() if '__init__' in t[0].funcs]

    elif parent_constr:
        objtypes = getgx().cnode[lookupvar('self', node.parent), node.dcpa, node.cpa].types() 
        funcs = [(t[0].funcs[ident], t[1], None) for t in objtypes if ident in t[0].funcs]

    elif direct_call:
        funcs = [(direct_call, 0, None)]
    
        if ident == 'dict':
            clnames = [t[0].ident for t in getgx().cnode[expr.args[0],node.dcpa,node.cpa].types() if isinstance(t[0], class_)]
            if 'dict' in clnames or 'defaultdict' in clnames:
                funcs = [(node.mv.ext_funcs['__dict'], 0, None)]

    elif method_call:
        objtypes = getgx().cnode[objexpr, node.dcpa, node.cpa].types() 
        funcs = [(t[0].funcs[ident], t[1], t) for t in objtypes if ident in t[0].funcs]

    # --- argument types XXX connect_actuals_formals

    args = [arg for arg in expr.args if not isinstance(arg, Keyword)]
    keywords = [arg for arg in expr.args if isinstance(arg, Keyword)]

    kwdict = {}
    for kw in keywords: kwdict[kw.name] = kw.expr

    if expr.star_args: args.append(expr.star_args)
    if expr.dstar_args: args.append(expr.dstar_args)

    if funcs: # XXX return here
        func = funcs[0][0] # XXX
        if parent_constr: # XXX merge
            formals = [f for f in func.formals if not f in [func.varargs, func.kwargs]]
        else:
            formals = [f for f in func.formals if not f in ['self', func.varargs, func.kwargs]]
        uglyoffset = len(func.defaults)-(len(formals)-len(args))

        for (i, formal) in enumerate(formals[len(args):]):
            #print 'formal', i, formal
            if formal in kwdict:
                args.append(kwdict[formal])
                continue

            if not func.defaults: # XXX
                continue
            default = func.defaults[i+uglyoffset]
            args.append(default)

            if not node.defnodes:
                defnode = cnode((inode(node.thing),i), node.dcpa, node.cpa, parent=func)
                getgx().types[defnode] = set()

                defnode.callfuncs.append(node.thing)
                addconstraint(getgx().cnode[default, 0, 0], defnode, worklist)
        node.defnodes = True

    argtypes = [] # XXX
    for arg in args:
        if (arg, node.dcpa, node.cpa) in getgx().cnode:
            argtypes.append(getgx().cnode[arg,node.dcpa,node.cpa].types()) 
        else:
            argtypes.append(inode(arg).types()) # XXX def arg?

    #print 'argtypes', argtypes, node #, args, argtypes, cartesian(*([funcs]+argtypes))

    return cartesian(*([funcs]+argtypes))


# --- cartesian product algorithm; adds interprocedural constraints
def cpa(callnode, worklist):
    cp = cartesian_product(callnode, worklist) 
    if not cp: return

    objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(callnode.thing)

    # --- iterate over argument type combinations
    for c in cp:
        #print '(func, dcpa, objtype), c', c[0], c[1:]
        (func, dcpa, objtype), c = c[0], c[1:]

        if isinstance(func.parent, class_) and func.ident in func.parent.staticmethods:
            dcpa = 1

        if objtype: objtype = (objtype,)
        else: objtype = ()

        if ident == 'defaultdict' and len(callnode.thing.args) == 2:
            clnames = [x[0].ident for x in c if isinstance(x[0], class_)]
            if 'dict' in clnames or 'defaultdict' in clnames:
                func = list(callnode.types())[0][0].funcs['__initdict__'] 
            else:
                func = list(callnode.types())[0][0].funcs['__inititer__'] 

        # filter CPA terms using filters on formals
        if not func.mv.module.builtin and not func.ident in ['__getattr__', '__setattr__']:
            #print 'cpa term', func, c
            blocked = 0
            if objtype: formals = func.formals[1:]
            else: formals = func.formals
            for t, filter in zip(c, [func.vars[formal].filter for formal in formals]):
                if filter and t[0] not in filter:
                    #print 'cpa filter', func, c, t[0], filter
                    blocked = 1
                    break
            if blocked:
                continue

        # property
        callfunc = callnode.thing
        if isinstance(callfunc.node, Getattr) and callfunc.node.attrname in ['__setattr__', '__getattr__']:
            if isinstance(func.parent, class_) and callfunc.args and callfunc.args[0].value in func.parent.properties:
                arg = callfunc.args[0].value
                if callfunc.node.attrname == '__setattr__':
                    func = func.parent.funcs[func.parent.properties[arg][1]]
                else:
                    func = func.parent.funcs[func.parent.properties[arg][0]]
                c = c[1:]

        if (func,)+objtype+c in callnode.nodecp:
            continue 
        callnode.nodecp.add((func,)+objtype+c)

        if not dcpa in func.cp: func.cp[dcpa] = {}
        template_exists = c in func.cp[dcpa]
        if template_exists:
            pass
        else:
            # --- unseen cartesian product: create new template
            func.cp[dcpa][c] = cpa = len(func.cp[dcpa]) # XXX +1

            #if not func.mv.module.builtin and not func.ident in ['__getattr__', '__setattr__']:
            #    print 'template', (func, dcpa), c

            getgx().templates += 1
            func_copy(func, dcpa, cpa, worklist, c)

        cpa = func.cp[dcpa][c]

        # --- actuals and formals 
        if isinstance(callfunc.node, Getattr) and callfunc.node.attrname in ['__setattr__', '__getattr__']: # variables
            if isinstance(func.parent, class_) and callfunc.args and callfunc.args[0].value in func.parent.properties:
                actuals_formals(callfunc, func, callnode, dcpa, cpa, objtype+c, worklist)
            else:
                # builtin methods
                varname = callfunc.args[0].value
                #if varname in func.parent.funcs and callfunc.node.attrname == '__getattr__' and not callnode.parent_callfunc: # XXX
                #    getgx().types[callnode] = set([(func.parent.funcs[varname], objtype[0][1])])
                #    addtoworklist(worklist, callnode)
                #    getgx().method_refs.add(callnode.thing)
                #    continue

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

                continue
        else: 
            # non-builtin methods, functions
            actuals_formals(callfunc, func, callnode, dcpa, cpa, objtype+c, worklist)

        # --- call and return expressions
        if func.retnode and not constructor:
            retnode = getgx().cnode[func.retnode.thing, dcpa, cpa]
            addconstraint(retnode, callnode, worklist)

def actuals_formals(expr, func, node, dcpa, cpa, types, worklist):
    objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(expr) # XXX call less

    actuals = [a for a in expr.args if not isinstance(a, Keyword)]
    formals = [f for f in func.formals if not f in [func.varargs, func.kwargs]]
    keywords = [a for a in expr.args if isinstance(a, Keyword)]

    if ident in ['__getattr__', '__setattr__']:
        actuals = actuals[1:]

    anon_func = False
    meth_func = False
    if not node.mv.module.builtin: # XXX to analyze_callfunc
        subnode = expr.node, node.dcpa, node.cpa
        if subnode in getgx().cnode:
            stypes = getgx().cnode[subnode].types() 
            if [t for t in stypes if isinstance(t[0], function)]:
                anon_func = True
            if [t for t in stypes if isinstance(t[0], function) and t[0].parent]:
                meth_func = True

    # --- check for correct number of arguments
   
    # add a slot in case of implicit 'self'
    smut = actuals[:] # XXX smut unneeded
    if meth_func:
        smut = [None]+smut # XXX add type here
    if parent_constr or anon_func:
        pass
    elif method_call or constructor:
        smut = [None]+smut # XXX add type here
    elif not direct_call: # XXX ?
        types2 = getgx().cnode[expr.node, node.dcpa, node.cpa].types()
        if list(types2)[0][0].parent: 
            smut = [None]+smut

    for formal in formals:
        for kw in keywords:
            if formal == kw.name:
                actuals.append(kw.expr)
                smut.append(kw.expr)

    # XXX add defaults to smut here, simplify code below
    if not ident in ['min','max','bool'] and not (expr.star_args or expr.dstar_args or func.varargs or func.kwargs) and (len(smut) < len(formals)-len(func.defaults) or len(smut) > len(formals)): # XXX star_args etc. XXX keywords <-> defaults
        return

    # --- connect/seed as much direct arguments as possible

    if len(smut) < len(formals):
        smut = smut + func.defaults[-len(formals)+len(smut):]

    #print 'aft', types #expr, smut, formals, types, zip(smut, formals, types)

    for (actual, formal, formaltype) in zip(smut, formals, types):
        #print 'connect', actual, formal, formaltype, node
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

def nodetypes(node):
    return list(set(inode(node).types()))

def merge_identical_types():
    pass

# --- XXX description, confusion_misc?
def confusion_misc(): 
    confusion = set()

    # --- tuple2

    # use regular tuple if both elements have the same type representation
    cl = defclass('tuple')
    var1 = lookupvar('first', cl)
    var2 = lookupvar('second', cl)
    if not var1 or not var2: return # XXX ?

    for dcpa in getgx().tuple2.copy():
        getgx().tuple2.remove(dcpa)

    # use regular tuple template for tuples used in addition
    for node in getgx().merged_all:
        if isinstance(node, CallFunc):
            if isinstance(node.node, Getattr) and node.node.attrname in ['__add__','__iadd__'] and not isinstance(node.args[0], Const):

                tupletypes = set()
                for types in [getgx().merged_all[node.node.expr], getgx().merged_all[node.args[0]]]:
                    for t in types: 
                        if t[0].ident == 'tuple':  
                            if t[1] in getgx().tuple2:
                                getgx().tuple2.remove(t[1])
                                getgx().types[getgx().cnode[var1, t[1], 0]].update(getgx().types[getgx().cnode[var2, t[1], 0]])

                            tupletypes.update(getgx().types[getgx().cnode[var1, t[1], 0]])

# --- determine virtual methods and variables
def analyze_virtuals(): 
    for node in getgx().merged_inh: # XXX all:
        # --- for every message
        if isinstance(node, CallFunc) and not inode(node).mv.module.builtin: #ident == 'builtin':
            objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(node)
            if not method_call or objexpr not in getgx().merged_inh: 
                continue # XXX

            # --- determine abstract receiver class
            classes = polymorphic_t(getgx().merged_inh[objexpr]) 
            if not classes:
                continue

            if isinstance(objexpr, Name) and objexpr.name == 'self': 
                abstract_cl = inode(objexpr).parent.parent
            else:
                lcp = lowest_common_parents(classes)
                lcp = [x for x in lcp if isinstance(x, class_)] # XXX 
                if not lcp:
                    continue
                abstract_cl = lcp[0] 

            if not abstract_cl or not isinstance(abstract_cl, class_):
                continue 
            subclasses = [cl for cl in classes if subclass(cl, abstract_cl)] 

            # --- register virtual method
            if not ident.startswith('__'):  
                redefined = False
                for concrete_cl in classes:
                    if [cl for cl in concrete_cl.ancestors_upto(abstract_cl) if ident in cl.funcs and not cl.funcs[ident].inherited]:
                        redefined = True

                if redefined:
                    abstract_cl.virtuals.setdefault(ident, set()).update(subclasses)

            # --- register virtual var
            elif ident in ['__getattr__','__setattr__'] and subclasses:      
                var = defaultvar(node.args[0].value, abstract_cl)
                abstract_cl.virtualvars.setdefault(node.args[0].value, set()).update(subclasses)


# --- merge variables assigned to via 'self.varname = ..' in inherited methods into base class
def upgrade_variables():
    for node, inheritnodes in getgx().inheritance_relations.items():
        if isinstance(node, AssAttr): 
            baseclass = inode(node).parent.parent
            inhclasses = [inode(x).parent.parent for x in inheritnodes]
            var = defaultvar(node.attrname, baseclass)

            for inhclass in inhclasses:
                inhvar = lookupvar(node.attrname, inhclass)

                if (var, 1, 0) in getgx().cnode:
                    newnode = getgx().cnode[var,1,0]
                else:
                    newnode = cnode(var, 1, 0, parent=baseclass)
                    getgx().types[newnode] = set()

                if inhvar in getgx().merged_all: # XXX ?
                    getgx().types[newnode].update(getgx().merged_all[inhvar])


def subclass(a, b):
    if b in a.bases:
        return True
    else:
        return a.bases and subclass(a.bases[0], b) # XXX mult inh

# --- iterative flow analysis: after each iteration, detect imprecisions, and split involved contours
def ifa():
    split = [] # [(set of creation nodes, new type number), ..]
    redundant = {} # {redundant contour: similar contour we will map it to}
    removals = [] # [removed contour, ..]

    classes = [defclass('list'), defclass('tuple'), defclass('tuple2'), defclass('dict'), defclass('set'),defclass('frozenset')]+[cl for cl in getgx().allclasses if cl.ident not in ['str_','int_','float_','none','pyseq','pyset','class_','list','tuple','tuple2','dict','set','frozenset']]

    for cl in classes:
        cl.splits = {}

    #print '\n*** iteration ***'
    sys.stdout.write('*')
    sys.stdout.flush()

    for cl in classes:
        if getgx().avoid_loops and cl.ident not in ['str_','int_','float_','none','pyiter','pyseq','class_','list','tuple','tuple2','dict','set', '__iter']:
            continue

        if split or redundant or removals:   
            return split, redundant, removals
            
        #print '---', cl.ident
        newdcpa = cl.dcpa 

        # --- determine instance variables XXX kill
        if cl.ident in ['list', 'tuple', 'frozenset', 'set','__iter']:
            names = ['unit']
        elif cl.ident == 'tuple2':
            names = ['first', 'second']
        elif cl.ident == 'dict':
            names = ['unit', 'value']
        else:
            names = [name for name in cl.vars if not name.startswith('__')]
        vars = [cl.vars[name] for name in names if name in cl.vars]

        #print 'vars', vars

        unused = cl.unused[:]

        # --- create table for previously deduced types: class set -> type nr; remove redundant types
        classes_nr = {}
        nr_classes = {}
        for dcpa in range(1, cl.dcpa):
            if dcpa in unused: continue

            attr_types = [] # XXX merge with ifa_merge_contours.. sep func?
            for var in vars:
                if (var,dcpa,0) in getgx().cnode:
                    attr_types.append(merge_simple_types(getgx().cnode[var,dcpa,0].types()))
                else:
                    attr_types.append(frozenset())
            attr_types = tuple(attr_types)

            #if cl.ident == 'node':
            #    print str(dcpa)+':', zip(vars, attr_types)
            nr_classes[dcpa] = attr_types
            classes_nr[attr_types] = dcpa

        #print 'unused', cl.unused
        if redundant or cl.splits: # investigate cl.splits.. suppose contour 3->5 and 1->5 splits.. 5->mother?
            #print 'skip class..', redundant, cl.splits
            continue

        # --- examine each contour:
        #     split contours on imprecisions; merge contours when reverse dataflow is unambiguous

        for dcpa in range(1, cl.dcpa):
            if dcpa in unused: continue
            #print 'examine pre', dcpa

            attr_types = nr_classes[dcpa]

            for (varnum, var) in enumerate(vars):
                if not (var, dcpa, 0) in getgx().cnode: continue
                  
                #if cl.ident == 'node':
                #    print 'var', var

                # --- determine assignment sets for this contour
                node = getgx().cnode[var, dcpa, 0]
                assignsets = {} # class set -> targets
                alltargets = set()

                for a in node.in_:
                    types = getgx().types[a]
                    if types:
                        if a.thing in getgx().assign_target: # XXX *args
                            target = getgx().cnode[getgx().assign_target[a.thing], a.dcpa, a.cpa]
                            #print 'target', a, target, types
                            alltargets.add(target)
                            assignsets.setdefault(merge_simple_types(types), []).append(target) 

                #print 'assignsets', (cl.ident, dcpa), assignsets
                #print 'examine contour', dcpa

                bah = set() # XXX coarse recursion check
                for ass in assignsets:
                    bah.update(ass)
                if cl.ident not in getgx().builtins:
                    if not [c for c, _ in bah if c.ident not in (cl.ident, 'none')]:
                        #print 'buggert!'
                        continue

                #print 'assignsets', (cl.ident, dcpa), assignsets

                # --- determine backflow paths and creation points per assignment set
                paths = {}
                creation_points = {}
                for assign_set, targets in assignsets.items():
                    #print 'assignset', assign_set, targets
                    path = backflow_path(targets, (cl,dcpa))
                    #print 'path', path

                    paths[assign_set] = path
                    alloc = [n for n in path if not n.in_]
                    creation_points[assign_set] = alloc

                #print 'creation points', creation_points

                # --- collect all nodes
                allnodes = set()
                for path in paths.values(): 
                   allnodes.update(path)
                endpoints = [huh for huh in allnodes if not huh.in_] # XXX call csites
                #print 'endpoints', endpoints

                # --- split off empty assignment sets (eg, [], or [x[0]] where x is None in some template)
                if assignsets and cl.ident in ['list', 'tuple']: # XXX amaze, msp_ss
                    allcsites = set()
                    for n, types in getgx().types.items():
                        if (cl, dcpa) in types and not n.in_:
                            allcsites.add(n)

                    empties = list(allcsites-set(endpoints))
                    #print 'EMPTIES', empties, assignsets

                    if empties:
                        split.append((cl, dcpa, empties, newdcpa))
                        cl.splits[newdcpa] = dcpa
                        newdcpa += 1
                        #return split, redundant, removals

                if len(merge_simple_types(getgx().types[node])) < 2 or len(assignsets) == 1:
                    #print 'singleton set'
                    continue

                # --- per node, determine paths it is located on
                for n in allnodes: n.paths = []

                for assign_set, path in paths.items():
                    for n in path:
                        n.paths.append(assign_set)

                # --- for each node, determine creation points that 'flow' through it
                csites = []
                for n in allnodes: 
                    n.csites = set()
                    if not n.in_: # and (n.dcpa, n.cpa) != (0,0): # XXX
                        n.csites.add(n)
                        csites.append(n)
                flow_creation_sites(csites, allnodes)
            
                if len(csites) == 1:
                    #print 'just one creation site!'
                    continue
                
                # --- determine creation nodes that are only one one path
                noconf = set() 
                for node in csites: #allnodes:
                    #if not node.in_ and len(node.paths) == 1:
                    #print 'noconf', node, node.paths
                    if len(node.paths) == 1:
                        noconf.add(node)
                        #print 'no confusion about:', node, node.paths[0], node.parent

                # --- for these, see if we can reuse existing contours; otherwise, create new contours
                removed = 0
                nr_of_nodes = len(noconf)
                for node in noconf:
                    #assign_set = set()
                    #for path in node.paths:
                    #    assign_set.update(path)
                    #assign_set = frozenset(assign_set)
                    assign_set = node.paths[0]

                    new_attr_types = list(attr_types)
                    new_attr_types[varnum] = assign_set
                    #print 'new type', tuple(new_attr_types)
                    new_attr_types = tuple(new_attr_types)
                     
                    if new_attr_types in classes_nr and (not [len(types)==1 and list(types)[0][0].ident in ['float_','str_','int_'] for types in new_attr_types if types].count(False) or classes_nr[new_attr_types] >= cl.dcpa): # XXX last check.. useful or not?
                        nr = classes_nr[new_attr_types]
                        if nr != dcpa: # XXX better check: classes_nr for dcpa
                            #print 'reuse', node, nr
                            split.append((cl, dcpa, [node], nr))
                            cl.splits[nr] = dcpa
                            
                            removed += 1
                        #else: 
                        #    print 'doh!!'
                    else: 
                        #print 'new!', node, newdcpa

                        classes_nr[new_attr_types] = newdcpa

                        split.append((cl, dcpa, [node], newdcpa))
                        cl.splits[newdcpa] = dcpa
                        newdcpa += 1

                        nr_of_nodes -= 1
                        removed += 1

                # --- remove contour if it becomes empty 
                if removed == len([node for node in allnodes if not node.in_]):
                    #print 'remove contour', dcpa
                    cl.unused.append(dcpa)
                    removals.append((cl,dcpa))
                
                if split: # XXX
                    break
                #print 'check confluence'

                # --- object contour splitting

                #print 'hoep?', cl.ident

                for node in allnodes:
                    # --- determine if node is a confluence point

                    conf_point = False
                    if len(node.in_) > 1 and isinstance(node.thing, variable):
                        #print 'possible confluence', node, node.csites
                        for csite in node.csites:
                            occ = [csite in crpoints for crpoints in creation_points.values()].count(True)
                            if occ > 1:
                                conf_point = True
                                break
                    if not conf_point:
                        continue

                    if not node.thing.formal_arg and not isinstance(node.thing.parent, class_):
                        #print 'bad split', node
                        continue

                    # --- determine split along incoming dataflow edges

                    #print 'confluence point', node, node.paths #, node.in_

                    remaining = [incoming.csites.copy() for incoming in node.in_ if incoming in allnodes]
                    #print 'remaining before', remaining

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
                    #print 'remaining after', remaining
                    
                    if len(remaining) < 2:
                        #print "one rem"
                        continue

                    # --- if it exists, perform actual splitting
                    #print 'split rem', remaining
                    for splitsites in remaining[1:]:
                        #print 'splitsites', splitsites

                        split.append((cl, dcpa, splitsites, newdcpa))
                        cl.splits[newdcpa] = dcpa
                        newdcpa += 1

                    return split, redundant, removals 
                
                # --- if all else fails, perform wholesale splitting
                # XXX assign sets should be different; len(paths) > 1?

                #print 'wholesale!', cl.ident, dcpa, assignsets

                if len(paths) > 1 and len(csites) > 1:
                    #print 'no confluence..split all?'
                    #print paths.keys(), csites

                    for csite in csites[1:]:
                        #print 'splitsites', splitsites

                        split.append((cl, dcpa, [csite], newdcpa))
                        cl.splits[newdcpa] = dcpa
                        newdcpa += 1

                    return split, redundant, removals

    return split, redundant, removals

# --- cartesian product algorithm (cpa) & iterative flow analysis (ifa)
def iterative_dataflow_analysis():
    print '[iterative type analysis..]'

    removed = []

    # --- backup constraint network 
    backup = backup_network()

    while True:
        getgx().iterations += 1
        # --- propagate using cartesian product algorithm

        getgx().new_alloc_info = {}

        #print 'table'
        #print '\n'.join([repr(e)+': '+repr(l) for e,l in getgx().alloc_info.items()])
        #print 'propagate'

        propagate()
        #printstate()

        getgx().alloc_info = getgx().new_alloc_info

        # --- ifa: detect conflicting assignments to instance variables, and split contours to resolve these
        split, redundant, removed = ifa()
        #if split: print 'splits', [(s[0], s[1], s[3]) for s in split]

        if not (split or redundant): # nothing has changed XXX 
            print '\niterations:', getgx().iterations, 'templates:', getgx().templates
            return

        # --- update alloc info table for split contours
        #print 'splits:', defclass('list').splits

        for cl, dcpa, nodes, newnr in split: 
            #print 'split', cl, dcpa, nodes, newnr

            for n in nodes:
                parent = parent_func(n.thing)
                if parent:
                    #print 'parent', n, parent, parent.cp
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

        # --- update constraint network and alloc info table for redundant contours
        if redundant:
            #print 'redundant', redundant

            for node, types in beforetypes.items():
                if not parent_func(node.thing):
                    newtypes = []
                    for t in types:
                        if t in redundant:
                            newtypes.append((t[0], redundant[t]))
                        else:
                            newtypes.append(t)
                    beforetypes[node] = set(newtypes)

            new_info = {}
            for (parent, cart, thing), x in getgx().alloc_info.items():
                remove = False
                new_cart = []
                for t in cart: 
                    if t in redundant: 
                        new_cart.append((t[0], redundant[t]))
                    else:
                        new_cart.append(t)

                if x in redundant: 
                    x = (x[0], redundant[x])

                new_info[parent, tuple(new_cart), thing] = x
            getgx().alloc_info = new_info

        # --- create new class types, and seed global nodes 
        for cl, dcpa, nodes, newnr in split: 
            if newnr == cl.dcpa:
                class_copy(cl, newnr)
                cl.dcpa += 1

            #print 'split off', nodes, newnr
            for n in nodes:
                if not parent_func(n.thing):
                    beforetypes[n] = set([(cl,newnr)])
                    #print 'seed global', n, (cl,newnr)

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
                #print 'constr', node

                # --- contour is specified in alloc_info
                parent = node.parent
                while isinstance(parent.parent, function): parent = parent.parent

                alloc_id = (parent.ident, cart, node.thing) # XXX ident?
                alloc_node = getgx().cnode[node.thing, dcpa, cpa]

                if alloc_id in getgx().alloc_info:
                    pass #    print 'specified', func.ident, cart, alloc_node, alloc_node.callfuncs, getgx().alloc_info[alloc_id]

                # --- contour is newly split: copy allocation type for 'mother' contour; modify alloc_info
                else:
                    mother_alloc_id = alloc_id

                    for (id, c, thing) in getgx().alloc_info:
                        if id ==  parent.ident and thing is node.thing:
                            okay = True
                            for a, b in zip(cart, c):
                                if a == b:
                                    pass #print 'eq', a, b
                                elif isinstance(a[0], class_) and a[0] is b[0] and a[1] in a[0].splits and a[0].splits[a[1]] == b[1]: 
                                    pass #print 'inh', a, b
                                else:
                                    okay = False
                                    break 
                            if okay:
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
                        #assert false

                    #if alloc_id in getgx().alloc_info: # XXX faster
                    #    print 'seed', func.ident, cart, alloc_node, getgx().alloc_info[alloc_id]

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
        merge.remove((defclass('none'),0))

    return frozenset(merge)

def merge_simple_types2(types):
    merge = types.copy()
    if len(types) > 1 and (defclass('none'),0) in types:
        merge.remove((defclass('none'),0))

    return frozenset(merge)

# --- iterative filter application/propagation
def apply_filters(types, merge):
    # XXX x = 1, x = [] etc.
    # XXX y = x+1, self.a = x.meth(), expr.a = x.meth() -> retvals
    # XXX y = expr.meth().meth() -> retvals

    print 'ass', getgx().assignments

    changed = 1
    while changed:
        changed = 0
        
        # --- initial filters, flow across function call
        for node in types: # XXX
            if node.thing in merge and not node.mv.module.builtin: 

                # --- var.a: limit builtins to have method named 'a'
                if isinstance(node.thing, Getattr) and isinstance(node.thing.expr, Name): # XXX out
                    if not inode(node.thing).fakert:
                        #print 'GETATTR', node.thing, inode(node.thing).fakert
                        var = lookupvar(node.thing.expr.name, node.parent)
                        filter = set([cl for cl in getgx().allclasses if not cl.mv.module.builtin or node.thing.attrname in cl.funcs])
                        if filter_flow(filter, var):
                            changed = 1
                            print 'getattr filter', var, var.filter, node.thing

                # --- var.a(): limit classes to have method named 'a'
                if isinstance(node.thing, CallFunc):
                    if isinstance(node.thing.node, Getattr) and node.thing.node.attrname.startswith('__') and node.thing.node.attrname in ['__getattr__', '__setattr__', '__str__', '__repr__', '__getfirst__', '__getsecond__', '__hash__', '__cmp__', '__eq__', '__ne__', '__le__', '__lt__', '__ge__', '__gt__']: # XXX
                        continue

                    #print node.thing, merge[node.thing]
                    objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(node.thing)
                    # --- var.meth() -> setup filter for var (can only be of class that implements 'meth')
                    if method_call:
                        #print 'method call', objexpr, ident

                        # name.meth()
                        if isinstance(objexpr, Name): # XXX move out of iter loop?
                            var = lookupvar(objexpr.name, node.parent)
                            #print 'on var', var
                            filter = set([cl for cl in getgx().allclasses if ident in cl.funcs])
                            #print 'filter', filter
                            if filter_flow(filter, var):
                                changed = 1
                                print 'var filter', var, var.filter, node.thing

                        # self.var.meth()
                        elif isinstance(objexpr, Getattr) and isinstance(objexpr.expr, Name) and objexpr.expr.name == 'self' and node.parent and node.parent.parent:
                            var = defaultvar(objexpr.attrname, node.parent.parent)
                            filter = set([cl for cl in getgx().allclasses if ident in cl.funcs])
                            if filter_flow(filter, var):
                                changed = 1
                                print 'self.var filter', node.thing, var, filter

                    # --- propagate filters along backward variable flow
                    targets = callfunc_targets(node.thing, merge)

                    if method_call and isinstance(objexpr, Name): # minimize targets with _new_ filters
                        var = lookupvar(objexpr.name, node.parent) 
                        if var.filter:
                            #print 'filter targets', node.thing, targets, var.filter

                            if targets: targetcls = set([target.parent for target in targets]) & var.filter
                            else: targetcls = var.filter

                            newtargets = [cl.funcs[ident] for cl in targetcls]
                            #if not targets or len(newtargets) < len(targets):
                            #    print 'filtered targets', node.thing, newtargets
                            targets = newtargets

                    if not [t for t in targets if t.mv.module.builtin]:
                        filters = [[] for i in range(len(node.thing.args))] 
                        # --- determine filters per 'variable' argument per target
                        for target in targets:
                            #print 'target:', target
                            pairs = connect_actual_formal(node.thing, target)
                            for ((a,b), f) in zip(pairs, filters):
                                if isinstance(a, Name): # XXX expr.a
                                    var, filter = lookupvar(a.name, node.parent), b.filter
                                    f.append(b.filter)

                        # --- OR filters per 'variable' argument and propagate
                        for arg, filter in zip(node.thing.args, filters):
                            if isinstance(arg, Name): # XXX expr.a
                                if filter and not [f for f in filter if not f]:
                                    orfilter = reduce(lambda x,y: x|y, filter)
                                    var = lookupvar(arg.name, node.parent)
                                    #print 'or filter:', var, orfilter
                                    if filter_flow(orfilter, var):
                                        changed = 1
                                        print 'prop filter', var, var.filter, node.thing

        # --- variable assignment flow
        for lvar, rvar in getgx().assignments:
            if isinstance(lvar, variable) and filter_flow(lvar.filter, rvar):
                changed = 1
                print 'flow filter', lvar, rvar

def filter_flow(filter, var):
    if not filter:
        return 0
    elif not var.filter: 
        var.filter = filter
        return 1
    elif len(var.filter & filter) < len(var.filter): 
        var.filter &= filter
        return 1
    return 0

def analysis(source, testing=False):
    if testing: 
        gx = newgx()
        setgx(gx)
        ast = parse(source+'\n')
    else:
        gx = getgx()
        ast = parsefile(source)

    mv = None
    setmv(mv)

    # --- build dataflow graph from source code
    gx.main_module = parse_module(gx.main_mod, ast)
    gx.main_module.filename = gx.main_mod+'.py'
    gx.modules[gx.main_mod] = gx.main_module
    mv = gx.main_module.mv
    setmv(mv)

    # --- seed class_.__name__ attributes..
    for cl in getgx().allclasses:
        if cl.ident == 'class_':
            var = defaultvar('__name__', cl)
            getgx().types[inode(var)] = set([(defclass('str_'), 0)])

    # --- number classes (-> constant-time subclass check)
    number_classes()

    # --- non-ifa: copy classes for each allocation site
    for cl in getgx().allclasses:
        if cl.ident in ['int_','float_','none', 'class_','str_']: continue

        if cl.ident == 'list':
            cl.dcpa = len(getgx().list_types)+2
        elif cl.ident == '__iter': # XXX huh
            pass
        else:
            cl.dcpa = 2

        for dcpa in range(1, cl.dcpa): 
            class_copy(cl, dcpa)

    var = defaultvar('unit', defclass('str_'))
    getgx().types[inode(var)] = set([(defclass('str_'), 0)])

    #printstate()
    #printconstraints()

    # --- filters
    #merge = merged(getgx().types)
    #apply_filters(getgx().types.copy(), merge)
   
    # --- cartesian product algorithm & iterative flow analysis
    iterative_dataflow_analysis()
    #propagate()

    #merge = merged(getgx().types)
    #apply_filters(getgx().types, merge)

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

    # --- determine template parameters
    template_parameters()

    # --- detect inheritance stuff
    upgrade_variables()
    getgx().merged_all = merged(getgx().types)

    getgx().merged_inh = merged(getgx().types, inheritance=True)

    analyze_virtuals()

    # --- determine integer/float types that cannot be unboxed
    confused_vars()
    # --- check other sources of confusion
    confusion_misc() 

    getgx().merge_dcpa = merged(getgx().types, dcpa=True)
    getgx().merged_all = merged(getgx().types) #, inheritance=True) # XXX

    # --- determine which classes need an __init__ method
    for node, types in getgx().merged_all.items():
        if isinstance(node, CallFunc):
            objexpr, ident, _ , method_call, _, _, _ = analyze_callfunc(node)
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
            #print 'inherited from', func, getgx().inheritance_relations[func]
            for inhfunc in getgx().inheritance_relations[func]:
                for a, b in zip(func.registered, inhfunc.registered):
                    #print a, '->', b 
                    inherit_rec(a, b)

    # --- finally, generate C++ code and Makefiles.. :-)

    #printstate()
    #printconstraints()
    generate_code()
    #generate_bindings()

    #print 'cnode!'
    #for (a,b) in getgx().cnode.items():
    #    print a, b
   # for (a,b) in getgx().types.items():
   #     print a, b

    # error for dynamic expression (XXX before codegen)
    for node in getgx().merged_all:
        if isinstance(node, Node) and not isinstance(node, AssAttr) and not inode(node).mv.module.builtin:
            typesetreprnew(node, inode(node).parent) 

    return gx

# --- generate C++ and Makefiles
def generate_code():
    print '[generating c++ code..]'

    getgx().dirs.setdefault('',[]).append(getgx().main_module)

    ident = getgx().main_module.ident 

    if sys.platform == 'win32':
        pyver = '%d%d' % sys.version_info[:2]
    else:
        includes = os.popen4('python-config --includes')[1].read().strip()
        ldflags = os.popen4('python-config --ldflags')[1].read().strip()

    if getgx().extension_module: 
        if sys.platform == 'win32': ident += '.pyd'
        else: ident += '.so'

    # --- repeat for each directory:
    for dir, mods in getgx().dirs.items():
        # --- generate C++ files
        for module in mods:
            if not module.builtin:
                gv = generateVisitor(module)
                mv = module.mv 
                setmv(mv)
                gv.func_pointers(False)
                walk(module.ast, gv)
                gv.out.close()
                gv.header_file()
                gv.out.close()
                gv.insert_consts(declare=False)
                gv.insert_consts(declare=True)

        # --- generate Makefile
        makefile = file(connect_paths(dir, 'Makefile'), 'w')

        cppfiles = ' '.join([m.filename[:-3].replace(' ', '\ ')+'.cpp' for m in mods])
        hppfiles = ' '.join([m.filename[:-3].replace(' ', '\ ')+'.hpp' for m in mods])

        # import flags
        if getgx().flags: flags = getgx().flags
        elif os.path.isfile('FLAGS'): flags = 'FLAGS'
        else: flags = connect_paths(getgx().sysdir, 'FLAGS')

        for line in file(flags):
            line = line[:-1]

            if line[:line.find('=')].strip() == 'CCFLAGS': 
                line += ' -I'+getgx().libdir.replace(' ', '\ ')
                if not getgx().wrap_around_check: line += ' -DNOWRAP' 
                if getgx().bounds_checking: line += ' -DBOUNDS' 
                if getgx().extension_module: 
                    if sys.platform == 'win32': line += ' -Ic:/Python%s/include -D__SS_BIND' % pyver
                    else: line += ' -g -fPIC -D__SS_BIND ' + includes

            elif line[:line.find('=')].strip() == 'LFLAGS': 
                if getgx().extension_module: 
                    if sys.platform == 'win32': line += ' -shared -Lc:/Python%s/libs -lpython%s' % (pyver, pyver) 
                    elif sys.platform == 'darwin': line += ' -bundle -Xlinker -dynamic ' + ldflags
                    else: line += ' -shared -Xlinker -export-dynamic ' + ldflags
                if 're' in [m.ident for m in mods]:
                    line += ' -lpcre'

            print >>makefile, line
        print >>makefile

        print >>makefile, 'all:\t'+ident+'\n'

        if not getgx().extension_module:
            print >>makefile, 'run:\tall'
            print >>makefile, '\t./'+ident+'\n'

            print >>makefile, 'full:'
            print >>makefile, '\tss '+ident+'; $(MAKE) run\n'

        print >>makefile, 'CPPFILES='+cppfiles
        print >>makefile, 'HPPFILES='+hppfiles+'\n'

        print >>makefile, ident+':\t$(CPPFILES) $(HPPFILES)'
        print >>makefile, '\t$(CC) $(CCFLAGS) $(CPPFILES) $(LFLAGS) -o '+ident+'\n'

        if sys.platform == 'win32':
            ident += '.exe'
        print >>makefile, 'clean:'
        print >>makefile, '\trm '+ident

        makefile.close()

def generate_bindings():
    for dir, mods in getgx().dirs.items():
        for mod in mods:
            if mod.builtin and not os.path.isfile(mod.ident+'_.hpp'):
                ident = mod.ident
                print 'generate!', ident

                gv = generateVisitor(mod)
                mv = mod.mv 
                setmv(mv)

                # --- generate *_.cpp file
                gv.output('#include <Python.h>\n#include "%s_.hpp"\n\nnamespace __%s__ {\n' % (ident, ident)) 
                gv.output('PyObject '+', '.join(['*__'+x for x in mod.funcs.keys()+mod.classes.keys()])+';\n')

                # class bindings
                for cl in mod.classes.values():
                    gv.visitm('/**', 'class %s' % cl.ident, '*/', None)
                    for func in cl.funcs.values():
                        if func.ident not in ['__getattr__', '__setattr__']:
                            bind_function(gv, func)

                # function bindings
                for func in mod.funcs.values():
                    bind_function(gv, func)

                # __init
                gv.output('void __init() {\n    '+'\n    '.join(['__%s = __import("%s", "%s");' % (x, ident, x) for x in mod.funcs.keys()+mod.classes.keys()])+'\n\n}\n')

                gv.output('} // namespace __%s__' % ident)
                gv.out.close()

                gv.out = file(mod.filename[:-3]+'.hpp','w')

                # --- generate *_.hpp file
                gv.output('#ifndef __%s_HPP\n#define __%s_HPP\n\n#include "builtin_.hpp"\n\nusing namespace __shedskin__;\n\nnamespace __%s__ {\n' % (ident.upper(), ident.upper(), ident))

                # class declarations 
                for cl in mod.classes.values():
                    gv.output('class %s : public pyobj {\npublic:' % cl.ident)
                    gv.indent()
                    gv.output('PyObject *self;\n')
                    for func in cl.funcs.values():
                        if func.ident not in ['__getattr__', '__setattr__']:
                            gv.func_header(func, declare=True)
                        
                    gv.deindent()
                    gv.output('\n};\n')

                # function declarations
                for func in mod.funcs.values():
                    gv.func_header(func, declare=True)

                gv.output('\nvoid __init();\n\n} // namespace __%s__\n#endif' % ident)
                gv.out.close()

def bind_function(gv, func):
    gv.func_header(func, declare=False)
    gv.indent()

    formals = func.formals
    if func.parent: formals = [f for f in formals if f != 'self'] 
    args = str(len(formals))
    if formals:
        args += ', '+', '.join(['__to_py(%s)' % f for f in formals])

    # constructor call
    if func.parent and func.ident == '__init__':
        gv.output('self = __call(__%s, __args(%s));\n' % (func.parent.ident, args))

    # method/function call
    else:
        if func.parent:
            gv.output('PyObject *__0 = __call(self, "%s", __args(%s));\n' % (func.ident, args))
        else:
            gv.output('PyObject *__0 = __call(__%s, __args(%s));\n' % (func.ident, args))

        if not func.fakeret:
            gv.output('return __to_ss<%s>(__0);' % typesetreprnew(func.retnode.thing, func).strip())
        else:
            gv.output('return 0;')

    gv.deindent()
    gv.output('}\n')

# --- annotate original code; use above function to merge results to original code dimensions
def annotate():
    def paste(expr, text):
        if not expr.lineno: return
        if (expr,0,0) in getgx().cnode and inode(expr).mv != mv: return # XXX
        line = source[expr.lineno-1][:-1]
        if '#' in line: line = line[:line.index('#')]
        if text != '':
            text = '# '+text
        line = string.rstrip(line)
        if text != '' and len(line) < 40: line += (40-len(line))*' '
        source[expr.lineno-1] = line 
        if text: source[expr.lineno-1] += ' ' + text
        source[expr.lineno-1] += '\n'

    for module in getgx().modules.values(): 
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
        if not module.builtin: 
            try:
                out = open(module.filename[:-3]+'.ss.py','w')
                out.write(''.join(source))
                out.close()
            except IOError:
                pass

def usage():
    print """Usage: ss.py [OPTION]... FILE

 -b --bounds            Enable bounds checking
 -e --extmod            Generate extension module
 -f --flags             Provide alternative Makefile flags
 -n --nowrap            Disable wrap-around checking 
 -i --infinite          Try to avoid infinite analysis time 
"""
    sys.exit()

def main():
    gx = newgx()
    setgx(gx)

    print '*** SHED SKIN Python-to-C++ Compiler 0.0.26 ***'
    print 'Copyright 2005-2008 Mark Dufour; License GNU GPL version 3 (See LICENSE)'
    print '(Please send bug reports here: mark.dufour@gmail.com)'
    print

    # --- parse command-line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'eibnf:', ['infinite', 'extmod', 'bounds', 'nowrap', 'flags='])
    except getopt.GetoptError:
        usage()
    
    for o, a in opts:
        if o in ['-h', '--help']: usage()
        if o in ['-b', '--bounds']: getgx().bounds_checking = True
        if o in ['-e', '--extmod']: getgx().extension_module = True
        if o in ['-i', '--infinite']: getgx().avoid_loops = True
        if o in ['-f', '--flags']: 
            if not os.path.isfile(a): 
                print "*ERROR* no such file: '%s'" % a
                sys.exit()
            getgx().flags = a
        if o in ['-n', '--nowrap']: getgx().wrap_around_check = False

    # --- argument
    if len(args) != 1:
        usage()
    name = args[0]
    if not name.endswith('.py'):
        name += '.py'
    gx.main_mod = name[:-3]
        
    # --- analyze & annotate
    analysis(name)
    annotate()

if __name__ == '__main__':
    main()
