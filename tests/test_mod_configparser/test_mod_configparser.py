# configparser # XXX readfp

import os
import configparser

if os.path.exists("testdata"):
    testdata = "testdata"
elif os.path.exists("../testdata"):
    testdata = "../testdata"
else:
    testdata = "../../testdata"
datafile = os.path.join(testdata, 'configparser_test.conf')

def test_minimal():
    config = configparser.ConfigParser(defaults={'aha': 'hah'})
    config.read(datafile)
    assert config
    # assert config.getint('ematter', 'pages') == 250 ## FIXME this fails

def test_configparser():
    config = configparser.ConfigParser()
    config.read(datafile)

    assert config.getint('ematter', 'pages') == 250
    assert config.getfloat('ematter', 'pages') == 250.0
    assert int(config.getboolean('ematter', 'hop')) == 1

    assert int(config.has_section('ematteu')) == 0

    config.add_section('meuk')
    config.set('meuk', 'submeuk1', 'oi')
    config.set('meuk', 'submeuk2', 'bwah')
    if config.has_section('meuk') and config.has_option('meuk', 'submeuk1'):
        config.remove_option('meuk', 'submeuk1')
    config.add_section('bagger')
    config.remove_section('bagger')

    assert not config.has_section('bagger')

    # # dump entire config file
    # dump = {}
    # for section in sorted(config.sections()):
    #     dump[section] = []
    #     for option in sorted(config.options(section)):
    #         dump[section].append({option: config.get(section, option)})
    # assert list(sorted(dump.keys())) == ['book', 'ematter', 'hardcopy', 'meuk']

    # assert config.get('ematter', 'pages', vars={'var': 'blah'}) == '250'

    # fl = open('testdata/configparser_test.ini', 'w')
    # config.write(fl)
    # fl.close()
    # print(sorted(open('testdata/configparser_test.ini').readlines()))

    # print(list(config.defaults().items()))
    # print(sorted(config.items('ematter', vars={'var': 'blah'})))

    # rcp = configparser.RawConfigParser()
    # rcp.read([datafile])

    # print(rcp.get('ematter', 'pages')) #, vars={'var': 'blah'})
    # print(sorted(rcp.items('ematter')))

    # # ConfigParser.items model
    # p = configparser.ConfigParser()
    # p.read("testdata/symbols.INI")
    # for entry in p.items("symbols"):
    #     print(entry)
    # itemz = p.defaults().items()
    # print(list(itemz))
    # sections = p.sections()
    # print(sections)




def test_all():
    test_minimal()
    test_configparser()


if __name__ == '__main__':
    test_all()


