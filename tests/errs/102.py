# list + list, with a non-literal operand that would need a wider element type

b = [1, 2]
print(b + [0.5])
c = b + [0.5]
print([0.5] + b)

d = [1.5]
print(b + d)

#*WARNING* 102.py:4: incompatible types
#*WARNING* 102.py:5: incompatible types
#*WARNING* 102.py:6: incompatible types
#*WARNING* 102.py:9: incompatible types
