#!/usr/bin/python
import sys, os

release = 'shedskin-%s' % sys.argv[1]
os.system('rm -R shedskin-%s' % sys.argv[1])
os.system('mkdir %s' % release)

for file in ['doc/LICENSE', 'doc/README.html', 'setup.py']:
    os.system('cp %s %s' % (file, release))

os.system('mkdir %s/shedskin' % release)
os.system('mkdir %s/shedskin/lib' % release)
os.system('mkdir %s/shedskin/lib/os' % release)

os.system('rm shedskin/lib/struct* shedskin/lib/pygame* shedskin/lib/serial* shedskin/lib/array*')

os.system('cp shedskin/lib/*.py %s/shedskin/lib' % release)
os.system('cp shedskin/lib/*.?pp %s/shedskin/lib' % release)
os.system('cp shedskin/lib/os/*.py %s/shedskin/lib/os' % release)
os.system('cp shedskin/lib/os/*.?pp %s/shedskin/lib/os' % release)
os.system('cp shedskin/*.py %s/shedskin' % release)
os.system('cp shedskin/FLAGS %s/shedskin' % release)

os.system("echo print \\'hello, world!\\' > %s/test.py" % release)

os.system('tar zcf %s.tgz %s' % (release, release))
os.system('rm -R shedskin-%s' % sys.argv[1])
