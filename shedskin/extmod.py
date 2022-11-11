from __future__ import print_function

"""
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

extmod.py: extension module support

"""
import logging

from .infer import called
from .python import Class, Module, def_class
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
    write = lambda s: print(s, file=gv.out)
    if def_class(gx, 'Exception') in cl.ancestors():  # XXX
        return
    write('PyObject *%s__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {' % clname(cl))
    write('    PyObject *t = PyTuple_New(3);')
    write('    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_%s, "__newobj__"));' % '_'.join(gv.module.name_list))
    write('    PyObject *a = PyTuple_New(1);')
    write('    Py_INCREF((PyObject *)&%sObjectType);' % clname(cl))
    write('    PyTuple_SetItem(a, 0, (PyObject *)&%sObjectType);' % clname(cl))
    write('    PyTuple_SetItem(t, 1, a);')
    write('    PyObject *b = PyTuple_New(%d);' % len(vars))
    for i, var in enumerate(vars):
        write('    PyTuple_SetItem(b, %d, __to_py(((%sObject *)self)->__ss_object->%s));' % (i, clname(cl), gv.cpp_name(var)))
    write('    PyTuple_SetItem(t, 2, b);')
    write('    return t;')
    write('}\n')
    write('PyObject *%s__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {' % clname(cl))
    write('    int l = PyTuple_Size(args);')
    write('    PyObject *state = PyTuple_GetItem(args, 0);')
    for i, var in enumerate(vars):
        vartype = nodetypestr(gx, var, var.parent, mv=gv.mv)
        write('    ((%sObject *)self)->__ss_object->%s = __to_ss<%s>(PyTuple_GetItem(state, %d));' % (clname(cl), gv.cpp_name(var), vartype, i))
    write('    Py_INCREF(Py_None);')
    write('    return Py_None;')
    write('}\n')


def convert_methods(gx, gv, cl, declare):
    write = lambda s: print(s, file=gv.out)
    if def_class(gx, 'Exception') in cl.ancestors():
        return
    if declare:
        write('    virtual PyObject *__to_py__();')
    else:
        for n in cl.module.name_list:
            write('namespace __%s__ { /* XXX */' % n)
        write('')

        write('PyObject *%s::__to_py__() {' % gv.cpp_name(cl))
        write('    PyObject *p;')
        write('    if(__ss_proxy->has_key(this))')
        write('        p = (PyObject *)(__ss_proxy->__getitem__(this));')
        write('    else {')
        write('        %sObject *self = (%sObject *)(%sObjectType.tp_alloc(&%sObjectType, 0));' % (4 * (clname(cl),)))
        write('        self->__ss_object = this;')
        write('        __ss_proxy->__setitem__(self->__ss_object, self);')
        write('        p = (PyObject *)self;')
        write('    }')
        write('    Py_INCREF(p);')
        write('    return p;')
        write('}\n')

        for n in cl.module.name_list:
            write('} // module namespace')
        write('')

        write('namespace __shedskin__ { /* XXX */\n')

        write('template<> %s::%s *__to_ss(PyObject *p) {' % (cl.module.full_path(), gv.cpp_name(cl)))
        write('    if(p == Py_None) return NULL;')
        write('    if(PyObject_IsInstance(p, (PyObject *)&%s::%sObjectType)!=1)' % (cl.module.full_path(), clname(cl)))
        write('        throw new TypeError(new str("error in conversion to Shed Skin (%s expected)"));' % cl.ident)
        write('    return ((%s::%sObject *)p)->__ss_object;' % (cl.module.full_path(), clname(cl)))
        write('}\n}')


