#new casting/conversion approach
digit_dict = {
              "1":{1:(1,2,3,4,5),2:(1,3,5)  ,3:()}
              ,"2":{1:(2,)           ,2:()          ,3:(4,)}
              ,"3":{1:(2,4)         ,2:()          ,3:()}
              ,"4":{1:(4,5)         ,2:(1,5)     ,3:()}
              ,"5":{1:(4,)           ,2:()          ,3:(2,)}
              ,"6":{1:()              ,2:()          ,3:(2,)}
              ,"7":{1:(2,3,4,5)  ,2:(3,5)     ,3:()}
              ,"8":{1:()              ,2:()          ,3:()}
              ,"9":{1:(4,)           ,2:()          ,3:()}
              ,"0":{1:()              ,2:(3,)       ,3:()}
}
for d in sorted(digit_dict):
    d2 = digit_dict[d]
    for e in sorted(d2):
        print d, e, d2[e]

l = [[7,8,9], [7.7,8.8,9.9]]
    
for ll in l:
    for lll in ll:
        print '%.2f' % lll

#circular includes
from testdata import bert
class Here:
    def __str__(self):
        return 'here'
bert.hello(Here())

#partial support for 'super'
class A(object):
    def __init__(self, x):
        print 'a', x
class C(A):
    def __init__(self, x):
        print 'c', x
class B(C):
    def __init__(self, x):
        super(B, self).__init__(x)
        super(C, self).__init__(3*x)
        A.__init__(self, 2*x)
        C.__init__(self, 3*x)
        print 'b', x
B(7)

#update with genexpr
_hextochr = dict(('%02x' % i, chr(i)) for i in range(256))
_hextochr.update(('%02X' % i, chr(i)) for i in range(256))
print(repr(_hextochr))

#C++ looks in classs namespace first
kwek = 18
class Test1(object) :
    def __init__(self, lenin) :
        self.len = lenin
        self.buf = "x" * lenin  
        self.kwek = 17
       
    def getlen(self) :
        print kwek
        return(len(self.buf))
       
f = Test1(100)
n = f.getlen()
print(n)

# IOError.{errno, strerror}
try :
    print("Try block")
    fd = open("nosuchfile") # open will fail
    print("File opened")
except IOError as e:
    print e, repr(e)
    print e.errno, e.strerror
