#include "builtin.hpp"
#include "test_builtins.hpp"

/**
not implemented:
aiter
anext
ascii
breakpoint
callable
classmethod
compile
copyright
credits
delattr
dir
display
eval
exec
format
getattr
globals
hasattr
help
id
input
locals
memoryview
setattr
super
type
vars
*/

namespace __test_builtins__ {

str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_26, *const_27, *const_28, *const_29, *const_30, *const_31, *const_8, *const_9;
bytes *const_2, *const_3, *const_4, *const_5, *const_6, *const_7;


__ss_int __void;
str *__name__;


static inline list<tuple2<__ss_int, str *> *> *list_comp_0();
static inline __ss_bool __lambda1__(__ss_int x);
static inline __ss_int __lambda2__(__ss_int x);
static inline str *__lambda3__(__ss_int a);
static inline __ss_int __lambda4__(__ss_int y);
static inline __ss_int __lambda5__(__ss_int y);
static inline __ss_int __lambda6__(__ss_int x);
static inline __ss_int __lambda7__(__ss_int a);
static inline __ss_int __lambda8__(__ss_int u);

static inline list<tuple2<__ss_int, str *> *> *list_comp_0() {
    tuple2<__ss_int, str *> *__0;
    __ss_int __3, i;
    str *obj;
    __iter<tuple2<__ss_int, str *> *> *__1, *__2;
    list<str *> *__4;
    __iter<tuple2<__ss_int, str *> *>::for_in_loop __5;

    list<tuple2<__ss_int, str *> *> *__ss_result = new list<tuple2<__ss_int, str *> *>();

    FOR_IN_ENUMERATE(obj,(new list<str *>(3,const_8,const_11,const_12)),4,3)
        i = __3;
        __ss_result->append((new tuple2<__ss_int, str *>(2,i,obj)));
    END_FOR

    return __ss_result;
}

static inline __ss_bool __lambda1__(__ss_int x) {
    return ___bool((x>__ss_int(10)));
}

static inline __ss_int __lambda2__(__ss_int x) {
    return (-x);
}

static inline str *__lambda3__(__ss_int a) {
    return __str(a);
}

static inline __ss_int __lambda4__(__ss_int y) {
    return (-y);
}

static inline __ss_int __lambda5__(__ss_int y) {
    return (-y);
}

static inline __ss_int __lambda6__(__ss_int x) {
    return (-x);
}

static inline __ss_int __lambda7__(__ss_int a) {
    return __int(a);
}

static inline __ss_int __lambda8__(__ss_int u) {
    return (-u);
}

/**
class Klass
*/

class_ *cl_Klass;

void *Klass::__init__(str *name) {
    this->name = name;
    return NULL;
}

/**
class SubKlass
*/

class_ *cl_SubKlass;

void SubKlass::__static__() {
}

void *test_abs() {
    ASSERT(___bool((__abs((-__ss_int(10)))==__ss_int(10))), 0);
    return NULL;
}

/**
class Bert
*/

class_ *cl_Bert;

__ss_int Bert::__index__() {
    return __ss_int(77);
}

void *test_bin() {
    ASSERT(___bool(__eq(bin(__ss_int(3)), const_1)), 0);
    return NULL;
}

void *test_bool() {
    ASSERT(___bool((___bool(___bool((__ss_int(2)>__ss_int(1))))==True)), 0);
    return NULL;
}

/**
class MyString
*/

class_ *cl_MyString;

void *test_bytes() {
    ASSERT(___bool(__eq(__bytes(), const_2)), 0);
    ASSERT(___bool(__eq(__bytes((new list<__ss_int>(3,__ss_int(1),__ss_int(2),__ss_int(3)))), const_3)), 0);
    ASSERT(___bool(__eq(__bytes((new set<__ss_int>((new list<__ss_int>(1,__ss_int(1)))))), const_4)), 0);
    ASSERT(___bool(__eq(__bytes(__ss_int(0)), const_2)), 0);
    ASSERT(___bool(__eq(__bytes(__ss_int(4)), const_5)), 0);
    ASSERT(___bool(__eq(__bytes(__ss_int(7)), const_6)), 0);
    ASSERT(___bool(__eq(__bytes(const_7), const_7)), 0);
    ASSERT(___bool(__eq(__bytes(__bytes(__ss_int(7))), const_6)), 0);
    return NULL;
}

void *test_chr() {
    ASSERT(___bool(__eq(chr(__ss_int(97)), const_8)), 0);
    ASSERT(___bool(__eq(chr(True), const_9)), 0);
    ASSERT(___bool(__eq(chr((new Bert())), const_10)), 0);
    return NULL;
}

void *test_complex() {
    complex a;

    a = mcomplex(__ss_int(1), __ss_int(2));
    ASSERT(___bool((a.imag==__ss_float(2.0))), 0);
    ASSERT(___bool((a.real==__ss_float(1.0))), 0);
    return NULL;
}

void *test_divmod() {
    ASSERT(___bool(__eq(divmod(__ss_int(10), __ss_int(2)), (__ss_tuple_int(2,__ss_int(5),__ss_int(0))))), 0);
    ASSERT(___bool(__eq(divmod((-__ss_int(496)), __ss_int(3)), (__ss_tuple_int(2,(-__ss_int(166)),__ss_int(2))))), 0);
    ASSERT(___bool(__eq(divmod((-__ss_float(496.0)), __ss_int(3)), (new tuple<__ss_float>(2,(-__ss_float(166.0)),__ss_float(2.0))))), 0);
    ASSERT(___bool(__eq(divmod((-__ss_int(496)), __ss_float(3.0)), (new tuple<__ss_float>(2,(-__ss_float(166.0)),__ss_float(2.0))))), 0);
    ASSERT(___bool(__eq(divmod((-__ss_int(496)), (-__ss_int(3))), (__ss_tuple_int(2,__ss_int(165),(-__ss_int(1)))))), 0);
    ASSERT(___bool(__eq(divmod((-__ss_float(496.0)), (-__ss_float(3.0))), (new tuple<__ss_float>(2,__ss_float(165.0),(-__ss_float(1.0)))))), 0);
    return NULL;
}

void *test_enumerate() {
    ASSERT(___bool(__eq(list_comp_0(), (new list<tuple2<__ss_int, str *> *>(3,(new tuple2<__ss_int, str *>(2,__ss_int(0),const_8)),(new tuple2<__ss_int, str *>(2,__ss_int(1),const_11)),(new tuple2<__ss_int, str *>(2,__ss_int(2),const_12)))))), 0);
    return NULL;
}

void *test_filter() {
    lambda1 is_gt_10;
    __xrange *xs;

    is_gt_10 = __lambda1__;
    xs = range(__ss_int(12));
    ASSERT(___bool(__eq((new list<__ss_int>(filter(is_gt_10, xs))), (new list<__ss_int>(1,__ss_int(11))))), 0);
    return NULL;
}

void *test_float() {
    ASSERT(___bool((__float(__ss_int(100))==__ss_float(100.0))), 0);
    return NULL;
}

void *test_hash() {
    ASSERT(___bool((hasher(const_13)==hasher(const_13))), 0);
    ASSERT(___bool((hasher(const_13)!=hasher(const_14))), 0);
    return NULL;
}

void *test_int() {
    ASSERT(___bool((__int(__ss_float(100.2))==__ss_int(100))), 0);
    ASSERT(___bool((__ss_bit_count(__ss_int(12345))==__ss_int(6))), 0);
    return NULL;
}

void *test_int_base() {
    ASSERT(___bool((__int(const_15, __ss_int(16))==__ss_int(255))), 0);
    ASSERT(___bool((__int(const_15, __ss_int(16))==__ss_int(255))), 0);
    ASSERT(___bool((__int(const_16, __ss_int(2))==__ss_int(5))), 0);
    ASSERT(___bool((__int(const_17, __ss_int(0))==__ss_int(26))), 0);
    ASSERT(___bool((__int(const_18)==__ss_int(42))), 0);
    ASSERT(___bool((__ss_bit_count(__ss_int(4294967295))==__ss_int(32))), 0);
    return NULL;
}

void *test_hex() {
    ASSERT(___bool(__eq(hex(__ss_int(1)), const_19)), 0);
    return NULL;
}

void *test_isinstance() {
    Klass *obj;

    obj = (new Klass(const_20));
    ASSERT(True, 0);
    return NULL;
}

void *test_len() {
    ASSERT(___bool((len((new list<__ss_int>(3,__ss_int(1),__ss_int(2),__ss_int(3))))==__ss_int(3))), 0);
    return NULL;
}

void *test_max() {
    list<__ss_int> *xs;
    lambda2 neg;
    __ss_int __7;

    ASSERT(___bool((___max(0, __ss_void, __ss_int(0), (new list<__ss_int>(4,__ss_int(4),__ss_int(5),__ss_int(9),__ss_int(12))))==__ss_int(12))), 0);
    ASSERT(___bool((___max(0, __ss_void, __ss_int(0), (new list<__ss_float>(4,__ss_float(1.2),__ss_float(3.14),__ss_float(5.56),__ss_float(9.31))))==__ss_float(9.31))), 0);
    ASSERT(___bool(__eq(___max(0, __ss_void, __ss_int(0), (new list<str *>(3,const_8,const_11,const_12))), const_12)), 0);
    ASSERT(___bool((___max(0, __ss_void, __ss_int(0), (new dict<__ss_int, __ss_int>(2, (new tuple<__ss_int >(2,__ss_int(1),__ss_int(2))),(new tuple<__ss_int >(2,__ss_int(3),__ss_int(4))))))==__ss_int(3))), 0);
    ASSERT(___bool((___max(0, __ss_void, __ss_int(0), (new list<__ss_int>(1,__ss_int(1))))==__ss_int(1))), 0);
    ASSERT(___bool((___max(2, __ss_void, __ss_int(0), __ss_int(1), __ss_int(2))==__ss_int(2))), 0);
    ASSERT(___bool((___max(2, __ss_void, (__ss_float(__ss_int(0))), __ss_float(7.7), (__ss_float(__ss_int(7))))==__ss_float(7.7))), 0);
    ASSERT(___bool((___max(2, __ss_void, (__ss_float(__ss_int(0))), (__ss_float(__ss_int(7))), __ss_float(7.7))==__ss_float(7.7))), 0);
    ASSERT(___bool((___max(3, __ss_void, __ss_int(0), __ss_int(1), __ss_int(2), __ss_int(3))==__ss_int(3))), 0);
    ASSERT(___bool((___max(5, __ss_void, __ss_int(0), __ss_int(1), __ss_int(2), __ss_int(3), __ss_int(4), __ss_int(5))==__ss_int(5))), 0);
    xs = (new list<__ss_int>(3,__ss_int(1),__ss_int(2),__ss_int(3)));
    neg = __lambda2__;
    ASSERT(___bool((___max(2, __ss_void, __ss_int(0), __ss_int(1), __ss_int(2))==__ss_int(2))), 0);
    ASSERT(___bool((___max(3, __ss_void, __ss_int(0), __ss_int(1), __ss_int(2), __ss_int(3))==__ss_int(3))), 0);
    ASSERT(___bool((___max(3, __ss_void, neg, __ss_int(1), __ss_int(2), __ss_int(3))==__ss_int(1))), 0);
    ASSERT(___bool((___max(3, __ss_void, __lambda3__, __ss_int(1), __ss_int(2), __ss_int(3))==__ss_int(3))), 0);
    ASSERT(___bool((___max(2, __ss_void, neg, __ss_int(1), __ss_int(2))==__ss_int(1))), 0);
    ASSERT(___bool((___max(0, __ss_void, __ss_int(0), xs)==__ss_int(3))), 0);
    ASSERT(___bool((___max(0, __ss_void, neg, xs)==__ss_int(1))), 0);
    ASSERT(___bool((___max(0, __ss_void, __lambda4__, xs)==__ss_int(1))), 0);
    xs = (__ss_list<__ss_int>());
    ASSERT(___bool((___max(0, __ss_int(7), __ss_int(0), xs)==__ss_int(7))), 0);
    ASSERT(___bool((___max(0, __ss_int(7), __lambda5__, xs)==__ss_int(7))), 0);
    try {
        __7 = 0;
        ___max(0, __ss_void, __ss_int(0), xs);
        __7 = 1;
    } catch (ValueError *) {
    }
    if(__7) { // else
        ASSERT(False, 0);
    }
    return NULL;
}

void *test_min() {
    list<__ss_int> *xs;
    lambda6 neg;

    ASSERT(___bool((___min(0, (new list<__ss_int>(1,__ss_int(1))))==__ss_int(1))), 0);
    ASSERT(___bool((___min(2, __ss_int(0), __ss_int(1), __ss_int(2))==__ss_int(1))), 0);
    ASSERT(___bool((___min(2, (__ss_float(__ss_int(0))), __ss_float(6.7), (__ss_float(__ss_int(7))))==__ss_float(6.7))), 0);
    ASSERT(___bool((___min(2, (__ss_float(__ss_int(0))), (__ss_float(__ss_int(7))), __ss_float(6.7))==__ss_float(6.7))), 0);
    ASSERT(___bool((___min(3, __ss_int(0), __ss_int(1), __ss_int(2), __ss_int(3))==__ss_int(1))), 0);
    ASSERT(___bool((___min(5, __ss_int(0), __ss_int(1), __ss_int(2), __ss_int(3), __ss_int(4), __ss_int(5))==__ss_int(1))), 0);
    ASSERT(___bool((___min(0, (new list<__ss_int>(4,__ss_int(4),__ss_int(5),__ss_int(9),__ss_int(12))))==__ss_int(4))), 0);
    ASSERT(___bool((___min(0, (new list<__ss_float>(4,__ss_float(1.2),__ss_float(3.14),__ss_float(5.56),__ss_float(9.31))))==__ss_float(1.2))), 0);
    ASSERT(___bool(__eq(___min(0, (new list<str *>(3,const_8,const_11,const_12))), const_8)), 0);
    xs = (new list<__ss_int>(3,__ss_int(1),__ss_int(2),__ss_int(3)));
    neg = __lambda6__;
    ASSERT(___bool((___min(2, __ss_int(0), __ss_int(1), __ss_int(2))==__ss_int(1))), 0);
    ASSERT(___bool((___min(3, __ss_int(0), __ss_int(1), __ss_int(2), __ss_int(3))==__ss_int(1))), 0);
    ASSERT(___bool((___min(3, __lambda7__, __ss_int(1), __ss_int(2), __ss_int(3))==__ss_int(1))), 0);
    ASSERT(___bool((___min(3, neg, __ss_int(1), __ss_int(2), __ss_int(3))==__ss_int(3))), 0);
    ASSERT(___bool((___min(2, neg, __ss_int(1), __ss_int(2))==__ss_int(2))), 0);
    ASSERT(___bool((___min(0, xs)==__ss_int(1))), 0);
    ASSERT(___bool((___min(0, neg, xs)==__ss_int(3))), 0);
    ASSERT(___bool((___min(0, __lambda8__, xs)==__ss_int(3))), 0);
    return NULL;
}

void *test_oct() {
    ASSERT(___bool(__eq(oct(__ss_int(10)), const_21)), 0);
    return NULL;
}

void *test_ord() {
    ASSERT(___bool((ord(const_8)==__ss_int(97))), 0);
    ASSERT(___bool((ord(const_22)==__ss_int(122))), 0);
    ASSERT(___bool((ord(const_23)==__ss_int(49))), 0);
    ASSERT(___bool((ord(const_24)==__ss_int(57))), 0);
    return NULL;
}

/**
class Account
*/

class_ *cl_Account;

void *Account::__init__() {
    this->_cash = __ss_int(0);
    return NULL;
}

__ss_int Account::cash() {
    return this->_cash;
}

void *Account::cash__setter__(__ss_int amount) {
    this->_cash = amount;
    return NULL;
}

void *test_property() {
    Account *a;

    a = (new Account(1));
    ASSERT(___bool((a->cash()==__ss_int(0))), 0);
    a->cash__setter__(__ss_int(10));
    ASSERT(___bool((a->cash()==__ss_int(10))), 0);
    return NULL;
}

void *test_print() {
    print(const_25);
    print(const_26);
    print(NULL);
    print((new set<__ss_int>(2,__ss_int(1),__ss_int(2))));
    print((__ss_list<void *>()));
    print_(2, False, NULL, const_27, const_28, __ss_int(1), __ss_float(2.2));
    print();
    ASSERT(True, 0);
    return NULL;
}

void *test_range() {
    __ss_int a;
    __xrange *r;

    a = __ss_int(1);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),__ss_int(1)), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(10),__ss_int(1),(-__ss_int(1))), (new list<__ss_int>(9,__ss_int(10),__ss_int(9),__ss_int(8),__ss_int(7),__ss_int(6),__ss_int(5),__ss_int(4),__ss_int(3),__ss_int(2))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),(+__ss_int(1))), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),a), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(10),__ss_int(1),(-a)), (new list<__ss_int>(9,__ss_int(10),__ss_int(9),__ss_int(8),__ss_int(7),__ss_int(6),__ss_int(5),__ss_int(4),__ss_int(3),__ss_int(2))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),(+a)), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),(a*__ss_int(1))), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),(-(-__ss_int(1)))), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),(+(+a))), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),__ss_int(1)), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),(+__ss_int(1))), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),a), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),(+a)), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),(-(-__ss_int(1)))), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),(+(+__ss_int(1)))), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),(+(+a))), (new list<__ss_int>(9,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(7),__ss_int(8),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(10),__ss_int(1),(-__ss_int(1))), (new list<__ss_int>(9,__ss_int(10),__ss_int(9),__ss_int(8),__ss_int(7),__ss_int(6),__ss_int(5),__ss_int(4),__ss_int(3),__ss_int(2))))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(10),__ss_int(1),(-a)), (new list<__ss_int>(9,__ss_int(10),__ss_int(9),__ss_int(8),__ss_int(7),__ss_int(6),__ss_int(5),__ss_int(4),__ss_int(3),__ss_int(2))))), 0);
    ASSERT(___bool((len(range(__ss_int(5)))==__ss_int(5))), 0);
    ASSERT(___bool((___max(0, __ss_void, __ss_int(0), range(__ss_int(10)))==__ss_int(9))), 0);
    ASSERT(___bool((___min(0, range(__ss_int(10)))==__ss_int(0))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(3)), (new list<__ss_int>(3,__ss_int(0),__ss_int(1),__ss_int(2))))), 0);
    ASSERT(___bool((__sum(range(__ss_int(20)))==__ss_int(190))), 0);
    ASSERT(___bool(__eq(__ss_list_range(__ss_int(1),__ss_int(10),__ss_int(2)), (new list<__ss_int>(5,__ss_int(1),__ss_int(3),__ss_int(5),__ss_int(7),__ss_int(9))))), 0);
    ASSERT(___bool(__eq(__ss_list_range((-__ss_int(17)),(-__ss_int(120)),(-__ss_int(17))), (new list<__ss_int>(7,(-__ss_int(17)),(-__ss_int(34)),(-__ss_int(51)),(-__ss_int(68)),(-__ss_int(85)),(-__ss_int(102)),(-__ss_int(119)))))), 0);
    r = range(__ss_int(4), __ss_int(10), __ss_int(2));
    ASSERT(___bool((r->start==__ss_int(4))), 0);
    ASSERT(___bool((r->stop==__ss_int(10))), 0);
    ASSERT(___bool((r->step==__ss_int(2))), 0);
    ASSERT(___bool((r)->__contains__(__ss_int(8))), 0);
    ASSERT(___bool((!(r)->__contains__(__ss_int(9)))), 0);
    r = range(__ss_int(1), __ss_int(10));
    ASSERT(___bool((r->count(__ss_int(7))==__ss_int(1))), 0);
    ASSERT(___bool((r->count(__ss_int(77))==__ss_int(0))), 0);
    ASSERT(___bool((r->index(__ss_int(7))==__ss_int(6))), 0);
    ASSERT(___bool((r->__getitem__(__ss_int(7))==__ss_int(8))), 0);
    ASSERT(___bool(r), 0);
    ASSERT(__NOT(___bool(range(__ss_int(0)))), 0);
    return NULL;
}

