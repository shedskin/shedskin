class Integer:
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return '<Integer: %s>' % self.x

    def __gt__(self, other):
        return self.x > other.x

    def __gte__(self, other):
        return self.x >= other.x
    
    def __lt__(self, other):
        return self.x < other.x
    
    def __lte__(self, other):
        return self.x <= other.x
    

def maxi(a, b):
    if a > b:
        return a
    return b


def test_int_class():
    a = Integer(10)
    b = Integer(12)
    assert maxi(a, b) == b


def test_all():
    test_int_class()


if __name__ == '__main__':
    test_all()
