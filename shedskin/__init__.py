"""
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2023 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)

"""

import argparse
import logging
import os
import os.path
import pathlib
import sys
import time

from . import cmake, config, cpp, error, graph, infer, log


class Shedskin:
    """Main shedskin frontend class
    """
    def __init__(self, options):
        self.configure_log()
        self.gx = self.configure(options)
        self.gx.options = options
        if 'name' in options:
            self.module_name = self.get_name(options.name)

    def configure_log(self):
        # silent -> WARNING only, debug -> DEBUG, default -> INFO
        console = logging.StreamHandler(stream=sys.stdout)
        console.setFormatter(log.ShedskinFormatter())
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(console)
        self.log.setLevel(logging.INFO)
        # debug=3 -> IFA (iterative flow analysis) logging enabled.
        self.ifa_log = logging.getLogger('infer.ifa')
        self.ifa_log.addHandler(console)
        self.ifa_log.setLevel(logging.INFO)

    def get_name(self, module_path):
        """Returns name of module to be translated.

        Also sets current working dir for nested targets
        and sets module_path configuration.

        :param      module_path:     The module path
        :type       module_name:     str
        """
        path = pathlib.Path(module_path)

        if path.is_dir():
            # TODO: add python package compilation
            #   check for __main__ for exe
            #   check for __init__ for ext
            self.log.error("module_path is a directory: '%s'", module_path)
            sys.exit(1)

        if path.parent != pathlib.Path('.'): # path is in current dir
            os.chdir(path.parent)
            path = pathlib.Path(path.name)

        if not path.name.endswith('.py'):
            path = path.with_suffix('.py')
        if not path.is_file():
            self.log.error("no such file: '%s'", path)
            sys.exit(1)
        self.gx.module_path = path.absolute()
        return path.stem

    def configure(self, args):
        # print(args)
        gx = config.GlobalInfo()

        if args.subcmd in ['build', 'run', 'test']:
            # ensure cmake is available and installed.
            cmake.check_cmake_availability()

        if args.subcmd in ['translate', 'build', 'run']: # i.e. not relevant for 'test'

            if args.nobounds:
                gx.bounds_checking = False

            if args.extmod:
                gx.executable_product = False
                gx.pyextension_product = True

            if args.debug:
                self.log.setLevel(logging.DEBUG)
                if args.debug == 3:
                    self.ifa_log.setLevel(logging.DEBUG)

            if args.long:
                gx.longlong = True

    #        if args.float:
    #            ss.gx.float = True

            if args.nogc:
                gx.nogc = True

            if args.nogcwarns:
                gx.gcwarns = False

            if args.nowrap:
                gx.wrap_around_check = False

#            if args.random:
#                gx.fast_random = True

            if args.noassert:
                gx.assertions = False

            if args.subcmd == 'translate':
                if args.nomakefile:
                    gx.nomakefile = True

                if args.makefile:
                    gx.makefile_name = args.makefile

                if args.flags:
                    if not os.path.isfile(args.flags):
                        self.log.error("no such file: '%s'", args.flags)
                        sys.exit(1)
                    gx.flags = args.flags

            if args.outputdir:
                if not os.path.exists(args.outputdir):
                    os.makedirs(args.outputdir, exist_ok=True)
                gx.outputdir = args.outputdir

            if args.silent:
                gx.silent = True
                self.log.setLevel(logging.WARNING)

            if args.traceback:
                gx.backtrace = True

            if args.executable:
                gx.executable_product = True

            if args.extra_lib:
                gx.libdirs = [args.extra_lib] + gx.libdirs

        # --- some checks
        major, minor = sys.version_info[:2]
        if (major, minor) not in [(3, 8), (3, 9), (3, 10), (3, 11), (3, 12)]:
            self.log.error('Shed Skin is not compatible with this version of Python')
            sys.exit(1)

        return gx

    def analyze(self):
        self.gx.main_module = graph.parse_module(self.module_name, self.gx)

    def translate(self):
