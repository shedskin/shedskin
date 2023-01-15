set(sys_modules
    array
    math
    os
    os.path
    stat
    struct
    sys
    time
)

set(app_modules
    # c64/__init__
    c64/cia
    c64/cpu
    c64/joysticks
    c64/loaders/__init__
    # c64/loaders/d64
    c64/loaders/entries
    c64/loaders/prg
    c64/loaders/t64
    c64/memory
    c64/mmu
    # c64/origscreens
    c64/palette
    c64/pixbufs
    c64/screens
    c64/sid
    c64/sprite
    c64/symbols
    c64/tape
    c64/vic_ii
)


copy_to_build_dir(
    "ROM"
    intkarat.t64
)

set(subdir "c64")

copy_to_build_dir(c64_main.py)

get_filename_component(name ${CMAKE_CURRENT_SOURCE_DIR} NAME_WLE)

set(PROJECT_EXT_DIR ${PROJECT_BINARY_DIR}/${name}/ext)

set(basename "c64")

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

target_include_directories(${EXT} PUBLIC
    ${Python_INCLUDE_DIRS}    
    /usr/local/include
    ${SHEDSKIN_LIB}
    ${CMAKE_SOURCE_DIR}
    ${PROJECT_EXT_DIR}
    ${PROJECT_EXT_DIR}/${subdir}
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
    $<$<BOOL:${APPLE}>:-fbracket-depth=500>
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

