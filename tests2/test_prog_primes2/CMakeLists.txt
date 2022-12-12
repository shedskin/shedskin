# cmake_minimum_required(VERSION 3.19)

# project(shedskin_tests LANGUAGES CXX)

# set(CMAKE_CXX_STANDARD 17)

include(CTest)

message("CMAKE_SOURCE_DIR: " ${CMAKE_SOURCE_DIR})
message("CMAKE_CURRENT_SOURCE_DIR: " ${CMAKE_CURRENT_SOURCE_DIR})

set(SHEDSKIN ${CMAKE_SOURCE_DIR}/../../shedskin)
set(SHEDSKIN_LIB ${SHEDSKIN}/shedskin/lib)

include_directories(
    ${SHEDSKIN_LIB}
)

link_directories(
    /usr/local/lib
)

get_filename_component(name ${CMAKE_CURRENT_SOURCE_DIR} NAME_WLE)
get_filename_component(basename_py ${CMAKE_CURRENT_SOURCE_DIR} NAME)

message("name: " ${name})
message("basename_py:" ${basename_py})

set(APP_NAME ${name})
set(APP ${APP_NAME})

execute_process(
    COMMAND shedskin ${basename_py}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    OUTPUT_QUIET
)


file(RENAME
    ${CMAKE_CURRENT_SOURCE_DIR}/${APP_NAME}.cpp 
    ${PROJECT_BINARY_DIR}/${APP_NAME}.cpp)

file(RENAME
    ${CMAKE_CURRENT_SOURCE_DIR}/${APP_NAME}.hpp 
    ${PROJECT_BINARY_DIR}/${APP_NAME}.hpp)

message("APP:" ${APP})

add_executable(${APP}
    ${PROJECT_BINARY_DIR}/${APP_NAME}.cpp
    ${PROJECT_BINARY_DIR}/${APP_NAME}.hpp
    ${SHEDSKIN_LIB}/builtin.cpp
    ${SHEDSKIN_LIB}/builtin.hpp
    ${SHEDSKIN_LIB}/math.cpp
    ${SHEDSKIN_LIB}/math.hpp
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

