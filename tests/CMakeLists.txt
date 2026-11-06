cmake_minimum_required(VERSION 3.18.4)

project(shedskin_products LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)

# -----------------------------------------------------------------------------
# options

option(DEBUG "Enable debug output" OFF)

option(BUILD_EXECUTABLE "Build executable" ON)
option(BUILD_EXTENSION "Build python extension" OFF)
option(BUILD_TEST "Build test" ON)

option(ENABLE_SPM "Enable shedskin dependency management" OFF)
option(ENABLE_FETCH_CONTENT "Enable FetchContent for dependency mgmt" OFF)
option(ENABLE_LOCAL_DEPS "Enable local dependency management" OFF)

# -----------------------------------------------------------------------------
# find python executable and shedskin package path

find_package(Python REQUIRED COMPONENTS Interpreter Development)
if(DEBUG)
    message("python:" ${Python_EXECUTABLE})
    message("python_include:" ${Python_INCLUDE_DIRS})
endif()

# -----------------------------------------------------------------------------
# find shedskin package path

if(NOT DEFINED SHEDSKIN)
    execute_process(
        COMMAND ${Python_EXECUTABLE} -c "from shedskin import pkg_path; pkg_path()"
        OUTPUT_VARIABLE SHEDSKIN_PATH
        COMMAND_ERROR_IS_FATAL ANY
    )
    set(SHEDSKIN ${SHEDSKIN_PATH} CACHE PATH "setting path to shedskin pkg" FORCE)
endif()

set(SHEDSKIN_LIB ${SHEDSKIN}/lib)

include_directories(
    ${SHEDSKIN_LIB}
)

# -----------------------------------------------------------------------------
# includes (must be before dependency mgmt to find shedskin_deps module)
list(APPEND CMAKE_MODULE_PATH "${SHEDSKIN}/resources/cmake")
include(utils)
include(fn_add_shedskin_product)

set(shedskin_lib_modules
    array
    base64
    binascii
    bisect
    builtin
    collections
    colorsys
    configparser
    copy
    csv
    datetime
    fnmatch
    functools
    gc
    getopt
    glob
    gzip
    heapq
    io
    itertools
    math
    math.integer
    mmap
    os
    os.path
    random
    re
    select
    signal
    socket
    stat
    string
    struct
    sys
    termios
    time
    tty
)

set(shedskin_library_sources)
foreach(mod ${shedskin_lib_modules})
# special case os, os.path
if(mod STREQUAL "os")
    list(APPEND shedskin_library_sources "${SHEDSKIN_LIB}/os/__init__.cpp")
    list(APPEND shedskin_library_sources "${SHEDSKIN_LIB}/os/__init__.hpp")
elseif(mod STREQUAL "os.path")
    list(APPEND shedskin_library_sources "${SHEDSKIN_LIB}/os/path.cpp")
    list(APPEND shedskin_library_sources "${SHEDSKIN_LIB}/os/path.hpp")
elseif(mod STREQUAL "math")
    list(APPEND shedskin_library_sources "${SHEDSKIN_LIB}/math/__init__.cpp")
    list(APPEND shedskin_library_sources "${SHEDSKIN_LIB}/math/__init__.hpp")
elseif(mod STREQUAL "math.integer")
    list(APPEND shedskin_library_sources "${SHEDSKIN_LIB}/math/integer.cpp")
    list(APPEND shedskin_library_sources "${SHEDSKIN_LIB}/math/integer.hpp")
else()
    list(APPEND shedskin_library_sources "${SHEDSKIN_LIB}/${mod}.cpp")
    list(APPEND shedskin_library_sources "${SHEDSKIN_LIB}/${mod}.hpp")
endif()
endforeach()

add_library(shedskin_library_exe ${shedskin_library_sources})

target_compile_options(shedskin_library_exe PRIVATE
    ${SHEDSKIN_COMPILE_OPTIONS}
    ${SHEDSKIN_OPT_FLAGS}
    $<$<BOOL:${UNIX}>:-ffp-contract=off> # no FMA contraction: match CPython float results
    $<$<BOOL:${UNIX}>:-Wno-unused-variable>
    $<$<BOOL:${UNIX}>:-Wno-unused-parameter>
    $<$<BOOL:${UNIX}>:-Wno-unused-but-set-variable>
    $<$<BOOL:${UNIX}>:-Wno-unused-result>
    $<$<BOOL:${UNIX}>:-Wno-missing-field-initializers>
    $<$<BOOL:${UNIX}>:-Wno-cast-function-type> # (PyCFunction) cast in extmods
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wall>
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wextra>
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wpedantic>
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wconversion>
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wsign-compare>
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wformat=2>
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wwrite-strings>
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wredundant-decls>
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wmissing-include-dirs>
    # windows
    $<$<AND:$<BOOL:${WIN32}>,$<BOOL:${ENABLE_WARNINGS}>>:/W4>
    $<$<AND:$<BOOL:${WIN32}>,$<BOOL:${ENABLE_WARNINGS}>>:/wd4100> # unreferenced formal
    $<$<AND:$<BOOL:${WIN32}>,$<BOOL:${ENABLE_WARNINGS}>>:/wd4101> # unreferenced local var
    $<$<BOOL:${WIN32}>:${WIN32_FLAGS}>
)

# GC_NOT_DLL is required on Windows when linking statically with bdwgc
# PCRE2_STATIC is required on Windows when linking statically with pcre2
# boost (bundled) containers are the default, as for 'shedskin build'
target_compile_definitions(shedskin_library_exe PRIVATE
    $<$<NOT:$<BOOL:${SHEDSKIN_NOBOOST}>>:__SS_BOOST>
    $<$<AND:$<BOOL:${WIN32}>,$<BOOL:${USING_STATIC_GC}>>:GC_NOT_DLL>
    $<$<AND:$<BOOL:${WIN32}>,$<BOOL:${USING_STATIC_GC}>,$<BOOL:${IMPORTS_RE_MODULE}>>:PCRE2_STATIC>
)


