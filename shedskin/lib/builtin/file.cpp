/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* system headers are included at the top of builtin.cpp, outside namespace __shedskin__ */

/* Reject directories opened as regular files: on POSIX, fopen() succeeds on
 * a directory path, but subsequent reads/writes through the FILE* invoke
 * undefined behavior (observed as a segfault) instead of failing cleanly.
 * CPython's io layer proactively stat()s the path and raises
 * IsADirectoryError; mirror that here. */
static inline void __check_not_directory(FILE *f, str *file_name) {
#ifndef WIN32
    if (f) {
        struct stat st;
        if (fstat(fileno(f), &st) == 0 and S_ISDIR(st.st_mode)) {
            fclose(f);
            errno = EISDIR;
            __throw_oserror(file_name);
        }
    }
#endif
}

#if (_POSIX_C_SOURCE >= 1 or _XOPEN_SOURCE or _POSIX_SOURCE or _BSD_SOURCE or _SVID_SOURCE) and (_BSD_SOURCE or _SVID_SOURCE)
#define HAVE_STDIO_UNLOCKED
#endif

#ifndef HAVE_STDIO_UNLOCKED
#define GETC   getc
#define FWRITE fwrite
#define FFLUSH fflush
#define FERROR ferror
#define FEOF   feof
#else // HAVE_STDIO_UNLOCKED
#define GETC   getc_unlocked
#define FWRITE fwrite_unlocked
#define FFLUSH fflush_unlocked
#define FERROR ferror_unlocked
#define FEOF   feof_unlocked
#endif // HAVE_STDIO_UNLOCKED

/* the msvc crt calls its invalid parameter handler, which by default
   terminates the process (0xc0000409), when fflush/fwrite/fclose meet a bad file
   descriptor, e.g. after os.close(f.fileno()). like cpython
   (_Py_BEGIN_SUPPRESS_IPH), suppress it so these fail with EBADF instead */
#ifdef _MSC_VER
static void __ss_file_noop_iph(const wchar_t *, const wchar_t *, const wchar_t *, unsigned int, uintptr_t) {}
struct __ss_file_suppress_iph {
    _invalid_parameter_handler old;
    __ss_file_suppress_iph() { old = _set_thread_local_invalid_parameter_handler(__ss_file_noop_iph); }
    ~__ss_file_suppress_iph() { _set_thread_local_invalid_parameter_handler(old); }
};
static int __ss_fflush(FILE *f) {
    __ss_file_suppress_iph guard;
    return fflush(f);
}
static size_t __ss_fwrite(const void *buf, size_t size, size_t n, FILE *f) {
    __ss_file_suppress_iph guard;
    return fwrite(buf, size, n, f);
}
#undef FFLUSH
#define FFLUSH __ss_fflush
#undef FWRITE
#define FWRITE __ss_fwrite
#else
struct __ss_file_suppress_iph { __ss_file_suppress_iph() {} };
#endif

/* as CPython: most file methods end the closed-file message with a period,
   the ones inherited from io.IOBase (fileno, isatty, readable..) do not.
   (StringIO, GzipFile.. use the header's __check_closed(), without one) */
#define __SS_CLOSED_MSG "I/O operation on closed file."
#define __SS_CLOSED_MSG_IOBASE "I/O operation on closed file"

/* flush and close even when flushing fails, as CPython; returns the first
   errno (0 on success), leaving it in errno. this is a free function, as on
   macOS errno expands to (*__error()), which file::__error would shadow */
static int __ss_fclose(FILE *f, bool closefd=true) {
    __ss_file_suppress_iph guard;
    /* (fflush() of a reading stream seeks the fd back to the stream position) */
    off_t offset_before = closefd ? -1 : ::lseek(fileno(f), 0, SEEK_CUR);
    int err = FFLUSH(f) ? errno : 0;
    /* closefd=False: there is no portable way to free a FILE * but not its
       fd, so let fclose() close a copy, and move that back in place */
    int fd = -1, saved = -1;
    off_t offset = -1;
#ifndef WIN32
    int fdflags = -1;
#endif
    if(!closefd) {
        fd = fileno(f);
        /* as CPython, the fd stays where reading/writing left it (fclose()
           would move it back to the stream position), and keeps FD_CLOEXEC
           (which dup2() clears) */
        offset = std::max(offset_before, ::lseek(fd, 0, SEEK_CUR)); /* (read ahead, or written) */
#ifndef WIN32
        fdflags = ::fcntl(fd, F_GETFD);
#endif
        saved = ::dup(fd);
        if(saved == -1) { /* leave the FILE * open rather than the fd closed */
            errno = err;
            return err;
        }
    }
    if(fclose(f) and not err and closefd)
        err = errno;
    if(saved != -1) {
        ::dup2(saved, fd);
        ::close(saved);
#ifndef WIN32
        if(fdflags != -1)
            ::fcntl(fd, F_SETFD, fdflags);
#endif
        if(offset != -1)
            ::lseek(fd, offset, SEEK_SET);
    }
    errno = err;
    return err;
}

static void __check_closefd(str *flags, __ss_int closefd) {
    if(!closefd) { /* (as cpython: after the mode check) */
        if(flags)
            __check_open_mode(flags);
        throw new ValueError(new str("Cannot use closefd=False with file name"));
    }
}

/* validate a mode as cpython's io.open does, before anything is opened:
   fopen() would otherwise pick the first of 'rwa' and ignore much of the
   rest, so that e.g. open(f, 'wa') silently truncates f */
