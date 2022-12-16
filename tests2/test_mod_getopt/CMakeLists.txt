include(CTest)


set(SHEDSKIN ${CMAKE_SOURCE_DIR}/../../shedskin)
set(SHEDSKIN_LIB ${SHEDSKIN}/shedskin/lib)


include_directories(
    ${SHEDSKIN_LIB}
)

link_directories(
    /usr/local/lib
)

get_filename_component(name ${CMAKE_CURRENT_SOURCE_DIR} NAME_WLE)

# message("name: " ${name})
set(basename_py "${name}.py")

set(APP_NAME ${name})
set(APP ${APP_NAME})

set(translated_files
    ${PROJECT_BINARY_DIR}/${APP_NAME}.cpp
    ${PROJECT_BINARY_DIR}/${APP_NAME}.hpp
)

add_custom_command(OUTPUT ${translated_files}
    COMMAND shedskin --nomakefile -o ../build "${basename_py}"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DEPENDS "${basename_py}"
    COMMENT "translating ${basename_py}"
    VERBATIM
)

add_custom_target(shedskin_${APP} DEPENDS ${translated_files})

# message("test:" ${APP})

add_executable(${APP}
    ${PROJECT_BINARY_DIR}/${APP_NAME}.cpp
    ${PROJECT_BINARY_DIR}/${APP_NAME}.hpp
    ${SHEDSKIN_LIB}/builtin.cpp
    ${SHEDSKIN_LIB}/builtin.hpp
    ${SHEDSKIN_LIB}/os/__init__.cpp
    ${SHEDSKIN_LIB}/os/__init__.hpp
    ${SHEDSKIN_LIB}/os/path.cpp
    ${SHEDSKIN_LIB}/os/path.hpp
    ${SHEDSKIN_LIB}/stat.cpp
    ${SHEDSKIN_LIB}/stat.hpp
    ${SHEDSKIN_LIB}/getopt.cpp
    ${SHEDSKIN_LIB}/getopt.hpp
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
