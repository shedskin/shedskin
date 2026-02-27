/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __CSV_HPP
#define __CSV_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __csv__ {

extern str *__name__;

extern __ss_int QUOTE_ALL;
extern __ss_int QUOTE_MINIMAL;
extern __ss_int QUOTE_NONNUMERIC;
extern __ss_int QUOTE_NONE;
extern __ss_int QUOTE_STRINGS;
extern __ss_int QUOTE_NOTNULL;

extern class_ *cl_Error;
extern class_ *cl_Dialect;
extern class_ *cl_Excel;
extern class_ *cl_UnixDialect;
extern class_ *cl_ExcelTab;
extern class_ *cl_reader;
extern class_ *cl_writer;
extern class_ *cl_DictReader;
extern class_ *cl_DictWriter;

class Error;

class Dialect;
class unix_dialect;
class excel;
class excel_tab;

class reader;
class writer;
class DictReader;
class DictWriter;

extern str *default_18, *default_19, *default_20; // TODO for DictWriter(); remove and scan other headers

extern dict<str *, Dialect *> *_dialects;

class Error : public Exception {
public:

    Error() {}
    Error(str *msg) : Exception(msg) {
        this->__class__ = cl_Error;
    }
};

class Dialect : public pyobj {
public:
    str *lineterminator;
    __ss_int skipinitialspace;
    __ss_int quoting;
    __ss_bool strict; //TODO generalize __ss_bool
    str *delimiter;
    str *escapechar;
    str *quotechar;
    __ss_int doublequote;

    Dialect() {
        this->__class__ = cl_Dialect;
    }
    void *__init__();
};

class unix_dialect : public Dialect {
public:
    unix_dialect() {
        this->__class__ = cl_UnixDialect;

        delimiter = new str(",");
        doublequote = True;
        escapechar = NULL;
        lineterminator = new str("\n");
        quotechar = new str("\"");
        quoting = 1;
        skipinitialspace = False;
        strict = False;
    }
    void *__init__();
};

class excel : public Dialect {
public:
    excel() {
        this->__class__ = cl_Excel;

        delimiter = new str(",");
        doublequote = True;
        escapechar = NULL;
        lineterminator = new str("\r\n");
        quotechar = new str("\"");
        quoting = 0;
        skipinitialspace = False;
        strict = False;
    }
    void *__init__();
};

class excel_tab : public Dialect {
public:
    excel_tab() {
        this->__class__ = cl_ExcelTab;

        delimiter = new str("\t");
        doublequote = True;
        escapechar = NULL;
        lineterminator = new str("\r\n");
        quotechar = new str("\"");
        quoting = 0;
        skipinitialspace = False;
        strict = False;
    }
    void *__init__();
};

class __csviter : public __iter<list<str *> *> {
public:
    reader *r;
    __csviter(reader *r_);
    list<str *> *__next__();
};

class reader : public __iter<list<str *> *> {
public:
    Dialect *dialect;
    __ss_int line_num;
    list<str *> *fields;
    list<str *> *field;
    __ss_int state;
    __ss_int numeric_field;
    file *input_iter;

    reader() {}
    template<class D> reader(
        file *input_iter_,
        D dialect_,
        str *delimiter,
        str *quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        str *lineterminator,
        __ss_int quoting,
        str *escapechar,
        __ss_int strict
    ) {
        this->__class__ = cl_reader;
        str *dialectstr;

        if constexpr (std::is_same_v<D, str *>) {
            dialectstr = dialect_;
        }
        else if constexpr (std::is_same_v<D, Dialect *>) { // TODO lookup and pass dialect object
            dialectstr = new str("excel");
        }
        else
            dialectstr = new str("excel");

        __init__(
            input_iter_,
            dialectstr,
            delimiter,
            quotechar,
            doublequote,
            skipinitialspace,
            lineterminator,
            quoting,
            escapechar,
            strict
        );
    }

    void *__init__(
        file *input_iter_,
        str *dialect_,
        str *delimiter,
        str *quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        str *lineterminator,
        __ss_int quoting,
        str *escapechar,
        __ss_int strict
    );

    list<str *> *__next__();
    __csviter *__iter__();

    // internal
    void *parse_process_char(str *c);
    void *parse_reset();
    void *parse_save_field();
    void *parse_add_char(str *c);
};

