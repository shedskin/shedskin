#include "builtin.hpp"
#include "test_prog_nqueens_min.hpp"

namespace __test_prog_nqueens_min__ {


file *__file;
__ss_int __void;
str *__name__;



list<list<__ss_int> *> *rec(__ss_int n) {
    if ((n==__ss_int(0LL))) {
        return (new list<list<__ss_int> *>(1,(__ss_list<__ss_int, 0>())));
    }
    return extend(rec((n-__ss_int(1LL))));
}

list<list<__ss_int> *> *extend(list<list<__ss_int> *> *prev) {
    list<list<__ss_int> *> *solutions;

    solutions = (__ss_list<list<__ss_int> *, 1>());
    solutions->append(__add_list_elt(prev->__getfast__(__ss_int(0LL)), __ss_int(1LL)));
    return solutions;
}

void __init() {
    __name__ = new str("__main__");


    rec(__ss_int(0LL));
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __shedskin__::__start(__test_prog_nqueens_min__::__init);
}
