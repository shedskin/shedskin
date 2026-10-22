import os

log = []


def plain():
    try:
        log.append('body')
    finally:
        log.append('fin')


def returns(x):
    try:
        if x > 0:
            return x * 2
        log.append('no return')
    finally:
        log.append('fin %d' % x)
    return -1


def return_value_before_finally():
    n = 1
    try:
        return n
    finally:
        n = 2  # does not change the value returned


def return_in_finally():
    try:
        raise ValueError('lost')
    finally:
        return 7


def raises():
    try:
        raise KeyError('k')
    finally:
        log.append('fin raises')


def caught():
    try:
        raises()
    except KeyError:
        log.append('caught')


def with_handlers(x):
    try:
        if x == 1:
            raise ValueError('v')
        log.append('ok')
    except ValueError as e:
        log.append('except ' + str(e))
        return 'from except'
    else:
        log.append('else')
    finally:
        log.append('fin handlers')
    return 'end'


def loops():
    for i in range(5):
        try:
            if i == 1:
                continue
            if i == 3:
                break
            log.append('loop %d' % i)
        finally:
            log.append('fin %d' % i)
    else:
        log.append('no break')
    n = 0
    while True:
        n += 1
        try:
            if n == 2:
                break
        finally:
            log.append('while fin %d' % n)


def loop_inside_try():
    try:
        for i in range(3):
            if i == 1:
                break  # leaves the loop, not the try
        log.append('after loop')
    finally:
        log.append('fin loop inside')


def nested():
    try:
        try:
            return 'inner'
        finally:
            log.append('inner fin')
    finally:
        log.append('outer fin')


def finally_raises():
    try:
        try:
            raise ValueError('first')
        finally:
            raise KeyError('second')
    except KeyError as e:
        log.append('replaced')
    except ValueError:
        log.append('not replaced')


def none_returning(flag):
    try:
        if flag:
            return
        log.append('none body')
    finally:
        log.append('none fin')


def gen(n):
    for i in range(n):
        yield i
    try:
        return
    finally:
        log.append('gen fin')


def with_inside():
    try:
        with open(os.devnull, 'w') as f:
            f.write('x')
            return 'with'
    finally:
        log.append('with fin')


# module level
for i in range(3):
    try:
        if i == 1:
            break
    finally:
        log.append('module %d' % i)
try:
    log.append('module body')
finally:
    log.append('module fin')
module_log = log[:]
del log[:]


def test_all():
    assert module_log == ['module 0', 'module 1', 'module body', 'module fin']
    assert list(gen(2)) == [0, 1]
    assert with_inside() == 'with'
    assert log == ['gen fin', 'with fin'], str(log)
    del log[:]
    plain()
    assert returns(3) == 6
    assert returns(0) == -1
    assert return_value_before_finally() == 1
    assert return_in_finally() == 7
    caught()
    assert with_handlers(1) == 'from except'
    assert with_handlers(0) == 'end'
    loops()
    loop_inside_try()
    assert nested() == 'inner'
    finally_raises()
    none_returning(True)
    none_returning(False)
    assert log == ['body', 'fin', 'fin 3', 'no return', 'fin 0',
                   'fin raises', 'caught',
                   'except v', 'fin handlers', 'ok', 'else', 'fin handlers',
                   'loop 0', 'fin 0', 'fin 1', 'loop 2', 'fin 2', 'fin 3',
                   'while fin 1', 'while fin 2',
                   'after loop', 'fin loop inside',
                   'inner fin', 'outer fin', 'replaced',
                   'none fin', 'none body', 'none fin'], str(log)


if __name__ == '__main__':
    test_all()