void __check_open_mode(str *mode) {
    if (!mode)
        return;
    bool seen[7] = {}; /* x r w a + t b */
    for (char32_t c : mode->unit) {
        int i;
        switch (c) {
            case 'x': i = 0; break;
            case 'r': i = 1; break;
            case 'w': i = 2; break;
            case 'a': i = 3; break;
            case '+': i = 4; break;
            case 't': i = 5; break;
            case 'b': i = 6; break;
            default: i = -1;
        }
        if (i == -1 || seen[i])
            throw new ValueError(__add_strs(3, new str("invalid mode: '"), mode, new str("'")));
        seen[i] = true;
    }
    if (seen[5] && seen[6])
        throw new ValueError(new str("can't have text and binary mode at once"));
    int kinds = seen[0] + seen[1] + seen[2] + seen[3];
    if (kinds > 1)
        throw new ValueError(new str("must have exactly one of create/read/write/append mode"));
    if (kinds == 0)
        throw new ValueError(new str("Must have exactly one of create/read/write/append mode and at most one plus"));
}

/* rewrite a (validated) mode for C fopen()/fdopen(): these need one of 'rwa'
   first (so e.g. 'br' becomes 'rb'), and C11 only accepts 'x' as a trailing
   modifier of a 'w' mode (e.g. 'x+' becomes 'w+x'; without excl, as for
   fdopen(), it is dropped) */
str *__c_open_mode(str *mode, bool excl) {
    const auto &u = mode->unit;
    bool x = u.find('x') != std::string::npos;
    str *m = new str(x ? "w" : u.find('r') != std::string::npos ? "r" : u.find('w') != std::string::npos ? "w" : "a");
    if (u.find('+') != std::string::npos)
        m->unit += '+';
    if (u.find('b') != std::string::npos)
        m->unit += 'b';
    if (x && excl)
        m->unit += 'x';
    return m;
}

/* the .mode of a binary file, as cpython's FileIO.mode: one of 'rb', 'wb',
   'ab' or 'xb', plus '+' when it is also writable/readable (so 'br' becomes
   'rb', and 'w+b' becomes 'rb+'). a text file keeps the mode as given */
str *__fileio_mode(str *mode) {
    const auto &u = mode->unit;
    bool plus = u.find('+') != std::string::npos;
    if (u.find('x') != std::string::npos)
        return new str(plus ? "xb+" : "xb");
    if (u.find('a') != std::string::npos)
        return new str(plus ? "ab+" : "ab");
    if (plus)
        return new str("rb+");
    return new str(u.find('r') != std::string::npos ? "rb" : "wb");
}

static FILE *__ss_fopen(str *file_name, str *flags) {
    flags = __c_open_mode(flags, true);
    /* like cpython (PEP 446): the file descriptor is non-inheritable */
#ifdef WIN32
    return _wfopen(__ss_wpath(file_name).c_str(), (__ss_wpath(flags) + L"N").c_str());
#else
    FILE *f = fopen(__ss_cpath(file_name), flags->c_str());
    if (f) {
        int fd = fileno(f);
        int fd_flags = fcntl(fd, F_GETFD);
        if (fd_flags != -1)
            fcntl(fd, F_SETFD, fd_flags | FD_CLOEXEC);
    }
    return f;
#endif
}

/* open(.., buffering): 0 means unbuffered (binary only), 1 line buffered
   (text only: in binary mode cpython warns and uses the default), n > 1 a
   buffer of n bytes (a hint: glibc picks its own size), and < 0 the default.
   setvbuf() must come before any other operation on the stream */
void __set_buffering(FILE *f, __ss_int buffering, bool text) {
    if (buffering == 0)
        setvbuf(f, NULL, _IONBF, 0);
    else if (buffering == 1) {
        if (text)
            setvbuf(f, NULL, _IOLBF, BUFSIZ);
    } else if (buffering > 1)
        setvbuf(f, NULL, _IOFBF, (size_t)std::min<__ss_int>(buffering, INT_MAX));
}

/* encoding, errors and newline, as for open() and os.fdopen() */
void file::__init_text(str *encoding, str *errors, str *newline) {
    options.universal_mode = true;
    /* 'locale' is no codec, but asks for the locale encoding: as in utf-8
       mode (shedskin's model, and CPython 3.15's default), utf-8 */
    if (encoding && encoding->unit == U"locale")
        encoding = new str("UTF-8");
    __encoding = __lookup_encoding(encoding);
    __errors = __lookup_errors(errors);
    this->encoding = encoding ? encoding : new str("utf-8");
    this->errors = errors ? errors : new str("strict");

    /* the file is always opened in binary mode: we translate newlines
       ourselves. the C runtime's text mode (Windows) would translate '\r\n'
       a second time, stop at a ctrl-z, and make ftell() count every '\n' in
       its buffer as a '\r\n', also when it was a lone '\n' on disk */
#ifdef WIN32
    options.crlf_out = true; /* newline=None writes os.linesep */
#endif
    if (newline) {
        if (newline->unit.empty() || newline->unit == U"\n") {
            options.universal_mode = false;
            options.split_cr = newline->unit.empty();
            options.crlf_out = false;
        } else if (newline->unit == U"\r" || newline->unit == U"\r\n")
            throw new ValueError(__add_strs(3, new str("newline="), repr(newline), new str(" is not supported by shedskin (only None, '' and '\\n')")));
        else
            throw new ValueError(__add_strs(2, new str("illegal newline value: "), newline));
    }
}

/* buffering, a utf-8-sig bom and .buffer, once f is open (and name/mode set) */
void file::__init_opened(__ss_int buffering) {
    if (buffering == 0) { /* (as cpython: after opening, so 'w' truncates) */
        fclose(f);
        f = 0;
        throw new ValueError(new str("can't have unbuffered text I/O"));
    }
    __set_buffering(f, buffering, true);
    line_buffering = __mbool(buffering == 1);
    if (mode->unit.find('a') != std::string::npos) /* (as cpython, also for an fd: */
        fseek(f, 0, SEEK_END);                      /*  tell() and reads start at the end) */

    if (__encoding == __SS_ENC_UTF8_SIG) {
        __encoding = __SS_ENC_UTF8;
        __utf8_sig = true;
        __sig_reset();
    }

    __make_buffer();
}

