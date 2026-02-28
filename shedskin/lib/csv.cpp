/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "csv.hpp"

namespace __csv__ {

str *__name__;

dict<str *, Dialect *> *_dialects;

tuple2<str *, str *> *const_3;

str *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_2, *const_20, *const_21, *const_22, *const_23, *const_25, *const_4, *const_5, *const_6, *const_7, *const_8;

char EOL = '\000';

const __ss_int QUOTE_MINIMAL = 0;
const __ss_int QUOTE_ALL = 1;
const __ss_int QUOTE_NONNUMERIC = 2;
const __ss_int QUOTE_NONE = 3;
const __ss_int QUOTE_STRINGS = 4;
const __ss_int QUOTE_NOTNULL = 5;

const __ss_int START_RECORD = 0;
const __ss_int START_FIELD = 1;
const __ss_int ESCAPED_CHAR = 2;
const __ss_int IN_FIELD = 3;
const __ss_int IN_QUOTED_FIELD = 4;
const __ss_int ESCAPE_IN_QUOTED_FIELD = 5;
const __ss_int QUOTE_IN_QUOTED_FIELD = 6;
const __ss_int EAT_CRNL = 7;
const __ss_int AFTER_ESCAPED_CRNL = 8;

__ss_int _field_limit;

class_ *cl_Error;
class_ *cl_Dialect;
class_ *cl_Excel;
class_ *cl_ExcelTab;
class_ *cl_UnixDialect;
class_ *cl_reader;
class_ *cl_writer;
class_ *cl_DictReader;
class_ *cl_DictWriter;

/* dialect */

void _dialect_check_char(str *name, str *c, Dialect *dialect, bool allowspace) { // TODO NOT_SET/None difference?
    if(!c)
        return;

    if(c->unit[0] == '\n' || c->unit[0] == '\r' || (c->unit[0] == ' ' && !allowspace))
        throw new ValueError(__add_strs(3, new str("bad "), name, new str(" value")));

    if(dialect->lineterminator != NULL) {
        if(dialect->lineterminator->__contains__(c))
            throw new ValueError(__add_strs(3, new str("bad "), name, new str(" or lineterminator value")));
    }
}

void _dialect_check_chars(str *name1, str *name2, str *val1, str *val2) { // TODO NOT_SET/None difference?
    if(!val1 || !val2)
        return;

    if(val1->unit[0] == val2->unit[0])
        throw new ValueError(__add_strs(5, new str("bad "), name1, new str(" or "), name2, new str(" value")));
}

Dialect *_make_dialect(
    str *name,
    str *delimiter,
    str *quotechar,
    __ss_int doublequote,
    __ss_int skipinitialspace,
    str *lineterminator,
    __ss_int quoting,
    str *escapechar,
    __ss_int strict
) {
    if(name == NULL)
        name = new str("excel");

    Dialect *from;
    try {
        from = _dialects->__getitem__(name);
    } catch (KeyError *) {
        throw new Error(new str("unknown dialect"));
    }

    Dialect *dialect = new Dialect();

    // TODO virtual dialect.copy() to maintain type eg as reader.dialect..?
    dialect->delimiter = from->delimiter;
    dialect->quotechar = from->quotechar;
    dialect->doublequote = from->doublequote;
    dialect->skipinitialspace = from->skipinitialspace;
    dialect->lineterminator = from->lineterminator;
    dialect->quoting = from->quoting;
    dialect->escapechar = from->escapechar;
    dialect->strict = from->strict;

    if ((delimiter!=NULL)) { // TODO exception when explicitly passing delimiter=None etc.
        if(len(delimiter) > 1)
            throw new TypeError(new str("\"delimiter\" must be a 1-character string"));
        dialect->delimiter = delimiter;
    }
    if ((quotechar!=NULL)) {
        if(len(quotechar) != 1)
            throw new TypeError(new str("\"quotechar\" must be a 1-character string"));
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
        if(quoting > 5)
            throw new TypeError(new str("bad \"quoting\" value"));
        if (quoting == QUOTE_NONNUMERIC)
            throw new ValueError(new str("QUOTE_NONNUMERIC is not supported"));
        dialect->quoting = quoting;
    }
    if ((escapechar!=NULL)) {
        if(len(escapechar) != 1)
            throw new TypeError(new str("\"escapechar\" must be a 1-character string"));
        dialect->escapechar = escapechar;
    }
    if ((strict!=(-1))) {
        dialect->strict = __mbool(strict);
    }

    /*
       TODO
    if (quotechar == Py_None && quoting == NULL)
        self->quoting = QUOTE_NONE;
    if (self->quoting != QUOTE_NONE && self->quotechar == NOT_SET) {
    */

    _dialect_check_char(new str("delimiter"), dialect->delimiter, dialect, true);
    _dialect_check_char(new str("escapechar"), dialect->escapechar, dialect, !dialect->skipinitialspace);
    _dialect_check_char(new str("quotechar"), dialect->quotechar, dialect, !dialect->skipinitialspace);

    _dialect_check_chars(new str("delimiter"), new str("escapechar"), dialect->delimiter, dialect->escapechar);
    _dialect_check_chars(new str("delimiter"), new str("quotechar"), dialect->delimiter, dialect->quotechar);
    _dialect_check_chars(new str("escapechar"), new str("quotechar"), dialect->escapechar, dialect->quotechar);

    return dialect;
}

list<str *> *list_dialects() {
    return new list<str *>(_dialects);
}

Dialect *get_dialect(str *name) {
    return _dialects->__getitem__(name);
}

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
) {
    Dialect *new_dialect = _make_dialect(dialect, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict);
    _dialects->__setitem__(name, new_dialect);
    return NULL;
}

