cmake_minimum_required(VERSION 3.19)

project(shedskin_tests LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

include(CTest)

set(SHEDSKIN ${CMAKE_SOURCE_DIR}/../../shedskin)
set(SHEDSKIN_LIB ${SHEDSKIN}/shedskin/lib)

file(GLOB test_sources "test_*.py")


include_directories(
    ${SHEDSKIN_LIB}
)

link_directories(
    /usr/local/lib
)

foreach(test_py ${test_sources})

    get_filename_component(name ${test_py} NAME_WLE)
    get_filename_component(basename_py ${test_py} NAME)

    set(APP_NAME ${name})
    set(APP ${APP_NAME})

    execute_process(
        COMMAND shedskin ${basename_py}
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        OUTPUT_QUIET
    )

    file(RENAME
        ${CMAKE_SOURCE_DIR}/${APP_NAME}.cpp 
        ${PROJECT_BINARY_DIR}/${APP_NAME}.cpp)

    file(RENAME
        ${CMAKE_SOURCE_DIR}/${APP_NAME}.hpp 
        ${PROJECT_BINARY_DIR}/${APP_NAME}.hpp)

    message("test:" ${APP})

    add_executable(${APP}
        ${PROJECT_BINARY_DIR}/${APP_NAME}.cpp
        ${PROJECT_BINARY_DIR}/${APP_NAME}.hpp
        ${SHEDSKIN_LIB}/builtin.cpp
        ${SHEDSKIN_LIB}/builtin.hpp
    )

    target_include_directories(${APP} PRIVATE
        /usr/local/include
        ${SHEDSKIN_LIB}
        ${CMAKE_SOURCE_DIR}
    )

    target_compile_options(${APP} PRIVATE
        "-O2"
        "-Wall"
        "-Wno-deprecated"
    )

    target_link_libraries(${APP} PRIVATE
        "-lgc"
        "-lgccpp"
        "-lpcre"
    )

    add_test(NAME ${APP} COMMAND ${APP})

endforeach()

# add tests which need extra config
add_subdirectory(test_prog_nnetwork)
add_subdirectory(test_prog_primes1)
add_subdirectory(test_prog_primes2)


