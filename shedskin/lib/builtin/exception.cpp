/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

/* Exceptions */

/* a plain OSError('msg') has no errno, strerror or filename (as in CPython):
   msg is just the message, as for other exceptions. for a failed call that
   did set errno, use __throw_oserror() instead */
OSError::OSError(str *msg) : Exception(msg) {
    this->__class__ = cl_oserror;
    __ss_errno = 0;
    strerror = 0;
    filename = filename2 = 0;
}
/* OSError(errno, strerror[, filename[, winerror[, filename2]]]) */
OSError::OSError(__ss_int e, str *strerror, str *filename, void *, str *filename2) : Exception(0) {
    this->__class__ = cl_oserror;
    __ss_errno = e;
    this->strerror = strerror;
    this->filename = filename;
    this->filename2 = filename2;
    message = this->__str__();
}
void OSError::__init_errno(int e, str *fname, str *fname2) {
    this->filename = fname;
    this->filename2 = fname2;
    __ss_errno = e;
    strerror = e ? new str(::strerror(e)) : 0;
    message = this->__str__();
}
str *OSError::__str__() {
    /* as CPython: a filename (also one set afterwards, as e.filename = ..)
       gives the long form, with None for a missing strerror */
    if(!strerror && !filename) /* e.g. user-raised OSError('msg') */
        return BaseException::__str__();
    str *s = strerror ? strerror : new str("None");
    if(!filename)
        return __add_strs(4, new str("[Errno "), __str(__ss_errno), new str("] "), s);
    if(!filename2)
        return __add_strs(6, new str("[Errno "), __str(__ss_errno), new str("] "), s, new str(": "), repr(filename));
    return __add_strs(8, new str("[Errno "), __str(__ss_errno), new str("] "), s, new str(": "), repr(filename), new str(" -> "), repr(filename2));
}
str *OSError::__repr__() {
    if(!strerror)
        return BaseException::__repr__();
    return __add_strs(5, this->__class__->__name__, new str("("), __str(__ss_errno), new str(", "), repr(strerror), new str(")"));
}

#ifdef __SS_BIND
/* OSError(errno, strerror, filename, winerror, filename2), so CPython sets
   the attributes and str() as for its own OSError (1025-B9) */
PyObject *OSError::__py_args__() {
    if(!strerror)
        return 0; /* use message */
    if(!filename)
        return Py_BuildValue("(iN)", (int)__ss_errno, __to_py(strerror));
    return Py_BuildValue("(iNNON)", (int)__ss_errno, __to_py(strerror), __to_py(filename), Py_None, __to_py(filename2));
}
#endif

/* errno is snapshotted by the caller, as allocation may clobber it */
template<class T> [[noreturn]] static void __throw_errno(int value, str *fname, str *fname2, str *strerror_) {
    T *exc = new T(); /* (thrown as T *, so 'catch (T *)' works) */
    exc->__init_errno(value, fname, fname2);
    if(strerror_) {
        exc->strerror = strerror_;
        exc->message = exc->__str__();
    }
    throw exc;
}

void __throw_oserror(str *fname, str *fname2) {
    int e = errno;
    __throw_oserror_errno(e, e, 0, fname, fname2);
}

/* errno to OSError subclass mapping, following CPython (PEP 3151): errno
   'value' (and strerror, default strerror(value)), as the subclass for
   errno e (socket.cpp: e differs for winsock codes) */
void __throw_oserror_errno(int value, int e, str *strerror_, str *fname, str *fname2) {
    if(e == EAGAIN)
        __throw_errno<BlockingIOError>(value, fname, fname2, strerror_);
#ifdef EALREADY
    if(e == EALREADY)
        __throw_errno<BlockingIOError>(value, fname, fname2, strerror_);
#endif
#ifdef EINPROGRESS
    if(e == EINPROGRESS)
        __throw_errno<BlockingIOError>(value, fname, fname2, strerror_);
#endif
#ifdef EWOULDBLOCK
    if(e == EWOULDBLOCK)
        __throw_errno<BlockingIOError>(value, fname, fname2, strerror_);
#endif
    if(e == EPIPE)
        __throw_errno<BrokenPipeError>(value, fname, fname2, strerror_);
#ifdef ESHUTDOWN
    if(e == ESHUTDOWN)
        __throw_errno<BrokenPipeError>(value, fname, fname2, strerror_);
#endif
    if(e == ECHILD)
        __throw_errno<ChildProcessError>(value, fname, fname2, strerror_);
#ifdef ECONNABORTED
    if(e == ECONNABORTED)
        __throw_errno<ConnectionAbortedError>(value, fname, fname2, strerror_);
#endif
#ifdef ECONNREFUSED
    if(e == ECONNREFUSED)
        __throw_errno<ConnectionRefusedError>(value, fname, fname2, strerror_);
#endif
#ifdef ECONNRESET
    if(e == ECONNRESET)
        __throw_errno<ConnectionResetError>(value, fname, fname2, strerror_);
#endif
    if(e == EEXIST)
        __throw_errno<FileExistsError>(value, fname, fname2, strerror_);
    if(e == ENOENT)
        __throw_errno<FileNotFoundError>(value, fname, fname2, strerror_);
    if(e == EISDIR)
        __throw_errno<IsADirectoryError>(value, fname, fname2, strerror_);
    if(e == ENOTDIR)
        __throw_errno<NotADirectoryError>(value, fname, fname2, strerror_);
    if(e == EINTR)
        __throw_errno<InterruptedError>(value, fname, fname2, strerror_);
    if(e == EACCES || e == EPERM)
        __throw_errno<PermissionError>(value, fname, fname2, strerror_);
#ifdef ENOTCAPABLE
    if(e == ENOTCAPABLE)
        __throw_errno<PermissionError>(value, fname, fname2, strerror_);
#endif
    if(e == ESRCH)
        __throw_errno<ProcessLookupError>(value, fname, fname2, strerror_);
#ifdef ETIMEDOUT
    if(e == ETIMEDOUT)
        __throw_errno<TimeoutError>(value, fname, fname2, strerror_);
#endif
    __throw_errno<OSError>(value, fname, fname2, strerror_);
}

