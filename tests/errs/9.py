def gen():
    try:
        yield 1
    finally:
        pass

print(list(gen()))

#*ERROR* 9.py:3: 'yield' inside 'try..finally' is not supported
