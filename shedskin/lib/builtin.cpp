#include "builtin.hpp"
#include "re.hpp"
#include <climits>
#include <cmath>
#include <numeric>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <limits.h>

namespace __shedskin__ {


class_ *cl_class_, *cl_none, *cl_str_, *cl_int_, *cl_bool, *cl_float_, *cl_complex, *cl_list, *cl_tuple, *cl_dict, *cl_set, *cl_object, *cl_rangeiter, *cl_xrange;

class_ *cl_stopiteration, *cl_assertionerror, *cl_eoferror, *cl_floatingpointerror, *cl_keyerror, *cl_indexerror, *cl_typeerror, *cl_ioerror, *cl_valueerror, *cl_zerodivisionerror, *cl_keyboardinterrupt, *cl_memoryerror, *cl_nameerror, *cl_notimplementederror, *cl_oserror, *cl_overflowerror, *cl_runtimeerror, *cl_syntaxerror, *cl_systemerror, *cl_systemexit;

str *sp, *nl, *__fmt_s, *__fmt_H, *__fmt_d;
__GC_STRING ws, __fmtchars;
__GC_VECTOR(str *) __char_cache;

__ss_bool True;
__ss_bool False;

list<str *> *__join_cache, *__mod5_cache;
list<pyobj *> *__print_cache;

char __str_cache[4000];

file *__ss_stdin, *__ss_stdout, *__ss_stderr;

#ifdef __SS_BIND
dict<void *, void *> *__ss_proxy;
#endif

void __init() {
    GC_INIT();
#ifdef __SS_BIND
#ifndef __SS_PYPY
    Py_Initialize();
#endif
    __ss_proxy = new dict<void *, void *>();
#endif

    cl_class_ = new class_ ("class", 0, 0);
    cl_none = new class_("None", 1, 1);
    cl_str_ = new class_("str", 2, 2);
    cl_int_ = new class_("int", 3, 3);
    cl_float_ = new class_("float", 4, 4);
    cl_list = new class_("list", 5, 5);
    cl_tuple = new class_("tuple", 6, 6);
    cl_dict = new class_("dict", 7, 7);
    cl_set = new class_("set", 8, 8);
    cl_object = new class_("object", 9, 9);
    cl_rangeiter = new class_("rangeiter", 10, 10);
    cl_complex = new class_("complex", 11, 11);
    cl_xrange = new class_("xrange", 12, 12);

    True.value = 1;
    False.value = 0;

    ws = " \n\r\t\f\v";
    __fmtchars = "#*-+ .0123456789hlL";
    sp = new str(" ");
    nl = new str("\n");
    __fmt_s = new str("%s");
    __fmt_H = new str("%H");
    __fmt_d = new str("%d");

    for(int i=0;i<256;i++) {
        char c = i;
        str *charstr = new str(&c, 1);
        charstr->charcache = 1;
        __char_cache.push_back(charstr);
    }

    __join_cache = new list<str *>();
    __print_cache = new list<pyobj *>();
    __mod5_cache = new list<str *>();

    for(int i=0; i<1000; i++) {
        __str_cache[4*i] = '0' + (i % 10);
        __str_cache[4*i+1] = '0' + ((i/10) % 10);
        __str_cache[4*i+2] = '0' + ((i/100) % 10);
    }

    __ss_stdin = new file(stdin);
    __ss_stdin->name = new str("<stdin>");
    __ss_stdout = new file(stdout);
    __ss_stdout->name = new str("<stdout>");
    __ss_stderr = new file(stderr);
    __ss_stderr->name = new str("<stderr>");

    cl_stopiteration = new class_("StopIteration", 13, 13);
    cl_assertionerror = new class_("AssertionError", 14, 14);
    cl_eoferror = new class_("EOFError", 15, 15);
    cl_floatingpointerror = new class_("FloatingPointError", 16, 16);
    cl_keyerror = new class_("KeyError", 17, 17);
    cl_indexerror = new class_("IndexError", 18, 18);
    cl_typeerror = new class_("TypeError", 19, 19);
    cl_ioerror = new class_("IOError", 20, 20);
    cl_valueerror = new class_("ValueError", 21, 21);
    cl_zerodivisionerror = new class_("ZeroDivisionError", 22, 22);
    cl_keyboardinterrupt = new class_("KeyboardInterrupt", 23, 23);
    cl_memoryerror = new class_("MemoryError", 24, 24);
    cl_nameerror = new class_("NameError", 25, 25);
    cl_notimplementederror = new class_("NotImplementedError", 26, 26);
    cl_oserror = new class_("OSError", 27, 27);
    cl_overflowerror = new class_("OverflowError", 28, 28);
    cl_runtimeerror = new class_("RuntimeError", 29, 29);
    cl_syntaxerror = new class_("SyntaxError", 30, 30);
    cl_systemerror = new class_("SystemError", 31, 31);
    cl_systemexit = new class_("SystemExit", 32, 32);

}

class_::class_(const char *name, int low, int high) {
    this->__name__ = new str(name);
    this->low = low; this->high = high;
}

str *class_::__repr__() {
    return (new str("class "))->__add__(__name__);
}

__ss_bool class_::__eq__(pyobj *c) {
    return __mbool(c == this);
}

#include "builtin/file.cpp"
#include "builtin/math.cpp"
#include "builtin/bool.cpp"
#include "builtin/complex.cpp"
#include "builtin/str.cpp"
#include "builtin/exception.cpp"
#include "builtin/function.cpp"
#include "builtin/format.cpp"


void __add_missing_newline() {
    if(__ss_stdout->options.lastchar != '\n')
        __ss_stdout->write(new str("\n"));
}

/* print traceback for uncaught exception, may only work for GCC */

void terminate_handler() {
    int code = 0;

    static bool terminating = false;
    if(terminating)
        abort();

    terminating = true;
    try
    {
        // rethrow to detect uncaught exception, will recursively
        // call terminate() if no exception is active (which is
        // detected above).
        throw;

    } catch (SystemExit *s) {
        __add_missing_newline();
        if(s->code)
            print2(NULL, 0, 1, s->message);
        code = s->code;

    } catch (BaseException *e) {
        __add_missing_newline();

#ifndef WIN32
#ifdef __SS_BACKTRACE
        print_traceback(stdout);
#endif
#endif

        str *s = __str(e);
        if(___bool(s))
            print2(NULL, 0, 1, __add_strs(3, e->__class__->__name__, new str(": "), s));
        else
            print2(NULL, 0, 1, e->__class__->__name__);
        code = 1;
    }

    std::exit(code);
}

/* starting and stopping */

void __start(void (*initfunc)()) {
    std::set_terminate(terminate_handler);
    initfunc();
    std::exit(0);
}

void __ss_exit(int code) {
    throw new SystemExit(code);
}

/* glue */

#ifdef __SS_BIND
#ifdef __SS_LONG
template<> PyObject *__to_py(__ss_int i) { return PyLong_FromLongLong(i); }
#endif
template<> PyObject *__to_py(int i) { return PyInt_FromLong(i); }
template<> PyObject *__to_py(__ss_bool i) { return PyBool_FromLong(i.value); }
template<> PyObject *__to_py(double d) { return PyFloat_FromDouble(d); }
template<> PyObject *__to_py(void *v) { Py_INCREF(Py_None); return Py_None; }

#ifdef __SS_LONG
template<> __ss_int __to_ss(PyObject *p) {
    if(PyLong_Check(p))
        return PyLong_AsLongLong(p);
    else if (PyInt_Check(p))
        return PyInt_AsLong(p);
    else
        throw new TypeError(new str("error in conversion to Shed Skin (integer expected)"));
}
#endif

template<> int __to_ss(PyObject *p) {
    if(!PyInt_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (integer expected)"));
    return PyInt_AsLong(p);
}

template<> __ss_bool __to_ss(PyObject *p) {
    if(!PyBool_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (boolean expected)"));
    return (p==Py_True)?(__mbool(true)):(__mbool(false));
}

template<> double __to_ss(PyObject *p) {
    if(!PyInt_Check(p) and !PyFloat_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (float or int expected)"));
    return PyFloat_AsDouble(p);
}

template<> void * __to_ss(PyObject *p) {
    if(p!=Py_None)
        throw new TypeError(new str("error in conversion to Shed Skin (None expected)"));
    return NULL;
}
#endif

template <> void *myallocate<__ss_int>(int n) { return GC_MALLOC_ATOMIC(n); }
template <> void *myallocate<__ss_int, __ss_int>(int n) { return GC_MALLOC_ATOMIC(n); }

template<> int __none() { throw new TypeError(new str("mixing None with int")); }
template<> double __none() { throw new TypeError(new str("mixing None with float")); }

list<tuple2<void *, void *> *> *__zip(int) {
    return new list<tuple2<void *, void *> *>();
}

/* pyobj */

str *pyobj::__str__() { return __repr__(); }

str *pyobj::__repr__() {
    return __add_strs(3, new str("<"), __class__->__name__, new str(" instance>"));
}

long pyobj::__hash__() {
    return (intptr_t)this;
}

__ss_int pyobj::__cmp__(pyobj *p) {
    return __cmp<void *>(this, p);
}

__ss_bool pyobj::__eq__(pyobj *p) { return __mbool(this == p); }
__ss_bool pyobj::__ne__(pyobj *p) { return __mbool(!__eq__(p)); }

__ss_bool pyobj::__gt__(pyobj *p) { return __mbool(__cmp__(p) == 1); }
__ss_bool pyobj::__lt__(pyobj *p) { return __mbool(__cmp__(p) == -1); }
__ss_bool pyobj::__ge__(pyobj *p) { return __mbool(__cmp__(p) != -1); }
__ss_bool pyobj::__le__(pyobj *p) { return __mbool(__cmp__(p) != 1); }

pyobj *pyobj::__copy__() { return this; }
pyobj *pyobj::__deepcopy__(dict<void *, pyobj *> *) { return this; }

__ss_int pyobj::__len__() { return 1; } /* XXX exceptions? */
__ss_int pyobj::__int__() { return 0; }

__ss_bool pyobj::__nonzero__() { return __mbool(__len__() != 0); }

__ss_int pyobj::__index__() { throw new TypeError(new str("no such method: '__index__'")); }

/* object */

object::object() { this->__class__ = cl_object; }

#ifdef __SS_BIND
PyObject *__ss__newobj__(PyObject *, PyObject *args, PyObject *kwargs) {
    PyObject *cls = PyTuple_GetItem(args, 0);
    PyObject *__new__ = PyObject_GetAttrString(cls, "__new__");
    return PyObject_Call(__new__, args, kwargs);
}
#endif

} // namespace __shedskin__
