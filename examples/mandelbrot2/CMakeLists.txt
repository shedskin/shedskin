set(modules
    colorsys
    sys
    time
)

copy_to_build_dir(
    mandelbrot2_main.py
)

add_shedskin_ext_example("${modules}")
