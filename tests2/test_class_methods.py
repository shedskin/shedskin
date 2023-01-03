class Dict:

    def __init__(self, name):
        self.name = name
        self.kwds = {}
    
    def __str__(self):
        return "<Dict '%s'>" % self.name
    
    def __setitem__(self, name, value):
        self.kwds[name] = value
    
    def __getitem__(self, name):
        if name in self.kwds:
            return self.kwds[name]
    
    def __delitem__(self, name):
        if name in self.kwds:
            del self.kwds[name]
    
    def __len__(self):
        return len(self.kwds)
    
    def __contains__(self, name):
        return name in self.kwds
    

def test_dictlike():
    obj = Dict('foo')
    obj['a1'] = 'b1'
    obj['a2'] = 'b2'
    obj['a3'] = 'b3'

    assert obj.name == 'foo'
    assert len(obj) == 3
    assert str(obj) == "<Dict 'foo'>"
    assert 'a1' in obj
    assert 'a2' in obj
    assert 'a3' in obj
    assert obj['a1'] == 'b1'
    assert obj['a2'] == 'b2'
    assert obj['a3'] == 'b3'
    del obj['a3']
    assert 'a3' not in obj
    assert len(obj) == 2




class C:
    def __abs__(self):
        return self

    def __neg__(self):
        return self

    def __repr__(self):
        return "C"

def test_numlike1():

    abs(C()) == C
    abs(23) == 23
    abs(-1.3) == 1.3
    -abs(C()) == C


class D:
    def __int__(self):
        return 7

    def __float__(self):
        return 7.0

    def __str__(self):
        return "__str__"

    def __repr__(self):
        return "__repr__"

    def __nonzero__(self):
        return True

    def __len__(self):
        return 1


def test_numlike2():

    d = D()
    assert bool(d)
    assert str(d) == '__str__'
    assert int(d) == 7
    assert float(d) == 7.0


class E:
    def __init__(self, value):
        self.value = value

    def __iadd__(self, other):
        self.value += other.value
        return self

    def __floordiv__(self, b):
        return E(self.value // b.value)

    def __ifloordiv__(self, b):
        self.value //= b.value
        return self

    def __str__(self):
        return str(self.value)

def test_numlike3():

    x = E(4)
    x += x
    x.__iadd__(x)
    assert str(x) == '16'

    assert [1, 2].__iadd__([2, 3]) == [1, 2, 2, 3]

    y = [1, 2, 3]
    y += set([4, 5])
    assert y == [1, 2, 3, 4, 5]

    v = 3
    v += 1.5
    assert v == 4.5

    hm = []
    hm += set([1])
    assert hm == [1]

    e = E(8)
    assert str(e // E(3)) == '2'

    e //= E(3)
    assert str(e) == '2'


class Num:
    def __init__(self, v):
        self.value = v

    def __str__(self):
        return str(self.value)

    def __bytes__(self):
        return bytes(self.value)

    def __truediv__(self, other):
        return Num(self.value / other.value)

    def __floordiv__(self, other):
        return Num(self.value // other.value)

def test_numlike4():
    a = Num(10)
    b = Num(2)

    assert str(a) == '10'
    assert bytes(a) == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    # assert str(a / b) == '5.0'
    # assert str(a // b) == '5'
    
    # a /= b
    # assert str(a) == '5.0'

    # a //= b
    # assert str(a) == '2.0'



class Function:
    def __call__(self, x, y):
        return x+y

def test_funclike():
    f = Function()
    assert f(1,2) == 3


class Range:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def __iter__(self):
         current = self.start
         while current < self.stop:
             yield current
             current += 1


def test_iterable():
    assert list(Range(0, 10)) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]



class String:
    def __init__(self, string):
        self.str = string

    def __add__(self, other):
        return String(self.str + other.str)

    def __repr__(self):
        return "<String '%s'>" % self.str

    def __str__(self):
        return self.str

    def __len__(self):
        return len(self.str)

    def __bytes__(self):
        return self.str.encode('utf8')

    def __contains__(self, substring):
        return substring in self.str

    def __eq__(self, other):
        return self.str == other.str

    def __lt__(self, other):
        return self.str < other.str

    def __le__(self, other):
        return self.str <= other.str

    def __ne__(self, other):
        return self.str != other.str

    def __gt__(self, other):
        return self.str > other.str

    def __ge__(self, other):
        return self.str >= other.str


def test_stringlike():
    s1 = String("Hello")
    assert (s1 + String(" Folks")) == String("Hello Folks")



class Set:
    def __init__(self, value):
        self.value = value

    def __iand__(self, b):
        return Set(self.value + b.value)

    def __isub__(self, b):
        return Set(self.value - b.value)

def test_setlike():
    wa = Set(4)
    wa &= Set(9)
    wa -= Set(2)
    assert wa.value == 11



def test_class_name():
    assert [].__class__.__name__ == 'list'
    assert set().__class__.__name__ == 'set'
    # etc..






def test_all():
    test_dictlike()
    test_numlike1()
    test_numlike2()
    test_numlike3()
    test_numlike4()
    test_funclike()
    test_iterable()
    test_stringlike()
    test_setlike()
    test_class_name()

if __name__ == '__main__':
    test_all()


