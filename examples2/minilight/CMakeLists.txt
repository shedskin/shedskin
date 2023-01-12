set(modules
    random
    math
    time
    sys
    re
)

copy_to_build_dir(
    cornellbox.txt
)

set(app_modules
    ml/__init__
    ml/camera
    ml/image
    ml/minilight
    ml/raytracer
    ml/scene
    ml/spatialindex
    ml/surfacepoint
    ml/triangle
    ml/vector3f
)

add_shedskin_example("${modules}" "${app_modules}")
