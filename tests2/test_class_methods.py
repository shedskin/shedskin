class DictLike:

    def __init__(self, name):
        self.name = name
        self.kwds = {}
    
    def __str__(self):
        return "<DictLike '%s'>" % self.name
    
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
    obj = DictLike('foo')
    obj['a1'] = 'b1'
    obj['a2'] = 'b2'
    obj['a3'] = 'b3'

    assert obj.name == 'foo'
    assert len(obj) == 3
    assert str(obj) == "<DictLike 'foo'>"
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


def test_all():
    test_dictlike()
    test_numlike1()
    test_numlike2()

if __name__ == '__main__':
    test_all()


