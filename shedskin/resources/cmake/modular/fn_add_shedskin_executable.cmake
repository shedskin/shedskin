set(__doc__ [[

    containing folder_name:
        default: cmake_path(GET CMAKE_CURRENT_SOURCE_DIR STEM name)
        else: can be overriden by setting SHEDSKIN_NAME 

    <main>.py: can be one of two cases:
        - <containing_folder>/<main>.py
        - <containing_folder>/<parentpath>/<main>.py
            where
                subpath is one or more directories
]])



function(add_shedskin_executable)

    # -------------------------------------------------------------------------
    # function api and default configuration

    set(options
        BUILD_TEST
        HAS_LIB
        ENABLE_CONAN
        ENABLE_SPM
        ENABLE_EXTERNAL_PROJECT
        DEBUG
    )
    set(oneValueArgs
        NAME
        MAIN_MODULE
    )
    set(multiValueArgs 
        SYS_MODULES
        APP_MODULES
        DATA
        INCLUDE_DIRS
        LINK_LIBS
        LINK_DIRS
        COMPILE_OPTIONS
        LINK_OPTIONS
        CMDLINE_OPTIONS
    )
    cmake_parse_arguments(SHEDSKIN "${options}" "${oneValueArgs}"
                          "${multiValueArgs}" ${ARGN})

    if(SHEDSKIN_BUILD_TEST)
        set(BUILD_TEST ON)
    endif()

    if(DEFINED SHEDSKIN_NAME)
        set(name "${SHEDSKIN_NAME}")
    else()
        cmake_path(GET CMAKE_CURRENT_SOURCE_DIR STEM name)
    endif()

    if(DEFINED SHEDSKIN_MAIN_MODULE)
        cmake_path(GET SHEDSKIN_MAIN_MODULE STEM main)
        cmake_path(GET SHEDSKIN_MAIN_MODULE FILENAME main_py)
        cmake_path(GET SHEDSKIN_MAIN_MODULE PARENT_PATH parentpath)
        set(IS_NESTED TRUE)
    else()
        set(main "${name}")
        set(main_py "${main}.py")
    endif()

    if(SHEDSKIN_SYS_MODULES)
        set(sys_modules "${SHEDSKIN_SYS_MODULES}")
    else()
        set(sys_modules)
    endif()

    if(SHEDSKIN_APP_MODULES)
        set(app_modules "${SHEDSKIN_APP_MODULES}")
    else()
        set(app_modules)
    endif()

    if(SHEDSKIN_DATA)
        foreach(fname ${SHEDSKIN_DATA})
            file(COPY ${fname} DESTINATION ${PROJECT_BINARY_DIR}/${name})
        endforeach()
    endif()

    if(SHEDSKIN_CMDLINE_OPTIONS)
        join(${SHEDSKIN_CMDLINE_OPTIONS} " " opts)
    else()
        set(opts)
    endif()

    set(PROJECT_EXE_DIR ${PROJECT_BINARY_DIR}/${name}/exe)
    set(IMPORTS_OS_MODULE FALSE)
    set(IMPORTS_RE_MODULE FALSE)
 
    # if ${name} starts_with test_ then set IS_TEST to TRUE
    string(FIND "${name}" "test_" index)
    if("${index}" EQUAL 0)
        set(IS_TEST TRUE)
    else()
        set(IS_TEST FALSE)
    endif()

    if(DEBUG)
        include(CMakePrintHelpers)
        cmake_print_variables(
            # boolean options
            SHEDSKIN_BUILD_TEST
            SHEDSKIN_HAS_LIB

            SHEDSKIN_ENABLE_CONAN
            SHEDSKIN_ENABLE_SPM
            SHEDSKIN_ENABLE_EXTERNAL_PROJECT
            SHEDSKIN_DEBUG

            # one value args
            SHEDSKIN_NAME
            SHEDSKIN_MAIN_MODULE
            
            # multi value args
            SHEDSKIN_SYS_MODULES
            SHEDSKIN_APP_MODULES
            SHEDSKIN_DATA

            SHEDSKIN_COMPILE_OPTIONS
            SHEDSKIN_INCLUDE_DIRS
            SHEDSKIN_LINK_OPTIONS
            SHEDSKIN_LINK_DIRS
            SHEDSKIN_LINK_LIBS

            SHEDSKIN_CMDLINE_OPTIONS
            
            # intermediate variables
            name
            main
            main_py
            parentpath
            opts
            IS_NESTED
            PROJECT_EXE_DIR
            __doc__
    )
    endif()

    # -------------------------------------------------------------------------
    # common section

    list(PREPEND sys_modules builtin)

    foreach(mod ${sys_modules})
        # special case os, os.path
        if(mod STREQUAL "os")
            set(IMPORTS_OS_MODULE TRUE)
            list(APPEND sys_module_list "${SHEDSKIN_LIB}/os/__init__.cpp")
            list(APPEND sys_module_list "${SHEDSKIN_LIB}/os/__init__.hpp")            
        elseif(mod STREQUAL "os.path")
            list(APPEND sys_module_list "${SHEDSKIN_LIB}/os/path.cpp")
            list(APPEND sys_module_list "${SHEDSKIN_LIB}/os/path.hpp")
        else()
            if(mod STREQUAL "re")
                set(IMPORTS_RE_MODULE TRUE)
            endif()
            list(APPEND sys_module_list "${SHEDSKIN_LIB}/${mod}.cpp")
            list(APPEND sys_module_list "${SHEDSKIN_LIB}/${mod}.hpp")
        endif()
    endforeach()

    if(ENABLE_EXEERNAL_PROJECT)
        set(LIB_DEPS
            ${install_dir}/lib/libgc.a
            ${install_dir}/lib/libgccpp.a
            $<$<BOOL:${IMPORTS_RE_MODULE}>:${install_dir}/lib/libpcre.a>
        )
        set(LIB_DIRS ${install_dir}/lib)
        set(LIB_INCLUDES ${install_dir}/include)
    elseif(ENABLE_SPM)
        set(LIB_DEPS
            ${SPM_LIB_DIRS}/libgc.a
            ${SPM_LIB_DIRS}/libgccpp.a
            $<$<BOOL:${IMPORTS_RE_MODULE}>:${SPM_LIB_DIRS}/libpcre.a>            
        )
        set(LIB_DIRS ${SPM_LIB_DIRS})
        set(LIB_INCLUDES ${SPM_INCLUDE_DIRS})
    elseif(ENABLE_CONAN)
        set(LIB_DEPS
            BDWgc::gc
            BDWgc::gccpp
            $<$<BOOL:${IMPORTS_RE_MODULE}>:PCRE::PCRE>
        )
        set(LIB_DIRS
            ${BDWgc_LIB_DIRS}
            $<$<BOOL:${IMPORTS_RE_MODULE}>:${PCRE_LIB_DIRS}>
        )
        # include PCRE headers irrespective (even if not used) to prevent header not found error
        set(LIB_INCLUDES
            ${BDWgc_INCLUDE_DIRS}
            ${PCRE_INCLUDE_DIRS}
        )
    else() 
        # adding -lutil for every use of os is not a good idea should only be temporary
        # better to just add it on demand if the two relevant pty functions are used
        set(local_prefix "/usr/local")
        if(CMAKE_HOST_APPLE) # i.e if is_macos check if homebrew is used aand if so get prefix
            execute_process(
                COMMAND brew --prefix
                OUTPUT_VARIABLE homebrew_prefix
                OUTPUT_STRIP_TRAILING_WHITESPACE
            )
            If(DEFINED homebrew_prefix)
                set(local_prefix ${homebrew_prefix})
            endif()
        endif()

        set(local_include "${local_prefix}/include")
        set(local_libdir "${local_prefix}/lib")

        set(LIB_DEPS 
            "-lgc"
            "-lgccpp"
            "$<$<BOOL:${IMPORTS_RE_MODULE}>:-lpcre>"
            # "$<$<BOOL:${IMPORTS_OS_MODULE}>:-lutil>"
            ${SHEDSKIN_LINK_LIBS}
        )
        set(LIB_DIRS
            ${local_libdir}
            ${SHEDSKIN_LINK_DIRS}
        )
        set(LIB_INCLUDES 
            ${local_include}            
            ${SHEDSKIN_INCLUDE_DIRS}
        )
    endif()

    set(EXE ${name}-exe)

    if(IS_NESTED)
        set(translated_files
            ${PROJECT_EXE_DIR}/${parentpath}/${main}.cpp
            ${PROJECT_EXE_DIR}/${parentpath}/${main}.hpp
        )
    else()
        set(translated_files
            ${PROJECT_EXE_DIR}/${main}.cpp
            ${PROJECT_EXE_DIR}/${main}.hpp
        )
    endif()

    foreach(mod ${app_modules})
        list(APPEND translated_files "${PROJECT_EXE_DIR}/${mod}.cpp")
        list(APPEND translated_files "${PROJECT_EXE_DIR}/${mod}.hpp")            
    endforeach()


    if(IS_NESTED)
        add_custom_command(OUTPUT ${translated_files}
            COMMAND shedskin translate --nomakefile -o ${PROJECT_EXE_DIR}/${parentpath} ${opts} "${SHEDSKIN_MAIN_MODULE}"
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            DEPENDS "${SHEDSKIN_MAIN_MODULE}"
            COMMENT "translating ${main_py} to exe"
            VERBATIM
        )        
    else()
        add_custom_command(OUTPUT ${translated_files}
            COMMAND shedskin translate --nomakefile -o ${PROJECT_EXE_DIR} ${opts} "${main_py}"
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            DEPENDS "${main_py}"
            COMMENT "translating ${main_py} to exe"
            VERBATIM
        )
    endif()

    add_custom_target(shedskin_${EXE} DEPENDS ${translated_files})

    if(SHEDSKIN_HAS_LIB AND NOT EXISTS ${PROJECT_EXE_DIR}/lib)
        file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/lib DESTINATION ${PROJECT_EXE_DIR})
    endif()

    add_executable(${EXE}
        ${translated_files}
        ${sys_module_list}
    )

    set_target_properties(${EXE} PROPERTIES
        OUTPUT_NAME ${name}
    )

    target_compile_options(${EXE} PRIVATE
        "-O2"
        "-Wall"
        "-Wno-deprecated"
        "-Wno-unused-variable"
        "-Wno-unused-but-set-variable"
        ${SHEDSKIN_COMPILE_OPTIONS}
    )

    target_include_directories(${EXE} PRIVATE
        ${SHEDSKIN_LIB}
        ${CMAKE_SOURCE_DIR}
        ${PROJECT_EXE_DIR}
        ${LIB_INCLUDES}
    )

    target_link_options(${EXE} PRIVATE
        ${SHEDSKIN_LINK_OPTIONS}
    )

    target_link_directories(${EXE} PRIVATE
        ${LIB_DIRS}
    )

    target_link_libraries(${EXE} PRIVATE
        ${LIB_DEPS}
    )

    if(BUILD_TEST AND IS_TEST)
        add_test(NAME ${EXE} COMMAND ${EXE})
    endif()
endfunction()