/* utf-8-sig, after opening or seeking (as cpython, which resets the codec):
   at position 0, a read skips a leading bom, and without one a write adds it */
void file::__sig_reset() {
    __bom_pending = false;
    __bom_skipped = false;
    if (ftell(f) != 0)
        return;
    if (mode->unit.find_first_of(__gcs("r+")) != std::string::npos) {
        char head[3];
        bool bom = fread(head, 1, 3, f) == 3 && std::string_view(head, 3) == "\xef\xbb\xbf";
        fseek(f, bom ? 3 : 0, SEEK_SET); /* (also needed before a write) */
        if (bom) {
            __bom_skipped = true;
            return;
        }
    }
    __bom_pending = mode->unit.find_first_of(__gcs("wax+")) != std::string::npos;
}

file::file(str *file_name, str *flags, str *encoding, str *errors, str *newline, __ss_int buffering) : closed(False) {
    __check_open_mode(flags);
    __init_text(encoding, errors, newline); /* LookupError before touching the file */

    if (!flags)
        flags = __char_cache['r'];
    str *cflags = flags;
    if (cflags->unit.find('b') == std::string::npos)
        cflags = new str(cflags->unit + __gcs("b"));
    f = __ss_fopen(file_name, cflags);
    if(f == 0)
        __throw_oserror(file_name);
    __check_not_directory(f, file_name);
    name = file_name;
    mode = flags;
    __init_opened(buffering);
}

/* os.fdopen(): as cpython, a bad encoding, newline or buffering closes g
   (and so the fd), as io.open() closes its FileIO */
file::file(FILE *g, str *name, str *mode, str *encoding, str *errors, str *newline, __ss_int buffering) : name(name), mode(mode), f(g), buffer(0), closed(False) {
    try {
        __init_text(encoding, errors, newline);
    } catch (...) {
        fclose(f);
        f = 0;
        throw;
    }
    __init_opened(buffering);
}

file::file(FILE *g, str *name, str *mode) : name(name), mode(mode), f(g), buffer(0), closed(False) {
    if (g)
        __make_buffer();
}

/* the binary file as .buffer: it shares our FILE *, so it closes that by
   closing us (so e.g. a pipe is pclosed), and closing us marks it closed */
void file::__make_buffer() {
    buffer = new file_binary(f, name, mode);
    buffer->__text = this;
}

void file::__close_buffer() {
    if (buffer)
        buffer->closed = True;
}

file *open(str *name, str *flags, __ss_int buffering, str *encoding, str *errors, str *newline, __ss_int closefd) {
    __check_closefd(flags, closefd);
    return new file(name, flags, encoding, errors, newline, buffering);
}

file *open(bytes *name, str *flags, __ss_int buffering, str *encoding, str *errors, str *newline, __ss_int closefd) {
    __check_closefd(flags, closefd);
    return new file(new str(name->unit), flags, encoding, errors, newline, buffering);
}

/* open(fd) (and os.fdopen). CPython's name is the fd itself (an int) */
FILE *__ss_fdopen(__ss_int fd, str *mode) {
    __check_open_mode(mode);
    /* like CPython (io.open), an fd out of C int range is no fd */
    if(fd < INT_MIN || fd > INT_MAX)
        throw new TypeError(new str("expected str, bytes or os.PathLike object, not int"));
    if(fd < 0)
        throw new ValueError(new str("negative file descriptor"));
    /* C fdopen() does not know 'x' (and never creates or truncates). like
       open(), a text file is opened in binary mode: we translate newlines
       ourselves */
    str *cmode = __c_open_mode(mode, false);
    if(cmode->unit.find('b') == std::string::npos)
        cmode->unit += 'b';
    FILE* fp;
    {
        /* the msvc crt aborts (0xc0000409) on a bad fd, e.g. open(9999) */
        __ss_file_suppress_iph guard;
        fp = ::fdopen((int)fd, cmode->c_str());
    }
    if(fp == NULL)
        __throw_oserror();
    return fp;
}

file *open(__ss_int fd, str *flags, __ss_int buffering, str *encoding, str *errors, str *newline, __ss_int closefd) {
    if(!flags)
        flags = new str("r");
    file *f = new file(__ss_fdopen(fd, flags), __str(fd), flags, encoding, errors, newline, buffering);
    f->__closefd = closefd;
    return f;
}

/* decode the bytes collected in __read_cache, with the file's encoding */
str *file::__decode_cache() {
    str *s = new str();
    if (!__read_cache.empty())
        __decode_into(s->unit, &__read_cache[0], __read_cache.size(), __encoding, __errors, errors);
    return s;
}

/* after a '\r': take the '\n' of a '\r\n', if one follows. with
   errors='ignore', bytes that decode to nothing may come in between, as
   CPython translates newlines only after decoding: these are dropped either
   way (the '\r' is a sequence boundary, so they decode to nothing whatever
   follows). a cut-short utf-8 sequence may still be completed by the bytes
   after it, so look ahead (and push back) up to a whole sequence */
static bool __take_lf(FILE *f, __ss_encoding enc, __ss_errors err) {
    char la[4]; /* lookahead: (the start of) a single character */
    size_t m = 0;
    bool eof = false;
    if(err == __SS_ERR_IGNORE) {
        for(;;) {
            if(!eof && (!m || (m < sizeof(la) && !__ignored_prefix(la, m, enc, false) &&
                               __ignored_prefix(la, m, enc, true) == m))) { /* undecided: need more */
                int d = GETC(f);
                if(d != EOF) {
                    la[m++] = (char)d;
                    continue;
                }
                eof = true;
            }
            size_t k = m ? __ignored_prefix(la, m, enc, eof) : 0;
            if(!k)
                break;
            memmove(la, la + k, m - k);
            m -= k;
        }
    } else {
        int d = GETC(f);
        if(d != EOF)
            la[m++] = (char)d;
    }
    bool lf = m && la[0] == '\n';
    while(m > size_t(lf)) /* (more than the one byte of ungetc that C guarantees, see __give_back) */
        ungetc((unsigned char)la[--m], f);
    return lf;
}

