
function(add_shedskin_test sys_modules)

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

    list(PREPEND sys_modules builtin)

    foreach(mod ${sys_modules})
        # special case os and os.path
        if(mod STREQUAL "os")
            list(APPEND sys_module_list "${SHEDSKIN_LIB}/os/__init__.cpp")
            list(APPEND sys_module_list "${SHEDSKIN_LIB}/os/__init__.hpp")            
        elseif(mod STREQUAL "os.path")
            list(APPEND sys_module_list "${SHEDSKIN_LIB}/os/path.cpp")
            list(APPEND sys_module_list "${SHEDSKIN_LIB}/os/path.hpp")
        else()
            list(APPEND sys_module_list "${SHEDSKIN_LIB}/${mod}.cpp")
            list(APPEND sys_module_list "${SHEDSKIN_LIB}/${mod}.hpp")
        endif()
    endforeach()

    if(ARGV1)
        set(app_modules ${ARGV1})
    else()
        set(app_modules)
    endif()
    foreach(mod ${app_modules})
        list(APPEND app_module_list "${PROJECT_BINARY_DIR}/${mod}.cpp")
        list(APPEND app_module_list "${PROJECT_BINARY_DIR}/${mod}.hpp")            
    endforeach()

    if(DEBUG)
        message("-------------------------------------------------------------")
        message("name:" ${name})
        foreach(mod ${app_module_list})
            get_filename_component(mod_name ${mod} NAME)
            message("app_module: ${mod_name}") 
        endforeach()
        foreach(mod ${sys_module_list})
            get_filename_component(mod_name ${mod} NAME)
            message("sys_module: ${mod_name}") 
        endforeach()
    endif()

    add_executable(${APP}
        ${PROJECT_BINARY_DIR}/${APP_NAME}.cpp
        ${PROJECT_BINARY_DIR}/${APP_NAME}.hpp
        ${app_module_list}        
        ${sys_module_list}
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
