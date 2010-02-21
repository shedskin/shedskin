#ifndef __CONFIGPARSER_HPP
#define __CONFIGPARSER_HPP

#include "builtin.hpp"
#include "re.hpp"

using namespace __shedskin__;
namespace __ConfigParser__ {

extern tuple2<str *, str *> *const_2;
extern str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_26, *const_27, *const_28, *const_29, *const_3, *const_30, *const_31, *const_32, *const_33, *const_34, *const_35, *const_36, *const_37, *const_38, *const_39, *const_4, *const_40, *const_41, *const_42, *const_43, *const_44, *const_45, *const_46, *const_47, *const_48, *const_49, *const_5, *const_50, *const_51, *const_52, *const_53, *const_6, *const_7, *const_8, *const_9;

class Error;
class NoSectionError;
class DuplicateSectionError;
class NoOptionError;
class InterpolationError;
class InterpolationMissingOptionError;
class InterpolationSyntaxError;
class InterpolationDepthError;
class ParsingError;
class MissingSectionHeaderError;
class RawConfigParser;
class ConfigParser;

extern list<str *> *__all__;
extern str *DEFAULTSECT, *__name__;
extern int MAX_INTERPOLATION_DEPTH;

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
    int __init__(str *msg);
};

extern class_ *cl_NoSectionError;
class NoSectionError : public Error {
/**
Raised when no section matches a requested option.
*/
public:
    str *section;

    NoSectionError() {}
    NoSectionError(str *section) {
        this->__class__ = cl_NoSectionError;
        __init__(section);
    }
    int __init__(str *section);
};

extern class_ *cl_DuplicateSectionError;
class DuplicateSectionError : public Error {
/**
Raised when a section is multiply-created.
*/
public:
    str *section;

    DuplicateSectionError() {}
    DuplicateSectionError(str *section) {
        this->__class__ = cl_DuplicateSectionError;
        __init__(section);
    }
    int __init__(str *section);
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
    NoOptionError(str *option, str *section) {
        this->__class__ = cl_NoOptionError;
        __init__(option, section);
    }
    int __init__(str *option, str *section);
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
    InterpolationError(str *option, str *section, str *msg) {
        this->__class__ = cl_InterpolationError;
        __init__(option, section, msg);
    }
    int __init__(str *option, str *section, str *msg);
};

extern class_ *cl_InterpolationMissingOptionError;
class InterpolationMissingOptionError : public InterpolationError {
/**
A string substitution required a setting which was not available.
*/
public:
    str *reference;

    InterpolationMissingOptionError() {}
    InterpolationMissingOptionError(str *option, str *section, str *rawval, str *reference) {
        this->__class__ = cl_InterpolationMissingOptionError;
        __init__(option, section, rawval, reference);
    }
    int __init__(str *option, str *section, str *rawval, str *reference);
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
    InterpolationDepthError(str *option, str *section, str *rawval) {
        this->__class__ = cl_InterpolationDepthError;
        __init__(option, section, rawval);
    }
    int __init__(str *option, str *section, str *rawval);
};

extern class_ *cl_ParsingError;
class ParsingError : public Error {
/**
Raised when a configuration file does not follow legal syntax.
*/
public:
    list<tuple2<int, str *> *> *errors;
    str *filename;

    ParsingError() {}
    ParsingError(str *filename) {
        this->__class__ = cl_ParsingError;
        __init__(filename);
    }
    int __init__(str *filename);
    int append(int lineno, str *line);
};

extern class_ *cl_MissingSectionHeaderError;
class MissingSectionHeaderError : public ParsingError {
/**
Raised when a key-value pair is found before any section header.
*/
public:
    int lineno;
    str *line;

    MissingSectionHeaderError() {}
    MissingSectionHeaderError(str *filename, int lineno, str *line) {
        this->__class__ = cl_MissingSectionHeaderError;
        __init__(filename, lineno, line);
    }
    int __init__(str *filename, int lineno, str *line);
};

extern class_ *cl_RawConfigParser;
class RawConfigParser : public pyobj {
public:
    static dict<str *, int> *_boolean_states;
    static __re__::re_object *SECTCRE;
    static __re__::re_object *OPTCRE;

    dict<str *, str *> *_defaults;
    dict<str *, dict<str *, str *> *> *_sections;

    RawConfigParser() {}
    RawConfigParser(dict<str *, str *> *defaults) {
        this->__class__ = cl_RawConfigParser;
        __init__(defaults);
    }
    virtual str *get(str *section, str *option, int raw, dict<str *, str *> *vars);
    str *optionxform(str *optionstr);
    double getfloat(str *section, str *option);
    void *_set(str *section, str *option, str *value);
    __ss_bool has_section(str *section);
    int remove_option(str *section, str *option);
    int remove_section(str *section);
    int __init__(dict<str *, str *> *defaults);
    int has_option(str *section, str *option);
    void *write(file *fp);
    void *add_section(str *section);
    list<str *> *sections();
    list<str *> *read(str *filename);
    list<str *> *read(list<str *> *filenames);
    int getboolean(str *section, str *option);
    list<tuple2<str *, str *> *> *items(str *section);
    void *_read(file *fp, str *fpname);
    int getint(str *section, str *option);
    dict<str *, str *> *defaults();
    list<str *> *options(str *section);
};

extern class_ *cl_ConfigParser;
class ConfigParser : public RawConfigParser {
public:
    static __re__::re_object *_KEYCRE;


    ConfigParser() {}
    ConfigParser(dict<str *, str *> *defaults) {
        this->__class__ = cl_ConfigParser;
        __init__(defaults);
    }
    str *_interpolate(str *section, str *option, str *rawval, dict<str *, str *> *vars);
    str *get(str *section, str *option, int raw, dict<str *, str *> *vars);
    list<tuple2<str *, str *> *> *items(str *section, int raw, dict<str *, str *> *vars);
};

str *_interpolation_replace(__re__::match_object *match);

extern str * default_11;
extern int  default_10;
extern int  default_13;
extern int  default_23;
extern int  default_2;
extern int  default_25;
extern int  default_28;
extern int  default_1;
extern int  default_5;
extern int  default_3;
extern int  default_19;
extern int  default_29;
extern int  default_12;
extern str * default_22;
extern int  default_31;
extern int  default_30;
extern str * default_9;
extern int  default_8;
extern str * default_24;
extern str * default_14;
extern str * default_16;
extern str * default_26;
extern int  default_17;
extern str * default_18;
extern int  default_6;
extern int  default_15;
extern int  default_27;
extern str * default_20;
extern int  default_7;
extern int  default_4;
extern str * default_0;
extern int  default_21;

void __init();

} // module namespace
#endif