void *unregister_dialect(str *name) {
    _dialects->__delitem__(name);
    return NULL;
}

static inline list<str *> *list_comp_0(DictWriter *self, dict<str *, str *> *rowdict) {
    list<str *> *__ss_result = new list<str *>();
    str *k;
    dict<str *, str *>::for_in_loop __3;
    int __2;
    dict<str *, str *> *__1;
    FOR_IN(k,rowdict,1,2,3)
        if ((!(self->fieldnames)->__contains__(k)))
            __ss_result->append(__add_strs(3, new str("'"), k, new str("'")));
    END_FOR
    return __ss_result;
}

static inline list<str *> *list_comp_1(DictWriter *self, dict<str *, str *> *rowdict) {
    list<str *> *__37;
    list<str *>::for_in_loop __123;
    __ss_int __39;
    str *key;
    list<str *> *__ss_result = new list<str *>();

    __37 = self->fieldnames;
    __ss_result->resize(len(__37));
    FOR_IN(key,__37,37,39,123)
        __ss_result->units[(size_t)__39] = rowdict->get(key, self->restval);
    END_FOR

    return __ss_result;
}

/* reader */

void *reader::__init__(pyiter<str *> *input_iter_, str *dialect_, str *delimiter, str *quotechar, __ss_int doublequote, __ss_int skipinitialspace, str *lineterminator, __ss_int quoting, str *escapechar, __ss_int strict) {
    this->input_iter = input_iter_->__iter__();
    this->line_num = 0;
    this->dialect = _make_dialect(dialect_, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict);
    return NULL;
}

