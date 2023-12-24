import os
import sys

class CustomError(Exception):
    pass

class Error(Exception):
    def __init__(self, x):
        print("error.__init__", x)


class ParsingError(Error):
    pass


class MissingSectionHeaderError(ParsingError):
    def __init__(self):
        print("missingsectionheadererror.__init__")
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

def test_system_exit_error():
    error = False
    try:
        sys.exit(0)
    except SystemExit:
        error = True
    assert error


# def test_type_error():
#     error = False
#     try:
#         1 + 'a'
#     except TypeError:
#         error = True
#     assert error


# class SalaryNotInRangeError(Exception):
#     """Exception raised for errors in the input salary.

#     Attributes:
#         salary -- input salary which caused the error
#         message -- explanation of the error

#     from: https://www.programiz.com/python-programming/user-defined-exception
#     """

#     def __init__(self, salary, message="Salary is not in (5000, 15000) range"):
#         self.salary = salary
#         self.message = message
#         super().__init__(self.message)


# def test_custom_salary_error():
#     error = False
#     salary = 1000
#     try:
#         if not 5000 < salary < 15000:
#             raise SalaryNotInRangeError(salary)
#     except SalaryNotInRangeError as e:
#         assert e.message == "Salary is not in (5000, 15000) range"
#         error = True
#     assert error


def test_all():
    test_key_error()
    # test_type_error() # cpp translated code will not compile :-)
    test_assert_error()
    test_index_error()
    # test_my_error()
    test_value_error()
    test_os_error()
    test_custom_error()
    test_custom_error2()
    test_custom_error3()
    test_system_exit_error()
    # test_custom_salary_error() # FIXME: super not supported


if __name__ == '__main__':
    test_all() 
