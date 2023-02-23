/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifdef WIN32
#include <io.h> // for _isatty
#endif // WIN32

#ifndef WIN32
#include <unistd.h>
#endif

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

file::file(str *file_name, str *flags) {
    options.universal_mode = true;

    if (flags) {
        size_t universal = flags->unit.find_first_of("Uu");
        if(universal != std::string::npos) {
            options.universal_mode = true;
            flags = new str(flags->unit);
            flags->unit[universal] = 'b'; // force binary mode as expected by readline
        }
    }
    else
        flags = __char_cache['r'];
    f = fopen(file_name->c_str(), flags->c_str());
    if(f == 0)
        throw new FileNotFoundError(file_name);
    name = file_name;
    mode = flags;

    buffer = new file_binary(f);
}

file *open(str *name, str *flags) {
    return new file(name, flags);
}

file *open(bytes *name, str *flags) {
    return new file(new str(name->unit), flags);
}

void *file::write(str *s) {
    __check_closed();
    if(f) {
        size_t size = s->size();
        if(FWRITE(s->unit.data(), 1, size, f) != size and __error())
            throw new OSError();
    }
    return NULL;
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

void *file::seek(__ss_int i, __ss_int w) {
    __check_closed();
    if(f) {
        if(fseek(f, i, w) == -1)
            throw new OSError();
    }
    return NULL;
}

__ss_int file::tell() {
    __check_closed();
    if(f) {
        long status = ftell(f);
        if(status == -1)
            throw new OSError();
        return __ss_int(status);
    }
    return -1;
}

str *file::readline(int n) {
    __check_closed();
    __read_cache.clear();
    if (options.universal_mode) {
        for(size_t i = 0; i < size_t(n); ++i) {
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
            if(c == '\r') {
                options.cr = true;
                c = '\n';
            }
            __read_cache.push_back(c);
            if(c == '\n')
                break;
        }
    } else {  /* If not universal mode, use the normal loop */
        for(size_t i = 0; i < size_t(n); ++i) {
            const int c = GETC(f);
            if(c == EOF)
                break;
            __read_cache.push_back(c);
            if(c == '\n')
                break;
        }
    }
    if(__error())
        throw new OSError();

    return new str(&__read_cache[0], __read_cache.size());
}

static void __throw_io_error() {
    throw new OSError();
}

str *file::read(int n) {
    __check_closed();
    if(n == 1) {
        const int c = GETC(f);
        if(FERROR(f) != 0) /* avoid virtual call */
            __throw_io_error();
        if(c != EOF)
            return __char_cache[static_cast<unsigned char>(c)];
        else
            return new str();
    } // other cases (n != 1):
    __read_cache.clear();
    for(size_t i = 0; i < size_t(n); ++i) {
        const int c = GETC(f);
        if(c == EOF)
            break;
        __read_cache.push_back(c);
    }
    if(__error())
        __throw_io_error();
    return new str(&__read_cache[0], __read_cache.size());
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

__iter<str *> *file::xreadlines() {
    return this;
}

void *file::close() {
    if(f and not closed) {
        flush();
        if(fclose(f))
            throw new OSError();
        closed = 1;
    }
    return NULL;
}

void *file::flush() {
    __check_closed();
    if(f)
        if(FFLUSH(f))
            throw new OSError();
    return NULL;
}

int file::__ss_fileno() {
    __check_closed();
    if(f)
        return fileno(f);
    return -1;
}
__ss_bool file::isatty()
{
    __check_closed();
#ifdef WIN32
    return ___bool(_isatty(__ss_fileno()));
#else // WIN32
    return ___bool(::isatty(__ss_fileno()));
#endif // WIN32
}

void *file::truncate(int size) {
    __check_closed();
    flush();
    if(size == -1)
        size = tell();  
#if(_BSD_SOURCE || _XOPEN_SOURCE >= 500 || _POSIX_C_SOURCE >= 200112L)
    if(ftruncate(__ss_fileno(), size) == -1)
        throw new OSError();
#endif
    return NULL;
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

file_binary::file_binary(str *file_name, str *flags) {
    if (flags) {
        size_t universal = flags->unit.find_first_of("Uu");
        if(universal != std::string::npos) {
            options.universal_mode = true;
            flags = new str(flags->unit);
            flags->unit[universal] = 'b'; // force binary mode as expected by readline
        }
    }
    else
        flags = __char_cache['r'];
    f = fopen(file_name->c_str(), flags->c_str());
    if(f == 0)
        throw new FileNotFoundError(file_name);
    name = file_name;
    mode = flags;
}

file_binary *open_binary(str *name, str *flags) {
    return new file_binary(name, flags);
}

file_binary *open_binary(bytes *name, str *flags) {
    return new file_binary(new str(name->unit), flags);
}

void *file_binary::write(bytes *s) {
    __check_closed();
    if(f) {
        size_t size = s->size();
        if(FWRITE(s->unit.data(), 1, size, f) != size and __error())
            throw new OSError();
    }
    return NULL;
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

void *file_binary::seek(__ss_int i, __ss_int w) {
    __check_closed();
    if(f) {
        if(fseek(f, i, w) == -1)
            throw new OSError();
    }
    return NULL;
}

__ss_int file_binary::tell() {
    __check_closed();
    if(f) {
        long status = ftell(f);
        if(status == -1)
            throw new OSError();
        return __ss_int(status);
    }
    return -1;
}

bytes *file_binary::readline(int n) {
    __check_closed();
    __read_cache.clear();
    if (options.universal_mode) {
        for(size_t i = 0; i < size_t(n); ++i) {
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
            if(c == '\r') {
                options.cr = true;
                c = '\n';
            }
            __read_cache.push_back(c);
            if(c == '\n')
                break;
        }
    } else {  /* If not universal mode, use the normal loop */
        for(size_t i = 0; i < size_t(n); ++i) {
            const int c = GETC(f);
            if(c == EOF)
                break;
            __read_cache.push_back(c);
            if(c == '\n')
                break;
        }
    }
    if(__error())
        throw new OSError();

    bytes *b = new bytes(&__read_cache[0], __read_cache.size());
    b->frozen = 1;
    return b;
}

bytes *file_binary::read(int n) {
    __check_closed();
    if(n == 1) {
        const int c = GETC(f);
        if(FERROR(f) != 0) /* avoid virtual call */
            __throw_io_error();
        if(c != EOF)
            return new bytes(__char_cache[static_cast<unsigned char>(c)]->unit);
        else
            return new bytes();
    } // other cases (n != 1):
    __read_cache.clear();
    for(size_t i = 0; i < size_t(n); ++i) {
        const int c = GETC(f);
        if(c == EOF)
            break;
        __read_cache.push_back(c);
    }
    if(__error())
        __throw_io_error();
    bytes *b = new bytes(&__read_cache[0], __read_cache.size());
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

__iter<bytes *> *file_binary::xreadlines() {
    return this->__iter__();
}

void *file_binary::close() {
    if(f and not closed) {
        flush();
        if(fclose(f))
            throw new OSError();
        closed = 1;
    }
    return NULL;
}

void *file_binary::flush() {
    __check_closed();
    if(f)
        if(FFLUSH(f))
            throw new OSError();
    return NULL;
}

int file_binary::__ss_fileno() {
    __check_closed();
    if(f)
        return fileno(f);
    return -1;
}
__ss_bool file_binary::isatty()
{
    __check_closed();
#ifdef WIN32
    return ___bool(_isatty(__ss_fileno()));
#else // WIN32
    return ___bool(::isatty(__ss_fileno()));
#endif // WIN32
}

void *file_binary::truncate(int size) {
    __check_closed();
    flush();
    if(size == -1)
        size = tell();  
#if(_BSD_SOURCE || _XOPEN_SOURCE >= 500 || _POSIX_C_SOURCE >= 200112L)
    if(ftruncate(__ss_fileno(), size) == -1)
        throw new OSError();
#endif
    return NULL;
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

