# configparser

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

def test_items_all_sections():
    rcp = configparser.RawConfigParser()
    rcp.read([datafile])

    all_items = dict(rcp.items())
    assert sorted(all_items.keys()) == ['DEFAULT', 'book', 'ematter', 'hardcopy']
    assert all_items['ematter']['pages'] == '250'
    assert all_items['book']['author'] == 'Fredrik Lundh'

    config = configparser.ConfigParser()
    config.read([datafile])

    all_items2 = dict(config.items())
    assert sorted(all_items2.keys()) == ['DEFAULT', 'book', 'ematter', 'hardcopy']
    assert all_items2['hardcopy']['pages'] == '350'

def test_items_raw_and_vars():
    config = configparser.ConfigParser(defaults={'root': '/tmp'})
    config.add_section('a')
    config.set('a', 'x', '%(root)s/a')

    interpolated = dict(config.items('a'))
    assert interpolated['x'] == '/tmp/a'

    raw_items = dict(config.items('a', raw=True))
    assert raw_items['x'] == '%(root)s/a'

    var_items = dict(config.items('a', raw=False, vars={'root': '/override'}))
    assert var_items['x'] == '/override/a'

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
    except configparser.InterpolationMissingOptionError as e:
        ok = True
        # regression: reference used to be hardcoded to '' instead of the
        # actual missing key, and str(e)/repr(e) used to print "None" (or
        # segfault for repr) instead of the real message, because the
        # Error hierarchy's __init__-based message never reached
        # BaseException.args (see Error::__init__ in configparser.cpp).
        assert 'does_not_exist' in e.reference
        assert 'does_not_exist' in str(e)
        assert 'does_not_exist' in repr(e)
    assert ok

def test_error_str_and_repr():
    # regression: str()/repr() on ConfigParser exceptions used to always
    # print "None" (str) or segfault (repr) since BaseException.args was
    # never populated by these exceptions' message-setting __init__ chain.
    config = configparser.ConfigParser()

    ok = False
    try:
        config.get('no_such_section', 'opt')
    except configparser.NoSectionError as e:
        ok = True
        assert str(e) != 'None'
        assert 'no_such_section' in str(e)
        assert 'no_such_section' in repr(e)
    assert ok

    config.add_section('paths')
    ok = False
    try:
        config.get('paths', 'no_such_option')
    except configparser.NoOptionError as e:
        ok = True
        assert str(e) != 'None'
        assert 'no_such_option' in str(e)
    assert ok


def test_read_string():
    config = configparser.ConfigParser()
    config.read_string("[book]\ntitle: Dune\npages: 412\n")
    assert config.get('book', 'title') == 'Dune'
    assert config.getint('book', 'pages') == 412

def test_read_dict():
    config = configparser.ConfigParser()
    config.read_dict({'server': {'host': 'localhost', 'port': '8080'}})
    assert config.get('server', 'host') == 'localhost'
    assert config.getint('server', 'port') == 8080

    # a second read_dict() call extends an already-existing section
    # rather than clobbering it
    config.read_dict({'server': {'timeout': '30'}})
    assert config.getint('server', 'timeout') == 30
    assert config.get('server', 'host') == 'localhost'

def test_get_fallback():
    config = configparser.ConfigParser()
    config.add_section('a')
    config.set('a', 'x', '1')

    # missing option / missing section: fallback is returned instead of raising
    assert config.get('a', 'missing', fallback='default_val') == 'default_val'
    assert config.get('nosuch', 'x', fallback='default_val2') == 'default_val2'

    # a present option is returned normally; fallback is ignored
    assert config.get('a', 'x', fallback='unused') == '1'

    # omitting fallback still raises, as before
    ok = False
    try:
        config.get('a', 'missing')
    except configparser.NoOptionError:
        ok = True
    assert ok

def test_duplicate_section_error():
    config = configparser.ConfigParser()
    config.add_section('dup')
    ok = False
    try:
        config.add_section('dup')
    except configparser.DuplicateSectionError:
        ok = True
    assert ok

def test_duplicate_section_error_while_parsing():
    config = configparser.ConfigParser()
    ok = False
    try:
        config.read_string('[a]\nx = 1\n[a]\ny = 2\n')
    except configparser.DuplicateSectionError as e:
        ok = True
        assert e.section == 'a'
        assert e.source == '<string>'
        assert e.lineno == 3
    assert ok
    # re-reading the same section across *separate* read_string() calls
    # (rather than repeating the header within one source) is not an error
    config2 = configparser.ConfigParser()
    config2.read_string('[a]\nx = 1\n')
    config2.read_string('[a]\ny = 2\n')
    assert config2.get('a', 'x') == '1'
    assert config2.get('a', 'y') == '2'

def test_duplicate_option_error():
    config = configparser.ConfigParser()
    ok = False
    try:
        config.read_string('[a]\nx = 1\nx = 2\n')
    except configparser.DuplicateOptionError as e:
        ok = True
        assert e.section == 'a'
        assert e.option == 'x'
        assert e.source == '<string>'
        assert e.lineno == 3
    assert ok

