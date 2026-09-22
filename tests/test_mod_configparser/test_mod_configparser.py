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
    # a literal '%' has to be doubled to survive interpolation (matching
    # modern configparser's BasicInterpolation: a bare '%' that is not
    # part of '%%' or '%(name)s' raises InterpolationSyntaxError)
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

def test_no_inline_comments():
    # CPython 3 has inline_comment_prefixes=None by default, so ';' and '#'
    # inside a value are data, not the start of a comment (python 2 stripped
    # ' ;'-comments here). Full-line comments are still comments.
    config = configparser.ConfigParser()
    config.read_string(
        "[a]\n"
        "; a real comment\n"
        "url = http://host/?x=1 ; y=2\n"
        "hash = red #ff0000\n"
        "semi = a;b\n"
        "tail = value ;\n"
    )
    assert config.get('a', 'url') == 'http://host/?x=1 ; y=2'
    assert config.get('a', 'hash') == 'red #ff0000'
    assert config.get('a', 'semi') == 'a;b'
    assert config.get('a', 'tail') == 'value ;'
    assert sorted(config.options('a')) == ['hash', 'semi', 'tail', 'url']

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

def test_add_default_section_error():
    # CPython's _validate_section_name: adding the default section used to be
    # accepted, which then made sections() (documented as excluding [DEFAULT])
    # return it
    config = configparser.ConfigParser()
    error = ''
    try:
        config.add_section('DEFAULT')
    except ValueError as e:
        error = str(e)
    assert error == "Invalid section name: 'DEFAULT'"
    assert config.sections() == []
    config.add_section('other')
    assert config.sections() == ['other']

    # ..and it follows a custom default_section
    config2 = configparser.ConfigParser(default_section='mydef')
    error = ''
    try:
        config2.add_section('mydef')
    except ValueError as e:
        error = str(e)
    assert error == "Invalid section name: 'mydef'"
    assert config2.sections() == []
    config2.add_section('DEFAULT')
    assert config2.sections() == ['DEFAULT']

    # read_dict still routes the default section to the defaults
    config3 = configparser.ConfigParser()
    config3.read_dict({'DEFAULT': {'a': '1'}, 's': {'b': '2'}})
    assert config3.sections() == ['s']
    assert config3.get('s', 'a') == '1'


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

def test_error_attribute_types():
    # exercise exception attributes as real strings/ints, so that untyped
    # attributes fail to compile (see shedskin/lib/configparser.py)
    config = configparser.ConfigParser()
    try:
        config.read_string('[a]\nx = 1\n[a]\ny = 2\n')
    except configparser.DuplicateSectionError as e:
        assert e.section.upper() == 'A'
        assert e.source.strip() == '<string>'
        assert e.lineno + 1 == 4
        assert len(e.message) > 0

    config2 = configparser.ConfigParser()
    try:
        config2.read_string('[a]\nx = 1\nx = 2\n')
    except configparser.DuplicateOptionError as e2:
        assert e2.section.upper() == 'A'
        assert e2.option.upper() == 'X'
        assert e2.source.strip() == '<string>'
        assert e2.lineno + 1 == 4

    config3 = configparser.ConfigParser()
    try:
        config3.get('nope', 'x')
    except configparser.NoSectionError as e3:
        assert e3.section.upper() == 'NOPE'
        assert 'nope' in e3.message

    config4 = configparser.ConfigParser()
    config4.read_string('[p]\nx = 1\n')
    try:
        config4.get('p', 'nope')
    except configparser.NoOptionError as e4:
        assert e4.option.upper() == 'NOPE'
        assert e4.section.upper() == 'P'

    config5 = configparser.ConfigParser()
    config5.read_string('[p]\na = %(b)s\n')
    try:
        config5.get('p', 'a')
    except configparser.InterpolationMissingOptionError as e5:
        assert e5.reference.upper() == 'B'
        assert e5.option.upper() == 'A'
        assert e5.section.upper() == 'P'

    config6 = configparser.ConfigParser()
    try:
        config6.read_string('x = 1\n')
    except configparser.MissingSectionHeaderError as e6:
        assert e6.lineno + 1 == 2
        assert e6.line.strip() == 'x = 1'


