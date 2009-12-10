#ifndef __CSV_HPP
#define __CSV_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __csv__ {

extern str *const_0, *const_1, *const_2, *const_3;

class reader;

extern str *__name__;
extern OSError *__exception;

extern class_ *cl_reader;
class reader : public pyobj {
public:
    int count;

    reader() {}
    reader(file *csvfile) {
        this->__class__ = cl_reader;
        __init__(csvfile);
    }
    list<str *> *next();
    reader *__iter__();
    void *__init__(file *csvfile);
};

void __init();

} // module namespace
#endif
