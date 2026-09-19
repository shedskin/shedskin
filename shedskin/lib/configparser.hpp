/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __CONFIGPARSER_HPP
#define __CONFIGPARSER_HPP

#include "builtin.hpp"
#include "re.hpp"
#include "io.hpp"
#include <limits>

using namespace __shedskin__;
namespace __configparser__ {

extern str *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_21, *const_22, *const_23, *const_25, *const_27, *const_28, *const_29, *const_3, *const_30, *const_31, *const_32, *const_33, *const_34, *const_35, *const_36, *const_37, *const_38, *const_4, *const_40, *const_41, *const_42, *const_43, *const_44, *const_45, *const_46, *const_47, *const_48, *const_5, *const_50, *const_51, *const_52, *const_53, *const_54, *const_55, *const_56, *const_57, *const_58, *const_59, *const_6, *const_60, *const_61, *const_62, *const_63, *const_64, *const_65, *const_66, *const_67, *const_68, *const_69, *const_7, *const_70, *const_71, *const_72, *const_73, *const_74, *const_75, *const_76, *const_77, *const_78, *const_79, *const_8, *const_80, *const_81, *const_82, *const_83, *const_84, *const_85, *const_86, *const_87, *const_9;

class Error;
class NoSectionError;
class DuplicateSectionError;
class DuplicateOptionError;
class NoOptionError;
class InterpolationError;
class InterpolationMissingOptionError;
class InterpolationSyntaxError;
class InterpolationDepthError;
class ParsingError;
class MissingSectionHeaderError;
class MultilineContinuationError;
class InvalidWriteError;
class Interpolation;
class BasicInterpolation;
class ExtendedInterpolation;
class RawConfigParser;
class ConfigParser;
class SectionProxy;

extern str *DEFAULTSECT, *__name__;
extern __ss_int MAX_INTERPOLATION_DEPTH;

extern class_ *cl_Error;
class Error : public Exception {
/**
Base class for ConfigParser exceptions.
*/
public:

    str *message;

    Error() {}
    Error(str *msg) {
        this->__class__ = cl_Error;
        __init__(msg);
    }
    void *__init__(str *msg);
};

extern class_ *cl_NoSectionError;
class NoSectionError : public Error {
/**
Raised when no section matches a requested option.
*/
public:
    str *section;

    NoSectionError() {}
    NoSectionError(str *section_) {
        this->__class__ = cl_NoSectionError;
        __init__(section_);
    }
    void *__init__(str *section_);
};

extern class_ *cl_DuplicateSectionError;
class DuplicateSectionError : public Error {
/**
Raised when a section is multiply-created.

Possible repetitions that raise this exception are: multiple creation
using the API, or (when `source` is given) a section found more than
once while parsing a single file, string or dict.
*/
public:
    str *section;
    str *source;
    __ss_int lineno;

    DuplicateSectionError() {}
    DuplicateSectionError(str *section_, str *source_=NULL, __ss_int lineno_=-1) {
        this->__class__ = cl_DuplicateSectionError;
        __init__(section_, source_, lineno_);
    }
    void *__init__(str *section_, str *source_=NULL, __ss_int lineno_=-1);
};

extern class_ *cl_DuplicateOptionError;
class DuplicateOptionError : public Error {
/**
Raised when an option is found more than once in a single file,
string or dict while parsing.
*/
public:
    str *section;
    str *option;
    str *source;
    __ss_int lineno;

    DuplicateOptionError() {}
    DuplicateOptionError(str *section_, str *option_, str *source_=NULL, __ss_int lineno_=-1) {
        this->__class__ = cl_DuplicateOptionError;
        __init__(section_, option_, source_, lineno_);
    }
    void *__init__(str *section_, str *option_, str *source_=NULL, __ss_int lineno_=-1);
};

extern class_ *cl_NoOptionError;
class NoOptionError : public Error {
/**
A requested option was not found.
*/
public:
    str *option;
    str *section;

    NoOptionError() {}
    NoOptionError(str *option_, str *section_) {
        this->__class__ = cl_NoOptionError;
        __init__(option_, section_);
    }
    void *__init__(str *option_, str *section_);
};

extern class_ *cl_InterpolationError;
class InterpolationError : public Error {
/**
Base class for interpolation-related exceptions.
*/
public:

