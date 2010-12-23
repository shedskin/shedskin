#include "ConfigParser.hpp"

/**
Configuration file parser.

A setup file consists of sections, lead by a "[section]" header,
and followed by "name: value" entries, with continuations and such in
the style of RFC 822.

The option values can contain format strings which refer to other values in
the same section, or values in a special [DEFAULT] section.

For example:

    something: %(dir)s/whatever

would resolve the "%(dir)s" to the value of dir.  All reference
expansions are done late, on demand.

Intrinsic defaults can be specified by passing them into the
ConfigParser constructor as a dictionary.

class:

ConfigParser -- responsible for parsing a list of
                configuration files, and managing the parsed database.

    methods:

    __init__(defaults=None)
        create the parser and specify a dictionary of intrinsic defaults.  The
        keys must be strings, the values must be appropriate for %()s string
        interpolation.  Note that `__name__' is always an intrinsic default;
        its value is the section's name.

    sections()
        return all the configuration section names, sans DEFAULT

    has_section(section)
        return whether the given section exists

    has_option(section, option)
        return whether the given option exists in the given section

    options(section)
        return list of configuration options for the named section

    read(filenames)
        read and parse the list of named configuration files, given by
        name.  A single filename is also allowed.  Non-existing files
        are ignored.  Return list of successfully read files.

    readfp(fp, filename=None)
        read and parse one configuration file, given as a file object.
        The filename defaults to fp.name; it is only used in error
        messages (if fp has no `name' attribute, the string `<???>' is used).

    get(section, option, raw=False, vars=None)
        return a string value for the named option.  All % interpolations are
        expanded in the return values, based on the defaults passed into the
        constructor and the DEFAULT section.  Additional substitutions may be
        provided using the `vars' argument, which must be a dictionary whose
        contents override any pre-existing defaults.

    getint(section, options)
        like get(), but convert value to an integer

    getfloat(section, options)
        like get(), but convert value to a float

    getboolean(section, options)
        like get(), but convert value to a boolean (currently case
        insensitively defined as 0, false, no, off for False, and 1, true,
        yes, on for True).  Returns False or True.

    items(section, raw=False, vars=None)
        return a list of tuples with (name, value) for each option
        in the section.

    remove_section(section)
        remove the given file section and all its options

    remove_option(section, option)
        remove the given option from the given section

    set(section, option, value)
        set the given option

    write(fp)
        write the configuration state in .ini format
*/

