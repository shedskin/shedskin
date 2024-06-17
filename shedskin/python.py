"""
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2023 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)

"""

import ast
import collections
import importlib.util
import os
import re
import sys
import pathlib

from . import ast_utils

# type-checking
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from . import config
    from . import graph


class PyObject:
    """Mixin for py objects"""
    ident: str

    def __repr__(self):
        return f"{self.__class__.__name__} {self.ident}"


class Module(PyObject):
    """python module class

    name: str               module name
    name_list: [str]        list of names
    ident: str              module name

    filename: Path          module path
    path: Path              module parentdir
    relative_filename: Path module relative_filenmae
    relative_path: Path     relative_filename parentdir

    ast: ast.Module         ast module or None
    builtin: bool           is_builtin ?
    node: ast.node          ast Node
    prop_includes: set      ?
    import_order: int       order of imports or number of imports?

    """

    def __init__(
            self, 
            name: str, 
            filename: str, 
            relative_filename: str, 
            builtin: bool, 
            node):
        # set name and its dependent fields
        self.name = name
        self.name_list = name.split(".")
        self.ident = self.name_list[-1]
        # set filename and its dependent fields
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent
        self.relative_filename = pathlib.Path(relative_filename)
        self.relative_path = self.relative_filename.parent
        self.mv: Optional['graph.ModuleVisitor'] = None

        # set the rest
        self.ast = None  # to be provided later after analysis
        self.builtin = builtin
        self.node = node
        self.prop_includes = set()
        self.import_order = 0

    def full_path(self) -> str:
        return "__" + "__::__".join(self.name_list) + "__"

    def include_path(self):
        if self.relative_filename.name.endswith("__init__.py"):
            return os.path.join(self.relative_path, "__init__.hpp")
        else:
            filename_without_ext = os.path.splitext(self.relative_filename)[0]
            return filename_without_ext + ".hpp"

    def in_globals(self, ident: str):
        assert self.mv, "must be graph.ModuleVisitor instance"
        return (
               ident in self.mv.globals
            or ident in self.mv.funcs
            or ident in self.mv.ext_funcs
            or ident in self.mv.classes
            or ident in self.mv.ext_classes
        )

    @property
    def doc(self) -> Optional[str]:
        """returns module docstring."""
        return ast.get_docstring(self.ast)


class Class(PyObject):
    def __init__(self, gx: 'config.GlobalInfo', node: ast.ClassDef, mv: 'graph.ModuleVisitor'):
        self.gx = gx
        self.node = node
        self.mv = mv
        self.ident: str = node.name
        self.bases: list['Class'] = []
        self.children: list['Class'] = []
        self.dcpa = 1
        self.vars: dict[str, 'Variable'] = {}
        self.funcs: dict[str, 'Function'] = {}
        self.virtuals = {}     # 'virtually' called methods
        self.virtualvars = {}  # 'virtual' variables
        self.properties = {}
        self.staticmethods = []
        self.splits = {}  # contour: old contour (used between iterations)
        self.has_copy = self.has_deepcopy = False
        self.def_order = self.gx.class_def_order
        self.gx.class_def_order += 1
        self.module: Optional[Module] = None # from graph.py:635
        self.parent: Optional['StaticClass'] = None # issues/479

    def ancestors(self, inclusive: bool = False):  # XXX attribute (faster)
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

    def ancestors_upto(self, other: 'Class'):
        a = self
        result = []
        while a != other:
            result.append(a)
            if not a.bases:
                break
            if len(a.bases) > 1:  # XXX multiple inheritance quick hack
                result = list(set(result) | set(a.bases))
            a = a.bases[0]
        return result

    def descendants(self, inclusive: bool = False):  # XXX attribute (faster)
        a = set()
        if inclusive:
            a.add(self)
        for cl in self.children:
            a.add(cl)
            a.update(cl.descendants())
        return a

    def tvar_names(self):
        if self.mv.module.builtin:
            if self.ident in [
                "list",
                "tuple",
                "set",
                "frozenset",
                "deque",
                "__iter",
                "pyseq",
                "pyiter",
                "pyset",
                "array",
            ]:
                return ["unit"]
            elif self.ident in ["dict", "defaultdict"]:
                return ["unit", "value"]
            elif self.ident == "tuple2":
                return ["first", "second"]
        return []


class StaticClass(PyObject):
    def __init__(self, cl, mv: 'graph.ModuleVisitor'):
        self.vars = {}
        self.static_nodes = []
        self.funcs = {}
        self.ident = cl.ident
        self.parent = None
        self.mv = mv
        self.module = cl.module


def get_arg_name(node, is_tuple_expansion: bool = False):
    if hasattr(node, "arg"):
        assert isinstance(node.arg, str), "non-arg string %s" % type(node.arg)
        return node.arg

    if isinstance(node, ast.Tuple):
        return tuple(
            get_arg_name(child, is_tuple_expansion=True) for child in node.elts
        )
    elif isinstance(node, ast.Name):
        assert (
            is_tuple_expansion
            and type(node.ctx) == ast.Store
            or type(node.ctx) == ast.Param
        )
        return node.id
    elif isinstance(node, str):
        return node
    else:
        assert False, "Unexpected argument type got %s" % type(node)


def extract_argnames(arg_struct):
    argnames = [get_arg_name(arg) for arg in arg_struct.args]
    if arg_struct.vararg:
        argnames.append(get_arg_name(arg_struct.vararg))
    # PY3: kwonlyargs
    if arg_struct.kwarg:
        argnames.append(arg_struct.kwarg)
    return argnames


