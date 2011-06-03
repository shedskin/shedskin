#!/usr/bin/python
import sys, os

release = 'shedskin-%s' % sys.argv[1]
os.system('rm -R shedskin-%s' % sys.argv[1])
os.system('mkdir %s' % release)

for file in ['doc/LICENSE', 'doc/README.html', 'setup.py']:
    os.system('cp %s %s' % (file, release))

for directory in ['shedskin', 'tests', 'examples']:
    os.system('rm %s -R' % directory)
    os.system('git checkout %s' % directory)
    os.system('cp -R %s %s' % (directory, release))

os.system('mkdir %s/scripts' % release)
os.system('cp scripts/shedskin %s/scripts' % release)

os.system("echo print \\'hello, world!\\' > %s/test.py" % release)

os.system('tar zcf %s.tgz %s' % (release, release))
os.system('rm -R shedskin-%s' % sys.argv[1])
