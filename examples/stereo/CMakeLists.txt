set(modules
    time
)

copy_to_build_dir(
    stereo_main.py
    "L.bmp"
    "R.bmp"
)

add_shedskin_ext_example("${modules}")
