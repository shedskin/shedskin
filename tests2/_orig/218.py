# files

# MAC
with open('cr.txt', 'w') as f1:
    f1.write('hello world\r')
    f1.write('bye\r')
with open('cr.txt', 'r') as f1:
    for line in f1:
        print(line,)
print('---')
with open('cr.txt', 'r') as f1:
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
with open('lf.txt', 'r') as f1:
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
with open('crlf.txt', 'r') as f1:
    for line in f1:
        print('%r' % line,)
print('===')

# next
print(next(open('run.py')).strip())

# io.BytesIO, file.seek
import io, sys

sio = io.BytesIO(open('testdata/hopsakee', 'rb').read())
print(sio.readlines())

sio = io.BytesIO(b'blaat')
sio.seek(-3, 2)
print(sio.read())

sio = io.BytesIO()
print(sio.tell())
sio.write(b'hallo\njoh')
print(sio.tell())
sio.seek(0, 0)
print(sio.tell())
print(sio.readlines())
print(sio.tell())
sio.seek(0, 0)
print(sio.tell())
sio.write(b'hoi')
print(sio.tell())
print(sio.readlines())
print(sio.tell())

# --- end-of-file problem
print([line for line in open('testdata/scene.txt') if line.startswith('material')])
