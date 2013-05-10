'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2011 Mark Dufour; License GNU GPL version 3 (See LICENSE)

makefile.py: generate makefile

'''
import os
import sys
from distutils import sysconfig
import config


def generate_makefile():
    if sys.platform == 'win32':
        pyver = '%d%d' % sys.version_info[:2]
        prefix = sysconfig.get_config_var('prefix')
    else:
        pyver = sysconfig.get_config_var('VERSION') or sysconfig.get_python_version()
        includes = '-I' + sysconfig.get_python_inc() + ' '
        if not config.getgx().pypy:
            includes += '-I' + sysconfig.get_python_inc(plat_specific=True)

        if sys.platform == 'darwin':
            ldflags = sysconfig.get_config_var('BASECFLAGS')
        else:
            ldflags = (sysconfig.get_config_var('LIBS') or '') + ' '
            ldflags += (sysconfig.get_config_var('SYSLIBS') or '') + ' '
            if not config.getgx().pypy:
                ldflags += '-lpython' + pyver
                if not sysconfig.get_config_var('Py_ENABLE_SHARED'):
                    ldflags += ' -L' + sysconfig.get_config_var('LIBPL')

    ident = config.getgx().main_module.ident
    if config.getgx().extension_module:
        if sys.platform == 'win32':
            ident += '.pyd'
        else:
            ident += '.so'

    makefile = file(config.getgx().makefile_name, 'w')

    if config.getgx().msvc:
        esc_space = '/ '

        def env_var(name):
            return '$(%s)' % name
    else:
        esc_space = '\ '

        def env_var(name):
            return '${%s}' % name

    libdirs = [d.replace(' ', esc_space) for d in config.getgx().libdirs]
    print >>makefile, 'SHEDSKIN_LIBDIR=%s' % (libdirs[-1])
    filenames = []
    modules = config.getgx().modules.values()
    for module in modules:
        filename = os.path.splitext(module.filename)[0]  # strip .py
        filename = filename.replace(' ', esc_space)  # make paths valid
        filename = filename.replace(libdirs[-1], env_var('SHEDSKIN_LIBDIR'))
        filenames.append(filename)

    cppfiles = [fn + '.cpp' for fn in filenames]
    hppfiles = [fn + '.hpp' for fn in filenames]
    for always in ('re',):
        repath = os.path.join(env_var('SHEDSKIN_LIBDIR'), always)
        if not repath in filenames:
            cppfiles.append(repath + '.cpp')
            hppfiles.append(repath + '.hpp')

    cppfiles.sort(reverse=True)
    hppfiles.sort(reverse=True)
    cppfiles = ' \\\n\t'.join(cppfiles)
    hppfiles = ' \\\n\t'.join(hppfiles)

    # import flags
    if config.getgx().flags:
        flags = config.getgx().flags
    elif os.path.isfile('FLAGS'):
        flags = 'FLAGS'
    elif os.path.isfile('/etc/shedskin/FLAGS'):
        flags = '/etc/shedskin/FLAGS'
    elif config.getgx().msvc:
        flags = os.path.join(config.getgx().sysdir, 'FLAGS.msvc')
    elif sys.platform == 'win32':
        flags = os.path.join(config.getgx().sysdir, 'FLAGS.mingw')
    elif sys.platform == 'darwin':
        flags = os.path.join(config.getgx().sysdir, 'FLAGS.osx')
    else:
        flags = os.path.join(config.getgx().sysdir, 'FLAGS')

    for line in file(flags):
        line = line[:-1]

        variable = line[:line.find('=')].strip()
        if variable == 'CCFLAGS':
            line += ' -I. -I%s' % env_var('SHEDSKIN_LIBDIR')
            line += ''.join(' -I' + libdir for libdir in libdirs[:-1])
            if sys.platform == 'darwin' and os.path.isdir('/usr/local/include'):
                line += ' -I/usr/local/include'  # XXX
            if sys.platform == 'darwin' and os.path.isdir('/opt/local/include'):
                line += ' -I/opt/local/include'  # XXX
            if not config.getgx().wrap_around_check:
                line += ' -D__SS_NOWRAP'
            if not config.getgx().bounds_checking:
                line += ' -D__SS_NOBOUNDS'
            if config.getgx().fast_random:
                line += ' -D__SS_FASTRANDOM'
            if config.getgx().gc_cleanup:
                line += ' -D__SS_GC_CLEANUP'
            if not config.getgx().assertions:
                line += ' -D__SS_NOASSERT'
            if config.getgx().fast_hash:
                line += ' -D__SS_FASTHASH'
            if config.getgx().longlong:
                line += ' -D__SS_LONG'
            if config.getgx().backtrace:
                line += ' -D__SS_BACKTRACE -rdynamic -fno-inline'
            if config.getgx().pypy:
                line += ' -D__SS_PYPY'
            if not config.getgx().gcwarns:
                line += ' -D__SS_NOGCWARNS'
            if config.getgx().extension_module:
                if sys.platform == 'win32':
                    line += ' -I%s\\include -D__SS_BIND' % prefix
                else:
                    line += ' -g -fPIC -D__SS_BIND ' + includes

        elif variable == 'LFLAGS':
            if sys.platform == 'darwin' and os.path.isdir('/opt/local/lib'):  # XXX
                line += ' -L/opt/local/lib'
            if sys.platform == 'darwin' and os.path.isdir('/usr/local/lib'):  # XXX
                line += ' -L/usr/local/lib'
            if config.getgx().extension_module:
                if config.getgx().msvc:
                    line += ' /dll /libpath:%s\\libs ' % prefix
                elif sys.platform == 'win32':
                    line += ' -shared -L%s\\libs -lpython%s' % (prefix, pyver)
                elif sys.platform == 'darwin':
                    line += ' -bundle -undefined dynamic_lookup ' + ldflags
                elif sys.platform == 'sunos5':
                    line += ' -shared -Xlinker ' + ldflags
                else:
                    line += ' -shared -Xlinker -export-dynamic ' + ldflags

            if 'socket' in (m.ident for m in modules):
                if sys.platform == 'win32':
                    line += ' -lws2_32'
                elif sys.platform == 'sunos5':
                    line += ' -lsocket -lnsl'
            if 'os' in (m.ident for m in modules):
                if sys.platform not in ['win32', 'darwin', 'sunos5']:
                    line += ' -lutil'
            if 'hashlib' in (m.ident for m in modules):
                line += ' -lcrypto'

        print >>makefile, line
    print >>makefile

    print >>makefile, 'CPPFILES=%s\n' % cppfiles
    print >>makefile, 'HPPFILES=%s\n' % hppfiles

    print >>makefile, 'all:\t' + ident + '\n'

    # executable (normal, debug, profile) or extension module
    _out = '-o '
    _ext = ''
    targets = [('', '')]
    if not config.getgx().extension_module:
        targets += [('_prof', '-pg -ggdb'), ('_debug', '-g -ggdb')]
    if config.getgx().msvc:
        _out = '/out:'
        _ext = ''
        targets = [('', '')]
        if not config.getgx().extension_module:
            _ext = '.exe'
    for suffix, options in targets:
        print >>makefile, ident + suffix + ':\t$(CPPFILES) $(HPPFILES)'
        print >>makefile, '\t$(CC) ' + options + ' $(CCFLAGS) $(CPPFILES) $(LFLAGS) ' + _out + ident + suffix + _ext + '\n'

    # clean
    ext = ''
    if sys.platform == 'win32' and not config.getgx().extension_module:
        ext = '.exe'
    print >>makefile, 'clean:'
    targets = [ident + ext]
    if not config.getgx().extension_module:
        if not config.getgx().msvc:
            targets += [ident + '_prof' + ext, ident + '_debug' + ext]
    print >>makefile, '\trm -f %s\n' % ' '.join(targets)

    # phony
    print >>makefile, '.PHONY: all clean\n'
    makefile.close()