    str *section;
    str *option;

    InterpolationError() {}
    InterpolationError(str *option_, str *section_, str *msg) {
        this->__class__ = cl_InterpolationError;
        __init__(option_, section_, msg);
    }
    void *__init__(str *option_, str *section_, str *msg);
};

extern class_ *cl_InterpolationMissingOptionError;
class InterpolationMissingOptionError : public InterpolationError {
/**
A string substitution required a setting which was not available.
*/
public:
    str *reference;

    InterpolationMissingOptionError() {}
    InterpolationMissingOptionError(str *option_, str *section_, str *rawval, str *reference_) {
        this->__class__ = cl_InterpolationMissingOptionError;
        __init__(option_, section_, rawval, reference_);
    }
    void *__init__(str *option_, str *section_, str *rawval, str *reference_);
};

extern class_ *cl_InterpolationSyntaxError;
class InterpolationSyntaxError : public InterpolationError {
/**
Raised when the source text into which substitutions are made
does not conform to the required syntax.
*/
public:

    InterpolationSyntaxError() { this->__class__ = cl_InterpolationSyntaxError; }
    InterpolationSyntaxError(str *option_, str *section_, str *msg) {
        this->__class__ = cl_InterpolationSyntaxError;
        InterpolationError::__init__(option_, section_, msg);
    }
};

extern class_ *cl_InterpolationDepthError;
class InterpolationDepthError : public InterpolationError {
/**
Raised when substitutions are nested too deeply.
*/
public:

    InterpolationDepthError() {}
    InterpolationDepthError(str *option_, str *section_, str *rawval) {
        this->__class__ = cl_InterpolationDepthError;
        __init__(option_, section_, rawval);
    }
    void *__init__(str *option_, str *section_, str *rawval);
};

extern class_ *cl_ParsingError;
class ParsingError : public Error {
/**
Raised when a configuration file does not follow legal syntax.
*/
public:
    list<tuple2<__ss_int, str *> *> *errors;
    str *source;    /* CPython 3.12+ name (the old 'filename' attribute is gone) */

    ParsingError() {}
    ParsingError(str *source_) {
        this->__class__ = cl_ParsingError;
        __init__(source_);
    }
    void *__init__(str *source_);
    void *append(__ss_int lineno, str *line);

    /* Merge the errors of any number of other ParsingErrors into this one
       and return self (CPython 3.13+). Templated on the list type so a
       list of a ParsingError subclass (e.g. MissingSectionHeaderError)
       also works despite template invariance. */
    template<class L> ParsingError *combine(L *others) {
        __ss_int n = len(others);
        for (__ss_int i = 0; i < n; i++) {
            ParsingError *other = others->__getitem__(i);
            __ss_int m = len(other->errors);
            for (__ss_int j = 0; j < m; j++) {
                tuple2<__ss_int, str *> *t = (other->errors)->__getitem__(j);
                this->append(t->__getfirst__(), t->__getsecond__());
            }
        }
        return this;
    }
};

extern class_ *cl_MissingSectionHeaderError;
class MissingSectionHeaderError : public ParsingError {
/**
Raised when a key-value pair is found before any section header.
*/
public:
    __ss_int lineno;
    str *line;

    MissingSectionHeaderError() {}
    MissingSectionHeaderError(str *source_, __ss_int lineno_, str *line_) {
        this->__class__ = cl_MissingSectionHeaderError;
        __init__(source_, lineno_, line_);
    }
    void *__init__(str *source_, __ss_int lineno_, str *line_);
};

extern class_ *cl_MultilineContinuationError;
class MultilineContinuationError : public ParsingError {
/**
Raised when a key without value (allow_no_value=True) is followed by
an indented continuation line (CPython 3.13+).
*/
public:
    __ss_int lineno;
    str *line;

