
class huhuhu:
    pass

obj = huhuhu()
if obj is obj:
    print 'ok1'
if obj is not None:
    print 'ok2'

obj = None
if obj is None:
    print 'ok3'
if obj == None:
    print 'ok4'
if obj is not None:
    print 'bad'
if obj != None:
    print 'bad'

if not obj:
    print 'ok5'

bla = "hoei"
if bla == 'hoei':
    print 'ok6'
if bla is 'hoei':
    print 'ok7'
if bla != 'meuk':
    print 'ok8'
if bla is not 'meuk':
    print 'ok9'

