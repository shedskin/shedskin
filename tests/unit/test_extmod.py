# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.extmod module."""

import argparse
import ast
import io
from unittest.mock import MagicMock, PropertyMock

import pytest

from shedskin.config import GlobalInfo
from shedskin import extmod, graph, infer, python


@pytest.fixture
def gx_with_builtin():
    """Create a GlobalInfo instance with builtin module loaded."""
    options = argparse.Namespace()
    gx = GlobalInfo(options)
    graph.parse_module("builtin", gx)
    return gx


class TestOverloadConstants:
    """Tests for overload operator constants."""

    def test_overload_single_contents(self):
        """OVERLOAD_SINGLE should contain unary operator names."""
        assert "__neg__" in extmod.OVERLOAD_SINGLE
        assert "__pos__" in extmod.OVERLOAD_SINGLE
        assert "__abs__" in extmod.OVERLOAD_SINGLE
        assert "__bool__" in extmod.OVERLOAD_SINGLE
        assert len(extmod.OVERLOAD_SINGLE) == 4

    def test_overload_contains_binary_ops(self):
        """OVERLOAD should contain binary operator names."""
        assert "__add__" in extmod.OVERLOAD
        assert "__sub__" in extmod.OVERLOAD
        assert "__mul__" in extmod.OVERLOAD
        assert "__mod__" in extmod.OVERLOAD
        assert "__divmod__" in extmod.OVERLOAD
        assert "__pow__" in extmod.OVERLOAD

    def test_overload_excludes_div(self):
        """OVERLOAD must not contain '__div__'.

        '__div__' is a Python 2 special method with no CPython 3
        PyNumberMethods slot; do_extmod_methoddef writes this list
        positionally into that struct, so a phantom '__div__' entry shifts
        every field after it (mod/divmod/pow/neg/pos/abs/bool) into the
        wrong slot. Confirmed by building and running an extension module:
        before this fix, __mod__ landed in the nb_divmod slot, __pow__ in
        nb_negative (wrong arity), and so on.
        """
        assert "__div__" not in extmod.OVERLOAD

    def test_overload_matches_pynumbermethods_layout(self):
        """OVERLOAD's order must match real PyNumberMethods field order.

        do_extmod_methoddef initializes the struct positionally, so this
        list has to line up with CPython's actual
        nb_add/nb_subtract/nb_multiply/nb_remainder/nb_divmod/nb_power/
        nb_negative/nb_positive/nb_absolute/nb_bool field order exactly.
        """
        assert extmod.OVERLOAD == [
            "__add__",
            "__sub__",
            "__mul__",
            "__mod__",
            "__divmod__",
            "__pow__",
            "__neg__",
            "__pos__",
            "__abs__",
            "__bool__",
        ]

    def test_overload_includes_single(self):
        """OVERLOAD should include all OVERLOAD_SINGLE entries."""
        for op in extmod.OVERLOAD_SINGLE:
            assert op in extmod.OVERLOAD

    def test_overload_total_count(self):
        """OVERLOAD should have 6 binary + 4 unary = 10 entries."""
        assert len(extmod.OVERLOAD) == 10


class TestClname:
    """Tests for clname function."""

    def test_simple_module(self, gx_with_builtin):
        """clname should generate proper prefixed name for single module."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        node = ast.ClassDef(
            name="MyClass",
            bases=[],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[],
        )
        cl = python.Class(gx, node, mv, mv.module)

        result = extmod.clname(cl)
        assert result == "__ss_builtin_MyClass"

    def test_nested_module(self, gx_with_builtin):
        """clname should join nested module names with underscores."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        node = ast.ClassDef(
            name="Widget",
            bases=[],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[],
        )
        cl = python.Class(gx, node, mv, mv.module)
        # Simulate nested module
        cl.mv.module.name_list = ["pkg", "sub", "mod"]

        result = extmod.clname(cl)
        assert result == "__ss_pkg_sub_mod_Widget"


