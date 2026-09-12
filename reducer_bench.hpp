#ifndef __REDUCER_BENCH_HPP
#define __REDUCER_BENCH_HPP

using namespace __shedskin__;
namespace __reducer_bench__ {

extern str *const_0, *const_1, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;


typedef __ss_int (*lambda0)();
typedef __ss_int (*lambda1)();
typedef __ss_int (*lambda2)();

extern str *__name__;
extern __ss_int ALL_REPS, ANY_REPS, MAX_REPS, MIN_REPS, N, SUM_REPS;
extern list<__ss_int> *DATA;
extern __ss_float total;


__ss_int bench_sum();
__ss_int bench_any();
__ss_int bench_all();
__ss_float timed(str *label, lambda2 fn);

} // module namespace
#endif