#        self.log.warning('translate option (using make) is deprecated. please use build option.')

        t0 = time.time()
        infer.analyze(self.gx, self.module_name)
        cpp.generate_code(self.gx)
        error.print_errors()
        self.log.info('\n[elapsed time: %.2f seconds]', (time.time() - t0))

    def build(self):
        cmake.generate_cmakefile(self.gx)
        builder = cmake.CMakeBuilder(self.gx.options)
        builder.build()

    def test(self):
        if self.gx.options.run_errs:
            testrunner = cmake.TestRunner(self.gx.options)
            testrunner.run_error_tests()
        else:
            testrunner = cmake.TestRunner(self.gx.options)
            testrunner.run_tests()

    def run(self):
        cwd = pathlib.Path.cwd()
        p = pathlib.Path(self.gx.options.name)
        if len(p.parts) == 1:
            executable = cwd / 'build' / p.stem
        else:
            executable = cwd.parent / 'build' / p.parent.name / p.parent.name
        os.system(executable)

    @classmethod
    def commandline(cls, bypassargs=None):
        """command line api
        """
        sys.setrecursionlimit(100000)

        # --- command-line options
        parser = argparse.ArgumentParser(
            prog = 'shedskin',
            description = 'Restricted-Python-to-C++ Compiler',
        )

        subparsers = parser.add_subparsers(
            title='subcommands',
            dest='subcmd')

        # common options
        arg = opt = parser.add_argument

        parser_analyze = subparsers.add_parser('analyze', help="analyze and validate python module")
        arg = opt = parser_analyze.add_argument

        arg("name", help="Python file or module to analyze")

        parser_translate = subparsers.add_parser('translate', help="translate python module to cpp")
        arg = opt = parser_translate.add_argument

        arg("name", help="Python file or module to compile")

        opt("-d", "--debug",        help="Set debug level", type=int)
        opt("-e", "--extmod",       help="Generate extension module", action="store_true")
        opt("-F", "--flags",        help="Provide alternate Makefile flags")
        opt("-I", "--include-dirs", help="Add an include directory", action="append")        
        opt("-L", "--link-dirs",    help="Add a link library directory", action="append")
        opt("-l", "--link-libs",    help="Add a link library", action="append")
        opt("-X", "--extra-lib",    help="Add an extra builtins library directory")
        opt("-m", "--makefile",     help="Specify alternate Makefile name")
        opt("-o", "--outputdir",    help="Specify output directory for generated files")
#        opt("-r", "--random",       help="Use fast random number generator (rand())", action="store_true")
        opt("-s", "--silent",       help="Silent mode, only show warnings", action="store_true")
        opt("-t", "--traceback",    help="Print traceback for uncaught exceptions", action="store_true")
        opt("-x", "--executable",   help="Generate executable", action="store_true")
    
        opt("--long",               help="Use long long '64-bit' integers", action="store_true")
        opt("--noassert",           help="Disable assert statements", action="store_true")
        opt("-b", "--nobounds",     help="Disable bounds checking", action="store_true")
        opt("--nogc",               help="Disable garbage collection", action="store_true")
        opt("--nogcwarns",          help="Disable runtime GC warnings", action="store_true")
        opt("--nomakefile",         help="Disable makefile generation", action="store_true")
        opt("-w", "--nowrap",             help="Disable wrap-around checking", action="store_true")

        parser_build = subparsers.add_parser('build', help="build translated module")
        arg = opt = parser_build.add_argument

        arg("name", help="Python file or module to compile")

        # opt("--debug",            help="set cmake debug on", action="store_true")
        opt("--generator",          help="specify a cmake build system generator", metavar="G")
        opt("--jobs",               help="build and run in parallel using N jobs", metavar="N", type=int)
        opt("--build-type",         help="set cmake build type (default: '%(default)s')", metavar="T", default="Debug")
        opt("--test",               help="run ctest", action="store_true")
        opt("--reset",              help="reset cmake build", action="store_true")
        opt("--conan",              help="install cmake dependencies with conan", action="store_true")
        opt("--spm",                help="install cmake dependencies with spm", action="store_true")
        opt("--extproject",         help="install cmake dependencies with externalproject", action="store_true")
        opt('--ccache',             help='enable ccache with cmake', action='store_true')
        opt('--target',             help='build only specified cmake targets', nargs="+", metavar="TARGET")
    
        opt("-d", "--debug",        help="Set debug level", type=int)
        opt("-e", "--extmod",       help="Generate extension module", action="store_true")
        opt("-I", "--include-dirs", help="Add an include directory", action="append")        
        opt("-L", "--link-dirs",    help="Add a link library directory", action="append")
        opt("-l", "--link-libs",    help="Add a link library", action="append")
        opt("-X", "--extra-lib",    help="Add an extra builtins library directory")
        opt("-o", "--outputdir",    help="Specify output directory for generated files")
#        opt("-r", "--random",       help="Use fast random number generator (rand())", action="store_true")
        opt("-s", "--silent",       help="Silent mode, only show warnings", action="store_true")
        opt("-t", "--traceback",    help="Print traceback for uncaught exceptions", action="store_true")
        opt("-x", "--executable",   help="Generate executable", action="store_true")
    
        opt("--long",               help="Use long long '64-bit' integers", action="store_true")
        opt("--noassert",           help="Disable assert statements", action="store_true")
        opt("--nobounds",           help="Disable bounds checking", action="store_true")
        opt("--nowarnings",         help="Disable '-Wall' compilation warnings", action="store_true")
        opt("--nogc",               help="Disable garbage collection", action="store_true")
        opt("--nogcwarns",          help="Disable runtime GC warnings", action="store_true")
        opt("--nowrap",             help="Disable wrap-around checking", action="store_true")

        parser_run = subparsers.add_parser('run', help="run built and translated module")
        arg = opt = parser_run.add_argument

        arg("name", help="Python file or module to run")

        # opt("--debug",            help="set cmake debug on", action="store_true")
        opt("--generator",          help="specify a cmake build system generator", metavar="G")
        opt("--jobs",               help="build and run in parallel using N jobs", metavar="N", type=int)
        opt("--build-type",         help="set cmake build type (default: '%(default)s')", metavar="T", default="Debug")
        opt("--test",               help="run ctest", action="store_true")
        opt("--reset",              help="reset cmake build", action="store_true")
        opt("--conan",              help="install cmake dependencies with conan", action="store_true")
        opt("--spm",                help="install cmake dependencies with spm", action="store_true")
        opt("--extproject",         help="install cmake dependencies with externalproject", action="store_true")
        opt('--ccache',             help='enable ccache with cmake', action='store_true')
        opt('--target',             help='build only specified cmake targets', nargs="+", metavar="TARGET")
    
        opt("-d", "--debug",        help="Set debug level", type=int)
        opt("-e", "--extmod",       help="Generate extension module", action="store_true")
        opt("-I", "--include-dirs", help="Add an include directory", action="append")        
        opt("-L", "--link-dirs",    help="Add a link library directory", action="append")
        opt("-l", "--link-libs",    help="Add a link library", action="append")
        opt("-X", "--extra-lib",    help="Add an extra builtins library directory")
        opt("-o", "--outputdir",    help="Specify output directory for generated files")
