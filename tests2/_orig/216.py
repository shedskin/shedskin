# configparser # XXX readfp

import configparser

config = configparser.ConfigParser(defaults={'aha': 'hah'})

config.read("testdata/test.conf")

print(config.getint('ematter', 'pages'), config.getfloat('ematter', 'pages'))
print(int(config.getboolean('ematter', 'hop')))

print(int(config.has_section('ematteu')))
config.add_section('meuk')
config.set('meuk', 'submeuk1', 'oi')
config.set('meuk', 'submeuk2', 'bwah')
if config.has_section('meuk') and config.has_option('meuk', 'submeuk1'):
    config.remove_option('meuk', 'submeuk1')
config.add_section('bagger')
config.remove_section('bagger')

# dump entire config file
for section in sorted(config.sections()):
    print(section)
    for option in sorted(config.options(section)):
        print(" ", option, "=", config.get(section, option))

print(config.get('ematter', 'pages', vars={'var': 'blah'}))

fl = open('testdata/test.ini', 'w')
config.write(fl)
fl.close()
print(sorted(open('testdata/test.ini').readlines()))

print(list(config.defaults().items()))
print(sorted(config.items('ematter', vars={'var': 'blah'})))

rcp = configparser.RawConfigParser()
rcp.read(["testdata/test.conf"])

print(rcp.get('ematter', 'pages')) #, vars={'var': 'blah'})
print(sorted(rcp.items('ematter')))

# ConfigParser.items model
p = configparser.ConfigParser()
p.read("testdata/symbols.INI")
for entry in p.items("symbols"):
    print(entry)
itemz = p.defaults().items()
print(list(itemz))
sections = p.sections()
print(sections)
