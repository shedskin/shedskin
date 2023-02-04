add_shedskin_nested_extension(
    MAIN SimpleGeometry
    SUBDIR pylot
    SYS_MODULES
        copy
        math
        random
        re
        sys
        time
    APP_MODULES
        pylot/Camera
        pylot/Color
        pylot/Material
        pylot/Ray
        pylot/Shape
        pylot/Utils
        pylot/Vector4
        pylot/World
    DATA
        pylot_main.py
)
