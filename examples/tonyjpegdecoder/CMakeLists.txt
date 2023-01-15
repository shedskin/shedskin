set(modules
    sys
)

copy_to_build_dir(
    tiger1.jpg
)

add_shedskin_example("${modules}")
