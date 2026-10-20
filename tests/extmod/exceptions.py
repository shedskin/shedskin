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


if __name__ == '__main__':
    # make sure everything is called with the types used from exceptions_main.py
    for i in range(9):
        try:
            boom(i)
        except Exception:
            pass
        catch_inside(i)
