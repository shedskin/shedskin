/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* boxing */

template<class T> T ___box(T t) { return t; } /* XXX */
int_ *___box(__ss_int);
bool_ *___box(__ss_bool);
float_ *___box(__ss_float);
complex_ *___box(complex);
pyobj *___box(long int); // None

/* string formatting */

size_t __fmtpos(str *fmt);
size_t __fmtpos2(str *fmt);
void __modfill(str **fmt, pyobj *t, str **s, pyobj *a1, pyobj *a2, bool bytes=false);
str *__mod5(list<pyobj *> *vals, str *sep);
str *mod_to_c2(pyobj *t);
int_ *mod_to_int(pyobj *t);
float_ *mod_to_float(pyobj *t);

str *__escape_bytes(bytes *t);

extern list<pyobj *> *__print_cache;
extern str *nl;
extern str *sp;
extern str *sep;

template <class T> void *__mod_dict_arg(T t, str *name) { return NULL; }
template <class V> V __mod_dict_arg(dict<str *, V> *d, str *name) {
    return d->__getitem__(name);
}

template <class T> void __mod_int(str *result, size_t &pos, T arg) {}
template<> inline void __mod_int(str *result, size_t &pos, __ss_int arg) {
    result->unit += __str(arg)->unit;
}

template <class T> void __mod_oct(str *result, size_t &pos, T arg) {}
template<> inline void __mod_oct(str *result, size_t &pos, __ss_int arg) {
    result->unit += __str(arg, 8)->unit;
}

template <class T> void __mod_hex(str *result, size_t &pos, char c, T arg) {}
template<> inline void __mod_hex(str *result, size_t &pos, char c, __ss_int arg) {
    str *hval = __str(arg, 16);
    if(c == 'X')
        hval = hval->upper();
    result->unit += hval->unit;
}

template <class T> void __mod_float(str *result, size_t &pos, T arg) {}
template<> inline void __mod_float(str *result, size_t &pos, __ss_float arg) {
    result->unit += __str(arg)->unit;
}

template <class T> void __mod_str(str *result, size_t &pos, char c, T arg) {
    if(c=='s')
        result->unit += __str(arg)->unit;
    else
        result->unit += repr(arg)->unit;
}

template<class T> void __mod_one(str *fmt, unsigned int fmtlen, unsigned int &j, str *result, size_t &pos, T arg) {
    int namepos;
    str *name = NULL;
    int skip = 0;

    for(; j<fmtlen; j++) {
        char c = fmt->unit[j];
        switch(c) {
            case '%':
                if(skip)
                    result->unit += '%';
                skip = 1-skip;
                break;

            case 'd':
            case 'i':
            case 'u':
                if(skip) {
                    skip = 0;
                    if(name) {
                        __mod_int(result, pos, __mod_dict_arg(arg, name));
                        name = NULL;
                        break;

                    } else {
                        __mod_int(result, pos, arg);
                        j++;
                        return;
                    }
                } else {
                    result->unit += c;
                    break;
                }

            case 'o':
                if(skip) {
                    skip = 0;
                    if(name) {
                        __mod_oct(result, pos, __mod_dict_arg(arg, name));
                        name = NULL;
                        break;

                    } else {
                        __mod_oct(result, pos, arg);
                        j++;
                        return;
                    }
                } else {
                    result->unit += c;
                    break;
                }

            case 'x':
            case 'X':
                if(skip) {
                    skip = 0;
                    if(name) {
                        __mod_hex(result, pos, c, __mod_dict_arg(arg, name));
                        name = NULL;
                        break;

                    } else {
                        __mod_hex(result, pos, c, arg);
                        j++;
                        return;
                    }
                } else {
                    result->unit += c;
                    break;
                }

            case 'e':
            case 'E':
            case 'f':
            case 'F':
            case 'g':
            case 'G':
                if(skip) {
                    skip = 0;
                    if(name) {
                        __mod_float(result, pos, __mod_dict_arg(arg, name));
                        name = NULL;
                        break;

                    } else {
                        __mod_float(result, pos, arg);
                        j++;
                        return;
                    }
                } else {
                    result->unit += c;
                    break;
                }

            case 's':
            case 'r':
                if(skip) {
                    skip = 0;
                    if(name) {
                        __mod_str(result, pos, c, __mod_dict_arg(arg, name));
                        name = NULL;
                        break;
                    } else {
                        __mod_str(result, pos, c, arg);
                        j++;
                        return;
                    }
                } else {
                    result->unit += c;
                    break;
                }

            case '(':
                if(skip) {
                    namepos = j+1;
                    while(fmt->unit[++j] != ')')  // TODO out of bounds
                        ;
                    name = new str(fmt->unit.c_str()+namepos, j-namepos);
                    break;
                } else {
                    result->unit += c;
                    break;
                }


            default:
                if(!skip)
                    result->unit += c;
        }

    }
}

template<class ... Args> str *__mod6(str *fmt, int count, Args ... args) {
    str *result = new str();
    size_t pos = 0;
    unsigned int fmtlen = fmt->__len__();
    unsigned int j = 0;

    (__mod_one(fmt, fmtlen, j, result, pos, args), ...);

    for(; j < fmtlen; j++)
        result->unit += fmt->unit[j];

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

    for(; j < fmtlen; j++)
        result->unit += fmt->unit[j];

    return result;
}
