set(modules
    sys
)

copy_to_build_dir(
    randam.ppm
)

add_shedskin_example("${modules}")