/* universal newlines translate '\r\n' lazily: after a '\r', the next read
   skips a '\n' (so reading a line never blocks on the character after it).
   settle that before the file position is used or changed */
static void __settle_cr(FILE *f, __file_options &options, __ss_encoding enc, __ss_errors err) {
    if(options.cr) {
        options.cr = false;
        __take_lf(f, enc, err);
    }
}

/* universal newlines, after a '\r' (options.cr): whether byte c is the '\n'
   of a '\r\n', to be skipped. with errors='ignore', bytes that decode to
   nothing may come in between, as CPython translates newlines only after
   decoding: so then keep options.cr, and drop those bytes at the '\n'.
   (cr_at moves past bytes already known to decode to nothing) */
bool file::__skip_lf(int c, size_t &cr_at, __char_counter &cc, size_t n) {
    size_t len = __read_cache.size() - cr_at;
    if(len) {
        cr_at += __ignored_prefix(&__read_cache[cr_at], len, __encoding, false);
        len = __read_cache.size() - cr_at;
    }
    bool ignored = !len || __ignored_prefix(&__read_cache[cr_at], len, __encoding, true) == len;
    if(ignored && c == '\n') {
        options.cr = false;
        __read_cache.resize(cr_at);
        cc.cut(n);
        return true;
    }
    if(!ignored || c < 0x80 || __errors != __SS_ERR_IGNORE)
        options.cr = false;
    return false;
}

/* C stdio needs a file positioning call when switching between reading and
   writing the same stream (C11 7.21.5.3). glibc does not care, but macOS and
   windows lose or misplace the data otherwise */
static inline void __switch_op(FILE *f, __file_options &options, char op,
                               __ss_encoding enc=__SS_ENC_UTF8, __ss_errors err=__SS_ERR_STRICT) {
    if(options.last_op != op) {
        if(options.last_op && f) {
            __settle_cr(f, options, enc, err);
            fseek(f, 0, SEEK_CUR);
        }
        options.last_op = op;
    }
    /* as cpython, a read after hitting the end sees data appended since
       (the stdio eof flag is sticky, e.g. for glibc 2.28+) */
    if(op == 'r' && f)
        clearerr(f);
}

/* readable(), writable() and seekable(), as cpython: from the mode (also
   'rwb' for a socket), while seekable() asks the os, so it is False for a
   pipe, socket or terminal. on a closed file only the capabilities the mode
   has raise ValueError (as cpython's buffered reader/writer: a closed 'r'
   file is still just not writable) */
static inline __ss_bool __mode_readable(str *mode) {
    /* (a socket's makefile('') is read-only, as is anything without w, a or x) */
    return ___bool(mode && (mode->unit.find_first_of(__gcs("r+")) != std::string::npos ||
                            mode->unit.find_first_of(__gcs("wax")) == std::string::npos));
}
static inline __ss_bool __mode_writable(str *mode) {
    return ___bool(mode && mode->unit.find_first_of(__gcs("wax+")) != std::string::npos);
}
/* reading a file not opened for reading (or writing one not opened for
   writing) raises io.UnsupportedOperation, as cpython, instead of the EBADF
   the C library gives. objects without a mode (BytesIO, StringIO, sockets,
   pipes) are left alone */
static inline void __check_mode_readable(str *mode, const char *msg) {
    if(mode && !__mode_readable(mode))
        throw new UnsupportedOperation(new str(msg));
}
static inline void __check_mode_writable(str *mode, const char *msg) {
    if(mode && !__mode_writable(mode))
        throw new UnsupportedOperation(new str(msg));
}

str *__ss_backslashreplace_surrogates(str *s) {
    str *r = new str();
    char buf[8];
    for (__ss_char cp : s->unit) {
        if (cp >= 0xd800 && cp <= 0xdfff) {
            snprintf(buf, sizeof(buf), "\\u%04x", (unsigned)cp);
            for (char *p = buf; *p; p++)
                r->unit += (__ss_char)*p;
        } else
            r->unit += cp;
    }
    return r;
}

static bool __has_surrogate(str *s) {
    for (__ss_char cp : s->unit)
        if (cp >= 0xd800 && cp <= 0xdfff)
            return true;
    return false;
}

__ss_int file::write(str *s) {
    __ss_int size = -1;
    __check_closed(__SS_CLOSED_MSG);
    __check_mode_writable(mode, "not writable");
    __switch_op(f, options, 'w', __encoding, __errors);
    if(f) {
        if (__backslashreplace && __has_surrogate(s)) {
            size = (__ss_int)s->unit.size(); /* (characters written, as CPython: before escaping) */
            s = __ss_backslashreplace_surrogates(s);
        }
        __GC_BYTES b;
        if (__bom_pending) {
            __bom_pending = false;
            b = "\xef\xbb\xbf";
        }
        if (options.crlf_out && s->unit.find(U'\n') != std::string::npos) {
            str *t = new str();
            t->unit.reserve(s->unit.size() + 16);
            for (char32_t c : s->unit) {
                if (c == U'\n')
                    t->unit += U'\r';
                t->unit += c;
            }
            size = (__ss_int)s->unit.size(); /* (the untranslated characters) */
            s = t;
        }
        if (__encoding == __SS_ENC_UTF8 && __errors == __SS_ERR_SURROGATEESCAPE && b.empty())
            b = __to_utf8_se(s); /* fast path (standard streams) */
        else
            __encode_into(b, s, __encoding, __errors, errors);
        if(FWRITE(b.data(), 1, b.size(), f) != b.size() and __error())
            __throw_oserror();
        if (size < 0)
            size = (__ss_int)s->unit.size(); /* characters written, as CPython */
        /* as CPython: line buffering flushes everything after a '\n' or a
           '\r' (stdio's _IOLBF keeps what follows the last '\n') */
        if (line_buffering && s->unit.find_first_of(U"\n\r") != std::string::npos)
            if (FFLUSH(f))
                __throw_oserror();
    }
    return size;
}

