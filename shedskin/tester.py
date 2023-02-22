"""shedskin testrunner
"""
import glob
import pathlib
import logging

from .cmake import CMakeBuilder

class TestRunner(CMakeBuilder):
    """basic test runner"""

    def __init__(self, options):
        self.options = options
        self.build_dir = pathlib.Path("build")
        self.source_dir = pathlib.Path.cwd()
        self.tests = sorted(glob.glob("./test_*/test_*.py", recursive=True))
        self.log = logging.getLogger(self.__class__.__name__)
