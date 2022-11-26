# str/bytes/bytearray

# str

# 'capitalize', 'casefold', 'center', 'find', 'index', 'isalnum', 'isalpha', 'isascii', 'isdecimal', 'isdigit', 'isidentifier', 'isnumeric', 'isspace', 'istitle', 'ljust', 'lstrip', 'maketrans', 'partition', 'replace', 'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit', 'rstrip', 'split', 'splitlines', 'startswith', 'strip', 'swapcase', 'title', 'translate', 'zfill'

print('bla'.endswith('la'), 'bla'.endswith('xx'))
print('-'.join(['a', 'b', 'c']))
print('bla'.isprintable(), chr(200).isprintable())
print('blaa'.count('a'), 'blaabla'.count('aa'))
print('bla\tbla'.expandtabs())
print('bla'.upper())
print('BLA'.isupper(), 'bla'.isupper())
print('BLA'.lower())
print('BLA'.islower(), 'bla'.islower())

# bytes

# {'fromhex', 'hex'} __add__, __mul__..?

print(b'bla'.endswith(b'la'), b'bla'.endswith(b'xx'))
print(b'-'.join([b'a', b'b', b'c']))
print(b'blaa'.count(ord('a')), b'blaa'.count(b'aa'))
print(b'bla\tbla'.expandtabs())
print(b'bla'.upper())
print(b'BLA'.isupper(), b'bla'.isupper())
print(b'BLA'.lower())
print(b'BLA'.islower(), b'bla'.islower())

# bytearray: {'__delitem__', 'pop', 'reverse', '__imul__', 'remove', '__iadd__', 'copy', 'insert', 'extend'} hashing

ba = bytearray(b'bla')
ba.clear()
print(ba)

ba = bytearray(b'bla')
ba[1] = 80
print(ba)

ba = bytearray(b'bla')
ba.append(81)
ba.append(187)
print(ba)
