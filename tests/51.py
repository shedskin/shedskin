
import testdata.bert

class zeug:
    def meuk(self):                      # self: [zeug()]
        return '2'                       # [str]

def hoi(): return 1                    # [float]


print hoi()                              # [float]
a = zeug()                               # [zeug()]

print testdata.bert.hello(1)                      # [str]
z = testdata.bert.zeug()                          # [bert::zeug()]
z.hallo(1)                               # [int]

print a.meuk()                           # [str]

l1 = lambda x,y: x+y                     # [lambda0]
print l1(1,2)                            # [int]

