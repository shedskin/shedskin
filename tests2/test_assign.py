
def test_assign_int():
    a = 1
    assert a == 1

def test_assign_list():
    a = [1]
    assert a == [1]


def test_all():
    test_assign_int()
    test_assign_list()


if __name__ == '__main__':
    test_all()
