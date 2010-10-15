'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2009 Mark Dufour; License GNU GPL version 3 (See LICENSE)

extmod.py: extension module support

'''

from shared import *
import cpp

OVERLOAD_SINGLE = ['__neg__', '__pos__', '__abs__', '__nonzero__']
OVERLOAD = ['__add__', '__sub__', '__mul__', '__div__', '__mod__', '__divmod__', '__pow__'] + OVERLOAD_SINGLE

def do_extmod(gv):
    print >>gv.out, '/* extension module glue */\n'
    print >>gv.out, 'extern "C" {'
    print >>gv.out, '#include <Python.h>'
    print >>gv.out, '#include <structmember.h>\n'

    print >>gv.out, 'PyObject *__ss_mod_%s;\n' % '_'.join(gv.module.mod_path)

    # classes
    classes = exported_classes(gv, warns=True)
    for cl in classes:
        do_extmod_class(gv, cl)

    for n in gv.module.mod_path:
        print >>gv.out, 'namespace __%s__ { /* XXX */' % n

    # global functions
    funcs = supported_funcs(gv, gv.module.funcs.values())
    for func in funcs:
        do_extmod_method(gv, func)
    do_extmod_methoddef(gv, 'Global_'+'_'.join(gv.module.mod_path), funcs)

    # module init function
    print >>gv.out, 'PyMODINIT_FUNC init%s(void) {' % '_'.join(gv.module.mod_path)

    # initialize modules
    __ss_mod = '__ss_mod_%s' % '_'.join(gv.module.mod_path)
    if gv.module == getgx().main_module:
        gv.do_init_modules()
        print >>gv.out, '    __'+gv.module.ident+'__::__init();'
    print >>gv.out, '\n    %s = Py_InitModule((char *)"%s", Global_%sMethods);' % (__ss_mod, gv.module.ident, '_'.join(gv.module.mod_path))
    print >>gv.out, '    if(!%s)' % __ss_mod
    print >>gv.out, '        return;\n'

    # add types to module
    for cl in classes:
        print >>gv.out, '    if (PyType_Ready(&%s::%sObjectType) < 0)' % (cl.module.full_path(), cl.ident)
        print >>gv.out, '        return;\n'
        print >>gv.out, '    PyModule_AddObject(%s, "%s", (PyObject *)&%s::%sObjectType);' % (__ss_mod, cl.ident, cl.module.full_path(), cl.ident)
    print >>gv.out

    if gv.module == getgx().main_module:
        do_init_mods(gv, 'init')
        do_init_mods(gv, 'add')
        print >>gv.out, '    add%s();' % gv.module.ident
    print >>gv.out, '\n}\n'

    print >>gv.out, 'PyMODINIT_FUNC add%s(void) {' % '_'.join(gv.module.mod_path)
    do_add_globals(gv, classes, __ss_mod)
    print >>gv.out, '\n}'

    for n in gv.module.mod_path:
        print >>gv.out, '\n} // namespace __%s__' % n
    print >>gv.out, '\n} // extern "C"'

    # conversion methods to/from CPython/Shedskin
    for cl in classes:
        convert_methods(gv, cl, False)

def do_init_mods(gv, what):
    for mod in getgx().modules.values():
        if not mod.builtin and not mod is gv.module:
            print >>gv.out, '    %s::%s%s();' % (mod.full_path(), what, '_'.join(mod.mod_path))

def do_add_globals(gv, classes, __ss_mod):
    # global variables
    for var in supported_vars(getmv().globals.values()):
        varname = gv.cpp_name(var.name)
        if [1 for t in gv.mergeinh[var] if t[0].ident in ['int_', 'float_', 'bool_']]:
            print >>gv.out, '    PyModule_AddObject(%(ssmod)s, (char *)"%(name)s", __to_py(%(var)s));' % {'name' : var.name, 'var': '__'+gv.module.ident+'__::'+varname, 'ssmod': __ss_mod}
        else:
            print >>gv.out, '    PyModule_AddObject(%(ssmod)s, (char *)"%(name)s", __to_py(%(var)s));' % {'name' : var.name, 'var': '__'+gv.module.ident+'__::'+varname, 'ssmod': __ss_mod}

def exported_classes(gv, warns=False):
    classes = []
    for cl in gv.module.classes.values():
        if defclass('Exception') in cl.ancestors():
            if warns:
                print '*WARNING* class not exported:', cl.ident
        else:
            classes.append(cl)
    return sorted(classes, key=lambda x: x.def_order)

def do_extmod_methoddef(gv, ident, funcs):
    print >>gv.out, 'static PyNumberMethods %s_as_number = {' % ident
    for overload in OVERLOAD:
        if [f for f in funcs if f.ident == overload]:
            if overload in OVERLOAD_SINGLE:
                print >>gv.out, '    (PyObject *(*)(PyObject *))%s_%s,' % (f.parent.ident, overload)
            else:
                print >>gv.out, '    (PyCFunction)%s_%s,' % (f.parent.ident, overload)
        else:
            print >>gv.out, '    0,'
    print >>gv.out, '};\n'
    if not ident.startswith('Global_'):
        print >>gv.out, 'PyObject *%s__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);' % ident
        print >>gv.out, 'PyObject *%s__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);\n' % ident
    print >>gv.out, 'static PyMethodDef %sMethods[] = {' % ident
    if ident.startswith('Global_'):
        print >>gv.out, '    {(char *)"__newobj__", (PyCFunction)__ss__newobj__, METH_VARARGS | METH_KEYWORDS, (char *)""},' 
    else:
        print >>gv.out, '    {(char *)"__reduce__", (PyCFunction)%s__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},' % ident
        print >>gv.out, '    {(char *)"__setstate__", (PyCFunction)%s__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},' % ident
    for func in funcs:
        if isinstance(func.parent, class_): id = func.parent.ident+'_'+func.ident
        else: id = 'Global_'+'_'.join(gv.module.mod_path)+'_'+func.ident
        print >>gv.out, '    {(char *)"%(id)s", (PyCFunction)%(id2)s, METH_VARARGS | METH_KEYWORDS, (char *)""},' % {'id': func.ident, 'id2': id}
    print >>gv.out, '    {NULL}\n};\n'

def do_extmod_method(gv, func):
    is_method = isinstance(func.parent, class_)
    if is_method: formals = func.formals[1:]
    else: formals = func.formals

    if isinstance(func.parent, class_): id = func.parent.ident+'_'+func.ident # XXX
    else: id = 'Global_'+'_'.join(gv.module.mod_path)+'_'+func.ident # XXX
    print >>gv.out, 'PyObject *%s(PyObject *self, PyObject *args, PyObject *kwargs) {' % id
    print >>gv.out, '    try {'

    for i, formal in enumerate(formals):
        gv.start('')
        typ = cpp.typesetreprnew(func.vars[formal], func)
        cls = [t[0] for t in gv.mergeinh[func.vars[formal]] if isinstance(t[0], class_)]
        cls = [c for c in cls if c.mv.module == getgx().main_module]
        if cls:
            typ = ('__%s__::' % cls[0].mv.module.ident)+typ
        if func.ident in OVERLOAD:
            print >>gv.out, '        %(type)sarg_%(num)d = __to_ss<%(type)s>(args);' % {'type' : typ, 'num' : i}
            continue
        gv.append('        %(type)sarg_%(num)d = __ss_arg<%(type)s>("%(name)s", %(num)d, ' % {'type' : typ, 'num' : i, 'name': formal})
        if i >= len(formals)-len(func.defaults):
            gv.append('1, ')
            defau = func.defaults[i-(len(formals)-len(func.defaults))]
            cast = cpp.assign_needs_cast(defau, None, func.vars[formal], func)
            if cast:
                gv.append('(('+cpp.typesetreprnew(func.vars[formal], func)+')')

            if defau in func.mv.defaults:
                if gv.mergeinh[defau] == set([(defclass('none'),0)]):
                    gv.append('0')
                else:
                    gv.append('%s::default_%d' % ('__'+func.mv.module.ident+'__', func.mv.defaults[defau]))
            else:
                gv.visit(defau, func)
            if cast:
                gv.append(')')
        elif typ.strip() == '__ss_bool':
            gv.append('0, False')
        else:
            gv.append('0, NULL')
        gv.append(', args, kwargs)')
        gv.eol()
    print >>gv.out

    # call
    if is_method: where = '((%sObject *)self)->__ss_object->' % func.parent.ident
    else: where = '__'+gv.module.ident+'__::'
    print >>gv.out, '        return __to_py('+where+gv.cpp_name(func.ident)+'('+', '.join(['arg_%d' % i for i in range(len(formals))])+'));\n'

    # convert exceptions
    print >>gv.out, '    } catch (Exception *e) {'
    print >>gv.out, '        PyErr_SetString(__to_py(e), ((e->msg)?(e->msg->unit.c_str()):""));'
    print >>gv.out, '        return 0;'
    print >>gv.out, '    }'
    print >>gv.out, '}\n'

def supported_funcs(gv, funcs):
    supported = []
    for func in funcs:
        if func.isGenerator or not cpp.hmcpa(func):
            continue
        if func.ident in ['__setattr__', '__getattr__', '__iadd__', '__isub__', '__imul__']: # XXX
            continue
        if isinstance(func.parent, class_):
            if func.invisible or func.inherited or not gv.inhcpa(func):
                continue
        if isinstance(func.parent, class_) and func.ident in func.parent.staticmethods:
            print '*WARNING* method not exported:', func.parent.ident+'.'+func.ident
            continue
        builtins = True
        for formal in func.formals:
            try:
                cpp.typesetreprnew(func.vars[formal], func, check_extmod=True)
                cpp.typesetreprnew(func.retnode.thing, func, check_extmod=True, check_ret=True)
            except cpp.ExtmodError:
                builtins = False
        if builtins:
            supported.append(func)
        else:
            if isinstance(func.parent, class_):
                print '*WARNING* method not exported:', func.parent.ident+'.'+func.ident
            else:
                print '*WARNING* function not exported:', func.ident
    return supported

def supported_vars(vars): # XXX virtuals?
    supported = []
    for var in vars:
        if not var in getgx().merged_inh or not getgx().merged_inh[var]:
            continue
        if var.name.startswith('__'): # XXX
            continue
        if var.invisible or cpp.singletype2(getgx().merged_inh[var], module):
            continue
        try:
            typehu = cpp.typesetreprnew(var, var.parent, check_extmod=True)
        except cpp.ExtmodError:
            if isinstance(var.parent, class_):
                print '*WARNING* variable not exported:', var.parent.ident+'.'+var.name
            else:
                print '*WARNING* variable not exported:', var.name
            continue
        supported.append(var)
    return supported

def hasmethod(cl, name): # XXX shared.py
    return name in cl.funcs and not cl.funcs[name].invisible and not cl.funcs[name].inherited and cpp.hmcpa(cl.funcs[name])

def do_extmod_class(gv, cl):
    for n in cl.module.mod_path:
        print >>gv.out, 'namespace __%s__ { /* XXX */' % n
    print >>gv.out

    # determine methods, vars to expose
    funcs = supported_funcs(gv, cl.funcs.values())
    vars = supported_vars(cl.vars.values())

    # python object
    print >>gv.out, '/* class %s */\n' % cl.ident
    print >>gv.out, 'typedef struct {'
    print >>gv.out, '    PyObject_HEAD'
    print >>gv.out, '    %s::%s *__ss_object;' % (cl.module.full_path(), cpp.nokeywords(cl.ident))
    print >>gv.out, '} %sObject;\n' % cl.ident
    print >>gv.out, 'static PyMemberDef %sMembers[] = {' % cl.ident
    print >>gv.out, '    {NULL}\n};\n'

    # methods
    for func in funcs:
        do_extmod_method(gv, func)
    do_extmod_methoddef(gv, cl.ident, funcs)

    # tp_init
    if hasmethod(cl, '__init__') and cl.funcs['__init__'] in funcs:
        print >>gv.out, 'int %s___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {' % cl.ident
        print >>gv.out, '    if(!%s___init__(self, args, kwargs))' % cl.ident
        print >>gv.out, '        return -1;'
        print >>gv.out, '    return 0;'
        print >>gv.out, '}\n'

    # tp_new
    print >>gv.out, 'PyObject *%sNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {' % cl.ident
    print >>gv.out, '    %sObject *self = (%sObject *)type->tp_alloc(type, 0);' % (cl.ident, cl.ident)
    print >>gv.out, '    self->__ss_object = new %s::%s();' % (cl.module.full_path(), cpp.nokeywords(cl.ident))
    print >>gv.out, '    self->__ss_object->__class__ = %s::cl_%s;' % (cl.module.full_path(), cl.ident)
    print >>gv.out, '    __ss_proxy->__setitem__(self->__ss_object, self);'
    print >>gv.out, '    return (PyObject *)self;'
    print >>gv.out, '}\n'

    # tp_dealloc
    print >>gv.out, 'void %sDealloc(%sObject *self) {' % (cl.ident, cl.ident)
    print >>gv.out, '    self->ob_type->tp_free((PyObject *)self);'
    print >>gv.out, '    __ss_proxy->__delitem__(self->__ss_object);'
    print >>gv.out, '}\n'

    # getset
    for var in vars:
        print >>gv.out, 'PyObject *__ss_get_%s_%s(%sObject *self, void *closure) {' % (cl.ident, var.name, cl.ident)
        print >>gv.out, '    PyObject *p = __to_py(self->__ss_object->%s);' % gv.cpp_name(var.name)
        print >>gv.out, '    Py_INCREF(p);'
        print >>gv.out, '    return p;'
        print >>gv.out, '}\n'

        print >>gv.out, 'int __ss_set_%s_%s(%sObject *self, PyObject *value, void *closure) {' % (cl.ident, var.name, cl.ident)
        print >>gv.out, '    try {'
        typ = cpp.typesetreprnew(var, var.parent)
        if typ == 'void *': # XXX investigate
            print >>gv.out, '        self->__ss_object->%s = NULL;' % gv.cpp_name(var.name)
        else:
            print >>gv.out, '        self->__ss_object->%s = __to_ss<%s>(value);' % (gv.cpp_name(var.name), typ)
        print >>gv.out, '    } catch (Exception *e) {'
        print >>gv.out, '        PyErr_SetString(__to_py(e), ((e->msg)?(e->msg->unit.c_str()):""));'
        print >>gv.out, '        return -1;'
        print >>gv.out, '    }'

        print >>gv.out, '    return 0;'
        print >>gv.out, '}\n'

    print >>gv.out, 'PyGetSetDef %sGetSet[] = {' % cl.ident
    for var in vars:
        print >>gv.out, '    {(char *)"%s", (getter)__ss_get_%s_%s, (setter)__ss_set_%s_%s, (char *)"", NULL},' % (var.name, cl.ident, var.name, cl.ident, var.name)
    print >>gv.out, '    {NULL}\n};\n'

    # python type
    print >>gv.out, 'static PyTypeObject %sObjectType = {' % cl.ident
    print >>gv.out, '    PyObject_HEAD_INIT(NULL)'
    print >>gv.out, '    0,              /* ob_size           */'
    print >>gv.out, '    "%s.%s",        /* tp_name           */' % (cl.module.ident, cl.ident)
    print >>gv.out, '    sizeof(%sObject), /* tp_basicsize      */' % cl.ident
    print >>gv.out, '    0,              /* tp_itemsize       */'
    print >>gv.out, '    (destructor)%sDealloc, /* tp_dealloc        */' % cl.ident
    print >>gv.out, '    0,              /* tp_print          */'
    print >>gv.out, '    0,              /* tp_getattr        */'
    print >>gv.out, '    0,              /* tp_setattr        */'
    print >>gv.out, '    0,              /* tp_compare        */'
    if hasmethod(cl, '__repr__'):
        print >>gv.out, '    (PyObject *(*)(PyObject *))%s___repr__, /* tp_repr           */' % cl.ident
    else:
        print >>gv.out, '    0,              /* tp_repr           */'
    print >>gv.out, '    &%s_as_number,  /* tp_as_number      */' % cl.ident
    print >>gv.out, '    0,              /* tp_as_sequence    */'
    print >>gv.out, '    0,              /* tp_as_mapping     */'
    print >>gv.out, '    0,              /* tp_hash           */'
    print >>gv.out, '    0,              /* tp_call           */'
    if hasmethod(cl, '__str__'):
        print >>gv.out, '    (PyObject *(*)(PyObject *))%s___str__, /* tp_str           */' % cl.ident
    else:
        print >>gv.out, '    0,              /* tp_str            */'
    print >>gv.out, '    0,              /* tp_getattro       */'
    print >>gv.out, '    0,              /* tp_setattro       */'
    print >>gv.out, '    0,              /* tp_as_buffer      */'
    print >>gv.out, '    Py_TPFLAGS_DEFAULT, /* tp_flags          */'
    print >>gv.out, '    0,              /* tp_doc            */'
    print >>gv.out, '    0,              /* tp_traverse       */'
    print >>gv.out, '    0,              /* tp_clear          */'
    print >>gv.out, '    0,              /* tp_richcompare    */'
    print >>gv.out, '    0,              /* tp_weaklistoffset */'
    print >>gv.out, '    0,              /* tp_iter           */'
    print >>gv.out, '    0,              /* tp_iternext       */'
    print >>gv.out, '    %sMethods,      /* tp_methods        */' % cl.ident
    print >>gv.out, '    %sMembers,      /* tp_members        */' % cl.ident
    print >>gv.out, '    %sGetSet,       /* tp_getset         */' % cl.ident
    if cl.bases and not cl.bases[0].ident == 'object':
        print >>gv.out, '    &%sObjectType,              /* tp_base           */' % cl.bases[0].ident
    else:
        print >>gv.out, '    0,              /* tp_base           */'
    print >>gv.out, '    0,              /* tp_dict           */'
    print >>gv.out, '    0,              /* tp_descr_get      */'
    print >>gv.out, '    0,              /* tp_descr_set      */'
    print >>gv.out, '    0,              /* tp_dictoffset     */'
    if hasmethod(cl, '__init__') and cl.funcs['__init__'] in funcs:
        print >>gv.out, '    %s___tpinit__, /* tp_init           */' % cl.ident
    else:
        print >>gv.out, '    0,              /* tp_init           */'
    print >>gv.out, '    0,              /* tp_alloc          */'
    print >>gv.out, '    %sNew,          /* tp_new            */' % cl.ident
    print >>gv.out, '};\n'
    do_reduce_setstate(gv, cl, vars)
    for n in cl.module.mod_path:
        print >>gv.out, '} // namespace __%s__' % n
    print >>gv.out

def do_reduce_setstate(gv, cl, vars):
    print >>gv.out, 'PyObject *%s__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {' % cl.ident
    print >>gv.out, '    PyObject *t = PyTuple_New(3);'
    print >>gv.out, '    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_%s, "__newobj__"));' % '_'.join(gv.module.mod_path)
    print >>gv.out, '    PyObject *a = PyTuple_New(1);'
    print >>gv.out, '    PyTuple_SetItem(a, 0, (PyObject *)&%sObjectType);' % cl.ident
    print >>gv.out, '    PyTuple_SetItem(t, 1, a);'
    print >>gv.out, '    PyObject *b = PyTuple_New(2);'
    for i, var in enumerate(vars):
        print >>gv.out, '    PyTuple_SetItem(b, %d, __to_py(((%sObject *)self)->__ss_object->%s));' % (i, cl.ident, gv.cpp_name(var.name))
    print >>gv.out, '    PyTuple_SetItem(t, 2, b);'
    print >>gv.out, '    return t;'
    print >>gv.out, '}\n'
    print >>gv.out, 'PyObject *%s__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {' % cl.ident
    print >>gv.out, '    int l = PyTuple_Size(args);'
    print >>gv.out, '    PyObject *state = PyTuple_GetItem(args, 0);'
    for i, var in enumerate(vars):
        vartype = cpp.typesetreprnew(var, var.parent)
        print >>gv.out, '    ((%sObject *)self)->__ss_object->%s = __to_ss<%s>(PyTuple_GetItem(state, %d));' % (cl.ident, gv.cpp_name(var.name), vartype, i)
    print >>gv.out, '    return Py_None;'
    print >>gv.out, '}\n'

def convert_methods(gv, cl, declare):
    if declare:
        print >>gv.out, '    PyObject *__to_py__();'
    else:
        for n in cl.module.mod_path:
            print >>gv.out, 'namespace __%s__ { /* XXX */' % n
        print >>gv.out

        print >>gv.out, 'PyObject *%s::__to_py__() {' % cpp.nokeywords(cl.ident)
        print >>gv.out, '    if(__ss_proxy->has_key(this))'
        print >>gv.out, '        return (PyObject *)(__ss_proxy->__getitem__(this));'
        print >>gv.out, '    %sObject *self = (%sObject *)(%sObjectType.tp_alloc(&%sObjectType, 0));' % (4*(cl.ident,))
        print >>gv.out, '    self->__ss_object = this;'
        print >>gv.out, '    __ss_proxy->__setitem__(self->__ss_object, self);'
        print >>gv.out, '    return (PyObject *)self;'
        print >>gv.out, '}\n'

        for n in cl.module.mod_path:
            print >>gv.out, '} // module namespace'
        print >>gv.out

        print >>gv.out, 'namespace __shedskin__ { /* XXX */\n'

        print >>gv.out, 'template<> %s::%s *__to_ss(PyObject *p) {' % (cl.module.full_path(), cpp.nokeywords(cl.ident))
        print >>gv.out, '    if(p == Py_None) return NULL;'
        print >>gv.out, '    if(PyObject_IsInstance(p, (PyObject *)&%s::%sObjectType)!=1)' % (cl.module.full_path(), cl.ident)
        print >>gv.out, '        throw new TypeError(new str("error in conversion to Shed Skin (%s expected)"));' % cl.ident
        print >>gv.out, '    return ((%s::%sObject *)p)->__ss_object;' % (cl.module.full_path(), cl.ident)
        print >>gv.out, '}\n}'

def pyinit_func(gv):
    for what in ('init', 'add'):
        print >>gv.out, 'PyMODINIT_FUNC %s%s(void);\n' % (what, '_'.join(gv.module.mod_path))
 
def convert_methods2(gv):
    print >>gv.out, 'namespace __shedskin__ { /* XXX */\n'
    for cl in exported_classes(gv):
        print >>gv.out, 'template<> %s::%s *__to_ss(PyObject *p);' % (cl.module.full_path(), cpp.nokeywords(cl.ident))
    print >>gv.out, '}'
