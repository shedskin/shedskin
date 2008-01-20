#!/usr/bin/env python

# *** SHED SKIN Python-to-C++ Compiler 0.0.26 ***
# Copyright 2005-2008 Mark Dufour; License GNU GPL version 3 (See LICENSE)

from compiler import *
from compiler.ast import *
from compiler.visitor import *

import sys, string, copy, getopt, os.path, textwrap, traceback

# python2.3 compatibility
try: enumerate
except NameError:
    def enumerate(collection):
        i = 0
        it = iter(collection)
        while 1:
            yield (i, it.next())
            i += 1

try: set
except NameError:
    from sets import Set, ImmutableSet
    set = Set; frozenset = ImmutableSet

# --- static class (class-level stuff)
class static_class: # XXX merge with regular class
    def __init__(self, cl):
        self.vars = {}
        self.funcs = {}
        self.class_ = cl
        cl.static_class = self
        self.ident = cl.ident
        self.bases = []
        self.parent = None
        self.mv = mv
        self.module = cl.module

    def __repr__(self):
        return 'static class '+self.class_.ident

class class_:
    def __init__(self, node):
        self.node = node
        self.ident = node.name
        self.bases = []
        self.children = []
        self.dcpa = 1
        self.mv = mv
        self.vars = {}
        self.funcs = {}
        self.virtuals = {}              # 'virtually' called methods 
        self.virtualvars = {}           # 'virtual' variables
        self.template_vars = {}

        self.typenr = gx.nrcltypes
        gx.nrcltypes += 1
        gx.typeclass[self.typenr] = self

        # data adaptive analysis
        self.nrcart = {}                # nr: cart
        self.cartnr = {}                # cart: nr
        self.splits = {}                # contour: old contour (used between iterations)
        self.unused = []                # unused contours

        self.has_init = self.has_copy = self.has_deepcopy = False

    def copy(self, dcpa):
        for var in self.vars.values(): # XXX 
            if not inode(var) in gx.types: continue # XXX research later

            inode(var).copy(dcpa, 0)
            gx.types[gx.cnode[var, dcpa, 0]] = inode(var).types().copy()

            for n in inode(var).in_: # XXX
                if isinstance(n.thing, Const):
                    addconstraint(n, gx.cnode[var,dcpa,0])

        for func in self.funcs.values():
            if self.mv.module.ident == 'builtin' and self.ident != '__iter' and func.ident == '__iter__': # XXX hack for __iter__:__iter() 
                itercl = defclass('__iter')
                gx.alloc_info[func.ident, ((self,dcpa),), func.returnexpr[0]] = (itercl, itercl.dcpa)

                #print 'itercopy', itercl.dcpa

                itercl.copy(itercl.dcpa)
                itercl.dcpa += 1

            func.copy(dcpa, 0)

    def ancestors(self): # XXX attribute (faster)
        a = set(self.bases)
        changed = 1
        while changed:
            changed = 0
            for cl in a.copy():
                if set(cl.bases)-a:
                    changed = 1
                    a.update(cl.bases)
        return a

    def ancestors_upto(self, other):
        a = self
        result = []
        while a != other:
            result.append(a)
            if not a.bases:
                break
            a = a.bases[0] 
        return result

    def descendants(self, inclusive=False): # XXX attribute (faster)
        a = set()
        if inclusive: 
            a.add(self)
        for cl in self.children:
            a.add(cl)
            a.update(cl.descendants())
        return a

    def __repr__(self):
        return 'class '+self.ident

    def template(self): # XXX nokeywords
        if self.template_vars: return self.ident+'<'+','.join(self.template_vars)+'>'
        else: return self.ident

def connect_paths(a, b, conn='/'):
    if a == '':
        return b
    return a+conn+b

def relative_path(a, b):
    c = b[len(a):]
    if c.startswith('/'): c = c[1:]
    return c

class module:
    def __init__(self, name, ast=None, parent=None, node=None):
        global mv

        for c in name: 
            if not c in string.letters+string.digits+'_.':
                print ("*ERROR*:%s.py: module names should consist of letters, digits and underscores" % name)
                sys.exit()

        self.ident = name.split('.')[-1]
        self.builtin = False

        if ast: # XXX
            self.ast = ast
            self.dir = ''
            self.mod_path = []
        else: 
            # --- locate module
            importfromlib = (parent and parent.dir == gx.libdir)

            relname = name.replace('.', '/')
            relpath = name.split('.')
            if parent: path = connect_paths(parent.dir, relname)
            else: path = name
            libpath = connect_paths(gx.libdir, relname)

            #print 'huh', name, parent, self.ident, relname, relpath

            if not importfromlib and os.path.isfile(path+'.py'): # local modules shadow library modules
                self.filename = path+'.py'
                if parent: self.mod_path = parent.mod_path + relpath[:-1]
                else: self.mod_path = relpath[:-1]
                split = path.split('/')
                self.dir = '/'.join(split[:-1])

            elif not importfromlib and os.path.isfile(connect_paths(path, '__init__.py')):
                self.filename = connect_paths(path, '__init__.py')
                if parent: self.mod_path = parent.mod_path + relpath
                else: self.mod_path = relpath
                self.dir = path

            elif os.path.isfile(libpath+'.py'):
                self.filename = libpath+'.py'
                self.mod_path = relpath[:-1]
                self.builtin = True
                split = libpath.split('/')
                self.dir = '/'.join(split[:-1])

            elif os.path.isfile(connect_paths(libpath, '__init__.py')):
                self.filename = connect_paths(libpath, '__init__.py')
                self.mod_path = relpath[:-1]
                self.builtin = True
                self.dir = libpath

            else:
                error('cannot locate module: '+name, node)

            if self.filename.startswith(libpath): self.builtin = True
            gx.modules['.'.join(self.mod_path+[self.ident])] = self
              
            #print 'done', self.filename, self.dir, self.mod_path, self.ident

            self.ast = parsefile(self.filename) 
            gx.dirs.setdefault('', []).append(self)

        old_mv = mv 
        self.mv = mv = moduleVisitor(self)

        mv.visit = mv.dispatch
        mv.visitor = mv
        mv.dispatch(self.ast)

        mv = old_mv

        self.funcs = self.mv.funcs
        self.classes = self.mv.classes

    def __repr__(self):
        return 'module '+self.ident 

class function:
    def __init__(self, node=None, parent=None, inherited_from=None):
        self.node = node
        if node:
            ident = node.name
            if inherited_from and ident in parent.funcs:
                ident += inherited_from.ident+'__' # XXX ugly
            self.ident = ident
            self.formals = node.argnames
            self.flags = node.flags
            self.doc = node.doc
        self.returnexpr = []
        self.retnode = None
        self.parent = parent 
        self.constraints = set()
        self.vars = {}
        self.template_vars = {}
        self.varargs = None
        self.kwargs = None
        self.globals = []
        self.mv = mv
        self.lnodes = []
        self.nodes = set()
        self.defaults = []
        self.misses = set()
        self.cp = {}
        self.listcomp = False
        self.isGenerator = False
        self.yieldNodes = []
        self.tvars = set()
        self.ftypes = []                # function is called via a virtual call: arguments may have to be cast
        self.inherited = None

        if node and mv.module.ident != 'builtin':
            gx.allfuncs.add(self)

        self.parent_constr = None
        self.retvars = []
        self.invisible = False
        self.fakeret = None
        self.declared = False

        self.registered = []

    # --- use dcpa=0,cpa=0 mold created by module visitor to duplicate function
    def copy(self, dcpa, cpa, worklist=None, cart=None):
        #print 'funccopy', self, cart, dcpa, cpa

        # --- copy local end points of each constraint
        for (a,b) in self.constraints:
            if not (isinstance(a.thing, variable) and parent_func(a.thing) != self) and a.dcpa == 0: 
                a = a.copy(dcpa, cpa, worklist)
            if not (isinstance(b.thing, variable) and parent_func(b.thing) != self) and b.dcpa == 0:
                b = b.copy(dcpa, cpa, worklist)

            addconstraint(a,b, worklist)

        # --- copy other nodes 
        for node in self.nodes:
            newnode = node.copy(dcpa, cpa, worklist)

        # --- copy tuple seed for varargs
        if self.varargs:
            var = self.vars[self.varargs]
            gx.types[gx.cnode[var,dcpa,cpa]] = gx.types[inode(var)].copy()

        # --- iterative flow analysis: seed allocation sites in new template
        ifa_seed_template(self, cart, dcpa, cpa, worklist)

    def __repr__(self):
        if self.parent: return 'function '+repr((self.parent, self.ident))
        return 'function '+self.ident

def is_method(parent):
    return isinstance(parent, function) and isinstance(parent.parent, class_)
def is_listcomp(parent):
    return isinstance(parent, function) and parent.listcomp

def fastfor(node):
    return isinstance(node.list, CallFunc) and isinstance(node.list.node, Name) and node.list.node.name in ['range', 'xrange']

class variable:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.invisible = False            # not in C++ output
        self.formal_arg = False
        self.template_variable = False    
        self.template_disabled = False
        self.imported = False
        self.initexpr = None
        self.filter = set()                # filters: x.append(..) means that x can only be of a class that has 'append'

    def types(self):
        return inode(self).types()

    def __repr__(self):
        if self.parent: return repr((self.parent, self.name))
        return self.name

def lookupvar(name, parent):
    return defvar(name, parent, False)

def defaultvar(name, parent, worklist=None, template_var=False):
    return defvar(name, parent, True, worklist, template_var)

def defvar(name, parent, local, worklist=None, template_var=False):
    if parent and name in parent.vars:
        return parent.vars[name]
    if template_var:
        dest = parent.template_vars
    elif parent and local:
        dest = parent.vars
    else:
        # recursive lookup
        chain = []
        while isinstance(parent, function):
            if name in parent.vars:
                for ancestor in chain:
                    if isinstance(ancestor, function): # XXX optimize
                        ancestor.misses.add(name)
                return parent.vars[name]
            chain.append(parent)
            parent = parent.parent
            
        # not found: global
        if name in mv.globals:
            return mv.globals[name]
        dest = mv.globals

    if not local:
        return None

    var = variable(name, parent)
    if template_var:
        var.template_variable = True
    else:
        gx.allvars.add(var)

    dest[name] = var
    newnode = cnode(var, parent=parent) 
    if parent:
        newnode.mv = parent.mv
    addtoworklist(worklist, newnode)
    gx.types[newnode] = set()

    return var

# --- constraint graph nodes
class cnode:
    def __init__(self, thing, dcpa=0, cpa=0, parent=None):
        self.thing = thing
        self.dcpa = dcpa
        self.cpa = cpa
        self.fakenodes = []
        self.fakefunc = None
        self.parent = parent
        self.defnodes = False # if callnode, notification nodes were made for default arguments
        self.mv = mv
        self.constructor = False # allocation site 
        self.copymetoo = False
        self.filters = [] # run-time type filters such as isinstance()
        #self.parent_callfunc = None
        self.fakert = False
     
        if isinstance(self.thing, CallFunc) and isinstance(self.thing.node, Name) and self.thing.node.name == 'set': 
            if (self.thing, self.dcpa, self.cpa) in gx.cnode:
                print 'killing something!', self
                traceback.print_stack() 

        gx.cnode[self.thing, self.dcpa, self.cpa] = self

        # --- in, outgoing constraints

        self.in_ = set()        # incoming nodes
        self.out = set()        # outgoing nodes
        self.fout = set()       # unreal outgoing edges, used in ifa
          
        # --- iterative dataflow analysis

        self.in_list = 0        # node in work-list
        self.callfuncs = []    # callfuncs to which node is object/argument
        self.copybyvalue = {}   # node is copy-by-value argument (int/str/float type->number)

        if isinstance(thing, CallFunc): self.changed = 1 # object/arguments have changed

        self.nodecp = set()        # already analyzed cp's # XXX kill! kill!

        # --- add node to surrounding non-listcomp function
        if parent: # do this only once! (not when copying)
            while parent and isinstance(parent, function) and parent.listcomp: parent = parent.parent 
            if isinstance(parent, function):
                if self not in parent.nodes:
                    parent.nodes.add(self)
                    #parent.lnodes.append(self)

    def copy(self, dcpa, cpa, worklist=None):
        #if not self.mv.module.builtin: print 'copy', self

        if (self.thing, dcpa, cpa) in gx.cnode:
            return gx.cnode[self.thing, dcpa, cpa]

        newnode = cnode(self.thing, dcpa, cpa)

        newnode.callfuncs = self.callfuncs[:] # XXX no copy?
        newnode.constructor = self.constructor
        newnode.copymetoo = self.copymetoo
        newnode.parent = self.parent
        newnode.mv = self.mv

        addtoworklist(worklist, newnode)

        if self.constructor or self.copymetoo or isinstance(self.thing, (Not, Compare)): # XXX XXX
            gx.types[newnode] = gx.types[self].copy()
        else:
            gx.types[newnode] = set()
        return newnode

    def types(self):
        return gx.types[self]

    def __repr__(self):
        return repr((self.thing, self.dcpa, self.cpa))

def inode(node):
    return gx.cnode[node,0,0]

class fakeGetattr(Getattr): pass # XXX ugly
class fakeGetattr2(Getattr): pass
class fakeGetattr3(Getattr): pass

# --- check whether local variables/expressions match with class/function template variable
def template_match(split, parent, orig_parent=None): 
    # --- global: no surrounding template
    if not parent:  
        return False

    parents = [parent]
    if is_method(parent): 
        parents = [parent.parent, parent]

    # --- match with class/function template variables
    for parent in parents:
        for var in parent.template_vars.values():
            match = True

            for (dcpa, cpa), types in split.items():
                if not types: continue
                if not (var,dcpa,0) in gx.cnode: continue # XXX ahm..
                if isinstance(parent, class_) and dcpa in parent.unused: # XXX research nicer fix
                    continue

                intfloat = [t for t in types if t[0].ident in ['int_', 'float_']]
                if len(polymorphic_t(types)) > 1 and intfloat: 
                    match = False

                if isinstance(parent, function):
                    node = gx.cnode[var, dcpa, cpa]
                else:
                    node = gx.cnode[var, dcpa, 0] # cpa=0 for class variables 

                if set([t[0] for t in types]) != set([t[0] for t in node.types()]): 
                    match = False
                    break
                    
            if match: 
                if isinstance(orig_parent, function) and orig_parent.listcomp:
                    orig_parent.tvars.add(var)
                return var
    return None
        
def template_match_node(node, parent):
    split = typesplit(node, parent)
    return template_match(split, parent)

# --- recursively determine (lvalue, rvalue) pairs in assignment expressions
def assign_rec(left, right):
    # determine lvalues and rvalues
    if isinstance(left, (AssTuple, AssList)): 
        lvalues = left.getChildNodes()
    else: 
        lvalues = [left]

    if len(lvalues) > 1:
        if isinstance(right, (Tuple, List)): 
            rvalues = right.getChildNodes()
        else:
            return [(left, right)]
    else:
        rvalues = [right]

    # pair corresponding arguments
    pairs = []
    for (lvalue,rvalue) in zip(lvalues, rvalues):
         if isinstance(lvalue, (AssTuple, AssList)): 
             pairs += assign_rec(lvalue, rvalue)
         else:
             pairs.append((lvalue, rvalue))

    return pairs

def slicenums(nodes):
    nodes2 = []
    x = 0
    for i, n in enumerate(nodes):
        if not n or (isinstance(n, Const) and n.value == None): 
            nodes2.append(Const(0))
        else: 
            nodes2.append(n)
            x |= (1 << i)
    return [Const(x)]+nodes2

class globalInfo: # XXX add comments
    def __init__(self):
        global gx
        gx = self

        self.constraints = set()
        self.allvars = set()
        self.allfuncs = set()
        self.allclasses = set()
        self.cnode = {}
        self.types = {}
        self.templates = 0
        self.modules = {}
        self.inheritance_relations = {}
        self.parent_nodes = {}
        self.inherited = set()
        self.nrcltypes = 8;
        self.empty_constructors = set()
        self.typeclass = {}
        self.sig_nr = {}
        self.nameclasses = {}
        self.dirs = {}                  # module management
        self.tuple2 = set()             # binary typed tuples 
        self.module = None
        self.simple_builtins = ['none', 'str_', 'float_', 'int_', 'class_']   
        self.builtins = self.simple_builtins + ['list', 'tuple', 'tuple2', 'dict', 'frozenset', 'set']
        self.assign_target = {}              # instance node for instance variable assignment
        self.alloc_info = {}                 # allocation site type information across iterations
        self.iterations = 0
        self.sysdir = os.environ.get('SHEDSKIN_ROOT', '.').replace('\\','/')
        self.libdir = connect_paths(self.sysdir, 'lib')
        self.main_mod = 'test'
        self.cpp_keywords = set(['asm', 'auto', 'bool', 'case', 'catch', 'char', 'const', 'const_cast', 'default', 'delete', 'do', 'double', 'dynamic_cast', 'enum', 'explicit', 'export', 'extern', 'false', 'float', 'friend', 'goto', 'inline', 'int', 'long', 'mutable', 'namespace', 'new', 'operator', 'private', 'protected', 'public', 'register', 'reinterpret_cast', 'short', 'signed', 'register', 'sizeof', 'static', 'static_cast', 'struct', 'switch', 'template', 'this', 'throw', 'true', 'typedef', 'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', 'void', 'volatile', 'wchar_t'])
        self.cpp_keywords.update(['stdin', 'stdout', 'stderr', 'std', 'abstract', 'st_mtime', 'st_atime', 'st_ctime', 'errno', 'fileno', 'environ']) # XXX
        self.cpp_keywords.update(['ST_ATIME', 'ST_CTIME', 'ST_DEV', 'ST_GID', 'ST_INO', 'ST_MODE', 'ST_MTIME', 'ST_NLINK', 'ST_SIZE', 'ST_UID', 'S_ENFMT', 'S_IEXEC', 'S_IFBLK', 'S_IFCHR', 'S_IFDIR', 'S_IFIFO', 'S_IFLNK', 'S_IFREG', 'S_IFSOCK', 'S_IREAD', 'S_IRGRP', 'S_IROTH', 'S_IRUSR', 'S_IRWXG', 'S_IRWXO', 'S_IRWXU', 'S_ISGID', 'S_ISUID', 'S_ISVTX', 'S_IWGRP', 'S_IWOTH', 'S_IWRITE', 'S_IWUSR', 'S_IXGRP', 'S_IXOTH', 'S_IXUSR', 'S_IMODE', 'S_IFMT', 'S_ISDIR', 'S_ISCHR', 'S_ISBLK', 'S_ISREG', 'S_ISFIFO', 'S_ISLNK', 'S_ISSOCK'])
        self.ss_prefix = '__ss_'
        self.list_types = {}
        self.classes_with_init = set()
        self.loopstack = [] # track nested loops
        self.comments = {}
        self.wrap_around_check = True
        self.bounds_checking = False
        self.extension_module = False
        self.flags = None
        self.method_refs = set()
        self.avoid_loops = False
        self.assignments = []
        
def get_ident(node):
    if not isinstance(node, Const) or not isinstance(node.value, int):
        return '__getitem__'

    if node.value == 0:  return '__getfirst__'
    elif node.value == 1: return '__getsecond__'
    return '__getitem__'

def check_redef(node, s=None, onlybuiltins=False): # XXX to modvisitor, rewrite
    if not mv.module.builtin:
        existing = [mv.ext_classes, mv.ext_funcs]
        if not onlybuiltins: existing += [mv.classes, mv.funcs]
        for whatsit in existing:
            if s != None: name = s
            else: name = node.name
            if name in whatsit:
                error("function/class redefinition is not supported ('%s')" % name, node)

def augmsg(node, msg):
    if hasattr(node, 'augment'): return '__i'+msg+'__'
    return '__'+msg+'__'

# --- maintain inheritance relations between copied AST nodes
def inherit_rec(original, copy):
    gx.inheritance_relations.setdefault(original, []).append(copy)
    gx.inherited.add(copy)
    gx.parent_nodes[copy] = original

    for (a,b) in zip(original.getChildNodes(), copy.getChildNodes()): 
        inherit_rec(a,b)
    
def register_node(node, func): 
    #print 'register', node, nr, func
    if func:
        func.registered.append(node)
        
