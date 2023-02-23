/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */


#if defined(WIN32)
#include <BaseTsd.h>
#include <stdlib.h>
typedef SSIZE_T ssize_t;
#endif

/* mod helpers */

#if defined(_WIN32) || defined(WIN32) || defined(__sun)
#if defined (_MSC_VER)
#define va_copy(dest, src) ((void)((dest) = (src)));
#endif
int vasprintf(char **ret, const char *format, va_list ap)
{
    va_list ap2;
    int len= 100;        /* First guess at the size */
    if ((*ret= (char *)malloc(len)) == NULL) return -1;
    while (1)
    {
        int nchar;
        va_copy(ap2, ap);
        nchar= vsnprintf(*ret, len, format, ap2);
        if (nchar > -1 && nchar < len) return nchar;
        if (nchar > len)
            len= nchar+1;
        else
            len*= 2;
        if ((*ret= (char *)realloc(*ret, len)) == NULL)
        {
            free(*ret);
            return -1;
        }
    }
}

int asprintf(char **ret, const char *format, ...)
{
    va_list ap;
    int nc;
    va_start (ap, format);
    nc = vasprintf(ret, format, ap);
    va_end(ap);
    return nc;
}
#endif

int __fmtpos(str *fmt) {
    int i = fmt->find('%');
    if(i == -1)
        return -1;
    return fmt->unit.find_first_not_of(__fmtchars, i+1);
}

int __fmtpos2(str *fmt) {
    size_t i = 0;
    while((i = fmt->find('%', i)) != std::string::npos) {
        if(i != fmt->size()-1) {
            char nextchar = fmt->unit[i+1];
            if(nextchar == '%')
                i++;
            else if(nextchar == '(')
                return i;
        }
        i++;
    }
    return -1;
}

template<class T> str *do_asprintf(const char *fmt, T t, pyobj *a1, pyobj *a2) {
    char *d;
    int x;
    str *r;
    if(a2)
        x = asprintf(&d, fmt, ((int)(((int_ *)a1)->unit)), ((int)(((int_ *)a2)->unit)), t);
    else if(a1)
        x = asprintf(&d, fmt, ((int)(((int_ *)a1)->unit)), t);
    else
        x = asprintf(&d, fmt, t);
    if(x == -1)
        throw new ValueError(new str("error in string formatting"));
    r = new str(d);
    free(d);
    return r;
}

/* XXX deal with null-chars.. ugh */
str *do_asprintf_str(const char *fmt, str *s, pyobj *a1, pyobj *a2) {
    char *d;
    int x;
    str *r;
    int nullchars = ((const str*)s)->find('\0') != -1; /* XXX %6.s */
    ssize_t len = s->size();
    str *old_s = s;
    if(nullchars) {
        s = new str(s->unit);
        std::replace(s->unit.begin(), s->unit.end(), '\0', ' ');
    }
    if(a2)
        x = asprintf(&d, fmt, ((int)(((int_ *)a1)->unit)), ((int)(((int_ *)a2)->unit)), s->c_str());
    else if(a1)
        x = asprintf(&d, fmt, ((int)(((int_ *)a1)->unit)), s->c_str());
    else
        x = asprintf(&d, fmt, s->c_str());
    if(nullchars) {
        for(int i=0; i<x && i<len; i++)
            if(old_s->unit[i] == '\0')
                d[i] = '\0';
    }
    r = new str(d, x);
    free(d);
    return r;
}

/* TODO use in str/bytes __repr__ */
str *__escape_bytes(pyobj *p) {
    bytes *t = (bytes *)p;

    std::stringstream ss;
    __GC_STRING sep = "\\\n\r\t";
    __GC_STRING let = "\\nrt";

    int hasq = t->unit.find('\'');
    int hasd = t->unit.find('\"');

    if (hasq != -1 && hasd != -1) {
        sep += "'"; let += "'";
    }

    for(unsigned int i=0; i<t->unit.size(); i++)
    {
        char c = t->unit[i];
        int k;

        if((k = sep.find_first_of(c)) != -1)
            ss << "\\" << let[k];
        else {
            int j = (int)((unsigned char)c);

            if(j<16)
                ss << "\\x0" << std::hex << j;
            else if(j>=' ' && j<='~')
                ss << (char)j;
            else
                ss << "\\x" << std::hex << j;
        }
    }

    return new str(ss.str().c_str());
}

