import os
import sys
import tempfile
import unittest
from distutils import sysconfig

from shedskin.config import GlobalInfo
from shedskin.makefile import generate_makefile
from shedskin.python import Module


class TestMakefile(unittest.TestCase):

    def setUp(self):
        self.gx = GlobalInfo()
        self.gx.main_module = (
            Module('main', 'filename.py', 'filename.py', False, None))
        self.gx.modules = {'main': self.gx.main_module}
        self.envs = [
            {'msvc': True,  'platform': 'win32',  'ext': True },
            {'msvc': False, 'platform': 'win32',  'ext': True },
            {'msvc': False, 'platform': 'linux2', 'ext': True },
            {'msvc': True,  'platform': 'win32',  'ext': False},
            {'msvc': False, 'platform': 'win32',  'ext': False},
            {'msvc': False, 'platform': 'linux2', 'ext': False},
        ]

    def test_matrix(self):
        for env in self.envs:
            sys.platform = env['platform']
            self.gx.msvc = env['msvc']
            self.gx.extension_module = env['ext']
            # Get the generated output
            with tempfile.NamedTemporaryFile() as makefile:
                self.gx.makefile_name = makefile.name
                generate_makefile(self.gx)

                output = makefile.read()

            # Get the expected output
            filename = os.path.join(
                'tests', 'testdata', 'makefile_outputs',
                '%d.Makefile' % (hash(tuple(sorted(env.items()))) % 10000))

            with open(filename) as f:
                expected_output = f.read()

            if output != expected_output:
                import difflib
                diff = "\n".join(difflib.context_diff(
                    output.splitlines(), expected_output.splitlines()))
                print 'full diff:', diff
                expected_diff = ["SHEDSKIN_LIBDIR", "CC=", "CCFLAGS=", "LFLAGS="]
                def strip_expected_diff(line):
                    for item in expected_diff:
                        if item in line:
                            return ""
                    else:
                        return item
                output = map(strip_expected_diff, output.splitlines())
                expected_output = map(strip_expected_diff, expected_output.splitlines())
                diff = "\n".join(difflib.context_diff(
                    output, expected_output))
                print 'stripped diff:', diff
                if diff:
                    raise ValueError('Generated Makefile was different')


if __name__ == '__main__':
    unittest.main()
