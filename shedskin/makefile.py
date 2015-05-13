'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

makefile.py: generate makefile

'''
import os
import sys
from distutils import sysconfig

import jinja2

from python import find_module, Module


def generate_makefile(gx):
    if sys.platform == 'win32':
        pyver = '%d%d' % sys.version_info[:2]
        prefix = sysconfig.get_config_var('prefix')
    else:
        pyver = sysconfig.get_config_var('VERSION') or sysconfig.get_python_version()
        includes = '-I' + sysconfig.get_python_inc() + ' '
        if not gx.pypy:
            includes += '-I' + sysconfig.get_python_inc(plat_specific=True)

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

    context = {
        'ident': ident,
    }

    if gx.msvc:
        esc_space = lambda s: s.replace(' ', '/ ')
        env_var = lambda s: '$(%s)' % s
    else:
        esc_space = lambda s: s.replace(' ', '\ ')
        env_var = lambda s: '${%s}' % s

    context['libdirs'] = [
        esc_space(lib) for lib in gx.libdirs[:-1]] + [
        env_var('SHEDSKIN_LIBDIR')]

    shedskin_libdir = context['shedskin_libdir'] = esc_space(gx.libdirs[-1])

    modules = context['modules'] = list(gx.modules.values())
    if all(m.ident != 're' for m in modules):
        re_module = Module(*find_module(gx, 're', gx.libdirs), node=None)
        modules.append(re_module)

    context['module_filenames'] = [
        mod.filename.strip().replace(shedskin_libdir, env_var('SHEDSKIN_LIBDIR'))
        for mod in sorted(modules, key=lambda m: m.ident, reverse=False)
    ]

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

    context['variables'] = [('SHEDSKIN_LIBDIR', shedskin_libdir)]

    for line in file(flags):
        line = line[:-1]

        variable, value = (s.strip() for s in line.split('=', 1))

        if variable == 'CCFLAGS':
            if sys.platform == 'darwin' and os.path.isdir('/usr/local/include'):
                value += ' -I/usr/local/include'  # XXX
            if sys.platform == 'darwin' and os.path.isdir('/opt/local/include'):
                value += ' -I/opt/local/include'  # XXX
            if not gx.wrap_around_check:
                value += ' -D__SS_NOWRAP'
            if not gx.bounds_checking:
                value += ' -D__SS_NOBOUNDS'
            if gx.fast_random:
                value += ' -D__SS_FASTRANDOM'
            if gx.gc_cleanup:
                value += ' -D__SS_GC_CLEANUP'
            if not gx.assertions:
                value += ' -D__SS_NOASSERT'
            if gx.fast_hash:
                value += ' -D__SS_FASTHASH'
            if gx.longlong:
                value += ' -D__SS_LONG'
            if gx.backtrace:
                value += ' -D__SS_BACKTRACE -rdynamic -fno-inline'
            if gx.pypy:
                value += ' -D__SS_PYPY'
            if not gx.gcwarns:
                value += ' -D__SS_NOGCWARNS'
            if gx.extension_module:
                if sys.platform == 'win32':
                    value += ' -I%s\\include -D__SS_BIND' % prefix
                else:
                    value += ' -g -fPIC -D__SS_BIND ' + includes

        elif variable == 'LFLAGS':
            if sys.platform == 'darwin' and os.path.isdir('/opt/local/lib'):  # XXX
                value += ' -L/opt/local/lib'
            if sys.platform == 'darwin' and os.path.isdir('/usr/local/lib'):  # XXX
                value += ' -L/usr/local/lib'
            if gx.extension_module:
                if gx.msvc:
                    value += ' /dll /libpath:%s\\libs ' % prefix
                elif sys.platform == 'win32':
                    value += ' -shared -L%s\\libs -lpython%s' % (prefix, pyver)
                elif sys.platform == 'darwin':
                    value += ' -bundle -undefined dynamic_lookup ' + ldflags
                elif sys.platform == 'sunos5':
                    value += ' -shared -Xlinker ' + ldflags
                else:
                    value += ' -shared -Xlinker -export-dynamic ' + ldflags

            if any(m.ident == 'socket' for m in modules):
                if sys.platform == 'win32':
                    value += ' -lws2_32'
                elif sys.platform == 'sunos5':
                    value += ' -lsocket -lnsl'
            if any(m.ident == 'os' for m in modules):
                if sys.platform not in ['win32', 'darwin', 'sunos5']:
                    value += ' -lutil'
            if any(m.ident == 'hashlib' for m in modules):
                value += ' -lcrypto'

        context['variables'].append((variable, value))

    context['extension_module'] = gx.extension_module
    context['platform'] = sys.platform

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            os.path.dirname(__file__) + '/templates/makefile/'),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tpl = 'Makefile.tpl'
    if gx.msvc:
        tpl = os.path.join('msvc', tpl)
    contents = jinja_env.get_template(tpl).render(**context)
    with open(gx.makefile_name, 'w') as f:
        f.write(contents)
