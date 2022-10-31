# 'if isinstance' guiding type inference experiment

class C:
    pass

class A(C):
    def woof(self):
       print('woof!')

class B(C):
    def meow(self):
       print('meow!')

def somefunc(x):
    if isinstance(x, A):
        x.woof()
    elif isinstance(x, B):
        x.meow()

somefunc(A())
somefunc(B())
x = A()
x = B()
somefunc(x)