# --- module visitor; analyze program, build constraint graph
class moduleVisitor(ASTVisitor):
    def __init__(self, module):
        ASTVisitor.__init__(self)

        self.module = module

        self.classes = {} 
        self.funcs = {}
        self.globals = {}
        self.lambdas = {}
        self.imports = {}
        self.ext_classes = {}
        self.ext_funcs = {}
        self.lambdaname = {}

        self.lambda_cache = {} # XXX ununboxable requires these.. 
        self.lambda_signum = {}

        self.tempcount = {}
        self.callfuncs = []
        self.for_in_iters = []
        self.listcomps = []

        self.importnodes = []

    def dispatch(self, node, *args):
        if (node, 0, 0) not in gx.cnode:
            ASTVisitor.dispatch(self, node, *args)

    def fakefunc(self, node, objexpr, attrname, args, func):
        if (node, 0, 0) in gx.cnode: # XXX 
            newnode = gx.cnode[node,0,0]
        else:
            newnode = cnode(node, parent=func)
            gx.types[newnode] = set()

        fakefunc = CallFunc(Getattr(objexpr, attrname), args)

        self.visit(fakefunc, func)
        self.addconstraint((inode(fakefunc), newnode), func)

        inode(objexpr).fakefunc = fakefunc
        return fakefunc

    # simple heuristic for initial list split: count nesting depth, first constant child type
    def list_type(self, node):
        count = 0
        child = node
        while isinstance(child, (List, ListComp)):
            if not child.getChildNodes():
                return None
            child = child.getChildNodes()[0]
            count += 1

        if isinstance(child, UnarySub): child = child.expr

        if isinstance(child, CallFunc) and isinstance(child.node, Name):
            map = {'int': int, 'str': str, 'float': float}
            if child.node.name in ('range'): #,'xrange'):
                count, child = count+1, int
            elif child.node.name in map:
                child = map[child.node.name]
            elif child.node.name in [cl.ident for cl in gx.allclasses] or child.node.name in mv.classes: # XXX mv.classes
                child = child.node.name 
            else:
                if count == 1: return None
                child = None
        elif isinstance(child, Const):
            child = type(child.value)
        elif isinstance(child, Tuple):
            child = tuple
        elif isinstance(child, Dict):
            child = dict
        else:
            if count == 1: return None
            child = None

        gx.list_types.setdefault((count, child), len(gx.list_types)+2)
        #print 'listtype', node, gx.list_types[count, child]
        return gx.list_types[count, child]

    def instance(self, node, cl, func=None):
        if (node, 0, 0) in gx.cnode: # XXX to create_node() func
            newnode = gx.cnode[node,0,0]
        else:
            newnode = cnode(node, parent=func)

        newnode.constructor = True 

        if cl.ident in ['int_','float_','str_','none', 'class_','bool']:
            gx.types[newnode] = set([(cl, cl.dcpa-1)])
        else:
            if cl.ident == 'list' and self.list_type(node):
                gx.types[newnode] = set([(cl, self.list_type(node))])
            else:
                gx.types[newnode] = set([(cl, cl.dcpa)])

    def constructor(self, node, classname, func): 
        cl = defclass(classname)

        self.instance(node, cl, func)
        var = defaultvar('unit', cl)

        if classname in ['list','tuple'] and not node.nodes:
            gx.empty_constructors.add(node) # ifa disables those that flow to instance variable assignments

        # --- internally flow binary tuples
        if cl.ident == 'tuple2':
            var3 = defaultvar('first', cl) 
            var2 = defaultvar('second', cl)
            elem0, elem1 = node.nodes

            self.visit(elem0, func)
            self.visit(elem1, func)

            self.add_dynamic_constraint(node, elem0, 'unit', func)
            self.add_dynamic_constraint(node, elem1, 'unit', func)

            self.add_dynamic_constraint(node, elem0, 'first', func)
            self.add_dynamic_constraint(node, elem1, 'second', func)

            return

        # --- add dynamic children constraints for other types
        if classname == 'dict': # XXX filter children
            keyvar = defaultvar('unit', cl)
            valvar = defaultvar('value', cl)

            for child in node.getChildNodes():
                self.visit(child, func)

            for (key,value) in node.items: # XXX filter
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
        if isinstance(node, UnarySub):
            node = node.expr

        if isinstance(node, (List, Tuple)):
            if isinstance(node, List): cl = defclass('list')
            elif len(node.nodes) == 2: cl = defclass('tuple2')
            else: cl = defclass('tuple')
               
            merged = set()
            for child in node.nodes:
                merged.add(self.child_type_rec(child))
                
            if len(merged) == 1:
                return (cl, merged.pop())

        elif isinstance(node, Const):
            return (list(inode(node).types())[0][0],)

        return None

    # --- add dynamic constraint for constructor argument, e.g. '[expr]' becomes [].__setattr__('unit', expr)
    def add_dynamic_constraint(self, parent, child, varname, func): 
        #print 'dynamic constr', child, parent

        gx.assign_target[child] = parent
        cu = Const(varname)
        self.visit(cu, func)
        fakefunc = CallFunc(fakeGetattr2(parent, '__setattr__'), [cu, child])
        self.visit(fakefunc, func)
          
        fakechildnode = cnode((child, varname), parent=func) # create separate 'fake' cnode per child, so we can have multiple 'callfuncs'
        gx.types[fakechildnode] = set()

        self.addconstraint((inode(parent), fakechildnode), func) # add constraint from parent to fake child node. if parent changes, all fake child nodes change, and the callfunc for each child node is triggered
        fakechildnode.callfuncs.append(fakefunc)

    # --- add regular constraint to function
    def addconstraint(self, constraint, func):
        in_out(constraint[0], constraint[1])
        gx.constraints.add(constraint)
        while func and func.listcomp: func = func.parent # XXX
        if func:
            func.constraints.add(constraint)

    def visitGenExpr(self, node, func=None):
        error('generator expressions are not supported', node)

    def visitStmt(self, node, func=None):
        comments = []
        for b in node.nodes:
            if isinstance(b, Discard) and isinstance(b.expr, Const) and type(b.expr.value) == str:
                comments.append(b.expr.value)
            elif comments:
                gx.comments[b] = comments
                comments = []
       
            self.visit(b, func)
            
    def visitModule(self, node):
        global mv

        # --- bootstrap built-in classes
        if self.module.ident == 'builtin':
            for dummy in gx.builtins:
                self.visit(Class(dummy, [], None, Pass()))

        if self.module.ident != 'builtin':
            if sys.version.startswith('2.5') or sys.version.startswith('2.6'): n = From('builtin', [('*', None)], None)
            else: n = From('builtin', [('*', None)])
            mv.importnodes.append(n)
            self.visit(n)

        # --- __name__
        if self.module.ident != 'builtin':
            namevar = defaultvar('__name__', None)
            gx.types[inode(namevar)] = set([(defclass('str_'),0)]) 

        # --- forward class references
        for child in node.getChildNodes():
            if isinstance(child, Stmt):
                for n in child.nodes:
                    if isinstance(n, Class):
                        #print 'class!!', n.name
                        check_redef(n) 
                        newclass = class_(n)
                        self.classes[n.name] = newclass
                        mv.classes[n.name] = newclass
                        newclass.module = self.module
                        newclass.parent = static_class(newclass)
         
        # --- visit children
        for child in node.getChildNodes():
            if isinstance(child, Stmt):
                mv.importnodes.extend([n for n in child.nodes if isinstance(n, (Import, From))])
            self.visit(child, None)

        # --- register classes
        for cl in mv.classes.values():
            gx.allclasses.add(cl)
            # add '_NR' to duplicate class names
            cl_list = gx.nameclasses.setdefault(cl.ident, [])
            cl.cpp_name = cl.ident
            cl_list.append(cl)
            if len(cl_list) > 1:
                for (i, cl) in enumerate(cl_list):
                    cl.cpp_name = cl.ident + '_' + str(i)

        # --- inheritance expansion

        # determine base classes
        for cl in self.classes.values():
            for node in cl.node.bases: # XXX getattr
                if node.name in self.classes:
                    ancestor = self.classes[node.name]
                else:
                    ancestor = self.ext_classes[node.name]

                cl.bases.append(ancestor)
                ancestor.children.append(cl)

        # for each base class, duplicate methods
        for cl in self.classes.values():
            for ancestor in cl.ancestors():
                for func in ancestor.funcs.values():
                    if not func.node or func.inherited: continue

                    #print 'inherit', func, ancestor, cl
                    #print func.ident, ancestor.ident

                    ident = func.ident
                    if ident in cl.funcs: 
                        ident += ancestor.ident+'__'

                    # deep-copy AST Function nodes
                    func_copy = copy.deepcopy(func.node)
                    inherit_rec(func.node, func_copy)

                    #print 'inherit func in', func.ident, mv.module, func.mv.module
                    tempmv, mv = mv, func.mv
                    #print 'tempmv', mv.module
                    self.visitFunction(func_copy, cl, inherited_from=ancestor)
                    mv = tempmv

                    # maintain relation with original
                    gx.inheritance_relations.setdefault(func, []).append(cl.funcs[ident])
                    cl.funcs[ident].inherited = func.node
                    func_copy.name = ident

    def visitImport(self, node, func=None):
        if not node in mv.importnodes: # XXX use (func, node) as parent..
            error("please place all imports (no 'try:' etc) at the top of the file", node)

        for (name, pseudonym) in node.names:
            if not pseudonym: pseudonym = name
            var = defaultvar(pseudonym, None)
            var.imported = True

            mod = self.analyzeModule(name, pseudonym, node)
            gx.types[inode(var)] = set([(mod,0)]) 

    def visitFrom(self, node, parent=None):
        if not node in mv.importnodes: # XXX use (func, node) as parent..
            error("please place all imports (no 'try:' etc) at the top of the file", node)

        mod = self.analyzeModule(node.modname, node.modname, node)

        for (name, pseudonym) in node.names:
            if name == '*':
                self.ext_funcs.update(mod.funcs)
                self.ext_classes.update(mod.classes)

                for name, extvar in mod.mv.globals.items(): 
                    if not extvar.imported and not name in ['__name__']:
                        var = defaultvar(name, None) # XXX merge
                        var.imported = True
                        var.invisible = True
                        self.addconstraint((inode(extvar), inode(var)), None)

                continue

            if not pseudonym: pseudonym = name
            if name in mod.funcs:
                self.ext_funcs[pseudonym] = mod.funcs[name]
            elif name in mod.classes:
                self.ext_classes[pseudonym] = mod.classes[name]
            elif name in mod.mv.globals:
                extvar = mod.mv.globals[name]
                if not extvar.imported:
                    var = defaultvar(pseudonym, None)
                    var.imported = True
                    var.invisible = True
                    self.addconstraint((inode(extvar), inode(var)), None)
            else:
                error("no identifier '%s' in module '%s'" % (name, node.modname), node)

    def analyzeModule(self, name, pseud, node):
        #print 'analyze', name, gx.modules.keys()
        if name in gx.modules: # XXX to module(..)
            mod = gx.modules[name]
        else:
            mod = module(name, None, mv.module, node)

        self.imports[pseud] = mod
        return mod

    def visitFunction(self, node, parent=None, is_lambda=False, inherited_from=None):
        if node.varargs or node.kwargs or [x for x in node.argnames if not isinstance(x, str)]: 
            error('argument (un)packing is not supported', node)

        func = function(node, parent, inherited_from)

        if isinstance(parent, function):
            error('nested functions are not supported', node)

        if not is_method(func): check_redef(node)
        elif func.ident in func.parent.funcs and func.ident not in ['__getattr__', '__setattr__']: # XXX
            error("function/class redefinition is not allowed ('%s')" % func.ident, node)

        if not parent: 
            if is_lambda: self.lambdas[func.ident] = func
            else: self.funcs[func.ident] = func
        else:
            if not func.formals or func.formals[0] != 'self':
                error("formal arguments of method must start with 'self'", node)
            if not func.mv.module.builtin and func.ident in ['__new__', '__getattr__', '__setattr__', '__radd__', '__rsub__', '__rmul__', '__rdiv__', '__rtruediv__', '__rfloordiv__', '__rmod__', '__rdivmod__', '__rpow__', '__rlshift__', '__rrshift__', '__rand__', '__rxor__', '__ror__', '__iter__']:
                error("'%s' is not supported" % func.ident, node, warning=True)

        formals = func.formals[:]
        if node.kwargs: func.kwargs = formals.pop()
        if node.varargs: func.varargs = formals.pop()
        func.defaults = node.defaults

        for formal in func.formals: 
            var = defaultvar(formal, func) 
            var.formal_arg = True
            
            if formal == func.varargs:
                # star argument 
                tnode = Tuple([])
                self.constructor(tnode, 'tuple', func)
                gx.empty_constructors.remove(tnode) # XXX research bad interaction
                self.addconstraint((inode(tnode), inode(var)), func)

            elif formal == func.kwargs:
                # dict argument
                dnode = Dict([])
                self.constructor(dnode, 'dict', func)
                self.addconstraint((inode(dnode), inode(var)), func)

        for child in node.getChildNodes():
            if child not in func.defaults:
                self.visit(child, func)

        for default in func.defaults:
            if func.mv.module.builtin:
                self.visit(default, func)
            else:
                self.visit(default, None) # defaults are global!! (XXX except when modeling..)

        # --- add implicit 'return None' if no return expressions 
        if not func.ident == '__init__' and not func.returnexpr:
            func.fakeret = Return(Name('None'))
            self.visit(func.fakeret, func)

        # --- flow return expressions together into single node
        func.retnode = retnode = cnode(node, parent=func)
        gx.types[retnode] = set()

        for expr in func.returnexpr:
            self.addconstraint((inode(expr), inode(node)), func)

        # --- register function
        if isinstance(parent, class_): 
            defaultvar('self', func)
            parent.funcs[func.ident] = func

    def visitLambda(self, node, func=None):
        name = '__lambda'+str(len(self.lambdas))+'__'
        self.lambdaname[node] = name
        try:
            fakenode = Function(None, name, node.argnames, node.defaults, node.flags, None, Return(node.code))
        except TypeError:
            fakenode = Function(name, node.argnames, node.defaults, node.flags, None, Return(node.code))
 
        self.visit(fakenode, None, True)

        newnode = cnode(node, parent=func)
        newnode.copymetoo = True
        gx.types[newnode] = set([(self.lambdas[name],0)])

    def visitAnd(self, node, func=None): # XXX merge
        newnode = cnode(node, parent=func)
        gx.types[newnode] = set()
        for child in node.getChildNodes():
            self.visit(child, func)
            self.addconstraint((inode(child), newnode), func)
            tvar = self.tempvar(child, func)
            self.addconstraint((newnode, inode(tvar)), func)

    def visitOr(self, node, func=None):
        newnode = cnode(node, parent=func)
        gx.types[newnode] = set() 
        for child in node.getChildNodes():
            self.visit(child, func)
            self.addconstraint((inode(child), newnode), func)
            tvar = self.tempvar(child, func)
            self.addconstraint((newnode, inode(tvar)), func)

    def visitIf(self, node, func=None):
        for test in node.tests:
            faker = CallFunc(Name('bool'), [test[0]])
            self.visit(faker, func)
            self.visit(test[1], func)
        if node.else_:
           self.visit(node.else_, func)

    def visitIfExp(self, node, func=None):
        newnode = cnode(node, parent=func)
        gx.types[newnode] = set() 

        for child in node.getChildNodes():
            self.visit(child, func)

        self.addconstraint((inode(node.then), newnode), func)
        self.addconstraint((inode(node.else_), newnode), func)

    def visitGlobal(self, node, func=None):
        func.globals += node.names

    def visitList(self, node, func=None):
        self.constructor(node, 'list', func)

    def visitDict(self, node, func=None):
        self.constructor(node, 'dict', func)

        if node.items: # XXX library bug
            node.lineno = node.items[0][0].lineno

    def visitNot(self, node, func=None):
        gx.types[cnode(node, parent=func)] = set([(defclass('int_'),0)])  # XXX new type?
        self.visit(node.expr, func)

    def visitBackquote(self, node, func=None):
        self.fakefunc(node, node.expr, '__repr__', [], func)

    def visitTuple(self, node, func=None):
        if len(node.nodes) == 2:
            self.constructor(node, 'tuple2', func)
        else:
            self.constructor(node, 'tuple', func)

    def visitSubscript(self, node, func=None): # XXX merge __setitem__, __getitem__
        #if len(node.subs) > 1:
        #    error('multidimensional subscripting is not supported', node)

        if len(node.subs) > 1:
            subscript = Tuple(node.subs)
            #inode(node).faketuple = subscript
        else:
            subscript = node.subs[0]

        if isinstance(subscript, Ellipsis): # XXX also check at setitem
            error('ellipsis is not supported', node)

        if isinstance(subscript, Sliceobj):
            self.slice(node, node.expr, subscript.nodes, func)
        else:
            if node.flags == 'OP_DELETE':
                self.fakefunc(node, node.expr, '__delitem__', [subscript], func) 
            elif len(node.subs) > 1:
                self.fakefunc(node, node.expr, '__getitem__', [subscript], func) 
            else:
                ident = get_ident(subscript) # XXX should model __getitem__ always..
                self.fakefunc(node, node.expr, ident, [subscript], func) 

    def visitSlice(self, node, func=None):
        self.slice(node, node.expr, [node.lower, node.upper, None], func)

    def slice(self, node, expr, nodes, func, replace=None):
        nodes2 = slicenums(nodes)
        if replace:
            self.fakefunc(node, expr, '__setslice__', nodes2+[replace], func)
        elif node.flags == 'OP_DELETE':
            self.fakefunc(node, expr, '__delete__', nodes2, func)
        else:
            self.fakefunc(node, expr, '__slice__', nodes2, func)

    def visitUnarySub(self, node, func=None):
        self.fakefunc(node, node.expr, '__neg__', [], func)

    def visitCompare(self, node, func=None):
        newnode = cnode(node, parent=func)
        gx.types[newnode] = set([(defclass('int_'),0)]) # XXX new type?

        self.visit(node.expr, func)

        left = node.expr
        for op, right in node.ops:
            self.visit(right, func)

            if op == '<': msg = '__lt__'
            elif op == '>': msg = '__gt__'
            elif op in ['in','not in']: msg = '__contains__'
            elif op in ['!=', 'is not']: msg = '__ne__'
            elif op in ['==', 'is']: msg = '__eq__'
            elif op == '<=': msg = '__le__'
            elif op == '>=': msg = '__ge__'
            else:
                print str(node.lineno)+': unsupported operator \''+op+'\''
                return

            if msg == '__contains__':
                self.fakefunc(node, right, msg, [left], func)
            else:
                self.fakefunc(node, left, msg, [right], func)

            left = right

        # tempvars, e.g. (t1=fun())
        for term in node.ops[:-1]:
            if not isinstance(term[1], (Name,Const)):
                tvar = self.tempvar(term[1], func)
                self.addconstraint((inode(term[1]), inode(tvar)), func)

    def visitBitand(self, node, func=None):
        self.visitbitpair(node, augmsg(node, 'and'), func)

    def visitBitor(self, node, func=None):
        self.visitbitpair(node, augmsg(node, 'or'), func)
        
    def visitBitxor(self, node, func=None):
        self.visitbitpair(node, augmsg(node, 'xor'), func)

    def visitbitpair(self, node, msg, func=None):
        newnode = cnode(node, parent=func)
        gx.types[inode(node)] = set()
        
        left = node.nodes[0]
        for right in node.nodes[1:]:
            faker = self.fakefunc(node, left, msg, [right], func) # XXX node
            self.addconstraint((inode(faker), inode(node)), func) # XXX beh
            left = right
        
    def visitAdd(self, node, func=None):
        self.fakefunc(node, node.left, augmsg(node, 'add'), [node.right], func)

    def visitInvert(self, node, func=None):
        self.fakefunc(node, node.expr, '__invert__', [], func)

    def visitRightShift(self, node, func=None):
        self.fakefunc(node, node.left, augmsg(node, 'rshift'), [node.right], func)

    def visitLeftShift(self, node, func=None):
        self.fakefunc(node, node.left, augmsg(node, 'lshift'), [node.right], func)

    def visitAugAssign(self, node, func=None): # a[b] += c -> a[b] = a[b]+c, using tempvars to handle sidefx
        newnode = cnode(node, parent=func)
        gx.types[newnode] = set()

        clone = copy.deepcopy(node)
        lnode = node.node

        if isinstance(node.node, Name): 
            blah = AssName(clone.node.name, 'OP_ASSIGN') 
        elif isinstance(node.node, Getattr): 
            blah = AssAttr(clone.node.expr, clone.node.attrname, 'OP_ASSIGN')
        elif isinstance(node.node, Subscript): 
            t1 = self.tempvar(node.node.expr, func)
            a1 = Assign([AssName(t1.name, 'OP_ASSIGN')], node.node.expr)
            self.visit(a1, func)
            self.addconstraint((inode(node.node.expr), inode(t1)), func)

            if len(node.node.subs) > 1: subs = Tuple(node.node.subs)
            else: subs = node.node.subs[0]
            t2 = self.tempvar(subs, func)
            a2 = Assign([AssName(t2.name, 'OP_ASSIGN')], subs)

            self.visit(a1, func)
            self.visit(a2, func)
            self.addconstraint((inode(subs), inode(t2)), func)

            inode(node).temp1 = t1.name
            inode(node).temp2 = t2.name
            inode(node).subs = subs

            blah = Subscript(Name(t1.name), 'OP_APPLY', [Name(t2.name)])
            lnode = Subscript(Name(t1.name), 'OP_APPLY', [Name(t2.name)])
        else:
            error('unsupported type of assignment', node)
        
        if node.op == '-=': blah2 = Sub((lnode, node.expr))
        if node.op == '+=': blah2 = Add((lnode, node.expr))
        if node.op == '|=': blah2 = Bitor((lnode, node.expr))
        if node.op == '&=': blah2 = Bitand((lnode, node.expr))
        if node.op == '^=': blah2 = Bitxor((lnode, node.expr))
        if node.op == '**=': blah2 = Power((lnode, node.expr))
        if node.op == '<<=': blah2 = LeftShift((lnode, node.expr))
        if node.op == '>>=': blah2 = RightShift((lnode, node.expr))
        if node.op == '%=': blah2 = Mod((lnode, node.expr))
        if node.op == '*=': blah2 = Mul((lnode, node.expr))
        if node.op == '/=': blah2 = Div((lnode, node.expr))
        if node.op == '//=': blah2 = FloorDiv((lnode, node.expr))
    
        blah2.augment = True

        assign = Assign([blah], blah2)
        register_node(assign, func)
        inode(node).assignhop = assign
        self.visit(assign, func)

    def visitSub(self, node, func=None):
        self.fakefunc(node, node.left, augmsg(node, 'sub'), [node.right], func)

    def visitMul(self, node, func=None):
        self.fakefunc(node, node.left, augmsg(node, 'mul'), [node.right], func)

    def visitDiv(self, node, func=None):
        self.fakefunc(node, node.left, augmsg(node, 'div'), [node.right], func)

    def visitFloorDiv(self, node, func=None):
        self.fakefunc(node, node.left, augmsg(node, 'floordiv'), [node.right], func)

    def visitPower(self, node, func=None):
        self.fakefunc(node, node.left, '__pow__', [node.right], func)

    def visitMod(self, node, func=None):
        if isinstance(node.left, Const) and isinstance(node.left.value, str):
            for i, c in enumerate(node.left.value):
                if c == '%' and i+1 < len(node.left.value) and node.left.value[i+1] == '(':
                    error("mapping keys ('%(..)') are not supported", node.left)

        if isinstance(node.right, Tuple):
            self.fakefunc(node, node.left, '__mod__', [], func)
            for child in node.right.getChildNodes():
                self.visit(child, func)
        else:
            self.fakefunc(node, node.left, '__mod__', [node.right], func)

    def visitPrintnl(self, node, func=None):
        self.visitPrint(node, func)

    def visitPrint(self, node, func=None):
        pnode = cnode(node, parent=func)
        gx.types[pnode] = set()

        for child in node.getChildNodes():
            self.visit(child, func)
            newnode = inode(child)
            pnode.fakenodes.append(newnode)

            self.fakefunc(newnode, child, '__str__', [], func)

    def tempvar(self, node, func=None):
        if node in gx.parent_nodes:
            varname = self.tempcount[gx.parent_nodes[node]]
        elif node in self.tempcount: # XXX investigate why this happens (patrick down)
            varname = self.tempcount[node]
        else:
            varname = '__'+str(len(self.tempcount))

        var = defaultvar(varname, func) 
        self.tempcount[node] = varname
        return var

    def visitRaise(self, node, func=None):
        if node.expr1 == None: error('first argument of raise cannot be None', node)
        elif node.expr3 != None: error('third argument of raise not supported', node)

        if isinstance(node.expr1, Name):
            name = node.expr1.name
            if not lookupvar(name, func) and not (name in mv.classes or name in mv.ext_classes):
                error("no such class: '%s'" % name, node)

        for child in node.getChildNodes():
            self.visit(child, func)

    def visitTryExcept(self, node, func=None):
        for handler in node.handlers:
            if not handler[0]: continue

            if isinstance(handler[0], Tuple):
                pairs = [(n, handler[1]) for n in handler[0].nodes]
            else:
                pairs = [(handler[0], handler[1])]

            for (h0, h1) in pairs:
                if isinstance(h0, Name): 
                    clname = h0.name
                    if clname in ['int','float','class']: clname += '_'
                    if not (clname in mv.classes or clname in mv.ext_classes):
                        error("no such class: '%s'" % clname, node)
                    cl = defclass(clname)

                else: # Getattr
                    if not isinstance(h0.expr, Name):
                        error('this type of exception is not supported', h0)

                    cl = gx.modules[h0.expr.name].classes[h0.attrname]

                if isinstance(h1, AssName):
                    var = defaultvar(h1.name, func) 
                else:
                    var = self.tempvar(h0, func)

                var.invisible = True
                inode(var).copymetoo = True
                gx.types[inode(var)] = set([(cl, 1)])

        for child in node.getChildNodes():
            self.visit(child, func)

        # else
        if node.else_:
            elsevar = self.tempvar(node.else_, func)
            gx.types[inode(elsevar)] = set([(defclass('int_'),0)])
            inode(elsevar).copymetoo = True

    def visitTryFinally(self, node, func=None):
        error("'try..finally' is not supported", node)

    def visitYield(self, node, func):
        if func.parent:
            error("generator _methods_ are not supported", node)

        func.isGenerator = True
        func.yieldNodes.append(node)

        self.visit(Return(CallFunc(Name('__iter'), [node.value])), func) 

    def visitFor(self, node, func=None):
        # --- iterable contents -> assign node
        assnode = cnode(node.assign, parent=func)
        gx.types[assnode] = set()

        get_iter = CallFunc(Getattr(node.list, '__iter__'), [])
        fakefunc = CallFunc(Getattr(get_iter, 'next'), [])

        self.visit(fakefunc, func)
        self.addconstraint((inode(fakefunc), assnode), func)

        # --- assign node -> variables  XXX merge into assign_pair
        if isinstance(node.assign, AssName):
            # for x in..
            if node.assign.name == '_': 
                lvar = self.tempvar((node.assign,1), func)
            else:
                lvar = defaultvar(node.assign.name, func)
            self.addconstraint((assnode, inode(lvar)), func)

        elif isinstance(node.assign, AssAttr): # XXX experimental :)
            # for expr.x in..
            cnode(node.assign, parent=func)

            gx.assign_target[node.assign.expr] = node.assign.expr # XXX multiple targets possible please
            fakefunc2 = CallFunc(Getattr(node.assign.expr, '__setattr__'), [Const(node.assign.attrname), fakefunc])
            self.visit(fakefunc2, func)

        elif isinstance(node.assign, (AssTuple, AssList)):
            # for (a,b, ..) in.. 
            self.tuple_flow(node.assign, node.assign, func)
        else:
            error('unsupported type of assignment', node)

        # --- for i in range(..) XXX i should not be modified.. use tempcounter; two bounds
        if fastfor(node):
            ivar = self.tempvar(node.assign, func) # index var
            
            self.addconstraint((assnode, inode(ivar)), func)

            evar = self.tempvar(node.list, func) # expr var
            self.addconstraint((inode(node.list.args[0]), inode(evar)), func)

           # print 'ff', ivar, evar

            if len(node.list.args) == 3 and not isinstance(node.list.args[2], (Const, UnarySub, Name)): # XXX merge with ListComp
                for arg in node.list.args:
                    if not isinstance(arg, (Const, UnarySub, Name)): # XXX create func for better check
                        tvar = self.tempvar(arg, func)
                        self.addconstraint((inode(arg), inode(tvar)), func)

        # --- temp vars for list, iter
        else:
            ovar = self.tempvar(node, func)
            self.addconstraint((inode(node.list), inode(ovar)), func) # node.list

            itervar = self.tempvar((node,1), func)
            self.addconstraint((inode(get_iter), inode(itervar)), func)

            xvar = self.tempvar(node.list, func)
            gx.types[inode(xvar)] = set([(defclass('int_'),0)])
            inode(xvar).copymetoo = True

        # --- for-else
        if node.else_:
            elsevar = self.tempvar(node.else_, func)
           # print 'elsevar', elsevar
            gx.types[inode(elsevar)] = set([(defclass('int_'),0)])
            inode(elsevar).copymetoo = True

            self.visit(node.else_, func)

        # --- loop body
        gx.loopstack.append(node)
        self.visit(node.body, func)
        gx.loopstack.pop()
        self.for_in_iters.append(node.list)

    def visitWhile(self, node, func=None):
        gx.loopstack.append(node)
        for child in node.getChildNodes():
            self.visit(child, func)
        gx.loopstack.pop()

        if node.else_:
            elsevar = self.tempvar(node.else_, func)
            gx.types[inode(elsevar)] = set([(defclass('int_'),0)])
            inode(elsevar).copymetoo = True

            self.visit(node.else_, func)

    def visitListComp(self, node, func=None):
        # --- [expr for iter in list for .. if cond ..]
        lcfunc = function()
        lcfunc.listcomp = True
        lcfunc.ident = 'l.c.' # XXX
        lcfunc.parent = func

        for qual in node.quals:
            # iter
            assign = qual.assign
            gx.types[cnode(assign, parent=func)] = set()

            # list.unit->iter
            get_iter = CallFunc(Getattr(qual.list, '__iter__'), [])
            fakefunc = CallFunc(Getattr(get_iter, 'next'), [])

            if isinstance(qual.list, Name) or fastfor(qual): # XXX merge
                self.visit(fakefunc, lcfunc)
                self.addconstraint((inode(fakefunc), inode(assign)), lcfunc)
            else:
                self.visit(fakefunc, func)
                self.addconstraint((inode(fakefunc), inode(assign)), func)

            if isinstance(assign, AssName): # XXX merge with visitFor
                if assign.name == '_':
                    lvar = self.tempvar((assign,1), lcfunc)
                else:
                    lvar = defaultvar(assign.name, lcfunc) # XXX str or Name?
                self.addconstraint((inode(assign), inode(lvar)), lcfunc)
            else: # AssTuple, AssList
                self.tuple_flow(assign, assign, lcfunc)

            if fastfor(qual): #XXX merge with visitFor above
                ivar = self.tempvar(assign, lcfunc) # index var 
                self.addconstraint((inode(assign), inode(ivar)), lcfunc)

                evar = self.tempvar(qual.list, lcfunc) # expr var
                self.addconstraint((inode(qual.list.args[0]), inode(evar)), lcfunc)

                if len(qual.list.args) == 3 and not isinstance(qual.list.args[2], (Const, UnarySub, Name)): # XXX merge with ListComp
                    for arg in qual.list.args:
                        if not isinstance(arg, (Const, UnarySub, Name)): # XXX create func for better check
                            tvar = self.tempvar(arg, lcfunc)
                            self.addconstraint((inode(arg), inode(tvar)), lcfunc)

            else:
                ovar = self.tempvar(qual.list, lcfunc)
                self.addconstraint((inode(qual.list), inode(ovar)), lcfunc)

                itervar = self.tempvar((qual,1), lcfunc)
                self.addconstraint((inode(get_iter), inode(itervar)), lcfunc)

                xvar = self.tempvar(qual) 
                gx.types[inode(xvar)] = set([(defclass('int_'),0)])
                inode(xvar).copymetoo = True

            # cond
            for child in qual.ifs:
                self.visit(child, lcfunc)

            self.for_in_iters.append(qual.list)

        # create list instance
        self.instance(node, defclass('list'), func)

        # expr->instance.unit
        self.visit(node.expr, lcfunc) 
        self.add_dynamic_constraint(node, node.expr, 'unit', lcfunc) 

        lcfunc.ident = 'list_comp_'+str(len(self.listcomps))
        self.listcomps.append((node, lcfunc, func))

    def visitReturn(self, node, func):
        self.visit(node.value, func)
        func.returnexpr.append(node.value)
        if isinstance(node.value, Const) and node.value.value == None: 
            return

        newnode = cnode(node, parent=func)
        gx.types[newnode] = set()
        if isinstance(node.value, Name):
            func.retvars.append(node.value.name)
        
    def visitAssign(self, node, func=None):
        #print 'assign', node, node.nodes

        # --- class-level attribute # XXX merge below
        if isinstance(func, class_):
            parent = func # XXX move above
            if len(node.nodes) > 1 or not isinstance(node.nodes[0], AssName): 
                error('at the class-level, only simple assignments are supported', node)

            lvar = defaultvar(node.nodes[0].name, parent.parent)

            self.visit(node.expr, None)
            self.addconstraint((inode(node.expr), inode(lvar)), None)
            lvar.initexpr = node.expr

            return

        newnode = cnode(node, parent=func)
        gx.types[newnode] = set()

        # --- a,b,.. = c,(d,e),.. = .. = expr 
        for target_expr in node.nodes:
            pairs = assign_rec(target_expr, node.expr)

            for (lvalue, rvalue) in pairs:
                #print 'pair', lvalue, rvalue

                # expr[expr] = expr
                if isinstance(lvalue, Subscript) and not isinstance(lvalue.subs[0], Sliceobj):
                    self.assign_pair(lvalue, rvalue, func) # XXX use here generally, and in tuple_flow

                # expr.attr = expr
                elif isinstance(lvalue, AssAttr):
                    self.assign_pair(lvalue, rvalue, func)

                    # filter flow 
                    if not mv.module.builtin: # XXX
                        rvar = None
                        if isinstance(rvalue, Name):
                            rvar = lookupvar(rvalue.name, func) 
                        elif isinstance(rvalue, Getattr) and isinstance(rvalue.expr, Name) and rvalue.expr.name == 'self':
                            rvar = defaultvar(rvalue.attrname, func.parent)

                        if isinstance(lvalue.expr, Name) and lvalue.expr.name == 'self':
                            lvar = defaultvar(lvalue.attrname, func.parent)
                        else: 
                            lvar = None 
            
                        if rvar:
                            gx.assignments.append((lvar, rvar))

                # name = expr
                elif isinstance(lvalue, AssName):
                    if (rvalue, 0, 0) not in gx.cnode: # XXX generalize 
                        self.visit(rvalue, func)

                    if lvalue.name != '_':
                        self.visit(lvalue, func)

                        if func and lvalue.name in func.globals:
                            lvar = defaultvar(lvalue.name, None)
                        else:
                            lvar = defaultvar(lvalue.name, func)

                        self.addconstraint((inode(rvalue), inode(lvar)), func)

                    # filter flow
                    if not mv.module.builtin: # XXX
                        if isinstance(rvalue, Name): # XXX
                            gx.assignments.append((lookupvar(lvalue.name, func), lookupvar(rvalue.name, func))) 
                        if isinstance(rvalue, Getattr) and isinstance(rvalue.expr, Name) and rvalue.expr.name == 'self':
                            gx.assignments.append((lookupvar(lvalue.name, func), defaultvar(rvalue.attrname, func.parent)))

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
                        if (child,0,0) not in gx.cnode: # (a,b) = (1,2): (1,2) never visited
                            continue
                        if not isinstance(child, Const) and not (isinstance(child, Name) and child.name == 'None'):
                            tvar = self.tempvar(child, func)
                            self.addconstraint((inode(child), inode(tvar)), func)
            elif not isinstance(node.expr, Const) and not (isinstance(node.expr, Name) and node.expr.name == 'None'):
                tvar = self.tempvar(node.expr, func)
                self.addconstraint((inode(node.expr), inode(tvar)), func)

    def assign_pair(self, lvalue, rvalue, func):
        # expr[expr] = expr
        if isinstance(lvalue, Subscript) and not isinstance(lvalue.subs[0], Sliceobj):
            if len(lvalue.subs) > 1:
                subscript = Tuple(lvalue.subs)
            else:
                subscript = lvalue.subs[0]
            
            fakefunc = CallFunc(Getattr(lvalue.expr, '__setitem__'), [subscript, rvalue])
            self.visit(fakefunc, func)
            inode(lvalue.expr).fakefunc = fakefunc
            if len(lvalue.subs) > 1:
                inode(lvalue.expr).faketuple = subscript

            if not isinstance(lvalue.expr, Name):
                var = self.tempvar(lvalue.expr, func)
                self.addconstraint((inode(lvalue.expr), inode(var)), func)

        # expr.attr = expr
        elif isinstance(lvalue, AssAttr):
            cnode(lvalue, parent=func)

            gx.assign_target[rvalue] = lvalue.expr
            fakefunc = CallFunc(Getattr(lvalue.expr, '__setattr__'), [Const(lvalue.attrname), rvalue])

            self.visit(fakefunc, func)

    def tuple_flow(self, lvalue, rvalue, func=None):
        #print 'tuple flow', lvalue, rvalue

        tvar = self.tempvar(lvalue, func)
        self.addconstraint((inode(rvalue), inode(tvar)), func)

        if isinstance(lvalue, (AssTuple, AssList)):
            lvalue = lvalue.nodes
        for (i, item) in enumerate(lvalue):
            fakenode = cnode((item,), parent=func) # fake node per item, for multiple callfunc triggers
            gx.types[fakenode] = set()
            self.addconstraint((inode(rvalue), fakenode), func)

            fakefunc = CallFunc(fakeGetattr3(rvalue, get_ident(Const(i))), [Const(i)])

            fakenode.callfuncs.append(fakefunc)
            self.visit(fakefunc, func)

            if isinstance(item, AssName):
                if item.name != '_':
                    lvar = defaultvar(item.name, func)
                    self.addconstraint((inode(fakefunc), inode(lvar)), func)
            elif isinstance(item, (Subscript, AssAttr)):
                self.assign_pair(item, fakefunc, func)
            elif isinstance(item, (AssTuple, AssList)): # recursion
                self.tuple_flow(item, fakefunc, func)
            else:
                error('unsupported type of assignment', item) 

    def visitCallFunc(self, node, func=None): # XXX analyze_callfunc? XXX clean up!!
        newnode = cnode(node, parent=func) 

        # --- identify target

        if isinstance(node.node, Getattr): # XXX import math; math.e
            # parent constr 
            if isinstance(node.node.expr, Name) and inode(node).parent:
                cl, ident = func.parent, node.node.expr.name
                
                if isinstance(cl, class_) and ident in [b.name for b in cl.node.bases] and not isinstance(node.node,fakeGetattr): # XXX fakegetattr
                    func.parent_constr = [ident] + node.args[1:]

            # method call
            if isinstance(node.node, fakeGetattr): # XXX butt ugly
                self.visit(node.node, func)
            elif isinstance(node.node, fakeGetattr2): 
                gx.types[newnode] = set() # XXX move above

                self.callfuncs.append((node, func))

                for arg in node.args: 
                    inode(arg).callfuncs.append(node) # this one too

                return
            elif isinstance(node.node, fakeGetattr3):
                pass
            else:
                self.visit(node.node, func) 
                inode(node.node).callfuncs.append(node) # XXX iterative dataflow analysis: move there?
                inode(node.node).fakert = True
                #inode(node.node).fakert.parent_callfunc = node

            ident = node.node.attrname
            inode(node.node.expr).callfuncs.append(node) # XXX iterative dataflow analysis: move there?

            if isinstance(node.node.expr, Name) and node.node.expr.name in mv.imports and node.node.attrname == '__getattr__': # XXX analyze_callfunc
                if node.args[0].value in mv.imports[node.node.expr.name].mv.globals: # XXX bleh
                    self.addconstraint((inode(mv.imports[node.node.expr.name].mv.globals[node.args[0].value]), newnode), func)


        elif isinstance(node.node, Name):
            # direct call
            ident = node.node.name

            if ident in ['reduce', 'map', 'filter', 'apply', 'getattr', 'setattr'] and ident not in mv.funcs:
                error("'%s' function is not supported" % ident, node.node)
            if ident in ['slice']:
                error("'%s' function is not supported" % ident, node.node)
            if ident == 'dict' and [x for x in node.args if isinstance(x, Keyword)]:
                error('unsupported method of initializing dictionaries', node)

            if ident not in self.funcs and ident not in self.ext_funcs:
                self.visit(node.node, func)
                inode(node.node).callfuncs.append(node) # XXX iterative dataflow analysis: move there
        else:
            self.visit(node.node, func)
            inode(node.node).callfuncs.append(node) # XXX iterative dataflow analysis: move there

        objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(node)

        if constructor and ident == 'defaultdict':
            node.args[0] = CallFunc(node.args[0], []) 

        # --- arguments
        for arg in node.args: 
            if isinstance(arg, Keyword):
                arg = arg.expr
            self.visit(arg, func)
            inode(arg).callfuncs.append(node) # this one too

        if node.star_args or node.dstar_args:
             error('automatic argument unpacking is not supported', node)

        # --- handle instantiation or call
        #objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(node)

        if constructor:
            self.instance(node, constructor, func)
            inode(node).callfuncs.append(node) # XXX see above, investigate
        else:
            gx.types[newnode] = set()

        self.callfuncs.append((node, func))

    def visitClass(self, node, parent=None):
        if parent: 
            error('nested classes are not supported', node)
        if len(node.bases) > 1:
            error('multiple inheritance is not supported', node)

        if not mv.module.builtin: # XXX doesn't have to be Name
            for base in node.bases:
                if not isinstance(base, Name):
                    error('specify base class with identifier for now', node)
                if base.name not in mv.classes and base.name not in mv.ext_classes:
                    error("name '%s' is not defined" % base.name, node)

                if base.name in mv.ext_classes and mv.ext_classes[base.name].mv.module.ident == 'builtin' and base.name not in ['object', 'Exception']: 
                    error('inheritance from builtins is not supported', node)

        if node.name in mv.classes:
            newclass = mv.classes[node.name] # set in visitModule, for forward references
        else:
            check_redef(node) # XXX merge with visitModule
            newclass = class_(node) 
            self.classes[node.name] = newclass
            mv.classes[node.name] = newclass
            newclass.module = self.module
            newclass.parent = static_class(newclass)

        # --- built-in functions
        for cl in [newclass, newclass.parent]:
            for ident in ['__setattr__', '__getattr__']:
                func = function()
                func.ident = ident
                func.parent = cl

                if ident == '__setattr__':
                    func.formals = ['name','whatsit']
                    retexpr = Return(Name('None'))
                    self.visit(retexpr, func)
                elif ident == '__getattr__':
                    func.formals = ['name']

                cl.funcs[ident] = func

        # --- built-in attributes
        if 'class_' in mv.classes or 'class_' in mv.ext_classes:
            var = defaultvar('__class__', newclass)
            var.invisible = True
            gx.types[inode(var)] = set([(defclass('class_'), defclass('class_').dcpa)])
            gx.typeclass[defclass('class_').dcpa] = newclass
            defclass('class_').dcpa += 1

        for child in node.code.getChildNodes():
            self.visit(child, self.classes[node.name])

        # --- __iadd__ etc.
        if not newclass.mv.module.builtin or newclass.ident in ['int_', 'float_', 'str_', 'tuple']: 
            msgs = ['add', 'mul'] # XXX mod, pow
            if newclass.ident in ['int_', 'float_']: msgs += ['sub', 'div', 'floordiv']
            if newclass.ident in ['int_']: msgs += ['lshift', 'rshift', 'and', 'xor', 'or']
            for msg in msgs:
                if not '__i'+msg+'__' in newclass.funcs:
                    try:
                        self.visit(Function(None, '__i'+msg+'__', ['self', 'other'], [], 0, None, Stmt([Return(CallFunc(Getattr(Name('self'), '__'+msg+'__'), [Name('other')], None, None))])), newclass)
                    except TypeError:
                        self.visit(Function('__i'+msg+'__', ['self', 'other'], [], 0, None, Stmt([Return(CallFunc(Getattr(Name('self'), '__'+msg+'__'), [Name('other')], None, None))])), newclass)

        # --- __str__
        if not newclass.mv.module.builtin and not '__str__' in newclass.funcs:
            try:
                self.visit(Function(None, '__str__', ['self'], [], 0, None, Return(CallFunc(Getattr(Name('self'), '__repr__'), []))), newclass)
            except TypeError:
                self.visit(Function('__str__', ['self'], [], 0, None, Return(CallFunc(Getattr(Name('self'), '__repr__'), []))), newclass)
            newclass.funcs['__str__'].invisible = True

    def visitGetattr(self, node, func=None):
        if node.attrname in ['__doc__']:
            error('%s attribute is not supported' % node.attrname, node)

        newnode = cnode(node, parent=func)
        gx.types[newnode] = set()

        fakefunc = CallFunc(fakeGetattr(node.expr, '__getattr__'), [Const(node.attrname)])
        self.visit(fakefunc, func)
        self.addconstraint((gx.cnode[fakefunc,0,0], newnode), func)
        #newnode.fakert = inode(fakefunc)

        self.callfuncs.append((fakefunc, func))

    def visitConst(self, node, func=None):
        if type(node.value) == unicode:
            error('unicode is not supported', node)
        map = {int: 'int_', str: 'str_', float: 'float_', type(None): 'none', long: 'int_'} # XXX 'return' -> Return(Const(None))?
        self.instance(node, defclass(map[type(node.value)]), func)

    def visitName(self, node, func=None):
        newnode = cnode(node, parent=func)
        gx.types[newnode] = set()

        if node.name == '__doc__': 
            error("'%s' attribute is not supported" % node.name, node)
        elif node.name in ['_']:
            error("'%s' cannot be used as variable name" % node.name, node)
       
        if node.name in ['None', 'True', 'False']: 
            if node.name == 'None': # XXX also bools, remove def seed_nodes()
                self.instance(node, defclass('none'), func)
            return

        if func and node.name in func.globals:
            var = defaultvar(node.name, None)
        else:
            var = lookupvar(node.name, func)
            if not var: # XXX define variables before use, or they are assumed to be global
                if node.name in self.funcs: # XXX remove: variable lookup should be uniform
                    gx.types[newnode] = set([(self.funcs[node.name], 0)])
                    self.lambdas[node.name] = self.funcs[node.name]
                elif node.name in self.classes or node.name in self.ext_classes: 
                    if node.name in self.classes: cl = self.classes[node.name] 
                    else: cl = self.ext_classes[node.name]
                    gx.types[newnode] = set([(cl.parent, 0)]) # XXX add warning
                    newnode.copymetoo = True # XXX merge into some kind of 'seeding' function
                elif node.name in ['int', 'float', 'str']: # XXX
                    cl = self.ext_classes[node.name+'_']
                    gx.types[newnode] = set([(cl.parent, 0)]) 
                    newnode.copymetoo = True
                else:
                    var = defaultvar(node.name, None)
        if var:
            self.addconstraint((inode(var), newnode), func)
        

