# more complex case

if(CMAKE_HOST_APPLE) # i.e if is_macos check if homebrew is used then get ssl prefix
    execute_process(
        COMMAND brew --prefix openssl
        OUTPUT_VARIABLE homebrew_ssl_prefix
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    If(DEFINED homebrew_ssl_prefix)
        set(ssl_prefix ${homebrew_ssl_prefix})
    endif()
endif()

add_shedskin_product(
    HAS_LIB

    SYS_MODULES
        collections

    APP_MODULES
        lib/hashlib

    OPTIONS
        "-Llib"

    INCLUDE_DIRS
        lib
        $<$<BOOL:${CMAKE_HOST_APPLE}>:${ssl_prefix}/include>

    LINK_DIRS
        $<$<BOOL:${CMAKE_HOST_APPLE}>:${ssl_prefix}/lib>

    LINK_LIBS
        "-lssl"
        "-lcrypto"
)