void *file::writelines(pyiter<str *> *iter) {
    __check_closed(__SS_CLOSED_MSG);
    str *e;
    int __2;
    pyiter<str *> *__1;
    pyiter<str *>::for_in_loop __3;
    FOR_IN(e,iter,1,2,3)
        write(e);
    END_FOR
    return NULL;
}

static inline __ss_bool __fd_seekable(FILE *f);

/* as cpython: a pipe, socket or terminal is checked up front */
static inline void __check_seekable(FILE *f, const char *msg) {
    if(f && !__fd_seekable(f))
        throw new UnsupportedOperation(new str(msg));
}

__ss_int file::seek(__ss_int i, __ss_int w) {
    __check_closed(__SS_CLOSED_MSG);
    __check_seekable(f, "underlying stream is not seekable");
    /* text files only allow seeking to a tell() position or to the end, as
       in cpython */
    if(w == 1 && i != 0)
        throw new UnsupportedOperation(new str("can't do nonzero cur-relative seeks"));
    if(w == 2 && i != 0)
        throw new UnsupportedOperation(new str("can't do nonzero end-relative seeks"));
    if(w < 0 || w > 2)
        throw new ValueError(__add_strs(3, new str("invalid whence ("), __str(w), new str(", should be 0, 1 or 2)")));
    if(i < 0)
        throw new ValueError(__add_strs(2, new str("negative seek position "), __str(i)));
    if(f) {
        __settle_cr(f, options, __encoding, __errors);
        if(fseek(f, i, (int)w) == -1)
            __throw_oserror();
        if (__utf8_sig)
            __sig_reset();
        return tell(); /* the new absolute position */
    }
    return -1;
}

__ss_int file::tell() {
    __check_closed(__SS_CLOSED_MSG);
    __check_seekable(f, "underlying stream is not seekable");
    if(f) {
        __settle_cr(f, options, __encoding, __errors);
        long status = ftell(f);
        if(status == -1)
            __throw_oserror();
        if(__bom_skipped && status == 3) /* (as CPython: after the bom is 0) */
            status = 0;
        return __ss_int(status);
    }
    return -1;
}

/* text-mode read(n) and readline(n) mean n *characters* (as in CPython), so
   stop -- pushing the byte back -- when character n+1 begins (see
   __char_counter). */

/* .. and push back the trailing bytes of a truncated sequence that turned out
   not to fit. (this needs more than the one byte of pushback that ungetc
   guarantees; glibc and the bsds give us more) */
static void __give_back(FILE *f, __GC_VECTOR(char) &cache, size_t k) {
    while(k--) {
        ungetc((unsigned char)cache.back(), f);
        cache.pop_back();
    }
}

str *file::readline(__ss_int n) {
    __check_closed(__SS_CLOSED_MSG);
    __check_mode_readable(mode, "not readable");
    if(n != 0) /* (as cpython: tell() is 0 after a bom only until a read) */
        __bom_skipped = false;
    __switch_op(f, options, 'r', __encoding, __errors);
    __read_cache.clear();
    __char_counter cc(__encoding, __errors);
    if (options.universal_mode) {
        size_t cr_at = 0; /* __read_cache size after the latest '\r' */
        for(;;) {
            int c = GETC(f);
            if(c == EOF)
                break;
            if(options.cr && __skip_lf(c, cr_at, cc, size_t(n)))
                continue;
            if(cc.full(c, size_t(n))) { /* character n+1 starts: not ours */
                ungetc(c, f); /* raw byte, before any cr translation */
                break;
            }
            if(c == '\r') {
                options.cr = true;
                c = '\n';
                cr_at = __read_cache.size() + 1;
            }
            __read_cache.push_back((char)c);
            if(c == '\n')
                break;
        }
    } else {  /* If not universal mode, use the normal loop */
        for(;;) {
            const int c = GETC(f);
            if(c == EOF)
                break;
            if(cc.full(c, size_t(n))) {
                ungetc(c, f);
                break;
            }
            __read_cache.push_back((char)c);
            if(c == '\n')
                break;
            if(c == '\r' && options.split_cr) { /* '\r' or '\r\n' ends the line too */
                if(__take_lf(f, __encoding, __errors)) {
                    if(cc.chars < size_t(n))
                        __read_cache.push_back('\n');
                    else
                        ungetc('\n', f);
                }
                break;
            }
        }
    }
    __give_back(f, __read_cache, cc.excess(size_t(n)));
    if(__error())
        __throw_oserror();

    return __decode_cache();
}

static void __throw_io_error() {
    __throw_oserror();
}

str *file::read(__ss_int n) {
    __check_closed(__SS_CLOSED_MSG);
    __check_mode_readable(mode, "not readable");
    if(n != 0) /* (as cpython: tell() is 0 after a bom only until a read) */
        __bom_skipped = false;
    __switch_op(f, options, 'r', __encoding, __errors);
    __char_counter cc(__encoding, __errors);
    if (options.universal_mode) {
        __read_cache.clear();
        size_t cr_at = 0; /* __read_cache size after the latest '\r' */
        for(;;) {
            int c = GETC(f);
            if(c == EOF)
                break;
            if(options.cr && __skip_lf(c, cr_at, cc, size_t(n)))
                continue;
            if(cc.full(c, size_t(n))) { /* character n+1 starts: not ours */
                ungetc(c, f); /* raw byte, before any cr translation */
                break;
            }
            if(c == '\r') {
                options.cr = true;
                c = '\n';
                cr_at = __read_cache.size() + 1;
            }
            __read_cache.push_back((char)c);
        }
        __give_back(f, __read_cache, cc.excess(size_t(n)));
        if(__error())
            __throw_io_error();
        return __decode_cache();
    }
    if(n == 1) {
        const int c = GETC(f);
        if(FERROR(f) != 0) /* avoid virtual call */
            __throw_io_error();
        if(c == EOF)
            return new str();
        if(!(c & 0x80)) /* ascii fast path */
            return __char_cache[static_cast<unsigned char>(c)];
        ungetc(c, f); /* multi-byte character: take the generic path */
    } // other cases (n != 1):
    __read_cache.clear();
    for(;;) {
        const int c = GETC(f);
        if(c == EOF)
            break;
        if(cc.full(c, size_t(n))) {
            ungetc(c, f);
            break;
        }
        __read_cache.push_back((char)c);
    }
    __give_back(f, __read_cache, cc.excess(size_t(n)));
    if(__error())
        __throw_io_error();
    return __decode_cache();
}

