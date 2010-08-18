
print [1,2] == [1,2]                     # [int]
print [(1,2),(2,3)] == [(1,2),(2,3)]     # [int]
print [(1,4),(2,3)] == [(1,2),(2,3)]     # [int]

print 1 in (1,2,3)                       # [int]
print 1 in (1,2)                         # [int]
print 3 in (1,2)                         # [int]

print (1,2) in [(1,2),(2,3)]             # [int]
print (1,4) in [(1,2),(2,3)]             # [int]

print ((1,)) in [((2,)),((1,))]          # [int]
print ((3,)) in [((2,)),((1,))]          # [int]

print [1] in ([2],[1])                   # [int]

