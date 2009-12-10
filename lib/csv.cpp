#include "csv.hpp"

namespace __csv__ {

str *const_0;

str *__name__;
OSError *__exception;

/**
class reader
*/

class_ *cl_reader;

__csviter *reader::__iter__() {
    
    return NULL;
}

void *reader::__init__(file *csvfile) {
    
    this->csvfile = csvfile;
    return NULL;
}

void __init() {
    const_0 = new str(",");

    __name__ = new str("csv");

    cl_reader = new class_("reader", 40, 40);

}

} // module namespace