void __modfill(str **fmt, pyobj *t, str **s, pyobj *a1, pyobj *a2, bool bytes) {
    char c;
    int i = (*fmt)->find('%');
    int j = __fmtpos(*fmt);
    *s = new str((*s)->unit + (*fmt)->unit.substr(0, i));
    str *add;

    c = (*fmt)->unit[j];
    if(c == 's' or c == 'r') {
        if(c == 's') {
            if(bytes and t->__class__ == cl_bytes)
                add = __escape_bytes(t);
            else
                add = __str(t);
        } else
            add = repr(t);
        (*fmt)->unit[j] = 's';
        add = do_asprintf_str((*fmt)->unit.substr(i, j+1-i).c_str(), add, a1, a2);
    } else if(c  == 'c')
        add = __str(t);
    else if(c == '%')
        add = new str("%");
    else if(t->__class__ == cl_int_) {
#ifdef __SS_LONG
        add = do_asprintf(((*fmt)->unit.substr(i, j-i)+__GC_STRING("ll")+(*fmt)->unit[j]).c_str(), ((int_ *)t)->unit, a1, a2);
#else
        add = do_asprintf((*fmt)->unit.substr(i, j+1-i).c_str(), ((int_ *)t)->unit, a1, a2);
#endif
    } else { /* cl_float_ */
        if(c == 'H') {
            (*fmt)->unit.replace(j, 1, ".12g");
            j += 3;
        }
        add = do_asprintf((*fmt)->unit.substr(i, j+1-i).c_str(), ((float_ *)t)->unit, a1, a2);
        if(c == 'H' && ((float_ *)t)->unit-((int)(((float_ *)t)->unit)) == 0)
            *add += ".0";
    }
    *s = (*s)->__add__(add);
    *fmt = new str((*fmt)->unit.substr(j+1, (*fmt)->size()-j-1));
}

pyobj *modgetitem(list<pyobj *> *vals, int i) {
    if(i==len(vals))
        throw new TypeError(new str("not enough arguments for format string"));
    return vals->__getitem__(i);
}

str *__mod4(str *fmts, list<pyobj *> *vals, bool bytes) {
    int i, j;
    str *r = new str();
    str *fmt = new str(fmts->c_str());
    i = 0;
    while((j = __fmtpos(fmt)) != -1) {
        pyobj *p, *a1, *a2;

        int perc_pos = fmt->find('%');
        int asterisks = std::count(fmt->unit.begin()+perc_pos+1, fmt->unit.begin()+j, '*');
        a1 = a2 = NULL;
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
                break;
            default:
                throw new ValueError(new str("unsupported format character"));
        }
    }
    if(i!=len(vals))
        throw new TypeError(new str("not all arguments converted during string formatting"));

    *r += fmt->c_str();
    return r;
}

str *__mod5(list<pyobj *> *vals, str *sep) {
    __mod5_cache->units.resize(0);
    for(int i=0;i<len(vals);i++) {
        pyobj *p = vals->__getitem__(i);
        if(p == NULL)
            __mod5_cache->append(__fmt_s);
        else if(p->__class__ == cl_float_)
            __mod5_cache->append(__fmt_H);
        else if(p->__class__== cl_int_)
            __mod5_cache->append(__fmt_d);
        else
            __mod5_cache->append(__fmt_s);
    }
    str *s = __mod4(sep->join(__mod5_cache), vals);
    return s;
}

str *__modcd(str *fmt, list<str *> *names, ...) {
    int i;
    list<pyobj *> *vals = new list<pyobj *>();
    va_list args;
    va_start(args, names);
    for(i=0; i<len(names); i++)
        vals->append(va_arg(args, pyobj *));
    va_end(args);

    str *naam;
    int pos, pos2;
    dict<str *, pyobj *> *d = new dict<str *, pyobj *>(__zip(2, names, vals));
    str *const_6 = new str(")");
    list<pyobj *> *values = new list<pyobj *>();

    while((pos = __fmtpos2(fmt)) != -1) {
        pos2 = fmt->find(const_6, pos);
        naam = fmt->__slice__(3, (pos+2), pos2, 0);
        values->append(d->__getitem__(naam));
        fmt = (fmt->__slice__(2, 0, (pos+1), 0))->__add__(fmt->__slice__(1, (pos2+1), 0, 0));
    }

    return __mod4(fmt, values);
}

