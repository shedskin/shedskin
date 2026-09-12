#ifndef __PYVM_HPP
#define __PYVM_HPP

using namespace __shedskin__;

namespace __pyvm__ {
class Obj;
class NoneObj;
class Null;
class Int;
class Bool;
class Str;
class Bytes;
class Tuple;
class Code;
class Function;
class PrintFn;
class Reader;
class Frame;
class Instr;
class Nop;
class PopTop;
class PushNull;
class ReturnValue;
class ToBool;
class BinaryOp;
class Call;
class CompareOp;
class Jump;
class PopJumpIfFalse;
class PopJumpIfTrue;
class LoadConst;
class LoadName;
class StoreName;
class LoadGlobal;
class LoadFast;
class LoadFastLoadFast;
class StoreFast;
class StoreFastStoreFast;
class StoreFastLoadFast;
class MakeFunction;
}
namespace __pyvm__ {

extern str *const_0, *const_1, *const_10, *const_100, *const_101, *const_102, *const_103, *const_104, *const_105, *const_106, *const_107, *const_108, *const_109, *const_11, *const_110, *const_111, *const_112, *const_113, *const_114, *const_115, *const_116, *const_117, *const_118, *const_119, *const_12, *const_120, *const_121, *const_122, *const_123, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_2, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_26, *const_27, *const_28, *const_29, *const_3, *const_30, *const_31, *const_32, *const_33, *const_34, *const_35, *const_36, *const_37, *const_38, *const_39, *const_4, *const_40, *const_41, *const_42, *const_43, *const_44, *const_45, *const_46, *const_47, *const_48, *const_49, *const_5, *const_50, *const_51, *const_52, *const_53, *const_55, *const_56, *const_57, *const_58, *const_59, *const_6, *const_60, *const_61, *const_62, *const_63, *const_64, *const_65, *const_66, *const_67, *const_68, *const_69, *const_7, *const_70, *const_71, *const_72, *const_73, *const_74, *const_75, *const_76, *const_77, *const_78, *const_79, *const_8, *const_80, *const_81, *const_82, *const_83, *const_84, *const_85, *const_86, *const_87, *const_88, *const_89, *const_9, *const_90, *const_91, *const_92, *const_93, *const_94, *const_95, *const_96, *const_97, *const_98, *const_99;
extern bytes *const_54;

class Obj;
class NoneObj;
class Null;
class Int;
class Bool;
class Str;
class Bytes;
class Tuple;
class Code;
class Function;
class PrintFn;
class Reader;
class Frame;
class Instr;
class Nop;
class PopTop;
class PushNull;
class ReturnValue;
class ToBool;
class BinaryOp;
class Call;
class CompareOp;
class Jump;
class PopJumpIfFalse;
class PopJumpIfTrue;
class LoadConst;
class LoadName;
class StoreName;
class LoadGlobal;
class LoadFast;
class LoadFastLoadFast;
class StoreFast;
class StoreFastStoreFast;
class StoreFastLoadFast;
class MakeFunction;


extern file *__file;
extern __ss_int CMP_EQ, CMP_GE, CMP_GT, CMP_LE, CMP_LT, CMP_NE, FLAG_REF, MAGIC, NB_ADD, NB_AND, NB_FLOOR_DIVIDE, NB_INPLACE_OFFSET, NB_LSHIFT, NB_MULTIPLY, NB_OR, NB_REMAINDER, NB_RSHIFT, NB_SUBTRACT, NB_XOR, OP_BINARY_OP, OP_CACHE, OP_CALL, OP_COMPARE_OP, OP_EXTENDED_ARG, OP_JUMP_BACKWARD, OP_JUMP_FORWARD, OP_LOAD_CONST, OP_LOAD_FAST, OP_LOAD_FAST_BORROW, OP_LOAD_FAST_BORROW_LOAD_FAST_BORROW, OP_LOAD_FAST_CHECK, OP_LOAD_FAST_LOAD_FAST, OP_LOAD_GLOBAL, OP_LOAD_NAME, OP_LOAD_SMALL_INT, OP_MAKE_FUNCTION, OP_NOP, OP_NOT_TAKEN, OP_POP_JUMP_IF_FALSE, OP_POP_JUMP_IF_TRUE, OP_POP_TOP, OP_PUSH_NULL, OP_RESUME, OP_RETURN_VALUE, OP_STORE_FAST, OP_STORE_FAST_LOAD_FAST, OP_STORE_FAST_STORE_FAST, OP_STORE_GLOBAL, OP_STORE_NAME, OP_TO_BOOL, TYPE_ASCII, TYPE_ASCII_INTERNED, TYPE_CODE, TYPE_FALSE, TYPE_INT, TYPE_NONE, TYPE_REF, TYPE_SHORT_ASCII, TYPE_SHORT_ASCII_INTERNED, TYPE_SMALL_TUPLE, TYPE_STRING, TYPE_TRUE, TYPE_TUPLE, TYPE_UNICODE, __void;
extern str *__name__;
extern dict<__ss_int, __ss_int> *INLINE_CACHE;
extern dict<__ss_int, str *> *OPNAME;
extern NoneObj *__ss_NONE;
extern Null *NULL_OBJ;
extern Bool *__ss_FALSE, *__ss_TRUE;
extern list<Obj *> *NO_ITEMS;
extern list<str *> *NO_NAMES;
extern list<Int *> *SMALL_INTS;
extern list<Instr *> *NO_INSTRS;
extern Code *NO_CODE;
extern dict<str *, PrintFn *> *BUILTINS;
extern list<__ss_bool> *VIRTUAL;


extern class_ *cl_Obj;
class Obj : public pyobj {
/**
Base class of all runtime values. Subclasses override what they support.
*/
public:

