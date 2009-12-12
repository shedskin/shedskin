#include "csv.hpp"

namespace __csv__ {

str *const_0, *const_1, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;

str *__name__;
list<int> *__0, *__1;
OSError *__exception;
int EAT_CRNL, ESCAPED_CHAR, ESCAPE_IN_QUOTED_FIELD, IN_FIELD, IN_QUOTED_FIELD, QUOTE_ALL, QUOTE_IN_QUOTED_FIELD, QUOTE_MINIMAL, QUOTE_NONE, QUOTE_NONNUMERIC, START_FIELD, START_RECORD, field_limit;
Dialect *excel;

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
class Dialect
*/

class_ *cl_Dialect;

void *Dialect::__init__() {
    
    this->lineterminator = const_0;
    this->skipinitialspace = 0;
    this->quoting = 0;
    this->delimiter = const_1;
    this->quotechar = const_2;
    this->doublequote = 1;
    this->escapechar = const_3;
    this->strict = 0;
    return NULL;
}

/**
class reader
*/

class_ *cl_reader;

int reader::parse_process_char(str *c) {
    Dialect *dialect;
    int __10, __11, __12, __5, __6, __7, __8, __9;

    dialect = this->dialect;
    if ((this->state==START_RECORD)) {
        if (__eq(c, const_4)) {
            return 0;
        }
        else if ((const_5)->__contains__(c)) {
            this->state = EAT_CRNL;
            return 0;
        }
        this->state = START_FIELD;
    }
    if ((this->state==START_FIELD)) {
        if ((const_6)->__contains__(c)) {
            if ((this->parse_save_field()<0)) {
                return (-1);
            }
            if (__eq(c, const_4)) {
                this->state = START_RECORD;
            }
            else {
                this->state = EAT_CRNL;
            }
        }
        else if (__AND(__eq(c, dialect->quotechar), (dialect->quoting!=QUOTE_NONE), 5)) {
            this->state = IN_QUOTED_FIELD;
        }
        else if (__eq(c, dialect->escapechar)) {
            this->state = ESCAPED_CHAR;
        }
        else if (__AND(__eq(c, const_7), dialect->skipinitialspace, 7)) {
        }
        else if (__eq(c, dialect->delimiter)) {
            if ((this->parse_save_field()<0)) {
                return (-1);
            }
        }
        else {
            if ((dialect->quoting==QUOTE_NONNUMERIC)) {
                throw (new Exception());
            }
            if ((this->parse_add_char(c)<0)) {
                return (-1);
            }
            this->state = IN_FIELD;
        }
    }
    else if ((this->state==ESCAPED_CHAR)) {
        if (__eq(c, const_4)) {
            c = const_8;
        }
        if ((this->parse_add_char(c)<0)) {
            return (-1);
        }
        this->state = IN_FIELD;
    }
    else if ((this->state==IN_FIELD)) {
        if ((const_9)->__contains__(c)) {
            if ((this->parse_save_field()<0)) {
                return (-1);
            }
            if (__eq(c, const_4)) {
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
            if ((this->parse_save_field()<0)) {
                return (-1);
            }
            this->state = START_FIELD;
        }
        else {
            if ((this->parse_add_char(c)<0)) {
                return (-1);
            }
        }
    }
    else if ((this->state==IN_QUOTED_FIELD)) {
        if (__eq(c, const_4)) {
        }
        else if (__eq(c, dialect->escapechar)) {
            this->state = ESCAPE_IN_QUOTED_FIELD;
        }
        else if (__AND(__eq(c, dialect->quotechar), (dialect->quoting!=QUOTE_NONE), 9)) {
            if (dialect->doublequote) {
                this->state = QUOTE_IN_QUOTED_FIELD;
            }
            else {
                this->state = IN_FIELD;
            }
        }
        else {
            if ((this->parse_add_char(c)<0)) {
                return (-1);
            }
        }
    }
    else if ((this->state==ESCAPE_IN_QUOTED_FIELD)) {
        if (__eq(c, const_4)) {
            c = const_8;
        }
        if ((this->parse_add_char(c)<0)) {
            return (-1);
        }
        this->state = IN_QUOTED_FIELD;
    }
    else if ((this->state==QUOTE_IN_QUOTED_FIELD)) {
        if (__AND((dialect->quoting!=QUOTE_NONE), __eq(c, dialect->quotechar), 11)) {
            if ((this->parse_add_char(c)<0)) {
                return (-1);
            }
            this->state = IN_QUOTED_FIELD;
        }
        else if (__eq(c, dialect->delimiter)) {
            if ((this->parse_save_field()<0)) {
                return (-1);
            }
            this->state = START_FIELD;
        }
        else if ((const_9)->__contains__(c)) {
            if ((this->parse_save_field()<0)) {
                return (-1);
            }
            if (__eq(c, const_4)) {
                this->state = START_RECORD;
            }
            else {
                this->state = EAT_CRNL;
            }
        }
        else if ((!dialect->strict)) {
            if ((this->parse_add_char(c)<0)) {
                return (-1);
            }
            this->state = IN_FIELD;
        }
        else {
            return (-1);
        }
    }
    else if ((this->state==EAT_CRNL)) {
        if ((const_5)->__contains__(c)) {
        }
        else if (__eq(c, const_4)) {
            this->state = START_RECORD;
        }
        else {
            return (-1);
        }
    }
    return 0;
}

void *reader::parse_reset() {
    
    this->fields = (new list<str *>());
    this->field = (new list<str *>());
    this->state = START_RECORD;
    return NULL;
}

list<str *> *reader::next() {
    list<str *> *fields;
    __iter<str *> *__3;
    str *__2, *c, *line;
    int __4;

    this->parse_reset();

    while (1) {
        line = (this->input_iter)->next();

        FOR_IN(c,line,3)
            if (__eq(c, const_4)) {
                return this->fields;
            }
            if ((this->parse_process_char(c)<0)) {
                return this->fields;
            }
        END_FOR

        if ((this->state!=START_RECORD)) {
            break;
        }
    }
    fields = this->fields;
    this->fields = (new list<str *>());
    return fields;
}

void *reader::__init__(file *input_iter) {
    
    this->input_iter = input_iter;
    this->line_num = 0;
    this->dialect = excel;
    return NULL;
}

int reader::parse_save_field() {
    
    (this->fields)->append((const_3)->join(this->field));
    this->field = (new list<str *>());
    return 0;
}

int reader::parse_add_char(str *c) {
    
    if ((len(this->field)>=field_limit)) {
        return (-1);
    }
    (this->field)->append(c);
    return 0;
}

/**
class writer
*/

class_ *cl_writer;

int writer::join_append_data(str *field, int quote_empty, int quoted) {
    __iter<str *> *__14;
    str *__13, *c, *lineterm;
    Dialect *dialect;
    int __15, __16, __17, __18, __19, __20, __21, want_escape;

    dialect = this->dialect;
    lineterm = dialect->lineterminator;
    if ((this->num_fields>0)) {
        (this->rec)->append(dialect->delimiter);
    }
    if (quoted) {
        (this->rec)->append(dialect->quotechar);
    }

    FOR_IN(c,field,14)
        want_escape = 0;
        if (__eq(c, const_4)) {
            break;
        }
        if (__OR(__eq(c, dialect->delimiter), __OR(__eq(c, dialect->escapechar), __OR(__eq(c, dialect->quotechar), lineterm->__contains__(c), 18), 17), 16)) {
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
                    return (-1);
                }
                (this->rec)->append(dialect->escapechar);
            }
        }
        (this->rec)->append(c);
    END_FOR

