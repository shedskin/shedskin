'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2022 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)

graph.py: build constraint graph used in dataflow analysis

constraint graph: graph along which possible types 'flow' during an 'abstract execution' of a program (a dataflow analysis). consider the assignment statement 'a = b'. it follows that the set of possible types of b is smaller than or equal to that of a (a constraint). we can determine possible types of a, by 'flowing' the types from b to a, in other words, along the constraint.

constraint graph nodes are stored in gx.cnode, and the set of types of for each node in gx.types. nodes are identified by an AST Node, and two integers. the integers are used in py to duplicate parts of the constraint graph along two dimensions. in the initial constraint graph, these integers are always 0.

class ModuleVisitor: inherits visitor pattern from ast_utils.BaseNodeVisitor, to recursively generate constraints for each syntactical Python construct. for example, the visitFor method is called in case of a for-loop. temporary variables are introduced in many places, to enable translation to a lower-level language.

parse_module(): locate module by name (e.g. 'os.path'), and use ModuleVisitor if not cached

'''
import ast
import copy
import os
import re
import sys

from . import ast_utils
from . import error
from . import infer
from . import python

# --- global variable mv
_mv = None


def setmv(mv):
    global _mv
    _mv = mv
    return _mv


def getmv():
    return _mv


class FakeGetattr3(ast.Attribute):
    pass


class FakeGetattr2(ast.Attribute):
    pass


class FakeGetattr(ast.Attribute):
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
                error.error("function/class redefinition is not supported", gx, node, mv=getmv())


# --- maintain inheritance relations between copied AST nodes
def inherit_rec(gx, original, copy, mv):
    gx.inheritance_relations.setdefault(original, []).append(copy)
    gx.inherited.add(copy)
    gx.parent_nodes[copy] = original

    for (a, b) in zip(ast.iter_child_nodes(original), ast.iter_child_nodes(copy)):
        inherit_rec(gx, a, b, mv)


def register_node(node, func):
    if func:
        func.registered.append(node)


def slice_nums(nodes):
    nodes2 = []
    x = 0
    for i, n in enumerate(nodes):
        if not n or ast_utils.is_none(n):
            nodes2.append(ast.Num(0))
        else:
            nodes2.append(n)
            x |= (1 << i)
    return [ast.Num(x)] + nodes2


# --- module visitor; analyze program, build constraint graph
class ModuleVisitor(ast_utils.BaseNodeVisitor):
    def __init__(self, module, gx):
        ast_utils.BaseNodeVisitor.__init__(self)
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
            ast_utils.BaseNodeVisitor.visit(self, node, *args)

    def fake_func(self, node, objexpr, attrname, args, func):
        if (node, 0, 0) in self.gx.cnode:  # XXX
            newnode = self.gx.cnode[node, 0, 0]
        else:
            newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
            self.gx.types[newnode] = set()

        fakefunc = ast_utils.make_call(ast.Attribute(objexpr, attrname, ast.Load()), args)
        fakefunc.lineno = objexpr.lineno
        self.visit(fakefunc, func)
        self.add_constraint((infer.inode(self.gx, fakefunc), newnode), func)

        infer.inode(self.gx, objexpr).fakefunc = fakefunc
        return fakefunc

    # simple heuristic for initial list split: count nesting depth, first constant child type
    def list_type(self, node):
        count = 0
        child = node
        while isinstance(child, (ast.List, ast.ListComp)):
            if isinstance(child, ast.List):
                if not child.elts:
                    return None
                child = child.elts[0]
                count += 1
            else:
                if not child.elt:
                    return None
                child = child.elt
                count += 1

        if isinstance(child, ast.UnaryOp) and isinstance(child.op, (ast.USub, ast.UAdd)):
            child = child.operand

        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
            map = {'int': int, 'str': str, 'float': float}
            if child.func.id in ('range'):  # ,'xrange'):
                count, child = count + 1, int
            elif child.func.id in map:
                child = map[child.func.id]
            elif child.func.id in (cl.ident for cl in self.gx.allclasses) or child.func.id in getmv().classes:  # XXX getmv().classes
                child = child.func.id
            else:
                if count == 1:
                    return None
                child = None
        elif isinstance(child, ast.Num):
            child = type(child.n)
        elif isinstance(child, ast.Str):
            child = type(child.s)
        elif isinstance(child, ast.Name) and child.id in ('True', 'False'):
            child = bool
        elif isinstance(child, ast.Tuple):
            child = tuple
        elif isinstance(child, ast.Dict):
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
            newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())

        newnode.constructor = True

        if cl.ident in ['int_', 'float_', 'str_', 'bytes_', 'none', 'class_', 'bool_']:
            self.gx.types[newnode] = set([(cl, cl.dcpa - 1)])
        else:
            if cl.ident == 'list' and self.list_type(node):
                self.gx.types[newnode] = set([(cl, self.list_type(node))])
            else:
                self.gx.types[newnode] = set([(cl, cl.dcpa)])

    def constructor(self, node, classname, func):
        cl = python.def_class(self.gx, classname)

        self.instance(node, cl, func)
        infer.default_var(self.gx, 'unit', cl)

        if classname in ['list', 'tuple'] and not node.elts:
            self.gx.empty_constructors.add(node)  # ifa disables those that flow to instance variable assignments

        # --- internally flow binary tuples
        if cl.ident == 'tuple2':
            infer.default_var(self.gx, 'first', cl)
            infer.default_var(self.gx, 'second', cl)
            elem0, elem1 = node.elts

            self.visit(elem0, func)
            self.visit(elem1, func)

            self.add_dynamic_constraint(node, elem0, 'unit', func)
            self.add_dynamic_constraint(node, elem1, 'unit', func)

            self.add_dynamic_constraint(node, elem0, 'first', func)
            self.add_dynamic_constraint(node, elem1, 'second', func)

            return

        # --- add dynamic children constraints for other types
        if classname == 'dict':  # XXX filter children
            infer.default_var(self.gx, 'unit', cl)
            infer.default_var(self.gx, 'value', cl)

            for child in ast.iter_child_nodes(node):
                self.visit(child, func)

            for (key, value) in zip(node.keys, node.values):  # XXX filter
                self.add_dynamic_constraint(node, key, 'unit', func)
                self.add_dynamic_constraint(node, value, 'value', func)
        else:
            for child in node.elts:
                self.visit(child, func)

            for child in self.filter_redundant_children(node):
                self.add_dynamic_constraint(node, child, 'unit', func)

    # --- for compound list/tuple/dict constructors, we only consider a single child node for each subtype
    def filter_redundant_children(self, node):
        done = set()
        nonred = []
        for child in node.elts:
            type = self.child_type_rec(child)
            if not type or not type in done:
                done.add(type)
                nonred.append(child)

        return nonred

    # --- determine single constructor child node type, used by the above
    def child_type_rec(self, node):
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            node = node.operand

        if isinstance(node, (ast.List, ast.Tuple)):
            if isinstance(node, ast.List):
                cl = python.def_class(self.gx, 'list')
            elif len(node.elts) == 2:
                cl = python.def_class(self.gx, 'tuple2')
            else:
                cl = python.def_class(self.gx, 'tuple')

            merged = set()
            for child in node.elts:
                merged.add(self.child_type_rec(child))

            if len(merged) == 1:
                return (cl, merged.pop())

        elif isinstance(node, (ast.Num, ast.Str)):
            return (list(infer.inode(self.gx, node).types())[0][0],)

    # --- add dynamic constraint for constructor argument, e.g. '[expr]' becomes [].__setattr__('unit', expr)
    def add_dynamic_constraint(self, parent, child, varname, func):
        # print 'dynamic constr', child, parent

        self.gx.assign_target[child] = parent
        cu = ast.Str(varname)
        self.visit(cu, func)
        fakefunc = ast_utils.make_call(FakeGetattr2(parent, '__setattr__', ast.Load()), [cu, child])
        self.visit(fakefunc, func)

        fakechildnode = infer.CNode(self.gx, (child, varname), parent=func, mv=getmv())  # create separate 'fake' infer.CNode per child, so we can have multiple 'callfuncs'
        self.gx.types[fakechildnode] = set()

        self.add_constraint((infer.inode(self.gx, parent), fakechildnode), func)  # add constraint from parent to fake child node. if parent changes, all fake child nodes change, and the callfunc for each child node is triggered
        fakechildnode.callfuncs.append(fakefunc)

    # --- add regular constraint to function
    def add_constraint(self, constraint, func):
        infer.in_out(constraint[0], constraint[1])
        self.gx.constraints.add(constraint)
        while isinstance(func, python.Function) and func.listcomp:
            func = func.parent  # XXX
        if isinstance(func, python.Function):
            func.constraints.add(constraint)

    def struct_unpack(self, rvalue, func):
        if isinstance(rvalue, ast.Call):
            if isinstance(rvalue.func, ast.Attribute) and isinstance(rvalue.func.value, ast.Name) and rvalue.func.value.id == 'struct' and rvalue.func.attr == 'unpack' and python.lookup_var('struct', func, mv=self).imported:  # XXX imported from where?
                return True
            elif isinstance(rvalue.func, ast.Name) and rvalue.func.id == 'unpack' and 'unpack' in self.ext_funcs and not python.lookup_var('unpack', func, mv=self):  # XXX imported from where?
                return True

    def struct_info(self, node, func):
        if isinstance(node, ast.Name):
            var = python.lookup_var(node.id, func, mv=self)  # XXX fwd ref?
            if not var or len(var.const_assign) != 1:
                error.error('non-constant format string', self.gx, node, mv=self)
            error.error('assuming constant format string', self.gx, node, mv=self, warning=True)
            fmt = var.const_assign[0].s
        elif isinstance(node, ast.Num):
            fmt = node.n
        elif isinstance(node, ast.Str):
            fmt = node.s
        else:
            error.error('non-constant format string', self.gx, node, mv=self)
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
                rtype = {'i': 'int', 's': 'bytes', 'b': 'bool', 'f': 'float', 'x': 'pad'}[char_type[c]]
                if rtype == 'bytes' and c != 'c':
                    result.append((ordering, c, 'bytes', int(digits or '1')))
                elif digits == '0':
                    result.append((ordering, c, rtype, 0))
                else:
                    result.extend(int(digits or '1') * [(ordering, c, rtype, 1)])
                digits = ''
            else:
                error.error('bad or unsupported char in struct format: ' + repr(c), self.gx, node, mv=self)
                digits = ''
        return result

    def struct_faketuple(self, info):
        result = []
        for o, c, t, d in info:
            if d != 0 or c == 's':
                if t == 'int':
                    result.append(ast.Num(1))
                elif t == 'bytes':
                    result.append(ast.Str(b''))
                elif t == 'float':
                    result.append(ast.Num(1.0))
                elif t == 'bool':
                    result.append(ast.Name('True', ast.Load()))
        return ast.Tuple(result, ast.Load())

    def visit_GeneratorExp(self, node, func=None):
        newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set()
        lc = ast.ListComp(node.elt, [ast.comprehension(qual.target, qual.iter, qual.ifs) for qual in node.generators], lineno=node.lineno)
        register_node(lc, func)
        self.gx.genexp_to_lc[node] = lc
        self.visit(lc, func)
        self.add_constraint((infer.inode(self.gx, lc), newnode), func)

    def visit_JoinedStr(self, node, func=None):
        error.error("f-strings are not supported", self.gx, node, mv=getmv())

#    def visit_Stmt(self, node, func=None):
#        comments = []
#        for b in node.nodes:
#            if isinstance(b, ast.Expr):
#                self.bool_test_add(b.expr)
#            if isinstance(b, ast.Expr) and isinstance(b.expr, Constant) and type(b.expr.value) == str:
#                comments.append(b.expr.value)
#            elif comments:
#                self.gx.comments[b] = comments
#                comments = []
#            self.visit(b, func)

    def visit_Expr(self, node, func=None):
        self.bool_test_add(node.value)
        self.visit(node.value, func)

    def visit_Module(self, node):
        # --- bootstrap built-in classes
        if self.module.ident == 'builtin':
            for dummy in self.gx.builtins:
                self.visit(ast.ClassDef(dummy, [], [], [ast.Pass()]))

        if self.module.ident != 'builtin':
            n = ast.ImportFrom('builtin', [ast.alias('*', None)], None)  # Python2.5+
            getmv().importnodes.append(n)
            self.visit(n)

        # --- __name__
        if self.module.ident != 'builtin':
            namevar = infer.default_var(self.gx, '__name__', None, mv=getmv())
            self.gx.types[infer.inode(self.gx, namevar)] = set([(python.def_class(self.gx, 'str_'), 0)])

        self.forward_references(node)

        # --- visit children
        getmv().importnodes.extend(n for n in node.body if isinstance(n, (ast.Import, ast.ImportFrom)))
        for child in node.body:
            self.visit(child, None)

        # --- register classes
        for cl in getmv().classes.values():
            self.gx.allclasses.add(cl)

        # --- inheritance expansion

        # determine base classes
        for cl in self.classes.values():
            for base in cl.node.bases:
                if not (isinstance(base, ast.Name) and base.id == 'object'):
                    ancestor = python.lookup_class(base, getmv())
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

    def stmt_nodes(self, node, cl):
        result = []
        for child in node.body:
            if isinstance(child, cl):
                result.append(child)
        return result

    def forward_references(self, node):
        getmv().classnodes = []

        # classes
        for n in self.stmt_nodes(node, ast.ClassDef):
            check_redef(self.gx, n)
            getmv().classnodes.append(n)
            newclass = python.Class(self.gx, n, getmv())
            self.classes[n.name] = newclass
            getmv().classes[n.name] = newclass
            newclass.module = self.module
            newclass.parent = python.StaticClass(newclass, getmv())

            # methods
            for m in self.stmt_nodes(n, ast.FunctionDef):
                if m.decorator_list and [dec for dec in m.decorator_list if python.is_property_setter(dec)]:
                    m.name = m.name + '__setter__'
                if m.name in newclass.funcs:  # and func.ident not in ['__getattr__', '__setattr__']: # XXX
                    error.error("function/class redefinition is not allowed", self.gx, m, mv=getmv())
                func = python.Function(self.gx, m, newclass, mv=getmv())
                newclass.funcs[func.ident] = func
                self.set_default_vars(m, func)

        # functions
        getmv().funcnodes = []
        for n in self.stmt_nodes(node, ast.FunctionDef):
            check_redef(self.gx, n)
            getmv().funcnodes.append(n)
            func = getmv().funcs[n.name] = python.Function(self.gx, n, mv=getmv())
            self.set_default_vars(n, func)

        # global variables XXX visit_Global
        for assname in self.local_assignments(node, global_=True):
            infer.default_var(self.gx, assname.id, None, mv=getmv())

    def set_default_vars(self, node, func):
        globals = set(self.get_globals(node))
        for assname in self.local_assignments(node):
            if assname.id not in globals:
                infer.default_var(self.gx, assname.id, func)

    def get_globals(self, node):
        if isinstance(node, ast.Global):
            result = node.names
        else:
            result = []
            for child in ast.iter_child_nodes(node):
                result.extend(self.get_globals(child))
        return result

    def local_assignments(self, node, global_=False):
        if global_ and isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            return []
        elif isinstance(node, ast.ListComp):
            return []
        elif isinstance(node, ast.Name) and type(node.ctx) == ast.Store:
            result = [node]
        else:
            # Try-Excepts introduce a new small scope with the exception name,
            # so we skip it here.
            if isinstance(node, ast.Try):
                children = list(node.body)
                for handler in node.handlers:
                    children.extend(handler.body)
                if node.orelse:
                    children.extend(node.orelse)
            elif isinstance(node, ast.With):
                children = list(node.body)
            else:
                children = ast.iter_child_nodes(node)

            result = []
            for child in children:
                result.extend(self.local_assignments(child, global_))
        return result

    def visit_Import(self, node, func=None):
        if not node in getmv().importnodes:
            error.error("please place all imports (no 'try:' etc) at the top of the file", self.gx, node, mv=getmv())

        for name_alias in node.names:
            (name, pseudonym) = (name_alias.name, name_alias.asname)
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
            var = infer.default_var(self.gx, pseudonym or name, None, mv=getmv())
            var.imported = True
            self.gx.types[infer.inode(self.gx, var)] = set([(module, 0)])
        return module

    def visit_ImportFrom(self, node, parent=None):
        if not node in getmv().importnodes:  # XXX use (func, node) as parent..
            error.error("please place all imports (no 'try:' etc) at the top of the file", self.gx, node, mv=getmv())

        if hasattr(node, 'level') and (node.level or 0) > 1:
            error.error("unsupported relative import", self.gx, node, mv=getmv())

        # from . import
        if node.module is None and hasattr(node, 'level') and node.level == 1:
            for alias in node.names:
                submod = self.import_module(alias.name, alias.asname, node, False)
                parent = getmv().module
                parent.mv.imports[submod.ident] = submod
                self.gx.from_module[node] = submod
                return

        # from __future__ import
        if node.module == '__future__':
            for node_name in node.names:
                name = node_name.name
                if name not in ['with_statement', 'print_function']:
                    error.error("future '%s' is not yet supported" % name, self.gx, node, mv=getmv())
            return

        # from [.]a.b.c import  TODO
        module = self.import_modules(node.module, node, True)
        self.gx.from_module[node] = module

        for name_alias in node.names:
            (name, pseudonym) = (name_alias.name, name_alias.asname)
            if name == '*':
                self.ext_funcs.update(module.mv.funcs)
                self.ext_classes.update(module.mv.classes)
                for import_name, import_module in module.mv.imports.items():
                    var = infer.default_var(self.gx, import_name, None, mv=getmv())  # XXX merge
                    var.imported = True
                    self.gx.types[infer.inode(self.gx, var)] = set([(import_module, 0)])
                    self.imports[import_name] = import_module
                for name, extvar in module.mv.globals.items():
                    if not extvar.imported and not name in ['__name__']:
                        var = infer.default_var(self.gx, name, None, mv=getmv())  # XXX merge
                        var.imported = True
                        self.add_constraint((infer.inode(self.gx, extvar), infer.inode(self.gx, var)), None)
                continue

            path = module.path
            pseudonym = pseudonym or name
            if name in module.mv.funcs:
                self.ext_funcs[pseudonym] = module.mv.funcs[name]
            elif name in module.mv.classes:
                self.ext_classes[pseudonym] = module.mv.classes[name]
            elif name in module.mv.globals and not module.mv.globals[name].imported:  # XXX
                extvar = module.mv.globals[name]
                var = infer.default_var(self.gx, pseudonym, None, mv=getmv())
                var.imported = True
                self.add_constraint((infer.inode(self.gx, extvar), infer.inode(self.gx, var)), None)
            elif os.path.isfile(os.path.join(path, name + '.py')) or \
                    os.path.isfile(os.path.join(path, name, '__init__.py')):
                modname = '.'.join(module.name_list + [name])
                self.import_module(modname, name, node, False)
            else:
                error.error("no identifier '%s' in module '%s'" % (name, node.module), self.gx, node, mv=getmv())

    def analyze_module(self, name, pseud, node, fake):
        module = parse_module(name, self.gx, getmv().module, node)
        if not fake:
            self.imports[pseud] = module
        else:
            self.fake_imports[pseud] = module
        return module

    def visit_FunctionDef(self, node, parent=None, is_lambda=False, inherited_from=None):
        if not getmv().module.builtin and (node.args.vararg or node.args.kwarg):
            error.error('argument (un)packing is not supported', self.gx, node, mv=getmv())

        if not parent and not is_lambda and node.name in getmv().funcs:
            func = getmv().funcs[node.name]
        elif isinstance(parent, python.Class) and not inherited_from and node.name in parent.funcs:
            func = parent.funcs[node.name]
        else:
            func = python.Function(self.gx, node, parent, inherited_from, mv=getmv())
            if inherited_from:
                self.set_default_vars(node, func)

        if not python.is_method(func):
            if not getmv().module.builtin and not node in getmv().funcnodes and not is_lambda:
                error.error("non-global function '%s'" % node.name, self.gx, node, mv=getmv())

        if node.decorator_list:
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name) and dec.id == 'staticmethod':
                    parent.staticmethods.append(node.name)
                elif isinstance(dec, ast.Name) and dec.id == 'property':
                    parent.properties[node.name] = [node.name, None]
                elif python.is_property_setter(dec):
                    parent.properties[dec.value.id][1] = node.name
                else:
                    error.error("unsupported type of decorator", self.gx, dec, mv=getmv())

        if parent:
            if not inherited_from and not func.ident in parent.staticmethods and (not func.formals or func.formals[0] != 'self'):
                error.error("formal arguments of method must start with 'self'", self.gx, node, mv=getmv())
            if not func.mv.module.builtin and func.ident in ['__new__', '__getattr__', '__setattr__', '__radd__', '__rsub__', '__rmul__', '__rdiv__', '__rtruediv__', '__rfloordiv__', '__rmod__', '__rdivmod__', '__rpow__', '__rlshift__', '__rrshift__', '__rand__', '__rxor__', '__ror__', '__iter__', '__call__', '__enter__', '__exit__', '__del__', '__copy__', '__deepcopy__']:
                error.error("'%s' is not supported" % func.ident, self.gx, node, warning=True, mv=getmv())

        if is_lambda:
            self.lambdas[node.name] = func

        # --- add unpacking statement for tuple formals
        func.expand_args = {}
        for i, formal in enumerate(func.formals):
            if isinstance(formal, tuple):
                tmp = self.temp_var((node, i), func)
                func.formals[i] = tmp.name
                fake_unpack = Assign([self.unpack_rec(formal)], ast.Name(tmp.name, ast.Load()))
                func.expand_args[tmp.name] = fake_unpack
                self.visit(fake_unpack, func)

        func.defaults = node.args.defaults

        for formal in func.formals:
            var = infer.default_var(self.gx, formal, func)
            var.formal_arg = True

        # --- flow return expressions together into single node
        func.retnode = retnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[retnode] = set()
        func.yieldnode = yieldnode = infer.CNode(self.gx, (node, 'yield'), parent=func, mv=getmv())
        self.gx.types[yieldnode] = set()

        for body_node in node.body:
            self.visit(body_node, func)

        for i, default in enumerate(func.defaults):
            if not python.is_literal(default):
                self.defaults[default] = (len(self.defaults), func, i)
            self.visit(default, None)  # defaults are global

        # --- add implicit 'return None' if no return expressions
        if not func.returnexpr:
            func.fakeret = ast.Return(ast.Name('None', ast.Load()))
            self.visit(func.fakeret, func)

        # --- register function
        if isinstance(parent, python.Class):
            if func.ident not in parent.staticmethods:  # XXX use flag
                infer.default_var(self.gx, 'self', func)
                if func.ident == '__init__' and '__del__' in parent.funcs:  # XXX what if no __init__
                    self.visit(ast_utils.make_call(ast.Attribute(ast.Name('self', ast.Load()), '__del__', ast.Load())), func)
                    self.gx.gc_cleanup = True
            parent.funcs[func.ident] = func

    def unpack_rec(self, formal):
        if isinstance(formal, str):
            return ast.Name(formal, ast.Store())
        else:
            return ast.Tuple([self.unpack_rec(elem) for elem in formal], ast.Store())

    def visit_Lambda(self, node, func=None):
        lambdanr = len(self.lambdas)
        name = '__lambda%d__' % lambdanr
        fakenode = ast.FunctionDef(name, node.args, [ast.Return(node.body)], [])
        self.visit(fakenode, None, True)
        f = self.lambdas[name]
        f.lambdanr = lambdanr
        self.lambdaname[node] = name
        newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set([(f, 0)])
        newnode.copymetoo = True

    def visit_BoolOp(self, node, func):
        newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set()
        for child in node.values:
            if node in self.gx.bool_test_only:
                self.bool_test_add(child)
            self.visit(child, func)
            self.add_constraint((infer.inode(self.gx, child), newnode), func)
            self.temp_var2(child, newnode, func)

    def visit_If(self, node, func=None):
        if python.is_isinstance(node.test):
            self.gx.filterstack.append(node.test.args)
        self.bool_test_add(node.test)
        faker = ast_utils.make_call(ast.Name('bool', ast.Load()), [node.test])
        self.visit(faker, func)
        for child in node.body:
            self.visit(child, func)
        if python.is_isinstance(node.test):
            self.gx.filterstack.pop()
        for child in node.orelse:
            self.visit(child, func)

    def visit_IfExp(self, node, func=None):
        newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set()

        for child in ast.iter_child_nodes(node):
            self.visit(child, func)

        self.add_constraint((infer.inode(self.gx, node.body), newnode), func)
        self.add_constraint((infer.inode(self.gx, node.orelse), newnode), func)

    def visit_Global(self, node, func=None):
        func.globals += node.names

    def visit_List(self, node, func=None):
        self.constructor(node, 'list', func)

    def visit_Dict(self, node, func=None):
        self.constructor(node, 'dict', func)
        #if node.items:  # XXX library bug
        #    node.lineno = node.items[0][0].lineno

    def visit_Repr(self, node, func=None):
        self.fake_func(node, node.value, '__repr__', [], func)

    def visit_Tuple(self, node, func=None):
        if isinstance(node.ctx, ast.Load):
            if len(node.elts) == 2:
                self.constructor(node, 'tuple2', func)
            else:
                self.constructor(node, 'tuple', func)
        elif isinstance(node.ctx, ast.Store):
            raise NotImplementedError
        else:
            error.error('Unknown value of ast.Tuple ctx', self.gx, node, mv=getmv())

    def visit_Subscript(self, node, func=None):  # XXX merge __setitem__, __getitem__
        if isinstance(node.slice, ast.Slice):
            nslice = node.slice
            self.slice(node, node.value, [nslice.lower, nslice.upper, nslice.step], func)

        elif isinstance(node.slice, ast.Del):
            if any(isinstance(dim, ast.Ellipsis) for dim in node.slice.dims):  # XXX also check at setitem
                error.error('ellipsis is not supported', self.gx, node, mv=getmv())
            raise NotImplementedError

        else:
            if isinstance(node.slice, ast.Index):
                subscript = node.slice.value
            else:
                subscript = node.slice

            if isinstance(node.ctx, ast.Del):
                self.fake_func(node, node.value, '__delitem__', [subscript], func)
            elif isinstance(subscript, (ast.List, ast.Tuple)):
                self.fake_func(node, node.value, '__getitem__', [subscript], func)
            else:
                ident = '__getitem__'
                self.fake_func(node, node.value, ident, [subscript], func)

    def visit_Slice(self, node, func=None):
        self.slice(node, node.expr, [node.lower, node.upper, None], func)

    def slice(self, node, expr, nodes, func, replace=None):
        nodes2 = slice_nums(nodes)
        if replace:
            self.fake_func(node, expr, '__setslice__', nodes2 + [replace], func)
        elif isinstance(node.ctx, ast.Del):
            self.fake_func(node, expr, '__delete__', nodes2, func)
        else:
            self.fake_func(node, expr, '__slice__', nodes2, func)

    def visit_UnaryOp(self, node, func=None):
        op_type = type(node.op)
        if op_type == ast.Not:
            self.bool_test_add(node.operand)
            newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
            newnode.copymetoo = True
            self.gx.types[newnode] = set([(python.def_class(self.gx, 'bool_'), 0)])  # XXX new type?
            self.visit(node.operand, func)
        else:
            op_map = {ast.USub: '__neg__', ast.UAdd: '__pos__', ast.Invert: '__invert__'}
            self.fake_func(node, node.operand, op_map[op_type], [], func)

    def visit_Compare(self, node, func=None):
        newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
        newnode.copymetoo = True
        self.gx.types[newnode] = set([(python.def_class(self.gx, 'bool_'), 0)])  # XXX new type?
        self.visit(node.left, func)
        msgs = {ast.Eq: 'eq', ast.NotEq: 'ne', ast.Lt: 'lt', ast.LtE: 'le', ast.Gt: 'gt', ast.GtE: 'ge', ast.In: 'contains', ast.NotIn: 'contains'} # 'Is' and IsNot only in cpp
        left = node.left
        for op, right in zip(node.ops, node.comparators):
            self.visit(right, func)
            msg = msgs.get(type(op))
            if msg == 'contains':
                self.fake_func(node, right, '__' + msg + '__', [left], func)
            elif msg in ('lt', 'gt', 'le', 'ge'):
                fakefunc = ast_utils.make_call(ast.Name('__%s' % msg, ast.Load()), [left, right])
                fakefunc.lineno = left.lineno
                self.visit(fakefunc, func)
            elif msg:
                self.fake_func(node, left, '__' + msg + '__', [right], func)
            left = right

        # tempvars, e.g. (t1=fun())
        for term in node.comparators[:-1]:
            if not (isinstance(term, ast.Name) or ast_utils.is_constant(term)):
                self.temp_var2(term, infer.inode(self.gx, term), func)

    def visit_BinOp(self, node, func=None):
        if type(node.op) == ast.Add:
            self.fake_func(node, node.left, python.aug_msg(node, 'add'), [node.right], func)
        elif type(node.op) == ast.Sub:
            self.fake_func(node, node.left, python.aug_msg(node, 'sub'), [node.right], func)
        elif type(node.op) == ast.Mult:
            self.fake_func(node, node.left, python.aug_msg(node, 'mul'), [node.right], func)
        elif type(node.op) == ast.Div:
            self.fake_func(node, node.left, python.aug_msg(node, 'truediv'), [node.right], func)
        elif type(node.op) == ast.FloorDiv:
            self.fake_func(node, node.left, python.aug_msg(node, 'floordiv'), [node.right], func)
        elif type(node.op) == ast.Pow:
            self.fake_func(node, node.left, '__pow__', [node.right], func)
        elif type(node.op) == ast.Mod:
            if isinstance(node.right, (ast.Tuple, ast.Dict)):
                self.fake_func(node, node.left, '__mod__', [], func)
                if isinstance(node.right, ast.Tuple):
                    for child in node.right.elts:
                        self.visit(child, func)
                        self.fake_func(infer.inode(self.gx, child), child, '__str__', [], func)
                else:
                    for child in ast.iter_child_nodes(node.right):
                        self.visit(child, func)
            else:
                self.fake_func(node, node.left, '__mod__', [node.right], func)
        elif type(node.op) == ast.LShift:
            self.fake_func(node, node.left, python.aug_msg(node, 'lshift'), [node.right], func)
        elif type(node.op) == ast.RShift:
            self.fake_func(node, node.left, python.aug_msg(node, 'rshift'), [node.right], func)
        elif type(node.op) == ast.BitOr:
            self.visit_impl_bitpair(node, python.aug_msg(node, 'or'), func)
        elif type(node.op) == ast.BitXor:
            self.visit_impl_bitpair(node, python.aug_msg(node, 'xor'), func)
        elif type(node.op) == ast.BitAnd:
            self.visit_impl_bitpair(node, python.aug_msg(node, 'and'), func)
        # PY3: elif type(node.op) == MatMult:
        else:
            error.error("Unknown op type for ast.BinOp: %s" % type(node.op), self.gx, node, mv=getmv())

    def visit_impl_bitpair(self, node, msg, func=None):
        infer.CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[infer.inode(self.gx, node)] = set()
        faker = self.fake_func((node.left, 0), node.left, msg, [node.right], func)
        self.add_constraint((infer.inode(self.gx, faker), infer.inode(self.gx, node)), func)

    def visit_AugAssign(self, node, func=None):  # a[b] += c -> a[b] = a[b]+c, using tempvars to handle sidefx
        newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set()

        clone = copy.deepcopy(node)
        lnode = node.target

        if isinstance(node.target, ast.Name):
            blah = node.target
            lnode = ast.Name(clone.target.id, ast.Load(), lineno=node.target.lineno)
        elif isinstance(node.target, ast.Attribute):
            blah = node.target
            lnode = ast.Attribute(clone.target.value, clone.target.attr, ast.Load(), lineno=node.target.lineno)
        elif isinstance(node.target, ast.Subscript):
            t1 = self.temp_var(node.target.value, func)
            a1 = ast.Assign([ast.Name(t1.name, ast.Store())], node.target.value)
            self.visit(a1, func)
            self.add_constraint((infer.inode(self.gx, node.target.value), infer.inode(self.gx, t1)), func)

            if isinstance(node.target.slice, ast.Index):
                subs = node.target.slice.value
            else:
                subs = node.target.slice
            t2 = self.temp_var(subs, func)
            a2 = ast.Assign([ast.Name(t2.name, ast.Store())], subs)

            self.visit(a1, func)
            self.visit(a2, func)
            self.add_constraint((infer.inode(self.gx, subs), infer.inode(self.gx, t2)), func)

            infer.inode(self.gx, node).temp1 = t1.name
            infer.inode(self.gx, node).temp2 = t2.name
            infer.inode(self.gx, node).subs = subs

            blah = ast.Subscript(ast.Name(t1.name, ast.Load(), lineno=node.lineno), ast.Index(ast.Name(t2.name, ast.Load())), ast.Store(), lineno=node.lineno)
            lnode = ast.Subscript(ast.Name(t1.name, ast.Load(), lineno=node.lineno), ast.Index(ast.Name(t2.name, ast.Load())), ast.Load(), lineno=node.lineno)
        else:
            error.error('unsupported type of assignment', self.gx, node, mv=getmv())

        blah2 = ast.BinOp(lnode, node.op, node.value)
        blah2.augment = True

        assign = ast.Assign([blah], blah2)
        register_node(assign, func)
        infer.inode(self.gx, node).assignhop = assign
        self.visit(assign, func)

    def visit_Print(self, node, func=None):
        pnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[pnode] = set()

        for child in ast.iter_child_nodes(node):
            self.visit(child, func)
            self.fake_func(infer.inode(self.gx, child), child, '__str__', [], func)

    def temp_var(self, node, func=None, looper=None, wopper=None, exc_name=False):
        if node in self.gx.parent_nodes:
            varname = self.tempcount[self.gx.parent_nodes[node]]
        elif node in self.tempcount:  # XXX investigate why this happens
            varname = self.tempcount[node]
        else:
            varname = '__' + str(len(self.tempcount))

        var = infer.default_var(self.gx, varname, func, mv=getmv(), exc_name=exc_name)
        var.looper = looper
        var.wopper = wopper
        self.tempcount[node] = varname

        infer.register_temp_var(var, func)
        return var

    def temp_var2(self, node, source, func):
        tvar = self.temp_var(node, func)
        self.add_constraint((source, infer.inode(self.gx, tvar)), func)
        return tvar

    def temp_var_int(self, node, func):
        var = self.temp_var(node, func)
        self.gx.types[infer.inode(self.gx, var)] = set([(python.def_class(self.gx, 'int_'), 0)])
        infer.inode(self.gx, var).copymetoo = True
        return var

    def visit_Raise(self, node, func=None):
        if hasattr(node, 'exc'):
            if node.exc is None or node.cause is not None:
                error.error('unsupported raise syntax', self.gx, node, mv=getmv())
        else: # py2
            if node.type is None or node.inst is not None or node.tback is not None:
                error.error('unsupported raise syntax', self.gx, node, mv=getmv())
        for child in ast.iter_child_nodes(node):
            self.visit(child, func)

    def visit_Assert(self, node, func=None):
        self.visit(node.test, func)
        if node.msg:
            self.visit(node.msg, func)

    def visit_Try(self, node, func=None): # py3
        self.visit_TryExcept(node, func)

    def visit_TryExcept(self, node, func=None):
        for child in node.body:
            self.visit(child, func)

        for handler in node.handlers:
            if not handler.type:
                continue

            if isinstance(handler.type, ast.Tuple):
                pairs = [(n, handler.name) for n in handler.type.elts]
            else:
                pairs = [(handler.type, handler.name)]

            for (h0, h1) in pairs:
                if isinstance(h0, ast.Name) and h0.id in ['int', 'float', 'str', 'class']:
                    continue  # handle in python.lookup_class
                cl = python.lookup_class(h0, getmv())
                if not cl:
                    if isinstance(h0, ast.Name):
                        name = "('" + h0.id + "')"
                    else:
                        name = ''
                    error.error("unknown/unsupported exception type %s" % name, self.gx, h0, mv=getmv())

                if isinstance(h1, str):
                    var = self.default_var(h1, func, exc_name=True)
                elif isinstance(h1, ast.Name): # py2
                    var = self.default_var(h1.id, func, exc_name=True)
                else:
                    var = self.temp_var(h0, func, exc_name=True)

                var.invisible = True
                infer.inode(self.gx, var).copymetoo = True
                self.gx.types[infer.inode(self.gx, var)] = set([(cl, 1)])

        if node.finalbody:
            error.error("'try..finally' is not supported", self.gx, node, mv=getmv())

        for handler in node.handlers:
            for child in handler.body:
                self.visit(child, func)

        # else
        if node.orelse:
            for child in node.orelse:
                self.visit(child, func)
            self.temp_var_int(ast_utils.orelse_to_node(node), func)

    def visit_Yield(self, node, func):
        func.isGenerator = True
        func.yieldNodes.append(node)
        if not node.value:
            node.value = ast.Name('None', ast.Load())
        self.visit(ast.Return(ast_utils.make_call(ast.Name('__iter', ast.Load()), [node.value])), func)
        self.add_constraint((infer.inode(self.gx, node.value), func.yieldnode), func)

    def visit_For(self, node, func=None):
        # --- iterable contents -> assign node
        assnode = infer.CNode(self.gx, node.target, parent=func, mv=getmv())
        self.gx.types[assnode] = set()

        get_iter = ast_utils.make_call(ast.Attribute(node.iter, '__iter__', ast.Load()), [])
        fakefunc = ast_utils.make_call(ast.Attribute(get_iter, '__next__', ast.Load()), [])

        self.visit(fakefunc, func)
        self.add_constraint((infer.inode(self.gx, fakefunc), assnode), func)

        # --- assign node -> variables  XXX merge into assign_pair
        if isinstance(node.target, ast.Name):
            # for x in..
            lvar = self.default_var(node.target.id, func)
            self.add_constraint((assnode, infer.inode(self.gx, lvar)), func)

        elif ast_utils.is_assign_attribute(node.target):  # XXX experimental :)
            # for expr.x in..
            infer.CNode(self.gx, node.target, parent=func, mv=getmv())

            self.gx.assign_target[node.target.value] = node.target.value  # XXX multiple targets possible please
            fakefunc2 = ast_utils.make_call(ast.Attribute(node.target.value, '__setattr__', ast.Load()), [ast.Str(node.target.attr), fakefunc])
            self.visit(fakefunc2, func)

        elif ast_utils.is_assign_list_or_tuple(node.target):
            # for (a,b, ..) in..
            self.tuple_flow(node.target, node.target, func)
        else:
            error.error('unsupported type of assignment', self.gx, node, mv=getmv())

        self.do_for(node, assnode, get_iter, func)

        # --- for-else
        if node.orelse:
            self.temp_var_int(ast_utils.orelse_to_node(node), func)
            for child in node.orelse:
                self.visit(child, func)

        # --- loop body
        self.gx.loopstack.append(node)
        for child in node.body:
            self.visit(child, func)
        self.gx.loopstack.pop()
        self.for_in_iters.append(node.iter)

    def do_for(self, node, assnode, get_iter, func):
        # --- for i in range(..) XXX i should not be modified.. use tempcounter; two bounds
        if python.is_fastfor(node):
            self.temp_var2(node.target, assnode, func)
            self.temp_var2(node.iter, infer.inode(self.gx, node.iter.args[0]), func)

            if len(node.iter.args) == 3 and not isinstance(node.iter.args[2], ast.Name) and not python.is_literal(node.iter.args[2]):  # XXX merge with ast.ListComp
                for arg in node.iter.args:
                    if not isinstance(arg, ast.Name) and not python.is_literal(arg):  # XXX create func for better check
                        self.temp_var2(arg, infer.inode(self.gx, arg), func)

        # --- temp vars for list, iter etc.
        else:
            self.temp_var2(node, infer.inode(self.gx, node.iter), func)
            self.temp_var2((node, 1), infer.inode(self.gx, get_iter), func)
            self.temp_var_int(node.iter, func)

            if python.is_enum(node) or python.is_zip2(node):
                self.temp_var2((node, 2), infer.inode(self.gx, node.iter.args[0]), func)
                if python.is_zip2(node):
                    self.temp_var2((node, 3), infer.inode(self.gx, node.iter.args[1]), func)
                    self.temp_var_int((node, 4), func)

            self.temp_var((node, 5), func, looper=node.iter)
            if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Attribute):
                self.temp_var((node, 6), func, wopper=node.iter.func.value)
                self.temp_var2((node, 7), infer.inode(self.gx, node.iter.func.value), func)

    def bool_test_add(self, node):
        if isinstance(node, ast.BoolOp) or isinstance(node, ast.UnaryOp) and type(node.op) == ast.FloorDiv:
            self.gx.bool_test_only.add(node)

    def visit_While(self, node, func=None):
        self.gx.loopstack.append(node)
        self.bool_test_add(node.test)
        for child in ast.iter_child_nodes(node):
            self.visit(child, func)
        self.gx.loopstack.pop()

        if node.orelse:
            self.temp_var_int(ast_utils.orelse_to_node(node), func)
            for child in node.orelse:
                self.visit(child, func)

    def visit_Continue(self, node, func=None):
        pass

    def visit_Break(self, node, func=None):
        pass

    def visit_With(self, node, func=None):
        for child in ast.iter_child_nodes(node):
            self.visit(child, func)

        if hasattr(node, 'items'):
            node = node.items[0] # TODO py3: multiple items

        if node.optional_vars:
            varnode = infer.CNode(self.gx, node.optional_vars, parent=func, mv=getmv())
            self.gx.types[varnode] = set()
            self.add_constraint((infer.inode(self.gx, node.context_expr), varnode), func)
            lvar = self.default_var(node.optional_vars.id, func)
            self.add_constraint((varnode, infer.inode(self.gx, lvar)), func)

    def visit_ListComp(self, node, func=None):
        # --- [expr for iter in list for .. if cond ..]
        lcfunc = python.Function(self.gx, mv=getmv())
        lcfunc.listcomp = True
        lcfunc.ident = 'l.c.'  # XXX
        lcfunc.parent = func

        for qual in node.generators:
            # iter
            assnode = infer.CNode(self.gx, qual.target, parent=func, mv=getmv())
            self.gx.types[assnode] = set()

            # list.unit->iter
            get_iter = ast_utils.make_call(ast.Attribute(qual.iter, '__iter__', ast.Load()), [])
            fakefunc = ast_utils.make_call(ast.Attribute(get_iter, '__next__', ast.Load()), [])
            self.visit(fakefunc, lcfunc)
            self.add_constraint((infer.inode(self.gx, fakefunc), infer.inode(self.gx, qual.target)), lcfunc)

            if isinstance(qual.target, ast.Name):  # XXX merge with visit_For
                lvar = infer.default_var(self.gx, qual.target.id, lcfunc)  # XXX str or ast.Name?
                self.add_constraint((infer.inode(self.gx, qual.target), infer.inode(self.gx, lvar)), lcfunc)
            else:  # AssTuple, AssList
                self.tuple_flow(qual.target, qual.target, lcfunc)

            self.do_for(qual, assnode, get_iter, lcfunc)

            # cond
            for child in qual.ifs:
                self.bool_test_add(child)
                self.visit(child, lcfunc)

            self.for_in_iters.append(qual.iter)

        # node type
        if node in self.gx.genexp_to_lc.values():  # converted generator expression
            self.instance(node, python.def_class(self.gx, '__iter'), func)
        else:
            self.instance(node, python.def_class(self.gx, 'list'), func)

        # expr->instance.unit
        self.visit(node.elt, lcfunc)
        self.add_dynamic_constraint(node, node.elt, 'unit', lcfunc)

        lcfunc.ident = 'list_comp_' + str(len(self.listcomps))
        self.listcomps.append((node, lcfunc, func))

    def visit_Return(self, node, func):
        if node.value is None:
            node.value = ast.Name('None', ast.Load())
        self.visit(node.value, func)
        func.returnexpr.append(node.value)
        if node.value is not None:  # Not naked return
            newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
            self.gx.types[newnode] = set()
            if isinstance(node.value, ast.Name):
                func.retvars.append(node.value.id)
        if func.retnode:
            self.add_constraint((infer.inode(self.gx, node.value), func.retnode), func)

    def visit_Delete(self, node, func=None):
        for child in node.targets:
            assert type(child.ctx) == ast.Del
            self.visit(child, func)

    def visit_Assign(self, node, func=None):
        # --- rewrite for struct.unpack XXX rewrite callfunc as tuple
        if len(node.targets) == 1:
            lvalue, rvalue = node.targets[0], node.value
            if self.struct_unpack(rvalue, func) and ast_utils.is_assign_list_or_tuple(lvalue) and not [n for n in lvalue.elts if ast_utils.is_assign_list_or_tuple(n)]:
                self.visit(node.value, func)
                sinfo = self.struct_info(rvalue.args[0], func)
                faketuple = self.struct_faketuple(sinfo)
                self.visit(ast.Assign(node.targets, faketuple), func)
                tvar = self.temp_var2(rvalue.args[1], infer.inode(self.gx, rvalue.args[1]), func)
                tvar_pos = self.temp_var_int(rvalue.args[0], func)
                self.gx.struct_unpack[node] = (sinfo, tvar.name, tvar_pos.name)
                return

        newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
        self.gx.types[newnode] = set()

        # --- a,b,.. = c,(d,e),.. = .. = expr
        for target_expr in node.targets:
            pairs = python.assign_rec(target_expr, node.value)
            for (lvalue, rvalue) in pairs:
                # expr[expr] = expr
                if isinstance(lvalue, ast.Subscript) and not isinstance(lvalue.slice, (ast.Slice, ast.Del)):
                    self.assign_pair(lvalue, rvalue, func)  # XXX use here generally, and in tuple_flow

                # expr.attr = expr
                elif ast_utils.is_assign_attribute(lvalue):
                    self.assign_pair(lvalue, rvalue, func)

                # name = expr
                elif isinstance(lvalue, ast.Name):
                    if (rvalue, 0, 0) not in self.gx.cnode:  # XXX generalize
                        self.visit(rvalue, func)
                    self.visit(lvalue, func)
                    lvar = self.default_var(lvalue.id, func)
                    if ast_utils.is_constant(rvalue):
                        lvar.const_assign.append(rvalue)
                    self.add_constraint((infer.inode(self.gx, rvalue), infer.inode(self.gx, lvar)), func)

                # (a,(b,c), ..) = expr
                elif ast_utils.is_assign_list_or_tuple(lvalue):
                    self.visit(rvalue, func)
                    self.tuple_flow(lvalue, rvalue, func)

                # expr[a:b] = expr # XXX bla()[1:3] = [1]
                elif isinstance(lvalue, ast.Slice):
                    assert False, "ast.Slice shouldn't appear outside ast.Subscript node"
                    self.slice(lvalue, lvalue.expr, [lvalue.lower, lvalue.upper, None], func, rvalue)

                # expr[a:b:c] = expr
                elif isinstance(lvalue, ast.Subscript) and isinstance(lvalue.slice, ast.Slice):
                    lslice = lvalue.slice
                    self.slice(lvalue, lvalue.value, [lslice.lower, lslice.upper, lslice.step], func, rvalue)

        # temp vars
        if len(node.targets) > 1 or isinstance(node.value, ast.Tuple):
            if isinstance(node.value, ast.Tuple):
                if [n for n in node.targets if ast_utils.is_assign_tuple(n)]:
                    for child in node.value.elts:
                        if (child, 0, 0) not in self.gx.cnode:  # (a,b) = (1,2): (1,2) never visited
                            continue
                        if not ast_utils.is_constant(child) and not ast_utils.is_none(child):
                            self.temp_var2(child, infer.inode(self.gx, child), func)
            elif not ast_utils.is_constant(node.value) and not ast_utils.is_none(node.value):
                self.temp_var2(node.value, infer.inode(self.gx, node.value), func)

    def assign_pair(self, lvalue, rvalue, func):
        # expr[expr] = expr
        if isinstance(lvalue, ast.Subscript) and not isinstance(lvalue.slice, (ast.Slice, ast.Del)):
            if isinstance(lvalue.slice, ast.Index):
                subscript = lvalue.slice.value
            else:
                subscript = lvalue.slice

            fakefunc = ast_utils.make_call(ast.Attribute(lvalue.value, '__setitem__', ast.Load()), [subscript, rvalue])
            self.visit(fakefunc, func)
            infer.inode(self.gx, lvalue.value).fakefunc = fakefunc

            if not isinstance(lvalue.value, ast.Name):
                self.temp_var2(lvalue.value, infer.inode(self.gx, lvalue.value), func)

        # expr.attr = expr
        elif ast_utils.is_assign_attribute(lvalue):
            infer.CNode(self.gx, lvalue, parent=func, mv=getmv())
            self.gx.assign_target[rvalue] = lvalue.value
            fakefunc = ast_utils.make_call(ast.Attribute(lvalue.value, '__setattr__', ast.Load()), [ast.Str(lvalue.attr), rvalue])
            self.visit(fakefunc, func)

    def default_var(self, name, func, exc_name=False):
        if isinstance(func, python.Function) and name in func.globals:
            return infer.default_var(self.gx, name, None, mv=getmv(), exc_name=exc_name)
        else:
            return infer.default_var(self.gx, name, func, mv=getmv(), exc_name=exc_name)

    def tuple_flow(self, lvalue, rvalue, func=None):
        self.temp_var2(lvalue, infer.inode(self.gx, rvalue), func)

        if ast_utils.is_assign_list_or_tuple(lvalue):
            lvalue = lvalue.elts
        for (i, item) in enumerate(lvalue):
            fakenode = infer.CNode(self.gx, (item,), parent=func, mv=getmv())  # fake node per item, for multiple callfunc triggers
            self.gx.types[fakenode] = set()
            self.add_constraint((infer.inode(self.gx, rvalue), fakenode), func)

            fakefunc = ast_utils.make_call(FakeGetattr3(rvalue, '__getitem__', ast.Load()), [ast.Num(i)])

            fakenode.callfuncs.append(fakefunc)
            self.visit(fakefunc, func)

            self.gx.item_rvalue[item] = rvalue
            if isinstance(item, ast.Name):
                lvar = self.default_var(item.id, func)
                self.add_constraint((infer.inode(self.gx, fakefunc), infer.inode(self.gx, lvar)), func)
            elif isinstance(item, ast.Subscript) or ast_utils.is_assign_attribute(item):
                self.assign_pair(item, fakefunc, func)
            elif ast_utils.is_assign_list_or_tuple(item):  # recursion
                self.tuple_flow(item, fakefunc, func)
            else:
                error.error('unsupported type of assignment', self.gx, item, mv=getmv())

    def super_call(self, orig, parent):
        node = orig.func
        while isinstance(parent, python.Function):
            parent = parent.parent
        if (isinstance(node.value, ast.Call) and
            node.attr not in ('__getattr__', '__setattr__') and
            isinstance(node.value.func, ast.Name) and
                node.value.func.id == 'super'):
            if (len(node.value.args) >= 2 and
                    isinstance(node.value.args[1], ast.Name) and node.value.args[1].id == 'self'):
                cl = python.lookup_class(node.value.args[0], getmv())
                if cl.node.bases:
                    return cl.node.bases[0]
            error.error("unsupported usage of 'super'", self.gx, orig, mv=getmv())

    def visit_Pass(self, node, func=None):
        pass

    def visit_Call(self, node, func=None):  # XXX clean up!!
        newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())

        if isinstance(node.func, ast.Attribute) and type(node.func.ctx) == ast.Load:  # XXX import math; math.e
            # rewrite super(..) call
            base = self.super_call(node, func)
            if base:
                node.func = ast.Attribute(copy.deepcopy(base), node.func.attr, ast.Load())
                node.args = [ast.Name('self', ast.Load())] + node.args

            # method call
            if isinstance(node.func, FakeGetattr):  # XXX butt ugly
                self.visit(node.func.value, func)
            elif isinstance(node.func, FakeGetattr2):
                self.gx.types[newnode] = set()  # XXX move above

                self.callfuncs.append((node, func))

                for arg in node.args:
                    infer.inode(self.gx, arg).callfuncs.append(node)  # this one too

                return
            elif isinstance(node.func, FakeGetattr3):
                pass
            else:
                self.visit_Attribute(node.func, func, callfunc=True)
                infer.inode(self.gx, node.func).callfuncs.append(node)  # XXX iterative dataflow analysis: move there?
                infer.inode(self.gx, node.func).fakert = True

            ident = node.func.attr
            infer.inode(self.gx, node.func.value).callfuncs.append(node)  # XXX iterative dataflow analysis: move there?

            if isinstance(node.func.value, ast.Name) and node.func.value.id in getmv().imports and node.func.attr == '__getattr__':  # XXX analyze_callfunc
                if node.args[0].s in getmv().imports[node.func.value.id].mv.globals:  # XXX bleh
                    self.add_constraint((infer.inode(self.gx, getmv().imports[node.func.value.id].mv.globals[node.args[0].s]), newnode), func)

        elif isinstance(node.func, ast.Name):
            # direct call
            ident = node.func.id
            if ident == 'print':
                ident = node.func.id = '__print'  # XXX

            if ident == 'open' and len(node.args) > 1 and 'b' in node.args[1].s:
                ident = node.func.id = 'open_binary'

            if ident in ['hasattr', 'getattr', 'setattr', 'slice', 'type', 'Ellipsis']:
                error.error("'%s' function is not supported" % ident, self.gx, node.func, mv=getmv())
            if ident == 'dict' and node.keywords:
                error.error('unsupported method of initializing dictionaries', self.gx, node, mv=getmv())
            if ident == 'isinstance':
                error.error("'isinstance' is not supported; always returns True", self.gx, node, mv=getmv(), warning=True)

            if python.lookup_var(ident, func, mv=getmv()):
                self.visit(node.func, func)
                infer.inode(self.gx, node.func).callfuncs.append(node)  # XXX iterative dataflow analysis: move there
        else:
            self.visit(node.func, func)
            infer.inode(self.gx, node.func).callfuncs.append(node)  # XXX iterative dataflow analysis: move there

        # --- arguments
        if not getmv().module.builtin and ast_utils.has_star_kwarg(node):
            error.error('argument (un)packing is not supported', self.gx, node, mv=getmv())

        for arg in ast_utils.get_arg_nodes(node):
            self.visit(arg, func)
            infer.inode(self.gx, arg).callfuncs.append(node)  # this one too

        # --- handle instantiation or call
        constructor = python.lookup_class(node.func, getmv())
        if constructor and (not isinstance(node.func, ast.Name) or not python.lookup_var(node.func.id, func, mv=getmv())):
            self.instance(node, constructor, func)
            infer.inode(self.gx, node).callfuncs.append(node)  # XXX see above, investigate
        else:
            self.gx.types[newnode] = set()

        self.callfuncs.append((node, func))

    def visit_ClassDef(self, node, parent=None):
        if not getmv().module.builtin and not node in getmv().classnodes:
            error.error("non-global class '%s'" % node.name, self.gx, node, mv=getmv())
        if len(node.bases) > 1:
            error.error('multiple inheritance is not supported', self.gx, node, mv=getmv())

        if not getmv().module.builtin:
            for base in node.bases:
                if not isinstance(base, (ast.Name, ast.Attribute)):
                    error.error("invalid expression for base class", self.gx, node, mv=getmv())

                if isinstance(base, ast.Name):
                    name = base.id
                else:
                    name = base.attr

                cl = python.lookup_class(base, getmv())
                if not cl:
                    error.error("no such class: '%s'" % name, self.gx, node, mv=getmv())

                elif cl.mv.module.builtin and name not in ['object', 'Exception', 'tzinfo']:
                    if python.def_class(self.gx, 'Exception') not in cl.ancestors():
                        error.error("inheritance from builtin class '%s' is not supported" % name, self.gx, node, mv=getmv())

        if node.name in getmv().classes:
            newclass = getmv().classes[node.name]  # set in visit_Module, for forward references
        else:
            check_redef(self.gx, node)  # XXX merge with visit_Module
            newclass = python.Class(self.gx, node, getmv())
            self.classes[node.name] = newclass
            getmv().classes[node.name] = newclass
            newclass.module = self.module
            newclass.parent = python.StaticClass(newclass, getmv())
            return

        # --- built-in functions
        for cl in [newclass, newclass.parent]:
            for ident in ['__setattr__', '__getattr__']:
                func = python.Function(self.gx, mv=getmv())
                func.ident = ident
                func.parent = cl

                if ident == '__setattr__':
                    func.formals = ['name', 'whatsit']
                    retexpr = ast.Return(value=None)
                    self.visit(retexpr, func)
                elif ident == '__getattr__':
                    func.formals = ['name']

                cl.funcs[ident] = func

        # --- built-in attributes
        if 'class_' in getmv().classes or 'class_' in getmv().ext_classes:
            var = infer.default_var(self.gx, '__class__', newclass)
            var.invisible = True
            self.gx.types[infer.inode(self.gx, var)] = set([(python.def_class(self.gx, 'class_'), python.def_class(self.gx, 'class_').dcpa)])
            python.def_class(self.gx, 'class_').dcpa += 1

        # --- staticmethod, property
        skip = []
        for child in node.body:
            if isinstance(child, ast.Assign) and len(child.targets) == 1:
                lvalue, rvalue = child.targets[0], child.value
                if isinstance(lvalue, ast.Name) and isinstance(rvalue, ast.Call) and isinstance(rvalue.func, ast.Name) and rvalue.func.id in ['staticmethod', 'property']:
                    if rvalue.func.id == 'property':
                        if len(rvalue.args) == 1 and isinstance(rvalue.args[0], ast.Name):
                            newclass.properties[lvalue.id] = rvalue.args[0].id, None
                        elif len(rvalue.args) == 2 and isinstance(rvalue.args[0], ast.Name) and isinstance(rvalue.args[1], ast.Name):
                            newclass.properties[lvalue.id] = rvalue.args[0].id, rvalue.args[1].id
                        else:
                            error.error("complex properties are not supported", self.gx, rvalue, mv=getmv())
                    else:
                        newclass.staticmethods.append(lvalue.id)
                    skip.append(child)

        # --- children
        for child in node.body:
            if child not in skip:
                cl = self.classes[node.name]
                if isinstance(child, ast.FunctionDef):
                    self.visit(child, cl)
                else:
                    cl.parent.static_nodes.append(child)
                    self.visit(child, cl.parent)

        # --- __iadd__ etc.
        if not newclass.mv.module.builtin or newclass.ident in ['int_', 'float_', 'str_', 'tuple', 'complex']:
            msgs = ['add', 'mul']  # XXX mod, pow
            if newclass.ident in ['int_', 'float_']:
                msgs += ['sub', 'truediv', 'floordiv']
            if newclass.ident in ['int_']:
                msgs += ['lshift', 'rshift', 'and', 'xor', 'or']
            for msg in msgs:
                if not '__i' + msg + '__' in newclass.funcs:
                    self.visit(ast_utils.parse_expr('def __i%s__(self, other): return self.__%s__(other)' % (msg, msg)), newclass)

        # --- __str__, __hash__ # XXX model in lib/builtin.py, other defaults?
        if not newclass.mv.module.builtin and not '__str__' in newclass.funcs:
            self.visit(ast.FunctionDef('__str__', ast_utils.make_arg_list(['self']), [ast.Return(ast_utils.make_call(ast.Attribute(ast.Name('self', ast.Load()), '__repr__', ast.Load())))], []), newclass)
            newclass.funcs['__str__'].invisible = True
        if not newclass.mv.module.builtin and not '__hash__' in newclass.funcs:
            self.visit(ast.FunctionDef('__hash__', ast_utils.make_arg_list(['self']), [ast.Return(ast.Num(0))], []), newclass)
            newclass.funcs['__hash__'].invisible = True

    def visit_Attribute(self, node, func=None, callfunc=False):
        if type(node.ctx) == ast.Load:
            if node.attr in ['__doc__']:
                error.error('%s attribute is not supported' % node.attr, self.gx, node, mv=getmv())

            newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
            self.gx.types[newnode] = set()

            fakefunc = ast_utils.make_call(FakeGetattr(node.value, '__getattr__', ast.Load()), [ast.Str(node.attr)])
            self.visit(fakefunc, func)
            self.add_constraint((self.gx.cnode[fakefunc, 0, 0], newnode), func)

            self.callfuncs.append((fakefunc, func))

            if not callfunc:
                self.fncl_passing(node, newnode, func)
        elif type(node.ctx) == ast.Store:
            raise NotImplementedError
        elif type(node.ctx) == ast.Del:
            self.visit(node.value, func)
        else:
            raise NotImplementedError
            error.error('unknown ctx type for ast.Attribute, %s' % node.ctx, self.gx, node, mv=getmv())

    def visit_Constant(self, node, func=None):
        if node.value.__class__.__name__ == 'ellipsis':
            error.error('ellipsis is not supported', self.gx, node, mv=getmv())
        else:
            map = {int: 'int_', float: 'float_', complex: 'complex', str: 'str_', bool: 'bool_', type(None): 'none', bytes: 'bytes_'}
            self.instance(node, python.def_class(self.gx, map[type(node.value)]), func)

    # py2 ast
    def visit_Num(self, node, func=None):
        map = {int: 'int_', float: 'float_', long: 'int_', complex: 'complex'}  # XXX 'return' -> ast.Return(Constant(None))?
        self.instance(node, python.def_class(self.gx, map[type(node.n)]), func)

    # py2 ast
    def visit_Str(self, node, func=None):
        map = {str: 'str_'}
        self.instance(node, python.def_class(self.gx, map[type(node.s)]), func)

    def fncl_passing(self, node, newnode, func):
        lfunc, lclass = python.lookup_func(node, getmv()), python.lookup_class(node, getmv())
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
        if type(node.ctx) == ast.Load:
            newnode = infer.CNode(self.gx, node, parent=func, mv=getmv())
            self.gx.types[newnode] = set()

            if node.id == '__doc__':
                error.error("'%s' attribute is not supported" % node.id, self.gx, node, mv=getmv())

            if node.id in ['None', 'True', 'False']:
                if node.id == 'None':  # XXX also bools, remove def seed_nodes()
                    self.instance(node, python.def_class(self.gx, 'none'), func)
                else:
                    self.instance(node, python.def_class(self.gx, 'bool_'), func)
                return

            if isinstance(func, python.Function) and node.id in func.globals:
                var = infer.default_var(self.gx, node.id, None, mv=getmv())
            else:
                var = python.lookup_var(node.id, func, mv=getmv())
                if not var:
                    if self.fncl_passing(node, newnode, func):
                        pass
                    elif node.id in ['int', 'float', 'str']:  # XXX
                        cl = self.ext_classes[node.id + '_']
                        self.gx.types[newnode] = set([(cl.parent, 0)])
                        newnode.copymetoo = True
                    else:
                        var = infer.default_var(self.gx, node.id, None, mv=getmv())
            if var:
                self.add_constraint((infer.inode(self.gx, var), newnode), func)
                for a, b in self.gx.filterstack:
                    if var.name == a.id:
                        self.gx.filters[node] = python.lookup_class(b, getmv())
        elif type(node.ctx) == ast.Store:
            # Adding vars for ast.Name store are handled elsewhere
            pass
        elif type(node.ctx) == ast.Del:
            # Do nothing
            pass
        else:
            error.error('unknown ctx type for ast.Name, %s' % node.ctx, self.gx, node, mv=getmv())

    def builtin_wrapper(self, node, func):
        node2 = ast_utils.make_call(copy.deepcopy(node), [ast.Name(x, ast.Load()) for x in 'abcde'])
        l = ast.Lambda(ast_utils.make_arg_list(list('abcde')), node2)
        self.visit(l, func)
        self.lwrapper[node] = self.lambdaname[l]
        self.gx.lambdawrapper[node2] = self.lambdaname[l]
        f = self.lambdas[self.lambdaname[l]]
        f.lambdawrapper = True
        infer.inode(self.gx, node2).lambdawrapper = f
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
        absolute_name, filename, relative_filename, builtin = python.find_module(gx, name, module_paths)
        module = python.Module(absolute_name, filename, relative_filename, builtin, node)
    except ImportError:
        error.error('cannot locate module: ' + name, gx, node, mv=getmv())

    # --- check cache
    if module.name in gx.modules:  # cached?
        return gx.modules[module.name]
    gx.modules[module.name] = module

    # --- not cached, so parse
    module.ast = python.parse_file(module.filename)

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