void *test_range_slicing() {
    __xrange *r;

    r = range(__ss_int(2), __ss_int(20), __ss_int(2));
    ASSERT(___bool(__eq((new list<__ss_int>(r->__slice__(__ss_int(7), __ss_int(2), __ss_int(4), __ss_int(3)))), (new list<__ss_int>(1,__ss_int(6))))), 0);
    ASSERT(___bool(__eq((new list<__ss_int>(r->__slice__(__ss_int(4), __ss_int(0), __ss_int(0), __ss_int(2)))), (new list<__ss_int>(5,__ss_int(2),__ss_int(6),__ss_int(10),__ss_int(14),__ss_int(18))))), 0);
    ASSERT(___bool(__eq((new list<__ss_int>(r->__slice__(__ss_int(3), __ss_int(1), __ss_int(5), __ss_int(0)))), (new list<__ss_int>(4,__ss_int(4),__ss_int(6),__ss_int(8),__ss_int(10))))), 0);
    ASSERT(___bool(__eq((new list<__ss_int>(r->__slice__(__ss_int(3), (-__ss_int(5)), (-__ss_int(2)), __ss_int(0)))), (new list<__ss_int>(3,__ss_int(10),__ss_int(12),__ss_int(14))))), 0);
    ASSERT(___bool(__eq((new list<__ss_int>(r->__slice__(__ss_int(3), __ss_int(4), __ss_int(1), __ss_int(0)))), (__ss_list<__ss_int>()))), 0);
    ASSERT(___bool(__eq((new list<__ss_int>(r->__slice__(__ss_int(7), __ss_int(4), __ss_int(1), (-__ss_int(2))))), (new list<__ss_int>(2,__ss_int(10),__ss_int(6))))), 0);
    r = range((-__ss_int(5)), (-__ss_int(5)), (-__ss_int(5)));
    ASSERT(___bool(__eq((new list<__ss_int>(r->__slice__(__ss_int(7), (-__ss_int(5)), (-__ss_int(4)), __ss_int(1)))), (__ss_list<__ss_int>()))), 0);
    return NULL;
}

