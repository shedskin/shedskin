/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __CSV_HPP
#define __CSV_HPP

#include "builtin.hpp"
#include "re.hpp"

using namespace __shedskin__;
namespace __csv__ {

extern str *__name__;

extern const __ss_int QUOTE_ALL;
extern const __ss_int QUOTE_MINIMAL;
extern const __ss_int QUOTE_NONNUMERIC;
extern const __ss_int QUOTE_NONE;
extern const __ss_int QUOTE_STRINGS;
extern const __ss_int QUOTE_NOTNULL;

extern class_ *cl_Error;
extern class_ *cl_Dialect;
extern class_ *cl_Excel;
extern class_ *cl_UnixDialect;
extern class_ *cl_ExcelTab;
extern class_ *cl_reader;
extern class_ *cl_writer;
extern class_ *cl_DictReader;
extern class_ *cl_DictWriter;
extern class_ *cl_Sniffer;

class Error;

class Dialect;
class unix_dialect;
class excel;
class excel_tab;

class reader;
class writer;
class DictReader;
class DictWriter;
class Sniffer;

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
    __ss_bool skipinitialspace;
    __ss_int quoting;
    __ss_bool strict;
    str *delimiter;
    str *escapechar;
    str *quotechar;
    __ss_bool doublequote;

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

Dialect *_lookup_dialect(str *name);

/* the str arguments (delimiter, quotechar, lineterminator, escapechar) reach
   _make_dialect as a str *: NULL when omitted (the model's __void default),
   and __csv_none when None is passed explicitly, since CPython tells these
   apart (quotechar=None means no quote character, for example) */
extern str *__csv_none;

template<class T> inline str *__csv_str_arg(T arg) {
    if constexpr (std::is_same_v<T, __ss_void_struct>)
        return NULL;
    else if constexpr (std::is_same_v<T, str *>)
        return arg ? arg : __csv_none;
    else /* None */
        return __csv_none;
}

/* the dialect argument: a registered name or a Dialect instance, or omitted
   or None for excel; 'given' tells CPython's 'dialect is not NULL' check */
template<class D> inline Dialect *__csv_dialect_arg(D dialect_, bool &given) {
    if constexpr (std::is_same_v<D, str *>) {
        given = (dialect_ != NULL);
        return _lookup_dialect(dialect_);
    }
    else if constexpr (std::is_convertible_v<D, Dialect *>) { /* Dialect or predefined subclass instance */
        given = (dialect_ != NULL);
        return dialect_ ? (Dialect *)(dialect_) : _lookup_dialect(new str("excel"));
    }
    else { /* omitted (__ss_void) or None */
        given = false;
        return _lookup_dialect(new str("excel"));
    }
}

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
    __iter<str *> *input_iter;

    __ss_int state;
    list<str *> *fields;
    list<str *> *field;
    size_t field_len;
    bool unquoted_field;


    reader() {}
    template<class D, class DL, class Q, class L, class E> reader(
        pyiter<str *> *input_iter_,
        D dialect_,
        DL delimiter,
        Q quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        L lineterminator,
        __ss_int quoting,
        E escapechar,
        __ss_int strict
    ) {
        this->__class__ = cl_reader;

        bool dialect_given;
        Dialect *from_dialect = __csv_dialect_arg(dialect_, dialect_given);

        __init__(
            input_iter_,
            from_dialect,
            dialect_given,
            __csv_str_arg(delimiter),
            __csv_str_arg(quotechar),
            doublequote,
            skipinitialspace,
            __csv_str_arg(lineterminator),
            quoting,
            __csv_str_arg(escapechar),
            strict
        );
    }

    void *__init__(
        pyiter<str *> *input_iter_,
        Dialect *dialect_,
        bool dialect_given,
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
    void *parse_add_char(__ss_char c);
};

/* whether CPython would consider a field of type T a number (PyNumber_Check),
   which decides quoting under QUOTE_NONNUMERIC */
template<class T> struct __csv_is_numeric : std::bool_constant<
    std::is_arithmetic_v<T> || std::is_same_v<T, __ss_int> || std::is_same_v<T, __ss_float> ||
    std::is_same_v<T, __ss_bool> || std::is_same_v<T, complex>> {};

class writer : public pyobj {
public:
    Dialect *dialect;
    __ss_int num_fields;
    file *output_file;
    list<str *> *rec;
    size_t rec_len;

