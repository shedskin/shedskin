#ifdef WIN32
#include <io.h> // for _isatty
#endif // WIN32

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
    f = fopen(file_name->unit.c_str(), flags->unit.c_str());
    if(f == 0)
        throw new IOError(file_name);
    name = file_name;
    mode = flags;
}

file *open(str *name, str *flags) {
    return new file(name, flags);
}

void *file::write(str *s) {
    __check_closed();
    if(f) {
        size_t size = s->unit.size();
        if(FWRITE(s->unit.data(), 1, size, f) != size and __error())
            throw new IOError();
    }
    return NULL;
}

void *file::seek(__ss_int i, __ss_int w) {
    __check_closed();
    if(f) {
        if(fseek(f, i, w) == -1)
            throw new IOError();
    }
    return NULL;
}

__ss_int file::tell() {
    __check_closed();
    if(f) {
        long status = ftell(f);
        if(status == -1)
            throw new IOError();
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
        throw new IOError();

    return new str(&__read_cache[0], __read_cache.size());
}

static void __throw_io_error() {
    throw new IOError();
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
    return this->__iter__();
}

void *file::close() {
    if(f and not closed) {
        flush();
        if(fclose(f))
            throw new IOError();
        closed = 1;
    }
    return NULL;
}

void *file::flush() {
    __check_closed();
    if(f)
        if(FFLUSH(f))
            throw new IOError();
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
        throw new IOError();
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

str *file::next() {
    if(__eof())
        throw new StopIteration();
    str *line = readline();
    if(__eof() and !len(line))
        throw new StopIteration();
    return line;
}

/* file iteration */

__iter<str *> *file::__iter__() {
    return new __fileiter(this);
}

__fileiter::__fileiter(file *p) {
    this->p = p;
}

str *__fileiter::next() {
    return p->next();
}
