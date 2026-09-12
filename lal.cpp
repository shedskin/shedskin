#include "builtin.hpp"
#include "io.hpp"
#include "lal.hpp"

namespace __lal__ {

str *const_0, *const_1;


__ss_int __void;
str *__name__;
file *s;



void __init() {
    __name__ = new str("__main__");

    const_0 = new str("test.py");
    const_1 = new str("hoepa bfloep\012blap");

    s = open(const_0);
    s = ((file *)((new __io__::StringIO(const_1))));
    print(__lal__::s->readline());
    print(__lal__::s->readline());
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __io__::__init();
    __shedskin__::__start(__lal__::__init);
}