    writer() {}
    template<class D, class DL, class Q, class L, class E> writer(
        file *output_file_,
        D dialect_,
        DL delimiter,
        Q quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        L lineterminator,
        __ss_int quoting,
        E escapechar,
        __ss_int strict
    ) {
        this->__class__ = cl_writer;

        bool dialect_given;
        Dialect *from_dialect = __csv_dialect_arg(dialect_, dialect_given);

        __init__(
            output_file_,
            from_dialect,
            dialect_given,
            __csv_str_arg(delimiter),
            __csv_str_arg(quotechar),
            doublequote,
            skipinitialspace,
            __csv_str_arg(lineterminator),
            quoting,
            __csv_str_arg(escapechar),
            strict
        );
    }

    void *__init__(
        file *output_file_,
        Dialect *dialect_,
        bool dialect_given,
        str *delimiter,
        str *quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        str *lineterminator,
        __ss_int quoting,
        str *escapechar,
        __ss_int strict
    );

    /* like CPython, accept any iterable of fields: str is written as is,
       None as an empty field and anything else as its str() */
    template<class T> __ss_int writerow(T *seq) {
        typedef typename T::for_in_unit E;
        E field;
        typename T::for_in_loop __3;
        int __2;
        T *__1;
        bool null_field = false;

        this->join_reset();

        FOR_IN(field,seq,1,2,3)
            null_field = this->append_field(field);
        END_FOR

        return this->join_finish(null_field);
    }

    /* append a single field, quoting it according to its type; returns whether it was None */
    template<class E> bool append_field(E field) {
        __ss_int quoting = this->dialect->quoting;
        bool null_field = false;
        if constexpr (std::is_pointer_v<E>)
            null_field = (field == NULL);

        __ss_int quoted;
        if (quoting == QUOTE_ALL)
            quoted = 1;
        else if (quoting == QUOTE_NONNUMERIC)
            quoted = !__csv_is_numeric<E>::value;
        else if (quoting == QUOTE_STRINGS)
            quoted = std::is_same_v<E, str *> && !null_field;
        else if (quoting == QUOTE_NOTNULL)
            quoted = !null_field;
        else
            quoted = 0;

        if constexpr (std::is_same_v<E, str *>)
            this->join_append(field, quoted);
        else if constexpr (std::is_pointer_v<E>)
            this->join_append(null_field ? NULL : __str(field), quoted);
        else
            this->join_append(__str(field), quoted);

        return null_field;
    }

    template<class T> void *writerows(T *seqs) {
        typename T::for_in_unit seq;
        typename T::for_in_loop __3;
        int __2;
        T *__1;

        FOR_IN(seq,seqs,1,2,3)
            this->writerow(seq);
        END_FOR

        return NULL;
    }

    // internal
    void *join_reset();
    __ss_int join_finish(bool null_field);
    void *join_append(str *field, __ss_int quoted);
    void *join_append_data(str *field, __ss_int quoted);
};

class __driter : public __iter<dict<str *, str *> *> {
public:
    DictReader *r;
    __driter(DictReader *r_);
    dict<str *, str *> *__next__();
};

class DictReader : public __iter<dict<str *, str *> *> {
public:
    Dialect *dialect;
    str *restkey;
    str *restval;
    __ss_int line_num;
    list<str *> *_fieldnames;
    reader *_reader;

    DictReader() {}
    template<class D, class DL, class Q, class L, class E> DictReader(
        pyiter<str *> *f,
        pyiter<str *> *fieldnames_,
        str *restkey_,
        str *restval_,
        D dialect_,
        DL delimiter,
        Q quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        L lineterminator,
        __ss_int quoting,
        E escapechar,
        __ss_int strict
    ) {
        this->__class__ = cl_DictReader;

        /* CPython's DictReader and DictWriter always pass a dialect on
           ("excel" by default), so only an explicit None counts as not given */
        bool dialect_given;
        Dialect *from_dialect = __csv_dialect_arg(dialect_, dialect_given);
        if constexpr (std::is_same_v<D, __ss_void_struct>)
            dialect_given = true;

        __init__(
            f,
            fieldnames_,
            restkey_,
            restval_,
            from_dialect,
            dialect_given,
            __csv_str_arg(delimiter),
            __csv_str_arg(quotechar),
            doublequote,
            skipinitialspace,
            __csv_str_arg(lineterminator),
            quoting,
            __csv_str_arg(escapechar),
            strict
        );
    }

