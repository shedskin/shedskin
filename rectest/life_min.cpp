#include "builtin.hpp"
#include "collections.hpp"
#include "life_min.hpp"

namespace __life_min__ {

using __collections__::defaultdict;

file *__file;
__ss_int __3, __void, value;
str *__name__;
__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *board;
tuple<__ss_int> *pos;
tuple2<tuple<__ss_int> *, __ss_int> *__0;
list<tuple2<tuple<__ss_int> *, __ss_int> *> *__1;
__iter<tuple2<tuple<__ss_int> *, __ss_int> *> *__2;
list<tuple2<tuple<__ss_int> *, __ss_int> *>::for_in_loop __4;


static inline __ss_int __lambda0__();
static inline __ss_int __lambda1__();

static inline __ss_int __lambda0__() {
    return __int();
}

static inline __ss_int __lambda1__() {
    return __int();
}

__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *snext(__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *board) {
    __collections__::defaultdict<tuple<__ss_int> *, __ss_int> *__ss_new;

    __ss_new = (new __collections__::defaultdict<tuple<__ss_int> *, __ss_int>(__lambda0__));
    __ss_new->__setitem__((__ss_tuple_int(2,__ss_int(0LL),__ss_int(0LL))), __ss_int(0LL));
    return __ss_new;
}

void __init() {
    __name__ = new str("__main__");


    board = (new __collections__::defaultdict<tuple<__ss_int> *, __ss_int>(__lambda1__));

    FOR_IN(__0,(new list<tuple2<tuple<__ss_int> *, __ss_int> *>(1,(new tuple2<tuple<__ss_int> *, __ss_int>(2,(__ss_tuple_int(2,__ss_int(0LL),__ss_int(0LL))),__ss_int(0LL))))),1,3,4)
        __0 = __0;
        __SS_UNPACK_CHECK(__0, 2);
        pos = __0->__getfirst__();
        value = __0->__getsecond__();
        __life_min__::board->__setitem__(__life_min__::pos, __ss_int(0LL));
    END_FOR

    board = snext(__life_min__::board);
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __collections__::__init();
    __shedskin__::__start(__life_min__::__init);
}
