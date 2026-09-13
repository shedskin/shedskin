#ifndef __WOEP_HPP
#define __WOEP_HPP

using namespace __shedskin__;
namespace __woep__ {

extern str *const_0, *const_1, *const_2, *const_3, *const_4, *const_5;


typedef __ss_int (*lambda0)();

extern str *__name__;
extern __ss_int ALL_REPS, ANY_REPS, MAX_REPS, MIN_REPS, N, SUM_REPS;
extern list<__ss_int> *DATA;
extern __ss_float total;


__ss_int bench_sum();
__ss_float timed(str *label, lambda0 fn);

} // module namespace
#endif
