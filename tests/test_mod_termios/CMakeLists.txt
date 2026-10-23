# termios/tty are POSIX-only
if(NOT WIN32)
    add_shedskin_product(
        SYS_MODULES
            termios
            tty
            copy
            os
            os.path
            stat
    )
endif()
