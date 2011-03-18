# exception hierarchy problem 1
class BadError(Exception):
    pass

if __name__=='__main__':
    BadError()
    BadError("AOE")

# exception hierarchy problem 2
class MyBaseException:
    def __init__(self, msg=None):
        self.msg = msg
class MyException(MyBaseException): pass
class MyStandardError(MyException): pass
class MyBadError(MyException):
    pass

if __name__=='__main__':
    MyStandardError()
    MyBadError()
