
function(add_shedskin_exe_tests)

    file(GLOB test_sources "test_*.py")

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

endfunction()
