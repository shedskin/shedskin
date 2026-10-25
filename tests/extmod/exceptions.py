import sys

# exception subclasses defined in an extension module are exported as Python
# exception types (with the same bases), so Python code can catch them by
# type, and their attributes are copied when raised; see exceptions_main.py

class MyError(Exception):
    pass

class SubError(MyError):
    pass

class MyValueError(ValueError):
    pass

class MyKeyError(KeyError):
    pass

class MyOSError(OSError):
    pass

class CodeError(MyError):
    def __init__(self, msg, code):
        super().__init__(msg)
        self.code = code
        self.where = ['here']

class SubCodeError(CodeError):
    def __init__(self, msg, code, extra):
        super().__init__(msg, code)
        self.extra = extra

class StrError(MyError):
    def __init__(self, code):
        MyError.__init__(self, 'base msg')
        self.code = code
    def __str__(self):
        return 'StrError code=%d' % self.code

class SubStrError(StrError):
    pass

class OtherStrError(StrError):
    def __str__(self):
        return 'other %d' % self.code

class ReprError(Exception):
    def __repr__(self):
        return 'ReprError!'

class BadStrError(KeyError):
    def __str__(self):
        if self.args[0] == 'bad':
            raise ValueError('no str')
        return 'fine'


def boom(n):
    if n == 1:
        raise MyError('boom')
    if n == 2:
        raise SubError('sub')
    if n == 3:
        raise MyValueError('value')
    if n == 4:
        raise MyKeyError('key')
    if n == 5:
        raise MyOSError('os')
    if n == 6:
        raise ValueError('plain')
    if n == 7:
        raise CodeError('code', 42)
    if n == 8:
        raise SubCodeError('subcode', 43, 1.5)
    if n == 9:
        raise StrError(7)
    if n == 10:
        raise SubStrError(8)
    if n == 11:
        raise OtherStrError(9)
    if n == 12:
        raise ReprError('repr')
    if n == 13:
        raise BadStrError('bad')
    return n

def catch_inside(n):
    try:
        boom(n)
    except MyError as e:
        return 'MyError ' + str(e)
    except ValueError as e:
        return 'ValueError ' + str(e)
    except LookupError:
        return 'LookupError'
    except OSError as e:
        return 'OSError ' + str(e)
    return 'none'

def stop(n):
    # exceptions that do not derive from Exception (1025-A3)
    if n == 0:
        raise SystemExit(3)
    if n == 1:
        sys.exit('bye')
    if n == 2:
        raise SystemExit
    if n == 3:
        raise KeyboardInterrupt('ctrl-c')
    if n == 4:
        raise GeneratorExit('gen')
    if n == 5:
        sys.exit(0)
    return n


if __name__ == '__main__':
    # make sure everything is called with the types used from exceptions_main.py
    for i in range(14):
        try:
            boom(i)
        except Exception:
            pass
    for i in range(9):
        catch_inside(i)
    for i in range(7):
        try:
            stop(i)
        except BaseException:
            pass
    # __str__/__repr__ are only exported when called
    for e in [StrError(1), SubStrError(2), OtherStrError(3), ReprError('r')]:
        str(e), repr(e)
    for msg in ['bad', 'good']:
        try:
            str(BadStrError(msg))
        except ValueError:
            pass
