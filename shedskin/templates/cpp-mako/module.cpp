#include "builtin.hpp"

<%block name="docs">
% if hasattr(node, 'doc'):
/**
% for line in node.doc.splitlines():
${line}
% endfor
*/
% endif
</%block>

<%block name="namespaces">
% for name in module.name_list:
namespace __${name}__ {
% endfor
</%block>

<%block name="imports">
<%include file="imports.cpp"/>
</%block>

<%block name="globals_block">
// globals
% for type, vars in globals:
${type} ${vars};
% endfor
</%block>

<%block name="defaults_block">
// defaults
% for type, number in defaults:
${type} default_${number};
% endfor
</%block>
