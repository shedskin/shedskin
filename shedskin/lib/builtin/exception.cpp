/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

/* Exceptions */

/* a plain OSError('msg') has no errno (as in CPython); for a failed call
   that did set errno, use __throw_oserror() instead */
OSError::OSError(str *fname) {
    this->__class__ = cl_oserror;
    __init_errno(0, fname);
}
void OSError::__init_errno(int e, str *fname) {
    this->filename = fname;
    this->filename2 = 0;
    __ss_errno = e;
    strerror = e ? new str(::strerror(e)) : 0;
    message = this->__str__();
}
str *OSError::__str__() {
    if(!__ss_errno) /* e.g. user-raised OSError('msg') */
        return filename ? filename : __ss_empty_str;
    if(!filename)
        return __add_strs(4, new str("[Errno "), __str(__ss_errno), new str("] "), strerror);
    return __add_strs(7, new str("[Errno "), __str(__ss_errno), new str("] "), strerror, new str(": '"), filename, new str("'"));
}
str *OSError::__repr__() {
    if(!__ss_errno)
        return __add_strs(4, this->__class__->__name__, new str("("), filename ? repr(filename) : __ss_empty_str, new str(")"));
    return __add_strs(5, this->__class__->__name__, new str("("), __str(__ss_errno), new str(", '"), strerror, new str("')"));
}

/* errno is snapshotted by the caller, as allocation may clobber it */
template<class T> [[noreturn]] static void __throw_errno(int e, str *fname) {
    T *exc = new T(fname);
    exc->__init_errno(e, fname);
    throw exc;
}

/* errno to OSError subclass mapping, following CPython (PEP 3151) */
void __throw_oserror(str *fname) {
    int e = errno;
    if(e == EAGAIN)
        __throw_errno<BlockingIOError>(e, fname);
#ifdef EALREADY
    if(e == EALREADY)
        __throw_errno<BlockingIOError>(e, fname);
#endif
#ifdef EINPROGRESS
    if(e == EINPROGRESS)
        __throw_errno<BlockingIOError>(e, fname);
#endif
#ifdef EWOULDBLOCK
    if(e == EWOULDBLOCK)
        __throw_errno<BlockingIOError>(e, fname);
#endif
    if(e == EPIPE)
        __throw_errno<BrokenPipeError>(e, fname);
#ifdef ESHUTDOWN
    if(e == ESHUTDOWN)
        __throw_errno<BrokenPipeError>(e, fname);
#endif
    if(e == ECHILD)
        __throw_errno<ChildProcessError>(e, fname);
#ifdef ECONNABORTED
    if(e == ECONNABORTED)
        __throw_errno<ConnectionAbortedError>(e, fname);
#endif
#ifdef ECONNREFUSED
    if(e == ECONNREFUSED)
        __throw_errno<ConnectionRefusedError>(e, fname);
#endif
#ifdef ECONNRESET
    if(e == ECONNRESET)
        __throw_errno<ConnectionResetError>(e, fname);
#endif
    if(e == EEXIST)
        __throw_errno<FileExistsError>(e, fname);
    if(e == ENOENT)
        __throw_errno<FileNotFoundError>(e, fname);
    if(e == EISDIR)
        __throw_errno<IsADirectoryError>(e, fname);
    if(e == ENOTDIR)
        __throw_errno<NotADirectoryError>(e, fname);
    if(e == EINTR)
        __throw_errno<InterruptedError>(e, fname);
    if(e == EACCES || e == EPERM)
        __throw_errno<PermissionError>(e, fname);
#ifdef ENOTCAPABLE
    if(e == ENOTCAPABLE)
        __throw_errno<PermissionError>(e, fname);
#endif
    if(e == ESRCH)
        __throw_errno<ProcessLookupError>(e, fname);
#ifdef ETIMEDOUT
    if(e == ETIMEDOUT)
        __throw_errno<TimeoutError>(e, fname);
#endif
    __throw_errno<OSError>(e, fname);
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
    this->_object = object;
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

/* SystemExit */

SystemExit::SystemExit(__ss_int c) {
        this->__class__ = cl_systemexit;
        this->code = c;
        this->message = __str(this->code);
        this->show_message = 0;
}

SystemExit::SystemExit() {
        this->__class__ = cl_systemexit;
        this->code = 0;
        this->message = __str(this->code);
        this->show_message = 0;
}

SystemExit::SystemExit(str *msg) : BaseException(msg) {
        this->__class__ = cl_systemexit;
        this->code = 1;
        this->show_message = 1;
}
