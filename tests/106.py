
def escapement():
    a = vars1()                          # [list(int)]
    return a                             # [list(int)]

def vars1():
    return [1,2]                         # [list(int)]

x = escapement()                         # [list(int)]
y = escapement()                         # [list(int)]
y.append(3)                              # []
print x                                  # [list(int)]


def escapement2():
    bla(vars3())                         # []

def bla(x):                              # x: [list(int)]*
    global bye
    bye = x                              # [list(int)]

def vars3():
    return [1]                           # [list(int)]

def joink():
    x = vars3()                          # [list(int)]

escapement2()                            # []
bye.append(2)                            # []
joink()                                  # []
print bye                                # [list(int)]


def transitive():
    a = vars2()                          # [list(int)]
    hoi()                                # []
    print a                              # [list(int)]

def vars2():
    return [1,2]                         # [list(int)]

def hoi():
    a = vars2()                          # [list(int)]
    a.append(3)                          # []

transitive()                             # []

