# posix-only: pthread_sigmask, sigpending and sigwait are #ifndef WIN32 in lib/signal
if(WIN32)
    return()
endif()

add_shedskin_product(
    SYS_MODULES
        os
        os.path
        stat
        signal
)
