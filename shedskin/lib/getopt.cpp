#include "getopt.hpp"

/**
Parser for command line options.

This module helps scripts to parse the command line arguments in
sys.argv.  It supports the same conventions as the Unix getopt()
function (including the special meanings of arguments of the form `-'
and `--').  Long options similar to those supported by GNU software
may be used as well via an optional third argument.  This module
provides two functions and an exception:

getopt() -- Parse command line options
gnu_getopt() -- Like getopt(), but allow option and non-option arguments
to be intermixed.
GetoptError -- exception (class) raised with 'opt' attribute, which is the
option involved with the exception.
*/

namespace __getopt__ {

str *const_0, *const_1, *const_10, *const_11, *const_12, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;

str *__name__;
__ss_int __18;

static inline list<str *> *list_comp_0(str *opt, pyiter<str *> *longopts) {
    list<str *> *result = new list<str *>();
    str *o;
    pyiter<str *>::for_in_loop __3;
    int __2;
    pyiter<str *> *__1;
    FOR_IN_NEW(o,longopts,1,2,3)
        if (o->startswith(opt))
            result->append(o);
    END_FOR
    return result;
}

/**
class GetoptError
*/

class_ *cl_GetoptError;

GetoptError::GetoptError(str *msg, str *opt) {
    this->__class__ = cl_GetoptError;

    this->msg = msg;
    if(opt)
        this->opt = opt;
    else
        this->opt = const_0;
}

void __init() {
    const_0 = new str("");
    const_1 = new str("-");
    const_2 = new str("--");
    const_3 = new str("+");
    const_4 = new str("POSIXLY_CORRECT");
    const_5 = new str("=");
    const_6 = new str("option --%s requires argument");
    const_7 = new str("option --%s must not have an argument");
    const_8 = new str("option --%s not recognized");
    const_9 = new str("option --%s not a unique prefix");
    const_10 = new str("option -%s requires argument");
    const_11 = new str(":");
    const_12 = new str("option -%s not recognized");

    __name__ = new str("getopt");

    cl_GetoptError = new class_("GetoptError", 15, 15);

}

tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *getopt(list<str *> *args, str *shortopts) {
    return getopt(args, shortopts, new list<str *>());
}
tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *getopt(list<str *> *args, str *shortopts, str *longopts) {
    return getopt(args, shortopts, new list<str *>(1, longopts));
}

tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *getopt(list<str *> *args, str *shortopts, pyiter<str *> *longopts) {
    /**
    getopt(args, options[, long_options]) -> opts, args

    Parses command line options and parameter list.  args is the
    argument list to be parsed, without the leading reference to the
    running program.  Typically, this means "sys.argv[1:]".  shortopts
    is the string of option letters that the script wants to
    recognize, with options that require an argument followed by a
    colon (i.e., the same format that Unix getopt() uses).  If
    specified, longopts is a list of strings with the names of the
    long options which should be supported.  The leading '--'
    characters should not be included in the option name.  Options
    which require an argument should be followed by an equal sign
    ('=').

    The return value consists of two elements: the first is a list of
    (option, value) pairs; the second is the list of program arguments
    left after the option list was stripped (this is a trailing slice
    of the first argument).  Each option-and-value pair returned has
    the option as its first element, prefixed with a hyphen (e.g.,
    '-x'), and the option argument as its second element, or an empty
    string if the option has no argument.  The options occur in the
    list in the same order in which they were found, thus allowing
    multiple occurrences.  Long and short options may be mixed.

    */
    list<str *> *__0, *__1, *__2;
    list<tuple2<str *, str *> *> *opts;
    tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *__3, *__4;

    opts = (new list<tuple2<str *, str *> *>());
    longopts = new list<str *>(longopts);

    while((___bool(args) && (args->__getfast__(0))->startswith(const_1) && __ne(args->__getfast__(0), const_1))) {
        if (__eq(args->__getfast__(0), const_2)) {
            args = args->__slice__(1, 1, 0, 0);
            break;
        }
        if ((args->__getfast__(0))->startswith(const_2)) {
            __3 = do_longs(opts, (args->__getfast__(0))->__slice__(1, 2, 0, 0), longopts, args->__slice__(1, 1, 0, 0));
            opts = __3->__getfirst__();
            args = __3->__getsecond__();
        }
        else {
            __4 = do_shorts(opts, (args->__getfast__(0))->__slice__(1, 1, 0, 0), shortopts, args->__slice__(1, 1, 0, 0));
            opts = __4->__getfirst__();
            args = __4->__getsecond__();
        }
    }
    return (new tuple2<list<tuple2<str *, str *> *> *, list<str *> *>(2, opts, args));
}

tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *gnu_getopt(list<str *> *args, str *shortopts) {
    return gnu_getopt(args, shortopts, new list<str *>());
}
tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *gnu_getopt(list<str *> *args, str *shortopts, str *longopts) {
    return gnu_getopt(args, shortopts, new list<str *>(1, longopts));
}

tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *gnu_getopt(list<str *> *args, str *shortopts, pyiter<str *> *longopts) {
    /**
    getopt(args, options[, long_options]) -> opts, args

    This function works like getopt(), except that GNU style scanning
    mode is used by default. This means that option and non-option
    arguments may be intermixed. The getopt() function stops
    processing options as soon as a non-option argument is
    encountered.

    If the first character of the option string is `+', or if the
    environment variable POSIXLY_CORRECT is set, then option
    processing stops as soon as a non-option argument is encountered.

    */
    list<str *> *prog_args;
    list<tuple2<str *, str *> *> *opts;
    __ss_int all_options_first;
    tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *__5, *__6;

    opts = (new list<tuple2<str *, str *> *>());
    prog_args = (new list<str *>());
    longopts = new list<str *>(longopts);
    if (shortopts->startswith(const_3)) {
        shortopts = shortopts->__slice__(1, 1, 0, 0);
        all_options_first = 1;
    }
    else if (___bool((__os__::__ss_environ)->get(const_4))) {
        all_options_first = 1;
    }
    else {
        all_options_first = 0;
    }

    while(___bool(args)) {
        if (__eq(args->__getfast__(0), const_2)) {
            prog_args = prog_args->__iadd__(args->__slice__(1, 1, 0, 0));
            break;
        }
        if (__eq((args->__getfast__(0))->__slice__(2, 0, 2, 0), const_2)) {
            __5 = do_longs(opts, (args->__getfast__(0))->__slice__(1, 2, 0, 0), longopts, args->__slice__(1, 1, 0, 0));
            opts = __5->__getfirst__();
            args = __5->__getsecond__();
        }
        else if (__eq((args->__getfast__(0))->__slice__(2, 0, 1, 0), const_1)) {
            __6 = do_shorts(opts, (args->__getfast__(0))->__slice__(1, 1, 0, 0), shortopts, args->__slice__(1, 1, 0, 0));
            opts = __6->__getfirst__();
            args = __6->__getsecond__();
        }
        else {
            if (all_options_first) {
                prog_args = prog_args->__iadd__(args);
                break;
            }
            else {
                prog_args->append(args->__getfast__(0));
                args = args->__slice__(1, 1, 0, 0);
            }
        }
    }
    return (new tuple2<list<tuple2<str *, str *> *> *, list<str *> *>(2, opts, prog_args));
}

tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *do_longs(list<tuple2<str *, str *> *> *opts, str *opt, pyiter<str *> *longopts, list<str *> *args) {
    list<str *> *__13;
    str *__12, *__14, *__15, *__8, *__9, *optarg;
    __ss_int __10, i;
    __ss_bool has_arg;
    tuple2<__ss_bool, str *> *__11;

    try {
        __10 = 0;
        i = opt->index(const_5);
        __10 = 1;
    } catch (ValueError *) {
        optarg = 0;
    }
    if(__10) { // else
        __8 = opt->__slice__(2, 0, i, 0);
        __9 = opt->__slice__(1, (i+1), 0, 0);
        opt = __8;
        optarg = __9;
    }
    __11 = long_has_args(opt, longopts);
    has_arg = __11->__getfirst__();
    opt = __11->__getsecond__();
    if (has_arg) {
        if ((optarg==0)) {
            if ((!___bool(args))) {
                throw ((new GetoptError(__modct(const_6, 1, opt),opt)));
            }
            __12 = args->__getfast__(0);
            __13 = args->__slice__(1, 1, 0, 0);
            optarg = __12;
            args = __13;
        }
    }
    else if (___bool(optarg)) {
        throw ((new GetoptError(__modct(const_7, 1, opt),opt)));
    }
    opts->append((new tuple2<str *, str *>(2, (const_2)->__add__(opt), __OR(optarg, const_0, 14))));
    return (new tuple2<list<tuple2<str *, str *> *> *, list<str *> *>(2, opts, args));
}

tuple2<__ss_bool, str *> *long_has_args(str *opt, pyiter<str *> *longopts) {
    list<str *> *possibilities;
    str *unique_match;
    __ss_bool has_arg;

    possibilities = list_comp_0(opt, longopts);
    if ((!___bool(possibilities))) {
        throw ((new GetoptError(__modct(const_8, 1, opt),opt)));
    }
    if (possibilities->__contains__(opt)) {
        return (new tuple2<__ss_bool, str *>(2, False, opt));
    }
    else if (possibilities->__contains__(opt->__add__(const_5))) {
        return (new tuple2<__ss_bool, str *>(2, True, opt));
    }
    if ((len(possibilities)>1)) {
        throw ((new GetoptError(__modct(const_9, 1, opt),opt)));
    }
    ASSERT((len(possibilities)==1), 0);
    unique_match = possibilities->__getfast__(0);
    has_arg = __mbool(unique_match->endswith(const_5));
    if (has_arg) {
        unique_match = unique_match->__slice__(2, 0, -1, 0);
    }
    return (new tuple2<__ss_bool, str *>(2, has_arg, unique_match));
}

tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *do_shorts(list<tuple2<str *, str *> *> *opts, str *optstring, str *shortopts, list<str *> *args) {
    list<str *> *__22;
    str *__19, *__20, *__21, *__23, *opt, *optarg;


    while(__ne(optstring, const_0)) {
        __19 = optstring->__getitem__(0);
        __20 = optstring->__slice__(1, 1, 0, 0);
        opt = __19;
        optstring = __20;
        if (short_has_arg(opt, shortopts)) {
            if (__eq(optstring, const_0)) {
                if ((!___bool(args))) {
                    throw ((new GetoptError(__modct(const_10, 1, opt),opt)));
                }
                __21 = args->__getfast__(0);
                __22 = args->__slice__(1, 1, 0, 0);
                optstring = __21;
                args = __22;
            }
            __23 = optstring;
            optarg = __23;
            optstring = const_0;
        }
        else {
            optarg = const_0;
        }
        opts->append((new tuple2<str *, str *>(2, (const_1)->__add__(opt), optarg)));
    }
    return (new tuple2<list<tuple2<str *, str *> *> *, list<str *> *>(2, opts, args));
}

__ss_bool short_has_arg(str *opt, str *shortopts) {
    str *__26;
    __ss_int __24, __25, i;


    FAST_FOR(i,0,len(shortopts),1,24,25)
        if ((__eq(opt, (__26=shortopts->__getitem__(i)))&&__ne(__26, const_11))) {
            return __mbool(shortopts->startswith(const_11, (i+1)));
        }
    END_FOR

    throw ((new GetoptError(__modct(const_12, 1, opt),opt)));
}

} // module namespace

