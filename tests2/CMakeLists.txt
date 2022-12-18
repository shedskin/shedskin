cmake_minimum_required(VERSION 3.19)

project(shedskin_tests LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(DEBUG off)


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

    if(DEBUG)
        message("test:" ${APP})
    endif()

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
        # special case os and os.path
        if(mod STREQUAL "os")
            list(APPEND module_list "${SHEDSKIN_LIB}/os/__init__.cpp")
            list(APPEND module_list "${SHEDSKIN_LIB}/os/__init__.hpp")            
        elseif(mod STREQUAL "os.path")
            list(APPEND module_list "${SHEDSKIN_LIB}/os/path.cpp")
            list(APPEND module_list "${SHEDSKIN_LIB}/os/path.hpp")
        else()
            list(APPEND module_list "${SHEDSKIN_LIB}/${mod}.cpp")
            list(APPEND module_list "${SHEDSKIN_LIB}/${mod}.hpp")
        endif()
    endforeach()

    if(DEBUG)
        message("-------------------------------------------------------------")
        message("name:" ${name})
        foreach(mod ${module_list})
            get_filename_component(mod_name ${mod} NAME)
            message("module: ${mod_name}") 
        endforeach()
    endif()

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
# build/test function to handle tests with imports

function(add_shedskin_pyxt_test)
    include(CTest)

    find_package(Python COMPONENTS Interpreter Development)
    message("python:" ${Python_EXECUTABLE})
    message("python_include" ${Python_INCLUDE_DIRS})

    get_filename_component(name ${CMAKE_CURRENT_SOURCE_DIR} NAME_WLE)

    set(HOME $ENV{HOME})

    set(PYEXT ${name})
    set(basename_py "${PYEXT}.py")


    link_directories(
        /usr/local/lib
    )

    set(translated_files
        ${PROJECT_BINARY_DIR}/${PYEXT}.cpp
        ${PROJECT_BINARY_DIR}/${PYEXT}.hpp
    )

    add_custom_command(OUTPUT ${translated_files}
        COMMAND shedskin --nomakefile -o ../build -e "${basename_py}"
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS "${basename_py}"
        COMMENT "translating ${basename_py}"
        VERBATIM
    )

    add_custom_target(shedskin_${PYEXT} DEPENDS ${translated_files})

    list(PREPEND modules builtin)

    foreach(mod ${modules})
        # special case os and os.path
        if(mod STREQUAL "os")
            list(APPEND module_list "${SHEDSKIN_LIB}/os/__init__.cpp")
            list(APPEND module_list "${SHEDSKIN_LIB}/os/__init__.hpp")            
        elseif(mod STREQUAL "os.path")
            list(APPEND module_list "${SHEDSKIN_LIB}/os/path.cpp")
            list(APPEND module_list "${SHEDSKIN_LIB}/os/path.hpp")
        else()
            list(APPEND module_list "${SHEDSKIN_LIB}/${mod}.cpp")
            list(APPEND module_list "${SHEDSKIN_LIB}/${mod}.hpp")
        endif()
    endforeach()

    if(DEBUG)
        message("-------------------------------------------------------------")
        message("name:" ${name})
        foreach(mod ${module_list})
            get_filename_component(mod_name ${mod} NAME)
            message("module: ${mod_name}") 
        endforeach()
    endif()

    add_library(${PYEXT} MODULE
        ${PROJECT_BINARY_DIR}/${PYEXT}.cpp
        ${PROJECT_BINARY_DIR}/${PYEXT}.hpp
        ${module_list}
    )

    set_target_properties(${PYEXT} PROPERTIES
        PREFIX ""
    )


    target_include_directories(${PYEXT} PUBLIC
        ${Python_INCLUDE_DIRS}    
        /usr/local/include
        ${SHEDSKIN_LIB}
        ${CMAKE_SOURCE_DIR}
    )

    target_compile_options(${PYEXT} PUBLIC
        "-fPIC"
        "-D__SS_BIND"
        "-Wno-unused-result"
        "-Wsign-compare"
        "-Wunreachable-code"
        "-DNDEBUG"
        "-g"
        "-fwrapv"
        "-O3"
        "-Wall"
    )


    target_link_options(${PYEXT} PUBLIC
        "-undefined"
        "dynamic_lookup"
        "-Wno-unused-result"
        "-Wsign-compare"
        "-Wunreachable-code"
        "-fno-common"
        "-dynamic"
    )

    target_link_libraries(${PYEXT} PUBLIC
        "-lgc"
        "-lgccpp"
        "-lpcre"
    )

    add_test(NAME ${PYEXT} 
             COMMAND ${Python_EXECUTABLE} -c "import ${PYEXT}; ${PYEXT}.test_all()")

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



