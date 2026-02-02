cmake_minimum_required(VERSION 3.18.4)

project(%(project_name)s LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)

# -----------------------------------------------------------------------------
# output directories

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

# -----------------------------------------------------------------------------
# options

option(DEBUG "Enable debug output" OFF)

option(SIMPLE_PROJECT "Project has a single target and no subprojects" %(is_simple_project)s)

option(BUILD_EXECUTABLE "Build executable" ON)
option(BUILD_EXTENSION "Build python extension" OFF)
option(BUILD_TEST "Build test" ON)
option(DISABLE_EXECUTABLES "Disable building executables" OFF)
option(DISABLE_EXTENSIONS "Disable building extensions" OFF)
option(COLLECT_STATS "Collect stats" OFF)
option(ENABLE_SPM "Enable shedskin dependency management" OFF)
option(ENABLE_CONAN "Enable conan for dependency management" OFF)
option(ENABLE_FETCH_CONTENT "Enable FetchContent for dependency mgmt" OFF)
option(ENABLE_LOCAL_DEPS "Enable local dependency management" OFF)

option(ENABLE_WARNINGS "Enable -Wall type of warnings" ON)

# -----------------------------------------------------------------------------
# reporting

message("Project: " ${PROJECT_NAME})
message("Build type: " ${CMAKE_BUILD_TYPE})
message("")

# -----------------------------------------------------------------------------
# warnings

if("${PROJECT_SOURCE_DIR}" STREQUAL "${PROJECT_BINARY_DIR}")
   message(FATAL_ERROR "In-source builds are not allowed.")
endif()

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
include(fn_add_shedskin_product)    # can build both executable and extension

# -----------------------------------------------------------------------------
# dependency mgmt solutions

if(ENABLE_SPM)
    execute_process(
        COMMAND ${Python_EXECUTABLE} -c "from shedskin import cmake; cmake.user_cache_dir()"
        OUTPUT_VARIABLE SPM_DEPS
        COMMAND_ERROR_IS_FATAL ANY
    )
    message(STATUS "SPM_DEPS: ${SPM_DEPS}")
    set(SPM_LIB_DIRS ${SPM_DEPS}/lib)
    set(SPM_INCLUDE_DIRS ${SPM_DEPS}/include)

elseif(ENABLE_CONAN)
    find_program(CONAN conan)
    if(NOT CONAN)
        message(FATAL_ERROR "conan not found, install with `pip install conan`")
    endif()
    find_package(BDWgc)
    find_package(PCRE2)

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
%(entry)s