void *test_repr() {
    ASSERT(___bool(__eq(repr(__ss_int(1)), const_23)), 0);
    ASSERT(___bool(__eq(repr(__ss_float(1.1)), const_29)), 0);
    return NULL;
}

void *test_reversed() {
    ASSERT(___bool(__eq((new list<__ss_int>(reversed((new list<__ss_int>(3,__ss_int(1),__ss_int(2),__ss_int(3)))))), (new list<__ss_int>(3,__ss_int(3),__ss_int(2),__ss_int(1))))), 0);
    ASSERT(___bool(__eq((new list<str *>(reversed((new list<str *>(3,const_8,const_11,const_12))))), (new list<str *>(3,const_12,const_11,const_8)))), 0);
    return NULL;
}

void *test_round() {
    ASSERT(___bool((___round(__ss_float(0.5))==((__ss_float)(__ss_int(0))))), 0);
    ASSERT(___bool((___round(__ss_float(1.5))==((__ss_float)(__ss_int(2))))), 0);
    ASSERT(___bool((___round(__ss_float(2.5))==((__ss_float)(__ss_int(2))))), 0);
    ASSERT(___bool((___round(__ss_float(3.5))==((__ss_float)(__ss_int(4))))), 0);
    ASSERT(___bool((___round(__ss_float(4.5))==((__ss_float)(__ss_int(4))))), 0);
    ASSERT(___bool((___round((-__ss_float(1.5)))==((__ss_float)((-__ss_int(2)))))), 0);
    ASSERT(___bool((___round((-__ss_float(2.5)))==((__ss_float)((-__ss_int(2)))))), 0);
    ASSERT(___bool((___round((-__ss_float(3.5)))==((__ss_float)((-__ss_int(4)))))), 0);
    ASSERT(___bool((___round((-__ss_float(4.5)))==((__ss_float)((-__ss_int(4)))))), 0);
    ASSERT(___bool((___round(__ss_float(1.15), __ss_int(0))==__ss_float(1.0))), 0);
    return NULL;
}

