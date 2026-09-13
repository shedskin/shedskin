#include "builtin.hpp"
#include "claude_min.hpp"

namespace __claude_min__ {


file *__file;
__ss_int __void;
str *__name__;



/**
class C
*/

class_ *cl_C;

void *C::f(__ss_int x) {
    set<__ss_int> *s;

    s = (new set<__ss_int>(1,x));
    return NULL;
}

void __init() {
    __name__ = new str("__main__");


    cl_C = new class_("C");
    ((new C()))->f(__ss_int(1LL));
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __shedskin__::__start(__claude_min__::__init);
}
