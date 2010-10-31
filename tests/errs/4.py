try:
    pass
except KeyboardInterrupt:
    print 'uhw'

l = [lambda x,y: (y,x)]
print l.pop()(1,2)

#*WARNING* 4.py:3: system 'KeyboardInterrupt' is not caught
#*WARNING* 4.py:6: 'list' instance containing function reference
