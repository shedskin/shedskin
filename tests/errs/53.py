s = 'abc'
n = 3
w = 5

# supported: default, explicit str conversion, repr/ascii conversion, '=' form,
# and constant format specs
print(f'{s}')
print(f'{s!s}')
print(f'{s!r}')
print(f'{s!a}')
print(f'{n=}')
print(f'{n:5d}|{n:*^+8,}|{s!r:>8}')
print(f'{n:{w}}')

#*ERROR* 53.py:13: non-constant format spec
