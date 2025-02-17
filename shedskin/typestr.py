# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.typestr: generate type declarations

Contains functions and classes for generating C++ type declarations from Python types.

The module provides functionality to:
- Convert Python type annotations and inferred types to C++ type declarations
- Handle template parameters and specialization
- Generate type declarations for variables, functions, and classes
- Resolve type dependencies and inheritance hierarchies
- Format type strings according to C++ syntax rules

Key components:
- `types_var_types()`: Get types associated with a variable
- `ExtmodError`: Exception raised for extension module type errors
- `Types`: Type alias for sets of (Class, int) tuples representing Python types

This module is used by the code generator to produce valid C++ type declarations
from the Python type information gathered during type inference.
"""

import ast
import logging
# type-checking
from typing import (TYPE_CHECKING, Any, Dict, Iterable, Optional, Tuple, Type,
                    TypeAlias, Union)

from . import error, infer, python

if TYPE_CHECKING:
    from . import config, graph

Types: TypeAlias = set[Tuple["python.Class", int]]  # TODO merge with cpp.py version


logger = logging.getLogger("typestr")


class ExtmodError(Exception):
    pass


def types_var_types(gx: "config.GlobalInfo", types: Types, varname: str) -> Types:
    """Get the types of a variable"""
    subtypes = set()
    for t in types:
        if varname not in t[0].vars:
            continue
        var = t[0].vars[varname]
        if (var, t[1], 0) in gx.cnode:
            subtypes.update(gx.cnode[var, t[1], 0].types())
    return subtypes


def types_classes(types: Types) -> set["python.Class"]:
    """Get the classes of a variable"""
    return set(t[0] for t in types if isinstance(t[0], python.Class))


def unboxable(gx: "config.GlobalInfo", types: Types) -> Optional[str]:
    """Check if a variable is unboxable"""
    if not isinstance(types, set):
        types = infer.inode(gx, types).types()
    classes = set(t[0] for t in types)

    if [cl for cl in classes if cl.ident not in ["int_", "float_", "bool_", "complex"]]:
        return None
    else:
        if classes:
            return classes.pop().ident
        return None


def singletype(gx: "config.GlobalInfo", node: Any, t: Type[Any]) -> Any:
    """Check if a variable has a single type"""
    types = [t[0] for t in infer.inode(gx, node).types()]
    if len(types) == 1 and isinstance(types[0], t):
        return types[0]


def singletype2(types: Types, t: Type[Any]) -> Any:
    """Check if a variable has a single type"""
    ltypes = list(types)
    if len(types) == 1 and isinstance(ltypes[0][0], t):
        return ltypes[0][0]


def polymorphic_t(gx: "config.GlobalInfo", types: Types) -> set["python.Class"]:
    """Get the polymorphic classes of a variable"""
    return polymorphic_cl(gx, (t[0] for t in types))


def polymorphic_cl(
    gx: "config.GlobalInfo", classes: Iterable["python.Class"]
) -> set["python.Class"]:
    """Get the polymorphic classes of a variable"""
    cls = set(cl for cl in classes)
    if (
        len(cls) > 1
        and python.def_class(gx, "none") in cls
        and python.def_class(gx, "int_") not in cls
        and python.def_class(gx, "float_") not in cls
        and python.def_class(gx, "bool_") not in cls
    ):
        cls.remove(python.def_class(gx, "none"))
    if (
        python.def_class(gx, "tuple2") in cls and python.def_class(gx, "tuple") in cls
    ):  # XXX hmm
        cls.remove(python.def_class(gx, "tuple2"))
    return cls


# --- determine lowest common parent classes (inclusive)
def lowest_common_parents(classes: Iterable["python.Class"]) -> list["python.Class"]:
    """Get the lowest common parent classes of a variable"""
    classes = [cl for cl in classes if isinstance(cl, python.Class)]

    # collect all possible parent classes
    parents = set()
    for parent in classes:
        while True:
            parent.lcpcount = 0
            parents.add(parent)
            if parent.bases:
                parent = parent.bases[0]
            else:
                break

    # count how many descendants in 'classes' each has
    for parent in classes:
        while True:
            parent.lcpcount += 1
            if parent.bases:
                parent = parent.bases[0]
            else:
                break

    # remove those that don't add anything
    useless = set()
    for parent in parents:
        orig = parent
        while True:
            if parent != orig:
                if parent.lcpcount > orig.lcpcount:
                    useless.add(orig)
                elif parent.lcpcount == orig.lcpcount:
                    useless.add(parent)
            if parent.bases:
                parent = parent.bases[0]
            else:
                break

    return list(parents - useless)


def nodetypestr(
    gx: "config.GlobalInfo",
    node: Any,
    parent: Optional[Any] = None,
    cplusplus: bool = True,
    check_extmod: bool = False,
    check_ret: bool = False,
    mv: Optional["graph.ModuleVisitor"] = None,
) -> str:
    """Get the type string of a node"""
    # XXX minimize
    if (
        cplusplus and isinstance(node, python.Variable) and node.looper
    ):  # XXX to declaredefs?
        return (
            nodetypestr(gx, node.looper, None, cplusplus, mv=mv)[:-2] + "::for_in_loop "
        )
    if (
        cplusplus and isinstance(node, python.Variable) and node.wopper
    ):  # XXX to declaredefs?
        ts = nodetypestr(gx, node.wopper, None, cplusplus, mv=mv)
        if ts.startswith("dict<"):
            return "__GC_DICT<" + ts[5:-3] + ">::iterator "
    types = gx.merged_inh[node]
    return typestr(gx, types, None, cplusplus, node, check_extmod, 0, check_ret, mv=mv)


def typestr(
    gx: "config.GlobalInfo",
    types: Types,
    parent: Optional["python.Function"] = None,
    cplusplus: bool = True,
    node: Optional[Union[ast.AST, "python.Variable"]] = None,
    check_extmod: bool = False,
    depth: int = 0,
    check_ret: bool = False,
    mv: Optional["graph.ModuleVisitor"] = None,
) -> str:
    """Get the type string of a node"""
    try:
        ts = typestrnew(
            gx,
            types,
            cplusplus,
            node,
            check_extmod,
            depth,
            check_ret,
            mv=mv,
        )
    except RuntimeError:
        assert mv
        if (
            not mv.module.builtin
            and isinstance(node, python.Variable)
            and not node.name.startswith("__")
        ):  # XXX startswith
            if node.parent:
                varname = repr(node)
            else:
                varname = "'%s'" % node.name
            error.error(
                "Variable %s has dynamic (sub)type" % varname, gx, node, warning=True
            )
        ts = "pyobj *"
    if cplusplus:
        if not ts.endswith("*"):
            ts += " "
        return ts
    return "[" + ts + "]"


def dynamic_variable_error(
    gx: "config.GlobalInfo",
    node: "python.Variable",
    types: Types,
    conv2: Dict[str, str],
) -> None:
    """Handle a dynamic variable error"""
    if not node.name.startswith("__"):  # XXX startswith
        classes = polymorphic_cl(gx, types_classes(types))
        if (
            python.def_class(gx, "bytes_") in classes
            and python.def_class(gx, "str_") in classes
        ):
            lcp = classes
        else:
            lcp = set(lowest_common_parents(classes))

        if node.parent:
            varname = "%s" % node
        else:
            varname = "'%s'" % node
        if [t for t in types if isinstance(t[0], python.Function)]:
            error.error(
                "Variable %s has dynamic (sub)type: {%s, function}"
                % (
                    varname,
                    ", ".join(sorted(conv2.get(cl.ident, cl.ident) for cl in lcp)),
                ),
                gx,
                node,
                warning=True,
            )
        else:
            error.error(
                "Variable %s has dynamic (sub)type: {%s}"
                % (
                    varname,
                    ", ".join(sorted(conv2.get(cl.ident, cl.ident) for cl in lcp)),
                ),
                gx,
                node,
                warning=True,
            )


def typestrnew(
    gx: "config.GlobalInfo",
    types: Types,
    cplusplus: bool = True,
    node: Optional[Union[ast.AST, "python.Variable"]] = None,
    check_extmod: bool = False,
    depth: int = 0,
    check_ret: bool = False,
    mv: Optional["graph.ModuleVisitor"] = None,
) -> str:
    """Get the type string of a node"""
    if depth == 10:
        raise RuntimeError()

    # --- annotation or c++ code
    conv1 = {
        "int_": "__ss_int",
        "float_": "__ss_float",
        "str_": "str",
        "none": "int",
        "bool_": "__ss_bool",
        "complex": "complex",
        "bytes_": "bytes",
    }
    conv2 = {
        "int_": "int",
        "float_": "float",
        "str_": "str",
        "class_": "class",
        "none": "None",
        "bool_": "bool",
        "complex": "complex",
        "bytes_": "bytes",
    }
    if cplusplus:
        sep, ptr, conv = "<>", " *", conv1
    else:
        sep, ptr, conv = "()", "", conv2

    def map(ident: str) -> str:
        """Map a type identifier to a C++ type string"""
        if cplusplus:
            return ident + " *"
        return conv.get(ident, ident)

    anon_funcs = set(t[0] for t in types if isinstance(t[0], python.Function))
    static_cls = set(t[0] for t in types if isinstance(t[0], python.StaticClass))
    if (anon_funcs or static_cls) and check_extmod:
        raise ExtmodError()
    if anon_funcs:
        if [
            t
            for t in types
            if not isinstance(t[0], python.Function)
            and t[0] is not python.def_class(gx, "none")
        ]:
            if isinstance(node, python.Variable):
                dynamic_variable_error(gx, node, types, conv2)
            else:
                error.error("function mixed with non-function", gx, node, warning=True)
        f = anon_funcs.pop()
        assert isinstance(f, python.Function)
        assert f.lambdanr is not None
        if f.mv != mv:
            return f.mv.module.full_path() + "::" + "lambda%d" % f.lambdanr
        return "lambda%d" % f.lambdanr

    classes = polymorphic_cl(gx, types_classes(types))
    if (
        python.def_class(gx, "bytes_") in classes
        and python.def_class(gx, "str_") in classes
    ):
        lcp = classes
    else:
        lcp = set(lowest_common_parents(classes))

    # --- multiple parent classes
    if len(lcp) > 1:
        if set(lcp) == set(
            [python.def_class(gx, "int_"), python.def_class(gx, "float_")]
        ):
            return conv["float_"]
        elif not node or (
            infer.inode(gx, node).mv and infer.inode(gx, node).mv.module.builtin
        ):
            if python.def_class(gx, "complex") in lcp:  # XXX
                return conv["complex"]
            elif python.def_class(gx, "float_") in lcp:
                return conv["float_"]
            elif python.def_class(gx, "int_") in lcp:
                return conv["int_"]
            else:
                return "pyobj *"
        elif isinstance(node, python.Variable):
            dynamic_variable_error(gx, node, types, conv2)
            return "pyobj *"
        elif node not in gx.bool_test_only:
            error.error(
                "expression has dynamic (sub)type: {%s}"
                % ", ".join(sorted(conv2.get(cl.ident, cl.ident) for cl in lcp)),
                gx,
                node,
                warning=True,
            )
    elif not classes:
        if cplusplus:
            return "void *"
        return ""

    cl = lcp.pop()

    if check_ret and cl.mv.module.ident == "collections" and cl.ident == "defaultdict":
        logger.warn("defaultdicts are returned as dicts")
    elif (
        check_extmod
        and cl.mv.module.builtin
        and not (
            cl.mv.module.ident == "builtin"
            and cl.ident
            in [
                "int_",
                "float_",
                "complex",
                "str_",
                "bytes_",
                "list",
                "tuple",
                "tuple2",
                "dict",
                "set",
                "frozenset",
                "none",
                "bool_",
            ]
        )
        and not (cl.mv.module.ident == "collections" and cl.ident == "defaultdict")
    ):
        raise ExtmodError()

    # --- simple built-in types
    if cl.ident in ["int_", "float_", "bool_", "complex"]:
        return conv[cl.ident]
    elif cl.ident == "str_":
        return cl.ident[:-1] + ptr
    elif cl.ident in ("bytes_", "bytearray"):
        return "bytes" + ptr
    elif cl.ident == "none":
        if cplusplus:
            return "void *"
        return "None"

    # --- namespace prefix
    namespace = ""
    assert mv
    if cl.module not in [mv.module, gx.modules["builtin"]]:
        if cplusplus:
            namespace = cl.module.full_path() + "::"
        else:
            namespace = "::".join(cl.module.name_list) + "::"
        if cplusplus:
            mv.module.prop_includes.add(cl.module)

    template_vars = cl.tvar_names()
    if template_vars:
        subtypes = []
        for tvar in template_vars:
            vartypes = types_var_types(gx, types, tvar)
            ts = typestrnew(
                gx,
                vartypes,
                cplusplus,
                node,
                check_extmod,
                depth + 1,
                mv=mv,
            )
            if [t[0] for t in vartypes if isinstance(t[0], python.Function)]:
                ident = cl.ident
                if ident == "tuple2":
                    ident = "tuple"
                error.error(
                    "'%s' instance containing function reference" % ident,
                    gx,
                    node,
                    warning=True,
                )  # XXX test
            subtypes.append(ts)
    else:
        if cl.ident in gx.cpp_keywords:
            return namespace + gx.ss_prefix + map(cl.ident)
        return namespace + map(cl.ident)

    ident = cl.ident

    # --- binary tuples
    if ident == "tuple2":
        if subtypes[0] == subtypes[1]:
            ident, subtypes = "tuple", [subtypes[0]]
    if ident == "tuple2" and not cplusplus:
        ident = "tuple"
    elif ident == "tuple" and cplusplus:
        return namespace + "tuple" + sep[0] + subtypes[0] + sep[1] + ptr

    if ident in ["frozenset", "pyset"] and cplusplus:
        ident = "set"

    if ident in gx.cpp_keywords:
        ident = gx.ss_prefix + ident

    # --- final type representation
    return namespace + ident + sep[0] + ", ".join(subtypes) + sep[1] + ptr


def incompatible_assignment_rec(
    gx: "config.GlobalInfo", argtypes: Types, formaltypes: Types, depth: int = 0
) -> bool:
    """Check if an assignment is incompatible"""
    if depth == 10:
        return False
    argclasses = types_classes(argtypes)
    formalclasses = types_classes(formaltypes)
    inttype = (python.def_class(gx, "int_"), 0)
    booltype = (python.def_class(gx, "bool_"), 0)
    floattype = (python.def_class(gx, "float_"), 0)

    # int -> float
    if depth > 0 and (argtypes == set([inttype]) and floattype in formaltypes):
        return True

    # bool -> int
    if depth > 0 and (argtypes == set([booltype]) and inttype in formaltypes):
        return True

    # void * -> non-pointer
    if not argclasses and [
        cl for cl in formalclasses if cl.ident in ["int_", "float_", "bool_", "complex"]
    ]:
        return True

    # None -> anything
    if len(argclasses) == 1 and python.def_class(gx, "none") in argclasses:
        return False

    # recurse on subvars
    lcp = lowest_common_parents(polymorphic_cl(gx, formalclasses))
    if len(lcp) != 1:  # XXX
        return False
    tvars = lcp[0].tvar_names()
    for tvar in tvars:
        argvartypes = types_var_types(gx, argtypes, tvar)
        formalvartypes = types_var_types(gx, formaltypes, tvar)
        if incompatible_assignment_rec(gx, argvartypes, formalvartypes, depth + 1):
            return True
    return False
