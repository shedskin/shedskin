
def hello(x):
    return 'rootbert'

def def1(a=-14):
    return a

a = 15
def def2(a=a):
    return a

def huh():
    return a

a = 17
def def3(a=2*a):
    return a

b = None
def def4(a=b):
    pass

def1()
def2()
def3()
huh()
def4([1])
