# TODO why no error for b''.hex(':', 2)?

# str

# 'casefold', 'index', 'isascii', 'isdecimal', 'isidentifier', 'isnumeric', 'maketrans', 'partition', 'rfind', 'rindex', 'rpartition', 'rsplit', 'splitlines', 'translate'

print('bla'.endswith('la'), 'bla'.endswith('xx'))
print('bla'.startswith('bla'), 'bla'.startswith('xx'))
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
print('bla'.istitle(), 'Bla'.istitle())
print('bla'.isspace(), '   '.isspace())
print('bla'.isalpha(), '123'.isalpha())
print('bla'.isdigit(), '123'.isdigit())
print('bla'.isalnum(), '123'.isalnum(), '12a'.isalnum())
print('bla'.find('la'), 'bla'.find('ba'))
print('bla'.center(10), 'bla'.center(10, '-'))
print('bla'.split('l'), 'b l a'.split(), 'haajaaja'.split('aa'))
print('bla'.zfill(10))
print('bla'.ljust(8), 'bla'.ljust(6, '+'))
print('bla'.rjust(8), 'bla'.rjust(6, '-'))
print('bla bla'.title())
print('bla bla'.capitalize())
print('bla'[1], 'bla'[1:], 'bla'[::-1])

# bytes

print(b'bla'.endswith(b'la'), b'bla'.endswith(b'xx'))
print(b'bla'.startswith(b'bla'), b'bla'.startswith(b'xx'))
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
print(b'bla'.istitle(), b'Bla'.istitle())
print(b'bla'.isspace(), b'   '.isspace())
print(b'bla'.isalpha(), b'123'.isalpha())
print(b'bla'.isdigit(), b'123'.isdigit())
print(b'bla'.isalnum(), b'123'.isalnum(), b'12a'.isalnum())
print(b'bla'.find(b'la'), b'bla'.find(b'ba'))
print(b'bla'.center(10), b'bla'.center(10, b'-'))
print(b'bla'.split(b'l'), b'b l a'.split(), b'haajaaja'.split(b'aa'))
print(b'bla'.zfill(10))
print(b'bla'.ljust(8), b'bla'.ljust(6, b'+'))
print(b'bla'.rjust(8), b'bla'.rjust(6, b'-'))
print(b'blabla'.hex(), b'blabla'.hex(':')) # TODO bytes_per_sep, bytes.fromhex
print(b'bla bla'.title())
print(b'bla bla'.capitalize())
print(b'bla'[1], b'bla'[1:], b'bla'[::-1])

# bytearray: {'reverse', '__imul__', 'remove', '__iadd__', 'insert', 'extend'} hashing .. check frozen in above tests? del/assign slice?

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

ba = bytearray(b'bla')
del ba[1]
print(ba)
del ba[-2]
print(ba)

ba = bytearray(b'bla')
print(ba.copy())

print(2*ba, ba*2, ba+ba)

ba = bytearray(b'bla')
print(ba.pop(0))
print(ba.pop())
print(ba)
