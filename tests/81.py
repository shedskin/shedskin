
def _reduce(f, l, i=-1):                  # f: [lambda0], l: [list(int)], i: [int]r
    if not l:                            # [list(int)]
        if i != -1: return i             # [int]
        print '*** ERROR! *** reduce() called with empty sequence and no initial value' # [str]

    if i != -1:                          # [int]
        r = f(i, l[0])                   # [int]
    else:
        r = l[0]                         # [int]

    for i in range(len(l)-1):            # [list(int)]
        r = f(r, l[i+1])                 # [int]

    return r                             # [int]

acc = lambda x,y: x+y                    # [lambda0]
score = [1,2,3,4]                        # [list(int)]

print _reduce(acc, score, 0)              # [int]

