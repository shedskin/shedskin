#include "csv.hpp"

namespace __csv__ {

str *const_0, *const_1, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;

str *__name__;
list<int> *__0, *__1;
OSError *__exception;
int EAT_CRNL, ESCAPED_CHAR, ESCAPE_IN_QUOTED_FIELD, IN_FIELD, IN_QUOTED_FIELD, QUOTE_ALL, QUOTE_IN_QUOTED_FIELD, QUOTE_MINIMAL, QUOTE_NONE, QUOTE_NONNUMERIC, START_FIELD, START_RECORD, field_limit;
Dialect *excel;

/**
class reader
*/

class_ *cl_reader;

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
    this->escapechar = NULL;
    this->strict = 0;
    return NULL;
}

/**
class reader
*/

int reader::parse_process_char(str *c) {
    Dialect *dialect;
    int __10, __11, __12, __5, __6, __7, __8, __9;

    dialect = this->dialect;
    if ((this->state==START_RECORD)) {
        if (__eq(c, const_3)) {
            return 0;
        }
        else if ((const_4)->__contains__(c)) {
            this->state = EAT_CRNL;
            return 0;
        }
        this->state = START_FIELD;
    }
    if ((this->state==START_FIELD)) {
        if ((const_5)->__contains__(c)) {
            if ((this->parse_save_field()<0)) {
                return (-1);
            }
            if (__eq(c, const_3)) {
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
        else if (__AND(__eq(c, const_6), dialect->skipinitialspace, 7)) {
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
        if (__eq(c, const_3)) {
            c = const_7;
        }
        if ((this->parse_add_char(c)<0)) {
            return (-1);
        }
        this->state = IN_FIELD;
    }
    else if ((this->state==IN_FIELD)) {
        if ((const_8)->__contains__(c)) {
            if ((this->parse_save_field()<0)) {
                return (-1);
            }
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
        if (__eq(c, const_3)) {
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
        if (__eq(c, const_3)) {
            c = const_7;
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
        else if ((const_8)->__contains__(c)) {
            if ((this->parse_save_field()<0)) {
                return (-1);
            }
            if (__eq(c, const_3)) {
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
        if ((const_4)->__contains__(c)) {
        }
        else if (__eq(c, const_3)) {
            this->state = START_RECORD;
        }
        else {
            return (-1);
        }
    }
    return 0;
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
            if (__eq(c, const_3)) {
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

int reader::parse_add_char(str *c) {
    
    if ((len(this->field)>=field_limit)) {
        return (-1);
    }
    (this->field)->append(c);
    return 0;
}

int reader::parse_save_field() {
    
    (this->fields)->append((const_9)->join(this->field));
    this->field = (new list<str *>());
    return 0;
}

void *reader::parse_reset() {
    
    this->fields = (new list<str *>());
    this->field = (new list<str *>());
    this->state = START_RECORD;
    return NULL;
}

void *reader::__init__(file *input_iter) {
    
    this->input_iter = input_iter;
    this->line_num = 0;
    this->dialect = excel;
    return NULL;
}

void __init() {
    const_0 = new str("\r\n");
    const_1 = new str(",");
    const_2 = new str("\"");
    const_3 = new str("\000", 1);
    const_4 = new str("\n\r");
    const_5 = new str("\n\r\000", 3);
    const_6 = new str(" ");
    const_7 = new str("\n");
    const_8 = new str("\000\n\r", 3);
    const_9 = new str("");

    __name__ = new str("csv");

    cl_Dialect = new class_("Dialect", 3, 3);
    cl_reader = new class_("reader", 42, 42);

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

