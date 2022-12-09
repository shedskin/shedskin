
'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2022 Mark Dufour; License GNU GPL version 3 (See LICENSE)

cpp.py: output C++ code

output equivalent C++ code, using templates and virtuals to support data and OO polymorphism.

class GenerateVisitor: inherits visitor pattern from ast_utils.BaseNodeVisitor,
to recursively generate C++ code for each syntactical Python construct.

The constraint graph, with inferred types, is first 'merged' back to program
dimensions (gx.merged_inh).

'''
import ast
import os
import string
import struct
import textwrap

import jinja2

from . import ast_utils
from . import error
from . import extmod
from . import infer
from . import makefile
from . import python
from . import typestr
from . import virtual


class CPPNamer(object):
    def __init__(self, gx, mv):
        self.gx = gx
        self.class_names = [cl.ident for cl in self.gx.allclasses]
        self.cpp_keywords = self.gx.cpp_keywords
        self.ss_prefix = self.gx.ss_prefix
        self.name_by_type = {
            str: self.name_str,
            python.Class: self.name_class,
            python.Function: self.name_function,
            python.Variable: self.name_variable,
        }
        self.mv = mv

    def nokeywords(self, name):
        if name in self.cpp_keywords:
            return self.ss_prefix + name
        return name

    def namespace_class(self, cl, add_cl=''):
        module = cl.mv.module
        if module.ident != 'builtin' and module != self.mv.module and module.name_list:
            return module.full_path() + '::' + add_cl + self.name(cl)
        else:
            return add_cl + self.name(cl)

    def name(self, obj):
        get_name = self.name_by_type[type(obj)]
        name = get_name(obj)

        return self.nokeywords(name)

    def name_variable(self, var):
        if var.masks_global():
            return '_' + var.name
        return self.name_str(var.name)

    def name_function(self, func):
        return self.name_str(func.ident)

    def name_class(self, obj):
        return obj.ident

    def name_str(self, name):
        if [x for x in ('init', 'add') if name == x + self.gx.main_module.ident] or \
                name in self.class_names or name + '_' in self.class_names:
            name = '_' + name
        return name


# --- code generation visitor; use type information

def escape_extra_newlines(text):
    patterns = ['<%block', '<%include']
    results = []
    for line in text.splitlines():
        if any(line.startswith(p) for p in patterns):
            line += '\\'
        results.append(line)
    return '\n'.join(results)


class GenerateVisitor(ast_utils.BaseNodeVisitor):
    def __init__(self, gx, module):
        self.gx = gx
        self.output_base = module.filename[:-3]
        self.out = open(self.output_base + '.cpp', 'w')
        self.indentation = ''
        self.consts = {}
        self.mergeinh = self.gx.merged_inh
        self.module = module
        self.mv = module.mv
        self.name = module.ident
        self.filling_consts = False
        self.with_count = 0
        self.bool_wrapper = {}
        self.namer = CPPNamer(self.gx, self)
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                self.gx.sysdir + '/templates/cpp/'),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.jinja_env.filters['depointer'] = (
            lambda ts: ts[:-1] if ts.endswith('*') else ts)
        self.extmod = extmod.ExtensionModule(self.gx, self)

    def cpp_name(self, obj):
        return self.namer.name(obj)

    # XXX this is too magical 
    def insert_consts(self, declare):  # XXX ugly
        if not self.consts:
            return
        self.filling_consts = True

        if declare:
            suffix = '.hpp'
        else:
            suffix = '.cpp'

        lines = open(self.output_base + suffix, 'r').readlines()
        newlines = []
        j = -1
        for (i, line) in enumerate(lines):
            if line.startswith('namespace ') and not 'XXX' in line:  # XXX
                j = i + 1
            newlines.append(line)

            if i == j:
                pairs = []
                done = set()
                for (node, name) in self.consts.items():
                    if not name in done and node in self.mergeinh and self.mergeinh[node]:  # XXX
                        ts = typestr.nodetypestr(self.gx, node, infer.inode(self.gx, node).parent, mv=self.mv)
                        if declare:
                            ts = 'extern ' + ts
                        pairs.append((ts, name))
                        done.add(name)

                newlines.extend(self.group_declarations(pairs))
                newlines.append('\n')

        newlines2 = []
        j = -1
        for (i, line) in enumerate(newlines):
            if line.startswith('void __init() {'):
                j = i
            newlines2.append(line)

            if i == j:
                todo = {}
                for (node, name) in self.consts.items():
                    if not name in todo:
                        todo[int(name[6:])] = node
                todolist = list(todo)
                todolist.sort()
                for number in todolist:
                    if self.mergeinh[todo[number]]:  # XXX
                        name = 'const_' + str(number)
                        self.start('    ' + name + ' = ')
                        if isinstance(todo[number], ast.Str) and len(todo[number].s.encode('utf-8')) == 1:
                            self.append("__char_cache[%d]" % ord(todo[number].s))
                        else:
                            self.visit(todo[number], infer.inode(self.gx, todo[number]).parent)
                        newlines2.append(self.line + ';\n')

                newlines2.append('\n')

        open(self.output_base + suffix, 'w').writelines(newlines2)
        self.filling_consts = False

    def insert_extras(self, suffix):
        lines = open(self.output_base + suffix, 'r').readlines()
        newlines = []
        for line in lines:
            newlines.append(line)
            if suffix == '.cpp' and line.startswith('#include'):
                newlines.extend(self.include_files())
            elif suffix == '.hpp' and line.startswith('using namespace'):
                newlines.extend(self.fwd_class_refs())
        open(self.output_base + suffix, 'w').writelines(newlines)

    def fwd_class_refs(self):
        lines = []
        for _module in self.module.prop_includes:
            if _module.builtin:
                continue
            for name in _module.name_list:
                lines.append('namespace __%s__ { /* XXX */\n' % name)
            for cl in _module.mv.classes.values():
                lines.append('class %s;\n' % self.cpp_name(cl))
            for name in _module.name_list:
                lines.append('}\n')
        if lines:
            lines.insert(0, '\n')
        return lines

    def include_files(self):
        # find all (indirect) dependencies
        includes = set()
        includes.add(self.module)
        changed = True
        while changed:
            size = len(includes)
            for module in list(includes):
                includes.update(module.prop_includes)
                includes.update(module.mv.imports.values())
                includes.update(module.mv.fake_imports.values())
            changed = (size != len(includes))
        includes = set(i for i in includes if i.ident != 'builtin')
        # order by cross-file inheritance dependencies
        for include in includes:
            include.deps = set()
        for include in includes:
            for cl in include.mv.classes.values():
                if cl.bases:
                    module = cl.bases[0].mv.module
                    if module.ident != 'builtin' and module != include:
                        include.deps.add(module)
        includes1 = [i for i in includes if i.builtin]
        includes2 = [i for i in includes if not i.builtin]
        includes = includes1 + self.includes_rec(set(includes2))
        return ['#include "%s"\n' % module.include_path() for module in includes]

    def includes_rec(self, includes):  # XXX should be recursive!? ugh
        todo = includes.copy()
        result = []
        while todo:
            for include in todo:
                if not include.deps - set(result):
                    todo.remove(include)
                    result.append(include)
                    break
            else:  # XXX circular dependency warning?
                result.append(todo.pop())
        return result

    # --- group pairs of (type, name) declarations, while paying attention to '*'
    def group_declarations(self, pairs):
        group = {}
        for (type, name) in pairs:
            group.setdefault(type, []).append(name)
        result = []
        for (type, names) in group.items():
            names.sort()
            if type.endswith('*'):
                result.append(type + (', *'.join(names)) + ';\n')
            else:
                result.append(type + (', '.join(names)) + ';\n')
        return result

    def header_file(self):
        self.out = open(self.output_base + '.hpp', 'w')
        self.visit(self.module.ast, True)
        self.out.close()

    def print(self, text=None):
        if text is not None:
            print(text, file=self.out)
        else:
            print(file=self.out)

    def output(self, text):
        self.print(self.indentation + text)

    def start(self, text=None):
        self.line = self.indentation
        if text:
            self.line += text

    def append(self, text):
        self.line += text

    def eol(self, text=None):
        if text:
            self.append(text)
        if self.line.strip():
            self.print(self.line + ';')

    def indent(self):
        self.indentation += 4 * ' '

    def deindent(self):
        self.indentation = self.indentation[:-4]

    def visitm(self, *args):
        func = None
        if args and isinstance(args[-1], (python.Function, python.Class)):
            func = args[-1]
        for arg in args[:-1]:
            if isinstance(arg, str):
                self.append(arg)
            else:
                self.visit(arg, func)

    def connector(self, node, func):
        if typestr.singletype(self.gx, node, python.Module):
            return '::'
        elif typestr.unboxable(self.gx, self.mergeinh[node]):
            return '.'
        else:
            return '->'

    def gen_declare_defs(self, vars):
        for name, var in vars:
            if (typestr.singletype(self.gx, var, python.Module) or var.invisible
                    or var.name in {'__exception', '__exception2'}):
                continue
            ts = typestr.nodetypestr(self.gx, var, var.parent, mv=self.mv)
            yield ts, self.cpp_name(var)

    def declare_defs(self, vars, declare):
        pairs = []
        for ts, name in self.gen_declare_defs(vars):
            if declare:
                if 'for_in_loop' in ts:  # XXX
                    continue
                ts = 'extern ' + ts
            pairs.append((ts, name))
        return ''.join(self.group_declarations(pairs))

    def get_constant(self, node):
        parent = infer.inode(self.gx, node).parent
        while isinstance(parent, python.Function) and parent.listcomp:  # XXX
            parent = parent.parent
        if isinstance(parent, python.Function) and (parent.inherited or not self.inhcpa(parent)):  # XXX
            return
        for other in self.consts:  # XXX use mapping
            if node.s == other.s:
                return self.consts[other]
        self.consts[node] = 'const_' + str(len(self.consts))
        return self.consts[node]

    def module_hpp(self, node):
        define = '_'.join(self.module.name_list).upper() + '_HPP'
        self.print('#ifndef __' + define)
        self.print('#define __' + define + '\n')

        # --- namespaces
        self.print('using namespace __shedskin__;')
        for n in self.module.name_list:
            self.print('namespace __' + n + '__ {')
        self.print()

        # class declarations
        for child in node.body:
            if isinstance(child, ast.ClassDef):
                cl = python.def_class(self.gx, child.name, mv=self.mv)
                self.print('class ' + self.cpp_name(cl) + ';')
        self.print()

        # --- lambda typedefs
        self.func_pointers()

        # globals
        defs = self.declare_defs(list(self.mv.globals.items()), declare=True)
        if defs:
            self.output(defs)
            self.print()

        # --- class definitions
        for child in node.body:
            if isinstance(child, ast.ClassDef):
                self.class_hpp(child)

        # --- defaults
        for type, number in self.gen_defaults():
            self.print('extern %s default_%d;' % (type, number))

        # function declarations
        if self.module != self.gx.main_module:
            self.print('void __init();')
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                func = self.mv.funcs[child.name]
                if self.inhcpa(func):
                    self.visit_FunctionDef(func.node, declare=True)
        self.print()

        if self.gx.extension_module:
            self.print('extern "C" {')
            self.extmod.pyinit_func()
            self.print('}')

        for n in self.module.name_list:
            self.print('} // module namespace')

        self.rich_comparison()

        if self.gx.extension_module:
            self.extmod.convert_methods2()

        self.print('#endif')

    def gen_defaults(self):
        for default, (nr, func, func_def_nr) in self.module.mv.defaults.items():
            formal = func.formals[len(func.formals) - len(func.defaults) + func_def_nr]
            var = func.vars[formal]
            yield typestr.typestr(self.gx, self.mergeinh[var], func, mv=self.mv), nr  #  + ' ' + ('default_%d;' % nr)

    def init_defaults(self, func):
        for default in func.args.defaults:
            if default in self.mv.defaults:
                nr, func, func_def_nr = self.mv.defaults[default]
                formal = func.formals[len(func.formals) - len(func.defaults) + func_def_nr]
                var = func.vars[formal]
                if self.mergeinh[var]:
                    ts = [t for t in self.mergeinh[default] if isinstance(t[0], python.Function)]
                    if not ts or [t for t in ts if infer.called(t[0])]:
                        self.start('default_%d = ' % nr)
                        self.impl_visit_conv(default, self.mergeinh[var], None)
                        self.eol()

    def rich_comparison(self):
        cmp_cls, lt_cls, gt_cls, le_cls, ge_cls = [], [], [], [], []
        for cl in self.mv.classes.values():
            if not '__cmp__' in cl.funcs and [f for f in ('__eq__', '__lt__', '__gt__') if f in cl.funcs]:
                cmp_cls.append(cl)
            if not '__lt__' in cl.funcs and '__gt__' in cl.funcs:
                lt_cls.append(cl)
            if not '__gt__' in cl.funcs and '__lt__' in cl.funcs:
                gt_cls.append(cl)
            if not '__le__' in cl.funcs and '__ge__' in cl.funcs:
                le_cls.append(cl)
            if not '__ge__' in cl.funcs and '__le__' in cl.funcs:
                ge_cls.append(cl)
        if cmp_cls or lt_cls or gt_cls or le_cls or ge_cls:
            self.print('namespace __shedskin__ { /* XXX */')
            for cl in cmp_cls:
                t = '__%s__::%s *' % (self.mv.module.ident, self.cpp_name(cl))
                self.print('template<> inline __ss_int __cmp(%sa, %sb) {' % (t, t))
                self.print('    if (!a) return -1;')
                if '__eq__' in cl.funcs:
                    self.print('    if(a->__eq__(b)) return 0;')
                if '__lt__' in cl.funcs:
                    self.print('    return (a->__lt__(b))?-1:1;')
                elif '__gt__' in cl.funcs:
                    self.print('    return (a->__gt__(b))?1:-1;')
                else:
                    self.print('    return __cmp<void *>(a, b);')
                self.print('}')
            self.rich_compare(lt_cls, 'lt', 'gt')
            self.rich_compare(gt_cls, 'gt', 'lt')
            self.rich_compare(le_cls, 'le', 'ge')
            self.rich_compare(ge_cls, 'ge', 'le')
            self.print('}')

    def rich_compare(self, cls, msg, fallback_msg):
        for cl in cls:
            t = '__%s__::%s *' % (self.mv.module.ident, self.cpp_name(cl))
            self.print('template<> inline __ss_bool __%s(%sa, %sb) {' % (msg, t, t))
            # print >>self.out, '    if (!a) return -1;' # XXX check
            self.print('    return b->__%s__(a);' % fallback_msg)
            self.print('}')

    def module_cpp(self, node):
        if ast.get_docstring(node):
            node.doc = ast.get_docstring(node) # necessary for the module-level comments

        file_top = self.jinja_env.get_template('module.cpp.tpl').render(
            node=node,
            module=self.module,
            imports=[
                (child, self.gx.from_module[child])
                for child in node.body
                if isinstance(child, ast.ImportFrom) and child.module != '__future__'],
            globals=self.gen_declare_defs(self.mv.globals.items()),
            nodetypestr=lambda var: typestr.nodetypestr(self.gx, var, var.parent, mv=self.mv),
            defaults=self.gen_defaults(),
            listcomps=self.mv.listcomps,
            cpp_name=self.cpp_name,
            namer=self.namer,
            dedent=textwrap.dedent,
        )
        
        self.print(file_top)

        # --- declarations
        self.listcomps = {}
        for (listcomp, lcfunc, func) in self.mv.listcomps:
            self.listcomps[listcomp] = (lcfunc, func)
        self.do_listcomps(True)
        self.do_lambdas(True)
        self.print()

        # --- definitions
        self.do_listcomps(False)
        self.do_lambdas(False)
        for child in node.body:
            if isinstance(child, ast.ClassDef):
                self.class_cpp(child)
            elif isinstance(child, ast.FunctionDef):
                self.do_comments(child)
                self.visit(child)

        # --- __init
        self.output('void __init() {')
        self.indent()
        if self.module == self.gx.main_module and not self.gx.extension_module:
            self.output('__name__ = new str("__main__");\n')
        else:
            self.output('__name__ = new str("%s");\n' % self.module.ident)

        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self.init_defaults(child)
            elif isinstance(child, ast.ClassDef):
                for child2 in child.body:
                    if isinstance(child2, ast.FunctionDef):
                        self.init_defaults(child2)
                if child.name in self.mv.classes:
                    cl = self.mv.classes[child.name]
                    self.output('cl_' + cl.ident + ' = new class_("%s");' % (cl.ident))
                    if cl.parent.static_nodes:
                        self.output('%s::__static__();' % self.cpp_name(cl))

            elif isinstance(child, ast.Expr):
                self.impl_visit_expr(child)

            elif isinstance(child, ast.ImportFrom) and child.module != '__future__':
                module = self.gx.from_module[child]
                for (name, pseudonym) in [(n.name, n.asname) for n in child.names]:
                    pseudonym = pseudonym or name
                    if name == '*':
                        for var in module.mv.globals.values():
                            if not var.invisible and not var.imported and not var.name.startswith('__') and infer.var_types(self.gx, var):
                                self.start(self.namer.nokeywords(var.name) + ' = ' + module.full_path() + '::' + self.namer.nokeywords(var.name))
                                self.eol()
                    elif pseudonym in self.module.mv.globals and not [t for t in infer.var_types(self.gx, self.module.mv.globals[pseudonym]) if isinstance(t[0], python.Module)]:
                        self.start(self.namer.nokeywords(pseudonym) + ' = ' + module.full_path() + '::' + self.namer.nokeywords(name))
                        self.eol()

            elif not isinstance(child, (ast.ClassDef, ast.FunctionDef)):
                self.do_comments(child)
                self.visit(child)

        self.deindent()
        self.output('}\n')

        # --- close namespace
        for n in self.module.name_list:
            self.print('} // module namespace')
        self.print()

        # --- c++ main/extension module setup
        if self.gx.extension_module:
            self.extmod.do_extmod()
        if self.module == self.gx.main_module:
            self.do_main()

    def impl_visit_expr(self, node, func=None):
        # RESOLVE: When can this happen using compiler?
        # if isinstance(node.value, Constant) and node.value.value is None:  # XXX merge with visit_Stmt
        #     pass
        if isinstance(node.value, ast.Str):
            # self.do_comment(node.value.s) # XXX disabled as it was double printing comments
            pass
        else:
            self.start('')
            self.visit(node.value, func)
            self.eol()

    def visit_Expr(self, node, func=None):
        self.impl_visit_expr(node, func)

    def visit_Import(self, node, func=None):
        pass

    def visit_ImportFrom(self, node, func=None):
        pass

    def visit_Module(self, node, declare=False):
        if declare:
            self.module_hpp(node)
        else:
            self.module_cpp(node)

    def do_main(self):
        modules = self.gx.modules.values()
        if any(module.builtin and module.ident == 'sys' for module in modules):
            self.print('int main(int __ss_argc, char **__ss_argv) {')
        else:
            self.print('int main(int, char **) {')
        self.do_init_modules()
        self.print('    __shedskin__::__start(__%s__::__init);' % self.module.ident)
        self.print('}')

    def do_init_modules(self, extmod=False):
        self.print('    __shedskin__::__init();')
        for module in sorted(self.gx.modules.values(), key=lambda x: x.import_order):
            if module != self.gx.main_module and module.ident != 'builtin':
                if module.ident == 'sys':
                    if self.gx.extension_module:
                        self.print('    __sys__::__init(0, 0);')
                    else:
                        self.print('    __sys__::__init(__ss_argc, __ss_argv);')
                else:
                    if extmod and not module.builtin:
                        self.print('    ' + module.full_path() + '::PyInit_%s();' % '_'.join(module.name_list))
                    self.print('    ' + module.full_path() + '::__init();')

    def do_comment(self, s):
        if not s:
            return
        doc = s.replace('/*', '//').replace('*/', '//').split('\n')
        self.output('/**')
        if doc[0].strip():
            self.output(doc[0])
        rest = textwrap.dedent('\n'.join(doc[1:])).splitlines()
        for l in rest:
            self.output(l)
        self.output('*/')

    def do_comments(self, child):
        if child in self.gx.comments:
            for n in self.gx.comments[child]:
                self.do_comment(n)

    def visit_Continue(self, node, func=None):
        self.output('continue;')

    def visit_With(self, node, func=None):
        orig = node
        if hasattr(node, 'items'):
            node = node.items[0]

        self.start()
        if node.optional_vars:
            self.visitm('WITH_VAR(', node.context_expr, ',', node.optional_vars, func)
        else:
            self.visitm('WITH(', node.context_expr, func)
        self.append(',%d)' % self.with_count)
        self.with_count += 1
        self.print(self.line)
        self.indent()
        self.mv.current_with_vars.append(ast_utils.handle_with_vars(node.optional_vars))
        for child in orig.body:
            self.visit(child, func)
        self.mv.current_with_vars.pop()
        self.deindent()
        self.output('END_WITH')

    def visit_While(self, node, func=None):
        self.print()
        if node.orelse:
            self.output('%s = 0;' % self.mv.tempcount[ast_utils.orelse_to_node(node)])

        self.start('while (')
        self.bool_test(node.test, func)
        self.append(') {')
        self.print(self.line)
        self.indent()
        self.gx.loopstack.append(node)
        for child in node.body:
            self.visit(child, func)
        self.gx.loopstack.pop()
        self.deindent()
        self.output('}')

        if node.orelse:
            self.output('if (!%s) {' % self.mv.tempcount[ast_utils.orelse_to_node(node)])
            self.indent()
            for child in node.orelse:
                self.visit(child, func)
            self.deindent()
            self.output('}')

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
            self.print(self.line + ' {')
            self.indent()
            self.output(class_name + ' *c = new ' + class_name + '();')
            if name == '__deepcopy__':
                self.output('memo->__setitem__(this, c);')
            for var in cl.vars.values():
                if not var.invisible and var in self.gx.merged_inh and self.gx.merged_inh[var]:
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
            self.copy_method(cl, '__copy__', declare)
        if cl.has_deepcopy:
            self.copy_method(cl, '__deepcopy__', declare)

    def class_hpp(self, node):
        cl = self.mv.classes[node.name]
        self.output('extern class_ *cl_' + cl.ident + ';')

        # --- header
        clnames = [self.namer.namespace_class(b) for b in cl.bases]
        if not clnames:
            clnames = ['pyobj']
            if '__iter__' in cl.funcs:  # XXX get return type of 'next'
                ts = typestr.nodetypestr(self.gx, cl.funcs['__iter__'].retnode.thing, mv=self.mv)
                if ts.startswith('__iter<'):
                    ts = ts[ts.find('<') + 1:ts.find('>')]
                    clnames = ['pyiter<%s>' % ts]  # XXX use iterable interface
            if '__call__' in cl.funcs:
                callfunc = cl.funcs['__call__']
                r_typestr = typestr.nodetypestr(self.gx, callfunc.retnode.thing, mv=self.mv).strip()
                nargs = len(callfunc.formals) - 1
                argtypes = [typestr.nodetypestr(self.gx, callfunc.vars[callfunc.formals[i + 1]], mv=self.mv).strip() for i in range(nargs)]
                clnames = ['pycall%d<%s,%s>' % (nargs, r_typestr, ','.join(argtypes))]
        self.output('class ' + self.cpp_name(cl) + ' : ' + ', '.join(['public ' + clname for clname in clnames]) + ' {')
        self.do_comment(ast.get_docstring(node))
        self.output('public:')
        self.indent()
        self.class_variables(cl)

        # --- constructor
        need_init = False
        if '__init__' in cl.funcs:
            initfunc = cl.funcs['__init__']
            if self.inhcpa(initfunc):
                need_init = True

        # --- default constructor
        if need_init:
            self.output(self.cpp_name(cl) + '() {}')
        else:
            self.output(self.cpp_name(cl) + '() { this->__class__ = cl_' + cl.ident + '; }')

        # --- init constructor
        if need_init:
            self.func_header(initfunc, declare=True, is_init=True)
            self.indent()
            self.output('this->__class__ = cl_' + cl.ident + ';')
            self.output('__init__(' + ', '.join(self.cpp_name(initfunc.vars[f]) for f in initfunc.formals[1:]) + ');')
            self.deindent()
            self.output('}')

        # --- destructor call
        if '__del__' in cl.funcs and self.inhcpa(cl.funcs['__del__']):
            self.output('~%s() { this->__del__(); }' % self.cpp_name(cl))

        # --- static code
        if cl.parent.static_nodes:
            self.output('static void __static__();')

        # --- methods
        virtual.virtuals(self, cl, True)
        for func in cl.funcs.values():
            if func.node and not (func.ident == '__init__' and func.inherited):
                self.visit_FunctionDef(func.node, cl, True)
        self.copy_methods(cl, True)
        if self.gx.extension_module:
            self.extmod.convert_methods(cl, True)

        self.deindent()
        self.output('};\n')

    def class_cpp(self, node):
        cl = self.mv.classes[node.name]
        if node in self.gx.comments:
            self.do_comments(node)
        else:
            self.output('/**\nclass %s\n*/\n' % cl.ident)
        self.output('class_ *cl_' + cl.ident + ';\n')

        # --- methods
        virtual.virtuals(self, cl, False)
        for func in cl.funcs.values():
            if func.node and not (func.ident == '__init__' and func.inherited):
                self.visit_FunctionDef(func.node, cl, False)
        self.copy_methods(cl, False)

        # --- class variable declarations
        if cl.parent.vars:  # XXX merge with visit_Module
            for var in cl.parent.vars.values():
                if var in self.gx.merged_inh and self.gx.merged_inh[var]:
                    self.start(typestr.nodetypestr(self.gx, var, cl.parent, mv=self.mv) + cl.ident + '::' + self.cpp_name(var))
                    self.eol()
            self.print()

        # --- static init
        if cl.parent.static_nodes:
            self.output('void %s::__static__() {' % self.cpp_name(cl))
            self.indent()
            for node in cl.parent.static_nodes:
                self.visit(node, cl.parent)
            self.deindent()
            self.output('}')
            self.print()

    def class_variables(self, cl):
        # --- class variables
        if cl.parent.vars:
            for var in cl.parent.vars.values():
                if var in self.gx.merged_inh and self.gx.merged_inh[var]:
                    self.output('static ' + typestr.nodetypestr(self.gx, var, cl.parent, mv=self.mv) + self.cpp_name(var) + ';')
            self.print()

        # --- instance variables
        for var in cl.vars.values():
            if var.invisible:
                continue  # var.name in cl.virtualvars: continue
            # var is masked by ancestor var
            vars = set()
            for ancestor in cl.ancestors():
                vars.update(ancestor.vars)
            if var.name in vars:
                continue
            if var in self.gx.merged_inh and self.gx.merged_inh[var]:
                self.output(typestr.nodetypestr(self.gx, var, cl, mv=self.mv) + self.cpp_name(var) + ';')

        if [v for v in cl.vars if not v.startswith('__')]:
            self.print()

    def nothing(self, types):
        if python.def_class(self.gx, 'complex') in (t[0] for t in types):
            return 'mcomplex(0.0, 0.0)'
        elif python.def_class(self.gx, 'bool_') in (t[0] for t in types):
            return 'False'
        else:
            return '0'

    def inhcpa(self, func):
        return infer.called(func) or (func in self.gx.inheritance_relations and [1 for f in self.gx.inheritance_relations[func] if infer.called(f)])

    def visit_Slice(self, node, func=None):
        assert False, "visit_Slice should never be called"
        if type(node.ctx) == ast.Del:
            self.start()
            self.visit(infer.inode(self.gx, node.expr).fakefunc, func)
            self.eol()
        else:
            self.visit(infer.inode(self.gx, node.expr).fakefunc, func)

    def visit_Lambda(self, node, parent=None):
        self.append(self.mv.lambdaname[node])

    def subtypes(self, types, varname):
        subtypes = set()
        for t in types:
            if isinstance(t[0], python.Class):
                var = t[0].vars.get(varname)
                if var and (var, t[1], 0) in self.gx.cnode:  # XXX yeah?
                    subtypes.update(self.gx.cnode[var, t[1], 0].types())
        return subtypes

    def bin_tuple(self, types):
        for t in types:
            if isinstance(t[0], python.Class) and t[0].ident == 'tuple2':
                var1 = t[0].vars.get('first')
                var2 = t[0].vars.get('second')
                if var1 and var2:
                    if (var1, t[1], 0) in self.gx.cnode and (var2, t[1], 0) in self.gx.cnode:
                        if self.gx.cnode[var1, t[1], 0].types() != self.gx.cnode[var2, t[1], 0].types():
                            return True
        return False

    def instance_new(self, node, argtypes):
        if argtypes is None:
            argtypes = self.gx.merged_inh[node]
        ts = typestr.typestr(self.gx, argtypes, mv=self.mv)
        if ts.startswith('pyseq') or ts.startswith('pyiter'):  # XXX
            argtypes = self.gx.merged_inh[node]
        ts = typestr.typestr(self.gx, argtypes, mv=self.mv)
        self.append('(new ' + ts[:-2] + '(')
        return argtypes

    def visit_Dict(self, node, func=None, argtypes=None):
        argtypes = self.instance_new(node, argtypes)
        if node.keys:
            self.append(str(len(node.keys)) + ', ')
        ts_key = typestr.typestr(self.gx, self.subtypes(argtypes, 'unit'), mv=self.mv)
        ts_value = typestr.typestr(self.gx, self.subtypes(argtypes, 'value'), mv=self.mv)
        items = list(zip(node.keys, node.values))
        for (key, value) in items:
            self.visitm('(new tuple2<%s, %s>(2,' % (ts_key, ts_value), func)
            type_child = self.subtypes(argtypes, 'unit')
            self.impl_visit_conv(key, type_child, func)
            self.append(',')
            type_child = self.subtypes(argtypes, 'value')
            self.impl_visit_conv(value, type_child, func)
            self.append('))')
            if (key, value) != items[-1]:
                self.append(',')
        self.append('))')

    def visit_tuple_list(self, node, func=None, argtypes=None):
        if isinstance(func, python.Class):  # XXX
            func = None
        argtypes = self.instance_new(node, argtypes)
        children = list(node.elts)
        if children:
            self.append(str(len(children)) + ',')
        if len(children) >= 2 and self.bin_tuple(argtypes):  # XXX >=2?
            type_child = self.subtypes(argtypes, 'first')
            self.impl_visit_conv(children[0], type_child, func)
            self.append(',')
            type_child = self.subtypes(argtypes, 'second')
            self.impl_visit_conv(children[1], type_child, func)
        else:
            for child in children:
                type_child = self.subtypes(argtypes, 'unit')
                self.impl_visit_conv(child, type_child, func)
                if child != children[-1]:
                    self.append(',')
        self.append('))')

    def visit_Tuple(self, node, func=None, argtypes=None):
        if type(node.ctx) == ast.Load:
            if len(node.elts) > 2:
                types = set()
                for child in node.elts:
                    types.update(self.mergeinh[child])
                typestr.typestr(self.gx, types, node=child, tuple_check=True, mv=self.mv)
            self.visit_tuple_list(node, func, argtypes)
        elif type(node.ctx) == ast.Store:
            assert False
        elif type(node.ctx) == ast.Del:
            assert False
        else:
            error.error("unknown ctx type for Tuple, " + type(node.ctx), self.gx, node, mv=self.mv)

    def visit_List(self, node, func=None, argtypes=None):
        if type(node.ctx) == ast.Load:
            self.visit_tuple_list(node, func, argtypes)
        elif type(node.ctx) == ast.Store:
            assert False
        elif type(node.ctx) == ast.Del:
            assert False
        else:
            error.error("unknown ctx type for ast.List, " + type(node.ctx), self.gx, node, mv=self.mv)

    def visit_Assert(self, node, func=None):
        self.start('ASSERT(')
        self.visitm(node.test, ', ', func)
        if node.msg:
            self.visit(node.msg, func)
        else:
            self.append('0')
        self.eol(')')

    def visit_Raise(self, node, func=None):
        if hasattr(node, 'exc'):
            exc = node.exc
        else: # py2
            exc = node.type

        cl = None  # XXX sep func
        t = [t[0] for t in self.mergeinh[exc]]
        if len(t) == 1:
            cl = t[0]
        self.start('throw (')

        # --- raise class [, constructor args]
        if isinstance(exc, ast.Name) and not python.lookup_var(exc.id, func, mv=self.mv):  # XXX python.lookup_class
            self.append('new %s(' % exc.id)
            if hasattr(node, 'inst') and node.inst: # XXX what was this for, seems untested also
                if isinstance(node.inst, ast.Tuple) and node.inst.elts:
                    for n in node.inst.elts:
                        self.visit(n, func)
                        if n != node.inst.elts[-1]:
                            self.append(', ')  # XXX visitcomma(nodes)
                else:
                    self.visit(node.inst, func)
            self.append(')')

        # --- raise instance
        elif isinstance(cl, python.Class) and cl.mv.module.ident == 'builtin' and not [a for a in cl.ancestors_upto(None) if a.ident == 'BaseException']:
            self.append('new Exception()')
        else:
            self.visit(exc, func)
        self.eol(')')

    def visit_Try(self, node, func=None): # py3
        self.visit_TryExcept(node, func)

    def visit_TryExcept(self, node, func=None):
        # try
        self.start('try {')
        self.print(self.line)
        self.indent()
        if node.orelse:
            self.output('%s = 0;' % self.mv.tempcount[ast_utils.orelse_to_node(node)])
        for child in node.body:
            self.visit(child, func)
        if node.orelse:
            self.output('%s = 1;' % self.mv.tempcount[ast_utils.orelse_to_node(node)])
        self.deindent()
        self.start('}')

        # except
        for handler in node.handlers:
            if isinstance(handler.type, ast.Tuple):
                pairs = [(n, handler.name, handler.body) for n in handler.type.elts]
            else:
                pairs = [(handler.type, handler.name, handler.body)]

            for (h0, h1, h2) in pairs:
                if isinstance(h0, ast.Name) and h0.id in ['int', 'float', 'str', 'class']:
                    continue  # XXX python.lookup_class
                elif h0:
                    cl = python.lookup_class(h0, self.mv)
                    if cl.mv.module.builtin and cl.ident in ['KeyboardInterrupt', 'FloatingPointError', 'OverflowError', 'ZeroDivisionError', 'SystemExit']:
                        error.error("system '%s' is not caught" % cl.ident, self.gx, h0, warning=True, mv=self.mv)
                    arg = self.namer.namespace_class(cl) + ' *'
                else:
                    arg = 'Exception *'

                if isinstance(h1, str):
                    arg += h1
                elif isinstance(h1, ast.Name): # py2
                    arg += h1.id

                self.append(' catch (%s) {' % arg)
                self.print(self.line)
                self.indent()
                for child in h2:
                    self.visit(child, func)
                self.deindent()
                self.start('}')
        self.print(self.line)

        # else
        if node.orelse:
            self.output('if(%s) { // else' % self.mv.tempcount[ast_utils.orelse_to_node(node)])
            self.indent()
            for child in node.orelse:
                self.visit(child, func)
            self.deindent()
            self.output('}')

    def do_fastfor(self, node, qual, quals, iter, func, genexpr):
        if len(qual.iter.args) == 3 and not python.is_literal(qual.iter.args[2]):
            for arg in qual.iter.args:  # XXX simplify
                if arg in self.mv.tempcount:
                    self.start()
                    self.visitm(self.mv.tempcount[arg], ' = ', arg, func)
                    self.eol()
        self.fastfor(qual, iter, func)
        self.forbody(node, quals, iter, func, False, genexpr)

    def impl_visit_temp(self, node, func):  # XXX generalize?
        if node in self.mv.tempcount:
            self.append(self.mv.tempcount[node])
        else:
            self.visit(node, func)

    def fastfor(self, node, assname, func=None):
        # --- for i in range(..) -> for( i=l, u=expr; i < u; i++ ) ..
        ivar, evar = self.mv.tempcount[node.target], self.mv.tempcount[node.iter]
        self.start('FAST_FOR(%s,' % assname)

        if len(node.iter.args) == 1:
            self.append('0,')
            self.impl_visit_temp(node.iter.args[0], func)
            self.append(',')
        else:
            self.impl_visit_temp(node.iter.args[0], func)
            self.append(',')
            self.impl_visit_temp(node.iter.args[1], func)
            self.append(',')

        if len(node.iter.args) != 3:
            self.append('1')
        else:
            self.impl_visit_temp(node.iter.args[2], func)
        self.append(',%s,%s)' % (ivar[2:], evar[2:]))
        self.print(self.line)

    def fastenum(self, node):
        return python.is_enum(node) and self.only_classes(node.iter.args[0], ('tuple', 'list', 'str_'))

    def fastzip2(self, node):
        names = ('tuple', 'list')
        return python.is_zip2(node) and self.only_classes(node.iter.args[0], names) and self.only_classes(node.iter.args[1], names)

    def fastdictiter(self, node):
        return isinstance(node.iter, ast.Call) and ast_utils.is_assign_list_or_tuple(node.target) and self.only_classes(node.iter.func, ('dict',)) and isinstance(node.iter.func, ast.Attribute) and node.iter.func.attr == 'iteritems'

    def only_classes(self, node, names):
        if node not in self.mergeinh:
            return False
        classes = [python.def_class(self.gx, name, mv=self.mv) for name in names] + [python.def_class(self.gx, 'none')]
        return not [t for t in self.mergeinh[node] if t[0] not in classes]

    def visit_For(self, node, func=None):
        if isinstance(node.target, ast.Name):
            assname = node.target.id
        elif ast_utils.is_assign_attribute(node.target):
            self.start('')
            self.visit_Attribute(node.target, func)
            assname = self.line.strip()  # XXX yuck
        else:
            assname = self.mv.tempcount[node.target]
        assname = self.cpp_name(assname)
        self.print()
        if node.orelse:
            self.output('%s = 0;' % self.mv.tempcount[ast_utils.orelse_to_node(node)])
        if python.is_fastfor(node):
            self.do_fastfor(node, node, None, assname, func, False)
        elif self.fastenum(node):
            self.do_fastenum(node, func, False)
            self.forbody(node, None, assname, func, True, False)
        elif self.fastzip2(node):
            self.do_fastzip2(node, func, False)
            self.forbody(node, None, assname, func, True, False)
        elif self.fastdictiter(node):
            self.do_fastdictiter(node, func, False)
            self.forbody(node, None, assname, func, True, False)
        else:
            pref, tail = self.forin_preftail(node)
            self.start('FOR_IN%s(%s,' % (pref, assname))
            self.visit(node.iter, func)
            self.print(self.line + ',' + tail + ')')
            self.forbody(node, None, assname, func, False, False)
        self.print()

    def do_fastzip2(self, node, func, genexpr):
        self.start('FOR_IN_ZIP(')
        left, right = node.target.elts
        self.do_fastzip2_one(left, func)
        self.do_fastzip2_one(right, func)
        self.visitm(node.iter.args[0], ',', node.iter.args[1], ',', func)
        tail1 = self.mv.tempcount[(node, 2)][2:] + ',' + self.mv.tempcount[(node, 3)][2:] + ','
        tail2 = self.mv.tempcount[(node.iter)][2:] + ',' + self.mv.tempcount[(node, 4)][2:]
        self.print(self.line + tail1 + tail2 + ')')
        self.indent()
        if ast_utils.is_assign_list_or_tuple(left):
            self.tuple_assign(left, self.mv.tempcount[left], func)
        if ast_utils.is_assign_list_or_tuple(right):
            self.tuple_assign(right, self.mv.tempcount[right], func)

    def do_fastzip2_one(self, node, func):
        if ast_utils.is_assign_list_or_tuple(node):
            self.append(self.mv.tempcount[node])
        else:
            self.visit(node, func)
        self.append(',')

    def do_fastenum(self, node, func, genexpr):
        if self.only_classes(node.iter.args[0], ('tuple', 'list')):
            self.start('FOR_IN_ENUM(')
        else:
            self.start('FOR_IN_ENUM_STR(')
        left, right = node.target.elts
        self.do_fastzip2_one(right, func)
        self.visit(node.iter.args[0], func)
        tail = self.mv.tempcount[(node, 2)][2:] + ',' + self.mv.tempcount[node.iter][2:]
        self.print(self.line + ',' + tail + ')')
        self.indent()
        self.start()
        self.visitm(left, ' = ' + self.mv.tempcount[node.iter], func)
        self.eol()
        if ast_utils.is_assign_list_or_tuple(right):
            self.tuple_assign(right, self.mv.tempcount[right], func)

    def do_fastdictiter(self, node, func, genexpr):
        self.start('FOR_IN_DICT(')
        left, right = node.target.elts
        tail = self.mv.tempcount[node, 7][2:] + ',' + self.mv.tempcount[node, 6][2:] + ',' + self.mv.tempcount[node.iter][2:]
        self.visit(node.iter.func.value, func)
        self.print(self.line + ',' + tail + ')')
        self.indent()
        self.start()
        if left in self.mv.tempcount:  # XXX not for zip, enum..?
            self.visitm('%s = %s->key' % (self.mv.tempcount[left], self.mv.tempcount[node, 6]), func)
        else:
            self.visitm(left, ' = %s->key' % self.mv.tempcount[node, 6], func)
        self.eol()
        self.start()
        if right in self.mv.tempcount:
            self.visitm('%s = %s->value' % (self.mv.tempcount[right], self.mv.tempcount[node, 6]), func)
        else:
            self.visitm(right, ' = %s->value' % self.mv.tempcount[node, 6], func)
        self.eol()
        if ast_utils.is_assign_list_or_tuple(left):
            self.tuple_assign(left, self.mv.tempcount[left], func)
        if ast_utils.is_assign_list_or_tuple(right):
            self.tuple_assign(right, self.mv.tempcount[right], func)

    def forin_preftail(self, node):
        tail = self.mv.tempcount[node][2:] + ',' + self.mv.tempcount[node.iter][2:]
        tail += ',' + self.mv.tempcount[(node, 5)][2:]
        return '', tail

    def forbody(self, node, quals, iter, func, skip, genexpr):
        if quals is not None:
            self.listcompfor_body(node, quals, iter, func, False, genexpr)
            return
        if not skip:
            self.indent()
            if ast_utils.is_assign_list_or_tuple(node.target):
                self.tuple_assign(node.target, self.mv.tempcount[node.target], func)
        self.gx.loopstack.append(node)
        for child in node.body:
            self.visit(child, func)
        self.gx.loopstack.pop()
        self.deindent()
        self.output('END_FOR')
        if node.orelse:
            self.output('if (!%s) {' % self.mv.tempcount[ast_utils.orelse_to_node(node)])
            self.indent()
            for child in node.orelse:
                self.visit(child, func)
            self.deindent()
            self.output('}')

    def func_pointers(self):
        for func in self.mv.lambdas.values():
            argtypes = [typestr.nodetypestr(self.gx, func.vars[formal], func, mv=self.mv).rstrip() for formal in func.formals]
            if func.largs is not None:
                argtypes = argtypes[:func.largs]
            rettype = typestr.nodetypestr(self.gx, func.retnode.thing, func, mv=self.mv)
            self.print('typedef %s(*lambda%d)(' % (rettype, func.lambdanr) + ', '.join(argtypes) + ');')
        self.print()

    # --- function/method header
    def func_header(self, func, declare, is_init=False):
        method = isinstance(func.parent, python.Class)
        if method:
            formals = [f for f in func.formals if f != 'self']
        else:
            formals = [f for f in func.formals]
        if func.largs is not None:
            formals = formals[:func.largs]

        if is_init:
            ident = self.cpp_name(func.parent)
        else:
            ident = self.cpp_name(func)

        self.start()

        # --- return expression
        header = ''
        if is_init:
            pass
        elif func.ident in ['__hash__']:
            header += 'long '  # XXX __ss_int leads to problem with virtual parent
        elif func.returnexpr:
            header += typestr.nodetypestr(self.gx, func.retnode.thing, func, mv=self.mv)  # XXX mult
        else:
            header += 'void '

        ftypes = [typestr.nodetypestr(self.gx, func.vars[f], func, mv=self.mv) for f in formals]

        # if arguments type too precise (e.g. virtually called) cast them back
        oldftypes = ftypes
        if func.ftypes:
            ftypes = func.ftypes[1:]

        # --- method header
        if method and not declare:
            header += self.cpp_name(func.parent) + '::'
        header += ident

        # --- cast arguments if necessary (explained above)
        casts = []
        casters = set()
        if func.ftypes:
            for i in range(min(len(oldftypes), len(ftypes))):  # XXX this is 'cast on specialize'.. how about generalization?
                if oldftypes[i] != ftypes[i]:
                    casts.append(oldftypes[i] + formals[i] + ' = (' + oldftypes[i] + ')__' + formals[i] + ';')
                    if not declare:
                        casters.add(i)

        formals2 = formals[:]
        for (i, f) in enumerate(formals2):  # XXX
            formals2[i] = self.cpp_name(func.vars[f])
            if i in casters:
                formals2[i] = '__' + formals2[i]
        formaldecs = [o + f for (o, f) in zip(ftypes, formals2)]
        if declare and isinstance(func.parent, python.Class) and func.ident in func.parent.staticmethods:
            header = 'static ' + header
        if is_init and not formaldecs:
            formaldecs = ['int __ss_init']
        if func.ident.startswith('__lambda'):  # XXX
            header = 'static inline ' + header

        # --- output
        self.append(header + '(' + ', '.join(formaldecs) + ')')
        if is_init:
            self.print(self.line + ' {')
        elif declare:
            self.eol()
        else:
            self.print(self.line + ' {')
            self.indent()
            if not declare and func.doc:
                self.do_comment(func.doc)
            for cast in casts:
                self.output(cast)
            self.deindent()

    def visit_FunctionDef(self, node, parent=None, declare=False):
        # locate right func instance
        if parent and isinstance(parent, python.Class):
            func = parent.funcs[node.name]
        elif node.name in self.mv.funcs:
            func = self.mv.funcs[node.name]
        else:
            func = self.mv.lambdas[node.name]
        if func.invisible or (func.inherited and not func.ident == '__init__'):
            return
        if declare and func.declared:  # XXX
            return

        # check whether function is called at all (possibly via inheritance)
        if not self.inhcpa(func):
            if func.ident in ['__iadd__', '__isub__', '__imul__']:
                return
            if func.lambdanr is None and not ast.dump(node.body[0]).startswith("Raise(type=Call(func=Name(id='NotImplementedError'"):
                error.error(repr(func) + ' not called!', self.gx, node, warning=True, mv=self.mv)
            if not (declare and func.parent and func.ident in func.parent.virtuals):
                return

        if func.isGenerator and not declare:
            self.generator_class(func)

        self.func_header(func, declare)
        if declare:
            return
        self.indent()

        if func.isGenerator:
            self.generator_body(func)
            return

        # --- local declarations
        self.local_defs(func)

        # --- function body
        for fake_unpack in func.expand_args.values():
            self.visit(fake_unpack, func)
        for child in node.body:
            self.visit(child, func)
        if func.fakeret:
            self.visit(func.fakeret, func)

        # --- add Return(None) (sort of) if function doesn't already end with a Return
        if node.body:
            lastnode = node.body[-1]
            if not func.ident == '__init__' and not func.fakeret and not isinstance(lastnode, ast.Return):
                self.output('return %s;' % self.nothing(self.mergeinh[func.retnode.thing]))

        self.deindent()
        self.output('}\n')

    def generator_ident(self, func):  # XXX merge?
        if func.parent:
            return func.parent.ident + '_' + func.ident
        return func.ident

    def generator_class(self, func):
        ident = self.generator_ident(func)
        self.output('class __gen_%s : public %s {' % (ident, typestr.nodetypestr(self.gx, func.retnode.thing, func, mv=self.mv)[:-2]))
        self.output('public:')
        self.indent()
        pairs = [(typestr.nodetypestr(self.gx, func.vars[f], func, mv=self.mv), self.cpp_name(func.vars[f])) for f in func.vars]
        self.output(self.indentation.join(self.group_declarations(pairs)))
        self.output('int __last_yield;\n')

        args = []
        for f in func.formals:
            args.append(typestr.nodetypestr(self.gx, func.vars[f], func, mv=self.mv) + self.cpp_name(func.vars[f]))
        self.output(('__gen_%s(' % ident) + ','.join(args) + ') {')
        self.indent()
        for f in func.formals:
            self.output('this->%s = %s;' % (self.cpp_name(func.vars[f]), self.cpp_name(func.vars[f])))
        for fake_unpack in func.expand_args.values():
            self.visit(fake_unpack, func)
        self.output('__last_yield = -1;')
        self.deindent()
        self.output('}\n')

        func2 = typestr.nodetypestr(self.gx, func.retnode.thing, func, mv=self.mv)[7:-3]
        self.output('%s __get_next() {' % func2)
        self.indent()
        self.output('switch(__last_yield) {')
        self.indent()
        for (i, n) in enumerate(func.yieldNodes):
            self.output('case %d: goto __after_yield_%d;' % (i, i))
        self.output('default: break;')
        self.deindent()
        self.output('}')

        for child in func.node.body:
            self.visit(child, func)

        self.output('__stop_iteration = true;')
        self.output('return __zero<%s>();' % func2)
        self.deindent()
        self.output('}\n')

        self.deindent()
        self.output('};\n')

    def generator_body(self, func):
        ident = self.generator_ident(func)
        if not (func.isGenerator and func.parent):
            formals = [self.cpp_name(func.vars[f]) for f in func.formals]
        else:
            formals = ['this'] + [self.cpp_name(func.vars[f]) for f in func.formals if f != 'self']
        self.output('return new __gen_%s(%s);\n' % (ident, ','.join(formals)))
        self.deindent()
        self.output('}\n')

    def visit_Yield(self, node, func):
        self.output('__last_yield = %d;' % func.yieldNodes.index(node))
        self.start('__result = ')
        self.impl_visit_conv(node.value, self.mergeinh[func.yieldnode.thing], func)
        self.eol()
        self.output('return __result;')
        self.output('__after_yield_%d:;' % func.yieldNodes.index(node))
        self.start()

    def visit_Global(self, node, func=None):
        pass

    def visit_Repr(self, node, func=None):
        self.visitm('repr(', infer.inode(self.gx, node.value).fakefunc.func.value, ')', func)

    def visit_If(self, node, func=None):
        self.start()
        self.append('if (')
        self.bool_test(node.test, func)
        self.print(self.line + ') {')
        self.indent()
        for child in node.body:
            self.visit(child, func)
        self.deindent()
        self.output('}')

        if node.orelse:
            self.output('else {')
            self.indent()
            for child in node.orelse:
                self.visit(child, func)
            self.deindent()
            self.output('}')

    def visit_IfExp(self, node, func=None):
        types = self.mergeinh[node]
        self.append('((')
        self.bool_test(node.test, func)
        self.append(')?(')
        self.impl_visit_conv(node.body, types, func)
        self.append('):(')
        self.impl_visit_conv(node.orelse, types, func)
        self.append('))')

    def impl_visit_conv(self, node, argtypes, func, check_temp=True):
        # convert/cast node to type it is assigned to
        actualtypes = self.mergeinh[node]
        if check_temp and node in self.mv.tempcount:  # XXX
            self.append(self.mv.tempcount[node])
        elif isinstance(node, ast.Dict):
            self.visit_Dict(node, func, argtypes=argtypes)
        elif isinstance(node, ast.Tuple):
            self.visit_Tuple(node, func, argtypes=argtypes)
        elif isinstance(node, ast.List):
            self.visit_List(node, func, argtypes=argtypes)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ('list', 'tuple', 'dict', 'set'):
            self.visit_Call(node, func, argtypes=argtypes)
        elif ast_utils.is_none(node):
            self.visit(node, func)
        else:  # XXX messy
            cast = ''
            if actualtypes and argtypes and typestr.typestr(self.gx, actualtypes, mv=self.mv) != typestr.typestr(self.gx, argtypes, mv=self.mv) and typestr.typestr(self.gx, actualtypes, mv=self.mv) not in ('str *', 'bytes *'):  # XXX
                if typestr.incompatible_assignment_rec(self.gx, actualtypes, argtypes):
                    error.error("incompatible types", self.gx, node, warning=True, mv=self.mv)
                else:
                    cast = '(' + typestr.typestr(self.gx, argtypes, mv=self.mv).strip() + ')'
                    if cast == '(complex)':
                        cast = 'mcomplex'
            if cast:
                self.append('(' + cast + '(')
            self.visit(node, func)
            if cast:
                self.append('))')

    def visit_Break(self, node, func=None):
        if self.gx.loopstack[-1].orelse:
            orelse_tempcount_id = ast_utils.orelse_to_node(self.gx.loopstack[-1])
            if orelse_tempcount_id in self.mv.tempcount:
                self.output('%s = 1;' % self.mv.tempcount[orelse_tempcount_id])
        self.output('break;')

    def visit_BoolOp(self, node, func=None):
        if type(node.op) == ast.Or:
            self.impl_visit_and_or(node, node.values, '__OR', 'or', func)
        elif type(node.op) == ast.And:
            self.impl_visit_and_or(node, node.values, '__AND', 'and', func)

    def impl_visit_and_or(self, node, nodes, op, mix, func=None):
        if node in self.gx.bool_test_only:
            self.append('(')
            for n in nodes:
                self.bool_test(n, func)
                if n != node.values[-1]:
                    self.append(' ' + mix + ' ')
            self.append(')')
        else:
            child = nodes[0]
            if len(nodes) > 1:
                self.append(op + '(')
            self.impl_visit_conv(child, self.mergeinh[node], func, check_temp=False)
            if len(nodes) > 1:
                self.append(', ')
                self.impl_visit_and_or(node, nodes[1:], op, mix, func)
                self.append(', ' + self.mv.tempcount[child][2:] + ')')

    def visit_Compare(self, node, func=None, wrapper=True):
        if not node in self.bool_wrapper:
            self.append('___bool(')
        self.done = set()
        mapping = {
            ast.Gt: ('__gt__', '>', None),
            ast.Lt: ('__lt__', '<', None),
            ast.NotEq: ('__ne__', '!=', None),
            ast.Eq: ('__eq__', '==', None),
            ast.LtE: ('__le__', '<=', None),
            ast.GtE: ('__ge__', '>=', None),
            ast.Is: (None, '==', None),
            ast.IsNot: (None, '!=', None),
            ast.In: ('__contains__', None, None),
            ast.NotIn: ('__contains__', None, '!'),
        }
        left = node.left
        for op, right in zip(node.ops, node.comparators):
            msg, short, pre = mapping[type(op)]
            if msg == '__contains__':
                self.do_compare(right, left, msg, short, func, pre)
            else:
                self.do_compare(left, right, msg, short, func, pre)
            if right != node.comparators[-1]:
                self.append('&&')
            left = right
        if not node in self.bool_wrapper:
            self.append(')')

    def visit_AugAssign(self, node, func=None):
        if isinstance(node.target, ast.Subscript):
            self.start()
            if set([t[0].ident for t in self.mergeinh[node.target.value] if isinstance(t[0], python.Class)]) in [set(['dict']), set(['defaultdict'])] and type(node.op) == ast.Add:
                self.visitm(node.target.value, '->__addtoitem__(', infer.inode(self.gx, node).subs, ', ', node.value, ')', func)
                self.eol()
                return

            self.visitm(infer.inode(self.gx, node).temp1 + ' = ', node.target.value, func)
            self.eol()
            self.start()
            self.visitm(infer.inode(self.gx, node).temp2 + ' = ', infer.inode(self.gx, node).subs, func)
            self.eol()
        self.visit(infer.inode(self.gx, node).assignhop, func)

    def visit_BinOp(self, node, func=None):
        if type(node.op) == ast.Add:
            str_nodes = self.rec_string_addition(node)
            if str_nodes and len(str_nodes) > 2:
                self.append('__add_strs(%d, ' % len(str_nodes))
                for (i, node) in enumerate(str_nodes):
                    self.visit(node, func)
                    if i < len(str_nodes) - 1:
                        self.append(', ')
                self.append(')')
            else:
                self.impl_visit_binary(node.left, node.right, python.aug_msg(node, 'add'), '+', func)
        elif type(node.op) == ast.Sub:
            self.impl_visit_binary(node.left, node.right, python.aug_msg(node, 'sub'), '-', func)
        elif type(node.op) == ast.Mult:
            self.impl_visit_binary(node.left, node.right, python.aug_msg(node, 'mul'), '*', func)
        elif type(node.op) == ast.Div:
            self.impl_visit_binary(node.left, node.right, python.aug_msg(node, 'truediv'), '/', func)
        elif type(node.op) == ast.FloorDiv:
            self.impl_visit_binary(node.left, node.right, python.aug_msg(node, 'floordiv'), '//', func)
        elif type(node.op) == ast.Pow:
            self.power(node.left, node.right, None, func)
        elif type(node.op) == ast.Mod:
            self.impl_visit_Mod(node, func)
        elif type(node.op) == ast.LShift:
            self.impl_visit_binary(node.left, node.right, python.aug_msg(node, 'lshift'), '<<', func)
        elif type(node.op) == ast.RShift:
            self.impl_visit_binary(node.left, node.right, python.aug_msg(node, 'rshift'), '>>', func)
        elif type(node.op) == ast.BitOr:
            self.impl_visit_bitop(node, python.aug_msg(node, 'or'), '|', func)
        elif type(node.op) == ast.BitXor:
            self.impl_visit_bitop(node, python.aug_msg(node, 'xor'), '^', func)
        elif type(node.op) == ast.BitAnd:
            self.impl_visit_bitop(node, python.aug_msg(node, 'and'), '&', func)
        # PY3: elif type(node.op) == MatMult:
        else:
            error.error("Unknown op type for ast.BinOp: %s" % type(node.op), self.gx, node, mv=getmv())

    def rec_string_addition(self, node):
        if isinstance(node, ast.BinOp) and type(node.op) == ast.Add:
            l, r = self.rec_string_addition(node.left), self.rec_string_addition(node.right)
            if l and r:
                return l + r
        elif self.mergeinh[node] == set([(python.def_class(self.gx, 'str_'), 0)]):
            return [node]

    def impl_visit_bitop(self, node, msg, inline, func=None):
        ltypes = self.mergeinh[node.left]
        ul = typestr.unboxable(self.gx, ltypes)
        self.append('(')
        self.append('(')
        self.visit(node.left, func)
        self.append(')')
        if ul:
            self.append(inline)
        else:
            self.append('->' + msg)
        self.append('(')
        self.visit(node.right, func)
        self.append(')')
        self.append(')')

    def power(self, left, right, mod, func=None):
        inttype = set([(python.def_class(self.gx, 'int_'), 0)])  # XXX merge
        if self.mergeinh[left] == inttype and self.mergeinh[right] == inttype:
            if not isinstance(right, ast.Num) or right.n < 0:
                error.error("pow(int, int) returns int after compilation", self.gx, left, warning=True, mv=self.mv)
        if mod:
            self.visitm('__power(', left, ', ', right, ', ', mod, ')', func)
        else:
            self.visitm('__power(', left, ', ', right, ')', func)

    def impl_visit_binary(self, left, right, middle, inline, func=None):  # XXX cleanup please
        ltypes = self.mergeinh[left]
        rtypes = self.mergeinh[right]
        ul, ur = typestr.unboxable(self.gx, ltypes), typestr.unboxable(self.gx, rtypes)

        inttype = set([(python.def_class(self.gx, 'int_'), 0)])  # XXX new type?
        floattype = set([(python.def_class(self.gx, 'float_'), 0)])  # XXX new type?

        # --- inline mod/div
        # XXX C++ knows %, /, so we can overload?
        if (floattype.intersection(ltypes) or inttype.intersection(ltypes)):
            if inline in ['%'] or (inline in ['/'] and not (floattype.intersection(ltypes) or floattype.intersection(rtypes))):
                if not python.def_class(self.gx, 'complex') in (t[0] for t in rtypes):  # XXX
                    self.append({'%': '__mods', '/': '__divs'}[inline] + '(')
                    self.visit(left, func)
                    self.append(', ')
                    self.visit(right, func)
                    self.append(')')
                    return

        # --- inline floordiv
        if (inline and ul and ur) and inline in ['//']:
            self.append({'//': '__floordiv'}[inline] + '(')
            self.visit(left, func)
            self.append(',')
            self.visit(right, func)
            self.append(')')
            return

        # --- beauty fix for '1 +- nj' notation
        if inline in ['+', '-'] and isinstance(right, ast.Num) and isinstance(right.n, complex):
            if floattype.intersection(ltypes) or inttype.intersection(ltypes):
                self.append('mcomplex(')
                self.visit(left, func)
                self.append(', ' + {'+': '', '-': '-'}[inline] + str(right.n.imag) + ')')
                return

        # --- inline other
        if inline and ((ul and ur) or not middle or ast_utils.is_none(left) or ast_utils.is_none(right)):  # XXX not middle, cleanup?
            self.append('(')
            self.visit(left, func)
            self.append(inline)
            self.visit(right, func)
            self.append(')')
            return

        # --- 'a.__mul__(b)': use template to call to b.__mul__(a), while maintaining evaluation order
        if inline in ['+', '*', '-', '/'] and ul and not ur:
            self.append('__' + {'+': 'add', '*': 'mul', '-': 'sub', '/': 'div'}[inline] + '2(')
            self.visit(left, func)
            self.append(', ')
            self.visit(right, func)
            self.append(')')
            return

        # --- default: left, connector, middle, right
        argtypes = ltypes | rtypes
        self.append('(')
        if middle == '__add__':
            self.impl_visit_conv(left, argtypes, func)
        else:
            self.visit(left, func)
        self.append(')')
        self.append(self.connector(left, func) + middle + '(')
        if middle == '__add__':
            self.impl_visit_conv(right, argtypes, func)
        else:
            self.visit(right, func)
        self.append(')')

    def do_compare(self, left, right, middle, inline, func=None, prefix=''):
        ltypes = self.mergeinh[left]
        rtypes = self.mergeinh[right]
        argtypes = ltypes | rtypes
        ul, ur = typestr.unboxable(self.gx, ltypes), typestr.unboxable(self.gx, rtypes)

        # name (not) in (expr, expr, ..)
        if middle == '__contains__' and isinstance(left, ast.Tuple) and isinstance(right, ast.Name):
            self.append('(')
            for i, elem in enumerate(left.elts):
                if prefix == '!':
                    self.append('!__eq(')  # XXX why does using __ne( fail test 199!?
                else:
                    self.append('__eq(')
                self.visit(right, func)
                self.append(',')
                self.visit(elem, func)
                self.append(')')
                if i != len(left.elts)-1:
                    if prefix == '!':
                        self.append(' && ')
                    else:
                        self.append(' | ')
            self.append(')')
            return

        # --- inline other
        if inline and ((ul and ur) or not middle or ast_utils.is_none(left) or ast_utils.is_none(right)):  # XXX not middle, cleanup?
            self.append('(')
            self.visit2(left, argtypes, middle, func)
            self.append(inline)
            self.visit2(right, argtypes, middle, func)
            self.append(')')
            return

        # --- prefix '!'
        postfix = ''
        if prefix:
            self.append('(' + prefix)
            postfix = ')'

        # --- comparison
        if middle in ['__eq__', '__ne__', '__gt__', '__ge__', '__lt__', '__le__']:
            self.append(middle[:-2] + '(')
            self.visit2(left, argtypes, middle, func)
            self.append(', ')
            self.visit2(right, argtypes, middle, func)
            self.append(')' + postfix)
            return

        # --- default: left, connector, middle, right
        self.append('(')
        self.visit2(left, argtypes, middle, func)
        self.append(')')
        if middle == '==':
            self.append('==(')
        else:
            self.append(self.connector(left, func) + middle + '(')
        self.visit2(right, argtypes, middle, func)
        self.append(')' + postfix)

    def visit2(self, node, argtypes, middle, func):  # XXX use temp vars in comparisons, e.g. (t1=fun())
        if node in self.mv.tempcount:
            if node in self.done:
                self.append(self.mv.tempcount[node])
            else:
                self.visitm('(' + self.mv.tempcount[node] + '=', node, ')', func)
                self.done.add(node)
        elif middle == '__contains__':
            self.visit(node, func)
        else:
            self.impl_visit_conv(node, argtypes, func)

    def visit_UnaryOp(self, node, func=None):
        if type(node.op) == ast.USub:
            self.visitm('(', func)
            if typestr.unboxable(self.gx, self.mergeinh[node.operand]):
                self.visitm('-', node.operand, func)
            else:
                self.visit_Call(infer.inode(self.gx, node.operand).fakefunc, func)
            self.visitm(')', func)
        elif type(node.op) == ast.UAdd:
            self.visitm('(', func)
            if typestr.unboxable(self.gx, self.mergeinh[node.operand]):
                self.visitm('+', node.operand, func)
            else:
                self.visit_Call(infer.inode(self.gx, node.operand).fakefunc, func)
            self.visitm(')', func)
        elif type(node.op) == ast.Invert:
            if typestr.unboxable(self.gx, self.mergeinh[node.operand]):
                self.visitm('~', node.operand, func)
            else:
                self.visit_Call(infer.inode(self.gx, node.operand).fakefunc, func)
        elif type(node.op) == ast.Not:
            self.append('__NOT(')
            self.bool_test(node.operand, func)
            self.append(')')
        else:
            error.error("Unknown op type for UnaryOp: %s" % type(node.op), self.gx, node, mv=getmv())

    def library_func(self, funcs, modname, clname, funcname):
        for func in funcs:
            if not func.mv.module.builtin or func.mv.module.ident != modname:
                continue
            if clname is not None:
                if not func.parent or func.parent.ident != clname:
                    continue
            return func.ident == funcname

    def add_args_arg(self, node, funcs):
        ''' append argument that describes which formals are actually filled in '''
        if self.library_func(funcs, 'datetime', 'time', 'replace') or \
                self.library_func(funcs, 'datetime', 'datetime', 'replace'):
            formals = funcs[0].formals[1:]  # skip self
            formal_pos = dict((v, k) for k, v in enumerate(formals))
            positions = []

            for i, arg in enumerate(node.args):
                if isinstance(arg, ast.keyword):
                    positions.append(formal_pos[arg.name])
                else:
                    positions.append(i)

            if positions:
                self.append(str(reduce(lambda a, b: a | b, ((1 << x) for x in positions))) + ', ')
            else:
                self.append('0, ')

    def visit_Pass(self, node, func=None):
        pass

    def visit_Call(self, node, func=None, argtypes=None):
        objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = infer.analyze_callfunc(self.gx, node, merge=self.gx.merged_inh)
        funcs = infer.callfunc_targets(self.gx, node, self.gx.merged_inh)

        if self.library_func(funcs, 're', None, 'findall') or \
                self.library_func(funcs, 're', 're_object', 'findall'):
            error.error("'findall' does not work with groups (use 'finditer' instead)", self.gx, node, warning=True, mv=self.mv)
        if self.library_func(funcs, 'socket', 'socket', 'settimeout') or \
                self.library_func(funcs, 'socket', 'socket', 'gettimeout'):
            error.error("socket.set/gettimeout do not accept/return None", self.gx, node, warning=True, mv=self.mv)
        if self.library_func(funcs, 'builtin', None, 'map') and len(node.args) > 2:
            error.error("default fillvalue for 'map' becomes 0 for integers", self.gx, node, warning=True, mv=self.mv)
        if self.library_func(funcs, 'itertools', None, 'izip_longest'):
            error.error("default fillvalue for 'izip_longest' becomes 0 for integers", self.gx, node, warning=True, mv=self.mv)
        if self.library_func(funcs, 'struct', None, 'unpack'):
            error.error("struct.unpack should be used as follows: 'a, .. = struct.unpack(..)'", self.gx, node, warning=True, mv=self.mv)
        if self.library_func(funcs, 'array', 'array', '__init__'):
            if not node.args or not isinstance(node.args[0], ast.Str) or node.args[0].s not in 'cbBhHiIlLfd':
                error.error("non-constant or unsupported type code", self.gx, node, warning=True, mv=self.mv)
        if self.library_func(funcs, 'builtin', None, 'id'):
            if struct.calcsize("P") == 8 and struct.calcsize('i') == 4 and not self.gx.longlong:
                error.error("return value of 'id' does not fit in 32-bit integer (try shedskin -l)", self.gx, node, warning=True, mv=self.mv)

        nrargs = len(node.args)
        if isinstance(func, python.Function) and func.largs:
            nrargs = func.largs

        # --- target expression
        if isinstance(node.func, ast.Attribute):
            node.func.called = True

        if node.func in self.mergeinh and [t for t in self.mergeinh[node.func] if isinstance(t[0], python.Function)]:  # anonymous function
            self.visitm(node.func, '(', func)

        elif constructor:
            ts = self.namer.nokeywords(typestr.nodetypestr(self.gx, node, func, mv=self.mv))
            if ts == 'complex ':
                self.append('mcomplex(')
                constructor = False  # XXX
            else:
                if argtypes is not None:  # XXX merge instance_new
                    ts = typestr.typestr(self.gx, argtypes, mv=self.mv)
                    if ts.startswith('pyseq') or ts.startswith('pyiter'):  # XXX
                        argtypes = self.gx.merged_inh[node]
                        ts = typestr.typestr(self.gx, argtypes, mv=self.mv)
                self.append('(new ' + ts[:-2] + '(')
            if funcs and len(funcs[0].formals) == 1 and not funcs[0].mv.module.builtin:
                self.append('1')  # don't call default constructor

        elif parent_constr:
            cl = python.lookup_class(node.func.value, self.mv)
            self.append(self.namer.namespace_class(cl) + '::' + node.func.attr + '(')

        elif direct_call:  # XXX no namespace (e.g., math.pow), check nr of args
            if ident == 'float' and node.args and self.mergeinh[node.args[0]] == set([(python.def_class(self.gx, 'float_'), 0)]):
                self.visit(node.args[0], func)
                return
            if ident in ['abs', 'int', 'float', 'str', 'bytes', 'bytearray', 'dict', 'tuple', 'list', 'type', 'cmp', 'sum', 'zip']:
                self.append('__' + ident + '(')
            elif ident in ['min', 'max', 'iter', 'round']:
                self.append('___' + ident + '(')
            elif ident == 'bool':
                self.bool_test(node.args[0], func, always_wrap=True)
                return
            elif ident == 'pow' and direct_call.mv.module.ident == 'builtin':
                if nrargs == 3:
                    third = node.args[2]
                else:
                    third = None
                self.power(node.args[0], node.args[1], third, func)
                return
            elif ident == 'hash':
                self.append('hasher(')  # XXX cleanup
            elif ident == '__print':  # XXX
                self.append('print(')
            elif ident == 'isinstance' and node.args[0] not in self.gx.filters:
                self.append('True')
                return
            else:
                if isinstance(node.func, ast.Name):
                    if isinstance(func, python.Function) and isinstance(func.parent, python.Class) and ident in func.parent.funcs:  # masked by method
                        self.append(funcs[0].mv.module.full_path() + '::')
                    self.append(self.cpp_name(funcs[0]))
                else:
                    self.visit(node.func)
                self.append('(')

        elif method_call:
            for cl, _ in self.mergeinh[objexpr]:
                if isinstance(cl, python.Class) and cl.ident != 'none' and ident not in cl.funcs:
                    conv = {'int_': 'int', 'float_': 'float', 'str_': 'str', 'class_': 'class', 'none': 'none'}
                    clname = conv.get(cl.ident, cl.ident)
                    error.error("class '%s' has no method '%s'" % (clname, ident), self.gx, node, warning=True, mv=self.mv)
                if isinstance(cl, python.Class) and ident in cl.staticmethods:
                    error.error("staticmethod '%s' called without using class name" % ident, self.gx, node, warning=True, mv=self.mv)
                    return

            # tuple2.__getitem -> __getfirst__/__getsecond
            if ident == '__getitem__' and isinstance(node.args[0], ast.Num) and node.args[0].n in (0, 1) and self.only_classes(objexpr, ('tuple2',)):
                self.visit(node.func.value, func)
                self.append('->%s()' % ['__getfirst__', '__getsecond__'][node.args[0].n])
                return

            if ident == '__call__':
                self.visitm(node.func, '->__call__(', func)
            elif ident == 'is_integer' and (python.def_class(self.gx, 'float_'), 0) in self.mergeinh[node.func.value]:
                self.visitm('__ss_is_integer(', node.func.value, ')', func)
                return
            else:
                self.visitm(node.func, '(', func)

        else:
            if ident:
                error.error("unresolved call to '" + ident + "'", self.gx, node, mv=self.mv, warning=True)
            else:
                error.error("unresolved call (possibly caused by method passing, which is currently not allowed)", self.gx, node, mv=self.mv, warning=True)
            return

        if not funcs:
            if constructor:
                self.append(')')
            self.append(')')
            return

        self.visit_callfunc_args(funcs, node, func)

        self.append(')')
        if constructor:
            self.append(')')

    def bool_test(self, node, func, always_wrap=False):
        wrapper = always_wrap or not self.only_classes(node, ('int_', 'bool_'))
        if node in self.gx.bool_test_only:
            self.visit(node, func)
        elif wrapper:
            self.append('___bool(')
            self.visit(node, func)
            is_func = bool([1 for t in self.mergeinh[node] if isinstance(t[0], python.Function)])
            self.append(('', '!=NULL')[is_func] + ')')  # XXX
        else:
            self.bool_wrapper[node] = True
            self.visit(node, func)

    def visit_callfunc_args(self, funcs, node, func):
        objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = infer.analyze_callfunc(self.gx, node, merge=self.gx.merged_inh)
        target = funcs[0]  # XXX

        print_function = self.library_func(funcs, 'builtin', None, '__print')

        castnull = False  # XXX
        if (self.library_func(funcs, 'random', None, 'seed') or
            self.library_func(funcs, 'random', None, 'triangular') or
            self.library_func(funcs, 'random', 'Random', 'seed') or
                self.library_func(funcs, 'random', 'Random', 'triangular')):
            castnull = True
        for itertools_func in ['islice', 'izip_longest', 'permutations']:
            if self.library_func(funcs, 'itertools', None, itertools_func):
                castnull = True
                break

        for f in funcs:
            if len(f.formals) != len(target.formals):
                error.error('calling functions with different numbers of arguments', self.gx, node, warning=True, mv=self.mv)
                self.append(')')
                return

        if target.inherited_from:
            target = target.inherited_from

        pairs, rest, err = infer.connect_actual_formal(self.gx, node, target, parent_constr, merge=self.mergeinh)
        if (err and not self.library_func(funcs, 'builtin', None, 'sum')
                and not self.library_func(funcs, 'builtin', None, 'next')):
            error.error('call with incorrect number of arguments', self.gx, node, warning=True, mv=self.mv)

        if isinstance(func, python.Function) and func.lambdawrapper:
            rest = func.largs

        if target.node.args.vararg:
            self.append('%d' % rest)
            if rest or pairs:
                self.append(', ')

        double = False
        if ident in ['min', 'max']:
            for arg in node.args:
                if arg in self.mergeinh and (python.def_class(self.gx, 'float_'), 0) in self.mergeinh[arg]:
                    double = True

        self.add_args_arg(node, funcs)

        if isinstance(func, python.Function) and func.largs is not None:
            kw = [p for p in pairs if p[1].name.startswith('__kw_')]
            nonkw = [p for p in pairs if not p[1].name.startswith('__kw_')]
            pairs = kw + nonkw[:func.largs]

        for (arg, formal) in pairs:
            cast = False
            builtin_types = self.cast_to_builtin(arg, func, formal, target, method_call, objexpr)
            formal_types = builtin_types or self.mergeinh[formal]

            if double and self.mergeinh[arg] == set([(python.def_class(self.gx, 'int_'), 0)]):
                cast = True
                self.append('(double(')
            elif castnull and ast_utils.is_none(arg):
                cast = True
                self.append('((void *)(')

            if (print_function or self.library_func(funcs, 'struct', None, 'pack')) and not formal.name.startswith('__kw_'):
                types = [t[0].ident for t in self.mergeinh[arg]]
                if 'float_' in types or 'int_' in types or 'bool_' in types or 'complex' in types:
                    cast = True
                    self.append('___box((')

            if arg in target.mv.defaults:
                if self.mergeinh[arg] == set([(python.def_class(self.gx, 'none'), 0)]):
                    self.append('NULL')
                elif target.mv.module == self.mv.module:
                    self.append('default_%d' % (target.mv.defaults[arg][0]))
                else:
                    self.append('%s::default_%d' % (target.mv.module.full_path(), target.mv.defaults[arg][0]))

            elif arg in self.consts:
                self.append(self.consts[arg])
            else:
                if constructor and ident in ['set', 'frozenset'] and typestr.nodetypestr(self.gx, arg, func, mv=self.mv) in ['list<void *> *', 'tuple<void *> *', 'pyiter<void *> *', 'pyseq<void *> *', 'pyset<void *>']:  # XXX
                    pass
                elif not builtin_types and target.mv.module.builtin:
                    self.visit(arg, func)
                else:
                    self.impl_visit_conv(arg, formal_types, func)

            if cast:
                self.append('))')
            if (arg, formal) != pairs[-1]:
                self.append(', ')

        if constructor and ident in ('frozenset', 'bytearray'):
            if pairs:
                self.append(',')
            if ident == 'frozenset':
                self.append('1')
            else:
                self.append('0')

    def cast_to_builtin(self, arg, func, formal, target, method_call, objexpr):
        # type inference cannot deduce all necessary casts to builtin formals
        vars = {'u': 'unit', 'v': 'value', 'o': None}
        if target.mv.module.builtin and method_call and formal.name in vars and target.parent.ident in ('list', 'dict', 'set'):
            subtypes = self.subtypes(self.mergeinh[objexpr], vars[formal.name])
            if typestr.nodetypestr(self.gx, arg, func, mv=self.mv) != typestr.typestr(self.gx, subtypes, mv=self.mv):
                return subtypes

    def cast_to_builtin2(self, arg, func, objexpr, msg, formal_nr):
        # shortcut for outside of visit_Call XXX merge with visit_Call?
        cls = [t[0] for t in self.mergeinh[objexpr] if isinstance(t[0], python.Class)]
        if cls:
            cl = cls.pop()
            if msg in cl.funcs:
                target = cl.funcs[msg]
                if formal_nr < len(target.formals):
                    formal = target.vars[target.formals[formal_nr]]
                    builtin_types = self.cast_to_builtin(arg, func, formal, target, True, objexpr)
                    if builtin_types:
                        return typestr.typestr(self.gx, builtin_types, mv=self.mv)

    def visit_Return(self, node, func=None):
        if func.isGenerator:
            self.output('__stop_iteration = true;')
            func2 = typestr.nodetypestr(self.gx, func.retnode.thing, mv=self.mv)[7:-3] # XXX meugh
            self.output('return __zero<%s>();' % func2)
            return
        self.start('return ')
        self.impl_visit_conv(node.value, self.mergeinh[func.retnode.thing], func)
        self.eol()

    def tuple_assign(self, lvalue, rvalue, func):
        temp = self.mv.tempcount[lvalue]
        if isinstance(lvalue, tuple):
            nodes = lvalue
        else:
            nodes = lvalue.elts

        # --- nested unpacking assignment: a, (b,c) = d, e
        if [item for item in nodes if not isinstance(item, ast.Name)]:
            self.start(temp + ' = ')
            if isinstance(rvalue, str):
                self.append(rvalue)
            else:
                self.visit(rvalue, func)
            self.eol()

            for i, item in enumerate(nodes):
                selector = self.get_selector(temp, item, i)
                if isinstance(item, ast.Name):
                    self.output('%s = %s;' % (item.id, selector))
                elif ast_utils.is_assign_list_or_tuple(item):  # recursion
                    self.tuple_assign(item, selector, func)
                elif isinstance(item, ast.Subscript):
                    self.assign_pair(item, selector, func)
                elif ast_utils.is_assign_attribute(item):
                    self.assign_pair(item, selector, func)
                    self.eol(' = ' + selector)

        # --- non-nested unpacking assignment: a,b,c = d
        else:
            self.start()
            self.visitm(temp, ' = ', rvalue, func)
            self.eol()
            for i, item in enumerate(lvalue.elts):
                self.start()
                self.visitm(item, ' = ', self.get_selector(temp, item, i), func)
                self.eol()

    def one_class(self, node, names):
        for clname in names:
            if self.only_classes(node, (clname,)):
                return True
        return False

    def get_selector(self, temp, item, i):
        rvalue_node = self.gx.item_rvalue[item]
        sel = '__getitem__(%d)' % i
        if i < 2 and self.only_classes(rvalue_node, ('tuple2',)):
            sel = ['__getfirst__()', '__getsecond__()'][i]
        elif self.one_class(rvalue_node, ('list', 'str_', 'tuple')):
            sel = '__getfast__(%d)' % i
        return '%s->%s' % (temp, sel)

    def subs_assign(self, lvalue, func):
        if isinstance(lvalue.slice, ast.Index):
            subs = lvalue.slice.value
        else:
            subs = lvalue.slice
        self.visitm(lvalue.value, self.connector(lvalue.value, func), '__setitem__(', subs, ', ', func)

    def struct_unpack_cpp(self, node, func):
        struct_unpack = self.gx.struct_unpack.get(node)
        if struct_unpack:
            sinfo, tvar, tvar_pos = struct_unpack
            self.start()
            self.visitm(tvar, ' = ', node.value.args[1], func)
            self.eol()
            self.output('%s = 0;' % tvar_pos)
            hop = 0
            for (o, c, t, d) in sinfo:
                self.start()
                expr = "__struct__::unpack_%s('%c', '%c', %d, %s, &%s)" % (t, o, c, d, tvar, tvar_pos)
                if c == 'x' or (d == 0 and c != 's'):
                    self.visitm(expr, func)
                else:
                    n = list(node.targets[0].elts)[hop]
                    hop += 1
                    if isinstance(n, ast.Subscript):  # XXX merge
                        self.subs_assign(n, func)
                        self.visitm(expr, ')', func)
                    elif isinstance(n, ast.Name):
                        self.visitm(n, ' = ', expr, func)
                    elif ast_utils.is_assign_attribute(n):
                        self.visit_Attribute(n, func)
                        self.visitm(' = ', expr, func)
                self.eol()
            return True
        return False

    def visit_Delete(self, node, func=None):
        for child in node.targets:
            assert type(child.ctx) == ast.Del
            self.visit(child, func)

    def visit_Assign(self, node, func=None):
        if self.struct_unpack_cpp(node, func):
            return

        # temp vars
        if len(node.targets) > 1 or isinstance(node.value, ast.Tuple):
            if isinstance(node.value, ast.Tuple):
                if [n for n in node.targets if ast_utils.is_assign_tuple(n)]:  # XXX a,b=d[i,j]=..?
                    for child in node.value.elts:
                        if not (child, 0, 0) in self.gx.cnode:  # (a,b) = (1,2): (1,2) never visited
                            continue
                        if not ast_utils.is_constant(child) and not ast_utils.is_none(child):
                            self.start(self.mv.tempcount[child] + ' = ')
                            self.visit(child, func)
                            self.eol()
            elif not ast_utils.is_constant(node.value) and not ast_utils.is_none(node.value):
                self.start(self.mv.tempcount[node.value] + ' = ')
                self.visit(node.value, func)
                self.eol()

        # a = (b,c) = .. = expr
        for left in node.targets:
            pairs = python.assign_rec(left, node.value)

            for (lvalue, rvalue) in pairs:
                self.start('')  # XXX remove?

                # expr[expr] = expr
                if isinstance(lvalue, ast.Subscript) and not isinstance(lvalue.slice, (ast.Slice, ast.ExtSlice)):
                    self.assign_pair(lvalue, rvalue, func)

                # expr.attr = expr
                elif ast_utils.is_assign_attribute(lvalue):
                    lcp = typestr.lowest_common_parents(typestr.polymorphic_t(self.gx, self.mergeinh[lvalue.value]))
                    # property
                    if len(lcp) == 1 and isinstance(lcp[0], python.Class) and lvalue.attr in lcp[0].properties:
                        self.visitm(lvalue.value, '->' + self.cpp_name(lcp[0].properties[lvalue.attr][1]) + '(', rvalue, ')', func)
                    elif lcp and isinstance(lcp[0], python.Class):
                        var = python.lookup_var(lvalue.attr, lcp[0], mv=self.mv)
                        vartypes = set()
                        if var:
                            vartypes = self.mergeinh[var]
                        self.visit(lvalue, func)
                        self.append(' = ')
                        self.impl_visit_conv(rvalue, vartypes, func)
                    else:
                        self.visitm(lvalue, ' = ', rvalue, func)
                    self.eol()

                # name = expr
                elif isinstance(lvalue, ast.Name):
                    vartypes = self.mergeinh[python.lookup_var(lvalue.id, func, mv=self.mv)]
                    self.visit(lvalue, func)
                    self.append(' = ')
                    self.impl_visit_conv(rvalue, vartypes, func)
                    self.eol()

                # (a,(b,c), ..) = expr
                elif ast_utils.is_assign_list_or_tuple(lvalue):
                    self.tuple_assign(lvalue, rvalue, func)

                elif isinstance(lvalue, ast.Slice):
                    assert False, "ast.Slice shouldn't appear outside ast.Subscript node"

                # expr[a:b] = expr
                # expr[a:b:c] = expr
                elif isinstance(lvalue, ast.Subscript) and isinstance(lvalue.slice, ast.Slice):  # XXX see comment above
                    if isinstance(rvalue, ast.Slice) and lvalue.upper == rvalue.upper == None and lvalue.lower == rvalue.lower == None:
                        self.visitm(lvalue.expr, self.connector(lvalue.expr, func), 'units = ', rvalue.expr, self.connector(rvalue.expr, func), 'units', func)
                    else:  # XXX let visit_Call(fakefunc) use cast_to_builtin
                        fakefunc = infer.inode(self.gx, lvalue.value).fakefunc
                        self.visitm('(', fakefunc.func.value, ')->__setslice__(', fakefunc.args[0], ',', fakefunc.args[1], ',', fakefunc.args[2], ',', fakefunc.args[3], ',', func)
                        if [t for t in self.mergeinh[lvalue.value] if t[0].ident == 'bytes_']:  # TODO more general fix
                            self.visit(fakefunc.args[4], func)
                        elif [t for t in self.mergeinh[fakefunc.args[4]] if t[0].ident == '__xrange']:
                            self.visit(fakefunc.args[4], func)
                        else:
                            self.impl_visit_conv(fakefunc.args[4], self.mergeinh[lvalue.value], func)
                        self.append(')')
                    self.eol()

    def assign_pair(self, lvalue, rvalue, func):
        self.start('')

        # expr[expr] = expr
        if isinstance(lvalue, ast.Subscript) and not isinstance(lvalue.slice, (ast.Slice, ast.ExtSlice)):
            self.subs_assign(lvalue, func)
            if isinstance(rvalue, str):
                self.append(rvalue)
            elif rvalue in self.mv.tempcount:
                self.append(self.mv.tempcount[rvalue])
            else:
                cast = self.cast_to_builtin2(rvalue, func, lvalue.value, '__setitem__', 2)
                if cast:
                    self.append('((%s)' % cast)
                self.visit(rvalue, func)
                if cast:
                    self.append(')')
            self.append(')')
            self.eol()

        # expr.x = expr
        elif ast_utils.is_assign_attribute(lvalue):
            self.visit_Attribute(lvalue, func)

    def do_lambdas(self, declare):
        for l in self.mv.lambdas.values():
            if l.ident not in self.mv.funcs:
                self.visit_FunctionDef(l.node, declare=declare)

    def do_listcomps(self, declare):
        for (listcomp, lcfunc, func) in self.mv.listcomps:  # XXX cleanup
            if lcfunc.mv.module.builtin:
                continue

            parent = func
            while isinstance(parent, python.Function) and parent.listcomp:
                parent = parent.parent

            if isinstance(parent, python.Function):
                if not self.inhcpa(parent) or parent.inherited:
                    continue

            genexpr = listcomp in self.gx.genexp_to_lc.values()
            if declare:
                self.listcomp_head(listcomp, True, genexpr)
            elif genexpr:
                self.genexpr_class(listcomp, declare)
            else:
                self.listcomp_func(listcomp)

    def listcomp_head(self, node, declare, genexpr):
        lcfunc, func = self.listcomps[node]
        args = [a + b for a, b in self.lc_args(lcfunc, func)]
        ts = typestr.nodetypestr(self.gx, node, lcfunc, mv=self.mv)
        if not ts.endswith('*'):
            ts += ' '
        if genexpr:
            self.genexpr_class(node, declare)
        else:
            self.output('static inline ' + ts + lcfunc.ident + '(' + ', '.join(args) + ')' + [' {', ';'][declare])

    def lc_args(self, lcfunc, func):
        args = []
        for name in lcfunc.misses:
            if python.lookup_var(name, func, mv=self.mv).parent:
                args.append((typestr.nodetypestr(self.gx, python.lookup_var(name, lcfunc, mv=self.mv), lcfunc, mv=self.mv), self.cpp_name(name)))
        return args

    def listcomp_func(self, node):
        lcfunc, func = self.listcomps[node]
        self.listcomp_head(node, False, False)
        self.indent()
        self.local_defs(lcfunc)
        self.output(typestr.nodetypestr(self.gx, node, lcfunc, mv=self.mv) + '__ss_result = new ' + typestr.nodetypestr(self.gx, node, lcfunc, mv=self.mv)[:-2] + '();\n')
        self.listcomp_rec(node, node.generators, lcfunc, False)
        self.output('return __ss_result;')
        self.deindent()
        self.output('}\n')

    def genexpr_class(self, node, declare):
        lcfunc, func = self.listcomps[node]
        args = self.lc_args(lcfunc, func)
        func1 = lcfunc.ident + '(' + ', '.join(a + b for a, b in args) + ')'
        func2 = typestr.nodetypestr(self.gx, node, lcfunc, mv=self.mv)[7:-3]
        if declare:
            ts = typestr.nodetypestr(self.gx, node, lcfunc, mv=self.mv)
            if not ts.endswith('*'):
                ts += ' '
            self.output('class ' + lcfunc.ident + ' : public ' + ts[:-2] + ' {')
            self.output('public:')
            self.indent()
            self.local_defs(lcfunc)
            for a, b in args:
                self.output(a + b + ';')
            self.output('int __last_yield;\n')
            self.output(func1 + ';')
            self.output(func2 + ' __get_next();')
            self.deindent()
            self.output('};\n')
        else:
            self.output(lcfunc.ident + '::' + func1 + ' {')
            for a, b in args:
                self.output('    this->%s = %s;' % (b, b))
            self.output('    __last_yield = -1;')
            self.output('}\n')
            self.output(func2 + ' ' + lcfunc.ident + '::__get_next() {')
            self.indent()
            self.output('if(!__last_yield) goto __after_yield_0;')
            self.output('__last_yield = 0;\n')
            self.listcomp_rec(node, node.generators, lcfunc, True)
            self.output('__stop_iteration = true;')
            self.output('return __zero<%s>();' % func2)
            self.deindent()
            self.output('}\n')

    def local_defs(self, func):
        pairs = []
        for (name, var) in func.vars.items():
            if not var.invisible and (not hasattr(func, 'formals') or name not in func.formals):  # XXX
                pairs.append((typestr.nodetypestr(self.gx, var, func, mv=self.mv), self.cpp_name(var)))
        self.output(self.indentation.join(self.group_declarations(pairs)))

    # --- nested for loops: loop headers, if statements
    def listcomp_rec(self, node, quals, lcfunc, genexpr):
        if not quals:
            if genexpr:
                self.start('__result = ')
                self.visit(node.elt, lcfunc)
                self.eol()
                self.output('return __result;')
                self.start('__after_yield_0:')
            elif len(node.generators) == 1 and not python.is_fastfor(node.generators[0]) and not self.fastenum(node.generators[0]) and not self.fastzip2(node.generators[0]) and not node.generators[0].ifs and self.one_class(node.generators[0].iter, ('tuple', 'list', 'str_', 'dict', 'set')):
                self.start('__ss_result->units[' + self.mv.tempcount[node.generators[0].iter] + '] = ')
                self.visit(node.elt, lcfunc)
            else:
                self.start('__ss_result->append(')
                self.visit(node.elt, lcfunc)
                self.append(')')
            self.eol()
            return

        qual = quals[0]

        # iter var
        if isinstance(qual.target, ast.Name):
            var = python.lookup_var(qual.target.id, lcfunc, mv=self.mv)
        else:
            var = python.lookup_var(self.mv.tempcount[qual.target], lcfunc, mv=self.mv)
        iter = self.cpp_name(var)

        if python.is_fastfor(qual):
            self.do_fastfor(node, qual, quals, iter, lcfunc, genexpr)
        elif self.fastenum(qual):
            self.do_fastenum(qual, lcfunc, genexpr)
            self.listcompfor_body(node, quals, iter, lcfunc, True, genexpr)
        elif self.fastzip2(qual):
            self.do_fastzip2(qual, lcfunc, genexpr)
            self.listcompfor_body(node, quals, iter, lcfunc, True, genexpr)
        elif self.fastdictiter(qual):
            self.do_fastdictiter(qual, lcfunc, genexpr)
            self.listcompfor_body(node, quals, iter, lcfunc, True, genexpr)
        else:
            if not isinstance(qual.iter, ast.Name):
                itervar = self.mv.tempcount[qual]
                self.start('')
                self.visitm(itervar, ' = ', qual.iter, lcfunc)
                self.eol()
            else:
                itervar = self.cpp_name(qual.iter.id)

            pref, tail = self.forin_preftail(qual)

            if len(node.generators) == 1 and not qual.ifs and not genexpr:
                if self.one_class(qual.iter, ('list', 'tuple', 'str_', 'dict', 'set')):
                    self.output('__ss_result->resize(len(' + itervar + '));')

            self.start('FOR_IN' + pref + '(' + iter + ',' + itervar + ',' + tail)
            self.print(self.line + ')')
            self.listcompfor_body(node, quals, iter, lcfunc, False, genexpr)

    def listcompfor_body(self, node, quals, iter, lcfunc, skip, genexpr):
        qual = quals[0]

        if not skip:
            self.indent()
            if ast_utils.is_assign_list_or_tuple(qual.target):
                self.tuple_assign(qual.target, iter, lcfunc)

        # if statements
        if qual.ifs:
            self.start('if (')
            self.indent()
            for cond in qual.ifs:
                self.bool_test(cond, lcfunc)
                if cond != qual.ifs[-1]:
                    self.append(' && ')
            self.append(') {')
            self.print(self.line)

        # recurse
        self.listcomp_rec(node, quals[1:], lcfunc, genexpr)

        # --- nested for loops: loop tails
        if qual.ifs:
            self.deindent()
            self.output('}')
        self.deindent()
        self.output('END_FOR\n')

    def visit_GeneratorExp(self, node, func=None):
        self.visit(self.gx.genexp_to_lc[node], func)

    def visit_ListComp(self, node, func=None):
        lcfunc, _ = self.listcomps[node]
        args = []
        temp = self.line

        for name in lcfunc.misses:
            var = python.lookup_var(name, func, mv=self.mv)
            if var.parent:
                if name == 'self' and not func.listcomp:  # XXX parent?
                    args.append('this')
                else:
                    args.append(self.cpp_name(var))

        self.line = temp
        if node in self.gx.genexp_to_lc.values():
            self.append('new ')
        self.append(lcfunc.ident + '(' + ', '.join(args) + ')')

    def visit_Subscript(self, node, func=None):
        if type(node.ctx) in (ast.Load, ast.Store):
            self.visit_Call(infer.inode(self.gx, node.value).fakefunc, func)
        elif type(node.ctx) == ast.Del:
            self.start()
            if isinstance(node.slice, ast.Slice):
                self.visit_Call(infer.inode(self.gx, node.value).fakefunc, func)
            else:
                self.visit_Call(infer.inode(self.gx, node.value).fakefunc, func)
            self.eol()
        else:
            error.error("unknown ctx type for ast.Subscript, " + type(node.ctx), self.gx, node, mv=self.mv)

    def impl_visit_Mod(self, node, func=None):
        # --- non-str % ..
        if [t for t in self.gx.merged_inh[node.left] if t[0].ident not in ('str_', 'bytes_')]:
            self.impl_visit_binary(node.left, node.right, '__mod__', '%', func)
            return

        # --- str % non-constant dict/tuple
        if not isinstance(node.right, (ast.Tuple, ast.Dict)) and node.right in self.gx.merged_inh:  # XXX
            if [t for t in self.gx.merged_inh[node.right] if t[0].ident == 'dict']:
                self.visitm('__moddict(', node.left, ', ', node.right, ')', func)
                return
            elif [t for t in self.gx.merged_inh[node.right] if t[0].ident in ['tuple', 'tuple2']]:
                self.visitm('__modtuple(', node.left, ', ', node.right, ')', func)
                return

        # --- str % constant-dict:
        if isinstance(node.right, ast.Dict):  # XXX geen str keys
            self.visitm('__modcd(', node.left, ', ', 'new list<str *>(%d, ' % len(node.right.keys), func)
            self.append(', '.join(('new str("%s")' % key.s) for key, value in zip(node.right.keys, node.right.values)))
            self.append(')')
            nodes = list(node.right.values)
        else:
            self.visitm('__modct(', node.left, func)
            # --- str % constant-tuple
            if isinstance(node.right, ast.Tuple):
                nodes = node.right.elts

            # --- str % non-tuple/non-dict
            else:
                nodes = [node.right]
            self.append(', %d' % len(nodes))

        # --- visit nodes, boxing scalars
        for n in nodes:
            if [clname for clname in ('float_', 'int_', 'bool_', 'complex') if python.def_class(self.gx, clname) in [t[0] for t in self.mergeinh[n]]]:
                self.visitm(', ___box(', n, ')', func)
            else:
                self.visitm(', ', n, func)
        self.append(')')

    def visit_Print(self, node, func=None):
        self.start('print2(')
        if node.dest:
            self.visitm(node.dest, ', ', func)
        else:
            self.append('NULL,')
        if node.nl is False:
            self.append('1,')
        else:
            self.append('0,')
        self.append(str(len(node.values)))
        for n in node.values:
            types = [t[0].ident for t in self.mergeinh[n]]
            if 'float_' in types or 'int_' in types or 'bool_' in types or 'complex' in types:
                self.visitm(', ___box(', n, ')', func)
            else:
                self.visitm(', ', n, func)
        self.eol(')')

    def attr_var_ref(self, node, ident):  # XXX blegh
        lcp = typestr.lowest_common_parents(typestr.polymorphic_t(self.gx, self.mergeinh[node.value]))
        if len(lcp) == 1 and isinstance(lcp[0], python.Class) and node.attr in lcp[0].vars and not node.attr in lcp[0].funcs:
            return self.cpp_name(lcp[0].vars[node.attr])
        return self.cpp_name(ident)

    def visit_Attribute(self, node, func=None):  # XXX merge with visitGetattr
        if type(node.ctx) == ast.Load:
            cl, module = python.lookup_class_module(node.value, infer.inode(self.gx, node).mv, func)

            # module.attr
            if module:
                self.append(module.full_path() + '::')

            # class.attr: staticmethod
            elif cl and node.attr in cl.staticmethods:
                ident = cl.ident
                if cl.ident in ['dict', 'defaultdict']:  # own namespace because of template vars
                    self.append('__' + cl.ident + '__::')
                elif isinstance(node.value, ast.Attribute):
                    submodule = python.lookup_module(node.value.value, infer.inode(self.gx, node).mv)
                    self.append(submodule.full_path() + '::' + ident + '::')
                else:
                    self.append(ident + '::')

            # class.attr
            elif cl:  # XXX merge above?
                ident = cl.ident
                if isinstance(node.value, ast.Attribute):
                    submodule = python.lookup_module(node.value.value, infer.inode(self.gx, node).mv)
                    self.append(submodule.full_path() + '::' + cl.ident + '::')
                else:
                    self.append(ident + '::')

            # obj.attr
            else:
                checkcls = []  # XXX better to just inherit vars?
                for t in self.mergeinh[node.value]:
                    if isinstance(t[0], python.Class):
                        checkcls.extend(t[0].ancestors(True))
                for cl in checkcls:
                    if not node.attr in t[0].funcs and node.attr in cl.parent.vars:  # XXX
                        error.error("class attribute '" + node.attr + "' accessed without using class name", self.gx, node, warning=True, mv=self.mv)
                        break

                    if not hasattr(node, 'called') and [cl for cl in checkcls if node.attr in cl.funcs]:
                        error.error('method passing is not supported', self.gx, node, warning=True, mv=self.mv)

                else:
                    if not self.mergeinh[node.value] and not node.attr.startswith('__'):  # XXX
                        error.error('expression has no type', self.gx, node, warning=True, mv=self.mv)
                    elif not self.mergeinh[node] and not [cl for cl in checkcls if node.attr in cl.funcs] and not node.attr.startswith('__'):  # XXX
                        error.error('expression has no type', self.gx, node, warning=True, mv=self.mv)

                if not isinstance(node.value, ast.Name):
                    self.append('(')
                if isinstance(node.value, ast.Name) and not python.lookup_var(node.value.id, func, mv=self.mv):  # XXX XXX
                    self.append(node.value.id)
                else:
                    self.visit(node.value, func)
                if not isinstance(node.value, (ast.Name)):
                    self.append(')')

                self.append(self.connector(node.value, func))

            ident = node.attr

            # property
            lcp = typestr.lowest_common_parents(typestr.polymorphic_t(self.gx, self.mergeinh[node.value]))
            if len(lcp) == 1 and node.attr in lcp[0].properties:
                self.append(self.cpp_name(lcp[0].properties[node.attr][0]) + '()')
                return

            # getfast
            if ident == '__getitem__' and self.one_class(node.value, ('list', 'str_', 'tuple')):
                ident = '__getfast__'
            elif ident == '__getitem__' and len(lcp) == 1 and lcp[0].ident == 'array':  # XXX merge into above
                ident = '__getfast__'

            self.append(self.attr_var_ref(node, ident))
        elif type(node.ctx) == ast.Del:
            error.error("'del' has no effect without refcounting", self.gx, node, warning=True, mv=self.mv)
        elif type(node.ctx) == ast.Store:
            cl, module = python.lookup_class_module(node.value, infer.inode(self.gx, node).mv, func)

            # module.attr
            if module:
                self.append(module.full_path() + '::')

            # class.attr
            elif cl:
                if isinstance(node.value, ast.Attribute):
                    submodule = python.lookup_module(node.value.value, infer.inode(self.gx, node).mv)
                    self.append(submodule.full_path() + '::' + cl.ident + '::')
                else:
                    self.append(cl.ident + '::')

            # obj.attr
            else:
                if isinstance(node.value, ast.Name) and not python.lookup_var(node.value.id, func, mv=self.mv):  # XXX
                    self.append(node.value.id)
                else:
                    self.visit(node.value, func)
                self.append(self.connector(node.value, func))  # XXX '->'

            self.append(self.attr_var_ref(node, node.attr))
        else:
            error.error("unknown ctx type for ast.Attribute, " + type(node.ctx), self.gx, node, mv=self.mv)

    def visit_Name(self, node, func=None, add_cl=True):
        if type(node.ctx) == ast.Del:
            error.error("'del' has no effect without refcounting", self.gx, node, warning=True, mv=self.mv)
        elif type(node.ctx) in (ast.Store, ast.Param):
            self.append(self.cpp_name(node.id))
        elif type(node.ctx) in (ast.Load,):
            map = {'True': 'True', 'False': 'False'}
            if node in self.mv.lwrapper:
                self.append(self.mv.lwrapper[node])
            elif node.id == 'None': # py2
                self.append('NULL')
            elif node.id == 'self':
                lcp = typestr.lowest_common_parents(typestr.polymorphic_t(self.gx, self.mergeinh[node]))
                if ((not func or func.listcomp or not isinstance(func.parent, python.Class)) or
                   (func and func.parent and func.isGenerator)):  # XXX python.lookup_var?
                    self.append('self')
                elif len(lcp) == 1 and not (lcp[0] is func.parent or lcp[0] in func.parent.ancestors()):  # see test 160
                    self.mv.module.prop_includes.add(lcp[0].module)  # XXX generalize
                    self.append('((' + self.namer.namespace_class(lcp[0]) + ' *)this)')
                else:
                    self.append('this')
            elif node.id in map:
                self.append(map[node.id])

            else:  # XXX clean up
                if not self.mergeinh[node] and not infer.inode(self.gx, node).parent in self.gx.inheritance_relations:
                    error.error("variable '" + node.id + "' has no type", self.gx, node, warning=True, mv=self.mv)
                    self.append(node.id)
                elif typestr.singletype(self.gx, node, python.Module):
                    self.append('__' + typestr.singletype(self.gx, node, python.Module).ident + '__')
                else:
                    if ((python.def_class(self.gx, 'class_'), 0) in self.mergeinh[node] or
                       (add_cl and [t for t in self.mergeinh[node] if isinstance(t[0], python.StaticClass)])):
                        cl = python.lookup_class(node, self.mv)
                        if cl:
                            self.append(self.namer.namespace_class(cl, add_cl='cl_'))
                        else:
                            self.append(self.cpp_name(node.id))
                    else:
                        if isinstance(func, python.Class) and node.id in func.parent.vars:  # XXX
                            self.append(func.ident + '::')
                        var = python.smart_lookup_var(node.id, func, mv=self.mv)
                        if var:
                            if node in self.gx.filters:
                                self.append('((%s *)' % self.gx.filters[node].ident)
                            if var.is_global:
                                self.append(self.module.full_path() + '::')
                            self.append(self.cpp_name(var.var))
                            if node in self.gx.filters:
                                self.append(')')
                        else:
                            self.append(node.id)  # XXX
        else:
            error.error("unknown ctx type for Name, " + type(node.ctx), self.gx, node, mv=self.mv)

    def expand_special_chars(self, value):
        if isinstance(value, str):
            value = value.encode('utf-8') # restriction

        value = [chr(c) for c in value]
        replace = dict(['\\\\', '\nn', '\tt', '\rr', '\ff', '\bb', '\vv', '""'])

        for i in range(len(value)):
            if value[i] in replace:
                value[i] = '\\' + replace[value[i]]
            elif value[i] not in string.printable:
                octval = oct(ord(value[i]))
                if octval.startswith('0o'): # py3
                    octval = octval[2:]
                value[i] = '\\' + octval.zfill(4)[1:]

        return ''.join(value)

    def visit_const(self, node, value):
        if isinstance(value, bool):
            self.append(str(value))

        elif value is None:
            self.append('NULL')

        elif value.__class__.__name__ in ('int', 'long'): #isinstance(value, int):
            self.append('__ss_int(')
            self.append(str(value))
            if self.gx.longlong:
                self.append('LL')
            self.append(')')

        elif isinstance(value, float):
            if str(value) in ['inf', '1.#INF', 'Infinity']:
                self.append('INFINITY')
            elif str(value) in ['-inf', '-1.#INF', '-Infinity']:
                self.append('-INFINITY')
            else:
                self.append(str(value))

        elif isinstance(value, complex):
            self.append('mcomplex(%s, %s)' % (value.real, value.imag))

        elif isinstance(value, str):
            if not self.filling_consts:
                self.append(self.get_constant(node))
            else:
                self.append('new str("%s"' % self.expand_special_chars(value))
                if '\0' in value:
                    self.append(', %d' % len(value))
                self.append(')')

        elif isinstance(value, bytes):  # TODO merge with str above
            self.append('new bytes("%s"' % self.expand_special_chars(value))
            if b'\0' in value:
                self.append(', %d' % len(value))
            self.append(')')

        else:
            assert False

    def visit_Constant(self, node, func=None):
        self.visit_const(node, node.value)

    def visit_Num(self, node, func=None):
        self.visit_const(node, node.n)

    def visit_Str(self, node, func=None):
        self.visit_const(node, node.s)


def generate_code(gx):
    for module in gx.modules.values():
        if not module.builtin:
            gv = GenerateVisitor(gx, module)
            gv.visit(module.ast)
            # from IPython import embed; embed()
            gv.out.close()
            gv.header_file()
            gv.out.close()
            gv.insert_consts(declare=False)
            gv.insert_consts(declare=True)
            gv.insert_extras('.hpp')
            gv.insert_extras('.cpp')
    makefile.generate_makefile(gx)


