/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* extmod glue */

#ifdef __SS_BIND
template<class T> T __to_ss(PyObject *p) {
    if(p==Py_None) return (T)NULL;
    return new (typename dereference<T>::type)(p); /* isn't C++ pretty :-) */
}

template<> __ss_int __to_ss(PyObject *p);
template<> __ss_bool __to_ss(PyObject *p);
template<> __ss_float __to_ss(PyObject *p);
template<> void *__to_ss(PyObject *p);

template<class T> PyObject *__to_py(T t) {
    if(!t) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return t->__to_py__();
}

template<> PyObject *__to_py(int32_t i);
template<> PyObject *__to_py(int64_t i);
#ifdef __SS_INT128
template<> PyObject *__to_py(__int128 i);
#endif
#ifdef WIN32
template<> PyObject *__to_py(long i);
#endif
#ifdef __APPLE__
template<> PyObject *__to_py(long i);
#endif
template<> PyObject *__to_py(__ss_bool i);
template<> PyObject *__to_py(__ss_float i);
template<> PyObject *__to_py(void *);

extern dict<void *, void *> *__ss_proxy;
#endif

/* binding args */

#ifdef __SS_BIND
template<class T> T __ss_arg(const char *name, int pos, int has_default, T default_value, PyObject *args, PyObject *kwargs) {
    PyObject *kwarg;
    Py_ssize_t nrofargs = PyTuple_Size(args);
    if (pos < (int)nrofargs)
        return __to_ss<T>(PyTuple_GetItem(args, pos));
    else if (kwargs && (kwarg = PyDict_GetItemString(kwargs, name)))
        return __to_ss<T>(kwarg);
    else if (has_default)
        return default_value;
    else
        throw new TypeError(new str("missing argument"));
}
#endif

#ifdef __SS_BIND
PyObject *__ss__newobj__(PyObject *, PyObject *args, PyObject *kwargs);
#endif

