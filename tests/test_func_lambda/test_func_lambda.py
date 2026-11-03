
def foo(l):
    return l(1, 2)

def f1(x,y):
    return x+y

def f2(x,y):
    return x-y

def f3(x,y):
    return 1.0

def f4(x,y):
    return f1(x,y)

def test_funcs():
    assert f1(10,2) == 12
    assert f2(10,2) == 8
    assert f3(10,2) == 1.0
    assert f4(10,2) == 12  ## only an issue with lambdas!


def test_lambdas():
    l1 = lambda x, y: x + y

    l2 = lambda x, y: x - y
    
    l3 = lambda x, y: 1.0
    
    # l4 = lambda x, y: l1(x,y) ## FIXME: uncomment to cause a strange error with l3!

    assert l1(10,2) == 12
    assert l2(10,2) == 8
    assert l3(10,2) == 1.0

    # assert l4(10,2) == 12

LAMBDA_N = 10

def lambda_default_global():
    g = lambda q=LAMBDA_N + 1, r=len('xyz'): q * 100 + r
    return g()

def apply0(fn):
    return fn()

def test_lambda_defaults():
    # non-constant defaults are evaluated where the lambda is created
    f = lambda q=len('ab'): q
    assert f() == 2
    assert f(5) == 5
    global LAMBDA_N
    LAMBDA_N = 20
    assert lambda_default_global() == 2103
    LAMBDA_N = 30
    assert lambda_default_global() == 3103
    assert apply0(lambda s=str(LAMBDA_N) + '!': s) == '30!'

def test_all():
    test_funcs()
    test_lambdas()
    test_lambda_defaults()


if __name__ == '__main__':
    test_all() 
