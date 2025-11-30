#include "builtin.hpp"
#include "test3.hpp"

namespace __test3__ {

str *const_0;


str *__name__;

unsigned char *SP;
unsigned char *SPEND;
const size_t STACKSIZE = 1024*1024;
unsigned char stackie[STACKSIZE];


class StackFrame {
public:
    unsigned char *__SP;

    StackFrame();
    ~StackFrame();

    template<class T> T *neu(__ss_int x, __ss_int y, __ss_int z);
};


StackFrame::StackFrame() {
    __SP = SP;
}

StackFrame::~StackFrame() {
    SP = __SP;
}

template<class T> T *StackFrame::neu(__ss_int x, __ss_int y, __ss_int z) {
    unsigned char *mymem = SP;

    size_t sz = sizeof(T);

    if(SP + sz >= SPEND) { // DEZE CHECKT MAAKT ALLES 10 KEER TRAGER :S
//        printf("DOE HEAP!!");
        return new T(x, y, z);
    } else {
        SP += sz;
        return new(mymem)T(x, y, z);
    }
}


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

Vector *woef(__ss_int x, __ss_int y, __ss_int z) {
    return (new Vector(x, y, z));
}

__ss_int draw() {
    __ss_int __0, __1, s, x;
    Vector *v;

    s = __ss_int(0LL);

    FAST_FOR(x,0,__power(__ss_int(10LL), __ss_int(5LL)),1,0,1)
        v = woef(x, (x+__ss_int(1LL)), (x-__ss_int(1LL)));
        s = (s+((v->x+v->y)+v->z));
    END_FOR

    return s;
}

void *__ss_main() {
    __ss_int __2, __3, s, x;

    s = __ss_int(0LL);

    FAST_FOR(x,0,__power(__ss_int(10LL), __ss_int(3LL)),1,2,3)
        s = (s+draw());
    END_FOR

    print(s);
    return NULL;
}

void __init() {
    const_0 = new str("__main__");

    __name__ = new str("__main__");

    SP = stackie;
    SPEND = stackie+STACKSIZE;

    cl_Vector = new class_("__main__.Vector");
    if (__eq(__test3__::__name__, const_0)) {
        __ss_main();
    }
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __shedskin__::__start(__test3__::__init);
}
