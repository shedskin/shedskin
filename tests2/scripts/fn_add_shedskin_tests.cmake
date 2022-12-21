
function(add_shedskin_tests)

    file(GLOB test_sources "test_*.py")

    foreach(test_py ${test_sources})

        get_filename_component(name ${test_py} NAME_WLE)
        get_filename_component(basename_py ${test_py} NAME)

        set(EXE ${name}-exe)
        set(EXT ${name}-ext)
        set(basename_py "${name}.py")

        if(DEBUG)
            message("test_py: " ${test_py})
            message("name: " ${name})
            message("basename_py: " ${basename_py})
            message("EXE: " ${EXE})
            message("EXT: " ${EXT})
        endif()

        set(translated_files
            ${PROJECT_EXE_DIR}/${name}.cpp
            ${PROJECT_EXE_DIR}/${name}.hpp
        )

        add_custom_command(OUTPUT ${translated_files}
            COMMAND shedskin --nomakefile -o ${PROJECT_EXE_DIR} "${basename_py}"
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
        )

        target_link_libraries(${EXE} PUBLIC
            "-lgc"
            "-lgccpp"
            "-lpcre"
        )

        add_test(NAME ${EXE} COMMAND ${EXE})


        if(TEST_EXT)
            set(translated_files
                ${PROJECT_EXT_DIR}/${name}.cpp
                ${PROJECT_EXT_DIR}/${name}.hpp
            )
            
            add_custom_command(OUTPUT ${translated_files}
                COMMAND shedskin --nomakefile -o ${PROJECT_EXT_DIR} -e "${basename_py}"
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                DEPENDS "${basename_py}"
                COMMENT "translating ${basename_py} to ext"
                VERBATIM
            )

            add_custom_target(shedskin_${EXT} DEPENDS ${translated_files})


            add_library(${EXT} MODULE
                ${translated_files}
                ${SHEDSKIN_LIB}/builtin.cpp
                ${SHEDSKIN_LIB}/builtin.hpp
            )

            set_target_properties(${EXT} PROPERTIES
                OUTPUT_NAME ${name}
                PREFIX ""
            )

            target_include_directories(${EXT} PUBLIC
                ${Python_INCLUDE_DIRS}    
                /usr/local/include
                ${SHEDSKIN_LIB}
                ${CMAKE_SOURCE_DIR}
            )

            target_compile_options(${EXT} PUBLIC
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

            target_link_options(${EXT} PUBLIC
                "-undefined"
                "dynamic_lookup"
                "-Wno-unused-result"
                "-Wsign-compare"
                "-Wunreachable-code"
                "-fno-common"
                "-dynamic"
            )

            target_link_libraries(${EXT} PUBLIC
                "-lgc"
                "-lgccpp"
                "-lpcre"
            )

            add_test(NAME ${EXT} 
                 COMMAND ${Python_EXECUTABLE} -c "from ${name} import test_all; test_all()")
        endif()

    endforeach()

endfunction()
