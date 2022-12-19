cmake_minimum_required(VERSION 3.19)

project(shedskin_tests LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(DEBUG off)

set(SHEDSKIN ${CMAKE_SOURCE_DIR}/../../shedskin)
set(SHEDSKIN_LIB ${SHEDSKIN}/shedskin/lib)
set(SCRIPTS ${CMAKE_SOURCE_DIR}/scripts)

option(ONLY_EXTS "build/run only python extension tests")

include(CTest)

include_directories(
    ${SHEDSKIN_LIB}
)

link_directories(
    /usr/local/lib
)

if(ONLY_EXTS)
    # build/test python extension tests
    find_package(Python COMPONENTS Interpreter Development)
    if(DEBUG)
        message("python:" ${Python_EXECUTABLE})
        message("python_include" ${Python_INCLUDE_DIRS})
    endif()
    include(${SCRIPTS}/fn_add_shedskin_ext_tests.cmake)
    add_shedskin_ext_tests()
    include(${SCRIPTS}/fn_add_shedskin_ext_import_test.cmake)
else()
    # build/test compiled executable tests
    include(${SCRIPTS}/fn_add_shedskin_exe_tests.cmake)
    add_shedskin_exe_tests()
    include(${SCRIPTS}/fn_add_shedskin_exe_import_test.cmake)
endif()

# -----------------------------------------------------------------------
# copy test data to cmake 'build' folder

file(COPY ${CMAKE_SOURCE_DIR}/testdata DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
file(COPY ${CMAKE_SOURCE_DIR}/test_hello.py DESTINATION ${CMAKE_CURRENT_BINARY_DIR})


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



