
function(add_shedskin_ext_tests)

    file(GLOB test_sources "test_*.py")

    foreach(test_py ${test_sources})

        get_filename_component(name ${test_py} NAME_WLE)
        get_filename_component(basename_py ${test_py} NAME)

        set(PYEXT ${name})
        set(basename_py "${PYEXT}.py")

        if(DEBUG)
            message("test_py: " ${test_py})
            message("name: " ${name})
            message("basename_py: " ${basename_py})
            message("PYEXT: " ${PYEXT})
        endif()

        set(translated_files
            ${PROJECT_BINARY_DIR}/${PYEXT}.cpp
            ${PROJECT_BINARY_DIR}/${PYEXT}.hpp
        )

        add_custom_command(OUTPUT ${translated_files}
            COMMAND shedskin --nomakefile -o build -e "${basename_py}"
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            DEPENDS "${basename_py}"
            COMMENT "translating ${basename_py}"
            VERBATIM
        )

        add_custom_target(shedskin_ext_${PYEXT} DEPENDS ${translated_files})

        if(DEBUG)
            message("test:" ${APP})
        endif()

        add_library(${PYEXT} MODULE
            ${PROJECT_BINARY_DIR}/${PYEXT}.cpp
            ${PROJECT_BINARY_DIR}/${PYEXT}.hpp
            ${SHEDSKIN_LIB}/builtin.cpp
            ${SHEDSKIN_LIB}/builtin.hpp
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

    endforeach()

endfunction()
