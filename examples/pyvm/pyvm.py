"""pyvm - a tiny CPython 3.14 bytecode interpreter, written in Shedskin-compatible Python.

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
"""

import sys

# ---------------------------------------------------------------------------
# CPython 3.14 constants

MAGIC = 3627  # importlib.util.MAGIC_NUMBER for 3.14, little-endian first two bytes

# marshal type codes
TYPE_NONE = ord('N')
TYPE_FALSE = ord('F')
TYPE_TRUE = ord('T')
TYPE_INT = ord('i')
TYPE_STRING = ord('s')      # bytes
TYPE_TUPLE = ord('(')
TYPE_SMALL_TUPLE = ord(')')
TYPE_ASCII = ord('a')
TYPE_ASCII_INTERNED = ord('A')
TYPE_SHORT_ASCII = ord('z')
TYPE_SHORT_ASCII_INTERNED = ord('Z')
TYPE_UNICODE = ord('u')
TYPE_REF = ord('r')
TYPE_CODE = ord('c')
FLAG_REF = 0x80

# opcodes (dis.opmap on 3.14)
OP_CACHE = 0
OP_NOP = 27
OP_NOT_TAKEN = 28
OP_MAKE_FUNCTION = 23
OP_POP_TOP = 31
OP_PUSH_NULL = 33
OP_RETURN_VALUE = 35
OP_TO_BOOL = 39
OP_BINARY_OP = 44
OP_CALL = 52
OP_COMPARE_OP = 56
OP_EXTENDED_ARG = 69
OP_JUMP_BACKWARD = 75
OP_JUMP_FORWARD = 77
OP_LOAD_CONST = 82
OP_LOAD_FAST = 84
OP_LOAD_FAST_BORROW = 86
OP_LOAD_FAST_BORROW_LOAD_FAST_BORROW = 87
OP_LOAD_FAST_CHECK = 88
OP_LOAD_FAST_LOAD_FAST = 89
OP_LOAD_GLOBAL = 92
OP_LOAD_NAME = 93
OP_LOAD_SMALL_INT = 94
OP_POP_JUMP_IF_FALSE = 100
OP_POP_JUMP_IF_TRUE = 103
OP_STORE_FAST = 112
OP_STORE_FAST_LOAD_FAST = 113
OP_STORE_FAST_STORE_FAST = 114
OP_STORE_GLOBAL = 115
OP_STORE_NAME = 116
OP_RESUME = 128

# number of inline CACHE entries following each opcode (dis._inline_cache_entries)
INLINE_CACHE = {
    OP_LOAD_GLOBAL: 4,
    OP_TO_BOOL: 3,
    OP_BINARY_OP: 5,
    OP_CALL: 3,
    OP_COMPARE_OP: 1,
    OP_JUMP_BACKWARD: 1,
    OP_POP_JUMP_IF_FALSE: 1,
    OP_POP_JUMP_IF_TRUE: 1,
}

OPNAME = {
    OP_CACHE: 'CACHE',
    OP_NOP: 'NOP',
    OP_NOT_TAKEN: 'NOT_TAKEN',
    OP_POP_TOP: 'POP_TOP',
    OP_PUSH_NULL: 'PUSH_NULL',
    OP_RETURN_VALUE: 'RETURN_VALUE',
    OP_TO_BOOL: 'TO_BOOL',
    OP_BINARY_OP: 'BINARY_OP',
    OP_CALL: 'CALL',
    OP_COMPARE_OP: 'COMPARE_OP',
    OP_EXTENDED_ARG: 'EXTENDED_ARG',
    OP_JUMP_BACKWARD: 'JUMP_BACKWARD',
    OP_JUMP_FORWARD: 'JUMP_FORWARD',
    OP_LOAD_CONST: 'LOAD_CONST',
    OP_LOAD_FAST: 'LOAD_FAST',
    OP_LOAD_FAST_BORROW: 'LOAD_FAST_BORROW',
    OP_LOAD_FAST_BORROW_LOAD_FAST_BORROW: 'LOAD_FAST_BORROW_LOAD_FAST_BORROW',
    OP_LOAD_FAST_CHECK: 'LOAD_FAST_CHECK',
    OP_LOAD_FAST_LOAD_FAST: 'LOAD_FAST_LOAD_FAST',
    OP_LOAD_GLOBAL: 'LOAD_GLOBAL',
    OP_MAKE_FUNCTION: 'MAKE_FUNCTION',
    OP_STORE_FAST: 'STORE_FAST',
    OP_STORE_FAST_LOAD_FAST: 'STORE_FAST_LOAD_FAST',
    OP_STORE_FAST_STORE_FAST: 'STORE_FAST_STORE_FAST',
    OP_STORE_GLOBAL: 'STORE_GLOBAL',
    OP_LOAD_NAME: 'LOAD_NAME',
    OP_LOAD_SMALL_INT: 'LOAD_SMALL_INT',
    OP_POP_JUMP_IF_FALSE: 'POP_JUMP_IF_FALSE',
    OP_POP_JUMP_IF_TRUE: 'POP_JUMP_IF_TRUE',
    OP_STORE_NAME: 'STORE_NAME',
    OP_RESUME: 'RESUME',
}