list<str *> *file::readlines(__ss_int size_hint) {
    __check_closed(__SS_CLOSED_MSG);
    list<str *> *lines = new list<str *>();
    __ss_int total = 0;
    while(true) {
        str *line = readline();
        if(line->unit.empty())
            break;
        lines->append(line);
        total += len(line);
        if(size_hint > 0 && total > size_hint)
            break;
    }
    return lines;
}

void *file::close() {
    if(f and not closed) {
        int err = __ss_fclose(f, __closefd);
        closed = True;
        __close_buffer();
        if(err)
            __throw_oserror();
    }
    return NULL;
}

void *file::flush() {
    __check_closed(__SS_CLOSED_MSG);
    if(f)
        if(FFLUSH(f))
            __throw_oserror();
    return NULL;
}

static inline __ss_bool __fd_seekable(FILE *f) {
    if (!f)
        return False;
#ifdef WIN32
    /* the windows CRT's lseek() does not fail on a pipe or a character
       device (it just returns 0), so only a regular file is seekable */
    int fd = _fileno(f);
    struct _stat64 st;
    if (_fstat64(fd, &st) != 0 || (st.st_mode & _S_IFMT) != _S_IFREG)
        return False;
    return ___bool(_lseeki64(fd, 0, SEEK_CUR) != -1);
#else
    return ___bool(lseek(fileno(f), 0, SEEK_CUR) != -1);
#endif
}

__ss_int file::__ss_fileno() {
    __check_closed(__SS_CLOSED_MSG_IOBASE);
    if(f)
        return fileno(f);
    return -1;
}
__ss_bool file::isatty()
{
    __check_closed(__SS_CLOSED_MSG_IOBASE);
#ifdef WIN32
    return ___bool(_isatty((int)__ss_fileno()));
#else // WIN32
    return ___bool(::isatty((int)__ss_fileno()));
#endif // WIN32
}

__ss_bool file::readable() { if (!__mode_readable(mode)) return False; __check_closed(__SS_CLOSED_MSG_IOBASE); return True; }
__ss_bool file::writable() { if (!__mode_writable(mode)) return False; __check_closed(__SS_CLOSED_MSG_IOBASE); return True; }
__ss_bool file::seekable() { __check_closed(__SS_CLOSED_MSG_IOBASE); return __fd_seekable(f); }

__ss_int file::truncate() {
    __check_closed(__SS_CLOSED_MSG);
    __check_mode_writable(mode, "truncate");
    flush();
    /* (as cpython: the raw position, so a pipe gives ESPIPE) */
    __settle_cr(f, options, __encoding, __errors);
    long pos = ftell(f);
    if(pos == -1)
        __throw_oserror();
    if(__bom_skipped && pos == 3) /* (as tell()) */
        pos = 0;
    return truncate((__ss_int)pos);
}

/* (a negative size is EINVAL, as cpython) */
__ss_int file::truncate(__ss_int size) {
    __check_closed(__SS_CLOSED_MSG);
    __check_mode_writable(mode, "truncate");
    flush();
#ifdef WIN32
    if(_chsize((int)__ss_fileno(), size) == -1)
        __throw_oserror();
#else
    if(ftruncate((int)__ss_fileno(), size) == -1)
        __throw_oserror();
#endif
    return size;
}

str *file::__repr__() {
    return (new str("file '"))->__add__(name)->__add__(new str("'"));
}

file *file::__enter__() {
    __check_closed(__SS_CLOSED_MSG);
    return this;
}

void *file::__exit__() {
    close();
    return NULL;
}

bool file::__error() {
    return (FERROR(f) != 0);
}

bool file::__eof() {
    __check_closed(__SS_CLOSED_MSG); /* (before touching f, which may be fclosed) */
    return (FEOF(f) != 0);
}

__iter<str *> *file::__iter__() {
    __check_closed(__SS_CLOSED_MSG); /* (as cpython: IOBase.__iter__) */
    return this;
}

str *file::__next__() {
    __check_closed(__SS_CLOSED_MSG);
    str *line = readline(); /* (not the eof flag: data may have been appended) */
    if(!len(line))
        throw new StopIteration();
    return line;
}

/* file_binary TODO merge with file */

file_binary::file_binary(str *file_name, str *flags, __ss_int buffering) : closed(False) {
    __check_open_mode(flags);
    if (!flags)
        flags = __char_cache['r'];
    f = __ss_fopen(file_name, flags);
    if(f == 0)
        __throw_oserror(file_name);
    __check_not_directory(f, file_name);
    if (flags->unit.find('a') != std::string::npos)
        fseek(f, 0, SEEK_END); /* (as cpython: tell() and reads start at the end) */
    __set_buffering(f, buffering, false);
    name = file_name;
    mode = __fileio_mode(flags);
}

file_binary::file_binary(FILE *g, str *name, str *mode) : name(name), mode(mode ? __fileio_mode(mode) : 0), f(g), closed(False) {}

