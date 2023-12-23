/* Copyright 2005-2023 Mark Dufour and contributors; License Expat (See LICENSE) */


#if defined(WIN32)
#include <BaseTsd.h>
#include <stdlib.h>
typedef SSIZE_T ssize_t;
#endif

/* mod helpers */

#if defined(_WIN32) || defined(WIN32) || defined(__sun)
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
    int nullchars = ((const str*)s)->unit.find('\0') != std::string::npos; /* XXX %6.s */
    ssize_t len = s->unit.size();
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

    size_t hasq = t->unit.find('\'');
    size_t hasd = t->unit.find('\"');

    if (hasq != std::string::npos && hasd != std::string::npos) {
        sep += "'"; let += "'";
    }

    for(size_t i=0; i<t->unit.size(); i++)
    {
        char c = t->unit[i];
        size_t k;

        if((k = sep.find_first_of(c)) != std::string::npos)
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
