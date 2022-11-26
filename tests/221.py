# TODO why no error for b''.hex(':', 2)?

# str

# 'capitalize', 'casefold', 'center', 'find', 'index', 'isalnum', 'isalpha', 'isascii', 'isdecimal', 'isdigit', 'isidentifier', 'isnumeric', 'isspace', 'istitle', 'ljust', 'maketrans', 'partition', 'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit', 'split', 'splitlines', 'startswith', 'title', 'translate', 'zfill'

print('bla'.endswith('la'), 'bla'.endswith('xx'))
print('-'.join(['a', 'b', 'c']))
print('bla'.isprintable(), chr(200).isprintable())
print('blaa'.count('a'), 'blaabla'.count('aa'))
print('bla\tbla'.expandtabs())
print('bla'.upper())
print('BLA'.isupper(), 'bla'.isupper())
print('BLA'.lower())
print('BLA'.islower(), 'bla'.islower())
print('bla'*2, 2*'bla', 'bla'+'bla')
print('bla'.replace('la', 'bla'))
print('bLa'.swapcase())
print('bla  '.strip(), '**bla**'.strip('*'), ' bla'.lstrip(), 'bla'.rstrip('a'))

# bytes

print(b'bla'.endswith(b'la'), b'bla'.endswith(b'xx'))
print(b'-'.join([b'a', b'b', b'c']))
print(b'blaa'.count(ord('a')), b'blaa'.count(b'aa'))
print(b'bla\tbla'.expandtabs())
print(b'bla'.upper())
print(b'BLA'.isupper(), b'bla'.isupper())
print(b'BLA'.lower())
print(b'BLA'.islower(), b'bla'.islower())
print(b'bla'*2, 2*b'bla', b'bla'+b'bla')
print(b'bla'.replace(b'la', b'bla'))
print(b'bLa'.swapcase())
print(b'bla  '.strip(), b'**bla**'.strip(b'*'), b' bla'.lstrip(), b'bla'.rstrip(b'a'))

print(b'blabla'.hex(), b'blabla'.hex(':')) # TODO bytes_per_sep, bytes.fromhex

# bytearray: {'__delitem__', 'pop', 'reverse', '__imul__', 'remove', '__iadd__', 'copy', 'insert', 'extend'} hashing .. __add__, __mul__.. check frozen in above tests?

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
