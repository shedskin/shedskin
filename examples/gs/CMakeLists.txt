add_shedskin_nested_extension(
    MAIN world_manager
    SUBDIR Gh0stenstein
    SYS_MODULES
        array
        math
    APP_MODULES
        Gh0stenstein/world_draw
    DATA
        gs_main.py
    OPTIONS
        "-b"
)
