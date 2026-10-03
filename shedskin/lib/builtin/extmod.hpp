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

/* pickled state (see extmod.do_reduce_setstate) is a name-keyed dict.
 * PyTuple_SetItem steals a reference but PyDict_SetItemString does not, so the
 * value __to_py just produced has to be released once it is stored. */
inline void __ss_dict_steal(PyObject *dict, const char *key, PyObject *value) {
    if(value) {
        PyDict_SetItemString(dict, key, value);
        Py_DECREF(value);
    }
}

/* Borrowed reference, or NULL when the key is absent -- which happens whenever
 * a pickle predates the attribute. Callers must check before converting:
 * __to_ss only special-cases Py_None and would dereference NULL. */
inline PyObject *__ss_dict_lookup(PyObject *state, const char *key) {
    if(!state || !PyDict_Check(state))
        return 0;
    return PyDict_GetItemString(state, key);
}

template<class T> PyObject *__to_py(T t) {
    if(!t) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return t->__to_py__();
}

/* set the CPython error for a caught shedskin exception. the message is
   passed as a str object rather than through PyErr_SetString: that decodes
   the char* strictly as utf-8, so a surrogate-escaped byte (e.g. a
   non-utf-8 file name in an OSError message) would turn into a
   UnicodeDecodeError */
inline void __ss_raise_py(Exception *e) {
    PyObject *args = e->__py_args__();
    if(args) {
        PyErr_SetObject(e->__to_py__(), args); /* type(*args) */
        Py_DECREF(args);
    } else {
        PyObject *msg = e->message ? e->message->__to_py__() : PyUnicode_FromStringAndSize("", 0);
        PyErr_SetObject(e->__to_py__(), msg); /* does not steal msg */
        Py_XDECREF(msg);
    }
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
/* check the arguments of a call against the formals, as CPython does for a
   Python function (same order of checks, same messages), before __ss_arg
   picks them up: otherwise extra positional arguments and unknown or
   duplicate keywords were silently ignored. 'names' holds the 'nformals'
   names of the formals (without 'self'), the first 'nrequired' of which have
   no default. args/kwargs may be NULL (e.g. when called from tp_hash). */
inline void __ss_check_args(const char *fname, int is_method, int nformals, int nrequired, const char *const *names, PyObject *args, PyObject *kwargs) {
    Py_ssize_t nargs = args ? PyTuple_Size(args) : 0;
    std::string prefix = std::string(fname) + "() ";

    /* keywords */
    if (kwargs && PyDict_Check(kwargs)) {
        PyObject *key, *value;
        Py_ssize_t pos = 0;
        while (PyDict_Next(kwargs, &pos, &key, &value)) {
            if (!PyUnicode_Check(key)) /* f(**{1: 2}) gets here for a C function */
                throw new TypeError(new str("keywords must be strings"));
            int index = -1;
            const char *utf8 = PyUnicode_AsUTF8(key);
            if (!utf8)
                PyErr_Clear(); /* e.g. a lone surrogate: matches no formal */
            else {
                for (int i = 0; i < nformals; i++) {
                    if (strcmp(utf8, names[i]) == 0) {
                        index = i;
                        break;
                    }
                }
            }
            if (index == -1 || index < nargs) {
                str *name = new str(key);
                const char *what = index == -1 ? "got an unexpected keyword argument '" : "got multiple values for argument '";
                throw new TypeError((new str((prefix + what).c_str()))->__add__(name)->__add__(new str("'")));
            }
        }
    }

    /* too many positional arguments ('self' counts, as in CPython) */
    if (nargs > nformals) {
        std::string msg = prefix + "takes ";
        if (nrequired == nformals)
            msg += std::to_string(nformals + is_method) + " positional argument" + (nformals + is_method == 1 ? "" : "s");
        else
            msg += "from " + std::to_string(nrequired + is_method) + " to " + std::to_string(nformals + is_method) + " positional arguments";
        msg += " but " + std::to_string(nargs + is_method) + (nargs + is_method == 1 ? " was" : " were") + " given";
        throw new TypeError(new str(msg.c_str()));
    }

    /* missing arguments */
    std::vector<std::string> missing;
    for (int i = (int)nargs; i < nrequired; i++)
        if (!kwargs || !PyDict_Check(kwargs) || !PyDict_GetItemString(kwargs, names[i]))
            missing.push_back(std::string("'") + names[i] + "'");
    if (!missing.empty()) {
        size_t n = missing.size();
        std::string msg = prefix + "missing " + std::to_string(n) + " required positional argument" + (n == 1 ? "" : "s") + ": ";
        for (size_t i = 0; i < n; i++) {
            if (i > 0)
                msg += n == 2 ? " and " : (i == n - 1 ? ", and " : ", ");
            msg += missing[i];
        }
        throw new TypeError(new str(msg.c_str()));
    }
}

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

