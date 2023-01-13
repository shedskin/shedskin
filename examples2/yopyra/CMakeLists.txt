set(modules
    math
    sys
)

copy_to_build_dir(
    scene.txt
)

add_shedskin_example("${modules}")
