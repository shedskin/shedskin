# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.cpp module."""

import argparse
import ast
from unittest.mock import MagicMock

import pytest

from shedskin.config import GlobalInfo
from shedskin import cpp, graph, python


@pytest.fixture
def gx_with_builtin():
    """Create a GlobalInfo instance with builtin module loaded."""
    options = argparse.Namespace()
    gx = GlobalInfo(options)
    graph.parse_module("builtin", gx)
    return gx


class TestCPPNamerNokeywords:
    """Tests for CPPNamer.nokeywords method."""

    def test_prefixes_cpp_keyword(self, gx_with_builtin):
        """nokeywords should prefix C++ keywords with __ss_."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        assert namer.nokeywords("int") == "__ss_int"
        assert namer.nokeywords("auto") == "__ss_auto"
        assert namer.nokeywords("const") == "__ss_const"
        assert namer.nokeywords("virtual") == "__ss_virtual"
        assert namer.nokeywords("template") == "__ss_template"

    def test_preserves_non_keywords(self, gx_with_builtin):
        """nokeywords should not modify non-keyword names."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        assert namer.nokeywords("my_variable") == "my_variable"
        assert namer.nokeywords("calculate") == "calculate"
        assert namer.nokeywords("x") == "x"
        assert namer.nokeywords("") == ""

    def test_preserves_similar_but_not_keyword(self, gx_with_builtin):
        """nokeywords should not prefix names similar to but not exactly keywords."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        assert namer.nokeywords("integer") == "integer"
        assert namer.nokeywords("constant") == "constant"
        assert namer.nokeywords("auto_") == "auto_"


class TestCPPNamerNameClass:
    """Tests for CPPNamer.name_class method."""

    def test_returns_class_ident(self, gx_with_builtin):
        """name_class should return the class identifier."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        node = ast.ClassDef(
            name="MyClass", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, node, mv, module)

        assert namer.name_class(cl) == "MyClass"


class TestCPPNamerNameVariable:
    """Tests for CPPNamer.name_variable method."""

    def test_regular_variable(self, gx_with_builtin):
        """name_variable should return name for regular variables."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        var = python.Variable("my_var", None)
        assert namer.name_variable(var) == "my_var"

    def test_variable_masking_global(self, gx_with_builtin):
        """name_variable should prefix with underscore when masking global."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        # Create a non-builtin module for the class
        # (masks_global checks `not mv.module.builtin`)
        fake_module = python.Module(
            "test_mod", "/fake/test_mod.py", "test_mod.py",
            False, None, ast.parse(""),
        )
        fake_mv = MagicMock()
        fake_mv.module = fake_module
        fake_mv.globals = {"x": python.Variable("x", None)}
        fake_mv.funcs = {}
        fake_mv.ext_funcs = {}
        fake_mv.classes = {}
        fake_mv.ext_classes = {}
        fake_module.mv = fake_mv

        cl_node = ast.ClassDef(
            name="TestCl", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, cl_node, fake_mv, fake_module)

        var = python.Variable("x", cl)
        result = namer.name_variable(var)
        assert result == "_x"


