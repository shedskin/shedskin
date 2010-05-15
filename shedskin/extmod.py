'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2009 Mark Dufour; License GNU GPL version 3 (See LICENSE)

extmod.py: extension module support

'''

from shared import *
import cpp

def do_extmod(gv):
    print >>gv.out, '/* extension module glue */\n'
    print >>gv.out, 'extern "C" {'
    print >>gv.out, '#include <Python.h>'
    print >>gv.out, '#include <structmember.h>\n'
    print >>gv.out, 'namespace __%s__ { /* XXX */\n' % gv.module.ident

    # filter out unsupported stuff
    classes = gv.module.classes.values()
    funcs = supported_funcs(gv, gv.module.funcs.values())
    vars = supported_vars(getmv().globals.values())

    # classes
    for cl in classes:
        do_extmod_class(gv, cl)

    # global functions
    print >>gv.out, '/* global functions */\n'
    for func in funcs:
        do_extmod_method(gv, func)
    do_extmod_methoddef(gv, 'Global_'+gv.module.ident, funcs)

    # module init function
    print >>gv.out, 'PyMODINIT_FUNC init%s(void) {' % gv.module.ident

    # initialize modules
    gv.do_init_modules()
    print >>gv.out, '    __'+gv.module.ident+'__::__init();'
    print >>gv.out, '\n    PyObject *mod = Py_InitModule((char *)"%s", Global_%sMethods);' % (gv.module.ident, gv.module.ident)
    print >>gv.out, '    if(!mod)'
    print >>gv.out, '        return;\n'

    # add types to module
    for cl in classes:
        print >>gv.out, '    if (PyType_Ready(&%sObjectType) < 0)' % cl.ident
        print >>gv.out, '        return;\n'
        print >>gv.out, '    PyModule_AddObject(mod, "%s", (PyObject *)&%sObjectType);' % (cl.ident, cl.ident)
    print >>gv.out

    # global variables
    for var in vars:
        varname = gv.cpp_name(var.name)
        if [1 for t in gv.mergeinh[var] if t[0].ident in ['int_', 'float_', 'bool_']]:
            print >>gv.out, '    PyModule_AddObject(mod, (char *)"%(name)s", __to_py(%(var)s));' % {'name' : var.name, 'var': '__'+gv.module.ident+'__::'+varname}
        else:
            print >>gv.out, '    PyModule_AddObject(mod, (char *)"%(name)s", __to_py(%(var)s));' % {'name' : var.name, 'var': '__'+gv.module.ident+'__::'+varname}

    print >>gv.out, '\n}'
    print >>gv.out, '\n} // namespace __%s__' % gv.module.ident
    print >>gv.out, '\n} // extern "C"'

    # conversion methods to/from CPython/Shedskin
    for cl in classes:
        convert_methods(gv, cl, False)

def do_extmod_methoddef(gv, ident, funcs):
    print >>gv.out, 'static PyMethodDef %sMethods[] = {' % ident
    for func in funcs:
        if isinstance(func.parent, class_): id = func.parent.ident+'_'+func.ident
        else: id = 'Global_'+func.ident
        print >>gv.out, '    {(char *)"%(id)s", (PyCFunction)%(id2)s, METH_VARARGS | METH_KEYWORDS, (char *)""},' % {'id': func.ident, 'id2': id}
    print >>gv.out, '    {NULL}\n};\n'

def do_extmod_method(gv, func):
    is_method = isinstance(func.parent, class_)
    if is_method: formals = func.formals[1:]
    else: formals = func.formals

    if isinstance(func.parent, class_): id = func.parent.ident+'_'+func.ident # XXX
    else: id = 'Global_'+func.ident # XXX
    print >>gv.out, 'PyObject *%s(PyObject *self, PyObject *args, PyObject *kwargs) {' % id
    print >>gv.out, '    try {'

    for i, formal in enumerate(formals):
        gv.start('')
        typ = cpp.typesetreprnew(func.vars[formal], func)
        cls = [t[0] for t in gv.mergeinh[func.vars[formal]] if isinstance(t[0], class_)]
        cls = [c for c in cls if c.mv.module == getgx().main_module]
        if cls:
            typ = ('__%s__::' % cls[0].mv.module.ident)+typ
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
    # determine methods, vars to expose
    funcs = supported_funcs(gv, cl.funcs.values())
    vars = supported_vars(cl.vars.values())

    # python object
    print >>gv.out, '/* class %s */\n' % cl.ident
    print >>gv.out, 'typedef struct {'
    print >>gv.out, '    PyObject_HEAD'
    print >>gv.out, '    __%s__::%s *__ss_object;' % (gv.module.ident, cl.ident)
    print >>gv.out, '} %sObject;\n' % cl.ident
    print >>gv.out, 'static PyMemberDef %sMembers[] = {' % cl.ident
    print >>gv.out, '    {NULL}\n};\n'

    # methods
    for func in funcs:
        do_extmod_method(gv, func)
    do_extmod_methoddef(gv, cl.ident, funcs)

    # tp_new
    print >>gv.out, 'PyObject *%sNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {' % cl.ident
    print >>gv.out, '    %sObject *self = (%sObject *)type->tp_alloc(type, 0);' % (cl.ident, cl.ident)
    print >>gv.out, '    self->__ss_object = new __%s__::%s();' % (gv.module.ident, cl.ident)
    print >>gv.out, '    __ss_proxy->__setitem__(self->__ss_object, self);'
    if hasmethod(cl, '__init__'):
        print >>gv.out, '    if(%s___init__((PyObject *)self, args, kwargs) == 0)' % cl.ident
        print >>gv.out, '        return 0;'
    print >>gv.out, '    return (PyObject *)self;'
    print >>gv.out, '}\n'

    # dealloc
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
    print >>gv.out, '    0,              /* tp_as_number      */'
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
    print >>gv.out, '    0,              /* tp_base           */'
    print >>gv.out, '    0,              /* tp_dict           */'
    print >>gv.out, '    0,              /* tp_descr_get      */'
    print >>gv.out, '    0,              /* tp_descr_set      */'
    print >>gv.out, '    0,              /* tp_dictoffset     */'
    print >>gv.out, '    0,              /* tp_init           */'
    print >>gv.out, '    0,              /* tp_alloc          */'
    print >>gv.out, '    %sNew,          /* tp_new            */' % cl.ident
    print >>gv.out, '};\n'

def convert_methods(gv, cl, declare):
    if declare:
        print >>gv.out, '#ifdef __SS_BIND'
        print >>gv.out, '    PyObject *__to_py__();'
        print >>gv.out, '#endif'
    else:
        print >>gv.out, '#ifdef __SS_BIND'
        print >>gv.out, 'namespace __%s__ { /* XXX */\n' % gv.module.ident

        print >>gv.out, 'PyObject *%s::__to_py__() {' % cl.cpp_name
        print >>gv.out, '    if(__ss_proxy->has_key(this))'
        print >>gv.out, '        return (PyObject *)(__ss_proxy->__getitem__(this));'
        print >>gv.out, '    %sObject *self = (%sObject *)(%sObjectType.tp_alloc(&%sObjectType, 0));' % (4*(cl.ident,))
        print >>gv.out, '    self->__ss_object = this;'
        print >>gv.out, '    __ss_proxy->__setitem__(self->__ss_object, self);'
        print >>gv.out, '    return (PyObject *)self;'
        print >>gv.out, '}\n}\n'

        print >>gv.out, 'namespace __shedskin__ { /* XXX */\n'

        print >>gv.out, 'template<> __%s__::%s *__to_ss(PyObject *p) {' % (gv.module.ident, cl.cpp_name)
        print >>gv.out, '    if(p == Py_None) return NULL;'
        print >>gv.out, '    if(p->ob_type != &__%s__::%sObjectType)' % (gv.module.ident, cl.ident)
        print >>gv.out, '        throw new TypeError(new str("error in conversion to Shed Skin (%s expected)"));' % cl.ident
        print >>gv.out, '    return ((__%s__::%sObject *)p)->__ss_object;' % (gv.module.ident, cl.ident)
        print >>gv.out, '}\n}'
        print >>gv.out, '#endif'

def convert_methods2(gv, classes):
    print >>gv.out, 'namespace __shedskin__ { /* XXX */\n'
    for cl in classes:
        print >>gv.out, 'template<> __%s__::%s *__to_ss(PyObject *p);' % (gv.module.ident, cl.cpp_name)
    print >>gv.out, '}'
