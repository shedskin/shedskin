
b = 'b'                                  # [str]
bert = [b,'e','r','t']                   # [list(str)]
print bert                               # [list(str)]

#c = 1                                    # [int]
c = 'c'                                  # [str]
cert = [c,'3','r','t']                     # [list(int,str)]
#cert = [c,3,'r','t']                     # [list(int,str)]
print c                                  # [int, str]
print cert                               # [list(int,str)]

def huhu(s):                             # s: [str]r
   # s += 'hola'                          # []
   # print s                              # [str]
    return s                             # [str]
def huhu2(s):                            # s: [int, str]r
    s += 'hola'                          # []
   # print s                              # [int, str]
    return s                             # [int, str]

d = 'crap'                               # [str]
huhu(d)                                  # [str]
print d                                  # [str]
f = 1
huhu(f)

#e = 2                                    # [int]
e = 'crap'                               # [str]
huhu2(e)                                 # [int, str]
print e                                  # [int, str]