class TestCPPNamerNameFunction:
    """Tests for CPPNamer.name_function method."""

    def test_regular_function(self, gx_with_builtin):
        """name_function should return function identifier."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        func_node = ast.FunctionDef(
            name="my_func",
            args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                kw_defaults=[], kwarg=None, defaults=[],
            ),
            body=[ast.Pass()],
            decorator_list=[],
            returns=None,
        )
        func = python.Function(gx, mv, func_node)
        assert namer.name_function(func) == "my_func"


class TestCPPNamerName:
    """Tests for CPPNamer.name dispatch method."""

    def test_name_dispatches_to_correct_handler(self, gx_with_builtin):
        """name should dispatch to the correct handler based on type."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        # String dispatch
        result = namer.name("my_name")
        assert isinstance(result, str)

        # Class dispatch
        cl_node = ast.ClassDef(
            name="Foo", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, cl_node, mv, module)
        assert namer.name(cl) == "Foo"

    def test_name_with_keyword_class(self, gx_with_builtin):
        """name should prefix class names that are C++ keywords."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        # Create a class named after a C++ keyword
        cl_node = ast.ClassDef(
            name="int", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, cl_node, mv, module)
        assert namer.name(cl) == "__ss_int"


class TestCPPNamerNameStr:
    """Tests for CPPNamer.name_str conflict avoidance."""

    def test_prefixes_init_plus_module_name(self, gx_with_builtin):
        """name_str should prefix 'init' + module_name to avoid conflicts."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        result = namer.name_str("init" + module.ident)
        assert result.startswith("_")

    def test_prefixes_add_plus_module_name(self, gx_with_builtin):
        """name_str should prefix 'add' + module_name to avoid conflicts."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        result = namer.name_str("add" + module.ident)
        assert result.startswith("_")

    def test_prefixes_class_name_collision(self, gx_with_builtin):
        """name_str should prefix names that collide with class names."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        # Register a class name
        cl_node = ast.ClassDef(
            name="Widget", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, cl_node, mv, module)
        gx.allclasses.add(cl)

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        result = namer.name_str("Widget")
        assert result == "_Widget"

    def test_no_prefix_for_normal_names(self, gx_with_builtin):
        """name_str should not prefix normal, non-conflicting names."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        assert namer.name_str("calculate") == "calculate"
        assert namer.name_str("result") == "result"
        assert namer.name_str("x") == "x"


class TestCPPNamerNamespaceClass:
    """Tests for CPPNamer.namespace_class method."""

    def test_builtin_no_namespace(self, gx_with_builtin):
        """namespace_class should not add namespace for builtin classes."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        int_cl = python.def_class(gx, "int_")
        result = namer.namespace_class(int_cl)
        assert "::" not in result or result == "int_"

    def test_same_module_no_namespace(self, gx_with_builtin):
        """namespace_class should not add namespace for same-module classes."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        cl_node = ast.ClassDef(
            name="Local", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, cl_node, mv, module)
        result = namer.namespace_class(cl)
        assert result == "Local"

    def test_add_cl_prefix(self, gx_with_builtin):
        """namespace_class should prepend add_cl prefix."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        module = mv.module
        gx.main_module = module

        mock_gv = MagicMock(spec=cpp.GenerateVisitor)
        mock_gv.gx = gx
        mock_gv.module = module

        namer = cpp.CPPNamer(gx, mock_gv)

        cl_node = ast.ClassDef(
            name="Local", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, cl_node, mv, module)
        result = namer.namespace_class(cl, add_cl="cl_")
        assert result == "cl_Local"


class TestBaseNodeVisitor:
    """Tests for BaseNodeVisitor (used by GenerateVisitor)."""

    def test_visit_dispatches(self):
        """visit should dispatch to visit_Name for Name nodes."""
        from shedskin.ast_utils import BaseNodeVisitor

        visited = []

        class TestVisitor(BaseNodeVisitor):
            def visit_Name(self, node, *args):
                visited.append(node.id)

        visitor = TestVisitor()
        node = ast.Name(id="x", ctx=ast.Load())
        visitor.visit(node)
        assert visited == ["x"]

    def test_visit_with_extra_args(self):
        """visit should pass extra args to visitor methods."""
        from shedskin.ast_utils import BaseNodeVisitor

        received_args = []

        class TestVisitor(BaseNodeVisitor):
            def visit_Name(self, node, *args):
                received_args.extend(args)

        visitor = TestVisitor()
        node = ast.Name(id="x", ctx=ast.Load())
        visitor.visit(node, "arg1", "arg2")
        assert received_args == ["arg1", "arg2"]

    def test_generic_visit_recurses(self):
        """generic_visit should recurse into child nodes."""
        from shedskin.ast_utils import BaseNodeVisitor

        visited = []

        class TestVisitor(BaseNodeVisitor):
            def visit_Name(self, node, *args):
                visited.append(node.id)

        visitor = TestVisitor()
        # Create: x + y
        binop = ast.BinOp(
            left=ast.Name(id="x", ctx=ast.Load()),
            op=ast.Add(),
            right=ast.Name(id="y", ctx=ast.Load()),
        )
        visitor.visit(binop)
        assert "x" in visited
        assert "y" in visited

    def test_visit_asserts_ast_node(self):
        """visit should assert that the argument is an AST node."""
        from shedskin.ast_utils import BaseNodeVisitor

        visitor = BaseNodeVisitor()
        with pytest.raises(AssertionError, match="Expected node of type ast.AST"):
            visitor.visit("not_an_ast_node")  # type: ignore


