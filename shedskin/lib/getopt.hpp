#ifndef __GETOPT_HPP
#define __GETOPT_HPP

#include "builtin.hpp"
#include "sys.hpp"
#include "os/__init__.hpp"

using namespace __shedskin__;
namespace __getopt__ {

extern str *const_0, *const_1, *const_10, *const_11, *const_12, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;

class GetoptError;

extern str *__name__;
extern __ss_int __18;

extern class_ *cl_GetoptError;
class GetoptError : public Exception {
public:
    str *opt;

    GetoptError(str *msg, str *opt=0);
};


extern str * __name__;
void __init();

tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *getopt(list<str *> *args, str *shortopts, pyiter<str *> *longopts);
tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *getopt(list<str *> *args, str *shortopts, str *longopts);
tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *getopt(list<str *> *args, str *shortopts);

tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *gnu_getopt(list<str *> *args, str *shortopts, pyiter<str *> *longopts);
tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *gnu_getopt(list<str *> *args, str *shortopts, str *longopts);
tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *gnu_getopt(list<str *> *args, str *shortopts);

tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *do_longs(list<tuple2<str *, str *> *> *opts, str *opt, pyiter<str *> *longopts, list<str *> *args);
tuple2<__ss_bool, str *> *long_has_args(str *opt, pyiter<str *> *longopts);
tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *do_shorts(list<tuple2<str *, str *> *> *opts, str *optstring, str *shortopts, list<str *> *args);
__ss_bool short_has_arg(str *opt, str *shortopts);

typedef GetoptError error;

} // module namespace
#endif
