import os
import sys

class CustomError(Exception):
    pass

class Error(Exception):
    def __init__(self, x):
        pass #print("error.__init__", x)


class ParsingError(Error):
    pass


class MissingSectionHeaderError(ParsingError):
    def __init__(self):
        #print("missingsectionheadererror.__init__")
        Error.__init__(self, "4")

class CustomExceptionA(Exception): pass
class CustomExceptionB(CustomExceptionA): pass
class CustomExceptionC(CustomExceptionB): pass
class CustomExceptionD(CustomExceptionC): pass
class CustomExceptionF(CustomExceptionD): pass


def test_key_error():
    error = False
    try:
        try:
            {1: 2}[3]
        except KeyError as e:
            raise e
    except KeyError:
        error = True
    assert error


def test_assert_error():
    error = False
    try:
        assert 1 == 0
    except AssertionError:
        error = True
    assert error


def test_custom_error():
    error = False
    try:
        raise CustomError()
    except CustomError:
        error = True
    assert error

def test_custom_error_message():
    # regression test: a subclass of Exception with no __init__ override
    # must properly propagate the constructor arg into args/str/repr,
    # instead of shadowing the inherited (uninitialized) args field.
    error = False
    try:
        raise CustomError("mine")
    except CustomError as e:
        assert e.args == ("mine",)
        assert str(e) == "mine"
        assert repr(e) == "CustomError('mine')"
        error = True
    assert error


def test_custom_error2():
    error = False
    try:
        raise MissingSectionHeaderError()
    except MissingSectionHeaderError:
        error = True
    assert error


def test_custom_error3():
    error = False
    try:
        raise CustomExceptionF()
    except CustomExceptionF:
        error = True
    assert error


def test_value_error():
    error = False
    try:
        hum = [1, 2, 3]
        hum.index(4)
    except ValueError:
        error = True
    assert error


def test_os_error():
    error = False
    try:
        os.listdir("/does/not/exist")
    except OSError:
        error = True
    assert error


def test_index_error():
    xs = [1, 2, 3]
    error = False
    try:
        xs[4]
    except IndexError:
        error = True
    assert error

def test_index_error_messages():
    try:
        [1, 2, 3][4]
        assert False
    except IndexError as e:
        assert str(e) == 'list index out of range'

    try:
        [1, 2, 3][4] = 1
        assert False
    except IndexError as e:
        assert str(e) == 'list assignment index out of range'

    try:
        del [1, 2, 3][4]
        assert False
    except IndexError as e:
        assert str(e) == 'list assignment index out of range'

    try:
        "abc"[4]
        assert False
    except IndexError as e:
        assert str(e) == 'string index out of range'

    try:
        (1, 2, 3)[4]
        assert False
    except IndexError as e:
        assert str(e) == 'tuple index out of range'

def test_system_exit_error():
    error = False
    try:
        sys.exit(0)
    except SystemExit:
        error = True
    assert error


def test_args():
    e = Exception('bert')
    assert e.args == ('bert',)
    assert str(e) == 'bert'
    assert repr(e) == "Exception('bert')"


def test_args_empty():
    # regression test: an exception raised without arguments has an empty
    # args tuple. it used to be (NULL,), so str()/repr() indexed straight
    # into a null str * and segfaulted.
    e = Exception()
    assert e.args == ()
    assert len(e.args) == 0
    assert str(e) == ''
    assert repr(e) == 'Exception()'

    error = False
    try:
        raise ValueError()
    except ValueError as e2:
        assert e2.args == ()
        assert str(e2) == ''
        assert repr(e2) == 'ValueError()'
        # assigning the result is the case that regressed: repr() was
        # modelled as returning x.__repr__(), which had no type for
        # exceptions, so 'r' came out untyped and printed None.
        r = repr(e2)
        assert r == 'ValueError()'
        assert len(r) == 12
        error = True
    assert error


def test_repr_result_is_str():
    # repr() must yield a str for every argument, so the result can be
    # assigned, concatenated and measured.
    a = repr(Exception('bert'))
    b = repr(None)
    assert a + ' ' + b == "Exception('bert') None"
    assert len(a) == 17


def test_else():
    a = 5
    try:
        a = 6
    except:
        a = 7
    else:
        a = 8
    assert a == 8


class SalaryNotInRangeError(Exception):
    """Exception raised for errors in the input salary.

    Attributes:
        salary -- input salary which caused the error
        message -- explanation of the error

    from: https://www.programiz.com/python-programming/user-defined-exception
    """

    def __init__(self, salary, message="Salary is not in (5000, 15000) range"):
        self.salary = salary
        self.message = message
        super().__init__(self.message)


def test_custom_salary_error():
    error = False
    salary = 1000
    try:
        if not 5000 < salary < 15000:
            raise SalaryNotInRangeError(salary)
    except SalaryNotInRangeError as e:
        assert e.message == "Salary is not in (5000, 15000) range"
        error = True
    assert error


def test_all():
    test_key_error()
    test_assert_error()
    test_index_error()
    test_value_error()
    test_os_error()
    test_custom_error()
    test_custom_error_message()
    test_custom_error2()
    test_custom_error3()
    test_system_exit_error()
    test_custom_salary_error()
    test_args()
    test_args_empty()
    test_repr_result_is_str()
    test_else()


if __name__ == '__main__':
    test_all() 
