from compiler import *
from compiler.ast import *
from compiler.visitor import *

import os

# --- global variables gx, mv

class globalInfo: # XXX add comments, split up
    def __init__(self):
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

def newgx():
    return globalInfo()

def getgx():
    return _gx

def setgx(gx):
    global _gx
    _gx = gx
    return _gx

def getmv():
    return _mv

def setmv(mv):
    global _mv
    _mv = mv
    return _mv

# --- python variable, function, class, module..

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
        self.mv = getmv()
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

        if node and getmv().module.ident != 'builtin':
            getgx().allfuncs.add(self)

        self.parent_constr = None
        self.retvars = []
        self.invisible = False
        self.fakeret = None
        self.declared = False

        self.registered = []


    def __repr__(self):
        if self.parent: return 'function '+repr((self.parent, self.ident))
        return 'function '+self.ident

class class_:
    def __init__(self, node):
        self.node = node
        self.ident = node.name
        self.bases = []
        self.children = []
        self.dcpa = 1
        self.mv = getmv()
        self.vars = {}
        self.funcs = {}
        self.virtuals = {}              # 'virtually' called methods 
        self.virtualvars = {}           # 'virtual' variables
        self.template_vars = {}
        self.properties = {}
        self.staticmethods = []

        self.typenr = getgx().nrcltypes
        getgx().nrcltypes += 1
        getgx().typeclass[self.typenr] = self

        # data adaptive analysis
        self.nrcart = {}                # nr: cart
        self.cartnr = {}                # cart: nr
        self.splits = {}                # contour: old contour (used between iterations)
        self.unused = []                # unused contours

        self.has_init = self.has_copy = self.has_deepcopy = False

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

class static_class: # XXX merge with regular class
    def __init__(self, cl):
        self.vars = {}
        self.funcs = {}
        self.class_ = cl
        cl.static_class = self
        self.ident = cl.ident
        self.bases = []
        self.parent = None
        self.mv = getmv()
        self.module = cl.module

    def __repr__(self):
        return 'static class '+self.class_.ident

class module:
    def __init__(self, ident, node):
        self.ident = ident
        self.node = node

    def __repr__(self):
        return 'module '+self.ident 

# --- constraint graph node

class cnode:
    def __init__(self, thing, dcpa=0, cpa=0, parent=None):
        self.thing = thing
        self.dcpa = dcpa
        self.cpa = cpa
        self.fakenodes = []
        self.fakefunc = None
        self.parent = parent
        self.defnodes = False # if callnode, notification nodes were made for default arguments
        self.mv = getmv()
        self.constructor = False # allocation site 
        self.copymetoo = False
        self.filters = [] # run-time type filters such as isinstance()
        #self.parent_callfunc = None
        self.fakert = False
     
        if isinstance(self.thing, CallFunc) and isinstance(self.thing.node, Name) and self.thing.node.name == 'set': 
            if (self.thing, self.dcpa, self.cpa) in getgx().cnode:
                print 'killing something!', self
                traceback.print_stack() 

        getgx().cnode[self.thing, self.dcpa, self.cpa] = self

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

    def copy(self, dcpa, cpa, worklist=None): # XXX to infer.py
        #if not self.mv.module.builtin: print 'copy', self

        if (self.thing, dcpa, cpa) in getgx().cnode:
            return getgx().cnode[self.thing, dcpa, cpa]

        newnode = cnode(self.thing, dcpa, cpa)

        newnode.callfuncs = self.callfuncs[:] # XXX no copy?
        newnode.constructor = self.constructor
        newnode.copymetoo = self.copymetoo
        newnode.parent = self.parent
        newnode.mv = self.mv

        addtoworklist(worklist, newnode)

        if self.constructor or self.copymetoo or isinstance(self.thing, (Not, Compare)): # XXX XXX
            getgx().types[newnode] = getgx().types[self].copy()
        else:
            getgx().types[newnode] = set()
        return newnode

    def types(self):
        return getgx().types[self]

    def __repr__(self):
        return repr((self.thing, self.dcpa, self.cpa))

def addtoworklist(worklist, node): # XXX to infer.py
    if worklist != None and not node.in_list:
        worklist.append(node)
        node.in_list = 1

# --- shortcuts

def inode(node):
    return getgx().cnode[node,0,0]

def connect_paths(a, b, conn='/'):
    if a == '':
        return b
    return a+conn+b

def relative_path(a, b):
    c = b[len(a):]
    if c.startswith('/'): c = c[1:]
    return c

def is_method(parent):
    return isinstance(parent, function) and isinstance(parent.parent, class_)

def is_listcomp(parent):
    return isinstance(parent, function) and parent.listcomp

def fastfor(node):
    return isinstance(node.list, CallFunc) and isinstance(node.list.node, Name) and node.list.node.name in ['range', 'xrange']

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
        if name in getmv().globals:
            return getmv().globals[name]
        dest = getmv().globals

    if not local:
        return None

    var = variable(name, parent)
    if template_var:
        var.template_variable = True
    else:
        getgx().allvars.add(var)

    dest[name] = var
    newnode = cnode(var, parent=parent) 
    if parent:
        newnode.mv = parent.mv
    addtoworklist(worklist, newnode)
    getgx().types[newnode] = set()

    return var
