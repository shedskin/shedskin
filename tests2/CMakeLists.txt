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

    # message("python_test (full path): " ${test_py})

    get_filename_component(name ${test_py} NAME_WLE)
    get_filename_component(basename_py ${test_py} NAME)

    set(APP_NAME ${name})
    set(APP ${APP_NAME})

    set(translated_files
        ${PROJECT_BINARY_DIR}/${APP_NAME}.cpp
        ${PROJECT_BINARY_DIR}/${APP_NAME}.hpp
    )

    add_custom_command(OUTPUT ${translated_files}
        COMMAND shedskin --nomakefile -o build "${basename_py}"
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
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

# -----------------------------------------------------------------------
# build/test function to handle tests with imports

function(add_shedskin_test modules)

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

    list(PREPEND modules builtin)

    foreach(mod ${modules})
    list(APPEND module_list "${SHEDSKIN_LIB}/${mod}.cpp")
    list(APPEND module_list "${SHEDSKIN_LIB}/${mod}.hpp")
    endforeach()

    message("-------------------------------------------------------------")
    message("name:" ${name})
    foreach(mod ${module_list})
        get_filename_component(mod_name ${mod} NAME)
        message("module: ${mod_name}") 
    endforeach()


    add_executable(${APP}
        ${PROJECT_BINARY_DIR}/${APP_NAME}.cpp
        ${PROJECT_BINARY_DIR}/${APP_NAME}.hpp
        ${module_list}
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

endfunction()


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
        # message("testdir_name:" ${testdir_name})
        add_subdirectory(${testdir_name})
    endif()
endforeach()



