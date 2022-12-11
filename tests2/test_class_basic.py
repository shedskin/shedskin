class Fred:
    a = 1
    def speak(self, x):
        return x

    def huh(self):
        self.b = 1

    def hottum(self, x):
        b = 4
        return b

def hottum():
    pass


def test_fred():
    f = Fred()
    assert f.a == 1

    c = f.speak('goedzo?')
    assert c == 'goedzo?'

    f.huh()
    assert f.b == f.a

    f.hallo = 1
    assert f.hallo == f.a

    f2 = Fred()
    f2.c = 'hello'
    assert f2.c == 'hello'

    h = Fred()
    assert h.hottum('jo') == 4


if __name__ == '__main__':
    test_fred()
