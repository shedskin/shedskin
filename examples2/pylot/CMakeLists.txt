set(sys_modules
    copy
    math
    random
    re
    sys
    time
)

set(subdir "pylot")


set(app_modules
    ${subdir}/Camera
    ${subdir}/Color
    ${subdir}/Material
    ${subdir}/Ray
    ${subdir}/Shape
    ${subdir}/Utils
    ${subdir}/Vector4
    ${subdir}/World
)

copy_to_build_dir(pylot_main.py)

get_filename_component(name ${CMAKE_CURRENT_SOURCE_DIR} NAME_WLE)

set(PROJECT_EXT_DIR ${PROJECT_BINARY_DIR}/${name}/ext)

set(basename "SimpleGeometry")

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
    COMMAND ${Python_EXECUTABLE} -m shedskin --nomakefile -o ${PROJECT_EXT_DIR}/${subdir} -e ${OPT_B} "${subdir}/${basename_py}"
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

target_include_directories(${EXT} PUBLIC
    ${Python_INCLUDE_DIRS}    
    /usr/local/include
    ${SHEDSKIN_LIB}
    ${CMAKE_SOURCE_DIR}
    ${PROJECT_EXT_DIR}
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
    $<$<BOOL:${APPLE}>:-undefined dynamic_lookup>
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