class TestExtensionModuleInit:
    """Tests for ExtensionModule initialization."""

    def test_init_stores_gx_and_gv(self, gx_with_builtin):
        """ExtensionModule should store gx and gv references."""
        gx = gx_with_builtin
        mock_gv = MagicMock()

        em = extmod.ExtensionModule(gx, mock_gv)
        assert em.gx is gx
        assert em.gv is mock_gv

    def test_write_outputs_to_gv_out(self, gx_with_builtin):
        """ExtensionModule.write should print to gv.out."""
        gx = gx_with_builtin
        output = io.StringIO()
        mock_gv = MagicMock()
        mock_gv.out = output

        em = extmod.ExtensionModule(gx, mock_gv)
        em.write("test output")

        assert "test output" in output.getvalue()


class TestSupportedVars:
    """Tests for supported_vars filtering."""

    def test_empty_vars(self, gx_with_builtin):
        """supported_vars should return empty list for no variables."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        em = extmod.ExtensionModule(gx, mock_gv)

        result = em.supported_vars([])
        assert result == []

    def test_filters_invisible_vars(self, gx_with_builtin):
        """supported_vars should filter out invisible variables."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        mock_gv.mv = gx.modules["builtin"].mv
        em = extmod.ExtensionModule(gx, mock_gv)

        var = python.Variable("_hidden", None)
        var.invisible = True

        # Variable not in merged_inh, so filtered first
        result = em.supported_vars([var])
        assert var not in result

    def test_filters_vars_not_in_merged_inh(self, gx_with_builtin):
        """supported_vars should filter out variables not in merged_inh."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        mock_gv.mv = gx.modules["builtin"].mv
        em = extmod.ExtensionModule(gx, mock_gv)

        var = python.Variable("myvar", None)

        result = em.supported_vars([var])
        assert var not in result

    def test_filters_dunder_vars(self, gx_with_builtin):
        """supported_vars should filter out __dunder__ variables."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        mock_gv.mv = gx.modules["builtin"].mv
        em = extmod.ExtensionModule(gx, mock_gv)

        var = python.Variable("__internal", None)
        int_cl = python.def_class(gx, "int_")
        gx.merged_inh[var] = {(int_cl, 0)}

        result = em.supported_vars([var])
        assert var not in result

    def test_filters_none_name_vars(self, gx_with_builtin):
        """supported_vars should filter out variables with None name."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        mock_gv.mv = gx.modules["builtin"].mv
        em = extmod.ExtensionModule(gx, mock_gv)

        var = python.Variable(None, None)  # type: ignore
        int_cl = python.def_class(gx, "int_")
        gx.merged_inh[var] = {(int_cl, 0)}

        result = em.supported_vars([var])
        assert var not in result

    def test_filters_empty_merged_inh(self, gx_with_builtin):
        """supported_vars should filter out variables with empty merged_inh."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        mock_gv.mv = gx.modules["builtin"].mv
        em = extmod.ExtensionModule(gx, mock_gv)

        var = python.Variable("myvar", None)
        gx.merged_inh[var] = set()  # empty type set

        result = em.supported_vars([var])
        assert var not in result


