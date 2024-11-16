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
import re
import subprocess
import sys
import sysconfig
import platform
from pathlib import Path
from typing import TYPE_CHECKING, Optional, TypeAlias

if TYPE_CHECKING:
    from . import config
    from . import python

PathLike: TypeAlias = Path | str

PLATFORM = platform.system()


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
        return sysconfig.get_config_var('LIBPL')

    @property
    def extension_suffix(self) -> str:
        """suffix of python extension"""
        if PLATFORM == "Windows":
            return ".pyd"
        else:
            return ".so"


class MakefileGenerator:
    """Generates Makefile for C/C++ code"""
    
    def __init__(self, path: PathLike):
        self.vars: dict[str, PathLike] = {} # variables
        self.includes: set[str] = set()     # include directories
        self.cflags: set[str] = set()       # c compiler flags
        self.cxxflags: set[str] = set()     # c++ compiler flags
        self.link_dirs: set[str] = set()    # link directories
        self.link_libs: set[str] = set()    # link libraries
        self.ldflags: set[str] = set()      # linker flags
        self.targets: set[str] = set()      # targets
        self.phony: set[str] = set()        # phony targets
        self.clean: set[str] = set()        # clean target
        # writer
        self.writer = MakefileWriter(path)

    def write(self, text: Optional[str] = None) -> None:
        """Write a line to the Makefile"""
        if not text:
            self.writer.write('')
        else:
            self.writer.write(text)

    def close(self) -> None:
        """Close the Makefile"""
        self.writer.close()

    def add_variable(self, key: str, value: str) -> None:
        """Add a variable to the Makefile"""
        self.vars[key] = value

    def add_include_dirs(self, *entries, **kwargs):
        """Add include directories to the Makefile"""
        for entry in entries:
            if entry:
                self.includes.add(f"-I{entry}")
        for key, value in kwargs.items():
            if value:
                self.vars[key] = value
                self.includes.add(f"-I$({key})")
            else:
                raise ValueError(f"Invalid value for {key}: {value}")

    def add_cflags(self, *entries, **kwargs):
        """Add compiler flags to the Makefile"""
        for entry in entries:
            if entry:
                self.cflags.add(entry)
        for key, value in kwargs.items():
            if value:
                self.vars[key] = value
                self.cflags.add(f"$({key})")
            else:
                raise ValueError(f"Invalid value for {key}: {value}")

    def add_cxxflags(self, *entries, **kwargs):
        """Add c++ compiler flags to the Makefile"""
        for entry in entries:
            if entry:
                self.cxxflags.add(entry)
        for key, value in kwargs.items():
            if value:
                self.vars[key] = value
                self.cxxflags.add(f"$({key})")
            else:
                raise ValueError(f"Invalid value for {key}: {value}")

    def add_link_dirs(self, *entries, **kwargs):
        """Add link directories to the Makefile"""
        for entry in entries:
            if entry:
                self.link_dirs.add(f"-L{entry}")
        for key, value in kwargs.items():
            if value:
                self.vars[key] = value
                self.link_dirs.add(f"-L$({key})")
            else:
                raise ValueError(f"Invalid value for {key}: {value}")

    def add_link_libs(self, *entries, **kwargs):
        """Add link libraries to the Makefile"""
        for entry in entries:
            if entry:
                self.link_libs.add(entry)
        for key, value in kwargs.items():
            if value:
                self.vars[key] = value
                self.link_libs.add(f"$({key})")
            else:
                raise ValueError(f"Invalid value for {key}: {value}")

    def add_ldflags(self, *entries, **kwargs):
        """Add linker flags to the Makefile"""
        for entry in entries:
            if entry:
                self.ldflags.add(entry)
        for key, value in kwargs.items():
            if value:
                self.vars[key] = value
                self.ldflags.add(f"$({key})")
            else:
                raise ValueError(f"Invalid value for {key}: {value}")

    def add_target(self, name: str, body: Optional[str] = None, deps: Optional[list[str]] = None):
        """Add targets to the Makefile"""
        if body and deps:
            _deps = " ".join(deps)
            self.targets.add(f"{name}: {_deps}\n\t{body}")
        elif body and not deps:
            self.targets.add(f"{name}:\n\t{body}")
        elif not body and deps:
            _deps = " ".join(deps)
            self.targets.add(f"{name}: {_deps}")
        else: # no body or dependencies
            raise ValueError("Either body or dependencies must be provided")

    def add_phony(self, *entries):
        """Add phony targets to the Makefile"""
        for entry in entries:
            self.phony.add(entry)

    def add_clean(self, *entries):
        """Add clean target to the Makefile"""
        for entry in entries:
            self.clean.add(entry)

    def _write_variables(self) -> None:
        """Write variables to the Makefile"""
        for key, value in self.vars.items():
            self.write(f"{key}={value}")
        self.write()
        # write cflags
        cflags = " ".join(self.cflags)
        self.write(f"CFLAGS+={cflags}")
        self.write()
        # write cxxflags
        cxxflags = " ".join(self.cxxflags)
        self.write(f"CXXFLAGS+={cxxflags}")
        self.write()
        # write ldflags / link_dirs
        ldflags = " ".join(self.ldflags)
        link_dirs = " ".join(self.link_dirs)
        self.write(f"LDFLAGS+={ldflags} {link_dirs}")
        self.write()
        # write link_libs
        link_libs = " ".join(self.link_libs)
        self.write(f"LDLIBS+={link_libs}")
        self.write()

    def _write_phony(self) -> None:
        """Write phony targets to the Makefile"""
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
        clean_targets = " ".join(self.clean)
        self.write(f"clean:\n\t@rm -rf {clean_targets}")
        self.write()

    def generate(self) -> None:
        """Generate the Makefile"""
        self._write_variables()
        self._write_phony()
        self._write_targets()
        self._write_clean()
        self.close()


