#include "getopt.hpp"

/* this is getopt.getopt, compiled to C++ from the PyPy getopt implementation; thanks! */
 
namespace __getopt__ {

str *const_0, *const_1, *const_10, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;

static inline list<str *> *list_comp_0(str *opt, list<str *> *longopts) {
    list<str *> *__7;
    int __8;
    str *o;
    list<str *> *result = new list<str *>();

    FOR_IN_SEQ(o,longopts,7,8)
        if (o->startswith(opt)) {
            result->append(o);
        }
    END_FOR

    return result;
}

/* class GetoptError */

class_ *cl_GetoptError;

GetoptError::GetoptError(str *msg, str *opt) : Exception(msg) {
    this->__class__ = cl_GetoptError;
    
    this->opt = opt;
}

void __init() {
    const_0 = new str("");
    const_1 = new str("-");
    const_2 = new str("--");
    const_3 = new str("=");
    const_4 = new str("option --%s requires argument");
    const_5 = new str("option --%s must not have an argument");
    const_6 = new str("option --%s not recognized");
    const_7 = new str("option --%s not a unique prefix");
    const_8 = new str("option -%s requires argument");
    const_9 = new str(":");
    const_10 = new str("option -%s not recognized");

    cl_GetoptError = new class_("GetoptError", 12, 12);
    
}

tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *getopt(list<str *> *args, str *shortopts, list<str *> *longopts) {
    list<tuple2<str *, str *> *> *opts;
    tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *__0, *__1;

//    throw (new GetoptError(const_7, const_7));

    opts = (new list<tuple2<str *, str *> *>());
 
    while((__bool(args) && (args->__getfast__(0))->startswith(const_1) && (!__eq(args->__getfast__(0), const_1)))) {
        if (__eq(args->__getfast__(0), const_2)) {
            args = args->__slice__(1, 1, 0, 0);
            break;
        }
        if ((args->__getfast__(0))->startswith(const_2)) {
            //TUPLE_ASSIGN2(opts,args,do_longs(opts, (args->__getfast__(0))->__slice__(1, 2, 0, 0), longopts, args->__slice__(1, 1, 0, 0)),0);
            __0 = do_longs(opts, (args->__getfast__(0))->__slice__(1, 2, 0, 0), longopts, args->__slice__(1, 1, 0, 0));
            opts = __0->__getfirst__();
            args = __0->__getsecond__();

        }
        else {
            //TUPLE_ASSIGN2(opts,args,do_shorts(opts, (args->__getfast__(0))->__slice__(1, 1, 0, 0), shortopts, args->__slice__(1, 1, 0, 0)),1);
            __1 = do_shorts(opts, (args->__getfast__(0))->__slice__(1, 1, 0, 0), shortopts, args->__slice__(1, 1, 0, 0));
            opts = __1->__getfirst__();
            args = __1->__getsecond__();
        }
    }
    return (new tuple2<list<tuple2<str *, str *> *> *, list<str *> *>(2, opts, args));
}

tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *do_longs(list<tuple2<str *, str *> *> *opts, str *opt, list<str *> *longopts, list<str *> *args) {
    list<str *> *__6;
    str *__2, *__3, *__5, *optarg;
    int has_arg, i;
    tuple2<int, str *> *__4;

    if (opt->__contains__(const_3)) {
        i = opt->index(const_3);
        __2 = opt->__slice__(2, 0, i, 0);
        __3 = opt->__slice__(1, (i+1), 0, 0);
        opt = __2;
        optarg = __3;
    }
    else {
        optarg = const_0;
    }
    //TUPLE_ASSIGN2(has_arg,opt,long_has_args(opt, longopts),4);

    __4 = long_has_args(opt, longopts);
    has_arg = __4->__getfirst__();
    opt = __4->__getsecond__();

    if (has_arg) {
        if ((optarg==0)) {
            if ((!__bool(args))) {
                throw ((new GetoptError(__mod(const_4, opt),opt)));
            }
            __5 = args->__getfast__(0);
            __6 = args->__slice__(1, 1, 0, 0);
            optarg = __5;
            args = __6;
        }
    }
    else if (__bool(optarg)) {
        throw ((new GetoptError(__mod(const_5, opt),opt)));
    }
    opts->append((new tuple2<str *, str *>(2, __add(const_2, opt), optarg)));
    return (new tuple2<list<tuple2<str *, str *> *> *, list<str *> *>(2, opts, args));
}

tuple2<int, str *> *long_has_args(str *opt, list<str *> *longopts) {
    list<str *> *possibilities;
    str *unique_match;
    int has_arg;

    possibilities = list_comp_0(opt, longopts);
    if ((!__bool(possibilities))) {
        throw ((new GetoptError(__mod(const_6, opt),opt)));
    }
    if (possibilities->__contains__(opt)) {
        return (new tuple2<int, str *>(2, 0, opt));
    }
    else if (possibilities->__contains__(__add(opt, const_3))) {
        return (new tuple2<int, str *>(2, 1, opt));
    }
    if ((len(possibilities)>1)) {
        throw ((new GetoptError(__mod(const_7, opt),opt)));
    }
    ASSERT((len(possibilities)==1), 0);
    unique_match = possibilities->__getfast__(0);
    has_arg = unique_match->endswith(const_3);
    if (has_arg) {
        unique_match = unique_match->__slice__(2, 0, -1, 0);
    }
    return (new tuple2<int, str *>(2, has_arg, unique_match));
}

tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *do_shorts(list<tuple2<str *, str *> *> *opts, str *optstring, str *shortopts, list<str *> *args) {
    list<str *> *__12;
    str *__10, *__11, *__13, *__9, *opt, *optarg;


    while((!__eq(optstring, const_0))) {
        __9 = optstring->__getitem__(0);
        __10 = optstring->__slice__(1, 1, 0, 0);
        opt = __9;
        optstring = __10;
        if (short_has_arg(opt, shortopts)) {
            if (__eq(optstring, const_0)) {
                if ((!__bool(args))) {
                    throw ((new GetoptError(__mod(const_8, opt),opt)));
                }
                __11 = args->__getfast__(0);
                __12 = args->__slice__(1, 1, 0, 0);
                optstring = __11;
                args = __12;
            }
            __13 = optstring;
            optarg = __13;
            optstring = const_0;
        }
        else {
            optarg = const_0;
        }
        opts->append((new tuple2<str *, str *>(2, __add(const_1, opt), optarg)));
    }
    return (new tuple2<list<tuple2<str *, str *> *> *, list<str *> *>(2, opts, args));
}

int short_has_arg(str *opt, str *shortopts) {
    str *__16;
    int __14, __15, i;


    FAST_FOR(i,0,len(shortopts),1,14,15)
        if ((__eq(opt, (__16=shortopts->__getitem__(i)))&&(!__eq(__16, const_9)))) {
            return shortopts->startswith(const_9, (i+1));
        }
    END_FOR

    throw ((new GetoptError(__mod(const_10, opt),opt)));
    return 0;
}

} // module namespace

