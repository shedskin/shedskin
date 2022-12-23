cmake_minimum_required(VERSION 3.19)

project(shedskin_tests LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

set(DEBUG off)

set(SHEDSKIN ${PROJECT_SOURCE_DIR}/../../shedskin)
set(SHEDSKIN_LIB ${SHEDSKIN}/shedskin/lib)

set(PROJECT_EXE_DIR ${PROJECT_BINARY_DIR}/exe)
set(PROJECT_EXT_DIR ${PROJECT_BINARY_DIR}/ext)

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/scripts)

option(TEST_EXT "build/run python extension tests")

include(CTest)

include_directories(
    ${SHEDSKIN_LIB}
)

link_directories(
    /usr/local/lib
)

if(TEST_EXT)
    find_package(Python COMPONENTS Interpreter Development)
    if(DEBUG)
        message("python:" ${Python_EXECUTABLE})
        message("python_include" ${Python_INCLUDE_DIRS})
    endif()
endif()

include(fn_add_shedskin_tests)
add_shedskin_tests()

include(fn_add_shedskin_import_test)


# -----------------------------------------------------------------------
# copy test data to cmake 'build' folder

file(COPY ${PROJECT_SOURCE_DIR}/testdata DESTINATION ${CMAKE_CURRENT_BINARY_DIR})


# -----------------------------------------------------------------------
# add tests in folders need extra or custom config

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