void *test_set() {
    ASSERT(___bool(__eq((new list<__ss_int>(((new set<__ss_int>((new list<__ss_int>(4,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4))))))->difference(1, (new set<__ss_int>((new list<__ss_int>(1,__ss_int(3)))))))), (new list<__ss_int>(3,__ss_int(1),__ss_int(2),__ss_int(4))))), 0);
    return NULL;
}

void *test_str() {
    ASSERT(___bool(__eq(__str(__ss_int(1)), const_23)), 0);
    ASSERT(___bool(__eq(__str(__ss_float(1.5)), const_30)), 0);
    return NULL;
}

void *test_sum() {
    list<__ss_int> *a;

    ASSERT(___bool((__sum((new list<__ss_float>(2,__ss_float(1.0),__ss_float(5.0))))==__ss_float(6.0))), 0);
    ASSERT(___bool((__sum(range(__ss_int(100)))==__ss_int(4950))), 0);
    ASSERT(___bool((__sum((new list<__ss_int>(3,__ss_int(1),__ss_int(2),__ss_int(3))))==__ss_int(6))), 0);
    ASSERT(___bool((__sum((new list<__ss_int>(3,__ss_int(1),__ss_int(2),__ss_int(3))), __ss_int(4))==__ss_int(10))), 0);
    ASSERT(___bool(__eq(__sum((new list<list<__ss_int> *>(3,(new list<__ss_int>(1,__ss_int(1))),(new list<__ss_int>(1,__ss_int(2))),(new list<__ss_int>(2,__ss_int(3),__ss_int(4))))), (new list<__ss_int>(1,__ss_int(0)))), (new list<__ss_int>(5,__ss_int(0),__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4))))), 0);
    ASSERT(___bool(__eq(__sum((new list<list<__ss_int> *>(3,(new list<__ss_int>(1,__ss_int(1))),(new list<__ss_int>(1,__ss_int(2))),(new list<__ss_int>(2,__ss_int(3),__ss_int(4))))), (__ss_list<void *>())), (new list<__ss_int>(4,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4))))), 0);
    a = (new list<__ss_int>(3,__ss_int(1),__ss_int(2),__ss_int(3)));
    a = (__ss_list<__ss_int>());
    ASSERT(___bool(__eq(__sum(a, __ss_int(7)), __ss_int(7))), 0);
    return NULL;
}

