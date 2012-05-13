#
# Copyright (c) 2012, Brent Pedersen
# All rights reserved.
#
# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided
# that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os.path as op
import sys
from shedskin import setgx, newgx, getgx, infer, annotate, cpp, shared
import inspect
import hashlib
import subprocess

class shedskinner(object):
    r"""
    decorator to shedskin-ify functions.
    and example is::

        @shedskinner((2, 4), (6, 12), long=True, random=True, wrap_around_check=False)
        def adder(a, b):
            return a + b


        print adder(6, 8)

    note the decorator is called with example invocations so that
    shedskin can infer types. After the first invocation, the extension
    module is stored so that subsequent calls will run quickly.

    If either the function or the decorator is changed, a new module
    will be recreated.

    Parts of this were written by: https://gist.github.com/fahhem
    """
    kwlookup = {
            'nobounds': 'bounds_checking',
            'long': 'longlong',
            'nowrap': 'wrap_around_check',
            'random': 'fast_random',
            'strhash': 'fast_hash',
            }

    def __init__(self, *invocations, **kwargs):
        self.modules = kwargs.pop('modules',())
        self.functions = kwargs.pop('functions',())
        self.kwargs = kwargs

        self.invocations = invocations

    def _hash(self, source):
        return hashlib.md5(source).hexdigest()

    def _tmp(self, source_hash, ext=".py"):
        return "shedskin" + source_hash + ext

    def _get_function_source(self, fn):
        if isinstance(fn, basestring):
            fn = globals()[fn]
        src = inspect.getsource(fn)
        return src


    def __call__(self, fn):
        setgx(newgx())
        # set kwargs from the __init__ call.
        for k, v in self.kwargs.items():
            k = shedskinner.kwlookup.get(k, k)
            setattr(getgx(), k, v)
        getgx().annotation = True
        getgx().extension_module = True

        src = self._get_function_source(fn)
        source_hash = self._hash(src)
        if self._is_up_to_date(source_hash):
            mod = self._get_module(self._tmp(source_hash))
            return getattr(mod, fn.func_name)

        tmp = open(self._tmp(source_hash), "w")
        for mod in self.modules:
            if hasattr(mod, "__module__"):
                print >> tmp, 'from %s import %s' % (mod.__module__,mod.__name__)
                continue
            elif hasattr(mod, "__name__"):
                mod = mod.__name__
            print >> tmp, 'import %s' % mod

        for other_fn in self.functions:
            print >> tmp, self._get_function_source(other_fn)

        # hack to get the function source without the decorator line...
        # needs to be fixed...
        if src[0] == "@":
            print >> tmp, src.split('\n', 1)[1]
        else:
            print >> tmp, src
        for i in self.invocations:
            print >>tmp, "%s%s" % (fn.func_name, str(i))
        tmp.close()

        makefile = getgx().makefile_name = "Makefile_%s" % source_hash
        self._run_shedskin(tmp.name, makefile)
        mod = self._get_module(tmp.name)
        return getattr(mod, fn.func_name)

    def _is_up_to_date(self, source_hash):
        return op.exists(self._tmp(source_hash, ext=".so"))

    def _run_shedskin(self, name, makefile):
        old = sys.stdout
        log = sys.stdout = open(name + ".log", "w")
        getgx().main_mod = name[:-3]
        infer.analyze(name)
        annotate.annotate()
        cpp.generate_code()
        shared.print_errors()
        ret = subprocess.call("make -f %s" % makefile, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log.close()
        sys.stdout = old
        if ret != 0:
            print >>sys.stderr, "error making %s" % makefile
            print open(log.name).read()

    def _get_module(self, name):
        if name.endswith(".py"):
            name = name[:-3]
        mod = __import__(name)
        return mod
