/* exceptions */

// stacktrace.h (c) 2008, Timo Bingmann from http://idlebox.net/
// published under the WTFPL v2.0

/** Print a demangled stack backtrace of the caller function to FILE* out. */

#ifdef __SS_BACKTRACE
static void print_stacktrace(FILE *out)
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

extern class_ *cl_stopiteration, *cl_assertionerror, *cl_eoferror, *cl_floatingpointerror, *cl_keyerror, *cl_indexerror, *cl_typeerror, *cl_ioerror, *cl_valueerror, *cl_zerodivisionerror, *cl_keyboardinterrupt, *cl_memoryerror, *cl_nameerror, *cl_notimplementederror, *cl_oserror, *cl_overflowerror, *cl_runtimeerror, *cl_syntaxerror, *cl_systemerror, *cl_systemexit;

class BaseException : public pyobj {
public:
    str *message; 
    BaseException(str *message=0) { 
        __init__(message); 
#ifdef __SS_BACKTRACE
        print_stacktrace(stdout);
#endif
    }
    void __init__(str *message) { 
        if(message) 
            this->message = message;
        else
            this->message = new str("");
    }
    void __init__(void *) { /* XXX test 148 */
        this->message = new str("");
    }
    str *__repr__() {
        return __add_strs(4, this->__class__->__name__, new str("('"), message, new str("',)"));
    }
    str *__str__() { 
        return message;
    }
};

class Exception: public BaseException {
public:
    Exception(str *message=0) : BaseException(message) {}

#ifdef __SS_BIND
   virtual PyObject *__to_py__() { return PyExc_Exception; }
#endif
};

class StopIteration : public Exception {
public:
    StopIteration(str *message=0) : Exception(message) { this->__class__ = cl_stopiteration; }
};

class StandardError : public Exception {
public:
    StandardError(str *message=0) : Exception(message) {}
};

class AssertionError : public StandardError {
public:
    AssertionError(str *message=0) : StandardError(message) { this->__class__ = cl_assertionerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_AssertionError; }
#endif
};

class EOFError : public StandardError {
public:
    EOFError(str *message=0) : StandardError(message) { this->__class__ = cl_eoferror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_EOFError; }
#endif
};

class FloatingPointError : public StandardError {
public:
    FloatingPointError(str *message=0) : StandardError(message) { this->__class__ = cl_floatingpointerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_FloatingPointError; }
#endif
};

class KeyError : public StandardError {
public:
    KeyError(str *message=0) : StandardError(message) { this->__class__ = cl_keyerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_KeyError; }
#endif
};

class IndexError : public StandardError {
public:
    IndexError(str *message=0) : StandardError(message) { this->__class__ = cl_indexerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_IndexError; }
#endif
};

class TypeError : public StandardError {
public:
    TypeError(str *message=0) : StandardError(message) { this->__class__ = cl_typeerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_TypeError; }
#endif
};

class IOError : public StandardError {
public:
    int __ss_errno;
    str *filename;
    str *message;
    str *strerror;

    IOError(str *message=0);
    str *__str__();
    str *__repr__();

#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_IOError; }
#endif
};

class KeyboardInterrupt : public BaseException {
public:
    KeyboardInterrupt(str *message=0) : BaseException(message) { this->__class__ = cl_keyboardinterrupt; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_KeyboardInterrupt; }
#endif
};

class MemoryError : public StandardError {
public:
    MemoryError(str *message=0) : StandardError(message) { this->__class__ = cl_memoryerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_MemoryError; }
#endif
};

class NameError : public StandardError {
public:
    NameError(str *message=0) : StandardError(message) { this->__class__ = cl_nameerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_NameError; }
#endif
};

class NotImplementedError : public StandardError {
public:
    NotImplementedError(str *message=0) : StandardError(message) { this->__class__ = cl_notimplementederror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_NotImplementedError; }
#endif
};

class OSError : public StandardError {
public:
    int __ss_errno;
    str *filename;
    str *message;
    str *strerror;

    OSError(str *message=0);
    str *__str__();
    str *__repr__();

#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_OSError; }
#endif
};

class OverflowError : public StandardError {
public:
    OverflowError(str *message=0) : StandardError(message) { this->__class__ = cl_overflowerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_OverflowError; }
#endif
};

class RuntimeError : public StandardError {
public:
    RuntimeError(str *message=0) : StandardError(message) { this->__class__ = cl_runtimeerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_RuntimeError; }
#endif
};

class SyntaxError : public StandardError {
public:
    SyntaxError(str *message=0) : StandardError(message) { this->__class__ = cl_syntaxerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SyntaxError; }
#endif
};

class SystemError : public StandardError {
public:
    SystemError(str *message=0) : StandardError(message) { this->__class__ = cl_systemerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SystemError; }
#endif
};

class SystemExit : public BaseException {
public:
    int code;
    SystemExit(str *message) : BaseException(message) { this->__class__ = cl_systemexit; this->code = 1; }
    SystemExit(__ss_int code) { this->__class__ = cl_systemexit; this->message = __str(code); this->code = code; }
    SystemExit() { this->__class__ = cl_systemexit; this->message = __str(0); this->code = 0; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SystemExit; }
#endif
};

class ValueError : public StandardError {
public:
    ValueError(str *message=0) : StandardError(message) { this->__class__ = cl_valueerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ValueError; }
#endif
};

class ZeroDivisionError : public StandardError {
public:
    ZeroDivisionError(str *message=0) : StandardError(message) { this->__class__ = cl_zerodivisionerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ZeroDivisionError; }
#endif
};
