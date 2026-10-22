# posix-only: os.fork is #ifndef WIN32 in lib/os
if(WIN32)
    return()
endif()

add_shedskin_product(
    SYS_MODULES
        os
        signal
        time
)