def defclass(name):
    if name in mv.classes: return mv.classes[name]
    else: return mv.ext_classes[name]

def deffunc(name):
    if name in mv.funcs: return mv.funcs[name]
    else: return mv.ext_funcs[name]

def singletype(node, type):
    types = [t[0] for t in inode(node).types()]
    if len(types) == 1 and isinstance(types[0], type):
        return types[0]
    return None

def singletype2(node, ident):
    return [t for t in inode(node).types() if t[0].ident == ident]

def hmcpa(func): 
    got_one = 0
    for dcpa, cpas in func.cp.items():
        if len(cpas) > 1: return len(cpas)
        if len(cpas) == 1: got_one = 1
    return got_one
    
class Bitpair:
    def __init__(self, nodes, msg, inline):
        self.nodes = nodes
        self.msg = msg
        self.inline = inline

# --- code generation visitor; use type information; c++ templates
class generateVisitor(ASTVisitor):
    def __init__(self, module):
        name = module.filename[:-3]
        self.fname = name
        self.out = file(name+'.cpp','w')
        self.indentation = ''
        self.consts = {}
        self.mergeinh = merged(gx.types, inheritance=True) 
        self.module = module
        self.name = module.ident

        self.filling_consts = False
        self.constant_nr = 0

    def insert_consts(self, declare): # XXX ugly
        if not self.consts: return
        self.filling_consts = True

        if declare: suffix = '.hpp'
        else: suffix = '.cpp'

        lines = file(self.fname+suffix,'r').readlines()
        newlines = [] 
        j = -1
        for (i,line) in enumerate(lines):
            if line.startswith('namespace '):
                j = i+1
            newlines.append(line)
        
            if i == j:
                pairs = []
                done = set()
                for (node, name) in self.consts.items():
                    if not name in done and self.mergeinh[node]:
                        ts = typesetreprnew(node, inode(node).parent)
                        if declare: ts = 'extern '+ts
                        pairs.append((ts, name))
                        done.add(name)

                newlines.extend(self.group_declarations(pairs))
                newlines.append('\n')

        newlines2 = [] 
        j = -1
        for (i,line) in enumerate(newlines):
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
                    if self.mergeinh[todo[number]]:
                        name = 'const_'+str(number)
                        self.start('    '+name+' = ')
                        self.visit(todo[number], inode(todo[number]).parent)
                        newlines2.append(self.line+';\n')

                newlines2.append('\n')
        
        file(self.fname+suffix,'w').writelines(newlines2)
        self.filling_consts = False
        
    # --- group pairs of (type, name) declarations, while paying attention to '*'
    def group_declarations(self, pairs):
        group = {}
        for (type, name) in pairs:
            group.setdefault(type, []).append(name)
        
        result = []
        for (type, names) in group.items():
            names.sort(cmp)
            if type.endswith('*'):
                result.append(type+(', *'.join(names))+';\n')
            else:
                result.append(type+(', '.join(names))+';\n')

        return result

    def header_file(self):
        self.out = file(self.module.filename[:-3]+'.hpp','w')
        self.visit(self.module.ast, True)
        self.out.close()

    def classes(self, node):
        return set([t[0].ident for t in inode(node).types()])

    def output(self, text):
        print >>self.out, self.indentation+text

    def start(self, text=None):
        self.line = self.indentation
        if text: self.line += text
    def append(self, text):
        self.line += text
    def eol(self, text=None):
        if text: self.append(text)
        if self.line.strip():
            print >>self.out, self.line+';'

    def indent(self):
        self.indentation += 4*' '
    def deindent(self):
        self.indentation = self.indentation[:-4]

    def connector(self, node, func):
        if singletype(node, module): return '::'

        elif func and func.listcomp:
            return '->'
        elif isinstance(node, Name) and not lookupvar(node.name, func): # XXX
            return '::'

        return '->'

    def declaredefs(self, vars, declare): # XXX use group_declarations
        decl = {}
        for (name,var) in vars:
            if singletype(var, module) or var.invisible: # XXX buh
                continue
            typehu = typesetreprnew(var, var.parent)
            if not typehu or typehu == 'void *': continue 

            decl.setdefault(typehu, []).append(self.cpp_name(name))
        decl2 = []
        for (t,names) in decl.items():
            names.sort(cmp)
            prefix=''
            if declare: prefix='extern '
            if t.endswith('*'):
                decl2.append(prefix+t+(', *'.join(names)))
            else:
                decl2.append(prefix+t+(', '.join(names)))
        return ';\n'.join(decl2)

    def constant_constructor(self, node):
        if isinstance(node, UnarySub):
            node = node.expr
        if isinstance(node, Const) and type(node.value) in [int, float, str]:
            return False

        return self.constant_constructor_rec(node)
       
    def constant_constructor_rec(self, node):
        if isinstance(node, UnarySub):
            node = node.expr

        # --- determine whether built-in constructor call builds a (compound) constant, e.g. [(1,),[1,(1,2)]]
        if isinstance(node, (List, Tuple, Dict)):
            return not False in [self.constant_constructor_rec(child) for child in node.getChildNodes()]

        # --- strings may also be constants of course
        elif isinstance(node, Const) and type(node.value) in [int, float, str]:
            if type(node.value) == str:
                self.get_constant(node)
            return True

        return False

    def find_constants(self):
        # --- determine (compound, non-str) constants
        for callfunc, _ in mv.callfuncs:
            if isinstance(callfunc.node, Getattr) and callfunc.node.attrname in ['__ne__', '__eq__', '__contains__']:
                for node in [callfunc.node.expr, callfunc.args[0]]:
                    if self.constant_constructor(node):
                        self.consts[node] = self.get_constant(node)

        for node in mv.for_in_iters:
            if self.constant_constructor(node):
                self.consts[node] = self.get_constant(node)

        for node in self.mergeinh:
            if isinstance(node, Subscript):
                if self.constant_constructor(node.expr):
                    self.consts[node.expr] = self.get_constant(node.expr)

        #for node in self.mergeinh:
        #    if isinstance(node, (Mul, Add)): # XXX extend, arbitrary methods on constructor? (getitem, find..)
        #        for child in [node.left, node.right]:
        #            if self.constant_constructor(child):
        #                self.consts[child] = self.get_constant(child)

    def get_constant(self, node):
        for other in self.consts:
            if node is other or self.equal_constructor_rec(node, other):
                return self.consts[other]
        
        self.consts[node] = 'const_'+str(self.constant_nr)
        self.constant_nr += 1
        return self.consts[node]
    
    def equal_constructor_rec(self, a, b):
        if isinstance(a, UnarySub) and isinstance(b, UnarySub):
            return self.equal_constructor_rec(a.expr, b.expr)

        if isinstance(a, Const) and isinstance(b, Const):
            for c in (int, float, str):
                if isinstance(a.value, c) and isinstance(b.value, c):
                    return a.value == b.value
        
        for c in (List, Tuple, Dict):
            if isinstance(a, c) and isinstance(b, c) and len(a.getChildNodes()) == len(b.getChildNodes()): 
                return not 0 in [self.equal_constructor_rec(d,e) for (d,e) in zip(a.getChildNodes(), b.getChildNodes())]

        return 0

    def ext_supported(self, types):
        if [t for t in types if not isinstance(t[0], class_)]:
            return False
        if [t for t in types if not t[0].mv.module.ident == 'builtin' or t[0].ident not in ['int_', 'float_', 'str_', 'list', 'tuple', 'tuple2', 'dict', 'set', 'none']]:
            return False
        return True

    def visitModule(self, node, declare=False):
        # --- header file
        if declare: 
            define = self.module.ident.upper()+'_HPP'
            print >>self.out, '#ifndef __'+define
            print >>self.out, '#define __'+define+'\n'

            # --- include header files
            if self.module.dir == '': depth = 0
            else: depth = self.module.dir.count('/')+1
            #print >>self.out, '#include "'+depth*'../'+'builtin_.hpp"'

            includes = get_includes(self.module)
            if 'getopt.hpp' in includes: # XXX
                includes.add('os/__init__.hpp')
                includes.add('os/path.hpp')
                includes.add('stat.hpp')
            if 'os/__init__.hpp' in includes: # XXX
                includes.add('os/path.hpp')
                includes.add('stat.hpp')
            for include in includes:
                print >>self.out, '#include "'+include+'"'
            if includes: print >>self.out

            # --- namespaces
            print >>self.out, 'using namespace __shedskin__;'
            for n in self.module.mod_path+[self.module.ident]:
                print >>self.out, 'namespace __'+n+'__ {'
            print >>self.out
                 
            skip = False
            for child in node.node.getChildNodes():
                if isinstance(child, From): 
                    skip = True
                    mod_id = '__'+'__::__'.join(child.modname.split('.'))+'__'

                    for (name, pseudonym) in child.names:
                        if name == '*':
                            for func in gx.modules[child.modname].funcs.values():
                                if func.cp: 
                                    print >>self.out, 'using '+mod_id+'::'+self.cpp_name(func.ident)+';';
                            for var in gx.modules[child.modname].mv.globals.values():
                                if not var.invisible and not var.imported and not var.name.startswith('__'):
                                    print >>self.out, 'using '+mod_id+'::'+self.cpp_name(var.name)+';';
                            for cl in gx.modules[child.modname].classes:
                                print >>self.out, 'using '+mod_id+'::'+cl+';';

                            continue

                        print >>self.out, 'using '+mod_id+'::'+self.nokeywords(name)+';'
            if skip: print >>self.out

            # class declarations
            gotcl = False
            for child in node.node.getChildNodes():
                if isinstance(child, Class): 
                    gotcl = True
                    cl = defclass(child.name)
                    print >>self.out, template_repr(cl)+'class '+self.nokeywords(cl.ident)+';'

            # --- lambda typedefs
            if gotcl: print >>self.out
            self.func_pointers(True)

            # globals
            defs = self.declaredefs(list(mv.globals.items()), declare=True);
            if defs:
                self.output(defs+';')
                print >>self.out

            # --- class definitions
            for child in node.node.getChildNodes():
                if isinstance(child, Class): self.visitClass(child, True)

            # --- variables
            if self.module != gx.main_module:
                print >>self.out
                for v in self.module.mv.globals.values():
                    if not v.invisible and not v.imported and not v.name in self.module.funcs:
                        print >>self.out, 'extern '+typesetreprnew(v, None)+' '+v.name+';'

            # function declarations
            if self.module != gx.main_module:
                print >>self.out, 'void __init();'
            for child in node.node.getChildNodes():
                if isinstance(child, Function): 
                    func = mv.funcs[child.name]
                    if not self.inhcpa(func):
                    #if not hmcpa(func) and (not func in gx.inheritance_relations or not [1 for f in gx.inheritance_relations[func] if hmcpa(f)]): # XXX merge with visitFunction
                        pass
                    elif not func.mv.module.builtin and not func.ident in ['min','max','zip','sum','__zip2','enumerate']: # XXX latter for test 116
                        self.visitFunction(func.node, declare=True)
            print >>self.out

            for n in self.module.mod_path+[self.module.ident]:
                print >>self.out, '} // module namespace'
            print >>self.out, '#endif'
            return

        # --- external dependencies 
        if self.module.filename.endswith('__init__.py'): # XXX nicer check
            print >>self.out, '#include "__init__.hpp"\n'
        else:
            print >>self.out, '#include "'+'/'.join(self.module.mod_path+[self.module.ident])+'.hpp"\n'

        # --- comments
        if node.doc:
            self.do_comment(node.doc)
            print >>self.out

        # --- namespace
        for n in self.module.mod_path+[self.module.ident]:
            print >>self.out, 'namespace __'+n+'__ {'
        print >>self.out

        # --- globals
        defs = self.declaredefs(list(mv.globals.items()), declare=False);
        if defs:
            self.output(defs+';')
            print >>self.out

        # --- constants: __eq__(const) or ==/__eq(List())
        self.find_constants()

        # --- list comprehensions
        self.listcomps = {}
        for (listcomp,lcfunc,func) in mv.listcomps:
            self.listcomps[listcomp] = (lcfunc, func)
        for (listcomp,lcfunc,func) in mv.listcomps: # XXX cleanup
            parent = func
            while isinstance(parent, function) and parent.listcomp: parent = parent.parent
            if isinstance(parent, function) and not parent.cp:
                continue
            if not func or not func.mv.module.builtin: # not in gx.builtin_funcs:
                self.listcomp_func(listcomp)

        # --- lambdas
        for l in mv.lambdas.values():
            if l.ident not in mv.funcs:
                self.visit(l.node)

        # --- classes 
        for child in node.node.getChildNodes():
            if isinstance(child, Class): self.visitClass(child, False)

        # --- __init
        self.output('void __init() {')
        self.indent()
        if self.module == gx.main_module and not gx.extension_module: self.output('__name__ = new str("__main__");\n')
        else: self.output('__name__ = new str("%s");\n' % self.module.ident)

        if mv.classes:
            for cl in mv.classes.values():
                self.output('cl_'+cl.cpp_name+' = new class_("%s", %d, %d);' % (cl.cpp_name, cl.low, cl.high))

                for var in cl.parent.vars.values():
                    if var.initexpr:
                        self.start()
                        self.visitm(cl.ident+'::'+self.cpp_name(var.name)+' = ', var.initexpr, None)
                        self.eol()

            print >>self.out

        for child in node.node.getChildNodes():
            if isinstance(child, Discard):
                if isinstance(child.expr, Const) and child.expr.value == None: # XXX merge with visitStmt
                    continue
                if isinstance(child.expr, Const) and type(child.expr.value) == str:
                    continue

                self.start('')
                self.visit(child)
                self.eol()

            elif not isinstance(child, (Class, Function)):
                self.do_comments(child)
                self.visit(child)

        self.deindent()
        self.output('}\n')

        for child in node.node.getChildNodes():
            if isinstance(child, Function): 
                self.do_comments(child)
                self.visit(child)

        # --- close namespace
        for n in self.module.mod_path+[self.module.ident]:
            print >>self.out, '} // module namespace'
        print >>self.out

        # --- c++ main/extension module setup
        if self.module == gx.main_module: 
            if gx.extension_module:
                print >>self.out, 'extern "C" {'
                print >>self.out, '#include <Python.h>\n'
                
                funcs = [] # select functions that are called and have copyable arg/return types
                for func in self.module.funcs.values():
                    if not hmcpa(func): # not called
                        continue 
                    builtins = True
                    for formal in func.formals:
                        if not self.ext_supported(self.mergeinh[func.vars[formal]]):
                            builtins = False
    
                    if builtins and self.ext_supported(self.mergeinh[func.retnode.thing]):
                        funcs.append(func)

                for func in funcs:
                    print >>self.out, 'PyObject *%s(PyObject *self, PyObject *args) {' % func.ident
                    print >>self.out, '    if(PyTuple_Size(args) < %d || PyTuple_Size(args) > %d) {' % (len(func.formals)-len(func.defaults), len(func.formals))
                    print >>self.out, '        PyErr_SetString(PyExc_Exception, "invalid number of arguments");'
                    print >>self.out, '        return 0;'
                    print >>self.out, '    }\n' 
                    print >>self.out, '    try {'

                    for i, formal in enumerate(func.formals):
                        self.start('')
                        self.append('        %(type)sarg_%(num)d = (PyTuple_Size(args) > %(num)d) ? __to_ss<%(type)s>(PyTuple_GetItem(args, %(num)d)) : ' % {'type' : typesetreprnew(func.vars[formal], func), 'num' : i})
                        if i >= len(func.formals)-len(func.defaults):
                            defau = func.defaults[i-(len(func.formals)-len(func.defaults))]
                            cast = assign_needs_cast(defau, None, func.vars[formal], func)
                            if cast:
                                self.append('(('+typesetreprnew(func.vars[formal], func)+')')
                            if self.constant_constructor(defau) or (isinstance(defau, Const) and type(defau.value) == str):
                                self.append('__'+func.mv.module.ident+'__::')
                            self.visit(defau, func)
                            if cast:
                                self.append(')')
                        else:
                            self.append('0')
                        self.eol()
                    print >>self.out

                    print >>self.out, '        return __to_py(__'+self.module.ident+'__::'+func.ident+'('+', '.join(['arg_%d' % i for i in range(len(func.formals))])+'));\n' 
                    print >>self.out, '    } catch (Exception *e) {'
                    print >>self.out, '        PyErr_SetString(__to_py(e), e->msg->unit.c_str());'
                    print >>self.out, '        return 0;'
                    print >>self.out, '    }'

                    print >>self.out, '}\n'

                print >>self.out, 'static PyMethodDef %sMethods[] = {' % self.module.ident
                for func in funcs:
                    print >>self.out, '    {"%(id)s", %(id)s, METH_VARARGS, ""},' % {'id': func.ident}
                print >>self.out, '    {NULL, NULL, 0, NULL}        /* Sentinel */\n};\n'

            if gx.extension_module:
                print >>self.out, 'PyMODINIT_FUNC init%s(void) {' % self.module.ident

                vars = []
                for (name,var) in mv.globals.items():
                    if singletype(var, module) or var.invisible: # XXX merge declaredefs 
                        continue
                    typehu = typesetreprnew(var, var.parent)
                    if not typehu or typehu == 'void *': continue 
                    if name.startswith('__'): continue
                    if not self.ext_supported(self.mergeinh[var]): continue

                    vars.append(var)

                for var in vars:
                    print >>self.out, '    __'+self.module.ident+'__::'+self.cpp_name(var.name)+' = 0;'
                if vars: print >>self.out
            else:
                print >>self.out, 'int main(int argc, char **argv) {'

            print >>self.out, '    __shedskin__::__init();'

            for mod in gx.modules.values():
                if mod != gx.main_module and mod.ident != 'builtin':
                    if mod.ident == 'sys':
                        if gx.extension_module:
                            print >>self.out, '    __sys__::__init(0, 0);'
                        else:
                            print >>self.out, '    __sys__::__init(argc, argv);'
                    else:
                        print >>self.out, '    __'+'__::__'.join([n for n in mod.mod_path+[mod.ident]])+'__::__init();' # XXX sep func

            print >>self.out, '    __'+self.module.ident+'__::__init();'
            if gx.extension_module:
                print >>self.out, '\n    PyObject *mod = Py_InitModule("%s", %sMethods);\n' % (self.module.ident, self.module.ident)
                for var in vars:
                    varname = self.cpp_name(var.name)
                    if [1 for t in self.mergeinh[var] if t[0].ident in ['int_', 'float_']]:
                        print >>self.out, '    PyModule_AddObject(mod, "%(name)s", __to_py(%(var)s));' % {'name' : var.name, 'var': '__'+self.module.ident+'__::'+varname}
                    else:
                        print >>self.out, '    if(%(var)s) PyModule_AddObject(mod, "%(name)s", __to_py(%(var)s));' % {'name' : var.name, 'var': '__'+self.module.ident+'__::'+varname}

                print >>self.out
            else:
                print >>self.out, '    __shedskin__::__exit();'
             
            print >>self.out, '}'

            if gx.extension_module:
                print >>self.out, '\n} // extern "C"'

    def do_comment(self, s):
        if not s: return
        doc = s.split('\n')
        self.output('/**')
        if doc[0].strip():
            self.output(doc[0])
        # re-indent the rest of the doc string
        rest = textwrap.dedent('\n'.join(doc[1:])).splitlines()
        for l in rest:
            self.output(l)
        self.output('*/')

    def do_comments(self, child):
        if child in gx.comments:
            for n in gx.comments[child]:
                self.do_comment(n)

    def visitContinue(self, node, func=None):
        self.start('continue')
        self.eol()

    def bool_test(self, node, func):
        if [1 for t in self.mergeinh[node] if isinstance(t[0], class_) and t[0].ident == 'int_']:
            self.visit(node, func)
        else:
            self.visitm('__bool(', node, ')', func)

    def visitWhile(self, node, func=None):
        print >>self.out

        if node.else_:
            self.output('%s = 0;' % mv.tempcount[node.else_])
         
        self.start('while(')
        self.bool_test(node.test, func)
        self.append(') {')
        print >>self.out, self.line

        self.indent()
        gx.loopstack.append(node)
        self.visit(node.body, func)
        gx.loopstack.pop()
        self.deindent()

        self.output('}')

        if node.else_:
            self.output('if (!%s) {' % mv.tempcount[node.else_])
            self.indent()
            self.visit(node.else_, func)
            self.deindent()
            self.output('}')

    def visitClass(self, node, declare):
        cl = mv.classes[node.name]

        # --- .cpp file: output class methods
        if not declare:
            if cl.template_vars:  # XXX
                self.output('class_ *cl_'+cl.cpp_name+';\n')
                return

            if cl.virtuals:
                self.virtuals(cl, declare)

            if node in gx.comments:
                self.do_comments(node)
            else:
                self.output('/**\nclass %s\n*/\n' % cl.ident)
            self.output('class_ *cl_'+cl.cpp_name+';\n')

            #if '__init__' in cl.funcs and cl.descendants() and len(cl.funcs['__init__'].formals) != 1:
            #    self.output(cl.ident+'::'+cl.ident+'() {}')

            # --- method definitions
            for func in cl.funcs.values():
                if func.node: 
                    self.visitFunction(func.node, cl, declare)
            if cl.has_init:
                self.visitFunction(cl.funcs['__init__'].node, cl, declare, True)
            if cl.has_copy and not 'copy' in cl.funcs and not cl.template_vars:
                self.copy_method(cl, '__copy__', declare)
            if cl.has_deepcopy and not 'deepcopy' in cl.funcs and not cl.template_vars:
                self.copy_method(cl, '__deepcopy__', declare)
            
            # --- class variable declarations
            if cl.parent.vars: # XXX merge with visitModule
                for var in cl.parent.vars.values():
                    self.start(typesetreprnew(var, cl.parent)+cl.ident+'::'+self.cpp_name(var.name)) 
                    self.eol()
                print >>self.out

            return

        # --- .hpp file: class declaration
        self.output('extern class_ *cl_'+cl.cpp_name+';') 

        # --- header
        if cl.bases: 
            pyobjbase = []
        else:
            pyobjbase = ['public pyobj']

        self.output(template_repr(cl)+'class '+self.nokeywords(cl.ident)+' : '+', '.join(pyobjbase+['public '+b.ident for b in cl.bases])+' {')
        self.do_comment(node.doc)
        self.output('public:')
        self.indent()

        # --- class variables 
        if cl.parent.vars:
            for var in cl.parent.vars.values():
                self.output('static '+typesetreprnew(var, cl.parent)+self.cpp_name(var.name)+';') 
            print >>self.out

        # --- instance variables
        for var in cl.vars.values():
            if var.invisible: continue # var.name in cl.virtualvars: continue

            # var is masked by ancestor var
            vars = set()
            for ancestor in cl.ancestors():
                vars.update(ancestor.vars)
                #vars.update(ancestor.virtualvars)
            if var.name in vars:
                continue

            # virtual
            if var.name in cl.virtualvars:
                ident = var.name
                subclasses = cl.virtualvars[ident]

                merged = set()
                for m in [gx.merged_inh[subcl.vars[ident]] for subcl in subclasses if ident in subcl.vars and subcl.vars[ident] in gx.merged_inh]: # XXX
                    merged.update(m)
            
                ts = self.padme(typestrnew({(1,0): merged}, cl, True, cl))
                if ts != 'void *':
                    self.output(ts+self.cpp_name(ident)+';') 


            # non-virtual
            elif typesetreprnew(var, cl) != 'void *': # XXX invisible?
                self.output(typesetreprnew(var, cl)+self.cpp_name(var.name)+';') 

        if [v for v in cl.vars if not v.startswith('__')]:
            print >>self.out
            
        # --- constructor 
        if [c for c in cl.ancestors() if c.ident == 'Exception']:
            if cl.funcs['__init__'].inherited:
                self.output(self.nokeywords(cl.ident)+'(str *msg=0) : %s(msg) {\n        __class__ = cl_'%cl.bases[0].ident+cl.cpp_name+';\n    }')
        elif not '__init__' in cl.funcs or len(cl.funcs['__init__'].formals) > 1: # XXX template vars
            self.output(self.nokeywords(cl.ident)+'() {\n        __class__ = cl_'+cl.cpp_name+';\n    }')
        elif cl.descendants() and len(cl.funcs['__init__'].formals) != 1: # XXX
            self.output(cl.ident+'();')

        # --- virtual methods
        if cl.virtuals:
            self.virtuals(cl, declare)

        # --- regular methods
        for func in cl.funcs.values():
            if func.node:
                self.visitFunction(func.node, cl, declare)

        if cl.has_init:
            self.visitFunction(cl.funcs['__init__'].node, cl, declare, True)

        if cl.has_copy and not 'copy' in cl.funcs:
            self.copy_method(cl, '__copy__', declare)
        if cl.has_deepcopy and not 'deepcopy' in cl.funcs:
            self.copy_method(cl, '__deepcopy__', declare)
        
        self.deindent()
        self.output('};\n')

    def copy_method(self, cl, name, declare): # XXX merge?
        header = cl.template()+' *'
        if not declare:
            header += cl.template()+'::'
        header += name+'('
        self.start(header)
        
        if name == '__deepcopy__':
            self.append('dict<void *, pyobj *> *memo')
        self.append(')')

        if (cl.template_vars and declare) or (not cl.template_vars and not declare):
            print >>self.out, self.line+' {'
            self.indent()
            self.output(cl.template()+' *c = new '+cl.template()+'();')
            if name == '__deepcopy__':
                self.output('memo->__setitem__(this, c);')
           
            for var in cl.vars.values():
                if typesetreprnew(var, cl) != 'void *' and not var.invisible:
                    if name == '__deepcopy__':
                        self.output('c->%s = __deepcopy(%s);' % (var.name, var.name))
                    else:
                        self.output('c->%s = %s;' % (var.name, var.name))
            self.output('return c;')

            self.deindent()
            self.output('}\n')
        else:
            self.eol()

    def padme(self, x): 
        if not x.endswith('*'): return x+' '
        return x

    def virtuals(self, cl, declare):
        for ident, subclasses in cl.virtuals.items():
            if not subclasses: continue

            # --- merge arg/return types
            formals = []
            retexpr = False

            for subcl in subclasses:
                if ident not in subcl.funcs: continue

                func = subcl.funcs[ident]
                sig_types = []

                if func.returnexpr:
                    retexpr = True
                    if func.retnode.thing in self.mergeinh:
                        sig_types.append(self.mergeinh[func.retnode.thing]) # XXX mult returns; some targets with return some without..
                    else:
                        sig_types.append(set()) # XXX

                for name in func.formals[1:]:
                    var = func.vars[name]
                    sig_types.append(self.mergeinh[var])
                formals.append(sig_types)

            merged = []
            for z in zip(*formals):
                merge = set()
                for types in z: merge.update(types)
                merged.append(merge)
                
            formals = list(subclasses)[0].funcs[ident].formals[1:]
            ftypes = [self.padme(typestrnew({(1,0): m}, func.parent, True, func.parent)) for m in merged] 

            # --- prepare for having to cast back arguments (virtual function call means multiple targets)
            for subcl in subclasses:
                subcl.funcs[ident].ftypes = ftypes

            # --- virtual function declaration
            if declare:
                self.start('virtual ')
                if retexpr: 
                    self.append(ftypes[0])
                    ftypes = ftypes[1:]
                else:
                    self.append('void ')
                self.append(self.cpp_name(ident)+'(')

                self.append(', '.join([t+f for (t,f) in zip(ftypes, formals)]))

                if ident in cl.funcs and self.inhcpa(cl.funcs[ident]):
                    self.eol(')')
                else:
                    self.eol(') = 0')

                if ident in cl.funcs: cl.funcs[ident].declared = True

    def inhcpa(self, func):
        return hmcpa(func) or (func in gx.inheritance_relations and [1 for f in gx.inheritance_relations[func] if hmcpa(f)])

    def visitSlice(self, node, func=None):
        if node.flags == 'OP_DELETE':
            self.start()
            self.visit(inode(node.expr).fakefunc, func)
            self.eol()
        else:
            self.visit(inode(node.expr).fakefunc, func)

    def visitLambda(self, node, parent=None):
        self.append(mv.lambdaname[node])

    def visitTuple(self, node, func=None):
        if not self.filling_consts and node in self.consts:
            self.append(self.consts[node])
            return

        temp = self.filling_consts
        self.filling_consts = False
        ts = typesetreprnew(node, func)

        if ts.endswith('*'): ts = ts[:-2]
        self.append('(new '+ts)
        self.children_args(node, func)
        self.append(')')
        self.filling_consts = temp

    def children_args(self, node, func=None, cppsucks=False, numberprefix=True):
        self.append('(')
        if numberprefix and len(node.getChildNodes()): 
            self.append(str(len(node.getChildNodes()))+', ')
        for child in node.getChildNodes():
            if child in mv.tempcount:
                print 'jahoor tempcount', child
                self.append(mv.tempcount[child])
            else:
                self.visit(child, func)

            if child != node.getChildNodes()[-1]:
                self.append(', ')
        self.append(')')

    def visitDict(self, node, func=None):
        if not self.filling_consts and node in self.consts:
            self.append(self.consts[node])
            return

        temp = self.filling_consts
        self.filling_consts = False
        self.append('(new '+typesetreprnew(node, func)[:-2]+'(')
        if node.items:
            self.append(str(len(node.items))+', ')

        for (key, value) in node.items:
            self.visitm('new tuple2'+typesetreprnew(node, func)[4:-2]+'(2,', key, ',', value, ')', func)
            if (key, value) != node.items[-1]:
                self.append(', ')
        self.append('))')
        self.filling_consts = temp

    def visitList(self, node, func=None):
        if not self.filling_consts and node in self.consts:
            self.append(self.consts[node])
            return

        temp = self.filling_consts
        self.filling_consts = False
        self.append('(new '+typesetreprnew(node, func)[:-2])
        self.children_args(node, func)
        self.append(')')
        self.filling_consts = temp

    def visitAssert(self, node, func=None):
        self.start('ASSERT(')
        self.visitm(node.test, ', ', func)
        if len(node.getChildNodes()) > 1:
            self.visit(node.getChildNodes()[1], func)
        else:
            self.append('0')
        self.eol(')')

    def visitm(self, *args):
        if args and isinstance(args[-1], function):
            func = args[-1]
        else:
            func = None

        for arg in args[:-1]:
            if not arg: return
            if isinstance(arg, str):
                self.append(arg)
            else:
                self.visit(arg, func)

    def visitRaise(self, node, func=None):
        self.start('throw (')
        # --- raise class [, constructor args]
        if isinstance(node.expr1, Name) and not lookupvar(node.expr1.name, func): # XXX var = MyException
            self.append('new %s(' % node.expr1.name)
            if node.expr2:
                if isinstance(node.expr2, Tuple) and node.expr2.nodes:
                    for n in node.expr2.nodes:
                        self.visit(n, func)
                        if n != node.expr2.nodes[-1]: self.append(', ') # XXX visitcomma(nodes)
                else:
                    self.visit(node.expr2, func)
            self.append(')')
        # --- raise instance
        else:
            self.visit(node.expr1, func)
        self.eol(')')
 
    def visitTryExcept(self, node, func=None):
        # try
        self.start('try {')
        print >>self.out, self.line
        self.indent()
        if node.else_:
            self.output('%s = 0;' % mv.tempcount[node.else_])
        self.visit(node.body, func)
        if node.else_:
            self.output('%s = 1;' % mv.tempcount[node.else_])
        self.deindent()
        self.start('}')

        # except
        for handler in node.handlers:
            if isinstance(handler[0], Tuple):
                pairs = [(n, handler[1], handler[2]) for n in handler[0].nodes]
            else:
                pairs = [(handler[0], handler[1], handler[2])]

            for (h0, h1, h2) in pairs:
                if not h0:
                    arg = 'Exception *'
                elif isinstance(h0, Name):
                    arg = h0.name+' *'
                else: # XXX flow & visit
                    arg = '__'+h0.expr.name+'__::'+h0.attrname+' *'
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
            self.output('if(%s) { // else' % mv.tempcount[node.else_])
            self.indent()
            self.visit(node.else_, func)
            self.deindent()
            self.output('}')
            
    def fastfor(self, node, assname, neg, func=None):
            ivar, evar = mv.tempcount[node.assign], mv.tempcount[node.list]

            self.start('FAST_FOR%s('%neg+assname+',')

            if len(node.list.args) == 1: 
                self.append('0,')
                if node.list.args[0] in mv.tempcount: # XXX in visit?
                    self.append(mv.tempcount[node.list.args[0]])
                else:
                    self.visit(node.list.args[0], func)
                self.append(',')
            else: 
                if node.list.args[0] in mv.tempcount: # XXX in visit?
                    self.append(mv.tempcount[node.list.args[0]])
                else:
                    self.visit(node.list.args[0], func)
                self.append(',')
                if node.list.args[1] in mv.tempcount: # XXX in visit?
                    self.append(mv.tempcount[node.list.args[1]])
                else:
                    self.visit(node.list.args[1], func)
                self.append(',')

            if len(node.list.args) != 3:
                self.append('1')
            else:
                if node.list.args[2] in mv.tempcount: # XXX in visit?
                    self.append(mv.tempcount[node.list.args[2]])
                else:
                    self.visit(node.list.args[2], func)
            self.append(',%s,%s)' % (ivar[2:],evar[2:]))
            #print 'ie', ivar, evar 

            print >>self.out, self.line

    def visitFor(self, node, func=None):
        if isinstance(node.assign, AssName):
            if node.assign.name != '_':
                assname = node.assign.name
            else:
                assname = mv.tempcount[(node.assign,1)]
        elif isinstance(node.assign, AssAttr): 
            self.start('')
            self.visitAssAttr(node.assign, func)
            assname = self.line.strip()
        else:
            assname = mv.tempcount[node.assign]

        print >>self.out

        if node.else_:
            self.output('%s = 0;' % mv.tempcount[node.else_])

        # --- for i in range(..) -> for( i=l, u=expr; i < u; i++ ) .. 
        if fastfor(node):
            if len(node.list.args) == 3 and not isinstance(node.list.args[2], (Const, UnarySub)): # XXX unarysub
                self.fastfor_switch(node, func)
                self.indent()
                self.fastfor(node, assname, '', func)
                self.forbody(node, func)
                self.deindent()
                self.output('} else {')
                self.indent()
                self.fastfor(node, assname, '_NEG', func)
                self.forbody(node, func)
                self.deindent()
                self.output('}')
            else:
                neg=''
                if len(node.list.args) == 3 and isinstance(node.list.args[2], UnarySub): # XXX and const
                    neg = '_NEG'

                self.fastfor(node, assname, neg, func)
                self.forbody(node, func)

        # --- otherwise, apply macro magic
        else:
            assname = self.cpp_name(assname)
                
            pref = ''
            if not [t for t in self.mergeinh[node.list] if t[0] != defclass('tuple2')]:
                pref = '_T2' # XXX generalize to listcomps

            if not [t for t in self.mergeinh[node.list] if t[0] not in (defclass('tuple'), defclass('list'))]:
                pref = '_SEQ'

            if pref == '': tail = mv.tempcount[(node,1)][2:]
            else: tail = mv.tempcount[node][2:]+','+mv.tempcount[node.list][2:]

            if node.list in self.consts:
                self.output('FOR_IN%s(%s, %s, %s)' % (pref, assname, self.consts[node.list], tail))
            else:
                self.start('FOR_IN%s(%s,' % (pref, assname))
                self.visit(node.list, func)
                print >>self.out, self.line+','+tail+')'

            self.forbody(node, func)

        print >>self.out

    def forbody(self, node, func=None):
        self.indent()

        if isinstance(node.assign, (AssTuple, AssList)):
            self.tuple_assign(node.assign, mv.tempcount[node.assign], func)

        gx.loopstack.append(node)
        self.visit(node.body, func)
        gx.loopstack.pop()
        self.deindent()

        self.output('END_FOR')

        if node.else_:
            self.output('if (!%s) {' % mv.tempcount[node.else_])
            self.indent()
            self.visit(node.else_, func)
            self.deindent()
            self.output('}')

    def func_pointers(self, print_them):
        mv.lambda_cache = {}
        mv.lambda_signum = {}

        for func in mv.lambdas.values():
            argtypes = [typesetreprnew(func.vars[formal], func).rstrip() for formal in func.formals]
            signature = '_'.join(argtypes)

            if func.returnexpr:
                rettype = typesetreprnew(func.retnode.thing,func)
            else:
                rettype = 'void '
            signature += '->'+rettype

            if signature not in mv.lambda_cache: 
                nr = len(mv.lambda_cache)
                mv.lambda_cache[signature] = nr
                if print_them:
                    print >>self.out, 'typedef %s(*lambda%d)(' % (rettype, nr) + ', '.join(argtypes)+');'

            mv.lambda_signum[func] = mv.lambda_cache[signature]

        if mv.lambda_cache and print_them: print >>self.out

    # --- function/method header
    def func_header(self, func, declare, is_init=False):
        method = isinstance(func.parent, class_)
        if method: 
            formals = [f for f in func.formals if f != 'self'] 
        else:
            formals = [f for f in func.formals] 

        ident = func.ident
        self.start()

        # --- function/method template
        header = ''
