#include "builtin.hpp"
#include "time.hpp"
#include "math/__init__.hpp"
#include "random.hpp"
#include "mytest.hpp"

namespace __mytest__ {

str *const_0, *const_1;


file *__file;
__ss_int __void;
str *__name__;


static inline __ss_int  list_comp_0();

static inline __ss_int  list_comp_0() {
    __ss_int __2, __3, x;

    __ss_int __ss_result = __zero<__ss_int >();

    FAST_FOR(x,0,__ss_int(64),1,2,3)
        if ((x>__ss_int(2))) {
            __ss_result = __add(__ss_result, (__ss_int(2)*x));
        }
    END_FOR

    return __ss_result;
}

void *case_a() {
    __ss_float t0;
    __ss_int __0, __1, i, s;

    t0 = __time__::time();
    s = __ss_int(0);

    FAST_FOR(i,0,__ss_int(50000000),1,0,1)
        s = (s+list_comp_0());
    END_FOR

    print(__mod6(const_0, 1, (__time__::time()-t0)));
    print(const_1);
    print(const_1);
    print(s);
    return NULL;
}

void *case_b() {
    __ss_float t0;
    __ss_int __4, __5, __6, __7, i, s, x;
    list<__ss_int> *l;

    t0 = __time__::time();
    s = __ss_int(0);

    FAST_FOR(i,0,__ss_int(50000000),1,4,5)
        l = (__ss_list<__ss_int, 0>());

        FAST_FOR(x,0,__ss_int(64),1,6,7)
            if ((x>__ss_int(2))) {
                l->append((__ss_int(2)*x));
            }
        END_FOR

        s = (s+__sum(l));
    END_FOR

    print(__mod6(const_0, 1, (__time__::time()-t0)));
    print(const_1);
    print(const_1);
    print(s);
    return NULL;
}

void *case_c() {
    __ss_float t0;
    __ss_int __10, __11, __8, __9, i, s, x;
    list<__ss_int> *l;

    t0 = __time__::time();
    s = __ss_int(0);

    FAST_FOR(i,0,__ss_int(50000000),1,8,9)
        l = (__ss_list<__ss_int, 1>());

        FAST_FOR(x,0,__random__::randrange(__ss_int(64)),1,10,11)
            if ((x>__ss_int(2))) {
                l->append((__ss_int(2)*x));
            }
        END_FOR

        s = (s+__sum(l));
    END_FOR

    print(__mod6(const_0, 1, (__time__::time()-t0)));
    print(s);
    return NULL;
}

void __init() {
    __name__ = new str("__main__");

    const_0 = new str("%.2f");
    const_1 = new str("---");

    case_a();
    case_b();
    case_c();
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __math__::__init();
    __time__::__init();
    __random__::__init();
    __shedskin__::__start(__mytest__::__init);
}
