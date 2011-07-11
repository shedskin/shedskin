#!/usr/bin/env python

from distutils.core import setup, Command
import os

class run_tests(Command):
    description = "run testsuite"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        self.cwd = os.getcwd()
        ss_dir = os.path.abspath(__file__).split(os.path.sep)[:-1]
        ss_dir.append('tests')
        self.tests_dir = os.path.sep.join(ss_dir)
    def run(self):
        os.chdir(self.tests_dir)
        os.system('./run.py')
        os.chdir(self.cwd)

setup(name='shedskin',
      version='0.9',
      description='Shed Skin is an experimental compiler, that can translate pure, but implicitly statically typed Python programs into optimized C++. It can generate stand-alone programs or extension modules that can be imported and used in larger Python programs.',
      url='http://code.google.com/p/shedskin/',
      scripts=['scripts/shedskin'],
      cmdclass={'test':run_tests},
      packages=['shedskin'],
      package_data={'shedskin': ['lib/*.cpp', 'lib/*.hpp', 'lib/builtin/*.cpp', 'lib/builtin/*.hpp', 'lib/*.py', 'lib/os/*.cpp', 'lib/os/*.hpp', 'lib/os/*.py', 'FLAGS*', 'illegal']},
     )
