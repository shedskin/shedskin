set(modules
    math
    random
    time
)

copy_to_build_dir(
    fysphun_main.py
)

add_shedskin_ext_example("${modules}")