    if (__AND((!___bool(field)), quote_empty, 20)) {
        if ((dialect->quoting==QUOTE_NONE)) {
            return (-1);
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
    str *field;
    list<str *> *__22;
    __iter<str *> *__23;
    Dialect *dialect;
    int __24, quoted;

    dialect = this->dialect;
    this->join_reset();

    FOR_IN_SEQ(field,seq,22,24)
        quoted = 0;
        if ((dialect->quoting==QUOTE_NONNUMERIC)) {
            throw (new Exception());
        }
        else if ((dialect->quoting==QUOTE_ALL)) {
            quoted = 1;
        }
        if ((field==NULL)) {
            quoted = this->join_append(const_3, quoted, (len(seq)==1));
        }
        else {
            quoted = this->join_append(__str(field), quoted, (len(seq)==1));
        }
    END_FOR

    (this->rec)->append((this->dialect)->lineterminator);
    (this->output_file)->write((const_3)->join(this->rec));
    return NULL;
}

void *writer::join_reset() {
    
    this->rec = (new list<str *>());
    this->num_fields = 0;
    return NULL;
}

void *writer::writerows(list<list<str *> *> *seqs) {
    list<str *> *seq;
    __iter<list<str *> *> *__26;
    list<list<str *> *> *__25;
    int __27;


    FOR_IN_SEQ(seq,seqs,25,27)
        this->writerow(seq);
    END_FOR

    return NULL;
}

int writer::join_append(str *field, int quoted, int quote_empty) {
    
    quoted = this->join_append_data(field, quote_empty, quoted);
    this->num_fields = (this->num_fields+1);
    return quoted;
}

void *writer::__init__(file *output_file) {
    
    this->output_file = output_file;
    this->dialect = excel;
    return NULL;
}

void __init() {
    const_0 = new str("\r\n");
    const_1 = new str(",");
    const_2 = new str("\"");
    const_3 = new str("");
    const_4 = new str("\000", 1);
    const_5 = new str("\n\r");
    const_6 = new str("\n\r\000", 3);
    const_7 = new str(" ");
    const_8 = new str("\n");
    const_9 = new str("\000\n\r", 3);

    __name__ = new str("csv");

    cl_Dialect = new class_("Dialect", 29, 29);
    cl_writer = new class_("writer", 1, 1);
    cl_reader = new class_("reader", 26, 26);

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
    field_limit = (128*1024);
    excel = (new Dialect(1));
}

} // module namespace

