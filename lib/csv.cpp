#include "csv.hpp"

namespace __csv__ {

str *const_0, *const_1, *const_2, *const_3;

str *__name__;
OSError *__exception;

/**
class reader
*/

class_ *cl_reader;

list<str *> *reader::next() {
    
    this->count = (this->count+1);
    if ((this->count==5)) {
        throw (new StopIteration());
    }
    return (new list<str *>(4, const_0, const_1, const_2, const_3));
}

reader *reader::__iter__() {
    
    return this;
}

void *reader::__init__(file *csvfile) {
    
    this->count = 0;
    return NULL;
}

void __init() {
    const_0 = new str("hoei");
    const_1 = new str("hop");
    const_2 = new str("18");
    const_3 = new str("hurk");

    __name__ = new str("csv");

    cl_reader = new class_("reader", 42, 42);

}

} // module namespace

