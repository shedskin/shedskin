#include "builtin.hpp"
#include "loop.hpp"

namespace __loop__ {


file *__file;
__ss_int __void, i, total;
str *__name__;



void __init() {
    __name__ = new str("__main__");


    i = __ss_int(0LL);
    total = __ss_int(0LL);

    while ((__loop__::i<__ss_int(300000LL))) {
        total = (__loop__::total+(__loop__::i*__ss_int(2LL)));
        i = (__loop__::i+__ss_int(1LL));
    }
    print(__loop__::total);
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __shedskin__::__start(__loop__::__init);
}