    void *__init__(
        pyiter<str *> *f,
        pyiter<str *> *fieldnames_,
        str *restkey_,
        str *restval_,
        Dialect *dialect_,
        bool dialect_given,
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
    template<class T> void *setfieldnames(T *value) { return setfieldnames(new list<str *>(value)); } /* tuple.. */
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
    template<class D, class DL, class Q, class L, class E> DictWriter(
        file *f,
        pyiter<str *> *fieldnames_,
        str *restval_,
        str *extrasaction_,
        D dialect_,
        DL delimiter,
        Q quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        L lineterminator,
        __ss_int quoting,
        E escapechar,
        __ss_int strict
    ) {
        this->__class__ = cl_DictWriter;

        /* CPython's DictReader and DictWriter always pass a dialect on
           ("excel" by default), so only an explicit None counts as not given */
        bool dialect_given;
        Dialect *from_dialect = __csv_dialect_arg(dialect_, dialect_given);
        if constexpr (std::is_same_v<D, __ss_void_struct>)
            dialect_given = true;

        __init__(
            f,
            fieldnames_,
            restval_,
            extrasaction_,
            from_dialect,
            dialect_given,
            __csv_str_arg(delimiter),
            __csv_str_arg(quotechar),
            doublequote,
            skipinitialspace,
            __csv_str_arg(lineterminator),
            quoting,
            __csv_str_arg(escapechar),
            strict
        );
    }

    void *__init__(
        file *f,
        pyiter<str *> *fieldnames_,
        str *restval_,
        str *extrasaction_,
        Dialect *dialect_,
        bool dialect_given,
        str *delimiter,
        str *quotechar,
        __ss_int doublequote,
        __ss_int skipinitialspace,
        str *lineterminator,
        __ss_int quoting,
        str *escapechar,
        __ss_int strict
    );

    __ss_int writeheader();

    /* like CPython, accept dicts with any value type: values are written
       as by writer.writerow, missing fields as restval */
    template<class T> __ss_int writerow(T *rowdict) {
        if (this->extrasaction->unit == U"raise") {
            list<str *> *wrong_fields = new list<str *>();
            typename T::for_in_unit k;
            typename T::for_in_loop __3;
            int __2;
            T *__1;
            FOR_IN(k,rowdict,1,2,3)
                if (!this->fieldnames->__contains__(k))
                    wrong_fields->append(repr(k));
            END_FOR
            if (___bool(wrong_fields))
                throw new ValueError((new str("dict contains fields not in fieldnames: "))->__add__((new str(", "))->join(wrong_fields)));
        }

        writer *w = this->_writer;
        bool null_field = false;
        w->join_reset();
        for (str *key : this->fieldnames->units) {
            if (rowdict->__contains__(key))
                null_field = w->append_field(rowdict->__getitem__(key));
            else
                null_field = w->append_field(this->restval);
        }
        return w->join_finish(null_field);
    }

    template<class T> void *writerows(T *rowdicts) {
        typename T::for_in_unit rowdict;
        typename T::for_in_loop __3;
        int __2;
        T *__1;

        FOR_IN(rowdict,rowdicts,1,2,3)
            this->writerow(rowdict);
        END_FOR

        return NULL;
    }
};

class Sniffer : public pyobj {
public:
    list<str *> *preferred;

    Sniffer() {
        this->__class__ = cl_Sniffer;
        preferred = new list<str *>();
        preferred->append(new str(","));
        preferred->append(new str("\t"));
        preferred->append(new str(";"));
        preferred->append(new str(" "));
        preferred->append(new str(":"));
    }
    void *__init__();

    Dialect *sniff(str *sample, str *delimiters = 0);
    __ss_bool has_header(str *sample);
};

list<str *> *list_dialects();

Dialect *get_dialect(str *name);

void *_register_dialect(
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
);

template<class DL, class Q, class L, class E> void *register_dialect( // TODO template dialect
    str *name,
    str *dialect,
    DL delimiter,
    Q quotechar,
    __ss_int doublequote,
    __ss_int skipinitialspace,
    L lineterminator,
    __ss_int quoting,
    E escapechar,
    __ss_int strict
) {
    return _register_dialect(name, dialect, __csv_str_arg(delimiter), __csv_str_arg(quotechar), doublequote, skipinitialspace, __csv_str_arg(lineterminator), quoting, __csv_str_arg(escapechar), strict);
}

void *unregister_dialect(str *name);

__ss_int field_size_limit(__ss_int new_limit);

void __init();

} // module namespace
#endif
