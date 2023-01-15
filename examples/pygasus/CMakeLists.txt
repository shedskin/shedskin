set(modules
    array
    struct
)

set(NO_BOUNDS "ON")

copy_to_build_dir(
    pygasus_main.py
    mario_bros.nes
)

add_shedskin_ext_example("${modules}")
