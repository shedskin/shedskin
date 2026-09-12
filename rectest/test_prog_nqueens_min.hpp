#ifndef __TEST_PROG_NQUEENS_MIN_HPP
#define __TEST_PROG_NQUEENS_MIN_HPP

using namespace __shedskin__;
namespace __test_prog_nqueens_min__ {



extern file *__file;
extern __ss_int __void;
extern str *__name__;


list<list<__ss_int> *> *rec(__ss_int n);
list<list<__ss_int> *> *extend(list<list<__ss_int> *> *prev);

} // module namespace
#endif
