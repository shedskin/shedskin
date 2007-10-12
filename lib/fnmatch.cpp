#include "fnmatch.hpp"

namespace std {
#include <fnmatch.h>

}

namespace __fnmatch__ {

void __init() {
}

int fnmatch(str *f, str *p) {
    return (std::fnmatch(p->unit.c_str(), f->unit.c_str(), 0) == 0);
}

int fnmatchcase(str *f, str *p) {
    return fnmatch(f, p);
}

} // module namespace

