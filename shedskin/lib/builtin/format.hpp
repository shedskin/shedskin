/* Copyright 2005-2023 Mark Dufour and contributors; License Expat (See LICENSE) */

/* printf-style string formatting */

#if defined(_WIN32) || defined(WIN32) || defined(__sun)
int asprintf(char **ret, const char *format, ...);
#endif

str *__escape_bytes(bytes *t);

extern str *nl;
extern str *sp;
extern str *sep;

template <class T> void *__mod_dict_arg(T t, str *name) { return NULL; }
template <class V> V __mod_dict_arg(dict<str *, V> *d, str *name) {
    return d->__getitem__(name);
}
template <class V> V __mod_dict_arg(dict<bytes *, V> *d, str *name) {
    bytes *key = new bytes(); // optimize
    key->unit = name->unit;
    return d->__getitem__(key);
}

template <class T> void __mod_int(str *result, size_t &pos, const char *fstr, T arg) {}
template<> inline void __mod_int(str *result, size_t &pos, const char *fstr, __ss_int arg) {
    char *d;
    int x;
    x = asprintf(&d, fstr, arg); // TODO modern C++ replacement for asprintf?
    if(x == -1)
        throw new ValueError(new str("error in string formatting"));
    result->unit += d;
    free(d);
}
template<> inline void __mod_int(str *result, size_t &pos, const char *fstr, __ss_float arg) {
    __mod_int(result, pos, fstr, (__ss_int)arg);
}

template <class T> void __mod_oct(str *result, size_t &pos, T arg) {}
template<> inline void __mod_oct(str *result, size_t &pos, __ss_int arg) { // TODO asprintf for precision (has issues with 0-bytes?)
    result->unit += __str(arg, (__ss_int)8)->unit;
}

template <class T> void __mod_hex(str *result, size_t &pos, char c, const char *fstr, T arg) {}
template<> inline void __mod_hex(str *result, size_t &pos, char c, const char *fstr, __ss_int arg) {
    char *d;
    int x;
    x = asprintf(&d, fstr, arg); // TODO modern C++ replacement for asprintf?
    if(x == -1)
        throw new ValueError(new str("error in string formatting"));
    result->unit += d;
    free(d);
}

template <class T> void __mod_float(str *result, size_t &pos, const char *fstr, T arg) {}
template<> inline void __mod_float(str *result, size_t &pos, const char *fstr, __ss_float arg) {
    char *d;
    int x;
    x = asprintf(&d, fstr, arg); // TODO modern C++ replacement for asprintf?
    if(x == -1)
        throw new ValueError(new str("error in string formatting"));
    result->unit += d;
    free(d);
}
template<> inline void __mod_float(str *result, size_t &pos, const char *fstr, __ss_int arg) {
    __mod_float(result, pos, fstr, (__ss_float)arg);
}

template <class T> void __mod_str(str *result, size_t &pos, char c, T arg) {
    if(c=='s')
        result->unit += __str(arg)->unit;
    else
        result->unit += repr(arg)->unit;
}
template<> inline void __mod_str(str *result, size_t &pos, char c, bytes *arg) {
    if(c=='s')
        result->unit += arg->unit;
    else
        result->unit += repr(arg)->unit;
}

template <class T> void __mod_char(str *result, size_t &pos, char c, T arg) {} /* TODO error */
template<> inline void __mod_char(str *result, size_t &pos, char c, __ss_int arg) {
    result->unit += (char)arg;
}
template<> inline void __mod_char(str *result, size_t &pos, char c, str *arg) {
    if(arg->unit.size() != 1)
        throw new TypeError(new str("%c requires int or char"));
    result->unit += arg->unit[0];
}

