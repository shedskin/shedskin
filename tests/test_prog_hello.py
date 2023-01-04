def hello(x):
    return 'hello %s!' % x

def test_hello():
    assert hello('world') == 'hello world!'

def test_all():
    test_hello()

if __name__ == '__main__':
    test_all() 

