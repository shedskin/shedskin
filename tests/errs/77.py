def gen():  # first yield in a handler
    try:
        pass
    except ValueError:
        yield 1
    finally:
        pass

print(list(gen()))

#*ERROR* 77.py:5: 'yield' inside 'try..finally' is not supported
