
def cond1(n):
    res = '%s : ' % n
    if (n >= 0):
            res += 'positive '
            if n % 2 == 0:
                res += 'divisible by 2 '
            elif n % 3 == 0:
                res += 'divisible by 3 '

            elif n % 5 == 0:
                res += 'divisible by 5 '
            else:
                res += 'funny '
    else:
        # negative
        res += 'negative '
    return res + 'number'

def test_if_elif_else():
    assert cond1(27) == '27 : positive divisible by 3 number'


def test_if_else_expr():
    assert 8 + (2 if 1 else 3) == 10
    assert 8 + (2 if 0 else 3) == 11

def test_all():
    test_if_else_expr()
    test_if_elif_else()

if __name__ == '__main__':
    test_all() 
