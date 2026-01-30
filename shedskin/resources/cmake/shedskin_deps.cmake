# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2025 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
#
# shedskin_deps.cmake - Centralized dependency management via FetchContent
#
# This module sets up bdwgc and pcre2 dependencies using FetchContent with
# a platform-specific user cache directory for persistent downloads.
#
# Usage:
#   include(shedskin_deps)
#
# After including, the following variables are available:
#   SHEDSKIN_DEP_LIBS        - Libraries to link (gc, gccpp, pcre2-8-static)
#   SHEDSKIN_DEP_INCLUDE_DIR - Include directory for gc/ headers
#   SHEDSKIN_PCRE2_INCLUDE_DIR - Include directory for pcre2.h
#

# Guard against multiple inclusion
if(SHEDSKIN_DEPS_INCLUDED)
    return()
endif()
set(SHEDSKIN_DEPS_INCLUDED TRUE)

# Get user cache directory from Python
execute_process(
    COMMAND ${Python_EXECUTABLE} -c "from shedskin import cmake; cmake.user_cache_dir()"
    OUTPUT_VARIABLE SHEDSKIN_USER_CACHE
    OUTPUT_STRIP_TRAILING_WHITESPACE
    COMMAND_ERROR_IS_FATAL ANY
)

# Set FetchContent base directory for persistent caching
set(FETCHCONTENT_BASE_DIR "${SHEDSKIN_USER_CACHE}/fetchcontent" CACHE PATH "" FORCE)
message(STATUS "FETCHCONTENT_BASE_DIR: ${FETCHCONTENT_BASE_DIR}")

include(FetchContent)

# Configure bdwgc options before fetching
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(enable_cplusplus ON CACHE BOOL "" FORCE)
set(build_cord OFF CACHE BOOL "" FORCE)
set(install_headers OFF CACHE BOOL "" FORCE)

# On MSVC, bdwgc expects libatomic_ops submodule which isn't fetched reliably.
# Force use of compiler intrinsics instead via GC_BUILTIN_ATOMIC.
if(MSVC)
    add_compile_definitions(GC_BUILTIN_ATOMIC)
endif()

FetchContent_Declare(
    bdwgc
    GIT_REPOSITORY https://github.com/ivmai/bdwgc.git
    GIT_TAG        v8.2.8
    GIT_SUBMODULES_RECURSE true
    GIT_SHALLOW    true
)

# Configure pcre2 options before fetching
set(PCRE2_BUILD_PCRE2_8 ON CACHE BOOL "" FORCE)
set(PCRE2_BUILD_PCRE2_16 OFF CACHE BOOL "" FORCE)
set(PCRE2_BUILD_PCRE2_32 OFF CACHE BOOL "" FORCE)
set(PCRE2_SUPPORT_JIT OFF CACHE BOOL "" FORCE)
set(PCRE2_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(PCRE2_BUILD_PCRE2GREP OFF CACHE BOOL "" FORCE)

FetchContent_Declare(
    pcre2
    GIT_REPOSITORY https://github.com/PCRE2Project/pcre2.git
    GIT_TAG        pcre2-10.44
    GIT_SHALLOW    TRUE
)

FetchContent_MakeAvailable(bdwgc pcre2)

# Create gc/ subdirectory structure for includes (shedskin expects gc/gc_allocator.h)
set(SHEDSKIN_DEP_INCLUDE_DIR ${FETCHCONTENT_BASE_DIR}/includes)
file(MAKE_DIRECTORY ${SHEDSKIN_DEP_INCLUDE_DIR}/gc)
file(GLOB _BDWGC_HEADERS "${bdwgc_SOURCE_DIR}/include/*.h")
file(COPY ${_BDWGC_HEADERS} DESTINATION ${SHEDSKIN_DEP_INCLUDE_DIR}/gc)

# pcre2.h is generated in the build directory
set(SHEDSKIN_PCRE2_INCLUDE_DIR ${pcre2_BINARY_DIR})

# Export library targets for linking
set(SHEDSKIN_DEP_LIBS gc gccpp pcre2-8-static)