    MultilineContinuationError() {}
    MultilineContinuationError(str *source_, __ss_int lineno_, str *line_) {
        this->__class__ = cl_MultilineContinuationError;
        __init__(source_, lineno_, line_);
    }
    void *__init__(str *source_, __ss_int lineno_, str *line_);
};

extern class_ *cl_InvalidWriteError;
class InvalidWriteError : public Error {
/**
Raised by write() for a key the parser would read back differently:
one that looks like a section header, or one containing a delimiter
(CPython 3.14+).
*/
public:
    InvalidWriteError() {}
    InvalidWriteError(str *msg) {
        this->__class__ = cl_InvalidWriteError;
        Error::__init__(msg);
    }
};

extern class_ *cl_Interpolation;
class Interpolation : public pyobj {
/**
Dummy interpolation that passes the value through with no changes.
Also the base class the parsers dispatch through: RawConfigParser
holds an Interpolation* and calls before_get()/before_set() on it,
so the interpolation style is selected per instance (matching
CPython) instead of per class.
*/
public:
    Interpolation() { this->__class__ = cl_Interpolation; }
    virtual str *before_get(RawConfigParser *parser, str *section, str *option, str *value, dict<str *, str *> *defaults);
    virtual str *before_set(RawConfigParser *parser, str *section, str *option, str *value);
    virtual str *before_read(RawConfigParser *parser, str *section, str *option, str *value);
    virtual str *before_write(RawConfigParser *parser, str *section, str *option, str *value);
    virtual ~Interpolation() {}
};

extern class_ *cl_BasicInterpolation;
class BasicInterpolation : public Interpolation {
/**
%(name)s interpolation, as used by ConfigParser by default. Ported
from CPython's BasicInterpolation._interpolate_some(), so (unlike
the old ConfigParser::_interpolate() it replaces) a bare '%' that is
not part of '%%' or '%(name)s' raises InterpolationSyntaxError even
when the value contains no reference at all.
*/
public:
    static __re__::Pattern *_KEYCRE;

    BasicInterpolation() { this->__class__ = cl_BasicInterpolation; }
    str *before_get(RawConfigParser *parser, str *section, str *option, str *value, dict<str *, str *> *defaults);
    str *before_set(RawConfigParser *parser, str *section, str *option, str *value);
    void _interpolate_some(RawConfigParser *parser, str *option, list<str *> *accum, str *rest, str *section, dict<str *, str *> *map, __ss_int depth);
};

extern class_ *cl_ExtendedInterpolation;
class ExtendedInterpolation : public Interpolation {
/**
${option} / ${section:option} interpolation, in the style of
zc.buildout. Enables interpolation between sections.
*/
public:
    static __re__::Pattern *_KEYCRE;

    ExtendedInterpolation() { this->__class__ = cl_ExtendedInterpolation; }
    str *before_get(RawConfigParser *parser, str *section, str *option, str *value, dict<str *, str *> *defaults);
    str *before_set(RawConfigParser *parser, str *section, str *option, str *value);
    void _interpolate_some(RawConfigParser *parser, str *option, list<str *> *accum, str *rest, str *section, dict<str *, str *> *map, __ss_int depth);
};

extern class_ *cl_RawConfigParser;
class RawConfigParser : public pyiter<str *> {
public:
    /* CPython's class-level BOOLEAN_STATES dict; every instance's
       BOOLEAN_STATES member points at the one shared _boolean_states
       dict, so in-place additions are seen by all parsers, as in CPython */
    static dict<str *, __ss_bool> *_boolean_states;
    dict<str *, __ss_bool> *BOOLEAN_STATES;
    static __re__::Pattern *SECTCRE;
    static __re__::Pattern *OPTCRE;
    static __re__::Pattern *OPTCRE_NV;
    static __re__::Pattern *NONSPACECRE;

    dict<str *, str *> *_defaults;
    dict<str *, dict<str *, str *> *> *_sections;
    str *default_section;
    Interpolation *_interpolation;

    /* constructor options (CPython names) */
    tuple<str *> *_delimiters;
    tuple<str *> *_comment_prefixes;
    tuple<str *> *_inline_comment_prefixes;   /* never NULL: empty tuple for None */
    __ss_int _strict;
    __ss_int _allow_no_value;
    __ss_int _empty_lines_in_values;
    __re__::Pattern *_optcre;

