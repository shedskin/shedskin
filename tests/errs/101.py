# 1178: a value of one type used as another type

l = [1, 2]
print(l.count(1.5))
print(1.5 in l)

d = {1: 'a'}
print(d.get(1.5))
print(d[2.5])

e = {1: 2}
print(e.get(3, 0.5))

f = {1: [1.0]}
g = [3]
f[2] = g

s = {1.0}
t = {1}
print(s == t)

#*WARNING* 101.py:4: incompatible types: 'float' is truncated to 'int'
#*WARNING* 101.py:5: incompatible types: 'float' is truncated to 'int'
#*WARNING* 101.py:8: incompatible types: 'float' is truncated to 'int'
#*WARNING* 101.py:9: incompatible types: 'float' is truncated to 'int'
#*WARNING* 101.py:12: incompatible types: 'float' is truncated to 'int'
#*WARNING* 101.py:16: incompatible types: 'list(int)' cannot be used as 'list(float)'
#*WARNING* 101.py:20: incompatible types: 'set(int)' cannot be used as 'set(float)'