void __check_binary_args(str *encoding, str *errors, str *newline) {
    if (encoding)
        throw new ValueError(new str("binary mode doesn't take an encoding argument"));
    if (errors)
        throw new ValueError(new str("binary mode doesn't take an errors argument"));
    if (newline)
        throw new ValueError(new str("binary mode doesn't take a newline argument"));
}

file_binary *open_binary(str *name, str *flags, __ss_int buffering, str *encoding, str *errors, str *newline, __ss_int closefd) {
    __check_open_mode(flags); /* (as cpython: before the other arguments) */
    __check_binary_args(encoding, errors, newline);
    __check_closefd(flags, closefd);
    return new file_binary(name, flags, buffering);
}

file_binary *open_binary(bytes *name, str *flags, __ss_int buffering, str *encoding, str *errors, str *newline, __ss_int closefd) {
    __check_open_mode(flags); /* (as cpython: before the other arguments) */
    __check_binary_args(encoding, errors, newline);
    __check_closefd(flags, closefd);
    return new file_binary(new str(name->unit), flags, buffering);
}

file_binary *open_binary(__ss_int fd, str *flags, __ss_int buffering, str *encoding, str *errors, str *newline, __ss_int closefd) {
    if(!flags)
        flags = new str("rb");
    __check_open_mode(flags); /* (as cpython: before the other arguments) */
    __check_binary_args(encoding, errors, newline); /* (as cpython: the fd stays open) */
    FILE *fp = __ss_fdopen(fd, flags);
    __set_buffering(fp, buffering, false);
    file_binary *f = new file_binary(fp, __str(fd), flags);
    f->__closefd = closefd;
    return f;
}

__ss_int file_binary::write(bytes *s) {
    __ss_int size = -1;
    __check_mode_writable(mode, "write"); /* (as cpython, before the closed check) */
    __check_closed("write to closed file");
    __switch_op(f, options, 'w');
    if(f) {
        size_t s_size = s->unit.size();
        if(FWRITE(s->unit.data(), 1, s_size, f) != s_size and __error())
            __throw_oserror();
        size = (__ss_int)s_size;
    }
    return size;
}

void *file_binary::writelines(pyiter<bytes *> *iter) {
    __check_closed(__SS_CLOSED_MSG);
    bytes *e;
    int __2;
    pyiter<bytes *> *__1;
    pyiter<bytes *>::for_in_loop __3;
    FOR_IN(e,iter,1,2,3)
        write(e);
    END_FOR
    return NULL;
}

__ss_int file_binary::seek(__ss_int i, __ss_int w) {
    /* (as cpython, before the closed check; also SEEK_DATA/SEEK_HOLE where the os has them) */
    bool whence_ok = w >= 0 && w <= 2;
#ifdef SEEK_DATA
    whence_ok = whence_ok || w == SEEK_DATA;
#endif
#ifdef SEEK_HOLE
    whence_ok = whence_ok || w == SEEK_HOLE;
#endif
    if(!whence_ok)
        throw new ValueError(__add_strs(3, new str("whence value "), __str(w), new str(" unsupported")));
    __check_closed("seek of closed file");
    __check_seekable(f, "File or stream is not seekable.");
    if(f) {
        if(w > 2) { /* SEEK_DATA/SEEK_HOLE: stdio does not know them, so ask the fd (an absolute offset) */
            if(FFLUSH(f))
                __throw_oserror();
            off_t pos = ::lseek(fileno(f), (off_t)i, (int)w);
            if(pos == -1)
                __throw_oserror();
            i = (__ss_int)pos;
            w = SEEK_SET;
        }
        if(fseek(f, i, (int)w) == -1)
            __throw_oserror();
        return tell(); /* the new absolute position */
    }
    return -1;
}

__ss_int file_binary::tell() {
    __check_closed(__SS_CLOSED_MSG_IOBASE);
    if(f) {
        long status = ftell(f);
        if(status == -1)
            __throw_oserror();
        return __ss_int(status);
    }
    return -1;
}

bytes *file_binary::readline(__ss_int n) {
    __check_mode_readable(mode, "read"); /* (as cpython, before the closed check) */
    __check_closed("readline of closed file");
    __switch_op(f, options, 'r');
    __read_cache.clear();
    for(size_t i = 0; i < size_t(n); ++i) {
        const int c = GETC(f);
        if(c == EOF)
            break;
        __read_cache.push_back((char)c);
        if(c == '\n')
            break;
    }
    if(__error())
        __throw_oserror();

    bytes *b = new bytes(__read_cache.empty() ? "" : &__read_cache[0], __read_cache.size());
    b->frozen = 1;
    return b;
}

bytes *file_binary::read(__ss_int n) {
    if(n < -1)
        throw new ValueError(new str("read length must be non-negative or -1"));
    __check_mode_readable(mode, "read"); /* (as cpython, before the closed check) */
    __check_closed("read of closed file");
    __switch_op(f, options, 'r');
    if(n == 1) {
        const int c = GETC(f);
        if(FERROR(f) != 0) /* avoid virtual call */
            __throw_io_error();
        if(c != EOF)
            return new bytes(__GC_BYTES(1, (char)c));
        else
            return new bytes();
    } // other cases (n != 1):
    __read_cache.clear();
    for(size_t i = 0; i < size_t(n); ++i) {
        const int c = GETC(f);
        if(c == EOF)
            break;
        __read_cache.push_back((char)c);
    }
    if(__error())
        __throw_io_error();
    bytes *b = new bytes(__read_cache.empty() ? "" : &__read_cache[0], __read_cache.size());
    b->frozen = 1;
    return b;
}

/* (as BytesIO/GzipFile; b must be a bytearray, as array.array/memoryview
   are not supported) */