class TestAstUtils:
    """Tests for ast_utils helper functions."""

    def test_is_assign_list_or_tuple_store(self):
        """is_assign_list_or_tuple should detect Store-context tuples."""
        from shedskin import ast_utils

        tup = ast.Tuple(elts=[], ctx=ast.Store())
        assert ast_utils.is_assign_list_or_tuple(tup) is True

        lst = ast.List(elts=[], ctx=ast.Store())
        assert ast_utils.is_assign_list_or_tuple(lst) is True

    def test_is_assign_list_or_tuple_load(self):
        """is_assign_list_or_tuple should reject Load-context tuples."""
        from shedskin import ast_utils

        tup = ast.Tuple(elts=[], ctx=ast.Load())
        assert ast_utils.is_assign_list_or_tuple(tup) is False

    def test_is_none_variants(self):
        """is_none should detect both Name('None') and Constant(None)."""
        from shedskin import ast_utils

        assert ast_utils.is_none(ast.Constant(value=None)) is True
        assert ast_utils.is_none(ast.Name(id="None", ctx=ast.Load())) is True
        assert ast_utils.is_none(ast.Constant(value=42)) is False
        assert ast_utils.is_none(ast.Name(id="x", ctx=ast.Load())) is False

    def test_is_literal_with_unary(self):
        """is_literal should detect negated numbers."""
        from shedskin import ast_utils

        neg = ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=5))
        assert ast_utils.is_literal(neg) is True

        pos = ast.UnaryOp(op=ast.UAdd(), operand=ast.Constant(value=3.14))
        assert ast_utils.is_literal(pos) is True

        # Not a number
        not_op = ast.UnaryOp(op=ast.Not(), operand=ast.Constant(value=True))
        assert ast_utils.is_literal(not_op) is False

    def test_is_fastfor(self):
        """is_fastfor should detect range/xrange loops."""
        from shedskin import ast_utils

        for_node = ast.For(
            target=ast.Name(id="i", ctx=ast.Store()),
            iter=ast.Call(
                func=ast.Name(id="range", ctx=ast.Load()),
                args=[ast.Constant(value=10)],
                keywords=[],
            ),
            body=[ast.Pass()],
            orelse=[],
        )
        assert ast_utils.is_fastfor(for_node) is True

        non_range = ast.For(
            target=ast.Name(id="i", ctx=ast.Store()),
            iter=ast.Name(id="mylist", ctx=ast.Load()),
            body=[ast.Pass()],
            orelse=[],
        )
        assert ast_utils.is_fastfor(non_range) is False

    def test_assign_rec_simple(self):
        """assign_rec should return (lvalue, rvalue) for simple assignment."""
        from shedskin import ast_utils

        left = ast.Name(id="x", ctx=ast.Store())
        right = ast.Constant(value=42)

        result = ast_utils.assign_rec(left, right)
        assert len(result) == 1
        assert result[0] == (left, right)

    def test_assign_rec_tuple_unpack(self):
        """assign_rec should handle tuple unpacking."""
        from shedskin import ast_utils

        left = ast.Tuple(
            elts=[
                ast.Name(id="x", ctx=ast.Store()),
                ast.Name(id="y", ctx=ast.Store()),
            ],
            ctx=ast.Store(),
        )
        right = ast.Tuple(
            elts=[ast.Constant(value=1), ast.Constant(value=2)],
            ctx=ast.Load(),
        )

        result = ast_utils.assign_rec(left, right)
        assert len(result) == 2

    def test_aug_msg_with_augment(self):
        """aug_msg should return __iXXX__ for augmented assignments."""
        from shedskin import ast_utils

        options = argparse.Namespace()
        gx = GlobalInfo(options)

        binop = ast.BinOp(
            left=ast.Name(id="x", ctx=ast.Load()),
            op=ast.Add(),
            right=ast.Constant(value=1),
        )
        gx.augment.add(binop)

        result = ast_utils.aug_msg(gx, binop, "add")
        assert result == "__iadd__"

    def test_aug_msg_without_augment(self):
        """aug_msg should return __XXX__ for non-augmented operations."""
        from shedskin import ast_utils

        options = argparse.Namespace()
        gx = GlobalInfo(options)

        binop = ast.BinOp(
            left=ast.Name(id="x", ctx=ast.Load()),
            op=ast.Add(),
            right=ast.Constant(value=1),
        )

        result = ast_utils.aug_msg(gx, binop, "add")
        assert result == "__add__"

    def test_is_enumerate(self):
        """is_enumerate should detect enumerate() with tuple target."""
        from shedskin import ast_utils

        enum_for = ast.For(
            target=ast.Tuple(
                elts=[
                    ast.Name(id="i", ctx=ast.Store()),
                    ast.Name(id="v", ctx=ast.Store()),
                ],
                ctx=ast.Store(),
            ),
            iter=ast.Call(
                func=ast.Name(id="enumerate", ctx=ast.Load()),
                args=[ast.Name(id="mylist", ctx=ast.Load())],
                keywords=[],
            ),
            body=[ast.Pass()],
            orelse=[],
        )
        assert ast_utils.is_enumerate(enum_for) is True

    def test_is_zip2(self):
        """is_zip2 should detect zip() with two args and tuple target."""
        from shedskin import ast_utils

        zip_for = ast.For(
            target=ast.Tuple(
                elts=[
                    ast.Name(id="a", ctx=ast.Store()),
                    ast.Name(id="b", ctx=ast.Store()),
                ],
                ctx=ast.Store(),
            ),
            iter=ast.Call(
                func=ast.Name(id="zip", ctx=ast.Load()),
                args=[
                    ast.Name(id="list1", ctx=ast.Load()),
                    ast.Name(id="list2", ctx=ast.Load()),
                ],
                keywords=[],
            ),
            body=[ast.Pass()],
            orelse=[],
        )
        assert ast_utils.is_zip2(zip_for) is True


