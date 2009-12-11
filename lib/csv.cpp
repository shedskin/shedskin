#include "csv.hpp"

namespace __csv__ {

str *const_0;

str *__name__;
OSError *__exception;

/**
class reader
*/

class_ *cl_reader;

__csviter::__csviter(reader *r) {
    this->r = r;
}

list<str *> *__csviter::next() {
    return NULL; //r->next()->strip()->split(new str(","));
}

__csviter *reader::__iter__() {
    return new __csviter(this);
}

void *reader::__init__(file *input_iter) {

    this->input_iter = input_iter;
    return NULL;
}

void __init() {
    const_0 = new str(",");

    __name__ = new str("csv");

    cl_reader = new class_("reader", 40, 40);

}

} // module namespace

