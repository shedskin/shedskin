#include <stdio.h>
#include <Python.h>

#include "pygame.hpp"

namespace __pygame__ {

PyObject *mod_pygame, *dict_pygame;
PyObject *pygame_init;

PyObject *mod_display, *dict_display;
PyObject *disp_flip, *disp_set_mode, *disp_set_caption;

PyObject *mod_draw, *dict_draw;
PyObject *drw_lines, *drw_circle;

PyObject *mod_event, *dict_event;
PyObject *evnt_get;

PyObject *mod_time, *dict_time;
PyObject *tme_wait;

int QUIT, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP;

surface::surface(PyObject *s) {
    screen = s;
}

int surface::fill(tuple2<int, int> *c) {
    PyObject *color = PyTuple_New(3);
    PyTuple_SetItem(color, 0, PyInt_FromLong(c->__getitem__(0)));
    PyTuple_SetItem(color, 1, PyInt_FromLong(c->__getitem__(1)));
    PyTuple_SetItem(color, 2, PyInt_FromLong(c->__getitem__(2)));

    PyObject *args = PyTuple_New(1);
    PyTuple_SetItem(args, 0, color);

    PyObject *screen_fill = PyObject_GetAttrString(screen, "fill");
    PyObject_CallObject(screen_fill, args);

    return 0;
}

int init() {
    MOUSEMOTION = 4;
    MOUSEBUTTONDOWN = 5;
    MOUSEBUTTONUP = 6;
    QUIT = 12;

    Py_Initialize();

    mod_pygame = PyImport_ImportModule("pygame");
    dict_pygame = PyObject_GetAttrString(mod_pygame, "__dict__");
    pygame_init = PyDict_GetItemString(dict_pygame, "init");

    mod_display = PyDict_GetItemString(dict_pygame, "display");
    dict_display = PyObject_GetAttrString(mod_display, "__dict__");
    disp_flip = PyDict_GetItemString(dict_display, "flip");
    disp_set_mode = PyDict_GetItemString(dict_display, "set_mode");
    disp_set_caption = PyDict_GetItemString(dict_display, "set_caption");

    mod_draw = PyDict_GetItemString(dict_pygame, "draw");
    dict_draw = PyObject_GetAttrString(mod_draw, "__dict__");
    drw_lines = PyDict_GetItemString(dict_draw, "lines");  
    drw_circle = PyDict_GetItemString(dict_draw, "circle");  

    mod_event = PyDict_GetItemString(dict_pygame, "event");
    dict_event = PyObject_GetAttrString(mod_event, "__dict__");
    evnt_get = PyDict_GetItemString(dict_event, "get");  

    mod_time = PyDict_GetItemString(dict_pygame, "time");
    dict_time = PyObject_GetAttrString(mod_time, "__dict__");
    tme_wait = PyDict_GetItemString(dict_time, "wait");  

    PyObject_CallObject(pygame_init, 0);

    return 0;
}

void __init() {
}

list<event *> *event_get() {
        list<event *> *l = new list<event *>();

        PyObject *g = PyObject_CallObject(evnt_get, 0);

        for(int i=0; i<PyList_Size(g); i++) {
            PyObject *type = PyObject_GetAttrString(PyList_GetItem(g, i), "type");
            PyObject *item = PyList_GetItem(g,i);
            event *e = new event();
            e->type = PyInt_AsLong(type);
        
            if(PyObject_HasAttrString(item, "pos")) {
                    PyObject *pos = PyObject_GetAttrString(item, "pos");
                    e->pos = new tuple2<int, int>(2, PyInt_AsLong(PyTuple_GetItem(pos, 0)), PyInt_AsLong(PyTuple_GetItem(pos, 1)));
            }
            if(PyObject_HasAttrString(item, "button")) {
                    PyObject *button = PyObject_GetAttrString(item, "button");
                    e->button = PyInt_AsLong(button);
            }

            l->append(e);
        }

        return l;
}

int display_set_caption(str *s) {
    PyObject *caption = PyString_FromString(s->unit.c_str());

    PyObject *args = PyTuple_New(1);
    PyTuple_SetItem(args, 0, caption);

    PyObject_CallObject(disp_set_caption, args);

    return 0;
}

surface *display_set_mode(tuple2<int, int> *t, int a, int b) {
    PyObject *dim = PyTuple_New(2);
    PyTuple_SetItem(dim, 0, PyInt_FromLong(t->__getitem__(0)));
    PyTuple_SetItem(dim, 1, PyInt_FromLong(t->__getitem__(1)));

    PyObject *args = PyTuple_New(3);
    PyTuple_SetItem(args, 0, dim);
    PyTuple_SetItem(args, 1, PyInt_FromLong(a));
    PyTuple_SetItem(args, 2, PyInt_FromLong(b));

    PyObject *screen = PyObject_CallObject(disp_set_mode, args);
    
    return (new surface(screen));
}

int display_flip() {
    PyObject_CallObject(disp_flip, 0);

    return 0;
}

int time_wait(int n) {
    PyObject *nr = PyInt_FromLong(n);

    PyObject *args = PyTuple_New(1);
    PyTuple_SetItem(args, 0, nr);

    PyObject_CallObject(tme_wait, args);

    return 0;
}

int draw_lines(surface *surf, tuple2<int, int> *c, int a, list<tuple2<int, int> *> *l, int b) {
    PyObject *points = PyList_New(0);
    for(int i=0; i<l->__len__(); i++) {
        PyObject *t = PyTuple_New(2);
        PyTuple_SetItem(t, 0, PyInt_FromLong(l->__getitem__(i)->__getitem__(0)));
        PyTuple_SetItem(t, 1, PyInt_FromLong(l->__getitem__(i)->__getitem__(1)));
        PyList_Append(points, t);
    }

    PyObject *color = PyTuple_New(3);
    PyTuple_SetItem(color, 0, PyInt_FromLong(c->__getitem__(0)));
    PyTuple_SetItem(color, 1, PyInt_FromLong(c->__getitem__(1)));
    PyTuple_SetItem(color, 2, PyInt_FromLong(c->__getitem__(2)));

    PyObject *args = PyTuple_New(5);
    PyTuple_SetItem(args, 0, surf->screen);
    PyTuple_SetItem(args, 1, color);
    PyTuple_SetItem(args, 2, PyInt_FromLong(a));
    PyTuple_SetItem(args, 3, points);
    PyTuple_SetItem(args, 4, PyInt_FromLong(b));

    PyObject_CallObject(drw_lines, args); 
    
    return 0;
} 

int draw_circle(surface *surf, tuple2<int, int> *c, tuple2<int, int> *dim, int r) {
    PyObject *color = PyTuple_New(3);
    PyTuple_SetItem(color, 0, PyInt_FromLong(c->__getitem__(0)));
    PyTuple_SetItem(color, 1, PyInt_FromLong(c->__getitem__(1)));
    PyTuple_SetItem(color, 2, PyInt_FromLong(c->__getitem__(2)));

    PyObject *dimension = PyTuple_New(2);
    PyTuple_SetItem(dimension, 0, PyInt_FromLong(dim->__getitem__(0)));
    PyTuple_SetItem(dimension, 1, PyInt_FromLong(dim->__getitem__(1)));

    PyObject *args = PyTuple_New(4);
    PyTuple_SetItem(args, 0, surf->screen);
    PyTuple_SetItem(args, 1, color);
    PyTuple_SetItem(args, 2, dimension);
    PyTuple_SetItem(args, 3, PyInt_FromLong(r));

    PyObject_CallObject(drw_circle, args); 

    return 0;
}

} // module namespace

