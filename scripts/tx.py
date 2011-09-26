import sys, os, random
random.seed(328497)

total = 199
parts, part = map(int, sys.argv[1:3])
extra = ''
if len(sys.argv) == 4:
    extra = sys.argv[3]

alles = range(total)
random.shuffle(alles)

tests = alles[part::parts]

os.system('rm -fR tx%d' % part)
os.system('mkdir tx%d' % part)
os.system('cp -R tests tx%d' % part)

os.system('cd tx%d/tests; time python run.py %s -f -l %s' % (part, extra, ' '.join(map(str, tests))))
