#include "builtin.hpp"
#include "hap.hpp"

namespace __hap__ {


__ss_int __void;
str *__name__;



void __init() {
    __name__ = new str("__main__");


    print(__str(__ss_float(18.8)));
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __shedskin__::__start(__hap__::__init);
}
