
a = 1                                    # [int]
a += 2                                   # [int]
print a                                  # [int]

b = [1]                                  # [list(int)]
b += [2]                                 # [list(int)]
print b                                  # [list(int)]

print 2*b                                # [list(int)]
print b*2                                # [list(int)]

print 2*'hoi'                            # [str]
print 'hoi'*2                            # [str]

class fred:
    def __add__(self, b):                # self: [fred], b: [pyobj]r
        return b                         # [pyobj]
    def __augadd__(self, b):             # self: [fred], b: [pyobj]
        pass
class bert:
    def __add__(self, b):                # self: [bert], b: [pyobj]r
        return b                         # [pyobj]
    def __augadd__(self, b):             # self: [bert], b: [pyobj]
        pass

p = fred()                               # [fred]
p = bert()                               # [bert]

p += p                                   # [pyobj]
p = p + p                                # [pyobj]

print sum([1,2,3,4])                     # [int]
print sum([1.25, 2.25, 3.25, 4.25])      # [float]

