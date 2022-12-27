class Object:

    def __init__(self, name):
        self.name = name
        self.kwds = {}
    
    def __str__(self):
        return "<Object '%s'>" % self.name
    
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
    

def test_object():
    obj = Object('foo')
    obj['a1'] = 'b1'
    obj['a2'] = 'b2'
    obj['a3'] = 'b3'

    assert obj.name == 'foo'
    assert len(obj) == 3
    assert str(obj) == "<Object 'foo'>"
    assert 'a1' in obj
    assert 'a2' in obj
    assert 'a3' in obj
    assert obj['a1'] == 'b1'
    assert obj['a2'] == 'b2'
    assert obj['a3'] == 'b3'
    del obj['a3']
    assert 'a3' not in obj
    assert len(obj) == 2

def test_all():
    test_object()

if __name__ == '__main__':
    test_all()


