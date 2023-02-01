# more complex case
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
        $<$<BOOL:${APPLE}>:/usr/local/opt/openssl@1.1/include>

    LINK_DIRS
        $<$<BOOL:${APPLE}>:/usr/local/opt/openssl@1.1/lib>

    LINK_LIBS
        "-lssl"
        "-lcrypto"
)