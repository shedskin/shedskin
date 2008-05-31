#!/usr/bin/env python

# *** SHED SKIN Python-to-C++ Compiler 0.0.28 ***
# Copyright 2005-2008 Mark Dufour; License GNU GPL version 3 (See LICENSE)

from compiler import *
from compiler.ast import *
from compiler.visitor import *

from shared import *
from graph import *
from cpp import *
from infer import *

import sys, string, copy, getopt, os.path, textwrap, traceback
from distutils import sysconfig

from backward import *

# --- XXX description, confusion_misc?
def confusion_misc(): 
    confusion = set()

    # --- tuple2

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

def analysis(source, testing=False):
    if testing: 
        gx = newgx()
        setgx(gx)
        ast = parse(source+'\n')
    else:
        gx = getgx()
        ast = parsefile(source)

    mv = None
    setmv(mv)

    # --- build dataflow graph from source code
    gx.main_module = parse_module(gx.main_mod, ast)
    gx.main_module.filename = gx.main_mod+'.py'
    gx.modules[gx.main_mod] = gx.main_module
    mv = gx.main_module.mv
    setmv(mv)

    # --- seed class_.__name__ attributes..
    for cl in getgx().allclasses:
        if cl.ident == 'class_':
            var = defaultvar('__name__', cl)
            getgx().types[inode(var)] = set([(defclass('str_'), 0)])

    # --- number classes (-> constant-time subclass check)
    number_classes()

    # --- non-ifa: copy classes for each allocation site
    for cl in getgx().allclasses:
        if cl.ident in ['int_','float_','none', 'class_','str_']: continue

        if cl.ident == 'list':
            cl.dcpa = len(getgx().list_types)+2
        elif cl.ident == '__iter': # XXX huh
            pass
        else:
            cl.dcpa = 2

        for dcpa in range(1, cl.dcpa): 
            class_copy(cl, dcpa)

    var = defaultvar('unit', defclass('str_'))
    getgx().types[inode(var)] = set([(defclass('str_'), 0)])

    #printstate()
    #printconstraints()

    # --- filters
    #merge = merged(getgx().types)
    #apply_filters(getgx().types.copy(), merge)
   
    # --- cartesian product algorithm & iterative flow analysis
    iterative_dataflow_analysis()
    #propagate()

    #merge = merged(getgx().types)
    #apply_filters(getgx().types, merge)

    for cl in getgx().allclasses:
        for name in cl.vars:
            if name in cl.parent.vars and not name.startswith('__'):
                error("instance variable '%s' of class '%s' shadows class variable" % (name, cl.ident))

    getgx().merged_all = merged(getgx().types) #, inheritance=True)
    getgx().merge_dcpa = merged(getgx().types, dcpa=True)

    mv = getgx().main_module.mv
    setmv(mv)
    propagate() # XXX remove 

    getgx().merged_all = merged(getgx().types) #, inheritance=True)
    getgx().merged_inh = merged(getgx().types, inheritance=True)

    # --- determine template parameters
    template_parameters()

    # --- detect inheritance stuff
    upgrade_variables()
    getgx().merged_all = merged(getgx().types)

    getgx().merged_inh = merged(getgx().types, inheritance=True)

    analyze_virtuals()

    # --- determine integer/float types that cannot be unboxed
    confused_vars()
    # --- check other sources of confusion
    confusion_misc() 

    getgx().merge_dcpa = merged(getgx().types, dcpa=True)
    getgx().merged_all = merged(getgx().types) #, inheritance=True) # XXX

    # --- determine which classes need an __init__ method
    for node, types in getgx().merged_all.items():
        if isinstance(node, CallFunc):
            objexpr, ident, _ , method_call, _, _, _ = analyze_callfunc(node)
            if method_call and ident == '__init__':
                for t in getgx().merged_all[objexpr]:
                    t[0].has_init = True

    # --- determine which classes need copy, deepcopy methods
    if 'copy' in getgx().modules:
        func = getgx().modules['copy'].funcs['copy']
        var = func.vars[func.formals[0]]
        for cl in set([t[0] for t in getgx().merged_inh[var]]):
            cl.has_copy = True # XXX transitive, modeling

        func = getgx().modules['copy'].funcs['deepcopy']
        var = func.vars[func.formals[0]]
        for cl in set([t[0] for t in getgx().merged_inh[var]]):
            cl.has_deepcopy = True # XXX transitive, modeling

    # --- add inheritance relationships for non-original Nodes (and tempvars?); XXX register more, right solution?
    for func in getgx().allfuncs:
        #if not func.mv.module.builtin and func.ident == '__init__':
        if func in getgx().inheritance_relations: 
            #print 'inherited from', func, getgx().inheritance_relations[func]
            for inhfunc in getgx().inheritance_relations[func]:
                for a, b in zip(func.registered, inhfunc.registered):
                    #print a, '->', b 
                    inherit_rec(a, b)

                for a, b in zip(func.registered_tempvars, inhfunc.registered_tempvars): # XXX more general
                    getgx().inheritance_tempvars.setdefault(a, []).append(b)

    getgx().merged_inh = merged(getgx().types, inheritance=True) # XXX why X times

    # --- finally, generate C++ code and Makefiles.. :-)

    #printstate()
    #printconstraints()
    generate_code()
    #generate_bindings()

    #print 'cnode!'
    #for (a,b) in getgx().cnode.items():
    #    print a, b
   # for (a,b) in getgx().types.items():
   #     print a, b

    # error for dynamic expression (XXX before codegen)
    for node in getgx().merged_all:
        if isinstance(node, Node) and not isinstance(node, AssAttr) and not inode(node).mv.module.builtin:
            typesetreprnew(node, inode(node).parent) 

    return gx

