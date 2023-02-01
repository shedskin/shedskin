
function(add_shedskin_executable)

    # -------------------------------------------------------------------------
    # function api and default configuration

    set(options
            DISABLE_EXECUTABLE
            BUILD_TEST DISABLE_TEST
            HAS_LIB
            ENABLE_CONAN ENABLE_SPM DEBUG)
    set(oneValueArgs NAME)
    set(multiValueArgs 
            SYS_MODULES APP_MODULES DATA
            COMPILE_OPTS INCLUDE_DIRS LINK_LIBS LINK_DIRS
            OPTIONS)
    cmake_parse_arguments(SHEDSKIN "${options}" "${oneValueArgs}"
                          "${multiValueArgs}" ${ARGN})

    if(DEBUG)
        message("ENABLE_CONAN: " "${ENABLE_CONAN}")

        message("DEBUG: " "${DEBUG}")

        message("SHEDSKIN_NAME: " "${SHEDSKIN_NAME}")

        message("SHEDSKIN_COMPILE_OPTS: " "${SHEDSKIN_COMPILE_OPTS}")
        message("SHEDSKIN_INCLUDE_DIRS: " "${SHEDSKIN_INCLUDE_DIRS}")
        message("SHEDSKIN_LINK_LIBS: " "${SHEDSKIN_LINK_LIBS}")
        message("SHEDSKIN_LINK_DIRS: " "${SHEDSKIN_LINK_DIRS}")

        message("SHEDSKIN_BUILD_TEST: " "${SHEDSKIN_BUILD_TEST}")

        message("SHEDSKIN_DISABLE_EXECUTABLE: " "${SHEDSKIN_DISABLE_EXECUTABLE}")
        message("SHEDSKIN_DISABLE_TEST: " "${SHEDSKIN_DISABLE_TEST}")

        message("SHEDSKIN_HAS_LIB: " "${SHEDSKIN_HAS_LIB}")

        message("SHEDSKIN_SYS_MODULES: " "${SHEDSKIN_SYS_MODULES}")
        message("SHEDSKIN_APP_MODULES: " "${SHEDSKIN_APP_MODULES}")

        message("SHEDSKIN_DATA: " "${SHEDSKIN_DATA}")
        message("SHEDSKIN_OPTIONS: " "${SHEDSKIN_OPTIONS}")
    endif()

    if(SHEDSKIN_DISABLE_EXECUTABLE)
        set(BUILD_EXECUTABLE OFF)
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
        get_filename_component(name ${CMAKE_CURRENT_SOURCE_DIR} NAME_WLE)
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

    if(SHEDSKIN_OPTIONS)
        join(${SHEDSKIN_OPTIONS} " " opts)
    else()
        set(opts)
    endif()

    set(PROJECT_EXE_DIR ${PROJECT_BINARY_DIR}/${name}/exe)
    set(IMPORTS_OS_MODULE FALSE)
    set(IMPORTS_RE_MODULE FALSE)

    set(basename_py "${name}.py")

    # if ${name} starts_with test_ then set IS_TEST to TRUE
    string(FIND "${name}" "test_" index)
    if("${index}" EQUAL 0)
        set(IS_TEST TRUE)
    else()
        set(IS_TEST FALSE)
    endif()

    if(DEBUG)
        message("name: " "${name}")
        message("sys_modules: " "${sys_modules}")
        message("app_modules: " "${app_modules}")
        message("opts: " "${opts}")
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
        set(LIB_DEPS 
            "-lgc"
            "-lgccpp"
            "$<$<BOOL:${IMPORTS_RE_MODULE}>:-lpcre>"
            ${SHEDSKIN_LINK_LIBS}
        )
        set(LIB_DIRS
            /usr/local/lib
            ${SHEDSKIN_LINK_DIRS}
        )
        set(LIB_INCLUDES 
            /usr/local/include
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

    set(EXE ${name}-exe)
    
    set(translated_files
        ${PROJECT_EXE_DIR}/${name}.cpp
        ${PROJECT_EXE_DIR}/${name}.hpp
    )

    foreach(mod ${app_modules})
        list(APPEND translated_files "${PROJECT_EXE_DIR}/${mod}.cpp")
        list(APPEND translated_files "${PROJECT_EXE_DIR}/${mod}.hpp")         
    endforeach()

    add_custom_command(OUTPUT ${translated_files}
        COMMAND ${Python_EXECUTABLE} -m shedskin --nomakefile -o ${PROJECT_EXE_DIR} ${opts} "${basename_py}"
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS "${basename_py}"
        COMMENT "translating ${basename_py} to exe"
        VERBATIM
    )

    add_custom_target(shedskin_${EXE} DEPENDS ${translated_files})

    if(SHEDSKIN_HAS_LIB)
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
    )

    target_include_directories(${EXE} PRIVATE
        ${SHEDSKIN_LIB}
        ${CMAKE_SOURCE_DIR}
        ${PROJECT_EXE_DIR}
        ${LIB_INCLUDES}
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

