#ifndef __CLAUDE_MIN_HPP
#define __CLAUDE_MIN_HPP

using namespace __shedskin__;
namespace __claude_min__ {

class C;


extern file *__file;
extern __ss_int __void;
extern str *__name__;


extern class_ *cl_C;
class C : public pyobj {
public:

    C() { this->__class__ = cl_C; }
    void *f(__ss_int x);
};


} // module namespace
#endif
