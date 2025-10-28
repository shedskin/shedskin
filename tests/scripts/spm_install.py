
"""
shedskin
    build
        deps (prefix)
            include
            lib
            downloads
            src
                bdwgc
                    build
                pcre2
                    build
"""
import os
import shutil
import sys
from pathlib import Path



WHITE = "\x1b[97;20m"
CYAN = "\x1b[36;20m"
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
        libpcre2 = self.lib_dir / f'libpcre2-8{self.lib_suffix}'
        gc_h = self.include_dir / 'gc.h'
        pcre2_h = self.include_dir / 'pcre2.h'
 
        targets = [libgc, libgccpp, libpcre2, gc_h, pcre2_h]
        return all(t.exists() for t in targets)

    def install_all(self):
        if not self.targets_exist():
            self.install_bdwgc()
            self.install_pcre2()
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

    def install_pcre2(self):
        """download / build / install pcre2"""
        pcre2_url = 'https://github.com/PCRE2Project/pcre2/releases/download/pcre2-10.44/pcre2-10.44.tar.gz'
        pcre2_archive = self.downloads_dir / 'pcre2-10.44.tar.gz'
        pcre2_src = self.src_dir / 'pcre2-10.44'
        pcre2_build = pcre2_src / 'build'

        print("download / build / install pcre2")
        wget(pcre2_url, self.downloads_dir)
        tar(pcre2_archive, self.src_dir)
        # pcre2_archive.unlink()
        pcre2_build.mkdir(parents=True, exist_ok=True)
        cmake_generate(pcre2_src, pcre2_build, prefix=self.deps_dir,
            BUILD_SHARED_LIBS=False,
            PCRE2_BUILD_PCRE2GREP=False,
            PCRE2_SUPPORT_LIBREADLINE=False,
            PCRE2_SUPPORT_LIBEDIT=False,
            PCRE2_SUPPORT_LIBZ=False,
            PCRE2_SUPPORT_LIBBZ2=False,
            PCRE2_BUILD_TESTS=False,
            PCRE2_SHOW_REPORT=False,
        )
        cmake_build(pcre2_build)
        cmake_install(pcre2_build)


if __name__ == '__main__':
    spm = ShedskinPackageManager()
    spm.install_all()

