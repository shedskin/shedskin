#!/usr/bin/python
import sys, os

release = 'shedskin-%s' % sys.argv[1]

files = ['doc/LICENSE', 'doc/README.html', 'FLAGS', 'ss.py', 'setup.py', 'bert.py', 'unit.py', 'shared.py', 'graph.py', 'cpp.py', 'infer.py', 'backward.py']

os.system('mkdir %s' % release)
os.system('mkdir %s/lib' % release)
os.system('mkdir %s/lib/os' % release)
os.system('mkdir %s/testdata' % release)
os.system('mkdir %s/testdata/crap2' % release)

for file in files:
    os.system('cp %s %s' % (file, release))

os.system('cp testdata/* %s/testdata' % release)
os.system('cp testdata/crap2/* %s/testdata/crap2' % release)
os.system('cp lib/* %s/lib' % release)
os.system('cp lib/os/* %s/lib/os' % release)

os.system("echo print \\'hello, world!\\' > %s/test.py" % release)

os.system('tar zcf %s.tgz %s' % (release, release))

os.system('rm blap -R; mkdir blap')
os.chdir('blap')
os.system('tar zxf ../%s.tgz' % release)
os.chdir(release)
os.system('python unit.py -rf') 


