
def test_basic_fstring():
    name = 'bert'
    half_age = 24
    s = f'{name} is {half_age*2} years old'
    assert s == 'bert is 48 years old'


def test_all():
    test_basic_fstring()


if __name__ == '__main__':
    test_all()