def test_typed_getters_fallback():
    config = configparser.ConfigParser()
    config.read_string('[a]\nx = 42\nf = 2.5\nb = yes\nbad = notanumber\n')

    # missing option / missing section: fallback is returned instead of raising
    assert config.getint('a', 'missing', fallback=7) == 7
    assert config.getint('nosuch', 'x', fallback=-1) == -1
    assert config.getfloat('a', 'missing', fallback=1.5) == 1.5
    assert config.getboolean('a', 'missing', fallback=True) == True
    assert config.getboolean('a', 'missing', fallback=False) == False

    # a present option is returned normally; fallback is ignored
    assert config.getint('a', 'x', fallback=0) == 42
    assert config.getfloat('a', 'f', fallback=0.0) == 2.5
    assert config.getboolean('a', 'b', fallback=False) == True

    # fallback only covers a *missing* option: a present but unconvertible
    # value still raises ValueError, same as cpython
    ok = False
    try:
        config.getint('a', 'bad', fallback=0)
    except ValueError:
        ok = True
    assert ok

    # omitting fallback still raises, as before
    ok = False
    try:
        config.getint('a', 'missing')
    except configparser.NoOptionError:
        ok = True
    assert ok
    ok = False
    try:
        config.getfloat('nosuch', 'x')
    except configparser.NoSectionError:
        ok = True
    assert ok

    # raw= / vars= are honored, as for get()
    config.set('a', 'y', '%(x)s0')
    assert config.getint('a', 'y') == 420
    assert config.get('a', 'y', raw=True) == '%(x)s0'
    assert config.getint('a', 'z', vars={'z': '9'}) == 9


def test_section_proxy_name_parser_repr():
    config = configparser.ConfigParser()
    config.read_string('[sect]\nx = 1\n')
    proxy = config['sect']
    assert proxy.name == 'sect'
    assert repr(proxy) == '<Section: sect>'
    assert repr(config['DEFAULT']) == '<Section: DEFAULT>'

    # .parser is the live parser the proxy writes through to
    proxy.parser.set('sect', 'x', '2')
    assert proxy['x'] == '2'
    assert proxy.parser.get('sect', 'x') == '2'


def test_section_proxy_get():
    config = configparser.ConfigParser()
    config.read_string('[DEFAULT]\nd = dflt\n[sect]\nx = 1\ny = %(x)s0\n')
    proxy = config['sect']

    assert proxy.get('x') == '1'
    # falls back to the DEFAULT section, like __getitem__
    assert proxy.get('d') == 'dflt'
    # unlike the parser's get(), a missing option returns None / the fallback
    # rather than raising
    assert proxy.get('missing') is None
    assert proxy.get('missing', 'fb') == 'fb'
    assert proxy.get('missing', fallback='fb2') == 'fb2'
    # interpolation goes through the parser, raw= disables it
    assert proxy.get('y') == '10'
    assert proxy.get('y', raw=True) == '%(x)s0'
    assert proxy.get('z', vars={'z': 'vz'}) == 'vz'


def test_section_proxy_typed_getters():
    config = configparser.ConfigParser()
    config.read_string('[sect]\nx = 42\nf = 2.5\nb = off\n')
    proxy = config['sect']

    assert proxy.getint('x') == 42
    assert proxy.getfloat('f') == 2.5
    assert proxy.getboolean('b') == False

    assert proxy.getint('missing', 7) == 7
    assert proxy.getint('missing', fallback=8) == 8
    assert proxy.getfloat('missing', fallback=0.5) == 0.5
    assert proxy.getboolean('missing', fallback=True) == True

    # present value wins over the fallback
    assert proxy.getint('x', 0) == 42

    # (not tested: cpython returns None when no fallback is given and the
    # option is missing; shedskin cannot return an optional int, so it raises
    # NoOptionError there, as the parser-level getters do)


def test_parsing_error_append():
    e = configparser.ParsingError('some.ini')
    e.append(3, 'bad line 3')
    e.append(7, 'bad line 7')
    assert e.errors == [(3, 'bad line 3'), (7, 'bad line 7')]