    Obj() { this->__class__ = cl_Obj; }
    static void __static__();
    virtual str *type_name() { return 0; };
    virtual str *_str_();
    virtual __ss_int  as_int();
    virtual str *as_str();
    virtual str *repr_();
    virtual bytes *as_bytes();
    virtual list<Obj *> *items();
    virtual Code *as_code();
    virtual __ss_bool  truth();
    virtual Obj *binary_op(__ss_int  op, Obj *other);
    virtual __ss_bool  compare(__ss_int  op, Obj *other);
    virtual Obj *call(list<Obj *> *args);
    virtual __ss_bool  is_code();
};

extern class_ *cl_NoneObj;
class NoneObj : public Obj {
public:

    NoneObj() { this->__class__ = cl_NoneObj; }
    str *type_name();
    str *_str_();
    __ss_bool truth();
    __ss_bool compare(__ss_int op, Obj *other);
};

extern class_ *cl_Null;
class Null : public Obj {
/**
The NULL pushed by PUSH_NULL: the empty self_or_null slot of a call.
*/
public:

    Null() { this->__class__ = cl_Null; }
    static void __static__();
    str *type_name();
};

extern class_ *cl_Int;
class Int : public Obj {
public:

    __ss_int v;

    Int() {}
    Int(__ss_int v) {
        this->__class__ = cl_Int;
        __init__(v);
    }
    void *__init__(__ss_int v);
    str *type_name();
    str *_str_();
    __ss_bool truth();
    __ss_int as_int();
    Obj *binary_op(__ss_int op, Obj *other);
    __ss_bool compare(__ss_int op, Obj *other);
};

extern class_ *cl_Bool;
class Bool : public Int {
public:

    Bool() {}
    Bool(__ss_int v) {
        this->__class__ = cl_Bool;
        __init__(v);
    }
    void *__init__(__ss_int v);
    str *type_name();
    str *_str_();
};

extern class_ *cl_Str;
class Str : public Obj {
public:
    str *s;

    Str() {}
    Str(str *s) {
        this->__class__ = cl_Str;
        __init__(s);
    }
    void *__init__(str *s);
    str *type_name();
    str *_str_();
    str *repr_();
    __ss_bool truth();
    str *as_str();
    Obj *binary_op(__ss_int op, Obj *other);
    __ss_bool compare(__ss_int op, Obj *other);
};

extern class_ *cl_Bytes;
class Bytes : public Obj {
public:
    bytes *b;

    Bytes() {}
    Bytes(bytes *b) {
        this->__class__ = cl_Bytes;
        __init__(b);
    }
    void *__init__(bytes *b);
    str *type_name();
    str *_str_();
    __ss_bool truth();
    bytes *as_bytes();
};

extern class_ *cl_Tuple;
class Tuple : public Obj {
public:
    list<Obj *> *l;