/* Unicode errors: str() follows CPython's formatting exactly, singling
   out a single-unit range ("byte 0x.. in position n" / "character '..'
   in position n") from a wider one ("bytes/characters in position a-b"). */

static str *__unicode_char_escape(__ss_char cp) { /* \xhh, \uhhhh, \Uhhhhhhhh, as CPython */
    char buf[16];
    if (cp < 0x100)
        snprintf(buf, sizeof(buf), "\\x%02x", (unsigned int)cp);
    else if (cp < 0x10000)
        snprintf(buf, sizeof(buf), "\\u%04x", (unsigned int)cp);
    else
        snprintf(buf, sizeof(buf), "\\U%08x", (unsigned int)cp);
    return new str(buf);
}

static str *__unicode_range(__ss_int start, __ss_int end) { /* "a-b" (end inclusive, as CPython) */
    return __add_strs(3, __str(start), new str("-"), __str(end - 1));
}

UnicodeDecodeError::UnicodeDecodeError(str *encoding, bytes *object, __ss_int start, __ss_int end, str *reason) {
    this->__class__ = cl_unicodedecodeerror;
    this->encoding = encoding;
    this->_object = object->frozen ? object : new bytes(object); /* as cpython: always a bytes copy */
    this->start = start;
    this->end = end;
    this->reason = reason;
    this->message = this->__str__();
    this->args->units.push_back(this->message);
}

str *UnicodeDecodeError::__str__() {
    if (end == start + 1 && start >= 0 && (size_t)start < _object->unit.size()) {
        char buf[8];
        snprintf(buf, sizeof(buf), "0x%02x", (unsigned int)(unsigned char)_object->unit[(size_t)start]);
        return __add_strs(7, new str("'"), encoding, new str("' codec can't decode byte "), new str(buf), new str(" in position "), __str(start), __add_strs(2, new str(": "), reason));
    }
    return __add_strs(6, new str("'"), encoding, new str("' codec can't decode bytes in position "), __unicode_range(start, end), new str(": "), reason);
}

str *UnicodeDecodeError::__repr__() {
    return __add_strs(11, new str("UnicodeDecodeError("), repr(encoding), new str(", "), repr(_object), new str(", "), __str(start), new str(", "), __str(end), new str(", "), repr(reason), new str(")"));
}

UnicodeEncodeError::UnicodeEncodeError(str *encoding, str *object, __ss_int start, __ss_int end, str *reason) {
    this->__class__ = cl_unicodeencodeerror;
    this->encoding = encoding;
    this->_object = object;
    this->start = start;
    this->end = end;
    this->reason = reason;
    this->message = this->__str__();
    this->args->units.push_back(this->message);
}

str *UnicodeEncodeError::__str__() {
    if (end == start + 1 && start >= 0 && (size_t)start < _object->unit.size())
        return __add_strs(8, new str("'"), encoding, new str("' codec can't encode character '"), __unicode_char_escape(_object->unit[(size_t)start]), new str("' in position "), __str(start), new str(": "), reason);
    return __add_strs(6, new str("'"), encoding, new str("' codec can't encode characters in position "), __unicode_range(start, end), new str(": "), reason);
}

str *UnicodeEncodeError::__repr__() {
    return __add_strs(11, new str("UnicodeEncodeError("), repr(encoding), new str(", "), repr(_object), new str(", "), __str(start), new str(", "), __str(end), new str(", "), repr(reason), new str(")"));
}

UnicodeTranslateError::UnicodeTranslateError(str *object, __ss_int start, __ss_int end, str *reason) {
    this->__class__ = cl_unicodetranslateerror;
    this->_object = object;
    this->start = start;
    this->end = end;
    this->reason = reason;
    this->message = this->__str__();
    this->args->units.push_back(this->message);
}

