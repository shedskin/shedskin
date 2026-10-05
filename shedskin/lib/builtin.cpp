/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "builtin.hpp"
#include "re.hpp"
#include <climits>
#include <cmath>
#include <numeric>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <limits.h>
#include <string_view>

/* system headers must be included here, outside namespace __shedskin__:
   the files under builtin/ are included below, from inside the namespace,
   so any header they include for the first time (e.g. <sys/stat.h> on
   FreeBSD) would get its declarations placed in the wrong namespace */
#ifdef WIN32
#include <io.h> // for _isatty
#else
#include <unistd.h>
#include <sys/stat.h>
#include <signal.h>
#endif

namespace __shedskin__ {


class_ *cl_class_, *cl_none, *cl_str_, *cl_int_, *cl_bool, *cl_float_, *cl_complex, *cl_list, *cl_tuple, *cl_dict, *cl_frozendict, *cl_set, *cl_object, *cl_rangeiter, *cl_xrange, *cl_bytes, *cl_bytearray;

class_ *cl_stopiteration, *cl_assertionerror, *cl_eoferror, *cl_floatingpointerror, *cl_keyerror, *cl_indexerror, *cl_typeerror, *cl_valueerror, *cl_zerodivisionerror, *cl_keyboardinterrupt, *cl_generatorexit, *cl_memoryerror, *cl_nameerror, *cl_notimplementederror, *cl_oserror, *cl_overflowerror, *cl_runtimeerror, *cl_syntaxerror, *cl_systemerror, *cl_systemexit, *cl_filenotfounderror, *cl_arithmeticerror, *cl_lookuperror, *cl_exception, *cl_baseexception, *cl_pythonfinalizationerror, *cl_unicodeerror, *cl_unicodedecodeerror, *cl_unicodeencodeerror, *cl_unicodetranslateerror;
class_ *cl_recursionerror, *cl_unboundlocalerror, *cl_referenceerror, *cl_buffererror;
class_ *cl_warning, *cl_byteswarning, *cl_deprecationwarning, *cl_encodingwarning, *cl_futurewarning, *cl_importwarning, *cl_pendingdeprecationwarning, *cl_resourcewarning, *cl_runtimewarning, *cl_syntaxwarning, *cl_unicodewarning, *cl_userwarning;
class_ *cl_blockingioerror, *cl_childprocesserror, *cl_connectionerror, *cl_brokenpipeerror, *cl_connectionabortederror, *cl_connectionrefusederror, *cl_connectionreseterror, *cl_fileexistserror, *cl_interruptederror, *cl_isadirectoryerror, *cl_notadirectoryerror, *cl_permissionerror, *cl_processlookuperror, *cl_timeouterror;

str *sp, *nl, *__fmt_s, *__fmt_H, *__fmt_d;
bytes *bsp;

__GC_STRING ws, __fmtchars;
__GC_VECTOR(str *) __char_cache;
str *__int_str_cache[256];
__GC_VECTOR(bytes *) __byte_cache;

__ss_bool True;
__ss_bool False;

__ss_void_struct __ss_void;

str *__case_swap_cache;

char __str_cache[4000];
str *__ss_empty_str;

file *__ss_stdin, *__ss_stdout, *__ss_stderr;

tuple<__ss_int> *__ss_tuple_cache[1600];

str *byteorder_big, *byteorder_little;

#ifdef __SS_BIND
dict<void *, void *> *__ss_proxy;
#endif

#ifndef __SS_NOGC
void gc_warning_handler(char *, GC_word) {}
#endif

void __init() {
#ifndef __SS_NOGC
    GC_INIT();
    GC_set_warn_proc(gc_warning_handler);

    /* GC tuning. bdwgc collects once it has allocated about (live pointer data + roots) /
       free_space_divisor bytes since the last collection, so a program that allocates many
       short-lived objects but keeps little alive would otherwise do a full collection after every
       few hundred KB of allocation. note that bdwgc reads some environment variables in GC_INIT
       (GC_INITIAL_HEAP_SIZE, GC_MAXIMUM_HEAP_SIZE, GC_FREE_SPACE_DIVISOR, GC_FULL_FREQUENCY,
       GC_ENABLE_INCREMENTAL, GC_PRINT_STATS, ..), and the calls below override these. */

#if GC_VERSION_MAJOR > 8 || (GC_VERSION_MAJOR == 8 && GC_VERSION_MINOR >= 2)
    /* allocate at least this many bytes between collections (bdwgc default: 1) */
    GC_set_min_bytes_allocd(4 << 20);
#else
    GC_expand_hp(4 << 20); /* older bdwgc: no GC_set_min_bytes_allocd, use a larger initial heap instead */
#endif

    /* grow the initial heap by this many bytes (bdwgc default initial heap: 64KB) */
    // GC_expand_hp(4 << 20);

    /* higher: collect more often, smaller heap; lower: fewer collections, larger heap (default: 3) */
    // GC_set_free_space_divisor(3);

    /* heap size limit in bytes, after which allocation fails with MemoryError (default: 0, no limit) */
    // GC_set_max_heap_size(1UL << 30);

    /* never grow the heap by itself, only collect (default: 0) */
    // GC_set_dont_expand(1);

    /* incremental/generational collection (uses virtual memory dirty bits; default: off) */
    // GC_enable_incremental();
    /* with incremental collection: do a full collection every n+1 collections (default: 19) */
    // GC_set_full_freq(19);
    /* with incremental collection: target pause time in ms (default: GC_TIME_UNLIMITED with parallel marking, else 15) */
    // GC_set_time_limit(15);
#endif

#ifdef __SS_BIND
    Py_Initialize();
    __ss_proxy = new dict<void *, void *>();
#endif

#if !defined(WIN32) && !defined(__SS_BIND)
    /* like CPython: writing to a closed pipe or socket raises BrokenPipeError
       (EPIPE), instead of silently killing the process (extension modules
       leave this to the interpreter, which does the same) */
    ::signal(SIGPIPE, SIG_IGN);
#endif

    cl_class_ = new class_ ("class");
    cl_none = new class_("None");
    cl_str_ = new class_("str");
    cl_bytes = new class_("bytes");
    cl_bytearray = new class_("bytearray");
    cl_int_ = new class_("int");
    cl_float_ = new class_("float");
    cl_list = new class_("list");
    cl_tuple = new class_("tuple");
    cl_dict = new class_("dict");
    cl_frozendict = new class_("frozendict");
    cl_set = new class_("set");
    cl_object = new class_("object");
    cl_rangeiter = new class_("rangeiter");
    cl_complex = new class_("complex");
    cl_xrange = new class_("xrange");

    True.value = 1;
    False.value = 0;

    byteorder_big = new str("big");
    byteorder_little = new str("little");

    ws = " \n\r\t\f\v";
    __fmtchars = "#*-+ .0123456789hlL";
    sp = new str(" ");
    bsp = new bytes(" ");
    nl = new str("\n");
    __fmt_s = new str("%s");
    __fmt_H = new str("%H");
    __fmt_d = new str("%d");

    for(int i=0;i<256;i++) {
        str *charstr = new str(__GC_STR(1, (__ss_char)i));
        charstr->charcache = 1;
        __char_cache.push_back(charstr);
    }

    /* str(i) for 0 <= i < 256 (strs are immutable, so they can be shared) */
    for(int i=0;i<256;i++) {
        if(i < 10)
            __int_str_cache[i] = __char_cache[(unsigned char)('0'+i)];
        else {
            char buf[4];
            int n = snprintf(buf, sizeof(buf), "%d", i);
            __int_str_cache[i] = new str(buf, (size_t)n);
        }
    }

    for(int i=0;i<256;i++) {
        char c = (char)i;
        bytes *charbytes = new bytes(&c, 1, 1);
//        charbytes->charcache = 1; // TODO add and use in bytes.__contains__
        __byte_cache.push_back(charbytes);
    }

    for(int i=0; i<1000; i++) {
        __str_cache[4*i] = '0' + (char)(i % 10);
        __str_cache[4*i+1] = '0' + (char)((i/10) % 10);
        __str_cache[4*i+2] = '0' + (char)((i/100) % 10);
    }
    __ss_empty_str = new str();

    __case_swap_cache = new str();
    for(int i=0; i<256; i++) {
        char c = (char)i;
        if(::islower(c))
            __case_swap_cache->unit += (char)::toupper(c);
        else
            __case_swap_cache->unit += (char)::tolower(c);
    }

    for(__ss_int i=0; i<40; i++)
        for(__ss_int j=0; j<40; j++)
            __ss_tuple_cache[i*40+j] = new tuple<__ss_int>(2, i-20, j-20);

    __ss_stdin = new file(stdin);
    __ss_stdin->name = new str("<stdin>");
    __ss_stdout = new file(stdout);
    __ss_stdout->name = new str("<stdout>");
    __ss_stderr = new file(stderr);
    __ss_stderr->name = new str("<stderr>");

    cl_baseexception = new class_("BaseException");
    cl_exception = new class_("Exception");
    cl_stopiteration = new class_("StopIteration");
    cl_assertionerror = new class_("AssertionError");
    cl_eoferror = new class_("EOFError");
    cl_floatingpointerror = new class_("FloatingPointError");
    cl_keyerror = new class_("KeyError");
    cl_indexerror = new class_("IndexError");
    cl_typeerror = new class_("TypeError");
    cl_filenotfounderror = new class_("FileNotFoundError");
    cl_valueerror = new class_("ValueError");
    cl_zerodivisionerror = new class_("ZeroDivisionError");
    cl_keyboardinterrupt = new class_("KeyboardInterrupt");
    cl_generatorexit = new class_("GeneratorExit");
    cl_memoryerror = new class_("MemoryError");
    cl_nameerror = new class_("NameError");
    cl_notimplementederror = new class_("NotImplementedError");
    cl_pythonfinalizationerror = new class_("PythonFinalizationError");
    cl_oserror = new class_("OSError");
    cl_blockingioerror = new class_("BlockingIOError");
    cl_childprocesserror = new class_("ChildProcessError");
    cl_connectionerror = new class_("ConnectionError");
    cl_brokenpipeerror = new class_("BrokenPipeError");
    cl_connectionabortederror = new class_("ConnectionAbortedError");
    cl_connectionrefusederror = new class_("ConnectionRefusedError");
    cl_connectionreseterror = new class_("ConnectionResetError");
    cl_fileexistserror = new class_("FileExistsError");
    cl_interruptederror = new class_("InterruptedError");
    cl_isadirectoryerror = new class_("IsADirectoryError");
    cl_notadirectoryerror = new class_("NotADirectoryError");
    cl_permissionerror = new class_("PermissionError");
    cl_processlookuperror = new class_("ProcessLookupError");
    cl_timeouterror = new class_("TimeoutError");
    cl_overflowerror = new class_("OverflowError");
    cl_runtimeerror = new class_("RuntimeError");
    cl_syntaxerror = new class_("SyntaxError");
    cl_systemerror = new class_("SystemError");
    cl_systemexit = new class_("SystemExit");
    cl_arithmeticerror = new class_("ArithmeticError");
    cl_lookuperror = new class_("LookupError");
    cl_unicodeerror = new class_("UnicodeError");
    cl_unicodedecodeerror = new class_("UnicodeDecodeError");
    cl_unicodeencodeerror = new class_("UnicodeEncodeError");
    cl_unicodetranslateerror = new class_("UnicodeTranslateError");
    cl_recursionerror = new class_("RecursionError");
    cl_unboundlocalerror = new class_("UnboundLocalError");
    cl_referenceerror = new class_("ReferenceError");
    cl_buffererror = new class_("BufferError");
    cl_warning = new class_("Warning");
    cl_byteswarning = new class_("BytesWarning");
    cl_deprecationwarning = new class_("DeprecationWarning");
    cl_encodingwarning = new class_("EncodingWarning");
    cl_futurewarning = new class_("FutureWarning");
    cl_importwarning = new class_("ImportWarning");
    cl_pendingdeprecationwarning = new class_("PendingDeprecationWarning");
    cl_resourcewarning = new class_("ResourceWarning");
    cl_runtimewarning = new class_("RuntimeWarning");
    cl_syntaxwarning = new class_("SyntaxWarning");
    cl_unicodewarning = new class_("UnicodeWarning");
    cl_userwarning = new class_("UserWarning");

}

class_::class_(const char *name) {
    this->__name__ = new str(name);
}

str *class_::__repr__() {
    return __add_strs(3, new str("<class "), __name__, new str(">"));
}

__ss_bool class_::__eq__(pyobj *c) {
    return __mbool(c == this);
}

#include "builtin/file.cpp"
#include "builtin/math.cpp"
#include "builtin/bool.cpp"
#include "builtin/complex.cpp"
#include "builtin/str.cpp"
#include "builtin/unicode.cpp"
#include "builtin/bytes.cpp"
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
        code = (int)s->code;
        try {
            __add_missing_newline(); /* XXX s->message -> stderr? */
            if(s->show_message)
                print_(0, False, __ss_stderr, NULL, NULL, s->message);
        } catch (BaseException *) {} /* e.g. stdout is a closed pipe */

    } catch (BaseException *e) {
        code = 1;
        try {
            __add_missing_newline();

#ifndef WIN32
#ifdef __SS_BACKTRACE
            print_traceback(stdout);
#endif
#endif

            str *s = __str(e);
            if(___bool(s))
                print_(0, False, NULL, NULL, NULL, __add_strs(3, e->__class__->__name__, new str(": "), s));
            else
                print_(0, False, NULL, NULL, NULL, e->__class__->__name__);
            if(e->__notes__)
                for(__ss_int i=0; i<len(e->__notes__); i++)
                    print_(0, False, NULL, NULL, NULL, e->__notes__->__getfast__(i));
        } catch (BaseException *) {} /* e.g. stdout is a closed pipe */
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
template<> PyObject *__to_py(int32_t i) { return PyLong_FromLong(i); }
template<> PyObject *__to_py(int64_t i) { return PyLong_FromLongLong(i); }

#ifdef __SS_INT128
template<> PyObject *__to_py(__int128 i) {
    int num = 1;
    bool little_endian = (*(char *)&num == 1);
    return _PyLong_FromByteArray((const unsigned char *)&i, sizeof(i), little_endian, 1);
}

#endif
#ifdef WIN32
template<> PyObject *__to_py(long i) { return PyLong_FromLong(i); }
#endif
#ifdef __APPLE__
template<> PyObject *__to_py(long i) { return PyLong_FromLong(i); }
#endif
template<> PyObject *__to_py(__ss_bool i) { return PyBool_FromLong(i.value); }
template<> PyObject *__to_py(__ss_float d) { return PyFloat_FromDouble(d); }
template<> PyObject *__to_py(void *) { Py_INCREF(Py_None); return Py_None; }

void throw_exception() {
    /* PyErr_Fetch hands back the *actual exception instance* (e.g. an
     * OverflowError), never a bytes object, so treating pvalue as a
     * PyBytesObject and reading it with PyBytes_AS_STRING is a type
     * confusion: it reinterprets the exception instance's memory layout as
     * if it were a bytes buffer, producing whatever garbage happens to be
     * at that offset (confirmed: converting an out-of-range int raised
     * TypeError('') -- wrong type, empty message -- instead of a proper
     * OverflowError with its real text). PyErr_Fetch also transfers
     * ownership of all three references to the caller; none of them were
     * ever released, leaking one to three PyObjects per exception.
     *
     * Fetch, normalize (so pvalue is guaranteed to be an instance rather
     * than sometimes a class/args tuple depending on how it was raised),
     * stringify it the same way Python's own traceback machinery would,
     * and release every reference before throwing onward. */
    PyObject *ptype, *pvalue, *ptraceback;
    PyErr_Fetch(&ptype, &pvalue, &ptraceback);
    PyErr_NormalizeException(&ptype, &pvalue, &ptraceback);

    str *message = new str("");
    if (pvalue) {
        PyObject *pystr = PyObject_Str(pvalue);
        if (pystr) {
            /* str(PyObject *) copies code points, so a message holding a
             * lone surrogate is kept as-is (PyUnicode_AsUTF8 would fail on
             * it and leave a UnicodeEncodeError set) */
            message = new str(pystr);
            Py_DECREF(pystr);
        } else {
            PyErr_Clear();
        }
    }

    /* keep an OverflowError (an int too large for a double, say): a
       conversion failure is otherwise a TypeError */
    bool overflow = ptype && PyErr_GivenExceptionMatches(ptype, PyExc_OverflowError);

    Py_XDECREF(ptype);
    Py_XDECREF(pvalue);
    Py_XDECREF(ptraceback);

    if (overflow)
        throw new OverflowError(message);
    throw new TypeError(message);
}

template<> __ss_int __to_ss(PyObject *p) {
    if(PyLong_Check(p)) {
        __ss_int result;
#ifdef __SS_INT128
        int num = 1;
        bool little_endian = (*(char *)&num == 1);
        _PyLong_AsByteArray((PyLongObject *)p, (unsigned char *)&result, sizeof(__ss_int), little_endian, 1);
        if (result == -1 && PyErr_Occurred() != NULL) {
            throw_exception();
        }
#else
        /* check the range before narrowing: under --int32, a value that
           fits in a long long but not in __ss_int was silently truncated */
        int overflow;
        long long value = PyLong_AsLongLongAndOverflow(p, &overflow);
        if (value == -1 && PyErr_Occurred() != NULL)
            throw_exception();
        if (overflow)
            throw new OverflowError(new str("Python int too large to convert to 64-bit int"));
        if constexpr (sizeof(__ss_int) < sizeof(long long)) {
            if (value < std::numeric_limits<__ss_int>::min() || value > std::numeric_limits<__ss_int>::max())
                throw new OverflowError(new str("Python int too large to convert to 32-bit int"));
        }
        result = (__ss_int)value;
#endif
        return result;
    }

    throw new TypeError(new str("error in conversion to Shed Skin (integer expected)"));
}

template<> __ss_bool __to_ss(PyObject *p) {
    if(!PyBool_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (boolean expected)"));
    return (p==Py_True)?(__mbool(true)):(__mbool(false));
}

template<> __ss_float __to_ss(PyObject *p) {
    if(!PyLong_Check(p) and !PyFloat_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (float or int expected)"));
    double d = PyFloat_AsDouble(p);
    if (d == -1.0 && PyErr_Occurred() != NULL) /* int too large (OverflowError) */
        throw_exception();
    return d;
}

template<> void * __to_ss(PyObject *p) {
    if(p!=Py_None)
        throw new TypeError(new str("error in conversion to Shed Skin (None expected)"));
    return NULL;
}
#endif

template<> int __none() { throw new TypeError(new str("mixing None with int")); }
template<> __ss_float __none() { throw new TypeError(new str("mixing None with float")); }
template<> __ss_bool __none() { throw new TypeError(new str("mixing None with bool")); }

/* pyobj */

str *pyobj::__str__() { return __repr__(); }

str *pyobj::__repr__() {
    std::stringstream stream;
    stream << "0x" << std::hex << reinterpret_cast<uintptr_t>(this);
    return __add_strs(5, new str("<"), __class__->__name__, new str(" object at "), new str(stream.str().c_str()), new str(">"));
}

__ss_int pyobj::__hash__() {
    return (__ss_int)(intptr_t)this;
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

__ss_int pyobj::__int__() { return this->__index__(); }
__ss_float pyobj::__float__() { return (__ss_float)(this->__index__()); }
complex pyobj::__ss___complex__() { return mcomplex(this->__float__()); }
__ss_bool pyobj::__bool__() { return __mbool(__len__() != 0); }

__ss_int pyobj::__index__() { throw new TypeError(new str("no such method: '__index__'")); }

/* object */

object::object() { this->__class__ = cl_object; }

#ifdef __SS_BIND
PyObject *__ss__newobj__(PyObject *, PyObject *args, PyObject *kwargs) {
    /* used once per unpickled object (see extmod.do_reduce_setstate); the
     * PyObject_GetAttrString result is a new reference that was never
     * released, leaking the bound __new__ method every call. */
    PyObject *cls = PyTuple_GetItem(args, 0);
    PyObject *__new__ = PyObject_GetAttrString(cls, "__new__");
    if (!__new__)
        return NULL;
    PyObject *result = PyObject_Call(__new__, args, kwargs);
    Py_DECREF(__new__);
    return result;
}
#endif

/* slicing helper */

void slicenr(__ss_int x, __ss_int &l, __ss_int &u, __ss_int &s, __ss_int len) {
    if(x&4) {
        if (s == 0)
            __throw_slice_step_zero();
    } else
        s = 1;

    __ss_int neg_clamp = (s<0) ? -1 : 0; // out-of-range negative index: -1 sentinel for a reverse step, 0 otherwise
    if (l>=len)
        l = (s<0) ? len-1 : len; // last valid index for a reverse step, one-past-the-end otherwise
    else if (l<0) {
        l = len+l;
        if(l<0)
            l = neg_clamp;
    }
    if (u>=len)
        u = len;
    else if (u<0) {
        u = len+u;
        if(u<0)
            u = neg_clamp;
    }

    if(s<0) {
        if (!(x&1))
            l = len-1;
        if (!(x&2))
            u = -1;
        if(s < -(len+1))
            s = -(len+1); // magnitude beyond len can only ever affect one iteration; clamp so i+=s can't overflow
    }
    else {
        if (!(x&1))
            l = 0;
        if (!(x&2))
            u = len;
        if(s > len+1)
            s = len+1; // ditto
    }
}

void __adjust_indices(__ss_int &start, __ss_int &end, __ss_int len) {
    if(end > len)
        end = len;
    else if(end < 0) {
        end += len;
        if(end < 0)
            end = 0;
    }
    if(start < 0) {
        start += len;
        if(start < 0)
            start = 0;
    }
}

__ss_int __extslice_size(__ss_int x, __ss_int l, __ss_int u, __ss_int s, __ss_int len) {
    slicenr(x, l, u, s, len);
    if(l == u) return 0;
    if(s > 0 && u < l) return 0;
    if(s < 0 && l < u) return 0;
    __ss_int slicelen = __abs(u-l);
    __ss_int absstep = __abs(s);
    __ss_int slicesize = slicelen/absstep;
    if(slicelen%absstep) slicesize += 1;
    return slicesize;
}

/* tuple caching */

tuple<__ss_int >*__ss_tuple_int(__ss_int, __ss_int a, __ss_int b) {
    if(-20 <= a && a < 20 && -20 <= b && b < 20)
        return __ss_tuple_cache[(a+20)*40+(b+20)];
    else
        return new tuple<__ss_int>(2, a, b);
}


} // namespace __shedskin__
