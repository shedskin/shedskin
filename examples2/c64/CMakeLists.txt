set(modules
    c64
    gi
    optparse
    sys
    time
)

copy_to_build_dir(
    "ROM"
    intkarat.t64
)

add_shedskin_example("${modules}")
