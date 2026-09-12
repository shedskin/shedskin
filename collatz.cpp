#include "builtin.hpp"
#include "time.hpp"
#include "collatz.hpp"

namespace __collatz__ {

str *const_0, *const_1, *const_2, *const_3;


str *__name__;
__ss_int __21, __22, n;
__ss_float t0;


static inline list<__ss_int> *list_comp_0(list<__ss_int> *lookup_c, list<__ss_int> *lookup_multistep);
static inline list<__ss_int> *list_comp_1(list<__ss_int> *lookup_multistep);
static inline list<__ss_int> *list_comp_2(__ss_int K);

static inline list<__ss_int> *list_comp_0(list<__ss_int> *lookup_c, list<__ss_int> *lookup_multistep) {
    tuple<__ss_int> *__2;
    __ss_int __5, __8, c, i;
    __iter<tuple<__ss_int> *> *__3, *__4;
    list<__ss_int> *__6, *__7;
    __iter<tuple<__ss_int> *>::for_in_loop __9;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    FOR_IN_ZIP(i,c,lookup_multistep,lookup_c,6,7,5,8)
        __ss_result->append((c+__mods(i, __ss_int(2))));
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_1(list<__ss_int> *lookup_multistep) {
    __ss_int __12, i;
    list<__ss_int> *__10;
    __iter<__ss_int> *__11;
    list<__ss_int>::for_in_loop __13;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(len(lookup_multistep));
    FOR_IN(i,lookup_multistep,10,12,13)
        __ss_result->units[__12] = step(i, True);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_2(__ss_int K) {
    __ss_int __14, __15, c;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->units.reserve(4);
    FAST_FOR(c,0,(K+__ss_int(1)),1,14,15)
        __ss_result->append(__power(__ss_int(3), c));
    END_FOR

    return __ss_result;
}

__ss_int step(__ss_int n, __ss_bool extra) {
    if ((__mods(n, __ss_int(2))==__ss_int(0))) {
        return __floordiv(n,__ss_int(2));
    }
    else if (extra) {
        return __floordiv(((__ss_int(3)*n)+__ss_int(1)),__ss_int(2));
    }
    else {
        return ((__ss_int(3)*n)+__ss_int(1));
    }
    return 0;
}

void *__ss_main() {
    __ss_int K, N, __0, __1, __16, __17, __18, __19, __20, a, b, bmask, c, d, delay_record, k, n, orign, rest9, steps;
    list<__ss_int> *lookup_c, *lookup_multistep, *lookup_pow, *lookup_tail;
    __ss_float t0;

    N = __ss_int(10000000);
    K = __ss_int(17);
    bmask = (__power(__ss_int(2), K)-__ss_int(1));
    lookup_multistep = __ss_list_range(__ss_int(0),__power(__ss_int(2), K));
    lookup_c = ((new list<__ss_int>(1,__ss_int(0))))->__mul__(len(lookup_multistep));

    FAST_FOR(k,0,K,1,0,1)
        lookup_c = list_comp_0(lookup_c, lookup_multistep);
        lookup_multistep = list_comp_1(lookup_multistep);
    END_FOR

    lookup_pow = list_comp_2(K);
    lookup_tail = (new list<__ss_int>(1,__ss_int(0)));

    FAST_FOR(n,__ss_int(1),__power(__ss_int(2), K),1,16,17)
        steps = __ss_int(0);

        while ((n!=__ss_int(1))) {
            n = step(n, False);
            steps = (steps+__ss_int(1));
        }
        lookup_tail->append(steps);
    END_FOR

    print(const_0);
    t0 = __time__::time();
    delay_record = __ss_int(0);
    rest9 = __ss_int(1);

    FAST_FOR(n,__ss_int(2),N,1,18,19)
        rest9 = (rest9+__ss_int(1));
        if ((rest9==__ss_int(9))) {
            rest9 = __ss_int(0);
        }
        if ((__eq(__20=rest9,__ss_int(2)) || __eq(__20,__ss_int(4)) || __eq(__20,__ss_int(5)) || __eq(__20,__ss_int(8)))) {
            continue;
        }
        if ((((n)&(__ss_int(7)))==__ss_int(5))) {
            continue;
        }
        orign = n;
        steps = __ss_int(0);

        while ((n>bmask)) {
            a = (n>>K);
            b = ((n)&(bmask));
            c = lookup_c->__getfast__(b);
            d = lookup_multistep->__getfast__(b);
            steps = (steps+((__ss_int(2)*c)+(K-c)));
            n = ((a*lookup_pow->__getfast__(c))+d);
        }
        steps = (steps+lookup_tail->__getfast__(n));
        if ((steps>delay_record)) {
            delay_record = steps;
            print(delay_record, orign);
        }
    END_FOR

    print(__mod6(const_1, 1, (N/(__time__::time()-t0))));
    return NULL;
}

void __init() {
    __name__ = new str("__main__");

    const_0 = new str("1 2");
    const_1 = new str("%.2f numbers/second");
    const_2 = new str("__main__");
    const_3 = new str("TIME %.2f");

    if (__eq(__collatz__::__name__, const_2)) {

        FAST_FOR(n,0,__ss_int(10),1,21,22)
            if ((__collatz__::n==__ss_int(5))) {
                t0 = __time__::time();
            }
            __ss_main();
        END_FOR

        print(__mod6(const_3, 1, (__time__::time()-__collatz__::t0)));
    }
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __time__::__init();
    __shedskin__::__start(__collatz__::__init);
}
