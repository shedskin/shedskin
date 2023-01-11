cmake_minimum_required(VERSION 3.19)

project(shedskin_examples LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

set(DEBUG off)

set(SHEDSKIN ${PROJECT_SOURCE_DIR}/../../shedskin)
set(SHEDSKIN_LIB ${SHEDSKIN}/shedskin/lib)

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/_cmake)

option(AS_EXT "build/run python extension examples")
option(NO_BOUNDS "enable no bounds checking")

if(NO_BOUNDS)
    set(OPT_B "-b")
else()
    set(OPT_B "")
endif()

include_directories(
    ${SHEDSKIN_LIB}
)

link_directories(
    /usr/local/lib
)

find_package(Python COMPONENTS Interpreter Development)
if(DEBUG)
    message("python:" ${Python_EXECUTABLE})
    message("python_include" ${Python_INCLUDE_DIRS})
endif()

include(fn_add_shedskin_example)
include(fn_add_shedskin_exe_example)
include(fn_add_shedskin_ext_example)
include(fn_copy_to_build_dir)


# -----------------------------------------------------------------------
# copy test data to cmake 'build' folder

file(COPY ${PROJECT_SOURCE_DIR}/testdata DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

# -----------------------------------------------------------------------
# add examples (_cmake/subdirs.cmake)
include(subdirs)


