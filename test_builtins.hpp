#ifndef __TEST_BUILTINS_HPP
#define __TEST_BUILTINS_HPP

using namespace __shedskin__;
namespace __test_builtins__ {

extern str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_26, *const_27, *const_28, *const_29, *const_30, *const_31, *const_8, *const_9;
extern bytes *const_2, *const_3, *const_4, *const_5, *const_6, *const_7;

class Klass;
class SubKlass;
class Bert;
class MyString;
class Account;

typedef void *(*lambda0)(void *, void *, void *, void *, void *);
typedef __ss_bool (*lambda1)(__ss_int);
typedef __ss_int (*lambda2)(__ss_int);
typedef str *(*lambda3)(__ss_int);
typedef __ss_int (*lambda4)(__ss_int);
typedef __ss_int (*lambda5)(__ss_int);
typedef __ss_int (*lambda6)(__ss_int);
typedef __ss_int (*lambda7)(__ss_int);
typedef __ss_int (*lambda8)(__ss_int);

extern __ss_int __void;
extern str *__name__;


extern class_ *cl_Klass;
class Klass : public pyobj {
public:
    str *name;

    Klass() {}
    Klass(str *name) {
        this->__class__ = cl_Klass;
        __init__(name);
    }
    void *__init__(str *name);
};

extern class_ *cl_SubKlass;
class SubKlass : public Klass {
public:
    SubKlass() { this->__class__ = cl_SubKlass; }
    static void __static__();
};

extern class_ *cl_Bert;
class Bert : public pyobj {
public:
    Bert() { this->__class__ = cl_Bert; }
    __ss_int __index__();
};

extern class_ *cl_MyString;
class MyString : public pyobj {
public:
    MyString() { this->__class__ = cl_MyString; }
};

extern class_ *cl_Account;
class Account : public pyobj {
public:
    __ss_int _cash;

    Account() {}
    Account(int __ss_init) {
        this->__class__ = cl_Account;
        __init__();
    }
    void *__init__();
    __ss_int cash();
    void *cash__setter__(__ss_int amount);
};

void *test_abs();
void *test_bin();
void *test_bool();
void *test_bytes();
void *test_chr();
void *test_complex();
void *test_divmod();
void *test_enumerate();
void *test_filter();
void *test_float();
void *test_hash();
void *test_int();
void *test_int_base();
void *test_hex();
void *test_isinstance();
void *test_len();
void *test_max();
void *test_min();
void *test_oct();
void *test_ord();
void *test_property();
void *test_print();
void *test_range();
void *test_range_slicing();
void *test_repr();
void *test_reversed();
void *test_round();
void *test_set();
void *test_str();
void *test_sum();
void *test_tuple();
void *test_zip();
void *test_all();

} // module namespace
#endif
