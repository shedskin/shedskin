try:
    pass
except KeyboardInterrupt:
    print('uhw')

l = [lambda x,y: (y,x)]
print(l.pop()(1,2))

kwa = (1, None, [1], 'boe')
stack = ('hoi', frozenset([(0,0)]), 'ah', 1.0)

#*WARNING* 4.py:3: system 'KeyboardInterrupt' is not caught
#*WARNING* 4.py:6: 'list' instance containing function reference
#*WARNING* 4.py:9: tuple with length > 3 and different types of elements
#*WARNING* 4.py:10: tuple with length > 3 and different types of elements
