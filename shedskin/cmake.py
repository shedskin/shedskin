# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2025 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.cmake: CMake generator and builder for Shedskin

This module provides functionality for generating CMake build files and managing
the build process for Shedskin-compiled projects. Key components include:

- CMake file generation
- Dependency management (`LocalDeps`, `SPM`, `FetchContent`)
- Build configuration and execution
- Test running utilities

Main classes:
- `LocalDependencyManager`: Local dependency manager using bundled ext/ sources (default)
- `ShedskinDependencyManager`: Legacy dependency manager (SPM)
- `CMakeBuilder`: Handles CMake configuration, building, and testing
- `TestRunner`: Specialized CMakeBuilder for running tests

Key functions:
- `generate_cmakefile`: Creates CMakeLists.txt for Shedskin projects
- `add_shedskin_product`: Generates CMake function call for Shedskin targets

The module also includes utilities for path handling, caching, and system-specific operations.
"""

import glob
import logging
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import textwrap
import time
import zipfile
from typing import Callable, List, Optional, Union

from . import config
from .utils import CYAN, GREEN, RED, RESET, WHITE

# type alias
Pathlike = Union[pathlib.Path, str]


def pkg_path() -> None:
    """Used by cmake to get the shedskin package path automatically"""
    sys.stdout.write(str(config.get_pkg_path()))


def user_cache_dir() -> None:
    """Used by CMakeLists.txt execute process"""
    sys.stdout.write(str(config.get_user_cache_dir()))


def build_local_deps() -> None:
    """CLI entry point for building local dependencies from ext/ sources.

    Usage: python -m shedskin.cmake build-local-deps [--force] [--status]
    """
    import argparse as ap

    parser = ap.ArgumentParser(
        description="Build shedskin dependencies from bundled ext/ sources"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force rebuild even if targets exist"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show status only, don't build"
    )
    parser.add_argument(
        "--reset", action="store_true", help="Reset cache before building"
    )
    args = parser.parse_args()

    # Import here to avoid circular imports at module load
    ldm = LocalDependencyManager(reset_on_run=args.reset)

    if args.status:
        status = ldm.status()
        print("\nLocal Dependencies Status:")
        print("-" * 40)
        for key, value in status.items():
            print(f"  {key}: {value}")
        print()
        return

    ldm.install_all(force=args.force)
    print(f"\nDependencies installed to: {ldm.deps_dir}")


class ShedskinDependencyManager:
    """Shedskin local dependency manager (SPM) class"""

    def __init__(self, source_dir: Pathlike, reset_on_run: bool = False):
        self.reset_on_run = reset_on_run
        self.source_dir = pathlib.Path(source_dir)
        self.build_dir = self.source_dir / "build"
        # self.deps_dir = self.build_dir / "deps"
        self.deps_dir = config.get_user_cache_dir()
        # self.deps_dir = pathlib.Path.home() / ".cache" / "shedskin"
        self.include_dir = self.deps_dir / "include"
        self.lib_dir = self.deps_dir / "lib"
        self.downloads_dir = self.deps_dir / "downloads"
        self.src_dir = self.deps_dir / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.lib_suffix = ".lib" if sys.platform == "win32" else ".a"

        if self.reset_on_run:
            shutil.rmtree(self.deps_dir)

    def shellcmd(self, cmd: str) -> None:
        """Run a shell command"""
        print("-" * 80)
        print(f"{WHITE}cmd{RESET}: {CYAN}{cmd}{RESET}")
        subprocess.run(cmd, shell=True, check=True)

    def git_clone(
        self, repo: str, to_dir: Pathlike, branch: Optional[str] = None
    ) -> None:
        """Retrieve a git clone of a repository"""
        if branch:
            self.shellcmd(f"git clone -b {branch} --depth=1 {repo} {to_dir}")
        else:
            self.shellcmd(f"git clone --depth=1 {repo} {to_dir}")

    def cmake_generate(
        self, src_dir: Pathlike, build_dir: Pathlike, prefix: Pathlike, **options: bool
    ) -> None:
        """Activate cmake configuration / generation stage"""
        opts = " ".join(f"-D{k}={v}" for k, v in options.items())
        self.shellcmd(
            f"cmake -S {src_dir} -B {build_dir} --install-prefix {prefix} {opts}"
        )

    def cmake_build(self, build_dir: Pathlike, release: bool = True) -> None:
        """Activate cmake build stage"""
        if release:
            build_type = "Release"
        else:
            build_type = "Debug"
        self.shellcmd(f"cmake --build {build_dir} --config {build_type}")

    def cmake_install(self, build_dir: Pathlike) -> None:
        """Activate cmake install stage"""
        self.shellcmd(f"cmake --install {build_dir}")

    def wget(self, url: str, output_dir: Pathlike) -> None:
        """Download url resource using wget"""
        self.shellcmd(f"wget -P {output_dir} {url}")

    def tar(self, archive: Pathlike, output_dir: Pathlike) -> None:
        """Uncompress tar archive"""
        self.shellcmd(f"tar -xvf {archive} -C {output_dir}")

    def targets_exist(self) -> bool:
        """Check if required targets exist"""
        libgc = self.lib_dir / f"libgc{self.lib_suffix}"
        libgccpp = self.lib_dir / f"libgccpp{self.lib_suffix}"
        libpcre2 = self.lib_dir / f"libpcre2-8{self.lib_suffix}"
        gc_h = self.include_dir / "gc.h"
        pcre2_h = self.include_dir / "pcre2.h"

        targets = [libgc, libgccpp, libpcre2, gc_h, pcre2_h]
        return all(t.exists() for t in targets)

    def install_all(self) -> None:
        """Install all dependencies"""
        if not self.targets_exist():
            self.install_bdwgc()
            self.install_pcre2()
        else:
            print(f"{WHITE}SPM:{RESET} targets exist, no need to run.")

    # def install_libatomics_ops(self):
    #     """install libatomic_ops, a bdwgc dependency on windws"""
    #     libatomic_repo = "https://github.com/ivmai/libatomic_ops.git"
    #     libatomic_src = self.src_dir / "libatomic_ops"
    #     libatomic_build = libatomic_src / "build"
    #     print("download / build / install libatomic_ops")
    #     self.git_clone(libatomic_repo, libatomic_src, branch="v7.8.2")
    #     libatomic_build.mkdir(exist_ok=True)
    #     self.cmake_generate(
    #         libatomic_src,
    #         libatomic_build,
    #         enable_atomic_intrinsics=False,
    #         prefix=self.deps_dir,
    #         BUILD_SHARED_LIBS=False,
    #     )
    #     self.cmake_build(libatomic_build)
    #     self.cmake_install(libatomic_build)

    def install_bdwgc(self) -> None:
        """Download / build / install bdwgc"""
        # if platform.system() == "Windows":
        #     self.install_libatomics_ops()
        bdwgc_repo = "https://github.com/ivmai/bdwgc"
        bdwgc_src = self.src_dir / "bdwgc"
        bdwgc_build = bdwgc_src / "build"

        print("download / build / install bdwgc")
        self.git_clone(bdwgc_repo, bdwgc_src, branch="v8.2.6")
        if platform.system() == "Windows":
            # windows needs libatomic_ops
            libatomic_repo = "https://github.com/ivmai/libatomic_ops.git"
            libatomic_src = bdwgc_src / "libatomic_ops"
            self.git_clone(libatomic_repo, libatomic_src, branch="v7.8.2")
        bdwgc_build.mkdir(exist_ok=True)
        self.cmake_generate(
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
        self.cmake_build(bdwgc_build)
        self.cmake_install(bdwgc_build)

    # def install_pcre(self):
    #         """download / build / install pcre"""
    #         pcre_url = (
    #             "https://sourceforge.net/projects/pcre/files/pcre/8.45/pcre-8.45.tar.gz"
    #         )
    #         pcre_archive = self.downloads_dir / "pcre-8.45.tar.gz"
    #         pcre_src = self.src_dir / "pcre-8.45"
    #         pcre_build = pcre_src / "build"

    #         print("download / build / install pcre")
    #         self.wget(pcre_url, self.downloads_dir)
    #         self.tar(pcre_archive, self.src_dir)
    #         # pcre_archive.unlink()
    #         pcre_build.mkdir(parents=True, exist_ok=True)
    #         self.cmake_generate(
    #             pcre_src,
    #             pcre_build,
    #             prefix=self.deps_dir,
    #             BUILD_SHARED_LIBS=False,
    #             PCRE_BUILD_PCREGREP=False,
    #             PCRE_BUILD_PCRECPP=True,
    #             PCRE_SUPPORT_LIBREADLINE=False,
    #             PCRE_SUPPORT_LIBEDIT=False,
    #             PCRE_SUPPORT_LIBZ=False,
    #             PCRE_SUPPORT_LIBBZ2=False,
    #             PCRE_BUILD_TESTS=False,
    #             PCRE_SHOW_REPORT=False,
    #         )
    #         self.cmake_build(pcre_build)
    #         self.cmake_install(pcre_build)

    def install_pcre2(self) -> None:
        """Download / build / install pcre2"""
        pcre2_repo = "https://github.com/PCRE2Project/pcre2.git"
        pcre2_src = self.src_dir / "pcre2"
        pcre2_build = pcre2_src / "build"
        print("download / build / install pcre2")
        self.git_clone(pcre2_repo, pcre2_src)
        pcre2_build.mkdir(parents=True, exist_ok=True)
        self.cmake_generate(
            pcre2_src,
            pcre2_build,
            prefix=self.deps_dir,
            BUILD_SHARED_LIBS=False,
            PCRE2_BUILD_PCRE2GREP=False,
            PCRE2_SUPPORT_LIBREADLINE=False,
            PCRE2_SUPPORT_LIBEDIT=False,
            PCRE2_SUPPORT_LIBZ=False,
            PCRE2_SUPPORT_LIBBZ2=False,
            PCRE2_BUILD_TESTS=False,
            PCRE2_SHOW_REPORT=False,
        )
        self.cmake_build(pcre2_build)
        self.cmake_install(pcre2_build)


class LocalDependencyManager:
    """Dependency manager that builds from embedded ext/ zip archives.

    This manager uses compressed zip archives bundled in shedskin/ext/
    (bdwgc.zip, pcre2.zip). On first use, archives are extracted to the
    platform-specific cache directory and built as static libraries.

    Supported platforms: Linux, macOS, Windows

    Cache structure:
        ~/Library/Caches/shedskin/  (macOS)
        ~/.cache/shedskin/          (Linux)
        %LOCALAPPDATA%/shedskin/    (Windows)
            src/
                bdwgc/              (extracted sources)
                pcre2/
            build/
                bdwgc/              (cmake build dir)
                pcre2/
            include/                (installed headers)
            lib/                    (installed static libs)
    """

    def __init__(self, reset_on_run: bool = False):
        self.reset_on_run = reset_on_run

        # ext/ directory contains zip archives
        self.ext_dir = config.get_pkg_path() / "ext"
        self.bdwgc_zip = self.ext_dir / "bdwgc.zip"
        self.pcre2_zip = self.ext_dir / "pcre2.zip"

        # Cache directories (platform-specific)
        self.deps_dir = config.get_user_cache_dir()
        self.src_dir = self.deps_dir / "src"
        self.include_dir = self.deps_dir / "include"
        self.lib_dir = self.deps_dir / "lib"
        self.build_cache_dir = self.deps_dir / "build"

        # Extracted source directories (in cache)
        self.bdwgc_src = self.src_dir / "bdwgc"
        self.pcre2_src = self.src_dir / "pcre2"

        # Platform-specific library suffix
        self.lib_suffix = ".lib" if sys.platform == "win32" else ".a"

        if self.reset_on_run and self.deps_dir.exists():
            shutil.rmtree(self.deps_dir)

        # Create directories
        self.deps_dir.mkdir(parents=True, exist_ok=True)
        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.build_cache_dir.mkdir(parents=True, exist_ok=True)

    def _log(self, msg: str) -> None:
        """Log a message with formatting."""
        print(f"{WHITE}[LocalDeps]{RESET} {msg}")

    def _run_cmd(self, cmd: list[str], cwd: Optional[Pathlike] = None) -> None:
        """Run a command with logging."""
        cmd_str = " ".join(str(c) for c in cmd)
        print("-" * 80)
        print(f"{WHITE}cmd{RESET}: {CYAN}{cmd_str}{RESET}")
        subprocess.run(cmd, cwd=cwd, check=True)

    def _extract_zip(self, zip_path: pathlib.Path, dest_dir: pathlib.Path) -> None:
        """Extract a zip archive to the destination directory."""
        if dest_dir.exists():
            self._log(f"Source already extracted: {dest_dir}")
            return

        if not zip_path.exists():
            raise FileNotFoundError(f"Zip archive not found: {zip_path}")

        self._log(f"Extracting {zip_path.name} to {dest_dir.parent}")
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(dest_dir.parent)

    def _cmake_generate(
        self, src_dir: Pathlike, build_dir: Pathlike, **options: bool
    ) -> None:
        """Run cmake configuration stage."""
        cmd = [
            "cmake",
            "-S", str(src_dir),
            "-B", str(build_dir),
            f"--install-prefix={self.deps_dir}",
        ]
        for key, value in options.items():
            cmd.append(f"-D{key}={value}")
        self._run_cmd(cmd)

    def _cmake_build(self, build_dir: Pathlike, cfg: str = "Release") -> None:
        """Run cmake build stage."""
        cmd = ["cmake", "--build", str(build_dir), "--config", cfg]
        # Use parallel build if available
        if platform.system() != "Windows":
            cmd.extend(["--", "-j"])
        self._run_cmd(cmd)

    def _cmake_install(self, build_dir: Pathlike) -> None:
        """Run cmake install stage."""
        cmd = ["cmake", "--install", str(build_dir)]
        self._run_cmd(cmd)

    def bdwgc_targets_exist(self) -> bool:
        """Check if bdwgc targets are already built."""
        libgc = self.lib_dir / f"libgc{self.lib_suffix}"
        libgccpp = self.lib_dir / f"libgccpp{self.lib_suffix}"
        gc_h = self.include_dir / "gc.h"
        return all(t.exists() for t in [libgc, libgccpp, gc_h])

    def pcre2_targets_exist(self) -> bool:
        """Check if pcre2 targets are already built."""
        libpcre2 = self.lib_dir / f"libpcre2-8{self.lib_suffix}"
        pcre2_h = self.include_dir / "pcre2.h"
        return all(t.exists() for t in [libpcre2, pcre2_h])

    def targets_exist(self) -> bool:
        """Check if all required targets exist."""
        return self.bdwgc_targets_exist() and self.pcre2_targets_exist()

    def install_bdwgc(self, force: bool = False) -> bool:
        """Build and install bdwgc from ext/bdwgc.zip.

        Returns True if build was performed, False if skipped (already exists).
        """
        if not force and self.bdwgc_targets_exist():
            self._log(f"bdwgc already installed in {self.lib_dir}")
            return False

        # Extract zip if needed
        self._extract_zip(self.bdwgc_zip, self.bdwgc_src)

        if not self.bdwgc_src.exists():
            raise FileNotFoundError(f"bdwgc source not found at {self.bdwgc_src}")

        self._log(f"Building bdwgc from {self.bdwgc_src}")

        # Use a separate build directory in cache (out-of-source build)
        build_dir = self.build_cache_dir / "bdwgc"
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir(parents=True, exist_ok=True)

        # Configure with options appropriate for shedskin
        self._cmake_generate(
            self.bdwgc_src,
            build_dir,
            BUILD_SHARED_LIBS="OFF",
            enable_cplusplus="ON",
            build_cord="OFF",
            enable_docs="OFF",
            enable_gcj_support="OFF",
            enable_java_finalization="OFF",
            CMAKE_POSITION_INDEPENDENT_CODE="ON",
        )

        self._cmake_build(build_dir)
        self._cmake_install(build_dir)

        self._log(f"{GREEN}bdwgc installed successfully{RESET}")
        return True

    def install_pcre2(self, force: bool = False) -> bool:
        """Build and install pcre2 from ext/pcre2.zip.

        Returns True if build was performed, False if skipped (already exists).
        """
        if not force and self.pcre2_targets_exist():
            self._log(f"pcre2 already installed in {self.lib_dir}")
            return False

        # Extract zip if needed
        self._extract_zip(self.pcre2_zip, self.pcre2_src)

        if not self.pcre2_src.exists():
            raise FileNotFoundError(
                f"pcre2 source not found at {self.pcre2_src}. "
                f"Zip archive: {self.pcre2_zip}"
            )

        self._log(f"Building pcre2 from {self.pcre2_src}")

        # Use a separate build directory in cache (out-of-source build)
        build_dir = self.build_cache_dir / "pcre2"
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir(parents=True, exist_ok=True)

        # Configure with minimal options for shedskin
        self._cmake_generate(
            self.pcre2_src,
            build_dir,
            BUILD_SHARED_LIBS="OFF",
            PCRE2_BUILD_PCRE2GREP="OFF",
            PCRE2_SUPPORT_LIBREADLINE="OFF",
            PCRE2_SUPPORT_LIBEDIT="OFF",
            PCRE2_SUPPORT_LIBZ="OFF",
            PCRE2_SUPPORT_LIBBZ2="OFF",
            PCRE2_BUILD_TESTS="OFF",
            PCRE2_SHOW_REPORT="OFF",
            CMAKE_POSITION_INDEPENDENT_CODE="ON",
        )

        self._cmake_build(build_dir)
        self._cmake_install(build_dir)

        self._log(f"{GREEN}pcre2 installed successfully{RESET}")
        return True

    def install_all(self, force: bool = False) -> None:
        """Install all dependencies from ext/ zip archives."""
        if not force and self.targets_exist():
            self._log("All targets exist, no build needed")
            return

        self.install_bdwgc(force=force)
        self.install_pcre2(force=force)

    def get_include_dir(self) -> pathlib.Path:
        """Return the include directory for compiled headers."""
        return self.include_dir

    def get_lib_dir(self) -> pathlib.Path:
        """Return the library directory for compiled static libs."""
        return self.lib_dir

    def status(self) -> dict:
        """Return status information about the local dependencies."""
        return {
            "ext_dir": str(self.ext_dir),
            "cache_dir": str(self.deps_dir),
            "bdwgc_zip_exists": self.bdwgc_zip.exists(),
            "pcre2_zip_exists": self.pcre2_zip.exists(),
            "bdwgc_extracted": self.bdwgc_src.exists(),
            "pcre2_extracted": self.pcre2_src.exists(),
            "bdwgc_built": self.bdwgc_targets_exist(),
            "pcre2_built": self.pcre2_targets_exist(),
            "platform": platform.system(),
            "lib_suffix": self.lib_suffix,
        }


def add_shedskin_product(
    main_module: Optional[str] = None,
    sys_modules: Optional[list[str]] = None,
    app_modules: Optional[list[str]] = None,
    data: Optional[list[str]] = None,
    include_dirs: Optional[list[str]] = None,
    link_libs: Optional[list[str]] = None,
    link_dirs: Optional[list[str]] = None,
    compile_options: Optional[str] = None,
    link_options: Optional[str] = None,
    cmdline_options: Optional[str] = None,
    build_executable: bool = False,
    build_extension: bool = False,
    build_test: bool = False,
    # disable_executable: bool = False,
    # disable_extension: bool = False,
    # disable_test: bool = False,
    # has_lib: bool = False,
    enable_externalproject: bool = False,
    enable_spm: bool = False,
    debug: bool = False,
    name: Optional[str] = None,
    extra_lib_dir: Optional[str] = None,
) -> str:
    """populates a cmake function with the same name

    boolean options:
        HAS_LIB
        DEBUG

    boolean option pairs (setting one unsets the other)
        BUILD_EXECUTABLE BUILD_EXTENSION BUILD_TEST
        # not-implemented: DISABLE_EXECUTABLE DISABLE_EXTENSION DISABLE_TEST

    radio options (mutually exclusive):
        ENABLE_SPM ENABLE_EXTERNALPROJECT

    single_value options:
        NAME MAIN_MODULE

    multiple value options:
        SYS_MODULES APP_MODULES DATA
        INCLUDE_DIRS LINK_LIBS LINK_DIRS
        COMPILE_OPTIONS LINK_OPTIONS CMDLINE_OPTIONS
        EXTRA_LIB_DIRS
    """

    if extra_lib_dir:
        cmdline_options = "-X" + extra_lib_dir
        include_dirs = [extra_lib_dir]

    def mk_add(lines: list[str], spaces: int = 4) -> Callable[[int, str], None]:
        def _append(level: int, txt: str) -> None:
            indentation = " " * spaces * level
            lines.append(f"{indentation}{txt}")

        return _append

    flist = ["add_shedskin_product("]
    add = mk_add(flist)

    if build_executable:
        add(1, "BUILD_EXECUTABLE")
    # if disable_executable:
    #     add(1, "DISABLE_EXECUTABLE")

    if build_extension:
        add(1, "BUILD_EXTENSION")
    # if disable_extension:
    #     add(1, "DISABLE_EXTENSION")

    if build_test:
        add(1, "BUILD_TEST")
    # if disable_test:
    #     add(1, "DISABLE_TEST")

    if enable_externalproject:
        add(1, "ENABLE_EXTERNALPROJECT")
    elif enable_spm:
        add(1, "ENABLE_SPM")

    if debug:
        add(1, "DEBUG")

    if name:
        add(1, f"NAME {name}")

    if main_module:
        add(1, f"MAIN_MODULE {main_module}")

    if extra_lib_dir:
        add(1, f"EXTRA_LIB_DIR {extra_lib_dir}")

    if include_dirs:
        add(1, "INCLUDE_DIRS")
        for include_dir in sorted(include_dirs):
            add(2, include_dir)

    if link_libs:
        add(1, "LINK_LIBS")
        for link_lib in sorted(link_libs):
            add(2, link_lib)

    if link_dirs:
        add(1, "LINK_DIRS")
        for link_dir in sorted(link_dirs):
            add(2, link_dir)

    if compile_options:
        add(1, f"COMPILE_OPTIONS {compile_options}")

    if link_options:
        add(1, f"LINK_OPTIONS {link_options}")

    if cmdline_options:
        add(1, f"CMDLINE_OPTIONS {cmdline_options}")

    if sys_modules:
        add(1, "SYS_MODULES")
        for sys_mod in sorted(sys_modules):
            add(2, sys_mod)

    if app_modules:
        add(1, "APP_MODULES")
        for app_mod in sorted(app_modules):
            add(2, app_mod)
    if data:
        add(1, "DATA")
        for elem in sorted(data):
            add(2, elem)

    add(0, ")")
    return "\n".join(flist)


def get_cmakefile_template(**kwds: str) -> str:
    """Return a cmake template"""
    _pkg_path = config.get_pkg_path()
    cmakelists_tmpl = _pkg_path / "resources" / "cmake" / "CMakeLists.txt"
    tmpl = cmakelists_tmpl.read_text()
    return tmpl % kwds


def check_cmake_availability() -> None:
    """Check if cmake executable is available in path"""
    if not bool(shutil.which("cmake")):
        raise RuntimeError("cmake not available in path")


def get_cmake_preset(mode, build_type) -> str:
    """Return a usable cmake preset"""
    output = subprocess.run(
        ["cmake", f"--list-presets={mode}"], encoding="utf-8", capture_output=True, text=True
    ).stdout

    # look for a quoted string and return it
    # cmake does not provide a nicer way
    presets = []

    for line in output.splitlines():
        parts = line.split('"')
        if len(parts) > 2:
            presets.append(parts[1])

    # choose any preset that looks as if it might be specifically appropriate
    # for the build type
    build_type = build_type.lower()

    for preset in presets:
        if build_type in preset:
            return preset

    # if nothing looks appropriate, just choose the first preset
    return presets and presets[0] or None

def generate_cmakefile(gx: config.GlobalInfo) -> None:
    """Improved generator using built-in machinery"""
    path = gx.main_module.filename

    # Determine build type based on source location relative to cwd
    if path.is_relative_to(gx.cwd):
        rel_path = path.relative_to(gx.cwd)
        if len(rel_path.parts) == 1:
            build_type = "in_source"  # source file directly in cwd
        else:
            build_type = "subdirectory"  # source file in subdirectory of cwd
    else:
        build_type = "external"  # source file outside cwd

    modules = gx.modules.values()
    # filenames = [f'{m.filename.parent / m.filename.stem}' for m in modules]

    sys_mods = set()
    app_mods = set()

    compile_options = []
    if gx.int32:
        compile_options.append("-D__SS_INT32")
    if gx.int64:
        compile_options.append("-D__SS_INT64")
    if gx.int128:
        compile_options.append("-D__SS_INT128")
    if gx.float32:
        compile_options.append("-D__SS_FLOAT32")
    if gx.float64:
        compile_options.append("-D__SS_FLOAT64")
    if not gx.bounds_checking:
        compile_options.append("-D__SS_NOBOUNDS")
    if not gx.wrap_around_check:
        compile_options.append("-D__SS_NOWRAP")
    if gx.backtrace:
        compile_options.append("-D__SS_BACKTRACE -rdynamic -fno-inline")
    if not gx.assertions:
        compile_options.append("-D__SS_NOASSERT")
    if gx.backtrace:
        compile_options.append("-D__SS_BACKTRACE -rdynamic -fno-inline")
    if gx.nogc:
        compile_options.append("-D__SS_NOGC")
    compile_opts = " ".join(compile_options)

    cmdline_options = []
    if gx.options.collect_stats:
        cmdline_options.append("--collect-stats")
    cmdline_opts = " ".join(cmdline_options)

    for module in modules:
        if module.builtin and module.filename.is_relative_to(gx.shedskin_lib):
            entry = module.filename.relative_to(gx.shedskin_lib)
            entry = entry.parent / entry.stem
            if entry.name == "builtin":  # don't include 'builtin' module
                continue
            sys_mods.add(entry.as_posix())
        else:
            if module.filename.is_relative_to(gx.main_module.filename.parent):
                entry = module.filename.relative_to(gx.main_module.filename.parent)
            else:
                entry = module.filename
            entry = entry.parent / entry.stem
            if entry.name == path.stem:  # don't include main_module
                continue
            app_mods.add(entry.as_posix())

    assert gx.options, "gx.options must be populated"
    if build_type == "in_source":
        # Source file directly in cwd (e.g., ./test.py)
        master_clfile = path.parent / "CMakeLists.txt"
        master_clfile_content = get_cmakefile_template(
            project_name=f"{gx.main_module.ident}_project",
            is_simple_project="ON",
            entry=add_shedskin_product(
                path.name,
                list(sys_mods),
                list(app_mods),
                name=path.stem,
                build_executable=gx.executable_product,
                build_extension=gx.pyextension_product,
                include_dirs=gx.options.include_dirs,
                link_dirs=gx.options.link_dirs,
                link_libs=gx.options.link_libs,
                extra_lib_dir=gx.options.extra_lib,
                compile_options=compile_opts,
                cmdline_options=cmdline_opts,
            )
        )
        master_clfile.write_text(master_clfile_content)

    elif build_type == "subdirectory":
        # Source file in subdirectory of cwd (e.g., ./subdir/test.py or ./nested/subdir/test.py)
        src_clfile = path.parent / "CMakeLists.txt"

        src_clfile.write_text(
            add_shedskin_product(
                path.name,
                list(sys_mods),
                list(app_mods),
                build_executable=gx.executable_product,
                build_extension=gx.pyextension_product,
                include_dirs=gx.options.include_dirs,
                link_dirs=gx.options.link_dirs,
                link_libs=gx.options.link_libs,
                extra_lib_dir=gx.options.extra_lib,
                compile_options=compile_opts,
                cmdline_options=cmdline_opts,
            )
        )

        # Master CMakeLists.txt always in cwd, with full relative path to source subdir
        master_clfile = gx.cwd / "CMakeLists.txt"
        # Get relative path from cwd to source directory (e.g., "nested/tmp" for nested/tmp/test.py)
        rel_subdir = path.parent.relative_to(gx.cwd)
        master_clfile_content = get_cmakefile_template(
            project_name=f"{gx.main_module.ident}_project",
            is_simple_project="OFF",
            entry=f"add_subdirectory({rel_subdir.as_posix()})",
        )
        master_clfile.write_text(master_clfile_content)

    else:
        # External source file outside cwd (e.g., ../tests/test_foo/test_foo.py)
        # Generate CMakeLists.txt in cwd, reference source with absolute path
        master_clfile = gx.cwd / "CMakeLists.txt"
        # Convert app_mods to absolute paths (they're relative to main module's parent)
        main_parent = gx.main_module.filename.parent
        abs_app_mods = [(main_parent / mod).as_posix() for mod in app_mods]
        master_clfile_content = get_cmakefile_template(
            project_name=f"{gx.main_module.ident}_project",
            is_simple_project="ON",
            entry=add_shedskin_product(
                path.as_posix(),  # absolute path to source (used as MAIN_MODULE)
                list(sys_mods),
                abs_app_mods,  # absolute paths for external sources
                name=path.stem,
                build_executable=gx.executable_product,
                build_extension=gx.pyextension_product,
                include_dirs=gx.options.include_dirs,
                link_dirs=gx.options.link_dirs,
                link_libs=gx.options.link_libs,
                extra_lib_dir=gx.options.extra_lib,
                compile_options=compile_opts,
                cmdline_options=cmdline_opts,
            )
        )
        master_clfile.write_text(master_clfile_content)


class CMakeBuilder:
    """Shedskin cmake builder"""

    def __init__(self, gx: config.GlobalInfo):
        self.gx = gx
        self.options = gx.options
        source_path = pathlib.Path(self.options.name).resolve()

        # Determine source_dir based on where CMakeLists.txt was generated
        # Since we no longer chdir, gx.cwd is always where the user ran the command
        if source_path.is_relative_to(gx.cwd):
            rel_path = source_path.relative_to(gx.cwd)
            if len(rel_path.parts) == 1:
                # Source in cwd (e.g., ./test.py)
                self.source_dir = gx.cwd
            else:
                # Source in subdirectory (e.g., ./tests/test_foo/test_foo.py)
                self.source_dir = gx.cwd
        else:
            # External source (e.g., ../tests/test_foo/test_foo.py)
            # CMakeLists.txt is in cwd
            self.source_dir = gx.cwd

        self.build_dir = self.source_dir / "build"
        self.tests = sorted(glob.glob("./test_*/test_*.py", recursive=True))
        self.log = logging.getLogger(self.__class__.__name__)

    def check(self, path: Pathlike) -> None:
        """Check file for syntax errors"""
        with open(path, encoding="utf8") as fopen:
            src = fopen.read()
        compile(src, path, "exec")

    def get_most_recent_test(self) -> Optional[str]:
        """Return the name of the recently modified test"""
        max_mtime = 0.0
        most_recent_test = None
        for test in self.tests:
            mtime = os.stat(os.path.abspath(test)).st_mtime
            if mtime > max_mtime:
                max_mtime = mtime
                most_recent_test = test
        return most_recent_test

    def error_tests(self) -> List[str]:
        """Test error messages from tests in the errs directory"""
        failures = []
        os.chdir("errs")
        tests = sorted(os.path.basename(t) for t in glob.glob("[0-9][0-9].py"))
        for test in tests:
            print("*** test:", test)
            try:
                checks = []
                with open(test, encoding="utf8") as fopen:
                    for line in fopen:
                        if line.startswith("#*"):
                            checks.append(line[1:].strip())
                cmd = f"{sys.executable} -m shedskin {test}".split()
                output = subprocess.run(
                    cmd, encoding="utf-8", capture_output=True, text=True
                ).stdout
                assert not [line for line in output if "Traceback" in line]
                for check in checks:
                    print(check)
                    assert [
                        line for line in output.splitlines() if line.startswith(check)
                    ]
                print(f"*** {GREEN}SUCCESS{RESET}:", test)
            except AssertionError:
                print(f"*** {RED}FAILURE{RESET}:", test)
                failures.append(test)
        os.chdir("..")
        return failures

    def rm_build(self) -> None:
        """Remove the build directory"""
        shutil.rmtree(self.build_dir)

    def mkdir_build(self) -> None:
        """Create the build directory"""
        os.makedirs(self.build_dir, exist_ok=True)

    def cmake_config(self, options: list[str], generator: Optional[str] = None) -> None:
        """CMake configuration phase"""
        opts = " ".join(options)

        cfg_cmd = f"cmake {opts} -S {self.source_dir} -B {self.build_dir}"
        if generator:
            cfg_cmd += ' -G "{generator}"'

        self.log.info(cfg_cmd)
        subprocess.run(cfg_cmd, shell=True, check=True)

    def cmake_build(self, options: list[str]) -> None:
        """Activate cmake build"""
        opts = " ".join(options)

        # --config is needed for multi-config generators (Visual Studio on Windows)
        build_type = self.options.build_type or "Debug"
        bld_cmd = f"cmake --build {self.build_dir} --config {build_type} {opts}"

        self.log.info(bld_cmd)
        subprocess.run(bld_cmd, shell=True, check=True)

    def cmake_test(self, options: list[str]) -> None:
        """Activate ctest"""
        opts = " ".join(options)

        if platform.system() == "Windows":
            cfg = f"-C {self.options.build_type}"
        else:
            cfg = ""
        tst_cmd = f"ctest {cfg} --output-on-failure {opts} --test-dir {self.build_dir}"

        self.log.info(tst_cmd)
        subprocess.run(tst_cmd, shell=True, check=True)

    def run_tests(self) -> None:
        """Run tests as a test runner"""
        self.process(run_tests=True)

    def build(self) -> None:
        """Build as a builder"""
        self.process(run_tests=False)

    def process(self, run_tests: bool = False) -> None:
        """Process a shedskin program with cmake"""
        start_time = time.time()

        cfg_options = (
            []
            if not getattr(self.options, "cfg", None)
            else [f"-D{opt}" for opt in self.options.cfg]
        )
        bld_options = []
        tst_options = []

        # -------------------------------------------------------------------------
        # cfg and bld options

        cfg_options.append("-DBUILD_EXECUTABLE=ON")
        if self.options.extmod:
            cfg_options.append("-DBUILD_EXTENSION=ON")

        if hasattr(self.options, "disable_exes"):
            if self.options.disable_exes:
                cfg_options.append("-DDISABLE_EXECUTABLES=ON")

        if hasattr(self.options, "disable_exts"):
            if self.options.disable_exts:
                cfg_options.append("-DDISABLE_EXTENSIONS=ON")

        if self.options.debug:
            cfg_options.append("-DDEBUG=ON")

        if self.options.collect_stats:
            cfg_options.append("-DCOLLECT_STATS=ON")

        if self.options.generator:
            cfg_options.append(f"-G{self.options.generator}")

        if self.options.build_type:
            cfg_options.append(f"-DCMAKE_BUILD_TYPE={self.options.build_type}")

        if self.options.jobs:
            bld_options.append(f"--parallel {self.options.jobs}")
            tst_options.append(f"--parallel {self.options.jobs}")

        if self.options.ccache:
            if shutil.which("ccache"):
                cfg_options.append("-DCMAKE_CXX_COMPILER_LAUNCHER=ccache")
            else:
                self.log.warning("'ccache' not found")

        if self.options.spm:
            cfg_options.append("-DENABLE_SPM=ON")

        elif self.options.fetchcontent:
            cfg_options.append("-DENABLE_FETCH_CONTENT=ON")

        elif getattr(self.options, 'local_deps', False):
            cfg_options.append("-DENABLE_LOCAL_DEPS=ON")
            cache_dir = config.get_user_cache_dir()
            cfg_options.append(f"-DLOCAL_DEPS_DIR={cache_dir}")

        if not self.options.nowarnings:
            cfg_options.append("-DENABLE_WARNINGS=ON")

        if not cfg_options:
            self.log.warning("no configuration options selected")
            return

        if self.build_dir.exists() and self.options.reset:
            self.rm_build()

        if not self.build_dir.exists():
            self.mkdir_build()

        if self.options.spm:
            spm = ShedskinDependencyManager(self.source_dir)
            spm.install_all()

        elif getattr(self.options, 'local_deps', False):
            ldm = LocalDependencyManager()
            ldm.install_all()

        if self.options.target:
            target_suffix = "-exe"
            for target in self.options.target:
                bld_options.append(f"--target {target}{target_suffix}")
                tst_options.append(f"--tests-regex {target}{target_suffix}")

        # -------------------------------------------------------------------------
        # test options

        if run_tests:
            if self.options.include:
                tst_options.append(f"--tests-regex {self.options.include}")

            if self.options.check:
                self.check(self.options.name)  # check python syntax

            if self.options.modified:
                test = self.get_most_recent_test()
                assert test, "test required"
                most_recent_test = pathlib.Path(test).stem
                bld_options.append(f"--target {most_recent_test}")
                tst_options.append(f"--tests-regex {most_recent_test}")

            # nocleanup

            if self.options.pytest:
                subprocess.run(["pytest"], check=True)

            if self.options.run:
                target_suffix = "-exe"
                if self.options.extmod:
                    target_suffix = "-ext"
                bld_options.append(f"--target {self.options.run}{target_suffix}")
                tst_options.append(f"--tests-regex {self.options.run}")

            if self.options.stoponfail:
                tst_options.append("--stop-on-failure")

            if self.options.progress:
                tst_options.append("--progress")

        self.cmake_config(cfg_options)

        # print("cfg_options:", cfg_options)
        # print("bld_options:", bld_options)
        self.cmake_build(bld_options)

        if run_tests:
            self.cmake_test(tst_options)

        end_time = time.time()
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))
        print(f"Total time: {elapsed_time}\n")

    def run_error_tests(self) -> None:
        """Run error tests"""
        start_time = time.time()

        if self.options.run_errs:
            failures = self.error_tests()
            if not failures:
                print(f"==> {GREEN}NO FAILURES, yay!{RESET}")
            else:
                print(f"==> {RED}TESTS FAILED:{RESET}", len(failures))
                print(failures)
        else:
            raise ValueError("option.run_errs not set")

        end_time = time.time()
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))
        print(f"Total time: {elapsed_time}\n")


class TestRunner(CMakeBuilder):
    """Basic test runner"""

    def __init__(self, gx: config.GlobalInfo):
        self.gx = gx
        self.options = gx.options
        self.source_dir = pathlib.Path.cwd()
        self.build_dir = pathlib.Path("build")
        self.tests = sorted(glob.glob("./test_*/test_*.py", recursive=True))
        self.log = logging.getLogger(self.__class__.__name__)
