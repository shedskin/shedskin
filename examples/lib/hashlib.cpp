#include "hashlib.hpp"
#include <openssl/md5.h>

namespace __hashlib__ {

str *__name__;


/**
class md5
*/

class_ *cl_md5;

str *md5::hexdigest() {
    str *digest = new str("                ");
    MD5((unsigned char *)data->unit.data(), data->unit.size(), (unsigned char *)digest->unit.data());
    str *hexdigest = new str();
    for(int i=0; i<16; i++) {
        hexdigest->unit.push_back(__str((digest->unit[i]>>4) & 0xf, 16)->unit[0]);
        hexdigest->unit.push_back(__str(digest->unit[i] & 0xf, 16)->unit[0]);
    }
    return hexdigest;
}

void *md5::__init__(str *data) {
    this->data = data;
    return NULL;
}

void __init() {
    __name__ = new str("hashlib");

    cl_md5 = new class_("md5");
}

} // module namespace

