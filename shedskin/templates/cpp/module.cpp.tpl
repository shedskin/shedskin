#include "builtin.hpp"
{% block docs %}
{% if node.doc %}
/**
{% set doc = node.doc.replace('/*', '//').replace('*/', '//').split('\n') %}
{% if doc[0].strip() %}{{ doc[0] }}{% endif %}
{% set lines = dedent('\n'.join(doc[1:])).splitlines() %}
{% for line in lines %}
{{ line }}
{% endfor %}
*/

{% endif %}
{% endblock %}

{% block namespaces %}
{% for name in module.name_list %}
namespace __{{name}}__ {
{% endfor %}
{% endblock %}

{% block imports %}
{% include "imports.cpp.tpl" %}
{% endblock %}

{% block globals %}
{% for type, vars in globals|groupby(0) %}
{# group variables of the same type together, but watch out for pointers #}
{% set pointer = '*' if type.endswith('*') else '' -%}

{{ type|depointer }}
{%- for var in vars -%}
  {% if not loop.first %}, {% endif -%}
  {{ pointer }}{{ var[1] }}
{%- endfor -%};
{% endfor -%}
{% endblock %}

{% block defaults %}
{% for type, number in defaults %}
{{type}} default_{{number}};
{% endfor %}
{% endblock %}

{% block end_namespaces %}
{% for name in module.name_list %}
{# } #}
{% endfor %}
{% endblock %}
