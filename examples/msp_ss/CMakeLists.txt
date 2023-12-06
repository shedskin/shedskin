# more complex case
add_shedskin_product(
    EXTRA_LIB_DIR
        lib

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

    CMDLINE_OPTIONS
        "-Xlib"

    INCLUDE_DIRS
        lib
)