str *UnicodeTranslateError::__str__() {
    if (end == start + 1 && start >= 0 && (size_t)start < _object->unit.size())
        return __add_strs(6, new str("can't translate character '"), __unicode_char_escape(_object->unit[(size_t)start]), new str("' in position "), __str(start), new str(": "), reason);
    return __add_strs(4, new str("can't translate characters in position "), __unicode_range(start, end), new str(": "), reason);
}

str *UnicodeTranslateError::__repr__() {
    return __add_strs(9, new str("UnicodeTranslateError("), repr(_object), new str(", "), __str(start), new str(", "), __str(end), new str(", "), repr(reason), new str(")"));
}

#ifdef __SS_BIND
PyObject *UnicodeDecodeError::__py_args__() {
    return Py_BuildValue("sNnns", encoding->c_str(), __to_py(_object), (Py_ssize_t)start, (Py_ssize_t)end, reason->c_str());
}
PyObject *UnicodeEncodeError::__py_args__() {
    return Py_BuildValue("sNnns", encoding->c_str(), __to_py(_object), (Py_ssize_t)start, (Py_ssize_t)end, reason->c_str());
}
PyObject *UnicodeTranslateError::__py_args__() {
    return Py_BuildValue("Nnns", __to_py(_object), (Py_ssize_t)start, (Py_ssize_t)end, reason->c_str());
}
#endif

void __throw_index_out_of_range(const char *msg) {
    throw new IndexError(new str(msg));
}
void __throw_range_step_zero() {
    throw new ValueError(new str("range() step argument must not be zero"));
}
void __throw_set_changed() {
    throw new RuntimeError(new str("set changed size during iteration"));
}
void __throw_dict_changed() {
    throw new RuntimeError(new str("dict changed size during iteration"));
}
void __throw_slice_step_zero() {
    throw new ValueError(new str("slice step cannot be zero"));
}
void __throw_stop_iteration() {
    throw new StopIteration();
}
void __throw_zero_division(const char *msg) {
    throw new ZeroDivisionError(new str(msg));
}
void __throw_pow_overflow() {
    throw new OverflowError(new str("(34, 'Numerical result out of range')")); /* as CPython (ERANGE) */
}
void __ss_repeat_error(size_t len, __ss_int n, const char *too_long) {
    if (too_long && (__ss_uint)n > (size_t)PTRDIFF_MAX / len)
        throw new OverflowError(new str(too_long));
    throw new MemoryError();
}

/* BaseException */

BaseException::BaseException(str *msg) {
    this->__class__ = cl_baseexception;
    this->__notes__ = 0;
    __init__(msg);
}

void *BaseException::add_note(str *note) {
    if(!__notes__)
        __notes__ = new list<str *>();
    __notes__->append(note);
    return NULL;
}

void BaseException::__init__(str *msg) {
    this->message = msg;
    this->args = new tuple<str *>();
    if(msg)
        this->args->units.push_back(msg);
}

str *BaseException::__str__() {
    if(len(this->args) > 0)
        return args->__getitem__(0);
    else
        return __ss_empty_str;
}

str *BaseException::__repr__() {
    if(len(this->args) > 0)
        return __add_strs(4, this->__class__->__name__, new str("("), repr(args->__getitem__(0)), new str(")"));
    else
        return __add_strs(2, this->__class__->__name__, new str("()"));
}

/* KeyError */

str *KeyError::__str__() {
    /* as in CPython, a single argument (the key) is repr'd */
    if(key_repr)
        return key_repr;
    if(len(this->args) == 1)
        return repr(args->__getitem__(0));
    return BaseException::__str__();
}

str *KeyError::__repr__() {
    if(key_repr)
        return __add_strs(4, this->__class__->__name__, new str("("), key_repr, new str(")"));
    return BaseException::__repr__();
}

#ifdef __SS_BIND
PyObject *KeyError::__py_args__() {
    if(key_to_py)
        return Py_BuildValue("(N)", key_to_py(key)); /* N: steals the new reference */
    return 0; /* use message */
}
#endif

/* SystemExit */

SystemExit::SystemExit(__ss_int c) : BaseException(__str(c)) {
        this->__class__ = cl_systemexit;
        this->code = c;
        this->show_message = 0;
        this->int_code = 1;
}

SystemExit::SystemExit() {
        this->__class__ = cl_systemexit;
        this->code = 0; /* code is None in cpython; no args, so str() is '' */
        this->show_message = 0;
        this->int_code = 0;
}

SystemExit::SystemExit(str *msg) : BaseException(msg) {
        this->__class__ = cl_systemexit;
        this->code = 1;
        this->show_message = 1;
        this->int_code = 0;
}

str *SystemExit::__repr__() {
    if(int_code) /* SystemExit(7), not SystemExit('7') */
        return __add_strs(4, this->__class__->__name__, new str("("), this->message, new str(")"));
    return BaseException::__repr__();
}

#ifdef __SS_BIND
PyObject *SystemExit::__py_args__() {
    if(int_code) /* SystemExit(7), not SystemExit('7') */
        return Py_BuildValue("(N)", __to_py(code)); /* N: steals the new reference */
    if(!show_message) /* plain SystemExit: no args, so code is None */
        return PyTuple_New(0);
    return 0; /* use message */
}
#endif
