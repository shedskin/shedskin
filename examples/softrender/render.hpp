#ifndef __RENDER_HPP
#define __RENDER_HPP

using namespace __shedskin__;
namespace __render__ {

extern str *const_0, *const_1, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7;
extern bytes *const_8;

class Bitmap;
class Vector4;
class Matrix4;
class Quaternion;
class Vertex;
class Transform;
class Camera;
class Mesh;
class Gradients;
class Edge;
class RenderContext;

typedef void *(*lambda0)(void *, void *, void *, void *, void *);
typedef __ss_float (*lambda1)(str *);
typedef __ss_float (*lambda2)(str *);
typedef __ss_float (*lambda3)(str *);
typedef __ss_int (*lambda4)(str *);

extern str *__name__;
extern Mesh *mesh;
extern Bitmap *texture;
extern Vector4 *v;
extern Transform *transform;
extern RenderContext *target;
extern Camera *camera;


extern class_ *cl_Bitmap;
class Bitmap : public pyobj {
public:
    __ss_int height;
    __ss_int width;
    bytes *components;
    bytes *reset;

    Bitmap() {}
    Bitmap(__ss_int width, __ss_int height, bytes *components) {
        this->__class__ = cl_Bitmap;
        __init__(width, height, components);
    }
    void *__init__(__ss_int width, __ss_int height, bytes *components);
    void *clear();
    virtual PyObject *__to_py__();
};

extern class_ *cl_Vector4;
class Vector4 : public pyobj {
public:
    __ss_float z;
    __ss_float w;
    __ss_float x;
    __ss_float y;

    Vector4() {}
    Vector4(__ss_float x, __ss_float y, __ss_float z, __ss_float w) {
        this->__class__ = cl_Vector4;
        __init__(x, y, z, w);
    }
    void *__init__(__ss_float x, __ss_float y, __ss_float z, __ss_float w);
    __ss_float length();
    Vector4 *normalized();
    Vector4 *mul(__ss_float r);
    Vector4 *sub(Vector4 *r);
    Vector4 *add(Vector4 *r);
    __ss_float dot(Vector4 *r);
    Vector4 *cross(Vector4 *r);
    Vector4 *lerp(Vector4 *dest, __ss_float lerpFactor);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Matrix4;
class Matrix4 : public pyobj {
public:
    list<list<__ss_float> *> *m;

    Matrix4() {}
    Matrix4(int __ss_init) {
        this->__class__ = cl_Matrix4;
        __init__();
    }
    void *__init__();
    Matrix4 *init_scale(__ss_float x, __ss_float y, __ss_float z);
    Matrix4 *init_translation(__ss_float x, __ss_float y, __ss_float z);
    Matrix4 *init_rotation(Vector4 *f, Vector4 *u, Vector4 *r);
    Matrix4 *init_screenspace_transform(__ss_float halfWidth, __ss_float halfHeight);
    Matrix4 *init_perspective(__ss_float fov, __ss_float aspectRatio, __ss_float zNear, __ss_float zFar);
    Vector4 *transform(Vector4 *r);
    Matrix4 *mul(Matrix4 *other);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Quaternion;
class Quaternion : public pyobj {
public:
    __ss_float y;
    __ss_float x;
    __ss_float w;
    __ss_float z;

    Quaternion() {}
    Quaternion(__ss_float x, __ss_float y, __ss_float z, __ss_float w) {
        this->__class__ = cl_Quaternion;
        __init__(x, y, z, w);
    }
    void *__init__(__ss_float x, __ss_float y, __ss_float z, __ss_float w);
    __ss_float length();
    Quaternion *normalized();
    Quaternion *conjugate();
    Quaternion *mul(Quaternion *r);
    Matrix4 *to_rotation_matrix();
    virtual PyObject *__to_py__();
};

extern class_ *cl_Vertex;
class Vertex : public pyobj {
public:
    Vector4 *pos;
    Vector4 *normal;
    Vector4 *texCoords;