void *reader::parse_process_char(str *s) {
    char c = s->unit[0];

    Dialect *dialect = this->dialect;

    switch (this->state) {
        case START_RECORD:
            /* start of record */
            if (c == EOL)
                /* empty line - return [] */
                break;
            else if (c == '\n' || c == '\r') {
                this->state = EAT_CRNL;
                break;
            }
            /* normal character - handle as START_FIELD */
            this->state = START_FIELD;

        case START_FIELD:
            /* expecting field */
            this->unquoted_field = true;
            if (c == '\n' || c == '\r' || c == EOL) {
                /* save empty field - return [fields] */
                parse_save_field();
                this->state = (c == EOL ? START_RECORD : EAT_CRNL);
            }
            else if (c == dialect->quotechar->unit[0] &&
                     dialect->quoting != QUOTE_NONE) {
                /* start quoted field */
                this->unquoted_field = false;
                this->state = IN_QUOTED_FIELD;
            }
            else if (dialect->escapechar && c == dialect->escapechar->unit[0]) { // TODO check which options can be None..
                /* possible escaped character */
                this->state = ESCAPED_CHAR;
            }
            else if (c == ' ' && dialect->skipinitialspace)
                /* ignore spaces at start of field */
                ;
            else if (c == dialect->delimiter->unit[0]) {
                /* save empty field */
                parse_save_field();
            }
            else {
                /* begin new unquoted field */
                parse_add_char(c);
                this->state = IN_FIELD;
            }
            break;

        case ESCAPED_CHAR:
            if (c == '\n' || c=='\r') {
                parse_add_char(c);
                this->state = AFTER_ESCAPED_CRNL;
                break;
            }
            if (c == EOL)
                c = '\n';
            parse_add_char(c);
            this->state = IN_FIELD;
            break;

        case AFTER_ESCAPED_CRNL:
            if (c == EOL)
                break;

        case IN_FIELD:
            /* in unquoted field */
            if (c == '\n' || c == '\r' || c == EOL) {
                /* end of line - return [fields] */
                parse_save_field();
                this->state = (c == EOL ? START_RECORD : EAT_CRNL);
            }
            else if (dialect->escapechar && c == dialect->escapechar->unit[0]) {
                /* possible escaped character */
                this->state = ESCAPED_CHAR;
            }
            else if (c == dialect->delimiter->unit[0]) {
                /* save field - wait for new field */
                parse_save_field();
                this->state = START_FIELD;
            }
            else {
                /* normal character - save in field */
                parse_add_char(c);
            }
            break;

        case IN_QUOTED_FIELD:
            /* in quoted field */
            if (c == EOL)
                ;
            else if (dialect->escapechar && c == dialect->escapechar->unit[0]) {
                /* Possible escape character */
                this->state = ESCAPE_IN_QUOTED_FIELD;
            }
            else if (c == dialect->quotechar->unit[0] &&
                     dialect->quoting != QUOTE_NONE) {
                if (dialect->doublequote) {
                    /* doublequote; " represented by "" */
                    this->state = QUOTE_IN_QUOTED_FIELD;
                }
                else {
                    /* end of quote part of field */
                    this->state = IN_FIELD;
                }
            }
            else {
                /* normal character - save in field */
                parse_add_char(c);
            }
            break;

        case ESCAPE_IN_QUOTED_FIELD:
            if (c == EOL)
                c = '\n';
            parse_add_char(c);
            this->state = IN_QUOTED_FIELD;
            break;

        case QUOTE_IN_QUOTED_FIELD:
            /* doublequote - seen a quote in a quoted field */
            if (dialect->quoting != QUOTE_NONE &&
                c == dialect->quotechar->unit[0]) {
                /* save "" as " */
                parse_add_char(c);
                this->state = IN_QUOTED_FIELD;
            }
            else if (c == dialect->delimiter->unit[0]) {
                /* save field - wait for new field */
                parse_save_field();
                this->state = START_FIELD;
            }
            else if (c == '\n' || c == '\r' || c == EOL) {
                /* end of line - return [fields] */
                parse_save_field();
                this->state = (c == EOL ? START_RECORD : EAT_CRNL);
            }
            else if (!dialect->strict) {
                parse_add_char(c);
                this->state = IN_FIELD;
            }
            else {
                /* illegal */
                // TODO illegal error
                return NULL;
            }
            break;

        case EAT_CRNL:
            if (c == '\n' || c == '\r')
                ;
            else if (c == EOL)
                this->state = START_RECORD;
            else {
                // TODO error
                return NULL;
            }
            break;
    }

    return NULL;
}

