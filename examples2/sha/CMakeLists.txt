# long exe version for lib cases

set(sys_modules
    copy
    struct
    sys
)

set(app_modules
    lib/hashlib
)

get_filename_component(name ${CMAKE_CURRENT_SOURCE_DIR} NAME_WLE)

set(PROJECT_EXE_DIR ${PROJECT_BINARY_DIR}/${name}/exe)
set(BUILD_DIR ${PROJECT_BINARY_DIR}/${name})

set(basename_py "${name}.py")

set(EXE ${name}-exe)

set(BUILD_DIR ${PROJECT_BINARY_DIR}/${name})

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/lib DESTINATION ${PROJECT_EXE_DIR})

set(translated_files
    ${PROJECT_EXE_DIR}/${name}.cpp
    ${PROJECT_EXE_DIR}/${name}.hpp
)

foreach(mod ${app_modules})
    list(APPEND translated_files "${PROJECT_EXE_DIR}/${mod}.cpp")
    list(APPEND translated_files "${PROJECT_EXE_DIR}/${mod}.hpp")            
endforeach()


add_custom_command(OUTPUT ${translated_files}
    COMMAND ${Python_EXECUTABLE} -m shedskin --nomakefile -Llib -o ${PROJECT_EXE_DIR} "${basename_py}"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DEPENDS "${basename_py}"
    COMMENT "translating ${basename_py} to exe"
    VERBATIM
)


add_custom_target(shedskin_${EXE} DEPENDS ${translated_files})

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

add_executable(${EXE}
    ${translated_files}
    ${sys_module_list}
)


set_target_properties(${EXE} PROPERTIES
    OUTPUT_NAME ${name}
)

target_include_directories(${EXE} PRIVATE
    /usr/local/include
    ${SHEDSKIN_LIB}
    ${CMAKE_SOURCE_DIR}
    ${PROJECT_EXE_DIR}
    $<$<BOOL:${APPLE}>:/usr/local/opt/openssl@1.1/include>
    lib
)

target_compile_options(${EXE} PRIVATE
    "-O2"
    "-Wall"
    "-Wno-deprecated"
)


target_link_directories(${EXE} PRIVATE
    $<$<BOOL:${APPLE}>:/usr/local/opt/openssl@1.1/lib>
)

target_link_libraries(${EXE} PRIVATE
    "-lgc"
    "-lgccpp"
    "-lpcre"
    "-lssl"
    "-lcrypto"
)






