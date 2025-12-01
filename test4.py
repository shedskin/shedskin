

def f(a, b):
    global g
    g = b

    v = 'haha' # doesn't escape
    return a


def g():
    c = 18 # global escape
    f(1, c)


g()
