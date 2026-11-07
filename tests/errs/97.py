from collections import Counter

c = Counter('aab')
dict.update(c, {'a': 5})  # non-virtual in Python: not Counter.update
print(c)

#*ERROR* 97.py:4: unsupported call 'dict.update(..)' with argument of type 'Counter'
