
class father(object):
    def __init__(self,a):
        self.a=a
        b=1
    def f(self,x):
            return x*self.a

class son(father):
    def g(self,x):
        return x*self.a*self.a

myfather=father(3)
print myfather.f(4)
myson=son(4)
print myson.g(5)

class mother(object):
    def __init__(self,a):
        self.a=a
        b=1
    def f(self,x):
            return x*self.a

class daughter(mother):
    def g(self,x):
        return x*self.a*self.a

mydaughter = daughter(4)
print mydaughter.g(5)