# BINARY_OP oparg (opcode._nb_ops); inplace variants are 13 + these
NB_ADD = 0
NB_AND = 1
NB_FLOOR_DIVIDE = 2
NB_LSHIFT = 3
NB_MULTIPLY = 5
NB_REMAINDER = 6
NB_OR = 7
NB_RSHIFT = 9
NB_SUBTRACT = 10
NB_XOR = 12
NB_INPLACE_OFFSET = 13

# COMPARE_OP: oparg >> 5 indexes dis.cmp_op, oparg & 16 means "coerce to bool"
CMP_LT = 0
CMP_LE = 1
CMP_EQ = 2
CMP_NE = 3
CMP_GT = 4
CMP_GE = 5


# ---------------------------------------------------------------------------
# object model

class Obj:
    """Base class of all runtime values. Subclasses override what they support."""

    def type_name(self) -> str:
        return 'object'

    def str_(self) -> str:
        return '<' + self.type_name() + '>'

    def repr_(self) -> str:
        return self.str_()

    def truth(self) -> bool:
        return True

    def as_int(self) -> int:
        raise Exception('TypeError: ' + self.type_name() + ' is not an int')
        return 0

    def as_str(self) -> str:
        raise Exception('TypeError: ' + self.type_name() + ' is not a str')
        return ''

    def as_bytes(self) -> bytes:
        raise Exception('TypeError: ' + self.type_name() + ' is not bytes')
        return b''

    def items(self):
        raise Exception('TypeError: ' + self.type_name() + ' is not a tuple')
        return NO_ITEMS

    def is_code(self) -> bool:
        return False

    def as_code(self):
        raise Exception('TypeError: ' + self.type_name() + ' is not a code object')
        return NO_CODE

    def binary_op(self, op: int, other):
        raise Exception('TypeError: unsupported operand type for binary op: ' + self.type_name())
        return NONE

    def compare(self, op: int, other) -> bool:
        raise Exception('TypeError: ' + self.type_name() + ' is not orderable')
        return False

    def call(self, args):
        raise Exception('TypeError: ' + self.type_name() + ' object is not callable')
        return NONE


class NoneObj(Obj):
    def type_name(self) -> str:
        return 'NoneType'

    def str_(self) -> str:
        return 'None'

    def truth(self) -> bool:
        return False

    def compare(self, op: int, other) -> bool:
        if op == CMP_EQ:
            return other is self
        if op == CMP_NE:
            return other is not self
        raise Exception("TypeError: '<' not supported for NoneType")
        return False


class Null(Obj):
    """The NULL pushed by PUSH_NULL: the empty self_or_null slot of a call."""

    def type_name(self) -> str:
        return 'NULL'


