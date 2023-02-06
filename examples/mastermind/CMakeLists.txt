add_shedskin_extension(
    MAIN_MODULE mm/mastermind.py
    SYS_MODULES
        random
        math
        time
        re
        sys
    APP_MODULES
        mm/board
        mm/code
        mm/colour
        mm/game
        mm/peg
        mm/row
    DATA
        mastermind_main.py
)
