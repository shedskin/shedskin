# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.python: models high-level python object types

This module models Python's high-level object types and program structure for
the Shedskin compiler.

Key Components:
- `Module`: Represents Python modules, tracking names, paths, AST, and dependencies
- `Class`: Models Python classes with inheritance, methods, and type information
- `Function`: Represents functions and methods with arguments and return types
- `Variable`: Tracks variables and their possible types
- `StaticClass`: Special class for built-in types like list, dict etc.

The type system uses these classes to:
1. Build the program model during parsing
2. Track type constraints during inference
3. Generate appropriate C++ code

Major Features:
- Full class hierarchy modeling with multiple inheritance
- Function overloading and polymorphism support
- Module import system and dependency tracking
- Static vs instance method handling
- Built-in type implementations
- Variable scope and lifetime management

The module works closely with:
- `graph.py`: Builds constraint graph using these types
- `infer.py`: Type inference using class/function information
- `cpp.py`: Code generation based on type model

This type model forms the core of Shedskin's static analysis and code generation,
bridging the gap between Python's dynamic types and C++'s static typing.
"""

import ast
import importlib.util
import os
import pathlib
import re
import sys
# type-checking
from typing import (TYPE_CHECKING, List, NamedTuple, Optional, Tuple,
                    TypeAlias, Union)

if TYPE_CHECKING:
    from . import config, graph, infer

Parent: TypeAlias = Union["Class", "Function"]
AllParent: TypeAlias = Union["Class", "Function", "StaticClass"]
CartesianProduct: TypeAlias = Tuple[Tuple["Class", int], ...]


class PyObject:
    """Mixin for py objects"""

    ident: str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.ident}"


class Module(PyObject):
    """Python module class

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
        node: Optional[ast.AST],
        ast: ast.Module,
    ):
        # set name and its dependent fields
        self.name = name
        self.name_list = name.split(".")
        self.ident = self.name_list[-1]
        # set filename and its dependent fields
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent
        self.relative_filename = pathlib.Path(relative_filename)
        self.relative_path = self.relative_filename.parent

        self.mv: "graph.ModuleVisitor"
        self.deps: set["Module"]

        # set the rest
        self.ast = ast
        self.builtin = builtin
        self.node = node
        self.prop_includes: set["Module"] = set()
        self.import_order = 0

    def full_path(self) -> str:
        """Get the full path of a module"""
        return "__" + "__::__".join(self.name_list) + "__"

    def include_path(self) -> str:
        """Get the include path of a module"""
        if self.relative_filename.name.endswith("__init__.py"):
            return os.path.join(self.relative_path, "__init__.hpp")
        else:
            filename_without_ext = os.path.splitext(self.relative_filename)[0]
            return filename_without_ext + ".hpp"

    def in_globals(self, ident: str) -> bool:
        """Check if a variable is global"""
        assert self.mv, "must have graph.ModuleVisitor instance"
        return (
            ident in self.mv.globals
            or ident in self.mv.funcs
            or ident in self.mv.ext_funcs
            or ident in self.mv.classes
            or ident in self.mv.ext_classes
        )

    @property
    def doc(self) -> Optional[str]:
        """Get the docstring of a module"""
        return ast.get_docstring(self.ast)


class Class(PyObject):
    """Python class class"""

    def __init__(
        self,
        gx: "config.GlobalInfo",
        node: ast.ClassDef,
        mv: "graph.ModuleVisitor",
        module: Module,
    ):
        self.gx = gx
        self.node = node
        self.mv = mv
        self.module = module
        self.ident: str = node.name
        self.bases: list["Class"] = []
        self.children: list["Class"] = []
        self.dcpa = 1
        self.newdcpa: int
        self.vars: dict[str, "Variable"] = {}
        self.funcs: dict[str, "Function"] = {}
        self.virtuals: dict[str, set["Class"]] = {}  # 'virtually' called methods
        self.virtualvars: dict[str, set["Class"]] = {}  # 'virtual' variables
        self.properties: dict[str, List[str]] = {}
        self.staticmethods: List[str] = []
        self.splits: dict[
            int, int
        ] = {}  # contour: old contour (used between iterations)
        self.has_copy = self.has_deepcopy = False
        self.def_order = self.gx.class_def_order
        self.gx.class_def_order += 1
        self.lcpcount: int = 0

        self.parent: StaticClass = StaticClass(self, mv)

    def ancestors(self, inclusive: bool = False) -> set["Class"]:
        """Get the ancestors of a class"""
        # XXX attribute (faster)
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

    def ancestors_upto(self, other: Optional["Class"]) -> List["Class"]:
        """Get the ancestors of a class up to a given class"""
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

    def descendants(self, inclusive: bool = False) -> set["Class"]:
        """Get the descendants of a class"""
        # XXX attribute (faster)
        a = set()
        if inclusive:
            a.add(self)
        for cl in self.children:
            a.add(cl)
            a.update(cl.descendants())
        return a

    def tvar_names(self) -> List[str]:
        """Get the names of the types of variables in a class"""
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
    """Static class class"""

    def __init__(self, cl: "Class", mv: "graph.ModuleVisitor"):
        self.vars: dict[str, Variable] = {}
        self.static_nodes: List[ast.AST] = []
        self.funcs: dict[str, Function] = {}
        self.ident = cl.ident
        self.parent = None
        self.mv = mv
        self.module = cl.module


