
t = (1,2,3)                              # [tuple(int)]
v = (1,)                                 # [tuple(int)]
w = (1,2,3)                              # [tuple(int)]

e = {}                                   # [dict(tuple(int), int)]
e[t] = 1                                 # [int]
e[v] = 2                                 # [int]
e[w] = 3                                 # [int]

print e[t], e[v], e[w]                   # [int], [int], [int]


