# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.makefile: makefile generator

This module generates Makefiles for building Shedskin-compiled C++ code.

Key components:
- Platform-specific configuration (Windows, macOS, Linux)
- Compiler and linker flags management
- Dependency tracking and linking
- Build target generation (debug, profile, static)
- Cleaning utilities

The generated Makefile handles:
- Building the main executable or extension module
- Debug and profile builds
- Static linking on macOS with `Homebrew`
- Cleaning build artifacts
"""

import os
import subprocess
import re
import sys
import sysconfig
import platform
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional, TypeAlias

if TYPE_CHECKING:
    from . import config
    from . import python

# type aliases
PathLike: TypeAlias = Path | str
TestFunc: TypeAlias = Callable[[str], bool]

# constants
PLATFORM = platform.system()

FLAGS = """\
CXX?=g++
CXXFLAGS?=-O2 -std=c++17 -march=native $(CPPFLAGS)
LFLAGS=-lgc -lgctba -lutil $(LDFLAGS)
"""

FLAGS_MINGW = """\
CXX?=g++
CXXFLAGS?=-O2 -DWIN32 -std=c++17 -march=native -Wno-deprecated -Wl,--enable-auto-import $(CPPFLAGS)
LFLAGS=-lgc -lpcre -lgccpp $(LDFLAGS)
"""

FLAGS_OSX = """\
CXX?=g++
CXXFLAGS?=-O2 -std=c++17 -Wno-deprecated $(CPPFLAGS)
LFLAGS=-lgc -lgctba -lpcre $(LDFLAGS)
"""


def env_var(name: str) -> str:
    return "$(%s)" % name


def check_output(cmd: str) -> Optional[str]:
    """Run a command and return its output, or None if command not found"""
    try:
        return subprocess.check_output(cmd.split(), encoding="utf8").strip()
    except FileNotFoundError:
        return None


class MakefileWriter:
    """Handles writing Makefile contents"""

    def __init__(self, path: PathLike):
        self.makefile = open(path, "w")

    def write(self, line: str = "") -> None:
        """Write a line to the Makefile"""
        print(line, file=self.makefile)

    def close(self) -> None:
        """Close the Makefile"""
        self.makefile.close()


class PythonSystem:
    def __init__(self):
        self.name = "Python"
        self.version_info = sys.version_info

    def __str__(self):
        return self.version

    @property
    def version(self) -> str:
        """semantic version of python: 3.11.10"""
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def ver(self) -> str:
        """short major.minor python version: 3.11"""
        return f"{self.major}.{self.minor}"

    @property
    def ver_nodot(self) -> str:
        """concat major and minor version components: 311 in 3.11.7"""
        return self.ver.replace(".", "")

    @property
    def major(self) -> str:
        """major component of semantic version: 3 in 3.11.7"""
        return self.version_info.major

    @property
    def minor(self) -> str:
        """minor component of semantic version: 11 in 3.11.7"""
        return self.version_info.minor

    @property
    def patch(self) -> str:
        """patch component of semantic version: 7 in 3.11.7"""
        return self.version_info.micro

    @property
    def name_version(self) -> str:
        """return name-<fullversion>: e.g. Python-3.11.7"""
        return f"{self.name}-{self.version}"

    @property
    def name_ver(self) -> str:
        """return name.lower-<ver>: e.g. python3.11"""
        return f"{self.name.lower()}{self.ver}"

    @property
    def executable_name(self) -> str:
        """executable name"""
        name = self.name.lower()
        if PLATFORM == "Windows":
            name = f"{self.name}.exe"
        return name

    @property
    def libname(self) -> str:
        """library name prefix"""
        return f"lib{self.name}"

    @property
    def linklib(self) -> str:
        """name of library for linking"""
        return f"-l{self.name_ver}"

    @property
    def staticlib_name(self) -> str:
        """static libname"""
        suffix = ".a"
        if PLATFORM == "Windows":
            suffix = ".lib"
        return f"{self.libname}{suffix}"

    @property
    def dylib_name(self) -> str:
        """dynamic link libname"""
        if PLATFORM == "Windows":
            return f"{self.libname}.dll"
        elif PLATFORM == "Darwin":
            return f"{self.libname}.dylib"
        else:
            return f"{self.libname}.so"

    @property
    def dylib_linkname(self) -> str:
        """symlink to dylib"""
        if PLATFORM == "Darwin":
            return f"{self.libname}.dylib"
        else:
            return f"{self.libname}.so"

    @property
    def prefix(self) -> str:
        """python system prefix"""
        return sysconfig.get_config_var("prefix")

    @property
    def include_dir(self) -> str:
        """python include directory"""
        return sysconfig.get_config_var("INCLUDEPY")

    @property
    def config_h_dir(self) -> str:
        """directory of config.h file"""
        return os.path.dirname(sysconfig.get_config_h_filename())

    @property
    def base_cflags(self) -> str:
        """python base cflags"""
        return sysconfig.get_config_var("BASECFLAGS")

    @property
    def libs(self) -> str:
        """python libs to link to"""
        return sysconfig.get_config_var("LIBS")

    @property
    def syslibs(self) -> str:
        """python system libs to link to"""
        return sysconfig.get_config_var("SYSLIBS")

    @property
    def is_shared(self) -> bool:
        """python system was built with enable_shared option"""
        return bool(sysconfig.get_config_var("Py_ENABLE_SHARED"))

    @property
    def libpl(self) -> str:
        """directory of python dependencies"""
        return sysconfig.get_config_var("LIBPL")

    @property
    def extension_suffix(self) -> str:
        """suffix of python extension"""
        if PLATFORM == "Windows":
            return ".pyd"
        else:
            return ".so"


class MakefileGenerator:
    """Generates Makefile for C/C++ code"""

    def __init__(self, path: PathLike, strict: bool = False):
        self.path = path
        self.strict = strict # raise error if variable or entry already exists
        self.cxx = "g++"
        self.vars: dict[str, PathLike] = {}  # variables
        self.var_order: list[str] = []  # write order of variables
        self.include_dirs: list[str] = []  # include directories
        self.cflags: list[str] = []  # c compiler flags
        self.cxxflags: list[str] = []  # c++ compiler flags
        self.link_dirs: list[str] = []  # link directories
        self.ldlibs: list[str] = []  # link libraries
        self.ldflags: list[str] = []  # linker flags + link_dirs
        self.targets: list[str] = []  # targets
        self.phony: list[str] = []  # phony targets
        self.clean: list[str] = []  # clean target
        # writer
        self.writer = MakefileWriter(path)


    def write(self, text: Optional[str] = None) -> None:
        """Write a line to the Makefile"""
        if not text:
            self.writer.write("")
        else:
            self.writer.write(text)

    def close(self) -> None:
        """Close the Makefile"""
        self.writer.close()

    def check_dir(self, path: PathLike) -> bool:
        """Check if a path is a valid directory"""
        str_path = str(path)
        match = re.match(r".*\$+\((.+)\).*", str_path)
        if match:
            key = match.group(1)
            assert key in self.vars, f"Invalid variable: {key}"
            assert os.path.isdir(
                self.vars[key]
            ), f"Value of variable {key} is not a directory: {self.vars[key]}"
            return True
        return os.path.isdir(str_path)

    def _add_entry_or_variable(
        self,
        attr: str,
        prefix: str = "",
        test_func: Optional[TestFunc] = None,
        *entries,
        **kwargs,
    ) -> None:
        """Add an entry or variable to the Makefile"""
        assert hasattr(self, attr), f"Invalid attribute: {attr}"
        _list = getattr(self, attr)
        if not test_func:
            test_func = lambda x: True
        for entry in entries:
            assert test_func(entry), f"Invalid entry: {entry}"
            if entry in _list:
                if self.strict:
                    raise ValueError(f"entry: {entry} already exists in {attr} list")
                else:
                    continue
            _list.append(f"{prefix}{entry}")
        for key, value in kwargs.items():
            assert test_func(value), f"Invalid value: {value}"
            if key in self.vars:
                if self.strict:
                    raise ValueError(f"variable: {key} already exists in vars dict")
                else:
                    continue
            self.vars[key] = value
            _list.append(f"{prefix}$({key})")
            self.var_order.append(key)

    def add_variable(self, key: str, value: str) -> None:
        """Add a variable to the Makefile"""
        self.vars[key] = value
        self.var_order.append(key)

    def add_include_dirs(self, *entries, **kwargs):
        """Add include directories to the Makefile"""
        self._add_entry_or_variable(
            "include_dirs", "-I", self.check_dir, *entries, **kwargs
        )

    def add_cflags(self, *entries, **kwargs):
        """Add compiler flags to the Makefile"""
        self._add_entry_or_variable("cflags", "", None, *entries, **kwargs)

    def add_cxxflags(self, *entries, **kwargs):
        """Add c++ compiler flags to the Makefile"""
        self._add_entry_or_variable("cxxflags", "", None, *entries, **kwargs)

    def add_link_dirs(self, *entries, **kwargs):
        """Add link directories to the Makefile"""
        self._add_entry_or_variable(
            "link_dirs", "-L", self.check_dir, *entries, **kwargs
        )

    def add_ldlibs(self, *entries, **kwargs):
        """Add link libraries to the Makefile"""
        self._add_entry_or_variable("ldlibs", "", None, *entries, **kwargs)

    def add_ldflags(self, *entries, **kwargs):
        """Add linker flags to the Makefile"""
        self._add_entry_or_variable("ldflags", "", None, *entries, **kwargs)

    def add_target(
        self, name: str, body: Optional[str] = None, deps: Optional[list[str]] = None
    ):
        """Add targets to the Makefile"""
        if body and deps:
            _deps = " ".join(deps)
            self.targets.append(f"{name}: {_deps}\n\t{body}")
        elif body and not deps:
            self.targets.append(f"{name}:\n\t{body}")
        elif not body and deps:
            _deps = " ".join(deps)
            self.targets.append(f"{name}: {_deps}")
        else:  # no body or dependencies
            raise ValueError("Either body or dependencies must be provided")

    def add_phony(self, *entries):
        """Add phony targets to the Makefile"""
        for entry in entries:
            if entry and entry not in self.phony:
                self.phony.append(entry)

    def add_clean(self, *entries):
        """Add clean target to the Makefile"""
        for entry in entries:
            if entry and entry not in self.clean:
                self.clean.append(entry)

    def _setup_defaults(self):
        """Setup default model configuration"""
        self.add_include_dirs(".")
        self.add_lflags("$(LDLIBS)", "$(LDFLAGS)")

    def _write_variables(self) -> None:
        """Write variables to the Makefile"""

        self.write("# project variables")
        for key in self.var_order:
            value = self.vars[key]
            self.write(f"{key}={value}")
        self.write()

        # write includes
        if self.include_dirs:
            include_dirs = " ".join(self.include_dirs)
            self.write(f"INCLUDEDIRS={include_dirs}")
        # write link_dirs
        if self.link_dirs:
            link_dirs = " ".join(self.link_dirs)
            self.write(f"LINKDIRS={link_dirs}")
        self.write()

        # write cxx compiler
        self.write(f"CXX={self.cxx}")
        # write cflags
        if self.cflags:
            cflags = " ".join(self.cflags)
            self.write(f"CFLAGS+={cflags} $(INCLUDEDIRS)")
        # write cxxflags
        if self.cxxflags:
            cxxflags = " ".join(self.cxxflags)
            self.write(f"CXXFLAGS+={cxxflags} $(INCLUDEDIRS)")
        # write ldflags / link_dirs
        if self.ldflags or self.link_dirs:
            ldflags = " ".join(self.ldflags)
            self.write(f"LDFLAGS+={ldflags} $(LINKDIRS)")
        # write ldlibs
        if self.ldlibs:
            ldlibs = " ".join(self.ldlibs)
            self.write(f"LDLIBS={ldlibs}")
        self.write()

    def _write_phony(self) -> None:
        """Write phony targets to the Makefile"""
        if self.phony:
            phone_targets = " ".join(self.phony)
            self.write(f".PHONY: {phone_targets}")
            self.write()

    def _write_targets(self) -> None:
        """Write targets to the Makefile"""
        for target in sorted(self.targets):
            self.write(target)
            self.write()

    def _write_clean(self) -> None:
        """Write clean target to the Makefile"""
        if self.clean:
            clean_targets = " ".join(self.clean)
            self.write(f"clean:\n\t@rm -rf {clean_targets}")
            self.write()

    def generate(self) -> None:
        """Generate the Makefile"""
        self._setup_defaults()
        self._write_variables()
        self._write_phony()
        self._write_targets()
        self._write_clean()
        self.close()


class ShedskinMakefileGenerator(MakefileGenerator):
    """Generates Makefile for Shedskin-compiled code"""

    def __init__(self, gx: "config.GlobalInfo", strict: bool = False):
        self.gx = gx
        self.no_flag_file = False
        super().__init__(path=self.gx.makefile_name, strict=strict)
        self.esc_space = r"\ "
        self.py = PythonSystem()

    @property
    def makefile_path(self) -> str:
        """Get the Makefile output path"""
        if self.gx.outputdir:
            return os.path.join(self.gx.outputdir, self.gx.makefile_name)
        return self.gx.makefile_name

    @property
    def shedskin_libdirs(self) -> list[str]:
        """List of shedskin libdirs"""
        return [d.replace(" ", self.esc_space) for d in self.gx.libdirs]

    @property
    def modules(self) -> list["python.Module"]:
        """List of modules"""
        return list(self.gx.modules.values())

    @property
    def filenames(self) -> list[str]:
        """List of filenames"""
        _filenames = []
        for module in self.modules:
            filename = os.path.splitext(module.filename)[0]  # strip .py
            filename = filename.replace(" ", self.esc_space)  # make paths valid
            if self.gx.outputdir and not module.builtin:
                filename = os.path.abspath(
                    os.path.join(self.gx.outputdir, os.path.basename(filename))
                )
            else:
                filename = filename.replace(
                    self.shedskin_libdirs[-1], env_var("SHEDSKIN_LIBDIR")
                )
            _filenames.append(filename)
        return _filenames

    @property
    def cppfiles(self) -> list[str]:
        """Reverse sorted list of .cpp files"""
        return sorted([fn + ".cpp" for fn in self.filenames], reverse=True)

    @property
    def hppfiles(self) -> list[str]:
        """Reverse sorted list of .hpp files"""
        return sorted([fn + ".hpp" for fn in self.filenames], reverse=True)

    @property
    def target_name(self) -> str:
        """Get the target executable/library name"""
        if self.gx.pyextension_product:
            return f"{self.gx.main_module.ident}{self.py.extension_suffix}"
        else:
            return self.gx.main_module.ident

    def homebrew_prefix(self, entry: Optional[str] = None) -> Optional[Path]:
        """Get Homebrew prefix"""
        if entry:
            res = check_output(f"brew --prefix {entry}")
            if res:
                return Path(res)
            return None
        else:
            res = check_output("brew --prefix")
            if res:
                return Path(res)
            return None

    def generate(self) -> None:
        """Generate the Makefile"""
        if self.gx.nomakefile:
            return

        self._setup_variables()
        self._setup_platform()

        if not self.no_flag_file:
            self._add_flag_file_options()
        self._add_feature_flags()
        self._add_user_options()
        self._add_module_linker_flags()
        self._add_targets()
        self._add_clean_target()
        self._add_phony_targets()

        self._write_variables()
        self._write_targets()
        self._write_clean()
        self._write_phony()

        self.writer.close()

    def _setup_variables(self) -> None:
        """Configure common variables"""
        self.add_include_dirs(SHEDSKIN_LIBDIR=self.shedskin_libdirs[-1])
        for _dir in self.shedskin_libdirs[:-1]:
            self.add_include_dirs(_dir)

        if self.gx.pyextension_product:
            self.add_include_dirs(PY_INCLUDE=self.py.include_dir)
            if self.py.include_dir != self.py.config_h_dir:
                self.add_include_dirs(PY_CONFIG_H_DIR=self.py.config_h_dir)

    def _setup_platform(self) -> None:
        """Configure platform-specific settings"""
        if PLATFORM == "Windows":
            self._setup_windows()
        else:
            self._setup_unix()

    def _setup_windows(self) -> None:
        """Configure Windows-specific settings"""
        if self.no_flag_file:
            self.add_cxxflags(
                "-O2",
                "-DWIN32",
                "-std=c++17",
                "-march=native",
                "-Wno-deprecated",
                "-Wl,--enable-auto-import",
                "$(CPPFLAGS)",
            )
            self.add_ldlibs("-lgc", "-lpcre", "-lgccpp")
        if self.gx.pyextension_product:
            self.add_include_dirs(f"{self.py.prefix}\\include")
            self.add_cxxflags("-D__SS_BIND")
            self.add_ldflags("-shared")
            self.add_link_dirs(f"{self.py.prefix}\\libs")
            self.add_ldlibs(f"-lpython{self.py.ver}")

    def _setup_unix(self) -> None:
        """Configure Unix-like platform settings"""
        if os.path.isdir("/usr/local/include"):
            self.add_include_dirs("/usr/local/include")
        if os.path.isdir("/opt/local/include"):
            self.add_include_dirs("/opt/local/include")
        if self.gx.pyextension_product:
            self.add_cxxflags("-g", "-fPIC", "-D__SS_BIND")

        if PLATFORM == "Darwin":
            if prefix := self.homebrew_prefix():
                self.add_variable("HOMEBREW_PREFIX", prefix)
                self.add_include_dirs(HOMEBREW_INCLUDE="$(HOMEBREW_PREFIX)/include")
                self.add_link_dirs(HOMEBREW_LIB="$(HOMEBREW_PREFIX)/lib")
                self.add_variable("STATIC_GC", "$(HOMEBREW_LIB)/libgc.a")
                self.add_variable("STATIC_GCCPP", "$(HOMEBREW_LIB)/libgccpp.a")
                self.add_variable("STATIC_PCRE", "$(HOMEBREW_LIB)/libpcre.a")
                self.add_variable(
                    "STATIC_LIBS", "$(STATIC_GC) $(STATIC_GCCPP) $(STATIC_PCRE)"
                )
            if self.no_flag_file:
                self.add_cxxflags("-O2", "-std=c++17", "-Wno-deprecated", "$(CPPFLAGS)")
                self.add_ldlibs("-lgc", "-lgctba", "-lpcre")
            self.add_ldflags(self.py.base_cflags, "-undefined dynamic_lookup")
        else:
            if self.gx.pyextension_product:
                self.add_ldflags(
                    self.py.libs,
                    self.py.syslibs,
                    self.py.linklib,
                    "-Wno-register",
                    "-shared",
                    "-Xlinker",
                    "-export-dynamic",
                )
                if not self.py.is_shared:
                    self.add_link_dirs(self.py.libpl)
            if self.no_flag_file:
                self.add_cxxflags("-O2", "-std=c++17", "-march=native", "$(CPPFLAGS)")
                self.add_ldlibs("-lgc", "-lgctba", "-lutil")

    def _add_feature_flags(self) -> None:
        """Add feature-specific compiler flags"""
        if not self.gx.wrap_around_check:
            self.add_cxxflags("-D__SS_NOWRAP")
        if not self.gx.bounds_checking:
            self.add_cxxflags("-D__SS_NOBOUNDS")
        if not self.gx.assertions:
            self.add_cxxflags("-D__SS_NOASSERT")
        if self.gx.int32:
            self.add_cxxflags("-D__SS_INT32")
        if self.gx.int64:
            self.add_cxxflags("-D__SS_INT64")
        if self.gx.int128:
            self.add_cxxflags("-D__SS_INT128")
        if self.gx.float32:
            self.add_cxxflags("-D__SS_FLOAT32")
        if self.gx.float64:
            self.add_cxxflags("-D__SS_FLOAT64")
        if self.gx.backtrace:
            self.add_cxxflags("-D__SS_BACKTRACE", "-rdynamic", "-fno-inline")
        if self.gx.nogc:
            self.add_cxxflags("-D__SS_NOGC")

    def _add_user_options(self) -> None:
        """Add user-specified commandline options"""
        if self.gx.options.include_dirs:
            for include_dir in self.gx.options.include_dirs:
                self.add_include_dirs(include_dir)
        if self.gx.options.link_dirs:
            for link_dir in self.gx.options.link_dirs:
                self.add_link_dirs(link_dir)
        if self.gx.options.link_libs:
            for link_lib in self.gx.options.link_libs:
                if PLATFORM == "Windows":
                    link_lib = link_lib.replace(" ", self.esc_space)
                else:
                    self.add_ldlibs(f"-l{link_lib}")

    def _add_module_linker_flags(self) -> None:
        """Add module-specific linker flags"""
        module_ids = [m.ident for m in self.modules]
        if "re" in module_ids:
            self.add_ldlibs("-lpcre")
        if "socket" in module_ids:
            if PLATFORM == "Windows":
                self.add_ldlibs("-lws2_32")
            elif PLATFORM == "SunOS":
                self.add_ldlibs("-lsocket", "-lnsl")
        if "os" in module_ids:
            if PLATFORM not in ["Windows", "Darwin", "SunOS"]:
                self.add_ldlibs("-lutil")
        if "hashlib" in module_ids:
            self.add_ldlibs("-lcrypto")

    def _add_targets(self) -> None:
        """Add targets to the Makefile"""
        self.add_target("all", deps=[self.target_name])
        # executable (normal, debug, profile) or extension module
        _out = "-o "
        _ext = ""
        targets = [("", "")]
        if not self.gx.pyextension_product:
            targets += [("_prof", "-pg -ggdb"), ("_debug", "-g -ggdb")]

        for suffix, options in targets:
            self.add_target(
                self.target_name + suffix,
                deps=["$(CPPFILES)", "$(HPPFILES)"],
                body=f"$(CXX) {options} $(CXXFLAGS) $(CPPFILES) $(LDLIBS) $(LDFLAGS) -o {self.target_name}{suffix}{_ext}",
            )

        if PLATFORM == "Darwin":
            self.add_target(
                "static",
                deps=["$(CPPFILES)", "$(HPPFILES)"],
                body=f"$(CXX) $(CXXFLAGS) $(CPPFILES) $(STATIC_LIBS) $(LDFLAGS) -o {self.target_name}",
            )

    def _add_clean_target(self) -> None:
        """Add clean target to the Makefile"""
        # self.add_clean(self.target_name)
        ext = ""
        if PLATFORM == "Windows" and not self.gx.pyextension_product:
            ext = ".exe"
        _targets = [self.target_name + ext]
        if not self.gx.pyextension_product:
            _targets += [
                self.target_name + "_prof" + ext,
                self.target_name + "_debug" + ext,
            ]
        if PLATFORM == "Darwin":
            _targets += ["*.dSYM"]
        self.add_clean(*_targets)

    def _add_phony_targets(self) -> None:
        """Add phony targets to the Makefile"""
        self.add_phony("all", "clean")
        if PLATFORM == "Darwin":
            self.add_phony("static")

    def _write_variables(self) -> None:
        """Write variables to the Makefile"""
        super()._write_variables()
        self._write_cpp_files()

    def _write_cpp_files(self) -> None:
        """Write C++ source and header file lists"""
        cppfiles_str = " \\\n\t".join(self.cppfiles)
        hppfiles_str = " \\\n\t".join(self.hppfiles)
        self.write("CPPFILES=%s\n" % cppfiles_str)
        self.write("HPPFILES=%s\n" % hppfiles_str)

    # --------------------------------------------------------------------------
    # Flags file management
    # --------------------------------------------------------------------------

    def _get_flags_file(self) -> Path:
        """Get the appropriate flags file for the current platform"""
        if self.gx.flags:
            return self.gx.flags
        elif os.path.isfile("FLAGS"):
            return Path("FLAGS")
        elif os.path.isfile("/etc/shedskin/FLAGS"):
            return Path("/etc/shedskin/FLAGS")
        elif PLATFORM == "Windows":
            return self.gx.shedskin_flags / "FLAGS.mingw"
        elif PLATFORM == "Darwin":
            return self.gx.shedskin_flags / "FLAGS.osx"
        return self.gx.shedskin_flags / "FLAGS"

    def _add_flag_file_options(self) -> None:
        """Add compiler and linker flags from flags file"""
        flags_file = self._get_flags_file()

        for line in open(flags_file):
            line = line[:-1]
            lvalue, rvalue = line.split("=", 1)
            variable = lvalue.strip().rstrip("?")
            entries = rvalue.split()

            if variable == "CXX":
                self.cxx = entries[0]
            elif variable == "INCLUDEDIRS":
                self.add_include_dirs(*entries)
            elif variable == "CFLAGS":
                self.add_cflags(*entries)
            elif variable == "CXXFLAGS":
                self.add_cxxflags(*entries)
            elif variable == "LINKDIRS":
                self.add_link_dirs(*entries)
            elif variable == "LDLIBS":
                self.add_ldlibs(*entries)
            elif variable == "LDFLAGS":
                self.add_ldflags(*entries)
            else:
                self.add_variable(variable, " ".join(entries))


def generate_makefile(gx: "config.GlobalInfo") -> None:
    """Generate a makefile for the Shedskin-compiled code"""
    generator = ShedskinMakefileGenerator(gx)
    generator.generate()


if __name__ == "__main__":

    def test_makefile_generator() -> None:
        """Test MakefileGenerator"""
        m = MakefileGenerator("Makefile")
        m.add_variable("TEST", "test")
        m.add_include_dirs("/usr/include")
        m.add_cflags("-Wall", "-Wextra")
        m.add_cxxflags("-Wall", "-Wextra", "-std=c++11", "-O3")
        m.add_ldflags("-shared", "-Wl,-rpath,/usr/local/lib", "-fPIC")
        m.add_link_dirs("/usr/lib", "/usr/local/lib")
        m.add_ldlibs("-lpthread")
        m.add_target("all", deps=["build", "test"])
        m.add_target("build", deps=["tool.exe"])
        m.add_target(
            "tool.exe",
            "$(CXX) $(CPPFILES) $(CXXFLAGS) $(LDFLAGS) -o $@ $^",
            deps=["a.o", "b.o"],
        )
        m.add_target("test", "echo $(TEST)", deps=["test.o"])
        m.add_phony("all", "build", "test")
        m.add_clean("test.o", "*.o")
        m.generate()

    test_makefile_generator()
