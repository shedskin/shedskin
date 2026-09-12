/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "configparser.hpp"

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

    read_string(string, source='<string>')
        read and parse configuration data from the given string, as if it
        were the contents of a file.

    read_dict(dictionary, source='<dict>')
        read configuration from a dict of dicts (section name -> option
        name -> value); existing sections are extended, new ones created.

    get(section, option, raw=False, vars=None, fallback=None)
        return a string value for the named option.  All % interpolations are
        expanded in the return values, based on the defaults passed into the
        constructor and the DEFAULT section.  Additional substitutions may be
        provided using the `vars' argument, which must be a dictionary whose
        contents override any pre-existing defaults.  If the section/option
        isn't found and `fallback' is given (non-None), it is returned
        instead of raising NoSectionError/NoOptionError.

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

namespace __configparser__ {

tuple<str *> *const_2;
str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_21, *const_22, *const_23, *const_24, *const_25, *const_26, *const_27, *const_28, *const_29, *const_3, *const_30, *const_31, *const_32, *const_33, *const_34, *const_35, *const_36, *const_37, *const_38, *const_4, *const_40, *const_41, *const_42, *const_43, *const_44, *const_45, *const_46, *const_47, *const_48, *const_5, *const_50, *const_51, *const_52, *const_53, *const_54, *const_55, *const_56, *const_57, *const_58, *const_59, *const_6, *const_60, *const_61, *const_62, *const_63, *const_64, *const_65, *const_66, *const_67, *const_68, *const_69, *const_7, *const_70, *const_71, *const_72, *const_8, *const_9;

str *DEFAULTSECT, *__name__;
__ss_int MAX_INTERPOLATION_DEPTH;

str * default_11;
__ss_int  default_10;
__ss_int  default_13;
__ss_int  default_23;
__ss_int  default_25;
__ss_int  default_28;
__ss_int  default_1;
__ss_int  default_5;
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

/**
class Error
*/

class_ *cl_Error;

void *Error::__init__(str *msg) {
    /* All subclasses funnel their formatted message through this
       post-construction __init__() call rather than through the base
       Exception(str*) constructor, so BaseException::args (a 1-tuple
       of the message, normally set by that constructor) is left as
       whatever the default-constructed base subobject had -- a
       tuple(1, NULL). BaseException::__str__()/__repr__() read args[0],
       so without this, str(e) prints "None" and repr(e) dereferences a
       null str* and segfaults. Setting args here, the same way the real
       constructor does, fixes both via the existing base implementations. */
    message = msg;
    this->args = new tuple<str *>(1, msg);
    Exception::__init__(msg);
    return NULL;
}


/**
class NoSectionError
*/

class_ *cl_NoSectionError;

void *NoSectionError::__init__(str *section_) {

    Error::__init__(__mod6(const_3, 1, section_));
    section = section_;
    return NULL;
}

/**
class DuplicateSectionError
*/

class_ *cl_DuplicateSectionError;

void *DuplicateSectionError::__init__(str *section_, str *source_, __ss_int lineno_) {

    if (source_ != NULL && lineno_ != -1) {
        Error::__init__(__mod6(const_54, 3, source_, lineno_, section_));
    }
    else {
        Error::__init__(__mod6(const_4, 1, section_));
    }
    section = section_;
    source = source_;
    lineno = lineno_;
    return NULL;
}

/**
class DuplicateOptionError
*/

class_ *cl_DuplicateOptionError;

void *DuplicateOptionError::__init__(str *section_, str *option_, str *source_, __ss_int lineno_) {

    if (source_ != NULL && lineno_ != -1) {
        Error::__init__(__mod6(const_56, 4, source_, lineno_, option_, section_));
    }
    else {
        Error::__init__(__mod6(const_55, 2, option_, section_));
    }
    section = section_;
    option = option_;
    source = source_;
    lineno = lineno_;
    return NULL;
}

/**
class NoOptionError
*/

class_ *cl_NoOptionError;

void *NoOptionError::__init__(str *option_, str *section_) {

    Error::__init__(__mod6(const_5, 2, option_, section_));
    option = option_;
    section = section_;
    return NULL;
}

/**
class InterpolationError
*/

class_ *cl_InterpolationError;

void *InterpolationError::__init__(str *option_, str *section_, str *msg) {

    Error::__init__(msg);
    option = option_;
    section = section_;
    return NULL;
}


/**
class InterpolationMissingOptionError
*/

class_ *cl_InterpolationMissingOptionError;

void *InterpolationMissingOptionError::__init__(str *option_, str *section_, str *rawval, str *reference_) {
    str *msg;

    msg = __mod6(const_6, 4, section_, option_, reference_, rawval);
    InterpolationError::__init__(option_, section_, msg);
    reference = reference_;
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

void *InterpolationDepthError::__init__(str *option_, str *section_, str *rawval) {
    str *msg;

    msg = __mod6(const_7, 3, section_, option_, rawval);
    InterpolationError::__init__(option_, section_, msg);
    return NULL;
}

/**
class ParsingError
*/

class_ *cl_ParsingError;

void *ParsingError::__init__(str *filename_) {

    Error::__init__(__mod6(const_8, 1, filename_));
    filename = filename_;
    errors = (new list<tuple2<__ss_int, str *> *>());
    return NULL;
}

void *ParsingError::append(__ss_int lineno, str *line) {

    (this->errors)->append((new tuple2<__ss_int, str *>(2, lineno, line)));
    this->message = (this->message)->__iadd__(__mod6(const_9, 2, lineno, line));
    return NULL;
}

/**
class MissingSectionHeaderError
*/

class_ *cl_MissingSectionHeaderError;

void *MissingSectionHeaderError::__init__(str *filename_, __ss_int lineno_, str *line_) {

    Error::__init__(__mod6(const_10, 3, filename_, lineno_, line_));
    filename = filename_;
    lineno = lineno_;
    line = line_;
    return NULL;
}

/**
class RawConfigParser
*/

class_ *cl_RawConfigParser;

str *RawConfigParser::optionxform(str *optionstr) {

    return optionstr->lower();
}

void *RawConfigParser::_set(str *section, str *option, str *value) {
    /**
    Set an option. Non-empty values are passed through the interpolation
    object's before_set() first (matching CPython's set()), which for
    BasicInterpolation/ExtendedInterpolation validates the %/$ syntax and
    raises ValueError on stray '%' or '$'. This also covers read_dict()
    and the mapping-protocol setters, which funnel through here, exactly
    like CPython's counterparts funnel through set().
    */
    __ss_int __16;
    dict<str *, str *> *sectdict;

    if (___bool(value)) {
        value = (this->_interpolation)->before_set(this, section, option, value);
    }
    if (__OR((!___bool(section)), __eq(section, this->default_section), 16)) {
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
    __ss_int __30;
    __ss_bool existed;
    dict<str *, str *> *sectdict;

    if (__OR((!___bool(section)), __eq(section, this->default_section), 30)) {
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

Interpolation *RawConfigParser::_default_interpolation() {
    return new Interpolation();
}

Interpolation *ConfigParser::_default_interpolation() {
    return new BasicInterpolation();
}

void *RawConfigParser::__init__(dict<str *, str *> *defaults, str *default_section_, Interpolation *interpolation_) {
    __ss_int __3;
    tuple<str *> *__0;
    str *key, *value;
    __iter<tuple<str *> *> *__1;


    __iter<tuple<str *> *>::for_in_loop __123;

    this->_sections = (new dict<str *, dict<str *, str *> *>());
    this->_defaults = (new dict<str *, str *>());
    this->default_section = (default_section_ != NULL) ? default_section_ : DEFAULTSECT;
    this->_interpolation = (interpolation_ != NULL) ? interpolation_ : this->_default_interpolation();
    if (___bool(defaults)) {

        FOR_IN(__0,defaults->items(),1,3,123)
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
    __ss_int __12;
    __ss_bool __14;

    if (__OR((!___bool(section)), __eq(section, this->default_section), 12)) {
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
    __ss_int __22, __29;

    str *key, *section, *value;
    tuple<str *> *__19, *__26;

    __iter<tuple<str *> *> *__20, *__27;

    __iter<tuple<str *> *>::for_in_loop __123;

    if (___bool(this->_defaults)) {
        fp->write(__mod6(const_11, 1, this->default_section));

        FOR_IN(__19,(this->_defaults)->items(),20,22,123)
            __19 = __19;
            key = __19->__getfirst__();
            value = __19->__getsecond__();
            fp->write(__mod6(const_12, 2, key, (__str(value))->replace(const_13, const_14)));
        END_FOR

        fp->write(const_13);
    }

    dict<str *, dict<str *, str *> *>::for_in_loop __3;
    int __2;
    dict<str *, dict<str *, str *> *> *__1;

    FOR_IN(section,this->_sections,1,2,3)
        fp->write(__mod6(const_11, 1, section));

        FOR_IN(__26,((this->_sections)->__getitem__(section))->items(),27,29,123)
            __26 = __26;
            key = __26->__getfirst__();
            value = __26->__getsecond__();
            if (__ne(key, const_15)) {
                fp->write(__mod6(const_12, 2, key, (__str(value))->replace(const_13, const_14)));
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

    return new list<str *>((this->_sections)->keys());
}

dict<str *, str *> *RawConfigParser::_unify_values(str *section, dict<str *, str *> *vars) {
    /**
    Create a copy of the DEFAULT values, updated with the values of the
    given section and the option-name-normalized contents of `vars`
    (CPython's _unify_values). Raises NoSectionError for an unknown
    non-default section.
    */
    __ss_int __46;
    tuple<str *> *__44;
    str *key, *value;
    __iter<tuple<str *> *> *__45;
    dict<str *, str *> *d;

    __iter<tuple<str *> *>::for_in_loop __123;

    d = (this->_defaults)->copy();
    try {
        d->update((this->_sections)->__getitem__(section));
    } catch (KeyError *) {
        if (__ne(section, this->default_section)) {
            throw ((new NoSectionError(section)));
        }
    }
    if (___bool(vars)) {

        FOR_IN(__44,vars->items(),45,46,123)
            __44 = __44;
            key = __44->__getfirst__();
            value = __44->__getsecond__();
            d->__setitem__(this->optionxform(key), value);
        END_FOR

    }
    return d;
}

str *RawConfigParser::get(str *section, str *option, __ss_int raw, dict<str *, str *> *vars, str *fallback) {
    /**
    Get an option value for a given section.

    If `vars' is provided, it must be a dictionary. The option is looked
    up in `vars' (if provided), `section', and in `DEFAULTSECT' in that
    order. If the key is not found and `fallback' is given (non-None), it
    is returned instead of raising NoSectionError/NoOptionError.

    Unless `raw' is true, the value is passed through the interpolation
    object's before_get(): a no-op for RawConfigParser's default dummy
    Interpolation, %-expansion for ConfigParser's default
    BasicInterpolation, ${}-expansion for ExtendedInterpolation.
    */
    str *value;
    dict<str *, str *> *d;

    try {
        d = this->_unify_values(section, vars);
        option = this->optionxform(option);
        try {
            value = d->__getitem__(option);
        } catch (KeyError *) {
            throw ((new NoOptionError(option,section)));
        }
    } catch (NoSectionError *) {
        if (fallback != NULL) return fallback;
        throw;
    } catch (NoOptionError *) {
        if (fallback != NULL) return fallback;
        throw;
    }
    if (raw) {
        return value;
    }
    return (this->_interpolation)->before_get(this, section, option, value, d);
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

    str *filename;
    __ss_int __9;
    file *fp;
    list<str *>::for_in_loop __123;

    read_ok = (new list<str *>());

    FOR_IN(filename,filenames,7,9,123)
        try {
            fp = open(filename);
        } catch (OSError *) {
            continue;
        }
        this->_read(fp, filename);
        fp->close();
        read_ok->append(filename);
    END_FOR

    return read_ok;
}

__ss_bool RawConfigParser::_to_boolean(str *v) {
    if ((!(RawConfigParser::_boolean_states)->__contains__(v->lower()))) {
        throw ((new ValueError(__mod6(const_16, 1, v))));
    }
    return __mbool((RawConfigParser::_boolean_states)->__getitem__(v->lower()));
}

list<tuple2<str *, SectionProxy *> *> *RawConfigParser::items(dict<str *, str *> *, __ss_int) {
    /**
    Return a list of (section_name, SectionProxy) pairs for every
    section, including the default section. Each proxy is a live,
    write-through view (calls through the virtual get()/has_option()/
    etc.), so this also picks up interpolation correctly when called
    on a ConfigParser.
    */
    list<tuple2<str *, SectionProxy *> *> *result;
    str *name;
    tuple2<str *, dict<str *, str *> *> *__1;
    __iter<tuple2<str *, dict<str *, str *> *> *> *__2;
    __ss_int __3;
    __iter<tuple2<str *, dict<str *, str *> *> *>::for_in_loop __123;

    result = (new list<tuple2<str *, SectionProxy *> *>());
    result->append((new tuple2<str *, SectionProxy *>(2, this->default_section, (new SectionProxy(this, this->default_section)))));

    FOR_IN(__1,(this->_sections)->items(),2,3,123)
        __1 = __1;
        name = __1->__getfirst__();
        result->append((new tuple2<str *, SectionProxy *>(2, name, (new SectionProxy(this, name)))));
    END_FOR

    return result;
}

list<tuple<str *> *> *RawConfigParser::items(dict<str *, str *> *vars, __ss_int raw, str *section) {
    /**
    Return a list of (name, value) tuples for each option in the section.

    Matching CPython: keys that only exist in `vars` are used for
    interpolation but do not show up in the result, and unless `raw` is
    true each value is passed through the interpolation object's
    before_get().
    */
    dict<str *, str *> *d, *d2;
    list<str *> *orig_keys;
    list<tuple<str *> *> *result;
    str *opt, *value;
    __ss_int __62;
    list<str *> *__63;
    list<str *>::for_in_loop __123;

    try {
        d2 = (this->_sections)->__getitem__(section);
    } catch (KeyError *) {
        if (__ne(section, this->default_section)) {
            throw ((new NoSectionError(section)));
        }
        d2 = (new dict<str *, str *>());
    }
    d = (this->_defaults)->copy();
    d->update(d2);
    if (d->__contains__(const_15)) {
        d->__delitem__(const_15);
    }
    orig_keys = new list<str *>(d->keys());
    if (___bool(vars)) {
        tuple<str *> *__65;
        __iter<tuple<str *> *> *__66;
        __ss_int __67;
        __iter<tuple<str *> *>::for_in_loop __124;

        FOR_IN(__65,vars->items(),66,67,124)
            __65 = __65;
            d->__setitem__(this->optionxform(__65->__getfirst__()), __65->__getsecond__());
        END_FOR

    }
    result = (new list<tuple<str *> *>());

    FOR_IN(opt,orig_keys,63,62,123)
        value = d->__getitem__(opt);
        if (!raw) {
            value = (this->_interpolation)->before_get(this, section, opt, value, d);
        }
        result->append((new tuple<str *>(2, opt, value)));
    END_FOR

    return result;
}

tuple2<str *, SectionProxy *> *RawConfigParser::popitem() {
    /**
    Remove a section from the parser and return it as a
    (section_name, section_proxy) tuple. If no section is present, raise
    KeyError. The default section is never returned because it cannot be
    removed.
    */
    list<str *> *secs;
    str *key;
    SectionProxy *value;

    secs = this->sections();
    if (len(secs) == 0) {
        throw ((new KeyError(const_17)));
    }
    key = secs->__getitem__(0);
    value = this->__getitem__(key);
    this->__delitem__(key);
    return (new tuple2<str *, SectionProxy *>(2, key, value));
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
    __ss_int __33, __41, __43, lineno, pos;

    ParsingError *e;
    str *line, *optname, *optval, *sectname, *value, *vi, *cursectname;
    dict<str *, str *> *cursect;
    set<str *> *elements_added;
    set<str *> *cur_options;

    cursect = 0;
    cursectname = 0;
    optname = 0;
    lineno = 0;
    e = 0;
    /* Tracks section names and "section\x01option" keys added while
       parsing *this* source, mirroring CPython's strict=True default:
       re-reading an already-existing section across multiple read()
       calls is fine, but repeating a section header or an option
       within a single file/string/dict is an error. */
    elements_added = (new set<str *>());
    cur_options = 0;

    while (1) {
        line = fp->readline();
        if ((!___bool(line))) {
            break;
        }
        lineno = (lineno+1);
        if (__OR(__eq(line->strip(), const_17), (const_18)->__contains__(line->__getitem__(0)), 33)) {
            continue;
        }
        if (((line->__getitem__(0))->isspace() && (cursect!=0) && ___bool(optname))) {
            value = line->strip();
            if (___bool(value)) {
                cursect->__setitem__(optname, __mod6(const_21, 2, cursect->__getitem__(optname), value));
            }
        }
        else {
            mo = (RawConfigParser::SECTCRE)->match(line);
            if (___bool(mo)) {
                sectname = mo->group(1, const_22);
                if (elements_added->__contains__(sectname)) {
                    throw ((new DuplicateSectionError(sectname, fpname, lineno)));
                }
                elements_added->add(sectname);
                if ((this->_sections)->__contains__(sectname)) {
                    cursect = (this->_sections)->__getitem__(sectname);
                }
                else if (__eq(sectname, this->default_section)) {
                    cursect = this->_defaults;
                }
                else {
                    cursect = (new dict<str *, str *>(1, new tuple<str *>(2,const_15,sectname)));
                    this->_sections->__setitem__(sectname, cursect);
                }
                cursectname = sectname;
                cur_options = (new set<str *>());
                optname = 0;
            }
            else if (cursect==0) {
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
                    if ((cur_options != 0) && cur_options->__contains__(optname)) {
                        throw ((new DuplicateOptionError(cursectname, optname, fpname, lineno)));
                    }
                    if (cur_options != 0) {
                        cur_options->add(optname);
                    }
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

void *RawConfigParser::read_string(str *string_, str *source) {
    /**
    Read configuration from a given string, as if it were the contents
    of a file.
    */
    __io__::StringIO *sfile;

    if (source == NULL) {
        source = new str("<string>");
    }
    sfile = new __io__::StringIO(string_);
    this->_read(sfile, source);
    return NULL;
}

void *RawConfigParser::read_file(file *fp, str *source) {
    /**
    Like read() but the argument must be a file-like object.

    The `source' argument is optional, and if not given, the `name'
    attribute of the given `fp' is used instead. This is aimed at
    non-string filenames such as pathlib.Path objects.
    */

    if (source == NULL) {
        source = fp->name;
        if (source == NULL) {
            source = new str("<?\?>");
        }
    }
    this->_read(fp, source);
    return NULL;
}

void *RawConfigParser::read_dict(dict<str *, dict<str *, str *> *> *dictionary, str *source) {
    /**
    Read configuration from a dict of dicts (section name -> option name
    -> value). Existing sections are extended in place, new ones created.

    `source` is accepted for signature compatibility with CPython but is
    currently unused: this parser doesn't implement strict-mode duplicate
    detection (DuplicateSectionError/DuplicateOptionError) for read_dict,
    since duplicate keys can't occur within a single Python dict anyway.
    */
    dict<str *, dict<str *, str *> *> *__300;
    int __301;
    dict<str *, dict<str *, str *> *>::for_in_loop __302;
    str *section, *key, *value;
    dict<str *, str *> *keys;
    tuple<str *> *pair;
    __iter<tuple<str *> *> *__310;
    __ss_int __311;
    __iter<tuple<str *> *>::for_in_loop __312;

    (void)source;

    FOR_IN(section,dictionary,300,301,302)
        if (__ne(section, this->default_section) && (!(this->_sections)->__contains__(section))) {
            this->add_section(section);
        }
        keys = dictionary->__getitem__(section);

        FOR_IN(pair,keys->items(),310,311,312)
            key = pair->__getfirst__();
            value = pair->__getsecond__();
            this->_set(section, key, value);
        END_FOR
    END_FOR

    return NULL;
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
    return new list<str *>(opts->keys());
}

SectionProxy *RawConfigParser::__getitem__(str *section) {
    /**
    Return a SectionProxy for the given section, supporting
    config[section][option]-style access. The DEFAULT section is
    accessible too, mirroring __contains__/__iter__ below.
    */

    if (__ne(section, this->default_section) && (!(this->_sections)->__contains__(section))) {
        throw ((new KeyError(section)));
    }
    return (new SectionProxy(this, section));
}

void *RawConfigParser::__setitem__(str *section, dict<str *, str *> *value) {
    /**
    Overwrite (or create) a whole section from a dict of option/value
    pairs, e.g. config[section] = {'x': '1'}.
    */

    if (__eq(section, this->default_section)) {
        (this->_defaults)->clear();
    }
    else if ((this->_sections)->__contains__(section)) {
        ((this->_sections)->__getitem__(section))->clear();
    }
    this->read_dict((new dict<str *, dict<str *, str *> *>(1, new tuple2<str *, dict<str *, str *> *>(2, section, value))), NULL);
    return NULL;
}

void *RawConfigParser::__delitem__(str *section) {

    if (__eq(section, this->default_section)) {
        throw ((new ValueError(const_58)));
    }
    if ((!(this->_sections)->__contains__(section))) {
        throw ((new KeyError(section)));
    }
    this->remove_section(section);
    return NULL;
}

__ss_bool RawConfigParser::__contains__(str *section) {

    return __mbool(__eq(section, this->default_section) || (this->_sections)->__contains__(section));
}

__ss_int RawConfigParser::__len__() {

    return (len(this->_sections)+1);
}

__iter<str *> *RawConfigParser::__iter__() {
    /**
    Iterate over section names, DEFAULT first (matching CPython).
    */
    list<str *> *names;

    names = (new list<str *>(1, this->default_section));
    names->extend((this->_sections)->keys());
    return names->__iter__();
}

dict<str *, __ss_int> *RawConfigParser::_boolean_states;
__re__::re_object *RawConfigParser::SECTCRE;
__re__::re_object *RawConfigParser::OPTCRE;

/**
class Interpolation
*/

class_ *cl_Interpolation;

str *Interpolation::before_get(RawConfigParser *, str *, str *, str *value, dict<str *, str *> *) {
    return value;
}

str *Interpolation::before_set(RawConfigParser *, str *, str *, str *value) {
    return value;
}

str *Interpolation::before_read(RawConfigParser *, str *, str *, str *value) {
    return value;
}

str *Interpolation::before_write(RawConfigParser *, str *, str *, str *value) {
    return value;
}

/**
class BasicInterpolation
*/

class_ *cl_BasicInterpolation;
__re__::re_object *BasicInterpolation::_KEYCRE;

str *BasicInterpolation::before_get(RawConfigParser *parser, str *section, str *option, str *value, dict<str *, str *> *defaults) {
    list<str *> *L;

    L = (new list<str *>());
    this->_interpolate_some(parser, option, L, value, section, defaults, 1);
    return const_17->join(L);
}

str *BasicInterpolation::before_set(RawConfigParser *, str *section, str *option, str *value) {
    str *tmp_value;
    __ss_int pos;

    tmp_value = value->replace(const_61, const_17); /* escaped percent signs */
    tmp_value = (BasicInterpolation::_KEYCRE)->sub(const_17, tmp_value); /* valid syntax */
    pos = tmp_value->find(const_63);
    if (pos >= 0) {
        throw ((new ValueError(__mod6(const_65, 2, value, pos))));
    }
    (void)section; (void)option;
    return value;
}

void BasicInterpolation::_interpolate_some(RawConfigParser *parser, str *option, list<str *> *accum, str *rest, str *section, dict<str *, str *> *map, __ss_int depth) {
    /**
    Faithful port of CPython's BasicInterpolation._interpolate_some().
    */
    str *rawval, *c, *var, *v;
    __ss_int p;
    __re__::match_object *m;

    rawval = parser->get(section, option, 1, NULL, rest);
    if (depth > MAX_INTERPOLATION_DEPTH) {
        throw ((new InterpolationDepthError(option, section, rawval)));
    }
    while (len(rest) > 0) {
        p = rest->find(const_63);
        if (p < 0) {
            accum->append(rest);
            return;
        }
        if (p > 0) {
            accum->append(rest->__slice__(2, 0, p, 0));
            rest = rest->__slice__(1, p, 0, 0);
        }
        /* p is no longer used */
        c = rest->__slice__(3, 1, 2, 0);
        if (__eq(c, const_63)) { /* '%' */
            accum->append(const_63);
            rest = rest->__slice__(1, 2, 0, 0);
        }
        else if (__eq(c, const_66)) { /* '(' */
            m = (BasicInterpolation::_KEYCRE)->match(rest);
            if (!m) {
                throw ((new InterpolationSyntaxError(option, section, __mod6(const_67, 1, rest))));
            }
            var = parser->optionxform(m->group(1, 1));
            rest = rest->__slice__(1, m->end(), 0, 0);
            try {
                v = map->__getitem__(var);
            } catch (KeyError *) {
                throw ((new InterpolationMissingOptionError(option, section, rawval, var)));
            }
            if (v->__contains__(const_63)) {
                this->_interpolate_some(parser, option, accum, v, section, map, (depth+1));
            }
            else {
                accum->append(v);
            }
        }
        else {
            throw ((new InterpolationSyntaxError(option, section, __mod6(const_68, 1, rest))));
        }
    }
}

/**
class ExtendedInterpolation
*/

class_ *cl_ExtendedInterpolation;
__re__::re_object *ExtendedInterpolation::_KEYCRE;

str *ExtendedInterpolation::before_get(RawConfigParser *parser, str *section, str *option, str *value, dict<str *, str *> *defaults) {
    list<str *> *L;

    L = (new list<str *>());
    this->_interpolate_some(parser, option, L, value, section, defaults, 1);
    return const_17->join(L);
}

str *ExtendedInterpolation::before_set(RawConfigParser *, str *section, str *option, str *value) {
    str *tmp_value;
    __ss_int pos;

    tmp_value = value->replace(const_62, const_17); /* escaped dollar signs */
    tmp_value = (ExtendedInterpolation::_KEYCRE)->sub(const_17, tmp_value); /* valid syntax */
    pos = tmp_value->find(const_64);
    if (pos >= 0) {
        throw ((new ValueError(__mod6(const_65, 2, value, pos))));
    }
    (void)section; (void)option;
    return value;
}

void ExtendedInterpolation::_interpolate_some(RawConfigParser *parser, str *option, list<str *> *accum, str *rest, str *section, dict<str *, str *> *map, __ss_int depth) {
    /**
    Faithful port of CPython's ExtendedInterpolation._interpolate_some():
    ${opt} looks up in the current section (via `map`), ${sect:opt} in
    another section; recursion re-derives the map for the target section.
    */
    str *rawval, *c, *sect, *opt, *v;
    list<str *> *path;
    __ss_int p;
    __re__::match_object *m;

    rawval = parser->get(section, option, 1, NULL, rest);
    if (depth > MAX_INTERPOLATION_DEPTH) {
        throw ((new InterpolationDepthError(option, section, rawval)));
    }
    while (len(rest) > 0) {
        p = rest->find(const_64);
        if (p < 0) {
            accum->append(rest);
            return;
        }
        if (p > 0) {
            accum->append(rest->__slice__(2, 0, p, 0));
            rest = rest->__slice__(1, p, 0, 0);
        }
        /* p is no longer used */
        c = rest->__slice__(3, 1, 2, 0);
        if (__eq(c, const_64)) { /* '$' */
            accum->append(const_64);
            rest = rest->__slice__(1, 2, 0, 0);
        }
        else if (__eq(c, const_69)) { /* '{' */
            m = (ExtendedInterpolation::_KEYCRE)->match(rest);
            if (!m) {
                throw ((new InterpolationSyntaxError(option, section, __mod6(const_70, 1, rest))));
            }
            path = (m->group(1, 1))->split(const_1);
            rest = rest->__slice__(1, m->end(), 0, 0);
            sect = section;
            opt = option;
            try {
                if (len(path) == 1) {
                    opt = parser->optionxform(path->__getfast__(0));
                    v = map->__getitem__(opt);
                }
                else if (len(path) == 2) {
                    sect = path->__getfast__(0);
                    opt = parser->optionxform(path->__getfast__(1));
                    v = parser->get(sect, opt, 1, NULL, NULL);
                }
                else {
                    throw ((new InterpolationSyntaxError(option, section, __mod6(const_71, 1, rest))));
                }
            } catch (KeyError *) {
                throw ((new InterpolationMissingOptionError(option, section, rawval, const_1->join(path))));
            } catch (NoSectionError *) {
                throw ((new InterpolationMissingOptionError(option, section, rawval, const_1->join(path))));
            } catch (NoOptionError *) {
                throw ((new InterpolationMissingOptionError(option, section, rawval, const_1->join(path))));
            }
            if (v->__contains__(const_64)) {
                dict<str *, str *> *submap;
                list<tuple<str *> *> *subitems;
                tuple<str *> *t;
                __ss_int k, n;

                submap = (new dict<str *, str *>());
                subitems = parser->items(NULL, 1, sect);
                n = len(subitems);
                for (k = 0; k < n; k++) {
                    t = subitems->__getfast__(k);
                    submap->__setitem__(t->__getfirst__(), t->__getsecond__());
                }
                this->_interpolate_some(parser, opt, accum, v, sect, submap, (depth+1));
            }
            else {
                accum->append(v);
            }
        }
        else {
            throw ((new InterpolationSyntaxError(option, section, __mod6(const_72, 1, rest))));
        }
    }
}

/**
class ConfigParser
*/

class_ *cl_ConfigParser;

/**
class SectionProxy
*/

class_ *cl_SectionProxy;

void *SectionProxy::__init__(RawConfigParser *parser_, str *name_) {

    _parser = parser_;
    _name = name_;
    return NULL;
}

str *RawConfigParser::_get_or_null(str *section, str *option, __ss_int raw, dict<str *, str *> *vars) {
    try {
        return this->get(section, option, raw, vars, NULL);
    } catch (NoSectionError *) {
        return NULL;
    } catch (NoOptionError *) {
        return NULL;
    }
}

str *SectionProxy::__repr__() {
    return __add_strs(3, new str("<Section: "), _name, new str(">"));
}

/* Unlike RawConfigParser.get(), a missing option returns 'fallback' (None
   by default) instead of raising, matching CPython's SectionProxy.get(). */
str *SectionProxy::get(str *option, str *fallback, __ss_int raw, dict<str *, str *> *vars) {
    str *v = _parser->_get_or_null(_name, option, raw, vars);
    return v ? v : fallback;
}

list<str *> *SectionProxy::_options() {
    /**
    The DEFAULT section has no entry of its own in _sections, so its
    options come from defaults() instead of options(name) -- same
    special-casing as get()/has_option() elsewhere in this file.
    */

    if (__eq(_name, _parser->default_section)) {
        return new list<str *>((_parser->defaults())->keys());
    }
    return _parser->options(_name);
}

str *SectionProxy::__getitem__(str *key) {

    if ((!_parser->has_option(_name, key))) {
        throw ((new KeyError(key)));
    }
    return _parser->get(_name, key, default_5, NULL);
}

void *SectionProxy::__setitem__(str *key, str *value) {

    _parser->_set(_name, key, value);
    return NULL;
}

void *SectionProxy::__delitem__(str *key) {

    if ((!_parser->has_option(_name, key))) {
        throw ((new KeyError(key)));
    }
    _parser->remove_option(_name, key);
    return NULL;
}

__ss_bool SectionProxy::__contains__(str *key) {

    return _parser->has_option(_name, key);
}

__ss_int SectionProxy::__len__() {

    return len(_options());
}

__iter<str *> *SectionProxy::__iter__() {

    return (_options())->__iter__();
}



void __init() {
    const_0 = new str("=");
    const_1 = new str(":");
    const_2 = (new tuple<str *>(2, const_0, const_1));
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
    const_40 = new str("NoSectionError");
    const_41 = new str("DuplicateSectionError");
    const_42 = new str("NoOptionError");
    const_43 = new str("InterpolationError");
    const_44 = new str("InterpolationDepthError");
    const_45 = new str("InterpolationSyntaxError");
    const_46 = new str("ParsingError");
    const_47 = new str("MissingSectionHeaderError");
    const_48 = new str("ConfigParser");
    const_50 = new str("RawConfigParser");
    const_51 = new str("DEFAULTSECT");
    const_52 = new str("MAX_INTERPOLATION_DEPTH");
    const_53 = new str("DEFAULT");
    const_54 = new str("While reading from %r [line %2d]: section %r already exists");
    const_55 = new str("Option %r in section %r already exists");
    const_56 = new str("While reading from %r [line %2d]: option %r in section %r already exists");
    const_57 = new str("DuplicateOptionError");
    const_58 = new str("Cannot remove the default section.");
    const_59 = new str("%\\(([^)]+)\\)s");
    const_60 = new str("\\$\\{([^}]+)\\}");
    const_61 = new str("%%");
    const_62 = new str("$$");
    const_63 = new str("%");
    const_64 = new str("$");
    const_65 = new str("invalid interpolation syntax in %r at position %d");
    const_66 = new str("(");
    const_67 = new str("bad interpolation variable reference %r");
    const_68 = new str("'%%' must be followed by '%%' or '(', found: %r");
    const_69 = new str("{");
    const_70 = new str("bad interpolation variable reference %r");
    const_71 = new str("More than one ':' found: %r");
    const_72 = new str("'$' must be followed by '$' or '{', found: %r");

    __name__ = new str("ConfigParser");

    cl_InterpolationError = new class_("InterpolationError");
    cl_InterpolationMissingOptionError = new class_("InterpolationMissingOptionError");
    cl_Error = new class_("Error");
    cl_InterpolationDepthError = new class_("InterpolationDepthError");
    cl_InterpolationSyntaxError = new class_("InterpolationSyntaxError");
    cl_MissingSectionHeaderError = new class_("MissingSectionHeaderError");
    cl_RawConfigParser = new class_("RawConfigParser");
    RawConfigParser::_boolean_states = (new dict<str *, __ss_int>(8, new tuple2<str *, __ss_int>(2,const_29,1), new tuple2<str *, __ss_int>(2,const_30,1), new tuple2<str *, __ss_int>(2,const_31,1), new tuple2<str *, __ss_int>(2,const_32,1), new tuple2<str *, __ss_int>(2,const_33,0), new tuple2<str *, __ss_int>(2,const_34,0), new tuple2<str *, __ss_int>(2,const_35,0), new tuple2<str *, __ss_int>(2,const_36,0)));
    RawConfigParser::SECTCRE = __re__::compile(const_37);
    RawConfigParser::OPTCRE = __re__::compile(const_38);
    cl_ParsingError = new class_("ParsingError");
    cl_DuplicateSectionError = new class_("DuplicateSectionError");
    cl_DuplicateOptionError = new class_("DuplicateOptionError");
    cl_NoOptionError = new class_("NoOptionError");
    cl_NoSectionError = new class_("NoSectionError");
    cl_ConfigParser = new class_("ConfigParser");
    cl_Interpolation = new class_("Interpolation");
    cl_BasicInterpolation = new class_("BasicInterpolation");
    cl_ExtendedInterpolation = new class_("ExtendedInterpolation");
    BasicInterpolation::_KEYCRE = __re__::compile(const_59);
    ExtendedInterpolation::_KEYCRE = __re__::compile(const_60);
    cl_SectionProxy = new class_("SectionProxy");

    DEFAULTSECT = const_53;
    MAX_INTERPOLATION_DEPTH = 10;
    default_0 = const_17;
    default_1 = 0;
    default_4 = 0;
    default_5 = 0;
    default_6 = 0;
    default_7 = 0;
    default_8 = 0;
}

} // module namespace

