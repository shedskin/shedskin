'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2009 Mark Dufour; License GNU GPL version 3 (See LICENSE)

shared.py: global variables, datastructures, shared functionality

'''

import os, sys, traceback
from compiler import *
from compiler.ast import *
from compiler.visitor import *

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
        self.inheritance_tempvars = {}
        self.parent_nodes = {}
        self.inherited = set()
        self.nrcltypes = 8;
        self.empty_constructors = set()
        self.sig_nr = {}
        self.nameclasses = {}
        self.tuple2 = set()             # binary typed tuples
        self.module = None
        self.builtins = ['none', 'str_', 'float_', 'int_', 'class_', 'list', 'tuple', 'tuple2', 'dict', 'set', 'frozenset', 'bool_']
        self.assign_target = {}              # instance node for instance variable assignment
        self.alloc_info = {}                 # allocation site type information across iterations
        self.iterations = 0
        self.lambdawrapper = {}
        self.sysdir = '/'.join(__file__.split(os.sep)[:-1])
        self.libdir = connect_paths(self.sysdir, 'lib')
        self.main_mod = 'test'
        self.cpp_keywords = set(['asm', 'auto', 'bool', 'case', 'catch', 'char', 'const', 'const_cast', 'default', 'delete', 'do', 'double', 'dynamic_cast', 'enum', 'explicit', 'export', 'extern', 'false', 'float', 'friend', 'goto', 'inline', 'int', 'long', 'mutable', 'namespace', 'new', 'operator', 'private', 'protected', 'public', 'register', 'reinterpret_cast', 'short', 'signed', 'register', 'sizeof', 'static', 'static_cast', 'struct', 'switch', 'template', 'this', 'throw', 'true', 'typedef', 'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', 'void', 'volatile', 'wchar_t'])
        self.cpp_keywords.update(['stdin', 'stdout', 'stderr', 'std', 'abstract', 'st_mtime', 'st_atime', 'st_ctime', 'errno', 'fileno', 'environ', 'rand', 'optind', 'opterr', 'optopt', 'optarg', 'exit'])
        self.cpp_keywords.update(['ST_ATIME', 'ST_CTIME', 'ST_DEV', 'ST_GID', 'ST_INO', 'ST_MODE', 'ST_MTIME', 'ST_NLINK', 'ST_SIZE', 'ST_UID', 'S_ENFMT', 'S_IEXEC', 'S_IFBLK', 'S_IFCHR', 'S_IFDIR', 'S_IFIFO', 'S_IFLNK', 'S_IFREG', 'S_IFSOCK', 'S_IREAD', 'S_IRGRP', 'S_IROTH', 'S_IRUSR', 'S_IRWXG', 'S_IRWXO', 'S_IRWXU', 'S_ISGID', 'S_ISUID', 'S_ISVTX', 'S_IWGRP', 'S_IWOTH', 'S_IWRITE', 'S_IWUSR', 'S_IXGRP', 'S_IXOTH', 'S_IXUSR', 'S_IMODE', 'S_IFMT', 'S_ISDIR', 'S_ISCHR', 'S_ISBLK', 'S_ISREG', 'S_ISFIFO', 'S_ISLNK', 'S_ISSOCK'])
        self.cpp_keywords.update(['F_OK', 'R_OK', 'W_OK', 'X_OK', 'NGROUPS_MAX', 'TMP_MAX', 'WCONTINUED', 'WNOHANG', 'WUNTRACED', 'O_RDONLY', 'O_WRONLY', 'O_RDWR', 'O_NDELAY', 'O_NONBLOCK', 'O_APPEND', 'O_DSYNC', 'O_RSYNC', 'O_SYNC', 'O_NOCTTY', 'O_CREAT', 'O_EXCL', 'O_TRUNC', 'O_BINARY', 'O_TEXT', 'O_LARGEFILE', 'O_SHLOCK', 'O_EXLOCK', 'O_NOINHERIT', '_O_SHORT_LIVED', 'O_TEMPORARY', 'O_RANDOM', 'O_SEQUENTIAL', 'O_ASYNC', 'O_DIRECT', 'O_DIRECTORY', 'O_NOFOLLOW', 'O_NOATIME', 'EX_OK', 'EX_USAGE', 'EX_DATAERR', 'EX_NOINPUT', 'EX_NOUSER', 'EX_NOHOST', 'EX_UNAVAILABLE', 'EX_SOFTWARE', 'EX_OSERR', 'EX_OSFILE', 'EX_CANTCREAT', 'EX_IOERR', 'EX_TEMPFAIL', 'EX_PROTOCOL', 'EX_NOPERM', 'EX_CONFIG', 'EX_NOTFOUND', 'P_WAIT', 'P_NOWAIT', 'P_OVERLAY', 'P_NOWAITO', 'P_DETACH', 'SEEK_CUR', 'SEEK_SET', 'SEEK_END'])
        self.cpp_keywords.update(['SIGABRT', 'SIGALRM', 'SIGBUS', 'SIGCHLD', 'SIGCLD', 'SIGCONT', 'SIGFPE', 'SIGHUP', 'SIGILL', 'SIGINT', 'SIGIO', 'SIGIOT', 'SIGKILL', 'SIGPIPE', 'SIGPOLL', 'SIGPROF', 'SIGPWR', 'SIGQUIT', 'SIGRTMAX', 'SIGRTMIN', 'SIGSEGV', 'SIGSTOP', 'SIGSYS', 'SIGTERM', 'SIGTRAP', 'SIGTSTP', 'SIGTTIN', 'SIGTTOU', 'SIGURG', 'SIGUSR1', 'SIGUSR2', 'SIGVTALRM', 'SIGWINCH', 'SIGXCPU', 'SIGXFSZ', 'SIG_DFL', 'SIG_IGN'])
        self.cpp_keywords.update(['AF_INET', 'AF_INET6', 'AI_PASSIVE', 'AF_UNIX', 'SOCK_STREAM', 'SOCK_DGRAM', 'SOL_IP', 'SOL_SOCKET', 'IP_TOS', 'IP_TTL', 'SHUT_RD', 'SHUT_WR', 'SHUT_RDWR', 'INADDR_ANY', 'INADDR_LOOPBACK', 'INADDR_NONE', 'INADDR_BROADCAST', 'SO_REUSEADDR', 'SOMAXCONN', 'htonl', 'htons', 'ntohl', 'ntohs'])
        self.cpp_keywords.update(['makedev', 'major', 'minor'])
        self.cpp_keywords.update(['main'])
        self.cpp_keywords.update(['sun'])
        self.cpp_keywords.update(['WITH', 'WITH_VAR', 'END_WITH', 'FOR_IN', 'FOR_IN_SEQ', 'FOR_IN_T2', 'FOR_IN_ZIP', 'FAST_FOR', 'FAST_FOR_NEG', 'END_FOR'])
        self.ss_prefix = '__ss_'
        self.list_types = {}
        self.loopstack = [] # track nested loops
        self.comments = {}
        self.import_order = 0 # module import order
        # command-line options
        self.wrap_around_check = True
        self.bounds_checking = True
        self.fast_random = False
        self.extension_module = False
        self.longlong = False
        self.flags = None
        self.annotation = False
        self.output_dir= ''
        self.makefile_name = 'Makefile' # XXX other default?
        self.item_rvalue = {}
        self.genexp_to_lc = {}
        self.bool_test_only = set()

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
        self.imported = False
        self.initexpr = None
        self.registered = False
        self.looper = None

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
        self.lambdanr = None
        self.lambdawrapper = False
        self.parent = parent
        self.constraints = set()
        self.vars = {}
        self.globals = []
        self.mv = getmv()
        self.lnodes = []
        self.nodes = set()
        self.defaults = []
        self.misses = set()
        self.cp = {}
        self.xargs = {}
        self.largs = None
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
        self.registered_tempvars = []

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
        self.properties = {}
        self.staticmethods = []
        self.typenr = getgx().nrcltypes
        getgx().nrcltypes += 1
        self.splits = {}                # contour: old contour (used between iterations)
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

    def tvar_names(self):
        if self.mv.module.builtin:
            if self.ident in ['list', 'tuple', 'frozenset', 'set', 'frozenset', 'deque', '__iter', 'pyseq', 'pyiter', 'pyset']:
                return ['unit']
            elif self.ident in ['dict', 'defaultdict']:
                return ['unit', 'value']
            elif self.ident == 'tuple2':
                return ['first', 'second']

    def __repr__(self):
        return 'class '+self.ident

class static_class: # XXX merge with regular class
    def __init__(self, cl):
        self.vars = {}
        self.varorder = [] # XXX
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
        self.prop_includes = set()
        self.import_order = 0

    def __repr__(self):
        return 'module '+self.ident

# --- constraint graph node

class cnode:
    __slots__ = ['thing', 'dcpa', 'cpa', 'fakefunc', 'parent', 'defnodes', 'mv', 'constructor', 'copymetoo', 'fakert', 'in_', 'out', 'fout', 'in_list', 'callfuncs', 'nodecp', 'changed']

    def __init__(self, thing, dcpa=0, cpa=0, parent=None):
        self.thing = thing
        self.dcpa = dcpa
        self.cpa = cpa
        self.fakefunc = None
        if isinstance(parent, class_): # XXX
            parent = None
        self.parent = parent
        self.defnodes = False # if callnode, notification nodes were made for default arguments
        self.mv = getmv()
        self.constructor = False # allocation site
        self.copymetoo = False
        self.fakert = False
        self.lambdawrapper = None

        getgx().cnode[self.thing, self.dcpa, self.cpa] = self

        # --- in, outgoing constraints

        self.in_ = set()        # incoming nodes
        self.out = set()        # outgoing nodes
        self.fout = set()       # unreal outgoing edges, used in ifa

        # --- iterative dataflow analysis

        self.in_list = 0        # node in work-list
        self.callfuncs = []    # callfuncs to which node is object/argument

        self.nodecp = set()        # already analyzed cp's # XXX kill!?
        self.changed = 0

        # --- add node to surrounding non-listcomp function
        if parent: # do this only once! (not when copying)
            while parent and isinstance(parent, function) and parent.listcomp: parent = parent.parent
            if isinstance(parent, function):
                if self not in parent.nodes:
                    parent.nodes.add(self)

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
            newnode.changed = 1
        else:
            getgx().types[newnode] = set()
        return newnode

    def types(self):
        if self in getgx().types:
            return getgx().types[self]
        else:
            return set() # XXX

    def __repr__(self):
        return repr((self.thing, self.dcpa, self.cpa))

def addtoworklist(worklist, node): # XXX to infer.py
    if worklist != None and not node.in_list:
        worklist.append(node)
        node.in_list = 1

def in_out(a, b):
    a.out.add(b)
    b.in_.add(a)

def addconstraint(a, b, worklist=None):
    getgx().constraints.add((a,b))
    in_out(a, b)
    addtoworklist(worklist, a)

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

def is_enum(node):
    return isinstance(node.list, CallFunc) and isinstance(node.list.node, Name) and node.list.node.name == 'enumerate' and len(node.list.args) == 1 and isinstance(node.assign, (AssList, AssTuple))

def is_zip2(node):
    return isinstance(node.list, CallFunc) and isinstance(node.list.node, Name) and node.list.node.name == 'zip' and len(node.list.args) == 2 and isinstance(node.assign, (AssList, AssTuple))

def lookupvar(name, parent):
    return defvar(name, parent, False)

def defaultvar(name, parent, worklist=None):
    var = defvar(name, parent, True, worklist)

    if isinstance(parent, function) and parent.listcomp and not var.registered:
        while isinstance(parent, function) and parent.listcomp: # XXX
            parent = parent.parent
        if isinstance(parent, function):
            register_tempvar(var, parent)

    return var

def defvar(name, parent, local, worklist=None):
    if isinstance(parent, class_) and name in parent.parent.vars: # XXX
        return parent.parent.vars[name]
    if parent and name in parent.vars:
        return parent.vars[name]
    if parent and local:
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
    getgx().allvars.add(var)

    dest[name] = var
    newnode = cnode(var, parent=parent)
    if parent:
        newnode.mv = parent.mv
    addtoworklist(worklist, newnode)
    getgx().types[newnode] = set()

    return var

def defclass(name):
    if name in getmv().classes: return getmv().classes[name]
    else: return getmv().ext_classes[name]

def deffunc(name):
    if name in getmv().funcs: return getmv().funcs[name]
    else: return getmv().ext_funcs[name]

class fakeGetattr(Getattr): pass # XXX ugly
class fakeGetattr2(Getattr): pass
class fakeGetattr3(Getattr): pass

def lookupmodule(node, mv):
    path = []
    imports = mv.imports

    while isinstance(node, Getattr):
        path = [node.attrname] + path
        node = node.expr

    if isinstance(node, Name):
        path = [node.name] + path

        # --- search import chain
        for ident in path:
            if ident in imports:
                mod = imports[ident]
                imports = mod.mv.imports
            else:
                return None

        return mod

def lookupclass(node, mv): # XXX lookupvar first?
    if isinstance(node, Name):
        if node.name in mv.classes: return mv.classes[node.name]
        elif node.name in mv.ext_classes: return mv.ext_classes[node.name]
        else: return None
    elif isinstance(node, Getattr):
        module = lookupmodule(node.expr, mv)
        if module and node.attrname in module.classes:
            return module.classes[node.attrname]
    return None

def lookupfunc(node, mv): # XXX lookupvar first?
    if isinstance(node, Name):
        if node.name in mv.funcs: return mv.funcs[node.name]
        elif node.name in mv.ext_funcs: return mv.ext_funcs[node.name]
        else: return None
    elif isinstance(node, Getattr):
        module = lookupmodule(node.expr, mv)
        if module and node.attrname in module.funcs:
            return module.funcs[node.attrname]
    return None

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

def augmsg(node, msg):
    if hasattr(node, 'augment'): return '__i'+msg+'__'
    return '__'+msg+'__'

errormsgs = set()

def error(msg, node=None, warning=False):
    if msg in errormsgs: return
    errormsgs.add(msg)

    if warning: type = '*WARNING*'
    else: type = '*ERROR*'

    if node: lineno = ':'+str(node.lineno)
    else: lineno = ''

    msg = type+' '+getmv().module.filename+lineno+': '+msg
    print msg

    if not warning:
        sys.exit(1)

# --- merge constraint network along combination of given dimensions (dcpa, cpa, inheritance)
# e.g. for annotation we merge everything; for code generation, we might want to create specialized code
def merged(nodes, dcpa=False, inheritance=False):
    ggx = getgx()
    merge = {}
    if inheritance: # XXX do we really need this crap
        mergeinh = merged([n for n in nodes if n.thing in ggx.inherited])
        mergenoinh = merged([n for n in nodes if not n.thing in ggx.inherited])

    for node in nodes:
        # --- merge node types
        if dcpa: sort = (node.thing, node.dcpa)
        else: sort = node.thing
        sortdefault = merge.setdefault(sort, set())
        sortdefault.update(ggx.types[node])

        # --- merge inheritance nodes
        if inheritance:
            inh = ggx.inheritance_relations.get(node.thing, [])

            # merge function variables with their inherited versions (we don't customize!)
            if isinstance(node.thing, variable) and isinstance(node.thing.parent, function):
                var = node.thing
                for inhfunc in ggx.inheritance_relations.get(var.parent, []):
                    if var.name in inhfunc.vars:
                        if inhfunc.vars[var.name] in mergenoinh:
                            sortdefault.update(mergenoinh[inhfunc.vars[var.name]])
                for inhvar in ggx.inheritance_tempvars.get(var, []): # XXX more general
                    if inhvar in mergenoinh:
                        sortdefault.update(mergenoinh[inhvar])

            # node is not a function variable
            else:
                for n in inh:
                    if n in mergeinh: # XXX ook mergenoinh?
                        sortdefault.update(mergeinh[n])
    return merge

def lookup_class_module(objexpr, mv, parent):
    if isinstance(objexpr, Name): # XXX Getattr?
        var = lookupvar(objexpr.name, parent)
        if var and not var.imported: # XXX cl?
            return None, None
    return lookupclass(objexpr, mv), lookupmodule(objexpr, mv)

# --- analyze call expression: namespace, method call, direct call/constructor..
def analyze_callfunc(node): # XXX generate target list XXX uniform variable system!
    #print 'analyze callnode', node, inode(node).parent
    namespace, objexpr, method_call, parent_constr = inode(node).mv.module, None, False, False 
    constructor, direct_call = None, None
    mv = inode(node).mv

    # method call
    if isinstance(node.node, Getattr):
        objexpr, ident = node.node.expr, node.node.attrname
        cl, module = lookup_class_module(objexpr, mv, inode(node).parent)

        if cl:
            # staticmethod call
            if ident in cl.staticmethods:
                direct_call = cl.funcs[ident]
                return objexpr, ident, direct_call, method_call, constructor, parent_constr

            # ancestor call
            elif ident not in ['__setattr__', '__getattr__'] and inode(node).parent:
                thiscl = inode(node).parent.parent
                if isinstance(thiscl, class_) and cl.ident in [x.ident for x in thiscl.ancestors_upto(None)]: # XXX
                    if lookupimplementor(cl,ident):
                        parent_constr = True
                        ident = ident+lookupimplementor(cl, ident)+'__' # XXX change data structure
                        return objexpr, ident, direct_call, method_call, constructor, parent_constr

        if module: # XXX elif?
            namespace, objexpr = module, None
        else:
            method_call = True

    elif isinstance(node.node, Name):
        ident = node.node.name
    else:
        ident = 'meuk' # XXX ?

    # direct [constructor] call
    if isinstance(node.node, Name) or namespace != inode(node).mv.module:
        if isinstance(node.node, Name):
            if lookupvar(ident, inode(node).parent):
                return objexpr, ident, direct_call, method_call, constructor, parent_constr
        if ident in namespace.mv.classes:
            constructor = namespace.mv.classes[ident]
        elif ident in namespace.mv.funcs:
            direct_call = namespace.mv.funcs[ident]
        elif ident in namespace.mv.ext_classes:
            constructor = namespace.mv.ext_classes[ident]
        elif ident in namespace.mv.ext_funcs:
            direct_call = namespace.mv.ext_funcs[ident]
        else:
            if namespace != inode(node).mv.module:
                return objexpr, ident, None, False, None, False

    return objexpr, ident, direct_call, method_call, constructor, parent_constr

# XXX ugly: find ancestor class that implements function 'ident'
def lookupimplementor(cl, ident):
    while cl:
        if ident in cl.funcs and not cl.funcs[ident].inherited:
            return cl.ident
        if cl.bases:
            cl = cl.bases[0]
        else:
            break
    return None

def nrargs(node):
    if inode(node).lambdawrapper:
        return inode(node).lambdawrapper.largs
    return len(node.args)

# --- return list of potential call targets
def callfunc_targets(node, merge):
    objexpr, ident, direct_call, method_call, constructor, parent_constr = analyze_callfunc(node)
    funcs = []

    if node.node in merge and [t for t in merge[node.node] if isinstance(t[0], function)]: # anonymous function call
        funcs = [t[0] for t in merge[node.node] if isinstance(t[0], function)]

    elif constructor:
        if ident in ('list', 'tuple', 'set', 'frozenset') and nrargs(node) == 1:
            funcs = [constructor.funcs['__inititer__']]
        elif (ident, nrargs(node)) in (('dict', 1), ('defaultdict', 2)): # XXX merge infer.redirect
            funcs = [constructor.funcs['__initdict__']] # XXX __inititer__?
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

def analyze_args(expr, func, node=None, skip_defaults=False, merge=None):
    objexpr, ident, direct_call, method_call, constructor, parent_constr = analyze_callfunc(expr)
    anon_func = is_anon_func(expr, node, merge)

    args = []
    kwdict = {}
    for a in expr.args:
        if isinstance(a, Keyword):
            kwdict[a.name] = a.expr
        else:
            args.append(a)
    formal_args = func.formals[:]
    if func.node.varargs:
        formal_args = formal_args[:-1]
    default_start = len(formal_args)-len(func.defaults)

    if ident in ['__getattr__', '__setattr__']: # property?
        args = args[1:]

    if (method_call or constructor) and not (parent_constr or anon_func): # XXX
        args = [None]+args

    argnr = 0
    actuals, formals, defaults = [], [], []
    missing = False
    for i, formal in enumerate(formal_args):
        if formal in kwdict:
            actuals.append(kwdict[formal])
            formals.append(formal)
        elif formal.startswith('__kw_') and formal[5:] in kwdict:
            actuals.insert(0, kwdict[formal[5:]])
            formals.insert(0, formal)
        elif argnr < len(args) and not formal.startswith('__kw_'):
            actuals.append(args[argnr])
            argnr += 1
            formals.append(formal)
        elif i >= default_start:
            if not skip_defaults:
                default = func.defaults[i-default_start]
                if formal.startswith('__kw_'):
                    actuals.insert(0,default)
                    formals.insert(0,formal)
                else:
                    actuals.append(default)
                    formals.append(formal)
                defaults.append(default)
        else:
            missing = True
    extra = args[argnr:]

    error = (missing or extra) and not func.node.varargs and not func.node.kwargs and not expr.star_args and func.lambdanr is None and expr not in getgx().lambdawrapper # XXX

    if func.node.varargs:
        for arg in extra:
            actuals.append(arg)
            formals.append(func.formals[-1])

    return actuals, formals, defaults, extra, error

def is_anon_func(expr, node, merge=None): # XXX move to analyze_callfunc
    types = set()
    if node:
        node = (expr.node, node.dcpa, node.cpa)
        if node in getgx().cnode:
            types = getgx().cnode[node].types()
    else:
        if expr.node in merge:
            types = merge[expr.node]
    return bool([t for t in types if isinstance(t[0], function)])

def connect_actual_formal(expr, func, parent_constr=False, check_error=False, merge=None):
    pairs = []

    actuals = [a for a in expr.args if not isinstance(a, Keyword)]
    if isinstance(func.parent, class_):
        formals = [f for f in func.formals if f != 'self']
    else:
        formals = [f for f in func.formals]
    keywords = [a for a in expr.args if isinstance(a, Keyword)]

    if parent_constr:
        actuals = actuals[1:]

    if check_error and func.ident != 'sum' and func.lambdanr is None and expr not in getgx().lambdawrapper: # XXX sum
        if not func.node.varargs and not func.node.kwargs and len(actuals)+len(keywords) > len(formals):
            error("too many arguments in call to '%s'" % func.ident, expr)
        if not func.node.varargs and not func.node.kwargs and len(actuals)+len(keywords) < len(formals)-len(func.defaults) and not expr.star_args:
            error("not enough arguments in call to '%s'" % func.ident, expr)
        missing = formals[len(actuals):-len(func.defaults)]

    skip_defaults = True # XXX
    if not func.mv.module.builtin or func.mv.module.ident in ['random', 'itertools', 'datetime', 'ConfigParser', 'csv'] or (func.ident in ('sort','sorted', 'min', 'max', 'print')):
        if not (func.mv.module.builtin and func.ident == 'randrange'):
            skip_defaults = False

    actuals, formals, _, extra, _ = analyze_args(expr, func, skip_defaults=skip_defaults, merge=merge)

    for (actual, formal) in zip(actuals, formals):
        if not (isinstance(func.parent, class_) and formal == 'self'):
            pairs.append((actual, func.vars[formal]))
    return pairs, len(extra)

def parent_func(thing):
    parent = inode(thing).parent
    while parent:
        if not isinstance(parent, function) or not parent.listcomp:
            return parent
        parent = parent.parent

def register_tempvar(var, func):
    if func:
        func.registered_tempvars.append(var)

def const_literal(node):
    if isinstance(node, (UnarySub, UnaryAdd)):
        node = node.expr
    return isinstance(node, Const) and isinstance(node.value, (int, float))

# --- XXX description, confusion_misc? what's this for..
def confusion_misc():
    confusion = set()

    # use regular tuple if both elements have the same type representation
    cl = defclass('tuple')
    var1 = lookupvar('first', cl)
    var2 = lookupvar('second', cl)
    if not var1 or not var2: return # XXX ?

    for dcpa in getgx().tuple2.copy():
        getgx().tuple2.remove(dcpa)

    # use regular tuple template for tuples used in addition
    for node in getgx().merged_all:
        if isinstance(node, CallFunc):
            if isinstance(node.node, Getattr) and node.node.attrname in ['__add__','__iadd__'] and not isinstance(node.args[0], Const):

                tupletypes = set()
                for types in [getgx().merged_all[node.node.expr], getgx().merged_all[node.args[0]]]:
                    for t in types:
                        if t[0].ident == 'tuple':
                            if t[1] in getgx().tuple2:
                                getgx().tuple2.remove(t[1])
                                getgx().types[getgx().cnode[var1, t[1], 0]].update(getgx().types[getgx().cnode[var2, t[1], 0]])

                            tupletypes.update(getgx().types[getgx().cnode[var1, t[1], 0]])