namespace __ConfigParser__ {

tuple2<str *, str *> *const_2;
str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_26, *const_27, *const_28, *const_29, *const_3, *const_30, *const_31, *const_32, *const_33, *const_34, *const_35, *const_36, *const_37, *const_38, *const_39, *const_4, *const_40, *const_41, *const_42, *const_43, *const_44, *const_45, *const_46, *const_47, *const_48, *const_49, *const_5, *const_50, *const_51, *const_52, *const_53, *const_6, *const_7, *const_8, *const_9;

list<str *> *__all__;
str *DEFAULTSECT, *__name__;
__ss_int MAX_INTERPOLATION_DEPTH;

str * default_11;
__ss_int  default_10;
__ss_int  default_13;
__ss_int  default_23;
__ss_int  default_2;
__ss_int  default_25;
__ss_int  default_28;
__ss_int  default_1;
__ss_int  default_5;
__ss_int  default_3;
__ss_int  default_19;
__ss_int  default_29;
__ss_int  default_12;
str * default_22;
__ss_int  default_31;
__ss_int  default_30;
str * default_9;
__ss_int  default_8;
str * default_24;
str * default_14;
str * default_16;
str * default_26;
__ss_int  default_17;
str * default_18;
__ss_int  default_6;
__ss_int  default_15;
__ss_int  default_27;
str * default_20;
__ss_int  default_7;
__ss_int  default_4;
str * default_0;
__ss_int  default_21;

static inline list<tuple2<str *, str *> *> *list_comp_0(list<str *> *options, dict<str *, str *> *d) {
    list<str *> *__56;
    __iter<str *> *__57;
    str *option;
    __ss_int __58;
    list<tuple2<str *, str *> *> *result = new list<tuple2<str *, str *> *>();

    result->resize(len(options));
    FOR_IN_SEQ(option,options,56,58)
        result->units[__58] = (new tuple2<str *, str *>(2, option, d->__getitem__(option)));
    END_FOR

    return result;
}

static inline list<tuple2<str *, str *> *> *list_comp_1(dict<str *, str *> *d, ConfigParser *self, list<str *> *options, str *section) {
    list<str *> *__59;
    __iter<str *> *__60;
    str *option;
    __ss_int __61;
    list<tuple2<str *, str *> *> *result = new list<tuple2<str *, str *> *>();

    result->resize(len(options));
    FOR_IN_SEQ(option,options,59,61)
        result->units[__61] = (new tuple2<str *, str *>(2, option, self->_interpolate(section, option, d->__getitem__(option), d)));
    END_FOR

    return result;
}

/**
class Error
*/

class_ *cl_Error;

void *Error::__init__(str *msg) {

    this->message = msg;
    Exception::__init__(msg);
    return NULL;
}


/**
class NoSectionError
*/

class_ *cl_NoSectionError;

void *NoSectionError::__init__(str *section) {

    Error::__init__(__modct(const_3, 1, section));
    this->section = section;
    return NULL;
}

/**
class DuplicateSectionError
*/

class_ *cl_DuplicateSectionError;

void *DuplicateSectionError::__init__(str *section) {

    Error::__init__(__modct(const_4, 1, section));
    this->section = section;
    return NULL;
}

/**
class NoOptionError
*/

class_ *cl_NoOptionError;

void *NoOptionError::__init__(str *option, str *section) {

    Error::__init__(__modct(const_5, 2, option, section));
    this->option = option;
    this->section = section;
    return NULL;
}

/**
class InterpolationError
*/

class_ *cl_InterpolationError;

void *InterpolationError::__init__(str *option, str *section, str *msg) {

    Error::__init__(msg);
    this->option = option;
    this->section = section;
    return NULL;
}


/**
class InterpolationMissingOptionError
*/

class_ *cl_InterpolationMissingOptionError;

void *InterpolationMissingOptionError::__init__(str *option, str *section, str *rawval, str *reference) {
    str *msg;

    msg = __modct(const_6, 4, section, option, reference, rawval);
    InterpolationError::__init__(option, section, msg);
    this->reference = reference;
    return NULL;
}

/**
class InterpolationSyntaxError
*/

class_ *cl_InterpolationSyntaxError;

/**
class InterpolationDepthError
*/

class_ *cl_InterpolationDepthError;

void *InterpolationDepthError::__init__(str *option, str *section, str *rawval) {
    str *msg;

    msg = __modct(const_7, 3, section, option, rawval);
    InterpolationError::__init__(option, section, msg);
    return NULL;
}

/**
class ParsingError
*/

class_ *cl_ParsingError;

void *ParsingError::__init__(str *filename) {

    Error::__init__(__modct(const_8, 1, filename));
    this->filename = filename;
    this->errors = (new list<tuple2<__ss_int, str *> *>());
    return NULL;
}

void *ParsingError::append(__ss_int lineno, str *line) {

    (this->errors)->append((new tuple2<__ss_int, str *>(2, lineno, line)));
    this->message = (this->message)->__iadd__(__modct(const_9, 2, ___box(lineno), line));
    return NULL;
}

/**
class MissingSectionHeaderError
*/

class_ *cl_MissingSectionHeaderError;

void *MissingSectionHeaderError::__init__(str *filename, __ss_int lineno, str *line) {

    Error::__init__(__modct(const_10, 3, filename, ___box(lineno), line));
    this->filename = filename;
    this->lineno = lineno;
    this->line = line;
    return NULL;
}

/**
class RawConfigParser
*/

class_ *cl_RawConfigParser;

str *RawConfigParser::optionxform(str *optionstr) {

    return optionstr->lower();
}

double RawConfigParser::getfloat(str *section, str *option) {

    return __float(this->get(section, option, default_5, NULL));
}

void *RawConfigParser::_set(str *section, str *option, str *value) {
    /**
    Set an option.
    */
    __ss_int __16, __17;
    dict<str *, str *> *sectdict;

    if (__OR((!___bool(section)), __eq(section, DEFAULTSECT), 16)) {
        sectdict = this->_defaults;
    }
    else {
        try {
            sectdict = (this->_sections)->__getitem__(section);
        } catch (KeyError *) {
            throw ((new NoSectionError(section)));
        }
    }
    sectdict->__setitem__(this->optionxform(option), value);
    return NULL;
}

__ss_bool RawConfigParser::has_section(str *section) {
    /**
    Indicate whether the named section is present in the configuration.

    The DEFAULT section is not acknowledged.
    */

    return __mbool((this->_sections)->__contains__(section));
}

__ss_bool RawConfigParser::remove_option(str *section, str *option) {
    /**
    Remove an option.
    */
    __ss_int __30, __31;
    __ss_bool existed;
    dict<str *, str *> *sectdict;

    if (__OR((!___bool(section)), __eq(section, DEFAULTSECT), 30)) {
        sectdict = this->_defaults;
    }
    else {
        try {
            sectdict = (this->_sections)->__getitem__(section);
        } catch (KeyError *) {
            throw ((new NoSectionError(section)));
        }
    }
    option = this->optionxform(option);
    existed = sectdict->__contains__(option);
    if (existed) {
        sectdict->__delitem__(option);
    }
    return existed;
}

__ss_bool RawConfigParser::remove_section(str *section) {
    /**
    Remove a file section.
    */
    __ss_bool existed;

    existed = (this->_sections)->__contains__(section);
    if (existed) {
        (this->_sections)->__delitem__(section);
    }
    return existed;
}

void *RawConfigParser::__init__(dict<str *, str *> *defaults) {
    __ss_int __3;
    tuple2<str *, str *> *__0;
    str *key, *value;
    list<tuple2<str *, str *> *> *__1;
    dict<str *, str *> *__4;
    __iter<tuple2<str *, str *> *> *__2;

    this->_sections = (new dict<str *, dict<str *, str *> *>());
    this->_defaults = (new dict<str *, str *>());
    if (___bool(defaults)) {

        FOR_IN_SEQ(__0,defaults->items(),1,3)
            __0 = __0;
            key = __0->__getfirst__();
            value = __0->__getsecond__();
            this->_defaults->__setitem__(this->optionxform(key), value);
        END_FOR

    }
    return NULL;
}

__ss_bool RawConfigParser::has_option(str *section, str *option) {
    /**
    Check for the existence of a given option in a given section.
    */
    __ss_int __12, __13, __15;
    __ss_bool __14;

    if (__OR((!___bool(section)), __eq(section, DEFAULTSECT), 12)) {
        option = this->optionxform(option);
        return (this->_defaults)->__contains__(option);
    }
    else if ((!(this->_sections)->__contains__(section))) {
        return False;
    }
    else {
        option = this->optionxform(option);
        return __OR(((this->_sections)->__getitem__(section))->__contains__(option), (this->_defaults)->__contains__(option), 14);
    }
    return False;
}

void *RawConfigParser::write(file *fp) {
    /**
    Write an .ini-format representation of the configuration state.
    */
    __ss_int __22, __25, __29;
    dict<str *, dict<str *, str *> *> *__23;
    str *key, *section, *value;
    tuple2<str *, str *> *__19, *__26;
    __iter<str *> *__24;
    list<tuple2<str *, str *> *> *__20, *__27;
    __iter<tuple2<str *, str *> *> *__21, *__28;

    if (___bool(this->_defaults)) {
        fp->write(__modct(const_11, 1, DEFAULTSECT));

        FOR_IN_SEQ(__19,(this->_defaults)->items(),20,22)
            __19 = __19;
            key = __19->__getfirst__();
            value = __19->__getsecond__();
            fp->write(__modct(const_12, 2, key, (__str(value))->replace(const_13, const_14)));
        END_FOR

        fp->write(const_13);
    }

    dict<str *, dict<str *, str *> *>::for_in_loop __3;
    int __2;
    dict<str *, dict<str *, str *> *> *__1;

    FOR_IN_NEW(section,this->_sections,1,2,3)
        fp->write(__modct(const_11, 1, section));

        FOR_IN_SEQ(__26,((this->_sections)->__getitem__(section))->items(),27,29)
            __26 = __26;
            key = __26->__getfirst__();
            value = __26->__getsecond__();
            if (__ne(key, const_15)) {
                fp->write(__modct(const_12, 2, key, (__str(value))->replace(const_13, const_14)));
            }
        END_FOR

        fp->write(const_13);
    END_FOR

    return NULL;
}

void *RawConfigParser::add_section(str *section) {
    /**
    Create a new section in the configuration.

    Raise DuplicateSectionError if a section by the specified name
    already exists.
    */
    dict<str *, dict<str *, str *> *> *__5;

    if ((this->_sections)->__contains__(section)) {
        throw ((new DuplicateSectionError(section)));
    }
    this->_sections->__setitem__(section, (new dict<str *, str *>()));
    return NULL;
}

list<str *> *RawConfigParser::sections() {
    /**
    Return a list of section names, excluding [DEFAULT]
    */

    return (this->_sections)->keys();
}

str *RawConfigParser::get(str *section, str *option, __ss_int raw, dict<str *, str *> *vars) {
    str *opt;

    opt = this->optionxform(option);
    if ((!(this->_sections)->__contains__(section))) {
        if (__ne(section, DEFAULTSECT)) {
            throw ((new NoSectionError(section)));
        }
        if ((this->_defaults)->__contains__(opt)) {
            return (this->_defaults)->__getitem__(opt);
        }
        else {
            throw ((new NoOptionError(option,section)));
        }
    }
    else if (((this->_sections)->__getitem__(section))->__contains__(opt)) {
        return ((this->_sections)->__getitem__(section))->__getitem__(opt);
    }
    else if ((this->_defaults)->__contains__(opt)) {
        return (this->_defaults)->__getitem__(opt);
    }
    else {
        throw ((new NoOptionError(option,section)));
    }
    return (str *)NULL;
}

list<str *> *RawConfigParser::read(str *filename) {
    return read(new list<str *>(1, filename));
}

list<str *> *RawConfigParser::read(list<str *> *filenames) {
    /**
    Read and parse a filename or a list of filenames.

    Files that cannot be opened are silently ignored; this is
    designed so that you can specify a list of potential
    configuration file locations (e.g. current directory, user's
    home directory, systemwide directory), and all existing
    configuration files in the list will be read.  A single
    filename may also be given.

    Return list of successfully read files.
    */
    list<str *> *__7, *read_ok;
    __iter<str *> *__8;
    str *filename;
    __ss_int __9;
    file *fp;

    read_ok = (new list<str *>());

    FOR_IN_SEQ(filename,filenames,7,9)
        try {
            fp = open(filename);
        } catch (IOError *) {
            continue;
        }
        this->_read(fp, filename);
        fp->close();
        read_ok->append(filename);
    END_FOR

    return read_ok;
}

__ss_bool RawConfigParser::getboolean(str *section, str *option) {
    str *v;

    v = this->get(section, option, default_5, NULL);
    if ((!(RawConfigParser::_boolean_states)->__contains__(v->lower()))) {
        throw ((new ValueError(__modct(const_16, 1, v))));
    }
    return __mbool((RawConfigParser::_boolean_states)->__getitem__(v->lower()));
}

list<tuple2<str *, str *> *> *RawConfigParser::items(str *section) {
    dict<str *, str *> *d, *d2;

    try {
        d2 = (this->_sections)->__getitem__(section);
    } catch (KeyError *) {
        if (__ne(section, DEFAULTSECT)) {
            throw ((new NoSectionError(section)));
        }
        d2 = (new dict<str *, str *>());
    }
    d = (this->_defaults)->copy();
    d->update(d2);
    if (d->__contains__(const_15)) {
        d->__delitem__(const_15);
    }
    return d->items();
}

void *RawConfigParser::_read(file *fp, str *fpname) {
    /**
    Parse a sectioned setup file.

    The sections in setup file contains a title line at the top,
    indicated by a name in square brackets (`[]'), plus key/value
    options lines, indicated by `name: value' format lines.
    Continuations are represented by an embedded newline then
    leading whitespace.  Blank lines, lines beginning with a '#',
    and just about everything else are ignored.
    */
    __re__::match_object *mo;
    __ss_int __33, __34, __35, __36, __41, __42, __43, __44, lineno, pos;
    dict<str *, dict<str *, str *> *> *__40;
    ParsingError *e;
    str *__37, *__38, *__39, *line, *optname, *optval, *sectname, *value, *vi;
    dict<str *, str *> *cursect;

    cursect = 0;
    optname = 0;
    lineno = 0;
    e = 0;

    while (1) {
        line = fp->readline();
        if ((!___bool(line))) {
            break;
        }
        lineno = (lineno+1);
        if (__OR(__eq(line->strip(), const_17), (const_18)->__contains__(line->__getitem__(0)), 33)) {
            continue;
        }
        if (__AND(__eq(((line->split(NULL, 1))->__getfast__(0))->lower(), const_19), (const_20)->__contains__(line->__getitem__(0)), 35)) {
            continue;
        }
        if (((line->__getitem__(0))->isspace() && (cursect!=0) && ___bool(optname))) {
            value = line->strip();
            if (___bool(value)) {
                cursect->__setitem__(optname, __modct(const_21, 2, cursect->__getitem__(optname), value));
            }
        }
        else {
            mo = (RawConfigParser::SECTCRE)->match(line);
            if (___bool(mo)) {
                sectname = mo->group(1, const_22);
                if ((this->_sections)->__contains__(sectname)) {
                    cursect = (this->_sections)->__getitem__(sectname);
                }
                else if (__eq(sectname, DEFAULTSECT)) {
                    cursect = this->_defaults;
                }
                else {
                    cursect = (new dict<str *, str *>(1, new tuple2<str *, str *>(2,const_15,sectname)));
                    this->_sections->__setitem__(sectname, cursect);
                }
                optname = 0;
            }
            else if ((cursect==0)) {
                throw ((new MissingSectionHeaderError(fpname,lineno,line)));
            }
            else {
                mo = (RawConfigParser::OPTCRE)->match(line);
                if (___bool(mo)) {
                    optname = mo->group(1, const_23);
                    vi = mo->group(1, const_24);
                    optval = mo->group(1, const_25);
                    if (__AND((const_2)->__contains__(vi), optval->__contains__(const_26), 41)) {
                        pos = optval->find(const_26);
                        if (__AND((pos!=(-1)), (optval->__getitem__((pos-1)))->isspace(), 43)) {
                            optval = optval->__slice__(2, 0, pos, 0);
                        }
                    }
                    optval = optval->strip();
                    if (__eq(optval, const_27)) {
                        optval = const_17;
                    }
                    optname = this->optionxform(optname->rstrip());
                    cursect->__setitem__(optname, optval);
                }
                else {
                    if ((!___bool(e))) {
                        e = (new ParsingError(fpname));
                    }
                    e->append(lineno, repr(line));
                }
            }
        }
    }
    if (___bool(e)) {
        throw (e);
    }
    return NULL;
}

__ss_int RawConfigParser::getint(str *section, str *option) {

    return __int(this->get(section, option, default_5, NULL));
}

dict<str *, str *> *RawConfigParser::defaults() {

    return this->_defaults;
}

list<str *> *RawConfigParser::options(str *section) {
    /**
    Return a list of option names for the given section name.
    */
    dict<str *, str *> *opts;

    try {
        opts = ((this->_sections)->__getitem__(section))->copy();
    } catch (KeyError *) {
        throw ((new NoSectionError(section)));
    }
    opts->update(this->_defaults);
    if (opts->__contains__(const_15)) {
        opts->__delitem__(const_15);
    }
    return opts->keys();
}

dict<str *, __ss_int> *RawConfigParser::_boolean_states;
__re__::re_object *RawConfigParser::SECTCRE;
__re__::re_object *RawConfigParser::OPTCRE;

/**
class ConfigParser
*/

class_ *cl_ConfigParser;

str *ConfigParser::_interpolate(str *section, str *option, str *rawval, dict<str *, str *> *vars) {
    str *value;
    __ss_int depth;

    value = rawval;
    depth = MAX_INTERPOLATION_DEPTH;

    while (depth) {
        depth = (depth-1);
        if (value->__contains__(const_28)) {
            value = (ConfigParser::_KEYCRE)->sub(_interpolation_replace, value);
            try {
                value = __moddict(value, vars);
            } catch (KeyError *e) {
                throw ((new InterpolationMissingOptionError(option,section,rawval,const_17)));
            }
        }
        else {
            break;
        }
    }
    if (value->__contains__(const_28)) {
        throw ((new InterpolationDepthError(option,section,rawval)));
    }
    return value;
}

str *ConfigParser::get(str *section, str *option, __ss_int raw, dict<str *, str *> *vars) {
    /**
    Get an option value for a given section.

    All % interpolations are expanded in the return values, based on the
    defaults passed into the constructor, unless the optional argument
    `raw' is true.  Additional substitutions may be provided using the
    `vars' argument, which must be a dictionary whose contents overrides
    any pre-existing defaults.

    The section DEFAULT is special.
    */
    __ss_int __49;
    tuple2<str *, str *> *__46;
    str *key, *value;
    list<tuple2<str *, str *> *> *__47;
    dict<str *, str *> *d;
    __iter<tuple2<str *, str *> *> *__48;

    d = (this->_defaults)->copy();
    try {
        d->update((this->_sections)->__getitem__(section));
    } catch (KeyError *) {
        if (__ne(section, DEFAULTSECT)) {
            throw ((new NoSectionError(section)));
        }
    }
    if (___bool(vars)) {

        FOR_IN_SEQ(__46,vars->items(),47,49)
            __46 = __46;
            key = __46->__getfirst__();
            value = __46->__getsecond__();
            d->__setitem__(this->optionxform(key), value);
        END_FOR

    }
    option = this->optionxform(option);
    try {
        value = d->__getitem__(option);
    } catch (KeyError *) {
        throw ((new NoOptionError(option,section)));
    }
    if (raw) {
        return value;
    }
    else {
        return this->_interpolate(section, option, value, d);
    }
    return (str *)NULL;
}

list<tuple2<str *, str *> *> *ConfigParser::items(str *section, __ss_int raw, dict<str *, str *> *vars) {
    /**
    Return a list of tuples with (name, value) for each option
    in the section.

    All % interpolations are expanded in the return values, based on the
    defaults passed into the constructor, unless the optional argument
    `raw' is true.  Additional substitutions may be provided using the
    `vars' argument, which must be a dictionary whose contents overrides
    any pre-existing defaults.

    The section DEFAULT is special.
    */
    list<str *> *options;
    __ss_int __55;
    tuple2<str *, str *> *__52;
    str *key, *value;
    list<tuple2<str *, str *> *> *__53;
    dict<str *, str *> *d;
    __iter<tuple2<str *, str *> *> *__54;

    d = (this->_defaults)->copy();
    try {
        d->update((this->_sections)->__getitem__(section));
    } catch (KeyError *) {
        if (__ne(section, DEFAULTSECT)) {
            throw ((new NoSectionError(section)));
        }
    }
    if (___bool(vars)) {

        FOR_IN_SEQ(__52,vars->items(),53,55)
            __52 = __52;
            key = __52->__getfirst__();
            value = __52->__getsecond__();
            d->__setitem__(this->optionxform(key), value);
        END_FOR

    }
    options = d->keys();
    if (options->__contains__(const_15)) {
        options->remove(const_15);
    }
    if (raw) {
        return list_comp_0(options, d);
    }
    else {
        return list_comp_1(d, this, options, section);
    }
    return (list<tuple2<str *, str *> *> *)NULL;
}

str *_interpolation_replace(__re__::match_object *match) {
    str *s;

    s = match->group(1, 1);
    if ((s==0)) {
        return match->group(1);
    }
    else {
        return __modct(new str("%%(%s)s"), 1, s->lower());
    }
    return (str *)NULL;
}

__re__::re_object *ConfigParser::_KEYCRE;

void __init() {
    const_0 = new str("=");
    const_1 = new str(":");
    const_2 = (new tuple2<str *, str *>(2, const_0, const_1));
    const_3 = new str("No section: %r");
    const_4 = new str("Section %r already exists");
    const_5 = new str("No option %r in section: %r");
    const_6 = new str("Bad value substitution:\n\tsection: [%s]\n\toption : %s\n\tkey    : %s\n\trawval : %s\n");
    const_7 = new str("Value interpolation too deeply recursive:\n\tsection: [%s]\n\toption : %s\n\trawval : %s\n");
    const_8 = new str("File contains parsing errors: %s");
    const_9 = new str("\n\t[line %2d]: %s");
    const_10 = new str("File contains no section headers.\nfile: %s, line: %d\n%r");
    const_11 = new str("[%s]\n");
    const_12 = new str("%s = %s\n");
    const_13 = new str("\n");
    const_14 = new str("\n\t");
    const_15 = new str("__name__");
    const_16 = new str("Not a boolean: %s");
    const_17 = new str("");
    const_18 = new str("#;");
    const_19 = new str("rem");
    const_20 = new str("rR");
    const_21 = new str("%s\n%s");
    const_22 = new str("header");
    const_23 = new str("option");
    const_24 = new str("vi");
    const_25 = new str("value");
    const_26 = new str(";");
    const_27 = new str("\"\"");
    const_28 = new str("%(");
    const_29 = new str("1");
    const_30 = new str("yes");
    const_31 = new str("true");
    const_32 = new str("on");
    const_33 = new str("0");
    const_34 = new str("no");
    const_35 = new str("false");
    const_36 = new str("off");
    const_37 = new str("\\[(?P<header>[^]]+)\\]");
    const_38 = new str("(?P<option>[^:=\\s][^:=]*)\\s*(?P<vi>[:=])\\s*(?P<value>.*)$");
    const_39 = new str("%\\(([^)]*)\\)s|.");
    const_40 = new str("NoSectionError");
    const_41 = new str("DuplicateSectionError");
    const_42 = new str("NoOptionError");
    const_43 = new str("InterpolationError");
    const_44 = new str("InterpolationDepthError");
    const_45 = new str("InterpolationSyntaxError");
    const_46 = new str("ParsingError");
    const_47 = new str("MissingSectionHeaderError");
    const_48 = new str("ConfigParser");
    const_49 = new str("SafeConfigParser");
    const_50 = new str("RawConfigParser");
    const_51 = new str("DEFAULTSECT");
    const_52 = new str("MAX_INTERPOLATION_DEPTH");
    const_53 = new str("DEFAULT");

    __name__ = new str("ConfigParser");

    cl_InterpolationError = new class_("InterpolationError", 16, 19);
    cl_InterpolationMissingOptionError = new class_("InterpolationMissingOptionError", 17, 17);
    cl_Error = new class_("Error", 15, 24);
    cl_InterpolationDepthError = new class_("InterpolationDepthError", 18, 18);
    cl_InterpolationSyntaxError = new class_("InterpolationSyntaxError", 19, 19);
    cl_MissingSectionHeaderError = new class_("MissingSectionHeaderError", 21, 21);
    cl_RawConfigParser = new class_("RawConfigParser", 27, 28);
    RawConfigParser::_boolean_states = (new dict<str *, __ss_int>(8, new tuple2<str *, __ss_int>(2,const_29,1), new tuple2<str *, __ss_int>(2,const_30,1), new tuple2<str *, __ss_int>(2,const_31,1), new tuple2<str *, __ss_int>(2,const_32,1), new tuple2<str *, __ss_int>(2,const_33,0), new tuple2<str *, __ss_int>(2,const_34,0), new tuple2<str *, __ss_int>(2,const_35,0), new tuple2<str *, __ss_int>(2,const_36,0)));
    RawConfigParser::SECTCRE = __re__::compile(const_37);
    RawConfigParser::OPTCRE = __re__::compile(const_38);
    cl_ParsingError = new class_("ParsingError", 20, 21);
    cl_DuplicateSectionError = new class_("DuplicateSectionError", 22, 22);
    cl_NoOptionError = new class_("NoOptionError", 23, 23);
    cl_NoSectionError = new class_("NoSectionError", 24, 24);
    cl_ConfigParser = new class_("ConfigParser", 28, 28);
    ConfigParser::_KEYCRE = __re__::compile(const_39);

    __all__ = (new list<str *>(13, const_40, const_41, const_42, const_43, const_44, const_45, const_46, const_47, const_48, const_49, const_50, const_51, const_52));
    DEFAULTSECT = const_53;
    MAX_INTERPOLATION_DEPTH = 10;
    default_0 = const_17;
    default_1 = 0;
    default_2 = 0;
    default_3 = 0;
    default_4 = 0;
    default_5 = 0;
    default_6 = 0;
    default_7 = 0;
    default_8 = 0;
}

} // module namespace

