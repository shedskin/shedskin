default settings:
    0.716 seconds

shedskin --nobounds --nawrap (accessing the board squares):
    0.595 seconds

shedskin --predict (mostly 8-len lists, possible_moves statistically around average):
    0.570 seconds

changing g++ flags to -O3 -flto:
    0.514 seconds

using g++ flags -fprofile-generate, then -fprofile-use:
    0.445 seconds
