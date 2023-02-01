#!/usr/bin/env python3
"""shedskin testrunner
"""
import argparse
import glob
import os
import subprocess
import time
import shutil
import sys
from pathlib import Path


WHITE = "\x1b[97;20m"
GREY = "\x1b[38;20m"
GREEN = "\x1b[32;20m"
CYAN = "\x1b[36;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
RED_BOLD = "\x1b[31;1m"
RESET = "\x1b[0m"



def shellcmd(cmd, *args, **kwds):
    print('-'*80)
    print(f'{WHITE}cmd{RESET}: {CYAN}{cmd}{RESET}')
    os.system(cmd.format(*args, **kwds))

def git_clone(repo, to_dir):
    shellcmd(f'git clone --depth=1 {repo} {to_dir}')

def cmake_generate(src_dir, build_dir, prefix, **options):
    opts = " ".join(f'-D{k}={v}' for k,v in options.items())
    shellcmd(f'cmake -S {src_dir} -B {build_dir} --install-prefix {prefix} {opts}')

def cmake_build(build_dir):
    shellcmd(f'cmake --build {build_dir}')

def cmake_install(build_dir):
    shellcmd(f'cmake --install {build_dir}')

def wget(url, output_dir):
    shellcmd(f'wget -P {output_dir} {url}')

def tar(archive, output_dir):
    shellcmd(f'tar -xvf {archive} -C {output_dir}')


class ShedskinPackageManager:
    """shedskin package manager (SPM) class"""

    def __init__(self, reset_on_run=False):
        self.reset_on_run = reset_on_run
        self.cwd = Path.cwd()
        self.build_dir = self.cwd / 'build'
        self.deps_dir = self.build_dir / 'deps'
        self.include_dir = self.deps_dir / 'include'
        self.lib_dir = self.deps_dir / 'lib'
        self.downloads_dir = self.deps_dir / 'downloads'
        self.src_dir = self.deps_dir / 'src'
        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.lib_suffix = '.lib' if sys.platform == 'win32' else '.a'

        if self.reset_on_run:
            shutil.rmtree(self.deps_dir)

    def targets_exist(self):
        libgc = self.lib_dir / f'libgc{self.lib_suffix}'
        libgccpp = self.lib_dir / f'libgccpp{self.lib_suffix}'
        libpcre = self.lib_dir / f'libgccpp{self.lib_suffix}'
        gc_h = self.include_dir / 'gc.h'
        pcre_h = self.include_dir / 'pcre.h'
 
        targets = [libgc, libgccpp, libpcre, gc_h, pcre_h]
        return all(t.exists() for t in targets)

    def install_all(self):
        if not self.targets_exist():
            self.install_bdwgc()
            self.install_pcre()
        else:
            print(f'{WHITE}SPM:{RESET} targets exist, no need to run.')

    def install_bdwgc(self):
        """download / build / install bdwgc"""
        bdwgc_repo = 'https://github.com/ivmai/bdwgc'
        bdwgc_src = self.src_dir / 'bdwgc'
        bdwgc_build = bdwgc_src / 'build'

        print("download / build / install bdwgc")
        git_clone(bdwgc_repo, bdwgc_src)
        bdwgc_build.mkdir(exist_ok=True)
        cmake_generate(bdwgc_src, bdwgc_build, prefix=self.deps_dir,
            BUILD_SHARED_LIBS=False,
            enable_cplusplus=True,
            build_cord=False,
            enable_docs=False,
            enable_gcj_support=False,
            enable_java_finalization=False,
        )
        cmake_build(bdwgc_build)
        cmake_install(bdwgc_build)

    def install_pcre(self):
        """download / build / install pcre"""
        pcre_url = 'https://sourceforge.net/projects/pcre/files/pcre/8.45/pcre-8.45.tar.gz'
        pcre_archive = self.downloads_dir / 'pcre-8.45.tar.gz'
        pcre_src = self.src_dir / 'pcre-8.45'
        pcre_build = pcre_src / 'build'

        print("download / build / install pcre")
        wget(pcre_url, self.downloads_dir)
        tar(pcre_archive, self.src_dir)
        # pcre_archive.unlink()
        pcre_build.mkdir(parents=True, exist_ok=True)
        cmake_generate(pcre_src, pcre_build, prefix=self.deps_dir,
            BUILD_SHARED_LIBS=False,
            PCRE_BUILD_PCREGREP=False,
            PCRE_BUILD_PCRECPP=True,
            PCRE_SUPPORT_LIBREADLINE=False,
            PCRE_SUPPORT_LIBEDIT=False,
            PCRE_SUPPORT_LIBZ=False,
            PCRE_SUPPORT_LIBBZ2=False,
            PCRE_BUILD_TESTS=False,
            PCRE_SHOW_REPORT=False,
        )
        cmake_build(pcre_build)
        cmake_install(pcre_build)



