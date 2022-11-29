# TODO del/assign slice
# TODO hex(bytes_per_sep), bytes.fromhex
# TODO maketrans, translate

# str

print('bla'.endswith('la'), 'bla'.endswith('xx'))
print('bla'.startswith('bla'), 'bla'.startswith('xx'))
print('-'.join(['a', 'b', 'c']))
print('blaa'.count('a'), 'blaabla'.count('aa'))
print('bla\tbla'.expandtabs())
print('bla'.upper())
print('BLA'.isupper(), 'bla'.isupper(), ''.isupper())
print('BLA'.lower())
print('BLA'.islower(), 'bla'.islower(), ''.islower())
print('bla'*2, 2*'bla', 'bla'+'bla')
print('bla'.replace('la', 'bla'))
print('bLa'.swapcase())
print('bla  '.strip(), '**bla**'.strip('*'), ' bla'.lstrip(), 'bla'.rstrip('a'))
print('bla'.find('la'), 'bla'.find('ba'))
print('bla'.rfind('la'), 'bla'.rfind('ba'))
print('bla'.index('la'), 'bla'.index('bl'))
print('bla'.rindex('la'), 'bla'.rindex('bl'))
print('bla'.center(10), 'bla'.center(10, '-'))
print('bla'.split('l'), 'b l a'.split(), 'haajaaja'.split('aa'))
print('bla'.rsplit('l'), 'b l a'.rsplit(), 'haajaaja'.rsplit('aa'))
print('bla'.zfill(10))
print('bla'.ljust(8), 'bla'.ljust(6, '+'))
print('bla'.rjust(8), 'bla'.rjust(6, '-'))
print('bla bla'.title())
print('bla bla'.capitalize())
print('bla'[1], 'bla'[1:], 'bla'[::-1])
print('bla'.istitle(), 'Bla'.istitle(), ''.istitle())
print('bla'.isspace(), '   '.isspace(), ''.isspace())
print('bla'.isalpha(), '123'.isalpha(), ''.isalpha())
print('bla'.isdigit(), '123'.isdigit(), ''.isdigit())
print('bla'.isalnum(), '123'.isalnum(), '12a'.isalnum(), ''.isalnum())
print('bla'.isprintable(), chr(200).isprintable(), ''.isprintable())
print('bla'.isnumeric(), '123'.isnumeric(), ''.isnumeric())
print('bla'.isdecimal(), '123'.isdecimal(), ''.isdecimal())
print('bla'.isascii(), '\xf0'.isascii(), ''.isascii())
print('Bla_'.isidentifier(), '9bla'.isidentifier(), ''.isidentifier())
print('bla\r\nblup'.splitlines(), 'bla\r\nblup'.splitlines(keepends=True))
print('aa-bb-cc'.partition('-'), 'aa-bb-cc'.rpartition('-'))
print('bla'[1], 'bla'[1:], 'bla'[::-1])
print('BLA'.casefold())
print('bla'+'bla', 'bla'*3, 3*'bla')
print('bla' == 'bla', 'bla' == 'blup', 'bla' != 'bla', 'bla' != 'blup')
print('aap' > 'blup', 'blup' >= 'aap', 'aap' < 'blup', 'aap' <= 'blup')
print(sorted(['blup', 'aap']))
print(list('aap'))

# bytes

