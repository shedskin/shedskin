
function(add_shedskin_exe_tests)

    file(GLOB test_sources "test_*.py")

    foreach(test_py ${test_sources})

        get_filename_component(name ${test_py} NAME_WLE)
        get_filename_component(basename_py ${test_py} NAME)

        set(EXE ${name}-exe)
        set(basename_py "${name}.py")

        if(DEBUG)
            message("test_py: " ${test_py})
            message("name: " ${name})
            message("basename_py: " ${basename_py})
            message("EXE: " ${EXE})
        endif()

        set(translated_files
            ${PROJECT_EXE_DIR}/${name}.cpp
            ${PROJECT_EXE_DIR}/${name}.hpp
        )

        add_custom_command(OUTPUT ${translated_files}
            COMMAND ${Python_EXECUTABLE} -m shedskin --nomakefile -o ${PROJECT_EXE_DIR} "${basename_py}"
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
            DEPENDS "${basename_py}"
            COMMENT "translating ${basename_py} to exe"
            VERBATIM
        )

        add_custom_target(shedskin_${EXE} DEPENDS ${translated_files})

        add_executable(${EXE}
            ${translated_files}
            ${SHEDSKIN_LIB}/builtin.cpp
            ${SHEDSKIN_LIB}/builtin.hpp
        )

        set_target_properties(${EXE} PROPERTIES
            OUTPUT_NAME ${name}
        )

        target_include_directories(${EXE} PUBLIC
            /usr/local/include
            ${SHEDSKIN_LIB}
            ${CMAKE_SOURCE_DIR}
        )

        target_compile_options(${EXE} PUBLIC
            "-O2"
            "-Wall"
            "-Wno-deprecated"
            "-Wno-unused-variable"
        )

        target_link_libraries(${EXE} PUBLIC
            "-lgc"
            "-lutil"
            "-lgccpp"
            "-lpcre"
        )

        add_test(NAME ${EXE} COMMAND ${EXE})

    endforeach()

endfunction()