def test_default_section_param():
    config = configparser.ConfigParser(default_section='COMMON')
    config.read_string('[COMMON]\nroot = /tmp\n[a]\nx = %(root)s/a\n')
    assert config.get('a', 'x') == '/tmp/a'
    assert 'COMMON' not in config.sections()

def test_read_file():
    config = configparser.ConfigParser()
    f = open(datafile)
    config.read_file(f)
    f.close()
    assert config.getint('ematter', 'pages') == 250

def test_missing_section_header_error():
    config = configparser.ConfigParser()
    ok = False
    try:
        config.read_string('no_section_here: value\n')
    except configparser.MissingSectionHeaderError:
        ok = True
    assert ok

def test_parsing_error():
    config = configparser.ConfigParser()
    ok = False
    try:
        config.read_string('[a]\nthis is not valid\n')
    except configparser.ParsingError:
        ok = True
    assert ok

def test_mapping_section_access():
    config = configparser.ConfigParser(defaults={'shared': 'yes'})
    config.add_section('a')
    config.set('a', 'x', '1')

    # SectionProxy: config['section']['option']
    section = config['a']
    assert section['x'] == '1'
    # falls back to DEFAULT, like get()/has_option() do
    assert section['shared'] == 'yes'
    assert 'x' in section
    assert 'nope' not in section
    assert sorted(section) == ['shared', 'x']
    assert len(section) == 2

    ok = False
    try:
        section['missing']
    except KeyError:
        ok = True
    assert ok

    # write-through: mutating via the proxy mutates the parser
    section['y'] = '2'
    assert config.get('a', 'y') == '2'

    del section['y']
    assert not config.has_option('a', 'y')
    ok = False
    try:
        del section['y']
    except KeyError:
        ok = True
    assert ok

    # interpolation still applies through the proxy (get() is virtual)
    config.set('a', 'z', '%(x)s-suffix')
    assert config['a']['z'] == '1-suffix'

    # DEFAULT section is itself accessible as a proxy
    assert config[config.default_section]['shared'] == 'yes'

def test_mapping_parser_access():
    config = configparser.ConfigParser()
    config.add_section('a')
    config.add_section('b')

    assert 'a' in config
    assert 'nosuch' not in config
    assert config.default_section in config
    assert len(config) == 3  # a, b, DEFAULT
    assert sorted(config) == sorted([config.default_section, 'a', 'b'])

    ok = False
    try:
        config['nosuch']
    except KeyError:
        ok = True
    assert ok

    config['c'] = {'k': 'v'}
    assert config.get('c', 'k') == 'v'

    del config['c']
    assert not config.has_section('c')
    ok = False
    try:
        del config['nosuch']
    except KeyError:
        ok = True
    assert ok

    ok = False
    try:
        del config[config.default_section]
    except ValueError:
        ok = True
    assert ok

def test_items_interpolation_through_proxy():
    # regression: items() (the no-section overload) used to hand back
    # plain dicts straight from _defaults/_sections, so a ConfigParser's
    # interpolation was silently skipped when reached via items(). Now
    # it returns SectionProxy objects, which go through the (virtual)
    # get() and interpolate correctly, same as config[section][option].
    config = configparser.ConfigParser()
    config.add_section('paths')
    config.set('paths', 'home_dir', '/home/user')
    config.set('paths', 'my_dir', '%(home_dir)s/mine')

    all_items = dict(config.items())
    assert all_items['paths']['my_dir'] == '/home/user/mine'
    # raw access is unaffected
    assert config.get('paths', 'my_dir', raw=True) == '%(home_dir)s/mine'

    # write-through still holds via items() too, not just __getitem__
    all_items['paths']['extra'] = 'added'
    assert config.get('paths', 'extra') == 'added'

def test_getboolean_invalid():
    config = configparser.ConfigParser()
    config.add_section('b')
    config.set('b', 'flag', 'not_a_bool')
    ok = False
    try:
        config.getboolean('b', 'flag')
    except ValueError:
        ok = True
    assert ok

def test_all():
    test_minimal()
    test_configparser()
    test_write_and_reread()
    test_rawconfigparser()
    test_items_all_sections()
    test_items_raw_and_vars()
    test_defaults_section()
    test_interpolation()
    test_error_str_and_repr()
    test_read_string()
    test_read_dict()
    test_get_fallback()
    test_duplicate_section_error()
    test_duplicate_section_error_while_parsing()
    test_duplicate_option_error()
    test_default_section_param()
    test_mapping_section_access()
    test_mapping_parser_access()
    test_items_interpolation_through_proxy()
    test_read_file()
    test_missing_section_header_error()
    test_parsing_error()
    test_getboolean_invalid()

if __name__ == '__main__':
    test_all()
    print("ALL OK")