#        if func.ident != '__init__' and func in gx.inheritance_relations: #XXX cleanup
#            for child in gx.inheritance_relations[func]:
#                if func.ident in child.parent.funcs and not child.parent.funcs[func.ident].inherited:
#                    header += 'virtual '
#                    break

        if method and not declare:
            header = template_repr(func.parent)
        header += template_repr(func)
            
        # --- return expression
        if func.ident in ['__hash__']:
            header += 'int '
        elif func.returnexpr: 
            header += typesetreprnew(func.retnode.thing, func) # XXX mult
        else:
            if ident.startswith('__init__') and not is_init: 
                ident = self.nokeywords(func.parent.ident)
            else:
                header += 'void '
                ident = self.cpp_name(ident)

        ftypes = [typesetreprnew(func.vars[f], func) for f in formals]

        # if arguments type too precise (e.g. virtually called) cast them back 
        oldftypes = ftypes
        if func.ftypes:
            ftypes = func.ftypes[1:]

        # --- method header
        if method and not declare:
            if func.parent.template_vars:
                header += self.nokeywords(func.parent.ident)+'<'+','.join(func.parent.template_vars.keys())+'>::'
            else:
                header += self.nokeywords(func.parent.ident)+'::'
        
        if func.ident != '__init__':
            ident = self.cpp_name(ident)
        header += ident

        # --- cast arguments if necessary (explained above)
        casts = []
        if func.ftypes:
            #print 'cast', oldftypes, formals, ftypes

            for i in range(len(oldftypes)): # XXX this is 'cast on specialize'.. how about generalization?
                if oldftypes[i] != ftypes[i]:
                    #print 'cast!', oldftypes[i], ftypes[i+1]
                    casts.append(oldftypes[i]+formals[i]+' = ('+oldftypes[i]+')__'+formals[i]+';')
                    if not declare:
                        formals[i] = '__'+formals[i]

        formals2 = formals[:]
        for (i,f) in enumerate(formals2): # XXX
            formals2[i] = self.cpp_name(f)

        formaldecs = [o+f for (o,f) in zip(ftypes, formals2)]

        # --- output 
        self.append(header+'('+', '.join(formaldecs)+')')
        if declare and not (is_method(func) and func.parent.template_vars) and not func.template_vars: # XXX general func
            self.eol()
            return
        else:
            if func.ident == '__init__':
                if func.inherited:
                    self.append(' : '+func.parent.bases[0].ident+'('+','.join([f for f in func.formals if f != 'self'])+')') # XXX
                elif func.parent_constr:
                    target = func.parent.bases[0].funcs['__init__'] # XXX use general pairing function (connect_actual..?)

                    pc = func.parent_constr
                    if len(pc) < len(target.formals):
                        pc += target.defaults[-len(target.formals)+len(pc):]

                    self.append(' : '+pc[0]+'(')
                    if len(pc) > 1:
                        for n in pc[1:-1]:
                            self.visitm(n, ',', func)
                        self.visitm(pc[-1], func)
                    self.append(')')
        
            print >>self.out, self.line+' {'
            self.indent()
                    
            if not declare and func.doc: 
                self.do_comment(func.doc)
                
            for cast in casts: 
                self.output(cast)
            self.deindent()

    def nokeywords(self, name):
        if name in gx.cpp_keywords:
            return gx.ss_prefix+name
        return name

    def cpp_name(self, name, func=None):
        if name in [cl.ident for cl in gx.allclasses]:
            return '_'+name
        elif name+'_' in [cl.ident for cl in gx.allclasses]:
            return '_'+name
        elif name in self.module.funcs and func and isinstance(func.parent, class_) and name in func.parent.funcs: 
            return '__'+func.mv.module.ident+'__::'+name

        return self.nokeywords(name)

    def visitFunction(self, node, parent=None, declare=False, is_init=False):
        # locate right func instance
        if parent and isinstance(parent, class_):
            func = parent.funcs[node.name]
        elif node.name in mv.funcs:
            func = mv.funcs[node.name]
        else:
            func = mv.lambdas[node.name]

        if func.invisible or (func.inherited and not func.ident == '__init__'):
            return
        if func.mv.module.builtin or func.ident in ['min','max','zip','sum','__zip2','enumerate']: # XXX latter for test 116
            return
        if declare and func.declared: # XXX
            return
        if not declare and ((is_method(func) and func.parent.template_vars) or func.template_vars): # XXX general func
            return

        # check whether function is called at all (possibly via inheritance)
        if not self.inhcpa(func):
            if func.ident in ['__iadd__', '__isub__', '__imul__']:
                return
            error(repr(func)+' not called!', node, warning=True)
            if not (declare and func.ident in func.parent.virtuals):
                return
              
        if func.isGenerator and ((declare and func.template_vars) or not declare):
            templatestr=''
            if func.template_vars: templatestr = 'template <'+','.join(['class '+f for f in func.template_vars])+'> '
            self.output('%sclass __gen_%s : public %s {' % (templatestr, func.ident, typesetreprnew(func.retnode.thing, func)[:-2]))
            self.output('public:')
            self.indent()
            for f in func.vars:
                self.output(typesetreprnew(func.vars[f], func)+self.cpp_name(f)+';') # XXX merge below
            self.output('int __last_yield;\n')

            args = []
            for f in func.formals:
                args.append(typesetreprnew(func.vars[f], func)+self.cpp_name(f))
            self.output(('__gen_%s(' % func.ident) + ','.join(args)+') {')
            self.indent()
            for f in func.formals:
                self.output('this->%s = %s;' % (self.cpp_name(f),self.cpp_name(f)))
            self.output('__last_yield = -1;')
            self.deindent()
            self.output('}\n')

            self.output('%s next() {' % typesetreprnew(func.retnode.thing, func)[7:-3])
            self.indent()
            self.output('switch(__last_yield) {')
            self.indent()
            for (i,n) in enumerate(func.yieldNodes):
                self.output('case %d: goto __after_yield_%d;' % (i,i))
            self.output('default: break;')
            self.deindent()
            self.output('}')

            for child in func.node.code.getChildNodes():
                self.visit(child, func)
            self.output('throw new StopIteration();')
            self.deindent()
            self.output('}\n')

            self.deindent()
            self.output('};\n')

        self.func_header(func, declare, is_init)
        if declare and not (is_method(func) and func.parent.template_vars) and not func.template_vars: # XXX general func
            return

        self.indent()

        if func.isGenerator:
            templatestr=''
            if func.template_vars: templatestr = '<'+','.join(func.template_vars)+'>'
            self.output('return new __gen_%s%s(%s);\n' % (func.ident, templatestr, ','.join([self.cpp_name(f) for f in func.formals]))) # XXX formals
            self.deindent()
            self.output('}\n')
            return

        if func.ident.startswith('__init__'):
            if func.parent:
                if not func.parent.has_init or not is_init:
                    self.output('this->__class__ = cl_'+parent.cpp_name+';')

                if func.parent.has_init and not is_init:
                    self.output('__init__('+','.join(func.formals[1:])+');')
                    self.deindent();
                    self.output('}\n')
                    return

            if func.inherited:
                self.deindent()
                self.output('}\n')
                return

        # --- local declarations
        pairs = []
        for (name, var) in func.vars.items():
            if var.invisible: continue

            if name not in func.formals:
                name = self.cpp_name(name)
                ts = typesetreprnew(var, func)
            
                pairs.append((ts, name))

        self.output(self.indentation.join(self.group_declarations(pairs)))

        # --- function body
        for child in node.getChildNodes():
            self.visit(child, func)
        if func.fakeret:
            self.visit(func.fakeret, func)
        
        # --- add Return(None) (sort of) if function doesn't already end with a Return
        if node.getChildNodes():
            lastnode = node.getChildNodes()[-1]
            if not func.ident == '__init__' and not func.fakeret and not isinstance(lastnode, Return) and not (isinstance(lastnode, Stmt) and isinstance(lastnode.nodes[-1], Return)): # XXX use Stmt in moduleVisitor
                self.output('return 0;')

        self.deindent()
        self.output('}\n')

    def visitYield(self, node, func):
        self.output('__last_yield = %d;' % func.yieldNodes.index(node))
        self.start()
        self.visitm('return ', node.value, func)
        self.eol()
        self.output('__after_yield_%d:;' % func.yieldNodes.index(node))
        self.start()
        
    def visitNot(self, node, func=None): 
        self.append('(!')
        if unboxable(self.mergeinh[node.expr]):
            self.visit(node.expr, func)
        else:
            self.visitm('__bool(', node.expr, ')', func)
        self.append(')')

    def visitBackquote(self, node, func=None):
        self.visit(inode(node.expr).fakefunc, func)

    def zeropointernone(self, node):
        return [t for t in self.mergeinh[node] if t[0].ident == 'none']

    def visitIf(self, node, func=None):
        for test in node.tests:
            self.start()
            if test == node.tests[0]:
                self.append('if (')
            else:
                self.append('else if (')

            self.bool_test(test[0], func)

            print >>self.out, self.line+') {'

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
        self.visitm('((', node.test, ')?(', node.then, '):(', node.else_, '))', func)

    def visitBreak(self, node, func=None):
        if gx.loopstack[-1].else_ in mv.tempcount:
            self.output('%s = 1;' % mv.tempcount[gx.loopstack[-1].else_])
        self.output('break;')

    def visitStmt(self, node, func=None):
        for b in node.nodes:
            if isinstance(b, Discard):
                if isinstance(b.expr, Const) and b.expr.value == None:
                    continue
                if isinstance(b.expr, Const) and type(b.expr.value) == str: 
                    self.do_comment(b.expr.value)
                    continue
                self.start('')
                self.visit(b, func)
                self.eol()
            else:
                self.visit(b, func)

    def visitOr(self, node, func=None):
        if not self.mixingboolean(node, '||', func): # allow type mixing, as result may not be used
            self.booleanOp(node, node.nodes, '__OR', func)

    def visitAnd(self, node, func=None):
        if not self.mixingboolean(node, '&&', func): # allow type mixing, as result may not be used
            self.booleanOp(node, node.nodes, '__AND', func)

    def mixingboolean(self, node, op, func):
        mixing = False
        for n in node.nodes:
            if self.booleancast(node, n, func) is None:
                mixing = True
        if not mixing: return False

        self.append('(')
        for n in node.nodes:
            if self.mergeinh[n] != set([(defclass('int_'),0)]):
                self.visitm('__bool(', n, ')', func)
            else:
                self.visit(n, func)
            if n != node.nodes[-1]:
                self.append(' '+op+' ')
        self.append(')')
        return True

    def booleancast(self, node, child, func=None):
        if typesetreprnew(child, func) == typesetreprnew(node, func):
            return '' # exactly the same types: no casting necessary
        elif assign_needs_cast(child, func, node, func) or (self.mergeinh[child] == set([(defclass('none'),0)]) and self.mergeinh[node] != set([(defclass('none'),0)])): # cast None or almost compatible types
            return '('+typesetreprnew(node, func)+')'
        else:
            return None # local dynamic typing

    def castup(self, node, child, func=None):
        cast = self.booleancast(node, child, func)
        if cast: self.visitm('('+cast, child, ')', func)
        else: self.visit(child, func)

    def booleanOp(self, node, nodes, op, func=None):
        if len(nodes) > 1:
            self.append(op+'(')
            self.castup(node, nodes[0], func)
            self.append(', ')
            self.booleanOp(node, nodes[1:], op, func)
            self.append(', '+mv.tempcount[nodes[0]][2:]+')')
        else:
            self.castup(node, nodes[0], func)

    def visitCompare(self, node, func=None):
        if len(node.ops) > 1:
            self.append('(')

        self.done = set() # (tvar=fun())

        left = node.expr
        for op, right in node.ops:
            if op == '>': msg, short, pre = '__gt__', '>', None # XXX map = {}!
            elif op == '<': msg, short, pre = '__lt__', '<', None
            elif op == 'in': msg, short, pre = '__contains__', None, None
            elif op == 'not in': msg, short, pre = '__contains__', None, '!'
            elif op == '!=': msg, short, pre = '__ne__', '!=', None
            elif op == '==': msg, short, pre = '__eq__', '==', None
            elif op == 'is': msg, short, pre = None, '==', None
            elif op == 'is not': msg, short, pre = None, '!=', None
            elif op == '<=': msg, short, pre = '__le__', '<=', None
            elif op == '>=': msg, short, pre = '__ge__', '>=', None
            else: return

            # --- comparison to [], (): convert to ..->empty() # XXX {}, __ne__
            if msg == '__eq__':
                leftcl, rightcl = polymorphic_t(self.mergeinh[left]), polymorphic_t(self.mergeinh[right])

                if len(leftcl) == 1 and leftcl == rightcl and leftcl.pop().ident in ['list', 'tuple', 'tuple2', 'dict']:
                    for (a,b) in [(left, right), (right, left)]:
                        if isinstance(b, (List, Tuple, Dict)) and len(b.nodes) == 0:
                            if pre: self.append(pre+'(')
                            self.visit2(a, func)
                            self.append('->empty()')
                            if pre: self.append(')')
                            return

            # --- 'x in range(n)' -> x > 0 && x < n # XXX not in, range(a,b)
            if msg == '__contains__':
                #op = node.ops[0][1] # XXX a in range(8): a doesn't have to be an int variable..; eval order
                if isinstance(right, CallFunc) and isinstance(right.node, Name) and right.node.name in ['range']: #, 'xrange']:
                    if len(right.args) == 1:
                        l, u = '0', right.args[0]
                    else:
                        l, u = right.args[0], right.args[1]
                    if pre: self.append(pre)
                    self.visitm('(', left, '>=', l, '&&', left, '<', u, ')', func)
                else:
                    self.visitBinary(right, left, msg, short, func, pre)

            else:
                self.visitBinary(left, right, msg, short, func, pre)

            if right != node.ops[-1][1]:
                self.append('&&')
            left = right

        if len(node.ops) > 1:
            self.append(')')

    def visitAugAssign(self, node, func=None):
        #print 'gen aug', node, inode(node).assignhop

        if isinstance(node.node, Subscript):
            self.start()
            if set([t[0].ident for t in self.mergeinh[node.node.expr] if isinstance(t[0], class_)]) in [set(['dict']), set(['defaultdict'])] and node.op == '+=':
                self.visitm(node.node.expr, '->__addtoitem__(', inode(node).subs, ', ', node.expr, ')', func)
                self.eol()
                return
            
            self.visitm(inode(node).temp1+' = ', node.node.expr, func)
            self.eol()
            self.start()
            self.visitm(inode(node).temp2+' = ', inode(node).subs, func)
            self.eol()
        self.visit(inode(node).assignhop, func)

    def visitAdd(self, node, func=None):
        str_nodes = self.rec_string_addition(node)
        if str_nodes and len(str_nodes) > 2:
            self.append('__add_strs(%d, ' % len(str_nodes))
            for (i, node) in enumerate(str_nodes):
                self.visit(node, func)
                if i < len(str_nodes)-1:
                    self.append(', ')
            self.append(')')
        else:
            self.visitBinary(node.left, node.right, augmsg(node, 'add'), '+', func)

    def rec_string_addition(self, node):
        if isinstance(node, Add):
            l, r = self.rec_string_addition(node.left), self.rec_string_addition(node.right)
            if l and r: 
                return l+r
        elif self.mergeinh[node] == set([(defclass('str_'),0)]):
            return [node]

        return None

    def visitBitand(self, node, func=None):
        self.visitBitop(node, augmsg(node, 'and'), '&', func)

    def visitBitor(self, node, func=None):
        self.visitBitop(node, augmsg(node, 'or'), '|', func)

    def visitBitxor(self, node, func=None):
        self.visitBitop(node, augmsg(node, 'xor'), '^', func)

    def visitBitop(self, node, msg, inline, func=None):
        self.visitBitpair(Bitpair(node.nodes, msg, inline), func)

    def visitBitpair(self, node, func=None):
        if len(node.nodes) == 1:
            self.visit(node.nodes[0], func)
        else:
            self.visitBinary(node.nodes[0], Bitpair(node.nodes[1:], node.msg, node.inline), node.msg, node.inline, func)

    def visitRightShift(self, node, func=None):
        self.visitBinary(node.left, node.right, augmsg(node, 'rshift'), '>>', func)

    def visitLeftShift(self, node, func=None):
        self.visitBinary(node.left, node.right, augmsg(node, 'lshift'), '<<', func)

    def visitMul(self, node, func=None):
        self.visitBinary(node.left, node.right, augmsg(node, 'mul'), '*', func)

    def visitDiv(self, node, func=None):
        self.visitBinary(node.left, node.right, augmsg(node, 'div'), '/', func)

    def visitInvert(self, node, func=None): # XXX visitUnarySub merge, template function __invert?
        if unboxable(self.mergeinh[node.expr]):
            self.visitm('~', node.expr, func)
        else:
            self.visitCallFunc(inode(node.expr).fakefunc, func)

    def visitFloorDiv(self, node, func=None):
        self.visitBinary(node.left, node.right, augmsg(node, 'floordiv'), '//', func)
        #self.visitm('__floordiv(', node.left, ', ', node.right, ')', func)

    def visitPower(self, node, func=None):
        self.power(node.left, node.right, None, func)

    def power(self, left, right, mod, func=None):
        if mod: self.visitm('__power(', left, ', ', right, ', ', mod, ')', func)
        else: 
            if self.mergeinh[left].intersection(set([(defclass('int_'),0),(defclass('float_'),0)])) and isinstance(right, Const) and type(right.value) == int and right.value in [2,3]:
                self.visitm(('__power%d(' % int(right.value)), left, ')', func)
            else:
                self.visitm('__power(', left, ', ', right, ')', func)

    def visitSub(self, node, func=None):
        self.visitBinary(node.left, node.right, augmsg(node, 'sub'), '-', func)

    def par(self, node, thingy):
        if (isinstance(node, Const) and not isinstance(node.value, (int, float))) or not isinstance(node, (Name, Const)):
            return thingy 
        return ''

    def visitBinary(self, left, right, middle, inline, func=None, prefix=''): # XXX cleanup please
        ltypes = self.mergeinh[left]
        #lclasses = set([t[0] for t in ltypes])
        origright = right
        if isinstance(right, Bitpair):
            right = right.nodes[0]
        rtypes = self.mergeinh[right]
        ul, ur = unboxable(ltypes), unboxable(rtypes)

        inttype = set([(defclass('int_'),0)]) # XXX new type?
        floattype = set([(defclass('float_'),0)]) # XXX new type?

        #print 'jow', left, right, ltypes, rtypes, middle, inline, inttype, floattype

        # --- inline mod/div
        if (floattype.intersection(ltypes) or inttype.intersection(ltypes)):
            if inline in ['%'] or (inline in ['/'] and not (floattype.intersection(ltypes) or floattype.intersection(rtypes))):
                self.append({'%': '__mods', '/': '__divs'}[inline]+'(')
                self.visit2(left, func)
                self.append(', ')
                self.visit2(origright, func)
                self.append(')')
                return

        # --- inline floordiv # XXX merge above?
        if (inline and ul and ur) and inline in ['//']:
            self.append({'//': '__floordiv'}[inline]+'(')
            self.visit2(left, func)
            self.append(',')
            self.visit2(right, func)
            self.append(')')
            return

        # --- inline other
        if (inline and ul and ur) or not middle or (isinstance(left, Name) and left.name == 'None') or (isinstance(origright, Name) and origright.name == 'None'): # XXX not middle, cleanup?
            self.append('(')
            self.visit2(left, func)
            self.append(inline)
            self.visit2(origright, func)
            self.append(')')
            return
            
        # --- prefix '!'
        postfix = '' 
        if prefix: 
            self.append('('+prefix)
            postfix = ')'

        # --- comparison
        if middle in ['__eq__', '__ne__', '__gt__', '__ge__', '__lt__', '__le__']:
            self.append(middle[:-2]+'(')
            self.visit2(left, func)
            self.append(', ')
            self.visit2(origright, func)
            self.append(')'+postfix)
            return
        
        # --- 'a.__mul__(b)': use template to call to b.__mul__(a), while maintaining evaluation order
        if inline == '*' and ul and not ur:
            self.append('__mul(')
            self.visit2(left, func)
            self.append(', ')
            self.visit2(origright, func)
            self.append(')'+postfix)
            return

        # --- default: left, connector, middle, right
        self.append(self.par(left, '('))
        self.visit2(left, func)
        self.append(self.par(left, ')'))
        if middle == '==':
            self.append('==(')
        else:
            self.append(self.connector(left, func)+middle+'(')
        self.refer(origright, func, visit2=True) # XXX bleh
        self.append(')'+postfix)

    def visit2(self, node, func): # XXX use temp vars in comparisons, e.g. (t1=fun())
        if node in mv.tempcount:
            if node in self.done:
                self.append(mv.tempcount[node])
            else:
                self.visitm('('+mv.tempcount[node]+'=', node, ')', func)
                self.done.add(node)
        else:
            self.visit(node, func)

    def visitUnarySub(self, node, func=None):
        if unboxable(self.mergeinh[node.expr]):
            self.visitm('-', node.expr, func)
        else:
            self.visitCallFunc(inode(node.expr).fakefunc, func)

    def refer(self, node, func, visit2=False):
        if isinstance(node, str):
            var = lookupvar(node, func)
            return node

        if isinstance(node, Name) and not node.name in ['None','True','False']:
            var = lookupvar(node.name, func)
        if visit2:
            self.visit2(node, func)
        else:
            self.visit(node, func)

    def bastard(self, ident, objexpr):
        if ident in ['__getfirst__','__getsecond__']:
           lcp = lowest_common_parents(polymorphic_t(self.mergeinh[objexpr]))
           if [cl for cl in lcp if cl.ident != 'tuple2']:
               return True
        return False

    def library_func(self, funcs, modname, clname, funcname):
        for func in funcs:
            if not func.mv.module.builtin or func.mv.module.ident != modname:
                continue

            if clname != None:
                if not func.parent or func.parent.ident != clname:
                    continue

            return func.ident == funcname

        return False

    def visitCallFunc(self, node, func=None): 
        #print 'callfunc', node
        objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(node)

        funcs = callfunc_targets(node, self.mergeinh)

        if self.library_func(funcs, 're', None, 'findall') or \
           self.library_func(funcs, 're', 're_object', 'findall'):
            error("assuming 'findall' returns list of strings", node, warning=True)

        if self.bastard(ident, objexpr):
            ident = '__getitem__'

        # --- target expression

        if node.node in self.mergeinh and [t for t in self.mergeinh[node.node] if isinstance(t[0], function)]: # anonymous function
            self.visitm(node.node, '(', func)

        elif constructor:
            self.append('(new '+self.nokeywords(typesetreprnew(node, func)[:-2])+'(')

        elif parent_constr:
            if ident.startswith('__init__'):
                return
            self.append(func.parent.bases[0].ident+'::'+node.node.attrname+'(') # XXX

        elif direct_call: # XXX no namespace (e.g., math.pow), check nr of args
            if ident == 'float' and node.args and self.mergeinh[node.args[0]] == set([(defclass('float_'), 0)]):
                self.visit(node.args[0], func)
                return
            if ident in ['abs', 'int', 'float', 'str', 'dict', 'tuple', 'list', 'type', 'bool', 'cmp', 'sum']:
                self.append('__'+ident+'(')
            elif ident == 'iter':
                self.append('___iter(') # XXX
            elif ident == 'pow' and direct_call.mv.module.ident == 'builtin':
                if len(node.args)==3: third = node.args[2]
                else: third = None
                self.power(node.args[0], node.args[1], third, func)
                return
            elif ident == 'hash':
                self.append('hasher(') # XXX cleanup
            elif ident == 'isinstance' and isinstance(node.args[1], Name) and node.args[1].name in ['float','int']:
                error("'isinstance' cannot be used with ints or floats; assuming always true", node, warning=True)
                self.append('1')
                return
            elif ident == 'round':
                self.append('___round(')
            elif ident in ['min','max']:
                self.append('__'+ident+'(')
                if len(node.args) > 3:
                    self.append(str(len(node.args))+', ')
            else:
                if ident in self.module.mv.ext_funcs: # XXX using as? :P
                     ident = self.module.mv.ext_funcs[ident].ident

                if isinstance(node.node, Name): # XXX ugly
                    self.append(self.cpp_name(ident, func))
                else:
                    self.visit(node.node)
                self.append('(')

        elif method_call:
            if isinstance(objexpr, Const) and objexpr.value == '' and ident == 'join' and isinstance(node.args[0], CallFunc) and \
                  isinstance(node.args[0].node, Name) and node.args[0].node.name == 'sorted' and \
                  self.mergeinh[node.args[0].args[0]] == set([(defclass('str_'), 0)]): # ''.join(sorted(str))
                #print 'nnee', objexpr, ident, self.mergeinh[node.args[0].args[0]], node.args
                self.visitm(node.args[0].args[0], '->sorted()', func)
                return
            else:
                for cl, _ in self.mergeinh[objexpr]:
                    if cl.ident != 'none' and ident not in cl.funcs:
                        conv = {'int_': 'int', 'float_': 'float', 'str_': 'str', 'class_': 'class', 'none': 'none'}
                        clname = conv.get(cl.ident, cl.ident)
                        error("class '%s' has no method '%s'" % (clname, ident), node, warning=True)
                self.visitm(node.node, '(', func)

        else:
            error("unbound identifier '"+ident+"'", node)

        if constructor and self.mergeinh[node] and 'Exception' in [c.ident for c in list(self.mergeinh[node])[0][0].ancestors()]: # XXX self.mergeinh[node], try getopt
            if node.args:
                for n in node.args[:-1]:
                    self.visit(n, func)
                    self.append(',')
                self.visit(node.args[-1], func)
            self.append('))')
            return

        elif not funcs:
            if constructor: self.append(')')
            self.append(')')
            return

        # --- arguments 
        target = funcs[0] # XXX

        # --- casting:
        """if target.returnexpr and not (target.formals and target.vars[target.formals[0]].parametric) and self.typestr(target.returnexpr[-1]) != self.typestr(node): # XXX cleanup & use more often
                cast = self.typestr(node)
                self.append('(('+cast+')(')"""


        if not target.mv.module.builtin:
            for default in target.defaults: # default constant arguments (are global!)
                if not isinstance(default, (UnarySub, Const)) and not (isinstance(default, Name) and default.name == 'None'):
                    self.get_constant(default)

        for f in funcs:
            #print 'sig', f.formals, f.varargs
            if len(f.formals) != len(target.formals) or (f.varargs and not target.varargs) or (not f.varargs and target.varargs): # incompatible signatures XXX fix function headers to cope
                error('incompatible target signatures', node, warning=True)
                self.append(')')
                return

        if ident in ['__getfirst__','__getsecond__']:
            self.append(')')
            return

        if target.mv.module.builtin and target.mv.module.ident == 'path' and ident=='join': # XXX
        #if ident == 'join' and not method_call:
            pairs = [(arg, target.formals[0]) for arg in node.args]
            self.append('%d, ' % len(node.args))
        elif ident in ['max','min'] and len(node.args) > 3:
            pairs = [(arg, target.formals[0]) for arg in node.args]
        else:
            args = node.args
            if node.star_args:
                args = [node.star_args]+args
        
            pairs = connect_actual_formal(node, target, parent_constr, check_error=True)

            if constructor and ident=='defaultdict' and node.args:
                pairs = pairs[1:]

        for (arg, formal) in pairs:
            if isinstance(arg, tuple):
                # --- pack arguments as tuple
                self.append('new '+typesetreprnew(formal, target)[:-2]+'(')
                
                if len(arg) > 0: 
                    self.append(str(len(arg))+',')

                    # XXX merge with children args, as below
                    for a in arg:
                        self.refer(a, func)
                        if a != arg[-1]:
                            self.append(',')
                self.append(')')

            elif isinstance(formal, tuple):
                # --- unpack tuple 
                self.append(', '.join(['(*'+arg.name+')['+str(i)+']' for i in range(len(formal))]))

            else:
                # --- connect regular argument to formal
                cast = False
                if not target.mv.module.builtin and assign_needs_cast(arg, func, formal, target): # XXX builtin (dict.fromkeys?)
                    #print 'cast!', node, arg, formal
                    cast = True
                    self.append('(('+typesetreprnew(formal, target)+')(')

                if arg in self.consts:
                    self.append(self.consts[arg])
                else:
                    if constructor and ident in ['set', 'frozenset'] and typesetreprnew(arg, func) in ['list<void *> *', 'tuple<void *> *', 'pyiter<void *> *', 'pyseq<void *> *', 'pyset<void *>']: # XXX to needs_cast
                        pass # XXX assign_needs_cast
                    else:
                        self.refer(arg, func)

                if cast: self.append('))')

            if (arg, formal) != pairs[-1]:
                self.append(', ')

        if constructor and ident == 'frozenset':
            if pairs: self.append(',')
            self.append('1')
        self.append(')')
        if constructor:
            self.append(')')

    def visitReturn(self, node, func=None):
        if func.isGenerator:
            self.output('throw new StopIteration();')
            return

        self.start('return ')

        cast = False
        if assign_needs_cast(node.value, func, func.retnode.thing, func):
            #print 'cast!', node
            cast = True
            self.append('(('+typesetreprnew(func.retnode.thing, func)+')(')

        elif isinstance(node.value, Name) and node.value.name == 'self': # XXX integrate with assign_needs_cast!? # XXX self?
            cl = lowest_common_parents(polymorphic_t(self.mergeinh[func.retnode.thing]))[0] # XXX simplify
            if not (cl == func.parent or cl in func.parent.ancestors()): 
                self.append('('+cl.ident+' *)')

        self.visit(node.value, func)
        if cast: self.append('))')
        self.eol()

    def tuple_assign(self, lvalue, rvalue, func): 
        temp = mv.tempcount[lvalue]

        if isinstance(lvalue, tuple): nodes = lvalue
        else: nodes = lvalue.nodes

        # --- nested unpacking assignment: a, (b,c) = d, e
        if [item for item in nodes if not isinstance(item, AssName)]:
            self.start(temp+' = ')
            if isinstance(rvalue, str):
                self.append(rvalue)
            else:
                self.visit(rvalue, func)
            self.eol()

            for i, item in enumerate(nodes):
                ident, arg = get_ident(Const(i)), ''
                if ident == '__getitem__':
                    arg = str(i)
                selector = '%s->%s(%s)' % (temp, ident, arg)

                if isinstance(item, AssName):
                    if item.name != '_':
                        self.output('%s = %s;' % (item.name, selector)) 
                elif isinstance(item, (AssTuple, AssList)): # recursion
                    self.tuple_assign(item, selector, func)
                elif isinstance(item, Subscript):
                    self.assign_pair(item, selector, func) 
                elif isinstance(item, AssAttr):
                    self.assign_pair(item, selector, func) 
                    self.eol(' = '+selector)

        # --- non-nested unpacking assignment: a,b,c = d 
        else: 
            self.start()
            self.visitm(temp, ' = ', rvalue, func)
            self.eol()

            for (n, item) in enumerate(lvalue.nodes):
                if item.name != '_': 
                    self.start()
                    if isinstance(rvalue, Const): sel = '__getitem__(%d)' % n
                    elif len(lvalue.nodes) > 2: sel = '__getfast__(%d)' % n
                    elif n == 0: sel = '__getfirst__()' # XXX merge
                    else: sel = '__getsecond__()'
                    self.visitm(item, ' = ', temp, '->'+sel, func)
                    self.eol()
            
    def subs_assign(self, lvalue, func):
        if defclass('list') in [t[0] for t in self.mergeinh[lvalue.expr]]:
            #if isinstance(lvalue.expr, Name):
            self.append('ELEM((')
            self.refer(lvalue.expr, func)
            self.append('),')
            self.visit(lvalue.subs[0], func)
            #else:
            #    self.append(mv.tempcount[lvalue.expr]+' = ')
            #    self.refer(lvalue.expr, func)
            #    self.eol()
            #    self.start('')
            #    self.append('ELEM('+mv.tempcount[lvalue.expr]+',')
            #    self.visit(lvalue.subs[0], func)
            self.append(')')

        else:
            if len(lvalue.subs) > 1:
                subs = inode(lvalue.expr).faketuple
            else:
                subs = lvalue.subs[0]
            self.visitm(lvalue.expr, self.connector(lvalue.expr, func), '__setitem__(', subs, ', ', func)

    def visitAssign(self, node, func=None):
        #print 'assign', node

        #temp vars
        if len(node.nodes) > 1 or isinstance(node.expr, Tuple):
            if isinstance(node.expr, Tuple):
                if [n for n in node.nodes if isinstance(n, AssTuple)]: # XXX a,b=d[i,j]=..?
                    for child in node.expr.nodes:
                        if not (child,0,0) in gx.cnode: # (a,b) = (1,2): (1,2) never visited
                            continue
                        if not isinstance(child, Const) and not (isinstance(child, Name) and child.name == 'None'):
                            self.start(mv.tempcount[child]+' = ')
                            self.visit(child, func)
                            self.eol()
            elif not isinstance(node.expr, Const) and not (isinstance(node.expr, Name) and node.expr.name == 'None'):
                self.start(mv.tempcount[node.expr]+' = ')
                self.visit(node.expr, func)
                self.eol()

        # a = (b,c) = .. = expr
        right = node.expr
        for left in node.nodes:
            pairs = assign_rec(left, node.expr)
            tempvars = len(pairs) > 1

            for (lvalue, rvalue) in pairs:
                self.start('') # XXX remove?
                
                # expr[expr] = expr
                if isinstance(lvalue, Subscript) and not isinstance(lvalue.subs[0], Sliceobj):
                    self.assign_pair(lvalue, rvalue, func)
                    continue

                # expr.attr = expr
                elif isinstance(lvalue, AssAttr):
                    self.assign_pair(lvalue, rvalue, func)
                    self.append(' = ')

                # name = expr: if name non-escaping, allocate list (comprehension) on stack
                elif isinstance(lvalue, AssName):
                    if lvalue.name != '_':
                        self.visit(lvalue, func)
                        self.append(' = ')

                # (a,(b,c), ..) = expr
                elif isinstance(lvalue, (AssTuple, AssList)):
                    self.tuple_assign(lvalue, rvalue, func)
                    continue
            
                # expr[a:b] = expr
                elif isinstance(lvalue, Slice):
                    if isinstance(rvalue, Slice) and lvalue.upper == rvalue.upper == None and lvalue.lower == rvalue.lower == None:
                        self.visitm(lvalue.expr, self.connector(lvalue.expr, func), 'units = ', rvalue.expr, self.connector(rvalue.expr, func), 'units', func)
                    else:
                        self.visitSlice(lvalue, func)
                    self.eol()
                    continue

                # expr[a:b:c] = expr
                elif isinstance(lvalue, Subscript) and isinstance(lvalue.subs[0], Sliceobj):
                    self.visit(inode(lvalue.expr).fakefunc, func)
                    self.eol()
                    continue

                # --- cast incompatible types (XXX conversion in cases)
                cast = False
                if isinstance(lvalue, AssName) and lvalue.name != '_': # XXX hm
                    var = lookupvar(lvalue.name, func) 
                
                    if assign_needs_cast(rvalue, func, var, func):
                        #print 'cast!', lvalue, rvalue
                        cast = True
                        self.append('(('+typesetreprnew(var, func)+')(')

                if rvalue in mv.tempcount:
                    self.append(mv.tempcount[rvalue])
                else:
                    self.visit(rvalue, func)
                if cast: self.append('))')
                self.eol()

    def assign_pair(self, lvalue, rvalue, func):
        self.start('')

        # expr[expr] = expr
        if isinstance(lvalue, Subscript) and not isinstance(lvalue.subs[0], Sliceobj):
            self.subs_assign(lvalue, func)
            if defclass('list') in [t[0] for t in self.mergeinh[lvalue.expr]]:
                self.append(' = ')

            if isinstance(rvalue, str):
                self.append(rvalue)
            elif rvalue in mv.tempcount:
                self.append(mv.tempcount[rvalue])
            else:
                self.visit(rvalue, func)

            if not defclass('list') in [t[0] for t in self.mergeinh[lvalue.expr]]:
                self.append(')')
            self.eol()

        # expr.x = expr
        elif isinstance(lvalue, AssAttr):
            self.visitAssAttr(lvalue, func)

    def listcomp_func(self, node):
        # --- [x*y for (x,y) in z if c]
        lcfunc, func = self.listcomps[node]

        # --- formals: target, z if not Name, out-of-scopes 
        args = []

        for qual in node.quals:
            if not fastfor(qual) and not isinstance(qual.list, Name): # XXX ugly!!
                mv.tempcount[qual.list] = varname = '__'+str(len(mv.tempcount)) 
                args.append(typesetreprnew(qual.list, lcfunc)+varname) 

        for name in lcfunc.misses:
            if lookupvar(name, func).parent:
                args.append(typesetreprnew(lookupvar(name, lcfunc), lcfunc)+self.cpp_name(name))

        ts = typesetreprnew(node, lcfunc) 
        if not ts.endswith('*'): ts += ' '
        trepr = ''
        if lcfunc.tvars:
            trepr = 'template<'+', '.join(['class '+tvar.name for tvar in lcfunc.tvars])+'> ' 
        self.output(trepr+'static inline '+ts+lcfunc.ident+'('+', '.join(args)+') {')
        self.indent()

        # --- local: (x,y), result
        decl = {}
        for (name,var) in lcfunc.vars.items(): # XXX merge with visitFunction 
            name = self.cpp_name(name)
            decl.setdefault(typesetreprnew(var, lcfunc), []).append(name)
        for ts, names in decl.items():
            if ts.endswith('*'):
                self.output(ts+', *'.join(names)+';')
            else:
                self.output(ts+', '.join(names)+';')

        self.output(typesetreprnew(node, lcfunc)+'result = new '+typesetreprnew(node, lcfunc)[:-2]+'();')
        print >>self.out
         
        self.listcomp_rec(node, node.quals, lcfunc)
      
        # --- return result
        self.output('return result;')
        self.deindent();
        self.output('}\n')

    def fastfor_switch(self, node, func):
        self.start()
        for arg in node.list.args:
            if arg in mv.tempcount:
                self.start()
                self.visitm(mv.tempcount[arg], ' = ', arg, func)
                self.eol()
        self.start('if(')
        if node.list.args[2] in mv.tempcount:
            self.append(mv.tempcount[node.list.args[2]])
        else:
            self.visit(node.list.args[2])
        self.append('>0) {')
        print >>self.out, self.line

    # --- nested for loops: loop headers, if statements
    def listcomp_rec(self, node, quals, lcfunc):
        if not quals:
            if len(node.quals) == 1 and not fastfor(node.quals[0]) and not node.quals[0].ifs and not [t for t in self.mergeinh[node.quals[0].list] if t[0] not in (defclass('tuple'), defclass('list'))]:
                self.start('result->units['+mv.tempcount[node.quals[0]]+'] = ')
                self.visit(node.expr, lcfunc)
            else:
                self.start('result->append(')
                self.visit(node.expr, lcfunc)
                self.append(')')
            self.eol()
            return

        qual = quals[0]

        # iter var
        if isinstance(qual.assign, AssName):
            if qual.assign.name != '_':
                var = lookupvar(qual.assign.name, lcfunc)
            else:
                var = lookupvar(mv.tempcount[(qual.assign,1)], lcfunc)
        else:
            var = lookupvar(mv.tempcount[qual.assign], lcfunc)

        iter = self.cpp_name(var.name)

        # for in
        if fastfor(qual):
            #self.output('result->resize(uh);') # XXX

            if len(qual.list.args) == 3 and not isinstance(qual.list.args[2], (Const, UnarySub)): # XXX unarysub
                self.fastfor_switch(qual, lcfunc)
                self.indent()
                self.fastfor(qual, iter, '', lcfunc)
                self.listcompfor_body(node, quals, iter, lcfunc)
                self.deindent()
                self.output('} else {')
                self.indent()
                self.fastfor(qual, iter, '_NEG', lcfunc)
                self.listcompfor_body(node, quals, iter, lcfunc)
                self.deindent()
                self.output('}')
            else:
                self.fastfor(qual, iter, '', lcfunc)
                self.listcompfor_body(node, quals, iter, lcfunc)

        else:
            pref = ''
            if not [t for t in self.mergeinh[qual.list] if t[0] not in (defclass('tuple'), defclass('list'))]:
                pref = '_SEQ'

            if not isinstance(qual.list, Name):
                itervar = mv.tempcount[qual.list]
            else:
                itervar = self.cpp_name(qual.list.name)

            if len(node.quals) == 1 and not qual.ifs and pref == '_SEQ':
                self.output('result->resize(len('+itervar+'));')

            if pref == '': tail = mv.tempcount[(qual,1)][2:]
            else: tail = mv.tempcount[qual.list][2:]+','+mv.tempcount[qual][2:]

            self.start('FOR_IN'+pref+'('+iter+','+itervar+','+tail)
            print >>self.out, self.line+')'

            self.listcompfor_body(node, quals, iter, lcfunc)

    def listcompfor_body(self, node, quals, iter, lcfunc):
        qual = quals[0]

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
        self.listcomp_rec(node, quals[1:], lcfunc)

        # --- nested for loops: loop tails
        if qual.ifs: 
            self.deindent();
            self.output('}')
        self.deindent();
        self.output('END_FOR\n')

    def visitListComp(self, node, func=None): #, target=None):
        lcfunc, _ = self.listcomps[node]
        args = []
        temp = self.line

        for qual in node.quals:
            if not fastfor(qual) and not isinstance(qual.list, Name):
                self.line = ''
                self.visit(qual.list, func)
                args.append(self.line)

        for name in lcfunc.misses:
            var = lookupvar(name, func)
            if var.parent:
                if name == 'self' and not func.listcomp: # XXX parent?
                    args.append('this')
                else:
                    args.append(self.cpp_name(name))

        self.line = temp
        self.append(lcfunc.ident+'('+', '.join(args)+')')

    def visitSubscript(self, node, func=None):
        if node.flags == 'OP_DELETE':
            self.start()
            if isinstance(node.subs[0], Sliceobj):
                self.visitCallFunc(inode(node.expr).fakefunc, func)
                self.eol()
                return

            self.visitCallFunc(inode(node.expr).fakefunc, func)
            #self.visitm(node.expr, '->__delitem__(', node.subs[0], ')', func) # XXX
            self.eol()
            return

        self.visitCallFunc(inode(node.expr).fakefunc, func)
        return

    def visitMod(self, node, func=None):
        if [t for t in self.mergeinh[node.left] if t[0].ident != 'str_']:
            self.visitBinary(node.left, node.right, '__mod__', '%', func)
            return

        elif not isinstance(node.left, Const):
            error('left-hand string in mod operation should be constant', node.left, warning=True)
            self.visitm(node.left, '%', node.right, func)
            return

        self.visitm('__mod(', node.left, func)

        # pair conversion flags to mod args
        # XXX error("unsupported format character", node)

        flags = [] # XXX use in mv.visitMod
        state = 0
        for i, c in enumerate(node.left.value):
            if c == '%':
                state = 1-state
                continue
            if state == 0:
                continue
            if c in 'diouxXeEfFgGcrs':
                flags.append(c)
                state = 0

        if state == 1:
            error("incomplete format", node, warning=True)

        # str % t
        if node.right in self.mergeinh and ('tuple' in [t[0].ident for t in self.mergeinh[node.right]] or 'tuple2' in [t[0].ident for t in self.mergeinh[node.right]]):
            self.visitm(', ', node.right, func)

        else:
            # str % (..)
            if isinstance(node.right, Tuple):
                nodes = node.right.nodes

            # str % non-t
            else:
                nodes = [node.right]

            if len(flags) != len(nodes):
                error("wrong number of format arguments", node, warning=True)

            for (f, n) in zip(flags, nodes):
                if f == 'c' and 'int_' in [t[0].ident for t in self.mergeinh[n]]:
                    self.visitm(', chr(', n, ')', func)
                elif f in 'eEfFgG' and 'float_' not in [t[0].ident for t in self.mergeinh[n]]:
                    self.visitm(', __float(', n, ')', func)
                elif f in 'diouxX' and (not 'int_' in [t[0].ident for t in self.mergeinh[n]] or 'float_' in [t[0].ident for t in self.mergeinh[n]]):
                    self.visitm(', __int(', n, ')', func)
                elif f in 'sr' and 'float_' in [t[0].ident for t in self.mergeinh[n]]:
                    self.visitm(', new float_(', n, ')', func)
                elif f in 'sr' and 'int_' in [t[0].ident for t in self.mergeinh[n]]:
                    self.visitm(', new int_(', n, ')', func)
                else:
                    self.visitm(', ', n, func)

        self.append(')')

    def visitPrintnl(self, node, func=None):
        self.visitPrint(node, func, '\\n')

    def visitPrint(self, node, func=None, newline=None):
        fstring = []
        self.line = ''

        for n in node.nodes:
            self.append(', ')

            types = [t[0].ident for t in self.mergeinh[n]]
            if 'float_' in types: fstring.append('%h') 
            elif 'int_' in types: fstring.append('%d')
            else: fstring.append('%s')

            self.visit(n, func)

        fmt = ' '.join(fstring).replace('\n', '\\n')
        if newline: fmt += newline

        line = self.line
        if not newline: self.start('printc(')
        else: self.start('print(')
        if node.dest:
            self.visitm(node.dest, ', ', func)
        line = '"'+fmt+'"'+line+')'
        self.eol(line)

    def visitGetattr(self, node, func=None):
        module = lookupmodule(node.expr, inode(node).mv.imports)

        if isinstance(node.expr, Name) and node.expr.name == 'dict':
            self.append('__dict__::')
        elif module and not (isinstance(node.expr, Name) and lookupvar(node.expr.name, func)): # XXX forbid redef?
            self.append('__'+module.replace('.', '__::__')+'__::')
        else:
            if not isinstance(node.expr, (Name)):
                self.append('(')
            if isinstance(node.expr, Name) and not lookupvar(node.expr.name, func): # XXX XXX
                self.append(node.expr.name)
            else:
                self.visit(node.expr, func)
            if not isinstance(node.expr, (Name)):
                self.append(')')

            self.append(self.connector(node.expr, func))

        if self.bastard(node.attrname, node.expr):
            ident = '__getitem__'
        else:
            ident = node.attrname

        if ident == '__getitem__':
            lcp = lowest_common_parents(polymorphic_t(self.mergeinh[node.expr]))
            if len(lcp) == 1 and lcp[0] == defclass('list'):
                ident = '__getfast__'

        self.append(self.cpp_name(ident))

    def visitAssAttr(self, node, func=None): # XXX stack/static
        module = lookupmodule(node.expr, inode(node).mv.imports) 
        if module and not (isinstance(node.expr, Name) and lookupvar(node.expr.name, func)):
            self.append('__'+module.replace('.', '__::__')+'__::'+self.cpp_name(node.attrname))
        else:
            if isinstance(node.expr, Name) and not lookupvar(node.expr.name, func): # XXX XXX
                self.append(node.expr.name)
            else:
                self.visit(node.expr, func)
            self.append(self.connector(node.expr, func)+self.cpp_name(node.attrname))

    def visitAssName(self, node, func=None):
        self.append(self.cpp_name(node.name))

    def visitName(self, node, func=None, add_cl=True):
        map = {'True': '1', 'False': '0', 'self': 'this'}
        if node.name == 'None':
            self.append('0')
        elif node.name == 'self' and ((func and func.listcomp) or not isinstance(func.parent, class_)):
            self.append('self')
        elif node.name in map:
            self.append(map[node.name])

        else: # XXX clean up
            if not self.mergeinh[node] and not inode(node).parent in gx.inheritance_relations:
                error("variable '"+node.name+"' has no type", node, warning=True)
                self.append(node.name)
            elif singletype(node, module):
                self.append('__'+singletype(node, module).ident+'__')
            else:
                if (defclass('class_'),0) in self.mergeinh[node]:
                    self.append('cl_'+node.name)
                elif add_cl and [t for t in self.mergeinh[node] if isinstance(t[0], static_class)]:
                    self.append('cl_'+node.name)
                else:
                    self.append(self.cpp_name(node.name))
                
    def expandspecialchars(self, value):
        value = list(value)
        replace = dict(['\\\\', '\nn', '\tt', '\rr', '\ff', '\bb', '\vv', '""'])

        for i in range(len(value)):
            if value[i] in replace: 
                value[i] = '\\'+replace[value[i]]
            elif value[i] not in string.printable:
                value[i] = '\\'+oct(ord(value[i])).zfill(4)[1:]
             
        return ''.join(value)

    def visitConst(self, node, func=None):
        if not self.filling_consts and isinstance(node.value, str): 
            self.append(self.get_constant(node))
            return

        if node.value == None: 
            self.append('0')
            return

        t = list(inode(node).types())[0]

        if t[0].ident in ['int_','float_']: 
            if node.value == 1e500: self.append('1e500')
            elif node.value == -1e500: self.append('-1e500')
            else: self.append(str(node.value)) 
        elif t[0].ident == 'str_': 
            self.append('new str("%s"' % self.expandspecialchars(node.value))
            if '\0' in node.value: # '\0' delimiter in C
                self.append(', %d' % len(node.value))
            self.append(')')
        else: 
            self.append('new %s(%s)' % (t[0].ident, node.value))

