
function(add_shedskin_test sys_modules)

    get_filename_component(name ${CMAKE_CURRENT_SOURCE_DIR} NAME_WLE)

    set(basename_py "${name}.py")

    set(EXE ${name}-exe)

    set(translated_files_exe
        ${PROJECT_EXE_DIR}/${name}.cpp
        ${PROJECT_EXE_DIR}/${name}.hpp
    )

    add_custom_command(OUTPUT ${translated_files_exe}
        COMMAND shedskin --nomakefile -o ../build/exe "${basename_py}"
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS "${basename_py}"
        COMMENT "translating ${basename_py} to exe"
        VERBATIM
    )

    add_custom_target(shedskin_${EXE} DEPENDS ${translated_files_exe})

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
        list(APPEND app_module_list "${PROJECT_EXE_DIR}/${mod}.cpp")
        list(APPEND app_module_list "${PROJECT_EXE_DIR}/${mod}.hpp")            
    endforeach()

    add_executable(${EXE}
        ${PROJECT_EXE_DIR}/${name}.cpp
        ${PROJECT_EXE_DIR}/${name}.hpp
        ${app_module_list}        
        ${sys_module_list}
    )

    set_target_properties(${EXE} PROPERTIES
        OUTPUT_NAME ${name}
    )

    target_include_directories(${EXE} PRIVATE
        /usr/local/include
        ${SHEDSKIN_LIB}
        ${CMAKE_SOURCE_DIR}
    )

    target_compile_options(${EXE} PRIVATE
        "-O2"
        "-Wall"
        "-Wno-deprecated"
    )

    target_link_libraries(${EXE} PRIVATE
        "-lgc"
        "-lgccpp"
        "-lpcre"
    )

    add_test(NAME ${EXE} COMMAND ${EXE})


    if(TEST_EXT)

        set(EXT ${name}-ext)

        set(translated_files_ext
            ${PROJECT_EXT_DIR}/${name}.cpp
            ${PROJECT_EXT_DIR}/${name}.hpp
        )
        
        add_custom_command(OUTPUT ${translated_files_ext}
            COMMAND shedskin --nomakefile -o ../build/ext -e "${basename_py}"
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            DEPENDS "${basename_py}"
            COMMENT "translating ${basename_py} to ext"
            VERBATIM
        )

        add_custom_target(shedskin_${EXT} DEPENDS ${translated_files_ext})

        # if there are local imports
        if(ARGV1)
            set(app_modules ${ARGV1})
        else()
            set(app_modules)
        endif()
        foreach(mod ${app_modules})
            list(APPEND app_module_list "${PROJECT_EXT_DIR}/${mod}.cpp")
            list(APPEND app_module_list "${PROJECT_EXT_DIR}/${mod}.hpp")            
        endforeach()

        add_library(${EXT} MODULE
            ${PROJECT_EXT_DIR}/${name}.cpp
            ${PROJECT_EXT_DIR}/${name}.hpp
            ${app_module_list}        
            ${sys_module_list}
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


endfunction()
