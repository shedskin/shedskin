add_shedskin_product(
    BUILD_EXTENSION
    MAIN_MODULE c64/c64.py
    SYS_MODULES
        array
        math
        os
        os.path
        stat
        struct
        sys
        time
    APP_MODULES
        # c64/__init__
        c64/cia
        c64/cpu
        c64/joysticks
        c64/loaders/__init__
        # c64/loaders/d64
        c64/loaders/entries
        c64/loaders/prg
        c64/loaders/t64
        c64/memory
        c64/mmu
        # c64/origscreens
        c64/palette
        c64/pixbufs
        c64/screens
        c64/sid
        c64/sprite
        c64/symbols
        c64/tape
        c64/vic_ii
    DATA
        "ROM"
        intkarat.t64
        c64_main.py
    CMDLINE_OPTIONS
        "-b"
    INCLUDE_DIRS
        ${PROJECT_BINARY_DIR}/c64/ext/c64
    COMPILE_OPTIONS
        $<$<BOOL:${APPLE}>:-fbracket-depth=500>
)
