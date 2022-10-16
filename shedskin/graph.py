'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2022 Mark Dufour; License GNU GPL version 3 (See LICENSE)

graph.py: build constraint graph used in dataflow analysis

constraint graph: graph along which possible types 'flow' during an 'abstract execution' of a program (a dataflow analysis). consider the assignment statement 'a = b'. it follows that the set of possible types of b is smaller than or equal to that of a (a constraint). we can determine possible types of a, by 'flowing' the types from b to a, in other words, along the constraint.

constraint graph nodes are stored in gx.cnode, and the set of types of for each node in gx.types. nodes are identified by an AST Node, and two integers. the integers are used in py to duplicate parts of the constraint graph along two dimensions. in the initial constraint graph, these integers are always 0.

class ModuleVisitor: inherits visitor pattern from ast.NodeVisitor, to recursively generate constraints for each syntactical Python construct. for example, the visitFor method is called in case of a for-loop. temporary variables are introduced in many places, to enable translation to a lower-level language.

parse_module(): locate module by name (e.g. 'os.path'), and use ModuleVisitor if not cached

'''
import copy
import os
import re
import sys

try:
    # python 2
    from compiler.ast import Const, AssTuple, AssList, From as ImportFrom, Add, ListCompFor, \
        UnaryAdd, Import, Bitand, Assign, FloorDiv, Not, Mod, AssAttr, \
        Keyword, GenExpr as GeneratorExp, LeftShift, AssName, Div, Or, Lambda, And, CallFunc as Call, \
        Global, Slice, RightShift, Sub, Getattr as Attribute, Dict, Ellipsis, Mul, \
        Subscript, Function as FunctionDef, Return, Power, Bitxor, Class as ClassDef, Name, List, \
        Sliceobj, Tuple, Pass, UnarySub, Bitor, ListComp, TryExcept as Try, With

except ModuleNotFoundError:
    # python 3
    from ast import Attribute, ClassDef, FunctionDef, Global, ListComp, \
        GeneratorExp, Assign, Try, With, Import, ImportFrom, And, Or, Not, \
        Constant, Return, Name, Call

from .compat import NodeVisitor, parse_expr, getChildNodes, \
    filter_statements, filter_rec, get_assnames, get_statements, is_const, \
    const_value, get_id, get_defaults, get_body, get_func, attr_value, \
    attr_attr

from .error import error
from .infer import inode, in_out, CNode, default_var, register_temp_var
from .python import StaticClass, lookup_func, Function, is_zip2, \
    lookup_class, is_method, is_literal, is_enum, lookup_var, assign_rec, \
    Class, is_property_setter, is_fastfor, aug_msg, is_isinstance, \
    Module, def_class, parse_file, find_module


# --- global variable mv
_mv = None


def setmv(mv):
    global _mv
    _mv = mv
    return _mv


def getmv():
    return _mv


class FakeAttribute3(Attribute):
    pass


class FakeAttribute2(Attribute):
    pass


class FakeAttribute(Attribute):
    pass  # XXX ugly


def check_redef(gx, node, s=None, onlybuiltins=False):  # XXX to modvisitor, rewrite
    if not getmv().module.builtin:
        existing = [getmv().ext_classes, getmv().ext_funcs]
        if not onlybuiltins:
            existing += [getmv().classes, getmv().funcs]
        for whatsit in existing:
            if s is not None:
                name = s
            else:
                name = node.name
            if name in whatsit:
                error("function/class redefinition is not supported", gx, node, mv=getmv())


# --- maintain inheritance relations between copied AST nodes
def inherit_rec(gx, original, copy, mv):
    gx.inheritance_relations.setdefault(original, []).append(copy)
    gx.inherited.add(copy)
    gx.parent_nodes[copy] = original

    for (a, b) in zip(getChildNodes(original), getChildNodes(copy)):
        inherit_rec(gx, a, b, mv)


def register_node(node, func):
    if func:
        func.registered.append(node)


def slice_nums(nodes):
    nodes2 = []
    x = 0
    for i, n in enumerate(nodes):
        if not n or (isinstance(n, Const) and n.value is None):
            nodes2.append(Const(0))
        else:
            nodes2.append(n)
            x |= (1 << i)
    return [Const(x)] + nodes2


# --- module visitor; analyze program, build constraint graph
class ModuleVisitor(NodeVisitor):
    def __init__(self, module, gx):
        self.module = module
        self.gx = gx
        self.classes = {}
        self.funcs = {}
        self.globals = {}
        self.exc_names = {}
        self.current_with_vars = []

        self.lambdas = {}
        self.imports = {}
        self.fake_imports = {}
        self.ext_classes = {}
        self.ext_funcs = {}
        self.lambdaname = {}
        self.lwrapper = {}
        self.tempcount = self.gx.tempcount
        self.callfuncs = []
        self.for_in_iters = []
        self.listcomps = []
        self.defaults = {}
        self.importnodes = []

    def visit(self, node, *args):
        if (node, 0, 0) not in self.gx.cnode:
            NodeVisitor.visit(self, node, *args)

    def fake_func(self, node, objexpr, attrname, args, func):
        if (node, 0, 0) in self.gx.cnode:  # XXX
            newnode = self.gx.cnode[node, 0, 0]
        else:
            newnode = CNode(self.gx, node, parent=func, mv=getmv())
            self.gx.types[newnode] = set()

        fakefunc = Call(Attribute(objexpr, attrname), args)
        fakefunc.lineno = objexpr.lineno
        self.visit(fakefunc, func)
        self.add_constraint((inode(self.gx, fakefunc), newnode), func)

        inode(self.gx, objexpr).fakefunc = fakefunc
        return fakefunc

    # simple heuristic for initial list split: count nesting depth, first constant child type
    def list_type(self, node):
        count = 0
        child = node
        while isinstance(child, (List, ListComp)):
            if not getChildNodes(child):
                return None
            child = getChildNodes(child)[0]
            count += 1

        if isinstance(child, (UnarySub, UnaryAdd)):
            child = child.expr

        if isinstance(child, Call) and isinstance(child.node, Name):
            map = {'int': int, 'str': str, 'float': float}
            if child.node.name in ('range'):  # ,'xrange'):
                count, child = count + 1, int
            elif child.node.name in map:
                child = map[child.node.name]
            elif child.node.name in (cl.ident for cl in self.gx.allclasses) or child.node.name in getmv().classes:  # XXX getmv().classes
                child = child.node.name
            else:
                if count == 1:
                    return None
                child = None
        elif isinstance(child, Const):
            child = type(child.value)
        elif isinstance(child, Name) and child.name in ('True', 'False'):
            child = bool
        elif isinstance(child, Tuple):
            child = tuple
        elif isinstance(child, Dict):
            child = dict
        else:
            if count == 1:
                return None
            child = None

        self.gx.list_types.setdefault((count, child), len(self.gx.list_types) + 2)
        # print 'listtype', node, self.gx.list_types[count, child]
        return self.gx.list_types[count, child]

    def instance(self, node, cl, func=None):
        if (node, 0, 0) in self.gx.cnode:  # XXX to create_node() func
            newnode = self.gx.cnode[node, 0, 0]
        else:
            newnode = CNode(self.gx, node, parent=func, mv=getmv())

        newnode.constructor = True

        if cl.ident in ['int_', 'float_', 'str_', 'none', 'class_', 'bool_']:
            self.gx.types[newnode] = set([(cl, cl.dcpa - 1)])
        else:
            if cl.ident == 'list' and self.list_type(node):
                self.gx.types[newnode] = set([(cl, self.list_type(node))])
            else:
                self.gx.types[newnode] = set([(cl, cl.dcpa)])

    def constructor(self, node, classname, func):
        cl = def_class(self.gx, classname)

        self.instance(node, cl, func)
        default_var(self.gx, 'unit', cl)

        if classname in ['list', 'tuple'] and not node.nodes:
            self.gx.empty_constructors.add(node)  # ifa disables those that flow to instance variable assignments

        # --- internally flow binary tuples
        if cl.ident == 'tuple2':
            default_var(self.gx, 'first', cl)
            default_var(self.gx, 'second', cl)
            elem0, elem1 = node.nodes

            self.visit(elem0, func)
            self.visit(elem1, func)

            self.add_dynamic_constraint(node, elem0, 'unit', func)
            self.add_dynamic_constraint(node, elem1, 'unit', func)

            self.add_dynamic_constraint(node, elem0, 'first', func)
            self.add_dynamic_constraint(node, elem1, 'second', func)

            return

        # --- add dynamic children constraints for other types
        if classname == 'dict':  # XXX filter children
            default_var(self.gx, 'unit', cl)
            default_var(self.gx, 'value', cl)

            for child in getChildNodes(node):
                self.visit(child, func)

            for (key, value) in node.items:  # XXX filter
                self.add_dynamic_constraint(node, key, 'unit', func)
                self.add_dynamic_constraint(node, value, 'value', func)
        else:
            for child in node.nodes:
                self.visit(child, func)

            for child in self.filter_redundant_children(node):
                self.add_dynamic_constraint(node, child, 'unit', func)

    # --- for compound list/tuple/dict constructors, we only consider a single child node for each subtype
    def filter_redundant_children(self, node):
        done = set()
        nonred = []
        for child in node.nodes:
            type = self.child_type_rec(child)
            if not type or not type in done:
                done.add(type)
                nonred.append(child)

        return nonred

    # --- determine single constructor child node type, used by the above
    def child_type_rec(self, node):
        if isinstance(node, (UnarySub, UnaryAdd)):
            node = node.expr

        if isinstance(node, (List, Tuple)):
            if isinstance(node, List):
                cl = def_class(self.gx, 'list')
            elif len(node.nodes) == 2:
                cl = def_class(self.gx, 'tuple2')
            else:
                cl = def_class(self.gx, 'tuple')

            merged = set()
            for child in node.nodes:
                merged.add(self.child_type_rec(child))

            if len(merged) == 1:
                return (cl, merged.pop())

        elif isinstance(node, Const):
            return (list(inode(self.gx, node).types())[0][0],)

    # --- add dynamic constraint for constructor argument, e.g. '[expr]' becomes [].__setattr__('unit', expr)
    def add_dynamic_constraint(self, parent, child, varname, func):
        # print 'dynamic constr', child, parent

        self.gx.assign_target[child] = parent
        cu = Const(varname)
        self.visit(cu, func)
        fakefunc = Call(FakeAttribute2(parent, '__setattr__'), [cu, child])
        self.visit(fakefunc, func)

        fakechildnode = CNode(self.gx, (child, varname), parent=func, mv=getmv())  # create separate 'fake' CNode per child, so we can have multiple 'callfuncs'
        self.gx.types[fakechildnode] = set()

        self.add_constraint((inode(self.gx, parent), fakechildnode), func)  # add constraint from parent to fake child node. if parent changes, all fake child nodes change, and the callfunc for each child node is triggered
        fakechildnode.callfuncs.append(fakefunc)

    # --- add regular constraint to function
    def add_constraint(self, constraint, func):
        in_out(constraint[0], constraint[1])
        self.gx.constraints.add(constraint)
        while isinstance(func, Function) and func.listcomp:
            func = func.parent  # XXX
        if isinstance(func, Function):
            func.constraints.add(constraint)

    def struct_unpack(self, rvalue, func):
        if isinstance(rvalue, Call):
            if isinstance(rvalue.node, Attribute) and isinstance(rvalue.node.expr, Name) and rvalue.node.expr.name == 'struct' and rvalue.node.attrname == 'unpack' and lookup_var('struct', func, mv=self).imported:  # XXX imported from where?
                return True
            elif isinstance(rvalue.node, Name) and rvalue.node.name == 'unpack' and 'unpack' in self.ext_funcs and not lookup_var('unpack', func, mv=self):  # XXX imported from where?
                return True

    def struct_info(self, node, func):
        if isinstance(node, Name):
            var = lookup_var(node.name, func, mv=self)  # XXX fwd ref?
            if not var or len(var.const_assign) != 1:
                error('non-constant format string', self.gx, node, mv=self)
            error('assuming constant format string', self.gx, node, mv=self, warning=True)
            fmt = var.const_assign[0].value
        elif isinstance(node, Const):
            fmt = node.value
        else:
            error('non-constant format string', self.gx, node, mv=self)
        char_type = dict(['xx', 'cs', 'bi', 'Bi', '?b', 'hi', 'Hi', 'ii', 'Ii', 'li', 'Li', 'qi', 'Qi', 'ff', 'df', 'ss', 'ps'])
        ordering = '@'
        if fmt and fmt[0] in '@<>!=':
            ordering, fmt = fmt[0], fmt[1:]
        result = []
        digits = ''
        for i, c in enumerate(fmt):
            if c.isdigit():
                digits += c
            elif c in char_type:
                rtype = {'i': 'int', 's': 'str', 'b': 'bool', 'f': 'float', 'x': 'pad'}[char_type[c]]
                if rtype == 'str' and c != 'c':
                    result.append((ordering, c, 'str', int(digits or '1')))
                elif digits == '0':
                    result.append((ordering, c, rtype, 0))
                else:
                    result.extend(int(digits or '1') * [(ordering, c, rtype, 1)])
                digits = ''
            else:
                error('bad or unsupported char in struct format: ' + repr(c), self.gx, node, mv=self)
                digits = ''
        return result

    def struct_faketuple(self, info):
        result = []
        for o, c, t, d in info:
            if d != 0 or c == 's':
                if t == 'int':
                    result.append(Const(1))
                elif t == 'str':
                    result.append(Const(''))
                elif t == 'float':
                    result.append(Const(1.0))
                elif t == 'bool':
                    result.append(Name('True'))
        return Tuple(result)

    def visit_Exec(self, node, func=None):
        error("'exec' is not supported", self.gx, node, mv=getmv())

    def visit_GenExpr(self, node, func=None):
        newnode = CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set()
        lc = ListComp(node.code.expr, [ListCompFor(qual.assign, qual.iter, qual.ifs, qual.lineno) for qual in node.code.quals], lineno=node.lineno)
        register_node(lc, func)
        self.gx.genexp_to_lc[node] = lc
        self.visit(lc, func)
        self.add_constraint((inode(self.gx, lc), newnode), func)

    def visit_statements(self, statements, func=None):
        comments = []
        for stmt in statements:
            self.bool_test_add(stmt)

            if is_const(stmt) and type(const_value(stmt)) == str:
                comments.append(const_value(stmt))
            elif comments:
                self.gx.comments[stmt] = comments
                comments = []

            self.visit(stmt, func)

    def visit_Module(self, node):
        # --- bootstrap built-in classes
        if self.module.ident == 'builtin':
            for dummy in self.gx.builtins:
                self.visit(parse_expr('class %s: pass' % dummy))

        if self.module.ident != 'builtin':
            n = parse_expr('from builtin import *')
            getmv().importnodes.append(n)
            self.visit(n)

        # --- __name__
        if self.module.ident != 'builtin':
            namevar = default_var(self.gx, '__name__', None, mv=getmv())
            self.gx.types[inode(self.gx, namevar)] = set([(def_class(self.gx, 'str_'), 0)])

        self.forward_references(node)

        # --- visit statements
        statements = get_statements(get_body(node))
        for stmt in statements:
            if isinstance(stmt, (Import, ImportFrom)):
                getmv().importnodes.append(stmt)
        self.visit_statements(statements, None)

        # --- register classes
        for cl in getmv().classes.values():
            self.gx.allclasses.add(cl)

        # --- inheritance expansion

        # determine base classes
        for cl in self.classes.values():
            for base in cl.node.bases:
                if not (isinstance(base, Name) and base.name == 'object'):
                    ancestor = lookup_class(base, getmv())
                    cl.bases.append(ancestor)
                    ancestor.children.append(cl)

        # for each base class, duplicate methods
        for cl in self.classes.values():
            for ancestor in cl.ancestors_upto(None)[1:]:

                cl.staticmethods.extend(ancestor.staticmethods)
                cl.properties.update(ancestor.properties)

                for func in ancestor.funcs.values():
                    if not func.node or func.inherited:
                        continue

                    ident = func.ident
                    if ident in cl.funcs:
                        ident += ancestor.ident + '__'

                    # deep-copy AST function nodes
                    func_copy = copy.deepcopy(func.node)
                    inherit_rec(self.gx, func.node, func_copy, func.mv)
                    tempmv, mv = getmv(), func.mv
                    setmv(mv)
                    self.visit_FunctionDef(func_copy, cl, inherited_from=ancestor)
                    mv = tempmv
                    setmv(mv)

                    # maintain relation with original
                    self.gx.inheritance_relations.setdefault(func, []).append(cl.funcs[ident])
                    cl.funcs[ident].inherited = func.node
                    cl.funcs[ident].inherited_from = func
                    func_copy.name = ident

                    if ident == func.ident:
                        cl.funcs[ident + ancestor.ident + '__'] = cl.funcs[ident]

    def forward_references(self, node):
        getmv().classnodes = []

        # classes
        for n in filter_statements(node, ClassDef):
            check_redef(self.gx, n)
            getmv().classnodes.append(n)
            newclass = Class(self.gx, n, getmv())
            self.classes[n.name] = newclass
            getmv().classes[n.name] = newclass
            newclass.module = self.module
            newclass.parent = StaticClass(newclass, getmv())

            # methods
            for m in filter_statements(n, FunctionDef):
                if hasattr(m, 'decorators') and m.decorators and [dec for dec in m.decorators if is_property_setter(dec)]:
                    m.name = m.name + '__setter__'
                if m.name in newclass.funcs:  # and func.ident not in ['__getattr__', '__setattr__']: # XXX
                    error("function/class redefinition is not allowed", self.gx, m, mv=getmv())
                func = Function(self.gx, m, newclass, mv=getmv())
                newclass.funcs[func.ident] = func
                self.set_default_vars(m, func)

        # functions
        getmv().funcnodes = []
        for n in filter_statements(node, FunctionDef):
            check_redef(self.gx, n)
            getmv().funcnodes.append(n)
            func = getmv().funcs[n.name] = Function(self.gx, n, mv=getmv())
            self.set_default_vars(n, func)

        # global variables XXX visitGlobal
        for name in self.local_assignments(node, global_=True):
            default_var(self.gx, name, None, mv=getmv())

    def set_default_vars(self, node, func):
        globals = set(self.get_globals(node))
        for name in self.local_assignments(node):
            if name not in globals:
                default_var(self.gx, name, func)

    def get_globals(self, node):
        if isinstance(node, Global):
            result = node.names
        else:
            result = []
            for child in getChildNodes(node):
                result.extend(self.get_globals(child))
        return result

    def local_assignments(self, node, global_=False):
        result = []
        if global_ and isinstance(node, (ClassDef, FunctionDef)):
            pass
        elif isinstance(node, (ListComp, GeneratorExp)):
            pass
        elif isinstance(node, Assign):
            result.extend(get_assnames(node))
        else:
            # Try-Excepts introduce a new small scope with the exception name,
            # so we skip it here.
            if isinstance(node, Try):
                children = list(getChildNodes(node.body))
                for handler in node.handlers:
                    children.extend(getChildNodes(handler[2]))
                if node.else_:
                    children.extend(getChildNodes(node.else_))
            elif isinstance(node, With):
                children = getChildNodes(node.body)
            else:
                children = getChildNodes(node)

            for child in children:
                result.extend(self.local_assignments(child, global_))

        return result

    def visit_Import(self, node, func=None):
        if not node in getmv().importnodes:
            error("please place all imports (no 'try:' etc) at the top of the file", self.gx, node, mv=getmv())

        for (name, pseudonym) in node.names:
            if pseudonym:
                # --- import a.b as c: don't import a
                self.import_module(name, pseudonym, node, False)
            else:
                self.import_modules(name, node, False)

    def import_modules(self, name, node, fake):
        # --- import a.b.c: import a, then a.b, then a.b.c
        split = name.split('.')
        module = getmv().module
        for i in range(len(split)):
            subname = '.'.join(split[:i + 1])
            parent = module
            module = self.import_module(subname, subname, node, fake)
            if module.ident not in parent.mv.imports:  # XXX
                if not fake:
                    parent.mv.imports[module.ident] = module
        return module

    def import_module(self, name, pseudonym, node, fake):
        module = self.analyze_module(name, pseudonym, node, fake)
        if not fake:
            var = default_var(self.gx, pseudonym or name, None, mv=getmv())
            var.imported = True
            self.gx.types[inode(self.gx, var)] = set([(module, 0)])
        return module

    def visit_ImportFrom(self, node, parent=None):
        if not node in getmv().importnodes:  # XXX use (func, node) as parent..
            error("please place all imports (no 'try:' etc) at the top of the file", self.gx, node, mv=getmv())
        if hasattr(node, 'level') and node.level:
            error("relative imports are not supported", self.gx, node, mv=getmv())

        if node.module == '__future__':
            for name, _ in node.names:
                if name not in ['with_statement', 'print_function']:
                    error("future '%s' is not yet supported" % name, self.gx, node, mv=getmv())
            return

        module = self.import_modules(node.module, node, True)
        self.gx.from_module[node] = module

        for name, pseudonym in node.names:
            if name == '*':
                self.ext_funcs.update(module.mv.funcs)
                self.ext_classes.update(module.mv.classes)
                for import_name, import_module in module.mv.imports.items():
                    var = default_var(self.gx, import_name, None, mv=getmv())  # XXX merge
                    var.imported = True
                    self.gx.types[inode(self.gx, var)] = set([(import_module, 0)])
                    self.imports[import_name] = import_module
                for name, extvar in module.mv.globals.items():
                    if not extvar.imported and not name in ['__name__']:
                        var = default_var(self.gx, name, None, mv=getmv())  # XXX merge
                        var.imported = True
                        self.add_constraint((inode(self.gx, extvar), inode(self.gx, var)), None)
                continue

            path = module.path
            pseudonym = pseudonym or name
            if name in module.mv.funcs:
                self.ext_funcs[pseudonym] = module.mv.funcs[name]
            elif name in module.mv.classes:
                self.ext_classes[pseudonym] = module.mv.classes[name]
            elif name in module.mv.globals and not module.mv.globals[name].imported:  # XXX
                extvar = module.mv.globals[name]
                var = default_var(self.gx, pseudonym, None, mv=getmv())
                var.imported = True
                self.add_constraint((inode(self.gx, extvar), inode(self.gx, var)), None)
            elif os.path.isfile(os.path.join(path, name + '.py')) or \
                    os.path.isfile(os.path.join(path, name, '__init__.py')):
                modname = '.'.join(module.name_list + [name])
                self.import_module(modname, name, node, False)
            else:
                error("no identifier '%s' in module '%s'" % (name, node.module), self.gx, node, mv=getmv())

    def analyze_module(self, name, pseud, node, fake):
        module = parse_module(name, self.gx, getmv().module, node)
        if not fake:
            self.imports[pseud] = module
        else:
            self.fake_imports[pseud] = module
        return module

    def visit_FunctionDef(self, node, parent=None, is_lambda=False, inherited_from=None):
        if not getmv().module.builtin and (node.varargs or node.kwargs):
            error('argument (un)packing is not supported', self.gx, node, mv=getmv())

        if not parent and not is_lambda and node.name in getmv().funcs:
            func = getmv().funcs[node.name]
        elif isinstance(parent, Class) and not inherited_from and node.name in parent.funcs:
            func = parent.funcs[node.name]
        else:
            func = Function(self.gx, node, parent, inherited_from, mv=getmv())
            if inherited_from:
                self.set_default_vars(node, func)

        if not is_method(func):
            if not getmv().module.builtin and not node in getmv().funcnodes and not is_lambda:
                error("non-global function '%s'" % node.name, self.gx, node, mv=getmv())

        if hasattr(node, 'decorators') and node.decorators:
            for dec in node.decorators.nodes:
                if isinstance(dec, Name) and dec.name == 'staticmethod':
                    parent.staticmethods.append(node.name)
                elif isinstance(dec, Name) and dec.name == 'property':
                    parent.properties[node.name] = [node.name, None]
                elif is_property_setter(dec):
                    parent.properties[dec.expr.name][1] = node.name
                else:
                    error("unsupported type of decorator", self.gx, dec, mv=getmv())

        if parent:
            if not inherited_from and not func.ident in parent.staticmethods and (not func.formals or func.formals[0] != 'self'):
                error("formal arguments of method must start with 'self'", self.gx, node, mv=getmv())
            if not func.mv.module.builtin and func.ident in ['__new__', '__getattr__', '__setattr__', '__radd__', '__rsub__', '__rmul__', '__rdiv__', '__rtruediv__', '__rfloordiv__', '__rmod__', '__rdivmod__', '__rpow__', '__rlshift__', '__rrshift__', '__rand__', '__rxor__', '__ror__', '__iter__', '__call__', '__enter__', '__exit__', '__del__', '__copy__', '__deepcopy__']:
                error("'%s' is not supported" % func.ident, self.gx, node, warning=True, mv=getmv())

        if is_lambda:
            self.lambdas[node.name] = func

        # --- add unpacking statement for tuple formals
        func.expand_args = {}
        for i, formal in enumerate(func.formals):
            if isinstance(formal, tuple):
                tmp = self.temp_var((node, i), func)
                func.formals[i] = tmp.name
                fake_unpack = Assign([self.unpack_rec(formal)], Name(tmp.name))
                func.expand_args[tmp.name] = fake_unpack
                self.visit(fake_unpack, func)

        func.defaults = get_defaults(node)

        for formal in func.formals:
            var = default_var(self.gx, formal, func)
            var.formal_arg = True

        # --- flow return expressions together into single node
        func.retnode = retnode = CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[retnode] = set()
        func.yieldnode = yieldnode = CNode(self.gx, (node, 'yield'), parent=func, mv=getmv())
        self.gx.types[yieldnode] = set()

        # --- statements
        for child in get_statements(get_body(node)):
            self.visit(child, func)

        for i, default in enumerate(func.defaults):
            if not is_literal(default):
                self.defaults[default] = (len(self.defaults), func, i)
            self.visit(default, None)  # defaults are global

        # --- add implicit 'return None' if no return expressions
        if not func.returnexpr:
            func.fakeret = Return(Name('None'))
            self.visit(func.fakeret, func)

        # --- register function
        if isinstance(parent, Class):
            if func.ident not in parent.staticmethods:  # XXX use flag
                default_var(self.gx, 'self', func)
                if func.ident == '__init__' and '__del__' in parent.funcs:  # XXX what if no __init__
                    self.visit(Call(Attribute(Name('self'), '__del__'), []), func)
                    self.gx.gc_cleanup = True
            parent.funcs[func.ident] = func

    def unpack_rec(self, formal):
        if isinstance(formal, str):
            return AssName(formal, 'OP_ASSIGN')
        else:
            return AssTuple([self.unpack_rec(elem) for elem in formal])

    def visit_Lambda(self, node, func=None):
        lambdanr = len(self.lambdas)
        name = '__lambda%d__' % lambdanr
        fakenode = FunctionDef(None, name, node.argnames, node.defaults, node.flags, None, Return(node.code))
        self.visit(fakenode, None, True)
        f = self.lambdas[name]
        f.lambdanr = lambdanr
        self.lambdaname[node] = name
        newnode = CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set([(f, 0)])
        newnode.copymetoo = True

    def visit_And(self, node, func=None):
        self.visit_and_or(node, func)

    def visit_Or(self, node, func=None):
        self.visit_and_or(node, func)

    def visit_and_or(self, node, func):
        newnode = CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set()
        for child in getChildNodes(node):
            if node in self.gx.bool_test_only:
                self.bool_test_add(child)
            self.visit(child, func)
            self.add_constraint((inode(self.gx, child), newnode), func)
            self.temp_var2(child, newnode, func)

    def visit_If(self, node, func=None):
        for test, code in node.tests:
            if is_isinstance(test):
                self.gx.filterstack.append(test.args)
            self.bool_test_add(test)
            faker = Call(Name('bool'), [test])
            self.visit(faker, func)
            self.visit_statements(get_statements(code), func)
            if is_isinstance(test):
                self.gx.filterstack.pop()
        if node.else_:
            self.visit_statements(get_statements(node.else_), func)

    def visit_IfExp(self, node, func=None):
        newnode = CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set()

        for child in getChildNodes(node):
            self.visit(child, func)

        self.add_constraint((inode(self.gx, node.then), newnode), func)
        self.add_constraint((inode(self.gx, node.else_), newnode), func)

    def visit_Global(self, node, func=None):
        func.globals += node.names

    def visit_List(self, node, func=None):
        self.constructor(node, 'list', func)

    def visit_Dict(self, node, func=None):
        self.constructor(node, 'dict', func)
        if node.items:  # XXX library bug
            node.lineno = node.items[0][0].lineno

    def visit_Not(self, node, func=None):
        self.bool_test_add(node.expr)
        newnode = CNode(self.gx, node, parent=func, mv=getmv())
        newnode.copymetoo = True
        self.gx.types[newnode] = set([(def_class(self.gx, 'bool_'), 0)])  # XXX new type?
        self.visit(node.expr, func)

    def visit_Backquote(self, node, func=None):
        self.fake_func(node, node.expr, '__repr__', [], func)

    def visit_Tuple(self, node, func=None):
        if len(node.nodes) == 2:
            self.constructor(node, 'tuple2', func)
        else:
            self.constructor(node, 'tuple', func)

    def visit_Subscript(self, node, func=None):  # XXX merge __setitem__, __getitem__
        if len(node.subs) > 1:
            subscript = Tuple(node.subs)
        else:
            subscript = node.subs[0]

        if isinstance(subscript, Ellipsis):  # XXX also check at setitem
            error('ellipsis is not supported', self.gx, node, mv=getmv())

        if isinstance(subscript, Sliceobj):
            self.slice(node, node.expr, subscript.nodes, func)
        else:
            if node.flags == 'OP_DELETE':
                self.fake_func(node, node.expr, '__delitem__', [subscript], func)
            elif len(node.subs) > 1:
                self.fake_func(node, node.expr, '__getitem__', [subscript], func)
            else:
                ident = '__getitem__'
                self.fake_func(node, node.expr, ident, [subscript], func)

    def visit_Slice(self, node, func=None):
        self.slice(node, node.expr, [node.lower, node.upper, None], func)

    def slice(self, node, expr, nodes, func, replace=None):
        nodes2 = slice_nums(nodes)
        if replace:
            self.fake_func(node, expr, '__setslice__', nodes2 + [replace], func)
        elif node.flags == 'OP_DELETE':
            self.fake_func(node, expr, '__delete__', nodes2, func)
        else:
            self.fake_func(node, expr, '__slice__', nodes2, func)

    def visit_UnarySub(self, node, func=None):
        self.fake_func(node, node.expr, '__neg__', [], func)

    def visit_UnaryAdd(self, node, func=None):
        self.fake_func(node, node.expr, '__pos__', [], func)

    def visit_Compare(self, node, func=None):
        newnode = CNode(self.gx, node, parent=func, mv=getmv())
        newnode.copymetoo = True
        self.gx.types[newnode] = set([(def_class(self.gx, 'bool_'), 0)])  # XXX new type?
        self.visit(node.expr, func)
        msgs = {'<': 'lt', '>': 'gt', 'in': 'contains', 'not in': 'contains', '!=': 'ne', '==': 'eq', '<=': 'le', '>=': 'ge'}
        left = node.expr
        for op, right in node.ops:
            self.visit(right, func)
            msg = msgs.get(op)
            if msg == 'contains':
                self.fake_func(node, right, '__' + msg + '__', [left], func)
            elif msg in ('lt', 'gt', 'le', 'ge'):
                fakefunc = Call(Name('__%s' % msg), [left, right])
                fakefunc.lineno = left.lineno
                self.visit(fakefunc, func)
            elif msg:
                self.fake_func(node, left, '__' + msg + '__', [right], func)
            left = right

        # tempvars, e.g. (t1=fun())
        for term in node.ops[:-1]:
            if not isinstance(term[1], (Name, Const)):
                self.temp_var2(term[1], inode(self.gx, term[1]), func)

    def visit_Bitand(self, node, func=None):
        self.visit_Bitpair(node, aug_msg(node, 'and'), func)

    def visit_Bitor(self, node, func=None):
        self.visit_Bitpair(node, aug_msg(node, 'or'), func)

    def visit_Bitxor(self, node, func=None):
        self.visit_Bitpair(node, aug_msg(node, 'xor'), func)

    def visit_Bitpair(self, node, msg, func=None):
        CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[inode(self.gx, node)] = set()
        left = node.nodes[0]
        for i, right in enumerate(node.nodes[1:]):
            faker = self.fake_func((left, i), left, msg, [right], func)
            left = faker
        self.add_constraint((inode(self.gx, faker), inode(self.gx, node)), func)

    def visit_Add(self, node, func=None):
        self.fake_func(node, node.left, aug_msg(node, 'add'), [node.right], func)

    def visit_Invert(self, node, func=None):
        self.fake_func(node, node.expr, '__invert__', [], func)

    def visit_RightShift(self, node, func=None):
        self.fake_func(node, node.left, aug_msg(node, 'rshift'), [node.right], func)

    def visit_LeftShift(self, node, func=None):
        self.fake_func(node, node.left, aug_msg(node, 'lshift'), [node.right], func)

    def visit_AugAssign(self, node, func=None):  # a[b] += c -> a[b] = a[b]+c, using tempvars to handle sidefx
        newnode = CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set()

        clone = copy.deepcopy(node)
        lnode = node.node

        if isinstance(node.node, Name):
            blah = AssName(clone.node.name, 'OP_ASSIGN')
        elif isinstance(node.node, Attribute):
            blah = AssAttr(clone.node.expr, clone.node.attrname, 'OP_ASSIGN')
        elif isinstance(node.node, Subscript):
            t1 = self.temp_var(node.node.expr, func)
            a1 = Assign([AssName(t1.name, 'OP_ASSIGN')], node.node.expr)
            self.visit(a1, func)
            self.add_constraint((inode(self.gx, node.node.expr), inode(self.gx, t1)), func)

            if len(node.node.subs) > 1:
                subs = Tuple(node.node.subs)
            else:
                subs = node.node.subs[0]
            t2 = self.temp_var(subs, func)
            a2 = Assign([AssName(t2.name, 'OP_ASSIGN')], subs)

            self.visit(a1, func)
            self.visit(a2, func)
            self.add_constraint((inode(self.gx, subs), inode(self.gx, t2)), func)

            inode(self.gx, node).temp1 = t1.name
            inode(self.gx, node).temp2 = t2.name
            inode(self.gx, node).subs = subs

            blah = Subscript(Name(t1.name), 'OP_APPLY', [Name(t2.name)])
            lnode = Subscript(Name(t1.name), 'OP_APPLY', [Name(t2.name)])
        else:
            error('unsupported type of assignment', self.gx, node, mv=getmv())

        if node.op == '-=':
            blah2 = Sub((lnode, node.expr))
        if node.op == '+=':
            blah2 = Add((lnode, node.expr))
        if node.op == '|=':
            blah2 = Bitor((lnode, node.expr))
        if node.op == '&=':
            blah2 = Bitand((lnode, node.expr))
        if node.op == '^=':
            blah2 = Bitxor((lnode, node.expr))
        if node.op == '**=':
            blah2 = Power((lnode, node.expr))
        if node.op == '<<=':
            blah2 = LeftShift((lnode, node.expr))
        if node.op == '>>=':
            blah2 = RightShift((lnode, node.expr))
        if node.op == '%=':
            blah2 = Mod((lnode, node.expr))
        if node.op == '*=':
            blah2 = Mul((lnode, node.expr))
        if node.op == '/=':
            blah2 = Div((lnode, node.expr))
        if node.op == '//=':
            blah2 = FloorDiv((lnode, node.expr))

        blah2.augment = True

        assign = Assign([blah], blah2)
        register_node(assign, func)
        inode(self.gx, node).assignhop = assign
        self.visit(assign, func)

    def visit_Sub(self, node, func=None):
        self.fake_func(node, node.left, aug_msg(node, 'sub'), [node.right], func)

    def visit_Mul(self, node, func=None):
        self.fake_func(node, node.left, aug_msg(node, 'mul'), [node.right], func)

    def visit_Div(self, node, func=None):
        self.fake_func(node, node.left, aug_msg(node, 'div'), [node.right], func)

    def visit_FloorDiv(self, node, func=None):
        self.fake_func(node, node.left, aug_msg(node, 'floordiv'), [node.right], func)

    def visit_Power(self, node, func=None):
        self.fake_func(node, node.left, '__pow__', [node.right], func)

    def visit_Mod(self, node, func=None):
        if isinstance(node.right, (Tuple, Dict)):
            self.fake_func(node, node.left, '__mod__', [], func)
            for child in getChildNodes(node.right):
                self.visit(child, func)
                if isinstance(node.right, Tuple):
                    self.fake_func(inode(self.gx, child), child, '__str__', [], func)
        else:
            self.fake_func(node, node.left, '__mod__', [node.right], func)

    def visit_Printnl(self, node, func=None):
        self.visit_Print(node, func)

    def visit_Print(self, node, func=None):
        pnode = CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[pnode] = set()

        for child in getChildNodes(node):
            self.visit(child, func)
            self.fake_func(inode(self.gx, child), child, '__str__', [], func)

    def temp_var(self, node, func=None, looper=None, wopper=None, exc_name=False):
        if node in self.gx.parent_nodes:
            varname = self.tempcount[self.gx.parent_nodes[node]]
        elif node in self.tempcount:  # XXX investigate why this happens
            varname = self.tempcount[node]
        else:
            varname = '__' + str(len(self.tempcount))

        var = default_var(self.gx, varname, func, mv=getmv(), exc_name=exc_name)
        var.looper = looper
        var.wopper = wopper
        self.tempcount[node] = varname

        register_temp_var(var, func)
        return var

    def temp_var2(self, node, source, func):
        tvar = self.temp_var(node, func)
        self.add_constraint((source, inode(self.gx, tvar)), func)
        return tvar

    def temp_var_int(self, node, func):
        var = self.temp_var(node, func)
        self.gx.types[inode(self.gx, var)] = set([(def_class(self.gx, 'int_'), 0)])
        inode(self.gx, var).copymetoo = True
        return var

    def visit_Raise(self, node, func=None):
        if node.expr1 is None or node.expr2 is not None or node.expr3 is not None:
            error('unsupported raise syntax', self.gx, node, mv=getmv())
        for child in getChildNodes(node):
            self.visit(child, func)

    def visit_TryExcept(self, node, func=None):
        self.visit_statements(get_statements(node.body), func)

        for handler in node.handlers:
            if not handler[0]:
                continue

            if isinstance(handler[0], Tuple):
                pairs = [(n, handler[1]) for n in handler[0].nodes]
            else:
                pairs = [(handler[0], handler[1])]

            for (h0, h1) in pairs:
                if isinstance(h0, Name) and h0.name in ['int', 'float', 'str', 'class']:
                    continue  # handle in lookup_class
                cl = lookup_class(h0, getmv())
                if not cl:
                    error("unknown or unsupported exception type", self.gx, h0, mv=getmv())

                if isinstance(h1, AssName):
                    var = self.default_var(h1.name, func, exc_name=True)
                else:
                    var = self.temp_var(h0, func, exc_name=True)

                var.invisible = True
                inode(self.gx, var).copymetoo = True
                self.gx.types[inode(self.gx, var)] = set([(cl, 1)])

        for handler in node.handlers:
            self.visit_statements(get_statements(handler[2]), func)

        # else
        if node.else_:
            self.visit_statements(get_statements(node.else_), func)
            self.temp_var_int(node.else_, func)

    def visit_TryFinally(self, node, func=None):
        error("'try..finally' is not supported", self.gx, node, mv=getmv())

    def visit_Yield(self, node, func):
        func.isGenerator = True
        func.yieldNodes.append(node)
        self.visit(Return(Call(Name('__iter'), [node.value])), func)
        self.add_constraint((inode(self.gx, node.value), func.yieldnode), func)

    def visit_For(self, node, func=None):
        # --- iterable contents -> assign node
        assnode = CNode(self.gx, node.assign, parent=func, mv=getmv())
        self.gx.types[assnode] = set()

        get_iter = Call(Attribute(node.list, '__iter__'), [])
        fakefunc = Call(Attribute(get_iter, 'next'), [])

        self.visit(fakefunc, func)
        self.add_constraint((inode(self.gx, fakefunc), assnode), func)

        # --- assign node -> variables  XXX merge into assign_pair
        if isinstance(node.assign, AssName):
            # for x in..
            lvar = self.default_var(node.assign.name, func)
            self.add_constraint((assnode, inode(self.gx, lvar)), func)

        elif isinstance(node.assign, AssAttr):  # XXX experimental :)
            # for expr.x in..
            CNode(self.gx, node.assign, parent=func, mv=getmv())

            self.gx.assign_target[node.assign.expr] = node.assign.expr  # XXX multiple targets possible please
            fakefunc2 = Call(Attribute(node.assign.expr, '__setattr__'), [Const(node.assign.attrname), fakefunc])
            self.visit(fakefunc2, func)

        elif isinstance(node.assign, (AssTuple, AssList)):
            # for (a,b, ..) in..
            self.tuple_flow(node.assign, node.assign, func)
        else:
            error('unsupported type of assignment', self.gx, node, mv=getmv())

        self.do_for(node, assnode, get_iter, func)

        # --- for-else
        if node.else_:
            self.temp_var_int(node.else_, func)
            self.visit_statements(get_statements(node.else_), func)

        # --- loop body
        self.gx.loopstack.append(node)
        self.visit_statements(get_statements(node.body), func)
        self.gx.loopstack.pop()
        self.for_in_iters.append(node.list)

    def do_for(self, node, assnode, get_iter, func):
        # --- for i in range(..) XXX i should not be modified.. use tempcounter; two bounds
        if is_fastfor(node):
            self.temp_var2(node.assign, assnode, func)
            self.temp_var2(node.list, inode(self.gx, node.list.args[0]), func)

            if len(node.list.args) == 3 and not isinstance(node.list.args[2], Name) and not is_literal(node.list.args[2]):  # XXX merge with ListComp
                for arg in node.list.args:
                    if not isinstance(arg, Name) and not is_literal(arg):  # XXX create func for better check
                        self.temp_var2(arg, inode(self.gx, arg), func)

        # --- temp vars for list, iter etc.
        else:
            self.temp_var2(node, inode(self.gx, node.list), func)
            self.temp_var2((node, 1), inode(self.gx, get_iter), func)
            self.temp_var_int(node.list, func)

            if is_enum(node) or is_zip2(node):
                self.temp_var2((node, 2), inode(self.gx, node.list.args[0]), func)
                if is_zip2(node):
                    self.temp_var2((node, 3), inode(self.gx, node.list.args[1]), func)
                    self.temp_var_int((node, 4), func)

            self.temp_var((node, 5), func, looper=node.list)
            if isinstance(node.list, Call) and isinstance(node.list.node, Attribute):
                self.temp_var((node, 6), func, wopper=node.list.node.expr)
                self.temp_var2((node, 7), inode(self.gx, node.list.node.expr), func)

    def bool_test_add(self, node):
        if isinstance(node, (And, Or, Not)):
            self.gx.bool_test_only.add(node)

    def visit_While(self, node, func=None):
        self.gx.loopstack.append(node)
        self.bool_test_add(node.test)
        self.visit(node.test, func)
        self.visit_statements(get_statements(node.body), func)
        self.gx.loopstack.pop()

        if node.else_:
            self.temp_var_int(node.else_, func)
            self.visit_statements(get_statements(node.else_), func)

    def visit_With(self, node, func=None):
        if node.vars:
            varnode = CNode(self.gx, node.vars, parent=func, mv=getmv())
            self.gx.types[varnode] = set()
            self.visit(node.expr, func)
            self.add_constraint((inode(self.gx, node.expr), varnode), func)
            lvar = self.default_var(node.vars.name, func)
            self.add_constraint((varnode, inode(self.gx, lvar)), func)
        else:
            self.visit(node.expr, func)
        self.visit_statements(get_statements(node.body), func)

    def visit_ListCompIf(self, node, func=None):
        self.bool_test_add(node.test)
        for child in getChildNodes(node):
            self.visit(child, func)

    def visit_ListComp(self, node, func=None):
        # --- [expr for iter in list for .. if cond ..]
        lcfunc = Function(self.gx, mv=getmv())
        lcfunc.listcomp = True
        lcfunc.ident = 'l.c.'  # XXX
        lcfunc.parent = func

        for qual in node.quals:
            # iter
            assnode = CNode(self.gx, qual.assign, parent=func, mv=getmv())
            self.gx.types[assnode] = set()

            # list.unit->iter
            get_iter = Call(Attribute(qual.list, '__iter__'), [])
            fakefunc = Call(Attribute(get_iter, 'next'), [])
            self.visit(fakefunc, lcfunc)
            self.add_constraint((inode(self.gx, fakefunc), inode(self.gx, qual.assign)), lcfunc)

            if isinstance(qual.assign, AssName):  # XXX merge with visitFor
                lvar = default_var(self.gx, qual.assign.name, lcfunc)  # XXX str or Name?
                self.add_constraint((inode(self.gx, qual.assign), inode(self.gx, lvar)), lcfunc)
            else:  # AssTuple, AssList
                self.tuple_flow(qual.assign, qual.assign, lcfunc)

            self.do_for(qual, assnode, get_iter, lcfunc)

            # cond
            for child in qual.ifs:
                self.visit(child, lcfunc)

            self.for_in_iters.append(qual.list)

        # node type
        if node in self.gx.genexp_to_lc.values():  # converted generator expression
            self.instance(node, def_class(self.gx, '__iter'), func)
        else:
            self.instance(node, def_class(self.gx, 'list'), func)

        # expr->instance.unit
        self.visit(node.expr, lcfunc)
        self.add_dynamic_constraint(node, node.expr, 'unit', lcfunc)

        lcfunc.ident = 'list_comp_' + str(len(self.listcomps))
        self.listcomps.append((node, lcfunc, func))

    def visit_Return(self, node, func):
        self.visit(node.value, func)
        func.returnexpr.append(node.value)
        if not (is_const(node.value) and const_value(node.value) is None):
            newnode = CNode(self.gx, node, parent=func, mv=getmv())
            self.gx.types[newnode] = set()
            if isinstance(node.value, Name):
                func.retvars.append(get_id(node.value))
        if func.retnode:
            self.add_constraint((inode(self.gx, node.value), func.retnode), func)

    def visit_Assign(self, node, func=None):
        # --- rewrite for struct.unpack XXX rewrite callfunc as tuple
        if len(node.nodes) == 1:
            lvalue, rvalue = node.nodes[0], node.expr
            if self.struct_unpack(rvalue, func) and isinstance(lvalue, (AssList, AssTuple)) and not [n for n in lvalue.nodes if isinstance(n, (AssList, AssTuple))]:
                self.visit(node.expr, func)
                sinfo = self.struct_info(rvalue.args[0], func)
                faketuple = self.struct_faketuple(sinfo)
                self.visit(Assign(node.nodes, faketuple), func)
                tvar = self.temp_var2(rvalue.args[1], inode(self.gx, rvalue.args[1]), func)
                tvar_pos = self.temp_var_int(rvalue.args[0], func)
                self.gx.struct_unpack[node] = (sinfo, tvar.name, tvar_pos.name)
                return

        newnode = CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set()

        # --- a,b,.. = c,(d,e),.. = .. = expr
        for target_expr in node.nodes:
            pairs = assign_rec(target_expr, node.expr)
            for (lvalue, rvalue) in pairs:
                # expr[expr] = expr
                if isinstance(lvalue, Subscript) and not isinstance(lvalue.subs[0], Sliceobj):
                    self.assign_pair(lvalue, rvalue, func)  # XXX use here generally, and in tuple_flow

                # expr.attr = expr
                elif isinstance(lvalue, AssAttr):
                    self.assign_pair(lvalue, rvalue, func)

                # name = expr
                elif isinstance(lvalue, AssName):
                    if (rvalue, 0, 0) not in self.gx.cnode:  # XXX generalize
                        self.visit(rvalue, func)
                    self.visit(lvalue, func)
                    lvar = self.default_var(lvalue.name, func)
                    if isinstance(rvalue, Const):
                        lvar.const_assign.append(rvalue)
                    self.add_constraint((inode(self.gx, rvalue), inode(self.gx, lvar)), func)

                # (a,(b,c), ..) = expr
                elif isinstance(lvalue, (AssTuple, AssList)):
                    self.visit(rvalue, func)
                    self.tuple_flow(lvalue, rvalue, func)

                # expr[a:b] = expr # XXX bla()[1:3] = [1]
                elif isinstance(lvalue, Slice):
                    self.slice(lvalue, lvalue.expr, [lvalue.lower, lvalue.upper, None], func, rvalue)

                # expr[a:b:c] = expr
                elif isinstance(lvalue, Subscript) and isinstance(lvalue.subs[0], Sliceobj):
                    self.slice(lvalue, lvalue.expr, lvalue.subs[0].nodes, func, rvalue)

        # temp vars
        if len(node.nodes) > 1 or isinstance(node.expr, Tuple):
            if isinstance(node.expr, Tuple):
                if [n for n in node.nodes if isinstance(n, AssTuple)]:
                    for child in node.expr.nodes:
                        if (child, 0, 0) not in self.gx.cnode:  # (a,b) = (1,2): (1,2) never visited
                            continue
                        if not isinstance(child, Const) and not (isinstance(child, Name) and child.name == 'None'):
                            self.temp_var2(child, inode(self.gx, child), func)
            elif not isinstance(node.expr, Const) and not (isinstance(node.expr, Name) and node.expr.name == 'None'):
                self.temp_var2(node.expr, inode(self.gx, node.expr), func)

    def assign_pair(self, lvalue, rvalue, func):
        # expr[expr] = expr
        if isinstance(lvalue, Subscript) and not isinstance(lvalue.subs[0], Sliceobj):
            if len(lvalue.subs) > 1:
                subscript = Tuple(lvalue.subs)
            else:
                subscript = lvalue.subs[0]

            fakefunc = Call(Attribute(lvalue.expr, '__setitem__'), [subscript, rvalue])
            self.visit(fakefunc, func)
            inode(self.gx, lvalue.expr).fakefunc = fakefunc
            if len(lvalue.subs) > 1:
                inode(self.gx, lvalue.expr).faketuple = subscript

            if not isinstance(lvalue.expr, Name):
                self.temp_var2(lvalue.expr, inode(self.gx, lvalue.expr), func)

        # expr.attr = expr
        elif isinstance(lvalue, AssAttr):
            CNode(self.gx, lvalue, parent=func, mv=getmv())
            self.gx.assign_target[rvalue] = lvalue.expr
            fakefunc = Call(Attribute(lvalue.expr, '__setattr__'), [Const(lvalue.attrname), rvalue])
            self.visit(fakefunc, func)

    def default_var(self, name, func, exc_name=False):
        if isinstance(func, Function) and name in func.globals:
            return default_var(self.gx, name, None, mv=getmv(), exc_name=exc_name)
        else:
            return default_var(self.gx, name, func, mv=getmv(), exc_name=exc_name)

    def tuple_flow(self, lvalue, rvalue, func=None):
        self.temp_var2(lvalue, inode(self.gx, rvalue), func)

        if isinstance(lvalue, (AssTuple, AssList)):
            lvalue = lvalue.nodes
        for (i, item) in enumerate(lvalue):
            fakenode = CNode(self.gx, (item,), parent=func, mv=getmv())  # fake node per item, for multiple callfunc triggers
            self.gx.types[fakenode] = set()
            self.add_constraint((inode(self.gx, rvalue), fakenode), func)

            fakefunc = Call(FakeAttribute3(rvalue, '__getitem__'), [Const(i)])

            fakenode.callfuncs.append(fakefunc)
            self.visit(fakefunc, func)

            self.gx.item_rvalue[item] = rvalue
            if isinstance(item, AssName):
                lvar = self.default_var(item.name, func)
                self.add_constraint((inode(self.gx, fakefunc), inode(self.gx, lvar)), func)
            elif isinstance(item, (Subscript, AssAttr)):
                self.assign_pair(item, fakefunc, func)
            elif isinstance(item, (AssTuple, AssList)):  # recursion
                self.tuple_flow(item, fakefunc, func)
            else:
                error('unsupported type of assignment', self.gx, item, mv=getmv())

    def super_call(self, expr, orig):
        value = attr_value(expr)
        attr = attr_attr(expr)

        if (isinstance(value, Call) and
            attr not in ('__getattr__', '__setattr__') and
            isinstance(get_func(value), Name) and
                get_id(get_func(value)) == 'super'):
            if (len(value.args) >= 2 and
                    isinstance(value.args[1], Name) and value.args[1].name == 'self'):
                cl = lookup_class(value.args[0], getmv())
                if cl.node.bases:
                    return cl.node.bases[0]
            error("unsupported usage of 'super'", self.gx, orig, mv=getmv())

    def visit_Call(self, node, func=None):  # XXX clean up!!
        newnode = CNode(self.gx, node, parent=func, mv=getmv())

        expr = get_func(node)

        if isinstance(expr, Attribute):  # XXX import math; math.e
            # rewrite super(..) call
            base = self.super_call(expr, node)
            if base:
                node.node = Attribute(copy.deepcopy(base), node.node.attrname)  # TODO py3
                expr = get_func(node)
                node.args = [Name('self')] + node.args

            # method call
            if isinstance(expr, FakeAttribute):  # XXX butt ugly
                self.visit(expr, func)
            elif isinstance(expr, FakeAttribute2):
                self.gx.types[newnode] = set()  # XXX move above

                self.callfuncs.append((node, func))

                for arg in node.args:
                    inode(self.gx, arg).callfuncs.append(node)  # this one too

                return
            elif isinstance(expr, FakeAttribute3):
                pass
            else:
                self.visit_Getattr(expr, func, callfunc=True)
                inode(self.gx, expr).callfuncs.append(node)  # XXX iterative dataflow analysis: move there?
                inode(self.gx, expr).fakert = True

            ident = node.node.attrname
            inode(self.gx, expr.expr).callfuncs.append(node)  # XXX iterative dataflow analysis: move there?

            if isinstance(expr.expr, Name) and get_id(expr.expr) in getmv().imports and attr_attr(expr) == '__getattr__':  # XXX analyze_callfunc
                if node.args[0].value in getmv().imports[expr.expr.name].mv.globals:  # XXX bleh
                    self.add_constraint((inode(self.gx, getmv().imports[expr.expr.name].mv.globals[node.args[0].value]), newnode), func)

        elif isinstance(expr, Name):
            # direct call
            ident = expr.name
            if ident == 'print':
                ident = expr.name = '__print'  # XXX

            if ident in ['hasattr', 'getattr', 'setattr', 'slice', 'type', 'Ellipsis']:
                error("'%s' function is not supported" % ident, self.gx, expr, mv=getmv())
            if ident == 'dict' and [x for x in node.args if isinstance(x, Keyword)]:
                error('unsupported method of initializing dictionaries', self.gx, node, mv=getmv())
            if ident == 'isinstance':
                error("'isinstance' is not supported; always returns True", self.gx, node, mv=getmv(), warning=True)

            if lookup_var(ident, func, mv=getmv()):
                self.visit(expr, func)
                inode(self.gx, expr).callfuncs.append(node)  # XXX iterative dataflow analysis: move there
        else:
            self.visit(expr, func)
            inode(self.gx, expr).callfuncs.append(node)  # XXX iterative dataflow analysis: move there

        # --- arguments
        if not getmv().module.builtin and (node.star_args or node.dstar_args):
            error('argument (un)packing is not supported', self.gx, node, mv=getmv())
        args = node.args[:]
        if node.star_args:
            args.append(node.star_args)  # partially allowed in builtins
        if node.dstar_args:
            args.append(node.dstar_args)
        for arg in args:
            if isinstance(arg, Keyword):
                arg = arg.expr
            self.visit(arg, func)
            inode(self.gx, arg).callfuncs.append(node)  # this one too

        # --- handle instantiation or call
        constructor = lookup_class(expr, getmv())
        if constructor and (not isinstance(expr, Name) or not lookup_var(expr.name, func, mv=getmv())):
            self.instance(node, constructor, func)
            inode(self.gx, node).callfuncs.append(node)  # XXX see above, investigate
        else:
            self.gx.types[newnode] = set()

        self.callfuncs.append((node, func))

    def visit_ClassDef(self, node, parent=None):
        if not getmv().module.builtin and not node in getmv().classnodes:
            error("non-global class '%s'" % node.name, self.gx, node, mv=getmv())
        if len(node.bases) > 1:
            error('multiple inheritance is not supported', self.gx, node, mv=getmv())

        if not getmv().module.builtin:
            for base in node.bases:
                if not isinstance(base, (Name, Attribute)):
                    error("invalid expression for base class", self.gx, node, mv=getmv())

                if isinstance(base, Name):
                    name = base.name
                else:
                    name = base.attrname

                cl = lookup_class(base, getmv())
                if not cl:
                    error("no such class: '%s'" % name, self.gx, node, mv=getmv())

                elif cl.mv.module.builtin and name not in ['object', 'Exception', 'tzinfo']:
                    if def_class(self.gx, 'Exception') not in cl.ancestors():
                        error("inheritance from builtin class '%s' is not supported" % name, self.gx, node, mv=getmv())

        if node.name in getmv().classes:
            newclass = getmv().classes[node.name]  # set in visitModule, for forward references
        else:
            check_redef(self.gx, node)  # XXX merge with visitModule
            newclass = Class(self.gx, node, getmv())
            self.classes[node.name] = newclass
            getmv().classes[node.name] = newclass
            newclass.module = self.module
            newclass.parent = StaticClass(newclass, getmv())

        # --- built-in functions
        for cl in [newclass, newclass.parent]:
            for ident in ['__setattr__', '__getattr__']:
                func = Function(self.gx, mv=getmv())
                func.ident = ident
                func.parent = cl

                if ident == '__setattr__':
                    func.formals = ['name', 'whatsit']
                    retexpr = Return(Name('None'))
                    self.visit(retexpr, func)
                elif ident == '__getattr__':
                    func.formals = ['name']

                cl.funcs[ident] = func

        # --- built-in attributes
        if 'class_' in getmv().classes or 'class_' in getmv().ext_classes:
            var = default_var(self.gx, '__class__', newclass)
            var.invisible = True
            self.gx.types[inode(self.gx, var)] = set([(def_class(self.gx, 'class_'), def_class(self.gx, 'class_').dcpa)])
            def_class(self.gx, 'class_').dcpa += 1

        # --- staticmethod, property
        skip = []
        for child in get_statements(get_body(node)):
            if isinstance(child, Assign) and len(child.nodes) == 1:
                lvalue, rvalue = child.nodes[0], child.expr
                if isinstance(lvalue, AssName) and isinstance(rvalue, Call) and isinstance(rvalue.node, Name) and rvalue.node.name in ['staticmethod', 'property']:
                    if rvalue.node.name == 'property':
                        if len(rvalue.args) == 1 and isinstance(rvalue.args[0], Name):
                            newclass.properties[lvalue.name] = rvalue.args[0].name, None
                        elif len(rvalue.args) == 2 and isinstance(rvalue.args[0], Name) and isinstance(rvalue.args[1], Name):
                            newclass.properties[lvalue.name] = rvalue.args[0].name, rvalue.args[1].name
                        else:
                            error("complex properties are not supported", self.gx, rvalue, mv=getmv())
                    else:
                        newclass.staticmethods.append(lvalue.name)
                    skip.append(child)

        # --- statements
        for child in get_statements(get_body(node)):
            if child not in skip:
                cl = self.classes[node.name]
                if isinstance(child, FunctionDef):
                    self.visit(child, cl)
                else:
                    cl.parent.static_nodes.append(child)
                    self.visit(child, cl.parent)

        # --- __iadd__ etc.
        if not newclass.mv.module.builtin or newclass.ident in ['int_', 'float_', 'str_', 'tuple', 'complex']:
            msgs = ['add', 'mul']  # XXX mod, pow
            if newclass.ident in ['int_', 'float_']:
                msgs += ['sub', 'div', 'floordiv']
            if newclass.ident in ['int_']:
                msgs += ['lshift', 'rshift', 'and', 'xor', 'or']
            for msg in msgs:
                if not '__i' + msg + '__' in newclass.funcs:
                    self.visit(parse_expr('def __i%s__(self, other): return self.__%s__(other)' % (msg, msg)), newclass)

        # --- __str__, __hash__ # XXX model in lib/builtin.py, other defaults?
        if not newclass.mv.module.builtin and not '__str__' in newclass.funcs:
            self.visit(parse_expr('def __str__(self): return self.__repr__()'), newclass)
            newclass.funcs['__str__'].invisible = True

        if not newclass.mv.module.builtin and not '__hash__' in newclass.funcs:
            self.visit(parse_expr('def __hash__(self): return 0'), newclass)
            newclass.funcs['__hash__'].invisible = True

    def visit_Getattr(self, node, func=None, callfunc=False):
        if node.attrname in ['__doc__']:
            error('%s attribute is not supported' % node.attrname, self.gx, node, mv=getmv())

        newnode = CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set()

        fakefunc = Call(FakeAttribute(node.expr, '__getattr__'), [Const(node.attrname)])
        self.visit(fakefunc, func)
        self.add_constraint((self.gx.cnode[fakefunc, 0, 0], newnode), func)

        self.callfuncs.append((fakefunc, func))

        if not callfunc:
            self.fncl_passing(node, newnode, func)

    def visit_Const(self, node, func=None):
        if type(node.value) == unicode:
            error('unicode is not supported', self.gx, node, mv=getmv())
        map = {int: 'int_', str: 'str_', float: 'float_', type(None): 'none', long: 'int_', complex: 'complex'}  # XXX 'return' -> Return(Const(None))?
        self.instance(node, def_class(self.gx, map[type(node.value)]), func)

    def fncl_passing(self, node, newnode, func):
        lfunc, lclass = lookup_func(node, getmv()), lookup_class(node, getmv())
        if lfunc:
            if lfunc.mv.module.builtin:
                lfunc = self.builtin_wrapper(node, func)
            elif lfunc.ident not in lfunc.mv.lambdas:
                lfunc.lambdanr = len(lfunc.mv.lambdas)
                lfunc.mv.lambdas[lfunc.ident] = lfunc
            self.gx.types[newnode] = set([(lfunc, 0)])
        elif lclass:
            if lclass.mv.module.builtin:
                lclass = self.builtin_wrapper(node, func)
            else:
                lclass = lclass.parent
            self.gx.types[newnode] = set([(lclass, 0)])
        else:
            return False
        newnode.copymetoo = True  # XXX merge into some kind of 'seeding' function
        return True

    def visit_Name(self, node, func=None):
        newnode = CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set()

        if node.id == '__doc__':
            error("'%s' attribute is not supported" % node.id, self.gx, node, mv=getmv())

        if node.id in ['None', 'True', 'False']:
            if node.id == 'None':  # XXX also bools, remove def seed_nodes()
                self.instance(node, def_class(self.gx, 'none'), func)
            else:
                self.instance(node, def_class(self.gx, 'bool_'), func)
            return

        if isinstance(func, Function) and node.id in func.globals:
            var = default_var(self.gx, node.id, None, mv=getmv())
        else:
            var = lookup_var(node.id, func, mv=getmv())
            if not var:
                if self.fncl_passing(node, newnode, func):
                    pass
                elif node.id in ['int', 'float', 'str']:  # XXX
                    cl = self.ext_classes[node.id + '_']
                    self.gx.types[newnode] = set([(cl.parent, 0)])
                    newnode.copymetoo = True
                else:
                    var = default_var(self.gx, node.id, None, mv=getmv())
        if var:
            self.add_constraint((inode(self.gx, var), newnode), func)
            for a, b in self.gx.filterstack:
                if var.name == a.name:
                    self.gx.filters[node] = lookup_class(b, getmv())

    def builtin_wrapper(self, node, func):
        node2 = Call(copy.deepcopy(node), [Name(x) for x in 'abcde'])
        l = Lambda(list('abcde'), [], 0, node2)
        self.visit(l, func)
        self.lwrapper[node] = self.lambdaname[l]
        self.gx.lambdawrapper[node2] = self.lambdaname[l]
        f = self.lambdas[self.lambdaname[l]]
        f.lambdawrapper = True
        inode(self.gx, node2).lambdawrapper = f
        return f


def parse_module(name, gx, parent=None, node=None):
    # --- valid name?
    if not re.match("^[a-zA-Z0-9_.]+$", name):
        print ("*ERROR*:%s.py: module names should consist of letters, digits and underscores" % name)
        sys.exit(1)

    # --- create module
    try:
        if parent and parent.path != os.getcwd():
            basepaths = [parent.path, os.getcwd()]
        else:
            basepaths = [os.getcwd()]
        module_paths = basepaths + gx.libdirs
        absolute_name, filename, relative_filename, builtin = find_module(gx, name, module_paths)
        module = Module(absolute_name, filename, relative_filename, builtin, node)
    except ImportError:
        error('cannot locate module: ' + name, gx, node, mv=getmv())

    # --- check cache
    if module.name in gx.modules:  # cached?
        return gx.modules[module.name]
    gx.modules[module.name] = module

    # --- not cached, so parse
    module.ast = parse_file(module.filename)

    old_mv = getmv()
    module.mv = mv = ModuleVisitor(module, gx)
    setmv(mv)

    mv.visitor = mv
    mv.visit(module.ast)
    module.import_order = gx.import_order
    gx.import_order += 1

    mv = old_mv
    setmv(mv)

    return module
