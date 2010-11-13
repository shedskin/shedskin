import sys, os, random
random.seed(1435440)

total = 195
parts, part = map(int, sys.argv[1:])

alles = range(total)
random.shuffle(alles)

tests = alles[part::parts]

os.system('rm -fR tx%d' % part)
os.system('mkdir tx%d' % part)
os.system('cp -R tests tx%d' % part)

os.system('cd tx%d/tests; python run.py -f -l %s' % (part, ' '.join(map(str, tests))))
