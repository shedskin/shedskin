from __future__ import print_function

'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

extmod.py: extension module support

'''
import logging

from .infer import called
from .python import Class, def_class, Module
from .typestr import ExtmodError, nodetypestr, singletype2


logger = logging.getLogger('extmod')
OVERLOAD_SINGLE = ['__neg__', '__pos__', '__abs__', '__nonzero__']
OVERLOAD = ['__add__', '__sub__', '__mul__', '__div__', '__mod__', '__divmod__', '__pow__'] + OVERLOAD_SINGLE


def do_init_mods(gx, gv, what):
    for module in gx.modules.values():
        if not module.builtin and not module is gv.module:
            print('    %s::%s%s();' % (module.full_path(), what, '_'.join(module.name_list)), file=gv.out)


def clname(cl):
    return '__ss_%s_%s' % ('_'.join(cl.mv.module.name_list), cl.ident)


def supported_vars(gx, gv, vars):  # XXX virtuals?
    supported = []
    for var in vars:
        if not var in gx.merged_inh or not gx.merged_inh[var]:
            continue
        if var.name.startswith('__'):  # XXX
            continue
        if var.invisible or singletype2(gx.merged_inh[var], Module):
            continue
        try:
            nodetypestr(gx, var, var.parent, check_extmod=True, mv=gv.mv)
        except ExtmodError:
            if isinstance(var.parent, Class):
                logger.warning("'%s.%s' variable not exported (cannot convert)", var.parent.ident, var.name)
            else:
                logger.warning("'%s' variable not exported (cannot convert)", var.name)
            continue
        supported.append(var)
    return supported


def supported_funcs(gx, gv, funcs):
    supported = []
    for func in funcs:
        if func.isGenerator or not called(func):
            continue
        if func.ident in ['__setattr__', '__getattr__', '__iadd__', '__isub__', '__imul__']:  # XXX
            continue
        if isinstance(func.parent, Class):
            if func.invisible or func.inherited or not gv.inhcpa(func):
                continue
        if isinstance(func.parent, Class) and func.ident in func.parent.staticmethods:
            logger.warning("'%s.%s' method not exported (staticmethod)", func.parent.ident, func.ident)
            continue
        builtins = True
        for formal in func.formals:
            try:
                nodetypestr(gx, func.vars[formal], func, check_extmod=True, mv=gv.mv)
            except ExtmodError:
                builtins = False
                reason = "cannot convert argument '%s'" % formal
        try:
            nodetypestr(gx, func.retnode.thing, func, check_extmod=True, check_ret=True, mv=gv.mv)
        except ExtmodError:
            builtins = False
            reason = 'cannot convert return value'
        if builtins:
            supported.append(func)
        else:
            if isinstance(func.parent, Class):
                logger.warning("'%s.%s' method not exported (%s)", func.parent.ident, func.ident, reason)
            else:
                logger.warning("'%s' function not exported (%s)", func.ident, reason)
    return supported


def has_method(cl, name):  # XXX shared.py
    return name in cl.funcs and not cl.funcs[name].invisible and not cl.funcs[name].inherited and called(cl.funcs[name])


def do_add_globals(gx, gv, classes, __ss_mod):
    # global variables
    for var in supported_vars(gx, gv, gv.mv.globals.values()):
        if [1 for t in gv.mergeinh[var] if t[0].ident in ['int_', 'float_', 'bool_']]:
            print('    PyModule_AddObject(%(ssmod)s, (char *)"%(name)s", __to_py(%(var)s));' % {'name': var.name, 'var': '__' + gv.module.ident + '__::' + gv.cpp_name(var), 'ssmod': __ss_mod}, file=gv.out)
        else:
            print('    PyModule_AddObject(%(ssmod)s, (char *)"%(name)s", __to_py(%(var)s));' % {'name': var.name, 'var': '__' + gv.module.ident + '__::' + gv.cpp_name(var), 'ssmod': __ss_mod}, file=gv.out)


def do_reduce_setstate(gx, gv, cl, vars):
    if def_class(gx, 'Exception') in cl.ancestors():  # XXX
        return
    print('PyObject *%s__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {' % clname(cl), file=gv.out)
    print('    PyObject *t = PyTuple_New(3);', file=gv.out)
    print('    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_%s, "__newobj__"));' % '_'.join(gv.module.name_list), file=gv.out)
    print('    PyObject *a = PyTuple_New(1);', file=gv.out)
    print('    Py_INCREF((PyObject *)&%sObjectType);' % clname(cl), file=gv.out)
    print('    PyTuple_SetItem(a, 0, (PyObject *)&%sObjectType);' % clname(cl), file=gv.out)
    print('    PyTuple_SetItem(t, 1, a);', file=gv.out)
    print('    PyObject *b = PyTuple_New(%d);' % len(vars), file=gv.out)
    for i, var in enumerate(vars):
        print('    PyTuple_SetItem(b, %d, __to_py(((%sObject *)self)->__ss_object->%s));' % (i, clname(cl), gv.cpp_name(var)), file=gv.out)
    print('    PyTuple_SetItem(t, 2, b);', file=gv.out)
    print('    return t;', file=gv.out)
    print('}\n', file=gv.out)
    print('PyObject *%s__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {' % clname(cl), file=gv.out)
    print('    int l = PyTuple_Size(args);', file=gv.out)
    print('    PyObject *state = PyTuple_GetItem(args, 0);', file=gv.out)
    for i, var in enumerate(vars):
        vartype = nodetypestr(gx, var, var.parent, mv=gv.mv)
        print('    ((%sObject *)self)->__ss_object->%s = __to_ss<%s>(PyTuple_GetItem(state, %d));' % (clname(cl), gv.cpp_name(var), vartype, i), file=gv.out)
    print('    Py_INCREF(Py_None);', file=gv.out)
    print('    return Py_None;', file=gv.out)
    print('}\n', file=gv.out)


def convert_methods(gx, gv, cl, declare):
    if def_class(gx, 'Exception') in cl.ancestors():
        return
    if declare:
        print('    virtual PyObject *__to_py__();', file=gv.out)
    else:
        for n in cl.module.name_list:
            print('namespace __%s__ { /* XXX */' % n, file=gv.out)
        print()

        print('PyObject *%s::__to_py__() {' % gv.cpp_name(cl), file=gv.out)
        print('    PyObject *p;', file=gv.out)
        print('    if(__ss_proxy->has_key(this))', file=gv.out)
        print('        p = (PyObject *)(__ss_proxy->__getitem__(this));', file=gv.out)
        print('    else {', file=gv.out)
        print('        %sObject *self = (%sObject *)(%sObjectType.tp_alloc(&%sObjectType, 0));' % (4 * (clname(cl),)), file=gv.out)
        print('        self->__ss_object = this;', file=gv.out)
        print('        __ss_proxy->__setitem__(self->__ss_object, self);', file=gv.out)
        print('        p = (PyObject *)self;', file=gv.out)
        print('    }', file=gv.out)
        print('    Py_INCREF(p);', file=gv.out)
        print('    return p;', file=gv.out)
        print('}\n', file=gv.out)

        for n in cl.module.name_list:
            print('} // module namespace', file=gv.out)
        print()

        print('namespace __shedskin__ { /* XXX */\n', file=gv.out)

        print('template<> %s::%s *__to_ss(PyObject *p) {' % (cl.module.full_path(), gv.cpp_name(cl)), file=gv.out)
        print('    if(p == Py_None) return NULL;', file=gv.out)
        print('    if(PyObject_IsInstance(p, (PyObject *)&%s::%sObjectType)!=1)' % (cl.module.full_path(), clname(cl)), file=gv.out)
        print('        throw new TypeError(new str("error in conversion to Shed Skin (%s expected)"));' % cl.ident, file=gv.out)
        print('    return ((%s::%sObject *)p)->__ss_object;' % (cl.module.full_path(), clname(cl)), file=gv.out)
        print('}\n}', file=gv.out)


def do_extmod_methoddef(gx, gv, ident, funcs, cl):
    if cl:
        ident = clname(cl)
    print('static PyNumberMethods %s_as_number = {' % ident, file=gv.out)
    for overload in OVERLOAD:
        if [f for f in funcs if f.ident == overload]:
            if overload == '__nonzero__':  # XXX
                print('    (int (*)(PyObject *))%s_%s,' % (clname(f.parent), overload), file=gv.out)
            elif overload in OVERLOAD_SINGLE:
                print('    (PyObject *(*)(PyObject *))%s_%s,' % (clname(f.parent), overload), file=gv.out)
            else:
                print('    (PyCFunction)%s_%s,' % (clname(f.parent), overload), file=gv.out)
        else:
            print('    0,', file=gv.out)
    print('};\n', file=gv.out)
    if cl and not def_class(gx, 'Exception') in cl.ancestors():
        print('PyObject *%s__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);' % ident, file=gv.out)
        print('PyObject *%s__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);\n' % ident, file=gv.out)
    print('static PyMethodDef %sMethods[] = {' % ident, file=gv.out)
    if not cl:
        print('    {(char *)"__newobj__", (PyCFunction)__ss__newobj__, METH_VARARGS | METH_KEYWORDS, (char *)""},', file=gv.out)
    elif cl and not def_class(gx, 'Exception') in cl.ancestors():
        print('    {(char *)"__reduce__", (PyCFunction)%s__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},' % ident, file=gv.out)
        print('    {(char *)"__setstate__", (PyCFunction)%s__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},' % ident, file=gv.out)
    for func in funcs:
        if isinstance(func.parent, Class):
            id = clname(func.parent) + '_' + func.ident
        else:
            id = 'Global_' + '_'.join(gv.module.name_list) + '_' + func.ident
        print('    {(char *)"%(id)s", (PyCFunction)%(id2)s, METH_VARARGS | METH_KEYWORDS, (char *)""},' % {'id': func.ident, 'id2': id}, file=gv.out)
    print('    {NULL}\n};\n', file=gv.out)


def do_extmod_method(gx, gv, func):
    is_method = isinstance(func.parent, Class)
    if is_method:
        formals = func.formals[1:]
    else:
        formals = func.formals

    if isinstance(func.parent, Class):
        id = clname(func.parent) + '_' + func.ident
    else:
        id = 'Global_' + '_'.join(gv.module.name_list) + '_' + func.ident
    print('PyObject *%s(PyObject *self, PyObject *args, PyObject *kwargs) {' % id, file=gv.out)
    print('    try {', file=gv.out)

    for i, formal in enumerate(formals):
        gv.start('')
        typ = nodetypestr(gx, func.vars[formal], func, mv=gv.mv)
        if func.ident in OVERLOAD:
            print('        %(type)sarg_%(num)d = __to_ss<%(type)s>(args);' % {'type': typ, 'num': i}, file=gv.out)
            continue
        gv.append('        %(type)sarg_%(num)d = __ss_arg<%(type)s>("%(name)s", %(num)d, ' % {'type': typ, 'num': i, 'name': formal})
        if i >= len(formals) - len(func.defaults):
            gv.append('1, ')
            defau = func.defaults[i - (len(formals) - len(func.defaults))]
            if defau in func.mv.defaults:
                if gv.mergeinh[defau] == set([(def_class(gx, 'none'), 0)]):
                    gv.append('0')
                else:
                    gv.append('%s::default_%d' % ('__' + func.mv.module.ident + '__', func.mv.defaults[defau][0]))
            else:
                gv.visit(defau, func)
        elif typ.strip() == '__ss_bool':
            gv.append('0, False')
        else:
            gv.append('0, 0')
        gv.append(', args, kwargs)')
        gv.eol()
    print()

    # call
    if is_method:
        where = '((%sObject *)self)->__ss_object->' % clname(func.parent)
    else:
        where = '__' + gv.module.ident + '__::'
    print('        return __to_py(' + where + gv.cpp_name(func.ident) + '(' + ', '.join('arg_%d' % i for i in range(len(formals))) + '));\n', file=gv.out)

    # convert exceptions
    print('    } catch (Exception *e) {', file=gv.out)
    print('        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));', file=gv.out)
    print('        return 0;', file=gv.out)
    print('    }', file=gv.out)
    print('}\n', file=gv.out)


def do_extmod(gx, gv):
    print('/* extension module glue */\n', file=gv.out)
    print('extern "C" {', file=gv.out)
    print('#include <Python.h>', file=gv.out)
    print('#include <structmember.h>\n', file=gv.out)

    print('PyObject *__ss_mod_%s;\n' % '_'.join(gv.module.name_list), file=gv.out)

    # classes
    classes = exported_classes(gx, gv, warns=True)
    for cl in classes:
        do_extmod_class(gx, gv, cl)

    for n in gv.module.name_list:
        print('namespace __%s__ { /* XXX */' % n, file=gv.out)

    # global functions
    funcs = supported_funcs(gx, gv, gv.module.mv.funcs.values())
    for func in funcs:
        do_extmod_method(gx, gv, func)
    do_extmod_methoddef(gx, gv, 'Global_' + '_'.join(gv.module.name_list), funcs, None)

    # module init function
    print('PyMODINIT_FUNC init%s(void) {' % '_'.join(gv.module.name_list), file=gv.out)

    # initialize modules
    __ss_mod = '__ss_mod_%s' % '_'.join(gv.module.name_list)
    if gv.module == gx.main_module:
        gv.do_init_modules()
        print('    __' + gv.module.ident + '__::__init();', file=gv.out)
    print('\n    %s = Py_InitModule((char *)"%s", Global_%sMethods);' % (__ss_mod, gv.module.ident, '_'.join(gv.module.name_list)), file=gv.out)
    print('    if(!%s)' % __ss_mod, file=gv.out)
    print('        return;\n', file=gv.out)

    # add types to module
    for cl in classes:
        print('    if (PyType_Ready(&%sObjectType) < 0)' % clname(cl), file=gv.out)
        print('        return;\n', file=gv.out)
        print('    PyModule_AddObject(%s, "%s", (PyObject *)&%sObjectType);' % (__ss_mod, cl.ident, clname(cl)), file=gv.out)
    print()

    if gv.module == gx.main_module:
        do_init_mods(gx, gv, 'init')
        do_init_mods(gx, gv, 'add')
        print('    add%s();' % gv.module.ident, file=gv.out)
    print('\n}\n', file=gv.out)

    print('PyMODINIT_FUNC add%s(void) {' % '_'.join(gv.module.name_list), file=gv.out)
    do_add_globals(gx, gv, classes, __ss_mod)
    print('\n}', file=gv.out)

    for n in gv.module.name_list:
        print('\n} // namespace __%s__' % n, file=gv.out)
    print('\n} // extern "C"', file=gv.out)

    # conversion methods to/from CPython/Shedskin
    for cl in classes:
        convert_methods(gx, gv, cl, False)


def do_extmod_class(gx, gv, cl):
    for n in cl.module.name_list:
        print('namespace __%s__ { /* XXX */' % n, file=gv.out)
    print()

    # determine methods, vars to expose
    funcs = supported_funcs(gx, gv, cl.funcs.values())
    vars = supported_vars(gx, gv, cl.vars.values())

    # python object
    print('/* class %s */\n' % cl.ident, file=gv.out)
    print('typedef struct {', file=gv.out)
    print('    PyObject_HEAD', file=gv.out)
    print('    %s::%s *__ss_object;' % (cl.module.full_path(), gv.cpp_name(cl)), file=gv.out)
    print('} %sObject;\n' % clname(cl), file=gv.out)
    print('static PyMemberDef %sMembers[] = {' % clname(cl), file=gv.out)
    print('    {NULL}\n};\n', file=gv.out)

    # methods
    for func in funcs:
        do_extmod_method(gx, gv, func)
    do_extmod_methoddef(gx, gv, cl.ident, funcs, cl)

    # tp_init
    if has_method(cl, '__init__') and cl.funcs['__init__'] in funcs:
        print('int %s___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {' % clname(cl), file=gv.out)
        print('    if(!%s___init__(self, args, kwargs))' % clname(cl), file=gv.out)
        print('        return -1;', file=gv.out)
        print('    return 0;', file=gv.out)
        print('}\n', file=gv.out)

    # tp_new
    print('PyObject *%sNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {' % clname(cl), file=gv.out)
    print('    %sObject *self = (%sObject *)type->tp_alloc(type, 0);' % (clname(cl), clname(cl)), file=gv.out)
    print('    self->__ss_object = new %s::%s();' % (cl.module.full_path(), gv.cpp_name(cl)), file=gv.out)
    print('    self->__ss_object->__class__ = %s::cl_%s;' % (cl.module.full_path(), cl.ident), file=gv.out)
    print('    __ss_proxy->__setitem__(self->__ss_object, self);', file=gv.out)
    print('    return (PyObject *)self;', file=gv.out)
    print('}\n', file=gv.out)

    # tp_dealloc
    print('void %sDealloc(%sObject *self) {' % (clname(cl), clname(cl)), file=gv.out)
    print('    self->ob_type->tp_free((PyObject *)self);', file=gv.out)
    print('    __ss_proxy->__delitem__(self->__ss_object);', file=gv.out)
    print('}\n', file=gv.out)

    # getset
    for var in vars:
        print('PyObject *__ss_get_%s_%s(%sObject *self, void *closure) {' % (clname(cl), var.name, clname(cl)), file=gv.out)
        print('    return __to_py(self->__ss_object->%s);' % gv.cpp_name(var), file=gv.out)
        print('}\n', file=gv.out)

        print('int __ss_set_%s_%s(%sObject *self, PyObject *value, void *closure) {' % (clname(cl), var.name, clname(cl)), file=gv.out)
        print('    try {', file=gv.out)
        typ = nodetypestr(gx, var, var.parent, mv=gv.mv)
        if typ == 'void *':  # XXX investigate
            print('        self->__ss_object->%s = NULL;' % gv.cpp_name(var), file=gv.out)
        else:
            print('        self->__ss_object->%s = __to_ss<%s>(value);' % (gv.cpp_name(var), typ), file=gv.out)
        print('    } catch (Exception *e) {', file=gv.out)
        print('        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));', file=gv.out)
        print('        return -1;', file=gv.out)
        print('    }', file=gv.out)

        print('    return 0;', file=gv.out)
        print('}\n', file=gv.out)

    print('PyGetSetDef %sGetSet[] = {' % clname(cl), file=gv.out)
    for var in vars:
        print('    {(char *)"%s", (getter)__ss_get_%s_%s, (setter)__ss_set_%s_%s, (char *)"", NULL},' % (var.name, clname(cl), var.name, clname(cl), var.name), file=gv.out)
    print('    {NULL}\n};\n', file=gv.out)

    # python type
    print('PyTypeObject %sObjectType = {' % clname(cl), file=gv.out)
    print('    PyObject_HEAD_INIT(NULL)', file=gv.out)
    print('    0,              /* ob_size           */', file=gv.out)
    print('    "%s.%s",        /* tp_name           */' % (cl.module.ident, cl.ident), file=gv.out)
    print('    sizeof(%sObject), /* tp_basicsize      */' % clname(cl), file=gv.out)
    print('    0,              /* tp_itemsize       */', file=gv.out)
    print('    (destructor)%sDealloc, /* tp_dealloc        */' % clname(cl), file=gv.out)
    print('    0,              /* tp_print          */', file=gv.out)
    print('    0,              /* tp_getattr        */', file=gv.out)
    print('    0,              /* tp_setattr        */', file=gv.out)
    print('    0,              /* tp_compare        */', file=gv.out)
    if has_method(cl, '__repr__'):
        print('    (PyObject *(*)(PyObject *))%s___repr__, /* tp_repr           */' % clname(cl), file=gv.out)
    else:
        print('    0,              /* tp_repr           */', file=gv.out)
    print('    &%s_as_number,  /* tp_as_number      */' % clname(cl), file=gv.out)
    print('    0,              /* tp_as_sequence    */', file=gv.out)
    print('    0,              /* tp_as_mapping     */', file=gv.out)
    print('    0,              /* tp_hash           */', file=gv.out)
    print('    0,              /* tp_call           */', file=gv.out)
    if has_method(cl, '__str__'):
        print('    (PyObject *(*)(PyObject *))%s___str__, /* tp_str           */' % clname(cl), file=gv.out)
    else:
        print('    0,              /* tp_str            */', file=gv.out)
    print('    0,              /* tp_getattro       */', file=gv.out)
    print('    0,              /* tp_setattro       */', file=gv.out)
    print('    0,              /* tp_as_buffer      */', file=gv.out)
    print('    Py_TPFLAGS_DEFAULT, /* tp_flags          */', file=gv.out)
    print('    0,              /* tp_doc            */', file=gv.out)
    print('    0,              /* tp_traverse       */', file=gv.out)
    print('    0,              /* tp_clear          */', file=gv.out)
    print('    0,              /* tp_richcompare    */', file=gv.out)
    print('    0,              /* tp_weaklistoffset */', file=gv.out)
    print('    0,              /* tp_iter           */', file=gv.out)
    print('    0,              /* tp_iternext       */', file=gv.out)
    print('    %sMethods,      /* tp_methods        */' % clname(cl), file=gv.out)
    print('    %sMembers,      /* tp_members        */' % clname(cl), file=gv.out)
    print('    %sGetSet,       /* tp_getset         */' % clname(cl), file=gv.out)
    if cl.bases and not cl.bases[0].mv.module.builtin:
            print('    &%sObjectType,              /* tp_base           */' % clname(cl.bases[0]), file=gv.out)
    else:
        print('    0,              /* tp_base           */', file=gv.out)
    print('    0,              /* tp_dict           */', file=gv.out)
    print('    0,              /* tp_descr_get      */', file=gv.out)
    print('    0,              /* tp_descr_set      */', file=gv.out)
    print('    0,              /* tp_dictoffset     */', file=gv.out)
    if has_method(cl, '__init__') and cl.funcs['__init__'] in funcs:
        print('    %s___tpinit__, /* tp_init           */' % clname(cl), file=gv.out)
    else:
        print('    0,              /* tp_init           */', file=gv.out)
    print('    0,              /* tp_alloc          */', file=gv.out)
    print('    %sNew,          /* tp_new            */' % clname(cl), file=gv.out)
    print('};\n', file=gv.out)
    do_reduce_setstate(gx, gv, cl, vars)
    for n in cl.module.name_list:
        print('} // namespace __%s__' % n, file=gv.out)
    print()


def pyinit_func(gv):
    for what in ('init', 'add'):
        print('PyMODINIT_FUNC %s%s(void);\n' % (what, '_'.join(gv.module.name_list)), file=gv.out)


def exported_classes(gx, gv, warns=False):
    classes = []
    for cl in gv.module.mv.classes.values():
        if def_class(gx, 'Exception') in cl.ancestors():
            if warns:
                logger.warning("'%s' class not exported (inherits from Exception)", cl.ident)
        else:
            classes.append(cl)
    return sorted(classes, key=lambda x: x.def_order)


def convert_methods2(gx, gv):
    for cl in exported_classes(gx, gv):
        print('extern PyTypeObject %sObjectType;' % clname(cl), file=gv.out)
    print('namespace __shedskin__ { /* XXX */\n', file=gv.out)
    for cl in exported_classes(gx, gv):
        print('template<> %s::%s *__to_ss(PyObject *p);' % (cl.module.full_path(), gv.cpp_name(cl)), file=gv.out)
    print('}', file=gv.out)