void *test_tuple() {
    ASSERT(___bool(__eq((new tuple<__ss_int>((new list<__ss_int>(2,__ss_int(1),__ss_int(2))))), (__ss_tuple_int(2,__ss_int(1),__ss_int(2))))), 0);
    return NULL;
}

void *test_zip() {
    ASSERT(___bool(__eq((new list<tuple<__ss_int> *>(__zip(1, False, (new list<__ss_int>(2,__ss_int(1),__ss_int(2)))))), (new list<tuple<__ss_int> *>(2,(new tuple<__ss_int>(1,__ss_int(1))),(new tuple<__ss_int>(1,__ss_int(2))))))), 0);
    ASSERT(___bool(__eq((new list<tuple<__ss_int> *>(__zip(2, False, (new list<__ss_int>(2,__ss_int(1),__ss_int(2))), (new list<__ss_int>(2,__ss_int(3),__ss_int(4)))))), (new list<tuple<__ss_int> *>(2,(__ss_tuple_int(2,__ss_int(1),__ss_int(3))),(__ss_tuple_int(2,__ss_int(2),__ss_int(4))))))), 0);
    ASSERT(___bool(__eq((new list<tuple2<__ss_int, str *> *>(__zip(2, False, (new list<__ss_int>(2,__ss_int(1),__ss_int(2))), (new list<str *>(2,const_8,const_11))))), (new list<tuple2<__ss_int, str *> *>(2,(new tuple2<__ss_int, str *>(2,__ss_int(1),const_8)),(new tuple2<__ss_int, str *>(2,__ss_int(2),const_11)))))), 0);
    ASSERT(___bool(__eq((new list<tuple<__ss_int> *>(__zip(3, False, (new list<__ss_int>(3,__ss_int(1),__ss_int(2),__ss_int(3))), (new list<__ss_int>(3,__ss_int(4),__ss_int(5),__ss_int(6))), (new list<__ss_int>(3,__ss_int(7),__ss_int(8),__ss_int(9)))))), (new list<tuple<__ss_int> *>(3,(new tuple<__ss_int>(3,__ss_int(1),__ss_int(4),__ss_int(7))),(new tuple<__ss_int>(3,__ss_int(2),__ss_int(5),__ss_int(8))),(new tuple<__ss_int>(3,__ss_int(3),__ss_int(6),__ss_int(9))))))), 0);
    ASSERT(___bool(__eq((new list<tuple<__ss_int> *>(__zip(5, False, (new list<__ss_int>(3,__ss_int(1),__ss_int(2),__ss_int(3))), (new list<__ss_int>(3,__ss_int(4),__ss_int(5),__ss_int(6))), (new list<__ss_int>(3,__ss_int(7),__ss_int(8),__ss_int(9))), (new list<__ss_int>(3,__ss_int(10),__ss_int(11),__ss_int(12))), (new list<__ss_int>(3,__ss_int(13),__ss_int(14),__ss_int(15)))))), (new list<tuple<__ss_int> *>(3,(new tuple<__ss_int>(5,__ss_int(1),__ss_int(4),__ss_int(7),__ss_int(10),__ss_int(13))),(new tuple<__ss_int>(5,__ss_int(2),__ss_int(5),__ss_int(8),__ss_int(11),__ss_int(14))),(new tuple<__ss_int>(5,__ss_int(3),__ss_int(6),__ss_int(9),__ss_int(12),__ss_int(15))))))), 0);
    return NULL;
}