class TestSupportedFuncs:
    """Tests for supported_funcs filtering."""

    def test_empty_funcs(self, gx_with_builtin):
        """supported_funcs should return empty list for no functions."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        em = extmod.ExtensionModule(gx, mock_gv)

        result = em.supported_funcs([])
        assert result == []

    def test_filters_generators(self, gx_with_builtin):
        """supported_funcs should filter out generators."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        mock_gv = MagicMock()
        mock_gv.inhcpa.return_value = True
        mock_gv.mv = mv
        em = extmod.ExtensionModule(gx, mock_gv)

        func_node = ast.FunctionDef(
            name="gen",
            args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                kw_defaults=[], kwarg=None, defaults=[],
            ),
            body=[ast.Pass()],
            decorator_list=[],
            returns=None,
        )
        func = python.Function(gx, mv, func_node)
        func.isGenerator = True

        result = em.supported_funcs([func])
        assert func not in result

    def test_filters_uncalled_funcs(self, gx_with_builtin):
        """supported_funcs should filter out uncalled functions."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        mock_gv = MagicMock()
        mock_gv.inhcpa.return_value = False
        mock_gv.mv = mv
        em = extmod.ExtensionModule(gx, mock_gv)

        func_node = ast.FunctionDef(
            name="uncalled",
            args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                kw_defaults=[], kwarg=None, defaults=[],
            ),
            body=[ast.Pass()],
            decorator_list=[],
            returns=None,
        )
        func = python.Function(gx, mv, func_node)

        result = em.supported_funcs([func])
        assert func not in result

    def test_filters_setattr_getattr(self, gx_with_builtin):
        """supported_funcs should filter __setattr__ and __getattr__."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        mock_gv = MagicMock()
        mock_gv.inhcpa.return_value = True
        mock_gv.mv = mv
        em = extmod.ExtensionModule(gx, mock_gv)

        for method_name in ["__setattr__", "__getattr__"]:
            func_node = ast.FunctionDef(
                name=method_name,
                args=ast.arguments(
                    posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                    kw_defaults=[], kwarg=None, defaults=[],
                ),
                body=[ast.Pass()],
                decorator_list=[],
                returns=None,
            )
            func = python.Function(gx, mv, func_node)

            result = em.supported_funcs([func])
            assert func not in result


