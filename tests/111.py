
a = (1,2)                                # [tuple(int)]
b = (1,2,3)                              # [tuple(int)]

c = a                                    # [tuple(int)]
c = b                                    # [tuple(int)]

d = a+b                                  # [tuple(int)]
print d                                  # [tuple(int)]

def bla(x):                              # x: [A]
    pass

bla(a)                                   # []
bla(b)                                   # []
bla([1,2,3])                               # []

dc = {}                                  # [dict(tuple(int), int)]
dc[a] = 2                                # [int]
dc[b] = 3                                # [int]

print a, dc[a], b, dc[b]                 # [tuple(int)], [int], [tuple(int)], [int]

