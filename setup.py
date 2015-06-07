#!/usr/bin/env python

from distutils.core import setup, Command
import os

with open('README.rst') as readme:
    description = [
        line.strip() for line in readme.readlines()
        if line.startswith('Shed Skin is an')][0]


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

templates = []
for root, _, files in os.walk(os.path.join('shedskin', 'templates')):
    templates.extend(os.path.join(root, f) for f in files)
print templates

setup(
    name='shedskin',
    version='0.9.4',
    description=description,
    url='http://code.google.com/p/shedskin/',
    scripts=['scripts/shedskin'],
    cmdclass={'test': run_tests},
    install_requires=['blessings', 'progressbar2', 'jinja2'],
    packages=['shedskin'],
    package_data={
        'shedskin': [
            'lib/*.cpp', 'lib/*.hpp', 'lib/builtin/*.cpp', 'lib/builtin/*.hpp',
            'lib/*.py', 'lib/os/*.cpp', 'lib/os/*.hpp', 'lib/os/*.py',
            'FLAGS*', 'illegal'] + templates},
)