def split_classes(split):
    alltypes = set()
    for (dcpa, cpa), types in split.items():
        alltypes.update(types)

    return set([t[0] for t in alltypes if isinstance(t[0], class_)])
    
def split_subsplit(split, varname, tvar=True):
    subsplit = {}
    for (dcpa, cpa), types in split.items():
        subsplit[dcpa, cpa] = set()
        for t in types:
            if tvar and not varname in t[0].template_vars: # XXX 
                continue

            if tvar:
                var = t[0].template_vars[varname]
            else:
                var = t[0].vars[varname]

            if (var, t[1], 0) in gx.cnode: # XXX yeah?
                subsplit[dcpa, cpa].update(gx.cnode[var, t[1], 0].types())

    return subsplit

# --- determine representation of node type set (within parameterized context)
def typesetreprnew(node, parent, cplusplus=True):
    orig_parent = parent
    while is_listcomp(parent): # XXX redundant with typesplit?
        parent = parent.parent

    # --- separate types in multiple duplicates, so we can do parallel template matching of subtypes..
    split = typesplit(node, parent)
    #print 'split', node, split

    # --- use this 'split' to determine type representation
    ts = typestrnew(split, parent, cplusplus, orig_parent, node) 
    if cplusplus: 
        if not ts.endswith('*'): ts += ' '
        return ts
    return '['+ts+']'

