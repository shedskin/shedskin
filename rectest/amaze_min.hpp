#ifndef __AMAZE_MIN_HPP
#define __AMAZE_MIN_HPP

using namespace __shedskin__;
namespace __amaze_min__ {

class Solver;


extern file *__file;
extern __ss_int __void;
extern str *__name__;


extern class_ *cl_Solver;
class Solver : public pyobj {
public:
    tuple<__ss_int> *_current;

    Solver() {}
    Solver(int __ss_init) {
        this->__class__ = cl_Solver;
        __init__();
    }
    void *__init__();
    list<tuple<__ss_int> *> *neighbours(tuple<__ss_int> *pt);
    void *solve(__ss_bool flag);
};


} // module namespace
#endif
