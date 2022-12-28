import pickle


class Foo:
    def __init__(self, a, b):
        self.a = a
        self.b = b



def test_pickle():
    foo = Foo(7, 'eight')
    s = pickle.dumps(foo)
    obj = pickle.loads(s)
    assert obj.a == 7
    assert obj.b == 'eight'

def test_all():
    test_pickle()


if __name__ == '__main__':
    test_all()
