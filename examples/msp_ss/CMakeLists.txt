# more complex case
add_shedskin_product(
    HAS_LIB

    SYS_MODULES
        getopt
        io
        os
        os.path
        stat
        struct
        sys
        time

    APP_MODULES
        lib/serial

    OPTIONS
        "-Llib"

    INCLUDE_DIRS
        lib

)




