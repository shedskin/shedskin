{% macro module_filename(modules, suffix) -%}
{% for module in modules %}
{% if not loop.first %}	{% endif %}
{{ module|replace('.py', suffix) -}}
{% if not loop.last %} \
{%+ endif %}
{%+ endfor %}
{%- endmacro -%}


{%- block variables %}
{% for name, value in variables %}
{% if name == 'CCFLAGS' -%}
  {% block CCFLAGS scoped -%}
  CCFLAGS={{ value }} -I.
  {%- for libdir in libdirs %} -I{{ libdir }}{% endfor %}

  {% endblock CCFLAGS %}
{% else -%}
  {{ name }}={{ value }}
{% endif %}
{% endfor %}

{% endblock variables %}

{% block files %}
CPPFILES={{ module_filename(module_filenames, '.cpp') }}
HPPFILES={{ module_filename(module_filenames, '.hpp') }}
{% endblock %}

{% block all %}
all:	{{ ident }}
{% endblock %}

{% set ext = '.exe' if platform == 'win32' and not extension_module else '' %}

{% block targets %}
{{ ident }}:	$(CPPFILES) $(HPPFILES)
	$(CC) $(CCFLAGS) $(CPPFILES) $(LFLAGS) -o {{ ident }}{{ ext }}

{% if not extension_module %}
{{ ident }}_prof:	$(CPPFILES) $(HPPFILES)
	$(CC) -pg -ggdb $(CCFLAGS) $(CPPFILES) $(LFLAGS) -o {{ ident }}_prof{{ ext }}

{{ ident }}_debug:	$(CPPFILES) $(HPPFILES)
	$(CC) -g -ggdb $(CCFLAGS) $(CPPFILES) $(LFLAGS) -o {{ ident }}_debug{{ ext }}
{% endif %}

{%- endblock targets %}

{% if not targets %}
  {% set targets = [ident, ident + '_prof', ident + '_debug'] %}
{% endif %}

{% block clean %}
clean:
	rm -f {% for target in targets %}{{ target }}{{ ext }} {% endfor %}
{% endblock %}

{% block phony %}
.PHONY: all clean
{% endblock %}
