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



def test_builtin_exception_hierarchy():
    # ArithmeticError is the base of the numeric errors
    caught = ''
    try:
        1 / 0
    except ArithmeticError as e:
        caught = str(e)
    assert caught == 'division by zero'

    caught = ''
    try:
        1 % 0
    except ZeroDivisionError as e:
        caught = str(e)
    assert caught == 'integer modulo by zero'

    caught = ''
    try:
        raise OverflowError('too big')
    except ArithmeticError as e:
        caught = str(e)
    assert caught == 'too big'

    caught = ''
    try:
        raise FloatingPointError('fp')
    except ArithmeticError as e:
        caught = str(e)
    assert caught == 'fp'

    # PythonFinalizationError is a RuntimeError
    caught = ''
    try:
        raise PythonFinalizationError('finalizing')
    except RuntimeError as e:
        caught = str(e)
    assert caught == 'finalizing'

    # FileNotFoundError is an OSError with errno/filename
    caught = ''
    try:
        open('shedskin_no_such_file.txt')
    except FileNotFoundError as fnf:
        caught = fnf.filename
        assert fnf.errno == 2
    assert caught == 'shedskin_no_such_file.txt'
    ok = False
    try:
        os.stat('shedskin_no_such_file.txt')
    except OSError:
        ok = True
    assert ok

    # KeyboardInterrupt and GeneratorExit are BaseExceptions, not Exceptions
    caught = ''
    try:
        raise KeyboardInterrupt('ctrl-c')
    except BaseException as e:
        caught = str(e)
    assert caught == 'ctrl-c'
    caught = ''
    try:
        try:
            raise GeneratorExit('gen')
        except Exception:
            caught = 'wrong'
    except GeneratorExit as e:
        caught = str(e)
    assert caught == 'gen'
    caught = ''
    try:
        try:
            raise KeyboardInterrupt()
        except Exception:
            caught = 'wrong'
    except KeyboardInterrupt:
        caught = 'right'
    assert caught == 'right'


def test_builtin_exception_raise_catch():
    # the remaining plain exceptions: raise, catch by exact type, and by
    # Exception, with args/str preserved
    caught = ''
    try:
        raise EOFError('eof')
    except EOFError as e:
        caught = str(e)
    assert caught == 'eof'

    caught = ''
    try:
        raise MemoryError('oom')
    except MemoryError as e:
        caught = str(e)
    assert caught == 'oom'

    caught = ''
    try:
        raise NameError('name')
    except NameError as e:
        caught = str(e)
    assert caught == 'name'

    caught = ''
    try:
        raise SyntaxError('syntax')
    except SyntaxError as e:
        caught = str(e)
    assert caught == 'syntax'

    caught = ''
    try:
        raise SystemError('system')
    except SystemError as e:
        caught = str(e)
    assert caught == 'system'

    caught = ''
    try:
        raise RuntimeError('runtime')
    except RuntimeError as e:
        caught = str(e)
    assert caught == 'runtime'

    caught = ''
    try:
        raise FloatingPointError('fpe')
    except FloatingPointError as e:
        caught = str(e)
    assert caught == 'fpe'

    caught = ''
    try:
        raise ZeroDivisionError('zde')
    except ZeroDivisionError as e:
        caught = str(e)
    assert caught == 'zde'

    caught = ''
    try:
        raise ArithmeticError('arith')
    except ArithmeticError as e:
        caught = str(e)
    assert caught == 'arith'

    # all of these are plain Exceptions with an empty str() when no args
    # (SyntaxError is the odd one out: its str() is 'None' without args)
    for i in range(6):
        caught = 'unset'
        try:
            if i == 0:
                raise EOFError()
            elif i == 1:
                raise MemoryError()
            elif i == 2:
                raise NameError()
            elif i == 3:
                raise SystemError()
            elif i == 4:
                raise RuntimeError()
            else:
                raise ArithmeticError()
        except Exception as e:
            caught = str(e)
        assert caught == ''

    # repr shows the class name and args
    assert repr(EOFError('x')) == "EOFError('x')"
    assert repr(NameError()) == 'NameError()'
    assert repr(SystemError('sys')) == "SystemError('sys')"