def extract_argnames(arg_struct: ast.arguments) -> List[str]:
    """Get the names of the arguments of a function"""
    argnames = [arg.arg for arg in arg_struct.args]
    if arg_struct.vararg:
        argnames.append(arg_struct.vararg.arg)
    if arg_struct.kwarg:
        argnames.append(arg_struct.kwarg.arg)
    return argnames


class Function:
    """Python function class"""

    def __init__(
        self,
        gx: "config.GlobalInfo",
        mv: "graph.ModuleVisitor",
        node: Optional[ast.FunctionDef] = None,
        parent: Optional[AllParent] = None,
        inherited_from: Optional[
            Union["Class", "Function"]
        ] = None,  # TODO should be one
    ):
        self.gx = gx
        self.node = node
        self.inherited_from = inherited_from
        self.inherited: Optional[ast.FunctionDef] = None
        self.ident: str
        if node:
            ident = node.name
            if inherited_from and isinstance(parent, Class) and ident in parent.funcs:
                ident += inherited_from.ident + "__"  # XXX ugly
            self.ident = ident
            self.formals = extract_argnames(node.args)
            self.flags = None
            self.doc = ast.get_docstring(node)
        self.returnexpr: List[ast.AST] = []
        self.retnode: Optional["infer.CNode"] = None
        self.lambdanr: Optional[int] = None
        self.lambdawrapper = False
        self.parent = parent
        self.constraints: set[Tuple["infer.CNode", "infer.CNode"]] = set()
        self.vars: dict[str, Variable] = {}
        self.globals: List[str] = []
        self.mv = mv
        self.nodes: set["infer.CNode"] = set()
        self.nodes_ordered: List["infer.CNode"] = []
        self.defaults: List[ast.expr] = []
        self.misses: set[str] = set()
        self.misses_by_ref: set[str] = set()
        self.cp: dict[int, dict[CartesianProduct, int]] = {}
        self.xargs: dict[Tuple[int, int], int] = {}
        self.largs: Optional[int] = None
        self.listcomp = False
        self.isGenerator = False
        self.yieldNodes: List[ast.Yield] = []
        self.yieldnode: "infer.CNode"
        # function is called via a virtual call: arguments may have to be cast
        self.ftypes: List[str] = []

        if node:
            self.gx.allfuncs.add(self)

        self.invisible = False
        self.fakeret: Optional[ast.Return] = None
        self.declared = False

        self.registered: List[ast.AST] = []
        self.registered_temp_vars: List[Variable] = []

    def __repr__(self) -> str:
        if self.parent:
            return "Function " + repr((self.parent, self.ident))
        return "Function " + self.ident


class Variable:
    """Python variable class"""

    def __init__(self, name: str, parent: Optional[AllParent]):
        self.name = name
        self.parent = parent
        self.invisible = False  # not in C++ output
        self.formal_arg = False
        self.imported = False
        self.registered = False
        self.looper: Optional[ast.AST] = None
        self.wopper: Optional[ast.AST] = None
        self.const_assign: List[ast.Constant] = []

    def masks_global(self) -> bool:
        """Check if a variable masks a global variable"""
        if isinstance(self.parent, Class):
            mv = self.parent.mv
            if not mv.module.builtin and mv.module.in_globals(self.name):
                return True
        return False

    def __repr__(self) -> str:
        if self.parent:
            return repr((self.parent, self.name))
        return self.name
        #     return f"<Variable '{self.parent.name}.{self.name}'>"
        # return f"<Variable '{self.name}'>"