void *reader::parse_reset() {
    this->fields = (new list<str *>());
    this->field = (new list<str *>()); // TODO remove
    this->field_len = 0;
    this->state = START_RECORD;
    this->unquoted_field = false;
    return NULL;
}

list<str *> *reader::__next__() {
    list<str *> *fields_;
    str *line;

    this->parse_reset();

    while (1) {
        line = (this->input_iter)->__next__();
        // TODO unexpected end of data
        this->line_num += 1;
        str *c;
        str::for_in_loop __3;
        int __2;
        str *__1;
        FOR_IN(c,line,1,2,3) // TODO char c
            if (__eq(c, const_7)) {
                throw ((new Error(const_15)));
            }
            this->parse_process_char(c);
        END_FOR

        this->parse_process_char(const_7);

        if (this->state == START_RECORD) {
            break;
        }
    }
    fields_ = this->fields;
    this->fields = (new list<str *>());
    return fields_;
}

void *reader::parse_save_field() {
    __ss_int quoting = this->dialect->quoting;

    str *field_;

    if (this->unquoted_field &&
        this->field_len == 0 &&
        (quoting == QUOTE_NOTNULL || quoting == QUOTE_STRINGS))
    {
        field_ = NULL;
    }
    else {
        field_ = (new str(""))->join(this->field); // TODO take stored to field_len

        this->field = (new list<str *>()); // TODO remove

        if (this->unquoted_field &&
            this->field_len != 0 &&
            (quoting == QUOTE_NONNUMERIC || quoting == QUOTE_STRINGS))
        {
            // TODO raise error
        }

        this->field_len = 0;
    }

    this->fields->append(field_);

    return NULL;
}

void *reader::parse_add_char(char c) {
    if ((len(this->field)>=_field_limit)) { // TODO use field_len
        throw ((new Error(__mod6(const_17, 1, _field_limit))));
    }
    str *s = new str();
    s->unit += c;
    this->field->append(s); // TODO [field_len++] = c;
    this->field_len += 1;
    return NULL;
}

__csviter::__csviter(reader *r_) {
    r = r_;
}

list<str *> *__csviter::__next__() {
    return r->__next__();
}

__csviter *reader::__iter__() {
    return new __csviter(this);
}

/* writer */

void *writer::__init__(file *output_file_, str *dialect_, str *delimiter, str *quotechar, __ss_int doublequote, __ss_int skipinitialspace, str *lineterminator, __ss_int quoting, str *escapechar, __ss_int strict) {
    this->output_file = output_file_;
    this->dialect = _make_dialect(dialect_, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict);
    return NULL;
}

void *writer::join_append_data(str *field, __ss_int quoted) {
    Dialect *dialect = this->dialect;

    /* If this is not the first field we need a field separator */
    if (this->num_fields > 0)
        this->rec->append(dialect->delimiter);

    str *rr = new str(); // TODO

    for (size_t i = 0; i < field->unit.size(); i++) {
        char c = field->unit[i];
        int want_escape = 0;

        if (c == dialect->delimiter->unit[0] ||
            (dialect->escapechar && c == dialect->escapechar->unit[0]) ||
            c == dialect->quotechar->unit[0] ||
            c == '\n' ||
            c == '\r' ||
            dialect->lineterminator->unit.find(c) != std::string::npos) {
            if (dialect->quoting == QUOTE_NONE)
                want_escape = 1;
            else {
                if (c == dialect->quotechar->unit[0]) {
                    if (dialect->doublequote)
                        rr->unit += dialect->quotechar->unit;
                    else
                        want_escape = 1;
                }
                else if (dialect->escapechar && c == dialect->escapechar->unit[0]) {
                    want_escape = 1;
                }
                if (!want_escape)
                    quoted = 1;
            }
            if (want_escape) {
                if (!dialect->escapechar)
                    ; // TODO raise error
                else {
                    rr->unit += dialect->escapechar->unit;
                }
            }
        }

        /* Copy field character into record buffer.
         */
        rr->unit += c;
    }

    if(quoted)
        this->rec->append(dialect->quotechar);
    this->rec->append(rr);
    if(quoted)
        this->rec->append(dialect->quotechar);

    return NULL;
}

