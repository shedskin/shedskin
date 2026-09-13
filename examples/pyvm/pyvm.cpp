#include "builtin.hpp"
#include "sys.hpp"
#include "pyvm.hpp"

/**
pyvm - a tiny CPython 3.14 bytecode interpreter, written in Shedskin-compatible Python.
Reads a real .pyc file produced by CPython 3.14 (marshal format, magic 3627),
decodes the code object into a list of Instruction objects and runs it.
Two dispatch strategies are implemented over the *same* decoded instruction
list, so they can be benchmarked against each other:
  --virtual  one Instruction subclass per opcode, `execute()` is a virtual call
  --ifelse   a single long if/elif chain on the opcode number
Only a handful of opcodes are supported: enough for module-level code with
integer/string constants, arithmetic, comparisons, while-loops and print().
Usage:
    pyvm [--virtual|--ifelse] file.pyc
    pyvm            (no arguments: run the bundled testdata with both dispatchers)
*/

namespace __pyvm__ {

str *const_0, *const_1, *const_10, *const_100, *const_101, *const_102, *const_103, *const_104, *const_105, *const_106, *const_107, *const_108, *const_109, *const_11, *const_110, *const_111, *const_112, *const_113, *const_114, *const_115, *const_116, *const_117, *const_118, *const_119, *const_12, *const_120, *const_121, *const_122, *const_123, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_2, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_26, *const_27, *const_28, *const_29, *const_3, *const_30, *const_31, *const_32, *const_33, *const_34, *const_35, *const_36, *const_37, *const_38, *const_39, *const_4, *const_40, *const_41, *const_42, *const_43, *const_44, *const_45, *const_46, *const_47, *const_48, *const_49, *const_5, *const_50, *const_51, *const_52, *const_53, *const_55, *const_56, *const_57, *const_58, *const_59, *const_6, *const_60, *const_61, *const_62, *const_63, *const_64, *const_65, *const_66, *const_67, *const_68, *const_69, *const_7, *const_70, *const_71, *const_72, *const_73, *const_74, *const_75, *const_76, *const_77, *const_78, *const_79, *const_8, *const_80, *const_81, *const_82, *const_83, *const_84, *const_85, *const_86, *const_87, *const_88, *const_89, *const_9, *const_90, *const_91, *const_92, *const_93, *const_94, *const_95, *const_96, *const_97, *const_98, *const_99;
bytes *const_54;


file *__file;
__ss_int CMP_EQ, CMP_GE, CMP_GT, CMP_LE, CMP_LT, CMP_NE, FLAG_REF, MAGIC, NB_ADD, NB_AND, NB_FLOOR_DIVIDE, NB_INPLACE_OFFSET, NB_LSHIFT, NB_MULTIPLY, NB_OR, NB_REMAINDER, NB_RSHIFT, NB_SUBTRACT, NB_XOR, OP_BINARY_OP, OP_CACHE, OP_CALL, OP_COMPARE_OP, OP_EXTENDED_ARG, OP_JUMP_BACKWARD, OP_JUMP_FORWARD, OP_LOAD_CONST, OP_LOAD_FAST, OP_LOAD_FAST_BORROW, OP_LOAD_FAST_BORROW_LOAD_FAST_BORROW, OP_LOAD_FAST_CHECK, OP_LOAD_FAST_LOAD_FAST, OP_LOAD_GLOBAL, OP_LOAD_NAME, OP_LOAD_SMALL_INT, OP_MAKE_FUNCTION, OP_NOP, OP_NOT_TAKEN, OP_POP_JUMP_IF_FALSE, OP_POP_JUMP_IF_TRUE, OP_POP_TOP, OP_PUSH_NULL, OP_RESUME, OP_RETURN_VALUE, OP_STORE_FAST, OP_STORE_FAST_LOAD_FAST, OP_STORE_FAST_STORE_FAST, OP_STORE_GLOBAL, OP_STORE_NAME, OP_TO_BOOL, TYPE_ASCII, TYPE_ASCII_INTERNED, TYPE_CODE, TYPE_FALSE, TYPE_INT, TYPE_NONE, TYPE_REF, TYPE_SHORT_ASCII, TYPE_SHORT_ASCII_INTERNED, TYPE_SMALL_TUPLE, TYPE_STRING, TYPE_TRUE, TYPE_TUPLE, TYPE_UNICODE, __void;
str *__name__;
dict<__ss_int, __ss_int> *INLINE_CACHE;
dict<__ss_int, str *> *OPNAME;
NoneObj *__ss_NONE;
Null *NULL_OBJ;
Bool *__ss_FALSE, *__ss_TRUE;
list<Obj *> *NO_ITEMS;
list<str *> *NO_NAMES;
list<Int *> *SMALL_INTS;
list<Instr *> *NO_INSTRS;
Code *NO_CODE;
dict<str *, PrintFn *> *BUILTINS;
list<__ss_bool> *VIRTUAL;


static inline list<str *> *list_comp_0(Tuple *self);
static inline list<str *> *list_comp_1(list<Obj *> *args);
static inline list<Int *> *list_comp_2();
static inline list<str *> *list_comp_3(bytes *b);
static inline list<str *> *list_comp_4(Reader *self);
static inline list<str *> *list_comp_5(Reader *self);

static inline list<str *> *list_comp_0(Tuple *self) {
    Obj *x;
    list<Obj *> *__3;
    __iter<Obj *> *__4;
    __ss_int __5;
    list<Obj *>::for_in_loop __6;

    list<str *> *__ss_result = new list<str *>();

    __3 = self->l;
    __ss_result->resize(len(__3));
    FOR_IN(x,__3,3,5,6)
        __ss_result->units[__5] = x->repr_();
    END_FOR

    return __ss_result;
}

static inline list<str *> *list_comp_1(list<Obj *> *args) {
    Obj *a;
    list<Obj *> *__10;
    __iter<Obj *> *__11;
    __ss_int __12;
    list<Obj *>::for_in_loop __13;

    list<str *> *__ss_result = new list<str *>();

    __ss_result->resize(len(args));
    FOR_IN(a,args,10,12,13)
        __ss_result->units[__12] = a->_str_();
    END_FOR

    return __ss_result;
}

static inline list<Int *> *list_comp_2() {
    __ss_int __14, __15, i;

    list<Int *> *__ss_result = new list<Int *>();

    __ss_result->resize(256);
    FAST_FOR(i,0,__ss_int(256LL),1,14,15)
        __ss_result->units[__14] = (new Int(i));
    END_FOR

    return __ss_result;
}

static inline list<str *> *list_comp_3(bytes *b) {
    __ss_int __18, c;
    bytes *__16;
    __iter<__ss_int> *__17;
    bytes::for_in_loop __19;

    list<str *> *__ss_result = new list<str *>();

    __ss_result->resize(len(b));
    FOR_IN(c,b,16,18,19)
        __ss_result->units[__18] = chr(c);
    END_FOR

    return __ss_result;
}

static inline list<str *> *list_comp_4(Reader *self) {
    Obj *__34, *x;
    list<Obj *> *__29;
    __iter<Obj *> *__30;
    __ss_int __31;
    list<Obj *>::for_in_loop __32;
    void *__33;

    list<str *> *__ss_result = new list<str *>();

    __29 = (self->read())->items();
    __ss_result->resize(len(__29));
    FOR_IN(x,__29,29,31,32)
        __ss_result->units[__31] = x->as_str();
    END_FOR

    return __ss_result;
}

static inline list<str *> *list_comp_5(Reader *self) {
    Obj *__40, *x;
    list<Obj *> *__35;
    __iter<Obj *> *__36;
    __ss_int __37;
    list<Obj *>::for_in_loop __38;
    void *__39;

    list<str *> *__ss_result = new list<str *>();

    __35 = (self->read())->items();
    __ss_result->resize(len(__35));
    FOR_IN(x,__35,35,37,38)
        __ss_result->units[__37] = x->as_str();
    END_FOR

    return __ss_result;
}

/**
class Obj
*/

class_ *cl_Obj;

str *Obj::_str_() {
    return __add_strs(3, const_47, ((Null *)this)->type_name(), const_48);
}

str *Obj::repr_() {
    return this->_str_();
}

__ss_bool Obj::truth() {
    return True;
}

__ss_int Obj::as_int() {
    throw ((new Exception(__add_strs(3, const_49, this->type_name(), const_50))));
    return __ss_int(0LL);
}

str *Obj::as_str() {
    throw ((new Exception(__add_strs(3, const_49, this->type_name(), const_51))));
    return const_52;
}

bytes *Obj::as_bytes() {
    throw ((new Exception(__add_strs(3, const_49, this->type_name(), const_53))));
    return const_54;
}

list<Obj *> *Obj::items() {
    throw ((new Exception(__add_strs(3, const_49, this->type_name(), const_55))));
    return __pyvm__::NO_ITEMS;
}

__ss_bool Obj::is_code() {
    return False;
}

Code *Obj::as_code() {
    throw ((new Exception(__add_strs(3, const_49, this->type_name(), const_56))));
    return __pyvm__::NO_CODE;
}

Obj *Obj::binary_op(__ss_int op, Obj *other) {
    throw ((new Exception((const_57)->__add__(this->type_name()))));
    return __pyvm__::__ss_NONE;
}

__ss_bool Obj::compare(__ss_int op, Obj *other) {
    throw ((new Exception(__add_strs(3, const_49, this->type_name(), const_58))));
    return False;
}

Obj *Obj::call(list<Obj *> *args) {
    throw ((new Exception(__add_strs(3, const_49, this->type_name(), const_59))));
    return __pyvm__::__ss_NONE;
}

void Obj::__static__() {
}

/**
class NoneObj
*/

class_ *cl_NoneObj;

str *NoneObj::type_name() {
    return const_60;
}

str *NoneObj::_str_() {
    return const_61;
}

__ss_bool NoneObj::truth() {
    return False;
}

__ss_bool NoneObj::compare(__ss_int op, Obj *other) {
    if ((op==__pyvm__::CMP_EQ)) {
        return ___bool((other==((Obj *)(this))));
    }
    if ((op==__pyvm__::CMP_NE)) {
        return ___bool((other!=((Obj *)(this))));
    }
    throw ((new Exception(const_62)));
    return False;
}

/**
class Null
*/

class_ *cl_Null;

str *Null::type_name() {
    return const_64;
}

void Null::__static__() {
}

/**
class Int
*/

class_ *cl_Int;

void *Int::__init__(__ss_int v) {
    this->v = v;
    return NULL;
}

str *Int::type_name() {
    return const_65;
}

str *Int::_str_() {
    return __str(this->v);
}

__ss_bool Int::truth() {
    return ___bool((this->v!=__ss_int(0LL)));
}

__ss_int Int::as_int() {
    return this->v;
}

Obj *Int::binary_op(__ss_int op, Obj *other) {
    __ss_int a, b;

    b = other->as_int();
    a = this->v;
    if ((op==__pyvm__::NB_ADD)) {
        return (new Int((a+b)));
    }
    else if ((op==__pyvm__::NB_SUBTRACT)) {
        return (new Int((a-b)));
    }
    else if ((op==__pyvm__::NB_MULTIPLY)) {
        return (new Int((a*b)));
    }
    else if ((op==__pyvm__::NB_FLOOR_DIVIDE)) {
        return (new Int(__floordiv(a,b)));
    }
    else if ((op==__pyvm__::NB_REMAINDER)) {
        return (new Int(__mods(a, b)));
    }
    else if ((op==__pyvm__::NB_AND)) {
        return (new Int(((a)&(b))));
    }
    else if ((op==__pyvm__::NB_OR)) {
        return (new Int(((a)|(b))));
    }
    else if ((op==__pyvm__::NB_XOR)) {
        return (new Int(((a)^(b))));
    }
    else if ((op==__pyvm__::NB_LSHIFT)) {
        return (new Int((a<<b)));
    }
    else if ((op==__pyvm__::NB_RSHIFT)) {
        return (new Int((a>>b)));
    }
    throw ((new Exception(__mod6(const_66, 1, op))));
    return 0;
}

__ss_bool Int::compare(__ss_int op, Obj *other) {
    __ss_int a, b;

    b = other->as_int();
    a = this->v;
    if ((op==__pyvm__::CMP_LT)) {
        return ___bool((a<b));
    }
    else if ((op==__pyvm__::CMP_LE)) {
        return ___bool((a<=b));
    }
    else if ((op==__pyvm__::CMP_EQ)) {
        return ___bool((a==b));
    }
    else if ((op==__pyvm__::CMP_NE)) {
        return ___bool((a!=b));
    }
    else if ((op==__pyvm__::CMP_GT)) {
        return ___bool((a>b));
    }
    return ___bool((a>=b));
}


/**
class Bool
*/

class_ *cl_Bool;

void *Bool::__init__(__ss_int v) {
    Int::__init__(v);
    return NULL;
}

str *Bool::type_name() {
    return const_67;
}

str *Bool::_str_() {
    if (this->v) {
        return const_68;
    }
    return const_69;
}

/**
class Str
*/

class_ *cl_Str;

void *Str::__init__(str *s) {
    this->s = s;
    return NULL;
}

str *Str::type_name() {
    return const_70;
}

str *Str::_str_() {
    return this->s;
}

str *Str::repr_() {
    return repr(this->s);
}

__ss_bool Str::truth() {
    return ___bool((len(this->s)!=__ss_int(0LL)));
}

str *Str::as_str() {
    return this->s;
}

Obj *Str::binary_op(__ss_int op, Obj *other) {
    if ((op==__pyvm__::NB_ADD)) {
        return (new Str((this->s)->__add__(other->as_str())));
    }
    else if ((op==__pyvm__::NB_MULTIPLY)) {
        return (new Str((this->s)->__mul__(other->as_int())));
    }
    throw ((new Exception(__mod6(const_71, 1, op))));
    return 0;
}

__ss_bool Str::compare(__ss_int op, Obj *other) {
    str *a, *b;

    b = other->as_str();
    a = this->s;
    if ((op==__pyvm__::CMP_LT)) {
        return ___bool(__lt(a, b));
    }
    else if ((op==__pyvm__::CMP_LE)) {
        return ___bool(__le(a, b));
    }
    else if ((op==__pyvm__::CMP_EQ)) {
        return ___bool(__eq(a, b));
    }
    else if ((op==__pyvm__::CMP_NE)) {
        return ___bool(__ne(a, b));
    }
    else if ((op==__pyvm__::CMP_GT)) {
        return ___bool(__gt(a, b));
    }
    return ___bool(__ge(a, b));
}

/**
class Bytes
*/

class_ *cl_Bytes;

void *Bytes::__init__(bytes *b) {
    this->b = b;
    return NULL;
}

str *Bytes::type_name() {
    return const_72;
}

str *Bytes::_str_() {
    return repr(this->b);
}

__ss_bool Bytes::truth() {
    return ___bool((len(this->b)!=__ss_int(0LL)));
}

bytes *Bytes::as_bytes() {
    return this->b;
}

/**
class Tuple
*/

class_ *cl_Tuple;

void *Tuple::__init__(list<Obj *> *l) {
    this->l = l;
    return NULL;
}

str *Tuple::type_name() {
    return const_73;
}

str *Tuple::_str_() {
    return __add_strs(3, const_6, (const_74)->join(list_comp_0(this)), const_7);
}

__ss_bool Tuple::truth() {
    return ___bool((len(this->l)!=__ss_int(0LL)));
}

list<Obj *> *Tuple::items() {
    return this->l;
}

/**
class Code
*/

class_ *cl_Code;

void *Code::__init__() {
    this->argcount = __ss_int(0LL);
    this->posonlyargcount = __ss_int(0LL);
    this->kwonlyargcount = __ss_int(0LL);
    this->stacksize = __ss_int(0LL);
    this->flags = __ss_int(0LL);
    this->co_code = const_54;
    this->consts = __pyvm__::NO_ITEMS;
    this->names = __pyvm__::NO_NAMES;
    this->localsplusnames = __pyvm__::NO_NAMES;
    this->localspluskinds = const_54;
    this->filename = const_52;
    this->name = const_52;
    this->qualname = const_52;
    this->firstlineno = __ss_int(0LL);
    this->linetable = const_54;
    this->exceptiontable = const_54;
    this->instrs = __pyvm__::NO_INSTRS;
    return NULL;
}

str *Code::type_name() {
    return const_76;
}

str *Code::_str_() {
    return __add_strs(5, const_77, this->name, const_78, this->filename, __mod6(const_79, 1, this->firstlineno));
}

__ss_bool Code::is_code() {
    return True;
}

Code *Code::as_code() {
    return this;
}

void Code::__static__() {
}

/**
class Function
*/

class_ *cl_Function;

void *Function::__init__(Code *code, dict<str *, Obj *> *globals_) {
    this->code = code;
    this->globals = globals_;
    return NULL;
}

str *Function::type_name() {
    return const_80;
}

str *Function::_str_() {
    return __add_strs(3, const_81, (this->code)->qualname, const_48);
}

Obj *Function::call(list<Obj *> *args) {
    Code *code;
    Frame *f;
    __ss_int __7, __8, i;
    list<Obj *> *__9;

    code = this->code;
    if ((len(args)!=code->argcount)) {
        throw ((new Exception(__mod6(const_82, 3, code->name, code->argcount, len(args)))));
    }
    f = (new Frame(code, this->globals));

    FAST_FOR(i,0,len(args),1,7,8)
        f->locals->__setitem__(i, args->__getfast__(i));
    END_FOR

    return run_frame(f);
}

/**
class PrintFn
*/

class_ *cl_PrintFn;

str *PrintFn::type_name() {
    return const_83;
}

str *PrintFn::_str_() {
    return const_84;
}

Obj *PrintFn::call(list<Obj *> *args) {
    print((const_85)->join(list_comp_1(args)));
    return __pyvm__::__ss_NONE;
}

str *decode_ascii(bytes *b) {
    return (const_52)->join(list_comp_3(b));
}

/**
class Reader
*/

class_ *cl_Reader;

void *Reader::__init__(bytes *data) {
    this->data = data;
    this->pos = __ss_int(0LL);
    this->refs = (new list<Obj *>(1,((Obj *)(__pyvm__::__ss_NONE))));
    this->nrefs = __ss_int(0LL);
    return NULL;
}

__ss_int Reader::byte() {
    __ss_int b;

    b = (this->data)->__getfast__(this->pos);
    this->pos = (this->pos+__ss_int(1LL));
    return b;
}

__ss_int Reader::__ss_long() {
    bytes *d;
    __ss_int p, v;

    d = this->data;
    p = this->pos;
    v = ((((((d->__getfast__(p))|((d->__getfast__((p+__ss_int(1LL)))<<__ss_int(8LL)))))|((d->__getfast__((p+__ss_int(2LL)))<<__ss_int(16LL)))))|((d->__getfast__((p+__ss_int(3LL)))<<__ss_int(24LL))));
    this->pos = (p+__ss_int(4LL));
    if ((v>=(__ss_int(1LL)<<__ss_int(31LL)))) {
        v = (v-(__ss_int(1LL)<<__ss_int(32LL)));
    }
    return v;
}

bytes *Reader::raw(__ss_int n) {
    bytes *b;

    b = (this->data)->__slice__(__ss_int(3LL), this->pos, (this->pos+n), __ss_int(0LL));
    this->pos = (this->pos+n);
    return b;
}

__ss_int Reader::reserve_ref() {
    __ss_int idx;
    list<Obj *> *__20;

    idx = this->nrefs;
    if ((idx<len(this->refs))) {
        this->refs->__setitem__(idx, ((Obj *)__pyvm__::__ss_NONE));
    }
    else {
        (this->refs)->append(((Obj *)(__pyvm__::__ss_NONE)));
    }
    this->nrefs = (this->nrefs+__ss_int(1LL));
    return idx;
}

Obj *Reader::read() {
    __ss_int code, flag, idx, t;
    Obj *obj;
    list<Obj *> *__21;

    code = this->byte();
    flag = ((code)&(__pyvm__::FLAG_REF));
    t = ((code)&(~__pyvm__::FLAG_REF));
    idx = (-__ss_int(1LL));
    if (flag) {
        idx = this->reserve_ref();
    }
    obj = this->read_type(t);
    if (flag) {
        this->refs->__setitem__(idx, obj);
    }
    return obj;
}

Obj *Reader::read_type(__ss_int t) {
    __ss_bool __22, __23, __24, __25, __26;

    if ((t==__pyvm__::TYPE_NONE)) {
        return ((Obj *)(__pyvm__::__ss_NONE));
    }
    else if ((t==__pyvm__::TYPE_TRUE)) {
        return ((Obj *)(__pyvm__::__ss_TRUE));
    }
    else if ((t==__pyvm__::TYPE_FALSE)) {
        return ((Obj *)(__pyvm__::__ss_FALSE));
    }
    else if ((t==__pyvm__::TYPE_INT)) {
        return ((Obj *)((new Int(this->__ss_long()))));
    }
    else if ((t==__pyvm__::TYPE_STRING)) {
        return ((Obj *)((new Bytes(this->raw(this->__ss_long())))));
    }
    else if (((t==__pyvm__::TYPE_SHORT_ASCII) or (t==__pyvm__::TYPE_SHORT_ASCII_INTERNED))) {
        return ((Obj *)((new Str(decode_ascii(this->raw(this->byte()))))));
    }
    else if (((t==__pyvm__::TYPE_ASCII) or (t==__pyvm__::TYPE_ASCII_INTERNED) or (t==__pyvm__::TYPE_UNICODE))) {
        return ((Obj *)((new Str(decode_ascii(this->raw(this->__ss_long()))))));
    }
    else if ((t==__pyvm__::TYPE_SMALL_TUPLE)) {
        return ((Obj *)((new Tuple(this->read_items(this->byte())))));
    }
    else if ((t==__pyvm__::TYPE_TUPLE)) {
        return ((Obj *)((new Tuple(this->read_items(this->__ss_long())))));
    }
    else if ((t==__pyvm__::TYPE_REF)) {
        return (this->refs)->__getfast__(this->__ss_long());
    }
    else if ((t==__pyvm__::TYPE_CODE)) {
        return ((Obj *)(this->read_code()));
    }
    throw ((new Exception(__mod6(const_86, 3, t, chr(t), (this->pos-__ss_int(1LL))))));
    return 0;
}

list<Obj *> *Reader::read_items(__ss_int n) {
    list<Obj *> *l;
    __ss_int __27, __28, i;

    l = ((new list<Obj *>(1,((Obj *)(__pyvm__::__ss_NONE)))))->__mul__(n);

    FAST_FOR(i,0,n,1,27,28)
        l->__setitem__(i, this->read());
    END_FOR

    return l;
}

Code *Reader::read_code() {
    Code *c;

    c = (new Code(1));
    c->argcount = this->__ss_long();
    c->posonlyargcount = this->__ss_long();
    c->kwonlyargcount = this->__ss_long();
    c->stacksize = this->__ss_long();
    c->flags = this->__ss_long();
    c->co_code = (this->read())->as_bytes();
    c->consts = (this->read())->items();
    c->names = list_comp_4(this);
    c->localsplusnames = list_comp_5(this);
    c->localspluskinds = (this->read())->as_bytes();
    c->filename = (this->read())->as_str();
    c->name = (this->read())->as_str();
    c->qualname = (this->read())->as_str();
    c->firstlineno = this->__ss_long();
    c->linetable = (this->read())->as_bytes();
    c->exceptiontable = (this->read())->as_bytes();
    return c;
}

Code *load_pyc(str *path) {
    bytes *data;
    __ss_int magic;
    Reader *r;
    __ss_bool __41, __42, __43;

    data = (open_binary(path, const_87))->read();
    magic = ((data->__getfast__(__ss_int(0LL)))|((data->__getfast__(__ss_int(1LL))<<__ss_int(8LL))));
    if (((magic!=__pyvm__::MAGIC) or (data->__getfast__(__ss_int(2LL))!=__ss_int(13LL)) or (data->__getfast__(__ss_int(3LL))!=__ss_int(10LL)))) {
        throw ((new Exception(__mod6(const_88, 3, path, magic, __pyvm__::MAGIC))));
    }
    r = (new Reader(data));
    r->pos = __ss_int(16LL);
    return (r->read())->as_code();
}

/**
class Frame
*/

class_ *cl_Frame;

void *Frame::__init__(Code *code, dict<str *, Obj *> *globals_) {
    this->code = code;
    this->globals = globals_;
    this->pc = __ss_int(0LL);
    this->stack = ((new list<Obj *>(1,((Obj *)(__pyvm__::__ss_NONE)))))->__mul__((code->stacksize+__ss_int(1LL)));
    this->locals = ((new list<Obj *>(1,((Obj *)(__pyvm__::__ss_NONE)))))->__mul__((len(code->localsplusnames)+__ss_int(1LL)));
    this->sp = __ss_int(0LL);
    this->running = True;
    this->retval = ((Obj *)(__pyvm__::__ss_NONE));
    return NULL;
}

void *Frame::push(Obj *o) {
    list<Obj *> *__44;

    this->stack->__setitem__(this->sp, o);
    this->sp = (this->sp+__ss_int(1LL));
    return NULL;
}

Obj *Frame::pop() {
    this->sp = (this->sp-__ss_int(1LL));
    return (this->stack)->__getfast__(this->sp);
}

/**
class Instr
*/

class_ *cl_Instr;

void *Instr::__init__(__ss_int op, __ss_int arg) {
    this->op = op;
    this->arg = arg;
    this->arg2 = __ss_int(0LL);
    this->target = __ss_int(0LL);
    this->value = ((Obj *)(__pyvm__::__ss_NONE));
    this->name = const_52;
    return NULL;
}

void *Instr::execute(Frame *f) {
    throw ((new Exception(__mod6(const_90, 1, this->op))));
    return NULL;
}

str *Instr::__repr__() {
    return __mod6(const_91, 2, __pyvm__::OPNAME->get(this->op, __mod6(const_92, 1, this->op)), this->arg);
}

void Instr::__static__() {
}

/**
class Nop
*/

class_ *cl_Nop;

void *Nop::execute(Frame *f) {
    return NULL;
}

/**
class PopTop
*/

class_ *cl_PopTop;

void *PopTop::execute(Frame *f) {
    f->sp = (f->sp-__ss_int(1LL));
    return NULL;
}

/**
class PushNull
*/

class_ *cl_PushNull;

void *PushNull::execute(Frame *f) {
    f->push(((Obj *)(__pyvm__::NULL_OBJ)));
    return NULL;
}

/**
class ReturnValue
*/

class_ *cl_ReturnValue;

void *ReturnValue::execute(Frame *f) {
    f->retval = f->pop();
    f->running = False;
    return NULL;
}

/**
class ToBool
*/

class_ *cl_ToBool;

void *ToBool::execute(Frame *f) {
    list<Obj *> *__45, *__46;

    if (((f->stack)->__getfast__((f->sp-__ss_int(1LL))))->truth()) {
        f->stack->__setitem__((f->sp-__ss_int(1LL)), ((Obj *)__pyvm__::__ss_TRUE));
    }
    else {
        f->stack->__setitem__((f->sp-__ss_int(1LL)), ((Obj *)__pyvm__::__ss_FALSE));
    }
    return NULL;
}

/**
class BinaryOp
*/

class_ *cl_BinaryOp;

void *BinaryOp::execute(Frame *f) {
    Obj *lhs, *rhs;
    list<Obj *> *__47;

    rhs = f->pop();
    lhs = (f->stack)->__getfast__((f->sp-__ss_int(1LL)));
    f->stack->__setitem__((f->sp-__ss_int(1LL)), lhs->binary_op(this->arg, rhs));
    return NULL;
}

/**
class Call
*/

class_ *cl_Call;

void *Call::execute(Frame *f) {
    f->push(do_call(f, this->arg));
    return NULL;
}

/**
class CompareOp
*/

class_ *cl_CompareOp;

void *CompareOp::execute(Frame *f) {
    Obj *lhs, *rhs;
    list<Obj *> *__48, *__49;

    rhs = f->pop();
    lhs = (f->stack)->__getfast__((f->sp-__ss_int(1LL)));
    if (lhs->compare(this->arg, rhs)) {
        f->stack->__setitem__((f->sp-__ss_int(1LL)), ((Obj *)__pyvm__::__ss_TRUE));
    }
    else {
        f->stack->__setitem__((f->sp-__ss_int(1LL)), ((Obj *)__pyvm__::__ss_FALSE));
    }
    return NULL;
}

/**
class Jump
*/

class_ *cl_Jump;

void *Jump::execute(Frame *f) {
    f->pc = this->target;
    return NULL;
}

/**
class PopJumpIfFalse
*/

class_ *cl_PopJumpIfFalse;

void *PopJumpIfFalse::execute(Frame *f) {
    if (__NOT((f->pop())->truth())) {
        f->pc = this->target;
    }
    return NULL;
}

/**
class PopJumpIfTrue
*/

class_ *cl_PopJumpIfTrue;

void *PopJumpIfTrue::execute(Frame *f) {
    if ((f->pop())->truth()) {
        f->pc = this->target;
    }
    return NULL;
}

/**
class LoadConst
*/

class_ *cl_LoadConst;

void *LoadConst::execute(Frame *f) {
    f->push(this->value);
    return NULL;
}

/**
class LoadName
*/

class_ *cl_LoadName;

void *LoadName::execute(Frame *f) {
    f->push(lookup_name(f, this->name));
    return NULL;
}

/**
class StoreName
*/

class_ *cl_StoreName;

void *StoreName::execute(Frame *f) {
    dict<str *, Obj *> *__50;

    f->globals->__setitem__(this->name, f->pop());
    return NULL;
}

/**
class LoadGlobal
*/

class_ *cl_LoadGlobal;

void *LoadGlobal::execute(Frame *f) {
    f->push(lookup_name(f, this->name));
    if (this->arg2) {
        f->push(((Obj *)(__pyvm__::NULL_OBJ)));
    }
    return NULL;
}

/**
class LoadFast
*/

class_ *cl_LoadFast;

void *LoadFast::execute(Frame *f) {
    f->push((f->locals)->__getfast__(this->arg));
    return NULL;
}

/**
class LoadFastLoadFast
*/

class_ *cl_LoadFastLoadFast;

void *LoadFastLoadFast::execute(Frame *f) {
    f->push((f->locals)->__getfast__(this->arg));
    f->push((f->locals)->__getfast__(this->arg2));
    return NULL;
}

/**
class StoreFast
*/

class_ *cl_StoreFast;

void *StoreFast::execute(Frame *f) {
    list<Obj *> *__51;

    f->locals->__setitem__(this->arg, f->pop());
    return NULL;
}

/**
class StoreFastStoreFast
*/

class_ *cl_StoreFastStoreFast;

void *StoreFastStoreFast::execute(Frame *f) {
    list<Obj *> *__52, *__53;

    f->locals->__setitem__(this->arg, f->pop());
    f->locals->__setitem__(this->arg2, f->pop());
    return NULL;
}

/**
class StoreFastLoadFast
*/

class_ *cl_StoreFastLoadFast;

void *StoreFastLoadFast::execute(Frame *f) {
    list<Obj *> *__54;

    f->locals->__setitem__(this->arg, f->pop());
    f->push((f->locals)->__getfast__(this->arg2));
    return NULL;
}

/**
class MakeFunction
*/

class_ *cl_MakeFunction;

void *MakeFunction::execute(Frame *f) {
    f->push(((Obj *)((new Function((f->pop())->as_code(), f->globals)))));
    return NULL;
}

Obj *lookup_name(Frame *f, str *name) {
    if ((f->globals)->__contains__(name)) {
        return (f->globals)->__getitem__(name);
    }
    if ((__pyvm__::BUILTINS)->__contains__(name)) {
        return ((Obj *)(__pyvm__::BUILTINS->__getitem__(name)));
    }
    throw ((new Exception(__add_strs(3, const_93, name, const_94))));
    return 0;
}

Obj *do_call(Frame *f, __ss_int nargs) {
    __ss_int base;
    list<Obj *> *args;
    Obj *func, *self_or_null;

    base = (f->sp-nargs);
    args = (f->stack)->__slice__(__ss_int(3LL), base, f->sp, __ss_int(0LL));
    self_or_null = (f->stack)->__getfast__((base-__ss_int(1LL)));
    func = (f->stack)->__getfast__((base-__ss_int(2LL)));
    f->sp = (base-__ss_int(2LL));
    if ((self_or_null!=((Obj *)(__pyvm__::NULL_OBJ)))) {
        args = ((new list<Obj *>(1,self_or_null)))->__add__(args);
    }
    return func->call(args);
}

Instr *make_instr(Code *code, __ss_int op, __ss_int arg) {
    Instr *ins;
    __ss_bool __55, __56, __57, __58, __59, __60, __61, __62, __63, __64, __65, __66;

    if ((op==__pyvm__::OP_LOAD_NAME)) {
        ins = ((Instr *)((new LoadName(op, arg))));
        ins->name = (code->names)->__getfast__(arg);
        return ins;
    }
    else if (((op==__pyvm__::OP_STORE_NAME) or (op==__pyvm__::OP_STORE_GLOBAL))) {
        ins = ((Instr *)((new StoreName(op, arg))));
        ins->name = (code->names)->__getfast__(arg);
        return ins;
    }
    else if ((op==__pyvm__::OP_LOAD_GLOBAL)) {
        ins = ((Instr *)((new LoadGlobal(op, arg))));
        ins->name = (code->names)->__getfast__((arg>>__ss_int(1LL)));
        ins->arg2 = ((arg)&(__ss_int(1LL)));
        return ins;
    }
    else if (((op==__pyvm__::OP_LOAD_FAST) or (op==__pyvm__::OP_LOAD_FAST_BORROW) or (op==__pyvm__::OP_LOAD_FAST_CHECK))) {
        return ((Instr *)((new LoadFast(op, arg))));
    }
    else if (((op==__pyvm__::OP_LOAD_FAST_LOAD_FAST) or (op==__pyvm__::OP_LOAD_FAST_BORROW_LOAD_FAST_BORROW))) {
        ins = ((Instr *)((new LoadFastLoadFast(op, arg))));
        ins->arg = (arg>>__ss_int(4LL));
        ins->arg2 = ((arg)&(__ss_int(15LL)));
        return ins;
    }
    else if ((op==__pyvm__::OP_STORE_FAST)) {
        return ((Instr *)((new StoreFast(op, arg))));
    }
    else if ((op==__pyvm__::OP_STORE_FAST_STORE_FAST)) {
        ins = ((Instr *)((new StoreFastStoreFast(op, arg))));
        ins->arg = (arg>>__ss_int(4LL));
        ins->arg2 = ((arg)&(__ss_int(15LL)));
        return ins;
    }
    else if ((op==__pyvm__::OP_STORE_FAST_LOAD_FAST)) {
        ins = ((Instr *)((new StoreFastLoadFast(op, arg))));
        ins->arg = (arg>>__ss_int(4LL));
        ins->arg2 = ((arg)&(__ss_int(15LL)));
        return ins;
    }
    else if ((op==__pyvm__::OP_MAKE_FUNCTION)) {
        return ((Instr *)((new MakeFunction(op, arg))));
    }
    else if ((op==__pyvm__::OP_LOAD_CONST)) {
        ins = ((Instr *)((new LoadConst(op, arg))));
        ins->value = (code->consts)->__getfast__(arg);
        return ins;
    }
    else if ((op==__pyvm__::OP_LOAD_SMALL_INT)) {
        ins = ((Instr *)((new LoadConst(op, arg))));
        ins->value = ((Obj *)(__pyvm__::SMALL_INTS->__getfast__(arg)));
        return ins;
    }
    else if ((op==__pyvm__::OP_BINARY_OP)) {
        ins = ((Instr *)((new BinaryOp(op, arg))));
        if ((arg>=__pyvm__::NB_INPLACE_OFFSET)) {
            ins->arg = (arg-__pyvm__::NB_INPLACE_OFFSET);
        }
        return ins;
    }
    else if ((op==__pyvm__::OP_COMPARE_OP)) {
        ins = ((Instr *)((new CompareOp(op, arg))));
        ins->arg = (arg>>__ss_int(5LL));
        return ins;
    }
    else if ((op==__pyvm__::OP_CALL)) {
        return ((Instr *)((new Call(op, arg))));
    }
    else if ((op==__pyvm__::OP_POP_TOP)) {
        return ((Instr *)((new PopTop(op, arg))));
    }
    else if ((op==__pyvm__::OP_PUSH_NULL)) {
        return ((Instr *)((new PushNull(op, arg))));
    }
    else if ((op==__pyvm__::OP_RETURN_VALUE)) {
        return ((Instr *)((new ReturnValue(op, arg))));
    }
    else if ((op==__pyvm__::OP_TO_BOOL)) {
        return ((Instr *)((new ToBool(op, arg))));
    }
    else if ((op==__pyvm__::OP_POP_JUMP_IF_FALSE)) {
        return ((Instr *)((new PopJumpIfFalse(op, arg))));
    }
    else if ((op==__pyvm__::OP_POP_JUMP_IF_TRUE)) {
        return ((Instr *)((new PopJumpIfTrue(op, arg))));
    }
    else if (((op==__pyvm__::OP_JUMP_FORWARD) or (op==__pyvm__::OP_JUMP_BACKWARD))) {
        return ((Instr *)((new Jump(op, arg))));
    }
    else if (((op==__pyvm__::OP_RESUME) or (op==__pyvm__::OP_NOP) or (op==__pyvm__::OP_NOT_TAKEN))) {
        return ((Instr *)((new Nop(op, arg))));
    }
    throw ((new Exception(__mod6(const_96, 2, op, __pyvm__::OPNAME->get(op, const_97)))));
    return 0;
}

list<Instr *> *decode(Code *code) {
    /**
    Decode co_code into Instr objects. CACHE entries are dropped; jump
    arguments (in code units, relative to the unit after the jump's caches)
    are converted to instruction-list indices.
    */
    bytes *co;
    __ss_int __67, __68, __74, __82, arg, ext, n, ncache, next_unit, nunits, op, u, unit;
    list<__ss_int> *unit_to_index;
    list<Instr *> *__72, *instrs;
    Instr *ins;
    Obj *c;
    __ss_bool __69, __70, __71, __76, __77, __78, __79;
    __iter<Instr *> *__73;
    list<Instr *>::for_in_loop __75;
    list<Obj *> *__80;
    __iter<Obj *> *__81;
    list<Obj *>::for_in_loop __83;

    co = code->co_code;
    nunits = __floordiv(len(co),__ss_int(2LL));
    unit_to_index = ((new list<__ss_int>(1,__ss_int(0LL))))->__mul__((nunits+__ss_int(1LL)));
    instrs = ((new list<Instr *>(1,__pyvm__::NO_INSTRS->__getfast__(__ss_int(0LL)))))->__mul__(nunits);
    n = __ss_int(0LL);
    unit = __ss_int(0LL);
    ext = __ss_int(0LL);

    while ((unit<nunits)) {
        op = co->__getfast__((__ss_int(2LL)*unit));
        arg = ((co->__getfast__(((__ss_int(2LL)*unit)+__ss_int(1LL))))|(ext));
        ext = __ss_int(0LL);
        unit_to_index->__setitem__(unit, n);
        if ((op==__pyvm__::OP_CACHE)) {
            unit = (unit+__ss_int(1LL));
            continue;
        }
        if ((op==__pyvm__::OP_EXTENDED_ARG)) {
            ext = (arg<<__ss_int(8LL));
            unit = (unit+__ss_int(1LL));
            continue;
        }
        ins = make_instr(code, op, arg);
        ncache = __pyvm__::INLINE_CACHE->get(op, __ss_int(0LL));
        next_unit = ((unit+__ss_int(1LL))+ncache);

        FAST_FOR(u,(unit+__ss_int(1LL)),next_unit,1,67,68)
            unit_to_index->__setitem__(u, n);
        END_FOR

        if (((op==__pyvm__::OP_JUMP_FORWARD) or (op==__pyvm__::OP_POP_JUMP_IF_FALSE) or (op==__pyvm__::OP_POP_JUMP_IF_TRUE))) {
            ins->target = (next_unit+arg);
        }
        else if ((op==__pyvm__::OP_JUMP_BACKWARD)) {
            ins->target = (next_unit-arg);
        }
        instrs->__setitem__(n, ins);
        n = (n+__ss_int(1LL));
        unit = next_unit;
    }
    unit_to_index->__setitem__(nunits, n);
    instrs = instrs->__slice__(__ss_int(2LL), __ss_int(0LL), n, __ss_int(0LL));

    FOR_IN(ins,instrs,72,74,75)
        if (((ins->op==__pyvm__::OP_JUMP_FORWARD) or (ins->op==__pyvm__::OP_JUMP_BACKWARD) or (ins->op==__pyvm__::OP_POP_JUMP_IF_FALSE) or (ins->op==__pyvm__::OP_POP_JUMP_IF_TRUE))) {
            ins->target = unit_to_index->__getfast__(ins->target);
        }
    END_FOR

    code->instrs = instrs;

    FOR_IN(c,code->consts,80,82,83)
        if (c->is_code()) {
            decode(c->as_code());
        }
    END_FOR

    return instrs;
}

void *disassemble(Code *code) {
    Obj *c;
    __ss_int __86, __91, i;
    Instr *ins;
    str *extra;
    list<Obj *> *__84;
    __iter<Obj *> *__85;
    list<Obj *>::for_in_loop __87;
    tuple2<__ss_int, Instr *> *__88;
    __iter<tuple2<__ss_int, Instr *> *> *__89, *__90;
    list<Instr *> *__92;
    __iter<tuple2<__ss_int, Instr *> *>::for_in_loop __93;
    __ss_bool __100, __101, __102, __103, __104, __105, __106, __107, __108, __109, __110, __111, __94, __95, __96, __97, __98, __99;


    FOR_IN(c,code->consts,84,86,87)
        if (c->is_code()) {
            disassemble(c->as_code());
        }
    END_FOR

    print((code->_str_())->__add__(__mod6(const_99, 1, len(code->instrs))));

    FOR_IN_ENUMERATE(ins,code->instrs,92,91)
        i = __91;
        extra = const_52;
        if (((ins->op==__pyvm__::OP_LOAD_CONST) or (ins->op==__pyvm__::OP_LOAD_SMALL_INT))) {
            extra = __add_strs(3, const_6, (ins->value)->repr_(), const_7);
        }
        else if (((ins->op==__pyvm__::OP_LOAD_NAME) or (ins->op==__pyvm__::OP_STORE_NAME) or (ins->op==__pyvm__::OP_LOAD_GLOBAL) or (ins->op==__pyvm__::OP_STORE_GLOBAL))) {
            extra = __add_strs(3, const_6, ins->name, const_7);
        }
        else if (((ins->op==__pyvm__::OP_LOAD_FAST) or (ins->op==__pyvm__::OP_LOAD_FAST_BORROW) or (ins->op==__pyvm__::OP_LOAD_FAST_CHECK) or (ins->op==__pyvm__::OP_STORE_FAST))) {
            extra = __add_strs(3, const_6, (code->localsplusnames)->__getfast__(ins->arg), const_7);
        }
        else if (((ins->op==__pyvm__::OP_LOAD_FAST_LOAD_FAST) or (ins->op==__pyvm__::OP_LOAD_FAST_BORROW_LOAD_FAST_BORROW) or (ins->op==__pyvm__::OP_STORE_FAST_STORE_FAST) or (ins->op==__pyvm__::OP_STORE_FAST_LOAD_FAST))) {
            extra = __add_strs(5, const_6, (code->localsplusnames)->__getfast__(ins->arg), const_74, (code->localsplusnames)->__getfast__(ins->arg2), const_7);
        }
        else if (((ins->op==__pyvm__::OP_JUMP_FORWARD) or (ins->op==__pyvm__::OP_JUMP_BACKWARD) or (ins->op==__pyvm__::OP_POP_JUMP_IF_FALSE) or (ins->op==__pyvm__::OP_POP_JUMP_IF_TRUE))) {
            extra = __mod6(const_100, 1, ins->target);
        }
        print(__mod6(const_101, 3, i, repr(ins), extra));
    END_FOR

    print();
    return NULL;
}

Obj *run_frame(Frame *f) {
    if (__pyvm__::VIRTUAL->__getfast__(__ss_int(0LL))) {
        return run_virtual(f);
    }
    return run_ifelse(f);
}

Obj *run_virtual(Frame *f) {
    list<Instr *> *instrs;
    Instr *ins;

    instrs = (f->code)->instrs;

    while (f->running) {
        ins = instrs->__getfast__(f->pc);
        f->pc = (f->pc+__ss_int(1LL));
        ins->execute(f);
    }
    return f->retval;
}

Obj *run_ifelse(Frame *f) {
    list<Instr *> *instrs;
    list<Obj *> *locals_, *stack;
    Instr *ins;
    __ss_int op;
    Obj *rhs;
    __ss_bool __112, __113, __114, __115, __117, __118, __119, __120, __121, __122, __123, __124, __125, __126;
    dict<str *, Obj *> *__116;

    instrs = (f->code)->instrs;
    stack = f->stack;
    locals_ = f->locals;

    while (f->running) {
        ins = instrs->__getfast__(f->pc);
        f->pc = (f->pc+__ss_int(1LL));
        op = ins->op;
        if ((op==__pyvm__::OP_LOAD_NAME)) {
            stack->__setitem__(f->sp, lookup_name(f, ins->name));
            f->sp = (f->sp+__ss_int(1LL));
        }
        else if (((op==__pyvm__::OP_LOAD_CONST) or (op==__pyvm__::OP_LOAD_SMALL_INT))) {
            stack->__setitem__(f->sp, ins->value);
            f->sp = (f->sp+__ss_int(1LL));
        }
        else if (((op==__pyvm__::OP_STORE_NAME) or (op==__pyvm__::OP_STORE_GLOBAL))) {
            f->sp = (f->sp-__ss_int(1LL));
            f->globals->__setitem__(ins->name, stack->__getfast__(f->sp));
        }
        else if (((op==__pyvm__::OP_LOAD_FAST) or (op==__pyvm__::OP_LOAD_FAST_BORROW) or (op==__pyvm__::OP_LOAD_FAST_CHECK))) {
            stack->__setitem__(f->sp, locals_->__getfast__(ins->arg));
            f->sp = (f->sp+__ss_int(1LL));
        }
        else if (((op==__pyvm__::OP_LOAD_FAST_LOAD_FAST) or (op==__pyvm__::OP_LOAD_FAST_BORROW_LOAD_FAST_BORROW))) {
            stack->__setitem__(f->sp, locals_->__getfast__(ins->arg));
            stack->__setitem__((f->sp+__ss_int(1LL)), locals_->__getfast__(ins->arg2));
            f->sp = (f->sp+__ss_int(2LL));
        }
        else if ((op==__pyvm__::OP_STORE_FAST)) {
            f->sp = (f->sp-__ss_int(1LL));
            locals_->__setitem__(ins->arg, stack->__getfast__(f->sp));
        }
        else if ((op==__pyvm__::OP_STORE_FAST_STORE_FAST)) {
            locals_->__setitem__(ins->arg, stack->__getfast__((f->sp-__ss_int(1LL))));
            locals_->__setitem__(ins->arg2, stack->__getfast__((f->sp-__ss_int(2LL))));
            f->sp = (f->sp-__ss_int(2LL));
        }
        else if ((op==__pyvm__::OP_STORE_FAST_LOAD_FAST)) {
            locals_->__setitem__(ins->arg, stack->__getfast__((f->sp-__ss_int(1LL))));
            stack->__setitem__((f->sp-__ss_int(1LL)), locals_->__getfast__(ins->arg2));
        }
        else if ((op==__pyvm__::OP_LOAD_GLOBAL)) {
            stack->__setitem__(f->sp, lookup_name(f, ins->name));
            f->sp = (f->sp+__ss_int(1LL));
            if (ins->arg2) {
                stack->__setitem__(f->sp, ((Obj *)__pyvm__::NULL_OBJ));
                f->sp = (f->sp+__ss_int(1LL));
            }
        }
        else if ((op==__pyvm__::OP_MAKE_FUNCTION)) {
            stack->__setitem__((f->sp-__ss_int(1LL)), ((Obj *)(new Function((stack->__getfast__((f->sp-__ss_int(1LL))))->as_code(), f->globals))));
        }
        else if ((op==__pyvm__::OP_BINARY_OP)) {
            f->sp = (f->sp-__ss_int(1LL));
            rhs = stack->__getfast__(f->sp);
            stack->__setitem__((f->sp-__ss_int(1LL)), (stack->__getfast__((f->sp-__ss_int(1LL))))->binary_op(ins->arg, rhs));
        }
        else if ((op==__pyvm__::OP_COMPARE_OP)) {
            f->sp = (f->sp-__ss_int(1LL));
            rhs = stack->__getfast__(f->sp);
            if ((stack->__getfast__((f->sp-__ss_int(1LL))))->compare(ins->arg, rhs)) {
                stack->__setitem__((f->sp-__ss_int(1LL)), ((Obj *)__pyvm__::__ss_TRUE));
            }
            else {
                stack->__setitem__((f->sp-__ss_int(1LL)), ((Obj *)__pyvm__::__ss_FALSE));
            }
        }
        else if ((op==__pyvm__::OP_POP_JUMP_IF_FALSE)) {
            f->sp = (f->sp-__ss_int(1LL));
            if (__NOT((stack->__getfast__(f->sp))->truth())) {
                f->pc = ins->target;
            }
        }
        else if ((op==__pyvm__::OP_POP_JUMP_IF_TRUE)) {
            f->sp = (f->sp-__ss_int(1LL));
            if ((stack->__getfast__(f->sp))->truth()) {
                f->pc = ins->target;
            }
        }
        else if (((op==__pyvm__::OP_JUMP_BACKWARD) or (op==__pyvm__::OP_JUMP_FORWARD))) {
            f->pc = ins->target;
        }
        else if (((op==__pyvm__::OP_NOT_TAKEN) or (op==__pyvm__::OP_NOP) or (op==__pyvm__::OP_RESUME))) {
        }
        else if ((op==__pyvm__::OP_POP_TOP)) {
            f->sp = (f->sp-__ss_int(1LL));
        }
        else if ((op==__pyvm__::OP_PUSH_NULL)) {
            stack->__setitem__(f->sp, ((Obj *)__pyvm__::NULL_OBJ));
            f->sp = (f->sp+__ss_int(1LL));
        }
        else if ((op==__pyvm__::OP_CALL)) {
            stack->__setitem__(f->sp, do_call(f, ins->arg));
            f->sp = (f->sp+__ss_int(1LL));
        }
        else if ((op==__pyvm__::OP_TO_BOOL)) {
            if ((stack->__getfast__((f->sp-__ss_int(1LL))))->truth()) {
                stack->__setitem__((f->sp-__ss_int(1LL)), ((Obj *)__pyvm__::__ss_TRUE));
            }
            else {
                stack->__setitem__((f->sp-__ss_int(1LL)), ((Obj *)__pyvm__::__ss_FALSE));
            }
        }
        else if ((op==__pyvm__::OP_RETURN_VALUE)) {
            f->sp = (f->sp-__ss_int(1LL));
            f->retval = stack->__getfast__(f->sp);
            f->running = False;
        }
        else {
            throw ((new Exception(__mod6(const_90, 1, op))));
        }
    }
    return f->retval;
}

dict<str *, Obj *> *run_file(str *path, __ss_bool __ss_virtual, __ss_bool show) {
    /**
    Load, decode and run a .pyc; returns the module globals afterwards.
    */
    Code *code;
    dict<str *, Obj *> *globals_;

    code = load_pyc(path);
    decode(code);
    if (show) {
        disassemble(code);
    }
    globals_ = (new dict<str *, Obj *>(1, (new tuple2<str *, Obj *>(2,const_103,((Obj *)((new Str(const_104))))))));
    __pyvm__::VIRTUAL->__setitem__(__ss_int(0LL), __ss_virtual);
    run_frame((new Frame(code, globals_)));
    return globals_;
}

void *self_test(__ss_bool __ss_virtual) {
    /**
    Run the bundled testdata and check results against CPython's answers.
    */
    str *mode;
    dict<str *, Obj *> *g;

    mode = const_106;
    if (__ss_virtual) {
        mode = const_107;
    }
    print(__mod6(const_108, 1, mode));
    run_file(const_109, __ss_virtual, __ss_virtual);
    print(__mod6(const_110, 1, mode));
    g = run_file(const_111, __ss_virtual, False);
    ASSERT(___bool(((g->__getitem__(const_112))->as_int()==__ss_int(89999700000LL))), 0);
    ASSERT(___bool(((g->__getitem__(const_4))->as_int()==__ss_int(300000LL))), 0);
    print(__mod6(const_113, 1, mode));
    g = run_file(const_114, __ss_virtual, False);
    ASSERT(___bool((((g->__getitem__(const_115))->call((new list<Obj *>(1,((Obj *)((new Int(__ss_int(20LL)))))))))->as_int()==__ss_int(6765LL))), 0);
    ASSERT(___bool((((g->__getitem__(const_115))->call((new list<Obj *>(1,((Obj *)((new Int(__ss_int(1LL)))))))))->as_int()==__ss_int(1LL))), 0);
    ASSERT(___bool((((g->__getitem__(const_116))->call((new list<Obj *>(1,((Obj *)((new Int(__ss_int(10LL)))))))))->as_int()==__ss_int(90LL))), 0);
    ASSERT(___bool(__eq(((g->__getitem__(const_117))->call((new list<Obj *>(2,((Obj *)((new Str(const_118)))),((Obj *)((new Int(__ss_int(2LL)))))))))->as_str(), const_119)), 0);
    ASSERT(___bool(__eq(((g->__getitem__(const_117))->call((new list<Obj *>(2,((Obj *)((new Str(const_118)))),((Obj *)((new Int(__ss_int(0LL)))))))))->as_str(), const_52)), 0);
    ASSERT(___bool(__eq((g->__getitem__(const_103))->as_str(), const_104)), 0);
    return NULL;
}

void *__ss_main() {
    list<str *> *__127, *__131, *args, *files;
    __ss_bool __ss_virtual, show;
    str *a, *path;
    __iter<str *> *__128, *__132;
    __ss_int __129, __133;
    list<str *>::for_in_loop __130, __134;

    args = (__sys__::argv)->__slice__(__ss_int(1LL), __ss_int(1LL), __ss_int(0LL), __ss_int(0LL));
    __ss_virtual = True;
    show = False;
    files = (__ss_list<str *, 0>());

    FOR_IN(a,args,127,129,130)
        if (__eq(a, const_120)) {
            __ss_virtual = True;
        }
        else if (__eq(a, const_121)) {
            __ss_virtual = False;
        }
        else if (__eq(a, const_122)) {
            show = True;
        }
        else {
            files->append(a);
        }
    END_FOR

    if ((len(files)==__ss_int(0LL))) {
        self_test(True);
        self_test(False);
        print(const_123);
    }
    else {

        FOR_IN(path,files,131,133,134)
            run_file(path, __ss_virtual, show);
        END_FOR

    }
    return NULL;
}

void __init() {
    __name__ = new str("__main__");

    const_0 = new str("pyvm - a tiny CPython 3.14 bytecode interpreter, written in Shedskin-compatible Python.\012\012Reads a real .pyc file produced by CPython 3.14 (marshal format, magic 3627),\012decodes the code object into a list of Instruction objects and runs it.\012\012Two dispatch strategies are implemented over the *same* decoded instruction\012list, so they can be benchmarked against each other:\012\012  --virtual  one Instruction subclass per opcode, `execute()` is a virtual call\012  --ifelse   a single long if/elif chain on the opcode number\012\012Only a handful of opcodes are supported: enough for module-level code with\012integer/string constants, arithmetic, comparisons, while-loops and print().\012\012Usage:\012    pyvm [--virtual|--ifelse] file.pyc\012    pyvm            (no arguments: run the bundled testdata with both dispatchers)\012");
    const_1 = __char_cache[78];
    const_2 = __char_cache[70];
    const_3 = __char_cache[84];
    const_4 = __char_cache[105];
    const_5 = __char_cache[115];
    const_6 = __char_cache[40];
    const_7 = __char_cache[41];
    const_8 = __char_cache[97];
    const_9 = __char_cache[65];
    const_10 = __char_cache[122];
    const_11 = __char_cache[90];
    const_12 = __char_cache[117];
    const_13 = __char_cache[114];
    const_14 = __char_cache[99];
    const_15 = new str("CACHE");
    const_16 = new str("NOP");
    const_17 = new str("NOT_TAKEN");
    const_18 = new str("POP_TOP");
    const_19 = new str("PUSH_NULL");
    const_20 = new str("RETURN_VALUE");
    const_21 = new str("TO_BOOL");
    const_22 = new str("BINARY_OP");
    const_23 = new str("CALL");
    const_24 = new str("COMPARE_OP");
    const_25 = new str("EXTENDED_ARG");
    const_26 = new str("JUMP_BACKWARD");
    const_27 = new str("JUMP_FORWARD");
    const_28 = new str("LOAD_CONST");
    const_29 = new str("LOAD_FAST");
    const_30 = new str("LOAD_FAST_BORROW");
    const_31 = new str("LOAD_FAST_BORROW_LOAD_FAST_BORROW");
    const_32 = new str("LOAD_FAST_CHECK");
    const_33 = new str("LOAD_FAST_LOAD_FAST");
    const_34 = new str("LOAD_GLOBAL");
    const_35 = new str("MAKE_FUNCTION");
    const_36 = new str("STORE_FAST");
    const_37 = new str("STORE_FAST_LOAD_FAST");
    const_38 = new str("STORE_FAST_STORE_FAST");
    const_39 = new str("STORE_GLOBAL");
    const_40 = new str("LOAD_NAME");
    const_41 = new str("LOAD_SMALL_INT");
    const_42 = new str("POP_JUMP_IF_FALSE");
    const_43 = new str("POP_JUMP_IF_TRUE");
    const_44 = new str("STORE_NAME");
    const_45 = new str("RESUME");
    const_46 = new str("Base class of all runtime values. Subclasses override what they support.");
    const_47 = __char_cache[60];
    const_48 = __char_cache[62];
    const_49 = new str("TypeError: ");
    const_50 = new str(" is not an int");
    const_51 = new str(" is not a str");
    const_52 = new str("");
    const_53 = new str(" is not bytes");
    const_54 = new bytes("");
    const_55 = new str(" is not a tuple");
    const_56 = new str(" is not a code object");
    const_57 = new str("TypeError: unsupported operand type for binary op: ");
    const_58 = new str(" is not orderable");
    const_59 = new str(" object is not callable");
    const_60 = new str("NoneType");
    const_61 = new str("None");
    const_62 = new str("TypeError: '<' not supported for NoneType");
    const_63 = new str("The NULL pushed by PUSH_NULL: the empty self_or_null slot of a call.");
    const_64 = new str("NULL");
    const_65 = new str("int");
    const_66 = new str("TypeError: unsupported int binary op %d");
    const_67 = new str("bool");
    const_68 = new str("True");
    const_69 = new str("False");
    const_70 = new str("str");
    const_71 = new str("TypeError: unsupported str binary op %d");
    const_72 = new str("bytes");
    const_73 = new str("tuple");
    const_74 = new str(", ");
    const_75 = new str("A code object, as unmarshalled from the .pyc (CPython 3.14 field layout).");
    const_76 = new str("code");
    const_77 = new str("<code object ");
    const_78 = new str(", file \042");
    const_79 = new str("\042, line %d>");
    const_80 = new str("function");
    const_81 = new str("<function ");
    const_82 = new str("TypeError: %s() takes %d positional arguments but %d were given");
    const_83 = new str("builtin_function_or_method");
    const_84 = new str("<built-in function print>");
    const_85 = __char_cache[32];
    const_86 = new str("marshal: unsupported type code %d (%s) at offset %d");
    const_87 = new str("rb");
    const_88 = new str("%s: bad magic number %d (expected %d, i.e. CPython 3.14)");
    const_89 = new str("One decoded instruction. All fields any opcode might need live in the\012    base class, so that the if/elif dispatcher can use them without downcasts.\012    Subclasses only override execute().");
    const_90 = new str("unsupported opcode %d");
    const_91 = new str("%-18s %d");
    const_92 = new str("op%d");
    const_93 = new str("NameError: name '");
    const_94 = new str("' is not defined");
    const_95 = new str("print");
    const_96 = new str("decode: unsupported opcode %d (%s)");
    const_97 = __char_cache[63];
    const_98 = new str("Decode co_code into Instr objects. CACHE entries are dropped; jump\012    arguments (in code units, relative to the unit after the jump's caches)\012    are converted to instruction-list indices.");
    const_99 = new str(" (%d instructions):");
    const_100 = new str("(to %d)");
    const_101 = new str("%4d  %s %s");
    const_102 = new str("Load, decode and run a .pyc; returns the module globals afterwards.");
    const_103 = new str("__name__");
    const_104 = new str("__main__");
    const_105 = new str("Run the bundled testdata and check results against CPython's answers.");
    const_106 = new str("ifelse");
    const_107 = new str("virtual");
    const_108 = new str("--- %s: testdata/hello.pyc");
    const_109 = new str("testdata/hello.pyc");
    const_110 = new str("--- %s: testdata/loop.pyc");
    const_111 = new str("testdata/loop.pyc");
    const_112 = new str("total");
    const_113 = new str("--- %s: testdata/funcs.pyc");
    const_114 = new str("testdata/funcs.pyc");
    const_115 = new str("fib");
    const_116 = new str("loop");
    const_117 = new str("greet");
    const_118 = __char_cache[120];
    const_119 = new str("hello x! hello x! ");
    const_120 = new str("--virtual");
    const_121 = new str("--ifelse");
    const_122 = new str("--dis");
    const_123 = new str("ok");

    MAGIC = __ss_int(3627LL);
    TYPE_NONE = ord(const_1);
    TYPE_FALSE = ord(const_2);
    TYPE_TRUE = ord(const_3);
    TYPE_INT = ord(const_4);
    TYPE_STRING = ord(const_5);
    TYPE_TUPLE = ord(const_6);
    TYPE_SMALL_TUPLE = ord(const_7);
    TYPE_ASCII = ord(const_8);
    TYPE_ASCII_INTERNED = ord(const_9);
    TYPE_SHORT_ASCII = ord(const_10);
    TYPE_SHORT_ASCII_INTERNED = ord(const_11);
    TYPE_UNICODE = ord(const_12);
    TYPE_REF = ord(const_13);
    TYPE_CODE = ord(const_14);
    FLAG_REF = __ss_int(128LL);
    OP_CACHE = __ss_int(0LL);
    OP_NOP = __ss_int(27LL);
    OP_NOT_TAKEN = __ss_int(28LL);
    OP_MAKE_FUNCTION = __ss_int(23LL);
    OP_POP_TOP = __ss_int(31LL);
    OP_PUSH_NULL = __ss_int(33LL);
    OP_RETURN_VALUE = __ss_int(35LL);
    OP_TO_BOOL = __ss_int(39LL);
    OP_BINARY_OP = __ss_int(44LL);
    OP_CALL = __ss_int(52LL);
    OP_COMPARE_OP = __ss_int(56LL);
    OP_EXTENDED_ARG = __ss_int(69LL);
    OP_JUMP_BACKWARD = __ss_int(75LL);
    OP_JUMP_FORWARD = __ss_int(77LL);
    OP_LOAD_CONST = __ss_int(82LL);
    OP_LOAD_FAST = __ss_int(84LL);
    OP_LOAD_FAST_BORROW = __ss_int(86LL);
    OP_LOAD_FAST_BORROW_LOAD_FAST_BORROW = __ss_int(87LL);
    OP_LOAD_FAST_CHECK = __ss_int(88LL);
    OP_LOAD_FAST_LOAD_FAST = __ss_int(89LL);
    OP_LOAD_GLOBAL = __ss_int(92LL);
    OP_LOAD_NAME = __ss_int(93LL);
    OP_LOAD_SMALL_INT = __ss_int(94LL);
    OP_POP_JUMP_IF_FALSE = __ss_int(100LL);
    OP_POP_JUMP_IF_TRUE = __ss_int(103LL);
    OP_STORE_FAST = __ss_int(112LL);
    OP_STORE_FAST_LOAD_FAST = __ss_int(113LL);
    OP_STORE_FAST_STORE_FAST = __ss_int(114LL);
    OP_STORE_GLOBAL = __ss_int(115LL);
    OP_STORE_NAME = __ss_int(116LL);
    OP_RESUME = __ss_int(128LL);
    INLINE_CACHE = (new dict<__ss_int, __ss_int>(8, (new tuple<__ss_int >(2,__pyvm__::OP_LOAD_GLOBAL,__ss_int(4LL))),(new tuple<__ss_int >(2,__pyvm__::OP_TO_BOOL,__ss_int(3LL))),(new tuple<__ss_int >(2,__pyvm__::OP_BINARY_OP,__ss_int(5LL))),(new tuple<__ss_int >(2,__pyvm__::OP_CALL,__ss_int(3LL))),(new tuple<__ss_int >(2,__pyvm__::OP_COMPARE_OP,__ss_int(1LL))),(new tuple<__ss_int >(2,__pyvm__::OP_JUMP_BACKWARD,__ss_int(1LL))),(new tuple<__ss_int >(2,__pyvm__::OP_POP_JUMP_IF_FALSE,__ss_int(1LL))),(new tuple<__ss_int >(2,__pyvm__::OP_POP_JUMP_IF_TRUE,__ss_int(1LL)))));
    OPNAME = (new dict<__ss_int, str *>(31, (new tuple2<__ss_int , str *>(2,__pyvm__::OP_CACHE,const_15)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_NOP,const_16)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_NOT_TAKEN,const_17)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_POP_TOP,const_18)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_PUSH_NULL,const_19)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_RETURN_VALUE,const_20)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_TO_BOOL,const_21)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_BINARY_OP,const_22)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_CALL,const_23)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_COMPARE_OP,const_24)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_EXTENDED_ARG,const_25)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_JUMP_BACKWARD,const_26)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_JUMP_FORWARD,const_27)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_LOAD_CONST,const_28)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_LOAD_FAST,const_29)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_LOAD_FAST_BORROW,const_30)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_LOAD_FAST_BORROW_LOAD_FAST_BORROW,const_31)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_LOAD_FAST_CHECK,const_32)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_LOAD_FAST_LOAD_FAST,const_33)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_LOAD_GLOBAL,const_34)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_MAKE_FUNCTION,const_35)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_STORE_FAST,const_36)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_STORE_FAST_LOAD_FAST,const_37)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_STORE_FAST_STORE_FAST,const_38)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_STORE_GLOBAL,const_39)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_LOAD_NAME,const_40)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_LOAD_SMALL_INT,const_41)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_POP_JUMP_IF_FALSE,const_42)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_POP_JUMP_IF_TRUE,const_43)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_STORE_NAME,const_44)),(new tuple2<__ss_int , str *>(2,__pyvm__::OP_RESUME,const_45))));
    NB_ADD = __ss_int(0LL);
    NB_AND = __ss_int(1LL);
    NB_FLOOR_DIVIDE = __ss_int(2LL);
    NB_LSHIFT = __ss_int(3LL);
    NB_MULTIPLY = __ss_int(5LL);
    NB_REMAINDER = __ss_int(6LL);
    NB_OR = __ss_int(7LL);
    NB_RSHIFT = __ss_int(9LL);
    NB_SUBTRACT = __ss_int(10LL);
    NB_XOR = __ss_int(12LL);
    NB_INPLACE_OFFSET = __ss_int(13LL);
    CMP_LT = __ss_int(0LL);
    CMP_LE = __ss_int(1LL);
    CMP_EQ = __ss_int(2LL);
    CMP_NE = __ss_int(3LL);
    CMP_GT = __ss_int(4LL);
    CMP_GE = __ss_int(5LL);
    cl_Obj = new class_("Obj");
    Obj::__static__();
    cl_NoneObj = new class_("NoneObj");
    cl_Null = new class_("Null");
    Null::__static__();
    cl_Int = new class_("Int");
    cl_Bool = new class_("Bool");
    cl_Str = new class_("Str");
    cl_Bytes = new class_("Bytes");
    cl_Tuple = new class_("Tuple");
    cl_Code = new class_("Code");
    Code::__static__();
    cl_Function = new class_("Function");
    cl_PrintFn = new class_("PrintFn");
    __ss_NONE = (new NoneObj());
    NULL_OBJ = (new Null());
    __ss_TRUE = (new Bool(__ss_int(1LL)));
    __ss_FALSE = (new Bool(__ss_int(0LL)));
    NO_ITEMS = ((new list<Obj *>(2,((Obj *)(__pyvm__::__ss_NONE)),((Obj *)(__pyvm__::__ss_TRUE)))))->__slice__(__ss_int(2LL), __ss_int(0LL), __ss_int(0LL), __ss_int(0LL));
    NO_NAMES = (new list<str *>(1,const_52));
    SMALL_INTS = list_comp_2();
    cl_Reader = new class_("Reader");
    cl_Frame = new class_("Frame");
    cl_Instr = new class_("Instr");
    Instr::__static__();
    cl_Nop = new class_("Nop");
    cl_PopTop = new class_("PopTop");
    cl_PushNull = new class_("PushNull");
    cl_ReturnValue = new class_("ReturnValue");
    cl_ToBool = new class_("ToBool");
    cl_BinaryOp = new class_("BinaryOp");
    cl_Call = new class_("Call");
    cl_CompareOp = new class_("CompareOp");
    cl_Jump = new class_("Jump");
    cl_PopJumpIfFalse = new class_("PopJumpIfFalse");
    cl_PopJumpIfTrue = new class_("PopJumpIfTrue");
    cl_LoadConst = new class_("LoadConst");
    cl_LoadName = new class_("LoadName");
    cl_StoreName = new class_("StoreName");
    cl_LoadGlobal = new class_("LoadGlobal");
    cl_LoadFast = new class_("LoadFast");
    cl_LoadFastLoadFast = new class_("LoadFastLoadFast");
    cl_StoreFast = new class_("StoreFast");
    cl_StoreFastStoreFast = new class_("StoreFastStoreFast");
    cl_StoreFastLoadFast = new class_("StoreFastLoadFast");
    cl_MakeFunction = new class_("MakeFunction");
    NO_INSTRS = (new list<Instr *>(1,(new Instr(__pyvm__::OP_NOP, __ss_int(0LL)))));
    NO_CODE = (new Code(1));
    BUILTINS = (new dict<str *, PrintFn *>(1, (new tuple2<str *, PrintFn *>(2,const_95,(new PrintFn())))));
    VIRTUAL = (new list<__ss_bool>(1,True));
    if (__eq(__pyvm__::__name__, const_104)) {
        __ss_main();
    }
}

} // module namespace

int main(int __ss_argc, char **__ss_argv) {
    __shedskin__::__init();
    __sys__::__init(__ss_argc, __ss_argv);
    __shedskin__::__start(__pyvm__::__init);
}
