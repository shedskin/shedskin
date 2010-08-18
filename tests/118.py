
class node:                              # activation: [int]*
    def __init__(self, euh, input):      # self: [node], euh: [int], input: [list(int)]
        pass

d = [11]                                 # [list(int)]
e = [12]                                 # [list(int)]

x = []                                   # [list(int)]
y = x                                    # [list(int)]
a = node(1, y)                           # [node]
b = node(2, d)                           # [node]
c = node(3, e)                           # [node]


