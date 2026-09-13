#include "builtin.hpp"
#include "amaze_min.hpp"

namespace __amaze_min__ {


file *__file;
__ss_int __void;
str *__name__;



/**
class Solver
*/

class_ *cl_Solver;

void *Solver::__init__() {
    this->_current = (__ss_tuple_int(2,__ss_int(0LL),__ss_int(0LL)));
    return NULL;
}

list<tuple<__ss_int> *> *Solver::neighbours(tuple<__ss_int> *pt) {
    __ss_int x, y;
    tuple<__ss_int> *__0;

    __0 = pt;
    __SS_UNPACK_CHECK(__0, 2);
    x = __0->__getfirst__();
    y = __0->__getsecond__();
    return (new list<tuple<__ss_int> *>(1,(__ss_tuple_int(2,(x-__ss_int(1LL)),y))));
}

void *Solver::solve(__ss_bool flag) {
    tuple<__ss_int> *pt;

    pt = (this->neighbours(this->_current))->__getfast__(__ss_int(0LL));
    if (flag) {
        pt = NULL;
    }
    this->_current = pt;
    return NULL;
}

void __init() {
    __name__ = new str("__main__");


    cl_Solver = new class_("Solver");
    ((new Solver(1)))->solve(False);
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __shedskin__::__start(__amaze_min__::__init);
}