def do_extmod_methoddef(gx, gv, ident, funcs, cl):
    write = lambda s: print(s, file=gv.out)
    if cl:
        ident = clname(cl)
    write('static PyNumberMethods %s_as_number = {' % ident)
    for overload in OVERLOAD:
        if [f for f in funcs if f.ident == overload]:
            if overload == '__nonzero__':  # XXX
                write('    (int (*)(PyObject *))%s_%s,' % (clname(f.parent), overload))
            elif overload in OVERLOAD_SINGLE:
                write('    (PyObject *(*)(PyObject *))%s_%s,' % (clname(f.parent), overload))
            else:
                write('    (PyCFunction)%s_%s,' % (clname(f.parent), overload))
        else:
            write('    0,')
    write('};\n')
    if cl and not def_class(gx, 'Exception') in cl.ancestors():
        write('PyObject *%s__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);' % ident)
        write('PyObject *%s__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);\n' % ident)
    write('static PyMethodDef %sMethods[] = {' % ident)
    if not cl:
        write('    {(char *)"__newobj__", (PyCFunction)__ss__newobj__, METH_VARARGS | METH_KEYWORDS, (char *)""},')
    elif cl and not def_class(gx, 'Exception') in cl.ancestors():
        write('    {(char *)"__reduce__", (PyCFunction)%s__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},' % ident)
        write('    {(char *)"__setstate__", (PyCFunction)%s__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},' % ident)
    for func in funcs:
        if isinstance(func.parent, Class):
            id = clname(func.parent) + '_' + func.ident
        else:
            id = 'Global_' + '_'.join(gv.module.name_list) + '_' + func.ident
        write('    {(char *)"%(id)s", (PyCFunction)%(id2)s, METH_VARARGS | METH_KEYWORDS, (char *)""},' % {'id': func.ident, 'id2': id})
    write('    {NULL}\n};\n')


def do_extmod_method(gx, gv, func):
    write = lambda s: print(s, file=gv.out)
    is_method = isinstance(func.parent, Class)
    if is_method:
        formals = func.formals[1:]
    else:
        formals = func.formals

    if isinstance(func.parent, Class):
        id = clname(func.parent) + '_' + func.ident
    else:
        id = 'Global_' + '_'.join(gv.module.name_list) + '_' + func.ident
    write('PyObject *%s(PyObject *self, PyObject *args, PyObject *kwargs) {' % id)
    write('    try {')

    for i, formal in enumerate(formals):
        gv.start('')
        typ = nodetypestr(gx, func.vars[formal], func, mv=gv.mv)
        if func.ident in OVERLOAD:
            write('        %(type)sarg_%(num)d = __to_ss<%(type)s>(args);' % {'type': typ, 'num': i})
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
    write('')

    # call
    if is_method:
        where = '((%sObject *)self)->__ss_object->' % clname(func.parent)
    else:
        where = '__' + gv.module.ident + '__::'
    write('        return __to_py(' + where + gv.cpp_name(func.ident) + '(' + ', '.join('arg_%d' % i for i in range(len(formals))) + '));\n')

    # convert exceptions
    write('    } catch (Exception *e) {')
    write('        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));')
    write('        return 0;')
    write('    }')
    write('}\n')


def do_extmod(gx, gv):
    write = lambda s: print(s, file=gv.out)
    write('/* extension module glue */\n')
    write('extern "C" {')
    write('#include <Python.h>')
    write('#include <structmember.h>\n')

    write('PyObject *__ss_mod_%s;\n' % '_'.join(gv.module.name_list))

    # classes
    classes = exported_classes(gx, gv, warns=True)
    for cl in classes:
        do_extmod_class(gx, gv, cl)

    for n in gv.module.name_list:
        write('namespace __%s__ { /* XXX */' % n)

    # global functions
    funcs = supported_funcs(gx, gv, gv.module.mv.funcs.values())
    for func in funcs:
        do_extmod_method(gx, gv, func)
    do_extmod_methoddef(gx, gv, 'Global_' + '_'.join(gv.module.name_list), funcs, None)

    # module init function
    write('PyMODINIT_FUNC init%s(void) {' % '_'.join(gv.module.name_list))

    # initialize modules
    __ss_mod = '__ss_mod_%s' % '_'.join(gv.module.name_list)
    if gv.module == gx.main_module:
        gv.do_init_modules()
        write('    __' + gv.module.ident + '__::__init();')
    write('\n    %s = Py_InitModule((char *)"%s", Global_%sMethods);' % (__ss_mod, gv.module.ident, '_'.join(gv.module.name_list)))
    write('    if(!%s)' % __ss_mod)
    write('        return;\n')

    # add types to module
    for cl in classes:
        write('    if (PyType_Ready(&%sObjectType) < 0)' % clname(cl))
        write('        return;\n')
        write('    PyModule_AddObject(%s, "%s", (PyObject *)&%sObjectType);' % (__ss_mod, cl.ident, clname(cl)))
    write('')

    if gv.module == gx.main_module:
        do_init_mods(gx, gv, 'init')
        do_init_mods(gx, gv, 'add')
        write('    add%s();' % gv.module.ident)
    write('\n}\n')

    write('PyMODINIT_FUNC add%s(void) {' % '_'.join(gv.module.name_list))
    do_add_globals(gx, gv, classes, __ss_mod)
    write('\n}')

    for n in gv.module.name_list:
        write('\n} // namespace __%s__' % n)
    write('\n} // extern "C"')

    # conversion methods to/from CPython/Shedskin
    for cl in classes:
        convert_methods(gx, gv, cl, False)


