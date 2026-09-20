# Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE)

DEBUG_STATS = 1
DEBUG_COLLECTABLE = 2
DEBUG_UNCOLLECTABLE = 4
DEBUG_SAVEALL = 32
DEBUG_LEAK = 38

def enable():
    pass

def disable():
    pass

def isenabled():
    return True

def collect(generation=2):
    return 1

def get_count():
    return (1, 1, 1)

def get_threshold():
    return (1, 1, 1)

def set_threshold(threshold0, threshold1=-1, threshold2=-1):
    pass

def get_debug():
    return 1

def set_debug(flags):
    pass

def freeze():
    pass

def unfreeze():
    pass

def get_freeze_count():
    return 1

def is_finalized(obj):
    return True
