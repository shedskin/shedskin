#ifndef __LIFE_MIN_HPP
#define __LIFE_MIN_HPP

using namespace __shedskin__;
namespace __life_min__ {


typedef __ss_int (*lambda0)();
typedef __ss_int (*lambda1)();

extern file *__file;
extern __ss_int __3, __void, value;
extern str *__name__;
extern __collections__::defaultdict<tuple<__ss_int> *, __ss_int> *board;
extern tuple<__ss_int> *pos;
extern tuple2<tuple<__ss_int> *, __ss_int> *__0;
extern list<tuple2<tuple<__ss_int> *, __ss_int> *> *__1;
extern __iter<tuple2<tuple<__ss_int> *, __ss_int> *> *__2;


__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *snext(__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *board);

} // module namespace
#endif
