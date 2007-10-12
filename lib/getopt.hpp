#ifndef __GETOPT_HPP
#define __GETOPT_HPP

#include "os/__init__.hpp"
#include "builtin.hpp"

using namespace __shedskin__;
namespace __getopt__ {

class GetoptError;

extern class_ *cl_GetoptError;
class GetoptError : public Exception {
public:
    str *opt;

    GetoptError(str *msg, str *opt);
};


void __init();
tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *getopt(list<str *> *args, str *shortopts, list<str *> *longopts);
tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *do_longs(list<tuple2<str *, str *> *> *opts, str *opt, list<str *> *longopts, list<str *> *args);
tuple2<int, str *> *long_has_args(str *opt, list<str *> *longopts);
tuple2<list<tuple2<str *, str *> *> *, list<str *> *> *do_shorts(list<tuple2<str *, str *> *> *opts, str *optstring, str *shortopts, list<str *> *args);
int short_has_arg(str *opt, str *shortopts);

} // module namespace
#endif
