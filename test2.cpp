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


__ss_int woef(__ss_int x, __ss_int y, __ss_int z) {
    tuple<__ss_int> *v;

    v = (new tuple<__ss_int>(3,x,y,z));
    return __sum(v);
}

void *__ss_main() {
    __ss_int __0, __1, s, x;

    s = __ss_int(0LL);

    FAST_FOR(x,0,__power(__ss_int(10LL), __ss_int(8LL)),1,0,1)
        s = (s+woef(x, (x+__ss_int(1LL)), (x-__ss_int(1LL))));
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
