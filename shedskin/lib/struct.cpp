#include "struct.hpp"
#include <stdio.h>

namespace __struct__ {

__ss_int unpack_int(char o, char c, int d, str *data, __ss_int *pos) {
    return 42;
}

str * unpack_str(char o, char c, int d, str *data, __ss_int *pos) {
    return new str("ole!");
}

__ss_int calcsize(str *fmt) {
    return 42;

}

void __init() {

}

} // module namespace

