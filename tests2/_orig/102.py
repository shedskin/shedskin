
a = (1,2)                                # [tuple2(int, int)]
a in [(1,2),(3,4)]                       # [int]
(1,2) in [(1,2),(3,4)]                   # [int]

a == (2,3)                               # []
(1,2) == a                               # []

b = [1]                                  # [list(int)]
b == []                                  # [int]
[] == b                                  # [list(int)]
b == [1]                                 # [int]
1 in b                                   # [int]
1 in [1]                                 # [int]
[1] == [1]                               # [int]

#b == 'hoi'                               # [int]
#'hoi' == b                               # [int]
'hoi' == 'hoi'                           # [int]

for c in [(2,3),(3,4)]:                  # [tuple2(int, int)]
    if c == (2,3):                       # []
        pass

[v for v in [(1,),(2,),(3,)] if v != (1,)] # [list(tuple(int))]

e = 1
a in [(1,e)]                             # [int]