template<class T> void __mod_one(str *fmt, unsigned int fmtlen, unsigned int &j, str *result, size_t &pos, T arg) {
    int namepos, startpos;
    str *name = NULL;
    int skip = 0;
    std::string fmtchars = "0123456789# -+.*";

    for(; j<fmtlen;) {
        char c = fmt->unit[j++];
        if(c != '%') {
            result->unit += c;
            continue;
        }

        if(j >= fmtlen)
            throw new ValueError(new str("incomplete format"));

        /* %% */
        if(fmt->unit[j] == '%') {
            result->unit += '%';
            j++;
            continue;
        }

        /* %(name) */
        if(fmt->unit[j] == '(') {
            j++;
            namepos = j;
            while(fmt->unit[j++] != ')')
                ;
            name = new str(fmt->unit.c_str()+namepos, j-namepos-1);
        }
        else
            name = NULL;

        /* extract format string e.g. '%.2f' */
        startpos = j;
        size_t pos = fmt->unit.find_first_not_of(fmtchars, j);
        if(pos == std::string::npos)
            throw new ValueError(new str("incomplete format"));
        j += (unsigned int)(pos-startpos);

        c = fmt->unit[j++];

        std::string fstr = "%";
        fstr += fmt->unit.substr(startpos, j-startpos-1);
        if(fstr.find('*') != std::string::npos)
            throw new ValueError(new str("unsupported format character"));

#ifdef __SS_LONG
        if(c == 'd' or c == 'i' or c == 'u' or c == 'x' or c == 'X')
            fstr += "l";
#endif
        fstr += c;

        /* check format flag */
        switch(c) {
            case 'd':
            case 'i':
            case 'u':
                if(name) {
                    __mod_int(result, pos, fstr.c_str(), __mod_dict_arg(arg, name));
                    break;
                } else {
                    __mod_int(result, pos, fstr.c_str(), arg);
                    return;
                }

            case 'o':
                if(name) {
                    __mod_oct(result, pos, __mod_dict_arg(arg, name));
                    break;
                } else {
                    __mod_oct(result, pos, arg);
                    return;
                }

            case 'x':
            case 'X':
                if(name) {
                    __mod_hex(result, pos, c, fstr.c_str(), __mod_dict_arg(arg, name));
                    break;
                } else {
                    __mod_hex(result, pos, c, fstr.c_str(), arg);
                    return;
                }

            case 'e':
            case 'E':
            case 'f':
            case 'F':
            case 'g':
            case 'G':
                if(name) {
                    __mod_float(result, pos, fstr.c_str(), __mod_dict_arg(arg, name));
                    break;
                } else {
                    __mod_float(result, pos, fstr.c_str(), arg);
                    return;
                }
                break;

            case 's':
            case 'r':
                if(name) {
                    __mod_str(result, pos, c, __mod_dict_arg(arg, name));
                    break;
                } else {
                    __mod_str(result, pos, c, arg);
                    return;
                }

            case 'c':
                if(name) {
                    __mod_char(result, pos, c, __mod_dict_arg(arg, name));
                    break;
                } else {
                    __mod_char(result, pos, c, arg);
                    return;
                }

            default:
                throw new ValueError(new str("unsupported format character"));
        }
    }
}

template<class ... Args> str *__mod6(str *fmt, int count, Args ... args) {
    str *result = new str();
    size_t pos = 0;
    unsigned int fmtlen = fmt->__len__();
    unsigned int j = 0;

    (__mod_one(fmt, fmtlen, j, result, pos, args), ...);

    for(; j < fmtlen; j++) {
        char c = fmt->unit[j];
        result->unit += c;
        if(c=='%' and fmt->unit[j+1] == '%') // TODO out of bounds
            j++;
    }

    return result;
}

template<class A, class B> str *__modtuple(str *fmt, tuple2<A,B> *t) {
    return __mod6(fmt, 2, t->__getfirst__(), t->__getsecond__());
}

template<class T> str *__modtuple(str *fmt, tuple2<T,T> *t) {
    str *result = new str();
    size_t pos = 0;
    unsigned int fmtlen = fmt->__len__();
    unsigned int j = 0;

    __ss_int l = len(t);
    for(__ss_int i=0;i<l; i++)
        __mod_one(fmt, fmtlen, j, result, pos, t->units[i]);

    for(; j < fmtlen; j++) {
        char c = fmt->unit[j];
        result->unit += c;
        if(c=='%' and j+1<fmtlen and fmt->unit[j+1] == '%') // TODO incomplete format exception if % is last char
            j++;
    }

    return result;
}

/* TODO optimize bytes variants */

template<class ... Args> bytes *__mod6(bytes *fmt, int count, Args ... args) {
    str *result = new str();
    bytes *r = new bytes();
    size_t pos = 0;
    unsigned int fmtlen = fmt->__len__();
    unsigned int j = 0;
    str *sfmt = new str();
    sfmt->unit = fmt->unit;

    (__mod_one(sfmt, fmtlen, j, result, pos, args), ...);

    for(; j < fmtlen; j++) {
        char c = fmt->unit[j];
        result->unit += c;
        if(c=='%' and j+1<fmtlen and fmt->unit[j+1] == '%')
            j++;
    }

    r->unit = result->unit;
    return r;
}

template<class T> bytes *__modtuple(bytes *bfmt, tuple2<T,T> *t) {
    str *fmt = new str();
    fmt->unit = bfmt->unit;

    str *result = __modtuple(fmt, t);

    bytes *r = new bytes();
    r->unit = result->unit;
    return r;
}

template<class A, class B> bytes *__modtuple(bytes *fmt, tuple2<A,B> *t) {
    return __mod6(fmt, 2, t->__getfirst__(), t->__getsecond__());
}
