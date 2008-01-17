
def copy(a):
    a.__copy__() # XXX hardcode in ss.py?
    return a

def deepcopy(a):
    a.__deepcopy__()
    return a