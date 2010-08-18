
class bla:                               # xx: [float, int]*
    pass

a = bla()                                # [bla(int)]
a.xx = 1                                 # [int]

b = bla()                                # [bla(float)]
b.xx = 1.0                               # [float]

def joink(d):                            # d: [bla(A)]
    c = bla()                            # [bla(A)]
    c.xx = d.xx                          # [A]
    return c                             # [bla(A)]

e = joink(a)                                 # [bla(int)]
f = joink(b)                                 # [bla(float)]