def do_extmod_class(gx, gv, cl):
    write = lambda s: print(s, file=gv.out)
    for n in cl.module.name_list:
        write('namespace __%s__ { /* XXX */' % n)
    write('')

    # determine methods, vars to expose
    funcs = supported_funcs(gx, gv, cl.funcs.values())
    vars = supported_vars(gx, gv, cl.vars.values())

    # python object
    write('/* class %s */\n' % cl.ident)
    write('typedef struct {')
    write('    PyObject_HEAD')
    write('    %s::%s *__ss_object;' % (cl.module.full_path(), gv.cpp_name(cl)))
    write('} %sObject;\n' % clname(cl))
    write('static PyMemberDef %sMembers[] = {' % clname(cl))
    write('    {NULL}\n};\n')

    # methods
    for func in funcs:
        do_extmod_method(gx, gv, func)
    do_extmod_methoddef(gx, gv, cl.ident, funcs, cl)

    # tp_init
    if has_method(cl, '__init__') and cl.funcs['__init__'] in funcs:
        write('int %s___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {' % clname(cl))
        write('    if(!%s___init__(self, args, kwargs))' % clname(cl))
        write('        return -1;')
        write('    return 0;')
        write('}\n')

    # tp_new
    write('PyObject *%sNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {' % clname(cl))
    write('    %sObject *self = (%sObject *)type->tp_alloc(type, 0);' % (clname(cl), clname(cl)))
    write('    self->__ss_object = new %s::%s();' % (cl.module.full_path(), gv.cpp_name(cl)))
    write('    self->__ss_object->__class__ = %s::cl_%s;' % (cl.module.full_path(), cl.ident))
    write('    __ss_proxy->__setitem__(self->__ss_object, self);')
    write('    return (PyObject *)self;')
    write('}\n')

    # tp_dealloc
    write('void %sDealloc(%sObject *self) {' % (clname(cl), clname(cl)))
    write('    self->ob_type->tp_free((PyObject *)self);')
    write('    __ss_proxy->__delitem__(self->__ss_object);')
    write('}\n')

    # getset
    for var in vars:
        write('PyObject *__ss_get_%s_%s(%sObject *self, void *closure) {' % (clname(cl), var.name, clname(cl)))
        write('    return __to_py(self->__ss_object->%s);' % gv.cpp_name(var))
        write('}\n')

        write('int __ss_set_%s_%s(%sObject *self, PyObject *value, void *closure) {' % (clname(cl), var.name, clname(cl)))
        write('    try {')
        typ = nodetypestr(gx, var, var.parent, mv=gv.mv)
        if typ == 'void *':  # XXX investigate
            write('        self->__ss_object->%s = NULL;' % gv.cpp_name(var))
        else:
            write('        self->__ss_object->%s = __to_ss<%s>(value);' % (gv.cpp_name(var), typ))
        write('    } catch (Exception *e) {')
        write('        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));')
        write('        return -1;')
        write('    }')

        write('    return 0;')
        write('}\n')

    write('PyGetSetDef %sGetSet[] = {' % clname(cl))
    for var in vars:
        write('    {(char *)"%s", (getter)__ss_get_%s_%s, (setter)__ss_set_%s_%s, (char *)"", NULL},' % (var.name, clname(cl), var.name, clname(cl), var.name))
    write('    {NULL}\n};\n')

    # python type
    write('PyTypeObject %sObjectType = {' % clname(cl))
    write('    PyObject_HEAD_INIT(NULL)')
    write('    0,              /* ob_size           */')
    write('    "%s.%s",        /* tp_name           */' % (cl.module.ident, cl.ident))
    write('    sizeof(%sObject), /* tp_basicsize      */' % clname(cl))
    write('    0,              /* tp_itemsize       */')
    write('    (destructor)%sDealloc, /* tp_dealloc        */' % clname(cl))
    write('    0,              /* tp_print          */')
    write('    0,              /* tp_getattr        */')
    write('    0,              /* tp_setattr        */')
    write('    0,              /* tp_compare        */')
    if has_method(cl, '__repr__'):
        write('    (PyObject *(*)(PyObject *))%s___repr__, /* tp_repr           */' % clname(cl))
    else:
        write('    0,              /* tp_repr           */')
    write('    &%s_as_number,  /* tp_as_number      */' % clname(cl))
    write('    0,              /* tp_as_sequence    */')
    write('    0,              /* tp_as_mapping     */')
    write('    0,              /* tp_hash           */')
    write('    0,              /* tp_call           */')
    if has_method(cl, '__str__'):
        write('    (PyObject *(*)(PyObject *))%s___str__, /* tp_str           */' % clname(cl))
    else:
        write('    0,              /* tp_str            */')
    write('    0,              /* tp_getattro       */')
    write('    0,              /* tp_setattro       */')
    write('    0,              /* tp_as_buffer      */')
    write('    Py_TPFLAGS_DEFAULT, /* tp_flags          */')
    write('    0,              /* tp_doc            */')
    write('    0,              /* tp_traverse       */')
    write('    0,              /* tp_clear          */')
    write('    0,              /* tp_richcompare    */')
    write('    0,              /* tp_weaklistoffset */')
    write('    0,              /* tp_iter           */')
    write('    0,              /* tp_iternext       */')
    write('    %sMethods,      /* tp_methods        */' % clname(cl))
    write('    %sMembers,      /* tp_members        */' % clname(cl))
    write('    %sGetSet,       /* tp_getset         */' % clname(cl))
    if cl.bases and not cl.bases[0].mv.module.builtin:
        write('    &%sObjectType,              /* tp_base           */' % clname(cl.bases[0]))
    else:
        write('    0,              /* tp_base           */')
    write('    0,              /* tp_dict           */')
    write('    0,              /* tp_descr_get      */')
    write('    0,              /* tp_descr_set      */')
    write('    0,              /* tp_dictoffset     */')
    if has_method(cl, '__init__') and cl.funcs['__init__'] in funcs:
        write('    %s___tpinit__, /* tp_init           */' % clname(cl))
    else:
        write('    0,              /* tp_init           */')
    write('    0,              /* tp_alloc          */')
    write('    %sNew,          /* tp_new            */' % clname(cl))
    write('};\n')
    do_reduce_setstate(gx, gv, cl, vars)
    for n in cl.module.name_list:
        write('} // namespace __%s__' % n)
    write('')


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
    write = lambda s: print(s, file=gv.out)
    for cl in exported_classes(gx, gv):
        write('extern PyTypeObject %sObjectType;' % clname(cl))
    write('namespace __shedskin__ { /* XXX */\n')
    for cl in exported_classes(gx, gv):
        write('template<> %s::%s *__to_ss(PyObject *p);' % (cl.module.full_path(), gv.cpp_name(cl)))
    write('}')
