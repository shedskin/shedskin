#include "builtin.hpp"
#include "wop.hpp"

namespace __wop__ {


file *__file;
__ss_int __void, a, b;
str *__name__;
void *x;


static inline __ss_int  list_comp_0();
static inline __ss_int  list_comp_1();
static inline __ss_int  list_comp_2();
static inline __ss_int  list_comp_3();
static inline __ss_int  list_comp_4();
static inline __ss_int  list_comp_5();

static inline __ss_int  list_comp_0() {
    __ss_int __0, __1, x;

    __ss_int __ss_result = __zero<__ss_int >();

    FAST_FOR(x,0,__ss_int(10LL),1,0,1)
        __ss_result = __add(__ss_result, (__ss_int(2LL)*x));
    END_FOR

    return __ss_result;
}

static inline __ss_int  list_comp_1() {
    __ss_int __2, __3, x;

    __ss_int __ss_result = __zero<__ss_int >();

    FAST_FOR(x,0,__ss_int(5LL),1,2,3)
        __ss_result = __add(__ss_result, (x+__ss_int(1LL)));
    END_FOR

    return __ss_result;
}

static inline __ss_int  list_comp_2() {
    __ss_int __4, __5, x;

    __ss_int __ss_result;

    bool __ss_first = true;

    FAST_FOR(x,0,__ss_int(10LL),1,4,5)
        if (__ss_first) {
            __ss_result = (__ss_int(2LL)*x);
            __ss_first = false;
        } else {
            __ss_result = ___min(2, __ss_void, 0, __ss_result, (__ss_int(2LL)*x));
        }
    END_FOR

    if (__ss_first) throw new ValueError(new str("min() arg is an empty sequence"));
    return __ss_result;
}

static inline __ss_int  list_comp_3() {
    __ss_int __6, __7, x;

    __ss_int __ss_result;

    bool __ss_first = true;

    FAST_FOR(x,0,__ss_int(5LL),1,6,7)
        if (__ss_first) {
            __ss_result = (x+__ss_int(1LL));
            __ss_first = false;
        } else {
            __ss_result = ___min(2, __ss_void, 0, __ss_result, (x+__ss_int(1LL)));
        }
    END_FOR

    if (__ss_first) throw new ValueError(new str("min() arg is an empty sequence"));
    return __ss_result;
}

static inline __ss_int  list_comp_4() {
    __ss_int __8, __9, x;

    __ss_int __ss_result;

    bool __ss_first = true;

    FAST_FOR(x,0,__ss_int(10LL),1,8,9)
        if (__ss_first) {
            __ss_result = (__ss_int(2LL)*x);
            __ss_first = false;
        } else {
            __ss_result = ___max(2, __ss_void, 0, __ss_result, (__ss_int(2LL)*x));
        }
    END_FOR

    if (__ss_first) throw new ValueError(new str("max() arg is an empty sequence"));
    return __ss_result;
}

static inline __ss_int  list_comp_5() {
    __ss_int __10, __11, x;

    __ss_int __ss_result;

    bool __ss_first = true;

    FAST_FOR(x,0,__ss_int(5LL),1,10,11)
        if (__ss_first) {
            __ss_result = (x+__ss_int(1LL));
            __ss_first = false;
        } else {
            __ss_result = ___max(2, __ss_void, 0, __ss_result, (x+__ss_int(1LL)));
        }
    END_FOR

    if (__ss_first) throw new ValueError(new str("max() arg is an empty sequence"));
    return __ss_result;
}

void __init() {
    __name__ = new str("__main__");


    a = list_comp_0();
    print(__wop__::a);
    b = list_comp_1();
    print(__wop__::b);
    a = list_comp_2();
    print(__wop__::a);
    b = list_comp_3();
    print(__wop__::b);
    a = list_comp_4();
    print(__wop__::a);
    b = list_comp_5();
    print(__wop__::b);
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __shedskin__::__start(__wop__::__init);
}
