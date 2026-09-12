#include "builtin.hpp"
#include "time.hpp"
#include "reducer_bench.hpp"

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

namespace __reducer_bench__ {

str *const_0, *const_1, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;


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
    typedef size_t for_in_loop;
    int __last_yield;

    __ss_int myresult;

    list_comp_1(__ss_int k);
    __ss_int __get_next();
    __ss_int __get_next_awesome();
    inline size_t for_in_init();
    inline bool for_in_has_next(size_t &i, __ss_int &e);
    inline __ss_int for_in_next(size_t &i);
};

class list_comp_2 : public __iter<__ss_bool> {
public:
    __ss_int __12, x;
    list<__ss_int> *__10;
    __iter<__ss_int> *__11;
    list<__ss_int>::for_in_loop __13;

    __ss_int k;
    typedef size_t for_in_loop;
    int __last_yield;

    __ss_bool myresult;

    list_comp_2(__ss_int k);
    __ss_bool __get_next();
    __ss_bool __get_next_awesome();
    inline size_t for_in_init();
    inline bool for_in_has_next(size_t &i, __ss_bool &);
    inline __ss_bool for_in_next(size_t &i);
};

class list_comp_3 : public __iter<__ss_bool> {
public:
    __ss_int __18, x;
    list<__ss_int> *__16;
    __iter<__ss_int> *__17;
    list<__ss_int>::for_in_loop __19;

    __ss_int k;
    typedef size_t for_in_loop;
    int __last_yield;

    __ss_bool myresult;

    list_comp_3(__ss_int k);
    __ss_bool __get_next();
    __ss_bool __get_next_awesome();
    inline size_t for_in_init();
    inline bool for_in_has_next(size_t &i, __ss_bool &);
    inline __ss_bool for_in_next(size_t &i);
};


static inline list<__ss_int> *list_comp_0() {
    __ss_int __0, __1, i;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->units.reserve(4);
    FAST_FOR(i,0,__reducer_bench__::N,1,0,1)
        __ss_result->append(__mods((i*__ss_int(2654435761LL)), __ss_int(1000LL)));
    END_FOR

    return __ss_result;
}

list_comp_1::list_comp_1(__ss_int k) {
    this->k = k;
    //printf("init\n");
    __last_yield = -1;
}

