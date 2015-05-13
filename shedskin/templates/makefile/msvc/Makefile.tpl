{% extends "Makefile.tpl" %}
{% set output = ident + '.exe' if not extension_module else ident %}
{% set targets = [ident] %}

{% block targets scoped %}
{{ ident }}:	$(CPPFILES) $(HPPFILES)
	$(CC) $(CCFLAGS) $(CPPFILES) $(LFLAGS) /out: {{ output }}
{%- endblock targets %}

