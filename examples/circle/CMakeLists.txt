set(modules
    sys
)

copy_to_build_dir(
    circle_main.py
)

add_shedskin_ext_example("${modules}")