__ss_int file_binary::readinto(bytes *b) {
    if(b->frozen)
        throw new TypeError(new str("readinto() argument must be read-write bytes-like object, not bytes"));
    __check_mode_readable(mode, "read");
    __check_closed("readinto of closed file");
    bytes *data = read((__ss_int)b->unit.size());
    size_t n = data->unit.size();
    b->unit.replace(0, n, data->unit);
    return (__ss_int)n;
}

/* bytes already in the stdio buffer (0 if unknown), so read1() need not block */
static inline size_t __ss_freadahead(FILE *f) {
#if defined(__GLIBC__)
    return f->_IO_read_end > f->_IO_read_ptr ? (size_t)(f->_IO_read_end - f->_IO_read_ptr) : 0;
#elif defined(__APPLE__) || defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__)
    return f->_r > 0 ? (size_t)f->_r : 0;
#else
    (void)f;
    return 0;
#endif
}

/* as cpython: at most one read of the os, so a pipe or socket gives what is
   there (instead of waiting for n bytes or eof) */
bytes *file_binary::read1(__ss_int n) {
    __check_mode_readable(mode, "read1");
    __check_closed("read of closed file");
    if(n > 0 && __fd_seekable(f)) /* (a regular file: one big read gives all) */
        return read(n);
    __switch_op(f, options, 'r');
    __read_cache.clear();
    if(n != 0) {
        const int c = GETC(f); /* (blocks only until something is there) */
        if(c != EOF) {
            __read_cache.push_back((char)c);
            size_t avail = __ss_freadahead(f);
            if(n > 0)
                avail = std::min(avail, (size_t)(n - 1));
            for(size_t i = 0; i < avail; ++i) {
                const int d = GETC(f);
                if(d == EOF)
                    break;
                __read_cache.push_back((char)d);
            }
        }
        if(__error())
            __throw_io_error();
    }
    bytes *b = new bytes(__read_cache.empty() ? "" : &__read_cache[0], __read_cache.size());
    b->frozen = 1;
    return b;
}

__ss_int file_binary::readinto1(bytes *b) {
    if(b->frozen)
        throw new TypeError(new str("readinto() argument must be read-write bytes-like object, not bytes"));
    __check_mode_readable(mode, "read");
    __check_closed("readinto of closed file");
    bytes *data = read1((__ss_int)b->unit.size());
    size_t n = data->unit.size();
    b->unit.replace(0, n, data->unit);
    return (__ss_int)n;
}

list<bytes *> *file_binary::readlines(__ss_int size_hint) {
    __check_closed(__SS_CLOSED_MSG);
    list<bytes *> *lines = new list<bytes *>();
    __ss_int total = 0;
    while(true) {
        bytes *line = readline();
        if(line->unit.empty())
            break;
        lines->append(line);
        total += len(line);
        if(size_hint > 0 && total > size_hint)
            break;
    }
    return lines;
}

void *file_binary::close() {
    if(__text) { /* our text file owns the FILE * */
        __text->close();
        closed = True;
        return NULL;
    }
    if(f and not closed) {
        int err = __ss_fclose(f, __closefd);
        closed = True;
        if(err)
            __throw_oserror();
    }
    return NULL;
}

void *file_binary::flush() {
    __check_closed(__mode_writable(mode) ? "flush of closed file" : __SS_CLOSED_MSG);
    if(f)
        if(FFLUSH(f))
            __throw_oserror();
    return NULL;
}

__ss_int file_binary::__ss_fileno() {
    __check_closed(__SS_CLOSED_MSG_IOBASE);
    if(f)
        return fileno(f);
    return -1;
}
__ss_bool file_binary::isatty()
{
    __check_closed(__SS_CLOSED_MSG_IOBASE);
#ifdef WIN32
    return ___bool(_isatty((int)__ss_fileno()));
#else // WIN32
    return ___bool(::isatty((int)__ss_fileno()));
#endif // WIN32
}

__ss_bool file_binary::readable() { if (!__mode_readable(mode)) return False; __check_closed(__SS_CLOSED_MSG_IOBASE); return True; }
__ss_bool file_binary::writable() { if (!__mode_writable(mode)) return False; __check_closed(__SS_CLOSED_MSG_IOBASE); return True; }
__ss_bool file_binary::seekable() { __check_closed(__SS_CLOSED_MSG_IOBASE); return __fd_seekable(f); }

__ss_int file_binary::truncate() {
    __check_closed("truncate of closed file");
    __check_mode_writable(mode, "truncate");
    flush();
    return truncate(tell());
}

/* (a negative size is EINVAL, as cpython) */
__ss_int file_binary::truncate(__ss_int size) {
    __check_closed("truncate of closed file");
    __check_mode_writable(mode, "truncate");
    flush();
#ifdef WIN32
    if(_chsize((int)__ss_fileno(), size) == -1)
        __throw_oserror();
#else
    if(ftruncate((int)__ss_fileno(), size) == -1)
        __throw_oserror();
#endif
    return size;
}

str *file_binary::__repr__() {
    return (new str("file '"))->__add__(name)->__add__(new str("'"));
}

file_binary *file_binary::__enter__() {
    __check_closed(__SS_CLOSED_MSG);
    return this;
}

void *file_binary::__exit__() {
    close();
    return NULL;
}

bool file_binary::__error() {
    return (FERROR(f) != 0);
}

bool file_binary::__eof() {
    __check_closed(__SS_CLOSED_MSG);
    return (FEOF(f) != 0);
}

__iter<bytes *> *file_binary::__iter__() {
    __check_closed(__SS_CLOSED_MSG); /* (as cpython: IOBase.__iter__) */
    return this;
}

bytes *file_binary::__next__() {
    /* (as cpython: a buffered reader's readline, else IOBase) */
    __check_closed(__mode_readable(mode) ? "readline of closed file" : __SS_CLOSED_MSG);
    bytes *line = readline(); /* (not the eof flag: data may have been appended) */
    if(!len(line))
        throw new StopIteration();
    return line;
}

