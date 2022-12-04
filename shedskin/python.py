'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

'''
import ast
import collections
import imp
import os
import re
import sys

from . import ast_utils

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
        self.ast = None # to be provided later after analysis
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

    @property
    def doc(self):
        """returns module docstring."""
        return ast.get_docstring(self.ast)


class Class(object):
    def __init__(self, gx, node, mv):
        self.gx = gx
        self.node = node
        self.mv = mv
        self.ident = node.name
        self.bases = []
        self.children = []
        self.dcpa = 1
        self.vars = {}
        self.funcs = {}
        self.virtuals = {}              # 'virtually' called methods
        self.virtualvars = {}           # 'virtual' variables
        self.properties = {}
        self.staticmethods = []
        self.typenr = self.gx.nrcltypes
        self.gx.nrcltypes += 1
        self.splits = {}                # contour: old contour (used between iterations)
        self.has_copy = self.has_deepcopy = False
        self.def_order = self.gx.class_def_order
        self.gx.class_def_order += 1

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
            if len(a.bases) > 1: # XXX multiple inheritance quick hack
                result = list(set(result) | set(a.bases))
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
            if self.ident in ['list', 'tuple', 'set', 'frozenset', 'deque', '__iter', 'pyseq', 'pyiter', 'pyset', 'array']:
                return ['unit']
            elif self.ident in ['dict', 'defaultdict']:
                return ['unit', 'value']
            elif self.ident == 'tuple2':
                return ['first', 'second']
        return []

    def __repr__(self):
        return 'class ' + self.ident


class StaticClass(object):
    def __init__(self, cl, mv):
        self.vars = {}
        self.static_nodes = []
        self.funcs = {}
        self.ident = cl.ident
        self.parent = None
        self.mv = mv
        self.module = cl.module

    def __repr__(self):
        return 'static class ' + self.ident


class Function(object):
    def __init__(self, gx, node=None, parent=None, inherited_from=None, mv=None):
        self.gx = gx
        self.node = node
        self.inherited_from = inherited_from
        if node:
            ident = node.name
            if inherited_from and ident in parent.funcs:
                ident += inherited_from.ident + '__'  # XXX ugly
            self.ident = ident
            self.formals = ast_utils.extract_argnames(node.args)
            self.flags = None
            self.doc = ast.get_docstring(node)
        self.returnexpr = []
        self.retnode = None
        self.lambdanr = None
        self.lambdawrapper = False
        self.parent = parent
        self.constraints = set()
        self.vars = {}
        self.globals = []
        self.mv = mv
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
            self.gx.allfuncs.add(self)

        self.retvars = []
        self.invisible = False
        self.fakeret = None
        self.declared = False

        self.registered = []
        self.registered_temp_vars = []

    def __repr__(self):
        if self.parent:
            return 'Function ' + repr((self.parent, self.ident))
        return 'Function ' + self.ident


class Variable(object):
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

    def masks_global(self):
        if isinstance(self.parent, Class):
            mv = self.parent.mv
            if not mv.module.builtin and mv.module.in_globals(self.name):
                return True
        return False

    def __repr__(self):
        if self.parent:
            return repr((self.parent, self.name))
        return self.name


def clear_block(m):
    return m.string.count('\n', m.start(), m.end()) * '\n'


def parse_file(name):
    # Convert block comments into strings which will be duely ignored.
    pat = re.compile(r"#{.*?#}[^\r\n]*$", re.MULTILINE | re.DOTALL)
    try:
        filebuf = re.sub(pat, clear_block, ''.join(open(name, 'U').readlines()))
    except ValueError:
        filebuf = re.sub(pat, clear_block, ''.join(open(name).readlines()))
    try:
        return ast.parse(filebuf)
    except SyntaxError as s:
        print('*ERROR* %s:%d: %s' % (name, s.lineno, s.msg))
        sys.exit(1)


def find_module(gx, name, paths):
    if '.' in name:
        name, module_name = name.rsplit('.', 1)
        name_as_path = name.replace('.', os.path.sep)
        import_paths = [os.path.join(path, name_as_path) for path in paths]
    else:
        module_name = name
        import_paths = paths
    _, filename, description = imp.find_module(module_name, import_paths)
    filename = os.path.splitext(filename)[0]

    absolute_import_paths = gx.libdirs + [os.getcwd()]
    absolute_import_path = next(
        path for path in absolute_import_paths
        if filename.startswith(path)
    )
    relative_filename = os.path.relpath(filename, absolute_import_path)
    absolute_name = relative_filename.replace(os.path.sep, '.')
    builtin = absolute_import_path in gx.libdirs

    is_a_package = description[2] == imp.PKG_DIRECTORY
    if is_a_package:
        filename = os.path.join(filename, '__init__.py')
        relative_filename = os.path.join(relative_filename, '__init__.py')
    else:
        filename = filename + '.py'
        relative_filename = relative_filename + '.py'

    return absolute_name, filename, relative_filename, builtin


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
    if isinstance(objexpr, ast.Name):  # XXX ast.Attribute?
        var = lookup_var(objexpr.id, parent, mv=mv)
        if var and not var.imported:  # XXX cl?
            return None, None
    return lookup_class(objexpr, mv), lookup_module(objexpr, mv)


def lookup_func(node, mv):  # XXX lookup_var first?
    if isinstance(node, ast.Name):
        if node.id in mv.funcs:
            return mv.funcs[node.id]
        elif node.id in mv.ext_funcs:
            return mv.ext_funcs[node.id]
        else:
            return None
    elif isinstance(node, ast.Attribute):
        module = lookup_module(node.value, mv)
        if module and node.attr in module.mv.funcs:
            return module.mv.funcs[node.attr]


def lookup_class(node, mv):  # XXX lookup_var first?
    if isinstance(node, ast.Name):
        if node.id in mv.classes:
            return mv.classes[node.id]
        elif node.id in mv.ext_classes:
            return mv.ext_classes[node.id]
        else:
            return None
    elif isinstance(node, ast.Attribute):
        module = lookup_module(node.value, mv)
        if module and node.attr in module.mv.classes:
            return module.mv.classes[node.attr]


def lookup_module(node, mv):
    path = []
    imports = mv.imports

    while isinstance(node, ast.Attribute) and type(node.ctx) == ast.Load:
        path = [node.attr] + path
        node = node.value

    if isinstance(node, ast.Name):
        path = [node.id] + path

        # --- search import chain
        for ident in path:
            if ident in imports:
                module = imports[ident]
                imports = module.mv.imports
            else:
                return None

        return module


def def_class(gx, name, mv=None):
    if mv is None:
        mv = gx.modules['builtin'].mv
    if name in mv.classes:
        return mv.classes[name]
    elif name in mv.ext_classes:
        return mv.ext_classes[name]


def lookup_var(name, parent, local=False, mv=None):
    var = smart_lookup_var(name, parent, local=local, mv=mv)
    if var:
        return var.var

VarLookup = collections.namedtuple('VarLookup', ['var', 'is_global'])


def smart_lookup_var(name, parent, local=False, mv=None):
    if not local and isinstance(parent, Class) and name in parent.parent.vars:  # XXX
        return VarLookup(parent.parent.vars[name], False)
    elif parent and name in parent.vars:
        return VarLookup(parent.vars[name], False)
    elif not (parent and local):
        # recursive lookup
        chain = []
        while isinstance(parent, Function):
            if name in parent.vars:
                for ancestor in chain:
                    if isinstance(ancestor, Function):  # XXX optimize
                        ancestor.misses.add(name)
                return VarLookup(parent.vars[name], False)
            chain.append(parent)
            parent = parent.parent

        # not found: global or exception name
        if name in mv.exc_names:
            return VarLookup(mv.exc_names[name], False)
        if any(name in vars for vars in mv.current_with_vars if vars):
            return
        if name in mv.globals:
            return VarLookup(mv.globals[name], True)


def subclass(a, b):
    if b in a.bases:
        return True
    else:
        return a.bases and subclass(a.bases[0], b)  # XXX mult inh


def is_property_setter(dec):
    return isinstance(dec, ast.Attribute) and isinstance(dec.value, ast.Name) and dec.attr == 'setter'


def is_literal(node):
    # RESOLVE: Can all UnaryOps be literals, Not?, Invert?
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        node = node.operand
    # RESOLVE: Isn't Str node also literal
    return isinstance(node, ast.Num) and isinstance(node.n, (int, float))


def is_fastfor(node):
    return isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id in ['range', 'xrange']


def is_method(parent):
    return isinstance(parent, Function) and isinstance(parent.parent, Class)


def is_enum(node):
    return isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'enumerate' and len(node.iter.args) == 1 and ast_utils.is_assign_list_or_tuple(node.target)


def is_zip2(node):
    return isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'zip' and len(node.iter.args) == 2 and ast_utils.is_assign_list_or_tuple(node.target)

def is_isinstance(node):
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'isinstance'

# --- recursively determine (lvalue, rvalue) pairs in assignment expressions
def assign_rec(left, right):
    if ast_utils.is_assign_list_or_tuple(left) and isinstance(right, (ast.Tuple, ast.List)):
        pairs = []
        for (lvalue, rvalue) in zip(left.elts, right.elts):
            pairs += assign_rec(lvalue, rvalue)
        return pairs
    else:
        return [(left, right)]


def aug_msg(node, msg):
    if hasattr(node, 'augment'):
        return '__i' + msg + '__'
    return '__' + msg + '__'
