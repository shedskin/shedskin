#ifndef __BLA_HPP
#define __BLA_HPP

using namespace __shedskin__;
namespace __bla__ {

class Entry;
class Loader;

typedef tuple2<__ss_int, Entry *> *(*lambda0)(Entry *);

extern file *__file;
extern __ss_int __void;
extern str *__name__;
extern Loader *l;


extern class_ *cl_Entry;
class Entry : public pyobj {
public:
    __ss_int end_addr;
    __ss_int tape_pos;

    Entry() {}
    Entry(__ss_int pos) {
        this->__class__ = cl_Entry;
        __init__(pos);
    }
    void *__init__(__ss_int pos);
};

extern class_ *cl_Loader;
class Loader : public pyobj {
public:
    list<Entry *> *entries;
    list<tuple2<__ss_int, Entry *> *> *offsets;

    Loader() {}
    Loader(int __ss_init) {
        this->__class__ = cl_Loader;
        __init__();
    }
    void *__init__();
    Loader *parse(__ss_int n);
};

list<tuple2<__ss_int, Entry *> *> *find_distances(list<tuple2<__ss_int, Entry *> *> *items);

} // module namespace
#endif