def typestrnew(split, root_class, cplusplus, orig_parent, node=None):
    #print 'typestrnew', split, root_class

    # --- annotation or c++ code
    conv1 = {'int_': 'int', 'float_': 'double', 'str_': 'str', 'none': 'int'}
    conv2 = {'int_': 'int', 'float_': 'float', 'str_': 'str', 'class_': 'class', 'none': 'None'}
    if cplusplus: sep, ptr, conv = '<>', ' *', conv1
    else: sep, ptr, conv = '()', '', conv2

    def map(ident):
        if cplusplus: return ident+' *'
        return conv.get(ident, ident)

    # --- examine split
    alltypes = set() # XXX
    for (dcpa, cpa), types in split.items():
        alltypes.update(types)

    anon_funcs = set([t[0] for t in alltypes if isinstance(t[0], function)])
    if anon_funcs:
        f = anon_funcs.pop()
        if not f in mv.lambda_signum: # XXX method reference
            return '__method_ref_0'
        return 'lambda'+str(mv.lambda_signum[f])

    classes = polymorphic_cl(split_classes(split))
    lcp = lowest_common_parents(classes)

    # --- multiple parent classes: check template variables
    if len(lcp) > 1:              
        tvar = template_match(split, root_class, orig_parent)
        if tvar: return tvar.name
        if set(lcp) == set([defclass('int_'),defclass('float_')]):
            return conv['float_']
        if inode(node).mv.module.builtin:
            return '***ERROR*** '
        if isinstance(node, variable):
            if not node.name.startswith('__') :
                #print 'beh', classes, lcp, split, template_match(split, root_class, orig_parent)

                if orig_parent: varname = "%s" % node
                else: varname = "'%s'" % node
                error("variable %s has dynamic (sub)type: {%s}" % (varname, ', '.join([conv2.get(cl.ident, cl.ident) for cl in lcp])), warning=True)
        elif not isinstance(node, (Or,And)):
            error("expression has dynamic (sub)type: {%s}" % ', '.join([conv2.get(cl.ident, cl.ident) for cl in lcp]), node, warning=True)

    elif not classes:
        if cplusplus: return 'void *'
        return ''

    cl = lcp.pop() 

    # --- simple built-in types
    if cl.ident in ['int_', 'float_','none']:
        return conv[cl.ident]
    elif cl.ident == 'str_':
        return 'str'+ptr 
            
    # --- namespace prefix
    namespace = ''
    if cl.module not in [mv.module, gx.modules['builtin']] and not (cl.ident in mv.ext_funcs or cl.ident in mv.ext_classes):
        namespace = cl.module.ident+'::'
        if cplusplus: namespace = '__'+cl.module.ident+'__::'

    # --- recurse for types with parametric subtypes
    template_vars = cl.template_vars # XXX why needed
    if cl.ident in ['pyiter', 'pyseq','pyset']: # XXX dynamic subtype check
        for c in classes:
            if 'A' in c.template_vars:
                template_vars = {'A': c.template_vars['A']}
    #else:
    #    template_vars = cl.template_vars

    if not template_vars:
        if cl.ident in gx.cpp_keywords:
            return namespace+gx.ss_prefix+map(cl.ident)
        return namespace+map(cl.ident)

    subtypes = [] 
    for tvar in template_vars:
        if cl.ident == 'tuple' and tvar != cl.unittvar:
            continue

        subsplit = split_subsplit(split, tvar)
        subtypes.append(typestrnew(subsplit, root_class, cplusplus, orig_parent, node))

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
        
    if ident in gx.cpp_keywords:
        ident = gx.ss_prefix+ident

    # --- final type representation
    return namespace+ident+sep[0]+', '.join(subtypes)+sep[1]+ptr


# --- separate types in multiple duplicates
def typesplit(node, parent):
    split = {} 

    if isinstance(parent, function) and parent in gx.inheritance_relations: # XXX templates
        if node in gx.merged_inh:
            split[1,0] = gx.merged_inh[node]
        return split

    while is_listcomp(parent): 
        parent = parent.parent

    if isinstance(parent, class_): # class variables
        for dcpa in range(1, parent.dcpa):
            if (node, dcpa, 0) in gx.cnode:
                split[dcpa, 0] = gx.cnode[node, dcpa, 0].types()

    elif isinstance(parent, function):
        if isinstance(parent.parent, class_): # method variables/expressions (XXX nested functions)
            for dcpa in range(1, parent.parent.dcpa):
                if dcpa in parent.cp:
                    for cpa in range(len(parent.cp[dcpa])): 
                        if (node, dcpa, cpa) in gx.cnode:
                            split[dcpa, cpa] = gx.cnode[node, dcpa, cpa].types()

        else: # function variables/expressions
            if 0 in parent.cp:
                for cpa in range(len(parent.cp[0])): 
                    if (node, 0, cpa) in gx.cnode:
                        split[0, cpa] = gx.cnode[node, 0, cpa].types()
    else:
        split[0, 0] = inode(node).types()

    return split

# --- determine lowest common parent classes (inclusive)
def lowest_common_parents(classes):
    lcp = set(classes)

    changed = 1
    while changed:
        changed = 0
        for cl in gx.allclasses:
             desc_in_classes = [[c for c in ch.descendants(inclusive=True) if c in lcp] for ch in cl.children]
             if len([d for d in desc_in_classes if d]) > 1:
                 for d in desc_in_classes:
                     lcp.difference_update(d)
                 lcp.add(cl)
                 changed = 1

    for cl in lcp.copy():
        if isinstance(cl, class_): # XXX
            lcp.difference_update(cl.descendants())

    result = [] # XXX there shouldn't be doubles
    for cl in lcp:
        if cl.ident not in [r.ident for r in result]:
            result.append(cl)
    return result

def printtypeset(types):
    l = list(types.items())
    l.sort(lambda x, y: cmp(repr(x[0]),repr(y[0])))
    for uh in l:
        if not uh[0].mv.module.builtin:
            print repr(uh[0])+':', uh[1] #, uh[0].parent
    print

def printstate():
    #print 'state:'
    printtypeset(gx.types)
    
def printconstraints():
    #print 'constraints:'
    l = list(gx.constraints)
    l.sort(lambda x, y: cmp(repr(x[0]),repr(y[0])))
    for (a,b) in l:
        if not (a.mv.module.builtin and b.mv.module.builtin):
            print a, '->', b
            if not a in gx.types or not b in gx.types:
                print 'NOTYPE', a in gx.types, b in gx.types
    print

def cartesian(*lists):
    if not lists:
        return [()]
    result = []
    prod = cartesian(*lists[:-1])
    for x in prod:
        for y in lists[-1]:
            result.append(x + (y,))
    return result
  
errormsgs = set()

def seed_nodes():
    for node in gx.types:
        if isinstance(node.thing, Name):
            if node.thing.name in ['True', 'False']:
                gx.types[node] = set([(defclass('int_'), 0)])
            elif node.thing.name == 'None':
                gx.types[node] = set([(defclass('none'), 0)])

def in_out(a, b):
    a.out.add(b)
    b.in_.add(a)

def addconstraint(a, b, worklist=None):
    gx.constraints.add((a,b))
    in_out(a, b)
    addtoworklist(worklist, a)
    
def addtoworklist(worklist, node):
    if worklist != None and not node.in_list:
        worklist.append(node)
        node.in_list = 1

def init_worklist():
    worklist = []
    for node, types in gx.types.items():
        if types: 
            addtoworklist(worklist, node)
    return worklist

# --- iterative dataflow analysis

def propagate():
    #print 'propagate'
    seed_nodes()
    worklist = init_worklist()
    #print 'worklist', worklist

    gx.checkcallfunc = [] # XXX 

    # --- check whether seeded nodes are object/argument to call  
    changed = set()
    for w in worklist:
        for callfunc in w.callfuncs:
            #print 'seed changed', w.callfunc, w.dcpa, w.cpa
            changed.add(gx.cnode[callfunc, w.dcpa, w.cpa])

    # --- statically bind calls without object/arguments 
    for node in gx.types:
        expr = node.thing
        if isinstance(expr, CallFunc) and not expr.args:
            changed.add(node)

    for node in changed:
        cpa(node, worklist)

    # --- iterative dataflow analysis
    while worklist:
        a = worklist.pop(0)
        a.in_list = 0
         
        for b in a.out.copy(): # XXX kan veranderen...?
            # for builtin types, the set of instance variables is known, so do not flow into non-existent ones # XXX ifa
            if isinstance(b.thing, variable) and isinstance(b.thing.parent, class_) and b.thing.parent.ident in gx.builtins:
                if b.thing.parent.ident in ['int_', 'float_', 'str_', 'none']: continue
                elif b.thing.parent.ident in ['list', 'tuple', 'frozenset', 'set', 'file','__iter'] and b.thing.name != 'unit': continue 
                elif b.thing.parent.ident == 'dict' and b.thing.name not in ['unit', 'value']: continue
                elif b.thing.parent.ident == 'tuple2' and b.thing.name not in ['unit', 'first', 'second']: continue

                #print 'flow', a, b #, difference #, difference, gx.types[b], b.callfunc

            difference = gx.types[a] - gx.types[b]

            if difference:
                if isinstance(b.thing, variable) and b.thing.filter: # apply filter
                    #print 'aha', b.thing.filter, difference, [d for d in difference if d[0] in b.thing.filter] 
                    difference = set([d for d in difference if d[0] in b.thing.filter])

                gx.types[b].update(difference)

                # --- flow may be constrained by run-time checks, e.g. isinstance(..) # XXX and by method calls
                #if (b.thing, 0, 0) in gx.cnode: # XXX
                #    filters = gx.cnode[b.thing, 0, 0].filters
                #    if filters:
                #        print 'filter', b.thing, filters
                #        gx.types[b] = set([t for t in gx.types[b] if t[0] in filters]) # XXX efficiency, inheritance

                # --- check whether node corresponds to actual argument: if so, perform cartesian product algorithm
                for callfunc in b.callfuncs:
                    #print 'id changed', b.callfunc, b.dcpa, b.cpa, gx.types[b], a
                    cpa(gx.cnode[callfunc, b.dcpa, b.cpa], worklist)

                addtoworklist(worklist, b)

                while gx.checkcallfunc: # XXX
                    b = gx.checkcallfunc.pop()
                    for callfunc in b.callfuncs:
                        cpa(gx.cnode[callfunc, b.dcpa, b.cpa], worklist)


def lookupmodule(node, imports):
    orig_node = node
    module = ''
    while isinstance(node, Getattr):
        module = '.' + node.attrname + module
        node = node.expr
    if isinstance(node, Name) and node.name + module in imports:
        return node.name + module
    return None

# --- static analysis of call: namespace, method call, direct call/constructor
def analyze_callfunc(node, check_exist=False): # XXX generate target list XXX uniform variable system!
    #print 'analyze callnode', node, inode(node).parent
    namespace, objexpr, method_call, mod_var, parent_constr = inode(node).mv.module, None, False, False, False # XXX mod_var
    constructor, direct_call = None, None
    imports = inode(node).mv.imports

    # method call
    if isinstance(node.node, Getattr): 
        objexpr, ident = node.node.expr, node.node.attrname

        if isinstance(objexpr, Name) and inode(node).parent:
            cl = inode(node).parent.parent
            if isinstance(cl, class_) and objexpr.name in [x.ident for x in cl.bases]:
                parent_constr = True
                ident = ident+objexpr.name+'__'
                return objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr

        var = lookupvar(ident, inode(node).parent)
        module = lookupmodule(node.node.expr, imports)
         
        if module and (not var or not var.parent): # XXX var.parent?
            namespace, objexpr = imports[module], None

        elif isinstance(objexpr, Name) and (objexpr.name == 'dict') and (not var or not var.parent):
            namespace, objexpr = defclass('dict'), None
            if ident in imports['builtin'].funcs:
                direct_call = imports['builtin'].funcs[ident] # XXX beh
                return objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr
        else:
            method_call = True

    elif isinstance(node.node, Name):
        ident = node.node.name
    else:
        ident = 'meuk' # XXX ?

    # direct [constructor] call
    if isinstance(node.node, Name) or namespace != inode(node).mv.module: 
        if ident in ['max','min','sum'] and len(node.args) == 1:
            ident = '__'+ident
        elif ident == 'zip' and len(node.args) <= 3:
            if not node.args:
                error("please provide 'zip' with arguments", node)
            ident = '__zip'+str(len(node.args))

        if ident in ['list','tuple','frozenset','set','dict'] and not node.args:
            constructor = namespace.mv.ext_classes[ident]
        elif ident in namespace.mv.classes:
            constructor = namespace.mv.classes[ident]
        elif ident not in ['list','tuple','dict'] and ident in namespace.mv.ext_classes: # XXX cleanup
            constructor = namespace.mv.ext_classes[ident]
        elif ident in namespace.mv.funcs:
            direct_call = namespace.mv.funcs[ident]
        elif ident in namespace.mv.ext_funcs:
            direct_call = namespace.mv.ext_funcs[ident]

        else:
            if isinstance(node.node, Name):
                var = lookupvar(ident, inode(node).parent)
                if var:
                    return objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr

            if namespace != inode(node).mv.module:
                return objexpr, ident, None, False, None, True, False
            elif check_exist: 
                traceback.print_stack()
                error("unbound identifier '"+ident+"'", node)

    return objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr

# --- return list of potential call targets
def callfunc_targets(node, merge):
    objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(node)
    funcs = []

    if node.node in merge and [t for t in merge[node.node] if isinstance(t[0], function)]: # anonymous function call
        funcs = [t[0] for t in merge[node.node]]

    elif constructor:
        if ident == 'defaultdict' and len(node.args) == 2:
            funcs = [constructor.funcs['__initdict__']] # XXX __initi__
        elif '__init__' in constructor.funcs: 
            funcs = [constructor.funcs['__init__']]

    elif parent_constr:
        if ident != '__init__':
            cl = inode(node).parent.parent
            funcs = [cl.funcs[ident]]

    elif direct_call:
        funcs = [direct_call]

    elif method_call:
        classes = set([t[0] for t in merge[objexpr]])
        funcs = [cl.funcs[ident] for cl in classes if ident in cl.funcs]

    return funcs
        
# --- determine cartesian product of possible function and argument types
def cartesian_product(node, worklist):
    expr = node.thing

    # --- determine possible target functions
    objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(expr, True)
    anon_func = False
    funcs = []

    if not node.mv.module.builtin or node.mv.module.ident == 'path': # XXX to analyze_callfunc
        subnode = expr.node, node.dcpa, node.cpa
        if subnode in gx.cnode:
            stypes = gx.cnode[subnode].types() 
            if [t for t in stypes if isinstance(t[0], function)]:
                anon_func = True

    if anon_func:
        # anonymous call 
        types = gx.cnode[expr.node, node.dcpa, node.cpa].types()

        if types:
            if list(types)[0][0].parent: # method reference XXX merge below?
                funcs = [(f[0], f[1], (f[0].parent, f[1])) for f in types] # node.dcpa: connect to right dcpa duplicate version 
            else: # function reference
                funcs = [(f[0], f[1], None) for f in types] # function call: only one version; no objtype
        else:
            funcs = []

    elif constructor:
        funcs = [(t[0].funcs['__init__'], t[1], t) for t in node.types() if '__init__' in t[0].funcs]

    elif parent_constr:
        objtypes = gx.cnode[lookupvar('self', node.parent), node.dcpa, node.cpa].types() 
        funcs = [(t[0].funcs[ident], t[1], None) for t in objtypes if ident in t[0].funcs]

    elif direct_call:
        funcs = [(direct_call, 0, None)]

        if ident == 'dict':
            clnames = [t[0].ident for t in gx.cnode[expr.args[0],node.dcpa,node.cpa].types() if isinstance(t[0], class_)]
            if 'dict' in clnames or 'defaultdict' in clnames:
                funcs = [(node.mv.ext_funcs['__dict'], 0, None)]

    elif method_call:
        objtypes = gx.cnode[objexpr, node.dcpa, node.cpa].types() 
        funcs = [(t[0].funcs[ident], t[1], t) for t in objtypes if ident in t[0].funcs]

    # --- argument types XXX connect_actuals_formals

    args = [arg for arg in expr.args if not isinstance(arg, Keyword)]
    keywords = [arg for arg in expr.args if isinstance(arg, Keyword)]

    kwdict = {}
    for kw in keywords: kwdict[kw.name] = kw.expr

    if expr.star_args: args.append(expr.star_args)
    if expr.dstar_args: args.append(expr.dstar_args)

    if funcs: # XXX return here
        func = funcs[0][0] # XXX
        if parent_constr: # XXX merge
            formals = [f for f in func.formals if not f in [func.varargs, func.kwargs]]
        else:
            formals = [f for f in func.formals if not f in ['self', func.varargs, func.kwargs]]
        uglyoffset = len(func.defaults)-(len(formals)-len(args))

        for (i, formal) in enumerate(formals[len(args):]):
            #print 'formal', i, formal
            if formal in kwdict:
                args.append(kwdict[formal])
                continue

            if not func.defaults: # XXX
                continue
            default = func.defaults[i+uglyoffset]
            args.append(default)

            if not node.defnodes:
                defnode = cnode((inode(node.thing),i), node.dcpa, node.cpa, parent=func)
                gx.types[defnode] = set()

                defnode.callfuncs.append(node.thing)
                addconstraint(gx.cnode[default, 0, 0], defnode, worklist)
        node.defnodes = True

    argtypes = [] # XXX
    for arg in args:
        if (arg, node.dcpa, node.cpa) in gx.cnode:
            argtypes.append(gx.cnode[arg,node.dcpa,node.cpa].types()) 
        else:
            argtypes.append(inode(arg).types()) # XXX def arg?

    #print 'argtypes', argtypes, node #, args, argtypes, cartesian(*([funcs]+argtypes))

    return cartesian(*([funcs]+argtypes))


# --- cartesian product algorithm; adds interprocedural constraints
def cpa(callnode, worklist):
    cp = cartesian_product(callnode, worklist) 
    if not cp: return

    objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(callnode.thing)

    # --- iterate over argument type combinations
    for c in cp:
        #print '(func, dcpa, objtype), c', c[0], c[1:]
        (func, dcpa, objtype), c = c[0], c[1:]

        if objtype: objtype = (objtype,)
        else: objtype = ()

        if ident == 'defaultdict' and len(callnode.thing.args) == 2:
            clnames = [x[0].ident for x in c if isinstance(x[0], class_)]
            if 'dict' in clnames or 'defaultdict' in clnames:
                func = list(callnode.types())[0][0].funcs['__initdict__'] 
            else:
                func = list(callnode.types())[0][0].funcs['__inititer__'] 

        # filter CPA terms using filters on formals
        if not func.mv.module.builtin and not func.ident in ['__getattr__', '__setattr__']:
            #print 'cpa term', func, c
            blocked = 0
            if objtype: formals = func.formals[1:]
            else: formals = func.formals
            for t, filter in zip(c, [func.vars[formal].filter for formal in formals]):
                if filter and t[0] not in filter:
                    #print 'cpa filter', func, c, t[0], filter
                    blocked = 1
                    break
            if blocked:
                continue

        if (func,)+objtype+c in callnode.nodecp:
            continue 
        callnode.nodecp.add((func,)+objtype+c)

        if not dcpa in func.cp: func.cp[dcpa] = {}
        template_exists = c in func.cp[dcpa]
        if template_exists:
            pass
        else:
            # --- unseen cartesian product: create new template
            func.cp[dcpa][c] = cpa = len(func.cp[dcpa]) # XXX +1

            #if not func.mv.module.builtin and not func.ident in ['__getattr__', '__setattr__']:
            #    print 'template', (func, dcpa), c

            gx.templates += 1
            func.copy(dcpa, cpa, worklist, c)

        cpa = func.cp[dcpa][c]
        callfunc = callnode.thing

        # --- actuals and formals 
        if isinstance(callfunc.node, Getattr) and callfunc.node.attrname in ['__setattr__', '__getattr__']: # variables
            # builtin methods
            varname = callfunc.args[0].value
            #if varname in func.parent.funcs and callfunc.node.attrname == '__getattr__' and not callnode.parent_callfunc: # XXX
            #    gx.types[callnode] = set([(func.parent.funcs[varname], objtype[0][1])])
            #    addtoworklist(worklist, callnode)
            #    gx.method_refs.add(callnode.thing)
            #    continue

            var = defaultvar(varname, func.parent, worklist) # XXX always make new var??
            inode(var).copy(dcpa,0,worklist)

            if not gx.cnode[var,dcpa,0] in gx.types:
                gx.types[gx.cnode[var,dcpa,0]] = set()

            gx.cnode[var,dcpa,0].mv = func.parent.module.mv # XXX move into defaultvar

            if callfunc.node.attrname == '__setattr__':
                addconstraint(gx.cnode[callfunc.args[1],callnode.dcpa,callnode.cpa], gx.cnode[var,dcpa,0], worklist)
            else:
                addconstraint(gx.cnode[var,dcpa,0], callnode, worklist)

            continue
        else: 
            # non-builtin methods, functions
            actuals_formals(callfunc, func, callnode, dcpa, cpa, objtype+c, worklist)

        # --- call and return expressions
        if func.retnode and not constructor:
            retnode = gx.cnode[func.retnode.thing, dcpa, cpa]
            addconstraint(retnode, callnode, worklist)

def actuals_formals(expr, func, node, dcpa, cpa, types, worklist):
    objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(expr) # XXX call less

    actuals = [a for a in expr.args if not isinstance(a, Keyword)]
    formals = [f for f in func.formals if not f in [func.varargs, func.kwargs]]
    keywords = [a for a in expr.args if isinstance(a, Keyword)]

    anon_func = False
    meth_func = False
    if not node.mv.module.builtin: # XXX to analyze_callfunc
        subnode = expr.node, node.dcpa, node.cpa
        if subnode in gx.cnode:
            stypes = gx.cnode[subnode].types() 
            if [t for t in stypes if isinstance(t[0], function)]:
                anon_func = True
            if [t for t in stypes if isinstance(t[0], function) and t[0].parent]:
                meth_func = True

    # --- check for correct number of arguments
   
    # add a slot in case of implicit 'self'
    smut = actuals[:] # XXX smut unneeded
    if meth_func:
        smut = [None]+smut # XXX add type here
    if parent_constr or anon_func:
        pass
    elif method_call or constructor:
        smut = [None]+smut # XXX add type here
    elif not direct_call: # XXX ?
        types2 = gx.cnode[expr.node, node.dcpa, node.cpa].types()
        if list(types2)[0][0].parent: 
            smut = [None]+smut

    for formal in formals:
        for kw in keywords:
            if formal == kw.name:
                actuals.append(kw.expr)
                smut.append(kw.expr)

    # XXX add defaults to smut here, simplify code below
    if not ident in ['min','max','bool'] and not (expr.star_args or expr.dstar_args or func.varargs or func.kwargs) and (len(smut) < len(formals)-len(func.defaults) or len(smut) > len(formals)): # XXX star_args etc. XXX keywords <-> defaults
        return

    # --- connect/seed as much direct arguments as possible

    if len(smut) < len(formals):
        smut = smut + func.defaults[-len(formals)+len(smut):]

    #print 'aft', types #expr, smut, formals, types, zip(smut, formals, types)

    for (actual, formal, formaltype) in zip(smut, formals, types):
        #print 'connect', actual, formal, formaltype, node
        formalnode = gx.cnode[func.vars[formal], dcpa, cpa]

        if formaltype[1] != 0: # ifa: remember dataflow information for non-simple types
            if actual == None:
                if constructor: 
                    objexpr = node.thing

                if method_call or constructor:
                    formalnode.in_.add(gx.cnode[objexpr, node.dcpa, node.cpa]) 
            else:
                if actual in func.defaults:
                    formalnode.in_.add(gx.cnode[actual, 0, 0])
                else:
                    formalnode.in_.add(gx.cnode[actual, node.dcpa, node.cpa])
                
        gx.types[formalnode].add(formaltype)
        addtoworklist(worklist, formalnode)