class Function:
    def __init__(self, gx: 'config.GlobalInfo', node=None, parent=None, inherited_from=None, mv: Optional['graph.ModuleVisitor'] = None):
        self.gx = gx
        self.node = node
        self.inherited_from = inherited_from
        if node:
            ident = node.name
            if inherited_from and ident in parent.funcs:
                ident += inherited_from.ident + "__"  # XXX ugly
            self.ident = ident
            self.formals = extract_argnames(node.args)
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
        self.misses_by_ref = set()
        self.cp = {}
        self.xargs = {}
        self.largs = None
        self.listcomp = False
        self.isGenerator = False
        self.yieldNodes = []
        self.tvars = set()
        self.ftypes = (
            []
        )  # function is called via a virtual call: arguments may have to be cast
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
            return "Function " + repr((self.parent, self.ident))
        return "Function " + self.ident
        #     return f"<Function '{self.parent.ident}.{self.ident}'>"
        # return f"<Function '{self.ident}'>"


class Variable:
    def __init__(self, name: str, parent):
        self.name = name
        self.parent = parent
        self.invisible = False  # not in C++ output
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
        #     return f"<Variable '{self.parent.name}.{self.name}'>"
        # return f"<Variable '{self.name}'>"


def clear_block(m):
    return m.string.count("\n", m.start(), m.end()) * "\n"


def parse_file(name: str):
    data = importlib.util.decode_source(open(name, 'rb').read())

    # Convert block comments into strings which will be duely ignored.
    pat = re.compile(r"#{.*?#}[^\r\n]*$", re.MULTILINE | re.DOTALL)
    filebuf = re.sub(pat, clear_block, data)

    try:
        return ast.parse(filebuf)
    except SyntaxError as s:
        print("*ERROR* %s:%d: %s" % (name, s.lineno, s.msg))
        sys.exit(1)


def find_module(gx: 'config.GlobalInfo', name: str, paths):
    if "." in name:
        name, module_name = name.rsplit(".", 1)
        name_as_path = name.replace(".", os.path.sep)
        import_paths = [os.path.join(path, name_as_path) for path in paths]
    else:
        module_name = name
        import_paths = paths

    filename = None
    is_a_package = False
    for path in import_paths:
        if os.path.isfile(os.path.join(path, module_name)+'.py'):
            filename = os.path.join(path, module_name)
        elif os.path.isfile(os.path.join(path, module_name, '__init__.py')):
            filename = os.path.join(path, module_name)
            is_a_package = True

    if filename is None:
        raise ModuleNotFoundError("No module named '%s'" % module_name)

    absolute_import_paths = gx.libdirs + [os.getcwd()]
    absolute_import_path = next(
        path for path in absolute_import_paths if filename.startswith(path)
    )
    relative_filename = os.path.relpath(filename, absolute_import_path)
    absolute_name = relative_filename.replace(os.path.sep, ".")
    builtin = absolute_import_path in gx.libdirs

    if is_a_package:
        filename = os.path.join(filename, "__init__.py")
        relative_filename = os.path.join(relative_filename, "__init__.py")
    else:
        filename = filename + ".py"
        relative_filename = relative_filename + ".py"

    return absolute_name, filename, relative_filename, builtin


# XXX ugly: find ancestor class that implements function 'ident'
def lookup_implementor(cl: Class, ident: str):
    while cl:
        if ident in cl.funcs and not cl.funcs[ident].inherited:
            return cl.ident
        if cl.bases:
            cl = cl.bases[0]
        else:
            break
    return None


def lookup_class_module(objexpr, mv: 'graph.ModuleVisitor', parent):
    if isinstance(objexpr, ast.Name):  # XXX ast.Attribute?
        var = lookup_var(objexpr.id, parent, mv=mv)
        if var and not var.imported:  # XXX cl?
            return None, None
    return lookup_class(objexpr, mv), lookup_module(objexpr, mv)


def lookup_func(node, mv: 'graph.ModuleVisitor'):  # XXX lookup_var first?
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


def lookup_class(node, mv: 'graph.ModuleVisitor'):  # XXX lookup_var first?
    if isinstance(node, ast.Name):
        if node.id == 'int': # TODO generalize
            return mv.ext_classes['int_']
        elif node.id in mv.classes:
            return mv.classes[node.id]
        elif node.id in mv.ext_classes:
            return mv.ext_classes[node.id]
        else:
            return None
    elif isinstance(node, ast.Attribute):
        module = lookup_module(node.value, mv)
        if module and node.attr in module.mv.classes:
            return module.mv.classes[node.attr]


def lookup_module(node, mv: 'graph.ModuleVisitor'):
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


def def_class(gx: 'config.GlobalInfo', name: str, mv: Optional['graph.ModuleVisitor'] = None):
    if mv is None:
        mv = gx.modules["builtin"].mv
    if name in mv.classes:
        return mv.classes[name]
    elif name in mv.ext_classes:
        return mv.ext_classes[name]


def lookup_var(name, parent, local: bool = False, mv: Optional['graph.ModuleVisitor'] = None):
    var = smart_lookup_var(name, parent, local=local, mv=mv)
    if var:
        return var.var


VarLookup = collections.namedtuple("VarLookup", ["var", "is_global"])


def smart_lookup_var(name, parent, local: bool = False, mv: Optional['graph.ModuleVisitor'] = None):
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

        assert mv, "'graph.ModuleVisitor' instance required"
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
