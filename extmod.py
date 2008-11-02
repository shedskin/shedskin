'''
*** SHED SKIN Python-to-C++ Compiler 0.0.29 ***
Copyright 2005-2008 Mark Dufour; License GNU GPL version 3 (See LICENSE)

extmod.py: extension module support

'''

from shared import *
import cpp

def do_extmod(gv):
    print >>gv.out, '/* extension module glue */\n'
    print >>gv.out, 'extern "C" {'
    print >>gv.out, '#include <Python.h>'
    print >>gv.out, '#include <structmember.h>\n'

    if getgx().extmod_classes:
        for cl in gv.module.classes.values(): 
            do_extmod_class(gv, cl)

    print >>gv.out, '/* global functions */\n'

    # --- select functions that are called and have copyable arg/return types
    funcs = [] 
    for func in gv.module.funcs.values():
        if not cpp.hmcpa(func): # not called
            continue 
        builtins = True
        for formal in func.formals:
            try:
                cpp.typesetreprnew(func.vars[formal], func, check_extmod=True)
                cpp.typesetreprnew(func.retnode.thing, func, check_extmod=True)
            except cpp.ExtmodError:
                builtins = False
        if builtins:
            funcs.append(func)

    # --- for each selected function, output glue code
    for func in funcs:
        do_extmod_method(gv, func)
    do_extmod_methoddef(gv, gv.module.ident, funcs)

    # --- module init function
    print >>gv.out, 'PyMODINIT_FUNC init%s(void) {' % gv.module.ident

    # initialize variables
    vars = []
    for (name,var) in getmv().globals.items():
        if cpp.singletype(var, module) or var.invisible: # XXX merge declaredefs 
            continue
        typehu = cpp.typesetreprnew(var, var.parent)
        # void *
        if not typehu or not var.types(): continue 
        if name.startswith('__'): continue

        try:
            cpp.typesetreprnew(var, var.parent, check_extmod=True)
        except cpp.ExtmodError:
            continue

        vars.append(var)

    for var in vars:
        print >>gv.out, '    __'+gv.module.ident+'__::'+gv.cpp_name(var.name)+' = 0;'
    if vars: print >>gv.out

    # initialize modules
    gv.do_init_modules()
    print >>gv.out, '\n    PyObject *mod = Py_InitModule((char *)"%s", %sMethods);' % (gv.module.ident, gv.module.ident)
    print >>gv.out, '    if(!mod)'
    print >>gv.out, '        return;\n'

    # add variables to module
    for var in vars:
        varname = gv.cpp_name(var.name)
        if [1 for t in gv.mergeinh[var] if t[0].ident in ['int_', 'float_']]:
            print >>gv.out, '    PyModule_AddObject(mod, (char *)"%(name)s", __to_py(%(var)s));' % {'name' : var.name, 'var': '__'+gv.module.ident+'__::'+varname}
        else:
            print >>gv.out, '    if(%(var)s) PyModule_AddObject(mod, (char *)"%(name)s", __to_py(%(var)s));' % {'name' : var.name, 'var': '__'+gv.module.ident+'__::'+varname}

    # add types to module
    if getgx().extmod_classes:
        for cl in gv.module.classes.values(): 
            print >>gv.out, '    %sObjectType.tp_new = PyType_GenericNew;' % cl.ident
            print >>gv.out, '    if (PyType_Ready(&%sObjectType) < 0)' % cl.ident
            print >>gv.out, '        return;\n'
            print >>gv.out, '    PyModule_AddObject(mod, "%s", (PyObject *)&%sObjectType);' % (cl.ident, cl.ident)

    print >>gv.out, '\n}'
    print >>gv.out, '\n} // extern "C"'

def do_extmod_methoddef(gv, ident, funcs):
    print >>gv.out, 'static PyMethodDef %sMethods[] = {' % ident
    for func in funcs:
        print >>gv.out, '    {(char *)"%(id)s", %(id2)s, METH_VARARGS, (char *)""},' % {'id': func.ident, 'id2': gv.cpp_name(func.ident)}
    print >>gv.out, '    {NULL}\n};\n'

def do_extmod_method(gv, func):
    is_method = isinstance(func.parent, class_)
    if is_method: formals = func.formals[1:]
    else: formals = func.formals

    print >>gv.out, 'PyObject *%s(PyObject *self, PyObject *args) {' % gv.cpp_name(func.ident)
    print >>gv.out, '    if(PyTuple_Size(args) < %d || PyTuple_Size(args) > %d) {' % (len(formals)-len(func.defaults), len(formals))
    print >>gv.out, '        PyErr_SetString(PyExc_Exception, "invalid number of arguments");'
    print >>gv.out, '        return 0;'
    print >>gv.out, '    }\n' 
    print >>gv.out, '    try {'

    if is_method:
        print >>gv.out, '        %(type)s_self = __to_ss<%(type)s>(self);' % {'type' : '__%s__::'%gv.module.ident+cpp.typesetreprnew(func.vars[func.formals[0]], func)}

    # convert [self,] args 
    for i, formal in enumerate(formals):
        gv.start('')
        gv.append('        %(type)sarg_%(num)d = (PyTuple_Size(args) > %(num)d) ? __to_ss<%(type)s>(PyTuple_GetItem(args, %(num)d)) : ' % {'type' : cpp.typesetreprnew(func.vars[formal], func), 'num' : i})
        if i >= len(formals)-len(func.defaults):
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
        else:
            gv.append('0')
        gv.eol()
    print >>gv.out

    # call 
    if is_method: where = '_self->'
    else: where = '__'+gv.module.ident+'__::'
    print >>gv.out, '        return __to_py('+where+gv.cpp_name(func.ident)+'('+', '.join(['arg_%d' % i for i in range(len(formals))])+'));\n' 

    # convert exceptions
    print >>gv.out, '    } catch (Exception *e) {'
    print >>gv.out, '        PyErr_SetString(__to_py(e), e->msg->unit.c_str());'
    print >>gv.out, '        return 0;'
    print >>gv.out, '    }'
    print >>gv.out, '}\n'

