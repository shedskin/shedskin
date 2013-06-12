'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

cpp.py: output C++ code

output equivalent C++ code, using templates and virtuals to support data and OO polymorphism.

class GenerateVisitor: inherits visitor pattern from compiler.visitor.ASTVisitor, to recursively generate C++ code for each syntactical Python construct. the constraint graph, with inferred types, is first 'merged' back to program dimensions (gx.merged_inh).

'''
import string
import struct
import textwrap
from compiler import walk
from compiler.ast import Const, AssTuple, AssList, From, Add, Stmt, AssAttr, \
    Keyword, AssName, CallFunc, Slice, Getattr, Dict, Subscript, \
    Function as FunctionNode, Return, Class as ClassNode, Name, List, Discard, Sliceobj, Tuple
from compiler.visitor import ASTVisitor

from error import error
from extmod import convert_methods, convert_methods2, do_extmod, pyinit_func
from infer import analyze_callfunc, callfunc_targets, connect_actual_formal, \
    called, inode, var_types
from makefile import generate_makefile
from python import assign_rec, aug_msg, Class, def_class, \
    is_enum, is_fastfor, is_literal, is_zip2, \
    lookup_class, lookup_class_module, lookup_var, lookup_module, \
    Function, Module, Variable, StaticClass
from typestr import incompatible_assignment_rec, lowest_common_parents, \
    nodetypestr, polymorphic_t, singletype, unboxable, typestr
from virtual import virtuals


class CPPNamer(object):
    def __init__(self, gx, mv):
        self.gx = gx
        self.class_names = [cl.ident for cl in self.gx.allclasses]
        self.cpp_keywords = self.gx.cpp_keywords
        self.ss_prefix = self.gx.ss_prefix
        self.name_by_type = {
            str: self.name_str,
            Class: self.name_class,
            Function: self.name_function,
            Variable: self.name_variable,
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
class GenerateVisitor(ASTVisitor):
    def __init__(self, gx, module):
        self.gx = gx
        self.output_base = module.filename[:-3]
        self.out = file(self.output_base + '.cpp', 'w')
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

    def cpp_name(self, obj):
        return self.namer.name(obj)

    def insert_consts(self, declare):  # XXX ugly
        if not self.consts:
            return
        self.filling_consts = True

        if declare:
            suffix = '.hpp'
        else:
            suffix = '.cpp'

        lines = file(self.output_base + suffix, 'r').readlines()
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
                        ts = nodetypestr(self.gx, node, inode(self.gx, node).parent, mv=self.mv)
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
                todolist = todo.keys()
                todolist.sort()
                for number in todolist:
                    if self.mergeinh[todo[number]]:  # XXX
                        name = 'const_' + str(number)
                        self.start('    ' + name + ' = ')
                        if isinstance(todo[number], Const) and isinstance(todo[number].value, str) and len(todo[number].value) == 1:
                            self.append("__char_cache[%d];" % ord(todo[number].value))
                        else:
                            self.visit(todo[number], inode(self.gx, todo[number]).parent)
                        newlines2.append(self.line + ';\n')

                newlines2.append('\n')

        file(self.output_base + suffix, 'w').writelines(newlines2)
        self.filling_consts = False

    def insert_extras(self, suffix):
        lines = file(self.output_base + suffix, 'r').readlines()
        newlines = []
        for line in lines:
            newlines.append(line)
            if suffix == '.cpp' and line.startswith('#include'):
                newlines.extend(self.include_files())
            elif suffix == '.hpp' and line.startswith('using namespace'):
                newlines.extend(self.fwd_class_refs())
        file(self.output_base + suffix, 'w').writelines(newlines)

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
        self.out = file(self.output_base + '.hpp', 'w')
        self.visit(self.module.ast, True)
        self.out.close()

    def output(self, text):
        print >>self.out, self.indentation + text

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
            print >>self.out, self.line + ';'

    def indent(self):
        self.indentation += 4 * ' '

    def deindent(self):
        self.indentation = self.indentation[:-4]

    def visitm(self, *args):
        func = None
        if args and isinstance(args[-1], (Function, Class)):
            func = args[-1]
        for arg in args[:-1]:
            if isinstance(arg, str):
                self.append(arg)
            else:
                self.visit(arg, func)

    def connector(self, node, func):
        if singletype(self.gx, node, Module):
            return '::'
        elif unboxable(self.gx, self.mergeinh[node]):
            return '.'
        else:
            return '->'

    def declare_defs(self, vars, declare):
        pairs = []
        for (name, var) in vars:
            if singletype(self.gx, var, Module) or var.invisible:
                continue
            ts = nodetypestr(self.gx, var, var.parent, mv=self.mv)
            if declare:
                if 'for_in_loop' in ts:  # XXX
                    continue
                ts = 'extern ' + ts
            if not var.name in ['__exception', '__exception2']:  # XXX
                pairs.append((ts, self.cpp_name(var)))
        return ''.join(self.group_declarations(pairs))

    def get_constant(self, node):
        parent = inode(self.gx, node).parent
        while isinstance(parent, Function) and parent.listcomp:  # XXX
            parent = parent.parent
        if isinstance(parent, Function) and (parent.inherited or not self.inhcpa(parent)):  # XXX
            return
        for other in self.consts:  # XXX use mapping
            if node.value == other.value:
                return self.consts[other]
        self.consts[node] = 'const_' + str(len(self.consts))
        return self.consts[node]

    def module_hpp(self, node):
        define = '_'.join(self.module.name_list).upper() + '_HPP'
        print >>self.out, '#ifndef __' + define
        print >>self.out, '#define __' + define + '\n'

        # --- namespaces
        print >>self.out, 'using namespace __shedskin__;'
        for n in self.module.name_list:
            print >>self.out, 'namespace __' + n + '__ {'
        print >>self.out

        # class declarations
        for child in node.node.getChildNodes():
            if isinstance(child, ClassNode):
                cl = def_class(self.gx, child.name, mv=self.mv)
                print >>self.out, 'class ' + self.cpp_name(cl) + ';'
        print >>self.out

        # --- lambda typedefs
        self.func_pointers()

        # globals
        defs = self.declare_defs(list(self.mv.globals.items()), declare=True)
        if defs:
            self.output(defs)
            print >>self.out

        # --- class definitions
        for child in node.node.getChildNodes():
            if isinstance(child, ClassNode):
                self.class_hpp(child)

        # --- defaults
        self.defaults(declare=True)

        # function declarations
        if self.module != self.gx.main_module:
            print >>self.out, 'void __init();'
        for child in node.node.getChildNodes():
            if isinstance(child, FunctionNode):
                func = self.mv.funcs[child.name]
                if self.inhcpa(func):
                    self.visitFunction(func.node, declare=True)
        print >>self.out

        if self.gx.extension_module:
            print >>self.out, 'extern "C" {'
            pyinit_func(self)
            print >>self.out, '}'

        for n in self.module.name_list:
            print >>self.out, '} // module namespace'

        self.rich_comparison()

        if self.gx.extension_module:
            convert_methods2(self.gx, self)

        print >>self.out, '#endif'

    def defaults(self, declare):
        if self.module.mv.defaults:
            extern = ['', 'extern '][declare]
            for default, (nr, func, func_def_nr) in self.module.mv.defaults.items():
                formal = func.formals[len(func.formals) - len(func.defaults) + func_def_nr]
                var = func.vars[formal]
                print >>self.out, extern + typestr(self.gx, self.mergeinh[var], func, mv=self.mv) + ' ' + ('default_%d;' % nr)
            print >>self.out

    def init_defaults(self, func):
        for default in func.defaults:
            if default in self.mv.defaults:
                nr, func, func_def_nr = self.mv.defaults[default]
                formal = func.formals[len(func.formals) - len(func.defaults) + func_def_nr]
                var = func.vars[formal]
                if self.mergeinh[var]:
                    ts = [t for t in self.mergeinh[default] if isinstance(t[0], Function)]
                    if not ts or [t for t in ts if called(t[0])]:
                        self.start('default_%d = ' % nr)
                        self.visit_conv(default, self.mergeinh[var], None)
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
            print >>self.out, 'namespace __shedskin__ { /* XXX */'
            for cl in cmp_cls:
                t = '__%s__::%s *' % (self.mv.module.ident, self.cpp_name(cl))
                print >>self.out, 'template<> inline __ss_int __cmp(%sa, %sb) {' % (t, t)
                print >>self.out, '    if (!a) return -1;'
                if '__eq__' in cl.funcs:
                    print >>self.out, '    if(a->__eq__(b)) return 0;'
                if '__lt__' in cl.funcs:
                    print >>self.out, '    return (a->__lt__(b))?-1:1;'
                elif '__gt__' in cl.funcs:
                    print >>self.out, '    return (a->__gt__(b))?1:-1;'
                else:
                    print >>self.out, '    return __cmp<void *>(a, b);'
                print >>self.out, '}'
            self.rich_compare(lt_cls, 'lt', 'gt')
            self.rich_compare(gt_cls, 'gt', 'lt')
            self.rich_compare(le_cls, 'le', 'ge')
            self.rich_compare(ge_cls, 'ge', 'le')
            print >>self.out, '}'

    def rich_compare(self, cls, msg, fallback_msg):
        for cl in cls:
            t = '__%s__::%s *' % (self.mv.module.ident, self.cpp_name(cl))
            print >>self.out, 'template<> inline __ss_bool __%s(%sa, %sb) {' % (msg, t, t)
            # print >>self.out, '    if (!a) return -1;' # XXX check
            print >>self.out, '    return b->__%s__(a);' % fallback_msg
            print >>self.out, '}'

    def module_cpp(self, node):
        print >>self.out, '#include "builtin.hpp"\n'

        # --- comments
        if node.doc:
            self.do_comment(node.doc)
            print >>self.out

        # --- namespace fun
        for n in self.module.name_list:
            print >>self.out, 'namespace __' + n + '__ {'
        print >>self.out

        for child in node.node.getChildNodes():
            if isinstance(child, From) and child.modname != '__future__':
                module = self.gx.from_module[child]
                using = 'using ' + module.full_path() + '::'
                for (name, pseudonym) in child.names:
                    pseudonym = pseudonym or name
                    if name == '*':
                        for func in module.mv.funcs.values():
                            if func.cp:  # XXX
                                print >>self.out, using + self.cpp_name(func) + ';'
                        for cl in module.mv.classes.values():
                            print >>self.out, using + self.cpp_name(cl) + ';'
                    elif pseudonym not in self.module.mv.globals:
                        if name in module.mv.funcs:
                            func = module.mv.funcs[name]
                            if func.cp:
                                print >>self.out, using + self.cpp_name(func) + ';'
                        else:
                            print >>self.out, using + self.namer.nokeywords(name) + ';'
        print >>self.out

        # --- globals
        defs = self.declare_defs(list(self.mv.globals.items()), declare=False)
        if defs:
            self.output(defs)
            print >>self.out

        # --- defaults
        self.defaults(declare=False)

        # --- declarations
        self.listcomps = {}
        for (listcomp, lcfunc, func) in self.mv.listcomps:
            self.listcomps[listcomp] = (lcfunc, func)
        self.do_listcomps(True)
        self.do_lambdas(True)
        print >>self.out

        # --- definitions
        self.do_listcomps(False)
        self.do_lambdas(False)
        for child in node.node.getChildNodes():
            if isinstance(child, ClassNode):
                self.class_cpp(child)
            elif isinstance(child, FunctionNode):
                self.do_comments(child)
                self.visit(child)

        # --- __init
        self.output('void __init() {')
        self.indent()
        if self.module == self.gx.main_module and not self.gx.extension_module:
            self.output('__name__ = new str("__main__");\n')
        else:
            self.output('__name__ = new str("%s");\n' % self.module.ident)

        for child in node.node.getChildNodes():
            if isinstance(child, FunctionNode):
                self.init_defaults(child)
            elif isinstance(child, ClassNode):
                for child2 in child.code.getChildNodes():
                    if isinstance(child2, FunctionNode):
                        self.init_defaults(child2)
                if child.name in self.mv.classes:
                    cl = self.mv.classes[child.name]
                    self.output('cl_' + cl.ident + ' = new class_("%s");' % (cl.ident))
                    if cl.parent.static_nodes:
                        self.output('%s::__static__();' % self.cpp_name(cl))

            elif isinstance(child, Discard):
                self.visit_discard(child)

            elif isinstance(child, From) and child.modname != '__future__':
                module = self.gx.from_module[child]
                for (name, pseudonym) in child.names:
                    pseudonym = pseudonym or name
                    if name == '*':
                        for var in module.mv.globals.values():
                            if not var.invisible and not var.imported and not var.name.startswith('__') and var_types(self.gx, var):
                                self.start(self.namer.nokeywords(var.name) + ' = ' + module.full_path() + '::' + self.namer.nokeywords(var.name))
                                self.eol()
                    elif pseudonym in self.module.mv.globals and not [t for t in var_types(self.gx, self.module.mv.globals[pseudonym]) if isinstance(t[0], Module)]:
                        self.start(self.namer.nokeywords(pseudonym) + ' = ' + module.full_path() + '::' + self.namer.nokeywords(name))
                        self.eol()

            elif not isinstance(child, (ClassNode, FunctionNode)):
                self.do_comments(child)
                self.visit(child)

        self.deindent()
        self.output('}\n')

        # --- close namespace
        for n in self.module.name_list:
            print >>self.out, '} // module namespace'
        print >>self.out

        # --- c++ main/extension module setup
        if self.gx.extension_module:
            do_extmod(self.gx, self)
        if self.module == self.gx.main_module:
            self.do_main()

    def visit_discard(self, node, func=None):
        if isinstance(node.expr, Const) and node.expr.value is None:  # XXX merge with visitStmt
            pass
        elif isinstance(node.expr, Const) and type(node.expr.value) == str:
            self.do_comment(node.expr.value)
        else:
            self.start('')
            self.visit(node, func)
            self.eol()

    def visitModule(self, node, declare=False):
        if declare:
            self.module_hpp(node)
        else:
            self.module_cpp(node)

    def do_main(self):
        modules = self.gx.modules.values()
        if any(module.builtin and module.ident == 'sys' for module in modules):
            print >>self.out, 'int main(int __ss_argc, char **__ss_argv) {'
        else:
            print >>self.out, 'int main(int, char **) {'
        self.do_init_modules()
        print >>self.out, '    __shedskin__::__start(__%s__::__init);' % self.module.ident
        print >>self.out, '}'

    def do_init_modules(self):
        print >>self.out, '    __shedskin__::__init();'
        for module in sorted(self.gx.modules.values(), key=lambda x: x.import_order):
            if module != self.gx.main_module and module.ident != 'builtin':
                if module.ident == 'sys':
                    if self.gx.extension_module:
                        print >>self.out, '    __sys__::__init(0, 0);'
                    else:
                        print >>self.out, '    __sys__::__init(__ss_argc, __ss_argv);'
                else:
                    print >>self.out, '    ' + module.full_path() + '::__init();'

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

    def visitContinue(self, node, func=None):
        self.output('continue;')

    def visitWith(self, node, func=None):
        self.start()
        if node.vars:
            self.visitm('WITH_VAR(', node.expr, ',', node.vars, func)
        else:
            self.visitm('WITH(', node.expr, func)
        self.append(',%d)' % self.with_count)
        self.with_count += 1
        print >>self.out, self.line
        self.indent()
        self.visit(node.body, func)
        self.deindent()
        self.output('END_WITH')

    def visitWhile(self, node, func=None):
        print >>self.out
        if node.else_:
            self.output('%s = 0;' % self.mv.tempcount[node.else_])

        self.start('while (')
        self.bool_test(node.test, func)
        self.append(') {')
        print >>self.out, self.line
        self.indent()
        self.gx.loopstack.append(node)
        self.visit(node.body, func)
        self.gx.loopstack.pop()
        self.deindent()
        self.output('}')

        if node.else_:
            self.output('if (!%s) {' % self.mv.tempcount[node.else_])
            self.indent()
            self.visit(node.else_, func)
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
            print >>self.out, self.line + ' {'
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
                ts = nodetypestr(self.gx, cl.funcs['__iter__'].retnode.thing, mv=self.mv)
                if ts.startswith('__iter<'):
                    ts = ts[ts.find('<') + 1:ts.find('>')]
                    clnames = ['pyiter<%s>' % ts]  # XXX use iterable interface
            if '__call__' in cl.funcs:
                callfunc = cl.funcs['__call__']
                r_typestr = nodetypestr(self.gx, callfunc.retnode.thing, mv=self.mv).strip()
                nargs = len(callfunc.formals) - 1
                argtypes = [nodetypestr(self.gx, callfunc.vars[callfunc.formals[i + 1]], mv=self.mv).strip() for i in range(nargs)]
                clnames = ['pycall%d<%s,%s>' % (nargs, r_typestr, ','.join(argtypes))]
        self.output('class ' + self.cpp_name(cl) + ' : ' + ', '.join(['public ' + clname for clname in clnames]) + ' {')
        self.do_comment(node.doc)
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
        virtuals(self, cl, True)
        for func in cl.funcs.values():
            if func.node and not (func.ident == '__init__' and func.inherited):
                self.visitFunction(func.node, cl, True)
        self.copy_methods(cl, True)
        if self.gx.extension_module:
            convert_methods(self.gx, self, cl, True)

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
        virtuals(self, cl, False)
        for func in cl.funcs.values():
            if func.node and not (func.ident == '__init__' and func.inherited):
                self.visitFunction(func.node, cl, False)
        self.copy_methods(cl, False)

        # --- class variable declarations
        if cl.parent.vars:  # XXX merge with visitModule
            for var in cl.parent.vars.values():
                if var in self.gx.merged_inh and self.gx.merged_inh[var]:
                    self.start(nodetypestr(self.gx, var, cl.parent, mv=self.mv) + cl.ident + '::' + self.cpp_name(var))
                    self.eol()
            print >>self.out

        # --- static init
        if cl.parent.static_nodes:
            self.output('void %s::__static__() {' % self.cpp_name(cl))
            self.indent()
            for node in cl.parent.static_nodes:
                self.visit(node, cl.parent)
            self.deindent()
            self.output('}')
            print >>self.out

    def class_variables(self, cl):
        # --- class variables
        if cl.parent.vars:
            for var in cl.parent.vars.values():
                if var in self.gx.merged_inh and self.gx.merged_inh[var]:
                    self.output('static ' + nodetypestr(self.gx, var, cl.parent, mv=self.mv) + self.cpp_name(var) + ';')
            print >>self.out

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
                self.output(nodetypestr(self.gx, var, cl, mv=self.mv) + self.cpp_name(var) + ';')

        if [v for v in cl.vars if not v.startswith('__')]:
            print >>self.out

    def nothing(self, types):
        if def_class(self.gx, 'complex') in (t[0] for t in types):
            return 'mcomplex(0.0, 0.0)'
        elif def_class(self.gx, 'bool_') in (t[0] for t in types):
            return 'False'
        else:
            return '0'

    def inhcpa(self, func):
        return called(func) or (func in self.gx.inheritance_relations and [1 for f in self.gx.inheritance_relations[func] if called(f)])

    def visitSlice(self, node, func=None):
        if node.flags == 'OP_DELETE':
            self.start()
            self.visit(inode(self.gx, node.expr).fakefunc, func)
            self.eol()
        else:
            self.visit(inode(self.gx, node.expr).fakefunc, func)

    def visitLambda(self, node, parent=None):
        self.append(self.mv.lambdaname[node])

    def subtypes(self, types, varname):
        subtypes = set()
        for t in types:
            if isinstance(t[0], Class):
                var = t[0].vars.get(varname)
                if var and (var, t[1], 0) in self.gx.cnode:  # XXX yeah?
                    subtypes.update(self.gx.cnode[var, t[1], 0].types())
        return subtypes

    def bin_tuple(self, types):
        for t in types:
            if isinstance(t[0], Class) and t[0].ident == 'tuple2':
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
        ts = typestr(self.gx, argtypes, mv=self.mv)
        if ts.startswith('pyseq') or ts.startswith('pyiter'):  # XXX
            argtypes = self.gx.merged_inh[node]
        ts = typestr(self.gx, argtypes, mv=self.mv)
        self.append('(new ' + ts[:-2] + '(')
        return argtypes

    def visitDict(self, node, func=None, argtypes=None):
        argtypes = self.instance_new(node, argtypes)
        if node.items:
            self.append(str(len(node.items)) + ', ')
        ts_key = typestr(self.gx, self.subtypes(argtypes, 'unit'), mv=self.mv)
        ts_value = typestr(self.gx, self.subtypes(argtypes, 'value'), mv=self.mv)
        for (key, value) in node.items:
            self.visitm('(new tuple2<%s, %s>(2,' % (ts_key, ts_value), func)
            type_child = self.subtypes(argtypes, 'unit')
            self.visit_conv(key, type_child, func)
            self.append(',')
            type_child = self.subtypes(argtypes, 'value')
            self.visit_conv(value, type_child, func)
            self.append('))')
            if (key, value) != node.items[-1]:
                self.append(',')
        self.append('))')

    def visit_tuple_list(self, node, func=None, argtypes=None):
        if isinstance(func, Class):  # XXX
            func = None
        argtypes = self.instance_new(node, argtypes)
        children = node.getChildNodes()
        if children:
            self.append(str(len(children)) + ',')
        if len(children) >= 2 and self.bin_tuple(argtypes):  # XXX >=2?
            type_child = self.subtypes(argtypes, 'first')
            self.visit_conv(children[0], type_child, func)
            self.append(',')
            type_child = self.subtypes(argtypes, 'second')
            self.visit_conv(children[1], type_child, func)
        else:
            for child in children:
                type_child = self.subtypes(argtypes, 'unit')
                self.visit_conv(child, type_child, func)
                if child != children[-1]:
                    self.append(',')
        self.append('))')

    def visitTuple(self, node, func=None, argtypes=None):
        if len(node.nodes) > 2:
            types = set()
            for child in node.nodes:
                types.update(self.mergeinh[child])
            typestr(self.gx, types, node=child, tuple_check=True, mv=self.mv)
        self.visit_tuple_list(node, func, argtypes)

    def visitList(self, node, func=None, argtypes=None):
        self.visit_tuple_list(node, func, argtypes)

    def visitAssert(self, node, func=None):
        self.start('ASSERT(')
        self.visitm(node.test, ', ', func)
        if len(node.getChildNodes()) > 1:
            self.visit(node.getChildNodes()[1], func)
        else:
            self.append('0')
        self.eol(')')

    def visitRaise(self, node, func=None):
        cl = None  # XXX sep func
        t = [t[0] for t in self.mergeinh[node.expr1]]
        if len(t) == 1:
            cl = t[0]
        self.start('throw (')

        # --- raise class [, constructor args]
        if isinstance(node.expr1, Name) and not lookup_var(node.expr1.name, func, mv=self.mv):  # XXX lookup_class
            self.append('new %s(' % node.expr1.name)
            if node.expr2:
                if isinstance(node.expr2, Tuple) and node.expr2.nodes:
                    for n in node.expr2.nodes:
                        self.visit(n, func)
                        if n != node.expr2.nodes[-1]:
                            self.append(', ')  # XXX visitcomma(nodes)
                else:
                    self.visit(node.expr2, func)
            self.append(')')

        # --- raise instance
        elif isinstance(cl, Class) and cl.mv.module.ident == 'builtin' and not [a for a in cl.ancestors_upto(None) if a.ident == 'BaseException']:
            self.append('new Exception()')
        else:
            self.visit(node.expr1, func)
        self.eol(')')

    def visitTryExcept(self, node, func=None):
        # try
        self.start('try {')
        print >>self.out, self.line
        self.indent()
        if node.else_:
            self.output('%s = 0;' % self.mv.tempcount[node.else_])
        self.visit(node.body, func)
        if node.else_:
            self.output('%s = 1;' % self.mv.tempcount[node.else_])
        self.deindent()
        self.start('}')

        # except
        for handler in node.handlers:
            if isinstance(handler[0], Tuple):
                pairs = [(n, handler[1], handler[2]) for n in handler[0].nodes]
            else:
                pairs = [(handler[0], handler[1], handler[2])]

            for (h0, h1, h2) in pairs:
                if isinstance(h0, Name) and h0.name in ['int', 'float', 'str', 'class']:
                    continue  # XXX lookup_class
                elif h0:
                    cl = lookup_class(h0, self.mv)
                    if cl.mv.module.builtin and cl.ident in ['KeyboardInterrupt', 'FloatingPointError', 'OverflowError', 'ZeroDivisionError', 'SystemExit']:
                        error("system '%s' is not caught" % cl.ident, self.gx, h0, warning=True, mv=self.mv)
                    arg = self.namer.namespace_class(cl) + ' *'
                else:
                    arg = 'Exception *'

                if h1:
                    arg += h1.name

                self.append(' catch (%s) {' % arg)
                print >>self.out, self.line
                self.indent()
                self.visit(h2, func)
                self.deindent()
                self.start('}')
        print >>self.out, self.line

        # else
        if node.else_:
            self.output('if(%s) { // else' % self.mv.tempcount[node.else_])
            self.indent()
            self.visit(node.else_, func)
            self.deindent()
            self.output('}')

    def do_fastfor(self, node, qual, quals, iter, func, genexpr):
        if len(qual.list.args) == 3 and not is_literal(qual.list.args[2]):
            for arg in qual.list.args:  # XXX simplify
                if arg in self.mv.tempcount:
                    self.start()
                    self.visitm(self.mv.tempcount[arg], ' = ', arg, func)
                    self.eol()
        self.fastfor(qual, iter, func)
        self.forbody(node, quals, iter, func, False, genexpr)

    def visit_temp(self, node, func):  # XXX generalize?
        if node in self.mv.tempcount:
            self.append(self.mv.tempcount[node])
        else:
            self.visit(node, func)

    def fastfor(self, node, assname, func=None):
        # --- for i in range(..) -> for( i=l, u=expr; i < u; i++ ) ..
        ivar, evar = self.mv.tempcount[node.assign], self.mv.tempcount[node.list]
        self.start('FAST_FOR(%s,' % assname)

        if len(node.list.args) == 1:
            self.append('0,')
            self.visit_temp(node.list.args[0], func)
            self.append(',')
        else:
            self.visit_temp(node.list.args[0], func)
            self.append(',')
            self.visit_temp(node.list.args[1], func)
            self.append(',')

        if len(node.list.args) != 3:
            self.append('1')
        else:
            self.visit_temp(node.list.args[2], func)
        self.append(',%s,%s)' % (ivar[2:], evar[2:]))
        print >>self.out, self.line

    def fastenum(self, node):
        return is_enum(node) and self.only_classes(node.list.args[0], ('tuple', 'list'))

    def fastzip2(self, node):
        names = ('tuple', 'list')
        return is_zip2(node) and self.only_classes(node.list.args[0], names) and self.only_classes(node.list.args[1], names)

    def fastdictiter(self, node):
        return isinstance(node.list, CallFunc) and isinstance(node.assign, (AssList, AssTuple)) and self.only_classes(node.list.node, ('dict',)) and isinstance(node.list.node, Getattr) and node.list.node.attrname == 'iteritems'

    def only_classes(self, node, names):
        if node not in self.mergeinh:
            return False
        classes = [def_class(self.gx, name, mv=self.mv) for name in names] + [def_class(self.gx, 'none')]
        return not [t for t in self.mergeinh[node] if t[0] not in classes]

    def visitFor(self, node, func=None):
        if isinstance(node.assign, AssName):
            assname = node.assign.name
        elif isinstance(node.assign, AssAttr):
            self.start('')
            self.visitAssAttr(node.assign, func)
            assname = self.line.strip()  # XXX yuck
        else:
            assname = self.mv.tempcount[node.assign]
        assname = self.cpp_name(assname)
        print >>self.out
        if node.else_:
            self.output('%s = 0;' % self.mv.tempcount[node.else_])
        if is_fastfor(node):
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
            self.visit(node.list, func)
            print >>self.out, self.line + ',' + tail + ')'
            self.forbody(node, None, assname, func, False, False)
        print >>self.out

    def do_fastzip2(self, node, func, genexpr):
        self.start('FOR_IN_ZIP(')
        left, right = node.assign.nodes
        self.do_fastzip2_one(left, func)
        self.do_fastzip2_one(right, func)
        self.visitm(node.list.args[0], ',', node.list.args[1], ',', func)
        tail1 = self.mv.tempcount[(node, 2)][2:] + ',' + self.mv.tempcount[(node, 3)][2:] + ','
        tail2 = self.mv.tempcount[(node.list)][2:] + ',' + self.mv.tempcount[(node, 4)][2:]
        print >>self.out, self.line + tail1 + tail2 + ')'
        self.indent()
        if isinstance(left, (AssTuple, AssList)):
            self.tuple_assign(left, self.mv.tempcount[left], func)
        if isinstance(right, (AssTuple, AssList)):
            self.tuple_assign(right, self.mv.tempcount[right], func)

    def do_fastzip2_one(self, node, func):
        if isinstance(node, (AssTuple, AssList)):
            self.append(self.mv.tempcount[node])
        else:
            self.visit(node, func)
        self.append(',')

    def do_fastenum(self, node, func, genexpr):
        self.start('FOR_IN_ENUM(')
        left, right = node.assign.nodes
        self.do_fastzip2_one(right, func)
        self.visit(node.list.args[0], func)
        tail = self.mv.tempcount[(node, 2)][2:] + ',' + self.mv.tempcount[node.list][2:]
        print >>self.out, self.line + ',' + tail + ')'
        self.indent()
        self.start()
        self.visitm(left, ' = ' + self.mv.tempcount[node.list], func)
        self.eol()
        if isinstance(right, (AssTuple, AssList)):
            self.tuple_assign(right, self.mv.tempcount[right], func)

    def do_fastdictiter(self, node, func, genexpr):
        self.start('FOR_IN_DICT(')
        left, right = node.assign.nodes
        tail = self.mv.tempcount[node, 7][2:] + ',' + self.mv.tempcount[node, 6][2:] + ',' + self.mv.tempcount[node.list][2:]
        self.visit(node.list.node.expr, func)
        print >>self.out, self.line + ',' + tail + ')'
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
        if isinstance(left, (AssTuple, AssList)):
            self.tuple_assign(left, self.mv.tempcount[left], func)
        if isinstance(right, (AssTuple, AssList)):
            self.tuple_assign(right, self.mv.tempcount[right], func)

    def forin_preftail(self, node):
        tail = self.mv.tempcount[node][2:] + ',' + self.mv.tempcount[node.list][2:]
        tail += ',' + self.mv.tempcount[(node, 5)][2:]
        return '', tail

    def forbody(self, node, quals, iter, func, skip, genexpr):
        if quals is not None:
            self.listcompfor_body(node, quals, iter, func, False, genexpr)
            return
        if not skip:
            self.indent()
            if isinstance(node.assign, (AssTuple, AssList)):
                self.tuple_assign(node.assign, self.mv.tempcount[node.assign], func)
        self.gx.loopstack.append(node)
        self.visit(node.body, func)
        self.gx.loopstack.pop()
        self.deindent()
        self.output('END_FOR')
        if node.else_:
            self.output('if (!%s) {' % self.mv.tempcount[node.else_])
            self.indent()
            self.visit(node.else_, func)
            self.deindent()
            self.output('}')

    def func_pointers(self):
        for func in self.mv.lambdas.values():
            argtypes = [nodetypestr(self.gx, func.vars[formal], func, mv=self.mv).rstrip() for formal in func.formals]
            if func.largs is not None:
                argtypes = argtypes[:func.largs]
            rettype = nodetypestr(self.gx, func.retnode.thing, func, mv=self.mv)
            print >>self.out, 'typedef %s(*lambda%d)(' % (rettype, func.lambdanr) + ', '.join(argtypes) + ');'
        print >>self.out

    # --- function/method header
    def func_header(self, func, declare, is_init=False):
        method = isinstance(func.parent, Class)
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
            header += nodetypestr(self.gx, func.retnode.thing, func, mv=self.mv)  # XXX mult
        else:
            header += 'void '

        ftypes = [nodetypestr(self.gx, func.vars[f], func, mv=self.mv) for f in formals]

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
        if declare and isinstance(func.parent, Class) and func.ident in func.parent.staticmethods:
            header = 'static ' + header
        if is_init and not formaldecs:
            formaldecs = ['int __ss_init']
        if func.ident.startswith('__lambda'):  # XXX
            header = 'static inline ' + header

        # --- output
        self.append(header + '(' + ', '.join(formaldecs) + ')')
        if is_init:
            print >>self.out, self.line + ' {'
        elif declare:
            self.eol()
        else:
            print >>self.out, self.line + ' {'
            self.indent()
            if not declare and func.doc:
                self.do_comment(func.doc)
            for cast in casts:
                self.output(cast)
            self.deindent()

    def visitFunction(self, node, parent=None, declare=False):
        # locate right func instance
        if parent and isinstance(parent, Class):
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
            if func.lambdanr is None and not repr(node.code).startswith("Stmt([Raise(CallFunc(Name('NotImplementedError')"):
                error(repr(func) + ' not called!', self.gx, node, warning=True, mv=self.mv)
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
        self.visit(node.code, func)
        if func.fakeret:
            self.visit(func.fakeret, func)

        # --- add Return(None) (sort of) if function doesn't already end with a Return
        if node.getChildNodes():
            lastnode = node.getChildNodes()[-1]
            if not func.ident == '__init__' and not func.fakeret and not isinstance(lastnode, Return) and not (isinstance(lastnode, Stmt) and isinstance(lastnode.nodes[-1], Return)):  # XXX use Stmt in moduleVisitor
                self.output('return %s;' % self.nothing(self.mergeinh[func.retnode.thing]))

        self.deindent()
        self.output('}\n')

    def generator_ident(self, func):  # XXX merge?
        if func.parent:
            return func.parent.ident + '_' + func.ident
        return func.ident

    def generator_class(self, func):
        ident = self.generator_ident(func)
        self.output('class __gen_%s : public %s {' % (ident, nodetypestr(self.gx, func.retnode.thing, func, mv=self.mv)[:-2]))
        self.output('public:')
        self.indent()
        pairs = [(nodetypestr(self.gx, func.vars[f], func, mv=self.mv), self.cpp_name(func.vars[f])) for f in func.vars]
        self.output(self.indentation.join(self.group_declarations(pairs)))
        self.output('int __last_yield;\n')

        args = []
        for f in func.formals:
            args.append(nodetypestr(self.gx, func.vars[f], func, mv=self.mv) + self.cpp_name(func.vars[f]))
        self.output(('__gen_%s(' % ident) + ','.join(args) + ') {')
        self.indent()
        for f in func.formals:
            self.output('this->%s = %s;' % (self.cpp_name(func.vars[f]), self.cpp_name(func.vars[f])))
        for fake_unpack in func.expand_args.values():
            self.visit(fake_unpack, func)
        self.output('__last_yield = -1;')
        self.deindent()
        self.output('}\n')

        self.output('%s __get_next() {' % nodetypestr(self.gx, func.retnode.thing, func, mv=self.mv)[7:-3])
        self.indent()
        self.output('switch(__last_yield) {')
        self.indent()
        for (i, n) in enumerate(func.yieldNodes):
            self.output('case %d: goto __after_yield_%d;' % (i, i))
        self.output('default: break;')
        self.deindent()
        self.output('}')

        for child in func.node.code.getChildNodes():
            if isinstance(child, Discard):
                self.visit_discard(child, func)
            else:
                self.visit(child, func)

        self.output('__stop_iteration = true;')
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

    def visitYield(self, node, func):
        self.output('__last_yield = %d;' % func.yieldNodes.index(node))
        self.start('__result = ')
        self.visit_conv(node.value, self.mergeinh[func.yieldnode.thing], func)
        self.eol()
        self.output('return __result;')
        self.output('__after_yield_%d:;' % func.yieldNodes.index(node))
        self.start()

    def visitNot(self, node, func=None):
        self.append('__NOT(')
        self.bool_test(node.expr, func)
        self.append(')')

    def visitBackquote(self, node, func=None):
        self.visitm('repr(', inode(self.gx, node.expr).fakefunc.node.expr, ')', func)

    def visitIf(self, node, func=None):
        for test in node.tests:
            self.start()
            if test != node.tests[0]:
                self.append('else ')
            self.append('if (')
            self.bool_test(test[0], func)
            print >>self.out, self.line + ') {'
            self.indent()
            self.visit(test[1], func)
            self.deindent()
            self.output('}')

        if node.else_:
            self.output('else {')
            self.indent()
            self.visit(node.else_, func)
            self.deindent()
            self.output('}')

    def visitIfExp(self, node, func=None):
        types = self.mergeinh[node]
        self.append('((')
        self.bool_test(node.test, func)
        self.append(')?(')
        self.visit_conv(node.then, types, func)
        self.append('):(')
        self.visit_conv(node.else_, types, func)
        self.append('))')

    def visit_conv(self, node, argtypes, func, check_temp=True):
        # convert/cast node to type it is assigned to
        actualtypes = self.mergeinh[node]
        if check_temp and node in self.mv.tempcount:  # XXX
            self.append(self.mv.tempcount[node])
        elif isinstance(node, Dict):
            self.visitDict(node, func, argtypes=argtypes)
        elif isinstance(node, Tuple):
            self.visitTuple(node, func, argtypes=argtypes)
        elif isinstance(node, List):
            self.visitList(node, func, argtypes=argtypes)
        elif isinstance(node, CallFunc) and isinstance(node.node, Name) and node.node.name in ('list', 'tuple', 'dict', 'set'):
            self.visitCallFunc(node, func, argtypes=argtypes)
        elif isinstance(node, Name) and node.name == 'None':
            self.visit(node, func)
        else:  # XXX messy
            cast = ''
            if actualtypes and argtypes and typestr(self.gx, actualtypes, mv=self.mv) != typestr(self.gx, argtypes, mv=self.mv) and typestr(self.gx, actualtypes, mv=self.mv) != 'str *':  # XXX
                if incompatible_assignment_rec(self.gx, actualtypes, argtypes):
                    error("incompatible types", self.gx, node, warning=True, mv=self.mv)
                else:
                    cast = '(' + typestr(self.gx, argtypes, mv=self.mv).strip() + ')'
                    if cast == '(complex)':
                        cast = 'mcomplex'
            if cast:
                self.append('(' + cast + '(')
            self.visit(node, func)
            if cast:
                self.append('))')

    def visitBreak(self, node, func=None):
        if self.gx.loopstack[-1].else_ in self.mv.tempcount:
            self.output('%s = 1;' % self.mv.tempcount[self.gx.loopstack[-1].else_])
        self.output('break;')

    def visitStmt(self, node, func=None):
        for b in node.nodes:
            if isinstance(b, Discard):
                self.visit_discard(b, func)
            else:
                self.visit(b, func)

    def visitOr(self, node, func=None):
        self.visit_and_or(node, node.nodes, '__OR', 'or', func)

    def visitAnd(self, node, func=None):
        self.visit_and_or(node, node.nodes,  '__AND', 'and', func)

    def visit_and_or(self, node, nodes, op, mix, func=None):
        if node in self.gx.bool_test_only:
            self.append('(')
            for n in nodes:
                self.bool_test(n, func)
                if n != node.nodes[-1]:
                    self.append(' ' + mix + ' ')
            self.append(')')
        else:
            child = nodes[0]
            if len(nodes) > 1:
                self.append(op + '(')
            self.visit_conv(child, self.mergeinh[node], func, check_temp=False)
            if len(nodes) > 1:
                self.append(', ')
                self.visit_and_or(node, nodes[1:], op, mix, func)
                self.append(', ' + self.mv.tempcount[child][2:] + ')')

    def visitCompare(self, node, func=None, wrapper=True):
        if not node in self.bool_wrapper:
            self.append('___bool(')
        self.done = set()
        mapping = {
            '>': ('__gt__', '>', None),
            '<': ('__lt__', '<', None),
            '!=': ('__ne__', '!=', None),
            '==': ('__eq__', '==', None),
            '<=': ('__le__', '<=', None),
            '>=': ('__ge__', '>=', None),
            'is': (None, '==', None),
            'is not': (None, '!=', None),
            'in': ('__contains__', None, None),
            'not in': ('__contains__', None, '!'),
        }
        left = node.expr
        for op, right in node.ops:
            msg, short, pre = mapping[op]
            if msg == '__contains__':
                self.do_compare(right, left, msg, short, func, pre)
            else:
                self.do_compare(left, right, msg, short, func, pre)
            if right != node.ops[-1][1]:
                self.append('&&')
            left = right
        if not node in self.bool_wrapper:
            self.append(')')

    def visitAugAssign(self, node, func=None):
        if isinstance(node.node, Subscript):
            self.start()
            if set([t[0].ident for t in self.mergeinh[node.node.expr] if isinstance(t[0], Class)]) in [set(['dict']), set(['defaultdict'])] and node.op == '+=':
                self.visitm(node.node.expr, '->__addtoitem__(', inode(self.gx, node).subs, ', ', node.expr, ')', func)
                self.eol()
                return

            self.visitm(inode(self.gx, node).temp1 + ' = ', node.node.expr, func)
            self.eol()
            self.start()
            self.visitm(inode(self.gx, node).temp2 + ' = ', inode(self.gx, node).subs, func)
            self.eol()
        self.visit(inode(self.gx, node).assignhop, func)

    def visitAdd(self, node, func=None):
        str_nodes = self.rec_string_addition(node)
        if str_nodes and len(str_nodes) > 2:
            self.append('__add_strs(%d, ' % len(str_nodes))
            for (i, node) in enumerate(str_nodes):
                self.visit(node, func)
                if i < len(str_nodes) - 1:
                    self.append(', ')
            self.append(')')
        else:
            self.visitBinary(node.left, node.right, aug_msg(node, 'add'), '+', func)

    def rec_string_addition(self, node):
        if isinstance(node, Add):
            l, r = self.rec_string_addition(node.left), self.rec_string_addition(node.right)
            if l and r:
                return l + r
        elif self.mergeinh[node] == set([(def_class(self.gx, 'str_'), 0)]):
            return [node]

    def visitBitand(self, node, func=None):
        self.visit_bitop(node, aug_msg(node, 'and'), '&', func)

    def visitBitor(self, node, func=None):
        self.visit_bitop(node, aug_msg(node, 'or'), '|', func)

    def visitBitxor(self, node, func=None):
        self.visit_bitop(node, aug_msg(node, 'xor'), '^', func)

    def visit_bitop(self, node, msg, inline, func=None):
        ltypes = self.mergeinh[node.nodes[0]]
        ul = unboxable(self.gx, ltypes)
        self.append('(')
        for child in node.nodes:
            self.append('(')
            self.visit(child, func)
            self.append(')')
            if child is not node.nodes[-1]:
                if ul:
                    self.append(inline)
                else:
                    self.append('->' + msg)
        self.append(')')

    def visitRightShift(self, node, func=None):
        self.visitBinary(node.left, node.right, aug_msg(node, 'rshift'), '>>', func)

    def visitLeftShift(self, node, func=None):
        self.visitBinary(node.left, node.right, aug_msg(node, 'lshift'), '<<', func)

    def visitMul(self, node, func=None):
        self.visitBinary(node.left, node.right, aug_msg(node, 'mul'), '*', func)

    def visitDiv(self, node, func=None):
        self.visitBinary(node.left, node.right, aug_msg(node, 'div'), '/', func)

    def visitInvert(self, node, func=None):  # XXX visitUnarySub merge, template function __invert?
        if unboxable(self.gx, self.mergeinh[node.expr]):
            self.visitm('~', node.expr, func)
        else:
            self.visitCallFunc(inode(self.gx, node.expr).fakefunc, func)

    def visitFloorDiv(self, node, func=None):
        self.visitBinary(node.left, node.right, aug_msg(node, 'floordiv'), '//', func)

    def visitPower(self, node, func=None):
        self.power(node.left, node.right, None, func)

    def power(self, left, right, mod, func=None):
        inttype = set([(def_class(self.gx, 'int_'), 0)])  # XXX merge
        if self.mergeinh[left] == inttype and self.mergeinh[right] == inttype:
            if not isinstance(right, Const):
                error("pow(int, int) returns int after compilation", self.gx, left, warning=True, mv=self.mv)
        if mod:
            self.visitm('__power(', left, ', ', right, ', ', mod, ')', func)
        else:
            self.visitm('__power(', left, ', ', right, ')', func)

    def visitSub(self, node, func=None):
        self.visitBinary(node.left, node.right, aug_msg(node, 'sub'), '-', func)

    def visitBinary(self, left, right, middle, inline, func=None):  # XXX cleanup please
        ltypes = self.mergeinh[left]
        rtypes = self.mergeinh[right]
        ul, ur = unboxable(self.gx, ltypes), unboxable(self.gx, rtypes)

        inttype = set([(def_class(self.gx, 'int_'), 0)])  # XXX new type?
        floattype = set([(def_class(self.gx, 'float_'), 0)])  # XXX new type?

        # --- inline mod/div
        # XXX C++ knows %, /, so we can overload?
        if (floattype.intersection(ltypes) or inttype.intersection(ltypes)):
            if inline in ['%'] or (inline in ['/'] and not (floattype.intersection(ltypes) or floattype.intersection(rtypes))):
                if not def_class(self.gx, 'complex') in (t[0] for t in rtypes):  # XXX
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
        if inline in ['+', '-'] and isinstance(right, Const) and isinstance(right.value, complex):
            if floattype.intersection(ltypes) or inttype.intersection(ltypes):
                self.append('mcomplex(')
                self.visit(left, func)
                self.append(', ' + {'+': '', '-': '-'}[inline] + str(right.value.imag) + ')')
                return

        # --- inline other
        if inline and ((ul and ur) or not middle or (isinstance(left, Name) and left.name == 'None') or (isinstance(right, Name) and right.name == 'None')):  # XXX not middle, cleanup?
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
            self.visit_conv(left, argtypes, func)
        else:
            self.visit(left, func)
        self.append(')')
        self.append(self.connector(left, func) + middle + '(')
        if middle == '__add__':
            self.visit_conv(right, argtypes, func)
        else:
            self.visit(right, func)
        self.append(')')

    def do_compare(self, left, right, middle, inline, func=None, prefix=''):
        ltypes = self.mergeinh[left]
        rtypes = self.mergeinh[right]
        argtypes = ltypes | rtypes
        ul, ur = unboxable(self.gx, ltypes), unboxable(self.gx, rtypes)

        # --- inline other
        if inline and ((ul and ur) or not middle or (isinstance(left, Name) and left.name == 'None') or (isinstance(right, Name) and right.name == 'None')):  # XXX not middle, cleanup?
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
            self.visit_conv(node, argtypes, func)

    def visitUnarySub(self, node, func=None):
        self.visitm('(', func)
        if unboxable(self.gx, self.mergeinh[node.expr]):
            self.visitm('-', node.expr, func)
        else:
            self.visitCallFunc(inode(self.gx, node.expr).fakefunc, func)
        self.visitm(')', func)

    def visitUnaryAdd(self, node, func=None):
        self.visitm('(', func)
        if unboxable(self.gx, self.mergeinh[node.expr]):
            self.visitm('+', node.expr, func)
        else:
            self.visitCallFunc(inode(self.gx, node.expr).fakefunc, func)
        self.visitm(')', func)

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
                if isinstance(arg, Keyword):
                    positions.append(formal_pos[arg.name])
                else:
                    positions.append(i)

            if positions:
                self.append(str(reduce(lambda a, b: a | b, ((1 << x) for x in positions))) + ', ')
            else:
                self.append('0, ')

    def visitCallFunc(self, node, func=None, argtypes=None):
        objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analyze_callfunc(self.gx, node, merge=self.gx.merged_inh)
        funcs = callfunc_targets(self.gx, node, self.gx.merged_inh)

        if self.library_func(funcs, 're', None, 'findall') or \
                self.library_func(funcs, 're', 're_object', 'findall'):
            error("'findall' does not work with groups (use 'finditer' instead)", self.gx, node, warning=True, mv=self.mv)
        if self.library_func(funcs, 'socket', 'socket', 'settimeout') or \
                self.library_func(funcs, 'socket', 'socket', 'gettimeout'):
            error("socket.set/gettimeout do not accept/return None", self.gx, node, warning=True, mv=self.mv)
        if self.library_func(funcs, 'builtin', None, 'map') and len(node.args) > 2:
            error("default fillvalue for 'map' becomes 0 for integers", self.gx, node, warning=True, mv=self.mv)
        if self.library_func(funcs, 'itertools', None, 'izip_longest'):
            error("default fillvalue for 'izip_longest' becomes 0 for integers", self.gx, node, warning=True, mv=self.mv)
        if self.library_func(funcs, 'struct', None, 'unpack'):
            error("struct.unpack should be used as follows: 'a, .. = struct.unpack(..)'", self.gx, node, warning=True, mv=self.mv)
        if self.library_func(funcs, 'array', 'array', '__init__'):
            if not node.args or not isinstance(node.args[0], Const) or node.args[0].value not in 'cbBhHiIlLfd':
                error("non-constant or unsupported type code", self.gx, node, warning=True, mv=self.mv)
        if self.library_func(funcs, 'builtin', None, 'id'):
            if struct.calcsize("P") == 8 and struct.calcsize('i') == 4 and not self.gx.longlong:
                error("return value of 'id' does not fit in 32-bit integer (try shedskin -l)", self.gx, node, warning=True, mv=self.mv)

        nrargs = len(node.args)
        if isinstance(func, Function) and func.largs:
            nrargs = func.largs

        # --- target expression
        if node.node in self.mergeinh and [t for t in self.mergeinh[node.node] if isinstance(t[0], Function)]:  # anonymous function
            self.visitm(node.node, '(', func)

        elif constructor:
            ts = self.namer.nokeywords(nodetypestr(self.gx, node, func, mv=self.mv))
            if ts == 'complex ':
                self.append('mcomplex(')
                constructor = False  # XXX
            else:
                if argtypes is not None:  # XXX merge instance_new
                    ts = typestr(self.gx, argtypes, mv=self.mv)
                    if ts.startswith('pyseq') or ts.startswith('pyiter'):  # XXX
                        argtypes = self.gx.merged_inh[node]
                        ts = typestr(self.gx, argtypes, mv=self.mv)
                self.append('(new ' + ts[:-2] + '(')
            if funcs and len(funcs[0].formals) == 1 and not funcs[0].mv.module.builtin:
                self.append('1')  # don't call default constructor

        elif parent_constr:
            cl = lookup_class(node.node.expr, self.mv)
            self.append(self.namer.namespace_class(cl) + '::' + node.node.attrname + '(')

        elif direct_call:  # XXX no namespace (e.g., math.pow), check nr of args
            if ident == 'float' and node.args and self.mergeinh[node.args[0]] == set([(def_class(self.gx, 'float_'), 0)]):
                self.visit(node.args[0], func)
                return
            if ident in ['abs', 'int', 'float', 'str', 'dict', 'tuple', 'list', 'type', 'cmp', 'sum', 'zip']:
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
            elif ident == 'isinstance':
                self.append('True')
                return
            else:
                if isinstance(node.node, Name):
                    if isinstance(func, Function) and isinstance(func.parent, Class) and ident in func.parent.funcs:  # masked by method
                        self.append(funcs[0].mv.module.full_path() + '::')
                    self.append(self.cpp_name(funcs[0]))
                else:
                    self.visit(node.node)
                self.append('(')

        elif method_call:
            for cl, _ in self.mergeinh[objexpr]:
                if isinstance(cl, Class) and cl.ident != 'none' and ident not in cl.funcs:
                    conv = {'int_': 'int', 'float_': 'float', 'str_': 'str', 'class_': 'class', 'none': 'none'}
                    clname = conv.get(cl.ident, cl.ident)
                    error("class '%s' has no method '%s'" % (clname, ident), self.gx, node, warning=True, mv=self.mv)
                if isinstance(cl, Class) and ident in cl.staticmethods:
                    error("staticmethod '%s' called without using class name" % ident, self.gx, node, warning=True, mv=self.mv)
                    return

            # tuple2.__getitem -> __getfirst__/__getsecond
            if ident == '__getitem__' and isinstance(node.args[0], Const) and node.args[0].value in (0, 1) and self.only_classes(objexpr, ('tuple2',)):
                self.visit(node.node.expr, func)
                self.append('->%s()' % ['__getfirst__', '__getsecond__'][node.args[0].value])
                return

            if ident == '__call__':
                self.visitm(node.node, '->__call__(', func)
            elif ident == 'is_integer' and (def_class(self.gx, 'float_'), 0) in self.mergeinh[node.node.expr]:
                self.visitm('__ss_is_integer(', node.node.expr, ')', func)
                return
            else:
                self.visitm(node.node, '(', func)

        else:
            if ident:
                error("unresolved call to '" + ident + "'", self.gx, node, mv=self.mv, warning=True)
            else:
                error("unresolved call (possibly caused by method passing, which is currently not allowed)", self.gx, node, mv=self.mv, warning=True)
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
            is_func = bool([1 for t in self.mergeinh[node] if isinstance(t[0], Function)])
            self.append(('', '!=NULL')[is_func] + ')')  # XXX
        else:
            self.bool_wrapper[node] = True
            self.visit(node, func)

    def visit_callfunc_args(self, funcs, node, func):
        objexpr, ident, direct_call, method_call, constructor, parent_constr, anon_func = analyze_callfunc(self.gx, node, merge=self.gx.merged_inh)
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
                error('calling functions with different numbers of arguments', self.gx, node, warning=True, mv=self.mv)
                self.append(')')
                return

        if target.inherited_from:
            target = target.inherited_from

        pairs, rest, err = connect_actual_formal(self.gx, node, target, parent_constr, merge=self.mergeinh)
        if err and not target.mv.module.builtin:  # XXX
            error('call with incorrect number of arguments', self.gx, node, warning=True, mv=self.mv)

        if isinstance(func, Function) and func.lambdawrapper:
            rest = func.largs

        if target.node.varargs:
            self.append('%d' % rest)
            if rest or pairs:
                self.append(', ')

        double = False
        if ident in ['min', 'max']:
            for arg in node.args:
                if arg in self.mergeinh and (def_class(self.gx, 'float_'), 0) in self.mergeinh[arg]:
                    double = True

        self.add_args_arg(node, funcs)

        if isinstance(func, Function) and func.largs is not None:
            kw = [p for p in pairs if p[1].name.startswith('__kw_')]
            nonkw = [p for p in pairs if not p[1].name.startswith('__kw_')]
            pairs = kw + nonkw[:func.largs]

        for (arg, formal) in pairs:
            cast = False
            builtin_types = self.cast_to_builtin(arg, func, formal, target, method_call, objexpr)
            formal_types = builtin_types or self.mergeinh[formal]

            if double and self.mergeinh[arg] == set([(def_class(self.gx, 'int_'), 0)]):
                cast = True
                self.append('((double)(')
            elif castnull and isinstance(arg, Name) and arg.name == 'None':
                cast = True
                self.append('((void *)(')

            if (print_function or self.library_func(funcs, 'struct', None, 'pack')) and not formal.name.startswith('__kw_'):
                types = [t[0].ident for t in self.mergeinh[arg]]
                if 'float_' in types or 'int_' in types or 'bool_' in types or 'complex' in types:
                    cast = True
                    self.append('___box((')

            if arg in target.mv.defaults:
                if self.mergeinh[arg] == set([(def_class(self.gx, 'none'), 0)]):
                    self.append('NULL')
                elif target.mv.module == self.mv.module:
                    self.append('default_%d' % (target.mv.defaults[arg][0]))
                else:
                    self.append('%s::default_%d' % (target.mv.module.full_path(), target.mv.defaults[arg][0]))

            elif arg in self.consts:
                self.append(self.consts[arg])
            else:
                if constructor and ident in ['set', 'frozenset'] and nodetypestr(self.gx, arg, func, mv=self.mv) in ['list<void *> *', 'tuple<void *> *', 'pyiter<void *> *', 'pyseq<void *> *', 'pyset<void *>']:  # XXX
                    pass
                elif not builtin_types and target.mv.module.builtin:
                    self.visit(arg, func)
                else:
                    self.visit_conv(arg, formal_types, func)

            if cast:
                self.append('))')
            if (arg, formal) != pairs[-1]:
                self.append(', ')

        if constructor and ident == 'frozenset':
            if pairs:
                self.append(',')
            self.append('1')

    def cast_to_builtin(self, arg, func, formal, target, method_call, objexpr):
        # type inference cannot deduce all necessary casts to builtin formals
        vars = {'u': 'unit', 'v': 'value', 'o': None}
        if target.mv.module.builtin and method_call and formal.name in vars and target.parent.ident in ('list', 'dict', 'set'):
            subtypes = self.subtypes(self.mergeinh[objexpr], vars[formal.name])
            if nodetypestr(self.gx, arg, func, mv=self.mv) != typestr(self.gx, subtypes, mv=self.mv):
                return subtypes

    def cast_to_builtin2(self, arg, func, objexpr, msg, formal_nr):
        # shortcut for outside of visitCallFunc XXX merge with visitCallFunc?
        cls = [t[0] for t in self.mergeinh[objexpr] if isinstance(t[0], Class)]
        if cls:
            cl = cls.pop()
            if msg in cl.funcs:
                target = cl.funcs[msg]
                if formal_nr < len(target.formals):
                    formal = target.vars[target.formals[formal_nr]]
                    builtin_types = self.cast_to_builtin(arg, func, formal, target, True, objexpr)
                    if builtin_types:
                        return typestr(self.gx, builtin_types, mv=self.mv)

    def visitReturn(self, node, func=None):
        if func.isGenerator:
            self.output('__stop_iteration = true;')
            self.output('return __zero<%s>();' % nodetypestr(self.gx, func.retnode.thing, mv=self.mv)[7:-3])  # XXX meugh
            return
        self.start('return ')
        self.visit_conv(node.value, self.mergeinh[func.retnode.thing], func)
        self.eol()

    def tuple_assign(self, lvalue, rvalue, func):
        temp = self.mv.tempcount[lvalue]
        if isinstance(lvalue, tuple):
            nodes = lvalue
        else:
            nodes = lvalue.nodes

        # --- nested unpacking assignment: a, (b,c) = d, e
        if [item for item in nodes if not isinstance(item, AssName)]:
            self.start(temp + ' = ')
            if isinstance(rvalue, str):
                self.append(rvalue)
            else:
                self.visit(rvalue, func)
            self.eol()

            for i, item in enumerate(nodes):
                selector = self.get_selector(temp, item, i)
                if isinstance(item, AssName):
                    self.output('%s = %s;' % (item.name, selector))
                elif isinstance(item, (AssTuple, AssList)):  # recursion
                    self.tuple_assign(item, selector, func)
                elif isinstance(item, Subscript):
                    self.assign_pair(item, selector, func)
                elif isinstance(item, AssAttr):
                    self.assign_pair(item, selector, func)
                    self.eol(' = ' + selector)

        # --- non-nested unpacking assignment: a,b,c = d
        else:
            self.start()
            self.visitm(temp, ' = ', rvalue, func)
            self.eol()
            for i, item in enumerate(lvalue.nodes):
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
        if len(lvalue.subs) > 1:
            subs = inode(self.gx, lvalue.expr).faketuple
        else:
            subs = lvalue.subs[0]
        self.visitm(lvalue.expr, self.connector(lvalue.expr, func), '__setitem__(', subs, ', ', func)

    def struct_unpack_cpp(self, node, func):
        struct_unpack = self.gx.struct_unpack.get(node)
        if struct_unpack:
            sinfo, tvar, tvar_pos = struct_unpack
            self.start()
            self.visitm(tvar, ' = ', node.expr.args[1], func)
            self.eol()
            self.output('%s = 0;' % tvar_pos)
            hop = 0
            for (o, c, t, d) in sinfo:
                self.start()
                expr = "__struct__::unpack_%s('%c', '%c', %d, %s, &%s)" % (t, o, c, d, tvar, tvar_pos)
                if c == 'x' or (d == 0 and c != 's'):
                    self.visitm(expr, func)
                else:
                    n = list(node.nodes[0])[hop]
                    hop += 1
                    if isinstance(n, Subscript):  # XXX merge
                        self.subs_assign(n, func)
                        self.visitm(expr, ')', func)
                    elif isinstance(n, AssName):
                        self.visitm(n, ' = ', expr, func)
                    elif isinstance(n, AssAttr):
                        self.visitAssAttr(n, func)
                        self.visitm(' = ', expr, func)
                self.eol()
            return True
        return False

    def visitAssign(self, node, func=None):
        if self.struct_unpack_cpp(node, func):
            return

        # temp vars
        if len(node.nodes) > 1 or isinstance(node.expr, Tuple):
            if isinstance(node.expr, Tuple):
                if [n for n in node.nodes if isinstance(n, AssTuple)]:  # XXX a,b=d[i,j]=..?
                    for child in node.expr.nodes:
                        if not (child, 0, 0) in self.gx.cnode:  # (a,b) = (1,2): (1,2) never visited
                            continue
                        if not isinstance(child, Const) and not (isinstance(child, Name) and child.name == 'None'):
                            self.start(self.mv.tempcount[child] + ' = ')
                            self.visit(child, func)
                            self.eol()
            elif not isinstance(node.expr, Const) and not (isinstance(node.expr, Name) and node.expr.name == 'None'):
                self.start(self.mv.tempcount[node.expr] + ' = ')
                self.visit(node.expr, func)
                self.eol()

        # a = (b,c) = .. = expr
        for left in node.nodes:
            pairs = assign_rec(left, node.expr)

            for (lvalue, rvalue) in pairs:
                self.start('')  # XXX remove?

                # expr[expr] = expr
                if isinstance(lvalue, Subscript) and not isinstance(lvalue.subs[0], Sliceobj):
                    self.assign_pair(lvalue, rvalue, func)

                # expr.attr = expr
                elif isinstance(lvalue, AssAttr):
                    lcp = lowest_common_parents(polymorphic_t(self.gx, self.mergeinh[lvalue.expr]))
                    # property
                    if len(lcp) == 1 and isinstance(lcp[0], Class) and lvalue.attrname in lcp[0].properties:
                        self.visitm(lvalue.expr, '->' + self.cpp_name(lcp[0].properties[lvalue.attrname][1]) + '(', rvalue, ')', func)
                    elif lcp and isinstance(lcp[0], Class):
                        var = lookup_var(lvalue.attrname, lcp[0], mv=self.mv)
                        vartypes = set()
                        if var:
                            vartypes = self.mergeinh[var]
                        self.visit(lvalue, func)
                        self.append(' = ')
                        self.visit_conv(rvalue, vartypes, func)
                    else:
                        self.visitm(lvalue, ' = ', rvalue, func)
                    self.eol()

                # name = expr
                elif isinstance(lvalue, AssName):
                    vartypes = self.mergeinh[lookup_var(lvalue.name, func, mv=self.mv)]
                    self.visit(lvalue, func)
                    self.append(' = ')
                    self.visit_conv(rvalue, vartypes, func)
                    self.eol()

                # (a,(b,c), ..) = expr
                elif isinstance(lvalue, (AssTuple, AssList)):
                    self.tuple_assign(lvalue, rvalue, func)

                # expr[a:b] = expr
                elif isinstance(lvalue, Slice):
                    if isinstance(rvalue, Slice) and lvalue.upper == rvalue.upper == None and lvalue.lower == rvalue.lower == None:
                        self.visitm(lvalue.expr, self.connector(lvalue.expr, func), 'units = ', rvalue.expr, self.connector(rvalue.expr, func), 'units', func)
                    else:  # XXX let visitCallFunc(fakefunc) use cast_to_builtin
                        fakefunc = inode(self.gx, lvalue.expr).fakefunc
                        self.visitm('(', fakefunc.node.expr, ')->__setslice__(', fakefunc.args[0], ',', fakefunc.args[1], ',', fakefunc.args[2], ',', fakefunc.args[3], ',', func)
                        self.visit_conv(fakefunc.args[4], self.mergeinh[lvalue.expr], func)
                        self.append(')')
                    self.eol()

                # expr[a:b:c] = expr
                elif isinstance(lvalue, Subscript) and isinstance(lvalue.subs[0], Sliceobj):  # XXX see comment above
                    fakefunc = inode(self.gx, lvalue.expr).fakefunc
                    self.visitm('(', fakefunc.node.expr, ')->__setslice__(', fakefunc.args[0], ',', fakefunc.args[1], ',', fakefunc.args[2], ',', fakefunc.args[3], ',', func)
                    self.visit_conv(fakefunc.args[4], self.mergeinh[lvalue.expr], func)
                    self.append(')')
                    self.eol()

    def assign_pair(self, lvalue, rvalue, func):
        self.start('')

        # expr[expr] = expr
        if isinstance(lvalue, Subscript) and not isinstance(lvalue.subs[0], Sliceobj):
            self.subs_assign(lvalue, func)
            if isinstance(rvalue, str):
                self.append(rvalue)
            elif rvalue in self.mv.tempcount:
                self.append(self.mv.tempcount[rvalue])
            else:
                cast = self.cast_to_builtin2(rvalue, func, lvalue.expr, '__setitem__', 2)
                if cast:
                    self.append('((%s)' % cast)
                self.visit(rvalue, func)
                if cast:
                    self.append(')')
            self.append(')')
            self.eol()

        # expr.x = expr
        elif isinstance(lvalue, AssAttr):
            self.visitAssAttr(lvalue, func)

    def do_lambdas(self, declare):
        for l in self.mv.lambdas.values():
            if l.ident not in self.mv.funcs:
                self.visitFunction(l.node, declare=declare)

    def do_listcomps(self, declare):
        for (listcomp, lcfunc, func) in self.mv.listcomps:  # XXX cleanup
            if lcfunc.mv.module.builtin:
                continue

            parent = func
            while isinstance(parent, Function) and parent.listcomp:
                parent = parent.parent

            if isinstance(parent, Function):
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
        ts = nodetypestr(self.gx, node, lcfunc, mv=self.mv)
        if not ts.endswith('*'):
            ts += ' '
        if genexpr:
            self.genexpr_class(node, declare)
        else:
            self.output('static inline ' + ts + lcfunc.ident + '(' + ', '.join(args) + ')' + [' {', ';'][declare])

    def lc_args(self, lcfunc, func):
        args = []
        for name in lcfunc.misses:
            if lookup_var(name, func, mv=self.mv).parent:
                args.append((nodetypestr(self.gx, lookup_var(name, lcfunc, mv=self.mv), lcfunc, mv=self.mv), self.cpp_name(name)))
        return args

    def listcomp_func(self, node):
        lcfunc, func = self.listcomps[node]
        self.listcomp_head(node, False, False)
        self.indent()
        self.local_defs(lcfunc)
        self.output(nodetypestr(self.gx, node, lcfunc, mv=self.mv) + '__ss_result = new ' + nodetypestr(self.gx, node, lcfunc, mv=self.mv)[:-2] + '();\n')
        self.listcomp_rec(node, node.quals, lcfunc, False)
        self.output('return __ss_result;')
        self.deindent()
        self.output('}\n')

    def genexpr_class(self, node, declare):
        lcfunc, func = self.listcomps[node]
        args = self.lc_args(lcfunc, func)
        func1 = lcfunc.ident + '(' + ', '.join(a + b for a, b in args) + ')'
        func2 = nodetypestr(self.gx, node, lcfunc, mv=self.mv)[7:-3]
        if declare:
            ts = nodetypestr(self.gx, node, lcfunc, mv=self.mv)
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
            self.listcomp_rec(node, node.quals, lcfunc, True)
            self.output('__stop_iteration = true;')
            self.deindent()
            self.output('}\n')

    def local_defs(self, func):
        pairs = []
        for (name, var) in func.vars.items():
            if not var.invisible and (not hasattr(func, 'formals') or name not in func.formals):  # XXX
                pairs.append((nodetypestr(self.gx, var, func, mv=self.mv), self.cpp_name(var)))
        self.output(self.indentation.join(self.group_declarations(pairs)))

    # --- nested for loops: loop headers, if statements
    def listcomp_rec(self, node, quals, lcfunc, genexpr):
        if not quals:
            if genexpr:
                self.start('__result = ')
                self.visit(node.expr, lcfunc)
                self.eol()
                self.output('return __result;')
                self.start('__after_yield_0:')
            elif len(node.quals) == 1 and not is_fastfor(node.quals[0]) and not self.fastenum(node.quals[0]) and not self.fastzip2(node.quals[0]) and not node.quals[0].ifs and self.one_class(node.quals[0].list, ('tuple', 'list', 'str_', 'dict', 'set')):
                self.start('__ss_result->units[' + self.mv.tempcount[node.quals[0].list] + '] = ')
                self.visit(node.expr, lcfunc)
            else:
                self.start('__ss_result->append(')
                self.visit(node.expr, lcfunc)
                self.append(')')
            self.eol()
            return

        qual = quals[0]

        # iter var
        if isinstance(qual.assign, AssName):
            var = lookup_var(qual.assign.name, lcfunc, mv=self.mv)
        else:
            var = lookup_var(self.mv.tempcount[qual.assign], lcfunc, mv=self.mv)
        iter = self.cpp_name(var)

        if is_fastfor(qual):
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
            if not isinstance(qual.list, Name):
                itervar = self.mv.tempcount[qual]
                self.start('')
                self.visitm(itervar, ' = ', qual.list, lcfunc)
                self.eol()
            else:
                itervar = self.cpp_name(qual.list.name)

            pref, tail = self.forin_preftail(qual)

            if len(node.quals) == 1 and not qual.ifs and not genexpr:
                if self.one_class(qual.list, ('list', 'tuple', 'str_', 'dict', 'set')):
                    self.output('__ss_result->resize(len(' + itervar + '));')

            self.start('FOR_IN' + pref + '(' + iter + ',' + itervar + ',' + tail)
            print >>self.out, self.line + ')'
            self.listcompfor_body(node, quals, iter, lcfunc, False, genexpr)

    def listcompfor_body(self, node, quals, iter, lcfunc, skip, genexpr):
        qual = quals[0]

        if not skip:
            self.indent()
            if isinstance(qual.assign, (AssTuple, AssList)):
                self.tuple_assign(qual.assign, iter, lcfunc)

        # if statements
        if qual.ifs:
            self.start('if (')
            self.indent()
            for cond in qual.ifs:
                self.bool_test(cond.test, lcfunc)
                if cond != qual.ifs[-1]:
                    self.append(' && ')
            self.append(') {')
            print >>self.out, self.line

        # recurse
        self.listcomp_rec(node, quals[1:], lcfunc, genexpr)

        # --- nested for loops: loop tails
        if qual.ifs:
            self.deindent()
            self.output('}')
        self.deindent()
        self.output('END_FOR\n')

    def visitGenExpr(self, node, func=None):
        self.visit(self.gx.genexp_to_lc[node], func)

    def visitListComp(self, node, func=None):
        lcfunc, _ = self.listcomps[node]
        args = []
        temp = self.line

        for name in lcfunc.misses:
            var = lookup_var(name, func, mv=self.mv)
            if var.parent:
                if name == 'self' and not func.listcomp:  # XXX parent?
                    args.append('this')
                else:
                    args.append(self.cpp_name(var))

        self.line = temp
        if node in self.gx.genexp_to_lc.values():
            self.append('new ')
        self.append(lcfunc.ident + '(' + ', '.join(args) + ')')

    def visitSubscript(self, node, func=None):
        if node.flags == 'OP_DELETE':
            self.start()
            if isinstance(node.subs[0], Sliceobj):
                self.visitCallFunc(inode(self.gx, node.expr).fakefunc, func)
            else:
                self.visitCallFunc(inode(self.gx, node.expr).fakefunc, func)
            self.eol()
        else:
            self.visitCallFunc(inode(self.gx, node.expr).fakefunc, func)

    def visitMod(self, node, func=None):
        # --- non-str % ..
        if [t for t in self.gx.merged_inh[node.left] if t[0].ident != 'str_']:
            self.visitBinary(node.left, node.right, '__mod__', '%', func)
            return

        # --- str % non-constant dict/tuple
        if not isinstance(node.right, (Tuple, Dict)) and node.right in self.gx.merged_inh:  # XXX
            if [t for t in self.gx.merged_inh[node.right] if t[0].ident == 'dict']:
                self.visitm('__moddict(', node.left, ', ', node.right, ')', func)
                return
            elif [t for t in self.gx.merged_inh[node.right] if t[0].ident in ['tuple', 'tuple2']]:
                self.visitm('__modtuple(', node.left, ', ', node.right, ')', func)
                return

        # --- str % constant-dict:
        if isinstance(node.right, Dict):  # XXX geen str keys
            self.visitm('__modcd(', node.left, ', ', 'new list<str *>(%d, ' % len(node.right.items), func)
            self.append(', '.join(('new str("%s")' % key.value) for key, value in node.right.items))
            self.append(')')
            nodes = [value for (key, value) in node.right.items]
        else:
            self.visitm('__modct(', node.left, func)
            # --- str % constant-tuple
            if isinstance(node.right, Tuple):
                nodes = node.right.nodes

            # --- str % non-tuple/non-dict
            else:
                nodes = [node.right]
            self.append(', %d' % len(nodes))

        # --- visit nodes, boxing scalars
        for n in nodes:
            if [clname for clname in ('float_', 'int_', 'bool_', 'complex') if def_class(self.gx, clname) in [t[0] for t in self.mergeinh[n]]]:
                self.visitm(', ___box(', n, ')', func)
            else:
                self.visitm(', ', n, func)
        self.append(')')

    def visitPrintnl(self, node, func=None):
        self.visitPrint(node, func, print_space=False)

    def visitPrint(self, node, func=None, print_space=True):
        self.start('print2(')
        if node.dest:
            self.visitm(node.dest, ', ', func)
        else:
            self.append('NULL,')
        if print_space:
            self.append('1,')
        else:
            self.append('0,')
        self.append(str(len(node.nodes)))
        for n in node.nodes:
            types = [t[0].ident for t in self.mergeinh[n]]
            if 'float_' in types or 'int_' in types or 'bool_' in types or 'complex' in types:
                self.visitm(', ___box(', n, ')', func)
            else:
                self.visitm(', ', n, func)
        self.eol(')')

    def visitGetattr(self, node, func=None):
        cl, module = lookup_class_module(node.expr, inode(self.gx, node).mv, func)

        # module.attr
        if module:
            self.append(module.full_path() + '::')

        # class.attr: staticmethod
        elif cl and node.attrname in cl.staticmethods:
            ident = cl.ident
            if cl.ident in ['dict', 'defaultdict']:  # own namespace because of template vars
                self.append('__' + cl.ident + '__::')
            elif isinstance(node.expr, Getattr):
                submodule = lookup_module(node.expr.expr, inode(self.gx, node).mv)
                self.append(submodule.full_path() + '::' + ident + '::')
            else:
                self.append(ident + '::')

        # class.attr
        elif cl:  # XXX merge above?
            ident = cl.ident
            if isinstance(node.expr, Getattr):
                submodule = lookup_module(node.expr.expr, inode(self.gx, node).mv)
                self.append(submodule.full_path() + '::' + cl.ident + '::')
            else:
                self.append(ident + '::')

        # obj.attr
        else:
            checkcls = []  # XXX better to just inherit vars?
            for t in self.mergeinh[node.expr]:
                if isinstance(t[0], Class):
                    checkcls.extend(t[0].ancestors(True))
            for cl in checkcls:
                if not node.attrname in t[0].funcs and node.attrname in cl.parent.vars:  # XXX
                    error("class attribute '" + node.attrname + "' accessed without using class name", self.gx, node, warning=True, mv=self.mv)
                    break
            else:
                if not self.mergeinh[node.expr] and not node.attrname.startswith('__'):  # XXX
                    error('expression has no type', self.gx, node, warning=True, mv=self.mv)
                elif not self.mergeinh[node] and not [cl for cl in checkcls if node.attrname in cl.funcs] and not node.attrname.startswith('__'):  # XXX
                    error('expression has no type', self.gx, node, warning=True, mv=self.mv)

            if not isinstance(node.expr, Name):
                self.append('(')
            if isinstance(node.expr, Name) and not lookup_var(node.expr.name, func, mv=self.mv):  # XXX XXX
                self.append(node.expr.name)
            else:
                self.visit(node.expr, func)
            if not isinstance(node.expr, (Name)):
                self.append(')')

            self.append(self.connector(node.expr, func))

        ident = node.attrname

        # property
        lcp = lowest_common_parents(polymorphic_t(self.gx, self.mergeinh[node.expr]))
        if len(lcp) == 1 and node.attrname in lcp[0].properties:
            self.append(self.cpp_name(lcp[0].properties[node.attrname][0]) + '()')
            return

        # getfast
        if ident == '__getitem__' and self.one_class(node.expr, ('list', 'str_', 'tuple')):
            ident = '__getfast__'
        elif ident == '__getitem__' and len(lcp) == 1 and lcp[0].ident == 'array':  # XXX merge into above
            ident = '__getfast__'

        self.append(self.attr_var_ref(node, ident))

    def attr_var_ref(self, node, ident):  # XXX blegh
        lcp = lowest_common_parents(polymorphic_t(self.gx, self.mergeinh[node.expr]))
        if len(lcp) == 1 and isinstance(lcp[0], Class) and node.attrname in lcp[0].vars and not node.attrname in lcp[0].funcs:
            return self.cpp_name(lcp[0].vars[node.attrname])
        return self.cpp_name(ident)

    def visitAssAttr(self, node, func=None):  # XXX merge with visitGetattr
        if node.flags == 'OP_DELETE':
            error("'del' has no effect without refcounting", self.gx, node, warning=True, mv=self.mv)
            return

        cl, module = lookup_class_module(node.expr, inode(self.gx, node).mv, func)

        # module.attr
        if module:
            self.append(module.full_path() + '::')

        # class.attr
        elif cl:
            if isinstance(node.expr, Getattr):
                submodule = lookup_module(node.expr.expr, inode(self.gx, node).mv)
                self.append(submodule.full_path() + '::' + cl.ident + '::')
            else:
                self.append(cl.ident + '::')

        # obj.attr
        else:
            if isinstance(node.expr, Name) and not lookup_var(node.expr.name, func, mv=self.mv):  # XXX
                self.append(node.expr.name)
            else:
                self.visit(node.expr, func)
            self.append(self.connector(node.expr, func))  # XXX '->'

        self.append(self.attr_var_ref(node, node.attrname))

    def visitAssName(self, node, func=None):
        if node.flags == 'OP_DELETE':
            error("'del' has no effect without refcounting", self.gx, node, warning=True, mv=self.mv)
            return
        self.append(self.cpp_name(node.name))

    def visitName(self, node, func=None, add_cl=True):
        map = {'True': 'True', 'False': 'False'}
        if node in self.mv.lwrapper:
            self.append(self.mv.lwrapper[node])
        elif node.name == 'None':
            self.append('NULL')
        elif node.name == 'self':
            lcp = lowest_common_parents(polymorphic_t(self.gx, self.mergeinh[node]))
            if ((not func or func.listcomp or not isinstance(func.parent, Class)) or
               (func and func.parent and func.isGenerator)):  # XXX lookup_var?
                self.append('self')
            elif len(lcp) == 1 and not (lcp[0] is func.parent or lcp[0] in func.parent.ancestors()):  # see test 160
                self.mv.module.prop_includes.add(lcp[0].module)  # XXX generalize
                self.append('((' + self.namer.namespace_class(lcp[0]) + ' *)this)')
            else:
                self.append('this')
        elif node.name in map:
            self.append(map[node.name])

        else:  # XXX clean up
            if not self.mergeinh[node] and not inode(self.gx, node).parent in self.gx.inheritance_relations:
                error("variable '" + node.name + "' has no type", self.gx, node, warning=True, mv=self.mv)
                self.append(node.name)
            elif singletype(self.gx, node, Module):
                self.append('__' + singletype(self.gx, node, Module).ident + '__')
            else:
                if ((def_class(self.gx, 'class_'), 0) in self.mergeinh[node] or
                   (add_cl and [t for t in self.mergeinh[node] if isinstance(t[0], StaticClass)])):
                    cl = lookup_class(node, self.mv)
                    if cl:
                        self.append(self.namer.namespace_class(cl, add_cl='cl_'))
                    else:
                        self.append(self.cpp_name(node.name))
                else:
                    if isinstance(func, Class) and node.name in func.parent.vars:  # XXX
                        self.append(func.ident + '::')
                    var = lookup_var(node.name, func, mv=self.mv)
                    if var:
                        self.append(self.cpp_name(var))
                    else:
                        self.append(node.name)  # XXX

    def expand_special_chars(self, value):
        value = list(value)
        replace = dict(['\\\\', '\nn', '\tt', '\rr', '\ff', '\bb', '\vv', '""'])

        for i in range(len(value)):
            if value[i] in replace:
                value[i] = '\\' + replace[value[i]]
            elif value[i] not in string.printable:
                value[i] = '\\' + oct(ord(value[i])).zfill(4)[1:]

        return ''.join(value)

    def visitConst(self, node, func=None):
        if not self.filling_consts and isinstance(node.value, str):
            self.append(self.get_constant(node))
            return
        if node.value is None:
            self.append('NULL')
            return
        t = list(inode(self.gx, node).types())[0]
        if t[0].ident == 'int_':
            self.append(str(node.value))
            if self.gx.longlong:
                self.append('LL')
        elif t[0].ident == 'float_':
            if str(node.value) in ['inf', '1.#INF', 'Infinity']:
                self.append('INFINITY')
            elif str(node.value) in ['-inf', '-1.#INF', 'Infinity']:
                self.append('-INFINITY')
            else:
                self.append(str(node.value))
        elif t[0].ident == 'str_':
            self.append('new str("%s"' % self.expand_special_chars(node.value))
            if '\0' in node.value:  # '\0' delimiter in C
                self.append(', %d' % len(node.value))
            self.append(')')
        elif t[0].ident == 'complex':
            self.append('mcomplex(%s, %s)' % (node.value.real, node.value.imag))
        else:
            self.append('new %s(%s)' % (t[0].ident, node.value))


def generate_code(gx):
    for module in gx.modules.values():
        if not module.builtin:
            gv = GenerateVisitor(gx, module)
            walk(module.ast, gv)
            gv.out.close()
            gv.header_file()
            gv.out.close()
            gv.insert_consts(declare=False)
            gv.insert_consts(declare=True)
            gv.insert_extras('.hpp')
            gv.insert_extras('.cpp')
    generate_makefile(gx)