# --- annotate original code; use above function to merge results to original code dimensions
def annotate():
    def paste(expr, text):
        if not expr.lineno: return
        if (expr,0,0) in getgx().cnode and inode(expr).mv != mv: return # XXX
        line = source[expr.lineno-1][:-1]
        if '#' in line: line = line[:line.index('#')]
        if text != '':
            text = '# '+text
        line = string.rstrip(line)
        if text != '' and len(line) < 40: line += (40-len(line))*' '
        source[expr.lineno-1] = line 
        if text: source[expr.lineno-1] += ' ' + text
        source[expr.lineno-1] += '\n'

    for module in getgx().modules.values(): 
        mv = module.mv
        setmv(mv)

        # merge type information for nodes in module XXX inheritance across modules?
        merge = merged([n for n in getgx().types if n.mv == mv], inheritance=True)

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
        funcs = getmv().funcs.values()
        for cl in getmv().classes.values():
            labels = [var.name+': '+typesetreprnew(var, cl, False) for var in cl.vars.values() if var in merge and merge[var] and not var.name.startswith('__')] 
            if labels: paste(cl.node, ', '.join(labels))
            funcs += cl.funcs.values()

        # --- function variables
        for func in funcs:
            if not func.node or func.node in getgx().inherited: continue
            vars = [func.vars[f] for f in func.formals]
            labels = [var.name+': '+typesetreprnew(var, func, False) for var in vars if not var.name.startswith('__')]
            paste(func.node, ', '.join(labels))

        # --- callfuncs
        for callfunc, _ in getmv().callfuncs:
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
                out = open(os.path.join(getgx().output_dir, module.filename[:-3]+'.ss.py'),'w')
                out.write(''.join(source))
                out.close()
            except IOError:
                pass

