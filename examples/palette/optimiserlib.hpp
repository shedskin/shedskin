#ifndef __OPTIMISERLIB_HPP
#define __OPTIMISERLIB_HPP

using namespace __shedskin__;
namespace __optimiserlib__ {

extern str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;

class SimpleImage;

typedef tuple<__ss_float> *(*lambda0)(tuple<__ss_int> *);
typedef tuple<tuple<__ss_int> *> *(*lambda1)(tuple<__ss_int> *);
typedef __ss_int (*lambda2)(__ss_float);

extern UnicodeDecodeError *__exception3;
extern UnicodeEncodeError *__exception4;
extern file *__file;
extern __ss_int __void;
extern str *__name__;
extern list<tuple<__ss_int> *> *bases, *corners, *data;
extern __iter<tuple<__ss_float> *> *scaled_corners;
extern list<tuple2<tuple<__ss_int> *, tuple<__ss_float> *> *> *zipped_corners;
extern list<tuple<tuple<__ss_int> *> *> *base_complements;
extern tuple<__ss_int> *rgb;
extern SimpleImage *im, *im2;


extern class_ *cl_SimpleImage;
class SimpleImage : public pyobj {
/**
An image behaving like PIL.Image.
*/
public:
    list<tuple<__ss_int> *> *_data;
    __ss_int height;
    tuple<__ss_int> *size;
    __ss_int width;

    SimpleImage() {}
    SimpleImage(list<tuple<__ss_int> *> *data, tuple<__ss_int> *size) {
        this->__class__ = cl_SimpleImage;
        __init__(data, size);
    }
    static void __static__();
    void *__init__(list<tuple<__ss_int> *> *data, tuple<__ss_int> *size);
    SimpleImage *copy();
    tuple<__ss_int> *getpixel(tuple<__ss_int> *xy);
    void *putpixel(tuple<__ss_int> *xy, tuple<__ss_int> *value);
    list<tuple<__ss_int> *> *getdata();
    virtual PyObject *__to_py__();
};

extern list<tuple<__ss_int> *> * default_0;
extern list<tuple<__ss_int> *> * default_1;
static __ss_float within(__ss_float v, __ss_int lower, __ss_int upper);
static __ss_int clip(__ss_float v);
static __ss_float distance(tuple<__ss_int> *rgb1, tuple<__ss_int> *rgb2);
static tuple<__ss_int> *restore(tuple<__ss_float> *srgb);
static tuple<__ss_float> *scale(tuple<__ss_int> *rgb);
static tuple<__ss_float> *invert(tuple<__ss_float> *srgb);
static list<tuple2<__ss_float, tuple<__ss_int> *> *> *combination(tuple<__ss_int> *rgb);
static tuple<tuple<__ss_int> *> *complements(tuple<__ss_int> *rgb);
static list<tuple2<__ss_float, tuple<__ss_int> *> *> *balance(list<tuple2<__ss_float, tuple<__ss_int> *> *> *d);
static tuple<__ss_int> *combine(list<tuple2<__ss_float, tuple<__ss_int> *> *> *d);
static list<tuple2<__ss_float, tuple<__ss_int> *> *> *pattern(tuple<__ss_int> *rgb, list<tuple<__ss_int> *> *chosen);
static tuple<__ss_int> *get_value(tuple<__ss_int> *rgb, list<tuple<__ss_int> *> *chosen, __ss_bool fail);
static __ss_int sign(__ss_float x);
static tuple<__ss_int> *saturate_rgb(tuple<__ss_int> *rgb, __ss_float exp);
static __ss_int saturate_value(__ss_int x, __ss_float exp);
static tuple<__ss_int> *amplify_rgb(tuple<__ss_int> *rgb, __ss_float exp);
static __ss_int amplify_value(__ss_int x, __ss_float exp);
static list<tuple2<__ss_float, tuple<__ss_int> *> *> *get_colours(SimpleImage *im, __ss_int y);
static list<tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *get_combinations(list<tuple2<__ss_float, tuple<__ss_int> *> *> *c, __ss_int n);
static tuple2<__ss_int, set<tuple<__ss_int> *> *> *count_colours(SimpleImage *im, __ss_int colours);
static void *process_image(SimpleImage *im, __ss_float saturate, __ss_float desaturate, __ss_float darken, __ss_float brighten);
static void *convert_image(SimpleImage *im, __ss_int colours, __ss_bool least_error);

extern "C" {
PyMODINIT_FUNC PyInit_optimiserlib(void);

}
} // module namespace
extern "C" PyTypeObject __ss_optimiserlib_SimpleImageObjectType;
namespace __shedskin__ {

template<> __optimiserlib__::SimpleImage *__to_ss(PyObject *p);
}
#endif