/* mod */

str *mod_to_c2(pyobj *t) {
    if(t == NULL)
        throw new TypeError(new str("an integer is required"));
    if(t->__class__ == cl_str_) {
        if(len((str *)t) == 1)
            return (str *)t;
        else
            throw new TypeError(new str("%c requires int or char"));
    }
    int value;
    if(t->__class__ == cl_int_)
        value = ((int_ *)t)->unit;
    else if(t->__class__ == cl_float_)
        value = ((int)(((float_ *)t)->unit));
    else
        value = t->__int__();
    if(value < 0)
        throw new OverflowError(new str("unsigned byte integer is less than minimum"));
    else if(value > 255)
        throw new OverflowError(new str("unsigned byte integer is greater than minimum"));
    return chr(value);
}

int_ *mod_to_int(pyobj *t) {
    if(t == NULL)
        throw new TypeError(new str("int argument required"));
    if(t->__class__ == cl_int_)
        return (int_ *)t;
    else if(t->__class__ == cl_float_)
        return new int_(((int)(((float_ *)t)->unit)));
    else
        return new int_(t->__int__());
}

float_ *mod_to_float(pyobj *t) {
    if(t == NULL)
        throw new TypeError(new str("float argument required"));
    if(t->__class__ == cl_float_)
        return (float_ *)t;
    else if(t->__class__ == cl_int_)
        return new float_(((int_ *)t)->unit);
    throw new TypeError(new str("float argument required"));
}

str *__modct(str *fmt, int n, ...) {
     list<pyobj *> *vals = new list<pyobj *>();
     va_list args;
     va_start(args, n);
     for(int i=0; i<n; i++)
         vals->append(va_arg(args, pyobj *));
     va_end(args);
     str *s = __mod4(fmt, vals);
     return s;
}

/* TODO optimize later */
bytes *__modct(bytes *fmt, int n, ...) {
     list<pyobj *> *vals = new list<pyobj *>();
     va_list args;
     va_start(args, n);
     for(int i=0; i<n; i++)
         vals->append(va_arg(args, pyobj *));
     va_end(args);
     str *s = __mod4(new str(fmt->unit), vals, true);
     return new bytes(s->unit);
}

/* print .., */

void print(int n, file *f, str *end, str *sep, ...) {
    __print_cache->units.resize(0);
    va_list args;
    va_start(args, sep);
    for(int i=0; i<n; i++)
        __print_cache->append(va_arg(args, pyobj *));
    va_end(args);
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

void print2(file *f, int comma, int n, ...) {
    __print_cache->units.resize(0);
    va_list args;
    va_start(args, n);
    for(int i=0; i<n; i++)
        __print_cache->append(va_arg(args, pyobj *));
    va_end(args);
    if (!f)
        f = __ss_stdout;
    __file_options *p_opt = &f->options;
    str *s = __mod5(__print_cache, sp);
    if(len(s)) {
        if(p_opt->space && (!isspace(p_opt->lastchar) || p_opt->lastchar==' ') && s->c_str()[0] != '\n')
            f->write(sp); /* space */
        f->write(s);
        p_opt->lastchar = s->c_str()[len(s)-1];
    }
    else if (comma)
        p_opt->lastchar = ' ';
    if(!comma) {
        f->write(nl); /* newline */
        p_opt->lastchar = '\n';
    }
    p_opt->space = comma;
}

#ifdef __SS_LONG
int_ *___box(__ss_int i) {
    return new int_(i);
}
#endif
int_ *___box(int i) {
    return new int_(i);
}
int_ *___box(unsigned int i) {
    return new int_(i);
}
int_ *___box(long i) {
    return new int_(i);
}
int_ *___box(unsigned long i) {
    return new int_(i);
}
int_ *___box(unsigned long long i) {
    return new int_(i);
}
bool_ *___box(__ss_bool b) {
    return new bool_(b);
}
float_ *___box(__ss_float d) {
    return new float_(d);
}
complex_ *___box(complex c) {
    return new complex_(c);
}
