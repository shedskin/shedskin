
# select() on Windows only supports sockets, while this test uses
# os.pipe() file descriptors, so it is POSIX-only for now
if(NOT WIN32)
    add_shedskin_product(
        SYS_MODULES
            select
            os
            os.path
            stat
    )
endif()
