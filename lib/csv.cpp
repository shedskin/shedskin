#include "csv.hpp"

namespace __csv__ {

str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;

str *__name__;
list<int> *__0, *__1;
int EAT_CRNL, ESCAPED_CHAR, ESCAPE_IN_QUOTED_FIELD, IN_FIELD, IN_QUOTED_FIELD, QUOTE_ALL, QUOTE_IN_QUOTED_FIELD, QUOTE_MINIMAL, QUOTE_NONE, QUOTE_NONNUMERIC, START_FIELD, START_RECORD, _field_limit;
OSError *__exception;

void * default_5;
void * default_6;
void * default_3;
void * default_4;
void * default_8;
void * default_1;
void * default_2;
void * default_9;
void * default_7;
void * default_10;
void * default_0;

__csviter::__csviter(reader *r) {
    this->r = r;
}

list<str *> *__csviter::next() {
    return r->next();
}

__csviter *reader::__iter__() {
    return new __csviter(this);
}

/**
class Error
*/

class_ *cl_Error;

/**
class Excel
*/

class_ *cl_Excel;

void *Excel::__init__() {
    
    this->delimiter = const_0;
    this->quotechar = const_1;
    this->doublequote = 1;
    this->skipinitialspace = 0;
    this->lineterminator = const_2;
    this->quoting = QUOTE_MINIMAL;
    this->escapechar = ((str *)(NULL));
    this->strict = 0;
    return NULL;
}

/**
class reader
*/

class_ *cl_reader;

void *reader::parse_process_char(str *c) {
    Excel *dialect;
    int __10, __11, __12, __13, __14, __7, __8, __9;

    dialect = this->dialect;
    if ((this->state==START_RECORD)) {
        if (__eq(c, const_3)) {
            return NULL;
        }
        else if ((const_4)->__contains__(c)) {
            this->state = EAT_CRNL;
            return NULL;
        }
        this->state = START_FIELD;
    }
    if ((this->state==START_FIELD)) {
        if ((const_5)->__contains__(c)) {
            this->parse_save_field();
            if (__eq(c, const_3)) {
                this->state = START_RECORD;
            }
            else {
                this->state = EAT_CRNL;
            }
        }
        else if (__AND(__eq(c, dialect->quotechar), (dialect->quoting!=QUOTE_NONE), 7)) {
            this->state = IN_QUOTED_FIELD;
        }
        else if (__eq(c, dialect->escapechar)) {
            this->state = ESCAPED_CHAR;
        }
        else if (__AND(__eq(c, const_6), dialect->skipinitialspace, 9)) {
        }
        else if (__eq(c, dialect->delimiter)) {
            this->parse_save_field();
        }
        else {
            if ((dialect->quoting==QUOTE_NONNUMERIC)) {
                this->numeric_field = 1;
            }
            this->parse_add_char(c);
            this->state = IN_FIELD;
        }
    }
    else if ((this->state==ESCAPED_CHAR)) {
        if (__eq(c, const_3)) {
            c = const_7;
        }
        this->parse_add_char(c);
        this->state = IN_FIELD;
    }
    else if ((this->state==IN_FIELD)) {
        if ((const_8)->__contains__(c)) {
            this->parse_save_field();
            if (__eq(c, const_3)) {
                this->state = START_RECORD;
            }
            else {
                this->state = EAT_CRNL;
            }
        }
        else if (__eq(c, dialect->escapechar)) {
            this->state = ESCAPED_CHAR;
        }
        else if (__eq(c, dialect->delimiter)) {
            this->parse_save_field();
            this->state = START_FIELD;
        }
        else {
            this->parse_add_char(c);
        }
    }
    else if ((this->state==IN_QUOTED_FIELD)) {
        if (__eq(c, const_3)) {
        }
        else if (__eq(c, dialect->escapechar)) {
            this->state = ESCAPE_IN_QUOTED_FIELD;
        }
        else if (__AND(__eq(c, dialect->quotechar), (dialect->quoting!=QUOTE_NONE), 11)) {
            if (dialect->doublequote) {
                this->state = QUOTE_IN_QUOTED_FIELD;
            }
            else {
                this->state = IN_FIELD;
            }
        }
        else {
            this->parse_add_char(c);
        }
    }
    else if ((this->state==ESCAPE_IN_QUOTED_FIELD)) {
        if (__eq(c, const_3)) {
            c = const_7;
        }
        this->parse_add_char(c);
        this->state = IN_QUOTED_FIELD;
    }
    else if ((this->state==QUOTE_IN_QUOTED_FIELD)) {
        if (__AND((dialect->quoting!=QUOTE_NONE), __eq(c, dialect->quotechar), 13)) {
            this->parse_add_char(c);
            this->state = IN_QUOTED_FIELD;
        }
        else if (__eq(c, dialect->delimiter)) {
            this->parse_save_field();
            this->state = START_FIELD;
        }
        else if ((const_8)->__contains__(c)) {
            this->parse_save_field();
            if (__eq(c, const_3)) {
                this->state = START_RECORD;
            }
            else {
                this->state = EAT_CRNL;
            }
        }
        else if ((!dialect->strict)) {
            this->parse_add_char(c);
            this->state = IN_FIELD;
        }
        else {
            throw ((new Error(__modct(const_9, 2, dialect->delimiter, dialect->quotechar))));
        }
    }
    else if ((this->state==EAT_CRNL)) {
        if ((const_4)->__contains__(c)) {
        }
        else if (__eq(c, const_3)) {
            this->state = START_RECORD;
        }
        else {
            throw ((new Error(const_10)));
        }
    }
    return 0;
}

void *reader::parse_reset() {
    
    this->fields = (new list<str *>());
    this->field = (new list<str *>());
    this->state = START_RECORD;
    this->numeric_field = 0;
    return NULL;
}

list<str *> *reader::next() {
    list<str *> *fields;
    str *__4, *c, *line;
    __iter<str *> *__5;
    int __6;

    this->parse_reset();

    while (1) {
        line = (this->input_iter)->next();
        this->line_num = (this->line_num+1);

        FOR_IN(c,line,5)
            if (__eq(c, const_3)) {
                throw ((new Error(const_11)));
            }
            this->parse_process_char(c);
        END_FOR

        this->parse_process_char(const_3);
        if ((this->state==START_RECORD)) {
            break;
        }
    }
    fields = this->fields;
    this->fields = (new list<str *>());
    return fields;
}

void *reader::__init__(file *input_iter, str *dialect, str *delimiter, str *quotechar, int doublequote, int skipinitialspace, str *lineterminator, int quoting, str *escapechar, int strict) {
    
    this->input_iter = input_iter;
    this->line_num = 0;
    this->dialect = _get_dialect(dialect, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict);
    return NULL;
}

void *reader::parse_save_field() {
    str *field;

    field = (const_12)->join(this->field);
    this->field = (new list<str *>());
    if (this->numeric_field) {
        this->numeric_field = 0;
    }
    (this->fields)->append(field);
    return NULL;
}

void *reader::parse_add_char(str *c) {
    
    if ((len(this->field)>=_field_limit)) {
        throw ((new Error(__modct(const_13, 1, __box(_field_limit)))));
    }
    (this->field)->append(c);
    return NULL;
}

/**
class writer
*/

class_ *cl_writer;

int writer::join_append_data(str *field, int quote_empty, int quoted) {
    __iter<str *> *__16;
    str *__15, *c, *lineterm;
    Excel *dialect;
    int __17, __18, __19, __20, __21, __22, __23, want_escape;

    dialect = this->dialect;
    lineterm = dialect->lineterminator;
    if ((this->num_fields>0)) {
        (this->rec)->append(dialect->delimiter);
    }
    if (quoted) {
        (this->rec)->append(dialect->quotechar);
    }

    FOR_IN(c,field,16)
        want_escape = 0;
        if (__eq(c, const_3)) {
            break;
        }
        if (__OR(__eq(c, dialect->delimiter), __OR(__eq(c, dialect->escapechar), __OR(__eq(c, dialect->quotechar), lineterm->__contains__(c), 20), 19), 18)) {
            if ((dialect->quoting==QUOTE_NONE)) {
                want_escape = 1;
            }
            else {
                if (__eq(c, dialect->quotechar)) {
                    if (dialect->doublequote) {
                        (this->rec)->append(dialect->quotechar);
                    }
                    else {
                        want_escape = 1;
                    }
                }
                if ((!want_escape)) {
                    quoted = 1;
                }
            }
            if (want_escape) {
                if ((!___bool(dialect->escapechar))) {
                    throw ((new Error(const_14)));
                }
                (this->rec)->append(dialect->escapechar);
            }
        }
        (this->rec)->append(c);
    END_FOR

    if (__AND((!___bool(field)), quote_empty, 22)) {
        if ((dialect->quoting==QUOTE_NONE)) {
            throw ((new Error(const_15)));
        }
        else {
            quoted = 1;
        }
    }
    if (quoted) {
        (this->rec)->append(dialect->quotechar);
    }
    return quoted;
}

void *writer::writerow(list<str *> *seq) {
    list<str *> *__24;
    __iter<str *> *__25;
    Excel *dialect;
    int __26, quoted;
    str *field;

    dialect = this->dialect;
    this->join_reset();

    FOR_IN_SEQ(field,seq,24,26)
        quoted = 0;
        if ((dialect->quoting==QUOTE_NONNUMERIC)) {
            quoted = 1;
        }
        else if ((dialect->quoting==QUOTE_ALL)) {
            quoted = 1;
        }
        if ((field==NULL)) {
            quoted = this->join_append(const_12, quoted, (len(seq)==1));
        }
        else {
            quoted = this->join_append(__str(field), quoted, (len(seq)==1));
        }
    END_FOR

    (this->rec)->append((this->dialect)->lineterminator);
    (this->output_file)->write((const_12)->join(this->rec));
    return NULL;
}

void *writer::join_reset() {
    
    this->rec = (new list<str *>());
    this->num_fields = 0;
    return NULL;
}

void *writer::writerows(list<list<str *> *> *seqs) {
    __iter<list<str *> *> *__28;
    list<str *> *seq;
    list<list<str *> *> *__27;
    int __29;


    FOR_IN_SEQ(seq,seqs,27,29)
        this->writerow(seq);
    END_FOR

    return NULL;
}

int writer::join_append(str *field, int quoted, int quote_empty) {
    
    quoted = this->join_append_data(field, quote_empty, quoted);
    this->num_fields = (this->num_fields+1);
    return quoted;
}

void *writer::__init__(file *output_file, str *dialect, str *delimiter, str *quotechar, int doublequote, int skipinitialspace, str *lineterminator, int quoting, str *escapechar, int strict) {
    
    this->output_file = output_file;
    this->dialect = _get_dialect(dialect, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict);
    return NULL;
}

void __init() {
    const_0 = new str(",");
    const_1 = new str("\"");
    const_2 = new str("\r\n");
    const_3 = new str("\000", 1);
    const_4 = new str("\n\r");
    const_5 = new str("\n\r\000", 3);
    const_6 = new str(" ");
    const_7 = new str("\n");
    const_8 = new str("\000\n\r", 3);
    const_9 = new str("'%c' expected after '%c'");
    const_10 = new str("new-line character seen in unquoted field - do you need to open the file in universal-newline mode?");
    const_11 = new str("line contains NULL byte");
    const_12 = new str("");
    const_13 = new str("field larger than field limit (%d)");
    const_14 = new str("need to escape, but no escapechar set");
    const_15 = new str("single empty field record must be quoted");
    const_16 = new str("excel");
    const_17 = new str("excel-tab");
    const_18 = new str("\t");
    const_19 = new str("unknown dialect");

    __name__ = new str("csv");

    cl_writer = new class_("writer", 44, 44);
    cl_reader = new class_("reader", 3, 3);
    cl_Excel = new class_("Excel", 43, 43);
    cl_Error = new class_("Error", 26, 26);

    __0 = range(8);
    START_RECORD = __0->__getfast__(0);
    START_FIELD = __0->__getfast__(1);
    ESCAPED_CHAR = __0->__getfast__(2);
    IN_FIELD = __0->__getfast__(3);
    IN_QUOTED_FIELD = __0->__getfast__(4);
    ESCAPE_IN_QUOTED_FIELD = __0->__getfast__(5);
    QUOTE_IN_QUOTED_FIELD = __0->__getfast__(6);
    EAT_CRNL = __0->__getfast__(7);
    __1 = range(4);
    QUOTE_MINIMAL = __1->__getfast__(0);
    QUOTE_ALL = __1->__getfast__(1);
    QUOTE_NONNUMERIC = __1->__getfast__(2);
    QUOTE_NONE = __1->__getfast__(3);
    _field_limit = (128*1024);
    default_0 = NULL;
    default_1 = NULL;
    default_2 = NULL;
    default_3 = NULL;
    default_4 = NULL;
    default_5 = NULL;
    default_6 = NULL;
    default_7 = NULL;
    default_8 = NULL;
    default_9 = NULL;
}

list<str *> *list_dialects() {
    
    return (new list<str *>(2, const_16, const_17));
}

Excel *_get_dialect(str *name, str *delimiter, str *quotechar, int doublequote, int skipinitialspace, str *lineterminator, int quoting, str *escapechar, int strict) {
    Excel *dialect;
    int __2, __3;

    if (__OR((name==NULL), (__eq(name,const_16)), 2)) {
        dialect = (new Excel(1));
    }
    else if (__eq(name, const_17)) {
        dialect = (new Excel(1));
        dialect->delimiter = const_18;
    }
    else {
        throw ((new Error(const_19)));
    }
    if ((delimiter!=NULL)) {
        dialect->delimiter = delimiter;
    }
    if ((quotechar!=NULL)) {
        dialect->quotechar = quotechar;
    }
    if ((doublequote!=(-1))) {
        dialect->doublequote = doublequote;
    }
    if ((skipinitialspace!=(-1))) {
        dialect->skipinitialspace = skipinitialspace;
    }
    if ((lineterminator!=NULL)) {
        dialect->lineterminator = lineterminator;
    }
    if ((quoting!=(-1))) {
        dialect->quoting = quoting;
    }
    if ((escapechar!=NULL)) {
        dialect->escapechar = escapechar;
    }
    if ((strict!=(-1))) {
        dialect->strict = strict;
    }
    return dialect;
}

int field_size_limit(int new_limit) {
    int old_limit;

    old_limit = _field_limit;
    if ((new_limit!=(-1))) {
        _field_limit = new_limit;
    }
    return old_limit;
}

} // module namespace

