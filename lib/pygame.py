
class surface: 
    def fill(self, color): 
        pass

class event:
    def __init__(self):
        self.type = 1
        self.pos = (1, 2)
        self.button = 1

def init(): 
    pass

def display_set_mode(dim, a, b):
    return surface()

def display_flip(): 
    pass

def display_set_caption(s): 
    pass

def draw_lines(surf, c, a, pts, b): 
    pass

def draw_circle(surf, c, dim, r):
    pass

def event_get():
    return [event()]

QUIT = 1

MOUSEMOTION = 4
MOUSEBUTTONDOWN = 5
MOUSEBUTTONUP = 6

def time_wait(n):
    pass

