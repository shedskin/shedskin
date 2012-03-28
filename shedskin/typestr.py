'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2011 Mark Dufour; License GNU GPL version 3 (See LICENSE)

typestr.py: generate type declarations

'''

from shared import *

def nodetypestr(node, parent=None, cplusplus=True, check_extmod=False, check_ret=False, var=None): # XXX minimize
    if cplusplus and isinstance(node, variable) and node.looper: # XXX to declaredefs?
        return nodetypestr(node.looper, None, cplusplus)[:-2]+'::for_in_loop '
    if cplusplus and isinstance(node, variable) and node.wopper: # XXX to declaredefs?
        ts = nodetypestr(node.wopper, None, cplusplus)
        if ts.startswith('dict<'):
            return 'dictentry'+ts[4:]
    types = getgx().merged_inh[node]
    return typestr(types, None, cplusplus, node, check_extmod, 0, check_ret, var)

def typestr(types, parent=None, cplusplus=True, node=None, check_extmod=False, depth=0, check_ret=False, var=None, tuple_check=False):
    try:
        ts = typestrnew(types, cplusplus, node, check_extmod, depth, check_ret, var, tuple_check)
    except RuntimeError:
        if not getmv().module.builtin and isinstance(node, variable) and not node.name.startswith('__'): # XXX startswith
            if node.parent: varname = repr(node)
            else: varname = "'%s'" % node.name
            error("variable %s has dynamic (sub)type" % varname, node, warning=True)
        ts = 'ERROR'
    if cplusplus:
        if not ts.endswith('*'): ts += ' '
        return ts
    return '['+ts+']'

class ExtmodError(Exception):
    pass

def typestrnew(types, cplusplus=True, node=None, check_extmod=False, depth=0, check_ret=False, var=None, tuple_check=False):
    if depth==10:
        raise RuntimeError()

    # --- annotation or c++ code
    conv1 = {'int_': '__ss_int', 'float_': 'double', 'str_': 'str', 'none': 'int', 'bool_':'__ss_bool', 'complex':'complex'}
    conv2 = {'int_': 'int', 'float_': 'float', 'str_': 'str', 'class_': 'class', 'none': 'None','bool_': 'bool', 'complex':'complex'}
    if cplusplus: sep, ptr, conv = '<>', ' *', conv1
    else: sep, ptr, conv = '()', '', conv2

    def map(ident):
        if cplusplus: return ident+' *'
        return conv.get(ident, ident)

    anon_funcs = set([t[0] for t in types if isinstance(t[0], function)])
    if anon_funcs and check_extmod:
        raise ExtmodError()
    if anon_funcs:
        f = anon_funcs.pop()
        if f.mv != getmv():
            return f.mv.module.full_path()+'::'+'lambda%d' % f.lambdanr
        return 'lambda%d' % f.lambdanr

    classes = polymorphic_cl(types_classes(types))
    lcp = lowest_common_parents(classes)

    # --- multiple parent classes
    if len(lcp) > 1:
        if set(lcp) == set([defclass('int_'),defclass('float_')]):
            return conv['float_']
        elif not node or inode(node).mv.module.builtin:
            if defclass('complex') in lcp: # XXX
                return conv['complex']
            elif defclass('float_') in lcp:
                return conv['float_']
            elif defclass('int_') in lcp:
                return conv['int_']
            else:
                return '***ERROR*** '
        elif isinstance(node, variable):
            if not node.name.startswith('__') : # XXX startswith
                if node.parent: varname = "%s" % node
                else: varname = "'%s'" % node
                error("variable %s has dynamic (sub)type: {%s}" % (varname, ', '.join(sorted([conv2.get(cl.ident, cl.ident) for cl in lcp]))), node, warning=True)
        elif node not in getgx().bool_test_only:
            if tuple_check:
                error("tuple with length > 2 and different types of elements", node, warning=True, mv=getmv())
            else:
                error("expression has dynamic (sub)type: {%s}" % ', '.join(sorted([conv2.get(cl.ident, cl.ident) for cl in lcp])), node, warning=True)
    elif not classes:
        if cplusplus: return 'void *'
        return ''

    cl = lcp.pop()

    if check_ret and cl.mv.module.ident == 'collections' and cl.ident == 'defaultdict':
        print '*WARNING* defaultdicts are returned as dicts'
    elif check_extmod and cl.mv.module.builtin and not (cl.mv.module.ident == 'builtin' and cl.ident in ['int_', 'float_', 'complex', 'str_', 'list', 'tuple', 'tuple2', 'dict', 'set', 'frozenset', 'none', 'bool_']) and not (cl.mv.module.ident == 'collections' and cl.ident == 'defaultdict'):
        raise ExtmodError()

    # --- simple built-in types
    if cl.ident in ['int_', 'float_', 'bool_', 'complex']:
        return conv[cl.ident]
    elif cl.ident == 'str_':
        return 'str'+ptr
    elif cl.ident == 'none':
        if cplusplus: return 'void *'
        return 'None'

    # --- namespace prefix
    namespace = ''
    if cl.module not in [getmv().module, getgx().modules['builtin']]:
        if cplusplus: namespace = cl.module.full_path()+'::'
        else: namespace = '::'.join(cl.module.mod_path)+'::'
        if cplusplus:
            getmv().module.prop_includes.add(cl.module)

    template_vars = cl.tvar_names()
    if template_vars:
        subtypes = []
        for tvar in template_vars:
            vartypes = types_var_types(types, tvar)
            ts = typestrnew(vartypes, cplusplus, node, check_extmod, depth+1, tuple_check=tuple_check)
            if tvar == var:
                return ts
            if [t[0] for t in vartypes if isinstance(t[0], function)]:
                ident = cl.ident
                if ident == 'tuple2': ident = 'tuple'
                error("'%s' instance containing function reference" % ident, node, warning=True) # XXX test
            subtypes.append(ts)
    else:
        if cl.ident in getgx().cpp_keywords:
            return namespace+getgx().ss_prefix+map(cl.ident)
        return namespace+map(cl.ident)

    ident = cl.ident

    # --- binary tuples
    if ident == 'tuple2':
        if subtypes[0] == subtypes[1]:
            ident, subtypes = 'tuple', [subtypes[0]]
    if ident == 'tuple2' and not cplusplus:
        ident = 'tuple'
    elif ident == 'tuple' and cplusplus:
        return namespace+'tuple2'+sep[0]+subtypes[0]+', '+subtypes[0]+sep[1]+ptr

    if ident in ['frozenset', 'pyset'] and cplusplus:
        ident = 'set'

    if ident in getgx().cpp_keywords:
        ident = getgx().ss_prefix+ident

    # --- final type representation
    return namespace+ident+sep[0]+', '.join(subtypes)+sep[1]+ptr

def incompatible_assignment_rec(argtypes, formaltypes, depth=0):
    if depth == 10:
        return False
    argclasses = types_classes(argtypes)
    formalclasses = types_classes(formaltypes)
    inttype = (defclass('int_'),0)
    booltype = (defclass('bool_'),0)
    floattype = (defclass('float_'),0)

    # int -> float
    if depth > 0 and (argtypes == set([inttype]) and floattype in formaltypes):
        return True

    # bool -> int
    if depth > 0 and (argtypes == set([booltype]) and inttype in formaltypes):
        return True

    # void * -> non-pointer
    if not argclasses and [cl for cl in formalclasses if cl.ident in ['int_', 'float_', 'bool_', 'complex']]:
        return True

    # None -> anything
    if len(argclasses) == 1 and defclass('none') in argclasses:
        return False

    # recurse on subvars
    lcp = lowest_common_parents(polymorphic_cl(formalclasses))
    if len(lcp) != 1: # XXX
        return False
    tvars = lcp[0].tvar_names()
    for tvar in tvars:
        argvartypes = types_var_types(argtypes, tvar)
        formalvartypes = types_var_types(formaltypes, tvar)
        if incompatible_assignment_rec(argvartypes, formalvartypes, depth+1):
            return True
    return False
