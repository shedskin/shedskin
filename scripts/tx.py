import sys, os, random
random.seed(1666008) # 1666008

total = 193
parts, part = map(int, sys.argv[1:])

alles = range(total)
random.shuffle(alles)

tests = alles[part::parts]

os.system('rm -fR tx%d' % part)
os.system('mkdir tx%d' % part)
os.system('cp -R testdata tx%d' % part)
os.system('cp -R shedskin tx%d' % part)
os.system('cp unit.py tx%d' % part)
os.system('cp FLAGS tx%d/shedskin' % part)

os.system('cd tx%d; python unit.py -f -l %s' % (part, ' '.join(map(str, tests))))
