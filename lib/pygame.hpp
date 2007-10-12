#ifndef __PYGAME_HPP
#define __PYGAME_HPP

#include "builtin.hpp"

using namespace __shedskin__;

namespace __pygame__ {

class surface : public pyobj {
public:
    struct _object *screen;

    surface(struct _object *s);
    int fill(tuple2<int, int> *color);
};

class event : public pyobj {
public:
    int type; 
    tuple2<int, int> *pos;
    int button;

};

extern int QUIT, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP;

void __init();
int init();
surface *display_set_mode(tuple2<int, int> *dim, int a, int b);
int display_set_caption(str *s);
int display_flip();
int draw_lines(surface *surf, tuple2<int, int> *c, int a, list<tuple2<int, int> *> *pts, int b);
int draw_circle(surface *surf, tuple2<int, int> *c, tuple2<int, int> *dim, int r);
list<event *> *event_get();
int time_wait(int n);

} // module namespace
#endif
