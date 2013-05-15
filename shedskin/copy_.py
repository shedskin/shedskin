'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2011 Mark Dufour; License GNU GPL version 3 (See LICENSE)

copy_.py: hacks to support copy module

'''
from config import getgx
from python import Class


def copy_method(self, cl, name, declare):
    class_name = self.cpp_name(cl)
    header = class_name + ' *'
    if not declare:
        header += class_name + '::'
    header += name + '('
    self.start(header)
    if name == '__deepcopy__':
        self.append('dict<void *, pyobj *> *memo')
    self.append(')')
    if not declare:
        print >>self.out, self.line + ' {'
        self.indent()
        self.output(class_name + ' *c = new ' + class_name + '();')
        if name == '__deepcopy__':
            self.output('memo->__setitem__(this, c);')
        for var in cl.vars.values():
            if not var.invisible and var in getgx().merged_inh and getgx().merged_inh[var]:
                varname = self.cpp_name(var)
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
    if cl.has_copy:
        copy_method(self, cl, '__copy__', declare)
    if cl.has_deepcopy:
        copy_method(self, cl, '__deepcopy__', declare)


def deepcopy_classes(classes):
    changed = True
    while changed:
        changed = False
        for cl in classes.copy():
            for var in cl.vars.values():
                if var in getgx().merged_inh:
                    newcl = set(t[0] for t in getgx().merged_inh[var] if isinstance(t[0], Class) and not t[0].mv.module.builtin)
                    if newcl - classes:
                        changed = True
                        classes.update(newcl)
    return classes


def determine_classes():  # XXX modeling..?
    if 'copy' not in getgx().modules:
        return
    func = getgx().modules['copy'].mv.funcs['copy']
    var = func.vars[func.formals[0]]
    classes = set(t[0] for t in getgx().merged_inh[var] if isinstance(t[0], Class) and not t[0].mv.module.builtin)
    for cl in classes:
        cl.has_copy = True
    func = getgx().modules['copy'].mv.funcs['deepcopy']
    var = func.vars[func.formals[0]]
    classes = set(t[0] for t in getgx().merged_inh[var] if isinstance(t[0], Class) and not t[0].mv.module.builtin)
    for cl in deepcopy_classes(classes):
        cl.has_deepcopy = True