    Tuple() {}
    Tuple(list<Obj *> *l) {
        this->__class__ = cl_Tuple;
        __init__(l);
    }
    void *__init__(list<Obj *> *l);
    str *type_name();
    str *_str_();
    __ss_bool truth();
    list<Obj *> *items();
};

extern class_ *cl_Code;
class Code : public Obj {
/**
A code object, as unmarshalled from the .pyc (CPython 3.14 field layout).
*/
public:
    __ss_int argcount;
    bytes *co_code;
    list<Obj *> *consts;
    bytes *exceptiontable;
    str *filename;
    __ss_int firstlineno;
    __ss_int flags;
    list<Instr *> *instrs;
    __ss_int kwonlyargcount;
    bytes *linetable;
    bytes *localspluskinds;
    list<str *> *localsplusnames;
    str *name;
    list<str *> *names;
    __ss_int posonlyargcount;
    str *qualname;
    __ss_int stacksize;

    Code() {}
    Code(int __ss_init) {
        this->__class__ = cl_Code;
        __init__();
    }
    static void __static__();
    void *__init__();
    str *type_name();
    str *_str_();
    __ss_bool is_code();
    Code *as_code();
};

extern class_ *cl_Function;
class Function : public Obj {
public:
    Code *code;
    dict<str *, Obj *> *globals;

    Function() {}
    Function(Code *code, dict<str *, Obj *> *globals_) {
        this->__class__ = cl_Function;
        __init__(code, globals_);
    }
    void *__init__(Code *code, dict<str *, Obj *> *globals_);
    str *type_name();
    str *_str_();
    Obj *call(list<Obj *> *args);
};

extern class_ *cl_PrintFn;
class PrintFn : public Obj {
public:

    PrintFn() { this->__class__ = cl_PrintFn; }
    str *type_name();
    str *_str_();
    Obj *call(list<Obj *> *args);
};

extern class_ *cl_Reader;
class Reader : public pyobj {
public:
    bytes *data;
    __ss_int nrefs;
    __ss_int pos;
    list<Obj *> *refs;

    Reader() {}
    Reader(bytes *data) {
        this->__class__ = cl_Reader;
        __init__(data);
    }
    void *__init__(bytes *data);
    __ss_int byte();
    __ss_int __ss_long();
    bytes *raw(__ss_int n);
    __ss_int reserve_ref();
    Obj *read();
    Obj *read_type(__ss_int t);
    list<Obj *> *read_items(__ss_int n);
    Code *read_code();
};

extern class_ *cl_Frame;
class Frame : public pyobj {
public:
    Code *code;
    dict<str *, Obj *> *globals;
    list<Obj *> *locals;
    __ss_int pc;
    Obj *retval;
    __ss_bool running;
    __ss_int sp;
    list<Obj *> *stack;

    Frame() {}
    Frame(Code *code, dict<str *, Obj *> *globals_) {
        this->__class__ = cl_Frame;
        __init__(code, globals_);
    }
    void *__init__(Code *code, dict<str *, Obj *> *globals_);
    void *push(Obj *o);
    Obj *pop();
};

extern class_ *cl_Instr;
class Instr : public pyobj {
/**
One decoded instruction. All fields any opcode might need live in the
base class, so that the if/elif dispatcher can use them without downcasts.
Subclasses only override execute().
*/
public:
    __ss_int arg;
    __ss_int arg2;
    str *name;
    __ss_int op;
    __ss_int target;
    Obj *value;

    Instr() {}
    Instr(__ss_int op, __ss_int arg) {
        this->__class__ = cl_Instr;
        __init__(op, arg);
    }
    static void __static__();
    virtual void *execute(Frame *f);
    void *__init__(__ss_int op, __ss_int arg);
    str *__repr__();
};

extern class_ *cl_Nop;
class Nop : public Instr {
public:

    Nop() {}
    Nop(__ss_int op, __ss_int arg) {
        this->__class__ = cl_Nop;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_PopTop;
class PopTop : public Instr {
public:

    PopTop() {}
    PopTop(__ss_int op, __ss_int arg) {
        this->__class__ = cl_PopTop;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_PushNull;
class PushNull : public Instr {
public:

    PushNull() {}
    PushNull(__ss_int op, __ss_int arg) {
        this->__class__ = cl_PushNull;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_ReturnValue;
class ReturnValue : public Instr {
public:

    ReturnValue() {}
    ReturnValue(__ss_int op, __ss_int arg) {
        this->__class__ = cl_ReturnValue;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_ToBool;
class ToBool : public Instr {
public:

    ToBool() {}
    ToBool(__ss_int op, __ss_int arg) {
        this->__class__ = cl_ToBool;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_BinaryOp;
class BinaryOp : public Instr {
public:

    BinaryOp() {}
    BinaryOp(__ss_int op, __ss_int arg) {
        this->__class__ = cl_BinaryOp;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_Call;
class Call : public Instr {
public:

    Call() {}
    Call(__ss_int op, __ss_int arg) {
        this->__class__ = cl_Call;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_CompareOp;
class CompareOp : public Instr {
public:

    CompareOp() {}
    CompareOp(__ss_int op, __ss_int arg) {
        this->__class__ = cl_CompareOp;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_Jump;
class Jump : public Instr {
public:

    Jump() {}
    Jump(__ss_int op, __ss_int arg) {
        this->__class__ = cl_Jump;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_PopJumpIfFalse;
class PopJumpIfFalse : public Instr {
public:

    PopJumpIfFalse() {}
    PopJumpIfFalse(__ss_int op, __ss_int arg) {
        this->__class__ = cl_PopJumpIfFalse;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_PopJumpIfTrue;
class PopJumpIfTrue : public Instr {
public:

    PopJumpIfTrue() {}
    PopJumpIfTrue(__ss_int op, __ss_int arg) {
        this->__class__ = cl_PopJumpIfTrue;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_LoadConst;
class LoadConst : public Instr {
public:

    LoadConst() {}
    LoadConst(__ss_int op, __ss_int arg) {
        this->__class__ = cl_LoadConst;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_LoadName;
class LoadName : public Instr {
public:

    LoadName() {}
    LoadName(__ss_int op, __ss_int arg) {
        this->__class__ = cl_LoadName;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_StoreName;
class StoreName : public Instr {
public:

    StoreName() {}
    StoreName(__ss_int op, __ss_int arg) {
        this->__class__ = cl_StoreName;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_LoadGlobal;
class LoadGlobal : public Instr {
public:

    LoadGlobal() {}
    LoadGlobal(__ss_int op, __ss_int arg) {
        this->__class__ = cl_LoadGlobal;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_LoadFast;
class LoadFast : public Instr {
public:

    LoadFast() {}
    LoadFast(__ss_int op, __ss_int arg) {
        this->__class__ = cl_LoadFast;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_LoadFastLoadFast;
class LoadFastLoadFast : public Instr {
public:

    LoadFastLoadFast() {}
    LoadFastLoadFast(__ss_int op, __ss_int arg) {
        this->__class__ = cl_LoadFastLoadFast;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_StoreFast;
class StoreFast : public Instr {
public:

    StoreFast() {}
    StoreFast(__ss_int op, __ss_int arg) {
        this->__class__ = cl_StoreFast;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_StoreFastStoreFast;
class StoreFastStoreFast : public Instr {
public:

    StoreFastStoreFast() {}
    StoreFastStoreFast(__ss_int op, __ss_int arg) {
        this->__class__ = cl_StoreFastStoreFast;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_StoreFastLoadFast;
class StoreFastLoadFast : public Instr {
public:

    StoreFastLoadFast() {}
    StoreFastLoadFast(__ss_int op, __ss_int arg) {
        this->__class__ = cl_StoreFastLoadFast;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

extern class_ *cl_MakeFunction;
class MakeFunction : public Instr {
public:

    MakeFunction() {}
    MakeFunction(__ss_int op, __ss_int arg) {
        this->__class__ = cl_MakeFunction;
        __init__(op, arg);
    }
    void *execute(Frame *f);
};

str *decode_ascii(bytes *b);
Code *load_pyc(str *path);
Obj *lookup_name(Frame *f, str *name);
Obj *do_call(Frame *f, __ss_int nargs);
Instr *make_instr(Code *code, __ss_int op, __ss_int arg);
list<Instr *> *decode(Code *code);
void *disassemble(Code *code);
Obj *run_frame(Frame *f);
Obj *run_virtual(Frame *f);
Obj *run_ifelse(Frame *f);
dict<str *, Obj *> *run_file(str *path, __ss_bool __ss_virtual, __ss_bool show);
void *self_test(__ss_bool __ss_virtual);
void *__ss_main();

} // module namespace
#endif
