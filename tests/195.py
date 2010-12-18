# !$!#$
try:
    [].pop(-1)
except IndexError:
    print 'kan niet poppen'
try:
    [].remove(0)
except ValueError:
    print 'kan niet vinden'
