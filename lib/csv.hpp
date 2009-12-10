#ifndef __CSV_HPP
#define __CSV_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __csv__ {

extern str *const_0;

class reader;

extern str *__name__;
extern OSError *__exception;

class __csviter : public __iter<list<str *> *> {
public:
    file *csvfile;
    __csviter(file *csvfile) { this->csvfile = csvfile; }
    list<str *> *next() {
        return csvfile->next()->split();
    }
};

extern class_ *cl_reader;
class reader : public pyiter<list<str *> *> {
public:
    file *csvfile;

    reader() {}
    reader(file *csvfile) {
        this->__class__ = cl_reader;
        __init__(csvfile);
    }
    __iter<list<str *> *> *next();
    __csviter *__iter__();
    void *__init__(file *csvfile);
};

void __init();

} // module namespace
#endif
