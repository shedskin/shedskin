{# imports -> using #}
{% for child_module in imports %}

{% for name, pseudo in child.names %}
{% if name == '*' %}

{% for func in child_module.mv.funcs.values()|selectattr("cp") %}
using {{ child_module }}::{{cpp_name(func)}};
{% endfor %}

{% for cl in child_module.mv.classes.values() %}
using {{ child_module }}::{{cpp_name(cl)}};
{% endfor %}

{% elif pseudo not in module.mv.globals %}
{% if name in child_module.mv.funcs %}
using {{ child_module }}::{{cpp_name(func)}};
{% else %}
using {{ child_module }}::{{namer.nokeywords(name)}};
{% endif %}
{% endif %}

{% endfor %}
{% endfor %}
