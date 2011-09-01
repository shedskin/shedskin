'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2011 Mark Dufour; License GNU GPL version 3 (See LICENSE)

copy_.py: hacks to support copy module

'''

from shared import *

def copy_method(self, cl, name, declare):
    header = nokeywords(cl.ident)+' *'
    if not declare:
        header += nokeywords(cl.ident)+'::'
    header += name+'('
    self.start(header)

    if name == '__deepcopy__':
        self.append('dict<void *, pyobj *> *memo')
    self.append(')')

    if not declare:
        print >>self.out, self.line+' {'
        self.indent()
        self.output(nokeywords(cl.ident)+' *c = new '+nokeywords(cl.ident)+'();')
        if name == '__deepcopy__':
            self.output('memo->__setitem__(this, c);')

        for var in cl.vars.values():
            if var in getgx().merged_inh and getgx().merged_inh[var]:
                varname = var.name
                if var.masks_global(): # XXX merge
                    varname = '_'+varname
                if name == '__deepcopy__':
                    self.output('c->%s = __deepcopy(%s);' % (varname, varname))
                else:
                    self.output('c->%s = %s;' % (varname, varname))
        self.output('return c;')

        self.deindent()
        self.output('}\n')
    else:
        self.eol()

def copy_methods(self, cl, declare):
    if cl.has_copy and not 'copy' in cl.funcs: # XXX not __copy__?
        copy_method(self, cl, '__copy__', declare)
    if cl.has_deepcopy and not 'deepcopy' in cl.funcs:
        copy_method(self, cl, '__deepcopy__', declare)
