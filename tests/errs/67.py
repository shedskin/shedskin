dicts = [{1: 2}, {3: 4}]
print({**d for d in dicts})

#*ERROR* 67.py:2: dict unpacking ('**') in a dict comprehension is not supported
