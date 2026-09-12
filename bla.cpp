#include "builtin.hpp"
#include "bla.hpp"

namespace __bla__ {


file *__file;
__ss_int __void;
str *__name__;
Loader *l;


static inline list<Entry *> *list_comp_0(__ss_int n);
static inline list<__ss_int> *list_comp_1();
static inline tuple2<__ss_int, Entry *> *__lambda0__(Entry *entry);

static inline list<Entry *> *list_comp_0(__ss_int n) {
    __ss_int __0, __1, i;

    list<Entry *> *__ss_result = new list<Entry *>();

    __SS_LIST_RESERVE(__ss_result, 4);
    FAST_FOR(i,0,n,1,0,1)
        __ss_result->append((new Entry(i)));
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_1() {
    Entry *e;
    list<Entry *> *__11;
    __iter<Entry *> *__12;
    __ss_int __13;
    list<Entry *>::for_in_loop __14;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __11 = __bla__::l->entries;
    __ss_result->resize(len(__11));
    FOR_IN(e,__11,11,13,14)
        __ss_result->units[__13] = e->end_addr;
    END_FOR

    return __ss_result;
}

static inline tuple2<__ss_int, Entry *> *__lambda0__(Entry *entry) {
    return (new tuple2<__ss_int, Entry *>(2,entry->tape_pos,entry));
}

/**
class Entry
*/

class_ *cl_Entry;

void *Entry::__init__(__ss_int pos) {
    this->tape_pos = pos;
    this->end_addr = __ss_int(0LL);
    return NULL;
}

/**
class Loader
*/

class_ *cl_Loader;

void *Loader::__init__() {
    this->entries = (__ss_list<Entry *, 0>());
    this->offsets = (__ss_list<tuple2<__ss_int, Entry *> *, 1>());
    return NULL;
}

Loader *Loader::parse(__ss_int n) {
    __ss_int __5, size;
    Entry *entry;
    tuple2<__ss_int, Entry *> *__2;
    list<tuple2<__ss_int, Entry *> *> *__3;
    __iter<tuple2<__ss_int, Entry *> *> *__4;
    list<tuple2<__ss_int, Entry *> *>::for_in_loop __6;

    this->entries = list_comp_0(n);
    this->offsets = sorted(map(1, False, __lambda0__, this->entries), __ss_int(0LL), __ss_int(0LL), __ss_int(0LL));
    (this->offsets)->append((new tuple2<__ss_int, Entry *>(2,__ss_int(99LL),NULL)));

    FOR_IN(__2,find_distances(this->offsets),3,5,6)
        __2 = __2;
        __SS_UNPACK_CHECK(__2, 2);
        size = __2->__getfirst__();
        entry = __2->__getsecond__();
        entry->end_addr = (entry->tape_pos+size);
    END_FOR

    return this;
}

list<tuple2<__ss_int, Entry *> *> *find_distances(list<tuple2<__ss_int, Entry *> *> *items) {
    tuple2<__ss_int, Entry *> *__7, *__9, *h, *hh;
    list<tuple2<__ss_int, Entry *> *> *__10, *__8, *t, *tt;

    __7 = items->__getfast__(__ss_int(0LL));
    __8 = items->__slice__(__ss_int(1LL), __ss_int(1LL), __ss_int(0LL), __ss_int(0LL));
    h = __7;
    t = __8;
    if ((len(t)==__ss_int(0LL))) {
        return (__ss_list<tuple2<__ss_int, Entry *> *, 2>());
    }
    else {
        __9 = t->__getfast__(__ss_int(0LL));
        __10 = t->__slice__(__ss_int(1LL), __ss_int(1LL), __ss_int(0LL), __ss_int(0LL));
        hh = __9;
        tt = __10;
        return ((new list<tuple2<__ss_int, Entry *> *>(1,(new tuple2<__ss_int, Entry *>(2,(hh->__getfirst__()-h->__getfirst__()),h->__getsecond__())))))->__add__(find_distances(t));
    }
    return 0;
}

void __init() {
    __name__ = new str("__main__");


    cl_Entry = new class_("Entry");
    cl_Loader = new class_("Loader");
    l = ((new Loader(1)))->parse(__ss_int(3LL));
    print(list_comp_1());
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __shedskin__::__start(__bla__::__init);
}