def test_oserror_subclasses():
    # PEP 3151 hierarchy
    hits = 0
    try:
        raise PermissionError('x')
    except OSError:
        hits += 1
    try:
        raise TimeoutError('x')
    except OSError:
        hits += 1
    try:
        raise BrokenPipeError('x')
    except ConnectionError:
        hits += 1
    try:
        raise ConnectionResetError('x')
    except OSError:
        hits += 1
    try:
        raise ProcessLookupError('x')
    except FileNotFoundError:
        hits += 100
    except OSError:
        hits += 1
    assert hits == 5

    # user-raised: no errno, str/repr as for a plain exception
    caught = ''
    try:
        raise FileExistsError('hoppa')
    except OSError as fee:
        caught = str(fee)
        assert repr(fee) == "FileExistsError('hoppa')"
    assert caught == 'hoppa'
    assert str(OSError()) == ''
    assert repr(OSError()) == 'OSError()'

    caught = ''
    try:
        raise ConnectionRefusedError('refused')
    except ConnectionError as ce:
        caught = str(ce)
    assert caught == 'refused'

    # catching a subclass as OSError keeps errno/filename/strerror
    try:
        open('shedskin_no_such_file.txt')
        assert False
    except OSError as oe:
        assert oe.errno == 2
        assert oe.filename == 'shedskin_no_such_file.txt'
        assert oe.strerror == 'No such file or directory'
        assert repr(oe) == "FileNotFoundError(2, 'No such file or directory')"
        assert str(oe) == "[Errno 2] No such file or directory: 'shedskin_no_such_file.txt'"

    # failed calls raise the subclass matching errno
    ok = False
    try:
        os.mkdir('.')
    except FileExistsError as fe:
        ok = fe.errno == 17 and fe.filename == '.'
    assert ok

    ok = False
    try:
        os.rmdir('shedskin_no_such_dir')
    except FileNotFoundError:
        ok = True
    assert ok


def test_more_builtin_exceptions():
    ok = False
    try:
        raise RecursionError('deep')
    except RuntimeError as re1:
        ok = repr(re1) == "RecursionError('deep')"
    assert ok

    ok = False
    try:
        raise UnboundLocalError('local x')
    except NameError as ne1:
        ok = repr(ne1) == "UnboundLocalError('local x')"
    assert ok

    ok = False
    try:
        raise ReferenceError('ref')
    except Exception as ex1:
        ok = repr(ex1) == "ReferenceError('ref')"
    assert ok

    ok = False
    try:
        raise BufferError('buf')
    except Exception as ex2:
        ok = repr(ex2) == "BufferError('buf')"
    assert ok


def test_warnings():
    warnings = [UserWarning('a'), DeprecationWarning('b'),
                PendingDeprecationWarning('c'), SyntaxWarning('d'),
                RuntimeWarning('e'), FutureWarning('f'), ImportWarning('g'),
                UnicodeWarning('h'), BytesWarning('i'), ResourceWarning('j'),
                EncodingWarning('k'), Warning('l')]
    reprs = []
    for w in warnings:
        try:
            raise w
        except Warning as we:
            reprs.append(repr(we))
    assert reprs == ["UserWarning('a')", "DeprecationWarning('b')",
                     "PendingDeprecationWarning('c')", "SyntaxWarning('d')",
                     "RuntimeWarning('e')", "FutureWarning('f')", "ImportWarning('g')",
                     "UnicodeWarning('h')", "BytesWarning('i')", "ResourceWarning('j')",
                     "EncodingWarning('k')", "Warning('l')"]

    ok = False
    try:
        raise DeprecationWarning('old')
    except Exception:
        ok = True
    assert ok


def test_exception_attributes():
    # NameError.name
    assert NameError('x').name is None
    assert NameError('msg', name='y').name == 'y'
    ok = False
    try:
        raise UnboundLocalError('msg', name='z')
    except NameError as ne2:
        ok = ne2.name == 'z' and str(ne2) == 'msg'
    assert ok

    # StopIteration.value (explicit raises)
    assert StopIteration().value is None
    ok = False
    try:
        raise StopIteration('done')
    except StopIteration as si:
        ok = si.value == 'done'
    assert ok

    # SystemExit.code
    ok = False
    try:
        raise SystemExit(3)
    except SystemExit as se:
        ok = se.code == 3
    assert ok

    # OSError errno/strerror/filename/filename2
    oe = OSError('plain')
    assert oe.errno is None or oe.errno == 0  # shedskin: 0
    assert oe.filename2 is None
    ok = False
    try:
        open('shedskin_no_such_file')
    except OSError as oe2:
        ok = oe2.errno > 0 and oe2.strerror is not None and \
            oe2.filename == 'shedskin_no_such_file' and oe2.filename2 is None
    assert ok

    # add_note / __notes__
    ve = ValueError('bad')
    ve.add_note('note 1')
    ve.add_note('note 2')
    assert ve.__notes__ == ['note 1', 'note 2']
    notes = []
    try:
        raise ve
    except ValueError as ve2:
        notes = ve2.__notes__
    assert notes == ['note 1', 'note 2']
    ke = KeyError('k')
    ke.add_note('hmm')
    assert ke.__notes__ == ['hmm']


def test_repr_escapes_argument():
    assert repr(ValueError("it's")) == 'ValueError("it\'s")'
    assert repr(TypeError('a"b')) == "TypeError('a\"b')"
    assert repr(ValueError('x')) == "ValueError('x')"
    assert repr(ValueError()) == 'ValueError()'


def test_all():
    test_repr_escapes_argument()
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
    test_builtin_exception_hierarchy()
    test_builtin_exception_raise_catch()
    test_oserror_subclasses()
    test_more_builtin_exceptions()
    test_warnings()
    test_exception_attributes()


if __name__ == '__main__':
    test_all() 
