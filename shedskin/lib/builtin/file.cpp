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

/* flush and close even when flushing fails, as CPython; returns the first
   errno (0 on success), leaving it in errno. this is a free function, as on
   macOS errno expands to (*__error()), which file::__error would shadow */
static int __ss_fclose(FILE *f) {
    int err = FFLUSH(f) ? errno : 0;
    if(fclose(f) and not err)
        err = errno;
    errno = err;
    return err;
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

file::file(str *file_name, str *flags, str *encoding, str *errors, str *newline) : closed(False) {
    __check_open_mode(flags);
    options.universal_mode = true;
    __encoding = __lookup_encoding(encoding); /* LookupError before touching the file */
    __errors = __lookup_errors(errors);
    this->encoding = encoding ? encoding : new str("utf-8");
    this->errors = errors ? errors : new str("strict");

    /* newline='' or '\n': no translation in either direction, so also
       none by the C runtime (Windows text mode) */
    bool untranslated = false;
    if (newline) {
        if (newline->unit.empty() || newline->unit == U"\n") {
            options.universal_mode = false;
            options.split_cr = newline->unit.empty();
            untranslated = true;
        } else if (newline->unit == U"\r" || newline->unit == U"\r\n")
            throw new ValueError(__add_strs(3, new str("newline="), repr(newline), new str(" is not supported by shedskin (only None, '' and '\\n')")));
        else
            throw new ValueError(__add_strs(2, new str("illegal newline value: "), newline));
    }

    if (!flags)
        flags = __char_cache['r'];
    str *cflags = flags;
    if (untranslated && cflags->unit.find('b') == std::string::npos)
        cflags = new str(cflags->unit + __gcs("b"));
    f = __ss_fopen(file_name, cflags);
    if(f == 0)
        __throw_oserror(file_name);
    __check_not_directory(f, file_name);
    name = file_name;
    mode = flags;

    if (__encoding == __SS_ENC_UTF8_SIG) {
        __encoding = __SS_ENC_UTF8;
        bool readable = mode->unit.find_first_of(__gcs("r+")) != std::string::npos;
        bool bom = false;
        if (readable) { /* skip a leading bom */
            char head[3];
            bom = fread(head, 1, 3, f) == 3 && std::string_view(head, 3) == "\xef\xbb\xbf";
            if (!bom)
                fseek(f, 0, SEEK_SET);
        }
        bool writable = mode->unit.find_first_of(__gcs("wax+")) != std::string::npos;
        if (!bom && writable) { /* bom first, unless appending to existing data */
            if (mode->unit.find('a') != std::string::npos)
                fseek(f, 0, SEEK_END);
            __bom_pending = (ftell(f) == 0);
        }
    }

    buffer = new file_binary(f);
}

file *open(str *name, str *flags, str *encoding, str *errors, str *newline) {
    return new file(name, flags, encoding, errors, newline);
}

file *open(bytes *name, str *flags, str *encoding, str *errors, str *newline) {
    return new file(new str(name->unit), flags, encoding, errors, newline);
}

/* decode the bytes collected in __read_cache, with the file's encoding */
str *file::__decode_cache() {
    str *s = new str();
    if (!__read_cache.empty())
        __decode_into(s->unit, &__read_cache[0], __read_cache.size(), __encoding, __errors, errors);
    return s;
}

/* universal newlines translate '\r\n' lazily: after a '\r', the next read
   skips a '\n' (so reading a line never blocks on the character after it).
   settle that before the file position is used or changed */
static void __settle_cr(FILE *f, __file_options &options) {
    if(options.cr) {
        options.cr = false;
        int c = GETC(f);
        if(c != '\n' && c != EOF)
            ungetc(c, f);
    }
}

/* C stdio needs a file positioning call when switching between reading and
   writing the same stream (C11 7.21.5.3). glibc does not care, but macOS and
   windows lose or misplace the data otherwise */
static inline void __switch_op(FILE *f, __file_options &options, char op) {
    if(options.last_op != op) {
        if(options.last_op && f) {
            __settle_cr(f, options);
            fseek(f, 0, SEEK_CUR);
        }
        options.last_op = op;
    }
}

__ss_int file::write(str *s) {
    __ss_int size = -1;
    __check_closed();
    __switch_op(f, options, 'w');
    if(f) {
        __GC_BYTES b;
        if (__bom_pending) {
            __bom_pending = false;
            b = "\xef\xbb\xbf";
        }
        if (__encoding == __SS_ENC_UTF8 && __errors == __SS_ERR_SURROGATEESCAPE && b.empty())
            b = __to_utf8_se(s); /* fast path (standard streams) */
        else
            __encode_into(b, s, __encoding, __errors, errors);
        if(FWRITE(b.data(), 1, b.size(), f) != b.size() and __error())
            __throw_oserror();
        size = (__ss_int)s->unit.size(); /* characters written, as CPython */
    }
    return size;
}

void *file::writelines(pyiter<str *> *iter) {
    __check_closed();
    str *e;
    int __2;
    pyiter<str *> *__1;
    pyiter<str *>::for_in_loop __3;
    FOR_IN(e,iter,1,2,3)
        write(e);
    END_FOR
    return NULL;
}

__ss_int file::seek(__ss_int i, __ss_int w) {
    __check_closed();
    /* text files only allow seeking to a tell() position or to the end, as
       in cpython (which raises io.UnsupportedOperation, a subclass of both
       OSError and ValueError, for the first two) */
    if(w == 1 && i != 0)
        throw new OSError(new str("can't do nonzero cur-relative seeks"));
    if(w == 2 && i != 0)
        throw new OSError(new str("can't do nonzero end-relative seeks"));
    if(w < 0 || w > 2)
        throw new ValueError(__add_strs(3, new str("invalid whence ("), __str(w), new str(", should be 0, 1 or 2)")));
    if(i < 0)
        throw new ValueError(__add_strs(2, new str("negative seek position "), __str(i)));
    if(f) {
        __settle_cr(f, options);
        if(fseek(f, i, (int)w) == -1)
            __throw_oserror();
        return tell(); /* the new absolute position */
    }
    return -1;
}

__ss_int file::tell() {
    __check_closed();
    if(f) {
        __settle_cr(f, options);
        long status = ftell(f);
        if(status == -1)
            __throw_oserror();
        return __ss_int(status);
    }
    return -1;
}

/* a utf-8 continuation byte never starts a character, so counting
   non-continuation bytes counts code points; text-mode read(n) and readline(n) mean n
   *characters* (as in CPython), so stop -- pushing the byte back -- when
   character n+1 begins. */
static inline bool __is_utf8_cont(int c) { return (c & 0xc0) == 0x80; }

str *file::readline(__ss_int n) {
    __check_closed();
    __switch_op(f, options, 'r');
    __read_cache.clear();
    size_t chars = 0;
    if (options.universal_mode) {
        for(;;) {
            int c = GETC(f);
            if(c == EOF)
                break;
            if(options.cr) {
                options.cr = false;
                if(c == '\n') {
                    c = GETC(f);
                    if(c == EOF)
                        break;
                }
            }
            if(!(__encoding == __SS_ENC_UTF8 && __is_utf8_cont(c))) {
                if(chars == size_t(n)) { /* character n+1 starts: not ours */
                    ungetc(c, f); /* raw byte, before any cr translation */
                    break;
                }
                chars++;
            }
            if(c == '\r') {
                options.cr = true;
                c = '\n';
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
            if(!(__encoding == __SS_ENC_UTF8 && __is_utf8_cont(c))) {
                if(chars == size_t(n)) {
                    ungetc(c, f);
                    break;
                }
                chars++;
            }
            __read_cache.push_back((char)c);
            if(c == '\n')
                break;
            if(c == '\r' && options.split_cr) { /* '\r' or '\r\n' ends the line too */
                const int d = GETC(f);
                if(d == '\n' && chars < size_t(n))
                    __read_cache.push_back('\n');
                else if(d != EOF)
                    ungetc(d, f);
                break;
            }
        }
    }
    if(__error())
        __throw_oserror();

    return __decode_cache();
}

static void __throw_io_error() {
    __throw_oserror();
}

str *file::read(__ss_int n) {
    __check_closed();
    __switch_op(f, options, 'r');
    size_t chars = 0;
    if (options.universal_mode) {
        __read_cache.clear();
        for(;;) {
            int c = GETC(f);
            if(c == EOF)
                break;
            if(options.cr) {
                options.cr = false;
                if(c == '\n') {
                    c = GETC(f);
                    if(c == EOF)
                        break;
                }
            }
            if(!(__encoding == __SS_ENC_UTF8 && __is_utf8_cont(c))) {
                if(chars == size_t(n)) { /* character n+1 starts: not ours */
                    ungetc(c, f); /* raw byte, before any cr translation */
                    break;
                }
                chars++;
            }
            if(c == '\r') {
                options.cr = true;
                c = '\n';
            }
            __read_cache.push_back((char)c);
        }
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
        if(!(__encoding == __SS_ENC_UTF8 && __is_utf8_cont(c))) {
            if(chars == size_t(n)) {
                ungetc(c, f);
                break;
            }
            chars++;
        }
        __read_cache.push_back((char)c);
    }
    if(__error())
        __throw_io_error();
    return __decode_cache();
}

list<str *> *file::readlines(__ss_int /*size_hint*/) {
    __check_closed();
    list<str *> *lines = new list<str *>();
    while(not __eof()) {
        str *line = readline();
        if(line->unit.empty())
            break;
        lines->append(line);
    }
    return lines;
}

void *file::close() {
    if(f and not closed) {
        int err = __ss_fclose(f);
        closed = True;
        if(err)
            __throw_oserror();
    }
    return NULL;
}

void *file::flush() {
    __check_closed();
    if(f)
        if(FFLUSH(f))
            __throw_oserror();
    return NULL;
}

__ss_int file::__ss_fileno() {
    __check_closed();
    if(f)
        return fileno(f);
    return -1;
}
__ss_bool file::isatty()
{
    __check_closed();
#ifdef WIN32
    return ___bool(_isatty((int)__ss_fileno()));
#else // WIN32
    return ___bool(::isatty((int)__ss_fileno()));
#endif // WIN32
}

__ss_int file::truncate(__ss_int size) {
    __check_closed();
    flush();
    if(size == -1)
        size = tell();
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

void file::__enter__() { }

void file::__exit__() {
    close();
}

bool file::__error() {
    return (FERROR(f) != 0);
}

bool file::__eof() {
    return (FEOF(f) != 0);
}

__iter<str *> *file::__iter__() {
    return this;
}

str *file::__next__() {
    if(__eof())
        throw new StopIteration();
    str *line = readline();
    if(__eof() and !len(line))
        throw new StopIteration();
    return line;
}

/* file_binary TODO merge with file */

file_binary::file_binary(str *file_name, str *flags) : closed(False) {
    __check_open_mode(flags);
    if (!flags)
        flags = __char_cache['r'];
    f = __ss_fopen(file_name, flags);
    if(f == 0)
        __throw_oserror(file_name);
    __check_not_directory(f, file_name);
    name = file_name;
    mode = flags;
}

static void __check_binary_args(str *encoding, str *errors, str *newline) {
    if (encoding)
        throw new ValueError(new str("binary mode doesn't take an encoding argument"));
    if (errors)
        throw new ValueError(new str("binary mode doesn't take an errors argument"));
    if (newline)
        throw new ValueError(new str("binary mode doesn't take a newline argument"));
}

file_binary *open_binary(str *name, str *flags, str *encoding, str *errors, str *newline) {
    __check_open_mode(flags); /* (as cpython: before the other arguments) */
    __check_binary_args(encoding, errors, newline);
    return new file_binary(name, flags);
}

file_binary *open_binary(bytes *name, str *flags, str *encoding, str *errors, str *newline) {
    __check_open_mode(flags); /* (as cpython: before the other arguments) */
    __check_binary_args(encoding, errors, newline);
    return new file_binary(new str(name->unit), flags);
}

__ss_int file_binary::write(bytes *s) {
    __ss_int size = -1;
    __check_closed();
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
    __check_closed();
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
    __check_closed();
    if(f) {
        if(fseek(f, i, (int)w) == -1)
            __throw_oserror();
        return tell(); /* the new absolute position */
    }
    return -1;
}

__ss_int file_binary::tell() {
    __check_closed();
    if(f) {
        long status = ftell(f);
        if(status == -1)
            __throw_oserror();
        return __ss_int(status);
    }
    return -1;
}

bytes *file_binary::readline(__ss_int n) {
    __check_closed();
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
    __check_closed();
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

list<bytes *> *file_binary::readlines(__ss_int /*size_hint*/) {
    __check_closed();
    list<bytes *> *lines = new list<bytes *>();
    while(not __eof()) {
        bytes *line = readline();
        if(line->unit.empty())
            break;
        lines->append(line);
    }
    return lines;
}

void *file_binary::close() {
    if(f and not closed) {
        int err = __ss_fclose(f);
        closed = True;
        if(err)
            __throw_oserror();
    }
    return NULL;
}

void *file_binary::flush() {
    __check_closed();
    if(f)
        if(FFLUSH(f))
            __throw_oserror();
    return NULL;
}

__ss_int file_binary::__ss_fileno() {
    __check_closed();
    if(f)
        return fileno(f);
    return -1;
}
__ss_bool file_binary::isatty()
{
    __check_closed();
#ifdef WIN32
    return ___bool(_isatty((int)__ss_fileno()));
#else // WIN32
    return ___bool(::isatty((int)__ss_fileno()));
#endif // WIN32
}

__ss_int file_binary::truncate(__ss_int size) {
    __check_closed();
    flush();
    if(size == -1)
        size = tell();
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

void file_binary::__enter__() { }

void file_binary::__exit__() {
    close();
}

bool file_binary::__error() {
    return (FERROR(f) != 0);
}

bool file_binary::__eof() {
    return (FEOF(f) != 0);
}

__iter<bytes *> *file_binary::__iter__() {
    return this;
}

bytes *file_binary::__next__() {
    if(__eof())
        throw new StopIteration();
    bytes *line = readline();
    if(__eof() and !len(line))
        throw new StopIteration();
    return line;
}

