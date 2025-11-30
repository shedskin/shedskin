#include "builtin.hpp"
#include "test.hpp"

namespace __test__ {

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

    unsigned char *nieuw(size_t sz);

//    template<T> T new(..) { // bypass 'new' and allocate on stack!
//        void *mymem = SP;
//        SP += sizeof(T);
//        return (T *)mymem; // reinterpret_cast or whatever?
//    }
};



StackFrame::StackFrame() {
    __SP = SP;
}

StackFrame::~StackFrame() {
    SP = __SP;
}

unsigned char *StackFrame::nieuw(size_t sz) {
    unsigned char *mymem = SP;

    if(SP + sz >= SPEND) {
        printf("DOE HEAP!!");
        return 0;
    } else {
        SP += sz;
        return mymem;
    }

}


//    tuple<__ss_int> *t = __sss.new<tuple<__ss_int>>(2, 7, 8);

/**
class Vector
*/

class_ *cl_Vector;

void *Vector::__init__(__ss_int x, __ss_int y, __ss_int z) {
    this->x = x;
    this->y = y;
    this->z = z;
    return NULL;
}

__ss_int woef(__ss_int x, __ss_int y, __ss_int z) {
    StackFrame __sss;

    Vector *v = (Vector *)(__sss.nieuw(sizeof(Vector)));
    v->__init__(x, y, z);
    return ((v->x+v->y)+v->z);
}

void *__ss_main() {
    __ss_int __0, __1, s, x;

    s = __ss_int(0LL);

    printf("stackie address %X\n", SP);

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

    cl_Vector = new class_("__main__.Vector");
    if (__eq(__test__::__name__, const_0)) {
        __ss_main();
    }
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __shedskin__::__start(__test__::__init);
}
