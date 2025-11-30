#include "builtin.hpp"
#include "test2.hpp"

namespace __test2__ {

str *const_0;


str *__name__;

unsigned char *SP;
unsigned char *SPEND;
unsigned char stackie[1024*1024];


class StackFrame {
public:
    unsigned char *__SP;

    StackFrame();
    ~StackFrame();

    template<class T> T *neu();
};


StackFrame::StackFrame() {
    __SP = SP;
}

StackFrame::~StackFrame() {
    SP = __SP;
}

template<class T> T *StackFrame::neu() {
    unsigned char *mymem = SP;

    size_t sz = sizeof(T);

    if(SP + sz >= SPEND) { // DEZE CHECKT MAAKT ALLES 10 KEER TRAGER :S
        printf("DOE HEAP!!");
        return 0;
    } else {
        SP += sz;
        return (T *)mymem; // reinterpret or whatever?
    }
}


tuple<__ss_int> *blaap(__ss_int x, __ss_int y) {
    return (new tuple<__ss_int>(2,(__ss_int(2LL)*x),(__ss_int(3LL)*y)));
}

void *__ss_main() {
    __ss_int __0, __1, a, b, i, s;
    tuple<__ss_int> *__2;

    s = __ss_int(0LL);

    FAST_FOR(i,0,__power(__ss_int(10LL), __ss_int(8LL)),1,0,1)
        __2 = blaap(i, (i+__ss_int(1LL)));
        __unpack_check(__2, 2);
        a = __2->__getfirst__();
        b = __2->__getsecond__();
        s = (s+(a+b));
    END_FOR

    print(s);
    return NULL;
}

void __init() {
    const_0 = new str("__main__");

    __name__ = new str("__main__");

    SP = stackie;
    SPEND = stackie+1024*1024;

    if (__eq(__test2__::__name__, const_0)) {
        __ss_main();
    }
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __shedskin__::__start(__test2__::__init);
}
