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
    template<class D> reader(
        pyiter<str *> *input_iter_,
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

        Dialect *from_dialect;
        if constexpr (std::is_same_v<D, str *>) {
            from_dialect = _lookup_dialect(dialect_);
        }
        else if constexpr (std::is_convertible_v<D, Dialect *>) { /* Dialect or predefined subclass instance */
            from_dialect = dialect_ ? (Dialect *)(dialect_) : _lookup_dialect(new str("excel"));
        }
        else /* omitted (__ss_void) or None */
            from_dialect = _lookup_dialect(new str("excel"));

        __init__(
            input_iter_,
            from_dialect,
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
        pyiter<str *> *input_iter_,
        Dialect *dialect_,
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
    template <class D> writer(
        file *output_file_,
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
        this->__class__ = cl_writer;

        Dialect *from_dialect;
        if constexpr (std::is_same_v<D, str *>) {
            from_dialect = _lookup_dialect(dialect_);
        }
        else if constexpr (std::is_convertible_v<D, Dialect *>) { /* Dialect or predefined subclass instance */
            from_dialect = dialect_ ? (Dialect *)(dialect_) : _lookup_dialect(new str("excel"));
        }
        else /* omitted (__ss_void) or None */
            from_dialect = _lookup_dialect(new str("excel"));

        __init__(
            output_file_,
            from_dialect,
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
        Dialect *dialect_,
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
        __ss_int quoting = this->dialect->quoting;
        bool null_field = false;

        this->join_reset();

        FOR_IN(field,seq,1,2,3)
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
        END_FOR

        return this->join_finish(null_field);
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
    template <class D> DictReader(
        pyiter<str *> *f,
        pyiter<str *> *fieldnames_,
        str *restkey_,
        str *restval_,
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
        this->__class__ = cl_DictReader;

        Dialect *from_dialect;
        if constexpr (std::is_same_v<D, str *>) {
            from_dialect = _lookup_dialect(dialect_);
        }
        else if constexpr (std::is_convertible_v<D, Dialect *>) { /* Dialect or predefined subclass instance */
            from_dialect = dialect_ ? (Dialect *)(dialect_) : _lookup_dialect(new str("excel"));
        }
        else /* omitted (__ss_void) or None */
            from_dialect = _lookup_dialect(new str("excel"));

        __init__(
            f,
            fieldnames_,
            restkey_,
            restval_,
            from_dialect,
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
        pyiter<str *> *f,
        pyiter<str *> *fieldnames_,
        str *restkey_,
        str *restval_,
        Dialect *dialect_,
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
    template <class D> DictWriter(
        file *f,
        pyiter<str *> *fieldnames_,
        str *restval_,
        str *extrasaction_,
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
        this->__class__ = cl_DictWriter;

        Dialect *from_dialect;
        if constexpr (std::is_same_v<D, str *>) {
            from_dialect = _lookup_dialect(dialect_);
        }
        else if constexpr (std::is_convertible_v<D, Dialect *>) { /* Dialect or predefined subclass instance */
            from_dialect = dialect_ ? (Dialect *)(dialect_) : _lookup_dialect(new str("excel"));
        }
        else /* omitted (__ss_void) or None */
            from_dialect = _lookup_dialect(new str("excel"));

        __init__(
            f,
            fieldnames_,
            restval_,
            extrasaction_,
            from_dialect,
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
        Dialect *dialect_,
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
    __ss_int writerow(dict<str *, str *> *rowdict);
    void *writerows(pyiter<dict<str *, str *> *> *rowdicts);

    // internal
    list<str *> *_dict_to_list(dict<str *, str *> *rowdict);
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