    RawConfigParser() {}
    RawConfigParser(dict<str *, str *> *defaults, __ss_int allow_no_value=0, tuple<str *> *delimiters=NULL, tuple<str *> *comment_prefixes=NULL, tuple<str *> *inline_comment_prefixes=NULL, __ss_int strict=1, __ss_int empty_lines_in_values=1, str *default_section_=NULL, Interpolation *interpolation_=NULL) {
        this->__class__ = cl_RawConfigParser;
        __init__(defaults, allow_no_value, delimiters, comment_prefixes, inline_comment_prefixes, strict, empty_lines_in_values, default_section_, interpolation_);
    }
    /* class-specific default for the interpolation= constructor argument
       (Interpolation for RawConfigParser, BasicInterpolation for
       ConfigParser); resolved with a virtual call from within the derived
       class's constructor body, where the dynamic type is already the
       derived class */
    virtual Interpolation *_default_interpolation();
    virtual str *get(str *section, str *option, __ss_int raw, dict<str *, str *> *vars, str *fallback=NULL);
    /* virtual, so a C++-side subclass could keep option case (shedskin
       itself does not support subclassing lib classes) */
    virtual str *optionxform(str *optionstr);
    void *_set(str *section, str *option, str *value);
    __ss_bool has_section(str *section);
    __ss_bool remove_option(str *section, str *option);
    __ss_bool remove_section(str *section);
    void *__init__(dict<str *, str *> *defaults, __ss_int allow_no_value=0, tuple<str *> *delimiters=NULL, tuple<str *> *comment_prefixes=NULL, tuple<str *> *inline_comment_prefixes=NULL, __ss_int strict=1, __ss_int empty_lines_in_values=1, str *default_section_=NULL, Interpolation *interpolation_=NULL);
    __ss_bool has_option(str *section, str *option);
    void *write(file *fp, __ss_int space_around_delimiters=1);
    void *_write_section(file *fp, str *section_name, dict<str *, str *> *section_items, str *delimiter);
    void *_validate_key_contents(str *key);
    /* flush the multi-line accumulator of the option being parsed */
    void *_join_value(dict<str *, str *> *cursect, str *optname, list<str *> *curval);
    void *add_section(str *section);
    list<str *> *sections();
    list<str *> *read(str *filename);
    list<str *> *read(list<str *> *filenames);
    void *read_string(str *string_, str *source=NULL);
    void *read_dict(dict<str *, dict<str *, str *> *> *dictionary, str *source=NULL);
    void *read_file(file *fp, str *source=NULL);
    list<tuple2<str *, SectionProxy *> *> *items(dict<str *, str *> *vars, __ss_int raw);
    list<tuple<str *> *> *items(dict<str *, str *> *vars, __ss_int raw, str *section);
    void *_read(file *fp, str *fpname);

    /* Typed getters, matching CPython's _get_conv(): look the value up
       through the (virtual) get(), so interpolation happens for a
       ConfigParser, then convert. 'fallback' is only used when the section
       or option is missing (NoSectionError/NoOptionError); a value that is
       present but fails conversion still raises ValueError. The model marks
       'no fallback' with the __void sentinel, which the compiler passes as
       __ss_void, so D is __ss_void_struct in that case and the lookup
       errors propagate. */
    str *_get_or_null(str *section, str *option, __ss_int raw, dict<str *, str *> *vars);
    __ss_bool _to_boolean(str *v);

    template<class D> __ss_int getint(str *section, str *option, __ss_int raw, dict<str *, str *> *vars, D fallback) {
        if constexpr (std::is_same_v<D, __ss_void_struct>)
            return __int(this->get(section, option, raw, vars, NULL));
        else {
            str *v = _get_or_null(section, option, raw, vars);
            return v ? __int(v) : (__ss_int)fallback;
        }
    }
    template<class D> __ss_float getfloat(str *section, str *option, __ss_int raw, dict<str *, str *> *vars, D fallback) {
        if constexpr (std::is_same_v<D, __ss_void_struct>)
            return __float(this->get(section, option, raw, vars, NULL));
        else {
            str *v = _get_or_null(section, option, raw, vars);
            return v ? __float(v) : (__ss_float)fallback;
        }
    }
    template<class D> __ss_bool getboolean(str *section, str *option, __ss_int raw, dict<str *, str *> *vars, D fallback) {
        if constexpr (std::is_same_v<D, __ss_void_struct>)
            return _to_boolean(this->get(section, option, raw, vars, NULL));
        else {
            str *v = _get_or_null(section, option, raw, vars);
            return v ? _to_boolean(v) : ___bool(fallback);
        }
    }
    dict<str *, str *> *defaults();
    list<str *> *options(str *section);

