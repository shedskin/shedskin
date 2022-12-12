# __NOT macro missing parentheses
x=10
if not 1<x<10:
    print("out of constraint")

# enumerate start arg
print(list(enumerate('hoppa', 2)))

# os.listdir crash
import os
try:
    print(os.listdir('/does/not/exist'))
except OSError:
    print('path does not exist!')

# itertools.izip missing constructor
#import itertools
#for a,b in itertools.izip(list(range(4)), list(range(4))):
#    print(a+b)

# sys.exit case
import sys
sys.exit(7)
