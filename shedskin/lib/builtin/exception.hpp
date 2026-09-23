/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

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

extern class_ *cl_stopiteration, *cl_assertionerror, *cl_eoferror, *cl_floatingpointerror, *cl_keyerror, *cl_indexerror, *cl_typeerror, *cl_valueerror, *cl_zerodivisionerror, *cl_keyboardinterrupt, *cl_generatorexit, *cl_memoryerror, *cl_nameerror, *cl_notimplementederror, *cl_oserror, *cl_overflowerror, *cl_runtimeerror, *cl_syntaxerror, *cl_systemerror, *cl_systemexit, *cl_arithmeticerror, *cl_lookuperror, *cl_exception, *cl_baseexception, *cl_pythonfinalizationerror, *cl_unicodeerror, *cl_unicodedecodeerror, *cl_unicodeencodeerror, *cl_unicodetranslateerror;
extern class_ *cl_recursionerror, *cl_unboundlocalerror, *cl_referenceerror, *cl_buffererror;
extern class_ *cl_warning, *cl_byteswarning, *cl_deprecationwarning, *cl_encodingwarning, *cl_futurewarning, *cl_importwarning, *cl_pendingdeprecationwarning, *cl_resourcewarning, *cl_runtimewarning, *cl_syntaxwarning, *cl_unicodewarning, *cl_userwarning;
extern class_ *cl_filenotfounderror, *cl_blockingioerror, *cl_childprocesserror, *cl_connectionerror, *cl_brokenpipeerror, *cl_connectionabortederror, *cl_connectionrefusederror, *cl_connectionreseterror, *cl_fileexistserror, *cl_interruptederror, *cl_isadirectoryerror, *cl_notadirectoryerror, *cl_permissionerror, *cl_processlookuperror, *cl_timeouterror;

class BaseException : public pyobj {
public:
    tuple<str *> *args;
    str *message; // TODO remove? now used by extmod code
    list<str *> *__notes__; /* 0 (None) until add_note is called */

    BaseException(str *msg=0);
    void *add_note(str *note);

    void __init__(str *msg);
    void __init__(void *) {
        this->message = 0;
    }

    str *__repr__();
    str *__str__();
};

class Exception: public BaseException {
public:
    Exception(str *msg=0) : BaseException(msg) {
        this->__class__ = cl_exception;
    }

#ifdef __SS_BIND
   virtual PyObject *__to_py__() { return PyExc_Exception; }
   /* constructor arguments for the CPython exception, as a new tuple
      reference, for exceptions that cannot be created from just their
      message (see __ss_raise_py in extmod.hpp); 0 means use message */
   virtual PyObject *__py_args__() { return 0; }
#endif
};

