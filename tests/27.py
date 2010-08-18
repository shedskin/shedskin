
class pears:                           # type: [str]*, amount: [int, float]*, music: [str]*, unit: [int, float, str]*
    def __init__(self, amount, hype):    # self: [pears(float,str), pears(int,int), pears(int,float)], type: [str]*, amount: [int, float]*
        self.amount = amount             # [int, float]
        self.hype = hype                 # [str]

    def shakeit(self, times):          # self: [pears(int,float)], times: [int]
        pass

    def setunit(self, unit):             # self: [pears(float,str), pears(int,int), pears(int,float)], unit: [int, float, str]*
        self.unit = unit                 # [int, float, str]

    def __repr__(self):                  # self: [pears(int,float)]
        return self.hype                 # [str]

#print 'pears simulator'

p = pears(2, 'it')                   # [pears(int,float)]
p.setunit(1.0)                           # []
q = pears(2, 'it')                   # [pears(int,int)]
q.setunit(1)                             # []
r = pears(2.0, 'it')                 # [pears(float,str)]
r.setunit('ha')                          # []

p.shakeit(7)                           # []
p.music = 'cool'                         # [str]

m = [1,2,3,4]                            # [list(int)]

lp = [q,q]                               # [list(pears(int,int))]
print p, m, lp                           # [str], [str], [str]

