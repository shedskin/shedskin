from __future__ import print_function

'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

makefile.py: generate makefile

'''
import os
import re
import subprocess
import sys
import sysconfig


def check_output(cmd):
    try:
        return subprocess.check_output(cmd.split(), encoding='utf8').strip()
    except FileNotFoundError:
        return None

def generate_makefile(gx):
    if sys.platform == 'win32':
        pyver = '%d%d' % sys.version_info[:2]
        prefix = sysconfig.get_config_var('prefix')
    else:
        pyver = sysconfig.get_config_var('VERSION') or sysconfig.get_python_version()
        includes = '-I' + sysconfig.get_config_var('INCLUDEPY') + ' '

        if not gx.pypy:
            includes += '-I' + os.path.dirname(sysconfig.get_config_h_filename())

        if sys.platform == 'darwin':
            ldflags = sysconfig.get_config_var('BASECFLAGS')
        else:
            ldflags = (sysconfig.get_config_var('LIBS') or '') + ' '
            ldflags += (sysconfig.get_config_var('SYSLIBS') or '') + ' '
            if not gx.pypy:
                ldflags += '-lpython' + pyver
                if not sysconfig.get_config_var('Py_ENABLE_SHARED'):
                    ldflags += ' -L' + sysconfig.get_config_var('LIBPL')

    ident = gx.main_module.ident
    if gx.extension_module:
        if sys.platform == 'win32':
            ident += '.pyd'
        else:
            ident += '.so'

    makefile = open(gx.makefile_name, 'w')

    write = lambda line='': print(line, file=makefile)

    if gx.msvc:
        esc_space = '/ '

        def env_var(name):
            return '$(%s)' % name
    else:
        esc_space = '\ '

        def env_var(name):
            return '${%s}' % name

    libdirs = [d.replace(' ', esc_space) for d in gx.libdirs]
    write('SHEDSKIN_LIBDIR=%s' % (libdirs[-1]))
    filenames = []
    modules = gx.modules.values()
    for module in modules:
        filename = os.path.splitext(module.filename)[0]  # strip .py
        filename = filename.replace(' ', esc_space)  # make paths valid
        filename = filename.replace(libdirs[-1], env_var('SHEDSKIN_LIBDIR'))
        filenames.append(filename)

    cppfiles = [fn + '.cpp' for fn in filenames]
    hppfiles = [fn + '.hpp' for fn in filenames]
    # used to be 're', but currently unused, but kept around just in case
    for always in ():
        repath = os.path.join(env_var('SHEDSKIN_LIBDIR'), always)
        if not repath in filenames:
            cppfiles.append(repath + '.cpp')
            hppfiles.append(repath + '.hpp')

    cppfiles.sort(reverse=True)
    hppfiles.sort(reverse=True)
    cppfiles = ' \\\n\t'.join(cppfiles)
    hppfiles = ' \\\n\t'.join(hppfiles)

    # import flags
    if gx.flags:
        flags = gx.flags
    elif os.path.isfile('FLAGS'):
        flags = 'FLAGS'
    elif os.path.isfile('/etc/shedskin/FLAGS'):
        flags = '/etc/shedskin/FLAGS'
    elif gx.msvc:
        flags = os.path.join(gx.sysdir, 'FLAGS.msvc')
    elif sys.platform == 'win32':
        flags = os.path.join(gx.sysdir, 'FLAGS.mingw')
    elif sys.platform == 'darwin':
        flags = os.path.join(gx.sysdir, 'FLAGS.osx')
    else:
        flags = os.path.join(gx.sysdir, 'FLAGS')

    for line in open(flags):
        line = line[:-1]

        variable = line[:line.find('=')].strip()
        if variable == 'CCFLAGS':
            line += ' -I. -I%s' % env_var('SHEDSKIN_LIBDIR')
            line += ''.join(' -I' + libdir for libdir in libdirs[:-1])
            if sys.platform == 'darwin' and os.path.isdir('/usr/local/include'):
                line += ' -I/usr/local/include'  # XXX
            if sys.platform == 'darwin' and os.path.isdir('/opt/local/include'):
                line += ' -I/opt/local/include'  # XXX
            if not gx.wrap_around_check:
                line += ' -D__SS_NOWRAP'
            if not gx.bounds_checking:
                line += ' -D__SS_NOBOUNDS'
            if gx.gc_cleanup:
                line += ' -D__SS_GC_CLEANUP'
            if not gx.assertions:
                line += ' -D__SS_NOASSERT'
            if gx.longlong:
                line += ' -D__SS_LONG'
            if gx.backtrace:
                line += ' -D__SS_BACKTRACE -rdynamic -fno-inline'
            if gx.pypy:
                line += ' -D__SS_PYPY'
            if gx.nogc:
                line += ' -D__SS_NOGC'
            if not gx.gcwarns:
                line += ' -D__SS_NOGCWARNS'
            if gx.extension_module:
                if sys.platform == 'win32':
                    line += ' -I%s\\include -D__SS_BIND' % prefix
                else:
                    line += ' -g -fPIC -D__SS_BIND ' + includes

        elif variable == 'LFLAGS':
            if sys.platform == 'darwin' and os.path.isdir('/opt/local/lib'):  # XXX
                line += ' -L/opt/local/lib'
            if sys.platform == 'darwin' and os.path.isdir('/usr/local/lib'):  # XXX
                line += ' -L/usr/local/lib'
            if gx.extension_module:
                if gx.msvc:
                    line += ' /dll /libpath:%s\\libs ' % prefix
                elif sys.platform == 'win32':
                    line += ' -shared -L%s\\libs -lpython%s' % (prefix, pyver)
                elif sys.platform == 'darwin':
                    line += ' -bundle -undefined dynamic_lookup ' + ldflags
                elif sys.platform == 'sunos5':
                    line += ' -shared -Xlinker ' + ldflags
                else:
                    line += ' -Wno-register -shared -Xlinker -export-dynamic ' + ldflags

            if 're' in [m.ident for m in modules]:
                line += ' -lpcre'
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

        write(line)
    write()

    write('CPPFILES=%s\n' % cppfiles)
    write('HPPFILES=%s\n' % hppfiles)

    # tests for static
    MATCH = re.match(r"^LFLAGS=(.+)(\$\(LDFLAGS\).+)", line)
    HOMEBREW=check_output('brew --prefix')
    if sys.platform == 'darwin' and HOMEBREW and MATCH:
        write('STATIC_PREFIX=$(shell brew --prefix)')
        write('STATIC_LIBDIR=$(STATIC_PREFIX)/lib')
        write('STATIC_INCLUDE=$(STATIC_PREFIX)/include')
        write()
        write('GC_STATIC=$(STATIC_LIBDIR)/libgc.a')
        write('GCCPP_STATIC=$(STATIC_LIBDIR)/libgccpp.a')
        write('GC_INCLUDE=$(STATIC_INCLUDE)/include')
        write('PCRE_STATIC=$(STATIC_LIBDIR)/libpcre.a')
        write('PCRE_INCLUDE=$(STATIC_INCLUDE)/include')
        write()
        write('STATIC_LIBS=$(GC_STATIC) $(GCCPP_STATIC) $(PCRE_STATIC)')
        write('STATIC_CCFLAGS=$(CCFLAGS) -I$(GC_INCLUDE) -I$(PCRE_INCLUDE)')
        write('STATIC_LFLAGS=' + MATCH.group(2))
        write()

    write('all:\t' + ident + '\n')

    # executable (normal, debug, profile) or extension module
    _out = '-o '
    _ext = ''
    targets = [('', '')]
    if not gx.extension_module:
        targets += [('_prof', '-pg -ggdb'), ('_debug', '-g -ggdb')]
    if gx.msvc:
        _out = '/out:'
        _ext = ''
        targets = [('', '')]
        if not gx.extension_module:
            _ext = '.exe'
    for suffix, options in targets:
        write(ident + suffix + ':\t$(CPPFILES) $(HPPFILES)')
        write('\t$(CC) ' + options + ' $(CCFLAGS) $(CPPFILES) $(LFLAGS) ' + _out + ident + suffix + _ext + '\n')

    if sys.platform == 'darwin' and HOMEBREW and MATCH:
        # static option
        write('static: $(CPPFILES) $(HPPFILES)')
        write(f'\t$(CC) $(STATIC_CCFLAGS) $(CPPFILES) $(STATIC_LIBS) $(STATIC_LFLAGS) -o {ident}\n')

    # clean
    ext = ''
    if sys.platform == 'win32' and not gx.extension_module:
        ext = '.exe'
    write('clean:')
    targets = [ident + ext]
    if not gx.extension_module:
        if not gx.msvc:
            targets += [ident + '_prof' + ext, ident + '_debug' + ext]
    write('\trm -f %s' % ' '.join(targets))
    if sys.platform == 'darwin':
        write('\trm -rf %s.dSYM\n' % ' '.join(targets))
    write()

    # phony
    phony = '.PHONY: all clean'
    if sys.platform == 'darwin' and HOMEBREW and MATCH:
        phony += ' static'
    phony += '\n'
    write(phony)
    makefile.close()
