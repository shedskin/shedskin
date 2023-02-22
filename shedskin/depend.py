
import os
import textwrap
import shutil
import sys

from .utils import WHITE, CYAN, RESET

class ConanDependency:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def __str__(self):
        return f"{self.name}/{self.version}"


class ConanBDWGC(ConanDependency):
    def __init__(
        self,
        name="bdwgc",
        version="8.2.2",
        cplusplus=True,
        cord=False,
        gcj_support=False,
        java_finalization=False,
        shared=False,
    ):
        self.name = name
        self.version = version
        self.cplusplus = cplusplus
        self.cord = cord
        self.gcj_support = gcj_support
        self.java_finalization = java_finalization
        self.shared = shared


class ConanPCRE(ConanDependency):
    def __init__(
        self,
        name="pcre",
        version="8.45",
        build_pcrecpp=True,
        build_pcregrep=False,
        shared=False,
        with_bzip2=False,
        with_zlib=False,
    ):
        self.name = name
        self.version = version
        self.build_pcrecpp = build_pcrecpp
        self.build_pcregrep = build_pcregrep
        self.shared = shared
        self.with_bzip2 = with_bzip2
        self.with_zlib = with_zlib


class ConanDependencyManager:
    def __init__(self, source_dir):
        self.source_dir = source_dir
        self.build_dir = self.source_dir / "build"
        self.bdwgc = ConanBDWGC()
        self.pcre = ConanPCRE()

    def generate_conanfile(self):
        bdwgc = self.bdwgc
        pcre = self.pcre
        content = textwrap.dedent(
            f"""
        [requires]
        {bdwgc}
        {pcre}

        [generators]
        cmake_find_package
        cmake_paths

        [options]
        bdwgc:cplusplus={bdwgc.cplusplus}
        bdwgc:cord={bdwgc.cord}
        bdwgc:gcj_support={bdwgc.gcj_support}
        bdwgc:java_finalization={bdwgc.java_finalization}
        bdwgc:shared={bdwgc.shared}
        pcre:build_pcrecpp={pcre.build_pcrecpp}
        pcre:build_pcregrep={pcre.build_pcregrep}
        pcre:shared={pcre.shared}
        pcre:with_bzip2={pcre.with_bzip2}
        pcre:with_zlib={pcre.with_zlib}
        """
        )
        conanfile = self.source_dir / "conanfile.txt"
        conanfile.write_text(content)
        # with open("conanfile.txt", "w") as cfile:
        #     cfile.write(content)

    def install(self):
        # os.system("cd build && conan install .. --build=missing")
        os.system(f"cd {self.build_dir} && conan install .. --build=missing")



def shellcmd(cmd, *args, **kwds):
    print("-" * 80)
    print(f"{WHITE}cmd{RESET}: {CYAN}{cmd}{RESET}")
    os.system(cmd.format(*args, **kwds))


def git_clone(repo, to_dir):
    shellcmd(f"git clone --depth=1 {repo} {to_dir}")


def cmake_generate(src_dir, build_dir, prefix, **options):
    opts = " ".join(f"-D{k}={v}" for k, v in options.items())
    shellcmd(f"cmake -S {src_dir} -B {build_dir} --install-prefix {prefix} {opts}")


def cmake_build(build_dir):
    shellcmd(f"cmake --build {build_dir}")


def cmake_install(build_dir):
    shellcmd(f"cmake --install {build_dir}")


def wget(url, output_dir):
    shellcmd(f"wget -P {output_dir} {url}")


def tar(archive, output_dir):
    shellcmd(f"tar -xvf {archive} -C {output_dir}")


class ShedskinDependencyManager:
    """shedskin local dependency manager (SPM) class"""

    def __init__(self, source_dir, reset_on_run=False):
        self.reset_on_run = reset_on_run
        self.source_dir = source_dir
        self.build_dir = self.source_dir / "build"
        self.deps_dir = self.build_dir / "deps"
        self.include_dir = self.deps_dir / "include"
        self.lib_dir = self.deps_dir / "lib"
        self.downloads_dir = self.deps_dir / "downloads"
        self.src_dir = self.deps_dir / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.lib_suffix = ".lib" if sys.platform == "win32" else ".a"

        if self.reset_on_run:
            shutil.rmtree(self.deps_dir)

    def targets_exist(self):
        libgc = self.lib_dir / f"libgc{self.lib_suffix}"
        libgccpp = self.lib_dir / f"libgccpp{self.lib_suffix}"
        libpcre = self.lib_dir / f"libgccpp{self.lib_suffix}"
        gc_h = self.include_dir / "gc.h"
        pcre_h = self.include_dir / "pcre.h"

        targets = [libgc, libgccpp, libpcre, gc_h, pcre_h]
        return all(t.exists() for t in targets)

    def install_all(self):
        if not self.targets_exist():
            self.install_bdwgc()
            self.install_pcre()
        else:
            print(f"{WHITE}SPM:{RESET} targets exist, no need to run.")

    def install_bdwgc(self):
        """download / build / install bdwgc"""
        bdwgc_repo = "https://github.com/ivmai/bdwgc"
        bdwgc_src = self.src_dir / "bdwgc"
        bdwgc_build = bdwgc_src / "build"

        print("download / build / install bdwgc")
        git_clone(bdwgc_repo, bdwgc_src)
        bdwgc_build.mkdir(exist_ok=True)
        cmake_generate(
            bdwgc_src,
            bdwgc_build,
            prefix=self.deps_dir,
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
        pcre_url = (
            "https://sourceforge.net/projects/pcre/files/pcre/8.45/pcre-8.45.tar.gz"
        )
        pcre_archive = self.downloads_dir / "pcre-8.45.tar.gz"
        pcre_src = self.src_dir / "pcre-8.45"
        pcre_build = pcre_src / "build"

        print("download / build / install pcre")
        wget(pcre_url, self.downloads_dir)
        tar(pcre_archive, self.src_dir)
        # pcre_archive.unlink()
        pcre_build.mkdir(parents=True, exist_ok=True)
        cmake_generate(
            pcre_src,
            pcre_build,
            prefix=self.deps_dir,
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
