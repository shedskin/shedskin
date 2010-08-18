
class Const:
    def __repr__(self):                  # self: [Const()]
        return 'const'                   # [str]
class Name:
    def __repr__(self):                  # self: [Name()]
        return 'name'                    # [str]

class Assign:                            # y: [int]*, x: [int, str]*
    def __init__(self, expr, i):         # self: [Assign(str), Assign(int)], expr: [Name(), Const()], i: [int, str]
        print expr                       # [Name(), Const()]

expr = Const()                           # [Const()]
expr = Name()                            # [Name()]
assign = Assign(expr, 1)                 # [Assign(int)]
assign.x = 1                             # [int]
assign.y = 7                             # [int]

bla = Const()                            # [Const()]
ass2 = Assign(bla, '1')                  # [Assign(str)]
ass2.x = '1'                             # [str]
ass2.y = 8                               # [int]

