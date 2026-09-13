#ifndef __LIFE_HPP
#define __LIFE_HPP

using namespace __shedskin__;
namespace __life__ {

extern str *const_0, *const_1, *const_2, *const_3, *const_4, *const_5, *const_6;


typedef __ss_int (*lambda0)();
typedef __ss_int (*lambda1)();
typedef __collections__::defaultdict<tuple<__ss_int> *, __ss_int> *(*lambda2)(__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *);

extern file *__file;
extern __ss_int __30, __31, __32, __33, __void, columns, count, m, n, rows;
extern str *__name__;
extern __ss_float t0;


__ss_int add(__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *board, tuple<__ss_int> *pos);
__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *snext(__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *board);
__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *process(__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *board);
__iter<__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *> *generator(__ss_int rows, __ss_int columns);
void *bruteforce(__ss_int rows, __ss_int columns);

} // module namespace
#endif
