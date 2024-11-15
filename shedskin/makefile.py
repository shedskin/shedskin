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
import pathlib
import re
import subprocess
import sys
import sysconfig
import platform 
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from . import config

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
    def __init__(self, path: str):
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
    def version(self):
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
        return f"-l{self.ver_name}"

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
        if PLATFORM == "Darwin":
            return f"{self.libname}.dylib"
        if PLATFORM == "Linux":
            return f"{self.libname}.so"
        if PLATFORM == "Windows":
            return f"{self.libname}.dll"

    @property
    def dylib_linkname(self) -> str:
        """symlink to dylib"""
        if PLATFORM == "Darwin":
            return f"{self.libname}.dylib"
        if PLATFORM == "Linux":
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
    """Generates Makefile for Shedskin-compiled code"""
    
    def __init__(self, gx: "config.GlobalInfo"):
        self.gx = gx
        self.includes = []
        self.ldflags = []
        self.writer = None
        self.esc_space = r"\ "
        self.is_static = False
        self.py = PythonSystem()

    @property
    def shedskin_libdirs(self):
        """List of shedskin libdirs"""
        return [d.replace(" ", self.esc_space) for d in self.gx.libdirs]
    
    @property
    def modules(self):
        """List of modules"""
        return self.gx.modules.values()
    
    @property
    def filenames(self):
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
    def cppfiles(self):
        """Reverse sorted list of .cpp files"""
        return sorted([fn + ".cpp" for fn in self.filenames], reverse=True)

    @property
    def hppfiles(self):
        """Reverse sorted list of .hpp files"""
        return sorted([fn + ".hpp" for fn in self.filenames], reverse=True)

    @property
    def target_name(self) -> str:
        """Get the target executable/library name"""
        if self.gx.pyextension_product: 
            return f"{self.gx.main_module.ident}{self.py.extension_suffix}"
        else:
            return self.gx.main_module.ident

    @property
    def makefile_path(self) -> str:
        """Get the Makefile output path"""
        if self.gx.outputdir:
            return os.path.join(self.gx.outputdir, self.gx.makefile_name)
        return self.gx.makefile_name

    def write(self, text: Optional[str] = None) -> None:
        """Write a line to the Makefile"""
        if not text:
            self.writer.write('')
        else:
            self.writer.write(text)

    def add_include_dirs(self, *entries):
        """Add include directories to the Makefile"""
        for entry in entries:
            if entry:
                self.includes.append(f"-I{entry}")
        
    def add_link_dirs(self, *entries):
        """Add link directories to the Makefile"""
        for entry in entries:
            if entry:
                self.ldflags.append(f"-L{entry}")
        
    def add_ldflags(self, *entries):
        """Add linker flags to the Makefile"""
        for entry in entries:
            if entry:
                self.ldflags.append(entry)

    def homebrew_prefix(self, entry: Optional[str] = None) -> Optional[str]:
        """Get Homebrew prefix"""
        if entry:
            return check_output(f"brew --prefix {entry}")
        else:
            return check_output("brew --prefix")

    def generate(self) -> None:
        """Generate the Makefile"""
        if self.gx.nomakefile:
            return
            
        self._setup_platform()
        self._add_user_dirs()
        
        self.writer = MakefileWriter(self.makefile_path)
        
        self._write_variables()
        self._write_targets()
        self._write_clean()
        self._write_phony()
        
        self.writer.close()

    def _setup_platform(self) -> None:
        """Configure platform-specific settings"""
        if PLATFORM == "Windows":
            self._setup_windows()
        else:
            self._setup_unix()
            
    def _setup_windows(self) -> None:
        """Configure Windows-specific settings"""
        
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
                self.write("HOMEBREW_PREFIX=%s" % self.homebrew_prefix())
                self.write("HOMEBREW_INCLUDE=%s/include" % self.homebrew_prefix())
                self.write("HOMEBREW_LIB=%s/lib" % self.homebrew_prefix())
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
        flags = self._get_flags_file()
        includes = " ".join(self.includes)
        ldflags = " ".join(self.ldflags)
        
        for line in open(flags):
            line = line[:-1]
            variable = line[: line.find("=")].strip().rstrip("?")
            
            if variable == "CXXFLAGS":
                line = self._update_cxx_flags(line, includes)
            elif variable == "LFLAGS":
                line = self._update_linker_flags(line, ldflags)
                
            self.write(line)
            self.write()
            
            self._handle_static_flags(line)
            
    def _get_flags_file(self) -> pathlib.Path:
        """Get the appropriate flags file for the current platform"""
        if self.gx.flags:
            return self.gx.flags
        elif os.path.isfile("FLAGS"):
            return pathlib.Path("FLAGS")
        elif os.path.isfile("/etc/shedskin/FLAGS"):
            return pathlib.Path("/etc/shedskin/FLAGS")
        elif PLATFORM == "Windows":
            return self.gx.shedskin_flags / "FLAGS.mingw"
        elif PLATFORM == "Darwin":
            self._setup_homebrew()
            return self.gx.shedskin_flags / "FLAGS.osx"
        return self.gx.shedskin_flags / "FLAGS"
        
    def _setup_homebrew(self) -> None:
        """Configure Homebrew paths if available"""
        if self.homebrew_prefix():
            self.add_include_dirs("$(HOMEBREW_INCLUDE)")
            self.add_link_dirs("$(HOMEBREW_LIB)")
            
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
    generator = MakefileGenerator(gx)
    generator.generate()
