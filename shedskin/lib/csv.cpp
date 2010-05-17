#include "csv.hpp"

namespace __csv__ {

tuple2<str *, str *> *const_3;
str *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_2, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_26, *const_27, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;
list<void *> *const_0;
str *const_88;

str *__name__;
list<__ss_int> *__0, *__1;
__ss_int EAT_CRNL, ESCAPED_CHAR, ESCAPE_IN_QUOTED_FIELD, IN_FIELD, IN_QUOTED_FIELD, QUOTE_ALL, QUOTE_IN_QUOTED_FIELD, QUOTE_MINIMAL, QUOTE_NONE, QUOTE_NONNUMERIC, START_FIELD, START_RECORD, _field_limit;
OSError *__exception;

void * default_9;
void * default_14;
void * default_16;
void * default_21;
void * default_23;
str * default_18;
void * default_25;
void * default_0;
void * default_2;
void * default_6;
void * default_3;
void * default_8;
void * default_10;
void * default_11;
void * default_13;
void * default_15;
void * default_12;
void * default_17;
void * default_24;
str * default_19;
str * default_20;
void * default_22;
void * default_7;
void * default_1;
void * default_5;
void * default_4;

__csviter::__csviter(reader *r) {
    this->r = r;
}

list<str *> *__csviter::next() {
    return r->next();
}

__csviter *reader::__iter__() {
    return new __csviter(this);
}

__driter::__driter(DictReader *r) {
    this->r = r;
}

dict<str *, str *> *__driter::next() {
    return r->next();
}

__driter *DictReader::__iter__() {
    return new __driter(this);
}

static inline list<str *> *list_comp_0(DictWriter *self, dict<str *, str *> *rowdict) {
    __iter<str *> *__35;
    str *k;
    __ss_int __36;
    dict<str *, str *> *__34;
    list<str *> *__ss_result = new list<str *>();

    FOR_IN(k,rowdict,35)
        if ((!(self->fieldnames)->__contains__(k))) {
            __ss_result->append(k);
        }
    END_FOR

    return __ss_result;
}

static inline list<str *> *list_comp_1(DictWriter *self, dict<str *, str *> *rowdict) {
    list<str *> *__37;
    __iter<str *> *__38;
    __ss_int __39;
    str *key;
    list<str *> *__ss_result = new list<str *>();

    __37 = self->fieldnames;
    __ss_result->resize(len(__37));
    FOR_IN_SEQ(key,__37,37,39)
        __ss_result->units[__39] = rowdict->get(key, self->restval);
    END_FOR

    return __ss_result;
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
    
    this->delimiter = const_4;
    this->quotechar = const_5;
    this->doublequote = 1;
    this->skipinitialspace = 0;
    this->lineterminator = const_6;
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
    __ss_int __10, __11, __12, __13, __14, __7, __8, __9;

    dialect = this->dialect;
    if ((this->state==START_RECORD)) {
        if (__eq(c, const_7)) {
            return NULL;
        }
        else if ((const_8)->__contains__(c)) {
            this->state = EAT_CRNL;
            return NULL;
        }
        this->state = START_FIELD;
    }
    if ((this->state==START_FIELD)) {
        if ((const_9)->__contains__(c)) {
            this->parse_save_field();
            if (__eq(c, const_7)) {
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
        else if (__AND(__eq(c, const_10), dialect->skipinitialspace, 9)) {
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
        if (__eq(c, const_7)) {
            c = const_11;
        }
        this->parse_add_char(c);
        this->state = IN_FIELD;
    }
    else if ((this->state==IN_FIELD)) {
        if ((const_12)->__contains__(c)) {
            this->parse_save_field();
            if (__eq(c, const_7)) {
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
        if (__eq(c, const_7)) {
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
        if (__eq(c, const_7)) {
            c = const_11;
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
        else if ((const_12)->__contains__(c)) {
            this->parse_save_field();
            if (__eq(c, const_7)) {
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
            throw ((new Error(__modct(const_13, 2, dialect->delimiter, dialect->quotechar))));
        }
    }
    else if ((this->state==EAT_CRNL)) {
        if ((const_8)->__contains__(c)) {
        }
        else if (__eq(c, const_7)) {
            this->state = START_RECORD;
        }
        else {
            throw ((new Error(const_14)));
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
    __ss_int __6;

    this->parse_reset();

    while (1) {
        line = (this->input_iter)->next();
        this->line_num = (this->line_num+1);

        FOR_IN(c,line,5)
            if (__eq(c, const_7)) {
                throw ((new Error(const_15)));
            }
            this->parse_process_char(c);
        END_FOR

        this->parse_process_char(const_7);
        if ((this->state==START_RECORD)) {
            break;
        }
    }
    fields = this->fields;
    this->fields = (new list<str *>());
    return fields;
}

void *reader::__init__(file *input_iter, str *dialect, str *delimiter, str *quotechar, __ss_int doublequote, __ss_int skipinitialspace, str *lineterminator, __ss_int quoting, str *escapechar, __ss_int strict) {
    if ((quoting==QUOTE_NONNUMERIC)) {
        throw ((new ValueError(const_88)));
    }
    this->input_iter = input_iter;
    this->line_num = 0;
    this->dialect = _get_dialect(dialect, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict);
    return NULL;
}

void *reader::parse_save_field() {
    str *field;

    field = (const_16)->join(this->field);
    this->field = (new list<str *>());
    if (this->numeric_field) {
        this->numeric_field = 0;
    }
    (this->fields)->append(field);
    return NULL;
}

void *reader::parse_add_char(str *c) {
    
    if ((len(this->field)>=_field_limit)) {
        throw ((new Error(__modct(const_17, 1, ___box(_field_limit)))));
    }
    (this->field)->append(c);
    return NULL;
}

/**
class writer
*/

class_ *cl_writer;

__ss_int writer::join_append_data(str *field, __ss_int quote_empty, __ss_int quoted) {
    __iter<str *> *__16;
    str *__15, *c, *lineterm;
    Excel *dialect;
    __ss_int __17, __18, __19, __20, __21, __22, __23, want_escape;

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
        if (__eq(c, const_7)) {
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
                    throw ((new Error(const_18)));
                }
                (this->rec)->append(dialect->escapechar);
            }
        }
        (this->rec)->append(c);
    END_FOR

    if (__AND((!___bool(field)), quote_empty, 22)) {
        if ((dialect->quoting==QUOTE_NONE)) {
            throw ((new Error(const_19)));
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
    __ss_int __26, quoted;
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
            quoted = this->join_append(const_16, quoted, (len(seq)==1));
        }
        else {
            quoted = this->join_append(__str(field), quoted, (len(seq)==1));
        }
    END_FOR

    (this->rec)->append((this->dialect)->lineterminator);
    (this->output_file)->write((const_16)->join(this->rec));
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
    __ss_int __29;


    FOR_IN_SEQ(seq,seqs,27,29)
        this->writerow(seq);
    END_FOR

    return NULL;
}

__ss_int writer::join_append(str *field, __ss_int quoted, __ss_int quote_empty) {
    
    quoted = this->join_append_data(field, quote_empty, quoted);
    this->num_fields = (this->num_fields+1);
    return quoted;
}

void *writer::__init__(file *output_file, str *dialect, str *delimiter, str *quotechar, __ss_int doublequote, __ss_int skipinitialspace, str *lineterminator, __ss_int quoting, str *escapechar, __ss_int strict) {
    if ((quoting==QUOTE_NONNUMERIC)) {
        throw ((new ValueError(const_88)));
    }
    this->output_file = output_file;
    this->dialect = _get_dialect(dialect, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict);
    return NULL;
}

/**
class DictReader
*/

class_ *cl_DictReader;

void *DictReader::setfieldnames(list<str *> *value) {
    
    this->_fieldnames = value;
    return NULL;
}

dict<str *, str *> *DictReader::next() {
    str *key;
    list<str *> *__31, *row;
    __iter<str *> *__32;
    __ss_int __33, lf, lr;
    dict<str *, str *> *d;

    if ((this->line_num==0)) {
        this->getfieldnames();
    }
    row = (this->_reader)->next();
    this->line_num = (this->_reader)->line_num;

    while (row->empty()) {
        row = (this->_reader)->next();
    }
    d = new dict<str *, str *>(__zip(2, this->getfieldnames(), row));
    lf = len(this->getfieldnames());
    lr = len(row);
    if ((lf<lr)) {
        throw ((new Error(const_20)));
    }
    else if ((lf>lr)) {

        FOR_IN_SEQ(key,(this->getfieldnames())->__slice__(1, lr, 0, 0),31,33)
            d->__setitem__(key, this->restval);
        END_FOR

    }
    return d;
}

list<str *> *DictReader::getfieldnames() {
    
    if ((this->_fieldnames==NULL)) {
        try {
            this->_fieldnames = (this->_reader)->next();
        } catch (StopIteration *) {
        }
    }
    this->line_num = (this->_reader)->line_num;
    return this->_fieldnames;
}

void *DictReader::__init__(file *f, list<str *> *fieldnames, str *restkey, str *restval, str *dialect, str *delimiter, str *quotechar, __ss_int doublequote, __ss_int skipinitialspace, str *lineterminator, __ss_int quoting, str *escapechar, __ss_int strict) {
    
    this->_fieldnames = fieldnames;
    this->restkey = restkey;
    this->restval = restval;
    this->_reader = (new reader(f, dialect, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict));
    this->dialect = dialect;
    this->line_num = 0;
    return NULL;
}

/**
class DictWriter
*/

class_ *cl_DictWriter;

list<str *> *DictWriter::_dict_to_list(dict<str *, str *> *rowdict) {
    list<str *> *wrong_fields;

    if (__eq(this->extrasaction, const_1)) {
        wrong_fields = list_comp_0(this, rowdict);
        if (___bool(wrong_fields)) {
            throw ((new ValueError((const_21)->__add__((const_22)->join(wrong_fields)))));
        }
    }
    return list_comp_1(this, rowdict);
}

void *DictWriter::writerow(dict<str *, str *> *rowdict) {
    
    return (this->_writer)->writerow(this->_dict_to_list(rowdict));
}

void *DictWriter::writerows(list<dict<str *, str *> *> *rowdicts) {
    __iter<dict<str *, str *> *> *__41;
    list<list<str *> *> *rows;
    list<dict<str *, str *> *> *__40;
    __ss_int __42;
    dict<str *, str *> *rowdict;

    rows = (new list<list<str *> *>());

    FOR_IN_SEQ(rowdict,rowdicts,40,42)
        rows->append(this->_dict_to_list(rowdict));
    END_FOR

    return (this->_writer)->writerows(rows);
}

void *DictWriter::__init__(file *f, list<str *> *fieldnames, str *restval, str *extrasaction, str *dialect, str *delimiter, str *quotechar, __ss_int doublequote, __ss_int skipinitialspace, str *lineterminator, __ss_int quoting, str *escapechar, __ss_int strict) {
    
    this->fieldnames = fieldnames;
    this->restval = restval;
    if ((!(const_3)->__contains__(extrasaction->lower()))) {
        throw ((new ValueError(__modct(const_23, 1, extrasaction))));
    }
    this->extrasaction = extrasaction;
    this->_writer = (new writer(f, dialect, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict));
    return NULL;
}

void __init() {
    const_0 = (new list<void *>());
    const_1 = new str("raise");
    const_2 = new str("ignore");
    const_3 = (new tuple2<str *, str *>(2, const_1, const_2));
    const_4 = new str(",");
    const_5 = new str("\"");
    const_6 = new str("\r\n");
    const_7 = new str("\000", 1);
    const_8 = new str("\n\r");
    const_9 = new str("\n\r\000", 3);
    const_10 = new str(" ");
    const_11 = new str("\n");
    const_12 = new str("\000\n\r", 3);
    const_13 = new str("'%c' expected after '%c'");
    const_14 = new str("new-line character seen in unquoted field - do you need to open the file in universal-newline mode?");
    const_15 = new str("line contains NULL byte");
    const_16 = new str("");
    const_17 = new str("field larger than field limit (%d)");
    const_18 = new str("need to escape, but no escapechar set");
    const_19 = new str("single empty field record must be quoted");
    const_20 = new str("shedskin: DictReader 'restkey' is not supported");
    const_21 = new str("dict contains fields not in fieldnames: ");
    const_22 = new str(", ");
    const_23 = new str("extrasaction (%s) must be 'raise' or 'ignore'");
    const_24 = new str("excel");
    const_25 = new str("excel-tab");
    const_26 = new str("\t");
    const_27 = new str("unknown dialect");
    const_88 = new str("shedskin: QUOTE_NONNUMERIC is not supported");

    __name__ = new str("csv");

    cl_writer = new class_("writer", 21, 21);
    cl_DictReader = new class_("DictReader", 48, 48);
    cl_Excel = new class_("Excel", 46, 46);
    cl_reader = new class_("reader", 44, 44);
    cl_Error = new class_("Error", 43, 43);
    cl_DictWriter = new class_("DictWriter", 2, 2);

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
    default_10 = NULL;
    default_11 = NULL;
    default_12 = NULL;
    default_13 = NULL;
    default_14 = NULL;
    default_15 = NULL;
    default_16 = NULL;
    default_17 = NULL;
    default_18 = const_16;
    default_19 = const_1;
    default_20 = const_24;
    default_21 = NULL;
    default_22 = NULL;
    default_23 = NULL;
    default_24 = NULL;
}

list<str *> *list_dialects() {
    
    return (new list<str *>(2, const_24, const_25));
}

Excel *_get_dialect(str *name, str *delimiter, str *quotechar, __ss_int doublequote, __ss_int skipinitialspace, str *lineterminator, __ss_int quoting, str *escapechar, __ss_int strict) {
    Excel *dialect;
    __ss_int __2, __3;

    if (__OR((name==NULL), __eq(name, const_24), 2)) {
        dialect = (new Excel(1));
    }
    else if (__eq(name, const_25)) {
        dialect = (new Excel(1));
        dialect->delimiter = const_26;
    }
    else {
        throw ((new Error(const_27)));
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

__ss_int field_size_limit(__ss_int new_limit) {
    __ss_int old_limit;

    old_limit = _field_limit;
    if ((new_limit!=(-1))) {
        _field_limit = new_limit;
    }
    return old_limit;
}

} // module namespace

