# configparser # XXX readfp not covered yet

import os
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
    config.set('paths', 'my_dir', '%(home_dir)s/mine')
    config.set('paths', 'both', 'prefix-%(home_dir)s-mid-%(my_dir)s-suffix')
    config.set('paths', 'no_ref', 'just a plain value')
    # a literal '%' has to be doubled to survive interpolation, but only
    # once the value also contains a real "%(...)s" reference somewhere
    # -- ConfigParser._interpolate only runs its %-substitution pass at
    # all when "%(" appears in the value (this mirrors old ConfigParser,
    # not modern configparser's BasicInterpolation).
    config.set('paths', 'mixed_percent', '%(home_dir)s has 100%% capacity')

    assert config.get('paths', 'home_dir') == '/home/user'
    assert config.get('paths', 'my_dir') == '/home/user/mine'
    assert config.get('paths', 'both') == 'prefix-/home/user-mid-/home/user/mine-suffix'
    assert config.get('paths', 'no_ref') == 'just a plain value'
    assert config.get('paths', 'mixed_percent') == '/home/user has 100% capacity'

    # raw bypasses interpolation entirely
    assert config.get('paths', 'both', raw=True) == 'prefix-%(home_dir)s-mid-%(my_dir)s-suffix'

    # a reference to a name that doesn't exist anywhere -> InterpolationMissingOptionError
    config.set('paths', 'bad_ref', '%(does_not_exist)s')
    ok = False
    try:
        config.get('paths', 'bad_ref')
    except configparser.InterpolationMissingOptionError:
        ok = True
    assert ok

def test_all():
    test_minimal()
    test_configparser()
    test_write_and_reread()
    test_rawconfigparser()
    test_defaults_section()
    test_interpolation()

if __name__ == '__main__':
    test_all()
    print("ALL OK")
