from __future__ import print_function

"""
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

extmod.py: extension module support

"""
import logging

from . import infer
from . import python
from . import typestr

logger = logging.getLogger("extmod")
OVERLOAD_SINGLE = ["__neg__", "__pos__", "__abs__", "__nonzero__"]
OVERLOAD = ["__add__", "__sub__", "__mul__", "__div__", 
            "__mod__", "__divmod__", "__pow__"] + OVERLOAD_SINGLE


def clname(cl):
    """class name normalizer

    :param      cl:   class object
    :type       cl:   python.Class

    :returns:   class name with shedksin prefix and module qualifier
    :rtype:     str
    """
    return "__ss_%s_%s" % ("_".join(cl.mv.module.name_list), cl.ident)


class ExtensionModule:
    """
    This class describes an extension module generator
    """

    def __init__(self, gx, gv):
        self.gx = gx
        self.gv = gv

    def write(self, entry):
        """
        { function_description }

        :param      entry:    { parameter_description }
        :type       entry:    str
        """
        print(entry, file=self.gv.out)

    def do_init_mods(self, what):
        """
        Does initialize mods.

        :param      what:  The what
        :type       what:  { type_description }

        :returns:   { description_of_the_return_value }
        :rtype:     { return_type_description }
        """
        for module in self.gx.modules.values():
            if not module.builtin and not module is self.gv.module:
                self.write(
                    "    %s::%s%s();"
                    % (module.full_path(), what, "_".join(module.name_list))
                )

    def supported_vars(self, variables):  # XXX virtuals?
        """XXX currently only classs / instance variables
        """
        supported = []
        for var in variables:
            if not var in self.gx.merged_inh or not self.gx.merged_inh[var]:
                continue
            if var.name is None or var.name.startswith("__"):  # XXX
                continue
            if var.invisible or typestr.singletype2(self.gx.merged_inh[var], python.Module):
                continue
            try:
                typestr.nodetypestr(self.gx, var, var.parent, check_extmod=True, mv=self.gv.mv)
            except typestr.ExtmodError:
                if isinstance(var.parent, python.Class):
                    logger.warning(
                        "'%s.%s' variable not exported (cannot convert)",
                        var.parent.ident,
                        var.name,
                    )
                else:
                    logger.warning(
                        "'%s' variable not exported (cannot convert)", var.name
                    )
                continue
            supported.append(var)
        return supported

    def supported_funcs(self, funcs):
        """
        { function_description }

        :param      funcs:  The funcs
        :type       funcs:  { type_description }

        :returns:   { description_of_the_return_value }
        :rtype:     { return_type_description }
        """
        supported = []
        for func in funcs:
            if func.isGenerator or not infer.called(func):
                continue
            if func.ident in [
                "__setattr__",
                "__getattr__",
                "__iadd__",
                "__isub__",
                "__imul__",
            ]:  # XXX
                continue
            if isinstance(func.parent, python.Class):
                if func.invisible or func.inherited or not self.gv.inhcpa(func):
                    continue
            if (
                isinstance(func.parent, python.Class)
                and func.ident in func.parent.staticmethods
            ):
                logger.warning(
                    "'%s.%s' method not exported (staticmethod)",
                    func.parent.ident,
                    func.ident,
                )
                continue
            builtins = True
            reason = ''
            for formal in func.formals:
                try:
                    typestr.nodetypestr(
                        self.gx, func.vars[formal], func, check_extmod=True, mv=self.gv.mv
                    )
                except typestr.ExtmodError:
                    builtins = False
                    reason = "cannot convert argument '%s'" % formal
            try:
                typestr.nodetypestr(
                    self.gx,
                    func.retnode.thing,
                    func,
                    check_extmod=True,
                    check_ret=True,
                    mv=self.gv.mv,
                )
            except typestr.ExtmodError:
                builtins = False
                reason = "cannot convert return value"
            if builtins:
                supported.append(func)
            else:
                if isinstance(func.parent, python.Class):
                    logger.warning(
                        "'%s.%s' method not exported (%s)",
                        func.parent.ident,
                        func.ident,
                        reason,
                    )
                else:
                    logger.warning(
                        "'%s' function not exported (%s)", func.ident, reason
                    )
        return supported

    def has_method(self, cl, name):  # XXX shared.py
        """
        Determines if method.

        :param      cl:    { parameter_description }
        :type       cl:    { type_description }
        :param      name:  The name
        :type       name:  { type_description }

        :returns:   True if method, False otherwise.
        :rtype:     bool
        """
        return (
            name in cl.funcs
            and not cl.funcs[name].invisible
            and not cl.funcs[name].inherited
            and infer.called(cl.funcs[name])
        )

    def do_add_globals(self, classes, __ss_mod):
        """
        Does add globals.

        :param      classes:   The classes
        :type       classes:   { type_description }
        :param      __ss_mod:  The ss modifier
        :type       __ss_mod:  { type_description }

        :returns:   { description_of_the_return_value }
        :rtype:     { return_type_description }
        """

        # global variables
        for var in self.supported_vars(self.gv.mv.globals.values()):
            if [
                1
                for t in self.gv.mergeinh[var]
                if t[0].ident in ["int_", "float_", "bool_"]
            ]:
                self.write(
                    '    PyModule_AddObject(%(ssmod)s, (char *)"%(name)s", __to_py(%(var)s));'
                    % {
                        "name": var.name,
                        "var": "__"
                        + self.gv.module.ident
                        + "__::"
                        + self.gv.cpp_name(var),
                        "ssmod": __ss_mod,
                    }
                )
            else:
                self.write(
                    '    PyModule_AddObject(%(ssmod)s, (char *)"%(name)s", __to_py(%(var)s));'
                    % {
                        "name": var.name,
                        "var": "__"
                        + self.gv.module.ident
                        + "__::"
                        + self.gv.cpp_name(var),
                        "ssmod": __ss_mod,
                    }
                )

    def do_reduce_setstate(self, cl, vars):
        """
        Does a reduce setstate.

        :param      cl:    { parameter_description }
        :type       cl:    { type_description }
        :param      vars:  The variables
        :type       vars:  { type_description }

        :returns:   { description_of_the_return_value }
        :rtype:     { return_type_description }
        """
        write = self.write
        if python.def_class(self.gx, "Exception") in cl.ancestors():  # XXX
            return
        write(
            "PyObject *%s__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {"
            % clname(cl)
        )
        write("    PyObject *t = PyTuple_New(3);")
        write(
            '    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_%s, "__newobj__"));'
            % "_".join(self.gv.module.name_list)
        )
        write("    PyObject *a = PyTuple_New(1);")
        write("    Py_INCREF((PyObject *)&%sObjectType);" % clname(cl))
        write("    PyTuple_SetItem(a, 0, (PyObject *)&%sObjectType);" % clname(cl))
        write("    PyTuple_SetItem(t, 1, a);")
        write("    PyObject *b = PyTuple_New(%d);" % len(vars))
        for i, var in enumerate(vars):
            write(
                "    PyTuple_SetItem(b, %d, __to_py(((%sObject *)self)->__ss_object->%s));"
                % (i, clname(cl), self.gv.cpp_name(var))
            )
        write("    PyTuple_SetItem(t, 2, b);")
        write("    return t;")
        write("}\n")
        write(
            "PyObject *%s__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {"
            % clname(cl)
        )
        write("    int l = PyTuple_Size(args);")
        write("    PyObject *state = PyTuple_GetItem(args, 0);")
        for i, var in enumerate(vars):
            vartype = typestr.nodetypestr(self.gx, var, var.parent, mv=self.gv.mv)
            write(
                "    ((%sObject *)self)->__ss_object->%s = __to_ss<%s>(PyTuple_GetItem(state, %d));"
                % (clname(cl), self.gv.cpp_name(var), vartype, i)
            )
        write("    Py_INCREF(Py_None);")
        write("    return Py_None;")
        write("}\n")


    def convert_methods(self, cl, declare):
        """
        { function_description }

        :param      cl:       { parameter_description }
        :type       cl:       { type_description }
        :param      declare:  The declare
        :type       declare:  { type_description }

        :returns:   { description_of_the_return_value }
        :rtype:     { return_type_description }
        """
        write = self.write
        if python.def_class(self.gx, "Exception") in cl.ancestors():
            return
        if declare:
            write("    virtual PyObject *__to_py__();")
        else:
            for n in cl.module.name_list:
                write("namespace __%s__ { /* XXX */" % n)
            write("")

            write("PyObject *%s::__to_py__() {" % self.gv.cpp_name(cl))
            write("    PyObject *p;")
            write("    if(__ss_proxy->has_key(this))")
            write("        p = (PyObject *)(__ss_proxy->__getitem__(this));")
            write("    else {")
            write(
                "        %sObject *self = (%sObject *)(%sObjectType.tp_alloc(&%sObjectType, 0));"
                % (4 * (clname(cl),))
            )
            write("        self->__ss_object = this;")
            write("        __ss_proxy->__setitem__(self->__ss_object, self);")
            write("        p = (PyObject *)self;")
            write("    }")
            write("    Py_INCREF(p);")
            write("    return p;")
            write("}\n")

            for n in cl.module.name_list:
                write("} // module namespace")
            write("")

            write("namespace __shedskin__ { /* XXX */\n")

            write(
                "template<> %s::%s *__to_ss(PyObject *p) {"
                % (cl.module.full_path(), self.gv.cpp_name(cl))
            )
            write("    if(p == Py_None) return NULL;")
            write(
                "    if(PyObject_IsInstance(p, (PyObject *)&%s::%sObjectType)!=1)"
                % (cl.module.full_path(), clname(cl))
            )
            write(
                '        throw new TypeError(new str("error in conversion to Shed Skin (%s expected)"));'
                % cl.ident
            )
            write(
                "    return ((%s::%sObject *)p)->__ss_object;"
                % (cl.module.full_path(), clname(cl))
            )
            write("}\n}")

    def do_extmod_methoddef(self, ident, funcs, cl):
        """
        Does an extmod methoddef.

        :param      ident:  The identifier
        :type       ident:  { type_description }
        :param      funcs:  The funcs
        :type       funcs:  { type_description }
        :param      cl:     { parameter_description }
        :type       cl:     { type_description }

        :returns:   { description_of_the_return_value }
        :rtype:     { return_type_description }
        """
        write = self.write
        if cl:
            ident = clname(cl)
        write("static PyNumberMethods %s_as_number = {" % ident)
        for overload in OVERLOAD:
            fs = [f for f in funcs if f.ident == overload]
            if fs:
                f = fs[0]
                if overload == "__abs__":  # XXX
                    write(
                        "    (int (*)(PyObject *))%s_%s," % (clname(f.parent), overload)
                    )
                elif overload in OVERLOAD_SINGLE:
                    write(
                        "    (PyObject *(*)(PyObject *))%s_%s,"
                        % (clname(f.parent), overload)
                    )
                else:
                    write("    (PyCFunction)%s_%s," % (clname(f.parent), overload))
            else:
                write("    0,")
        write("};\n")
        if cl and not python.def_class(self.gx, "Exception") in cl.ancestors():
            write(
                "PyObject *%s__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);"
                % ident
            )
            write(
                "PyObject *%s__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);\n"
                % ident
            )
        write("static PyMethodDef %sMethods[] = {" % ident)
        if not cl:
            write(
                '    {(char *)"__newobj__", (PyCFunction)__ss__newobj__, METH_VARARGS | METH_KEYWORDS, (char *)""},'
            )
        elif cl and not python.def_class(self.gx, "Exception") in cl.ancestors():
            write(
                '    {(char *)"__reduce__", (PyCFunction)%s__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},'
                % ident
            )
            write(
                '    {(char *)"__setstate__", (PyCFunction)%s__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},'
                % ident
            )
        for func in funcs:
            if isinstance(func.parent, python.Class):
                id = clname(func.parent) + "_" + func.ident
            else:
                id = "Global_" + "_".join(self.gv.module.name_list) + "_" + func.ident
            write(
                '    {(char *)"%(id)s", (PyCFunction)%(id2)s, METH_VARARGS | METH_KEYWORDS, (char *)""},'
                % {"id": func.ident, "id2": id}
            )
        # write("    {NULL}\n};\n")
        write("    {NULL, NULL, 0, NULL}\n};\n")


    def do_extmod_method(self, func):
        """
        Does an extmod method.

        :param      func:  The function
        :type       func:  { type_description }

        :returns:   { description_of_the_return_value }
        :rtype:     { return_type_description }
        """
        write = self.write
        is_method = isinstance(func.parent, python.Class)
        if is_method:
            formals = func.formals[1:]
        else:
            formals = func.formals

        if isinstance(func.parent, python.Class):
            id = clname(func.parent) + "_" + func.ident
        else:
            id = "Global_" + "_".join(self.gv.module.name_list) + "_" + func.ident
        write("PyObject *%s(PyObject *self, PyObject *args, PyObject *kwargs) {" % id)
        write("    try {")

        for i, formal in enumerate(formals):
            self.gv.start("")
            typ = typestr.nodetypestr(self.gx, func.vars[formal], func, mv=self.gv.mv)
            if func.ident in OVERLOAD:
                write(
                    "        %(type)sarg_%(num)d = __to_ss<%(type)s>(args);"
                    % {"type": typ, "num": i}
                )
                continue
            self.gv.append(
                '        %(type)sarg_%(num)d = __ss_arg<%(type)s>("%(name)s", %(num)d, '
                % {"type": typ, "num": i, "name": formal}
            )
            if i >= len(formals) - len(func.defaults):
                self.gv.append("1, ")
                defau = func.defaults[i - (len(formals) - len(func.defaults))]
                if defau in func.mv.defaults:
                    if self.gv.mergeinh[defau] == set([(python.def_class(self.gx, "none"), 0)]):
                        self.gv.append("0")
                    else:
                        self.gv.append(
                            "%s::default_%d"
                            % (
                                "__" + func.mv.module.ident + "__",
                                func.mv.defaults[defau][0],
                            )
                        )
                else:
                    self.gv.visit(defau, func)
            elif typ.strip() == "__ss_bool":
                self.gv.append("0, False")
            else:
                self.gv.append("0, 0")
            self.gv.append(", args, kwargs)")
            self.gv.eol()
        write("")

        # call
        if is_method:
            where = "((%sObject *)self)->__ss_object->" % clname(func.parent)
        else:
            where = "__" + self.gv.module.ident + "__::"
        write(
            "        return __to_py("
            + where
            + self.gv.cpp_name(func.ident)
            + "("
            + ", ".join("arg_%d" % i for i in range(len(formals)))
            + "));\n"
        )

        # convert exceptions
        write("    } catch (Exception *e) {")
        write(
            '        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));'
        )
        write("        return 0;")
        write("    }")
        write("}\n")

    def do_extmod(self):
        """Generate an python c-api extension module
        """
        write = self.write
        write("/* extension module glue */\n")
        write('extern "C" {')
        write("#include <Python.h>")
        write("#include <structmember.h>\n")

        write("PyObject *__ss_mod_%s;\n" % "_".join(self.gv.module.name_list))

        # classes
        classes = self.exported_classes(warns=True)
        for cl in classes:
            self.do_extmod_class(cl)

        for n in self.gv.module.name_list:
            write("namespace __%s__ { /* XXX */" % n)

        # global functions
        funcs = self.supported_funcs(self.gv.module.mv.funcs.values())
        for func in funcs:
            self.do_extmod_method(func)
        self.do_extmod_methoddef(
            "Global_" + "_".join(self.gv.module.name_list), funcs, None
        )

        # module init function
        # write("PyMODINIT_FUNC init%s(void) {" % "_".join(self.gv.module.name_list))

        # # initialize modules
        # __ss_mod = "__ss_mod_%s" % "_".join(self.gv.module.name_list)
        # if self.gv.module == self.gx.main_module:
        #     self.gv.do_init_modules()
        #     write("    __" + self.gv.module.ident + "__::__init();")
        # write(
        #     '\n    %s = Py_InitModule((char *)"%s", Global_%sMethods);'
        #     % (__ss_mod, self.gv.module.ident, "_".join(self.gv.module.name_list))
        # )
        # write("    if(!%s)" % __ss_mod)
        # write("        return;\n")

        # module init function
        # write("static struct PyModuleDef %smodule = {" % "_".join(self.gv.module.name_list))
        # write("    PyModuleDef_HEAD_INIT,")
        # write('    "%s",   /* name of module */' % "_".join(self.gv.module.name_list))
        # write("    NULL,   /* module documentation, may be NULL */") # FIXME
        # write("    -1,     /* size of per-interpreter state of the module or -1 if the module keeps state in global variables. */")
        # write("    %s" % "Global_" + "_".join(self.gv.module.name_list) + "Methods")
        # write("};")

        write("static struct PyModuleDef Module_%s = {" % "_".join(self.gv.module.name_list))
        write("    PyModuleDef_HEAD_INIT,")
        write('    .m_name = "%s",   /* name of module */' % "_".join(self.gv.module.name_list))
        write('    .m_doc = "module docstring",   /* module documentation, may be NULL */') # FIXME
        write("    .m_size = -1,     /* size of per-interpreter state of the module or -1 if the module keeps state in global variables. */")
        write("    .m_methods = %sMethods," % ("Global_" + "_".join(self.gv.module.name_list)))
        write("};")

        # # add types to module
        # for cl in classes:
        #     write("    if (PyType_Ready(&%sObjectType) < 0)" % clname(cl))
        #     write("        return;\n")
        #     write(
        #         '    PyModule_AddObject(%s, "%s", (PyObject *)&%sObjectType);'
        #         % (__ss_mod, cl.ident, clname(cl))
        #     )
        # write("")

        # if self.gv.module == self.gx.main_module:
        #     self.do_init_mods("init")
        #     self.do_init_mods("add")
        #     write("    add%s();" % self.gv.module.ident)
        # write("\n}\n")

        # write("PyMODINIT_FUNC add%s(void) {" % "_".join(self.gv.module.name_list))
        # self.do_add_globals(classes, __ss_mod)
        # write("\n}")

        write("")
        write("PyMODINIT_FUNC PyInit_%s(void) {\n" % "_".join(self.gv.module.name_list))
        if self.gv.module == self.gx.main_module:
            self.gv.do_init_modules(extmod=True)
            write("    __" + self.gv.module.ident + "__::__init();")

        write("")
        write("    PyObject *m;\n")

        for cl in classes:
            write("    if (PyType_Ready(&%sObjectType) < 0)" % clname(cl))
            write("        return NULL;\n")

        write("    // create extension module")
        __ss_mod = "_".join(self.gv.module.name_list)
        write("    __ss_mod_%s = m = PyModule_Create(&Module_%s);" % (__ss_mod, __ss_mod))
        write("    if (m == NULL)")
        write("        return NULL;\n")

        write("    // add global variables")
        self.do_add_globals(classes, 'm')
        write("")

        write("    // add type objects")
        for cl in classes:
            write("    Py_INCREF(&%sObjectType);" % clname(cl))
            write('    if (PyModule_AddObject(m, "%s", (PyObject *) &%sObjectType) < 0) {' % (cl.ident, clname(cl)))
            write("        Py_DECREF(&%sObjectType);" % clname(cl))
            write("        Py_DECREF(m);")
            write("        return NULL;")
            write("    }\n")
        write("    return m;")
        write("}\n")

        for n in self.gv.module.name_list:
            write("\n} // namespace __%s__" % n)
        write('\n} // extern "C"')

        # conversion methods to/from CPython/Shedskin
        for cl in classes:
            self.convert_methods(cl, False)

    def do_extmod_class(self, cl):
        """Generates a python c-api extension type.

        :param      cl:   class object
        :type       cl:   python.Class
        """
        write = self.write
        for n in cl.module.name_list:
            write("namespace __%s__ { /* XXX */" % n)
        write("")

        # determine methods, vars to expose
        funcs = self.supported_funcs(cl.funcs.values())
        vars = self.supported_vars(cl.vars.values())

        # python object
        write("/* class %s */\n" % cl.ident)
        write("typedef struct {")
        write("    PyObject_HEAD")
        write("    %s::%s *__ss_object;" % (
            cl.module.full_path(), self.gv.cpp_name(cl)))
        write("} %sObject;\n" % clname(cl))

        ## FIXME: temporarly hardcoded
        ## this should include type struct members
        ## https://docs.python.org/3/c-api/structures.html
        write("static PyMemberDef %sMembers[] = {" % clname(cl))
        write("    {NULL}\n};\n")

        # methods
        for func in funcs:
            self.do_extmod_method(func)
        self.do_extmod_methoddef(cl.ident, funcs, cl)

        # tp_init
        if self.has_method(cl, "__init__") and cl.funcs["__init__"] in funcs:
            write(
                "int %s___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {"
                % clname(cl)
            )
            write("    if(!%s___init__(self, args, kwargs))" % clname(cl))
            write("        return -1;")
            write("    return 0;")
            write("}\n")

        # tp_new
        write(
            "PyObject *%sNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {"
            % clname(cl)
        )
        write(
            "    %sObject *self = (%sObject *)type->tp_alloc(type, 0);"
            % (clname(cl), clname(cl))
        )
        write(
            "    self->__ss_object = new %s::%s();"
            % (cl.module.full_path(), self.gv.cpp_name(cl))
        )
        write(
            "    self->__ss_object->__class__ = %s::cl_%s;"
            % (cl.module.full_path(), cl.ident)
        )
        write("    __ss_proxy->__setitem__(self->__ss_object, self);")
        write("    return (PyObject *)self;")
        write("}\n")

        # tp_dealloc
        write("void %sDealloc(%sObject *self) {" % (clname(cl), clname(cl)))
        write("    Py_TYPE(self)->tp_free((PyObject *)self);")        
        write("    __ss_proxy->__delitem__(self->__ss_object);")
        write("}\n")

        # getset
        for var in vars:
            write(
                "PyObject *__ss_get_%s_%s(%sObject *self, void *closure) {"
                % (clname(cl), var.name, clname(cl))
            )
            write("    return __to_py(self->__ss_object->%s);" % self.gv.cpp_name(var))
            write("}\n")

            write(
                "int __ss_set_%s_%s(%sObject *self, PyObject *value, void *closure) {"
                % (clname(cl), var.name, clname(cl))
            )
            write("    try {")
            typ = typestr.nodetypestr(self.gx, var, var.parent, mv=self.gv.mv)
            if typ == "void *":  # XXX investigate
                write("        self->__ss_object->%s = NULL;" % self.gv.cpp_name(var))
            else:
                write(
                    "        self->__ss_object->%s = __to_ss<%s>(value);"
                    % (self.gv.cpp_name(var), typ)
                )
            write("    } catch (Exception *e) {")
            write(
                '        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));'
            )
            write("        return -1;")
            write("    }")

            write("    return 0;")
            write("}\n")

        write("PyGetSetDef %sGetSet[] = {" % clname(cl))
        for var in vars:
            write(
                '    {(char *)"%s", (getter)__ss_get_%s_%s, (setter)__ss_set_%s_%s, (char *)"", NULL},'
                % (var.name, clname(cl), var.name, clname(cl), var.name)
            )
        write("    {NULL}\n};\n")

        # python type (new)
        write('PyTypeObject %sObjectType = {' % clname(cl))
        write('    PyVarObject_HEAD_INIT(NULL, 0)')
        write('    .tp_name = "%s.%s",' % (cl.module.ident, cl.ident))
        write('    .tp_basicsize = sizeof( %sObject),' % clname(cl))
        write('    .tp_itemsize = 0,')
        write('    .tp_dealloc = (destructor) %sDealloc,' % clname(cl))
        if self.has_method(cl, "__repr__"):
            write('    .tp_repr = (PyObject *(*)(PyObject *))%s___repr__, ' % clname(cl))
        else:
            write('    .tp_repr = 0,')
        write('    .tp_as_number = &%s_as_number,' % clname(cl))
        if self.has_method(cl, "__str__"):
            write('    .tp_str = (PyObject *(*)(PyObject *))%s___str__, ' % clname(cl))
        else:
            write('    .tp_str = 0,')
        write('    .tp_flags = Py_TPFLAGS_DEFAULT,')
        write('    .tp_doc = PyDoc_STR("Custom objects"),') # XXX needs class docstring
        write('    .tp_methods = %sMethods,' % clname(cl))
        write('    .tp_members = %sMembers,' % clname(cl))
        write('    .tp_getset = %sGetSet,' % clname(cl))

        if cl.bases and not cl.bases[0].mv.module.builtin:
            write('    .tp_base = &%sObjectType,' % clname(cl.bases[0]))
        else:
            write('    .tp_base = 0, ')

        if self.has_method(cl, "__init__") and cl.funcs["__init__"] in funcs:
            write('    .tp_init = (initproc) %s___tpinit__,' % clname(cl))
        else:
            write('    .tp_init = 0,')
        write('    .tp_new = %sNew,' % clname(cl))
        write('};\n')

        self.do_reduce_setstate(cl, vars)
        for n in cl.module.name_list:
            write("} // namespace __%s__" % n)
        write("")

    def pyinit_func(self):
        """
        { function_description }
        """
        self.write("PyMODINIT_FUNC PyInit_%s(void);\n" % "_".join(self.gv.module.name_list))
        # for what in ("init", "add"):
        #     self.write(
        #         "PyMODINIT_FUNC %s%s(void);\n" % (what, "_".join(self.gv.module.name_list))
        #     )

    def exported_classes(self, warns=False):
        """
        { function_description }

        :param      warns:  The warns
        :type       warns:  bool
        """
        classes = []
        for cl in self.gv.module.mv.classes.values():
            if python.def_class(self.gx, "Exception") in cl.ancestors():
                if warns:
                    logger.warning(
                        "'%s' class not exported (inherits from Exception)", cl.ident
                    )
            else:
                classes.append(cl)
        return sorted(classes, key=lambda x: x.def_order)

    def convert_methods2(self):
        """
        { function_description }
        """
        write = lambda s: print(s, file=self.gv.out)

        for cl in self.exported_classes():
            write('extern "C" PyTypeObject %sObjectType;' % clname(cl))

        write("namespace __shedskin__ { /* XXX */\n")
        for cl in self.exported_classes():
            write(
                "template<> %s::%s *__to_ss(PyObject *p);"
                % (cl.module.full_path(), self.gv.cpp_name(cl))
            )
        write("}")