def connect_actual_formal(expr, func, parent_constr=False, check_error=False):
    pairs = []

    actuals = [a for a in expr.args if not isinstance(a, Keyword)]
    if isinstance(func.parent, class_): 
        formals = [f for f in func.formals if not f in ['self', func.varargs, func.kwargs]]
    else:
        formals = [f for f in func.formals if not f in [func.varargs, func.kwargs]]
    keywords = [a for a in expr.args if isinstance(a, Keyword)]

    if parent_constr: actuals = actuals[1:] 

    if check_error and func.ident not in ['min', 'max']:
        if len(actuals)+len(keywords) > len(formals) and not func.varargs:
            #if func.ident != 'join':
            if not (func.mv.module.builtin and func.mv.module.ident == 'path' and func.ident == 'join'): # XXX
                traceback.print_stack()
                error("too many arguments in call to '%s'" % func.ident, expr)
        if len(actuals)+len(keywords) < len(formals)-len(func.defaults) and not expr.star_args:
            error("not enough arguments in call to '%s'" % func.ident, expr)

        missing = formals[len(actuals):-len(func.defaults)] 
        if [x for x in missing if not x in [a.name for a in keywords]]:
            error("no '%s' argument in call to '%s'" % (missing[0], func.ident))

    kwdict = {}
    for kw in keywords: 
        if kw.name not in formals:
            error("no argument '%s' in call to '%s'" % (kw.name, func.ident), expr)
        kwdict[kw.name] = kw.expr

    uglyoffset = len(func.defaults)-(len(formals)-len(actuals))

    # --- connect regular, default and keyword arguments
    if not func.mv.module.builtin or func.mv.module.ident in ['random', 'itertools']: # XXX investigate
        for (i, formal) in enumerate(formals[len(actuals):]):
            if formal in kwdict:
                actuals.append(kwdict[formal])
                continue

            if not func.defaults: # XXX
                continue
            default = func.defaults[i+uglyoffset]
            actuals.append(default)

    for (actual, formal) in zip(actuals, formals):
        pairs.append((actual, func.vars[formal]))

    # --- actual star argument: unpack to extra formals
    if expr.star_args: 
        pairs.append((expr.star_args, tuple([func.vars[f] for f in formals[len(actuals):]])))

    # --- formal star argument: pack actual arguments
    if func.varargs:
        pairs.append((tuple(actuals[len(formals):]), func.vars[func.varargs]))

    return pairs

def error(msg, node=None, warning=False):
    if msg in errormsgs: return
    errormsgs.add(msg)
        
    if warning: type = '*WARNING*'
    else: type = '*ERROR*'
    if node: lineno = ':'+str(node.lineno)
    else: lineno = ''
    msg = type+' '+mv.module.ident+lineno+': '+msg
    print msg

    if not warning:
        sys.exit()

# --- merge constraint network along combination of given dimensions (dcpa, cpa, inheritance)
# e.g. for annotation we merge everything; for code generation, we might want to create specialized code
def merged(nodes, dcpa=False, inheritance=False): 
    merge = {}

    #for n in nodes:
    #    if isinstance(n.thing, Name) and n.thing.name == '__0':
    #        print 'jow', n, n.parent, n.thing in gx.inherited

    if inheritance: # XXX do we really need this crap
        mergeinh = merged([n for n in nodes if n.thing in gx.inherited])
        nodes = [n for n in nodes if not n.thing in gx.inherited] 
        mergenoinh = merged(nodes)

    for node in nodes:
        # --- merge node types
        if dcpa: sort = (node.thing, node.dcpa)
        else: sort = node.thing
        merge.setdefault(sort, set()).update(gx.types[node]) 

        # --- merge inheritance nodes
        if inheritance:
            inh = gx.inheritance_relations.get(node.thing, [])

            # merge function variables with their inherited versions (we don't customize!)
            if isinstance(node.thing, variable) and isinstance(node.thing.parent, function):
                var = node.thing

                for inhfunc in gx.inheritance_relations.get(var.parent, []):
                    if var.name in inhfunc.vars:
                        if inhfunc.vars[var.name] in mergenoinh: # XXX
                            merge.setdefault(sort, set()).update(mergenoinh[inhfunc.vars[var.name]])

            # node is not a function variable
            else:
                if isinstance(node, Name) and node.name == '__0':
                    print 'merge', node

                for n in inh:
                    if n in mergeinh: # XXX
                        merge.setdefault(sort, set()).update(mergeinh[n]) 

    return merge

# --- annotate original code; use above function to merge results to original code dimensions
def annotate():
    global mv
    def paste(expr, text):
        if not expr.lineno: return
        if (expr,0,0) in gx.cnode and inode(expr).mv != mv: return # XXX
        line = source[expr.lineno-1][:-1]
        if '#' in line: line = line[:line.index('#')]
        if text != '':
            text = '# '+text
        line = string.rstrip(line)
        if text != '' and len(line) < 40: line += (40-len(line))*' '
        source[expr.lineno-1] = line 
        if text: source[expr.lineno-1] += ' ' + text
        source[expr.lineno-1] += '\n'

    for module in gx.modules.values(): 
        mv = module.mv

        # merge type information for nodes in module XXX inheritance across modules?
        merge = merged([n for n in gx.types if n.mv == mv], inheritance=True)

        source = open(module.filename).readlines()

        # --- constants/names/attributes
        for expr in merge:
            if isinstance(expr, (Const, Name)):
                paste(expr, typesetreprnew(expr, inode(expr).parent, False))
        for expr in merge:
            if isinstance(expr, Getattr):
                paste(expr, typesetreprnew(expr, inode(expr).parent, False))
        for expr in merge:
            if isinstance(expr, (Tuple,List,Dict)):
                paste(expr, typesetreprnew(expr, inode(expr).parent, False))

        # --- instance variables
        funcs = mv.funcs.values()
        for cl in mv.classes.values():
            labels = [var.name+': '+typesetreprnew(var, cl, False) for var in cl.vars.values() if var in merge and merge[var] and not var.name.startswith('__')] 
            if labels: paste(cl.node, ', '.join(labels))
            funcs += cl.funcs.values()

        # --- function variables
        for func in funcs:
            if not func.node or func.node in gx.inherited: continue
            vars = [func.vars[f] for f in func.formals]
            labels = [var.name+': '+typesetreprnew(var, func, False) for var in vars if not var.name.startswith('__')]
            paste(func.node, ', '.join(labels))

        # --- callfuncs
        for callfunc, _ in mv.callfuncs:
            if isinstance(callfunc.node, Getattr):
                if not isinstance(callfunc.node, (fakeGetattr, fakeGetattr2, fakeGetattr3)):
                    paste(callfunc.node.expr, typesetreprnew(callfunc, inode(callfunc).parent, False))
            else: 
                paste(callfunc.node, typesetreprnew(callfunc, inode(callfunc).parent, False))

        # --- higher-level crap (listcomps, returns, assignments, prints)
        for expr in merge: 
            if isinstance(expr, ListComp):
                paste(expr, typesetreprnew(expr, inode(expr).parent, False))
            elif isinstance(expr, Return):
                paste(expr, typesetreprnew(expr.value, inode(expr).parent, False))
            elif isinstance(expr, (AssTuple, AssList)):
                paste(expr, typesetreprnew(expr, inode(expr).parent, False))
            elif isinstance(expr, (Print,Printnl)):
                paste(expr, ', '.join([typesetreprnew(child, inode(child).parent, False) for child in expr.nodes]))

        # --- assignments
        for expr in merge: 
            if isinstance(expr, Assign):
                pairs = assign_rec(expr.nodes[0], expr.expr)
                paste(expr, ', '.join([typesetreprnew(r, inode(r).parent, False) for (l,r) in pairs]))
            elif isinstance(expr, AugAssign):
                paste(expr, typesetreprnew(expr.expr, inode(expr).parent, False))

        # --- output annotated file (skip if no write permission)
        if not module.builtin: 
            try:
                out = open(module.filename[:-3]+'.ss.py','w')
                out.write(''.join(source))
                out.close()
            except IOError:
                pass


def nodetypes(node):
    return list(set(inode(node).types()))

def merge_identical_types():
    pass

def unboxable(types):
    if not isinstance(types, set):
        types = inode(types).types()
    classes = set([t[0] for t in types])

    if [cl for cl in classes if cl.ident not in ['int_','float_']]:
        return None
    else:
        if classes:
            return classes.pop().ident
        return None

# --- XXX description, confusion_misc?
def confusion_misc(): 
    confusion = set()

    # --- tuple2

    # use regular tuple if both elements have the same type representation
    cl = defclass('tuple')
    var1 = lookupvar('first', cl)
    var2 = lookupvar('second', cl)
    if not var1 or not var2: return # XXX ?

    for dcpa in gx.tuple2.copy():
        gx.tuple2.remove(dcpa)

    # use regular tuple template for tuples used in addition
    for node in gx.merged_all:
        if isinstance(node, CallFunc):
            if isinstance(node.node, Getattr) and node.node.attrname in ['__add__','__iadd__'] and not isinstance(node.args[0], Const):

                tupletypes = set()
                for types in [gx.merged_all[node.node.expr], gx.merged_all[node.args[0]]]:
                    for t in types: 
                        if t[0].ident == 'tuple':  
                            if t[1] in gx.tuple2:
                                gx.tuple2.remove(t[1])
                                gx.types[gx.cnode[var1, t[1], 0]].update(gx.types[gx.cnode[var2, t[1], 0]])

                            tupletypes.update(gx.types[gx.cnode[var1, t[1], 0]])

# --- determine virtual methods and variables
def analyze_virtuals(): 
    for node in gx.merged_inh: # XXX all:
        # --- for every message
        if isinstance(node, CallFunc) and not inode(node).mv.module.builtin: #ident == 'builtin':
            objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(node)
            if not method_call or objexpr not in gx.merged_inh: 
                continue # XXX

            # --- determine abstract receiver class
            classes = polymorphic_t(gx.merged_inh[objexpr]) 
            if not classes:
                continue

            if isinstance(objexpr, Name) and objexpr.name == 'self': 
                abstract_cl = inode(objexpr).parent.parent
            else:
                lcp = lowest_common_parents(classes)
                lcp = [x for x in lcp if isinstance(x, class_)] # XXX 
                if not lcp:
                    continue
                abstract_cl = lcp[0] 

            if not abstract_cl or not isinstance(abstract_cl, class_):
                continue 
            subclasses = [cl for cl in classes if subclass(cl, abstract_cl)] 

            # --- register virtual method
            if not ident.startswith('__'):  
                redefined = False
                for concrete_cl in classes:
                    if [cl for cl in concrete_cl.ancestors_upto(abstract_cl) if ident in cl.funcs and not cl.funcs[ident].inherited]:
                        redefined = True

                if redefined:
                    abstract_cl.virtuals.setdefault(ident, set()).update(subclasses)

            # --- register virtual var
            elif ident in ['__getattr__','__setattr__'] and subclasses:      
                var = defaultvar(node.args[0].value, abstract_cl)
                abstract_cl.virtualvars.setdefault(node.args[0].value, set()).update(subclasses)


# --- merge variables assigned to via 'self.varname = ..' in inherited methods into base class
def upgrade_variables():
    for node, inheritnodes in gx.inheritance_relations.items():
        if isinstance(node, AssAttr): 
            baseclass = inode(node).parent.parent
            inhclasses = [inode(x).parent.parent for x in inheritnodes]
            var = defaultvar(node.attrname, baseclass)

            for inhclass in inhclasses:
                inhvar = lookupvar(node.attrname, inhclass)

                if (var, 1, 0) in gx.cnode:
                    newnode = gx.cnode[var,1,0]
                else:
                    newnode = cnode(var, 1, 0, parent=baseclass)
                    gx.types[newnode] = set()

                if inhvar in gx.merged_all: # XXX ?
                    gx.types[newnode].update(gx.merged_all[inhvar])


def subclass(a, b):
    if b in a.bases:
        return True
    else:
        return a.bases and subclass(a.bases[0], b) # XXX mult inh

def template_parameters():
    # --- determine initial template variables (we might add prediction here later on)
    for cl in gx.allclasses: # (first do class template vars, as function depend on them) # XXX recursion!
         #if not cl.bases and not cl.children: # XXX
             if cl.ident in ['dict', 'defaultdict'] and 'unit' in cl.vars and 'value' in cl.vars:
                 vars = [cl.vars['unit'], cl.vars['value']]
             elif cl == defclass('tuple2') and 'first' in cl.vars and 'second' in cl.vars:
                 vars = [cl.vars['first'], cl.vars['second']]
             else:
                 vars = cl.vars.values()

             for var in vars:
                 template_detect(var, cl)

    for clname in ['list', 'tuple', 'set', 'frozenset']: # XXX remove
        if not 'A' in defclass(clname).template_vars:
            defaultvar('A', defclass(clname), template_var=True)
    for clname in ['tuple2', 'dict']:
        #if not 'A' in defclass(clname).template_vars:
        #    defaultvar('A', defclass(clname), template_var=True)
        if not 'B' in defclass(clname).template_vars:
            defaultvar('B', defclass(clname), template_var=True)

    allfuncs = gx.allfuncs.copy() 
    allfuncs.update(gx.modules['builtin'].funcs.values())
 
    for func in allfuncs:
        #if func.mv.module.ident != 'builtin':
            formals = func.formals
            if func.defaults:
                formals = formals[:-len(func.defaults)]
            for formal in formals:
                if func.parent and formal == 'self': continue
                template_detect(func.vars[formal], func)

    # --- remove template variables until the C++ compiler exactly knows all types
    #     (uncertainty arises from passing truly polymorphic object into parameterized arguments)
    gx.changed = True
    while gx.changed:
        gx.changed = False

        for node in gx.merged_all:
            if isinstance(node, CallFunc):
                objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(node)
                if ident and ident.startswith('__'): continue # XXX

                targets = callfunc_targets(node, gx.merged_all) # XXX getting targets, pairs in sep func..
                for target in targets:
                    if isinstance(target.parent, class_) and target.parent.module.ident == 'builtin':
                        continue

                    pairs = connect_actual_formal(node, target)

                    for (lvalue, rvalue) in pairs:
                        if isinstance(lvalue, tuple) or isinstance(rvalue, tuple): 
                            continue
                        argsplit = typesplit(lvalue, inode(node).parent)
                        formalsplit = typesplit(rvalue, target)
                        template_disable_rec(argsplit, inode(node).parent, formalsplit, target)

        for parent in gx.allfuncs.union(gx.allclasses):
            new_dict = {}
            var_nr = 0
            if is_method(parent): 
                var_nr = len(parent.parent.template_vars)

            for tvar in parent.template_vars.values():
                if not tvar.template_disabled: 
                    tvar.name = string.ascii_uppercase[var_nr]
                    new_dict[tvar.name] = tvar
                    var_nr += 1

            parent.template_vars = new_dict
             
    # --- output generic classes/functions
    for cl in gx.allclasses: 
        if cl.template_vars and not cl.mv.module.builtin:
            print template_repr(cl)+'class '+cl.ident
    for func in gx.allfuncs:
        if func.template_vars and not func.mv.module.builtin:
            print template_repr(func)+func.ident 


def template_repr(parent):
    if not parent or not parent.template_vars:
        return ''

    return 'template <'+', '.join(['class '+n for n in parent.template_vars.keys()])+'> '

# --- detect template variables: recurse over type, creating template variables for each polymorphic variable
def template_detect(var, parent):
    split = typesplit(var, parent)
    #print 'split', var, split 

    if (var.name == 'unit' and var.parent.ident in ['list','tuple','set','frozenset','__iter', 'deque']) or (var.name in ['unit', 'value'] and var.parent.ident in ['dict', 'defaultdict']) or (var.name in ['first', 'second'] and var.parent.ident == 'tuple2'):
        if var.name == 'unit' and var.parent.ident == 'tuple': # XXX
            var.parent.unittvar = string.ascii_uppercase[len(parent.template_vars)]

        insert_template_var(split, parent)
    else:
        template_detect_rec(split, parent)

def polymorphic_cl(classes):
    cls = set([cl for cl in classes])
    if len(cls) > 1 and defclass('none') in cls and not defclass('int_') in cls and not defclass('float_') in cls:
        cls.remove(defclass('none'))
#    if defclass('float_') in cls and defclass('int_') in cls:
#        cls.remove(defclass('int_'))
    if defclass('tuple2') in cls and defclass('tuple') in cls: # XXX hmm
        cls.remove(defclass('tuple2'))
    return cls

def polymorphic_t(types):
    return polymorphic_cl([t[0] for t in types])

def template_detect_rec(split, parent):
    classes = polymorphic_cl(split_classes(split))
    lcp = lowest_common_parents(classes)

    for ts in split.values(): # confused type in single template
        if len(polymorphic_t(ts)) > 1:
            return

    if len(lcp) > 1:
        # --- create template var if no match with existing one
        if not template_match(split, parent):
            insert_template_var(split, parent)
        return

    elif len(classes) == 0:
        return

    cl = classes.pop()

    template_vars = cl.template_vars
    if lcp[0].ident in ['pyiter','pyseq', 'pyset']: # XXX
        if 'A' in cl.template_vars:
            template_vars = {'A':cl.template_vars['A']}

    for tvar in template_vars: 
        subsplit = split_subsplit(split, tvar)
        template_detect_rec(subsplit, parent)

def insert_template_var(split, parent):
#    print 'insert', parent, split
    
    var_nr = len(parent.template_vars)
    if is_method(parent): 
        var_nr += len(parent.parent.template_vars)

    name = string.ascii_uppercase[var_nr]
    new_tvar = defaultvar(name, parent, template_var=True)

    for (dcpa, cpa), types in split.items():
        newnode = cnode(new_tvar, dcpa, cpa)
        gx.types[newnode] = types


# --- disable template variables, if a truly polymorphic object reaches them
def template_disable_rec(argsplit, func, formalsplit, target):
    argclasses = polymorphic_cl(split_classes(argsplit))
    formalclasses = polymorphic_cl(split_classes(formalsplit))

    if len(formalclasses) > 1:
        lcp = lowest_common_parents(argclasses)
        if len(lcp) == 2 and defclass('int_') in lcp and defclass('float_') in lcp: # XXX
            return
        if len(lcp) > 1 and not template_match(argsplit, func) and template_match(formalsplit, target) and not template_match(formalsplit, target).template_disabled:
            gx.changed = True
            template_match(formalsplit, target).template_disabled = True
        return

    elif len(formalclasses) == 0:
        return
        
    cl = formalclasses.pop()

    for tvar in cl.template_vars: # XXX all polymorphic variables? 
        argsubsplit = split_subsplit(argsplit, tvar)
        formalsubsplit = split_subsplit(formalsplit, tvar)

        template_disable_rec(argsubsplit, func, formalsubsplit, target)


# --- recursively visit all variable types, to see if ints/floats flow together with each other or pointer types
def confused_vars():
    for var in gx.allvars:
        #print 'confvar', var
        parent = parent_func(var) # XXX not necessary?
        if isinstance(parent, static_class): continue # XXX

        split = typesplit(var, parent)
        confused_var_rec(split, parent, var)

def confused_var_rec(split, parent, var, dichotomy=False):
    if template_match(split, parent):
        return

    alltypes = set() # XXX merge somehow
    for (dcpa, cpa), types in split.items():
        alltypes.update(types)

    classes = polymorphic_t([t for t in alltypes if isinstance(t[0], class_)])
             
    if len(classes) > 1:
        intfloat = [t[0] for t in alltypes if t[0].ident in ['int_', 'float_']]
        if len(intfloat) == 2: # merge int/float interactions into floats
            return

        #print 'multismulti', classes, split, parent, var
        if parent and isinstance(parent,class_) and parent.ident == 'tuple2' and var.name == 'unit':
            return

        if parent and isinstance(parent,function) and parent.ident in ['min','max']: # XXX builtin
            return

        return

    elif len(classes) == 0:
        return

    cl = classes.pop()

    for tvar in cl.template_vars: # XXX all polymorphic variables? 
        subsplit = split_subsplit(split, tvar)
        confused_var_rec(subsplit, parent, var, dichotomy)


# --- assignment (incl. passing arguments, returning values) may require a cast 
def assign_needs_cast(arg, func, formal, target):
    argsplit = typesplit(arg, func)
    formalsplit = typesplit(formal, target)

    return assign_needs_cast_rec(argsplit, func, formalsplit, target)

def assign_needs_cast_rec(argsplit, func, formalsplit, target):
    argclasses = split_classes(argsplit)
    formalclasses = split_classes(formalsplit)
    #print 'splitclasses', argclasses, formalclasses

    if defclass('none') in argclasses: return False # XXX research later

    #if len(formalclasses) > 1 and len(argclasses) == 1:
    #    if not template_match(argsplit, func) and not template_match(formalsplit, target):
    #        return True
         
    if len(formalclasses) != 1:
        return False

    if not len(argclasses): # a = [[]]
        return True

    cl = formalclasses.pop()

    for tvar in cl.template_vars:
        argsubsplit = split_subsplit(argsplit, tvar)
        formalsubsplit = split_subsplit(formalsplit, tvar)

        if assign_needs_cast_rec(argsubsplit, func, formalsubsplit, target):
            return True

    return False

# --- number classes with low and high numbers, to enable constant-time subclass check
def number_classes():
    counter = 0
    for cl in gx.allclasses:
        if not cl.bases: 
            counter = number_class_rec(cl, counter+1)

def number_class_rec(cl, counter):
    cl.low = counter
    for child in cl.children:
        counter = number_class_rec(child, counter+1)
    cl.high = counter
    return counter

# --- iterative flow analysis: after each iteration, detect imprecisions, and split involved contours
def ifa():
    split = [] # [(set of creation nodes, new type number), ..]
    redundant = {} # {redundant contour: similar contour we will map it to}
    removals = [] # [removed contour, ..]

    classes = [defclass('list'), defclass('tuple'), defclass('tuple2'), defclass('dict'), defclass('set'),defclass('frozenset')]+[cl for cl in gx.allclasses if cl.ident not in ['str_','int_','float_','none','pyseq','pyset','class_','list','tuple','tuple2','dict','set','frozenset']]

    for cl in classes:
        cl.splits = {}

    #print '\n*** iteration ***'
    sys.stdout.write('*')
    sys.stdout.flush()

    for cl in classes:
        if gx.avoid_loops and cl.ident not in ['str_','int_','float_','none','pyiter','pyseq','class_','list','tuple','tuple2','dict','set', '__iter']:
            continue

        if split or redundant or removals:   
            return split, redundant, removals
            
        #print '---', cl.ident
        newdcpa = cl.dcpa 

        # --- determine instance variables XXX kill
        if cl.ident in ['list', 'tuple', 'frozenset', 'set','__iter']:
            names = ['unit']
        elif cl.ident == 'tuple2':
            names = ['first', 'second']
        elif cl.ident == 'dict':
            names = ['unit', 'value']
        else:
            names = [name for name in cl.vars if not name.startswith('__')]
        vars = [cl.vars[name] for name in names if name in cl.vars]

        #print 'vars', vars

        unused = cl.unused[:]

        # --- create table for previously deduced types: class set -> type nr; remove redundant types
        classes_nr = {}
        nr_classes = {}
        for dcpa in range(1, cl.dcpa):
            if dcpa in unused: continue

            attr_types = [] # XXX merge with ifa_merge_contours.. sep func?
            for var in vars:
                if (var,dcpa,0) in gx.cnode:
                    attr_types.append(merge_simple_types(gx.cnode[var,dcpa,0].types()))
                else:
                    attr_types.append(frozenset())
            attr_types = tuple(attr_types)

            #if cl.ident == 'node':
            #    print str(dcpa)+':', zip(vars, attr_types)
            nr_classes[dcpa] = attr_types
            classes_nr[attr_types] = dcpa

        #print 'unused', cl.unused
        if redundant or cl.splits: # investigate cl.splits.. suppose contour 3->5 and 1->5 splits.. 5->mother?
            #print 'skip class..', redundant, cl.splits
            continue

        # --- examine each contour:
        #     split contours on imprecisions; merge contours when reverse dataflow is unambiguous

        for dcpa in range(1, cl.dcpa):
            if dcpa in unused: continue
            #print 'examine pre', dcpa

            attr_types = nr_classes[dcpa]

            for (varnum, var) in enumerate(vars):
                if not (var, dcpa, 0) in gx.cnode: continue
                  
                #if cl.ident == 'node':
                #    print 'var', var

                # --- determine assignment sets for this contour
                node = gx.cnode[var, dcpa, 0]
                assignsets = {} # class set -> targets
                alltargets = set()

                for a in node.in_:
                    types = gx.types[a]
                    if types:
                        if a.thing in gx.assign_target: # XXX *args
                            target = gx.cnode[gx.assign_target[a.thing], a.dcpa, a.cpa]
                            #print 'target', a, target, types
                            alltargets.add(target)
                            assignsets.setdefault(merge_simple_types(types), []).append(target) 

                #print 'assignsets', (cl.ident, dcpa), assignsets
                #print 'examine contour', dcpa

                bah = set() # XXX coarse recursion check
                for ass in assignsets:
                    bah.update(ass)
                if cl.ident not in gx.builtins:
                    if not [c for c, _ in bah if c.ident not in (cl.ident, 'none')]:
                        #print 'buggert!'
                        continue

                #print 'assignsets', (cl.ident, dcpa), assignsets

                # --- determine backflow paths and creation points per assignment set
                paths = {}
                creation_points = {}
                for assign_set, targets in assignsets.items():
                    #print 'assignset', assign_set, targets
                    path = backflow_path(targets, (cl,dcpa))
                    #print 'path', path

                    paths[assign_set] = path
                    alloc = [n for n in path if not n.in_]
                    creation_points[assign_set] = alloc

                #print 'creation points', creation_points

                # --- collect all nodes
                allnodes = set()
                for path in paths.values(): 
                   allnodes.update(path)
                endpoints = [huh for huh in allnodes if not huh.in_] # XXX call csites
                #print 'endpoints', endpoints

                # --- split off empty assignment sets (eg, [], or [x[0]] where x is None in some template)
                if assignsets and cl.ident in ['list', 'tuple']: # XXX amaze, msp_ss
                    allcsites = set()
                    for n, types in gx.types.items():
                        if (cl, dcpa) in types and not n.in_:
                            allcsites.add(n)

                    empties = list(allcsites-set(endpoints))
                    #print 'EMPTIES', empties, assignsets

                    if empties:
                        split.append((cl, dcpa, empties, newdcpa))
                        cl.splits[newdcpa] = dcpa
                        newdcpa += 1
                        #return split, redundant, removals

                if len(merge_simple_types(gx.types[node])) < 2 or len(assignsets) == 1:
                    #print 'singleton set'
                    continue

                # --- per node, determine paths it is located on
                for n in allnodes: n.paths = []

                for assign_set, path in paths.items():
                    for n in path:
                        n.paths.append(assign_set)

                # --- for each node, determine creation points that 'flow' through it
                csites = []
                for n in allnodes: 
                    n.csites = set()
                    if not n.in_: # and (n.dcpa, n.cpa) != (0,0): # XXX
                        n.csites.add(n)
                        csites.append(n)
                flow_creation_sites(csites, allnodes)
            
                if len(csites) == 1:
                    #print 'just one creation site!'
                    continue
                
                # --- determine creation nodes that are only one one path
                noconf = set() 
                for node in csites: #allnodes:
                    #if not node.in_ and len(node.paths) == 1:
                    #print 'noconf', node, node.paths
                    if len(node.paths) == 1:
                        noconf.add(node)
                        #print 'no confusion about:', node, node.paths[0], node.parent

                # --- for these, see if we can reuse existing contours; otherwise, create new contours
                removed = 0
                nr_of_nodes = len(noconf)
                for node in noconf:
                    #assign_set = set()
                    #for path in node.paths:
                    #    assign_set.update(path)
                    #assign_set = frozenset(assign_set)
                    assign_set = node.paths[0]

                    new_attr_types = list(attr_types)
                    new_attr_types[varnum] = assign_set
                    #print 'new type', tuple(new_attr_types)
                    new_attr_types = tuple(new_attr_types)
                     
                    if new_attr_types in classes_nr and (not [len(types)==1 and list(types)[0][0].ident in ['float_','str_','int_'] for types in new_attr_types if types].count(False) or classes_nr[new_attr_types] >= cl.dcpa): # XXX last check.. useful or not?
                        nr = classes_nr[new_attr_types]
                        if nr != dcpa: # XXX better check: classes_nr for dcpa
                            #print 'reuse', node, nr
                            split.append((cl, dcpa, [node], nr))
                            cl.splits[nr] = dcpa
                            
                            removed += 1
                        #else: 
                        #    print 'doh!!'
                    else: 
                        #print 'new!', node, newdcpa

                        classes_nr[new_attr_types] = newdcpa

                        split.append((cl, dcpa, [node], newdcpa))
                        cl.splits[newdcpa] = dcpa
                        newdcpa += 1

                        nr_of_nodes -= 1
                        removed += 1

                # --- remove contour if it becomes empty 
                if removed == len([node for node in allnodes if not node.in_]):
                    #print 'remove contour', dcpa
                    cl.unused.append(dcpa)
                    removals.append((cl,dcpa))
                
                if split: # XXX
                    break
                #print 'check confluence'

                # --- object contour splitting

                #print 'hoep?', cl.ident

                for node in allnodes:
                    # --- determine if node is a confluence point

                    conf_point = False
                    if len(node.in_) > 1 and isinstance(node.thing, variable):
                        #print 'possible confluence', node, node.csites
                        for csite in node.csites:
                            occ = [csite in crpoints for crpoints in creation_points.values()].count(True)
                            if occ > 1:
                                conf_point = True
                                break
                    if not conf_point:
                        continue

                    if not node.thing.formal_arg and not isinstance(node.thing.parent, class_):
                        #print 'bad split', node
                        continue

                    # --- determine split along incoming dataflow edges

                    #print 'confluence point', node, node.paths #, node.in_

                    remaining = [incoming.csites.copy() for incoming in node.in_ if incoming in allnodes]
                    #print 'remaining before', remaining

                    # --- try to clean out larger collections, if subsets are in smaller ones

                    for (i, seti) in enumerate(remaining):
                        for setj in remaining[i+1:]:
                            in_both = seti.intersection(setj)
                            if in_both:
                                if len(seti) > len(setj):
                                    seti -= in_both
                                else:
                                    setj -= in_both

                    remaining = [setx for setx in remaining if setx]
                    #print 'remaining after', remaining
                    
                    if len(remaining) < 2:
                        #print "one rem"
                        continue

                    # --- if it exists, perform actual splitting
                    #print 'split rem', remaining
                    for splitsites in remaining[1:]:
                        #print 'splitsites', splitsites

                        split.append((cl, dcpa, splitsites, newdcpa))
                        cl.splits[newdcpa] = dcpa
                        newdcpa += 1

                    return split, redundant, removals 
                
                # --- if all else fails, perform wholesale splitting
                # XXX assign sets should be different; len(paths) > 1?

                #print 'wholesale!', cl.ident, dcpa, assignsets

                if len(paths) > 1 and len(csites) > 1:
                    #print 'no confluence..split all?'
                    #print paths.keys(), csites

                    for csite in csites[1:]:
                        #print 'splitsites', splitsites

                        split.append((cl, dcpa, [csite], newdcpa))
                        cl.splits[newdcpa] = dcpa
                        newdcpa += 1

                    return split, redundant, removals

    return split, redundant, removals

