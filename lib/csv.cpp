#include "csv.hpp"

namespace __csv__ {

str *const_0;

str *__name__;
OSError *__exception;

/**
class reader
*/

class_ *cl_reader;

__csviter::__csviter(file *csvfile) { 
    this->csvfile = csvfile; 
}

list<str *> *__csviter::next() {
    return csvfile->next()->strip()->split(new str(","));
}

__csviter *reader::__iter__() {
    return new __csviter(csvfile);
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

