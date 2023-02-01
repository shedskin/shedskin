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
    )
    set(LIB_DIRS
        /usr/local/lib
    )
    set(LIB_INCLUDES 
        /usr/local/include
    )
endif()


set(sys_modules
    array
    math
)

set(subdir "Gh0stenstein")


set(app_modules
    ${subdir}/world_draw
)


get_filename_component(name ${CMAKE_CURRENT_SOURCE_DIR} NAME_WLE)

set(PROJECT_EXT_DIR ${PROJECT_BINARY_DIR}/${name}/ext)


file(COPY gs_main.py DESTINATION ${PROJECT_BINARY_DIR}/${name})


set(basename "world_manager")

set(basename_py "${basename}.py")

set(EXT ${name}-ext)

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

set(translated_files
    ${PROJECT_EXT_DIR}/${subdir}/${basename}.cpp
    ${PROJECT_EXT_DIR}/${subdir}/${basename}.hpp
)

foreach(mod ${app_modules})
    list(APPEND translated_files "${PROJECT_EXT_DIR}/${mod}.cpp")
    list(APPEND translated_files "${PROJECT_EXT_DIR}/${mod}.hpp")            
endforeach()

add_custom_command(OUTPUT ${translated_files}
    COMMAND ${Python_EXECUTABLE} -m shedskin --nomakefile -o ${PROJECT_EXT_DIR}/${subdir} -be
     "${subdir}/${basename_py}"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DEPENDS "${subdir}/${basename_py}"
    COMMENT "translating ${basename_py} to ext"
    VERBATIM
)

add_custom_target(shedskin_${EXT} DEPENDS ${translated_files})

add_library(${EXT} MODULE
    ${translated_files}
    ${sys_module_list}
)

set_target_properties(${EXT} PROPERTIES
    OUTPUT_NAME ${basename}
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
    "-Wno-unused-variable"
)

target_link_options(${EXT} PRIVATE
    $<$<BOOL:${APPLE}>:-undefined dynamic_lookup>
    "-Wno-unused-result"
    "-Wsign-compare"
    "-Wunreachable-code"
    "-fno-common"
    "-dynamic"
)

target_link_libraries(${EXT} PRIVATE
    ${LIB_DEPS}
)

target_link_directories(${EXT} PRIVATE
    ${LIB_DIRS}
)


