
print 'hello, world!'                    # [str]

l = 'luis gonzales'                      # [str]
print l[3:7]                             # [str]
print l[1::2]                            # [str]

t = (1,2,3,4,5)                          # [tuple(int)]
print t[1:4]                             # [tuple(int)]

s = 'we are testing shedskin on windows' # [str]

d = {}                                   # [dict(str, int)]

for i in s:                              # [str]
    if not i in d:                       # []
        d[i]= 1                          # [int]
    else:
        d[i]= d[i] + 1                   # [int]

for k,v in d.items():                    # [tuple(str, int)]
    if k == ' ':
        print k, ':', v                      # [str], [str], [int]

x=[]                                     # [list(dude)]

class dude:                              # age: [int], last: [str], name: [str]
    def __init__(self, name, last , age): # self: [dude], name: [str]*, last: [str]*, age: [int]*
        self.name = name                 # [str]
        self.last = last                 # [str]
        self.age = age                   # [int]
        x.append(self)                   # []
    def __repr__(self):                  # self: [dude]
        return '%s %s is %s years old' %(self.name, self.last, str(self.age)) # [str]

dude('luis','gonzalez',35)               # [dude]
print x[0]                               # [dude]

