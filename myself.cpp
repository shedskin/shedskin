#include "builtin.hpp"
#include "time.hpp"
#include "myself.hpp"

namespace __myself__ {

str *const_0, *const_1, *const_2, *const_3, *const_4;


str *__name__;
__ss_int ALL_REPS, ANY_REPS, MAX_REPS, MIN_REPS, N, SUM_REPS;
list<__ss_int> *DATA;
__ss_float total;


static inline list<__ss_int> *list_comp_0();

static inline list<__ss_int> *list_comp_0() {
    __ss_int __0, __1, i;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->units.reserve(4);
    FAST_FOR(i,0,__myself__::N,1,0,1)
        __ss_result->append(__mods((i*__ss_int(2654435761LL)), __ss_int(1000LL)));
    END_FOR

    return __ss_result;
}

__ss_int bench_sum() {
    /**
    sum(<genexpr>) in a hot loop -- accumulator fold over runtime data.
    */
    __ss_int __2, __3, __6, k, s, total, x;
    list<__ss_int> *__4;
    __iter<__ss_int> *__5;
    list<__ss_int>::for_in_loop __7;

    total = __ss_int(0LL);

    FAST_FOR(k,0,__myself__::SUM_REPS,1,2,3)
        s = __ss_int(0LL);

        FOR_IN(x,__myself__::DATA,4,6,7)
            s = (s+((x)^(k)));
        END_FOR

        total = (total+s);
    END_FOR

    return total;
}

__ss_float timed(str *label, lambda0 fn) {
    __ss_float dt, t0;
    __ss_int r;

    t0 = __time__::time();
    r = fn();
    dt = (__time__::time()-t0);
    print(__mod6(const_1, 3, label, dt, r));
    return dt;
}

void __init() {
    __name__ = new str("__main__");

    const_0 = new str("sum(<genexpr>) in a hot loop -- accumulator fold over runtime data.");
    const_1 = new str("%s %.3f CHECKSUM %d");
    const_2 = new str("__main__");
    const_3 = new str("SUM");
    const_4 = new str("TIME %.3f");

    SUM_REPS = __ss_int(2000LL);
    ANY_REPS = __ss_int(2000LL);
    ALL_REPS = __ss_int(2000LL);
    MIN_REPS = __ss_int(2000LL);
    MAX_REPS = __ss_int(2000LL);
    N = __ss_int(20000LL);
    DATA = list_comp_0();
    if (__eq(__myself__::__name__, const_2)) {
        bench_sum();
        total = __ss_float(0.0);
        total = (__myself__::total+timed(const_3, bench_sum));
        print(__mod6(const_4, 1, __myself__::total));
    }
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __time__::__init();
    __shedskin__::__start(__myself__::__init);
}
