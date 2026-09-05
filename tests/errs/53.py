s = 'abc'
n = 3

print(f'{s!a}')
print(f'{n:5d}')

# supported: default, explicit str conversion, repr conversion, '=' form
print(f'{s}')
print(f'{s!s}')
print(f'{s!r}')
print(f'{n=}')

#*WARNING* 53.py:4: f-string conversion '!a' is not supported
#*WARNING* 53.py:5: f-string format spec is not supported
