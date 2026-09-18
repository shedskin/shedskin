# posix-only os functionality: these functions are #ifndef WIN32 in lib/os,
# and shedskin translates every called function regardless of runtime
# os.name checks, so this test cannot even be compiled on windows.
if(WIN32)
    return()
endif()

add_shedskin_product(
    SYS_MODULES
        os
        os.path
        stat
)
