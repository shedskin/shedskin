try:
    raise ValueError('x')
except* ValueError:
    print('v')

#*ERROR* 65.py:1: 'except*' is not supported
