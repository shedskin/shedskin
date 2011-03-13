# exception descendant constructor problem
class BadError(Exception):
    pass

if __name__=='__main__':
    BadError()
    BadError("AOE")

