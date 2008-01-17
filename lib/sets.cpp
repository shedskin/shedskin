#include "sets.hpp"

namespace __sets__ {

str *__name__;
double t0;
set<int> *seta, *setb;
int __4, __5, i;

static inline list<int> *list_comp_0() {
    int __1, __0, n;
    list<int> *result = new list<int>();

    FAST_FOR(n,0,10000,1,0,1)
        result->append(__random__::randint(0, 100000));
    END_FOR

    return result;
}

static inline list<int> *list_comp_1() {
    int __2, __3, n;
    list<int> *result = new list<int>();

    FAST_FOR(n,0,10000,1,2,3)
        result->append(__random__::randint(0, 100000));
    END_FOR

    return result;
}

void __init() {
    __name__ = new str("__main__");

    __random__::seed(1);
    seta = (new set<int>(list_comp_0()));
    setb = (new set<int>(list_comp_1()));
    print("%d %d %d\n", len(seta->__and__(setb)), len(seta->__or__(setb)), len(seta->__xor__(setb)));
    t0 = __time__::clock();

    FAST_FOR(i,0,1000,1,4,5)
        seta->__and__(setb);
        seta->__or__(setb);
        seta->__xor__(setb);
    END_FOR

    print("%h\n", (__time__::clock()-t0));
}

} // module namespace

int main(int argc, char **argv) {
    __shedskin__::__init();
    __random__::__init();
    __math__::__init();
    __time__::__init();
    __sets__::__init();
    __shedskin__::__exit();
}