class TestPythonModuleModel:
    """Tests for python.Module used by code generation."""

    def test_full_path(self):
        """Module.full_path should return namespaced path."""
        mod = python.Module("pkg.sub.mod", "/fake/mod.py", "mod.py", False, None, ast.parse(""))
        assert mod.full_path() == "__pkg__::__sub__::__mod__"

    def test_full_path_simple(self):
        """Module.full_path should work for simple module names."""
        mod = python.Module("test", "/fake/test.py", "test.py", False, None, ast.parse(""))
        assert mod.full_path() == "__test__"

    def test_include_path(self):
        """Module.include_path should return .hpp extension."""
        mod = python.Module("test", "/fake/test.py", "test.py", False, None, ast.parse(""))
        result = mod.include_path()
        assert result.endswith(".hpp")

    def test_include_path_init(self):
        """Module.include_path should handle __init__.py correctly."""
        mod = python.Module("pkg", "/fake/pkg/__init__.py", "pkg/__init__.py", False, None, ast.parse(""))
        result = mod.include_path()
        assert "__init__.hpp" in result


class TestPythonClassModel:
    """Tests for python.Class used by code generation."""

    def test_tvar_names_list(self, gx_with_builtin):
        """tvar_names should return ['unit'] for list class."""
        gx = gx_with_builtin
        list_cl = python.def_class(gx, "list")
        assert list_cl.tvar_names() == ["unit"]

    def test_tvar_names_dict(self, gx_with_builtin):
        """tvar_names should return ['unit', 'value'] for dict class."""
        gx = gx_with_builtin
        dict_cl = python.def_class(gx, "dict")
        assert dict_cl.tvar_names() == ["unit", "value"]

    def test_tvar_names_tuple2(self, gx_with_builtin):
        """tvar_names should return ['first', 'second'] for tuple2 class."""
        gx = gx_with_builtin
        tuple2_cl = python.def_class(gx, "tuple2")
        assert tuple2_cl.tvar_names() == ["first", "second"]

    def test_tvar_names_non_template(self, gx_with_builtin):
        """tvar_names should return [] for non-template classes."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        assert int_cl.tvar_names() == []

    def test_ancestors_empty_for_base_class(self, gx_with_builtin):
        """ancestors should return empty set for class with no bases."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        cl_node = ast.ClassDef(
            name="Orphan", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, cl_node, mv, mv.module)
        assert cl.ancestors() == set()

    def test_ancestors_inclusive(self, gx_with_builtin):
        """ancestors(inclusive=True) should include the class itself."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        cl_node = ast.ClassDef(
            name="Self", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, cl_node, mv, mv.module)
        result = cl.ancestors(inclusive=True)
        assert cl in result

    def test_descendants_empty(self, gx_with_builtin):
        """descendants should return empty set for leaf class."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        cl_node = ast.ClassDef(
            name="Leaf", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, cl_node, mv, mv.module)
        assert cl.descendants() == set()

    def test_descendants_inclusive(self, gx_with_builtin):
        """descendants(inclusive=True) should include the class itself."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        cl_node = ast.ClassDef(
            name="Root", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, cl_node, mv, mv.module)
        result = cl.descendants(inclusive=True)
        assert cl in result


class TestLookupImplementor:
    """Tests for python.lookup_implementor function."""

    def test_direct_implementor(self, gx_with_builtin):
        """lookup_implementor should find method in direct class."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        cl_node = ast.ClassDef(
            name="Impl", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, cl_node, mv, mv.module)

        func_node = ast.FunctionDef(
            name="method",
            args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                kw_defaults=[], kwarg=None, defaults=[],
            ),
            body=[ast.Pass()],
            decorator_list=[],
            returns=None,
        )
        func = python.Function(gx, mv, func_node, cl)
        func.inherited = None
        cl.funcs["method"] = func

        result = python.lookup_implementor(cl, "method")
        assert result == "Impl"

    def test_no_implementor(self, gx_with_builtin):
        """lookup_implementor should return None when method not found."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        cl_node = ast.ClassDef(
            name="Empty", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, cl_node, mv, mv.module)

        result = python.lookup_implementor(cl, "nonexistent")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
