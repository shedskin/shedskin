set(modules
    getopt
    math
    sys
    os
    os.path
    stat
)

copy_to_build_dir(
    voronoi2.txt
)

add_shedskin_example("${modules}")
