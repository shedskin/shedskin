/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

/* exceptions */

#if !defined(WIN32) && !defined(__APPLE__)

// stacktrace.h (c) 2008, Timo Bingmann from http://idlebox.net/
// published under the WTFPL v2.0

/** Print a demangled stack backtrace of the caller function to FILE* out. */

#ifdef __SS_BACKTRACE
static void print_traceback(FILE *out)
{
    fprintf(out, "\nTraceback (most recent call last):\n");

    // storage array for stack trace address data
    void* addrlist[64];

    // retrieve current stack addresses
    int addrlen = backtrace(addrlist, sizeof(addrlist) / sizeof(void*));

    if (addrlen == 0) {
        fprintf(out, "  <empty, possibly corrupt>\n");
        return;
    }

    // resolve addresses into strings containing "filename(function+address)",
    // this array must be free()-ed
    char** symbollist = backtrace_symbols(addrlist, addrlen);

    // allocate string which will be filled with the demangled function name
    size_t funcnamesize = 256;
    char* funcname = (char*)malloc(funcnamesize);

    // iterate over the returned symbol lines. skip the first, it is the
    // address of this function.
    for (int i = addrlen-1; i > 0; i--)
    {
        char *begin_name = 0, *begin_offset = 0, *end_offset = 0;

        // find parentheses and +address offset surrounding the mangled name:
        // ./module(function+0x15c) [0x8048a6d]
        for (char *p = symbollist[i]; *p; ++p)
        {
            if (*p == '(')
                begin_name = p;
            else if (*p == '+')
                begin_offset = p;
            else if (*p == ')' && begin_offset) {
                end_offset = p;
                break;
            }
        }

        if (begin_name && begin_offset && end_offset
            && begin_name < begin_offset)
        {
            *begin_name++ = '\0';
            *begin_offset++ = '\0';
            *end_offset = '\0';

            // mangled name is now in [begin_name, begin_offset) and caller
            // offset in [begin_offset, end_offset). now apply
            // __cxa_demangle():

            int status;
            char* ret = abi::__cxa_demangle(begin_name,
                                            funcname, &funcnamesize, &status);
            if (status == 0) {
                funcname = ret; // use possibly realloc()-ed string
                if(strncmp(funcname, "__shedskin__::", 14) != 0)
                    //fprintf(out, "  %s : %s+%s\n", symbollist[i], funcname, begin_offset);
                    fprintf(out, "  %s : %s\n", symbollist[i], funcname);
            }
            else {
                // demangling failed. Output function name as a C function with
                // no arguments.
                //fprintf(out, "  %s : %s()+%s\n",
                //        symbollist[i], begin_name, begin_offset);
            }
        }
        else
        {
            // couldn't parse the line? print the whole line.
            //fprintf(out, "  %s\n", symbollist[i]);
        }
    }

    free(funcname);
    free(symbollist);
}
#endif
#endif

extern class_ *cl_stopiteration, *cl_assertionerror, *cl_eoferror, *cl_floatingpointerror, *cl_keyerror, *cl_indexerror, *cl_typeerror, *cl_valueerror, *cl_zerodivisionerror, *cl_keyboardinterrupt, *cl_memoryerror, *cl_nameerror, *cl_notimplementederror, *cl_oserror, *cl_overflowerror, *cl_runtimeerror, *cl_syntaxerror, *cl_systemerror, *cl_systemexit, *cl_arithmeticerror, *cl_lookuperror, *cl_exception, *cl_baseexception, *cl_pythonfinalizationerror;

class BaseException : public pyobj {
public:
    tuple<str *> *args;
    str *message; // TODO remove

    BaseException(str *msg=0);

    void __init__(str *msg) {}
    void __init__(void *) {}
    str *__repr__();
    str *__str__();
};

class Exception: public BaseException {
public:
    Exception(str *msg=0) : BaseException(msg) { this->__class__ = cl_exception; }

#ifdef __SS_BIND
   virtual PyObject *__to_py__() { return PyExc_Exception; }
#endif
};

class StopIteration : public Exception {
public:
    StopIteration(str *msg=0) : Exception(msg) { this->__class__ = cl_stopiteration; }
};

class AssertionError : public Exception {
public:
    AssertionError(str *msg=0) : Exception(msg) { this->__class__ = cl_assertionerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_AssertionError; }
#endif
};

class EOFError : public Exception {
public:
    EOFError(str *msg=0) : Exception(msg) { this->__class__ = cl_eoferror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_EOFError; }
#endif
};

