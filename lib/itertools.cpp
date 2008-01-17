#include "itertools.hpp"

namespace __itertools__ {

str *__name__;

void __init() {
    __name__ = new str("itertools");

}

class __gen_count : public __iter<int> {
public:
    int n;
    int __last_yield;

    __gen_count(int n) {
        this->n = n;
        __last_yield = -1;
    }

    int next() {
        switch(__last_yield) {
            case 0: goto __after_yield_0;
            default: break;
        }

        while(1) {
            __last_yield = 0;
            return n;
            __after_yield_0:;
            n += 1;
        }
        throw new StopIteration();
    }

};

__iter<int> *count(int n) {
    return new __gen_count(n);

}

} // module namespace

