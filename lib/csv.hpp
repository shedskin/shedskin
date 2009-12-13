#ifndef __CSV_HPP
#define __CSV_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __csv__ {

extern str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;

class Error;
class Excel;
class reader;
class writer;

extern str *__name__;
extern list<int> *__0, *__1;
extern int EAT_CRNL, ESCAPED_CHAR, ESCAPE_IN_QUOTED_FIELD, IN_FIELD, IN_QUOTED_FIELD, QUOTE_ALL, QUOTE_IN_QUOTED_FIELD, QUOTE_MINIMAL, QUOTE_NONE, QUOTE_NONNUMERIC, START_FIELD, START_RECORD, _field_limit;
extern OSError *__exception;

extern class_ *cl_Error;
class Error : public Exception {
public:

    Error() {}
    Error(str *msg) {
        this->__class__ = cl_Error;
        __init__(msg);
    }
};

extern class_ *cl_Excel;
class Excel : public pyobj {
public:
    str *lineterminator;
    int skipinitialspace;
    int quoting;
    int strict;
    str *delimiter;
    str *escapechar;
    str *quotechar;
    int doublequote;

    Excel() {}
    Excel(int __ss_init) {
        this->__class__ = cl_Excel;
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
    Excel *dialect;
    int line_num;
    list<str *> *fields;
    int state;
    list<str *> *field;
    int numeric_field;
    file *input_iter;

    reader() {}
    reader(file *input_iter, str *dialect, str *delimiter, str *quotechar, int doublequote, int skipinitialspace, str *lineterminator, int quoting, str *escapechar, int strict) {
        this->__class__ = cl_reader;
        __init__(input_iter, dialect, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict);
    }
    void *parse_process_char(str *c);
    void *parse_reset();
    list<str *> *next();
    __csviter *__iter__();
    void *__init__(file *input_iter, str *dialect, str *delimiter, str *quotechar, int doublequote, int skipinitialspace, str *lineterminator, int quoting, str *escapechar, int strict);
    void *parse_save_field();
    void *parse_add_char(str *c);
};

extern class_ *cl_writer;
class writer : public pyobj {
public:
    Excel *dialect;
    int num_fields;
    file *output_file;
    list<str *> *rec;

    writer() {}
    writer(file *output_file, str *dialect, str *delimiter, str *quotechar, int doublequote, int skipinitialspace, str *lineterminator, int quoting, str *escapechar, int strict) {
        this->__class__ = cl_writer;
        __init__(output_file, dialect, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict);
    }
    int join_append_data(str *field, int quote_empty, int quoted);
    void *writerow(list<str *> *seq);
    void *join_reset();
    void *writerows(list<list<str *> *> *seqs);
    int join_append(str *field, int quoted, int quote_empty);
    void *__init__(file *output_file, str *dialect, str *delimiter, str *quotechar, int doublequote, int skipinitialspace, str *lineterminator, int quoting, str *escapechar, int strict);
};

extern void * default_5;
extern void * default_6;
extern void * default_3;
extern void * default_4;
extern void * default_8;
extern void * default_1;
extern void * default_2;
extern void * default_9;
extern void * default_7;
extern void * default_10;
extern void * default_0;

void __init();
list<str *> *list_dialects();
Excel *_get_dialect(str *name, str *delimiter, str *quotechar, int doublequote, int skipinitialspace, str *lineterminator, int quoting, str *escapechar, int strict);
int field_size_limit(int new_limit);

} // module namespace
#endif