void *writer::writerow(list<str *> *seq) {
    list<str *> *__24;
    list<str *>::for_in_loop __123;
    __ss_int __26, quoted;
    str *field;

    this->join_reset();

    FOR_IN(field,seq,24,26,123)
        if (dialect->quoting == QUOTE_ALL)
            quoted = 1;
        else if (dialect->quoting == QUOTE_NOTNULL)
            quoted = field ? 1 : 0;
        else
            quoted = 0;

        if (field == NULL) {
            this->join_append(NULL, quoted);
        }
        else {
            this->join_append(field, quoted);
        }
    END_FOR

    if (this->num_fields > 0 && len(this->rec) == 0) {
        // TODO check error

        this->num_fields -= 1;
        this->join_append(NULL, 1);
    }

    (this->rec)->append((this->dialect)->lineterminator);
    (this->output_file)->write((const_16)->join(this->rec));
    return NULL;
}

void *writer::join_reset() {
    this->rec = (new list<str *>());
    this->num_fields = 0;
    return NULL;
}

void *writer::writerows(pyiter<list<str *> *> *seqs) {
    list<str *> *seq;

    pyiter<list<str *> *> *__0;
    __ss_int __2;
    pyiter<list<str *> *>::for_in_loop __3;

    FOR_IN(seq,seqs,0,2,3)
        this->writerow(seq);
    END_FOR

    return NULL;
}

void *writer::join_append(str *field, __ss_int quoted) {
    Dialect *dialect = this->dialect;
    size_t field_len = field->unit.size();

    if (!field_len && dialect->delimiter->unit[0] == ' ' && dialect->skipinitialspace) {
        // TODO empty field check?

        quoted = 1;
    }

    this->join_append_data(field, quoted);
    this->num_fields += 1;

    return NULL;
}

/* DictReader */

void *DictReader::__init__(pyiter<str *> *f, pyiter<str *> *fieldnames_, str *restkey, str *restval_, str *dialect_, str *delimiter, str *quotechar, __ss_int doublequote, __ss_int skipinitialspace, str *lineterminator, __ss_int quoting, str *escapechar, __ss_int strict) {
    if(fieldnames_)
        this->_fieldnames = new list<str *>(fieldnames_);
    else
        this->_fieldnames = NULL;
    if(restkey)
        throw new ValueError(new str("DictReader(restkey) argument is not supported"));
    this->restval = restval_;
    this->_reader = (new reader(f, dialect_, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict));
    this->dialect = dialect_;
    this->line_num = 0;
    return NULL;
}

void *DictReader::setfieldnames(list<str *> *value) {
    this->_fieldnames = value;
    return NULL;
}

dict<str *, str *> *DictReader::__next__() {
    str *key;
    list<str *> *__31, *row;
    list<str *>::for_in_loop __123;
    __ss_int __33, lf, lr;
    dict<str *, str *> *d;

    if (this->line_num == 0) {
        this->getfieldnames();
    }
    row = (this->_reader)->__next__();
    this->line_num = (this->_reader)->line_num;

    while (row->empty()) {
        row = (this->_reader)->__next__();
    }
    d = new dict<str *, str *>(__zip(2, False, this->getfieldnames(), row));
    lf = len(this->getfieldnames());
    lr = len(row);
    if ((lf<lr)) {
        throw ((new Error(const_20)));
    }
    else if ((lf>lr)) {

        FOR_IN(key,(this->getfieldnames())->__slice__(1, lr, 0, 0),31,33,123)
            d->__setitem__(key, this->restval);
        END_FOR

    }
    return d;
}

