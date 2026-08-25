/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __CONFIGPARSER_HPP
#define __CONFIGPARSER_HPP

#include "builtin.hpp"
#include "re.hpp"
#include "io.hpp"

using namespace __shedskin__;
namespace __configparser__ {

extern tuple2<str *, str *> *const_2;
extern str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_21, *const_22, *const_23, *const_24, *const_25, *const_26, *const_27, *const_28, *const_29, *const_3, *const_30, *const_31, *const_32, *const_33, *const_34, *const_35, *const_36, *const_37, *const_38, *const_39, *const_4, *const_40, *const_41, *const_42, *const_43, *const_44, *const_45, *const_46, *const_47, *const_48, *const_5, *const_50, *const_51, *const_52, *const_53, *const_54, *const_55, *const_56, *const_57, *const_6, *const_7, *const_8, *const_9;

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
class RawConfigParser;
class ConfigParser;

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
    str *filename;

    ParsingError() {}
    ParsingError(str *filename_) {
        this->__class__ = cl_ParsingError;
        __init__(filename_);
    }
    void *__init__(str *filename_);
    void *append(__ss_int lineno, str *line);
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
    MissingSectionHeaderError(str *filename_, __ss_int lineno_, str *line_) {
        this->__class__ = cl_MissingSectionHeaderError;
        __init__(filename_, lineno_, line_);
    }
    void *__init__(str *filename_, __ss_int lineno_, str *line_);
};

extern class_ *cl_RawConfigParser;
class RawConfigParser : public pyobj {
public:
    static dict<str *, __ss_int> *_boolean_states;
    static __re__::re_object *SECTCRE;
    static __re__::re_object *OPTCRE;

    dict<str *, str *> *_defaults;
    dict<str *, dict<str *, str *> *> *_sections;
    str *default_section;

    RawConfigParser() {}
    RawConfigParser(dict<str *, str *> *defaults, str *default_section_=NULL) {
        this->__class__ = cl_RawConfigParser;
        __init__(defaults, default_section_);
    }
    virtual str *get(str *section, str *option, __ss_int raw, dict<str *, str *> *vars, str *fallback=NULL);
    str *optionxform(str *optionstr);
    double getfloat(str *section, str *option);
    void *_set(str *section, str *option, str *value);
    __ss_bool has_section(str *section);
    __ss_bool remove_option(str *section, str *option);
    __ss_bool remove_section(str *section);
    void *__init__(dict<str *, str *> *defaults, str *default_section_=NULL);
    __ss_bool has_option(str *section, str *option);
    void *write(file *fp);
    void *add_section(str *section);
    list<str *> *sections();
    list<str *> *read(str *filename);
    list<str *> *read(list<str *> *filenames);
    void *read_string(str *string_, str *source=NULL);
    void *read_dict(dict<str *, dict<str *, str *> *> *dictionary, str *source=NULL);
    void *read_file(file *fp, str *source=NULL);
    __ss_bool getboolean(str *section, str *option);
    __iter<tuple2<str *, str *> *> *items(str *section);
    void *_read(file *fp, str *fpname);
    __ss_int getint(str *section, str *option);
    dict<str *, str *> *defaults();
    list<str *> *options(str *section);
};

extern class_ *cl_ConfigParser;
class ConfigParser : public RawConfigParser {
public:
    static __re__::re_object *_KEYCRE;


    ConfigParser() {}
    ConfigParser(dict<str *, str *> *defaults, str *default_section_=NULL) {
        this->__class__ = cl_ConfigParser;
        __init__(defaults, default_section_);
    }
    str *_interpolate(str *section, str *option, str *rawval, dict<str *, str *> *vars);
    str *get(str *section, str *option, __ss_int raw, dict<str *, str *> *vars, str *fallback=NULL);
    __iter<tuple2<str *, str *> *> *items(str *section, __ss_int raw, dict<str *, str *> *vars);
};

str *_interpolation_replace(__re__::match_object *match);

extern str * default_11;
extern __ss_int  default_10;
extern __ss_int  default_13;
extern __ss_int  default_23;
extern __ss_int  default_25;
extern __ss_int  default_28;
extern __ss_int  default_1;
extern __ss_int  default_5;
extern __ss_int  default_19;
extern __ss_int  default_29;
extern __ss_int  default_12;
extern str * default_22;
extern __ss_int  default_31;
extern __ss_int  default_30;
extern str * default_9;
extern __ss_int  default_8;
extern str * default_24;
extern str * default_14;
extern str * default_16;
extern str * default_26;
extern __ss_int  default_17;
extern str * default_18;
extern __ss_int  default_6;
extern __ss_int  default_15;
extern __ss_int  default_27;
extern str * default_20;
extern __ss_int  default_7;
extern __ss_int  default_4;
extern str * default_0;
extern __ss_int  default_21;

void __init();

} // module namespace
#endif
