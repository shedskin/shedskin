# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2025 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
#
# shedskin_deps.cmake - Centralized dependency management via FetchContent
#
# This module sets up the bdwgc dependency using FetchContent with
# a platform-specific user cache directory for persistent downloads.
#
# Usage:
#   include(shedskin_deps)
#
# After including, the following variables are available:
#   SHEDSKIN_DEP_LIBS        - Libraries to link (gc)
#   SHEDSKIN_DEP_INCLUDE_DIR - Include directory for gc/ headers
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

# On Windows, FetchContent doesn't reliably fetch git submodules.
# Fetch libatomic_ops separately and make headers available globally.
if(WIN32)
    FetchContent_Declare(
        libatomic_ops
        GIT_REPOSITORY https://github.com/ivmai/libatomic_ops.git
        GIT_TAG        v7.8.2
    )
    FetchContent_MakeAvailable(libatomic_ops)
    include_directories(${libatomic_ops_SOURCE_DIR}/src)
endif()

FetchContent_Declare(
    bdwgc
    GIT_REPOSITORY https://github.com/ivmai/bdwgc.git
    GIT_TAG        v8.2.8
    GIT_SUBMODULES_RECURSE TRUE
)

FetchContent_MakeAvailable(bdwgc)

# Create gc/ subdirectory structure for includes (shedskin expects gc/gc_allocator.h)
set(SHEDSKIN_DEP_INCLUDE_DIR ${FETCHCONTENT_BASE_DIR}/includes)
file(MAKE_DIRECTORY ${SHEDSKIN_DEP_INCLUDE_DIR}/gc)
file(GLOB _BDWGC_HEADERS "${bdwgc_SOURCE_DIR}/include/*.h")
file(COPY ${_BDWGC_HEADERS} DESTINATION ${SHEDSKIN_DEP_INCLUDE_DIR}/gc)

# Export library targets for linking
set(SHEDSKIN_DEP_LIBS gc)