class TestHasMethod:
    """Tests for has_method function."""

    def test_no_method(self, gx_with_builtin):
        """has_method should return False when method doesn't exist."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        mock_gv = MagicMock()
        em = extmod.ExtensionModule(gx, mock_gv)

        node = ast.ClassDef(
            name="Test", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, node, mv, mv.module)

        result = em.has_method(cl, "__init__")
        assert result is False

    def test_invisible_method(self, gx_with_builtin):
        """has_method should return False for invisible methods."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        mock_gv = MagicMock()
        em = extmod.ExtensionModule(gx, mock_gv)

        node = ast.ClassDef(
            name="Test", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, node, mv, mv.module)

        func_node = ast.FunctionDef(
            name="hidden",
            args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                kw_defaults=[], kwarg=None, defaults=[],
            ),
            body=[ast.Pass()],
            decorator_list=[],
            returns=None,
        )
        func = python.Function(gx, mv, func_node, cl)
        func.invisible = True
        cl.funcs["hidden"] = func

        result = em.has_method(cl, "hidden")
        assert result is False

    def test_inherited_method(self, gx_with_builtin):
        """has_method should return False for inherited methods."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        mock_gv = MagicMock()
        em = extmod.ExtensionModule(gx, mock_gv)

        node = ast.ClassDef(
            name="Test", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, node, mv, mv.module)

        func_node = ast.FunctionDef(
            name="inherited_func",
            args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                kw_defaults=[], kwarg=None, defaults=[],
            ),
            body=[ast.Pass()],
            decorator_list=[],
            returns=None,
        )
        func = python.Function(gx, mv, func_node, cl)
        func.inherited = func_node  # mark as inherited
        cl.funcs["inherited_func"] = func

        result = em.has_method(cl, "inherited_func")
        assert result is False


class TestExportedClasses:
    """Tests for exported_classes method."""

    @pytest.fixture
    def fake_module_mv(self, gx_with_builtin):
        """Create a fake non-builtin module with its own mv for testing."""
        gx = gx_with_builtin
        builtin_mv = gx.modules["builtin"].mv

        fake_module = python.Module(
            "test_mod", "/fake/test_mod.py", "test_mod.py",
            False, None, ast.parse(""),
        )
        # Create a minimal mock mv for the fake module
        fake_mv = MagicMock()
        fake_mv.module = fake_module
        fake_mv.classes = {}
        fake_module.mv = fake_mv

        return gx, fake_mv, fake_module

    def test_excludes_exception_subclasses(self, fake_module_mv):
        """exported_classes should exclude classes inheriting from Exception."""
        gx, fake_mv, fake_module = fake_module_mv
        builtin_mv = gx.modules["builtin"].mv

        mock_gv = MagicMock()
        mock_gv.module = fake_module
        mock_gv.module.mv = fake_mv
        em = extmod.ExtensionModule(gx, mock_gv)

        exception_cl = python.def_class(gx, "Exception")

        node = ast.ClassDef(
            name="MyError", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        error_cl = python.Class(gx, node, builtin_mv, fake_module)
        error_cl.bases = [exception_cl]
        error_cl.def_order = 0

        fake_mv.classes = {"MyError": error_cl}

        result = em.exported_classes()
        assert error_cl not in result

    def test_includes_regular_classes(self, fake_module_mv):
        """exported_classes should include regular classes."""
        gx, fake_mv, fake_module = fake_module_mv
        builtin_mv = gx.modules["builtin"].mv

        mock_gv = MagicMock()
        mock_gv.module = fake_module
        mock_gv.module.mv = fake_mv
        em = extmod.ExtensionModule(gx, mock_gv)

        node = ast.ClassDef(
            name="MyClass", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        regular_cl = python.Class(gx, node, builtin_mv, fake_module)
        regular_cl.def_order = 0

        fake_mv.classes = {"MyClass": regular_cl}

        result = em.exported_classes()
        assert regular_cl in result

    def test_sorted_by_def_order(self, fake_module_mv):
        """exported_classes should be sorted by def_order."""
        gx, fake_mv, fake_module = fake_module_mv
        builtin_mv = gx.modules["builtin"].mv

        mock_gv = MagicMock()
        mock_gv.module = fake_module
        mock_gv.module.mv = fake_mv
        em = extmod.ExtensionModule(gx, mock_gv)

        node_a = ast.ClassDef(
            name="A", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        node_b = ast.ClassDef(
            name="B", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl_a = python.Class(gx, node_a, builtin_mv, fake_module)
        cl_b = python.Class(gx, node_b, builtin_mv, fake_module)
        cl_a.def_order = 5
        cl_b.def_order = 2

        fake_mv.classes = {"A": cl_a, "B": cl_b}

        result = em.exported_classes()
        assert result == [cl_b, cl_a]  # B (order=2) before A (order=5)


class TestDoInitMods:
    """Tests for do_init_mods method."""

    def test_skips_builtin_and_current(self, gx_with_builtin):
        """do_init_mods should skip builtin and current module."""
        gx = gx_with_builtin
        output = io.StringIO()
        mock_gv = MagicMock()
        mock_gv.out = output
        mock_gv.module = gx.modules["builtin"]
        em = extmod.ExtensionModule(gx, mock_gv)

        # Only builtin module loaded, which should be skipped
        em.do_init_mods("__init")

        # Should not output anything (builtin is skipped)
        assert output.getvalue() == ""



if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestReduceSetstate:
    """Tests for the pickle support generated by do_reduce_setstate.

    The state is keyed by attribute name rather than by position. With a
    positional tuple, adding or removing an attribute renumbers every slot
    after it, so a pickle written by one build of a module is misread by the
    next -- and when the stored tuple is shorter than the current variable
    count the conversion is handed a NULL and aborts the interpreter.
    """

    def _generate(self, gx, varnames):
        """Run do_reduce_setstate for a class with the given attributes."""
        output = io.StringIO()
        mock_gv = MagicMock()
        mock_gv.out = output
        mock_gv.mv = gx.modules["builtin"].mv
        mock_gv.module.name_list = ["m"]
        mock_gv.cpp_name.side_effect = lambda var: var.name
        em = extmod.ExtensionModule(gx, mock_gv)

        cl = MagicMock()
        cl.ident = "C"
        cl.ancestors.return_value = set()
        cl.module.name_list = ["m"]

        int_class = python.def_class(gx, "int_")
        variables = []
        for name in varnames:
            var = python.Variable(name, None)
            var.parent = None
            # nodetypestr consults merged_inh to render the __setstate__ cast
            gx.merged_inh[var] = {(int_class, 0)}
            variables.append(var)

        em.do_reduce_setstate(cl, variables)
        return output.getvalue()

    def test_state_is_a_dict_keyed_by_name(self, gx_with_builtin):
        """__reduce__ should build a name-keyed dict, not a positional tuple."""
        out = self._generate(gx_with_builtin, ["alpha", "beta"])

        assert "PyDict_New()" in out
        assert '__ss_dict_steal(b, "alpha"' in out
        assert '__ss_dict_steal(b, "beta"' in out
        # the state must not be built positionally
        assert "PyTuple_SetItem(b," not in out

    def test_setstate_looks_up_by_name(self, gx_with_builtin):
        """__setstate__ should read each attribute by name."""
        out = self._generate(gx_with_builtin, ["alpha", "beta"])

        assert '__ss_dict_lookup(state, "alpha")' in out
        assert '__ss_dict_lookup(state, "beta")' in out
        assert "PyTuple_GetItem(state," not in out

    def test_missing_key_is_guarded(self, gx_with_builtin):
        """A key absent from an older pickle must not reach __to_ss as NULL."""
        out = self._generate(gx_with_builtin, ["alpha"])

        for line in out.splitlines():
            if "__to_ss<" in line and "__ss_object->alpha" in line:
                assert line.strip().startswith("if (value)"), line
                break
        else:
            raise AssertionError("no assignment generated for 'alpha'")

    def test_attribute_order_does_not_change_keys(self, gx_with_builtin):
        """Adding an attribute must not disturb the others' state keys."""
        before = self._generate(gx_with_builtin, ["beta", "gamma"])
        after = self._generate(gx_with_builtin, ["alpha", "beta", "gamma"])

        for name in ("beta", "gamma"):
            assert '__ss_dict_steal(b, "%s"' % name in before
            assert '__ss_dict_steal(b, "%s"' % name in after
            assert '__ss_dict_lookup(state, "%s")' % name in before
            assert '__ss_dict_lookup(state, "%s")' % name in after


