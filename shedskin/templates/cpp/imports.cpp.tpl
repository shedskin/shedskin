{# imports -> using #}
{% for child, child_module in imports -%}
{% set mod_name = child_module.full_path() -%}

{% for name, pseudo in child.names -%}
{% set pseudo = pseudo or name -%}
{% if name == '*' -%}

  {% for func in child_module.mv.funcs.values()|selectattr("cp") -%}
    using {{ mod_name }}::{{cpp_name(func)}};
  {% endfor %}

  {% for cl in child_module.mv.classes.values() -%}
    using {{ mod_name }}::{{cpp_name(cl)}};
  {% endfor %}

{% elif pseudo not in module.mv.globals -%}
  {% if name in child_module.mv.funcs -%}
    {% set func = child_module.mv.funcs[name] %}
    {% if func.cp -%}
      using {{ mod_name }}::{{cpp_name(func)}};
    {% endif %}
  {% else -%}
    using {{ mod_name }}::{{namer.nokeywords(name)}};
  {% endif %}
{% endif %}

{% endfor %}
{% endfor %}
