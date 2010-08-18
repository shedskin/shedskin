
def ident(x, y, z):                      # x: [int, str]r, y: [int, str], z: [float]
    return x                             # [int, str]

def retint():
    return 1                             # [int]

a = ident(1, 1, 1.1)                     # [int]
b = ident('1', '1', 1.1)                 # [str]
c = retint()                             # [int]

