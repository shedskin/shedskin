
def bla(x):                              # x: [A]*
    a = []                               # [list(A)]
    return a                             # [list(A)]
    return [x]                           # [list(A)]


a = bla(1)                               # [list(int)]
b = bla(1.1)                             # [list(float)]


d = []                                   # [list(str)]
c = d                                    # [list(str)]
c = ['1']                                # [list(str)]

if d == []:                              # [int]
    print 'yo'                           # [str]
if c == []:
    print 'no'