    Vertex() {}
    Vertex(Vector4 *pos, Vector4 *texCoords, Vector4 *normal) {
        this->__class__ = cl_Vertex;
        __init__(pos, texCoords, normal);
    }
    void *__init__(Vector4 *pos, Vector4 *texCoords, Vector4 *normal);
    Vertex *transform(Matrix4 *transform, Matrix4 *normalTransform);
    __ss_bool inside_view_frustum();
    Vertex *perspective_divide();
    __ss_float triangle_area_times_two(Vertex *b, Vertex *c);
    __ss_float get(__ss_int index);
    Vertex *lerp(Vertex *other, __ss_float lerpAmt);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Transform;
class Transform : public pyobj {
public:
    Vector4 *scale;
    Quaternion *rot;
    Vector4 *pos;

    Transform() {}
    Transform(Vector4 *pos, Quaternion *rot, Vector4 *scale) {
        this->__class__ = cl_Transform;
        __init__(pos, rot, scale);
    }
    void *__init__(Vector4 *pos, Quaternion *rot, Vector4 *scale);
    Transform *rotate(Quaternion *rotation);
    Matrix4 *get_transformation();
    virtual PyObject *__to_py__();
};

extern class_ *cl_Camera;
class Camera : public pyobj {
public:
    Transform *_transform;
    Matrix4 *projection;

    Camera() {}
    Camera(Matrix4 *projection) {
        this->__class__ = cl_Camera;
        __init__(projection);
    }
    void *__init__(Matrix4 *projection);
    Matrix4 *get_view_projection();
    virtual PyObject *__to_py__();
};

extern class_ *cl_Mesh;
class Mesh : public pyobj {
public:
    list<Vertex *> *vertices;
    list<__ss_int> *faces;

    Mesh() {}
    Mesh(str *filename, __ss_int scale) {
        this->__class__ = cl_Mesh;
        __init__(filename, scale);
    }
    void *__init__(str *filename, __ss_int scale);
    void *draw(RenderContext *context, Matrix4 *view_projection, Matrix4 *transform, Bitmap *texture, Vector4 *lightDir);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Gradients;
class Gradients : public pyobj {
public:
    __ss_float depthXStep;
    list<__ss_float> *depth;
    __ss_float texCoordYXStep;
    list<__ss_float> *lightAmt;
    list<__ss_float> *oneOverZ;
    __ss_float oneOverZYStep;
    __ss_float lightAmtXStep;
    list<__ss_float> *texCoordY;
    __ss_float texCoordXYStep;
    __ss_float depthYStep;
    __ss_float lightAmtYStep;
    list<__ss_float> *texCoordX;
    __ss_float texCoordYYStep;
    __ss_float texCoordXXStep;
    __ss_float oneOverZXStep;

    Gradients() {}
    Gradients(Vertex *minYVert, Vertex *midYVert, Vertex *maxYVert, Vector4 *lightDir) {
        this->__class__ = cl_Gradients;
        __init__(minYVert, midYVert, maxYVert, lightDir);
    }
    void *__init__(Vertex *minYVert, Vertex *midYVert, Vertex *maxYVert, Vector4 *lightDir);
    __ss_float CalcXStep(list<__ss_float> *values, Vertex *minYVert, Vertex *midYVert, Vertex *maxYVert, __ss_float oneOverdX);
    __ss_float CalcYStep(list<__ss_float> *values, Vertex *minYVert, Vertex *midYVert, Vertex *maxYVert, __ss_float oneOverdY);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Edge;
class Edge : public pyobj {
public:
    __ss_float xStep;
    __ss_float x;
    __ss_int yEnd;
    __ss_int yStart;
    __ss_float oneOverZ;
    __ss_float lightAmtStep;
    __ss_float lightAmt;
    __ss_float depth;
    __ss_float texCoordXStep;
    __ss_float texCoordX;
    __ss_float texCoordY;
    __ss_float texCoordYStep;
    __ss_float depthStep;
    __ss_float oneOverZStep;

