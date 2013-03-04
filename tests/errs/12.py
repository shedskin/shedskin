f = file('meuh', 'w')
del f

class A:
   pass
a = A()
a.b = 'woef'
del a.b

#*WARNING* 12.py:2: 'del' has no effect without refcounting
#*WARNING* 12.py:8: 'del' has no effect without refcounting
