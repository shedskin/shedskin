# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2025 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.__init__: main entrypoint

Contains the `Shedskin` class, the main entrypoint to shedskin, a Restricted-Python-to-C++
Compiler, providing both a programmatic class-based interface and command-line interface
to the compiler.
"""

import argparse
import logging
import os
import os.path
import pathlib
import platform
import subprocess
import sys
import time
from typing import List, Optional

from . import cmake, config, cpp, error, graph, infer, log, makefile, stats


class Shedskin:
    """Main shedskin frontend class"""

    def __init__(self, options: argparse.Namespace):
        self.configure_log()
        self.gx = self.configure(options)
        self.gx.options = options
        if "name" in options:
            self.module_name = self.get_name(options.name)

    def configure_log(self) -> None:
        """Configure logging for shedskin"""
        # silent -> WARNING only, debug -> DEBUG, default -> INFO
        console = logging.StreamHandler(stream=sys.stdout)
        console.setFormatter(log.ShedskinFormatter())
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(console)
        self.log.setLevel(logging.INFO)
        # debug=3 -> IFA (iterative flow analysis) logging enabled.
        self.ifa_log = logging.getLogger("infer.ifa")
        self.ifa_log.addHandler(console)
        self.ifa_log.setLevel(logging.INFO)

    def get_name(self, module_path: str) -> str:
        """Returns name of module to be translated.

        Sets source_root (for module resolution) and module_path configuration.

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

        # Resolve to absolute path
        path = path.resolve()

        if not path.name.endswith(".py"):
            path = path.with_suffix(".py")
        if not path.is_file():
            self.log.error("no such file: '%s'", path)
            sys.exit(1)

        # Set source_root for module resolution (replaces os.chdir approach)
        self.gx.source_root = path.parent
        self.gx.module_path = path

        return path.stem

    def configure(self, args: argparse.Namespace) -> "config.GlobalInfo":
        """Configure global information for shedskin"""
        # print(args)
        gx = config.GlobalInfo(args)

        if args.subcmd in ["build", "run", "runtests"]:
            # ensure cmake is available and installed.
            cmake.check_cmake_availability()

        if args.subcmd in [
            "translate",
            "build",
            "run",
        ]:  # i.e. not relevant for 'runtests'
            if args.nobounds:
                gx.bounds_checking = False

            if args.extmod:
                gx.executable_product = False
                gx.pyextension_product = True

            if args.debug:
                self.log.setLevel(logging.DEBUG)
                if args.debug == 3:
                    self.ifa_log.setLevel(logging.DEBUG)

            if args.int32:
                gx.int32 = True

            if args.int64:
                gx.int64 = True

            if args.int128:
                if platform.system() == "Windows":
                    self.log.error("--int128 not supported on windows")
                    sys.exit(1)
                gx.int128 = True

            if args.float32:
                gx.float32 = True

            if args.float64:
                gx.float64 = True

            if args.nogc:
                gx.nogc = True

            if args.nowrap:
                gx.wrap_around_check = False

            #            if args.random:
            #                gx.fast_random = True

            if args.noassert:
                gx.assertions = False

            if args.subcmd == "translate":
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
        if (major, minor) not in [
            (3, 8),
            (3, 9),
            (3, 10),
            (3, 11),
            (3, 12),
            (3, 13),
            (3, 14),
        ]:
            self.log.error("Shed Skin is not compatible with this version of Python")
            sys.exit(1)

        return gx

    def pre_analyze(self) -> None:
        """Parse the main module"""
        self.gx.main_module = graph.parse_module(self.module_name, self.gx)

    def analyze(self) -> None:
        """Analyze the main module"""
        self.pre_analyze()
        t0 = time.time()
        infer.analyze(self.gx, self.module_name)
        cpp.generate_code(self.gx, analyze=True)
        error.print_errors()
        prebuild_secs = time.time() - t0
        if self.gx.options.collect_stats:
            stats_mgr = stats.ShedskinStatsManager(self.gx)
            stats_mgr.insert_pymodule(prebuild_secs)
            stats_mgr.print_current_stats(prebuild_secs)
        else:
            self.log.info(f"\n[prebuild time: {prebuild_secs:.2f} seconds]")

    def print_times(
        self, prebuild_secs: float, build_secs: float = 0.0, run_secs: float = 0.0
    ) -> None:
        """Print the times"""
        _out = [f"prebuild time: {prebuild_secs:.2f} secs"]
        if build_secs > 0:
            _out.append(f"build time: {build_secs:.2f} secs")
        if run_secs > 0:
            _out.append(f"run time: {run_secs:.2f} secs")
        self.log.info("\n[" + ", ".join(_out) + "]\n")

    def translate(self) -> None:
        """Translate the main module"""
        self.pre_analyze()
        t0 = time.time()
        infer.analyze(self.gx, self.module_name)
        cpp.generate_code(self.gx)
        error.print_errors()
        prebuild_secs = time.time() - t0
        build_secs = 0.0
        run_secs = 0.0
        if self.gx.options.compile or self.gx.options.run:
            builder = makefile.ShedskinBuilder(self.gx)
            builder.build(self.gx.options.dry_run)
            build_secs = time.time() - t0 - prebuild_secs
            if self.gx.options.run:
                builder.run_executable()
                run_secs = time.time() - t0 - build_secs
        else:
            if not self.gx.nomakefile:
                generator = makefile.ShedskinMakefileGenerator(self.gx)
                generator.generate()
        if self.gx.options.collect_stats:
            stats_mgr = stats.ShedskinStatsManager(self.gx)
            stats_mgr.insert_pymodule(prebuild_secs, build_secs, run_secs)
            stats_mgr.print_current_stats(prebuild_secs, build_secs, run_secs)
            # stats_mgr.print_all_stats()
        else:
            self.print_times(prebuild_secs, build_secs, run_secs)

    def build(self) -> None:
        """Build the main module"""
        self.pre_analyze()
        cmake.generate_cmakefile(self.gx)
        builder = cmake.CMakeBuilder(self.gx)
        builder.build()

    def runtests(self) -> None:
        """Run tests"""
        if self.gx.options.run_errs:
            testrunner = cmake.TestRunner(self.gx)
            testrunner.run_error_tests()
        else:
            testrunner = cmake.TestRunner(self.gx)
            testrunner.run_tests()

    def run(self) -> None:
        """Run the main module"""
        p = pathlib.Path(self.gx.options.name).resolve()

        # Executable is always in gx.cwd/build/ for all cases
        if p.is_relative_to(self.gx.cwd):
            rel_path = p.relative_to(self.gx.cwd)
            if len(rel_path.parts) == 1:
                # Source in cwd
                executable = self.gx.cwd / "build" / p.stem
            else:
                # Source in subdirectory
                executable = (
                    self.gx.cwd / "build" / rel_path.parent.name / rel_path.parent.name
                )
        else:
            # External source - executable is in cwd/build/
            executable = self.gx.cwd / "build" / p.stem
        subprocess.run([str(executable)], check=True)

    @classmethod
    def _create_shared_parsers(cls) -> dict:
        """Create shared argument parsers for reuse across subcommands."""
        parsers = {}

        # Stats options (used by all subcommands)
        parsers["stats"] = argparse.ArgumentParser(add_help=False)
        parsers["stats"].add_argument(
            "--collect-stats",
            help="Collect and report shedskin stats",
            action="store_true",
        )

        # Type options (int32/64/128, float32/64)
        parsers["types"] = argparse.ArgumentParser(add_help=False)
        grp = parsers["types"].add_argument
        grp("--int32", help="Use 32-bit integers", action="store_true")
        grp("--int64", help="Use 64-bit integers", action="store_true")
        grp("--int128", help="Use 128-bit integers", action="store_true")
        grp("--float32", help="Use 32-bit floats", action="store_true")
        grp("--float64", help="Use 64-bit floats", action="store_true")

        # Disable options (noassert, nobounds, nogc, nowrap)
        parsers["disable"] = argparse.ArgumentParser(add_help=False)
        grp = parsers["disable"].add_argument
        grp("--noassert", help="Disable assert statements", action="store_true")
        grp("-b", "--nobounds", help="Disable bounds checking", action="store_true")
        grp("--nogc", help="Disable garbage collection", action="store_true")
        grp("-w", "--nowrap", help="Disable wrap-around checking", action="store_true")

        # Compiler options (debug, extmod, dirs, output, etc.)
        parsers["compiler"] = argparse.ArgumentParser(add_help=False)
        grp = parsers["compiler"].add_argument
        grp("-d", "--debug", help="Set debug level", type=int)
        grp("-e", "--extmod", help="Generate extension module", action="store_true")
        grp("-I", "--include-dirs", help="Add an include directory", action="append")
        grp("-L", "--link-dirs", help="Add a link library directory", action="append")
        grp("-l", "--link-libs", help="Add a link library", action="append")
        grp("-X", "--extra-lib", help="Add an extra builtins library directory")
        grp("-o", "--outputdir", help="Specify output directory for generated files")
        grp(
            "-s",
            "--silent",
            help="Silent mode, only show warnings",
            action="store_true",
        )
        grp(
            "-t",
            "--traceback",
            help="Print traceback for uncaught exceptions",
            action="store_true",
        )
        grp("-x", "--executable", help="Generate executable", action="store_true")

        # CMake options (generator, jobs, build-type, etc.)
        parsers["cmake"] = argparse.ArgumentParser(add_help=False)
        grp = parsers["cmake"].add_argument
        grp("--generator", help="Specify a cmake build system generator", metavar="G")
        grp(
            "--jobs",
            help="Build and run in parallel using N jobs",
            metavar="N",
            type=int,
        )
        grp(
            "--build-type",
            help="Set cmake build type (default: '%(default)s')",
            metavar="T",
            default="Debug",
        )
        grp("--test", help="Run ctest", action="store_true")
        grp("--reset", help="Reset cmake build", action="store_true")
        grp("--spm", help="Install cmake dependencies with spm", action="store_true")
        grp(
            "--fetchcontent",
            help="Install cmake dependencies with fetchcontent",
            action="store_true",
        )
        grp(
            "--local-deps",
            help="Build dependencies from bundled ext/ sources",
            action="store_true",
        )
        grp("--ccache", help="Enable ccache with cmake", action="store_true")
        grp(
            "--target",
            help="Build only specified cmake targets",
            nargs="+",
            metavar="TARGET",
        )
        grp(
            "--nowarnings",
            help="Disable '-Wall' compilation warnings",
            action="store_true",
        )

        return parsers

    @classmethod
    def commandline(cls, bypassargs: Optional[List[str]] = None) -> None:
        """Command line API."""
        sys.setrecursionlimit(100000)
        # Enable ANSI color output on Windows by invoking cmd
        if platform.system() == "Windows":
            subprocess.run(["cmd", "/c", ""], shell=False, check=False)

        # Create shared argument parsers
        shared = cls._create_shared_parsers()

        # --- command-line options
        parser = argparse.ArgumentParser(
            prog="shedskin",
            description="Restricted-Python-to-C++ Compiler",
        )

        subparsers = parser.add_subparsers(
            title="subcommands",
            dest="subcmd",
        )

        # ---------------------------------------------------------------------
        # analyze subcommand
        parser_analyze = subparsers.add_parser(
            "analyze",
            help="Analyze and validate python module",
            parents=[shared["stats"]],
        )
        parser_analyze.add_argument("name", help="Python file or module to analyze")

        # ---------------------------------------------------------------------
        # translate subcommand
        parser_translate = subparsers.add_parser(
            "translate",
            help="Translate python module to cpp (Makefile)",
            parents=[
                shared["stats"],
                shared["types"],
                shared["disable"],
                shared["compiler"],
            ],
        )
        opt = parser_translate.add_argument
        opt("name", help="Python file or module to compile")
        opt(
            "-c",
            "--compile",
            help="Directly compile translated code",
            action="store_true",
        )
        opt("-F", "--flags", help="Provide alternate Makefile flags")
        opt(
            "-S",
            "--static-libs",
            help="Use static compilation if possible",
            action="store_true",
        )
        opt("-m", "--makefile", help="Specify alternate Makefile name")
        opt("-r", "--run", help="Build and run executable", action="store_true")
        opt(
            "-D",
            "--dry-run",
            help="Only print compilation command",
            action="store_true",
        )
        opt("--nomakefile", help="Disable makefile generation", action="store_true")
        opt(
            "--nocleanup",
            help="Disable cleanup of generated files",
            action="store_true",
        )
        opt(
            "--local-deps",
            help="Use dependencies from bundled ext/ sources",
            action="store_true",
        )

        # ---------------------------------------------------------------------
        # build subcommand
        parser_build = subparsers.add_parser(
            "build",
            help="Translate and build python module (CMake)",
            parents=[
                shared["stats"],
                shared["types"],
                shared["disable"],
                shared["compiler"],
                shared["cmake"],
            ],
        )
        parser_build.add_argument("name", help="Python file or module to compile")

        # ---------------------------------------------------------------------
        # run subcommand
        parser_run = subparsers.add_parser(
            "run",
            help="Translate, build and run module (CMake)",
            parents=[
                shared["stats"],
                shared["types"],
                shared["disable"],
                shared["compiler"],
                shared["cmake"],
            ],
        )
        parser_run.add_argument("name", help="Python file or module to run")

        # ---------------------------------------------------------------------
        # runtests subcommand
        parser_test = subparsers.add_parser(
            "runtests",
            help="Run tests",
            parents=[shared["stats"], shared["cmake"]],
        )
        opt = parser_test.add_argument
        opt("-e", "--extmod", help="Generate extension module", action="store_true")
        opt("-x", "--executable", help="Generate executable", action="store_true")
        opt("--disable-exts", help="Disable building extensions", action="store_true")
        opt("--disable-exes", help="Disable building executables", action="store_true")
        opt("--dryrun", help="Dryrun without any changes", action="store_true")
        opt(
            "--include",
            help="Provide regex of tests to include with cmake",
            metavar="PATTERN",
        )
        opt(
            "--check",
            help="Check testfile py syntax before running",
            action="store_true",
        )
        opt("--modified", help="Run only recently modified test", action="store_true")
        opt("--nocleanup", help="Do not cleanup built test", action="store_true")
        opt("--pytest", help="Run pytest before each test run", action="store_true")
        opt("--run", help="Run single test", metavar="TEST")
        opt(
            "--stoponfail",
            help="Stop when first failure happens in ctest",
            action="store_true",
        )
        opt("--run-errs", help="Run error/warning message tests", action="store_true")
        opt(
            "--progress",
            help="Enable short progress output from ctest",
            action="store_true",
        )
        opt("--debug", help="Set cmake debug on", action="store_true")
        opt(
            "-c",
            "--cfg",
            help="Add a cmake option '-D' prefix not needed",
            nargs="*",
            metavar="CMAKE_OPT",
        )

        # ---------------------------------------------------------------------
        # parse command line

        # make 'translate' the default subparser
        for _arg in sys.argv[1:]:
            if _arg in ("-h", "--help"):
                break
        else:
            if len(sys.argv) > 1 and sys.argv[1] not in (
                "analyze",
                "translate",
                "build",
                "run",
                "runtests",
            ):
                sys.argv.insert(1, "translate")

        args = parser.parse_args(args=bypassargs)

        if platform.system() == "Windows" and args.subcmd in ("build", "run"):
            args.build_type = "Release"  # Debug doesn't work in CI, possibly because of missing debug symbols

        # Make --local-deps the default unless another dep manager is specified
        if args.subcmd in ("build", "run", "runtests"):
            if not args.spm and not args.fetchcontent and not args.local_deps:
                args.local_deps = True

        ss = cls(args)

        ss.log.info("*** SHED SKIN Python-to-C++ Compiler 0.9.12 ***")
        ss.log.info(
            "Copyright 2005-2026 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)"
        )
        ss.log.info("")

        if args.subcmd == "analyze":
            ss.analyze()

        if args.subcmd == "translate":
            ss.translate()

        if args.subcmd == "build":
            ss.build()

        if args.subcmd == "runtests":
            ss.runtests()

        if args.subcmd == "run":
            ss.build()
            ss.run()


def pkg_path() -> None:
    """used by cmake to get package path automatically"""
    cmake.pkg_path()


if __name__ == "__main__":
    Shedskin.commandline()