class Int(Obj):
    def __init__(self, v: int):
        self.v = v

    def type_name(self) -> str:
        return 'int'

    def str_(self) -> str:
        return str(self.v)

    def truth(self) -> bool:
        return self.v != 0

    def as_int(self) -> int:
        return self.v

    def binary_op(self, op: int, other):
        b = other.as_int()
        a = self.v
        if op == NB_ADD:
            return Int(a + b)
        elif op == NB_SUBTRACT:
            return Int(a - b)
        elif op == NB_MULTIPLY:
            return Int(a * b)
        elif op == NB_FLOOR_DIVIDE:
            return Int(a // b)
        elif op == NB_REMAINDER:
            return Int(a % b)
        elif op == NB_AND:
            return Int(a & b)
        elif op == NB_OR:
            return Int(a | b)
        elif op == NB_XOR:
            return Int(a ^ b)
        elif op == NB_LSHIFT:
            return Int(a << b)
        elif op == NB_RSHIFT:
            return Int(a >> b)
        raise Exception('TypeError: unsupported int binary op %d' % op)

    def compare(self, op: int, other) -> bool:
        b = other.as_int()
        a = self.v
        if op == CMP_LT:
            return a < b
        elif op == CMP_LE:
            return a <= b
        elif op == CMP_EQ:
            return a == b
        elif op == CMP_NE:
            return a != b
        elif op == CMP_GT:
            return a > b
        return a >= b


class Bool(Int):
    def __init__(self, v: int):
        Int.__init__(self, v)

    def type_name(self) -> str:
        return 'bool'

    def str_(self) -> str:
        if self.v:
            return 'True'
        return 'False'


class Str(Obj):
    def __init__(self, s: str):
        self.s = s

    def type_name(self) -> str:
        return 'str'

    def str_(self) -> str:
        return self.s

    def repr_(self) -> str:
        return repr(self.s)

    def truth(self) -> bool:
        return len(self.s) != 0

    def as_str(self) -> str:
        return self.s

    def binary_op(self, op: int, other):
        if op == NB_ADD:
            return Str(self.s + other.as_str())
        elif op == NB_MULTIPLY:
            return Str(self.s * other.as_int())
        raise Exception('TypeError: unsupported str binary op %d' % op)

    def compare(self, op: int, other) -> bool:
        b = other.as_str()
        a = self.s
        if op == CMP_LT:
            return a < b
        elif op == CMP_LE:
            return a <= b
        elif op == CMP_EQ:
            return a == b
        elif op == CMP_NE:
            return a != b
        elif op == CMP_GT:
            return a > b
        return a >= b


class Bytes(Obj):
    def __init__(self, b: bytes):
        self.b = b

    def type_name(self) -> str:
        return 'bytes'

    def str_(self) -> str:
        return repr(self.b)

    def truth(self) -> bool:
        return len(self.b) != 0

    def as_bytes(self) -> bytes:
        return self.b


class Tuple(Obj):
    def __init__(self, l):
        self.l = l

    def type_name(self) -> str:
        return 'tuple'

    def str_(self) -> str:
        return '(' + ', '.join([x.repr_() for x in self.l]) + ')'

    def truth(self) -> bool:
        return len(self.l) != 0

    def items(self):
        return self.l


class Code(Obj):
    """A code object, as unmarshalled from the .pyc (CPython 3.14 field layout)."""

    def __init__(self):
        self.argcount = 0
        self.posonlyargcount = 0
        self.kwonlyargcount = 0
        self.stacksize = 0
        self.flags = 0
        self.co_code = b''
        self.consts = NO_ITEMS
        self.names = NO_NAMES
        self.localsplusnames = NO_NAMES
        self.localspluskinds = b''
        self.filename = ''
        self.name = ''
        self.qualname = ''
        self.firstlineno = 0
        self.linetable = b''
        self.exceptiontable = b''
        self.instrs = NO_INSTRS  # filled in by decode()

    def type_name(self) -> str:
        return 'code'

    def str_(self) -> str:
        return '<code object ' + self.name + ', file "' + self.filename + '", line %d>' % self.firstlineno

    def is_code(self) -> bool:
        return True

    def as_code(self):
        return self


class Function(Obj):
    def __init__(self, code: Code, globals_):
        self.code = code
        self.globals = globals_

    def type_name(self) -> str:
        return 'function'

    def str_(self) -> str:
        return '<function ' + self.code.qualname + '>'

    def call(self, args):
        code = self.code
        if len(args) != code.argcount:
            raise Exception('TypeError: %s() takes %d positional arguments but %d were given' % (code.name, code.argcount, len(args)))
        f = Frame(code, self.globals)
        for i in range(len(args)):
            f.locals[i] = args[i]
        return run_frame(f)


class PrintFn(Obj):
    def type_name(self) -> str:
        return 'builtin_function_or_method'

    def str_(self) -> str:
        return '<built-in function print>'

    def call(self, args):
        print(' '.join([a.str_() for a in args]))
        return NONE


NONE = NoneObj()
NULL_OBJ = Null()   # 'NULL' itself clashes with the C macro in generated C++
TRUE = Bool(1)
FALSE = Bool(0)
NO_ITEMS = [NONE, TRUE][:0]   # empty list[Obj]: shedskin types the literal by its (lca) contents
NO_NAMES = ['']
SMALL_INTS = [Int(i) for i in range(256)]


# ---------------------------------------------------------------------------
# marshal reader

def decode_ascii(b: bytes) -> str:
    return ''.join([chr(c) for c in b])


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.refs = [NONE]
        self.nrefs = 0

    def byte(self) -> int:
        b = self.data[self.pos]
        self.pos += 1
        return b

    def long(self) -> int:
        d = self.data
        p = self.pos
        v = d[p] | (d[p + 1] << 8) | (d[p + 2] << 16) | (d[p + 3] << 24)
        self.pos = p + 4
        if v >= (1 << 31):
            v -= (1 << 32)
        return v

    def raw(self, n: int) -> bytes:
        b = self.data[self.pos:self.pos + n]
        self.pos += n
        return b

    def reserve_ref(self) -> int:
        idx = self.nrefs
        if idx < len(self.refs):
            self.refs[idx] = NONE
        else:
            self.refs.append(NONE)
        self.nrefs += 1
        return idx

    def read(self) -> Obj:
        code = self.byte()
        flag = code & FLAG_REF
        t = code & ~FLAG_REF
        idx = -1
        if flag:
            idx = self.reserve_ref()
        obj = self.read_type(t)
        if flag:
            self.refs[idx] = obj
        return obj

    def read_type(self, t: int) -> Obj:
        if t == TYPE_NONE:
            return NONE
        elif t == TYPE_TRUE:
            return TRUE
        elif t == TYPE_FALSE:
            return FALSE
        elif t == TYPE_INT:
            return Int(self.long())
        elif t == TYPE_STRING:
            return Bytes(self.raw(self.long()))
        elif t == TYPE_SHORT_ASCII or t == TYPE_SHORT_ASCII_INTERNED:
            return Str(decode_ascii(self.raw(self.byte())))
        elif t == TYPE_ASCII or t == TYPE_ASCII_INTERNED or t == TYPE_UNICODE:
            return Str(decode_ascii(self.raw(self.long())))  # utf-8 not decoded
        elif t == TYPE_SMALL_TUPLE:
            return Tuple(self.read_items(self.byte()))
        elif t == TYPE_TUPLE:
            return Tuple(self.read_items(self.long()))
        elif t == TYPE_REF:
            return self.refs[self.long()]
        elif t == TYPE_CODE:
            return self.read_code()
        raise Exception('marshal: unsupported type code %d (%s) at offset %d' % (t, chr(t), self.pos - 1))

    def read_items(self, n: int):
        l = [NONE] * n
        for i in range(n):
            l[i] = self.read()
        return l

    def read_code(self) -> Code:
        c = Code()
        c.argcount = self.long()
        c.posonlyargcount = self.long()
        c.kwonlyargcount = self.long()
        c.stacksize = self.long()
        c.flags = self.long()
        c.co_code = self.read().as_bytes()
        c.consts = self.read().items()
        c.names = [x.as_str() for x in self.read().items()]
        c.localsplusnames = [x.as_str() for x in self.read().items()]
        c.localspluskinds = self.read().as_bytes()
        c.filename = self.read().as_str()
        c.name = self.read().as_str()
        c.qualname = self.read().as_str()
        c.firstlineno = self.long()
        c.linetable = self.read().as_bytes()
        c.exceptiontable = self.read().as_bytes()
        return c


def load_pyc(path: str) -> Code:
    data = open(path, 'rb').read()
    magic = data[0] | (data[1] << 8)
    if magic != MAGIC or data[2] != 13 or data[3] != 10:
        raise Exception('%s: bad magic number %d (expected %d, i.e. CPython 3.14)' % (path, magic, MAGIC))
    r = Reader(data)
    r.pos = 16  # magic(4) flags(4) mtime(4) size(4)
    return r.read().as_code()


# ---------------------------------------------------------------------------
# instructions

class Frame:
    def __init__(self, code: Code, globals_):
        self.code = code
        self.globals = globals_
        self.pc = 0
        self.stack = [NONE] * (code.stacksize + 1)
        self.locals = [NONE] * (len(code.localsplusnames) + 1)
        self.sp = 0
        self.running = True
        self.retval = NONE

    def push(self, o: Obj) -> None:
        self.stack[self.sp] = o
        self.sp += 1

    def pop(self) -> Obj:
        self.sp -= 1
        return self.stack[self.sp]


class Instr:
    """One decoded instruction. All fields any opcode might need live in the
    base class, so that the if/elif dispatcher can use them without downcasts.
    Subclasses only override execute()."""

    def __init__(self, op: int, arg: int):
        self.op = op
        self.arg = arg
        self.arg2 = 0         # second operand of the LOAD_FAST_LOAD_FAST family
        self.target = 0       # resolved jump target (index into code.instrs)
        self.value = NONE     # pre-resolved constant (LOAD_CONST/LOAD_SMALL_INT)
        self.name = ''        # pre-resolved name (LOAD_NAME/STORE_NAME)

    def execute(self, f: Frame) -> None:
        raise Exception('unsupported opcode %d' % self.op)

    def __repr__(self) -> str:
        return '%-18s %d' % (OPNAME.get(self.op, 'op%d' % self.op), self.arg)


class Nop(Instr):
    def execute(self, f: Frame) -> None:
        pass


class PopTop(Instr):
    def execute(self, f: Frame) -> None:
        f.sp -= 1


class PushNull(Instr):
    def execute(self, f: Frame) -> None:
        f.push(NULL_OBJ)


class ReturnValue(Instr):
    def execute(self, f: Frame) -> None:
        f.retval = f.pop()
        f.running = False


class ToBool(Instr):
    def execute(self, f: Frame) -> None:
        if f.stack[f.sp - 1].truth():
            f.stack[f.sp - 1] = TRUE
        else:
            f.stack[f.sp - 1] = FALSE


class BinaryOp(Instr):
    def execute(self, f: Frame) -> None:
        rhs = f.pop()
        lhs = f.stack[f.sp - 1]
        f.stack[f.sp - 1] = lhs.binary_op(self.arg, rhs)


class Call(Instr):
    def execute(self, f: Frame) -> None:
        f.push(do_call(f, self.arg))


class CompareOp(Instr):
    def execute(self, f: Frame) -> None:
        rhs = f.pop()
        lhs = f.stack[f.sp - 1]
        if lhs.compare(self.arg, rhs):
            f.stack[f.sp - 1] = TRUE
        else:
            f.stack[f.sp - 1] = FALSE


class Jump(Instr):
    def execute(self, f: Frame) -> None:
        f.pc = self.target


class PopJumpIfFalse(Instr):
    def execute(self, f: Frame) -> None:
        if not f.pop().truth():
            f.pc = self.target


class PopJumpIfTrue(Instr):
    def execute(self, f: Frame) -> None:
        if f.pop().truth():
            f.pc = self.target


class LoadConst(Instr):
    def execute(self, f: Frame) -> None:
        f.push(self.value)


class LoadName(Instr):
    def execute(self, f: Frame) -> None:
        f.push(lookup_name(f, self.name))


class StoreName(Instr):
    def execute(self, f: Frame) -> None:
        f.globals[self.name] = f.pop()


class LoadGlobal(Instr):
    def execute(self, f: Frame) -> None:
        f.push(lookup_name(f, self.name))
        if self.arg2:
            f.push(NULL_OBJ)


class LoadFast(Instr):
    def execute(self, f: Frame) -> None:
        f.push(f.locals[self.arg])


class LoadFastLoadFast(Instr):
    def execute(self, f: Frame) -> None:
        f.push(f.locals[self.arg])
        f.push(f.locals[self.arg2])


class StoreFast(Instr):
    def execute(self, f: Frame) -> None:
        f.locals[self.arg] = f.pop()


class StoreFastStoreFast(Instr):
    def execute(self, f: Frame) -> None:
        f.locals[self.arg] = f.pop()
        f.locals[self.arg2] = f.pop()


class StoreFastLoadFast(Instr):
    def execute(self, f: Frame) -> None:
        f.locals[self.arg] = f.pop()
        f.push(f.locals[self.arg2])


class MakeFunction(Instr):
    def execute(self, f: Frame) -> None:
        f.push(Function(f.pop().as_code(), f.globals))


NO_INSTRS = [Instr(OP_NOP, 0)]
NO_CODE = Code()


def lookup_name(f: Frame, name: str) -> Obj:
    if name in f.globals:
        return f.globals[name]
    if name in BUILTINS:
        return BUILTINS[name]
    raise Exception("NameError: name '" + name + "' is not defined")


def do_call(f: Frame, nargs: int) -> Obj:
    # stack layout (3.13+): callable, self_or_null, arg0 .. argN-1
    base = f.sp - nargs
    args = f.stack[base:f.sp]
    self_or_null = f.stack[base - 1]
    func = f.stack[base - 2]
    f.sp = base - 2
    if self_or_null is not NULL_OBJ:
        args = [self_or_null] + args
    return func.call(args)


BUILTINS = {'print': PrintFn()}


# ---------------------------------------------------------------------------
# decoding: bytes -> list of Instr, with jump targets resolved

def make_instr(code: Code, op: int, arg: int) -> Instr:
    if op == OP_LOAD_NAME:
        ins = LoadName(op, arg)
        ins.name = code.names[arg]
        return ins
    elif op == OP_STORE_NAME or op == OP_STORE_GLOBAL:
        ins = StoreName(op, arg)
        ins.name = code.names[arg]
        return ins
    elif op == OP_LOAD_GLOBAL:
        ins = LoadGlobal(op, arg)
        ins.name = code.names[arg >> 1]
        ins.arg2 = arg & 1     # low bit: also push NULL (call setup)
        return ins
    elif op == OP_LOAD_FAST or op == OP_LOAD_FAST_BORROW or op == OP_LOAD_FAST_CHECK:
        return LoadFast(op, arg)
    elif op == OP_LOAD_FAST_LOAD_FAST or op == OP_LOAD_FAST_BORROW_LOAD_FAST_BORROW:
        ins = LoadFastLoadFast(op, arg)
        ins.arg = arg >> 4
        ins.arg2 = arg & 15
        return ins
    elif op == OP_STORE_FAST:
        return StoreFast(op, arg)
    elif op == OP_STORE_FAST_STORE_FAST:
        ins = StoreFastStoreFast(op, arg)
        ins.arg = arg >> 4
        ins.arg2 = arg & 15
        return ins
    elif op == OP_STORE_FAST_LOAD_FAST:
        ins = StoreFastLoadFast(op, arg)
        ins.arg = arg >> 4
        ins.arg2 = arg & 15
        return ins
    elif op == OP_MAKE_FUNCTION:
        return MakeFunction(op, arg)
    elif op == OP_LOAD_CONST:
        ins = LoadConst(op, arg)
        ins.value = code.consts[arg]
        return ins
    elif op == OP_LOAD_SMALL_INT:
        ins = LoadConst(op, arg)
        ins.value = SMALL_INTS[arg]
        return ins
    elif op == OP_BINARY_OP:
        ins = BinaryOp(op, arg)
        if arg >= NB_INPLACE_OFFSET:
            ins.arg = arg - NB_INPLACE_OFFSET   # x += y is x + y for our immutable ints/strs
        return ins
    elif op == OP_COMPARE_OP:
        ins = CompareOp(op, arg)
        ins.arg = arg >> 5   # low bits: coerce-to-bool flag, always true for us
        return ins
    elif op == OP_CALL:
        return Call(op, arg)
    elif op == OP_POP_TOP:
        return PopTop(op, arg)
    elif op == OP_PUSH_NULL:
        return PushNull(op, arg)
    elif op == OP_RETURN_VALUE:
        return ReturnValue(op, arg)
    elif op == OP_TO_BOOL:
        return ToBool(op, arg)
    elif op == OP_POP_JUMP_IF_FALSE:
        return PopJumpIfFalse(op, arg)
    elif op == OP_POP_JUMP_IF_TRUE:
        return PopJumpIfTrue(op, arg)
    elif op == OP_JUMP_FORWARD or op == OP_JUMP_BACKWARD:
        return Jump(op, arg)
    elif op == OP_RESUME or op == OP_NOP or op == OP_NOT_TAKEN:
        return Nop(op, arg)
    raise Exception('decode: unsupported opcode %d (%s)' % (op, OPNAME.get(op, '?')))


def decode(code: Code):
    """Decode co_code into Instr objects. CACHE entries are dropped; jump
    arguments (in code units, relative to the unit after the jump's caches)
    are converted to instruction-list indices."""
    co = code.co_code
    nunits = len(co) // 2
    unit_to_index = [0] * (nunits + 1)
    instrs = [NO_INSTRS[0]] * nunits   # upper bound; trimmed below
    n = 0
    unit = 0
    ext = 0
    while unit < nunits:
        op = co[2 * unit]
        arg = co[2 * unit + 1] | ext
        ext = 0
        unit_to_index[unit] = n
        if op == OP_CACHE:
            unit += 1
            continue
        if op == OP_EXTENDED_ARG:
            ext = arg << 8
            unit += 1
            continue
        ins = make_instr(code, op, arg)
        ncache = INLINE_CACHE.get(op, 0)
        next_unit = unit + 1 + ncache
        for u in range(unit + 1, next_unit):
            unit_to_index[u] = n
        if op == OP_JUMP_FORWARD or op == OP_POP_JUMP_IF_FALSE or op == OP_POP_JUMP_IF_TRUE:
            ins.target = next_unit + arg
        elif op == OP_JUMP_BACKWARD:
            ins.target = next_unit - arg
        instrs[n] = ins
        n += 1
        unit = next_unit
    unit_to_index[nunits] = n
    instrs = instrs[:n]
    for ins in instrs:
        if ins.op == OP_JUMP_FORWARD or ins.op == OP_JUMP_BACKWARD or ins.op == OP_POP_JUMP_IF_FALSE or ins.op == OP_POP_JUMP_IF_TRUE:
            ins.target = unit_to_index[ins.target]
    code.instrs = instrs
    for c in code.consts:
        if c.is_code():
            decode(c.as_code())
    return instrs


def disassemble(code: Code) -> None:
    for c in code.consts:
        if c.is_code():
            disassemble(c.as_code())
    print(code.str_() + ' (%d instructions):' % len(code.instrs))
    for i, ins in enumerate(code.instrs):
        extra = ''
        if ins.op == OP_LOAD_CONST or ins.op == OP_LOAD_SMALL_INT:
            extra = '(' + ins.value.repr_() + ')'
        elif ins.op == OP_LOAD_NAME or ins.op == OP_STORE_NAME or ins.op == OP_LOAD_GLOBAL or ins.op == OP_STORE_GLOBAL:
            extra = '(' + ins.name + ')'
        elif ins.op == OP_LOAD_FAST or ins.op == OP_LOAD_FAST_BORROW or ins.op == OP_LOAD_FAST_CHECK or ins.op == OP_STORE_FAST:
            extra = '(' + code.localsplusnames[ins.arg] + ')'
        elif ins.op == OP_LOAD_FAST_LOAD_FAST or ins.op == OP_LOAD_FAST_BORROW_LOAD_FAST_BORROW or ins.op == OP_STORE_FAST_STORE_FAST or ins.op == OP_STORE_FAST_LOAD_FAST:
            extra = '(' + code.localsplusnames[ins.arg] + ', ' + code.localsplusnames[ins.arg2] + ')'
        elif ins.op == OP_JUMP_FORWARD or ins.op == OP_JUMP_BACKWARD or ins.op == OP_POP_JUMP_IF_FALSE or ins.op == OP_POP_JUMP_IF_TRUE:
            extra = '(to %d)' % ins.target
        print('%4d  %s %s' % (i, repr(ins), extra))
    print()


# ---------------------------------------------------------------------------
# the two dispatch loops

VIRTUAL = [True]   # dispatch mode, shared by nested calls


def run_frame(f: Frame) -> Obj:
    if VIRTUAL[0]:
        return run_virtual(f)
    return run_ifelse(f)


def run_virtual(f: Frame) -> Obj:
    instrs = f.code.instrs
    while f.running:
        ins = instrs[f.pc]
        f.pc += 1
        ins.execute(f)
    return f.retval


def run_ifelse(f: Frame) -> Obj:
    instrs = f.code.instrs
    stack = f.stack
    locals_ = f.locals
    while f.running:
        ins = instrs[f.pc]
        f.pc += 1
        op = ins.op
        if op == OP_LOAD_NAME:
            stack[f.sp] = lookup_name(f, ins.name)
            f.sp += 1
        elif op == OP_LOAD_CONST or op == OP_LOAD_SMALL_INT:
            stack[f.sp] = ins.value
            f.sp += 1
        elif op == OP_STORE_NAME or op == OP_STORE_GLOBAL:
            f.sp -= 1
            f.globals[ins.name] = stack[f.sp]
        elif op == OP_LOAD_FAST or op == OP_LOAD_FAST_BORROW or op == OP_LOAD_FAST_CHECK:
            stack[f.sp] = locals_[ins.arg]
            f.sp += 1
        elif op == OP_LOAD_FAST_LOAD_FAST or op == OP_LOAD_FAST_BORROW_LOAD_FAST_BORROW:
            stack[f.sp] = locals_[ins.arg]
            stack[f.sp + 1] = locals_[ins.arg2]
            f.sp += 2
        elif op == OP_STORE_FAST:
            f.sp -= 1
            locals_[ins.arg] = stack[f.sp]
        elif op == OP_STORE_FAST_STORE_FAST:
            locals_[ins.arg] = stack[f.sp - 1]
            locals_[ins.arg2] = stack[f.sp - 2]
            f.sp -= 2
        elif op == OP_STORE_FAST_LOAD_FAST:
            locals_[ins.arg] = stack[f.sp - 1]
            stack[f.sp - 1] = locals_[ins.arg2]
        elif op == OP_LOAD_GLOBAL:
            stack[f.sp] = lookup_name(f, ins.name)
            f.sp += 1
            if ins.arg2:
                stack[f.sp] = NULL_OBJ
                f.sp += 1
        elif op == OP_MAKE_FUNCTION:
            stack[f.sp - 1] = Function(stack[f.sp - 1].as_code(), f.globals)
        elif op == OP_BINARY_OP:
            f.sp -= 1
            rhs = stack[f.sp]
            stack[f.sp - 1] = stack[f.sp - 1].binary_op(ins.arg, rhs)
        elif op == OP_COMPARE_OP:
            f.sp -= 1
            rhs = stack[f.sp]
            if stack[f.sp - 1].compare(ins.arg, rhs):
                stack[f.sp - 1] = TRUE
            else:
                stack[f.sp - 1] = FALSE
        elif op == OP_POP_JUMP_IF_FALSE:
            f.sp -= 1
            if not stack[f.sp].truth():
                f.pc = ins.target
        elif op == OP_POP_JUMP_IF_TRUE:
            f.sp -= 1
            if stack[f.sp].truth():
                f.pc = ins.target
        elif op == OP_JUMP_BACKWARD or op == OP_JUMP_FORWARD:
            f.pc = ins.target
        elif op == OP_NOT_TAKEN or op == OP_NOP or op == OP_RESUME:
            pass
        elif op == OP_POP_TOP:
            f.sp -= 1
        elif op == OP_PUSH_NULL:
            stack[f.sp] = NULL_OBJ
            f.sp += 1
        elif op == OP_CALL:
            stack[f.sp] = do_call(f, ins.arg)
            f.sp += 1
        elif op == OP_TO_BOOL:
            if stack[f.sp - 1].truth():
                stack[f.sp - 1] = TRUE
            else:
                stack[f.sp - 1] = FALSE
        elif op == OP_RETURN_VALUE:
            f.sp -= 1
            f.retval = stack[f.sp]
            f.running = False
        else:
            raise Exception('unsupported opcode %d' % op)
    return f.retval


def run_file(path: str, virtual: bool, show: bool):
    """Load, decode and run a .pyc; returns the module globals afterwards."""
    code = load_pyc(path)
    decode(code)
    if show:
        disassemble(code)
    globals_ = {'__name__': Str('__main__')}
    VIRTUAL[0] = virtual
    run_frame(Frame(code, globals_))
    return globals_


def self_test(virtual: bool) -> None:
    """Run the bundled testdata and check results against CPython's answers."""
    mode = 'ifelse'
    if virtual:
        mode = 'virtual'
    print('--- %s: testdata/hello.pyc' % mode)
    run_file('testdata/hello.pyc', virtual, virtual)

    print('--- %s: testdata/loop.pyc' % mode)
    g = run_file('testdata/loop.pyc', virtual, False)
    assert g['total'].as_int() == 89999700000
    assert g['i'].as_int() == 300000

    print('--- %s: testdata/funcs.pyc' % mode)
    g = run_file('testdata/funcs.pyc', virtual, False)
    assert g['fib'].call([Int(20)]).as_int() == 6765
    assert g['fib'].call([Int(1)]).as_int() == 1
    assert g['loop'].call([Int(10)]).as_int() == 90
    assert g['greet'].call([Str('x'), Int(2)]).as_str() == 'hello x! hello x! '
    assert g['greet'].call([Str('x'), Int(0)]).as_str() == ''
    assert g['__name__'].as_str() == '__main__'


def main() -> None:
    args = sys.argv[1:]
    virtual = True
    show = False
    files = []
    for a in args:
        if a == '--virtual':
            virtual = True
        elif a == '--ifelse':
            virtual = False
        elif a == '--dis':
            show = True
        else:
            files.append(a)
    if len(files) == 0:
        self_test(True)
        self_test(False)
        print('ok')
    else:
        for path in files:
            run_file(path, virtual, show)


if __name__ == '__main__':
    main()
