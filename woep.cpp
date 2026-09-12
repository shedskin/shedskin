#include "builtin.hpp"
#include "time.hpp"
#include "woep.hpp"

/**
Synthetic benchmark for reducer/genexpr fusion (REVIEW.md finding 3A.1).
Each timed section drives one of the fusible builtins -- sum / any / all / min /
max -- over a generator expression inside a hot loop. This is the pattern that
Shed Skin lowers to a `static inline` accumulator when the fusion optimization is
enabled, and to a heap-allocated iterator class with a virtual `__get_next()` per
element otherwise.
Each reducer iterates over a runtime-populated list (`DATA`) and mixes in the
outer loop variable `k`, so the reducer is neither loop-invariant nor a
closed-form series: the C++ optimizer cannot hoist, constant-fold, or eliminate
it. This measures real per-element iteration + dispatch cost, keeping the
fused-vs-unfused comparison fair and representative.
Run standalone (prints a checksum for correctness and a wall-clock TIME):
    shedskin translate reducer_bench.py && make && ./reducer_bench
To compare fused vs unfused, build once with the current compiler and once with
the fusion removed, then diff the TIME lines (see tests/benchmarks/README.md).
*/

namespace __woep__ {

str *const_0, *const_1, *const_2, *const_3, *const_4, *const_5;


str *__name__;
__ss_int ALL_REPS, ANY_REPS, MAX_REPS, MIN_REPS, N, SUM_REPS;
list<__ss_int> *DATA;
__ss_float total;


static inline list<__ss_int> *list_comp_0();
class list_comp_1 : public __iter<__ss_int> {
public:
    __ss_int __6, x;
    list<__ss_int> *__4;
    __iter<__ss_int> *__5;
    list<__ss_int>::for_in_loop __7;

    __ss_int k;
    int __last_yield;

    list_comp_1(__ss_int k);
    __ss_int __get_next();
};


static inline list<__ss_int> *list_comp_0() {
    __ss_int __0, __1, i;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->units.reserve(4);
    FAST_FOR(i,0,__woep__::N,1,0,1)
        __ss_result->append(__mods((i*__ss_int(2654435761LL)), __ss_int(1000LL)));
    END_FOR

    return __ss_result;
}

list_comp_1::list_comp_1(__ss_int k) {
    this->k = k;
    __last_yield = -1;
}

__ss_int list_comp_1::__get_next() {
    if(!__last_yield) goto __after_yield_0;
    __last_yield = 0;

    FOR_IN(x,DATA,4,6,7)
        __result = ((x)^(k));
        return __result;
        __after_yield_0:;
    END_FOR

    __stop_iteration = true;
    return __zero<__ss_int>();
}

__ss_int bench_sum() {
    /**
    sum(<genexpr>) in a hot loop -- accumulator fold over runtime data.
    */
    __ss_int __2, __3, k, total;
    void *x;

    total = __ss_int(0LL);

    FAST_FOR(k,0,__woep__::SUM_REPS,1,2,3)
        total = (total+__sum(new list_comp_1(k)));
    END_FOR

    return total;
}

__ss_float timed(str *label, lambda0 fn) {
    __ss_float dt, t0;
    __ss_int r;

    t0 = __time__::time();
    r = fn();
    dt = (__time__::time()-t0);
    print(__mod6(const_2, 3, label, dt, r));
    return dt;
}

void __init() {
    __name__ = new str("__main__");

    const_0 = new str("Synthetic benchmark for reducer/genexpr fusion (REVIEW.md finding 3A.1).\012\012Each timed section drives one of the fusible builtins -- sum / any / all / min /\012max -- over a generator expression inside a hot loop. This is the pattern that\012Shed Skin lowers to a `static inline` accumulator when the fusion optimization is\012enabled, and to a heap-allocated iterator class with a virtual `__get_next()` per\012element otherwise.\012\012Each reducer iterates over a runtime-populated list (`DATA`) and mixes in the\012outer loop variable `k`, so the reducer is neither loop-invariant nor a\012closed-form series: the C++ optimizer cannot hoist, constant-fold, or eliminate\012it. This measures real per-element iteration + dispatch cost, keeping the\012fused-vs-unfused comparison fair and representative.\012\012Run standalone (prints a checksum for correctness and a wall-clock TIME):\012\012    shedskin translate reducer_bench.py && make && ./reducer_bench\012\012To compare fused vs unfused, build once with the current compiler and once with\012the fusion removed, then diff the TIME lines (see tests/benchmarks/README.md).\012");
    const_1 = new str("sum(<genexpr>) in a hot loop -- accumulator fold over runtime data.");
    const_2 = new str("%s %.3f CHECKSUM %d");
    const_3 = new str("__main__");
    const_4 = new str("SUM");
    const_5 = new str("TIME %.3f");

    SUM_REPS = __ss_int(2000LL);
    ANY_REPS = __ss_int(2000LL);
    ALL_REPS = __ss_int(2000LL);
    MIN_REPS = __ss_int(2000LL);
    MAX_REPS = __ss_int(2000LL);
    N = __ss_int(20000LL);
    DATA = list_comp_0();
    if (__eq(__woep__::__name__, const_3)) {
        bench_sum();
        total = __ss_float(0.0);
        total = (__woep__::total+timed(const_4, bench_sum));
        print(__mod6(const_5, 1, __woep__::total));
    }
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __time__::__init();
    __shedskin__::__start(__woep__::__init);
}
