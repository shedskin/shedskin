
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

