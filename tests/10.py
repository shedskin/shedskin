
class fred:                              # hallo: [int]
   pass

a = fred()                               # [fred_int]
a.hallo = 1                              # [int]
b = a.hallo                              # [int]

c = fred()                               # [fred_str]
c.a = 'god'                              # [str]
d = c.a                                  # [str]

