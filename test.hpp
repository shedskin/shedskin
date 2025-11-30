#ifndef __TEST_HPP
#define __TEST_HPP

using namespace __shedskin__;
namespace __test__ {

extern str *const_0;

class Vector;


extern str *__name__;


extern class_ *cl_Vector;
class Vector : public pyobj {
public:
    __ss_int x;
    __ss_int y;
    __ss_int z;

    Vector() {}
    Vector(__ss_int x, __ss_int y, __ss_int z) {
        this->__class__ = cl_Vector;
        __init__(x, y, z);
    }
    void *__init__(__ss_int x, __ss_int y, __ss_int z);
};

__ss_int woef(__ss_int x, __ss_int y, __ss_int z);
void *__ss_main();

} // module namespace
#endif
