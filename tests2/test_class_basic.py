class Person:
    a = 1
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Person: '%s'>" % self.name

    def speak(self, x):
        return x

    def huh(self):
        self.b = 1

    def goodbye(self, x):
        b = 4
        return b



def test_person():
    f = Person('fred')
    assert f.a == 1

    g = f.speak('goedzo?')
    assert g == 'goedzo?'

    f.huh()
    assert f.b == f.a

    f.hallo = 1
    assert f.hallo == f.a

    f2 = Person('fred')
    f2.c = 'hello'
    assert f2.c == 'hello'

    f3 = Person('fred')
    assert f3.goodbye('jo') == 4

    y = None
    y = Person('bert')
    assert y.name == 'bert'

def test_all():
    test_person()

if __name__ == '__main__':
    test_all()
