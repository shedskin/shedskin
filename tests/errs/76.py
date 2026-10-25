def gen(n):  # first yield in the finally body
    try:
        n += 1
    finally:
        yield n
    yield n + 1

print(list(gen(1)))

#*ERROR* 76.py:5: 'yield' inside 'try..finally' is not supported