def test_parsing_error_combine():
    e1 = configparser.ParsingError('a.ini')
    e1.append(1, 'one')
    e2 = configparser.ParsingError('b.ini')
    e2.append(2, 'two')
    e2.append(3, 'three')
    e3 = configparser.ParsingError('c.ini')
    e3.append(4, 'four')
    combined = e1.combine([e2, e3])
    assert combined is e1
    assert e1.errors == [(1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')]
    assert 'two' in e1.message and 'four' in e1.message
    # the donors are unchanged
    assert e2.errors == [(2, 'two'), (3, 'three')]


def test_popitem():
    config = configparser.ConfigParser()
    config.read_string('[DEFAULT]\nd = 1\n[s1]\nx = a\n[s2]\ny = b\n')
    # note: CPython pops the *first* section in insertion order; shedskin
    # dicts are not insertion-ordered, so only check the popped set here
    name1, proxy1 = config.popitem()
    assert proxy1.name == name1
    name2, proxy2 = config.popitem()
    assert sorted([name1, name2]) == ['s1', 's2']
    # the default section is never popped
    assert config.sections() == []
    assert config.defaults()['d'] == '1'
    ok = False
    try:
        config.popitem()
    except KeyError:
        ok = True
    assert ok


def test_interpolation_kwarg():
    # dummy Interpolation() passes values through untouched, even on a
    # ConfigParser; BasicInterpolation() enables %-expansion, even on a
    # RawConfigParser
    config = configparser.ConfigParser(interpolation=configparser.Interpolation())
    config.read_string('[p]\nhome = /home/user\nmy = %(home)s/mine\n')
    assert config.get('p', 'my') == '%(home)s/mine'

    config2 = configparser.RawConfigParser(interpolation=configparser.BasicInterpolation())
    config2.read_string('[p]\nhome = /home/user\nmy = %(home)s/mine\n')
    assert config2.get('p', 'my') == '/home/user/mine'
    assert config2.get('p', 'my', raw=True) == '%(home)s/mine'


def test_extended_interpolation():
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read_string('[DEFAULT]\nroot = /opt\n'
                       '[common]\nprefix = ${root}/app\n'
                       '[paths]\nbin = ${common:prefix}/bin\n'
                       'both = ${bin} and ${common:prefix}\n'
                       'money = 100$$\n')
    assert config.get('common', 'prefix') == '/opt/app'
    # cross-section reference, recursing through another section
    assert config.get('paths', 'bin') == '/opt/app/bin'
    assert config.get('paths', 'both') == '/opt/app/bin and /opt/app'
    # '$$' is an escaped dollar sign
    assert config.get('paths', 'money') == '100$'
    # raw bypasses interpolation
    assert config.get('paths', 'bin', raw=True) == '${common:prefix}/bin'
    # through the mapping protocol / SectionProxy too
    assert config['paths']['bin'] == '/opt/app/bin'
    # items() interpolates as well
    assert dict(config.items('common'))['prefix'] == '/opt/app'

    # missing reference
    ok = False
    try:
        config.read_string('[q]\nbad = ${nope}\n')
        config.get('q', 'bad')
    except configparser.InterpolationMissingOptionError as e:
        ok = True
        assert 'nope' in e.reference
    assert ok

    # missing section in a cross-section reference
    ok = False
    try:
        config.read_string('[r]\nbad = ${gone:opt}\n')
        config.get('r', 'bad')
    except configparser.InterpolationMissingOptionError as e2:
        ok = True
        assert 'gone' in e2.reference
    assert ok

    # more than one ':' -> InterpolationSyntaxError
    ok = False
    try:
        config.read_string('[t]\nbad = ${a:b:c}\n')
        config.get('t', 'bad')
    except configparser.InterpolationSyntaxError:
        ok = True
    assert ok

    # set() validates the '$' syntax
    ok = False
    try:
        config.set('common', 'oops', 'stray $ sign')
    except ValueError:
        ok = True
    assert ok


def test_basic_interpolation_syntax_errors():
    config = configparser.ConfigParser()
    # a bare '%' read from input raises InterpolationSyntaxError on get
    config.read_string('[p]\nbad = 100% sure\n')
    ok = False
    try:
        config.get('p', 'bad')
    except configparser.InterpolationSyntaxError:
        ok = True
    assert ok
    assert config.get('p', 'bad', raw=True) == '100% sure'
    # set() validates the '%' syntax up front
    ok = False
    try:
        config.set('p', 'oops', '100% sure')
    except ValueError:
        ok = True
    assert ok
    # ...but escaped/reference forms are fine to set
    config.set('p', 'fine', '100%% sure')
    assert config.get('p', 'fine') == '100% sure'



def test_module_constants():
    assert configparser.DEFAULTSECT == 'DEFAULT'
    assert configparser.MAX_INTERPOLATION_DEPTH == 10

    # DEFAULTSECT names the section whose values every other section
    # inherits, but is never listed as a section itself
    config = configparser.ConfigParser()
    config.read_string('[DEFAULT]\nshared = 1\n[main]\nown = 2\n')
    assert config.sections() == ['main']
    assert configparser.DEFAULTSECT not in config.sections()
    assert config.has_option('main', 'shared')
    assert config.get('main', 'shared') == '1'
    assert config.has_section(configparser.DEFAULTSECT) is False


def test_interpolation_depth_error():
    config = configparser.ConfigParser()
    config.read_string('[s]\na = %(b)s\nb = %(a)s\nc = %(a)s\n')
    raised = False
    try:
        config.get('s', 'a')
    except configparser.InterpolationDepthError as e:
        raised = True
        assert e.option == 'a'
        assert e.section == 's'
        assert 'Recursion limit exceeded' in str(e)
        assert "'%(b)s'" in str(e)  # raw value is part of the message
    assert raised

    # a chain that stays within MAX_INTERPOLATION_DEPTH is fine
    config.set('s', 'b', 'end')
    assert config.get('s', 'c') == 'end'

    # ..and it is an InterpolationError, so the generic handlers still catch it
    config.set('s', 'b', '%(a)s')
    raised = False
    try:
        config.get('s', 'c')
    except configparser.InterpolationError:
        raised = True
    assert raised

    # raw access never interpolates, so never hits the limit
    assert config.get('s', 'a', raw=True) == '%(b)s'

def test_optionxform():
    # RawConfigParser.optionxform: lower-cases option names on the way
    # in (set/read/get), and is a public method in its own right
    config = configparser.RawConfigParser()
    assert config.optionxform('MiXeD') == 'mixed'
    config.read_string('[s]\nKeyOne = 1\n')
    config.set('s', 'KeyTwo', '2')
    assert sorted(config.options('s')) == ['keyone', 'keytwo']
    assert config.get('s', 'KEYONE') == '1'
    assert config.has_option('s', 'keytwo')


def test_boolean_states():
    config = configparser.RawConfigParser()
    states = config.BOOLEAN_STATES
    assert states['yes'] is True
    assert states['off'] is False
    assert len(states) == 8
    assert sorted(states) == ['0', '1', 'false', 'no', 'off', 'on', 'true', 'yes']
    config.read_string('[s]\na = YES\nb = Off\nc = 1\nd = 0\n')
    assert config.getboolean('s', 'a') and not config.getboolean('s', 'b')
    assert config.getboolean('s', 'c') and not config.getboolean('s', 'd')
    # it's one shared dict: an addition is seen by every parser
    config.BOOLEAN_STATES['sure'] = True
    other = configparser.ConfigParser()
    other.read_string('[s]\ne = sure\n')
    assert other.getboolean('s', 'e') is True
    assert other['s'].getboolean('e') is True
    del config.BOOLEAN_STATES['sure']
    ok = False
    try:
        other.getboolean('s', 'e')
    except ValueError:
        ok = True
    assert ok


def test_constructor_defaults_and_default_section():
    # defaults= are option-name normalized and live in the default section
    config = configparser.RawConfigParser(defaults={'Home': '/root', 'shell': 'sh'})
    assert config.defaults() == {'home': '/root', 'shell': 'sh'}
    assert config.get('DEFAULT', 'home') == '/root'
    config.add_section('user')
    assert config.get('user', 'home') == '/root'   # inherited
    assert config['user']['shell'] == 'sh'
    assert sorted(config.options('user')) == ['home', 'shell']

    # default_section= renames the section that feeds every other one
    config = configparser.ConfigParser(default_section='common')
    config.read_string('[common]\nbase = /opt\n[app]\npath = %(base)s/app\n')
    assert config.default_section == 'common'
    assert config.sections() == ['app']
    assert config.get('app', 'path') == '/opt/app'
    assert config.defaults() == {'base': '/opt'}
    assert 'common' in config
    assert config['common']['base'] == '/opt'


def test_allow_no_value():
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string('[s]\nnovalue\nempty =\nnormal = x\n')
    assert config.has_option('s', 'novalue')
    assert config.get('s', 'novalue') is None
    assert config['s']['novalue'] is None
    assert config.get('s', 'empty') == ''
    assert config.get('s', 'normal') == 'x'
    assert sorted(config.options('s')) == ['empty', 'normal', 'novalue']
    # CPython quirk: ConfigParser.items() interpolates the None into '',
    # while raw=True (and RawConfigParser) keep the None
    assert sorted(config.items('s')) == [('empty', ''), ('normal', 'x'), ('novalue', '')]
    assert dict(config.items('s', raw=True)) == {'novalue': None, 'empty': '', 'normal': 'x'}
    raw = configparser.RawConfigParser(allow_no_value=True)
    raw.read_string('[s]\nnovalue\n')
    assert raw.items('s') == [('novalue', None)]

    # write() emits a bare key for a valueless option, and the result
    # reads back the same
    fl = open(writefile, 'w')
    config.write(fl)
    fl.close()
    text = open(writefile).read()
    assert '\nnovalue\n' in text
    assert '\nempty = \n' in text
    reread = configparser.ConfigParser(allow_no_value=True)
    reread.read(writefile)
    assert reread.get('s', 'novalue') is None
    assert reread.get('s', 'empty') == ''

    # without allow_no_value a bare key is a parsing error
    strict = configparser.ConfigParser()
    ok = False
    try:
        strict.read_string('[s]\nnovalue\n')
    except configparser.ParsingError as e:
        ok = True
        assert e.errors == [(2, 'novalue\n')]   # raw line (3.13+); repr()'d in the message
    assert ok


def test_delimiters():
    config = configparser.ConfigParser(delimiters=('->', '='))
    config.read_string('[s]\na -> 1\nb=2\nc: 3 -> x\n')
    assert config.get('s', 'a') == '1'
    assert config.get('s', 'b') == '2'
    assert not config.has_option('s', 'c')
    assert config.get('s', 'c: 3') == 'x'   # ':' is not a delimiter now
    ok = False
    try:
        config.read_string('[s]\nd: 4\n')  # ... so this line has no delimiter
    except configparser.ParsingError as e:
        ok = True
        assert e.errors == [(2, 'd: 4\n')]
    assert ok

    # write() uses the first delimiter, with or without spaces
    fl = open(writefile, 'w')
    config.write(fl)
    fl.close()
    text = open(writefile).read()
    assert 'a -> 1\n' in text
    fl = open(writefile, 'w')
    config.write(fl, space_around_delimiters=False)
    fl.close()
    text = open(writefile).read()
    assert 'a->1\n' in text
    assert 'b->2\n' in text

    # the default delimiters
    config = configparser.ConfigParser()
    config.read_string('[s]\na = 1\nb : 2\nc=3\n')
    assert sorted(config.items('s')) == [('a', '1'), ('b', '2'), ('c', '3')]
    fl = open(writefile, 'w')
    config.write(fl, space_around_delimiters=False)
    fl.close()
    assert sorted(open(writefile).read().split('\n')) == ['', '', '[s]', 'a=1', 'b=2', 'c=3']


def test_comment_prefixes():
    # full-line comments: default '#' and ';', only at the start of a
    # (stripped) line
    config = configparser.ConfigParser()
    config.read_string('[s]\n# c1\n  ; c2\na = 1 # not a comment\n')
    assert config.items('s') == [('a', '1 # not a comment')]

    # a custom prefix; then '#' and ';' are plain option lines
    config = configparser.ConfigParser(comment_prefixes=('//',))
    config.read_string('[s]\n// c\n# not a comment = 1\n; also = 2\n')
    assert sorted(config.items('s')) == [('# not a comment', '1'), ('; also', '2')]

    # inline comments only when the prefix follows whitespace (or starts
    # the line)
    config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
    config.read_string(
        '[s]  ; header comment\n'
        'url = http://host/?x=1 ; y=2\n'
        'hash = red#ff0000\n'
        'both = value # c1 ; c2\n'
        'tail = value ;\n'
        'only = ; nothing\n'
    )
    assert config.sections() == ['s']
    assert config.get('s', 'url') == 'http://host/?x=1'
    assert config.get('s', 'hash') == 'red#ff0000'
    assert config.get('s', 'both') == 'value'
    assert config.get('s', 'tail') == 'value'
    assert config.get('s', 'only') == ''
    assert sorted(config.options('s')) == ['both', 'hash', 'only', 'tail', 'url']


def test_multiline_values():
    config = configparser.ConfigParser()
    config.read_string(
        '[s]\n'
        'a = first\n'
        '    second\n'
        '\n'
        '    third\n'
        'b = x\n'
        '\n'
        '\n'
        'c =\n'
        '  only continuation\n'
    )
    assert config.get('s', 'a') == 'first\nsecond\n\nthird'
    assert config.get('s', 'b') == 'x'   # trailing empty lines are stripped
    assert config.get('s', 'c') == '\nonly continuation'

    # empty_lines_in_values=False: an empty line ends the value
    # (and a later indented line is then just a bad line)
    config = configparser.ConfigParser(empty_lines_in_values=False)
    config.read_string('[s]\na = first\n    second\n\nb = x\n')
    assert config.get('s', 'a') == 'first\nsecond'
    assert config.get('s', 'b') == 'x'
    ok = False
    try:
        config.read_string('[t]\na = first\n\n    orphan\n')
    except configparser.ParsingError as e:
        ok = True
        assert e.errors == [(4, '    orphan\n')]
    assert ok
    assert config.get('t', 'a') == 'first'

    # continuation lines survive a write()/read() round trip
    config = configparser.ConfigParser()
    config.set('DEFAULT', 'm', 'l1\nl2\n\nl4')
    fl = open(writefile, 'w')
    config.write(fl)
    fl.close()
    assert open(writefile).read() == '[DEFAULT]\nm = l1\n\tl2\n\t\n\tl4\n\n'
    reread = configparser.ConfigParser()
    reread.read(writefile)
    assert reread.get('DEFAULT', 'm') == 'l1\nl2\n\nl4'


def test_strict():
    # strict=False: duplicate sections and options in one source are
    # merged/overwritten instead of raising
    config = configparser.ConfigParser(strict=False)
    config.read_string('[s]\na = 1\na = 2\n[s]\nb = 3\n')
    assert sorted(config.items('s')) == [('a', '2'), ('b', '3')]

    config = configparser.ConfigParser()   # strict=True default
    for text in ('[s]\na = 1\na = 2\n', '[s]\na = 1\n[s]\nb = 3\n'):
        ok = False
        try:
            config.read_string(text)
        except configparser.DuplicateOptionError as doe:
            ok = True
            assert doe.section == 's' and doe.option == 'a'
            assert doe.source == '<string>' and doe.lineno == 3
        except configparser.DuplicateSectionError as dse:
            ok = True
            assert dse.section == 's' and dse.source == '<string>' and dse.lineno == 3
        assert ok

    # across two sources the same section may be extended even when strict
    config = configparser.ConfigParser()
    config.read_string('[s]\na = 1\n')
    config.read_string('[s]\nb = 2\n')
    assert sorted(config.items('s')) == [('a', '1'), ('b', '2')]


def test_raw_constructor_args():
    # the same keyword arguments, but on RawConfigParser itself
    config = configparser.RawConfigParser(
        delimiters=('->',),
        comment_prefixes=('//',),
        inline_comment_prefixes=('!',),
        strict=False,
        empty_lines_in_values=False,
        default_section='common',
    )
    assert config.default_section == 'common'
    config.read_string(
        '[common]\n'
        'shared -> %(x)s\n'
        '[s]\n'
        '// comment\n'
        '# a -> 1 ! inline\n'
        'b -> first\n'
        '    second\n'
        '\n'
        'b -> again\n'
        '[s]\n'
        'c -> 3\n'
    )
    assert config.sections() == ['s']
    assert config.get('s', '# a') == '1'
    assert config.get('s', 'b') == 'again'           # strict=False: overwritten
    assert config.get('s', 'c') == '3'               # ... and section merged
    assert config.get('s', 'shared') == '%(x)s'      # no interpolation
    assert config.has_section('common') == False

    config = configparser.RawConfigParser(empty_lines_in_values=False)
    config.read_string('[s]\na = first\n    second\n\nb = x\n')
    assert config.get('s', 'a') == 'first\nsecond'

    config = configparser.RawConfigParser()   # strict=True default
    ok = False
    try:
        config.read_string('[s]\na = 1\na = 2\n')
    except configparser.DuplicateOptionError:
        ok = True
    assert ok


def test_multiline_continuation_error():
    config = configparser.ConfigParser(allow_no_value=True)
    ok = False
    try:
        config.read_string('[s]\nnovalue\n    continued\n', source='cfg.ini')
    except configparser.MultilineContinuationError as e:
        ok = True
        assert e.source == 'cfg.ini'
        assert e.lineno == 3
        assert e.line == '    continued\n'
        assert 'Key without value' in e.message
        assert isinstance(e, configparser.ParsingError)
    assert ok


def test_invalid_write_error():
    config = configparser.ConfigParser()
    config.add_section('s')
    config['s']['[looks like a section]'] = 'x'
    fl = open(writefile, 'w')
    ok = False
    try:
        config.write(fl)
    except configparser.InvalidWriteError as e:
        ok = True
        assert 'begins with section pattern' in e.message
        assert isinstance(e, configparser.Error)
    fl.close()
    assert ok

    config = configparser.ConfigParser()
    config.read_dict({'s': {'a=b': '1'}})
    fl = open(writefile, 'w')
    ok = False
    try:
        config.write(fl)
    except configparser.InvalidWriteError as e:
        ok = True
        assert 'contains delimiter =' in e.message
    fl.close()
    assert ok


def test_parsing_error_source():
    pe = configparser.ParsingError('some.ini')
    assert pe.source == 'some.ini'
    assert pe.message == "Source contains parsing errors: 'some.ini'"
    assert pe.errors == []

    # the source= argument of read_string/read_file/read_dict names the
    # source in the raised errors (repr()'d in the message)
    config = configparser.ConfigParser()
    ok = False
    try:
        config.read_string('[s]\nbad line\nworse line\n', source='my.ini')
    except configparser.ParsingError as e:
        ok = True
        assert e.source == 'my.ini'
        assert e.errors == [(2, 'bad line\n'), (3, 'worse line\n')]
        assert e.message == "Source contains parsing errors: 'my.ini'\n\t[line  2]: 'bad line\\n'\n\t[line  3]: 'worse line\\n'"
    assert ok

    ok = False
    try:
        config.read_string('nosection = 1\n', source='x.ini')
    except configparser.MissingSectionHeaderError as mshe:
        ok = True
        assert mshe.source == 'x.ini' and mshe.lineno == 1 and mshe.line == 'nosection = 1\n'
    assert ok

    fl = open(writefile, 'w')
    fl.write('[s]\noops\n')
    fl.close()
    fl = open(writefile)
    ok = False
    try:
        config.read_file(fl, source='named.ini')
    except configparser.ParsingError as e:
        ok = True
        assert e.source == 'named.ini'
    fl.close()
    assert ok
    fl = open(writefile)
    ok = False
    try:
        config.read_file(fl)
    except configparser.ParsingError as e:
        ok = True
        assert e.source == writefile   # taken from fp.name
    fl.close()
    assert ok

    # read_dict(source=) is accepted (a dict can't produce parsing errors)
    config.read_dict({'d': {'k': 'v'}}, source='some dict')
    assert config.get('d', 'k') == 'v'


def test_typed_getters_raw_and_vars():
    config = configparser.ConfigParser()
    config.read_string('[s]\nn = 4\ndouble = %(n)s%(n)s\nflag = %(yes)s\nhalf = 0.5\n')
    assert config.getint('s', 'double') == 44
    assert config.getint('s', 'double', vars={'n': '7'}) == 77
    assert config.getint('s', 'n', raw=True) == 4
    assert config.getfloat('s', 'half', vars={'half': '0.25'}) == 0.25
    assert config.getfloat('s', 'half', raw=True) == 0.5
    assert config.getboolean('s', 'flag', vars={'yes': 'on'}) is True
    assert config.getboolean('s', 'flag', vars={'yes': 'no'}) is False
    ok = False
    try:
        config.getboolean('s', 'flag', raw=True)   # '%(yes)s' is not a boolean
    except ValueError:
        ok = True
    assert ok

    # the same three arguments on SectionProxy (fallback comes first there)
    sec = config['s']
    assert sec.getint('double', vars={'n': '2'}) == 22
    assert sec.getint('n', 0, raw=True) == 4
    assert sec.getfloat('half', raw=True) == 0.5
    assert sec.getfloat('half', vars={'half': '2.5'}) == 2.5
    assert sec.getboolean('flag', vars={'yes': 'true'}) is True
    ok = False
    try:
        sec.getboolean('flag', False, raw=True)   # present but raw: not a boolean
    except ValueError:
        ok = True
    assert ok
    assert sec.getboolean('missing', True, raw=True) is True


def test_unnamed_section():
    U = configparser.UNNAMED_SECTION
    assert str(U) == '<UNNAMED_SECTION>'

    # options before the first header go into the unnamed section
    config = configparser.ConfigParser(allow_unnamed_section=True)
    config.read_string('a = 1\nb = 2\n\n[s]\nc = 3\n')
    # (no order checks: shed skin dicts are unordered)
    assert len(config.sections()) == 2
    assert U in config.sections()
    assert 's' in config.sections()
    assert config.has_section(U)
    assert config.get(U, 'a') == '1'
    assert config[U]['b'] == '2'
    assert sorted(config.items(U)) == [('a', '1'), ('b', '2')]
    assert config.get('s', 'c') == '3'

    # write(): the unnamed section comes first, without a header
    fl = open(writefile, 'w')
    config.write(fl)
    fl.close()
    text = open(writefile).read()
    unnamed, rest = text.split('\n\n[s]\n')
    assert sorted(unnamed.split('\n')) == ['a = 1', 'b = 2']
    assert rest == 'c = 3\n\n'

    # an empty unnamed section is not written
    config = configparser.RawConfigParser(allow_unnamed_section=True)
    config.read_string('[s]\nc = 3\n')
    assert config.has_section(U)
    assert config.options(U) == []
    fl = open(writefile, 'w')
    config.write(fl)
    fl.close()
    assert open(writefile).read() == '[s]\nc = 3\n\n'

    # add_section()/set()/read_dict()
    config = configparser.ConfigParser(allow_unnamed_section=True)
    config.add_section(U)
    config.set(U, 'x', 'y')
    config.read_dict({'t': {'k': 'v'}})
    fl = open(writefile, 'w')
    config.write(fl)
    fl.close()
    assert open(writefile).read() == 'x = y\n\n[t]\nk = v\n\n'
    try:
        config.add_section(U)
        assert False
    except configparser.DuplicateSectionError:
        pass

    # disabled by default
    config = configparser.ConfigParser()
    try:
        config.read_string('a = 1\n')
        assert False
    except configparser.MissingSectionHeaderError:
        pass
    try:
        config.add_section(U)
        assert False
    except configparser.UnnamedSectionDisabledError as e:
        assert str(e) == 'Support for UNNAMED_SECTION is disabled.'
    try:
        config.read_dict({U: {'a': '1'}})
        assert False
    except configparser.Error:
        pass
    assert not config.has_section(U)


def test_interpolation_before_methods():
    # the before_* hooks can also be called directly
    p = configparser.ConfigParser()
    p.read_string('[o]\nx = X\n')
    d = {'a': 'A'}

    di = configparser.Interpolation()   # passes everything through
    assert di.before_get(p, 's', 'o', '%(x', d) == '%(x'
    assert di.before_set(p, 's', 'o', '%') == '%'
    assert di.before_read(p, 's', 'o', '$') == '$'
    assert di.before_write(p, 's', 'o', '$') == '$'

    bi = configparser.BasicInterpolation()
    assert bi.before_get(p, 's', 'o', '%(a)s-%%', d) == 'A-%'
    assert bi.before_set(p, 's', 'o', '100%%') == '100%%'
    assert bi.before_read(p, 's', 'o', '%(x') == '%(x'
    assert bi.before_write(p, 's', 'o', '%(x') == '%(x'
    ok = False
    try:
        bi.before_set(p, 's', 'o', '100%')
    except ValueError as e:
        ok = True
        assert str(e) == "invalid interpolation syntax in '100%' at position 3"
    assert ok
    ok = False
    try:
        bi.before_get(p, 's', 'opt', '%(nope)s', d)
    except configparser.InterpolationMissingOptionError as e2:
        ok = True
        assert (e2.section, e2.option, e2.reference) == ('s', 'opt', 'nope')
    assert ok
    ok = False
    try:
        bi.before_get(p, 's', 'opt', '%(a)s %', d)
    except configparser.InterpolationSyntaxError as e3:
        ok = True
        assert (e3.section, e3.option) == ('s', 'opt')
    assert ok
    ok = False
    try:
        bi.before_get(p, 's', 'opt', '%(a)s', {'a': '%(a)s'})
    except configparser.InterpolationDepthError as e4:
        ok = True
        assert (e4.section, e4.option) == ('s', 'opt')
    assert ok

    ei = configparser.ExtendedInterpolation()
    assert ei.before_get(p, 's', 'o', '${a}-$$', d) == 'A-$'
    assert ei.before_get(p, 's', 'o', '${o:x}/${a}', d) == 'X/A'
    assert ei.before_set(p, 's', 'o', '$$5') == '$$5'
    assert ei.before_read(p, 's', 'o', '${x') == '${x'
    assert ei.before_write(p, 's', 'o', '${x') == '${x'
    ok = False
    try:
        ei.before_set(p, 's', 'o', '5$')
    except ValueError as e5:
        ok = True
        assert str(e5) == "invalid interpolation syntax in '5$' at position 1"
    assert ok
    for ref in ('${nope}', '${o:nope}'):
        ok = False
        try:
            ei.before_get(p, 's', 'opt', ref, d)
        except configparser.InterpolationMissingOptionError as e6:
            ok = True
            assert e6.reference == ref[2:-1]
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
    test_no_inline_comments()
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
    test_error_attribute_types()
    test_typed_getters_fallback()
    test_section_proxy_name_parser_repr()
    test_section_proxy_get()
    test_section_proxy_typed_getters()
    test_parsing_error_append()
    test_parsing_error_combine()
    test_popitem()
    test_interpolation_kwarg()
    test_extended_interpolation()
    test_basic_interpolation_syntax_errors()
    test_module_constants()
    test_interpolation_depth_error()
    test_optionxform()
    test_boolean_states()
    test_constructor_defaults_and_default_section()
    test_allow_no_value()
    test_delimiters()
    test_comment_prefixes()
    test_multiline_values()
    test_strict()
    test_raw_constructor_args()
    test_multiline_continuation_error()
    test_invalid_write_error()
    test_parsing_error_source()
    test_typed_getters_raw_and_vars()
    test_unnamed_section()
    test_interpolation_before_methods()
    test_add_default_section_error()

if __name__ == '__main__':
    test_all()
    print("ALL OK")