list<str *> *DictReader::getfieldnames() {
    if (this->_fieldnames == NULL) {
        try {
            this->_fieldnames = (this->_reader)->__next__();
        } catch (StopIteration *) {
        }
    }
    this->line_num = (this->_reader)->line_num;
    return this->_fieldnames;
}

__driter::__driter(DictReader *r_) {
    r = r_;
}

dict<str *, str *> *__driter::__next__() {
    return r->__next__();
}

__driter *DictReader::__iter__() {
    return new __driter(this);
}

/* DictWriter */

void *DictWriter::__init__(file *f, pyiter<str *> *fieldnames_, str *restval_, str *extrasaction_, str *dialect_, str *delimiter, str *quotechar, __ss_int doublequote, __ss_int skipinitialspace, str *lineterminator, __ss_int quoting, str *escapechar, __ss_int strict) {
    if(!restval_)
        restval_ = new str();
    if(!extrasaction_)
        extrasaction_ = new str("raise");
    if(!dialect_)
        dialect_ = new str("excel");
    if(fieldnames_)
        this->fieldnames = new list<str *>(fieldnames_);
    else
        this->fieldnames = NULL;
    this->restval = restval_;
    if ((!(const_3)->__contains__(extrasaction_->lower()))) {
        throw ((new ValueError(__mod6(const_23, 1, extrasaction_))));
    }
    this->extrasaction = extrasaction_;
    this->_writer = (new writer(f, dialect_, delimiter, quotechar, doublequote, skipinitialspace, lineterminator, quoting, escapechar, strict));
    return NULL;
}

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

void *DictWriter::writeheader() {
    this->_writer->writerow(this->fieldnames);
    return NULL;
}

void *DictWriter::writerow(dict<str *, str *> *rowdict) {
    return (this->_writer)->writerow(this->_dict_to_list(rowdict));
}

void *DictWriter::writerows(pyiter<dict<str *, str *> *> *rowdicts) {
    list<list<str *> *> *rows;

    pyiter<dict<str *, str *> *> *__40;
    pyiter<dict<str *, str *> *>::for_in_loop __123;
    __ss_int __42;

    dict<str *, str *> *rowdict;
    FOR_IN(rowdict,rowdicts,40,42,123)
        (this->_writer)->writerow(this->_dict_to_list(rowdict));
    END_FOR

    return NULL;
}

/* field_size_limit */

__ss_int field_size_limit(__ss_int new_limit) {
    __ss_int old_limit;

    old_limit = _field_limit;
    if ((new_limit!=(-1))) {
        _field_limit = new_limit;
    }
    return old_limit;
}

void __init() {
    const_1 = new str("raise");
    const_2 = new str("ignore");
    const_3 = (new tuple2<str *, str *>(2, const_1, const_2));
    const_4 = new str(",");
    const_5 = new str("\"");
    const_6 = new str("\r\n");
    const_7 = new str("\000", 1);
    const_8 = new str("\n\r");
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
    const_25 = new str("excel-tab");

    __name__ = new str("csv");

    _dialects = new dict<str *, Dialect *>();
    _dialects->__setitem__(new str("unix"), new unix_dialect());
    _dialects->__setitem__(new str("excel"), new excel());
    _dialects->__setitem__(new str("excel-tab"), new excel_tab());

    cl_writer = new class_("writer");
    cl_DictReader = new class_("DictReader");
    cl_Dialect = new class_("Dialect");
    cl_Excel = new class_("excel");
    cl_ExcelTab = new class_("excel_tab");
    cl_UnixDialect = new class_("unix_dialect");
    cl_reader = new class_("reader");
    cl_Error = new class_("Error");
    cl_DictWriter = new class_("DictWriter");

    _field_limit = 128*1024;
}

} // module namespace

