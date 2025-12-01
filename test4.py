g = 0

def f(a, b):  # a, b escape, v doesn't
    global g
    g = b

    v = (1, 2) # doesn't escape

    return a # escapes one level


def e():  # c escapes via g, j doesn't escape
    c = 18
    f(1, c)

    for j in range(10):
        pass

e()