class ShedskinMakefileGenerator(MakefileGenerator):
    """Generates Makefile for Shedskin-compiled code"""
    
    def __init__(self, gx: "config.GlobalInfo"):
        self.gx = gx
        super().__init__(path=self.gx.makefile_name)
        self.esc_space = r"\ "
        self.is_static = False
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
    def modules(self) -> list['python.Module']:
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
                filename = filename.replace(self.shedskin_libdirs[-1], env_var("SHEDSKIN_LIBDIR"))
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
        self._add_user_dirs()
        
        self._write_variables()
        self._write_targets()
        self._write_clean()
        self._write_phony()

        self.writer.close()

    def _setup_variables(self) -> None:
        """Configure general variables"""
        self.vars['SHEDSKIN_LIBDIR'] = self.shedskin_libdirs[-1]
        self.vars['PY_INCLUDE'] = self.py.include_dir
        if prefix := self.homebrew_prefix():
            self.vars["HOMEBREW_PREFIX"] = prefix
            self.vars["HOMEBREW_INCLUDE"] = prefix / 'include'
            self.vars["HOMEBREW_LIB"] = prefix / 'lib'
            self.add_include_dirs("$(HOMEBREW_INCLUDE)")
            self.add_link_dirs("$(HOMEBREW_LIB)")

    def _setup_platform(self) -> None:
        """Configure platform-specific settings"""
        if PLATFORM == "Windows":
            self._setup_windows()
        else:
            self._setup_unix()
            
    def _setup_windows(self) -> None:
        """Configure Windows-specific settings"""
        # placeholder
        
    def _setup_unix(self) -> None:
        """Configure Unix-like platform settings"""
        if self.py.include_dir != self.py.config_h_dir:
            self.add_include_dirs(
                "$(PY_INCLUDE)",
                self.py.config_h_dir,
            )
        else:
            self.add_include_dirs("$(PY_INCLUDE)")
        if PLATFORM == "Darwin":
            self.add_ldflags(self.py.base_cflags)
        else:
            self.add_ldflags(
                self.py.libs,
                self.py.syslibs,
                self.py.linklib,
            )
            if not self.py.is_shared:
                self.add_link_dirs(self.py.libpl)
    
    def _add_user_dirs(self) -> None:
        """Add user-specified include and link directories"""
        if self.gx.options.include_dirs:
            for include_dir in self.gx.options.include_dirs:
                self.add_include_dirs(include_dir)
        if self.gx.options.link_dirs:
            for link_dir in self.gx.options.link_dirs:
                self.add_link_dirs(link_dir)
    
    def _write_variables(self) -> None:
        """Write variables to the Makefile"""
        self.write("SHEDSKIN_LIBDIR=%s" % self.shedskin_libdirs[-1])
        self.write("PY_INCLUDE=%s" % self.py.include_dir)
        if PLATFORM == "Darwin":
            if self.homebrew_prefix():
                prefix = self.homebrew_prefix()
                self.write(f"HOMEBREW_PREFIX={prefix}")
                self.write(f"HOMEBREW_INCLUDE={prefix}/include")
                self.write(f"HOMEBREW_LIB={prefix}/lib")
        self._write_flags()
        self._write_cpp_files()
        
    def _write_cpp_files(self) -> None:
        """Write C++ source and header file lists"""
        cppfiles_str = " \\\n\t".join(self.cppfiles)
        hppfiles_str = " \\\n\t".join(self.hppfiles)
        self.write("CPPFILES=%s\n" % cppfiles_str)
        self.write("HPPFILES=%s\n" % hppfiles_str)
        
    def _write_flags(self) -> None:
        """Write compiler and linker flags"""
        flags_file = self._get_flags_file()
        includes = " ".join(self.includes)
        ldflags = " ".join(self.ldflags)
        
        for line in open(flags_file):
            line = line[:-1]
            variable = line[: line.find("=")].strip().rstrip("?")
            
            if variable == "CXXFLAGS":
                line = self._update_cxx_flags(line, includes)
            elif variable == "LFLAGS":
                line = self._update_linker_flags(line, ldflags)
                
            self.write(line)
            self.write()
            
            self._handle_static_flags(line)
            
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
            
    def _update_cxx_flags(self, line: str, includes: str) -> str:
        """Update C++ compiler flags"""
        line += " -I. -I%s" % env_var("SHEDSKIN_LIBDIR")
        line += "".join(" -I" + libdir for libdir in self.shedskin_libdirs[:-1])
        line += " " + includes
        
        if PLATFORM == "Darwin":
            if os.path.isdir("/usr/local/include"):
                line += " -I/usr/local/include"
            if os.path.isdir("/opt/local/include"):
                line += " -I/opt/local/include"
                
        line = self._add_feature_flags(line)
        line = self._add_extension_flags(line, includes)
        return line
        
    def _add_feature_flags(self, line: str) -> str:
        """Add feature-specific compiler flags"""
        if not self.gx.wrap_around_check:
            line += " -D__SS_NOWRAP"
        if not self.gx.bounds_checking:
            line += " -D__SS_NOBOUNDS"
        if not self.gx.assertions:
            line += " -D__SS_NOASSERT"
        if self.gx.int32:
            line += " -D__SS_INT32"
        if self.gx.int64:
            line += " -D__SS_INT64"
        if self.gx.int128:
            line += " -D__SS_INT128"
        if self.gx.float32:
            line += " -D__SS_FLOAT32"
        if self.gx.float64:
            line += " -D__SS_FLOAT64"
        if self.gx.backtrace:
            line += " -D__SS_BACKTRACE -rdynamic -fno-inline"
        if self.gx.nogc:
            line += " -D__SS_NOGC"
        return line
        
    def _add_extension_flags(self, line: str, includes: str) -> str:
        """Add Python extension-specific flags"""
        if self.gx.pyextension_product:
            if PLATFORM == "Windows":
                line += " -I%s\\include -D__SS_BIND" % self.py.prefix
            else:
                line += " -g -fPIC -D__SS_BIND " + includes
        return line
        
    def _update_linker_flags(self, line: str, ldflags: str) -> str:
        """Update linker flags"""
        line += ldflags
        
        if PLATFORM == "Darwin":
            if os.path.isdir("/opt/local/lib"):
                line += " -L/opt/local/lib"
            if os.path.isdir("/usr/local/lib"):
                line += " -L/usr/local/lib"
                
        line = self._add_extension_linker_flags(line, ldflags)
        line = self._add_module_linker_flags(line)
        return line
        
    def _add_extension_linker_flags(self, line: str, ldflags: str) -> str:
        """Add Python extension-specific linker flags"""
        if self.gx.pyextension_product:
            if PLATFORM == "Windows":
                line += " -shared -L%s\\libs -lpython%s" % (self.py.prefix, self.py.ver)
            elif PLATFORM == "Darwin":
                line += " -bundle -undefined dynamic_lookup " + ldflags
            elif PLATFORM == "SunOS":
                line += " -shared -Xlinker " + ldflags
            else:
                line += " -Wno-register -shared -Xlinker -export-dynamic " + ldflags
        return line
        
    def _add_module_linker_flags(self, line: str) -> str:
        """Add module-specific linker flags"""
        module_ids = [m.ident for m in self.modules]
        
        if "re" in module_ids:
            line += " -lpcre"
        if "socket" in module_ids:
            if PLATFORM == "Windows":
                line += " -lws2_32"
            elif PLATFORM == "SunOS":
                line += " -lsocket -lnsl"
        if "os" in module_ids:
            if PLATFORM not in ["Windows", "Darwin", "SunOS"]:
                line += " -lutil"
        if "hashlib" in module_ids:
            line += " -lcrypto"
        return line
        
    def _handle_static_flags(self, line: str) -> None:
        """Handle static linking configuration"""
        MATCH = re.match(r"^LFLAGS=(.+)(\$\(LDFLAGS\).+)", line)
        if PLATFORM == "Darwin" and self.homebrew_prefix() and MATCH:
            self.is_static = True
            self._write_static_vars(MATCH.group(2))
            
    def _write_static_vars(self, ldflags: str) -> None:
        """Write static linking variables"""
        self.write("STATIC_PREFIX=$(shell brew --prefix)")
        self.write("STATIC_LIBDIR=$(STATIC_PREFIX)/lib")
        self.write("STATIC_INCLUDE=$(STATIC_PREFIX)/include")
        self.write()
        self.write("GC_STATIC=$(STATIC_LIBDIR)/libgc.a")
        self.write("GCCPP_STATIC=$(STATIC_LIBDIR)/libgccpp.a")
        self.write("GC_INCLUDE=$(STATIC_INCLUDE)/include")
        self.write("PCRE_STATIC=$(STATIC_LIBDIR)/libpcre.a")
        self.write("PCRE_INCLUDE=$(STATIC_INCLUDE)/include")
        self.write()
        self.write("STATIC_LIBS=$(GC_STATIC) $(GCCPP_STATIC) $(PCRE_STATIC)")
        self.write("STATIC_CXXFLAGS=$(CXXFLAGS) -I$(GC_INCLUDE) -I$(PCRE_INCLUDE)")
        self.write("STATIC_LFLAGS=" + ldflags)
        self.write()

    def _write_targets(self) -> None:
        """Write targets to the Makefile"""
        self.write("all:\t" + self.target_name + "\n")

        # executable (normal, debug, profile) or extension module
        _out = "-o "
        _ext = ""
        targets = [("", "")]
        if not self.gx.pyextension_product:
            targets += [("_prof", "-pg -ggdb"), ("_debug", "-g -ggdb")]

        for suffix, options in targets:
            self.write(self.target_name + suffix + ":\t$(CPPFILES) $(HPPFILES)")
            self.write(
                "\t$(CXX) "
                + options
                + " $(CXXFLAGS) $(CPPFILES) $(LFLAGS) "
                + _out
                + self.target_name
                + suffix
                + _ext
                + "\n"
            )

        # if PLATFORM == "Darwin" and self.homebrew_prefix() and MATCH:
        if PLATFORM == "Darwin" and self.is_static:
            # static option
            self.write("static: $(CPPFILES) $(HPPFILES)")
            self.write(
                f"\t$(CXX) $(STATIC_CXXFLAGS) $(CPPFILES) $(STATIC_LIBS) $(STATIC_LFLAGS) -o {self.target_name}\n"
            )

    def _write_clean(self) -> None:
        """Write clean target to the Makefile"""
        ext = ""
        if PLATFORM == "Windows" and not self.gx.pyextension_product:
            ext = ".exe"
        self.write("clean:")
        _targets = [self.target_name + ext]
        if not self.gx.pyextension_product:
            _targets += [self.target_name + "_prof" + ext, self.target_name + "_debug" + ext]
        self.write("\trm -f %s" % " ".join(_targets))
        if PLATFORM == "Darwin":
            self.write("\trm -rf %s.dSYM\n" % " ".join(_targets))
        self.write()

    def _write_phony(self) -> None:
        """Write phony targets to the Makefile"""
        phony = ".PHONY: all clean"
        if PLATFORM == "Darwin" and self.is_static:
        # if PLATFORM == "Darwin" and HOMEBREW and MATCH:
            phony += " static"
        phony += "\n"
        self.write(phony)


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
        m.add_link_libs("-lpthread")
        m.add_target("all", deps=["build", "test"])
        m.add_target("build", deps=["tool.exe"])
        m.add_target("tool.exe", "$(CXX) $(CPPFILES) $(CXXFLAGS) $(LDFLAGS) -o $@ $^", deps=["a.o", "b.o"])
        m.add_target("test", "echo $(TEST)", deps=["test.o"])
        m.add_phony("all", "build","test")
        m.add_clean("test.o", "*.o")
        m.generate()

    test_makefile_generator()
