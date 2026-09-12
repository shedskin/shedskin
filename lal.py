import io

s = open('test.py')

s = io.StringIO('hoepa bfloep\nblap')

print(s.readline())
print(s.readline())