# --- cartesian product algorithm (cpa) & iterative flow analysis (ifa)
def iterative_dataflow_analysis():
    print '[iterative type analysis..]'

    removed = []

    # --- backup constraint network 
    backup = backup_network()

    while True:
        gx.iterations += 1
        # --- propagate using cartesian product algorithm

        gx.new_alloc_info = {}

        #print 'table'
        #print '\n'.join([repr(e)+': '+repr(l) for e,l in gx.alloc_info.items()])
        #print 'propagate'

        propagate()
        #printstate()

        gx.alloc_info = gx.new_alloc_info

        # --- ifa: detect conflicting assignments to instance variables, and split contours to resolve these
        split, redundant, removed = ifa()
        #if split: print 'splits', [(s[0], s[1], s[3]) for s in split]

        if not (split or redundant): # nothing has changed XXX 
            print '\niterations:', gx.iterations, 'templates:', gx.templates
            return

        # --- update alloc info table for split contours
        #print 'splits:', defclass('list').splits

        for cl, dcpa, nodes, newnr in split: 
            #print 'split', cl, dcpa, nodes, newnr

            for n in nodes:
                parent = parent_func(n.thing)
                if parent:
                    #print 'parent', n, parent, parent.cp
                    if n.dcpa in parent.cp: 
                        for cart, cpa in parent.cp[n.dcpa].items(): # XXX not very fast
                            if cpa == n.cpa:
                                if parent.parent and isinstance(parent.parent, class_): # self
                                    cart = ((parent.parent, n.dcpa),)+cart

                                gx.alloc_info[parent.ident, cart, n.thing] = (cl, newnr) 
                                break

        beforetypes = backup[0]

        # --- clean out constructor node types in functions, possibly to be seeded again
        for node in beforetypes:
            if isinstance(parent_func(node.thing), function):
                if node.constructor and isinstance(node.thing, (List,Dict,Tuple,ListComp,CallFunc)):
                    beforetypes[node] = set()

        # --- update constraint network and alloc info table for redundant contours
        if redundant:
            #print 'redundant', redundant

            for node, types in beforetypes.items():
                if not parent_func(node.thing):
                    newtypes = []
                    for t in types:
                        if t in redundant:
                            newtypes.append((t[0], redundant[t]))
                        else:
                            newtypes.append(t)
                    beforetypes[node] = set(newtypes)

            new_info = {}
            for (parent, cart, thing), x in gx.alloc_info.items():
                remove = False
                new_cart = []
                for t in cart: 
                    if t in redundant: 
                        new_cart.append((t[0], redundant[t]))
                    else:
                        new_cart.append(t)

                if x in redundant: 
                    x = (x[0], redundant[x])

                new_info[parent, tuple(new_cart), thing] = x
            gx.alloc_info = new_info

        # --- create new class types, and seed global nodes 
        for cl, dcpa, nodes, newnr in split: 
            if newnr == cl.dcpa:
                cl.copy(newnr)
                cl.dcpa += 1

            #print 'split off', nodes, newnr
            for n in nodes:
                if not parent_func(n.thing):
                    beforetypes[n] = set([(cl,newnr)])
                    #print 'seed global', n, (cl,newnr)

        # --- restore network 
        restore_network(backup)

# --- seed allocation sites in newly created templates (called by function.copy())
def ifa_seed_template(func, cart, dcpa, cpa, worklist):
    if cart != None: # (None means we are not in the process of propagation)
        #print 'funccopy', func.ident #, func.nodes

        if isinstance(func.parent, class_): # self
            cart = ((func.parent, dcpa),)+cart

        for node in func.nodes:
            if node.constructor and isinstance(node.thing, (List, Dict, Tuple, ListComp, CallFunc)): 
                #print 'constr', node

                # --- contour is specified in alloc_info
                parent = node.parent
                while isinstance(parent.parent, function): parent = parent.parent

                alloc_id = (parent.ident, cart, node.thing) # XXX ident?
                alloc_node = gx.cnode[node.thing, dcpa, cpa]

                if alloc_id in gx.alloc_info:
                    pass #    print 'specified', func.ident, cart, alloc_node, alloc_node.callfuncs, gx.alloc_info[alloc_id]

                # --- contour is newly split: copy allocation type for 'mother' contour; modify alloc_info
                else:
                    mother_alloc_id = alloc_id

                    for (id, c, thing) in gx.alloc_info:
                        if id ==  parent.ident and thing is node.thing:
                            okay = True
                            for a, b in zip(cart, c):
                                if a == b:
                                    pass #print 'eq', a, b
                                elif isinstance(a[0], class_) and a[0] is b[0] and a[1] in a[0].splits and a[0].splits[a[1]] == b[1]: 
                                    pass #print 'inh', a, b
                                else:
                                    okay = False
                                    break 
                            if okay:
                                mother_alloc_id = (id, c, thing)
                                break

                    #print 'not specified.. mother id:', mother_alloc_id

                    if mother_alloc_id in gx.alloc_info:
                        gx.alloc_info[alloc_id] = gx.alloc_info[mother_alloc_id]
                        #print 'mothered', alloc_node, gx.alloc_info[mother_alloc_id]
                    elif gx.types[node]: # empty constructors that do not flow to assignments have no type
                        #print 'no mother', func.ident, cart, mother_alloc_id, alloc_node, gx.types[node]
                        gx.alloc_info[alloc_id] = list(gx.types[node])[0]
                    else:
                        #print 'oh boy'
                        for (id, c, thing) in gx.alloc_info: # XXX vhy?
                            if id == parent.ident and thing is node.thing:
                                mother_alloc_id = (id, c, thing)
                                gx.alloc_info[alloc_id] = gx.alloc_info[mother_alloc_id]
                                break
                        #assert false

                    #if alloc_id in gx.alloc_info: # XXX faster
                    #    print 'seed', func.ident, cart, alloc_node, gx.alloc_info[alloc_id]

                if alloc_id in gx.alloc_info:
                    gx.new_alloc_info[alloc_id] = gx.alloc_info[alloc_id]

                    gx.types[alloc_node] = set()
                    #print 'seeding..', alloc_node, gx.alloc_info[alloc_id], alloc_node.thing in gx.empty_constructors
                    gx.types[alloc_node].add(gx.alloc_info[alloc_id])
                    addtoworklist(worklist, alloc_node)

                    if alloc_node.callfuncs: # XXX 
                        gx.checkcallfunc.append(alloc_node)

# --- for a set of target nodes of a specific type of assignment (e.g. int to (list,7)), flow back to creation points
def backflow_path(worklist, t):
    path = set(worklist)
    while worklist:
        new = []
        for node in worklist:
            for incoming in node.in_:
                if t in gx.types[incoming]:
                    incoming.fout.add(node)

                    if not incoming in path: 
                        path.add(incoming)
                        new.append(incoming)
        worklist = new
    return path

def flow_creation_sites(worklist, allnodes):
    while worklist:
        new = []
        for node in worklist:
            for out in node.fout:
                if out in allnodes:
                    difference = node.csites - out.csites

                    if difference:
                        out.csites.update(difference)
                        if not out in new:
                            new.append(out)
        worklist = new

# --- backup constraint network
def backup_network():
    beforetypes = {}
    for node, typeset in gx.types.items():
        beforetypes[node] = typeset.copy()

    beforeconstr = gx.constraints.copy()

    beforeinout = {}
    for node in gx.types:
        beforeinout[node] = (node.in_.copy(), node.out.copy()) 

    beforecnode = gx.cnode.copy()

    return (beforetypes, beforeconstr, beforeinout, beforecnode)

# --- restore constraint network, introducing new types
def restore_network(backup):
    beforetypes, beforeconstr, beforeinout, beforecnode = backup

    gx.types = {}
    for node, typeset in beforetypes.items():
        gx.types[node] = typeset.copy()

    gx.constraints = beforeconstr.copy()
    gx.cnode = beforecnode.copy()

    for node, typeset in gx.types.items():
        node.nodecp = set()
        node.defnodes = False
        befinout = beforeinout[node]
        node.in_, node.out = befinout[0].copy(), befinout[1].copy()
        node.fout = set() # XXX ?

    for var in gx.allvars: # XXX we have to restore some variable constraint nodes.. remove vars?
        if not (var, 0, 0) in gx.cnode:
            newnode = cnode(var, parent=var.parent)

    # --- clear templates 
    for func in gx.allfuncs:
        func.cp = {}

    for cl in gx.modules['builtin'].classes.values():
        for func in cl.funcs.values():
            func.cp = {}
    for func in gx.modules['builtin'].funcs.values():
        func.cp = {}

def merge_simple_types(types):
    merge = types.copy()
    if len(types) > 1 and (defclass('none'),0) in types:
        merge.remove((defclass('none'),0))

    return frozenset(merge)

def merge_simple_types2(types):
    merge = types.copy()
    if len(types) > 1 and (defclass('none'),0) in types:
        merge.remove((defclass('none'),0))

    return frozenset(merge)

def parent_func(thing):
    parent = inode(thing).parent
    while parent:
        if not isinstance(parent, function) or not parent.listcomp:
            return parent
        parent = parent.parent

    return None

# --- iterative filter application/propagation
def apply_filters(types, merge):
    # XXX x = 1, x = [] etc.
    # XXX y = x+1, self.a = x.meth(), expr.a = x.meth() -> retvals
    # XXX y = expr.meth().meth() -> retvals

    print 'ass', gx.assignments

    changed = 1
    while changed:
        changed = 0
        
        # --- initial filters, flow across function call
        for node in types: # XXX
            if node.thing in merge and not node.mv.module.builtin: 

                # --- var.a: limit builtins to have method named 'a'
                if isinstance(node.thing, Getattr) and isinstance(node.thing.expr, Name): # XXX out
                    if not inode(node.thing).fakert:
                        #print 'GETATTR', node.thing, inode(node.thing).fakert
                        var = lookupvar(node.thing.expr.name, node.parent)
                        filter = set([cl for cl in gx.allclasses if not cl.mv.module.builtin or node.thing.attrname in cl.funcs])
                        if filter_flow(filter, var):
                            changed = 1
                            print 'getattr filter', var, var.filter, node.thing

                # --- var.a(): limit classes to have method named 'a'
                if isinstance(node.thing, CallFunc):
                    if isinstance(node.thing.node, Getattr) and node.thing.node.attrname.startswith('__') and node.thing.node.attrname in ['__getattr__', '__setattr__', '__str__', '__repr__', '__getfirst__', '__getsecond__', '__hash__', '__cmp__', '__eq__', '__ne__', '__le__', '__lt__', '__ge__', '__gt__']: # XXX
                        continue

                    #print node.thing, merge[node.thing]
                    objexpr, ident, direct_call, method_call, constructor, mod_var, parent_constr = analyze_callfunc(node.thing)
                    # --- var.meth() -> setup filter for var (can only be of class that implements 'meth')
                    if method_call:
                        #print 'method call', objexpr, ident

                        # name.meth()
                        if isinstance(objexpr, Name): # XXX move out of iter loop?
                            var = lookupvar(objexpr.name, node.parent)
                            #print 'on var', var
                            filter = set([cl for cl in gx.allclasses if ident in cl.funcs])
                            #print 'filter', filter
                            if filter_flow(filter, var):
                                changed = 1
                                print 'var filter', var, var.filter, node.thing

                        # self.var.meth()
                        elif isinstance(objexpr, Getattr) and isinstance(objexpr.expr, Name) and objexpr.expr.name == 'self' and node.parent and node.parent.parent:
                            var = defaultvar(objexpr.attrname, node.parent.parent)
                            filter = set([cl for cl in gx.allclasses if ident in cl.funcs])
                            if filter_flow(filter, var):
                                changed = 1
                                print 'self.var filter', node.thing, var, filter

                    # --- propagate filters along backward variable flow
                    targets = callfunc_targets(node.thing, merge)

                    if method_call and isinstance(objexpr, Name): # minimize targets with _new_ filters
                        var = lookupvar(objexpr.name, node.parent) 
                        if var.filter:
                            #print 'filter targets', node.thing, targets, var.filter

                            if targets: targetcls = set([target.parent for target in targets]) & var.filter
                            else: targetcls = var.filter

                            newtargets = [cl.funcs[ident] for cl in targetcls]
                            #if not targets or len(newtargets) < len(targets):
                            #    print 'filtered targets', node.thing, newtargets
                            targets = newtargets

                    if not [t for t in targets if t.mv.module.builtin]:
                        filters = [[] for i in range(len(node.thing.args))] 
                        # --- determine filters per 'variable' argument per target
                        for target in targets:
                            #print 'target:', target
                            pairs = connect_actual_formal(node.thing, target)
                            for ((a,b), f) in zip(pairs, filters):
                                if isinstance(a, Name): # XXX expr.a
                                    var, filter = lookupvar(a.name, node.parent), b.filter
                                    f.append(b.filter)

                        # --- OR filters per 'variable' argument and propagate
                        for arg, filter in zip(node.thing.args, filters):
                            if isinstance(arg, Name): # XXX expr.a
                                if filter and not [f for f in filter if not f]:
                                    orfilter = reduce(lambda x,y: x|y, filter)
                                    var = lookupvar(arg.name, node.parent)
                                    #print 'or filter:', var, orfilter
                                    if filter_flow(orfilter, var):
                                        changed = 1
                                        print 'prop filter', var, var.filter, node.thing

        # --- variable assignment flow
        for lvar, rvar in gx.assignments:
            if isinstance(lvar, variable) and filter_flow(lvar.filter, rvar):
                changed = 1
                print 'flow filter', lvar, rvar

def filter_flow(filter, var):
    if not filter:
        return 0
    elif not var.filter: 
        var.filter = filter
        return 1
    elif len(var.filter & filter) < len(var.filter): 
        var.filter &= filter
        return 1
    return 0

def parsefile(name):
    try:
        return parseFile(name)
    except SyntaxError, s:
        print '*ERROR* %s:%d: %s' % (name, s.lineno, s.msg)
        sys.exit()

def analysis(source, testing=False):
    global mv, gx

    if testing: 
        gx = globalInfo()
        ast = parse(source+'\n')
    else:
        ast = parsefile(source)
    mv = None

    # --- build dataflow graph from source code
    gx.main_module = module(gx.main_mod, ast)
    gx.main_module.filename = gx.main_mod+'.py'
    gx.modules[gx.main_mod] = gx.main_module
    mv = gx.main_module.mv

    # --- seed class_.__name__ attributes..
    for cl in gx.allclasses:
        if cl.ident == 'class_':
            var = defaultvar('__name__', cl)
            gx.types[inode(var)] = set([(defclass('str_'), 0)])

    # --- number classes (-> constant-time subclass check)
    number_classes()

    # --- non-ifa: copy classes for each allocation site
    for cl in gx.allclasses:
        if cl.ident in ['int_','float_','none', 'class_','str_']: continue

        if cl.ident == 'list':
            cl.dcpa = len(gx.list_types)+2
        elif cl.ident == '__iter': # XXX huh
            pass
        else:
            cl.dcpa = 2

        for dcpa in range(1, cl.dcpa): 
            cl.copy(dcpa)

    var = defaultvar('unit', defclass('str_'))
    gx.types[inode(var)] = set([(defclass('str_'), 0)])

    #printstate()
    #printconstraints()

    # --- filters
    #merge = merged(gx.types)
    #apply_filters(gx.types.copy(), merge)
   
    # --- cartesian product algorithm & iterative flow analysis
    iterative_dataflow_analysis()
    #propagate()

    #merge = merged(gx.types)
    #apply_filters(gx.types, merge)

    for cl in gx.allclasses:
        for name in cl.vars:
            if name in cl.parent.vars and not name.startswith('__'):
                error("instance variable '%s' of class '%s' shadows class variable" % (name, cl.ident))

    gx.merged_all = merged(gx.types) #, inheritance=True)
    gx.merge_dcpa = merged(gx.types, dcpa=True)

    mv = gx.main_module.mv
    propagate() # XXX remove 

    gx.merged_all = merged(gx.types) #, inheritance=True)
    gx.merged_inh = merged(gx.types, inheritance=True)

    # --- determine template parameters
    template_parameters()

    # --- detect inheritance stuff
    upgrade_variables()
    gx.merged_all = merged(gx.types)

    gx.merged_inh = merged(gx.types, inheritance=True)

    analyze_virtuals()

    # --- determine integer/float types that cannot be unboxed
    confused_vars()
    # --- check other sources of confusion
    confusion_misc() 

    gx.merge_dcpa = merged(gx.types, dcpa=True)
    gx.merged_all = merged(gx.types) #, inheritance=True) # XXX

    # --- determine which classes need an __init__ method
    for node, types in gx.merged_all.items():
        if isinstance(node, CallFunc):
            objexpr, ident, _ , method_call, _, _, _ = analyze_callfunc(node)
            if method_call and ident == '__init__':
                for t in gx.merged_all[objexpr]:
                    t[0].has_init = True

    # --- determine which classes need copy, deepcopy methods
    if 'copy' in gx.modules:
        func = gx.modules['copy'].funcs['copy']
        var = func.vars[func.formals[0]]
        for cl in set([t[0] for t in gx.merged_inh[var]]):
            cl.has_copy = True # XXX transitive, modeling

        func = gx.modules['copy'].funcs['deepcopy']
        var = func.vars[func.formals[0]]
        for cl in set([t[0] for t in gx.merged_inh[var]]):
            cl.has_deepcopy = True # XXX transitive, modeling

    # --- add inheritance relationships for non-original Nodes (and tempvars?); XXX register more, right solution?
    for func in gx.allfuncs:
        #if not func.mv.module.builtin and func.ident == '__init__':
        if func in gx.inheritance_relations: 
            #print 'inherited from', func, gx.inheritance_relations[func]
            for inhfunc in gx.inheritance_relations[func]:
                for a, b in zip(func.registered, inhfunc.registered):
                    #print a, '->', b 
                    inherit_rec(a, b)

    # --- finally, generate C++ code and Makefiles.. :-)

    #printstate()
    #printconstraints()
    generate_code()
    #generate_bindings()

    #print 'cnode!'
    #for (a,b) in gx.cnode.items():
    #    print a, b
   # for (a,b) in gx.types.items():
   #     print a, b

    # error for dynamic expression (XXX before codegen)
    for node in gx.merged_all:
        if isinstance(node, Node) and not isinstance(node, AssAttr) and not inode(node).mv.module.builtin:
            typesetreprnew(node, inode(node).parent) 

    return gx

# --- generate C++ and Makefiles
def generate_code():
    global mv
    print '[generating c++ code..]'

    gx.dirs.setdefault('',[]).append(gx.main_module)

    ident = gx.main_module.ident 

    if sys.platform == 'win32':
        pyver = '%d%d' % sys.version_info[:2]
    else:
        includes = os.popen4('python-config --includes')[1].read().strip()
        ldflags = os.popen4('python-config --ldflags')[1].read().strip()

    if gx.extension_module: 
        if sys.platform == 'win32': ident += '.pyd'
        else: ident += '.so'

    # --- repeat for each directory:
    for dir, mods in gx.dirs.items():
        # --- generate C++ files
        for module in mods:
            if not module.builtin:
                gv = generateVisitor(module)
                mv = module.mv 
                gv.func_pointers(False)
                walk(module.ast, gv)
                gv.out.close()
                gv.header_file()
                gv.out.close()
                gv.insert_consts(declare=False)
                gv.insert_consts(declare=True)

        # --- generate Makefile
        makefile = file(connect_paths(dir, 'Makefile'), 'w')

        cppfiles = ' '.join([m.filename[:-3].replace(' ', '\ ')+'.cpp' for m in mods])
        hppfiles = ' '.join([m.filename[:-3].replace(' ', '\ ')+'.hpp' for m in mods])

        # import flags
        if gx.flags: flags = gx.flags
        elif os.path.isfile('FLAGS'): flags = 'FLAGS'
        else: flags = connect_paths(gx.sysdir, 'FLAGS')

        for line in file(flags):
            line = line[:-1]

            if line[:line.find('=')].strip() == 'CCFLAGS': 
                line += ' -I'+gx.libdir.replace(' ', '\ ')
                if not gx.wrap_around_check: line += ' -DNOWRAP' 
                if gx.bounds_checking: line += ' -DBOUNDS' 
                if gx.extension_module: 
                    if sys.platform == 'win32': line += ' -Ic:/Python%s/include -D__SS_BIND' % pyver
                    else: line += ' -g -fPIC -D__SS_BIND ' + includes

            elif line[:line.find('=')].strip() == 'LFLAGS': 
                if gx.extension_module: 
                    if sys.platform == 'win32': line += ' -shared -Lc:/Python%s/libs -lpython%s' % (pyver, pyver) 
                    elif sys.platform == 'darwin': line += ' -bundle -Xlinker -dynamic ' + ldflags
                    else: line += ' -shared -Xlinker -export-dynamic ' + ldflags
                if 're' in [m.ident for m in mods]:
                    line += ' -lpcre'

            print >>makefile, line
        print >>makefile

        print >>makefile, 'all:\t'+ident+'\n'

        if not gx.extension_module:
            print >>makefile, 'run:\tall'
            print >>makefile, '\t./'+ident+'\n'

            print >>makefile, 'full:'
            print >>makefile, '\tss '+ident+'; $(MAKE) run\n'

        print >>makefile, 'CPPFILES='+cppfiles
        print >>makefile, 'HPPFILES='+hppfiles+'\n'

        print >>makefile, ident+':\t$(CPPFILES) $(HPPFILES)'
        print >>makefile, '\t$(CC) $(CCFLAGS) $(CPPFILES) $(LFLAGS) -o '+ident+'\n'

        if sys.platform == 'win32':
            ident += '.exe'
        print >>makefile, 'clean:'
        print >>makefile, '\trm '+ident

        makefile.close()

def generate_bindings():
    for dir, mods in gx.dirs.items():
        for mod in mods:
            if mod.builtin and not os.path.isfile(mod.ident+'_.hpp'):
                ident = mod.ident
                print 'generate!', ident

                gv = generateVisitor(mod)
                mv = mod.mv 

                # --- generate *_.cpp file
                gv.output('#include <Python.h>\n#include "%s_.hpp"\n\nnamespace __%s__ {\n' % (ident, ident)) 
                gv.output('PyObject '+', '.join(['*__'+x for x in mod.funcs.keys()+mod.classes.keys()])+';\n')

                # class bindings
                for cl in mod.classes.values():
                    gv.visitm('/**', 'class %s' % cl.ident, '*/', None)
                    for func in cl.funcs.values():
                        if func.ident not in ['__getattr__', '__setattr__']:
                            bind_function(gv, func)

                # function bindings
                for func in mod.funcs.values():
                    bind_function(gv, func)

                # __init
                gv.output('void __init() {\n    '+'\n    '.join(['__%s = __import("%s", "%s");' % (x, ident, x) for x in mod.funcs.keys()+mod.classes.keys()])+'\n\n}\n')

                gv.output('} // namespace __%s__' % ident)
                gv.out.close()

                gv.out = file(mod.filename[:-3]+'.hpp','w')

                # --- generate *_.hpp file
                gv.output('#ifndef __%s_HPP\n#define __%s_HPP\n\n#include "builtin_.hpp"\n\nusing namespace __shedskin__;\n\nnamespace __%s__ {\n' % (ident.upper(), ident.upper(), ident))

                # class declarations 
                for cl in mod.classes.values():
                    gv.output('class %s : public pyobj {\npublic:' % cl.ident)
                    gv.indent()
                    gv.output('PyObject *self;\n')
                    for func in cl.funcs.values():
                        if func.ident not in ['__getattr__', '__setattr__']:
                            gv.func_header(func, declare=True)
                        
                    gv.deindent()
                    gv.output('\n};\n')

                # function declarations
                for func in mod.funcs.values():
                    gv.func_header(func, declare=True)

                gv.output('\nvoid __init();\n\n} // namespace __%s__\n#endif' % ident)
                gv.out.close()

def bind_function(gv, func):
    gv.func_header(func, declare=False)
    gv.indent()

    formals = func.formals
    if func.parent: formals = [f for f in formals if f != 'self'] 
    args = str(len(formals))
    if formals:
        args += ', '+', '.join(['__to_py(%s)' % f for f in formals])

    # constructor call
    if func.parent and func.ident == '__init__':
        gv.output('self = __call(__%s, __args(%s));\n' % (func.parent.ident, args))

    # method/function call
    else:
        if func.parent:
            gv.output('PyObject *__0 = __call(self, "%s", __args(%s));\n' % (func.ident, args))
        else:
            gv.output('PyObject *__0 = __call(__%s, __args(%s));\n' % (func.ident, args))

        if not func.fakeret:
            gv.output('return __to_ss<%s>(__0);' % typesetreprnew(func.retnode.thing, func).strip())
        else:
            gv.output('return 0;')

    gv.deindent()
    gv.output('}\n')

def get_includes(mod):
    imports = set()
    for mod in mod.mv.imports.values():
        if mod.filename.endswith('__init__.py'): # XXX
            imports.add('/'.join(mod.mod_path+[mod.ident])+'/__init__.hpp')
        else:
            imports.add('/'.join(mod.mod_path+[mod.ident])+'.hpp')
    return imports

def usage():
    print """Usage: ss.py [OPTION]... FILE

 -b --bounds            Enable bounds checking
 -e --extmod            Generate extension module
 -f --flags             Provide alternative Makefile flags
 -n --nowrap            Disable wrap-around checking 
 -i --infinite          Try to avoid infinite analysis time 
"""
    sys.exit()

def main():
    global gx
    gx = globalInfo()

    print '*** SHED SKIN Python-to-C++ Compiler 0.0.26 ***'
    print 'Copyright 2005-2008 Mark Dufour; License GNU GPL version 3 (See LICENSE)'
    print '(Please send bug reports here: mark.dufour@gmail.com)'
    print

    # --- parse command-line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'eibnf:', ['infinite', 'extmod', 'bounds', 'nowrap', 'flags='])
    except getopt.GetoptError:
        usage()
    
    for o, a in opts:
        if o in ['-h', '--help']: usage()
        if o in ['-b', '--bounds']: gx.bounds_checking = True
        if o in ['-e', '--extmod']: gx.extension_module = True
        if o in ['-i', '--infinite']: gx.avoid_loops = True
        if o in ['-f', '--flags']: 
            if not os.path.isfile(a): 
                print "*ERROR* no such file: '%s'" % a
                sys.exit()
            gx.flags = a
        if o in ['-n', '--nowrap']: gx.wrap_around_check = False

    # --- argument
    if len(args) != 1:
        usage()
    name = args[0]
    if not name.endswith('.py'):
        name += '.py'
    gx.main_mod = name[:-3]
        
    # --- analyze & annotate
    analysis(name)
    annotate()

if __name__ == '__main__':
    main()