class writer : public pyobj {
public:
    Dialect *dialect;
    __ss_int num_fields;
    file *output_file;
    list<str *> *rec;

    writer() {}
    writer(
        file *output_file_,
        str *dialect_,
        str *delimiter,
        str *quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        str *lineterminator,
        __ss_int quoting,
        str *escapechar,
        __ss_int strict
    ) {
        this->__class__ = cl_writer;
        __init__(
            output_file_,
            dialect_,
            delimiter,
            quotechar,
            doublequote,
            skipinitialspace,
            lineterminator,
            quoting,
            escapechar,
            strict
        );
    }

    void *__init__(
        file *output_file_,
        str *dialect_,
        str *delimiter,
        str *quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        str *lineterminator,
        __ss_int quoting,
        str *escapechar,
        __ss_int strict
    );

    void *writerow(list<str *> *seq);
    void *writerows(pyiter<list<str *> *> *seqs);

    // internal
    __ss_int join_append_data(str *field, __ss_int quote_empty, __ss_int quoted);
    void *join_reset();
    __ss_int join_append(str *field, __ss_int quoted, __ss_int quote_empty);
};

class __driter : public __iter<dict<str *, str *> *> {
public:
    DictReader *r;
    __driter(DictReader *r_);
    dict<str *, str *> *__next__();
};

class DictReader : public __iter<dict<str *, str *> *> {
public:
    str *restval;
    str *dialect;
    __ss_int line_num;
    str *restkey;
    list<str *> *_fieldnames;
    reader *_reader;

    DictReader() {}
    DictReader(
        file *f,
        pyiter<str *> *fieldnames_,
        str *restkey_,
        str *restval_,
        str *dialect_,
        str *delimiter,
        str *quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        str *lineterminator,
        __ss_int quoting,
        str *escapechar,
        __ss_int strict
    ) {
        this->__class__ = cl_DictReader;
        __init__(
            f,
            fieldnames_,
            restkey_,
            restval_,
            dialect_,
            delimiter,
            quotechar,
            doublequote,
            skipinitialspace,
            lineterminator,
            quoting,
            escapechar,
            strict
        );
    }

    void *__init__(
        file *f,
        pyiter<str *> *fieldnames_,
        str *restkey_,
        str *restval_,
        str *dialect_,
        str *delimiter,
        str *quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        str *lineterminator,
        __ss_int quoting,
        str *escapechar,
        __ss_int strict
    );

    void *setfieldnames(list<str *> *value);
    list<str *> *getfieldnames();

    dict<str *, str *> *__next__();
    __driter *__iter__();
};

class DictWriter : public pyobj {
public:
    str *restval;
    writer *_writer;
    list<str *> *fieldnames;
    str *extrasaction;

    DictWriter() {}
    DictWriter(
        file *f,
        pyiter<str *> *fieldnames_,
        str *restval_,
        str *extrasaction_,
        str *dialect_,
        str *delimiter,
        str *quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        str *lineterminator,
        __ss_int quoting,
        str *escapechar,
        __ss_int strict
    ) {
        this->__class__ = cl_DictWriter;
        __init__(
            f,
            fieldnames_,
            restval_,
            extrasaction_,
            dialect_,
            delimiter,
            quotechar,
            doublequote,
            skipinitialspace,
            lineterminator,
            quoting,
            escapechar,
            strict
        );
    }

    void *__init__(
        file *f,
        pyiter<str *> *fieldnames_,
        str *restval_,
        str *extrasaction_,
        str *dialect_,
        str *delimiter,
        str *quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        str *lineterminator,
        __ss_int quoting,
        str *escapechar,
        __ss_int strict
    );

    void *writeheader();
    void *writerow(dict<str *, str *> *rowdict);
    void *writerows(pyiter<dict<str *, str *> *> *rowdicts);

    // internal
    list<str *> *_dict_to_list(dict<str *, str *> *rowdict);
};

list<str *> *list_dialects();

Dialect *get_dialect(str *name);

void *register_dialect(
    str *name,
    str *dialect,
    str *delimiter,
    str *quotechar,
    __ss_int doublequote,
    __ss_int skipinitialspace,
    str *lineterminator,
    __ss_int quoting,
    str *escapechar,
    __ss_int strict
); // TODO template dialect

void *unregister_dialect(str *name);

__ss_int field_size_limit(__ss_int new_limit);

void __init();

} // module namespace
#endif
