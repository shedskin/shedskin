import leak
print leak.__file__

p = leak.Point()
while True:
    p.x
    
