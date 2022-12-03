#include "builtin.hpp"

<%!
    import itertools
    from textwrap import dedent

    # this should be a method
    def module_doc(node):
        doc = node.doc.replace('/*', '//').replace('*/', '//').split('\n')
        lines = []
        if doc[0].strip():
            lines.append(doc[0])
        lines.extend(dedent('\n'.join(doc[1:])).splitlines())
        return lines

    depointer = lambda ts: ts[:-1] if ts.endswith('*') else ts

    def groupby(data, index):
        keyfunc = lambda x: x[index]
        data = sorted(data, key=keyfunc)
        return itertools.groupby(data, keyfunc)
%>

<%block name="docs">
% if hasattr(node, 'doc'):
/**
% for line in module_doc(node):
${line}
% endfor
*/
% endif
</%block>


<%block name="namespaces">
// namespaces
% for name in module.name_list:
namespace __${name}__ {
% endfor
// end namespaces
</%block>


<%block name="imports">
// imports
<%include file="imports.cpp"/>
// end imports
</%block>

<%block name="globals_block">
// globals
% for type, vars in groupby(globals, 0):
<% 
    pointer = '*' if type.endswith('*') else ''
%>
${depointer(type)}
% for var in vars:
% if not loop.index == 0:
, 
% endif
% if len(var) > 1:
${pointer} ${var[1]}
% endif
% endfor
% endfor
// end globals
</%block>

<%block name="defaults_block">
// defaults
% for type, number in defaults:
${type} default_${number};
% endfor
// end defaults
</%block>


<%block name="end_namespaces">
% for name in module.name_list:
## }
% endfor
</%block>
