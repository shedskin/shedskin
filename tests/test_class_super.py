

class A:
    def __init__(self, x):
        self.x = x


class B(A):
    def __init__(self, x, y):
        # super().__init__(x) ## this form is not supported
        super(B, self).__init__(x)
        self.y = y



class C(B):
    def __init__(self, x, y, z):
        # super().__init__(x, y) ## this form is not supported
        super(C, self).__init__(x, y)
        self.z = z

def test_super():
    c = C('a', 'b', 'c')
    assert c.x == 'a'
    assert c.y == 'b'
    assert c.z == 'c'


class A1:
    def __init__(self, x):
        self.x = x


class B1(A1):
    def __init__(self, x, y):
        A1.__init__(self, x)
        self.y = y

class C1(B1):
    def __init__(self, x, y, z):
        B1.__init__(self, x, y)
        self.z = z


def test_init():
    c = C1('a', 'b', 'c')
    assert c.x == 'a'
    assert c.y == 'b'
    assert c.z == 'c'



def test_all():
    test_super()
    test_init()




if __name__ == '__main__':
    test_all() 