    Edge() {}
    Edge(Gradients *gradients, Vertex *minYVert, Vertex *maxYVert, __ss_int minYVertIndex) {
        this->__class__ = cl_Edge;
        __init__(gradients, minYVert, maxYVert, minYVertIndex);
    }
    void *__init__(Gradients *gradients, Vertex *minYVert, Vertex *maxYVert, __ss_int minYVertIndex);
    void *step();
    virtual PyObject *__to_py__();
};

extern class_ *cl_RenderContext;
class RenderContext : public pyobj {
public:
    __ss_int height;
    Bitmap *bitmap;
    __ss_int width;
    list<__ss_float> *zbuffer;
    list<__ss_float> *zbuffer_reset;
    Matrix4 *screenSpaceTransform;

    RenderContext() {}
    RenderContext(__ss_int width, __ss_int height) {
        this->__class__ = cl_RenderContext;
        __init__(width, height);
    }
    void *__init__(__ss_int width, __ss_int height);
    void *clear();
    void *clear_zbuffer();
    void *draw_triangle(Vertex *v1, Vertex *v2, Vertex *v3, Bitmap *texture, Vector4 *lightDir);
    __ss_bool ClipPolygonAxis(list<Vertex *> *vertices, list<Vertex *> *auxillaryList, __ss_int componentIndex);
    void *ClipPolygonComponent(list<Vertex *> *vertices, __ss_int componentIndex, __ss_float componentFactor, list<Vertex *> *result);
    void *fill_triangle(Vertex *v1, Vertex *v2, Vertex *v3, Bitmap *texture, Vector4 *lightDir);
    void *scan_triangle(Vertex *minYVert, Vertex *midYVert, Vertex *maxYVert, __ss_bool handedness, Bitmap *texture, Vector4 *lightDir);
    void *scan_edges(Gradients *gradients, Edge *a, Edge *b, __ss_bool handedness, Bitmap *texture);
    void *draw_scanline(Gradients *gradients, Edge *left, Edge *right, __ss_int j, Bitmap *texture);
    void *copy_pixel(__ss_int destX, __ss_int destY, __ss_int srcX, __ss_int srcY, Bitmap *src, __ss_float lightAmt);
    virtual PyObject *__to_py__();
};

extern bytes * default_0;
extern Matrix4 * default_1;
extern Vector4 * default_2;
extern Quaternion * default_3;
extern Vector4 * default_4;
__ss_float saturate(__ss_float val);
Quaternion *quaternion_from_axis_angle(Vector4 *axis, __ss_float angle);

extern "C" {
PyMODINIT_FUNC PyInit_render(void);

}
} // module namespace
extern "C" PyTypeObject __ss_render_BitmapObjectType;
extern "C" PyTypeObject __ss_render_Vector4ObjectType;
extern "C" PyTypeObject __ss_render_Matrix4ObjectType;
extern "C" PyTypeObject __ss_render_QuaternionObjectType;
extern "C" PyTypeObject __ss_render_VertexObjectType;
extern "C" PyTypeObject __ss_render_TransformObjectType;
extern "C" PyTypeObject __ss_render_CameraObjectType;
extern "C" PyTypeObject __ss_render_MeshObjectType;
extern "C" PyTypeObject __ss_render_GradientsObjectType;
extern "C" PyTypeObject __ss_render_EdgeObjectType;
extern "C" PyTypeObject __ss_render_RenderContextObjectType;
namespace __shedskin__ { /* XXX */

template<> __render__::Bitmap *__to_ss(PyObject *p);
template<> __render__::Vector4 *__to_ss(PyObject *p);
template<> __render__::Matrix4 *__to_ss(PyObject *p);
template<> __render__::Quaternion *__to_ss(PyObject *p);
template<> __render__::Vertex *__to_ss(PyObject *p);
template<> __render__::Transform *__to_ss(PyObject *p);
template<> __render__::Camera *__to_ss(PyObject *p);
template<> __render__::Mesh *__to_ss(PyObject *p);
template<> __render__::Gradients *__to_ss(PyObject *p);
template<> __render__::Edge *__to_ss(PyObject *p);
template<> __render__::RenderContext *__to_ss(PyObject *p);
}
#endif