void *test_all() {
    test_abs();
    test_bin();
    test_bool();
    test_bytes();
    test_chr();
    test_complex();
    test_divmod();
    test_enumerate();
    test_filter();
    test_float();
    test_hash();
    test_hex();
    test_int();
    test_int_base();
    test_isinstance();
    test_len();
    test_max();
    test_min();
    test_oct();
    test_ord();
    test_property();
    test_print();
    test_range();
    test_range_slicing();
    test_repr();
    test_reversed();
    test_round();
    test_set();
    test_str();
    test_sum();
    test_tuple();
    test_zip();
    return NULL;
}

void __init() {
    __name__ = new str("__main__");

    const_0 = new str("\012not implemented:\012\012    aiter\012    anext\012    ascii\012    breakpoint\012    callable\012    classmethod\012    compile\012    copyright\012    credits\012    delattr\012    dir\012    display\012    eval\012    exec\012    format\012    getattr\012    globals\012    hasattr\012    help\012    id\012    input\012    locals\012    memoryview\012    setattr\012    super\012    type\012    vars\012\012 ");
    const_1 = new str("0b11");
    const_2 = new bytes("");
    const_3 = new bytes("\001\002\003");
    const_4 = __byte_cache[1];
    const_5 = new bytes("\000\000\000\000", (size_t)4);
    const_6 = new bytes("\000\000\000\000\000\000\000", (size_t)7);
    const_7 = new bytes("hop");
    const_8 = __char_cache[97];
    const_9 = __char_cache[1];
    const_10 = __char_cache[77];
    const_11 = __char_cache[98];
    const_12 = __char_cache[99];
    const_13 = new str("abc");
    const_14 = new str("cba");
    const_15 = new str("ff");
    const_16 = new str("101");
    const_17 = new str("0x1A");
    const_18 = new str("  42  ");
    const_19 = new str("0x1");
    const_20 = new str("foo");
    const_21 = new str("0o12");
    const_22 = __char_cache[122];
    const_23 = __char_cache[49];
    const_24 = __char_cache[57];
    const_25 = new str("");
    const_26 = __char_cache[10];
    const_27 = new str("hoep");
    const_28 = new str("--");
    const_29 = new str("1.1");
    const_30 = new str("1.5");
    const_31 = new str("__main__");

    cl_Klass = new class_("Klass");
    cl_SubKlass = new class_("SubKlass");
    SubKlass::__static__();
    cl_Bert = new class_("Bert");
    cl_MyString = new class_("MyString");
    cl_Account = new class_("Account");
    if (__eq(__test_builtins__::__name__, const_31)) {
        test_all();
    }
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __shedskin__::__start(__test_builtins__::__init);
}
