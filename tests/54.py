from __future__ import print_function

import copy

class bert:
    pass

a = [1,2]                                # [list(int)]
b = copy.deepcopy(a)                     # [list(int)]

a[0] = 3

print(a, b)

