#include "builtin.hpp"
#include "test_prog_nqueens.hpp"

namespace __test_prog_nqueens__ {

str *const_0;


file *__file;
__ss_int __void;
str *__name__;



list<list<__ss_int> *> *n_queens(__ss_int n, __ss_int width) {
    if ((n==__ss_int(0LL))) {
        return (new list<list<__ss_int> *>(1,(__ss_list<__ss_int, 0>())));
    }
    else {
        return add_queen((n-__ss_int(1LL)), width, n_queens((n-__ss_int(1LL)), width));
    }
    return 0;
}

list<list<__ss_int> *> *add_queen(__ss_int new_row, __ss_int width, list<list<__ss_int> *> *previous_solutions) {
    list<list<__ss_int> *> *__0, *solutions;
    list<__ss_int> *sol;
    __ss_int __2, __4, __5, new_col;
    __iter<list<__ss_int> *> *__1;
    list<list<__ss_int> *>::for_in_loop __3;

    solutions = (__ss_list<list<__ss_int> *, 1>());

    FOR_IN(sol,previous_solutions,0,2,3)

        FAST_FOR(new_col,0,width,1,4,5)
            if (safe_queen(new_row, new_col, sol)) {
                solutions->append(__add_list_elt(sol, new_col));
            }
        END_FOR

    END_FOR

    return solutions;
}

__ss_int safe_queen(__ss_int new_row, __ss_int new_col, list<__ss_int> *sol) {
    __ss_int __6, __7, row;
    __ss_bool __10, __8, __9;


    FAST_FOR(row,0,new_row,1,6,7)
        if (((sol->__getfast__(row)==new_col) or ((sol->__getfast__(row)+row)==(new_col+new_row)) or ((sol->__getfast__(row)-row)==(new_col-new_row)))) {
            return __ss_int(0LL);
        }
    END_FOR

    return __ss_int(1LL);
}

void *test_nqueens() {
    __ss_int n;
    list<list<__ss_int> *> *solutions;

    n = __ss_int(4LL);
    solutions = n_queens(n, n);
    ASSERT(___bool((len(solutions)==__ss_int(2LL))), 0);
    return NULL;
}

void *test_all() {
    test_nqueens();
    return NULL;
}

void __init() {
    __name__ = new str("__main__");

    const_0 = new str("__main__");

    if (__eq(__test_prog_nqueens__::__name__, const_0)) {
        test_all();
    }
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __shedskin__::__start(__test_prog_nqueens__::__init);
}