class TestDealloc:
    """Tests for the generated tp_dealloc function.

    self->__ss_object must be read (to remove the __ss_proxy entry) before
    tp_free releases self's memory. Reading it afterwards is a use-after-free:
    confirmed with valgrind, which flags an "Invalid read" inside the
    generated Dealloc function once tp_free has already freed that block.
    """

    def _generate(self, gx):
        builtin_mv = gx.modules["builtin"].mv

        fake_module = python.Module(
            "test_mod", "/fake/test_mod.py", "test_mod.py",
            False, None, ast.parse(""),
        )
        fake_mv = MagicMock()
        fake_mv.module = fake_module
        fake_mv.classes = {}
        fake_module.mv = fake_mv

        node = ast.ClassDef(
            name="Foo", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, node, builtin_mv, fake_module)
        cl.def_order = 0
        cl.funcs = {}
        cl.vars = {}
        cl.bases = []

        mock_gv = MagicMock()
        mock_gv.module = fake_module
        mock_gv.out = io.StringIO()
        mock_gv.gx = gx

        em = extmod.ExtensionModule(gx, mock_gv)
        em.do_extmod_class(cl)
        return mock_gv.out.getvalue()

    def test_proxy_removed_before_tp_free(self, gx_with_builtin):
        """__ss_proxy->__delitem__ must run before tp_free, not after."""
        out = self._generate(gx_with_builtin)

        start = out.index("Dealloc(")
        body = out[start:out.index("}", start)]

        delitem_pos = body.index("__ss_proxy->__delitem__")
        tp_free_pos = body.index("tp_free")

        assert delitem_pos < tp_free_pos, (
            "self->__ss_object is read after tp_free has freed self "
            "(use-after-free)"
        )