class StopIteration : public Exception {
public:
    str *value; /* only for explicit raises; generator return values are not tracked */
    StopIteration(str *msg=0) : Exception(msg) { this->__class__ = cl_stopiteration; this->value = msg; }
#ifdef __SS_BIND
   virtual PyObject *__to_py__() { return PyExc_StopIteration; }
#endif
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

/* KeyError raised by a failed dict/set/Counter lookup: keeps the key itself,
   so an extension module can pass it to CPython as-is (message is repr(key),
   which KeyError.__str__ would otherwise repr a second time) */
template<class T> str *repr(T t);
#ifdef __SS_BIND
template<class T> PyObject *__to_py(T t);

/* can __to_py(T) be instantiated? true for the non-pointer types that have
   explicit specializations (int, float, bool, complex) and for pointers to
   classes defining __to_py__(); false for e.g. datetime.date keys, which have
   no conversion and would otherwise break the extension module build */
template<class T, class = void> struct __ss_has_to_py : std::bool_constant<!std::is_pointer_v<T>> {};
template<class T> struct __ss_has_to_py<T, std::void_t<decltype(std::declval<T>()->__to_py__())>> : std::true_type {};
#endif

template<class T> class KeyErrorT : public KeyError {
public:
    T key;
    KeyErrorT(T key) : KeyError(repr(key)), key(key) {}
#ifdef __SS_BIND
    PyObject *__py_args__() {
        if constexpr (__ss_has_to_py<T>::value)
            return Py_BuildValue("(N)", __to_py(key)); /* N: steals the new reference */
        else
            return 0; /* fall back to the message (repr(key)) */
    }
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

class GeneratorExit : public BaseException {
public:
    GeneratorExit(str *msg=0) : BaseException(msg) { this->__class__ = cl_generatorexit; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_GeneratorExit; }
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
    str *name;
    NameError(str *msg=0, str *name=0) : Exception(msg) { this->__class__ = cl_nameerror; this->name = name; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_NameError; }
#endif
};

class UnboundLocalError : public NameError {
public:
    UnboundLocalError(str *msg=0, str *name=0) : NameError(msg, name) { this->__class__ = cl_unboundlocalerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_UnboundLocalError; }
#endif
};

class ReferenceError : public Exception {
public:
    ReferenceError(str *msg=0) : Exception(msg) { this->__class__ = cl_referenceerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ReferenceError; }
#endif
};

class BufferError : public Exception {
public:
    BufferError(str *msg=0) : Exception(msg) { this->__class__ = cl_buffererror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_BufferError; }
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

class RecursionError : public RuntimeError {
public:
    RecursionError(str *msg=0) : RuntimeError(msg) { this->__class__ = cl_recursionerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_RecursionError; }
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
    __ss_int __ss_errno;
    str *filename;
    str *filename2;
    str *strerror;

    OSError(str *msg=0);
    void __init_errno(int e, str *fname);
    str *__str__();
    str *__repr__();

#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_OSError; }
#endif
};

/* OSError subclasses (PEP 3151); __throw_oserror() picks one based on errno */

class BlockingIOError : public OSError {
public:
    BlockingIOError(str *msg=0) : OSError(msg) { this->__class__ = cl_blockingioerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_BlockingIOError; }
#endif
};

class ChildProcessError : public OSError {
public:
    ChildProcessError(str *msg=0) : OSError(msg) { this->__class__ = cl_childprocesserror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ChildProcessError; }
#endif
};

class ConnectionError : public OSError {
public:
    ConnectionError(str *msg=0) : OSError(msg) { this->__class__ = cl_connectionerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ConnectionError; }
#endif
};

class BrokenPipeError : public ConnectionError {
public:
    BrokenPipeError(str *msg=0) : ConnectionError(msg) { this->__class__ = cl_brokenpipeerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_BrokenPipeError; }
#endif
};

class ConnectionAbortedError : public ConnectionError {
public:
    ConnectionAbortedError(str *msg=0) : ConnectionError(msg) { this->__class__ = cl_connectionabortederror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ConnectionAbortedError; }
#endif
};

class ConnectionRefusedError : public ConnectionError {
public:
    ConnectionRefusedError(str *msg=0) : ConnectionError(msg) { this->__class__ = cl_connectionrefusederror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ConnectionRefusedError; }
#endif
};

class ConnectionResetError : public ConnectionError {
public:
    ConnectionResetError(str *msg=0) : ConnectionError(msg) { this->__class__ = cl_connectionreseterror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ConnectionResetError; }
#endif
};

class FileExistsError : public OSError {
public:
    FileExistsError(str *msg=0) : OSError(msg) { this->__class__ = cl_fileexistserror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_FileExistsError; }
#endif
};

class FileNotFoundError : public OSError {
public:
    FileNotFoundError(str *msg=0) : OSError(msg) { this->__class__ = cl_filenotfounderror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_FileNotFoundError; }
#endif
};

class InterruptedError : public OSError {
public:
    InterruptedError(str *msg=0) : OSError(msg) { this->__class__ = cl_interruptederror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_InterruptedError; }
#endif
};

class IsADirectoryError : public OSError {
public:
    IsADirectoryError(str *msg=0) : OSError(msg) { this->__class__ = cl_isadirectoryerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_IsADirectoryError; }
#endif
};

class NotADirectoryError : public OSError {
public:
    NotADirectoryError(str *msg=0) : OSError(msg) { this->__class__ = cl_notadirectoryerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_NotADirectoryError; }
#endif
};

class PermissionError : public OSError {
public:
    PermissionError(str *msg=0) : OSError(msg) { this->__class__ = cl_permissionerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_PermissionError; }
#endif
};

class ProcessLookupError : public OSError {
public:
    ProcessLookupError(str *msg=0) : OSError(msg) { this->__class__ = cl_processlookuperror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ProcessLookupError; }
#endif
};

class TimeoutError : public OSError {
public:
    TimeoutError(str *msg=0) : OSError(msg) { this->__class__ = cl_timeouterror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_TimeoutError; }
#endif
};

/* throw the OSError subclass matching errno (as CPython does), with the
   given file name (or none); use this for failed calls that set errno */
[[noreturn]] void __throw_oserror(str *fname=0);

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
    __ss_int code;
    int show_message;
    SystemExit();
    SystemExit(__ss_int c);
    SystemExit(str *msg);

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

class UnicodeError : public ValueError {
public:
    UnicodeError(str *msg=0) : ValueError(msg) { this->__class__ = cl_unicodeerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_UnicodeError; }
#endif
};

/* the three concrete unicode errors carry the CPython attributes
   (encoding, object, start, end, reason); str()/repr() are derived from
   those, as in CPython. start/end delimit the offending range
   [start, end) in object. */

class UnicodeDecodeError : public UnicodeError {
public:
    str *encoding;
    bytes *_object; /* 'object' in python; the compiler mangles it to _object (class name) */
    __ss_int start;
    __ss_int end;
    str *reason;

    UnicodeDecodeError(str *encoding, bytes *object, __ss_int start, __ss_int end, str *reason);
    str *__str__();
    str *__repr__();
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_UnicodeDecodeError; }
    PyObject *__py_args__();
#endif
};

class UnicodeEncodeError : public UnicodeError {
public:
    str *encoding;
    str *_object; /* see UnicodeDecodeError */
    __ss_int start;
    __ss_int end;
    str *reason;

    UnicodeEncodeError(str *encoding, str *object, __ss_int start, __ss_int end, str *reason);
    str *__str__();
    str *__repr__();
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_UnicodeEncodeError; }
    PyObject *__py_args__();
#endif
};

class UnicodeTranslateError : public UnicodeError {
public:
    str *_object; /* see UnicodeDecodeError */
    __ss_int start;
    __ss_int end;
    str *reason;

