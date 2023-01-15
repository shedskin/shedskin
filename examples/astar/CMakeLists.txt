set(modules)

copy_to_build_dir(
	astar_main.py
	astar_orig.py
)

add_shedskin_ext_example("${modules}")
