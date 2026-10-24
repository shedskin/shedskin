def gen():  # first yield in the else clause
    try:
        pass
    except ValueError:
        pass
    else:
        yield 1
    finally:
        pass

print(list(gen()))

#*ERROR* 78.py:7: 'yield' inside 'try..finally' is not supported
