'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2011 Mark Dufour; License GNU GPL version 3 (See LICENSE)

'''
import os
from compiler.ast import AssTuple, AssList, List, Tuple, CallFunc, Name, \
    Const, UnaryAdd, UnarySub, Getattr

import graph
import infer
from config import getgx
from typestr import lowest_common_parents, polymorphic_t


class Module(object):
    def __init__(self, name, filename, relative_filename, builtin, node):
        #set name and its dependent fields
        self.name = name
        self.name_list = name.split('.')
        self.ident = self.name_list[-1]

        #set filename and its dependent fields
        self.filename = filename
        self.path = os.path.dirname(filename)
        self.relative_filename = relative_filename
        self.relative_path = os.path.dirname(relative_filename)

        #set the rest
        self.builtin = builtin
        self.node = node
        self.prop_includes = set()
        self.import_order = 0

    def full_path(self):
        return '__' + '__::__'.join(self.name_list) + '__'

    def include_path(self):
        if self.relative_filename.endswith('__init__.py'):
            return os.path.join(self.relative_path, '__init__.hpp')
        else:
            filename_without_ext = os.path.splitext(self.relative_filename)[0]
            return filename_without_ext + '.hpp'

    def in_globals(self, ident):
        return ident in self.mv.globals \
            or ident in self.mv.funcs \
            or ident in self.mv.ext_funcs \
            or ident in self.mv.classes \
            or ident in self.mv.ext_classes

    def __repr__(self):
        return 'Module ' + self.ident


class Class:
    def __init__(self, node):
        self.node = node
        self.ident = node.name
        self.bases = []
        self.children = []
        self.dcpa = 1
        self.mv = graph.getmv()
        self.vars = {}
        self.funcs = {}
        self.virtuals = {}              # 'virtually' called methods
        self.virtualvars = {}           # 'virtual' variables
        self.properties = {}
        self.staticmethods = []
        self.typenr = getgx().nrcltypes
        getgx().nrcltypes += 1
        self.splits = {}                # contour: old contour (used between iterations)
        self.has_copy = self.has_deepcopy = False
        self.def_order = getgx().class_def_order
        getgx().class_def_order += 1

    def ancestors(self, inclusive=False):  # XXX attribute (faster)
        a = set(self.bases)
        changed = 1
        while changed:
            changed = 0
            for cl in a.copy():
                if set(cl.bases) - a:
                    changed = 1
                    a.update(cl.bases)
        if inclusive:
            a.add(self)
        return a

    def ancestors_upto(self, other):
        a = self
        result = []
        while a != other:
            result.append(a)
            if not a.bases:
                break
            a = a.bases[0]
        return result

    def descendants(self, inclusive=False):  # XXX attribute (faster)
        a = set()
        if inclusive:
            a.add(self)
        for cl in self.children:
            a.add(cl)
            a.update(cl.descendants())
        return a

    def tvar_names(self):
        if self.mv.module.builtin:
            if self.ident in ['list', 'tuple', 'frozenset', 'set', 'frozenset', 'deque', '__iter', 'pyseq', 'pyiter', 'pyset', 'array']:
                return ['unit']
            elif self.ident in ['dict', 'defaultdict']:
                return ['unit', 'value']
            elif self.ident == 'tuple2':
                return ['first', 'second']
        return []

    def cpp_name(self):
        return nokeywords(self.ident)

    def __repr__(self):
        return 'class ' + self.ident


class StaticClass:  # XXX merge with regular class
    def __init__(self, cl):
        self.vars = {}
        self.static_nodes = []
        self.funcs = {}
        self.class_ = cl
        cl.static_class = self
        self.ident = cl.ident
        self.bases = []
        self.parent = None
        self.mv = graph.getmv()
        self.module = cl.module

    def __repr__(self):
        return 'static class ' + self.class_.ident


class Function:
    def __init__(self, node=None, parent=None, inherited_from=None):
        self.node = node
        self.inherited_from = inherited_from
        if node:
            ident = node.name
            if inherited_from and ident in parent.funcs:
                ident += inherited_from.ident + '__'  # XXX ugly
            self.ident = ident
            self.formals = node.argnames
            self.flags = node.flags
            self.doc = node.doc
        self.returnexpr = []
        self.retnode = None
        self.lambdanr = None
        self.lambdawrapper = False
        self.parent = parent
        self.constraints = set()
        self.vars = {}
        self.globals = []
        self.mv = graph.getmv()
        self.lnodes = []
        self.nodes = set()
        self.nodes_ordered = []
        self.defaults = []
        self.misses = set()
        self.cp = {}
        self.xargs = {}
        self.largs = None
        self.listcomp = False
        self.isGenerator = False
        self.yieldNodes = []
        self.tvars = set()
        self.ftypes = []                # function is called via a virtual call: arguments may have to be cast
        self.inherited = None

        if node:
            getgx().allfuncs.add(self)

        self.retvars = []
        self.invisible = False
        self.fakeret = None
        self.declared = False

        self.registered = []
        self.registered_temp_vars = []

    def cpp_name(self):  # XXX merge
        if self.ident in (cl.ident for cl in getgx().allclasses) or \
                self.ident + '_' in (cl.ident for cl in getgx().allclasses):
            return '_' + self.ident  # XXX ss_prefix
        return nokeywords(self.ident)

    def __repr__(self):
        if self.parent:
            return 'Function ' + repr((self.parent, self.ident))
        return 'Function ' + self.ident


class Variable:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.invisible = False            # not in C++ output
        self.formal_arg = False
        self.imported = False
        self.registered = False
        self.looper = None
        self.wopper = None
        self.const_assign = []

    def types(self):
        return infer.inode(self).types()

    def masks_global(self):
        if isinstance(self.parent, Class):
            mv = self.parent.mv
            if not mv.module.builtin and mv.module.in_globals(self.name):
                return True
        return False

    def cpp_name(self):
        name = self.name
        if self.masks_global() or \
                name in (cl.ident for cl in getgx().allclasses) or \
                name + '_' in (cl.ident for cl in getgx().allclasses):  # XXX name in..
            name = '_' + name  # XXX use prefix
        return nokeywords(name)

    def __repr__(self):
        if self.parent:
            return repr((self.parent, self.name))
        return self.name


def nokeywords(name):
    if name in getgx().cpp_keywords:
        return getgx().ss_prefix + name
    return name


# XXX ugly: find ancestor class that implements function 'ident'
def lookup_implementor(cl, ident):
    while cl:
        if ident in cl.funcs and not cl.funcs[ident].inherited:
            return cl.ident
        if cl.bases:
            cl = cl.bases[0]
        else:
            break
    return None


def lookup_class_module(objexpr, mv, parent):
    if isinstance(objexpr, Name):  # XXX Getattr?
        var = lookup_var(objexpr.name, parent, mv=mv)
        if var and not var.imported:  # XXX cl?
            return None, None
    return lookup_class(objexpr, mv), lookup_module(objexpr, mv)


def lookup_func(node, mv):  # XXX lookup_var first?
    if isinstance(node, Name):
        if node.name in mv.funcs:
            return mv.funcs[node.name]
        elif node.name in mv.ext_funcs:
            return mv.ext_funcs[node.name]
        else:
            return None
    elif isinstance(node, Getattr):
        module = lookup_module(node.expr, mv)
        if module and node.attrname in module.mv.funcs:
            return module.mv.funcs[node.attrname]


def lookup_class(node, mv):  # XXX lookup_var first?
    if isinstance(node, Name):
        if node.name in mv.classes:
            return mv.classes[node.name]
        elif node.name in mv.ext_classes:
            return mv.ext_classes[node.name]
        else:
            return None
    elif isinstance(node, Getattr):
        module = lookup_module(node.expr, mv)
        if module and node.attrname in module.mv.classes:
            return module.mv.classes[node.attrname]


def lookup_module(node, mv):
    path = []
    imports = mv.imports

    while isinstance(node, Getattr):
        path = [node.attrname] + path
        node = node.expr

    if isinstance(node, Name):
        path = [node.name] + path

        # --- search import chain
        for ident in path:
            if ident in imports:
                module = imports[ident]
                imports = module.mv.imports
            else:
                return None

        return module


def lookup_variable(node, gv):
    lcp = lowest_common_parents(polymorphic_t(gv.mergeinh[node.expr]))
    if len(lcp) == 1 and isinstance(lcp[0], Class) and node.attrname in lcp[0].vars and not node.attrname in lcp[0].funcs:
        return lcp[0].vars[node.attrname]


def lookup_var(name, parent, mv=None):
    return def_var(name, parent, False, mv=mv)


def register_temp_var(var, parent):
    if isinstance(parent, Function):
        parent.registered_temp_vars.append(var)


def def_class(name):
    if name in graph.getmv().classes:
        return graph.getmv().classes[name]
    else:
        return graph.getmv().ext_classes[name]


def def_var(name, parent, local, worklist=None, mv=None):
    if not mv:
        mv = graph.getmv()
    if isinstance(parent, Class) and name in parent.parent.vars:  # XXX
        return parent.parent.vars[name]
    if parent and name in parent.vars:
        return parent.vars[name]
    if parent and local:
        dest = parent.vars
    else:
        # recursive lookup
        chain = []
        while isinstance(parent, Function):
            if name in parent.vars:
                for ancestor in chain:
                    if isinstance(ancestor, Function):  # XXX optimize
                        ancestor.misses.add(name)
                return parent.vars[name]
            chain.append(parent)
            parent = parent.parent

        # not found: global
        if name in mv.globals:
            return mv.globals[name]
        dest = mv.globals

    if not local:
        return None

    var = Variable(name, parent)
    getgx().allvars.add(var)

    dest[name] = var
    newnode = infer.CNode(var, parent=parent)
    if parent:
        newnode.mv = parent.mv
    else:
        newnode.mv = mv
    infer.add_to_worklist(worklist, newnode)
    getgx().types[newnode] = set()

    return var


def default_var(name, parent, worklist=None):
    var = def_var(name, parent, True, worklist)

    if isinstance(parent, Function) and parent.listcomp and not var.registered:
        while isinstance(parent, Function) and parent.listcomp:  # XXX
            parent = parent.parent
        register_temp_var(var, parent)

    return var


def subclass(a, b):
    if b in a.bases:
        return True
    else:
        return a.bases and subclass(a.bases[0], b)  # XXX mult inh


def is_property_setter(dec):
    return isinstance(dec, Getattr) and isinstance(dec.expr, Name) and dec.attrname == 'setter'


def is_literal(node):
    if isinstance(node, (UnarySub, UnaryAdd)):
        node = node.expr
    return isinstance(node, Const) and isinstance(node.value, (int, float))


def is_fastfor(node):
    return isinstance(node.list, CallFunc) and isinstance(node.list.node, Name) and node.list.node.name in ['range', 'xrange']


def is_method(parent):
    return isinstance(parent, Function) and isinstance(parent.parent, Class)


def is_enum(node):
    return isinstance(node.list, CallFunc) and isinstance(node.list.node, Name) and node.list.node.name == 'enumerate' and len(node.list.args) == 1 and isinstance(node.assign, (AssList, AssTuple))


def is_zip2(node):
    return isinstance(node.list, CallFunc) and isinstance(node.list.node, Name) and node.list.node.name == 'zip' and len(node.list.args) == 2 and isinstance(node.assign, (AssList, AssTuple))


# --- recursively determine (lvalue, rvalue) pairs in assignment expressions
def assign_rec(left, right):
    if isinstance(left, (AssTuple, AssList)) and isinstance(right, (Tuple, List)):
        pairs = []
        for (lvalue, rvalue) in zip(left.getChildNodes(), right.getChildNodes()):
            pairs += assign_rec(lvalue, rvalue)
        return pairs
    else:
        return [(left, right)]


def aug_msg(node, msg):
    if hasattr(node, 'augment'):
        return '__i' + msg + '__'
    return '__' + msg + '__'