add_library(shedskin_library_ext ${shedskin_library_sources})

target_include_directories(shedskin_library_ext PRIVATE
    ${Python_INCLUDE_DIRS}
)
target_compile_options(shedskin_library_ext PRIVATE
    ${SHEDSKIN_COMPILE_OPTIONS}
    # common
    "-D__SS_BIND"
    # unix
    $<$<BOOL:${UNIX}>:-DNDEBUG>
    $<$<BOOL:${UNIX}>:-fPIC>
    $<$<BOOL:${UNIX}>:-fwrapv>
    $<$<BOOL:${UNIX}>:-g>
    ${SHEDSKIN_OPT_FLAGS}
    $<$<BOOL:${UNIX}>:-ffp-contract=off> # no FMA contraction: match CPython float results
    # hide all symbols by default so shedskin's Boehm-GC-backed
    # operator new/delete (and other runtime internals) don't leak
    # into the process-global symbol table and interpose over the
    # same symbols in other C++ extensions (e.g. numpy) loaded into
    # the same host process; PyMODINIT_FUNC forces the entry point
    # back to default visibility via Py_EXPORTED_SYMBOL, so the
    # module still loads correctly
    $<$<BOOL:${UNIX}>:-fvisibility=hidden>
    $<$<BOOL:${UNIX}>:-fvisibility-inlines-hidden>
    $<$<BOOL:${UNIX}>:-Wno-unused-result>
    $<$<BOOL:${UNIX}>:-Wno-unused-variable>
    $<$<BOOL:${UNIX}>:-Wno-unused-parameter>
    $<$<BOOL:${UNIX}>:-Wno-unused-but-set-variable>
    $<$<BOOL:${UNIX}>:-Wno-missing-field-initializers>
    $<$<BOOL:${UNIX}>:-Wno-cast-function-type> # (PyCFunction) cast in extmods
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wall>
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wextra>
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wconversion>
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-Wsign-compare>
    $<$<AND:$<BOOL:${UNIX}>,$<BOOL:${ENABLE_WARNINGS}>>:-pedantic>
    # windows
    $<$<AND:$<BOOL:${WIN32}>,$<BOOL:${ENABLE_WARNINGS}>>:/W4>
    $<$<AND:$<BOOL:${WIN32}>,$<BOOL:${ENABLE_WARNINGS}>>:/wd4100> # unreferenced formal
    $<$<AND:$<BOOL:${WIN32}>,$<BOOL:${ENABLE_WARNINGS}>>:/wd4101> # unreferenced local var
    $<$<BOOL:${WIN32}>:${WIN32_FLAGS}>
    # $<$<BOOL:${WIN32}>:/LD>
)

# GC_NOT_DLL is required on Windows when linking statically with bdwgc
# PCRE2_STATIC is required on Windows when linking statically with pcre2
target_compile_definitions(shedskin_library_ext PRIVATE
    $<$<NOT:$<BOOL:${SHEDSKIN_NOBOOST}>>:__SS_BOOST>
    $<$<AND:$<BOOL:${WIN32}>,$<BOOL:${USING_STATIC_GC}>>:GC_NOT_DLL>
    $<$<AND:$<BOOL:${WIN32}>,$<BOOL:${USING_STATIC_GC}>,$<BOOL:${IMPORTS_RE_MODULE}>>:PCRE2_STATIC>
)

# -----------------------------------------------------------------------------
# dependency mgmt solutions

if(ENABLE_SPM)
    set(SPM_DEPS ${CMAKE_BINARY_DIR}/deps)
    set(SPM_LIB_DIRS ${SPM_DEPS}/lib)
    set(SPM_INCLUDE_DIRS ${SPM_DEPS}/include)

elseif(ENABLE_FETCH_CONTENT)
    include(shedskin_deps)
    set(FETCHCONTENT_INCLUDE_DIR ${SHEDSKIN_DEP_INCLUDE_DIR})
    set(FETCHCONTENT_PCRE2_INCLUDE_DIR ${SHEDSKIN_PCRE2_INCLUDE_DIR})

elseif(ENABLE_LOCAL_DEPS)
    if(NOT DEFINED LOCAL_DEPS_DIR)
        message(FATAL_ERROR "LOCAL_DEPS_DIR must be defined when ENABLE_LOCAL_DEPS is ON")
    endif()
    message(STATUS "LOCAL_DEPS_DIR: ${LOCAL_DEPS_DIR}")
    set(LOCAL_DEPS_LIB_DIRS ${LOCAL_DEPS_DIR}/lib)
    set(LOCAL_DEPS_INCLUDE_DIRS ${LOCAL_DEPS_DIR}/include)
endif()

# -----------------------------------------------------------------------
# any 'test_*' folders are automatically treated as tests

if(BUILD_TEST)
    enable_testing()
    if (EXISTS ${PROJECT_SOURCE_DIR}/testdata)
        # copy test data to cmake 'build' folder
        file(COPY ${PROJECT_SOURCE_DIR}/testdata DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
    endif()

    # add_subdirectory(tests)
    file(GLOB test_dirs "test_*"
        LIST_DIRECTORIES true
    )

    foreach(testdir ${test_dirs})
        if(IS_DIRECTORY ${testdir})
            get_filename_component(testdir_name ${testdir} NAME_WLE)
            if (DEBUG)
                message("testdir_name:" ${testdir_name})
            endif()
            add_subdirectory(${testdir_name})
        endif()
    endforeach()
endif()


# -----------------------------------------------------------------------
# add subdirectories here
