#ifndef __TEST_PROG_NQUEENS_HPP
#define __TEST_PROG_NQUEENS_HPP

using namespace __shedskin__;
namespace __test_prog_nqueens__ {

extern str *const_0;



extern file *__file;
extern __ss_int __void;
extern str *__name__;


list<list<__ss_int> *> *n_queens(__ss_int n, __ss_int width);
list<list<__ss_int> *> *add_queen(__ss_int new_row, __ss_int width, list<list<__ss_int> *> *previous_solutions);
__ss_int safe_queen(__ss_int new_row, __ss_int new_col, list<__ss_int> *sol);
void *test_nqueens();
void *test_all();

} // module namespace
#endif
