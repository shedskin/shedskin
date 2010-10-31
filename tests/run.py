#!/usr/bin/env python
import traceback, sys, os, time, subprocess, glob, getopt

def usage():
    print "'-l': give individual test numbers"
    print "'-r': reverse test order"
    print "'-f': break after first failure"
    print "'-e': run extension module tests"
    print "'-x': run error/warning message tests"
    sys.exit()

def parse_options():
    args, options = [], set()
    for arg in sys.argv[1:]:
        if arg.startswith('-'):
            options.update(arg[1:])
        else: 
            args.append(int(arg))
    return args, options

def test_numbers(args, options):
    if 'l' in options:
        test_nrs = args

    elif len(args) == 1:
        test_nrs = [args[0]]
    elif len(args) == 2:
        if args[0] > args[1]:
            args[0], args[1] = args[1], args[0]
            options.add('r')
        test_nrs = range(args[0],args[1])
    else:
        test_nrs = sorted([int(os.path.splitext(f)[0]) for f in glob.glob('*.py') if f != 'run.py'])

    if 'r' in options:
        test_nrs.reverse()

    return test_nrs

def tests(args, options):
    test_nrs = test_numbers(args, options)
    msvc = 'v' in options

    failures = []
    for test_nr in test_nrs:
        if os.path.exists('%d.py' % test_nr): # XXX
            run_test(test_nr, failures, msvc)
            if failures and 'f' in options:
                break
            print

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
        print '*** no failures, yay!'
    else:
        print '*** tests failed:', len(failures)
        print failures

def run_test(test_nr, failures, msvc):
    try:
        print '*** test:', test_nr
        if msvc: 
            assert os.system('shedskin -v %d' % test_nr) == 0
        else:
            assert os.system('shedskin -m Makefile.%d %d' % (test_nr, test_nr)) == 0
        if msvc:
            assert os.system('nmake /C /S clean') == 0
            assert os.system('nmake /C /S') == 0
            command = '.\\%d' % test_nr
        else:
            assert os.system('make clean -f Makefile.%d; make -f Makefile.%d' % (test_nr, test_nr)) == 0
            command = './%d' % test_nr
        check_output(command, 'python %d.py' % test_nr)
        print '*** success:', test_nr
    except AssertionError:
        print '*** failure:', test_nr
        traceback.print_exc()
        failures.append(test_nr)

def extmod_tests(args, options):
    failures = []
    for test in glob.glob('e*'):
        if test == 'errs':
            continue
        print '*** test:', test
        os.chdir(test)
        try:
            extmod = file('main.py').next()[1:].strip()
            assert os.system('shedskin -e %s' % extmod) == 0
            assert os.system('make') == 0
            native_output = get_output('python main.py')
            assert os.system('rm %s.so' % extmod) == 0
            cpython_output = get_output('python main.py')
            if native_output != cpython_output:
                print 'output:'
                print native_output
                print 'expected:'
                print cpython_output
                raise AssertionError
            print '*** success:', test
        except AssertionError:
            print '*** failure:', test
            failures.append(test)
        os.chdir('..')
    return failures

def error_tests(args, options):
    failures = []
    os.chdir('errs')
    for test in glob.glob('*.py'):
        if not test[:-3].isdigit():
            continue
        print '*** test:', test
        try:
            checks = []
            for line in file(test):
                if line.startswith('#*'):
                    checks.append(line[1:].strip())
            output = get_output('shedskin %s 2>&1' % test).splitlines()
            assert not [l for l in output if 'Traceback' in l]
            for check in checks:
                assert [l for l in output if l.startswith(check)]
            print '*** success:', test
        except AssertionError:
            print '*** failure:', test
            failures.append(test)
    os.chdir('..')
    return failures

def get_output(command):
    com = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout
    output = ''.join(com.readlines())
    com.close()
    return output

def check_output(command, command2):
    native_output = get_output(command)
    cpython_output = get_output(command2)
    if native_output != cpython_output:
        print 'output:'
        print native_output
        print 'expected:'
        print cpython_output
        raise AssertionError

if __name__ == '__main__':
    main()
