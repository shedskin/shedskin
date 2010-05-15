#!/usr/bin/env python

from distutils.core import setup

setup(name='shedskin',
      version='0.5',
      description='Shed Skin is an experimental compiler, that can translate pure, but implicitly statically typed Python programs into optimized C++. It can generate stand-alone programs or extension modules that can be imported and used in larger Python programs.',
      url='http://code.google.com/p/shedskin/',
      scripts=['scripts/shedskin'],
      packages=['shedskin'],
      package_data={'shedskin': ['lib/*.cpp', 'lib/*.hpp', 'lib/*.py', 'lib/os/*.cpp', 'lib/os/*.hpp', 'lib/os/*.py', 'FLAGS']},
     )