__ss_int list_comp_1::__get_next_awesome() {
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

__ss_int list_comp_1::__get_next() {
    return __get_next_awesome();
}

inline size_t list_comp_1::for_in_init() {
    __stop_iteration = false;
    return 0;
}

inline bool list_comp_1::for_in_has_next(size_t &i, __ss_int &e) {
    //printf("has next?\n");
    e = __get_next_awesome();
    //print(e);
    return !__stop_iteration;
}

inline __ss_int list_comp_1::for_in_next(size_t &i) {
    return myresult;
}

list_comp_2::list_comp_2(__ss_int k) {
    this->k = k;
    __last_yield = -1;
}

__ss_bool list_comp_2::__get_next_awesome() {
    if(!__last_yield) goto __after_yield_0;
    __last_yield = 0;

    FOR_IN(x,DATA,10,12,13)
        __result = ___bool((x>(__ss_int(1000000LL)+k)));
        return __result;
        __after_yield_0:;
    END_FOR

    __stop_iteration = true;
    return __zero<__ss_bool>();
}

__ss_bool list_comp_2::__get_next() {
    return __get_next_awesome();
}

inline size_t list_comp_2::for_in_init() {
    __stop_iteration = false;
    return 0;
}

inline bool list_comp_2::for_in_has_next(size_t &i, __ss_bool &e) {
    e = __get_next_awesome();
    return !__stop_iteration;
}

inline __ss_bool list_comp_2::for_in_next(size_t &i) {
    return myresult;
}

list_comp_3::list_comp_3(__ss_int k) {
    this->k = k;
    __last_yield = -1;
}

__ss_bool list_comp_3::__get_next_awesome() {
    if(!__last_yield) goto __after_yield_0;
    __last_yield = 0;

    FOR_IN(x,DATA,16,18,19)
        __result = ___bool((x<(__ss_int(1000000LL)+k)));
        return __result;
        __after_yield_0:;
    END_FOR

    __stop_iteration = true;
    return __zero<__ss_bool>();
}

__ss_bool list_comp_3::__get_next() {
    return __get_next_awesome();
}

inline size_t list_comp_3::for_in_init() {
    __stop_iteration = false;
    return 0;
}

inline bool list_comp_3::for_in_has_next(size_t &i, __ss_bool &e) {
    e = __get_next_awesome();
    return !__stop_iteration;
}

inline __ss_bool list_comp_3::for_in_next(size_t &i) {
    return myresult;
}

__ss_int bench_sum() {
    /**
    sum(<genexpr>) in a hot loop -- accumulator fold over runtime data.
    */
    __ss_int __2, __3, k, total;
    void *x;

    total = __ss_int(0LL);

    FAST_FOR(k,0,__reducer_bench__::SUM_REPS,1,2,3)
        total = (total+__sum(new list_comp_1(k)));
    END_FOR

    return total;
}

__ss_int bench_any() {
    /**
    any(<genexpr>) in a hot loop -- condition never true, so full scan.
    */
    __ss_int __8, __9, hits, k;
    void *x;

    hits = __ss_int(0LL);

    FAST_FOR(k,0,__reducer_bench__::ANY_REPS,1,8,9)
        if (any(new list_comp_2(k))) {
            hits = (hits+__ss_int(1LL));
        }
    END_FOR

    return hits;
}

__ss_int bench_all() {
    /**
    all(<genexpr>) in a hot loop -- condition always true, so full scan.
    */
    __ss_int __14, __15, hits, k;
    void *x;

    hits = __ss_int(0LL);

    FAST_FOR(k,0,__reducer_bench__::ALL_REPS,1,14,15)
        if (all(new list_comp_3(k))) {
            hits = (hits+__ss_int(1LL));
        }
    END_FOR

    return hits;
}

__ss_float timed(str *label, lambda2 fn) {
    __ss_float dt, t0;
    __ss_int r;

    t0 = __time__::time();
    r = fn();
    dt = (__time__::time()-t0);
    print(__mod6(const_4, 3, label, dt, r));
    return dt;
}

void __init() {
    __name__ = new str("__main__");

    const_0 = new str("Synthetic benchmark for reducer/genexpr fusion (REVIEW.md finding 3A.1).\012\012Each timed section drives one of the fusible builtins -- sum / any / all / min /\012max -- over a generator expression inside a hot loop. This is the pattern that\012Shed Skin lowers to a `static inline` accumulator when the fusion optimization is\012enabled, and to a heap-allocated iterator class with a virtual `__get_next()` per\012element otherwise.\012\012Each reducer iterates over a runtime-populated list (`DATA`) and mixes in the\012outer loop variable `k`, so the reducer is neither loop-invariant nor a\012closed-form series: the C++ optimizer cannot hoist, constant-fold, or eliminate\012it. This measures real per-element iteration + dispatch cost, keeping the\012fused-vs-unfused comparison fair and representative.\012\012Run standalone (prints a checksum for correctness and a wall-clock TIME):\012\012    shedskin translate reducer_bench.py && make && ./reducer_bench\012\012To compare fused vs unfused, build once with the current compiler and once with\012the fusion removed, then diff the TIME lines (see tests/benchmarks/README.md).\012");
    const_1 = new str("sum(<genexpr>) in a hot loop -- accumulator fold over runtime data.");
    const_2 = new str("any(<genexpr>) in a hot loop -- condition never true, so full scan.");
    const_3 = new str("all(<genexpr>) in a hot loop -- condition always true, so full scan.");
    const_4 = new str("%s %.3f CHECKSUM %d");
    const_5 = new str("__main__");
    const_6 = new str("SUM");
    const_7 = new str("ANY");
    const_8 = new str("ALL");
    const_9 = new str("TIME %.3f");

    SUM_REPS = __ss_int(2000LL);
    ANY_REPS = __ss_int(2000LL);
    ALL_REPS = __ss_int(2000LL);
    MIN_REPS = __ss_int(2000LL);
    MAX_REPS = __ss_int(2000LL);
    N = __ss_int(20000LL);
    DATA = list_comp_0();
    if (__eq(__reducer_bench__::__name__, const_5)) {
        bench_sum();
        bench_any();
        bench_all();
        total = __ss_float(0.0);
        total = (__reducer_bench__::total+timed(const_6, ((lambda2)(bench_sum))));
        total = (__reducer_bench__::total+timed(const_7, ((lambda2)(bench_any))));
        total = (__reducer_bench__::total+timed(const_8, bench_all));
        print(__mod6(const_9, 1, __reducer_bench__::total));
    }
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __time__::__init();
    __shedskin__::__start(__reducer_bench__::__init);
}
