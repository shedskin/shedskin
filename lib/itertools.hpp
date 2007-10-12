#ifndef __ITERTOOLS_HPP
#define __ITERTOOLS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __itertools__ {


extern str * __name__;
void __init();
__iter<int> *count(int n);

template <class A> class __gen_cycle : public __iter<A> {
public:
    A element;
    int __5;
    __iter<A> *__4;
    __iter<A> *__1;
    pyiter<A> *__0;
    list<A> *__3;
    int __2;
    list<A> *saved;
    pyiter<A> *iterable;
    int __last_yield;

    __gen_cycle(pyiter<A> *iterable) {
        this->iterable = iterable;
        __last_yield = -1;
    }

    A next() {
        switch(__last_yield) {
            case 0: goto __after_yield_0;
            case 1: goto __after_yield_1;
            default: break;
        }
        saved = (new list<A>());

        FOR_IN(element,iterable,1)
            __last_yield = 0;
            return element;
            __after_yield_0:;
            saved->append(element);
        END_FOR


        while(__bool(saved)) {

            FOR_IN_SEQ(element,saved,3,5)
                __last_yield = 1;
                return element;
                __after_yield_1:;
            END_FOR

        }
        throw new StopIteration();
    }

};

template <class A> __iter<A> *cycle(pyiter<A> *iterable) {
    return new __gen_cycle<A>(iterable);

}

template <class A> class __gen_repeat : public __iter<A> {
public:
    int i;
    int __7;
    A _object;
    int __6;
    int times;
    int __last_yield;

    __gen_repeat(A _object,int times) {
        this->_object = _object;
        this->times = times;
        __last_yield = -1;
    }

    A next() {
        switch(__last_yield) {
            case 0: goto __after_yield_0;
            case 1: goto __after_yield_1;
            default: break;
        }
        if ((times==-1)) {

            while(1) {
                __last_yield = 0;
                return _object;
                __after_yield_0:;
            }
        }
        else {

            FAST_FOR(i,0,times,1,6,7)
                __last_yield = 1;
                return _object;
                __after_yield_1:;
            END_FOR

        }
        throw new StopIteration();
    }

};

template <class A> __iter<A> *repeat(A _object, int times) {
    return new __gen_repeat<A>(_object,times);

}

} // module namespace
#endif
