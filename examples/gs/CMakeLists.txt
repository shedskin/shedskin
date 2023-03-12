add_shedskin_product(
    BUILD_EXTENSION
    MAIN_MODULE  Gh0stenstein/world_manager.py
    SYS_MODULES
        array
        math
    APP_MODULES
        Gh0stenstein/world_draw
    DATA
        gs_main.py
    CMDLINE_OPTIONS
        "-b"
)