print(b'bla'.endswith(b'la'), b'bla'.endswith(b'xx'))
print(b'bla'.startswith(b'bla'), b'bla'.startswith(b'xx'))
print(b'-'.join([b'a', b'b', b'c']))
print(b'blaa'.count(ord('a')), b'blaa'.count(b'aa'))
print(b'bla\tbla'.expandtabs())
print(b'bla'.upper())
print(b'BLA'.isupper(), b'bla'.isupper(), b''.isupper())
print(b'BLA'.lower())
print(b'BLA'.islower(), b'bla'.islower(), b''.islower())
print(b'bla'*2, 2*b'bla', b'bla'+b'bla')
print(b'bla'.replace(b'la', b'bla'))
print(b'bLa'.swapcase())
print(b'bla  '.strip(), b'**bla**'.strip(b'*'), b' bla'.lstrip(), b'bla'.rstrip(b'a'))
print(b'bla'.find(b'la'), b'bla'.find(b'ba'))
print(b'bla'.rfind(b'la'), b'bla'.rfind(b'ba'))
print(b'bla'.index(b'la'), b'bla'.index(b'bl'))
print(b'bla'.rindex(b'la'), b'bla'.rindex(b'bl'))
print(b'bla'.center(10), b'bla'.center(10, b'-'))
print(b'bla'.split(b'l'), b'b l a'.split(), b'haajaaja'.split(b'aa'))
print(b'bla'.rsplit(b'l'), b'b l a'.rsplit(), b'haajaaja'.rsplit(b'aa'))
print(b'bla'.zfill(10))
print(b'bla'.ljust(8), b'bla'.ljust(6, b'+'))
print(b'bla'.rjust(8), b'bla'.rjust(6, b'-'))
print(b'blabla'.hex(), b'blabla'.hex(':'))
print(b'bla bla'.title())
print(b'bla bla'.capitalize())
print(b'bla'.istitle(), b'Bla'.istitle(), b''.istitle())
print(b'bla'.isspace(), b'   '.isspace(), b''.isspace())
print(b'bla'.isalpha(), b'123'.isalpha(), b''.isalpha())
print(b'bla'.isdigit(), b'123'.isdigit(), b''.isdigit())
print(b'bla'.isalnum(), b'123'.isalnum(), b'12a'.isalnum(), b''.isalnum())
print(b'bla'.isascii(), b'\xf0'.isascii(), b''.isascii())
print(b'bla\r\nblup'.splitlines(), b'bla\r\nblup'.splitlines(keepends=True))
print(b'aa-bb-cc'.partition(b'-'), b'aa-bb-cc'.rpartition(b'-'))
print(b'bla'[1], b'bla'[1:], b'bla'[::-1])
print(b'bla'+b'bla', b'bla'*3, 3*b'bla')
print(b'bla' == b'bla', b'bla' == b'blup', b'bla' != b'bla', b'bla' != b'blup')
print(b'aap' > b'blup', b'blup' >= b'aap', b'aap' < b'blup', b'aap' <= b'blup')
print(sorted([b'blup', b'aap']))
print(list(b'aap'))

h = hash(b'bla')

bdict = {
    b'bla': 18,
    b'blup': 19,
}
for key in sorted(bdict):
    print(key, bdict[key])

print(set([b'blup']))

# bytearray

BLA = bytearray(b'bla')
BA = bytearray(b'-')
A = bytearray(b'a')
B = bytearray(b'b')
C = bytearray(b'c')

print(BA.join([A, B, C]))
print(BA.expandtabs())
print(BA.upper())
print(BA.lower())
print(BA.replace(A, B))
print(BA.swapcase())
print(BA.split())
print(BA.rsplit())
print(BA.strip(), BA.lstrip(), BA.rstrip())
print(BA.center(10))
print(bytearray(b'-').zfill(10))
print(BA.ljust(10), BA.rjust(10))
print(BA.title())
print(BA.capitalize())
print(BA.splitlines())
print(BLA.partition(A), BLA.rpartition(B))
print(BLA[1], BLA[1:], BLA[::-1])
print(BLA+BLA, 3*BLA, BLA*3)

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

ba = bytearray(b'bla')
ba.extend([1,2])
ba.extend(b'ab')
ba.extend(BA)
print(ba)

ba = bytearray(b'bla')
ba.reverse()
print(ba)

ba = bytearray(b'bla')
ba.remove(ord('l'))
print(ba)

ba = bytearray(b'bla')
ba += A + B
print(ba)
ba *= 2
print(ba)

ba = bytearray(b'bla')
ba.insert(1, ord('u'))
ba.insert(-2, ord('w'))
print(ba)

try:
    h = hash(bytearray(b'bla'))
except TypeError:
    print('bytearray unhashable')

ba = bytearray(b'blablabla')
ba[1:4] = [ord('c'), ord('d')]
print(ba)
ba[1:4] = BLA
print(ba)

del ba[::2]
print(ba)
