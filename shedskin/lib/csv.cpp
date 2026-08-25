/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "csv.hpp"
#include <vector>
#include <map>
#include <string>
#include <algorithm>
#include <utility>

namespace __csv__ {

str *__name__;

dict<str *, Dialect *> *_dialects;

tuple2<str *, str *> *const_3;

str *const_1, *const_16, *const_17, *const_2, *const_21, *const_22, *const_23, *const_7;

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
class_ *cl_Sniffer;

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
                throw new Error(__add_strs(5, new str("'"), dialect->delimiter, new str("' expected after '"), dialect->quotechar, new str("'")));
            }
            break;

        case EAT_CRNL:
            if (c == '\n' || c == '\r')
                ;
            else if (c == EOL)
                this->state = START_RECORD;
            else {
                throw new Error(new str("new-line character seen in unquoted field - do you need to open the file with newline=''?"));
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
        try {
            line = (this->input_iter)->__next__();
        } catch (StopIteration *) {
            /* underlying iterator exhausted mid-row (e.g. an unterminated
               quoted field on the last line); if we have no partial data,
               this is a genuine end of iteration, otherwise flush what we
               have, matching CPython's behavior of returning the row
               collected so far rather than silently dropping it. */
            if (this->state == START_RECORD && this->fields->__len__() == 0 && this->field_len == 0) {
                throw;
            }
            this->parse_save_field();
            break;
        }
        this->line_num += 1;
        str *c;
        str::for_in_loop __3;
        int __2;
        str *__1;
        FOR_IN(c,line,1,2,3) // TODO char c
            if (__eq(c, const_7)) {
                throw new Error(new str("line contains NULL byte"));
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
    if (this->num_fields > 0) {
        this->rec->append(dialect->delimiter);
        this->rec_len += dialect->delimiter->unit.size();
    }

    str *rr = new str(); // TODO

    for (size_t i = 0; field != NULL && i < field->unit.size(); i++) {
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
                    throw new Error(new str("need to escape, but no escapechar set"));
                else {
                    rr->unit += dialect->escapechar->unit;
                }
            }
        }

        /* Copy field character into record buffer.
         */
        rr->unit += c;
    }

    if(quoted) {
        this->rec->append(dialect->quotechar);
        this->rec_len += dialect->quotechar->unit.size();
    }
    this->rec->append(rr);
    this->rec_len += rr->unit.size();
    if(quoted) {
        this->rec->append(dialect->quotechar);
        this->rec_len += dialect->quotechar->unit.size();
    }

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
        else if (dialect->quoting == QUOTE_NOTNULL || dialect->quoting == QUOTE_STRINGS)
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

    if (this->num_fields > 0 && this->rec_len == 0) {
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
    this->rec_len = 0;
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
    size_t field_len = field ? field->unit.size() : 0;

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
        throw new Error(new str("DictReader 'restkey' is not supported"));
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

/* Sniffer */

/* small helper: a Counter-like structure that remembers first-insertion
   order for its keys, so that tie-breaking in max(..., key=...) matches
   CPython's dict-iteration-order semantics exactly. */
struct __ordered_int_counter {
    std::vector<int> order;
    std::map<int, int> counts;

    void add(int key, int amount = 1) {
        if (counts.find(key) == counts.end()) {
            order.push_back(key);
            counts[key] = amount;
        }
        else {
            counts[key] += amount;
        }
    }
};

/* count non-overlapping occurrences of `needle` in `hay`, matching
   str.count() semantics (used for the skipinitialspace heuristic:
   count(delim) vs count("%c " % delim)). */
static __ss_int __count_substr(const std::string &hay, const std::string &needle) {
    if (needle.empty()) return (__ss_int)(hay.size() + 1);
    __ss_int n = 0;
    size_t pos = 0;
    while ((pos = hay.find(needle, pos)) != std::string::npos) {
        n++;
        pos += needle.size();
    }
    return n;
}

struct __qd_result {
    std::string quotechar;   // '' if none found
    bool doublequote;
    std::string delimiter;   // '' if none found (single-column data)
    __ss_int skipinitialspace;
};

/* Sniffer::_guess_quote_and_delimiter, ported from CPython's Lib/csv.py.
   Looks for text enclosed between two identical quotes which are preceded
   and followed by the same character (the probable delimiter). */
static __qd_result __guess_quote_and_delimiter(str *data, str *delimiters) {
    static const char *patterns[4] = {
        "(?P<delim>[^\\w\\n\"'])(?P<space> ?)(?P<quote>[\"']).*?(?P=quote)(?P=delim)",
        "(?:^|\\n)(?P<quote>[\"']).*?(?P=quote)(?P<delim>[^\\w\\n\"'])(?P<space> ?)",
        "(?P<delim>[^\\w\\n\"'])(?P<space> ?)(?P<quote>[\"']).*?(?P=quote)(?:$|\\n)",
        "(?:^|\\n)(?P<quote>[\"']).*?(?P=quote)(?:$|\\n)"
    };

    __re__::re_object *regexp = NULL;
    std::vector<__re__::match_object *> matches;

    __qd_result result;
    result.doublequote = false;
    result.skipinitialspace = 0;

    if (data->unit.size() == 0) {
        return result; // finditer() rejects an empty subject; nothing to find anyway
    }

    for (int p = 0; p < 4; p++) {
        regexp = __re__::compile(new str(patterns[p]), __re__::DOTALL | __re__::MULTILINE);
        matches.clear();
        __iter<__re__::match_object *> *it = regexp->finditer(data);
        while (1) {
            try {
                matches.push_back(it->__next__());
            } catch (StopIteration *) {
                break;
            }
        }
        if (!matches.empty()) break;
    }

    __qd_result result2;
    result2.doublequote = false;
    result2.skipinitialspace = 0;

    if (matches.empty() || regexp == NULL) {
        return result2; // no matches -> quotechar='', delimiter=None-ish
    }

    bool has_delim_group = regexp->groupindex->has_key(new str("delim"));

    std::vector<char> quote_order, delim_order;
    std::map<char, int> quote_counts, delim_counts;
    int spaces = 0;

    for (size_t i = 0; i < matches.size(); i++) {
        __re__::match_object *m = matches[i];

        str *qstr = m->group(0, new str("quote"));
        if (qstr != NULL && qstr->unit.size() > 0) {
            char key = qstr->unit[0];
            if (quote_counts.find(key) == quote_counts.end()) {
                quote_order.push_back(key);
                quote_counts[key] = 1;
            }
            else quote_counts[key]++;
        }

        if (!has_delim_group) continue;

        str *dstr = m->group(0, new str("delim"));
        if (dstr != NULL && dstr->unit.size() > 0) {
            char key = dstr->unit[0];
            if (delimiters == NULL || delimiters->unit.find(key) != __GC_STRING::npos) {
                if (delim_counts.find(key) == delim_counts.end()) {
                    delim_order.push_back(key);
                    delim_counts[key] = 1;
                }
                else delim_counts[key]++;
            }
        }

        str *sstr = m->group(0, new str("space"));
        if (sstr != NULL && sstr->unit.size() > 0) spaces++;
    }

    // quotechar = max(quotes, key=quotes.get)  (first-seen wins ties)
    char quotechar = 0;
    int best = -1;
    for (size_t i = 0; i < quote_order.size(); i++) {
        char c = quote_order[i];
        if (quote_counts[c] > best) {
            best = quote_counts[c];
            quotechar = c;
        }
    }
    if (best >= 0) result.quotechar = std::string(1, quotechar);

    std::string delim;
    if (!delim_order.empty()) {
        char delimchar = 0;
        int dbest = -1;
        for (size_t i = 0; i < delim_order.size(); i++) {
            char c = delim_order[i];
            if (delim_counts[c] > dbest) {
                dbest = delim_counts[c];
                delimchar = c;
            }
        }
        result.skipinitialspace = (dbest == spaces) ? 1 : 0;
        if (delimchar == '\n') delim = ""; // most likely a single-column file
        else delim = std::string(1, delimchar);
    }
    else {
        delim = "";
        result.skipinitialspace = 0;
    }
    result.delimiter = delim;

    if (best < 0) {
        // no quotechar found at all -> we're done, no doublequote check possible
        return result;
    }

    // check for an extra quote between delimiters -> doubled-quote format
    std::string escaped_delim(delim.empty() ? "" :
        std::string(__re__::escape(new str(delim.c_str(), delim.size()))->unit.c_str()));
    std::string qc(1, quotechar);
    std::string dq_pattern =
        "((" + escaped_delim + ")|^)\\W*" + qc + "[^" + escaped_delim + "\\n]*" +
        qc + "[^" + escaped_delim + "\\n]*" + qc + "\\W*((" + escaped_delim + ")|$)";

    __re__::re_object *dq_regexp = __re__::compile(
        new str(dq_pattern.c_str(), dq_pattern.size()), __re__::MULTILINE);
    __re__::match_object *dqm = dq_regexp->search(data);
    result.doublequote = (dqm != NULL);

    return result;
}

/* Sniffer::_guess_delimiter, ported from CPython's Lib/csv.py.
   Builds a per-character frequency table across lines and picks the
   character whose per-line occurrence count is most consistent. */
static void __guess_delimiter(str *data_str, str *delimiters, std::string &out_delim, __ss_int &out_skip) {
    std::vector<std::string> data;
    {
        list<str *> *lines = data_str->split(new str("\n"));
        for (__ss_int i = 0; i < lines->__len__(); i++) {
            str *line = lines->__getitem__(i);
            if (line->unit.size() > 0) data.push_back(std::string(line->unit.c_str(), line->unit.size()));
        }
    }

    if (data.empty()) {
        out_delim = "";
        out_skip = 0;
        return;
    }

    size_t chunkLength = std::min((size_t)10, data.size());
    __ss_int iteration = 0;
    __ss_int num_lines = 0;

    std::map<char, __ordered_int_counter> char_frequency;
    std::map<char, std::pair<int,int> > modes;      // char -> (count_key, adjusted_freq)
    std::map<char, std::pair<int,int> > delims;     // char -> (count_key, adjusted_freq)

    size_t start = 0, end = chunkLength;

    while (start < data.size()) {
        iteration++;

        for (size_t li = start; li < end && li < data.size(); li++) {
            num_lines++;
            const std::string &line = data[li];

            // per-line char -> count histogram (ascii chars only)
            std::map<char, int> line_counts;
            for (size_t ci = 0; ci < line.size(); ci++) {
                unsigned char c = (unsigned char)line[ci];
                if (c < 128) line_counts[(char)c]++;
            }
            for (std::map<char,int>::iterator it = line_counts.begin(); it != line_counts.end(); ++it) {
                char_frequency[it->first].add(it->second, 1);
            }
        }

        for (std::map<char, __ordered_int_counter>::iterator it = char_frequency.begin(); it != char_frequency.end(); ++it) {
            char ch = it->first;
            __ordered_int_counter &counts = it->second;

            int total_seen = 0;
            for (size_t i = 0; i < counts.order.size(); i++) total_seen += counts.counts[counts.order[i]];
            int missed_lines = num_lines - total_seen;

            // effective items = real (key,count) pairs, plus a synthetic
            // (0, missed_lines) entry appended last if nonzero
            std::vector<int> item_keys = counts.order;
            std::vector<int> item_vals;
            for (size_t i = 0; i < counts.order.size(); i++) item_vals.push_back(counts.counts[counts.order[i]]);
            if (missed_lines != 0) {
                item_keys.push_back(0);
                item_vals.push_back(missed_lines);
            }

            if (item_keys.size() == 1 && item_keys[0] == 0) continue; // useless: char never appears

            if (item_keys.size() > 1) {
                // mode = max(items, key=lambda x: x[1]), first-seen wins ties
                size_t best_idx = 0;
                int best_val = -1;
                for (size_t i = 0; i < item_keys.size(); i++) {
                    if (item_vals[i] > best_val) {
                        best_val = item_vals[i];
                        best_idx = i;
                    }
                }
                int sum_others = 0;
                for (size_t i = 0; i < item_keys.size(); i++) {
                    if (i != best_idx) sum_others += item_vals[i];
                }
                modes[ch] = std::make_pair(item_keys[best_idx], item_vals[best_idx] - sum_others);
            }
            else {
                modes[ch] = std::make_pair(item_keys[0], item_vals[0]);
            }
        }

        double total = (double)std::min(chunkLength * (size_t)iteration, data.size());
        double consistency = 1.0;
        const double threshold = 0.9;

        delims.clear();
        while (delims.empty() && consistency >= threshold) {
            for (std::map<char, std::pair<int,int> >::iterator it = modes.begin(); it != modes.end(); ++it) {
                char ch = it->first;
                int key = it->second.first;
                int val = it->second.second;
                if (key > 0 && val > 0) {
                    if (((double)val / total) >= consistency &&
                        (delimiters == NULL || delimiters->unit.find(ch) != __GC_STRING::npos)) {
                        delims[ch] = it->second;
                    }
                }
            }
            consistency -= 0.01;
        }

        if (delims.size() == 1) {
            char delim = delims.begin()->first;
            std::string delim_s(1, delim);
            std::string pat = delim_s + " ";
            out_skip = (__count_substr(data[0], delim_s) == __count_substr(data[0], pat)) ? 1 : 0;
            out_delim = delim_s;
            return;
        }

        start = end;
        end += chunkLength;
    }

    if (delims.empty()) {
        out_delim = "";
        out_skip = 0;
        return;
    }

    if (delims.size() > 1) {
        // fall back to the 'preferred' list
        static const char *preferred[5] = {",", "\t", ";", " ", ":"};
        for (int p = 0; p < 5; p++) {
            char d = preferred[p][0];
            if (delims.find(d) != delims.end()) {
                std::string delim_s(1, d);
                std::string pat = delim_s + " ";
                out_skip = (__count_substr(data[0], delim_s) == __count_substr(data[0], pat)) ? 1 : 0;
                out_delim = delim_s;
                return;
            }
        }
    }

    // nothing else indicates a preference: pick greatest (value, char) pair
    // (Python: items = [(v,k) for (k,v) in delims.items()]; items.sort(); items[-1][1])
    char best_char = 0;
    std::pair<int,int> best_val = std::make_pair(-1, -1);
    bool have_best = false;
    for (std::map<char, std::pair<int,int> >::iterator it = delims.begin(); it != delims.end(); ++it) {
        std::pair<int,int> v = it->second;
        char k = it->first;
        if (!have_best || v > best_val || (v == best_val && k > best_char)) {
            best_val = v;
            best_char = k;
            have_best = true;
        }
    }
    std::string delim_s(1, best_char);
    std::string pat = delim_s + " ";
    out_skip = (__count_substr(data[0], delim_s) == __count_substr(data[0], pat)) ? 1 : 0;
    out_delim = delim_s;
}

/* helper for has_header(): does this field parse the way CPython's
   complex(x) would accept it? (int/float/complex literal, whitespace ok) */
static bool __is_complex_parseable(str *s) {
    try {
        __shedskin__::mcomplex(s);
        return true;
    } catch (ValueError *) {
        return false;
    }
}

void *Sniffer::__init__() {
    return NULL;
}

Dialect *Sniffer::sniff(str *sample, str *delimiters) {
    __qd_result qd = __guess_quote_and_delimiter(sample, delimiters);

    std::string delimiter = qd.delimiter;
    __ss_int skipinitialspace = qd.skipinitialspace;

    if (delimiter.empty()) {
        __guess_delimiter(sample, delimiters, delimiter, skipinitialspace);
    }
    if (delimiter.empty()) {
        throw new Error(new str("Could not determine delimiter"));
    }

    Dialect *dialect = new Dialect();
    dialect->lineterminator = new str("\r\n");
    dialect->quoting = QUOTE_MINIMAL;
    dialect->doublequote = qd.doublequote ? 1 : 0;
    dialect->delimiter = new str(delimiter.c_str(), delimiter.size());
    dialect->quotechar = qd.quotechar.empty() ? new str("\"") : new str(qd.quotechar.c_str(), qd.quotechar.size());
    dialect->skipinitialspace = skipinitialspace;
    dialect->escapechar = NULL;
    dialect->strict = False;

    return dialect;
}

__ss_bool Sniffer::has_header(str *sample) {
    Dialect *dialect = sniff(sample);

    list<str *> *sample_lines = sample->split(new str("\n"));
    // pass the sniffed dialect as explicit overrides on top of "excel", since
    // reader's constructor only resolves a *named*, registered dialect and
    // otherwise silently falls back to excel defaults (see the `D dialect_`
    // template dispatch above) -- an ad-hoc Dialect object isn't threaded
    // through directly.
    reader *rdr = new reader(
        sample_lines, new str("excel"),
        dialect->delimiter, dialect->quotechar,
        dialect->doublequote, dialect->skipinitialspace,
        NULL, -1, NULL, -1
    );

    list<str *> *header = rdr->__next__();
    __ss_int columns = header->__len__();

    // tag: 0 = unset, 1 = numeric ("complex"-parseable), 2 = fixed string
    // length, -1 = disqualified/inconsistent
    std::vector<int> col_kind(columns, 0);
    std::vector<int> col_length(columns, 0);

    int checked = 0;
    while (1) {
        list<str *> *row;
        try {
            row = rdr->__next__();
        } catch (StopIteration *) {
            break;
        }
        if (checked > 20) break;
        checked++;

        if (row->__len__() != columns) continue;

        for (__ss_int col = 0; col < columns; col++) {
            if (col_kind[col] == -1) continue;

            str *field = row->__getitem__(col);
            int this_kind, this_length;
            if (__is_complex_parseable(field)) {
                this_kind = 1;
                this_length = 0;
            }
            else {
                this_kind = 2;
                this_length = (int)field->unit.size();
            }

            if (col_kind[col] == 0) {
                col_kind[col] = this_kind;
                col_length[col] = this_length;
            }
            else if (this_kind != col_kind[col] || this_length != col_length[col]) {
                col_kind[col] = -1;
            }
        }
    }

    __ss_int hasHeader = 0;
    for (__ss_int col = 0; col < columns; col++) {
        int kind = col_kind[col];
        if (kind == -1 || kind == 0) continue;

        str *field = header->__getitem__(col);
        if (kind == 2) {
            if ((__ss_int)field->unit.size() != col_length[col]) hasHeader++;
            else hasHeader--;
        }
        else { // kind == 1, numeric column: does the header value ALSO parse as a number?
            if (__is_complex_parseable(field)) hasHeader--;
            else hasHeader++;
        }
    }

    return ___bool(hasHeader > 0);
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
    __name__ = new str("csv");

    const_1 = new str("raise");
    const_2 = new str("ignore");
    const_3 = (new tuple2<str *, str *>(2, const_1, const_2));
    const_7 = new str("\000", 1);
    const_16 = new str("");
    const_17 = new str("field larger than field limit (%d)");
    const_21 = new str("dict contains fields not in fieldnames: ");
    const_22 = new str(", ");
    const_23 = new str("extrasaction (%s) must be 'raise' or 'ignore'");

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
    cl_Sniffer = new class_("Sniffer");

    _field_limit = 128*1024;
}

} // module namespace

