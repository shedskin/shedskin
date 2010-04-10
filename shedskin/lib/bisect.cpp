#include "bisect.hpp"

namespace __bisect__ {

str *__name__;

void __init() {
    __name__ = new str("bisect");
}

void __pos_check(__ss_int lo, __ss_int hi) {
    if(lo<0 || hi<0)
        throw new ValueError(new str("bisect: 'lo' and 'hi' arguments must be positive"));

}


} // module namespace

