'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2011 Mark Dufour; License GNU GPL version 3 (See LICENSE)

struct_.py: hacks to support struct module

'''

from shared import *

# --- struct.unpack "type inference"
def struct_info(node, func):
    if isinstance(node, Name):
        var = lookupvar(node.name, func) # XXX fwd ref?
        if not var or len(var.const_assign) != 1:
            error('non-constant format string', node, mv=getmv())
        error('assuming constant format string', node, mv=getmv(), warning=True)
        fmt = var.const_assign[0].value
    elif isinstance(node, Const):
        fmt = node.value
    else:
        error('non-constant format string', node, mv=getmv())
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
                result.extend(int(digits or '1')*[(ordering, c, rtype, 1)])
            digits = ''
        else:
            error('bad or unsupported char in struct format: '+repr(c), node, mv=getmv())
            digits = ''
    return result

def struct_unpack(rvalue, func):
    if isinstance(rvalue, CallFunc):
        if isinstance(rvalue.node, Getattr) and isinstance(rvalue.node.expr, Name) and rvalue.node.expr.name == 'struct' and rvalue.node.attrname == 'unpack' and lookupvar('struct', func).imported: # XXX imported from where?
            return True
        elif isinstance(rvalue.node, Name) and rvalue.node.name == 'unpack' and 'unpack' in getmv().ext_funcs and not lookupvar('unpack', func): # XXX imported from where?
            return True

def struct_faketuple(info):
   result = []
   for o, c, t, d in info:
       if d != 0 or c == 's':
           if t == 'int': result.append(Const(1))
           elif t == 'str': result.append(Const(''))
           elif t == 'float': result.append(Const(1.0))
           elif t == 'bool': result.append(Name('True'))
   return Tuple(result)

def struct_unpack_cpp(self, node, func):
    struct_unpack = getgx().struct_unpack.get(node)
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
                if isinstance(n, Subscript): # XXX merge
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
