# termios/tty are POSIX-only
if(NOT WIN32)
    add_shedskin_product(
        SYS_MODULES
            tty
            termios
            copy
            os
            os.path
            stat
    )
endif()
