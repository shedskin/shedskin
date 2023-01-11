set(modules
    random
    math
    time
)

copy_to_build_dir(
    pylife_main.py
)

add_shedskin_example("${modules}")