class TestNumberMethodsTable:
    """Tests for the generated PyNumberMethods initializer.

    do_extmod_methoddef writes operator overloads into the struct
    positionally, so the order and per-slot casts have to match CPython's
    real field layout (add, subtract, multiply, remainder, divmod, power,
    negative, positive, absolute, bool, ...). Building and running an actual
    extension module confirmed these were misaligned: __mod__ ended up in
    the nb_divmod slot, __pow__ (a 3-arg function) in nb_negative (a 1-arg
    slot), and nb_bool held a PyObject*-returning function reinterpreted as
    an int-returning one, making bool(obj) true for essentially any object
    regardless of its actual truthiness.
    """

    def _make_func(self, gx, mv, cl, ident, extra_formals=()):
        args = ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg="self")] + [ast.arg(arg=n) for n in extra_formals],
            vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[],
        )
        node = ast.FunctionDef(
            name=ident, args=args, body=[ast.Pass()], decorator_list=[], returns=None,
        )
        func = python.Function(gx, mv, node, cl)
        func.defaults = []
        func.vars = {n: MagicMock() for n in extra_formals}
        cl.funcs[ident] = func
        return func

    def _generate(self, gx_with_builtin, idents_and_formals):
        gx = gx_with_builtin
        builtin_mv = gx.modules["builtin"].mv

        fake_module = python.Module(
            "test_mod", "/fake/test_mod.py", "test_mod.py",
            False, None, ast.parse(""),
        )
        fake_mv = MagicMock()
        fake_mv.module = fake_module
        fake_mv.classes = {}
        fake_module.mv = fake_mv

        node = ast.ClassDef(
            name="Foo", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, node, builtin_mv, fake_module)
        cl.def_order = 0
        cl.funcs = {}

        funcs = [
            self._make_func(gx, builtin_mv, cl, ident, formals)
            for ident, formals in idents_and_formals
        ]

        mock_gv = MagicMock()
        mock_gv.module = fake_module
        mock_gv.out = io.StringIO()
        mock_gv.gx = gx

        em = extmod.ExtensionModule(gx, mock_gv)
        em.do_extmod_methoddef("Foo", funcs, cl)
        return mock_gv.out.getvalue()

    def _struct_body(self, out):
        start = out.index("_as_number = {")
        end = out.index("};", start)
        body = out[start:end]
        # one struct entry per line, in written order
        return [
            line.strip().rstrip(",")
            for line in body.splitlines()[1:]
            if line.strip()
        ]

    def test_full_slot_order_and_targets(self, gx_with_builtin):
        """Every overload lands in the correct positional slot."""
        idents = [
            ("__add__", ["other"]),
            ("__mod__", ["other"]),
            ("__pow__", ["other"]),
            ("__neg__", []),
            ("__abs__", []),
            ("__bool__", []),
        ]
        out = self._generate(gx_with_builtin, idents)
        entries = self._struct_body(out)

        # add, sub(missing->0), mul(missing->0), mod, divmod(missing->0),
        # pow, neg, pos(missing->0), abs, bool
        assert len(entries) == 10
        assert "__ss_builtin_Foo___add__" in entries[0]
        assert entries[1] == "0"  # nb_subtract: not defined
        assert entries[2] == "0"  # nb_multiply: not defined
        assert "__ss_builtin_Foo___mod__" in entries[3]  # nb_remainder
        assert entries[4] == "0"  # nb_divmod: not defined
        assert "__ss_builtin_Foo___pow__" in entries[5]  # nb_power
        assert "__ss_builtin_Foo___neg__" in entries[6]  # nb_negative
        assert entries[7] == "0"  # nb_positive: not defined
        assert "__ss_builtin_Foo___abs__" in entries[8]  # nb_absolute
        assert "nb_bool" in entries[9]  # nb_bool: the wrapper, not the raw method

    def test_pow_uses_ternary_cast(self, gx_with_builtin):
        """nb_power needs a 3-arg cast to match the (self,args,kwargs) function."""
        out = self._generate(gx_with_builtin, [("__pow__", ["other"])])
        entries = self._struct_body(out)
        assert "PyObject *(*)(PyObject *, PyObject *, PyObject *)" in entries[5]

    def test_bool_gets_int_returning_wrapper(self, gx_with_builtin):
        """nb_bool must not be a raw cast of the PyObject*-returning method.

        Casting the (PyObject *)-returning __bool__ method straight into the
        `int (*)(PyObject *)` slot would hand CPython a pointer value where
        it expects 0/1/-1; bool(obj) would then be driven by pointer
        truncation instead of the actual boolean value.
        """
        out = self._generate(gx_with_builtin, [("__bool__", [])])
        assert "static int __ss_builtin_Foo___bool___nb_bool(PyObject *self) {" in out
        assert "PyObject_IsTrue" in out
        entries = self._struct_body(out)
        assert entries[9] == "__ss_builtin_Foo___bool___nb_bool"

    def test_bool_wrapper_precedes_struct(self, gx_with_builtin):
        """The wrapper must be defined before it's referenced in the struct."""
        out = self._generate(gx_with_builtin, [("__bool__", [])])
        wrapper_def = out.index("_nb_bool(PyObject *self) {")
        struct_start = out.index("_as_number = {")
        assert wrapper_def < struct_start