# --- generate C++ and Makefiles
def generate_code():
    print '[generating c++ code..]'

    ident = getgx().main_module.ident 

    pyver = sysconfig.get_config_var('VERSION')

    if sys.platform != 'win32':
        includes = '-I' + sysconfig.get_python_inc() + ' ' + \
                   '-I' + sysconfig.get_python_inc(plat_specific=True)

        ldflags = sysconfig.get_config_var('LIBS') + ' ' + \
                  sysconfig.get_config_var('SYSLIBS') + ' ' + \
                  '-lpython'+pyver 
        if not sysconfig.get_config_var('Py_ENABLE_SHARED'):
            ldflags += ' -L' + sysconfig.get_config_var('LIBPL')

    if getgx().extension_module: 
        if sys.platform == 'win32': ident += '.pyd'
        else: ident += '.so'

    # --- generate C++ files
    mods = getgx().modules.values()
    for module in mods:
        if not module.builtin:
            # create output directory if necessary
            if getgx().output_dir:
                output_dir = os.path.join(getgx().output_dir, module.dir)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

            gv = generateVisitor(module)
            mv = module.mv 
            setmv(mv)
            gv.func_pointers(False)
            walk(module.ast, gv)
            gv.out.close()
            gv.header_file()
            gv.out.close()
            gv.insert_consts(declare=False)
            gv.insert_consts(declare=True)
            gv.insert_includes()

    # --- generate Makefile
    makefile = file(os.path.join(getgx().output_dir, 'Makefile'), 'w')

    cppfiles = ' '.join([m.filename[:-3].replace(' ', '\ ')+'.cpp' for m in mods])
    hppfiles = ' '.join([m.filename[:-3].replace(' ', '\ ')+'.hpp' for m in mods])

    # import flags
    if getgx().flags: flags = getgx().flags
    elif os.path.isfile('FLAGS'): flags = 'FLAGS'
    else: flags = connect_paths(getgx().sysdir, 'FLAGS')

    for line in file(flags):
        line = line[:-1]

        if line[:line.find('=')].strip() == 'CCFLAGS': 
            line += ' -I. -I'+getgx().libdir.replace(' ', '\ ')
            if sys.platform == 'darwin' and os.path.isdir('/opt/local/include'): 
                line += ' -I/opt/local/include' # macports... and fink?
            if not getgx().wrap_around_check: line += ' -DNOWRAP' 
            if getgx().bounds_checking: line += ' -DBOUNDS' 
            if getgx().extension_module: 
                if sys.platform == 'win32': line += ' -Ic:/Python%s/include -D__SS_BIND' % pyver
                else: line += ' -g -fPIC -D__SS_BIND ' + includes

        elif line[:line.find('=')].strip() == 'LFLAGS': 
            if sys.platform == 'darwin' and os.path.isdir('/opt/local/lib'):  
                line += ' -L/opt/local/lib'
            if getgx().extension_module: 
                if sys.platform == 'win32': line += ' -shared -Lc:/Python%s/libs -lpython%s' % (pyver, pyver) 
                elif sys.platform == 'darwin': line += ' -bundle -Xlinker -dynamic ' + ldflags
                else: line += ' -shared -Xlinker -export-dynamic ' + ldflags
            if 're' in [m.ident for m in mods]:
                line += ' -lpcre'

        print >>makefile, line
    print >>makefile

    print >>makefile, 'all:\t'+ident+'\n'

    if not getgx().extension_module:
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

def usage():
    print """Usage: shedskin [OPTION]... FILE

 -a --noann             Don't output annotated source code
 -b --bounds            Enable bounds checking
 -d --dir               Specify alternate directory for output files
 -e --extmod            Generate extension module
 -f --flags             Provide alternate Makefile flags
 -i --infinite          Try to avoid infinite analysis time 
 -n --nowrap            Disable wrap-around checking 
"""
    sys.exit()

def main():
    gx = newgx()
    setgx(gx)

    print '*** SHED SKIN Python-to-C++ Compiler 0.0.28 ***'
    print 'Copyright 2005-2008 Mark Dufour; License GNU GPL version 3 (See LICENSE)'
    print '(Please send bug reports here: mark.dufour@gmail.com)'
    print
    
    # --- some checks
    major, minor = sys.version_info[:2]
    if major != 2 or minor < 3:
        print '*ERROR* Shed Skin is not compatible with this version of Python'
        sys.exit()

    if sys.platform == 'win32' and os.path.isdir('c:/mingw'):
        print '*ERROR* please rename or remove c:/mingw, as it conflicts with Shed Skin'
        sys.exit()

    # --- command-line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'eibnfad:', ['infinite', 'extmod', 'bounds', 'nowrap', 'flags=', 'dir='])
    except getopt.GetoptError:
        usage()
    
    for o, a in opts:
        if o in ['-h', '--help']: usage()
        if o in ['-b', '--bounds']: getgx().bounds_checking = True
        if o in ['-e', '--extmod']: getgx().extension_module = True
        if o in ['-a', '--noann']: getgx().annotation = False
        if o in ['-i', '--infinite']: getgx().avoid_loops = True
        if o in ['-d', '--dir']: getgx().output_dir = a
        if o in ['-f', '--flags']: 
            if not os.path.isfile(a): 
                print "*ERROR* no such file: '%s'" % a
                sys.exit()
            getgx().flags = a
        if o in ['-n', '--nowrap']: getgx().wrap_around_check = False

    # --- argument
    if len(args) != 1:
        usage()
    name = args[0]
    if not name.endswith('.py'):
        name += '.py'
    if not os.path.isfile(name): 
        print "*ERROR* no such file: '%s'" % name
        sys.exit()
    gx.main_mod = name[:-3]
        
    # --- analyze & annotate
    analysis(name)
    if getgx().annotation:
        annotate()

if __name__ == '__main__':
    main()