#        opt("-r", "--random",       help="Use fast random number generator (rand())", action="store_true")
        opt("-s", "--silent",       help="Silent mode, only show warnings", action="store_true")
        opt("-t", "--traceback",    help="Print traceback for uncaught exceptions", action="store_true")
        opt("-x", "--executable",   help="Generate executable", action="store_true")
    
        opt("--long",               help="Use long long '64-bit' integers", action="store_true")
        opt("--noassert",           help="Disable assert statements", action="store_true")
        opt("--nobounds",           help="Disable bounds checking", action="store_true")
        opt("--nogc",               help="Disable garbage collection", action="store_true")
        opt("--nowarnings",         help="Disable '-Wall' compilation warnings", action="store_true")        
        opt("--nogcwarns",          help="Disable runtime GC warnings", action="store_true")
        opt("--nowrap",             help="Disable wrap-around checking", action="store_true")

        parser_test = subparsers.add_parser('test', help="run tests")
        arg = opt = parser_test.add_argument

        opt("-e", "--extmod",     help="Generate extension module", action="store_true")
        opt("-x", "--executable", help="Generate executable", action="store_true")

        opt('--dryrun',           help='dryrun without any changes ', action='store_true')
        opt('--include',          help='provide regex of tests to include with cmake', metavar="PATTERN")
        opt('--check',            help='check testfile py syntax before running', action='store_true')
        opt('--modified',         help='run only recently modified test', action='store_true')
        opt('--nocleanup',        help='do not cleanup built test', action='store_true')
        opt('--pytest',           help='run pytest before each test run', action='store_true')
        opt('--run',              help='run single test', metavar="TEST")
        opt('--stoponfail',       help='stop when first failure happens in ctest', action='store_true')
        opt('--run-errs',         help='run error/warning message tests', action='store_true')
        opt('--progress',         help='enable short progress output from ctest', action='store_true')

        opt("--debug",            help="set cmake debug on", action="store_true")
        opt("--generator",        help="specify a cmake build system generator", metavar="G")
        opt("--jobs",             help="build and run in parallel using N jobs", metavar="N", type=int)
        opt("--build-type",       help="set cmake build type (default: '%(default)s')", metavar="T", default="Debug")
        opt("--reset",            help="reset cmake build", action="store_true")
        opt("--conan",            help="install cmake dependencies with conan", action="store_true")
        opt("--spm",              help="install cmake dependencies with spm", action="store_true")
        opt("--extproject",       help="install cmake dependencies with externalproject", action="store_true")
        opt('--ccache',           help='enable ccache with cmake', action='store_true')
        opt('--target',           help='build only specified cmake targets', nargs="+", metavar="TARGET")

        opt("-c", "--cfg",        help="Add a cmake option '-D' prefix not needed", nargs='*', metavar="CMAKE_OPT")
        opt("--nowarnings",       help="Disable '-Wall' compilation warnings", action="store_true")        

        # make 'translate' the default subparser
        for arg in sys.argv[1:]:
            if arg in ('-h', '--help'):
                break
        else:
            if len(sys.argv) > 1 and sys.argv[1] not in ('analyze', 'translate', 'build', 'run', 'test'):
                sys.argv.insert(1, 'translate')

        args = parser.parse_args(args=bypassargs)
        # print(args)

        ss = cls(args)

        ss.log.info('*** SHED SKIN Python-to-C++ Compiler 0.9.8 ***')
        ss.log.info('Copyright 2005-2023 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)')
        ss.log.info('')

        if args.subcmd == 'analyze':
            ss.analyze()

        if args.subcmd == 'translate':
            ss.analyze()
            ss.translate()

        if args.subcmd == 'build':
            ss.analyze()
            ss.build()

        if args.subcmd == 'test':
            ss.test()

        if args.subcmd == 'run':
            ss.analyze()
            ss.build()
            ss.run()


def pkg_path():
    """used by cmake to get package path automatically"""
    cmake.pkg_path()


if __name__ == '__main__':
    Shedskin.commandline()
