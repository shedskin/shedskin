#ifndef __CSV_HPP
#define __CSV_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __csv__ {

extern str *const_0, *const_1, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;

class Dialect;
class reader;

extern str *__name__;
extern list<int> *__0, *__1;
extern OSError *__exception;
extern int EAT_CRNL, ESCAPED_CHAR, ESCAPE_IN_QUOTED_FIELD, IN_FIELD, IN_QUOTED_FIELD, QUOTE_ALL, QUOTE_IN_QUOTED_FIELD, QUOTE_MINIMAL, QUOTE_NONE, QUOTE_NONNUMERIC, START_FIELD, START_RECORD, field_limit;
extern Dialect *excel;

extern class_ *cl_Dialect;
class Dialect : public pyobj {
public:
    str *escapechar;
    int skipinitialspace;
    int quoting;
    int strict;
    str *delimiter;
    str *lineterminator;
    str *quotechar;
    int doublequote;

    Dialect() {}
    Dialect(int __ss_init) {
        this->__class__ = cl_Dialect;
        __init__();
    }
    void *__init__();
};

class __csviter : public __iter<list<str *> *> {
public:
    reader *r;
    __csviter(reader *reader);
    list<str *> *next();
};

extern class_ *cl_reader;
class reader : public pyiter<list<str *> *> {
public:
/*    file *csvfile;

    reader() {}
    reader(file *csvfile) {
        this->__class__ = cl_reader;
        __init__(csvfile);
    }
    __csviter *__iter__();
    void *__init__(file *csvfile); */

    Dialect *dialect;
    int state;
    list<str *> *fields;
    int line_num;
    list<str *> *field;
    file *input_iter;

    reader() {}
    reader(file *input_iter) {
        this->__class__ = cl_reader;
        __init__(input_iter);
    }
    int parse_process_char(str *c);
    list<str *> *next();
    __csviter *__iter__();
    int parse_add_char(str *c);
    int parse_save_field();
    void *parse_reset();
    void *__init__(file *input_iter);
};

void __init();

} // module namespace
#endif
