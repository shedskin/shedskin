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

template<class T> str *__modtuple(str *fmt, tuple2<T,T> *t) {
    list<pyobj *> *vals = new list<pyobj *>();
    for(int i=0;i<len(t);i++)
        vals->append(___box(t->__getitem__(i)));
    return __mod4(fmt, vals);
}

template<class A, class B> str *__modtuple(str *fmt, tuple2<A,B> *t) {
    list<pyobj *> *vals = new list<pyobj *>(2, ___box(t->__getfirst__()), ___box(t->__getsecond__()));
    return __mod4(fmt, vals);
}

template<class T> str *__moddict(str *v, dict<str *, T> *d) {
    str *const_6 = new str(")");
    int i, pos, pos2;
    list<str *> *names = (new list<str *>());

    while((pos = (__ss_int)__fmtpos2(v)) != -1) {
        pos2 = v->find(const_6, pos);
        names->append(v->__slice__(3, (pos+2), pos2, 0));
        v = (v->__slice__(2, 0, (pos+1), 0))->__add__(v->__slice__(1, (pos2+1), 0, 0));
    }

    list<pyobj *> *vals = new list<pyobj *>();
    for(i=0;i<len(names);i++)
        vals->append(___box(d->__getitem__(names->__getitem__(i))));
    return __mod4(v, vals);
}

template <class T> void *__mod_dict_arg(T t, str *name) { return NULL; }
template <class V> V __mod_dict_arg(dict<str *, V> *d, str *name) {
    return d->__getitem__(name);
}

template <class T> void __mod_int(str *result, size_t &pos, T arg) {
    result->unit += '*';
}
template<> inline void __mod_int(str *result, size_t &pos, __ss_int arg) {
    result->unit += __str(arg)->unit;
}

template <class T> void __mod_float(str *result, size_t &pos, T arg) {
    result->unit += '?';
}
template<> inline void __mod_float(str *result, size_t &pos, __ss_float arg) {
    result->unit += "<F>";
}

template<class T> void __mod_one(str *fmt, unsigned int fmtlen, unsigned int &j, str *result, size_t &pos, T arg) {
    int namepos;
    str *name = NULL;
    int skip = 0;

    for(; j<fmtlen; j++) {
        char c = fmt->unit[j];
        switch(c) {
            case '%':
                skip = 1;
                break;

            case 'd':
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

            case 'f':
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

            case 's':
                skip = 0;
                result->unit += "<S>";
                j++;
                return;

            case '(':
                namepos = j+1;
                break;

            case ')':
                name = new str(fmt->unit.c_str()+namepos, j-namepos);
                break;

            default:
                if(!skip)
                    result->unit += c;
        }

    }

/*        p = a1 = a2 = NULL;
        if(asterisks==1) {
            a1 = modgetitem(vals, i++);
        } else if(asterisks==2) {
            a1 = modgetitem(vals, i++);
            a2 = modgetitem(vals, i++);
        }

        char c = fmt->c_str()[j];
        if(c != '%')
            p = modgetitem(vals, i++);

        switch(c) {
            case 'c':
                __modfill(&fmt, mod_to_c2(p), &r, a1, a2);
                break;
            case 's':
            case 'r':
                __modfill(&fmt, p, &r, a1, a2, bytes);
                break;
            case 'd':
            case 'i':
            case 'o':
            case 'u':
            case 'x':
            case 'X':
                __modfill(&fmt, mod_to_int(p), &r, a1, a2);
                break;
            case 'e':
            case 'E':
            case 'f':
            case 'F':
            case 'g':
            case 'G':
            case 'H':
                __modfill(&fmt, mod_to_float(p), &r, a1, a2);
                break;
            case '%':
                __modfill(&fmt, NULL, &r, a1, a2);
                break; */

}

template<class ... Args> str *__mod6(str *fmt, int count, Args ... args) {
    str *result = new str();
    size_t pos = 0;
    unsigned int fmtlen = fmt->__len__();
    unsigned int j = 0;

    (__mod_one(fmt, fmtlen, j, result, pos, args), ...);

    return result;
}
