'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

typestr.py: generate type declarations

'''
import logging

from . import error
from . import python
from . import infer

logger = logging.getLogger('typestr')


class ExtmodError(Exception):
    pass


def types_var_types(gx, types, varname):
    subtypes = set()
    for t in types:
        if not varname in t[0].vars:
            continue
        var = t[0].vars[varname]
        if (var, t[1], 0) in gx.cnode:
            subtypes.update(gx.cnode[var, t[1], 0].types())
    return subtypes


def types_classes(types):
    return set(t[0] for t in types if isinstance(t[0], python.Class))


def unboxable(gx, types):
    if not isinstance(types, set):
        types = infer.inode(gx, types).types()
    classes = set(t[0] for t in types)

    if [cl for cl in classes if cl.ident not in ['int_', 'float_', 'bool_', 'complex']]:
        return None
    else:
        if classes:
            return classes.pop().ident
        return None


def singletype(gx, node, type):
    types = [t[0] for t in infer.inode(gx, node).types()]
    if len(types) == 1 and isinstance(types[0], type):
        return types[0]


def singletype2(types, type):
    ltypes = list(types)
    if len(types) == 1 and isinstance(ltypes[0][0], type):
        return ltypes[0][0]


def polymorphic_t(gx, types):
    return polymorphic_cl(gx, (t[0] for t in types))


def polymorphic_cl(gx, classes):
    cls = set(cl for cl in classes)
    if len(cls) > 1 and python.def_class(gx, 'none') in cls and not python.def_class(gx, 'int_') in cls and not python.def_class(gx, 'float_') in cls and not python.def_class(gx, 'bool_') in cls:
        cls.remove(python.def_class(gx, 'none'))
    if python.def_class(gx, 'tuple2') in cls and python.def_class(gx, 'tuple') in cls:  # XXX hmm
        cls.remove(python.def_class(gx, 'tuple2'))
    return cls


# --- determine lowest common parent classes (inclusive)
def lowest_common_parents(classes):
    classes = [cl for cl in classes if isinstance(cl, python.Class)]

    # collect all possible parent classes
    parents = set()
    for parent in classes:
        while parent:
            parent.lcpcount = 0
            parents.add(parent)
            if parent.bases:
                parent = parent.bases[0]
            else:
                parent = None

    # count how many descendants in 'classes' each has
    for parent in classes:
        while parent:
            parent.lcpcount += 1
            if parent.bases:
                parent = parent.bases[0]
            else:
                parent = None

    # remove those that don't add anything
    useless = set()
    for parent in parents:
        orig = parent
        while parent:
            if parent != orig:
                if parent.lcpcount > orig.lcpcount:
                    useless.add(orig)
                elif parent.lcpcount == orig.lcpcount:
                    useless.add(parent)
            if parent.bases:
                parent = parent.bases[0]
            else:
                parent = None
    return list(parents - useless)


def nodetypestr(gx, node, parent=None, cplusplus=True, check_extmod=False, check_ret=False, var=None, mv=None):  # XXX minimize
    if cplusplus and isinstance(node, python.Variable) and node.looper:  # XXX to declaredefs?
        return nodetypestr(gx, node.looper, None, cplusplus, mv=mv)[:-2] + '::for_in_loop '
    if cplusplus and isinstance(node, python.Variable) and node.wopper:  # XXX to declaredefs?
        ts = nodetypestr(gx, node.wopper, None, cplusplus, mv=mv)
        if ts.startswith('dict<'):
            return 'dictentry' + ts[4:]
    types = gx.merged_inh[node]
    return typestr(gx, types, None, cplusplus, node, check_extmod, 0, check_ret, var, mv=mv)


def typestr(gx, types, parent=None, cplusplus=True, node=None, check_extmod=False, depth=0, check_ret=False, var=None, tuple_check=False, mv=None):
    try:
        ts = typestrnew(gx, types, cplusplus, node, check_extmod, depth, check_ret, var, tuple_check, mv=mv)
    except RuntimeError:
        if not mv.module.builtin and isinstance(node, python.Variable) and not node.name.startswith('__'):  # XXX startswith
            if node.parent:
                varname = repr(node)
            else:
                varname = "'%s'" % node.name
            error.error("Variable %s has dynamic (sub)type" % varname, gx, node, warning=True)
        ts = 'pyobj *'
    if cplusplus:
        if not ts.endswith('*'):
            ts += ' '
        return ts
    return '[' + ts + ']'


def dynamic_variable_error(gx, node, types, conv2):
    if not node.name.startswith('__'):  # XXX startswith
        classes = polymorphic_cl(gx, types_classes(types))
        lcp = lowest_common_parents(classes)
        if node.parent:
            varname = "%s" % node
        else:
            varname = "'%s'" % node
        if [t for t in types if isinstance(t[0], python.Function)]:
            error.error("Variable %s has dynamic (sub)type: {%s, function}" % (varname, ', '.join(sorted(conv2.get(cl.ident, cl.ident) for cl in lcp))), gx, node, warning=True)
        else:
            error.error("Variable %s has dynamic (sub)type: {%s}" % (varname, ', '.join(sorted(conv2.get(cl.ident, cl.ident) for cl in lcp))), gx, node, warning=True)


def typestrnew(gx, types, cplusplus=True, node=None, check_extmod=False, depth=0, check_ret=False, var=None, tuple_check=False, mv=None):
    if depth == 10:
        raise RuntimeError()

    # --- annotation or c++ code
    conv1 = {'int_': '__ss_int', 'float_': 'double', 'str_': 'str', 'none': 'int', 'bool_': '__ss_bool', 'complex': 'complex'}
    conv2 = {'int_': 'int', 'float_': 'float', 'str_': 'str', 'class_': 'class', 'none': 'None', 'bool_': 'bool', 'complex': 'complex'}
    if cplusplus:
        sep, ptr, conv = '<>', ' *', conv1
    else:
        sep, ptr, conv = '()', '', conv2

    def map(ident):
        if cplusplus:
            return ident + ' *'
        return conv.get(ident, ident)

    anon_funcs = set(t[0] for t in types if isinstance(t[0], python.Function))
    static_cls = set(t[0] for t in types if isinstance(t[0], python.StaticClass))
    if (anon_funcs or static_cls) and check_extmod:
        raise ExtmodError()
    if anon_funcs:
        if [t for t in types if not isinstance(t[0], python.Function) and t[0] is not python.def_class(gx, 'none')]:
            if isinstance(node, python.Variable):
                dynamic_variable_error(gx, node, types, conv2)
            else:
                error.error("function mixed with non-function", gx, node, warning=True)
        f = anon_funcs.pop()
        if f.mv != mv:
            return f.mv.module.full_path() + '::' + 'lambda%d' % f.lambdanr
        return 'lambda%d' % f.lambdanr

    classes = polymorphic_cl(gx, types_classes(types))
    lcp = lowest_common_parents(classes)

    # --- multiple parent classes
    if len(lcp) > 1:
        if set(lcp) == set([python.def_class(gx, 'int_'), python.def_class(gx, 'float_')]):
            return conv['float_']
        elif not node or (infer.inode(gx,node).mv and infer.inode(gx, node).mv.module.builtin):
            if python.def_class(gx, 'complex') in lcp:  # XXX
                return conv['complex']
            elif python.def_class(gx, 'float_') in lcp:
                return conv['float_']
            elif python.def_class(gx, 'int_') in lcp:
                return conv['int_']
            else:
                return 'pyobj *'
        elif isinstance(node, python.Variable):
            dynamic_variable_error(gx, node, types, conv2)
            return 'pyobj *'
        elif node not in gx.bool_test_only:
            if tuple_check:
                error.error("tuple with length > 2 and different types of elements", gx, node, warning=True, mv=mv)
            else:
                error.error("expression has dynamic (sub)type: {%s}" % ', '.join(sorted(conv2.get(cl.ident, cl.ident) for cl in lcp)), gx, node, warning=True)
    elif not classes:
        if cplusplus:
            return 'void *'
        return ''

    cl = lcp.pop()

    if check_ret and cl.mv.module.ident == 'collections' and cl.ident == 'defaultdict':
        logger.warn('defaultdicts are returned as dicts')
    elif check_extmod and cl.mv.module.builtin and not (cl.mv.module.ident == 'builtin' and cl.ident in ['int_', 'float_', 'complex', 'str_', 'bytes_', 'list', 'tuple', 'tuple2', 'dict', 'set', 'frozenset', 'none', 'bool_']) and not (cl.mv.module.ident == 'collections' and cl.ident == 'defaultdict'):
        raise ExtmodError()

    # --- simple built-in types
    if cl.ident in ['int_', 'float_', 'bool_', 'complex']:
        return conv[cl.ident]
    elif cl.ident == 'str_':
        return cl.ident[:-1] + ptr
    elif cl.ident in ('bytes_', 'bytearray'):
        return 'bytes' + ptr
    elif cl.ident == 'none':
        if cplusplus:
            return 'void *'
        return 'None'

    # --- namespace prefix
    namespace = ''
    if cl.module not in [mv.module, gx.modules['builtin']]:
        if cplusplus:
            namespace = cl.module.full_path() + '::'
        else:
            namespace = '::'.join(cl.module.name_list) + '::'
        if cplusplus:
            mv.module.prop_includes.add(cl.module)

    template_vars = cl.tvar_names()
    if template_vars:
        subtypes = []
        for tvar in template_vars:
            vartypes = types_var_types(gx, types, tvar)
            ts = typestrnew(gx, vartypes, cplusplus, node, check_extmod, depth + 1, tuple_check=tuple_check, mv=mv)
            if tvar == var:
                return ts
            if [t[0] for t in vartypes if isinstance(t[0], python.Function)]:
                ident = cl.ident
                if ident == 'tuple2':
                    ident = 'tuple'
                error.error("'%s' instance containing function reference" % ident, gx, node, warning=True)  # XXX test
            subtypes.append(ts)
    else:
        if cl.ident in gx.cpp_keywords:
            return namespace + gx.ss_prefix + map(cl.ident)
        return namespace + map(cl.ident)

    ident = cl.ident

    # --- binary tuples
    if ident == 'tuple2':
        if subtypes[0] == subtypes[1]:
            ident, subtypes = 'tuple', [subtypes[0]]
    if ident == 'tuple2' and not cplusplus:
        ident = 'tuple'
    elif ident == 'tuple' and cplusplus:
        return namespace + 'tuple2' + sep[0] + subtypes[0] + ', ' + subtypes[0] + sep[1] + ptr

    if ident in ['frozenset', 'pyset'] and cplusplus:
        ident = 'set'

    if ident in gx.cpp_keywords:
        ident = gx.ss_prefix + ident

    # --- final type representation
    return namespace + ident + sep[0] + ', '.join(subtypes) + sep[1] + ptr


def incompatible_assignment_rec(gx, argtypes, formaltypes, depth=0):
    if depth == 10:
        return False
    argclasses = types_classes(argtypes)
    formalclasses = types_classes(formaltypes)
    inttype = (python.def_class(gx, 'int_'), 0)
    booltype = (python.def_class(gx, 'bool_'), 0)
    floattype = (python.def_class(gx, 'float_'), 0)

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
    if len(argclasses) == 1 and python.def_class(gx, 'none') in argclasses:
        return False

    # recurse on subvars
    lcp = lowest_common_parents(polymorphic_cl(gx, formalclasses))
    if len(lcp) != 1:  # XXX
        return False
    tvars = lcp[0].tvar_names()
    for tvar in tvars:
        argvartypes = types_var_types(gx, argtypes, tvar)
        formalvartypes = types_var_types(gx, formaltypes, tvar)
        if incompatible_assignment_rec(gx, argvartypes, formalvartypes, depth + 1):
            return True
    return False
