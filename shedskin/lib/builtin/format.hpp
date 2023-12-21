/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* boxing */

template<class T> T ___box(T t) { return t; } /* XXX */
int_ *___box(__ss_int);
bool_ *___box(__ss_bool);
float_ *___box(__ss_float);
complex_ *___box(complex);

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

/* print .., */

template<class ... Args> void print(int n, file *f, str *end, str *sep, Args ... args) {
    __print_cache->units.resize(0);
    (__print_cache->append(args), ...);

    str *s = __mod5(__print_cache, sep?sep:sp);
    if(!end)
        end = nl;
    if(f) {
        f->write(s);
        f->write(end);
    }
    else
        printf("%s%s", s->c_str(), end->c_str());
}
