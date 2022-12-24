function(add_shedskin_static_library target)

    include(shedskin_sources)

    add_library(${target} STATIC
        ${CPP_SOURCES}
        ${CPP_HEADERS}
    )

    target_include_directories(${target} PUBLIC
        /usr/local/include
        ${SHEDSKIN_LIB}
        ${CMAKE_SOURCE_DIR}
    )

endfunction()


