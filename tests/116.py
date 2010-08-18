
def _enumerate(x):                        # x: [pyiter(A)]
    i = 0                                # [int]
    result = []                          # [list(tuple2(int, A))]
    for e in x:                          # [pyiter(A)]
        result.append((i,e))             # []
        i += 1
    return result                        # [list(tuple2(int, A))]

print _enumerate(['0','1','2'])           # [list(tuple2(int, str))]
print _enumerate((2,1,0))                 # [list(tuple(int))]
print _enumerate({1: 2, 3: 4})            # [list(tuple(int))]

def mini(arg1, arg2=None):                # arg1: [A], arg2: [pyobj]
    return arg1.getunit()                # [pyobj]

def maxi(arg1, arg2=None):                # arg1: [], arg2: []
    return arg1.getunit()                # []

print mini([8,7,9])                       # [int]
print mini(2,1)                           # [int]
print mini(1.1,2.1)                       # [float]

def _zip(a, b):                           # a: [pyiter(A)], b: [pyiter(B)]
    la = [e for e in a]                  # [list(A)]
    lb = [e for e in b]                  # [list(B)]

    result = []                          # [list(tuple2(A, B))]

    for i in range(mini(len(la), len(lb))): # [list(int)]
        result.append((la[i], lb[i]))    # []
    return result                        # [list(tuple2(A, B))]


print _zip({1:2, 2:3}, (1.1,2.2,3.3))     # [list(tuple2(int, float))]
print _zip((1.1,2.2,3.3), {1:2, 2:3})     # [list(tuple2(float, int))]

def _sum(l):                              # l: [pyiter(A)]
    first = True                         # [int]
    for e in l:                          # [pyiter(A)]
        if first:                        # []
            result = e                   # [A]
            first = False                # [int]
        else:
            result += e                  # [A]
    return result                        # [A]

print _sum([1,2,3,4])                     # [int]
print _sum({1.1: 2.2, 3.3: 4.4})          # [float]