def do_extmod_class(gv, cl):
    # determine methods, vars to expose XXX merge
    funcs = []
    vars = []
    for func in cl.funcs.values():
        if cpp.hmcpa(func) and not func.ident in ['__setattr__', '__getattr__']:
            funcs.append(func)
    for var in cl.vars.values():
         if var.invisible: continue
         if var in getgx().merged_inh and getgx().merged_inh[var]:
             vars.append(var)

    print >>gv.out, '/* class %s */\n' % cl.ident

    # python object 
    print >>gv.out, 'typedef struct {'
    print >>gv.out, '    PyObject_HEAD'
    for var in vars:
        print >>gv.out, '    PyObject *%s;' % gv.cpp_name(var.name)
    print >>gv.out, '} %sObject;\n' % cl.ident

    # attributes
    print >>gv.out, 'static PyMemberDef %sMembers[] = {' % cl.ident
    for var in vars:
        print >>gv.out, '    {(char *)"%s", T_OBJECT_EX, offsetof(%sObject, %s), 0, (char *)""},' % (var.name, cl.cpp_name, gv.cpp_name(var.name))
    print >>gv.out, '    {NULL}\n};\n'

    # methods
    for func in funcs:
        do_extmod_method(gv, func)
    do_extmod_methoddef(gv, cl.ident, funcs)

    # python type
    print >>gv.out, 'static PyTypeObject %sObjectType = {' % cl.ident
    print >>gv.out, '    PyObject_HEAD_INIT(NULL)'
    print >>gv.out, '    0,              /* ob_size           */'
    print >>gv.out, '    "%s.%s",            /* tp_name           */' % (cl.module.ident, cl.ident)
    print >>gv.out, '    sizeof(%sObject),     /* tp_basicsize      */' % cl.ident
    print >>gv.out, '    0,              /* tp_itemsize       */'
    print >>gv.out, '    0,              /* tp_dealloc        */'
    print >>gv.out, '    0,              /* tp_print          */'
    print >>gv.out, '    0,              /* tp_getattr        */'
    print >>gv.out, '    0,              /* tp_setattr        */'
    print >>gv.out, '    0,              /* tp_compare        */'
    print >>gv.out, '    0,              /* tp_repr           */'
    print >>gv.out, '    0,              /* tp_as_number      */'
    print >>gv.out, '    0,              /* tp_as_sequence    */'
    print >>gv.out, '    0,              /* tp_as_mapping     */'
    print >>gv.out, '    0,              /* tp_hash           */'
    print >>gv.out, '    0,              /* tp_call           */'
    print >>gv.out, '    0,              /* tp_str            */'
    print >>gv.out, '    0,              /* tp_getattro       */'
    print >>gv.out, '    0,              /* tp_setattro       */'
    print >>gv.out, '    0,              /* tp_as_buffer      */'
    print >>gv.out, '    Py_TPFLAGS_DEFAULT,     /* tp_flags          */'
    print >>gv.out, '    0,              /* tp_doc            */'
    print >>gv.out, '    0,              /* tp_traverse       */'
    print >>gv.out, '    0,              /* tp_clear          */'
    print >>gv.out, '    0,              /* tp_richcompare    */'
    print >>gv.out, '    0,              /* tp_weaklistoffset */'
    print >>gv.out, '    0,              /* tp_iter           */'
    print >>gv.out, '    0,              /* tp_iternext       */'
    print >>gv.out, '    %sMethods,               /* tp_methods        */' % cl.ident
    print >>gv.out, '    %sMembers,           /* tp_members        */' % cl.ident
    print >>gv.out, '};\n'

def convert_methods(gv, cl, declare):
    if declare:
        print >>gv.out, '#ifdef __SS_BIND'
        print >>gv.out, '    %s(PyObject *);' % cl.cpp_name
        print >>gv.out, '    PyObject *__to_py__();' 
        print >>gv.out, '#endif'
    else:
        print >>gv.out, '#ifdef __SS_BIND'
        print >>gv.out, '%s::%s(PyObject *) {' % (cl.cpp_name, cl.cpp_name)
        print >>gv.out, '}\n'
        print >>gv.out, 'PyObject *%s::__to_py__() {' % cl.cpp_name
        print >>gv.out, '    return Py_None;'
        print >>gv.out, '}\n'
        print >>gv.out, '#endif'

