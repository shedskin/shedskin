Shed Skin
=========

An experimental (restricted-Python)-to-C++ compiler
---------------------------------------------------

**Shed Skin** is an *experimental* compiler, that can translate pure, but *implicitly statically* typed Python (2.4-2.6) programs into optimized C++. It can generate stand-alone programs or extension modules that can be imported and used in larger Python programs.

Besides the typing restriction, programs cannot freely use the Python standard library (although about 25 common modules, such as :code:`random` and :code:`re`, are currently supported). Also, not all Python features, such as nested functions and variable numbers of arguments, are supported.

For a set of a `75 non-trivial programs <https://github.com/shedskin/shedskin/releases/download/v0.9.4/shedskin-examples-0.9.4.tgz>`_ (at over 25,000 lines in total (sloccount)), measurements show a typical speedup of 2-200 times over CPython.

Documentation
-------------

.. toctree::
   :maxdepth: 5

   documentation
