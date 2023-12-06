# more complex case

if(CMAKE_HOST_APPLE) # i.e if is_macos check if homebrew is used then get ssl prefix
    if(NOT DEFINED ssl_prefix AND NOT DEFINED CACHE{ssl_prefix})
        execute_process(
            COMMAND brew --prefix --installed openssl
            OUTPUT_VARIABLE homebrew_ssl_prefix
            ERROR_VARIABLE homebrew_ssl_error
            ECHO_ERROR_VARIABLE
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )
        set(ssl_prefix ${homebrew_ssl_prefix} CACHE STRING "prefix of installed openssl library")
    elseif(NOT DEFINED ssl_prefix AND DEFINED CACHE{ssl_prefix})
        set(ssl_prefix $CACHE{ssl_prefix})
    else()
        message("using provided ssl_prefix")
    endif()
endif()


add_shedskin_product(
    EXTRA_LIB_DIR
        lib

    SYS_MODULES
        collections

    APP_MODULES
        lib/hashlib

    CMDLINE_OPTIONS
        "-Xlib"

    INCLUDE_DIRS
        lib
        $<$<BOOL:${CMAKE_HOST_APPLE}>:${ssl_prefix}/include>

    LINK_DIRS
        $<$<BOOL:${CMAKE_HOST_APPLE}>:${ssl_prefix}/lib>

    LINK_LIBS
        "-lssl"
        "-lcrypto"
)