class ArithmeticError : public Exception {
public:
    ArithmeticError(str *msg=0) : Exception(msg) { this->__class__ = cl_arithmeticerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ArithmeticError; }
#endif
};

class FloatingPointError : public ArithmeticError {
public:
    FloatingPointError(str *msg=0) : ArithmeticError(msg) { this->__class__ = cl_floatingpointerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_FloatingPointError; }
#endif
};

class LookupError : public Exception {
public:
    LookupError(str *msg=0) : Exception(msg) { this->__class__ = cl_lookuperror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_LookupError; }
#endif
};

class KeyError : public LookupError {
public:
    KeyError(str *msg=0) : LookupError(msg) { this->__class__ = cl_keyerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_KeyError; }
#endif
};

class IndexError : public LookupError {
public:
    IndexError(str *msg=0) : LookupError(msg) { this->__class__ = cl_indexerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_IndexError; }
#endif
};

class TypeError : public Exception {
public:
    TypeError(str *msg=0) : Exception(msg) { this->__class__ = cl_typeerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_TypeError; }
#endif
};

class KeyboardInterrupt : public BaseException {
public:
    KeyboardInterrupt(str *msg=0) : BaseException(msg) { this->__class__ = cl_keyboardinterrupt; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_KeyboardInterrupt; }
#endif
};

class MemoryError : public Exception {
public:
    MemoryError(str *msg=0) : Exception(msg) { this->__class__ = cl_memoryerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_MemoryError; }
#endif
};

class NameError : public Exception {
public:
    NameError(str *msg=0) : Exception(msg) { this->__class__ = cl_nameerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_NameError; }
#endif
};

class RuntimeError : public Exception {
public:
    RuntimeError(str *msg=0) : Exception(msg) { this->__class__ = cl_runtimeerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_RuntimeError; }
#endif
};

class NotImplementedError : public RuntimeError {
public:
    NotImplementedError(str *msg=0) : RuntimeError(msg) { this->__class__ = cl_notimplementederror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_NotImplementedError; }
#endif
};

class PythonFinalizationError : public RuntimeError {
public:
    PythonFinalizationError(str *msg=0) : RuntimeError(msg) { this->__class__ = cl_pythonfinalizationerror; }
#ifdef __SS_BIND
#if PY_MINOR_VERSION > 12
    PyObject *__to_py__() { return PyExc_PythonFinalizationError; }
#else
    PyObject *__to_py__() { return PyExc_RuntimeError; }
#endif
#endif
};

class OSError : public Exception {
public:
    int __ss_errno;
    str *filename;
    str *message;
    str *strerror;

    OSError(str *msg=0);
    str *__str__();
    str *__repr__();

#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_OSError; }
#endif
};

class FileNotFoundError : public OSError {
public:
    int __ss_errno;
    str *filename;
    str *message;
    str *strerror;

    FileNotFoundError(str *msg=0);
    str *__str__();
    str *__repr__();

#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_FileNotFoundError; }
#endif
};

class OverflowError : public ArithmeticError {
public:
    OverflowError(str *msg=0) : ArithmeticError(msg) { this->__class__ = cl_overflowerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_OverflowError; }
#endif
};

class SyntaxError : public Exception {
public:
    SyntaxError(str *msg=0) : Exception(msg) { this->__class__ = cl_syntaxerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SyntaxError; }
#endif
};

class SystemError : public Exception {
public:
    SystemError(str *msg=0) : Exception(msg) { this->__class__ = cl_systemerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SystemError; }
#endif
};

class SystemExit : public BaseException {
public:
    int code;
    int show_message;
    str *message;
    SystemExit(__ss_int c) {
        this->__class__ = cl_systemexit;
        this->code = c;
        this->message = __str(this->code);
        this->show_message = 0;
    }
    SystemExit() {
        this->__class__ = cl_systemexit;
        this->code = 0;
        this->message = __str(this->code);
        this->show_message = 0;
    }
    SystemExit(str *msg) : BaseException(msg) {
        this->__class__ = cl_systemexit;
        this->code = 1;
        this->show_message = 1;
    }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SystemExit; }
#endif
};

class ValueError : public Exception {
public:
    ValueError(str *msg=0) : Exception(msg) { this->__class__ = cl_valueerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ValueError; }
#endif
};

class ZeroDivisionError : public ArithmeticError {
public:
    ZeroDivisionError(str *msg=0) : ArithmeticError(msg) { this->__class__ = cl_zerodivisionerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ZeroDivisionError; }
#endif
};