class TestVoidStarSetter:
    """Tests for generated setters on 'void *'-typed attributes.

    An attribute whose merged type is only ever None gets typed as
    'void *'. The setter for such an attribute used to unconditionally
    assign NULL, silently discarding whatever value the caller actually
    passed -- no error, no assignment, just quiet data loss. Confirmed by
    building and running an extension module: `obj.val = "oops"` used to
    succeed silently and leave `val` as None; now it raises TypeError, same
    as every other attribute type.
    """

    def _generate(self, gx_with_builtin):
        gx = gx_with_builtin
        builtin_mv = gx.modules["builtin"].mv

        fake_module = python.Module(
            "test_mod", "/fake/test_mod.py", "test_mod.py",
            False, None, ast.parse(""),
        )
        fake_mv = MagicMock()
        fake_mv.module = fake_module
        fake_mv.classes = {}
        fake_module.mv = fake_mv

        node = ast.ClassDef(
            name="Foo", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, node, builtin_mv, fake_module)
        cl.def_order = 0
        cl.funcs = {}

        # a variable whose merged type is only ever None -- this is exactly
        # what nodetypestr renders as "void *"
        var = python.Variable("val", cl)
        cl.vars = {"val": var}
        gx.merged_inh[var] = {(python.def_class(gx, "none"), 0)}
        cl.bases = []

        mock_gv = MagicMock()
        mock_gv.module = fake_module
        mock_gv.out = io.StringIO()
        mock_gv.gx = gx
        mock_gv.mergeinh = gx.merged_inh
        mock_gv.cpp_name = lambda x: x.name if hasattr(x, "name") else str(x)

        em = extmod.ExtensionModule(gx, mock_gv)
        em.do_extmod_class(cl)
        return mock_gv.out.getvalue()

    def test_setter_routes_through_to_ss_instead_of_hardcoding_null(
        self, gx_with_builtin
    ):
        """The generated setter must actually convert `value`, not discard it."""
        out = self._generate(gx_with_builtin)

        start = out.index("__ss_set_")
        body = out[start:out.index("}", start)]

        assert "__to_ss<void *>(value)" in body, (
            "setter should route the assignment through __to_ss<void *>, "
            "which validates the value (accepts None, raises TypeError "
            "otherwise) instead of silently discarding it"
        )
        assert "= NULL;" not in body, (
            "setter must not unconditionally overwrite the attribute with "
            "NULL regardless of what value was passed in"
        )
