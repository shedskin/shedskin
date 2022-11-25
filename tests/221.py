# str/bytes/bytearray

# str

# 'capitalize', 'casefold', 'center', 'count', 'expandtabs', 'find', 'index', 'isalnum', 'isalpha', 'isascii', 'isdecimal', 'isdigit', 'isidentifier', 'islower', 'isnumeric', 'isprintable', 'isspace', 'istitle', 'isupper', 'join', 'ljust', 'lower', 'lstrip', 'maketrans', 'partition', 'replace', 'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit', 'rstrip', 'split', 'splitlines', 'startswith', 'strip', 'swapcase', 'title', 'translate', 'upper', 'zfill'

print('bla'.endswith('la'))

# bytes

# str ^ bytes: {'casefold', 'isidentifier', 'fromhex', 'format', 'isprintable', 'hex', 'decode', 'isdecimal', 'isnumeric'}

print(b'bla'.endswith(b'la'))

# bytes ^ bytearray: {'__delitem__', 'pop', 'reverse', '__imul__', 'remove', 'append', '__iadd__', 'copy', 'insert', '__setitem__', 'extend'}

ba = bytearray(b'bla')
ba.clear()
print(ba)
