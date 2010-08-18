
def hoi():                               # dinges: [list(int)], bla: [list(int)]
    bla = [1,2]                          # [list(int)]
    dinges = [1,2]                       # [list(int)]
    jada = [1,2]                         # [list(int)]

    u = [x for x in bla]                 # [list(int)]
    v = [[a for a in bla] for c in dinges] # [list(list(int))]
    w = [[[a for a in jada] for c in bla] for d in dinges] # [list(list(list(int)))]

    print u                              # [list(int)]
    print v                              # [list(list(int))]
    print w                              # [list(list(list(int)))]

    return bla                           # [list(int)]
    return dinges                        # [list(int)]

print hoi()                              # [list(int)]

