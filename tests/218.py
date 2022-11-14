# files

# open('U')
# MAC
with open('cr.txt', 'w') as f1:
    f1.write('hello world\r')
    f1.write('bye\r')
with open('cr.txt', 'r') as f1:
    for line in f1:
        print(line,)
print('---')
with open('cr.txt', 'rU') as f1:
    for line in f1:
        print(line,)
print('===')

# UNIX
with open('lf.txt', 'w') as f1:
    f1.write('hello world\n')
    f1.write('bye\n')
with open('lf.txt', 'r') as f1:
    for line in f1:
        print(line,)
print('---')
with open('lf.txt', 'rU') as f1:
    for line in f1:
        print(line,)
print('===')

##  DOS
with open('crlf.txt', 'w') as f1:
    f1.write('hello world\r\n')
    f1.write('bye\r\n')
    f1.write('foo\r')
    f1.write('bar\n')
    f1.write('baz\r\n')
    f1.write('qux')
with open('crlf.txt', 'r') as f1:
    for line in f1:
        print('%r' % line,)
print('---')
with open('crlf.txt', 'rU') as f1:
    for line in f1:
        print('%r' % line,)
print('===')

# next
print(next(open('run.py')).strip())

# cStringIO.StringIO, file.seek
import cStringIO, sys

sio = cStringIO.StringIO(open('testdata/hopsakee').read())
print(sio.readlines())

sio = cStringIO.StringIO('blaat')
sio.seek(-3, 2)
print(sio.read())

sio = cStringIO.StringIO()
print(sio.tell())
sio.write('hallo\njoh')
print(sio.tell())
sio.seek(0, 0)
print(sio.tell())
print(sio.readlines())
print(sio.tell())
sio.seek(0, 0)
print(sio.tell())
sio.write('hoi')
print(sio.tell())
print(sio.readlines())
print(sio.tell())
