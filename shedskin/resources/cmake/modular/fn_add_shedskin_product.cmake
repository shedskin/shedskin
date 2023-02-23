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

function(add_shedskin_product)

    # -------------------------------------------------------------------------
    # function api and default configuration

    set(options
        BUILD_EXECUTABLE
        BUILD_EXTENSION
        BUILD_TEST 
        DISABLE_EXECUTABLE
        DISABLE_EXTENSION
        DISABLE_TEST
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

    if(SHEDSKIN_BUILD_EXECUTABLE)
        set(BUILD_EXECUTABLE ON)
    endif()

    if(SHEDSKIN_DISABLE_EXECUTABLE)
        set(BUILD_EXECUTABLE OFF)
    endif()

    if(SHEDSKIN_BUILD_EXTENSION)
        set(BUILD_EXTENSION ON)
    endif()

    if(SHEDSKIN_DISABLE_EXTENSION)
        set(BUILD_EXTENSION OFF)
    endif()

    if(SHEDSKIN_BUILD_TEST)
        set(BUILD_TEST ON)
    endif()

    if(SHEDSKIN_DISABLE_TEST)
        set(BUILD_TEST OFF)
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
    set(PROJECT_EXT_DIR ${PROJECT_BINARY_DIR}/${name}/ext)
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
            SHEDSKIN_BUILD_EXECUTABLE
            SHEDSKIN_BUILD_EXTENSION
            SHEDSKIN_BUILD_TEST 
            SHEDSKIN_DISABLE_EXECUTABLE
            SHEDSKIN_DISABLE_EXTENSION
            SHEDSKIN_DISABLE_TEST

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
            PROJECT_EXT_DIR
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

    if(ENABLE_EXTERNAL_PROJECT)
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

    if(DEBUG)
        message("LIB_DEPS: " ${LIB_DEPS})
        message("LIB_DIRS: " ${LIB_DIRS})
        message("LIB_INCLUDES: " ${LIB_INCLUDES})
    endif()

    # -------------------------------------------------------------------------
    # build executable section

    if(BUILD_EXECUTABLE)
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
            "-Wall"
            $<$<BOOL:${UNIX}>:-O2>
            $<$<BOOL:${UNIX}>:-Wno-deprecated>
            $<$<BOOL:${UNIX}>:-Wno-unused-variable>
            $<$<BOOL:${UNIX}>:-Wno-unused-but-set-variable>
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
    endif()

    # -------------------------------------------------------------------------
    # build extension section

    if(BUILD_EXTENSION)

        set(EXT ${name}-ext)

        if(IS_NESTED)
            set(translated_files
                ${PROJECT_EXT_DIR}/${parentpath}/${main}.cpp
                ${PROJECT_EXT_DIR}/${parentpath}/${main}.hpp
            )
        else()
            set(translated_files
                ${PROJECT_EXT_DIR}/${main}.cpp
                ${PROJECT_EXT_DIR}/${main}.hpp
            )
        endif()

        foreach(mod ${app_modules})
            list(APPEND translated_files "${PROJECT_EXT_DIR}/${mod}.cpp")
            list(APPEND translated_files "${PROJECT_EXT_DIR}/${mod}.hpp")            
        endforeach()


        if(IS_NESTED)
            add_custom_command(OUTPUT ${translated_files}
                COMMAND shedskin translate --nomakefile -o ${PROJECT_EXT_DIR}/${parentpath} -e ${opts} "${SHEDSKIN_MAIN_MODULE}"
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                DEPENDS "${SHEDSKIN_MAIN_MODULE}"
                COMMENT "translating ${main_py} to ext"
                VERBATIM
            )        
        else()
            add_custom_command(OUTPUT ${translated_files}
                COMMAND shedskin translate --nomakefile -o ${PROJECT_EXT_DIR} -e ${opts} "${main_py}"
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                DEPENDS "${main_py}"
                COMMENT "translating ${main_py} to ext"
                VERBATIM
            )
        endif()

        add_custom_target(shedskin_${EXT} DEPENDS ${translated_files})

        if(SHEDSKIN_HAS_LIB AND NOT EXISTS ${PROJECT_EXT_DIR}/lib)
            file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/lib DESTINATION ${PROJECT_EXT_DIR})
        endif()

        add_library(${EXT} MODULE
            ${translated_files}
            ${sys_module_list}
        )

        set_target_properties(${EXT} PROPERTIES
            OUTPUT_NAME ${name}
            PREFIX ""
        )

        target_include_directories(${EXT} PRIVATE
            ${Python_INCLUDE_DIRS}
            ${SHEDSKIN_LIB}
            ${CMAKE_SOURCE_DIR}
            ${PROJECT_EXT_DIR}
            ${LIB_INCLUDES}
        )

        target_compile_options(${EXT} PRIVATE
            "-D__SS_BIND"
            "-DNDEBUG"
            "-fPIC"
            "-fwrapv"
            "-g"
            "-O3"
            "-Wall"
            "-Wunreachable-code"
            "-Wno-unused-but-set-variable"
            "-Wno-unused-result"
            "-Wno-unused-variable"
            ${SHEDSKIN_COMPILE_OPTIONS}
        )

        target_link_options(${EXT} PRIVATE
            $<$<BOOL:${APPLE}>:-undefined dynamic_lookup>
            # "-fno-common" # can be excluded because it is already the default
            "-dynamic" # can be excluded because it is already the default
            ${SHEDSKIN_LINK_OPTIONS}
        )

        target_link_libraries(${EXT} PRIVATE
            ${LIB_DEPS}
        )

        target_link_directories(${EXT} PRIVATE
            ${LIB_DIRS}
        )

        if(BUILD_TEST AND IS_TEST)
            add_test(NAME ${EXT} 
                 COMMAND ${Python_EXECUTABLE} -c "from ${name} import test_all; test_all()")
        endif()

    endif()

endfunction()