    /* Mapping-protocol access: config['section'] / config['section']['option'].
       Lives on RawConfigParser (matching CPython) so ConfigParser inherits it
       for free -- SectionProxy calls the (virtual) get(), so interpolation
       still happens correctly for a wrapped ConfigParser instance. */
    /* defaults + section + normalized vars merged into one lookup dict
       (CPython's _unify_values); raises NoSectionError */
    dict<str *, str *> *_unify_values(str *section, dict<str *, str *> *vars);

    /* Remove a section (never the default section) and return it as a
       (section_name, section_proxy) tuple; KeyError when no section is
       left (CPython 3.x MutableMapping API) */
    tuple2<str *, SectionProxy *> *popitem();

    SectionProxy *__getitem__(str *section);
    void *__setitem__(str *section, dict<str *, str *> *value);
    void *__delitem__(str *section);
    __ss_bool __contains__(str *section);
    __ss_int __len__();
    __iter<str *> *__iter__();
};

extern class_ *cl_ConfigParser;
class ConfigParser : public RawConfigParser {
/**
Same as RawConfigParser, but with BasicInterpolation as the default
interpolation. get()/items()/set() are inherited: they dispatch
through the _interpolation member, so no overrides are needed here.
*/
public:

    ConfigParser() {}
    ConfigParser(dict<str *, str *> *defaults, __ss_int allow_no_value=0, tuple<str *> *delimiters=NULL, tuple<str *> *comment_prefixes=NULL, tuple<str *> *inline_comment_prefixes=NULL, __ss_int strict=1, __ss_int empty_lines_in_values=1, str *default_section_=NULL, Interpolation *interpolation_=NULL) {
        this->__class__ = cl_ConfigParser;
        __init__(defaults, allow_no_value, delimiters, comment_prefixes, inline_comment_prefixes, strict, empty_lines_in_values, default_section_, interpolation_);
    }
    Interpolation *_default_interpolation();
};

extern class_ *cl_SectionProxy;
class SectionProxy : public pyiter<str *> {
/**
A dict-like, write-through view onto a single section of a
RawConfigParser (or ConfigParser) instance, as returned by
config[section]. Falls back to the DEFAULT section/defaults() the
same way get()/has_option() do, and -- since it calls through the
(virtual) get() -- still interpolates correctly when wrapping a
ConfigParser.
*/
public:
    RawConfigParser *_parser;
    str *_name;

    SectionProxy() {}
    SectionProxy(RawConfigParser *parser_, str *name_) {
        this->__class__ = cl_SectionProxy;
        __init__(parser_, name_);
    }
    void *__init__(RawConfigParser *parser_, str *name_);
    list<str *> *_options();
    str *getname() { return _name; }
    RawConfigParser *getparser() { return _parser; }
    str *__repr__();
    str *get(str *option, str *fallback, __ss_int raw, dict<str *, str *> *vars);
    template<class D> __ss_int getint(str *option, D fallback, __ss_int raw, dict<str *, str *> *vars) {
        return _parser->getint(_name, option, raw, vars, fallback);
    }
    template<class D> __ss_float getfloat(str *option, D fallback, __ss_int raw, dict<str *, str *> *vars) {
        return _parser->getfloat(_name, option, raw, vars, fallback);
    }
    template<class D> __ss_bool getboolean(str *option, D fallback, __ss_int raw, dict<str *, str *> *vars) {
        return _parser->getboolean(_name, option, raw, vars, fallback);
    }
    str *__getitem__(str *key);
    void *__setitem__(str *key, str *value);
    void *__delitem__(str *key);
    __ss_bool __contains__(str *key);
    __ss_int __len__();
    __iter<str *> *__iter__();
};

void __init();

} // module namespace
#endif
