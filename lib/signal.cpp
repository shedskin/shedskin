#include "signal.hpp"

namespace __signal__ {

str *__name__;
int __ss_SIGTERM;

void __init() {
    __name__ = new str("signal");

    __ss_SIGTERM = 15;
}

} // module namespace

