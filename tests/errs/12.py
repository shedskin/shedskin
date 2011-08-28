f = file('meuh', 'w')
del f

class A:
   pass
a = A()
a.b = 'woef'
del a.b

#*WARNING* 12.py:2: variable won't be deleted
#*WARNING* 12.py:8: attribute won't be deleted
