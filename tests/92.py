
def doubles(x):                          # x: [pyiter(A)]
    return [2*e for e in x]              # [list(A)]

f = {1: 1.1, 2: 2.2}                     # [dict(int, float)]
h = {3.1: 3, 2.3: 4}                     # [dict(float, int)]

print doubles(f)                         # [list(int)]
print doubles(h)                         # [list(float)]
print doubles([1.1, 2.2, 3.3])           # [list(float)]

