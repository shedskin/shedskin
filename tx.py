import sys, os

total = 181
parts, part = map(int, sys.argv[1:])

tests = range(total)[part::parts]

os.system('rm -fR tx%d' % part)
os.system('mkdir tx%d' % part)
os.system('cp -R lib tx%d' % part)
os.system('cp -R testdata tx%d' % part)
os.system('cp *.py tx%d' % part)
os.system('cp FLAGS tx%d' % part)

os.system('cd tx%d; python unit.py -f -l %s' % ' '.join(map(str, tests)))
