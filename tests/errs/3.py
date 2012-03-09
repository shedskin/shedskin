import camera

def hap(x):
    print x

def hap2():
    pass

hoplist = [hap2]
hoplist = [hop2]

class A(object):
    pass

class B(object):
    pass

s = A()
s = B()
print s

#*WARNING* camera.py:6: function runpix not called!
#*WARNING* 3.py:3: function hap not called!
#*WARNING* 3.py:9: 'list' instance containing function reference
#*WARNING* 3.py:10: variable 'hop2' has no type
#*WARNING* 3.py: variable 's' has dynamic (sub)type: {A, B}
#*WARNING* 3.py:20: expression has dynamic (sub)type: {A, B}

