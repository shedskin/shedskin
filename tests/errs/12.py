f = file('meuh', 'w')
del f

class A:
   pass
a = A()
a.b = 'woef'
del a.b

azo = 1
azo = lambda x: -x

def blah(b):
    pass

blah(1)
blah(blah)

#def hoep(a,b):
#    pass
#
#if False:
#    hoep(1)
#*WARNING* 12.py:2: 'del' has no effect without refcounting
#*WARNING* 12.py:8: 'del' has no effect without refcounting
#*WARNING* 12.py: Variable 'azo' has dynamic (sub)type
#*WARNING* 12.py: Variable (Function blah, 'b') has dynamic (sub)type
