# configparser # XXX readfp not covered yet

import os
import re
import configparser

if os.path.exists("testdata"):
    testdata = "testdata"
elif os.path.exists("../testdata"):
    testdata = "../testdata"
else:
    testdata = "../../testdata"
datafile = os.path.join(testdata, 'configparser_test.conf')
writefile = os.path.join(testdata, 'configparser_write_test.ini')

def test_minimal():
    config = configparser.ConfigParser(defaults={'aha': 'hah'})
    config.read(datafile)
    assert config
    assert config.getint('ematter', 'pages') == 250

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
    assert not config.has_option('meuk', 'submeuk1')
    assert config.has_option('meuk', 'submeuk2')

    # dump entire config file
    dump = {}
    for section in sorted(config.sections()):
        dump[section] = []
        for option in sorted(config.options(section)):
            dump[section].append({option: config.get(section, option)})
    assert list(sorted(dump.keys())) == ['book', 'ematter', 'hardcopy', 'meuk']

    assert config.get('ematter', 'pages', vars={'var': 'blah'}) == '250'

def test_write_and_reread():
    config = configparser.ConfigParser()
    config.read(datafile)

    fl = open(writefile, 'w')
    config.write(fl)
    fl.close()

    reread = configparser.ConfigParser()
    reread.read(writefile)
    assert reread.getint('ematter', 'pages') == 250
    assert reread.get('book', 'author') == 'Fredrik Lundh'
    assert sorted(reread.sections()) == sorted(config.sections())

def test_rawconfigparser():
    rcp = configparser.RawConfigParser()
    rcp.read([datafile])

    assert rcp.get('ematter', 'pages') == '250'
    items = dict(rcp.items('ematter'))
    assert items['pages'] == '250'
    assert items['hop'] == 'True'

def test_defaults_section():
    config = configparser.ConfigParser(defaults={'shared': 'yes'})
    config.add_section('one')
    config.add_section('two')
    config.set('one', 'own', 'a')

    assert config.get('one', 'shared') == 'yes'
    assert config.get('two', 'shared') == 'yes'
    assert 'shared' in config.defaults()
    assert config.has_option('two', 'shared')
    assert not config.has_option('two', 'own')

def test_interpolation():
    config = configparser.ConfigParser()
    config.add_section('paths')
    config.set('paths', 'home_dir', '/home/user')
    config.set('paths', 'config_dir', '%(home_dir)s')

    assert config.get('paths', 'config_dir') == '/home/user'
    assert config.get('paths', 'config_dir', raw=True) == '%(home_dir)s'

def test_interpolation_bug():
    # KNOWN BUG: interpolation currently raises whenever the value
    # contains anything besides a single, bare %(name)s reference.
    # ConfigParser._KEYCRE ("%\\(([^)]*)\\)s|.") falls back to matching
    # any other character one at a time via the "." alternative, in
    # which case group 1 does not participate in the match. CPython's
    # re returns None for such a group; shedskin's match_object.group()
    # instead raises re.error("group is unmatched") (see re.cpp), which
    # ConfigParser._interpolate/_interpolation_replace don't handle.
    # This effectively breaks interpolation for any realistic value
    # (e.g. "%(home_dir)s/config"), not just contrived ones.
    config = configparser.ConfigParser()
    config.add_section('paths')
    config.set('paths', 'home_dir', '/home/user')
    config.set('paths', 'config_dir', '%(home_dir)s/config')

    ok = False
    try:
        config.get('paths', 'config_dir')
    except re.error:
        ok = True
    assert ok

def test_all():
    test_minimal()
    test_configparser()
    test_write_and_reread()
    test_rawconfigparser()
    test_defaults_section()
    test_interpolation()
#    test_interpolation_bug()

if __name__ == '__main__':
    test_all()