class TestRunner:
    """shedskin test runner"""

    def __init__(self, options=None):
        self.options = options
        self.build_dir = Path('build')
        self.tests = sorted(glob.glob("./test_*/test_*.py", recursive=True))

    def check_output(self, args, cwd='.', nosplit=False):
        """run command and return output"""
        if not nosplit:
            args = args.split()
        return subprocess.check_output(args,
            stderr=subprocess.STDOUT,
            cwd=cwd,
        )

    def run_step(self, cmd, cwd='.', nosplit=False):
        """run command step in specified directory"""
        try:
            self.check_output(cmd, cwd, nosplit)
        except subprocess.CalledProcessError as e:
            print(f"\n{RED}ERROR{RESET}: '{cmd}' returns {e.returncode}")
            print(e.output.decode('utf8'))
            raise

    def check(self, path):
        """check file for syntax errors"""
        with open(path) as f:
            src = f.read()
        compile(src, path, 'exec')

    def get_most_recent_test(self):
        """returns name of recently modified test"""
        max_mtime = 0
        most_recent_test = None
        for test in self.tests:
            mtime = os.stat(os.path.abspath(test)).st_mtime
            if mtime > max_mtime:
                max_mtime = mtime
                most_recent_test = test
        return most_recent_test

    def run_test(self, path):
        """run test in path"""
        path = Path(path)
        name = path.stem

        if path.is_dir():
            file_path = path / f'{name}.py'
            self.run_test(file_path)

        else:
            is_nested = bool(path.parent.stem)

            print(f'testing {name:30s}', end='')

            if self.options.check:
                self.check(path) # check python syntax

            if self.options.extension:
                translation_step = f'shedskin -e {path.name}'
                compiled_product = f'{name}.so'
            else:
                translation_step = f'shedskin {path.name}'
                compiled_product = name

            try:
                if is_nested:
                    self.run_step(translation_step, cwd=path.parent)
                    self.run_step('make', cwd=path.parent)
                    if self.options.extension:
                        self.run_step(["python3", "-c",
                            repr(f'from {name} import test_all; test_all()')],
                            cwd=path.parent, nosplit=True)
                    else:
                        self.run_step(f'./{name}', cwd=path.parent)
                else:
                    self.run_step(translation_step)
                    self.run_step('make')
                    if self.options.extension:
                        self.run_step(["python3", "-c",
                            repr(f'from {name} import test_all; test_all()')],
                            nosplit=True)
                    else:
                        self.run_step(f'./{name}')
            except:
                print(f"{RED}ERROR{RESET}: '{path}' terminated early")
                return

            print(f'{GREEN}OK{RESET}')

            files_to_clean = [f'{name}.cpp', f'{name}.hpp', compiled_product, 'Makefile']
            folders_to_clean = [f'{name}.so.dSYM']

            if self.options.nocleanup:
                files_to_clean.remove(compiled_product)
            for f in files_to_clean:
                if not is_nested:
                    os.remove(f)
                else:
                    os.remove(path.parent / f)

            for f in folders_to_clean:
                if not is_nested:
                    if os.path.exists(f):
                        shutil.rmtree(f)
                else:
                    if os.path.exists(path.parent / f):
                        shutil.rmtree(path.parent / f)

    def sequence(self, *cmds):
        """run test steps in sequence"""
        cmd = " && ".join(cmds)
        print(f'{CYAN}cmd{RESET}: {cmd}')
        if not self.options.dryrun:
            os.system(cmd)

    def run_tests(self):
        """build and run all tests"""
        st = time.time()

        if self.options.pytest:
            try:
                import pytest
                os.system('pytest')
            except ImportError:
                print('pytest not found')
            print()

        if self.options.cmake:
            rm_build = "rm -rf ./build"
            mkdir_build = "mkdir -p build"
            cd_build = "cd build"
            conan_install = "conan install .. --build=missing"
            spm_install = "python3 scripts/spm_install.py"
            cmake_config = "cmake .."
            cmake_build = "cmake --build ."
            cmake_test = "ctest --output-on-failure"

            # defaults
            cmake_config += " -DBUILD_EXECUTABLE=ON"


            if self.options.ccache:
                if shutil.which('ccache'):
                    cmake_config += " -DCMAKE_CXX_COMPILER_LAUNCHER=ccache"
                else:
                    print(f"\n{YELLOW}WARNING{RESET}: 'ccache' not found")

            # if self.options.cpm:
            #     cmake_config += " -DENABLE_CPM=ON"

            if self.options.debug:
                cmake_config += " -DDEBUG=ON"

            if self.options.external_project:
                cmake_config += " -DENABLE_EXTERNAL_PROJECT=ON"

            if self.options.spm:
                cmake_config += " -DENABLE_SPM=ON"

            if self.options.conan:
                cmake_config += " -DENABLE_CONAN=ON"

            if self.options.extension:
                cmake_config += " -DBUILD_EXTENSION=ON"

            if self.options.build_type:
                cmake_config += f" -DCMAKE_BUILD_TYPE={self.options.build_type}"

            if self.options.generator:
                cmake_config += f" -G{self.options.generator}"

            if self.options.include:
                cmake_test += f" --tests-regex {self.options.include}"

            if self.options.modified:
                most_recent_test = Path(self.get_most_recent_test()).stem
                cmake_build += f" --target {most_recent_test}"
                cmake_test += f" --tests-regex {most_recent_test}"                

            if self.options.parallel:
                cmake_build += f" --parallel {self.options.parallel}"
                cmake_test  += f" --parallel {self.options.parallel}"

            if self.options.progress:
                cmake_test += " --progress"

            if self.options.run:
                target_suffix = '-exe'
                if self.options.extension:
                    target_suffix = '-ext'
                cmake_build += f" --target {self.options.run}{target_suffix}"
                cmake_test += f" --tests-regex {self.options.run}"

            if self.options.stoponfail:
                cmake_test += " --stop-on-failure"

            if self.options.target:
                target_suffix = '-exe'
                for target in self.options.target:
                    cmake_build += f" --target {target}{target_suffix}"
                    cmake_test += f" --tests-regex {target}{target_suffix}"
            
            actions = [
                cmake_config,
                cmake_build,
                cmake_test,
            ]

            pre_actions = [cd_build]

            if self.build_dir.exists() and self.options.reset:
                pre_actions = [rm_build, mkdir_build] + pre_actions

            if not self.build_dir.exists():
                pre_actions = [mkdir_build] + pre_actions

            if len(pre_actions) > 1:
                if self.options.conan:
                    pre_actions.append(conan_install)

                if self.options.spm:
                    pre_actions.insert(2, spm_install)

            actions = pre_actions + actions

            self.sequence(*actions)
            if os.path.exists('Makefile'):
                os.remove('Makefile')
        else:
            print(f'Running {CYAN}shedskin{RESET} tests:')
            if self.options.modified: # run only most recently modified test
                most_recent_test = self.get_most_recent_test()
                self.run_test(most_recent_test)
            else:
                for test in self.tests:
                    self.run_test(test)
        et = time.time()
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(et - st))
        print(f'Total time: {YELLOW}{elapsed_time}{RESET}\n')

    def error_tests(self):
        """test error messages from tests in errs directory""" 
        failures = []
        os.chdir('errs')
        tests = sorted(os.path.basename(t) for t in glob.glob('[0-9][0-9].py'))
        for test in tests:
            print('*** test:', test)
            try:
                checks = []
                for line in open(test):                  
                    if line.startswith('#*'):
                        checks.append(line[1:].strip())
                cmd=f'{sys.executable} -m shedskin {test}'.split()
                output = subprocess.run(cmd, encoding='utf-8', 
                    capture_output=True, text=True).stdout
                assert not [l for l in output if 'Traceback' in l]
                for check in checks:
                    print(check)
                    assert [l for l in output.splitlines() if l.startswith(check)]
                print(f'*** {GREEN}SUCCESS{RESET}:', test)
            except AssertionError:
                print(f'*** {RED}FAILURE{RESET}:', test)
                failures.append(test)
        os.chdir('..')
        return failures

    @classmethod
    def commandline(cls):
        """command line interace to test runner"""
        parser = argparse.ArgumentParser(
            prog = 'runtests',
            description = 'runs shedskin tests')
        arg = opt = parser.add_argument
        opt('-b', '--build-type', help='set cmake build type', default='Debug')        
        opt('-c', '--cmake',      help='run tests using cmake', action='store_true')
        opt('-d', '--dryrun',     help='dryrun without any changes ', action='store_true')
        opt('-e', '--extension',  help='include python extension tests', action='store_true')
        opt('-g', '--generator',  help='specify a cmake build system generator')
        opt('-i', '--include',    help='provide regex of tests to include with cmake', metavar="PATTERN")        
        opt('-j', '--parallel',   help='build and run tests in parallel using N jobs', metavar="N", type=int)
        opt('-k', '--check',      help='check testfile py syntax before running', action='store_true')
        opt('-m', '--modified',   help='run only recently modified test', action='store_true')
        opt('-n', '--nocleanup',  help='do not cleanup built test', action='store_true')
        opt('-p', '--pytest',     help='run pytest before each test run', action='store_true')
        opt('-r', '--run',        help='run single test', metavar="TEST")
        opt('-s', '--stoponfail', help='stop when first failure happens in ctest', action='store_true')
        opt('-t', '--target',     help='build only specified targets', nargs="+")
        opt('-x', '--run-errs',   help='run error/warning message tests', action='store_true')
        opt('--ccache',           help='enable ccache with cmake', action='store_true')
        opt('--progress',         help='enable short progress output from ctest', action='store_true')
        opt('--reset',            help='reset cmake build', action='store_true')
        opt('--conan',            help='install dependencies with conan', action='store_true')
        opt('--spm',              help='install dependencies with spm', action='store_true')
        opt('--external-project', help='install dependencies with externalproject', action='store_true')
        opt('--debug',            help='set cmake debug on', action='store_true')
        
        args = parser.parse_args()
        runner = cls(args)
        if args.cmake:
            runner.run_tests()
        else:
            if args.run:
                runner.run_test(args.run)
            elif args.run_errs:
                failures = runner.error_tests()
                if not failures:
                    print(f'==> {GREEN}NO FAILURES, yay!{RESET}')
                else:
                    print(f'==> {RED}TESTS FAILED:{RESET}', len(failures))
                    print(failures)
                    sys.exit()

if __name__ == '__main__':
    TestRunner.commandline()