def clear_block(m: re.Match[str]) -> str:
    """Clear a block comment"""
    return m.string.count("\n", m.start(), m.end()) * "\n"


def parse_file(name: pathlib.Path) -> ast.Module:
    """Parse a Python file"""
    data = importlib.util.decode_source(open(name, "rb").read())

    # Convert block comments into strings which will be duely ignored.
    pat = re.compile(r"#{.*?#}[^\r\n]*$", re.MULTILINE | re.DOTALL)
    filebuf = re.sub(pat, clear_block, data)

    try:
        return ast.parse(filebuf)
    except SyntaxError as s:
        print("*ERROR* %s:%s: %s" % (name, str(s.lineno), s.msg))
        sys.exit(1)


def find_module(
    gx: "config.GlobalInfo", name: str, paths: List[str]
) -> Tuple[str, str, str, bool]:
    """Find a module by name"""
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
        if os.path.isfile(os.path.join(path, module_name) + ".py"):
            filename = os.path.join(path, module_name)
        elif os.path.isfile(os.path.join(path, module_name, "__init__.py")):
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
def lookup_implementor(cl: Class, ident: str) -> Optional[str]:
    """Find the class that implements a given function"""
    while cl:
        if ident in cl.funcs and not cl.funcs[ident].inherited:
            return cl.ident
        if cl.bases:
            cl = cl.bases[0]
        else:
            break
    return None


def lookup_class_module(
    objexpr: ast.AST, mv: "graph.ModuleVisitor", parent: Optional[AllParent]
) -> Tuple[Optional["Class"], Optional["Module"]]:
    """Find the class and module of an expression"""
    if isinstance(objexpr, ast.Name):  # XXX ast.Attribute?
        var = lookup_var(objexpr.id, parent, mv)
        if var and not var.imported:  # XXX cl?
            return None, None
    return lookup_class(objexpr, mv), lookup_module(objexpr, mv)


def lookup_func(
    node: ast.AST, mv: "graph.ModuleVisitor"
) -> Optional["Function"]:  # XXX lookup_var first?
    """Find a function by name"""
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
    return None


def lookup_class(
    node: ast.AST, mv: "graph.ModuleVisitor"
) -> Optional["Class"]:  # XXX lookup_var first?
    """Find a class by name"""
    if isinstance(node, ast.Name):
        if node.id == "int":  # TODO generalize
            return mv.ext_classes["int_"]
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

    return None


def lookup_module(node: ast.AST, mv: "graph.ModuleVisitor") -> Optional[Module]:
    """Find a module by name"""
    path: List[str] = []
    module: Optional[Module] = None

    imports = mv.imports

    while isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
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


# XXX: this is weird class or bool?
def def_class(
    gx: "config.GlobalInfo", name: str, mv: Optional["graph.ModuleVisitor"] = None
) -> Class:
    """Define a class"""
    if not mv:
        mv = gx.modules["builtin"].mv
    assert mv
    if name in mv.classes:
        return mv.classes[name]
    elif name in mv.ext_classes:
        return mv.ext_classes[name]
    assert False


def lookup_var(
    name: str,
    parent: Optional[AllParent],
    mv: "graph.ModuleVisitor",
    local: bool = False,
) -> Optional["Variable"]:
    """Find a variable by name"""
    var = smart_lookup_var(name, parent, mv, local=local)
    if var:
        return var.var
    return None


class VarLookup(NamedTuple):
    """Variable lookup result"""

    var: "Variable"
    is_global: bool


def smart_lookup_var(
    name: str,
    parent: Optional[AllParent],
    mv: "graph.ModuleVisitor",
    local: bool = False,
) -> Optional[VarLookup]:
    """Smart lookup of a variable"""
    if not local and isinstance(parent, Class) and name in parent.parent.vars:  # XXX
        return VarLookup(parent.parent.vars[name], False)
    elif parent and name in parent.vars:
        return VarLookup(parent.vars[name], False)
    elif not (parent and local):
        # recursive lookup
        chain: List[Function] = []
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
            return None
        if name in mv.globals:
            return VarLookup(mv.globals[name], True)
    return None


def subclass(a: Class, b: Class) -> bool:
    """Check if a class is a subclass of another class"""
    if b in a.bases:
        return True
    else:
        return bool(a.bases) and subclass(a.bases[0], b)  # XXX mult inh
