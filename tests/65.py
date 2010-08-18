
def ident(x):
    return x

b = []
a = []
ident(b).append(1.0)
ident(a).append(1)

def hoppa(y):
    k = []
    k.append(1.0)
    l = []
    l.append(y[0])
    return l

c = hoppa(a)
d = hoppa(b)

