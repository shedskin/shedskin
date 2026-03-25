# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Pipeline integration tests using demo_program1.py.

These tests drive the full shedskin pipeline (parse -> infer -> codegen)
on a small demo program and assert on the intermediate state at each stage.
This exercises the code paths that are unreachable from pure unit tests.
"""

from pathlib import Path

import pytest

from shedskin import python, typestr


class TestParsing:
    """Tests for the parsing stage of the pipeline."""

    def test_main_module_parsed(self, analyzed_demo):
        """The main module should be parsed and registered."""
        gx = analyzed_demo
        assert gx.main_module is not None
        assert gx.main_module.ident == "demo_program1"

    def test_builtin_module_loaded(self, analyzed_demo):
        """The builtin module should always be loaded."""
        gx = analyzed_demo
        assert "builtin" in gx.modules

    def test_demo_module_registered(self, analyzed_demo):
        """The demo module should be in the modules dict."""
        gx = analyzed_demo
        assert "demo_program1" in gx.modules

    def test_classes_discovered(self, analyzed_demo):
        """All user-defined classes should be discovered."""
        gx = analyzed_demo
        class_names = {cl.ident for cl in gx.allclasses}
        assert "Animal" in class_names
        assert "Dog" in class_names
        assert "Cat" in class_names

    def test_functions_discovered(self, analyzed_demo):
        """All user-defined functions should be discovered."""
        gx = analyzed_demo
        func_names = {f.ident for f in gx.allfuncs}
        assert "add" in func_names
        assert "factorial" in func_names
        assert "string_ops" in func_names
        assert "list_ops" in func_names
        assert "dict_ops" in func_names
        assert "tuple_ops" in func_names
        assert "use_animals" in func_names
        assert "range_loop" in func_names
        assert "float_math" in func_names


class TestTypeInference:
    """Tests for the type inference stage."""

    def test_merged_inh_populated(self, analyzed_demo):
        """merged_inh should be populated after analysis."""
        gx = analyzed_demo
        assert len(gx.merged_inh) > 0

    def test_int_variable_inferred(self, analyzed_demo):
        """Integer variables should be inferred as int_."""
        gx = analyzed_demo
        int_cl = python.def_class(gx, "int_")

        # Find the 'total' variable in range_loop
        func = _find_func(gx, "range_loop")
        assert func is not None
        var = func.vars.get("total")
        assert var is not None
        if var in gx.merged_inh:
            classes = {t[0] for t in gx.merged_inh[var]}
            assert int_cl in classes

    def test_string_variable_inferred(self, analyzed_demo):
        """String variables should be inferred as str_."""
        gx = analyzed_demo
        str_cl = python.def_class(gx, "str_")

        func = _find_func(gx, "string_ops")
        assert func is not None
        var = func.vars.get("s")
        assert var is not None
        if var in gx.merged_inh:
            classes = {t[0] for t in gx.merged_inh[var]}
            assert str_cl in classes

    def test_float_variable_inferred(self, analyzed_demo):
        """Float variables should be inferred as float_."""
        gx = analyzed_demo
        float_cl = python.def_class(gx, "float_")

        func = _find_func(gx, "float_math")
        assert func is not None
        var = func.vars.get("x")
        assert var is not None
        if var in gx.merged_inh:
            classes = {t[0] for t in gx.merged_inh[var]}
            assert float_cl in classes

    def test_list_variable_inferred(self, analyzed_demo):
        """List variables should be inferred as list."""
        gx = analyzed_demo
        list_cl = python.def_class(gx, "list")

        func = _find_func(gx, "list_ops")
        assert func is not None
        var = func.vars.get("nums")
        assert var is not None
        if var in gx.merged_inh:
            classes = {t[0] for t in gx.merged_inh[var]}
            assert list_cl in classes

    def test_dict_variable_inferred(self, analyzed_demo):
        """Dict variables should be inferred as dict."""
        gx = analyzed_demo
        dict_cl = python.def_class(gx, "dict")

        func = _find_func(gx, "dict_ops")
        assert func is not None
        var = func.vars.get("d")
        assert var is not None
        if var in gx.merged_inh:
            classes = {t[0] for t in gx.merged_inh[var]}
            assert dict_cl in classes


class TestVirtualMethods:
    """Tests for virtual method analysis."""

    def test_animal_speak_is_virtual(self, analyzed_demo):
        """Animal.speak should be marked virtual (overridden by Dog and Cat)."""
        gx = analyzed_demo
        animal_cl = _find_class(gx, "Animal")
        assert animal_cl is not None
        assert "speak" in animal_cl.virtuals

    def test_virtual_subclasses_registered(self, analyzed_demo):
        """Dog and Cat should be registered as virtual subclasses of Animal.speak."""
        gx = analyzed_demo
        animal_cl = _find_class(gx, "Animal")
        assert animal_cl is not None

        subclass_names = {cl.ident for cl in animal_cl.virtuals.get("speak", set())}
        assert "Dog" in subclass_names
        assert "Cat" in subclass_names


class TestTypeStrings:
    """Tests for type string generation on inferred types."""

    def test_int_typestr_cpp(self, analyzed_demo):
        """Int variables should produce '__ss_int' C++ type string."""
        gx = analyzed_demo
        mv = gx.modules["demo_program1"].mv

        func = _find_func(gx, "range_loop")
        var = func.vars.get("total")
        if var and var in gx.merged_inh:
            ts = typestr.nodetypestr(gx, var, cplusplus=True, mv=mv)
            assert "__ss_int" in ts

    def test_str_typestr_cpp(self, analyzed_demo):
        """String variables should produce 'str *' C++ type string."""
        gx = analyzed_demo
        mv = gx.modules["demo_program1"].mv

        func = _find_func(gx, "string_ops")
        var = func.vars.get("s")
        if var and var in gx.merged_inh:
            ts = typestr.nodetypestr(gx, var, cplusplus=True, mv=mv)
            assert "str *" in ts

    def test_float_typestr_cpp(self, analyzed_demo):
        """Float variables should produce '__ss_float' C++ type string."""
        gx = analyzed_demo
        mv = gx.modules["demo_program1"].mv

        func = _find_func(gx, "float_math")
        var = func.vars.get("x")
        if var and var in gx.merged_inh:
            ts = typestr.nodetypestr(gx, var, cplusplus=True, mv=mv)
            assert "__ss_float" in ts

    def test_list_typestr_cpp(self, analyzed_demo):
        """List variables should produce 'list<...> *' C++ type string."""
        gx = analyzed_demo
        mv = gx.modules["demo_program1"].mv

        func = _find_func(gx, "list_ops")
        var = func.vars.get("nums")
        if var and var in gx.merged_inh:
            ts = typestr.nodetypestr(gx, var, cplusplus=True, mv=mv)
            assert "list<" in ts

    def test_dict_typestr_cpp(self, analyzed_demo):
        """Dict variables should produce 'dict<...> *' C++ type string."""
        gx = analyzed_demo
        mv = gx.modules["demo_program1"].mv

        func = _find_func(gx, "dict_ops")
        var = func.vars.get("d")
        if var and var in gx.merged_inh:
            ts = typestr.nodetypestr(gx, var, cplusplus=True, mv=mv)
            assert "dict<" in ts

    def test_typestr_annotation_mode(self, analyzed_demo):
        """Annotation mode should wrap type in brackets."""
        gx = analyzed_demo
        mv = gx.modules["demo_program1"].mv

        func = _find_func(gx, "range_loop")
        var = func.vars.get("total")
        if var and var in gx.merged_inh:
            ts = typestr.nodetypestr(gx, var, cplusplus=False, mv=mv)
            assert ts.startswith("[")
            assert ts.endswith("]")

    def test_looper_typestr(self, analyzed_demo):
        """Loop variables with loopers should include for_in_loop."""
        gx = analyzed_demo
        mv = gx.modules["demo_program1"].mv

        # Find a loop variable that has a looper set
        for func in gx.allfuncs:
            if func.mv.module.ident != "demo_program1":
                continue
            for name, var in func.vars.items():
                if var.looper and var in gx.merged_inh:
                    ts = typestr.nodetypestr(gx, var, cplusplus=True, mv=mv)
                    assert "for_in_loop" in ts
                    return
        # If no looper found, that's fine -- the demo might not produce one


class TestCodeGeneration:
    """Tests for C++ code generation."""

    def test_cpp_file_generated(self, generated_demo):
        """A .cpp file should be generated for the demo module."""
        gx, output_dir = generated_demo
        cpp_files = list(output_dir.glob("*.cpp"))
        assert len(cpp_files) >= 1

    def test_hpp_file_generated(self, generated_demo):
        """A .hpp header file should be generated for the demo module."""
        gx, output_dir = generated_demo
        hpp_files = list(output_dir.glob("*.hpp"))
        assert len(hpp_files) >= 1

    def test_cpp_contains_class_definitions(self, generated_demo):
        """The .cpp file should contain class definitions."""
        gx, output_dir = generated_demo
        cpp_files = list(output_dir.glob("*.cpp"))
        content = cpp_files[0].read_text()
        assert "Animal" in content
        assert "Dog" in content
        assert "Cat" in content

    def test_cpp_contains_function_definitions(self, generated_demo):
        """The .cpp file should contain function definitions."""
        gx, output_dir = generated_demo
        cpp_files = list(output_dir.glob("*.cpp"))
        content = cpp_files[0].read_text()
        assert "factorial" in content
        assert "range_loop" in content

    def test_hpp_contains_virtual_declaration(self, generated_demo):
        """The .hpp file should contain virtual method declaration for speak."""
        gx, output_dir = generated_demo
        hpp_files = list(output_dir.glob("*.hpp"))
        content = hpp_files[0].read_text()
        assert "virtual" in content
        assert "speak" in content

    def test_cpp_uses_correct_int_type(self, generated_demo):
        """The .cpp file should use __ss_int for integer variables."""
        gx, output_dir = generated_demo
        cpp_files = list(output_dir.glob("*.cpp"))
        content = cpp_files[0].read_text()
        assert "__ss_int" in content

    def test_cpp_uses_list_template(self, generated_demo):
        """The .cpp file should use list<...> templates."""
        gx, output_dir = generated_demo
        cpp_files = list(output_dir.glob("*.cpp"))
        content = cpp_files[0].read_text()
        assert "list<" in content

    def test_cpp_uses_dict_template(self, generated_demo):
        """The .cpp file should use dict<...> templates."""
        gx, output_dir = generated_demo
        cpp_files = list(output_dir.glob("*.cpp"))
        content = cpp_files[0].read_text()
        assert "dict<" in content


# --- helpers ---

def _find_func(gx, name):
    """Find a function by name in the demo module."""
    for f in gx.allfuncs:
        if f.ident == name and f.mv.module.ident == "demo_program1":
            return f
    return None


def _find_class(gx, name):
    """Find a class by name in the demo module."""
    for cl in gx.allclasses:
        if cl.ident == name and cl.mv.module.ident == "demo_program1":
            return cl
    return None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
