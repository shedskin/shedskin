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


/* TODO use in str/bytes __repr__ */
str *__escape_bytes(pyobj *p) {
    bytes *t = (bytes *)p;

    std::stringstream ss;
    __GC_STRING separator = "\\\n\r\t";
    __GC_STRING let = "\\nrt";

    size_t hasq = t->unit.find('\'');
    size_t hasd = t->unit.find('\"');

    if (hasq != std::string::npos && hasd != std::string::npos) {
        separator += "'"; let += "'";
    }

    for(size_t i=0; i<t->unit.size(); i++)
    {
        char c = t->unit[i];
        size_t k;

        if((k = separator.find_first_of(c)) != std::string::npos)
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
