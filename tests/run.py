#!/usr/bin/env python
from __future__ import print_function
import traceback
import sys
import os
import tempfile
import threading
import time
import subprocess
import glob
import os.path
import functools
import itertools
from difflib import unified_diff
from multiprocessing import Pool
from multiprocessing.pool import IMapIterator


#Fix for multiprocessing. Without this, Ctrl+C will not kill the process immediately
set_timeout_decorator = lambda func: lambda self: func(self, timeout=1e100)
IMapIterator.next = set_timeout_decorator(IMapIterator.next)


SS = ' -m shedskin'
os.environ['PYTHONPATH'] = os.path.realpath('..')


def usage():
    print("'-l': give individual test numbers")
    print("'-r': reverse test order")
    print("'-f': break after first failure")
    print("'-e': run extension module tests")
    print("'-n': normal tests as extension modules")
    print("'-x': run error/warning message tests")
    print("'-p': run the tests in parallel")
    print("'--output': show output even when run in parallel")
    sys.exit()


def parse_options():
    args, options = [], set()
    for arg in sys.argv[1:]:
        if arg.startswith('--'):
            options.add(arg[2:])
        elif arg.startswith('-'):
            options.update(arg[1:])
        else:
            args.append(int(arg))
    return args, options


def test_numbers(args, options):
    if 'l' in options:
        tests = args

    elif len(args) == 1:
        tests = [args[0]]
    elif len(args) == 2:
        if args[0] > args[1]:
            args[0], args[1] = args[1], args[0]
            options.add('r')
        tests = list(range(args[0], args[1]))
    else:
        tests = sorted([int(os.path.splitext(f)[0]) for f in glob.glob('*.py') if f != 'run.py'])

    if 'r' in options:
        tests.reverse()

    return tests


def tests(args, options):
    parallel = 'p' in options
    msvc = 'v' in options
    partial_run_test = functools.partial(run_test, msvc=msvc, options=options)
    tests = [test for test in test_numbers(args, options)
             if os.path.exists('%d.py' % test)]
    failures = []

    try:
        default_imap = itertools.imap
    except AttributeError:
        default_imap = map

    if "OMP_NUM_THREADS" in os.environ:
        imap = Pool(int(os.environ["OMP_NUM_THREADS"])).imap if parallel else default_imap
    else:
        imap = Pool().imap if parallel else default_imap

    for result in imap(partial_run_test, tests):
        if result is not None:
            failures.append(result)
            if 'f' in options:
                break

    return failures


def main():
    args, options = parse_options()
    if 'h' in options:
        usage()

    if 'e' in options:
        failures = extmod_tests(args, options)
    elif 'x'in options:
        failures = error_tests(args, options)
    else:
        failures = tests(args, options)

    if not failures:
        print('*** no failures, yay!')
    else:
        print('*** tests failed:', len(failures))
        print(failures)
        sys.exit(failures)


output_lock = threading.Lock()
def run_test(test, msvc, options):
    parallel = 'p' in options
    show_parallel_output = 'output' in options

    def run_test_with_output(output):
        execute = functools.partial(subprocess.call, stdout=output, stderr=output, shell=True)
        t0 = time.time()
        try:
            if msvc:
                assert execute('%s %s -v %d' % (sys.executable, SS, test)) == 0
            elif 'n' in options:
                assert execute('%s %s -e -m Makefile.%d %d' % (sys.executable, SS, test, test)) == 0
            else:
                assert execute('%s %s -m Makefile.%d %d' % (sys.executable, SS, test, test)) == 0
            if msvc:
                assert execute('nmake /C /S clean') == 0
                assert execute('nmake /C /S') == 0
                command = '.\\%d' % test
            else:
                assert execute('make clean -f Makefile.%d' % test) == 0
                assert execute('make -f Makefile.%d' % test) == 0
                if sys.platform == 'win32':
                    command = '%d' % test
                else:
                    command = './%d' % test
            if 'n' in options:
                if test not in [136, 154, 163, 191, 196, 197, 198]:  # sys.exit
                    assert execute('%s -c "__import__(str(%d))"' % (sys.executable, test)) == 0
            else:
                check_output(command, '%s %d.py' % (sys.executable, test))
            with output_lock:
                print('*** success: %d (%.2f)' % (test, time.time() - t0))
        except AssertionError:
            with output_lock:
                print('*** failure:', test)
                traceback.print_exc()
            return test

    print('*** test:', test)
    if parallel and not show_parallel_output:
        with open(os.devnull, "w") as fnull:
            return run_test_with_output(fnull)
    elif not parallel:
        return run_test_with_output(None)
    elif parallel:
        with tempfile.TemporaryFile() as temp:
            res = run_test_with_output(temp)
            temp.seek(0)
            with output_lock:
                print('*** output:', test)
                print(temp.read())
            return res


def extmod_tests(args, options):
    failures = []
    tests = sorted([int(t[1:]) for t in glob.glob('e*') if t[1:].isdigit()])
    for test in tests:
        print('*** test:', test)
        os.chdir('e%d' % test)
        try:
            extmod = file('main.py').next()[1:].strip()
            assert os.system('%s %s -e %s' % (sys.executable, SS, extmod)) == 0
            assert os.system('make') == 0
            native_output = get_output('%s main.py' % (sys.executable, ))
            if sys.platform == 'win32':
                ext = '.pyd'
            else:
                ext = '.so'
            assert os.system('rm %s' % (extmod + ext)) == 0
            cpython_output = get_output('%s main.py' % (sys.executable, ))
            if native_output != cpython_output:
                print('diff:')
                print(generate_diff(native_output, cpython_output))
                raise AssertionError
            print('*** success:', test)
        except AssertionError:
            print('*** failure:', test)
            failures.append(test)
        os.chdir('..')
    return failures


def error_tests(args, options):
    failures = []
    os.chdir('errs')
    tests = sorted([int(t[:-3]) for t in glob.glob('*.py') if t[:-3].isdigit()])
    for test in tests:
        print('*** test:', test)
        try:
            checks = []
            for line in file('%d.py' % test):
                if line.startswith('#*'):
                    checks.append(line[1:].strip())
            output = get_output('%s %s %d 2>&1' % (sys.executable, SS, test))
            assert not [l for l in output if 'Traceback' in l]
            for check in checks:
                print(check)
                assert [l for l in output if l.startswith(check)]
            print('*** success:', test)
        except AssertionError:
            print('*** failure:', test)
            failures.append(test)
    os.chdir('..')
    return failures


def get_output(command):
    com = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout
    output = com.readlines()
    com.close()
    return output


def check_output(command, command2):
    native_output = get_output(command)
    cpython_output = get_output(command2)
    if native_output != cpython_output:
        print('diff:')
        print(generate_diff(native_output, cpython_output))
        raise AssertionError


def generate_diff(native_output, cpython_output):
    return ''.join(unified_diff(native_output, cpython_output, lineterm="\n"))

if __name__ == '__main__':
    main()