    UnicodeTranslateError(str *object, __ss_int start, __ss_int end, str *reason);
    str *__str__();
    str *__repr__();
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_UnicodeTranslateError; }
    PyObject *__py_args__();
#endif
};

class ZeroDivisionError : public ArithmeticError {
public:
    ZeroDivisionError(str *msg=0) : ArithmeticError(msg) { this->__class__ = cl_zerodivisionerror; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ZeroDivisionError; }
#endif
};

/* warnings */

class Warning : public Exception {
public:
    Warning(str *msg=0) : Exception(msg) { this->__class__ = cl_warning; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_Warning; }
#endif
};

class BytesWarning : public Warning {
public:
    BytesWarning(str *msg=0) : Warning(msg) { this->__class__ = cl_byteswarning; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_BytesWarning; }
#endif
};

class DeprecationWarning : public Warning {
public:
    DeprecationWarning(str *msg=0) : Warning(msg) { this->__class__ = cl_deprecationwarning; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_DeprecationWarning; }
#endif
};

class EncodingWarning : public Warning {
public:
    EncodingWarning(str *msg=0) : Warning(msg) { this->__class__ = cl_encodingwarning; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_EncodingWarning; }
#endif
};

class FutureWarning : public Warning {
public:
    FutureWarning(str *msg=0) : Warning(msg) { this->__class__ = cl_futurewarning; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_FutureWarning; }
#endif
};

class ImportWarning : public Warning {
public:
    ImportWarning(str *msg=0) : Warning(msg) { this->__class__ = cl_importwarning; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ImportWarning; }
#endif
};

class PendingDeprecationWarning : public Warning {
public:
    PendingDeprecationWarning(str *msg=0) : Warning(msg) { this->__class__ = cl_pendingdeprecationwarning; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_PendingDeprecationWarning; }
#endif
};

class ResourceWarning : public Warning {
public:
    ResourceWarning(str *msg=0) : Warning(msg) { this->__class__ = cl_resourcewarning; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ResourceWarning; }
#endif
};

class RuntimeWarning : public Warning {
public:
    RuntimeWarning(str *msg=0) : Warning(msg) { this->__class__ = cl_runtimewarning; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_RuntimeWarning; }
#endif
};

class SyntaxWarning : public Warning {
public:
    SyntaxWarning(str *msg=0) : Warning(msg) { this->__class__ = cl_syntaxwarning; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SyntaxWarning; }
#endif
};

class UnicodeWarning : public Warning {
public:
    UnicodeWarning(str *msg=0) : Warning(msg) { this->__class__ = cl_unicodewarning; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_UnicodeWarning; }
#endif
};

class UserWarning : public Warning {
public:
    UserWarning(str *msg=0) : Warning(msg) { this->__class__ = cl_userwarning; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_UserWarning; }
#endif
};
