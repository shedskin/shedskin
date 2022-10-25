from __future__ import print_function

def pascal(n):
    """pascal(n): print n first lines of Pascal's
    triangle (shortest version)."""
    r = [[1]]
    for i in range(1, n):
        r += [[1] + [sum(r[-1][j:j+2]) for j in range(i)]]
    return r

print(pascal(9))

