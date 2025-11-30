#include "builtin.hpp"
#include "math.hpp"
#include "render.hpp"

namespace __render__ {

str *const_0, *const_1, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7;
bytes *const_8;


str *__name__;
Mesh *mesh;
Bitmap *texture;
Vector4 *v;
Transform *transform;
RenderContext *target;
Camera *camera;


bytes * default_0;
Matrix4 * default_1;
Vector4 * default_2;
Quaternion * default_3;
Vector4 * default_4;
static inline list<__ss_float> *list_comp_0();
static inline list<list<__ss_float> *> *list_comp_1();
static inline __ss_float __lambda1__(str *a);
static inline __ss_float __lambda2__(str *a);
static inline __ss_float __lambda3__(str *a);
static inline __ss_int __lambda4__(str *a);

static inline list<__ss_float> *list_comp_0() {
    __ss_int __10, __11, i;

    list<__ss_float> *__ss_result = new list<__ss_float>();

    FAST_FOR(i,0,__ss_int(4),1,10,11)
        __ss_result->append(__ss_float(0.0));
    END_FOR

    return __ss_result;
}

static inline list<list<__ss_float> *> *list_comp_1() {
    __ss_int __8, __9, j;

    list<list<__ss_float> *> *__ss_result = new list<list<__ss_float> *>();

    FAST_FOR(j,0,__ss_int(4),1,8,9)
        __ss_result->append(list_comp_0());
    END_FOR

    return __ss_result;
}

static inline __ss_float __lambda1__(str *a) {
    return __float(a);
}

static inline __ss_float __lambda2__(str *a) {
    return __float(a);
}

static inline __ss_float __lambda3__(str *a) {
    return __float(a);
}

static inline __ss_int __lambda4__(str *a) {
    return __int(a);
}

__ss_float saturate(__ss_float val) {
    return ___max(2, (__ss_float(__ss_int(0))), __ss_float(0.0), ___min(2, (__ss_float(__ss_int(0))), val, __ss_float(1.0)));
}

/**
class Bitmap
*/

class_ *cl_Bitmap;

void *Bitmap::__init__(__ss_int width, __ss_int height, bytes *components) {
    __ss_int __0, __1;
    bytes *__2, *__3;

    __0 = width;
    __1 = height;
    this->width = __0;
    this->height = __1;
    this->components = __OR(components, __bytearray(((width*height)*__ss_int(4))), 2);
    this->reset = __bytearray(((width*height)*__ss_int(4)));
    return NULL;
}

void *Bitmap::clear() {
    (this->components)->__setslice__(__ss_int(0),__ss_int(0),__ss_int(0),__ss_int(0),this->reset);
    return NULL;
}

/**
class Vector4
*/

class_ *cl_Vector4;

void *Vector4::__init__(__ss_float x, __ss_float y, __ss_float z, __ss_float w) {
    __ss_float __4, __5, __6, __7;

    __4 = x;
    __5 = y;
    __6 = z;
    __7 = w;
    this->x = __4;
    this->y = __5;
    this->z = __6;
    this->w = __7;
    return NULL;
}

__ss_float Vector4::length() {
    return __math__::sqrt(((((this->x*this->x)+(this->y*this->y))+(this->z*this->z))+(this->w*this->w)));
}

Vector4 *Vector4::normalized() {
    return this->mul((__ss_int(1)/this->length()));
}

Vector4 *Vector4::mul(__ss_float r) {
    return (new Vector4((this->x*r), (this->y*r), (this->z*r), (this->w*r)));
}

Vector4 *Vector4::sub(Vector4 *r) {
    return (new Vector4((this->x-r->x), (this->y-r->y), (this->z-r->z), (this->w-r->w)));
}

Vector4 *Vector4::add(Vector4 *r) {
    return (new Vector4((this->x+r->x), (this->y+r->y), (this->z+r->z), (this->w+r->w)));
}

__ss_float Vector4::dot(Vector4 *r) {
    return ((((this->x*r->x)+(this->y*r->y))+(this->z*r->z))+(this->w*r->w));
}

Vector4 *Vector4::cross(Vector4 *r) {
    return (new Vector4(((this->y*r->z)-(this->z*r->y)), ((this->z*r->x)-(this->x*r->z)), ((this->x*r->y)-(this->y*r->x)), ((__ss_float)(__ss_int(0)))));
}

Vector4 *Vector4::lerp(Vector4 *dest, __ss_float lerpFactor) {
    return ((dest->sub(this))->mul(lerpFactor))->add(this);
}

/**
class Matrix4
*/

class_ *cl_Matrix4;

void *Matrix4::__init__() {
    this->m = list_comp_1();
    return NULL;
}

Matrix4 *Matrix4::init_scale(__ss_float x, __ss_float y, __ss_float z) {
    list<list<__ss_float> *> *m;
    list<__ss_float> *__12, *__13, *__14, *__15, *__16, *__17, *__18, *__19, *__20, *__21, *__22, *__23, *__24, *__25, *__26, *__27;

    m = this->m;
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(0), x);
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(1), y);
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(2), z);
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(1)));
    return this;
}

Matrix4 *Matrix4::init_translation(__ss_float x, __ss_float y, __ss_float z) {
    list<list<__ss_float> *> *m;
    list<__ss_float> *__28, *__29, *__30, *__31, *__32, *__33, *__34, *__35, *__36, *__37, *__38, *__39, *__40, *__41, *__42, *__43;

    m = this->m;
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(1)));
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(3), x);
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(1)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(3), y);
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(1)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(3), z);
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(1)));
    return this;
}

Matrix4 *Matrix4::init_rotation(Vector4 *f, Vector4 *u, Vector4 *r) {
    list<list<__ss_float> *> *m;
    list<__ss_float> *__44, *__45, *__46, *__47, *__48, *__49, *__50, *__51, *__52, *__53, *__54, *__55, *__56, *__57, *__58, *__59;

    m = this->m;
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(0), r->x);
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(1), r->y);
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(2), r->z);
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(0), u->x);
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(1), u->y);
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(2), u->z);
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(0), f->x);
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(1), f->y);
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(2), f->z);
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(1)));
    return this;
}

Matrix4 *Matrix4::init_screenspace_transform(__ss_float halfWidth, __ss_float halfHeight) {
    list<list<__ss_float> *> *m;
    list<__ss_float> *__60, *__61, *__62, *__63, *__64, *__65, *__66, *__67, *__68, *__69, *__70, *__71, *__72, *__73, *__74, *__75;

    m = this->m;
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(0), halfWidth);
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(3), (halfWidth-__ss_float(0.5)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(1), (-halfHeight));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(3), (halfHeight-__ss_float(0.5)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(1)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(1)));
    return this;
}

Matrix4 *Matrix4::init_perspective(__ss_float fov, __ss_float aspectRatio, __ss_float zNear, __ss_float zFar) {
    __ss_float tanHalfFOV, zRange;
    list<list<__ss_float> *> *m;
    list<__ss_float> *__76, *__77, *__78, *__79, *__80, *__81, *__82, *__83, *__84, *__85, *__86, *__87, *__88, *__89, *__90, *__91;

    tanHalfFOV = __math__::tan((fov/__ss_int(2)));
    zRange = (zNear-zFar);
    m = this->m;
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(0), (__ss_float(1.0)/(tanHalfFOV*aspectRatio)));
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(0))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(1), (__ss_float(1.0)/tanHalfFOV));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(1))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(2), (((-zNear)-zFar)/zRange));
    m->__getfast__(__ss_int(2))->__setitem__(__ss_int(3), (((__ss_int(2)*zFar)*zNear)/zRange));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(0), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(1), ((__ss_float )__ss_int(0)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(2), ((__ss_float )__ss_int(1)));
    m->__getfast__(__ss_int(3))->__setitem__(__ss_int(3), ((__ss_float )__ss_int(0)));
    return this;
}

Vector4 *Matrix4::transform(Vector4 *r) {
    list<list<__ss_float> *> *m;

    m = this->m;
    return (new Vector4((((((m->__getfast__(__ss_int(0)))->__getfast__(__ss_int(0))*r->x)+((m->__getfast__(__ss_int(0)))->__getfast__(__ss_int(1))*r->y))+((m->__getfast__(__ss_int(0)))->__getfast__(__ss_int(2))*r->z))+((m->__getfast__(__ss_int(0)))->__getfast__(__ss_int(3))*r->w)), (((((m->__getfast__(__ss_int(1)))->__getfast__(__ss_int(0))*r->x)+((m->__getfast__(__ss_int(1)))->__getfast__(__ss_int(1))*r->y))+((m->__getfast__(__ss_int(1)))->__getfast__(__ss_int(2))*r->z))+((m->__getfast__(__ss_int(1)))->__getfast__(__ss_int(3))*r->w)), (((((m->__getfast__(__ss_int(2)))->__getfast__(__ss_int(0))*r->x)+((m->__getfast__(__ss_int(2)))->__getfast__(__ss_int(1))*r->y))+((m->__getfast__(__ss_int(2)))->__getfast__(__ss_int(2))*r->z))+((m->__getfast__(__ss_int(2)))->__getfast__(__ss_int(3))*r->w)), (((((m->__getfast__(__ss_int(3)))->__getfast__(__ss_int(0))*r->x)+((m->__getfast__(__ss_int(3)))->__getfast__(__ss_int(1))*r->y))+((m->__getfast__(__ss_int(3)))->__getfast__(__ss_int(2))*r->z))+((m->__getfast__(__ss_int(3)))->__getfast__(__ss_int(3))*r->w))));
}

Matrix4 *Matrix4::mul(Matrix4 *other) {
    list<list<__ss_float> *> *m, *r;
    Matrix4 *res;
    __ss_int __92, __93, __94, __95, i, j;
    list<__ss_float> *__96;

    m = this->m;
    r = other->m;
    res = (new Matrix4(1));

    FAST_FOR(i,0,__ss_int(4),1,92,93)

        FAST_FOR(j,0,__ss_int(4),1,94,95)
            (res->m)->__getfast__(i)->__setitem__(j, (((((m->__getfast__(i))->__getfast__(__ss_int(0))*(r->__getfast__(__ss_int(0)))->__getfast__(j))+((m->__getfast__(i))->__getfast__(__ss_int(1))*(r->__getfast__(__ss_int(1)))->__getfast__(j)))+((m->__getfast__(i))->__getfast__(__ss_int(2))*(r->__getfast__(__ss_int(2)))->__getfast__(j)))+((m->__getfast__(i))->__getfast__(__ss_int(3))*(r->__getfast__(__ss_int(3)))->__getfast__(j))));
        END_FOR

    END_FOR

    return res;
}

/**
class Quaternion
*/

class_ *cl_Quaternion;

void *Quaternion::__init__(__ss_float x, __ss_float y, __ss_float z, __ss_float w) {
    __ss_float __100, __97, __98, __99;

    __97 = x;
    __98 = y;
    __99 = z;
    __100 = w;
    this->x = __97;
    this->y = __98;
    this->z = __99;
    this->w = __100;
    return NULL;
}

__ss_float Quaternion::length() {
    return __math__::sqrt(((((this->x*this->x)+(this->y*this->y))+(this->z*this->z))+(this->w*this->w)));
}

Quaternion *Quaternion::normalized() {
    __ss_float length;

    length = this->length();
    return (new Quaternion((this->x/length), (this->y/length), (this->z/length), (this->w/length)));
}

Quaternion *Quaternion::conjugate() {
    return (new Quaternion((-this->x), (-this->y), (-this->z), this->w));
}

Quaternion *Quaternion::mul(Quaternion *r) {
    return (new Quaternion(((((this->x*r->w)+(this->w*r->x))+(this->y*r->z))-(this->z*r->y)), ((((this->y*r->w)+(this->w*r->y))+(this->z*r->x))-(this->x*r->z)), ((((this->z*r->w)+(this->w*r->z))+(this->x*r->y))-(this->y*r->x)), ((((this->w*r->w)-(this->x*r->x))-(this->y*r->y))-(this->z*r->z))));
}

Matrix4 *Quaternion::to_rotation_matrix() {
    return ((new Matrix4(1)))->init_rotation((new Vector4((__ss_float(2.0)*((this->x*this->z)-(this->w*this->y))), (__ss_float(2.0)*((this->y*this->z)+(this->w*this->x))), (__ss_float(1.0)-(__ss_float(2.0)*((this->x*this->x)+(this->y*this->y)))), __ss_float(1.0))), (new Vector4((__ss_float(2.0)*((this->x*this->y)+(this->w*this->z))), (__ss_float(1.0)-(__ss_float(2.0)*((this->x*this->x)+(this->z*this->z)))), (__ss_float(2.0)*((this->y*this->z)-(this->w*this->x))), __ss_float(1.0))), (new Vector4((__ss_float(1.0)-(__ss_float(2.0)*((this->y*this->y)+(this->z*this->z)))), (__ss_float(2.0)*((this->x*this->y)-(this->w*this->z))), (__ss_float(2.0)*((this->x*this->z)+(this->w*this->y))), __ss_float(1.0))));
}

Quaternion *quaternion_from_axis_angle(Vector4 *axis, __ss_float angle) {
    __ss_float cos_half_angle, sin_half_angle;

    sin_half_angle = __math__::sin((angle/__ss_int(2)));
    cos_half_angle = __math__::cos((angle/__ss_int(2)));
    return (new Quaternion((axis->x*sin_half_angle), (axis->y*sin_half_angle), (axis->z*sin_half_angle), cos_half_angle));
}

/**
class Vertex
*/

class_ *cl_Vertex;

void *Vertex::__init__(Vector4 *pos, Vector4 *texCoords, Vector4 *normal) {
    this->pos = pos;
    this->texCoords = texCoords;
    this->normal = normal;
    return NULL;
}

Vertex *Vertex::transform(Matrix4 *transform, Matrix4 *normalTransform) {
    Vector4 *normal;

    if (___bool(normalTransform)) {
        normal = (normalTransform->transform(this->normal))->normalized();
    }
    else {
        normal = this->normal;
    }
    return (new Vertex(transform->transform(this->pos), this->texCoords, normal));
}

__ss_bool Vertex::inside_view_frustum() {
    __ss_bool __101, __102, __103;

    return __AND(___bool((__abs((this->pos)->x)<=__abs((this->pos)->w))), __AND(___bool((__abs((this->pos)->y)<=__abs((this->pos)->w))), ___bool((__abs((this->pos)->z)<=__abs((this->pos)->w))), 102), 101);
}

Vertex *Vertex::perspective_divide() {
    __ss_float w;

    w = (this->pos)->w;
    return (new Vertex((new Vector4(((this->pos)->x/w), ((this->pos)->y/w), ((this->pos)->z/w), w)), this->texCoords, this->normal));
}

__ss_float Vertex::triangle_area_times_two(Vertex *b, Vertex *c) {
    return ((((b->pos)->x-(this->pos)->x)*((c->pos)->y-(this->pos)->y))-(((c->pos)->x-(this->pos)->x)*((b->pos)->y-(this->pos)->y)));
}

__ss_float Vertex::get(__ss_int index) {
    if ((index==__ss_int(0))) {
        return (this->pos)->x;
    }
    else if ((index==__ss_int(1))) {
        return (this->pos)->y;
    }
    else if ((index==__ss_int(2))) {
        return (this->pos)->z;
    }
    else if ((index==__ss_int(3))) {
        return (this->pos)->w;
    }
    throw (new IndexError());
    return 0;
}

Vertex *Vertex::lerp(Vertex *other, __ss_float lerpAmt) {
    return (new Vertex((this->pos)->lerp(other->pos, lerpAmt), (this->texCoords)->lerp(other->texCoords, lerpAmt), (this->normal)->lerp(other->normal, lerpAmt)));
}

/**
class Transform
*/

class_ *cl_Transform;

void *Transform::__init__(Vector4 *pos, Quaternion *rot, Vector4 *scale) {
    Vector4 *__104, *__105, *__108, *__109;
    Quaternion *__106, *__107;

    this->pos = __OR(pos, (new Vector4(__ss_float(0.0), __ss_float(0.0), __ss_float(0.0), __ss_float(0.0))), 104);
    this->rot = __OR(rot, (new Quaternion(__ss_float(0.0), __ss_float(0.0), __ss_float(0.0), __ss_float(1.0))), 106);
    this->scale = __OR(scale, (new Vector4(__ss_float(1.0), __ss_float(1.0), __ss_float(1.0), __ss_float(1.0))), 108);
    return NULL;
}

Transform *Transform::rotate(Quaternion *rotation) {
    return (new Transform(this->pos, (rotation->mul(this->rot))->normalized(), this->scale));
}

Matrix4 *Transform::get_transformation() {
    Matrix4 *rotationMatrix, *scaleMatrix, *translationMatrix;

    translationMatrix = ((new Matrix4(1)))->init_translation((this->pos)->x, (this->pos)->y, (this->pos)->z);
    rotationMatrix = (this->rot)->to_rotation_matrix();
    scaleMatrix = ((new Matrix4(1)))->init_scale((this->scale)->x, (this->scale)->y, (this->scale)->z);
    return translationMatrix->mul(rotationMatrix->mul(scaleMatrix));
}

/**
class Camera
*/

class_ *cl_Camera;

void *Camera::__init__(Matrix4 *projection) {
    this->projection = projection;
    this->_transform = (new Transform(NULL, NULL, NULL));
    return NULL;
}

Matrix4 *Camera::get_view_projection() {
    Matrix4 *camera_rotation, *camera_translation;
    Vector4 *camera_pos;

    camera_rotation = (((this->_transform)->rot)->conjugate())->to_rotation_matrix();
    camera_pos = ((this->_transform)->pos)->mul(((__ss_float)((-__ss_int(1)))));
    camera_translation = ((new Matrix4(1)))->init_translation(camera_pos->x, camera_pos->y, camera_pos->z);
    return (this->projection)->mul(camera_rotation->mul(camera_translation));
}

/**
class Mesh
*/

class_ *cl_Mesh;

void *Mesh::__init__(str *filename, __ss_int scale) {
    list<tuple<__ss_float> *> *normals, *texcoords, *vertices;
    str *__126, *line, *token;
    __ss_float a, b, c, tu, tv, x, y, z;
    dict<tuple<__ss_int> *, __ss_int> *index;
    list<__ss_int> *__138, *idcs;
    __ss_int __112, __119, __123, __133, __134, __135, __136, __137, __141, __145, i, i0, i1, i2, idx, j, n, t, v;
    Vertex *vertex, *vtx;
    dict<tuple<__ss_float> *, Vector4 *> *pos_normal;
    Vector4 *havenormal, *normal, *v1, *v2;
    tuple<__ss_float> *__128, *__129, *__132, *key;
    file *__110, *__117;
    __iter<str *> *__111, *__118, *__122;
    file::for_in_loop __113, __120;
    __iter<__ss_float> *__114, *__115, *__116;
    list<str *> *__121;
    list<str *>::for_in_loop __124;
    void *__125;
    __iter<__ss_int> *__127, *__140;
    pyobj *__130, *__131;
    tuple<__ss_int> *__139;
    tuple<__ss_int>::for_in_loop __142;
    list<Vertex *> *__143;
    __iter<Vertex *> *__144;
    list<Vertex *>::for_in_loop __146;

    this->vertices = (new list<Vertex *>());
    this->faces = (new list<__ss_int>());
    vertices = (new list<tuple<__ss_float> *>());
    texcoords = (new list<tuple<__ss_float> *>());
    normals = (new list<tuple<__ss_float> *>());

    FOR_IN(line,open(filename),110,112,113)
        if (line->startswith(const_0)) {
            __114 = map(1, False, __lambda1__, (line->__slice__(__ss_int(1), __ss_int(2), __ss_int(0), __ss_int(0)))->split(NULL, (-__ss_int(1))));
            list<__ss_float > *__114_list = new list<__ss_float >(__114);
            __unpack_check(__114_list, 3);
            x = __114_list->__getitem__(0);
            y = __114_list->__getitem__(1);
            z = __114_list->__getitem__(2);
            vertices->append((new tuple<__ss_float>(3,(x/scale),(y/scale),(z/scale))));
        }
        else if (line->startswith(const_1)) {
            __115 = map(1, False, __lambda2__, (line->__slice__(__ss_int(1), __ss_int(2), __ss_int(0), __ss_int(0)))->split(NULL, (-__ss_int(1))));
            list<__ss_float > *__115_list = new list<__ss_float >(__115);
            __unpack_check(__115_list, 2);
            tu = __115_list->__getitem__(0);
            tv = __115_list->__getitem__(1);
            texcoords->append((new tuple<__ss_float>(2,tu,(__ss_float(1.0)-tv))));
        }
        else if (line->startswith(const_2)) {
            __116 = map(1, False, __lambda3__, (line->__slice__(__ss_int(1), __ss_int(2), __ss_int(0), __ss_int(0)))->split(NULL, (-__ss_int(1))));
            list<__ss_float > *__116_list = new list<__ss_float >(__116);
            __unpack_check(__116_list, 3);
            x = __116_list->__getitem__(0);
            y = __116_list->__getitem__(1);
            z = __116_list->__getitem__(2);
            normals->append((new tuple<__ss_float>(3,x,y,z)));
        }
    END_FOR

    index = (new dict<tuple<__ss_int> *, __ss_int>());

    FOR_IN(line,open(filename),117,119,120)
        if (line->startswith(const_3)) {
            idcs = (new list<__ss_int>());

            FOR_IN(token,(line->__slice__(__ss_int(1), __ss_int(2), __ss_int(0), __ss_int(0)))->split(NULL, (-__ss_int(1))),121,123,124)
                __127 = map(1, False, __lambda4__, token->split(const_4, (-__ss_int(1))));
                list<__ss_int > *__127_list = new list<__ss_int >(__127);
                __unpack_check(__127_list, 3);
                v = __127_list->__getitem__(0);
                t = __127_list->__getitem__(1);
                n = __127_list->__getitem__(2);
                if (__NOT(___bool(normals))) {
                    n = __ss_int(0);
                }
                idx = index->get((new tuple<__ss_int>(3,v,t,n)), (-__ss_int(1)));
                if ((idx==(-__ss_int(1)))) {
                    __128 = vertices->__getfast__((v-__ss_int(1)));
                    __unpack_check(__128, 3);
                    x = __128->__getfast__(0);
                    y = __128->__getfast__(1);
                    z = __128->__getfast__(2);
                    __129 = texcoords->__getfast__((t-__ss_int(1)));
                    __unpack_check(__129, 2);
                    tu = __129->__getfirst__();
                    tv = __129->__getsecond__();
                    a = ((__ss_float)(__ss_int(0)));
                    b = ((__ss_float)(__ss_int(0)));
                    c = ((__ss_float)(__ss_int(0)));
                    if ((___bool(normals) and ((n-__ss_int(1))<len(normals)))) {
                        __132 = normals->__getfast__((n-__ss_int(1)));
                        __unpack_check(__132, 3);
                        a = __132->__getfast__(0);
                        b = __132->__getfast__(1);
                        c = __132->__getfast__(2);
                    }
                    vertex = (new Vertex((new Vector4(x, y, z, ((__ss_float)(__ss_int(1))))), (new Vector4(tu, tv, ((__ss_float)(__ss_int(0))), ((__ss_float)(__ss_int(0))))), (new Vector4(a, b, c, ((__ss_float)(__ss_int(0)))))));
                    __133 = len(this->vertices);
                    index->__setitem__((new tuple<__ss_int>(3,v,t,n)), __133);
                    idx = __133;
                    (this->vertices)->append(vertex);
                }
                idcs->append(idx);
            END_FOR


            FAST_FOR(i,0,(len(idcs)-__ss_int(2)),1,134,135)
                (this->faces)->extend((new list<__ss_int>(3,idcs->__getfast__(__ss_int(0)),idcs->__getfast__((i+__ss_int(1))),idcs->__getfast__((i+__ss_int(2))))));
            END_FOR

        }
    END_FOR

    if (__NOT(___bool(normals))) {
        pos_normal = (new dict<tuple<__ss_float> *, Vector4 *>());

        FAST_FOR(i,__ss_int(0),len(this->faces),__ss_int(3),136,137)
            __138 = (this->faces)->__slice__(__ss_int(3), i, (i+__ss_int(3)), __ss_int(0));
            __unpack_check(__138, 3);
            i0 = __138->__getfast__(0);
            i1 = __138->__getfast__(1);
            i2 = __138->__getfast__(2);
            v1 = (((this->vertices)->__getfast__(i1))->pos)->sub(((this->vertices)->__getfast__(i0))->pos);
            v2 = (((this->vertices)->__getfast__(i2))->pos)->sub(((this->vertices)->__getfast__(i0))->pos);
            normal = (v1->cross(v2))->normalized();

            FOR_IN(j,(new tuple<__ss_int>(3,i0,i1,i2)),139,141,142)
                vtx = (this->vertices)->__getfast__(j);
                key = (new tuple<__ss_float>(3,(vtx->pos)->x,(vtx->pos)->y,(vtx->pos)->z));
                if ((pos_normal)->__contains__(key)) {
                    havenormal = pos_normal->__getitem__(key);
                }
                else {
                    havenormal = (new Vector4(((__ss_float)(__ss_int(0))), ((__ss_float)(__ss_int(0))), ((__ss_float)(__ss_int(0))), ((__ss_float)(__ss_int(0)))));
                }
                pos_normal->__setitem__(key, havenormal->add(normal));
            END_FOR

        END_FOR


        FOR_IN(vtx,this->vertices,143,145,146)
            vtx->normal = (pos_normal->__getitem__((new tuple<__ss_float>(3,(vtx->pos)->x,(vtx->pos)->y,(vtx->pos)->z))))->normalized();
        END_FOR

    }
    return NULL;
}

void *Mesh::draw(RenderContext *context, Matrix4 *view_projection, Matrix4 *transform, Bitmap *texture, Vector4 *lightDir) {
    Matrix4 *mvp;
    __ss_int __147, __148, i;

    mvp = view_projection->mul(transform);

    FAST_FOR(i,__ss_int(0),len(this->faces),__ss_int(3),147,148)
        context->draw_triangle(((this->vertices)->__getfast__((this->faces)->__getfast__(i)))->transform(mvp, transform), ((this->vertices)->__getfast__((this->faces)->__getfast__((i+__ss_int(1)))))->transform(mvp, transform), ((this->vertices)->__getfast__((this->faces)->__getfast__((i+__ss_int(2)))))->transform(mvp, transform), texture, lightDir);
    END_FOR

    return NULL;
}

/**
class Gradients
*/

class_ *cl_Gradients;

void *Gradients::__init__(Vertex *minYVert, Vertex *midYVert, Vertex *maxYVert, Vector4 *lightDir) {
    __ss_float oneOverdX, oneOverdY;

    this->depth = (new list<__ss_float>(3,(minYVert->pos)->z,(midYVert->pos)->z,(maxYVert->pos)->z));
    this->oneOverZ = (new list<__ss_float>(3,(__ss_float(1.0)/(minYVert->pos)->w),(__ss_float(1.0)/(midYVert->pos)->w),(__ss_float(1.0)/(maxYVert->pos)->w)));
    this->lightAmt = (new list<__ss_float>(3,((saturate((minYVert->normal)->dot(lightDir))*__ss_float(0.5))+__ss_float(0.5)),((saturate((midYVert->normal)->dot(lightDir))*__ss_float(0.5))+__ss_float(0.5)),((saturate((maxYVert->normal)->dot(lightDir))*__ss_float(0.5))+__ss_float(0.5))));
    this->texCoordX = (new list<__ss_float>(3,((minYVert->texCoords)->x*(this->oneOverZ)->__getfast__(__ss_int(0))),((midYVert->texCoords)->x*(this->oneOverZ)->__getfast__(__ss_int(1))),((maxYVert->texCoords)->x*(this->oneOverZ)->__getfast__(__ss_int(2)))));
    this->texCoordY = (new list<__ss_float>(3,((minYVert->texCoords)->y*(this->oneOverZ)->__getfast__(__ss_int(0))),((midYVert->texCoords)->y*(this->oneOverZ)->__getfast__(__ss_int(1))),((maxYVert->texCoords)->y*(this->oneOverZ)->__getfast__(__ss_int(2)))));
    oneOverdX = (__ss_float(1.0)/((((midYVert->pos)->x-(maxYVert->pos)->x)*((minYVert->pos)->y-(maxYVert->pos)->y))-(((minYVert->pos)->x-(maxYVert->pos)->x)*((midYVert->pos)->y-(maxYVert->pos)->y))));
    oneOverdY = (-oneOverdX);
    this->texCoordXXStep = this->CalcXStep(this->texCoordX, minYVert, midYVert, maxYVert, oneOverdX);
    this->texCoordXYStep = this->CalcYStep(this->texCoordX, minYVert, midYVert, maxYVert, oneOverdY);
    this->texCoordYXStep = this->CalcXStep(this->texCoordY, minYVert, midYVert, maxYVert, oneOverdX);
    this->texCoordYYStep = this->CalcYStep(this->texCoordY, minYVert, midYVert, maxYVert, oneOverdY);
    this->oneOverZXStep = this->CalcXStep(this->oneOverZ, minYVert, midYVert, maxYVert, oneOverdX);
    this->oneOverZYStep = this->CalcYStep(this->oneOverZ, minYVert, midYVert, maxYVert, oneOverdY);
    this->depthXStep = this->CalcXStep(this->depth, minYVert, midYVert, maxYVert, oneOverdX);
    this->depthYStep = this->CalcYStep(this->depth, minYVert, midYVert, maxYVert, oneOverdY);
    this->lightAmtXStep = this->CalcXStep(this->lightAmt, minYVert, midYVert, maxYVert, oneOverdX);
    this->lightAmtYStep = this->CalcYStep(this->lightAmt, minYVert, midYVert, maxYVert, oneOverdY);
    return NULL;
}

__ss_float Gradients::CalcXStep(list<__ss_float> *values, Vertex *minYVert, Vertex *midYVert, Vertex *maxYVert, __ss_float oneOverdX) {
    return ((((values->__getfast__(__ss_int(1))-values->__getfast__(__ss_int(2)))*((minYVert->pos)->y-(maxYVert->pos)->y))-((values->__getfast__(__ss_int(0))-values->__getfast__(__ss_int(2)))*((midYVert->pos)->y-(maxYVert->pos)->y)))*oneOverdX);
}

__ss_float Gradients::CalcYStep(list<__ss_float> *values, Vertex *minYVert, Vertex *midYVert, Vertex *maxYVert, __ss_float oneOverdY) {
    return ((((values->__getfast__(__ss_int(1))-values->__getfast__(__ss_int(2)))*((minYVert->pos)->x-(maxYVert->pos)->x))-((values->__getfast__(__ss_int(0))-values->__getfast__(__ss_int(2)))*((midYVert->pos)->x-(maxYVert->pos)->x)))*oneOverdY);
}

/**
class Edge
*/

class_ *cl_Edge;

void *Edge::__init__(Gradients *gradients, Vertex *minYVert, Vertex *maxYVert, __ss_int minYVertIndex) {
    __ss_float xDist, xPrestep, yDist, yPrestep;

    this->yStart = __math__::ceil((minYVert->pos)->y);
    this->yEnd = __math__::ceil((maxYVert->pos)->y);
    yDist = ((maxYVert->pos)->y-(minYVert->pos)->y);
    xDist = ((maxYVert->pos)->x-(minYVert->pos)->x);
    if ((yDist==((__ss_float)(__ss_int(0))))) {
        this->xStep = ((__ss_float)(__ss_int(0)));
    }
    else {
        this->xStep = (xDist/yDist);
    }
    yPrestep = (this->yStart-(minYVert->pos)->y);
    this->x = ((minYVert->pos)->x+(yPrestep*this->xStep));
    xPrestep = (this->x-(minYVert->pos)->x);
    this->texCoordX = (((gradients->texCoordX)->__getfast__(minYVertIndex)+(gradients->texCoordXXStep*xPrestep))+(gradients->texCoordXYStep*yPrestep));
    this->texCoordXStep = (gradients->texCoordXYStep+(gradients->texCoordXXStep*this->xStep));
    this->texCoordY = (((gradients->texCoordY)->__getfast__(minYVertIndex)+(gradients->texCoordYXStep*xPrestep))+(gradients->texCoordYYStep*yPrestep));
    this->texCoordYStep = (gradients->texCoordYYStep+(gradients->texCoordYXStep*this->xStep));
    this->oneOverZ = (((gradients->oneOverZ)->__getfast__(minYVertIndex)+(gradients->oneOverZXStep*xPrestep))+(gradients->oneOverZYStep*yPrestep));
    this->oneOverZStep = (gradients->oneOverZYStep+(gradients->oneOverZXStep*this->xStep));
    this->depth = (((gradients->depth)->__getfast__(minYVertIndex)+(gradients->depthXStep*xPrestep))+(gradients->depthYStep*yPrestep));
    this->depthStep = (gradients->depthYStep+(gradients->depthXStep*this->xStep));
    this->lightAmt = (((gradients->lightAmt)->__getfast__(minYVertIndex)+(gradients->lightAmtXStep*xPrestep))+(gradients->lightAmtYStep*yPrestep));
    this->lightAmtStep = (gradients->lightAmtYStep+(gradients->lightAmtXStep*this->xStep));
    return NULL;
}

void *Edge::step() {
    this->x = (this->x+this->xStep);
    this->texCoordX = (this->texCoordX+this->texCoordXStep);
    this->texCoordY = (this->texCoordY+this->texCoordYStep);
    this->oneOverZ = (this->oneOverZ+this->oneOverZStep);
    this->depth = (this->depth+this->depthStep);
    this->lightAmt = (this->lightAmt+this->lightAmtStep);
    return NULL;
}

/**
class RenderContext
*/

class_ *cl_RenderContext;

void *RenderContext::__init__(__ss_int width, __ss_int height) {
    __ss_int __149, __150;

    this->bitmap = (new Bitmap(width, height, NULL));
    __149 = width;
    __150 = height;
    this->width = __149;
    this->height = __150;
    this->zbuffer = (((new list<__ss_float>(1,__ss_float(0.0))))->__mul__(width))->__mul__(height);
    this->zbuffer_reset = (((new list<__ss_float>(1,__float(const_5))))->__mul__(width))->__mul__(height);
    this->screenSpaceTransform = ((new Matrix4(1)))->init_screenspace_transform(__divs(this->width, __ss_int(2)), __divs(this->height, __ss_int(2)));
    return NULL;
}

void *RenderContext::clear() {
    (this->bitmap)->clear();
    return NULL;
}

void *RenderContext::clear_zbuffer() {
    (this->zbuffer)->__setslice__(__ss_int(0),__ss_int(0),__ss_int(0),__ss_int(0),this->zbuffer_reset);
    return NULL;
}

void *RenderContext::draw_triangle(Vertex *v1, Vertex *v2, Vertex *v3, Bitmap *texture, Vector4 *lightDir) {
    list<Vertex *> *auxillaryList, *vertices;
    Vertex *initialVertex;
    __ss_int __157, __158, i;
    __ss_bool __151, __152, __153, __154, __155, __156;

    if ((v1->inside_view_frustum() and v2->inside_view_frustum() and v3->inside_view_frustum())) {
        this->fill_triangle(v1, v2, v3, texture, lightDir);
    }
    else {
        vertices = (new list<Vertex *>(3,v1,v2,v3));
        auxillaryList = (new list<Vertex *>());
        if ((this->ClipPolygonAxis(vertices, auxillaryList, __ss_int(0)) and this->ClipPolygonAxis(vertices, auxillaryList, __ss_int(1)) and this->ClipPolygonAxis(vertices, auxillaryList, __ss_int(2)))) {
            initialVertex = vertices->__getfast__(__ss_int(0));

            FAST_FOR(i,__ss_int(1),(len(vertices)-__ss_int(1)),1,157,158)
                this->fill_triangle(initialVertex, vertices->__getfast__(i), vertices->__getfast__((i+__ss_int(1))), texture, lightDir);
            END_FOR

        }
    }
    return NULL;
}

__ss_bool RenderContext::ClipPolygonAxis(list<Vertex *> *vertices, list<Vertex *> *auxillaryList, __ss_int componentIndex) {
    this->ClipPolygonComponent(vertices, componentIndex, __ss_float(1.0), auxillaryList);
    (vertices)->__setslice__(__ss_int(0),__ss_int(0),__ss_int(0),__ss_int(0),(new list<Vertex *>()));
    if (__NOT(___bool(auxillaryList))) {
        return False;
    }
    this->ClipPolygonComponent(auxillaryList, componentIndex, (-__ss_float(1.0)), vertices);
    (auxillaryList)->__setslice__(__ss_int(0),__ss_int(0),__ss_int(0),__ss_int(0),(new list<Vertex *>()));
    return ___bool(vertices);
}

void *RenderContext::ClipPolygonComponent(list<Vertex *> *vertices, __ss_int componentIndex, __ss_float componentFactor, list<Vertex *> *result) {
    Vertex *currentVertex, *previousVertex;
    __ss_float currentComponent, lerpAmt, previousComponent;
    __ss_bool currentInside, previousInside;
    list<Vertex *> *__159;
    __iter<Vertex *> *__160;
    __ss_int __161;
    list<Vertex *>::for_in_loop __162;

    previousVertex = vertices->__getfast__((len(vertices)-__ss_int(1)));
    previousComponent = (previousVertex->get(componentIndex)*componentFactor);
    previousInside = ___bool((previousComponent<=(previousVertex->pos)->w));

    FOR_IN(currentVertex,vertices,159,161,162)
        currentComponent = (currentVertex->get(componentIndex)*componentFactor);
        currentInside = ___bool((currentComponent<=(currentVertex->pos)->w));
        if (((currentInside)^(previousInside))) {
            lerpAmt = (((previousVertex->pos)->w-previousComponent)/(((previousVertex->pos)->w-previousComponent)-((currentVertex->pos)->w-currentComponent)));
            result->append(previousVertex->lerp(currentVertex, lerpAmt));
        }
        if (currentInside) {
            result->append(currentVertex);
        }
        previousVertex = currentVertex;
        previousComponent = currentComponent;
        previousInside = currentInside;
    END_FOR

    return NULL;
}

void *RenderContext::fill_triangle(Vertex *v1, Vertex *v2, Vertex *v3, Bitmap *texture, Vector4 *lightDir) {
    Vertex *__163, *__164, *__165, *__166, *__167, *__168, *maxYVert, *midYVert, *minYVert;

    minYVert = (v1->transform(this->screenSpaceTransform, NULL))->perspective_divide();
    midYVert = (v2->transform(this->screenSpaceTransform, NULL))->perspective_divide();
    maxYVert = (v3->transform(this->screenSpaceTransform, NULL))->perspective_divide();
    if ((minYVert->triangle_area_times_two(maxYVert, midYVert)<((__ss_float)(__ss_int(0))))) {
        if (((maxYVert->pos)->y<(midYVert->pos)->y)) {
            __163 = midYVert;
            __164 = maxYVert;
            maxYVert = __163;
            midYVert = __164;
        }
        if (((midYVert->pos)->y<(minYVert->pos)->y)) {
            __165 = minYVert;
            __166 = midYVert;
            midYVert = __165;
            minYVert = __166;
        }
        if (((maxYVert->pos)->y<(midYVert->pos)->y)) {
            __167 = midYVert;
            __168 = maxYVert;
            maxYVert = __167;
            midYVert = __168;
        }
        this->scan_triangle(minYVert, midYVert, maxYVert, ___bool((minYVert->triangle_area_times_two(maxYVert, midYVert)>=((__ss_float)(__ss_int(0))))), texture, lightDir);
    }
    return NULL;
}

void *RenderContext::scan_triangle(Vertex *minYVert, Vertex *midYVert, Vertex *maxYVert, __ss_bool handedness, Bitmap *texture, Vector4 *lightDir) {
    Gradients *gradients;
    Edge *middleToBottom, *topToBottom, *topToMiddle;

    gradients = (new Gradients(minYVert, midYVert, maxYVert, lightDir));
    topToBottom = (new Edge(gradients, minYVert, maxYVert, __ss_int(0)));
    topToMiddle = (new Edge(gradients, minYVert, midYVert, __ss_int(0)));
    middleToBottom = (new Edge(gradients, midYVert, maxYVert, __ss_int(1)));
    this->scan_edges(gradients, topToBottom, topToMiddle, handedness, texture);
    this->scan_edges(gradients, topToBottom, middleToBottom, handedness, texture);
    return NULL;
}

void *RenderContext::scan_edges(Gradients *gradients, Edge *a, Edge *b, __ss_bool handedness, Bitmap *texture) {
    Edge *__169, *__170, *__171, *__172, *left, *right;
    __ss_int __173, __174, j;

    __169 = a;
    __170 = b;
    left = __169;
    right = __170;
    if (handedness) {
        __171 = right;
        __172 = left;
        left = __171;
        right = __172;
    }

    FAST_FOR(j,b->yStart,b->yEnd,1,173,174)
        this->draw_scanline(gradients, left, right, j, texture);
        left->step();
        right->step();
    END_FOR

    return NULL;
}

void *RenderContext::draw_scanline(Gradients *gradients, Edge *left, Edge *right, __ss_int j, Bitmap *texture) {
    __ss_int __175, __176, i, index, srcX, srcY, xMax, xMin;
    __ss_float depth, depthXStep, lightAmt, lightAmtXStep, oneOverZ, oneOverZXStep, texCoordX, texCoordXXStep, texCoordY, texCoordYXStep, xPrestep, z;
    list<__ss_float> *__177;

    xMin = __math__::ceil(left->x);
    xMax = __math__::ceil(right->x);
    xPrestep = (xMin-left->x);
    texCoordXXStep = gradients->texCoordXXStep;
    texCoordYXStep = gradients->texCoordYXStep;
    oneOverZXStep = gradients->oneOverZXStep;
    depthXStep = gradients->depthXStep;
    lightAmtXStep = gradients->lightAmtXStep;
    texCoordX = (left->texCoordX+(texCoordXXStep*xPrestep));
    texCoordY = (left->texCoordY+(texCoordYXStep*xPrestep));
    oneOverZ = (left->oneOverZ+(oneOverZXStep*xPrestep));
    depth = (left->depth+(depthXStep*xPrestep));
    lightAmt = (left->lightAmt+(lightAmtXStep*xPrestep));

    FAST_FOR(i,xMin,xMax,1,175,176)
        index = (i+(j*this->width));
        if ((depth<(this->zbuffer)->__getfast__(index))) {
            this->zbuffer->__setitem__(index, depth);
            z = (__ss_float(1.0)/oneOverZ);
            srcX = __ss_int(0);
            srcY = __ss_int(0);
            if (___bool(texture)) {
                srcX = __int((((texCoordX*z)*(texture->width-__ss_int(1)))+__ss_float(0.5)));
                srcY = __int((((texCoordY*z)*(texture->width-__ss_int(1)))+__ss_float(0.5)));
            }
            this->copy_pixel(i, j, srcX, srcY, texture, lightAmt);
        }
        oneOverZ = (oneOverZ+oneOverZXStep);
        texCoordX = (texCoordX+texCoordXXStep);
        texCoordY = (texCoordY+texCoordYXStep);
        depth = (depth+depthXStep);
        lightAmt = (lightAmt+lightAmtXStep);
    END_FOR

    return NULL;
}

void *RenderContext::copy_pixel(__ss_int destX, __ss_int destY, __ss_int srcX, __ss_int srcY, Bitmap *src, __ss_float lightAmt) {
    __ss_int destIndex, srcIndex;
    bytes *components;

    destIndex = ((destX+(destY*this->width))*__ss_int(4));
    components = (this->bitmap)->components;
    if ((src!=NULL)) {
        srcIndex = ((srcX+(srcY*src->width))*__ss_int(4));
        components->__setitem__(destIndex, __int(((src->components)->__getitem__(srcIndex)*lightAmt)));
        components->__setitem__((destIndex+__ss_int(1)), __int(((src->components)->__getitem__((srcIndex+__ss_int(1)))*lightAmt)));
        components->__setitem__((destIndex+__ss_int(2)), __int(((src->components)->__getitem__((srcIndex+__ss_int(2)))*lightAmt)));
        components->__setitem__((destIndex+__ss_int(3)), __int(((src->components)->__getitem__((srcIndex+__ss_int(3)))*lightAmt)));
    }
    else {
        components->__setitem__(destIndex, __int((lightAmt*__ss_int(255))));
        components->__setitem__((destIndex+__ss_int(1)), __int((lightAmt*__ss_int(255))));
        components->__setitem__((destIndex+__ss_int(2)), __int((lightAmt*__ss_int(255))));
        components->__setitem__((destIndex+__ss_int(3)), __int((lightAmt*__ss_int(255))));
    }
    return NULL;
}

void __init() {
    const_0 = new str("v ");
    const_1 = new str("vt ");
    const_2 = new str("vn ");
    const_3 = new str("f ");
    const_4 = __char_cache[47];
    const_5 = new str("inf");
    const_6 = new str("__main__");
    const_7 = new str("buddha2.obj");
    const_8 = new bytes("");

    __name__ = new str("render");

    default_0 = NULL;
    cl_Bitmap = new class_("render.Bitmap");
    cl_Vector4 = new class_("render.Vector4");
    cl_Matrix4 = new class_("render.Matrix4");
    cl_Quaternion = new class_("render.Quaternion");
    default_1 = NULL;
    cl_Vertex = new class_("render.Vertex");
    default_2 = NULL;
    default_3 = NULL;
    default_4 = NULL;
    cl_Transform = new class_("render.Transform");
    cl_Camera = new class_("render.Camera");
    cl_Mesh = new class_("render.Mesh");
    cl_Gradients = new class_("render.Gradients");
    cl_Edge = new class_("render.Edge");
    cl_RenderContext = new class_("render.RenderContext");
    if (__eq(__render__::__name__, const_6)) {
        mesh = (new Mesh(const_7, __ss_int(1)));
        texture = (new Bitmap(__ss_int(1), __ss_int(1), const_8));
        v = (new Vector4(__ss_float(0.0), __ss_float(0.0), __ss_float(0.0), __ss_float(1.0)));
        transform = ((new Transform(__render__::v, NULL, NULL)))->rotate(quaternion_from_axis_angle(__render__::v, __ss_float(80.0)));
        target = (new RenderContext(__ss_int(0), __ss_int(0)));
        __render__::target->clear();
        __render__::target->clear_zbuffer();
        camera = (new Camera(((new Matrix4(1)))->init_perspective(__ss_float(1.0), __ss_float(1.0), __ss_float(0.1), __ss_float(1000.0))));
        __render__::mesh->draw(__render__::target, __render__::camera->get_view_projection(), __render__::transform->get_transformation(), __render__::texture, __render__::v);
    }
}

} // module namespace

/* extension module glue */

extern "C" {
#include <Python.h>
#include "math.hpp"
#include "render.hpp"
#include <structmember.h>
#include "math.hpp"
#include "render.hpp"

PyObject *__ss_mod_render;

namespace __render__ { /* XXX */

/* class Bitmap */

typedef struct {
    PyObject_HEAD
    __render__::Bitmap *__ss_object;
} __ss_render_BitmapObject;

static PyMemberDef __ss_render_BitmapMembers[] = {
    {NULL}
};

PyObject *__ss_render_Bitmap___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_int arg_0 = __ss_arg<__ss_int >("width", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("height", 1, 0, 0, args, kwargs);
        bytes *arg_2 = __ss_arg<bytes *>("components", 2, 1, 0, args, kwargs);

        return __to_py(((__ss_render_BitmapObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Bitmap_clear(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_BitmapObject *)self)->__ss_object->clear());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_render_Bitmap_as_number = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

PyObject *__ss_render_Bitmap__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_render_Bitmap__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_render_BitmapMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_render_Bitmap__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_render_Bitmap__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_render_Bitmap___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"clear", (PyCFunction)__ss_render_Bitmap_clear, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_render_Bitmap___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_render_Bitmap___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_render_BitmapNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_render_BitmapObject *self = (__ss_render_BitmapObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __render__::Bitmap();
    self->__ss_object->__class__ = __render__::cl_Bitmap;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_render_BitmapDealloc(__ss_render_BitmapObject *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
    __ss_proxy->__delitem__(self->__ss_object);
}

PyObject *__ss_get___ss_render_Bitmap_height(__ss_render_BitmapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->height);
}

int __ss_set___ss_render_Bitmap_height(__ss_render_BitmapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->height = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Bitmap_width(__ss_render_BitmapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->width);
}

int __ss_set___ss_render_Bitmap_width(__ss_render_BitmapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->width = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Bitmap_components(__ss_render_BitmapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->components);
}

int __ss_set___ss_render_Bitmap_components(__ss_render_BitmapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->components = __to_ss<bytes *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Bitmap_reset(__ss_render_BitmapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->reset);
}

int __ss_set___ss_render_Bitmap_reset(__ss_render_BitmapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->reset = __to_ss<bytes *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_render_BitmapGetSet[] = {
    {(char *)"height", (getter)__ss_get___ss_render_Bitmap_height, (setter)__ss_set___ss_render_Bitmap_height, (char *)"", NULL},
    {(char *)"width", (getter)__ss_get___ss_render_Bitmap_width, (setter)__ss_set___ss_render_Bitmap_width, (char *)"", NULL},
    {(char *)"components", (getter)__ss_get___ss_render_Bitmap_components, (setter)__ss_set___ss_render_Bitmap_components, (char *)"", NULL},
    {(char *)"reset", (getter)__ss_get___ss_render_Bitmap_reset, (setter)__ss_set___ss_render_Bitmap_reset, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_render_BitmapObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "render.Bitmap",
    sizeof( __ss_render_BitmapObject),
    0,
    (destructor) __ss_render_BitmapDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_render_Bitmap_as_number,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT,
    PyDoc_STR("Custom objects"),
    0,
    0,
    0,
    0,
    0,
    0,
    __ss_render_BitmapMethods,
    __ss_render_BitmapMembers,
    __ss_render_BitmapGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_render_Bitmap___tpinit__,
    0,
    __ss_render_BitmapNew,
};

PyObject *__ss_render_Bitmap__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_render, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_render_BitmapObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_render_BitmapObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyTuple_New(4);
    PyTuple_SetItem(b, 0, __to_py(((__ss_render_BitmapObject *)self)->__ss_object->height));
    PyTuple_SetItem(b, 1, __to_py(((__ss_render_BitmapObject *)self)->__ss_object->width));
    PyTuple_SetItem(b, 2, __to_py(((__ss_render_BitmapObject *)self)->__ss_object->components));
    PyTuple_SetItem(b, 3, __to_py(((__ss_render_BitmapObject *)self)->__ss_object->reset));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_render_Bitmap__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    ((__ss_render_BitmapObject *)self)->__ss_object->height = __to_ss<__ss_int >(PyTuple_GetItem(state, 0));
    ((__ss_render_BitmapObject *)self)->__ss_object->width = __to_ss<__ss_int >(PyTuple_GetItem(state, 1));
    ((__ss_render_BitmapObject *)self)->__ss_object->components = __to_ss<bytes *>(PyTuple_GetItem(state, 2));
    ((__ss_render_BitmapObject *)self)->__ss_object->reset = __to_ss<bytes *>(PyTuple_GetItem(state, 3));
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __render__

namespace __render__ { /* XXX */

/* class Vector4 */

typedef struct {
    PyObject_HEAD
    __render__::Vector4 *__ss_object;
} __ss_render_Vector4Object;

static PyMemberDef __ss_render_Vector4Members[] = {
    {NULL}
};

PyObject *__ss_render_Vector4___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_float arg_0 = __ss_arg<__ss_float >("x", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("y", 1, 0, 0, args, kwargs);
        __ss_float arg_2 = __ss_arg<__ss_float >("z", 2, 0, 0, args, kwargs);
        __ss_float arg_3 = __ss_arg<__ss_float >("w", 3, 1, __ss_float(1.0), args, kwargs);

        return __to_py(((__ss_render_Vector4Object *)self)->__ss_object->__init__(arg_0, arg_1, arg_2, arg_3));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vector4_length(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_Vector4Object *)self)->__ss_object->length());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vector4_normalized(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_Vector4Object *)self)->__ss_object->normalized());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vector4_mul(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_float arg_0 = __ss_arg<__ss_float >("r", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Vector4Object *)self)->__ss_object->mul(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vector4_sub(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vector4 *arg_0 = __ss_arg<Vector4 *>("r", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Vector4Object *)self)->__ss_object->sub(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vector4_add(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vector4 *arg_0 = __ss_arg<Vector4 *>("r", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Vector4Object *)self)->__ss_object->add(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vector4_dot(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vector4 *arg_0 = __ss_arg<Vector4 *>("r", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Vector4Object *)self)->__ss_object->dot(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vector4_cross(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vector4 *arg_0 = __ss_arg<Vector4 *>("r", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Vector4Object *)self)->__ss_object->cross(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vector4_lerp(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vector4 *arg_0 = __ss_arg<Vector4 *>("dest", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("lerpFactor", 1, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Vector4Object *)self)->__ss_object->lerp(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_render_Vector4_as_number = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

PyObject *__ss_render_Vector4__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_render_Vector4__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_render_Vector4Methods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_render_Vector4__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_render_Vector4__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_render_Vector4___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"length", (PyCFunction)__ss_render_Vector4_length, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"normalized", (PyCFunction)__ss_render_Vector4_normalized, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"mul", (PyCFunction)__ss_render_Vector4_mul, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"sub", (PyCFunction)__ss_render_Vector4_sub, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"add", (PyCFunction)__ss_render_Vector4_add, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"dot", (PyCFunction)__ss_render_Vector4_dot, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"cross", (PyCFunction)__ss_render_Vector4_cross, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"lerp", (PyCFunction)__ss_render_Vector4_lerp, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_render_Vector4___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_render_Vector4___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_render_Vector4New(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_render_Vector4Object *self = (__ss_render_Vector4Object *)type->tp_alloc(type, 0);
    self->__ss_object = new __render__::Vector4();
    self->__ss_object->__class__ = __render__::cl_Vector4;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_render_Vector4Dealloc(__ss_render_Vector4Object *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
    __ss_proxy->__delitem__(self->__ss_object);
}

PyObject *__ss_get___ss_render_Vector4_z(__ss_render_Vector4Object *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->z);
}

int __ss_set___ss_render_Vector4_z(__ss_render_Vector4Object *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->z = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Vector4_x(__ss_render_Vector4Object *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->x);
}

int __ss_set___ss_render_Vector4_x(__ss_render_Vector4Object *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->x = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Vector4_w(__ss_render_Vector4Object *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->w);
}

int __ss_set___ss_render_Vector4_w(__ss_render_Vector4Object *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->w = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Vector4_y(__ss_render_Vector4Object *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->y);
}

int __ss_set___ss_render_Vector4_y(__ss_render_Vector4Object *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->y = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_render_Vector4GetSet[] = {
    {(char *)"z", (getter)__ss_get___ss_render_Vector4_z, (setter)__ss_set___ss_render_Vector4_z, (char *)"", NULL},
    {(char *)"x", (getter)__ss_get___ss_render_Vector4_x, (setter)__ss_set___ss_render_Vector4_x, (char *)"", NULL},
    {(char *)"w", (getter)__ss_get___ss_render_Vector4_w, (setter)__ss_set___ss_render_Vector4_w, (char *)"", NULL},
    {(char *)"y", (getter)__ss_get___ss_render_Vector4_y, (setter)__ss_set___ss_render_Vector4_y, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_render_Vector4ObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "render.Vector4",
    sizeof( __ss_render_Vector4Object),
    0,
    (destructor) __ss_render_Vector4Dealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_render_Vector4_as_number,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT,
    PyDoc_STR("Custom objects"),
    0,
    0,
    0,
    0,
    0,
    0,
    __ss_render_Vector4Methods,
    __ss_render_Vector4Members,
    __ss_render_Vector4GetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_render_Vector4___tpinit__,
    0,
    __ss_render_Vector4New,
};

PyObject *__ss_render_Vector4__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_render, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_render_Vector4ObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_render_Vector4ObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyTuple_New(4);
    PyTuple_SetItem(b, 0, __to_py(((__ss_render_Vector4Object *)self)->__ss_object->z));
    PyTuple_SetItem(b, 1, __to_py(((__ss_render_Vector4Object *)self)->__ss_object->x));
    PyTuple_SetItem(b, 2, __to_py(((__ss_render_Vector4Object *)self)->__ss_object->w));
    PyTuple_SetItem(b, 3, __to_py(((__ss_render_Vector4Object *)self)->__ss_object->y));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_render_Vector4__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    ((__ss_render_Vector4Object *)self)->__ss_object->z = __to_ss<__ss_float >(PyTuple_GetItem(state, 0));
    ((__ss_render_Vector4Object *)self)->__ss_object->x = __to_ss<__ss_float >(PyTuple_GetItem(state, 1));
    ((__ss_render_Vector4Object *)self)->__ss_object->w = __to_ss<__ss_float >(PyTuple_GetItem(state, 2));
    ((__ss_render_Vector4Object *)self)->__ss_object->y = __to_ss<__ss_float >(PyTuple_GetItem(state, 3));
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __render__

namespace __render__ { /* XXX */

/* class Matrix4 */

typedef struct {
    PyObject_HEAD
    __render__::Matrix4 *__ss_object;
} __ss_render_Matrix4Object;

static PyMemberDef __ss_render_Matrix4Members[] = {
    {NULL}
};

PyObject *__ss_render_Matrix4___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_Matrix4Object *)self)->__ss_object->__init__());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Matrix4_init_scale(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_float arg_0 = __ss_arg<__ss_float >("x", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("y", 1, 0, 0, args, kwargs);
        __ss_float arg_2 = __ss_arg<__ss_float >("z", 2, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Matrix4Object *)self)->__ss_object->init_scale(arg_0, arg_1, arg_2));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Matrix4_init_translation(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_float arg_0 = __ss_arg<__ss_float >("x", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("y", 1, 0, 0, args, kwargs);
        __ss_float arg_2 = __ss_arg<__ss_float >("z", 2, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Matrix4Object *)self)->__ss_object->init_translation(arg_0, arg_1, arg_2));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Matrix4_init_rotation(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vector4 *arg_0 = __ss_arg<Vector4 *>("f", 0, 0, 0, args, kwargs);
        Vector4 *arg_1 = __ss_arg<Vector4 *>("u", 1, 0, 0, args, kwargs);
        Vector4 *arg_2 = __ss_arg<Vector4 *>("r", 2, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Matrix4Object *)self)->__ss_object->init_rotation(arg_0, arg_1, arg_2));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Matrix4_init_screenspace_transform(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_float arg_0 = __ss_arg<__ss_float >("halfWidth", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("halfHeight", 1, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Matrix4Object *)self)->__ss_object->init_screenspace_transform(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Matrix4_init_perspective(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_float arg_0 = __ss_arg<__ss_float >("fov", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("aspectRatio", 1, 0, 0, args, kwargs);
        __ss_float arg_2 = __ss_arg<__ss_float >("zNear", 2, 0, 0, args, kwargs);
        __ss_float arg_3 = __ss_arg<__ss_float >("zFar", 3, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Matrix4Object *)self)->__ss_object->init_perspective(arg_0, arg_1, arg_2, arg_3));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Matrix4_transform(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vector4 *arg_0 = __ss_arg<Vector4 *>("r", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Matrix4Object *)self)->__ss_object->transform(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Matrix4_mul(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Matrix4 *arg_0 = __ss_arg<Matrix4 *>("other", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_render_Matrix4Object *)self)->__ss_object->mul(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_render_Matrix4_as_number = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

PyObject *__ss_render_Matrix4__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_render_Matrix4__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_render_Matrix4Methods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_render_Matrix4__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_render_Matrix4__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_render_Matrix4___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"init_scale", (PyCFunction)__ss_render_Matrix4_init_scale, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"init_translation", (PyCFunction)__ss_render_Matrix4_init_translation, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"init_rotation", (PyCFunction)__ss_render_Matrix4_init_rotation, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"init_screenspace_transform", (PyCFunction)__ss_render_Matrix4_init_screenspace_transform, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"init_perspective", (PyCFunction)__ss_render_Matrix4_init_perspective, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"transform", (PyCFunction)__ss_render_Matrix4_transform, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"mul", (PyCFunction)__ss_render_Matrix4_mul, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_render_Matrix4___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_render_Matrix4___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_render_Matrix4New(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_render_Matrix4Object *self = (__ss_render_Matrix4Object *)type->tp_alloc(type, 0);
    self->__ss_object = new __render__::Matrix4();
    self->__ss_object->__class__ = __render__::cl_Matrix4;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_render_Matrix4Dealloc(__ss_render_Matrix4Object *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
    __ss_proxy->__delitem__(self->__ss_object);
}

PyObject *__ss_get___ss_render_Matrix4_m(__ss_render_Matrix4Object *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->m);
}

int __ss_set___ss_render_Matrix4_m(__ss_render_Matrix4Object *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->m = __to_ss<list<list<__ss_float> *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_render_Matrix4GetSet[] = {
    {(char *)"m", (getter)__ss_get___ss_render_Matrix4_m, (setter)__ss_set___ss_render_Matrix4_m, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_render_Matrix4ObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "render.Matrix4",
    sizeof( __ss_render_Matrix4Object),
    0,
    (destructor) __ss_render_Matrix4Dealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_render_Matrix4_as_number,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT,
    PyDoc_STR("Custom objects"),
    0,
    0,
    0,
    0,
    0,
    0,
    __ss_render_Matrix4Methods,
    __ss_render_Matrix4Members,
    __ss_render_Matrix4GetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_render_Matrix4___tpinit__,
    0,
    __ss_render_Matrix4New,
};

PyObject *__ss_render_Matrix4__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_render, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_render_Matrix4ObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_render_Matrix4ObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyTuple_New(1);
    PyTuple_SetItem(b, 0, __to_py(((__ss_render_Matrix4Object *)self)->__ss_object->m));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_render_Matrix4__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    ((__ss_render_Matrix4Object *)self)->__ss_object->m = __to_ss<list<list<__ss_float> *> *>(PyTuple_GetItem(state, 0));
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __render__

namespace __render__ { /* XXX */

/* class Quaternion */

typedef struct {
    PyObject_HEAD
    __render__::Quaternion *__ss_object;
} __ss_render_QuaternionObject;

static PyMemberDef __ss_render_QuaternionMembers[] = {
    {NULL}
};

PyObject *__ss_render_Quaternion___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_float arg_0 = __ss_arg<__ss_float >("x", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("y", 1, 0, 0, args, kwargs);
        __ss_float arg_2 = __ss_arg<__ss_float >("z", 2, 0, 0, args, kwargs);
        __ss_float arg_3 = __ss_arg<__ss_float >("w", 3, 0, 0, args, kwargs);

        return __to_py(((__ss_render_QuaternionObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2, arg_3));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Quaternion_length(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_QuaternionObject *)self)->__ss_object->length());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Quaternion_normalized(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_QuaternionObject *)self)->__ss_object->normalized());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Quaternion_conjugate(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_QuaternionObject *)self)->__ss_object->conjugate());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Quaternion_mul(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Quaternion *arg_0 = __ss_arg<Quaternion *>("r", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_render_QuaternionObject *)self)->__ss_object->mul(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Quaternion_to_rotation_matrix(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_QuaternionObject *)self)->__ss_object->to_rotation_matrix());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_render_Quaternion_as_number = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

PyObject *__ss_render_Quaternion__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_render_Quaternion__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_render_QuaternionMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_render_Quaternion__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_render_Quaternion__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_render_Quaternion___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"length", (PyCFunction)__ss_render_Quaternion_length, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"normalized", (PyCFunction)__ss_render_Quaternion_normalized, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"conjugate", (PyCFunction)__ss_render_Quaternion_conjugate, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"mul", (PyCFunction)__ss_render_Quaternion_mul, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"to_rotation_matrix", (PyCFunction)__ss_render_Quaternion_to_rotation_matrix, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_render_Quaternion___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_render_Quaternion___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_render_QuaternionNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_render_QuaternionObject *self = (__ss_render_QuaternionObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __render__::Quaternion();
    self->__ss_object->__class__ = __render__::cl_Quaternion;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_render_QuaternionDealloc(__ss_render_QuaternionObject *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
    __ss_proxy->__delitem__(self->__ss_object);
}

PyObject *__ss_get___ss_render_Quaternion_y(__ss_render_QuaternionObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->y);
}

int __ss_set___ss_render_Quaternion_y(__ss_render_QuaternionObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->y = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Quaternion_x(__ss_render_QuaternionObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->x);
}

int __ss_set___ss_render_Quaternion_x(__ss_render_QuaternionObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->x = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Quaternion_w(__ss_render_QuaternionObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->w);
}

int __ss_set___ss_render_Quaternion_w(__ss_render_QuaternionObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->w = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Quaternion_z(__ss_render_QuaternionObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->z);
}

int __ss_set___ss_render_Quaternion_z(__ss_render_QuaternionObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->z = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_render_QuaternionGetSet[] = {
    {(char *)"y", (getter)__ss_get___ss_render_Quaternion_y, (setter)__ss_set___ss_render_Quaternion_y, (char *)"", NULL},
    {(char *)"x", (getter)__ss_get___ss_render_Quaternion_x, (setter)__ss_set___ss_render_Quaternion_x, (char *)"", NULL},
    {(char *)"w", (getter)__ss_get___ss_render_Quaternion_w, (setter)__ss_set___ss_render_Quaternion_w, (char *)"", NULL},
    {(char *)"z", (getter)__ss_get___ss_render_Quaternion_z, (setter)__ss_set___ss_render_Quaternion_z, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_render_QuaternionObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "render.Quaternion",
    sizeof( __ss_render_QuaternionObject),
    0,
    (destructor) __ss_render_QuaternionDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_render_Quaternion_as_number,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT,
    PyDoc_STR("Custom objects"),
    0,
    0,
    0,
    0,
    0,
    0,
    __ss_render_QuaternionMethods,
    __ss_render_QuaternionMembers,
    __ss_render_QuaternionGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_render_Quaternion___tpinit__,
    0,
    __ss_render_QuaternionNew,
};

PyObject *__ss_render_Quaternion__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_render, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_render_QuaternionObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_render_QuaternionObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyTuple_New(4);
    PyTuple_SetItem(b, 0, __to_py(((__ss_render_QuaternionObject *)self)->__ss_object->y));
    PyTuple_SetItem(b, 1, __to_py(((__ss_render_QuaternionObject *)self)->__ss_object->x));
    PyTuple_SetItem(b, 2, __to_py(((__ss_render_QuaternionObject *)self)->__ss_object->w));
    PyTuple_SetItem(b, 3, __to_py(((__ss_render_QuaternionObject *)self)->__ss_object->z));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_render_Quaternion__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    ((__ss_render_QuaternionObject *)self)->__ss_object->y = __to_ss<__ss_float >(PyTuple_GetItem(state, 0));
    ((__ss_render_QuaternionObject *)self)->__ss_object->x = __to_ss<__ss_float >(PyTuple_GetItem(state, 1));
    ((__ss_render_QuaternionObject *)self)->__ss_object->w = __to_ss<__ss_float >(PyTuple_GetItem(state, 2));
    ((__ss_render_QuaternionObject *)self)->__ss_object->z = __to_ss<__ss_float >(PyTuple_GetItem(state, 3));
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __render__

namespace __render__ { /* XXX */

/* class Vertex */

typedef struct {
    PyObject_HEAD
    __render__::Vertex *__ss_object;
} __ss_render_VertexObject;

static PyMemberDef __ss_render_VertexMembers[] = {
    {NULL}
};

PyObject *__ss_render_Vertex___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vector4 *arg_0 = __ss_arg<Vector4 *>("pos", 0, 0, 0, args, kwargs);
        Vector4 *arg_1 = __ss_arg<Vector4 *>("texCoords", 1, 0, 0, args, kwargs);
        Vector4 *arg_2 = __ss_arg<Vector4 *>("normal", 2, 0, 0, args, kwargs);

        return __to_py(((__ss_render_VertexObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vertex_transform(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Matrix4 *arg_0 = __ss_arg<Matrix4 *>("transform", 0, 0, 0, args, kwargs);
        Matrix4 *arg_1 = __ss_arg<Matrix4 *>("normalTransform", 1, 1, 0, args, kwargs);

        return __to_py(((__ss_render_VertexObject *)self)->__ss_object->transform(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vertex_inside_view_frustum(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_VertexObject *)self)->__ss_object->inside_view_frustum());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vertex_perspective_divide(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_VertexObject *)self)->__ss_object->perspective_divide());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vertex_triangle_area_times_two(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vertex *arg_0 = __ss_arg<Vertex *>("b", 0, 0, 0, args, kwargs);
        Vertex *arg_1 = __ss_arg<Vertex *>("c", 1, 0, 0, args, kwargs);

        return __to_py(((__ss_render_VertexObject *)self)->__ss_object->triangle_area_times_two(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vertex_get(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_int arg_0 = __ss_arg<__ss_int >("index", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_render_VertexObject *)self)->__ss_object->get(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Vertex_lerp(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vertex *arg_0 = __ss_arg<Vertex *>("other", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("lerpAmt", 1, 0, 0, args, kwargs);

        return __to_py(((__ss_render_VertexObject *)self)->__ss_object->lerp(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_render_Vertex_as_number = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

PyObject *__ss_render_Vertex__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_render_Vertex__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_render_VertexMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_render_Vertex__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_render_Vertex__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_render_Vertex___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"transform", (PyCFunction)__ss_render_Vertex_transform, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"inside_view_frustum", (PyCFunction)__ss_render_Vertex_inside_view_frustum, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"perspective_divide", (PyCFunction)__ss_render_Vertex_perspective_divide, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"triangle_area_times_two", (PyCFunction)__ss_render_Vertex_triangle_area_times_two, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"get", (PyCFunction)__ss_render_Vertex_get, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"lerp", (PyCFunction)__ss_render_Vertex_lerp, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_render_Vertex___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_render_Vertex___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_render_VertexNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_render_VertexObject *self = (__ss_render_VertexObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __render__::Vertex();
    self->__ss_object->__class__ = __render__::cl_Vertex;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_render_VertexDealloc(__ss_render_VertexObject *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
    __ss_proxy->__delitem__(self->__ss_object);
}

PyObject *__ss_get___ss_render_Vertex_pos(__ss_render_VertexObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->pos);
}

int __ss_set___ss_render_Vertex_pos(__ss_render_VertexObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->pos = __to_ss<Vector4 *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Vertex_normal(__ss_render_VertexObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->normal);
}

int __ss_set___ss_render_Vertex_normal(__ss_render_VertexObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->normal = __to_ss<Vector4 *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Vertex_texCoords(__ss_render_VertexObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->texCoords);
}

int __ss_set___ss_render_Vertex_texCoords(__ss_render_VertexObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->texCoords = __to_ss<Vector4 *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_render_VertexGetSet[] = {
    {(char *)"pos", (getter)__ss_get___ss_render_Vertex_pos, (setter)__ss_set___ss_render_Vertex_pos, (char *)"", NULL},
    {(char *)"normal", (getter)__ss_get___ss_render_Vertex_normal, (setter)__ss_set___ss_render_Vertex_normal, (char *)"", NULL},
    {(char *)"texCoords", (getter)__ss_get___ss_render_Vertex_texCoords, (setter)__ss_set___ss_render_Vertex_texCoords, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_render_VertexObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "render.Vertex",
    sizeof( __ss_render_VertexObject),
    0,
    (destructor) __ss_render_VertexDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_render_Vertex_as_number,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT,
    PyDoc_STR("Custom objects"),
    0,
    0,
    0,
    0,
    0,
    0,
    __ss_render_VertexMethods,
    __ss_render_VertexMembers,
    __ss_render_VertexGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_render_Vertex___tpinit__,
    0,
    __ss_render_VertexNew,
};

PyObject *__ss_render_Vertex__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_render, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_render_VertexObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_render_VertexObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyTuple_New(3);
    PyTuple_SetItem(b, 0, __to_py(((__ss_render_VertexObject *)self)->__ss_object->pos));
    PyTuple_SetItem(b, 1, __to_py(((__ss_render_VertexObject *)self)->__ss_object->normal));
    PyTuple_SetItem(b, 2, __to_py(((__ss_render_VertexObject *)self)->__ss_object->texCoords));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_render_Vertex__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    ((__ss_render_VertexObject *)self)->__ss_object->pos = __to_ss<Vector4 *>(PyTuple_GetItem(state, 0));
    ((__ss_render_VertexObject *)self)->__ss_object->normal = __to_ss<Vector4 *>(PyTuple_GetItem(state, 1));
    ((__ss_render_VertexObject *)self)->__ss_object->texCoords = __to_ss<Vector4 *>(PyTuple_GetItem(state, 2));
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __render__

namespace __render__ { /* XXX */

/* class Transform */

typedef struct {
    PyObject_HEAD
    __render__::Transform *__ss_object;
} __ss_render_TransformObject;

static PyMemberDef __ss_render_TransformMembers[] = {
    {NULL}
};

PyObject *__ss_render_Transform___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vector4 *arg_0 = __ss_arg<Vector4 *>("pos", 0, 1, 0, args, kwargs);
        Quaternion *arg_1 = __ss_arg<Quaternion *>("rot", 1, 1, 0, args, kwargs);
        Vector4 *arg_2 = __ss_arg<Vector4 *>("scale", 2, 1, 0, args, kwargs);

        return __to_py(((__ss_render_TransformObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Transform_rotate(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Quaternion *arg_0 = __ss_arg<Quaternion *>("rotation", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_render_TransformObject *)self)->__ss_object->rotate(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Transform_get_transformation(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_TransformObject *)self)->__ss_object->get_transformation());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_render_Transform_as_number = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

PyObject *__ss_render_Transform__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_render_Transform__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_render_TransformMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_render_Transform__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_render_Transform__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_render_Transform___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"rotate", (PyCFunction)__ss_render_Transform_rotate, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"get_transformation", (PyCFunction)__ss_render_Transform_get_transformation, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_render_Transform___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_render_Transform___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_render_TransformNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_render_TransformObject *self = (__ss_render_TransformObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __render__::Transform();
    self->__ss_object->__class__ = __render__::cl_Transform;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_render_TransformDealloc(__ss_render_TransformObject *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
    __ss_proxy->__delitem__(self->__ss_object);
}

PyObject *__ss_get___ss_render_Transform_scale(__ss_render_TransformObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->scale);
}

int __ss_set___ss_render_Transform_scale(__ss_render_TransformObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->scale = __to_ss<Vector4 *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Transform_rot(__ss_render_TransformObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->rot);
}

int __ss_set___ss_render_Transform_rot(__ss_render_TransformObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->rot = __to_ss<Quaternion *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Transform_pos(__ss_render_TransformObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->pos);
}

int __ss_set___ss_render_Transform_pos(__ss_render_TransformObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->pos = __to_ss<Vector4 *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_render_TransformGetSet[] = {
    {(char *)"scale", (getter)__ss_get___ss_render_Transform_scale, (setter)__ss_set___ss_render_Transform_scale, (char *)"", NULL},
    {(char *)"rot", (getter)__ss_get___ss_render_Transform_rot, (setter)__ss_set___ss_render_Transform_rot, (char *)"", NULL},
    {(char *)"pos", (getter)__ss_get___ss_render_Transform_pos, (setter)__ss_set___ss_render_Transform_pos, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_render_TransformObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "render.Transform",
    sizeof( __ss_render_TransformObject),
    0,
    (destructor) __ss_render_TransformDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_render_Transform_as_number,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT,
    PyDoc_STR("Custom objects"),
    0,
    0,
    0,
    0,
    0,
    0,
    __ss_render_TransformMethods,
    __ss_render_TransformMembers,
    __ss_render_TransformGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_render_Transform___tpinit__,
    0,
    __ss_render_TransformNew,
};

PyObject *__ss_render_Transform__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_render, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_render_TransformObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_render_TransformObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyTuple_New(3);
    PyTuple_SetItem(b, 0, __to_py(((__ss_render_TransformObject *)self)->__ss_object->scale));
    PyTuple_SetItem(b, 1, __to_py(((__ss_render_TransformObject *)self)->__ss_object->rot));
    PyTuple_SetItem(b, 2, __to_py(((__ss_render_TransformObject *)self)->__ss_object->pos));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_render_Transform__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    ((__ss_render_TransformObject *)self)->__ss_object->scale = __to_ss<Vector4 *>(PyTuple_GetItem(state, 0));
    ((__ss_render_TransformObject *)self)->__ss_object->rot = __to_ss<Quaternion *>(PyTuple_GetItem(state, 1));
    ((__ss_render_TransformObject *)self)->__ss_object->pos = __to_ss<Vector4 *>(PyTuple_GetItem(state, 2));
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __render__

namespace __render__ { /* XXX */

/* class Camera */

typedef struct {
    PyObject_HEAD
    __render__::Camera *__ss_object;
} __ss_render_CameraObject;

static PyMemberDef __ss_render_CameraMembers[] = {
    {NULL}
};

PyObject *__ss_render_Camera___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Matrix4 *arg_0 = __ss_arg<Matrix4 *>("projection", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_render_CameraObject *)self)->__ss_object->__init__(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Camera_get_view_projection(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_CameraObject *)self)->__ss_object->get_view_projection());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_render_Camera_as_number = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

PyObject *__ss_render_Camera__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_render_Camera__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_render_CameraMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_render_Camera__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_render_Camera__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_render_Camera___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"get_view_projection", (PyCFunction)__ss_render_Camera_get_view_projection, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_render_Camera___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_render_Camera___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_render_CameraNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_render_CameraObject *self = (__ss_render_CameraObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __render__::Camera();
    self->__ss_object->__class__ = __render__::cl_Camera;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_render_CameraDealloc(__ss_render_CameraObject *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
    __ss_proxy->__delitem__(self->__ss_object);
}

PyObject *__ss_get___ss_render_Camera_transform(__ss_render_CameraObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->_transform);
}

int __ss_set___ss_render_Camera_transform(__ss_render_CameraObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->_transform = __to_ss<Transform *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Camera_projection(__ss_render_CameraObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->projection);
}

int __ss_set___ss_render_Camera_projection(__ss_render_CameraObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->projection = __to_ss<Matrix4 *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_render_CameraGetSet[] = {
    {(char *)"transform", (getter)__ss_get___ss_render_Camera_transform, (setter)__ss_set___ss_render_Camera_transform, (char *)"", NULL},
    {(char *)"projection", (getter)__ss_get___ss_render_Camera_projection, (setter)__ss_set___ss_render_Camera_projection, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_render_CameraObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "render.Camera",
    sizeof( __ss_render_CameraObject),
    0,
    (destructor) __ss_render_CameraDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_render_Camera_as_number,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT,
    PyDoc_STR("Custom objects"),
    0,
    0,
    0,
    0,
    0,
    0,
    __ss_render_CameraMethods,
    __ss_render_CameraMembers,
    __ss_render_CameraGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_render_Camera___tpinit__,
    0,
    __ss_render_CameraNew,
};

PyObject *__ss_render_Camera__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_render, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_render_CameraObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_render_CameraObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyTuple_New(2);
    PyTuple_SetItem(b, 0, __to_py(((__ss_render_CameraObject *)self)->__ss_object->_transform));
    PyTuple_SetItem(b, 1, __to_py(((__ss_render_CameraObject *)self)->__ss_object->projection));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_render_Camera__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    ((__ss_render_CameraObject *)self)->__ss_object->_transform = __to_ss<Transform *>(PyTuple_GetItem(state, 0));
    ((__ss_render_CameraObject *)self)->__ss_object->projection = __to_ss<Matrix4 *>(PyTuple_GetItem(state, 1));
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __render__

namespace __render__ { /* XXX */

/* class Mesh */

typedef struct {
    PyObject_HEAD
    __render__::Mesh *__ss_object;
} __ss_render_MeshObject;

static PyMemberDef __ss_render_MeshMembers[] = {
    {NULL}
};

PyObject *__ss_render_Mesh___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        str *arg_0 = __ss_arg<str *>("filename", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("scale", 1, 1, __ss_int(1), args, kwargs);

        return __to_py(((__ss_render_MeshObject *)self)->__ss_object->__init__(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Mesh_draw(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        RenderContext *arg_0 = __ss_arg<RenderContext *>("context", 0, 0, 0, args, kwargs);
        Matrix4 *arg_1 = __ss_arg<Matrix4 *>("view_projection", 1, 0, 0, args, kwargs);
        Matrix4 *arg_2 = __ss_arg<Matrix4 *>("transform", 2, 0, 0, args, kwargs);
        Bitmap *arg_3 = __ss_arg<Bitmap *>("texture", 3, 0, 0, args, kwargs);
        Vector4 *arg_4 = __ss_arg<Vector4 *>("lightDir", 4, 0, 0, args, kwargs);

        return __to_py(((__ss_render_MeshObject *)self)->__ss_object->draw(arg_0, arg_1, arg_2, arg_3, arg_4));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_render_Mesh_as_number = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

PyObject *__ss_render_Mesh__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_render_Mesh__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_render_MeshMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_render_Mesh__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_render_Mesh__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_render_Mesh___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"draw", (PyCFunction)__ss_render_Mesh_draw, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_render_Mesh___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_render_Mesh___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_render_MeshNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_render_MeshObject *self = (__ss_render_MeshObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __render__::Mesh();
    self->__ss_object->__class__ = __render__::cl_Mesh;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_render_MeshDealloc(__ss_render_MeshObject *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
    __ss_proxy->__delitem__(self->__ss_object);
}

PyObject *__ss_get___ss_render_Mesh_faces(__ss_render_MeshObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->faces);
}

int __ss_set___ss_render_Mesh_faces(__ss_render_MeshObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->faces = __to_ss<list<__ss_int> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Mesh_vertices(__ss_render_MeshObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->vertices);
}

int __ss_set___ss_render_Mesh_vertices(__ss_render_MeshObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->vertices = __to_ss<list<Vertex *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_render_MeshGetSet[] = {
    {(char *)"faces", (getter)__ss_get___ss_render_Mesh_faces, (setter)__ss_set___ss_render_Mesh_faces, (char *)"", NULL},
    {(char *)"vertices", (getter)__ss_get___ss_render_Mesh_vertices, (setter)__ss_set___ss_render_Mesh_vertices, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_render_MeshObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "render.Mesh",
    sizeof( __ss_render_MeshObject),
    0,
    (destructor) __ss_render_MeshDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_render_Mesh_as_number,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT,
    PyDoc_STR("Custom objects"),
    0,
    0,
    0,
    0,
    0,
    0,
    __ss_render_MeshMethods,
    __ss_render_MeshMembers,
    __ss_render_MeshGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_render_Mesh___tpinit__,
    0,
    __ss_render_MeshNew,
};

PyObject *__ss_render_Mesh__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_render, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_render_MeshObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_render_MeshObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyTuple_New(2);
    PyTuple_SetItem(b, 0, __to_py(((__ss_render_MeshObject *)self)->__ss_object->faces));
    PyTuple_SetItem(b, 1, __to_py(((__ss_render_MeshObject *)self)->__ss_object->vertices));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_render_Mesh__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    ((__ss_render_MeshObject *)self)->__ss_object->faces = __to_ss<list<__ss_int> *>(PyTuple_GetItem(state, 0));
    ((__ss_render_MeshObject *)self)->__ss_object->vertices = __to_ss<list<Vertex *> *>(PyTuple_GetItem(state, 1));
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __render__

namespace __render__ { /* XXX */

/* class Gradients */

typedef struct {
    PyObject_HEAD
    __render__::Gradients *__ss_object;
} __ss_render_GradientsObject;

static PyMemberDef __ss_render_GradientsMembers[] = {
    {NULL}
};

PyObject *__ss_render_Gradients___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vertex *arg_0 = __ss_arg<Vertex *>("minYVert", 0, 0, 0, args, kwargs);
        Vertex *arg_1 = __ss_arg<Vertex *>("midYVert", 1, 0, 0, args, kwargs);
        Vertex *arg_2 = __ss_arg<Vertex *>("maxYVert", 2, 0, 0, args, kwargs);
        Vector4 *arg_3 = __ss_arg<Vector4 *>("lightDir", 3, 0, 0, args, kwargs);

        return __to_py(((__ss_render_GradientsObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2, arg_3));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Gradients_CalcXStep(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        list<__ss_float> *arg_0 = __ss_arg<list<__ss_float> *>("values", 0, 0, 0, args, kwargs);
        Vertex *arg_1 = __ss_arg<Vertex *>("minYVert", 1, 0, 0, args, kwargs);
        Vertex *arg_2 = __ss_arg<Vertex *>("midYVert", 2, 0, 0, args, kwargs);
        Vertex *arg_3 = __ss_arg<Vertex *>("maxYVert", 3, 0, 0, args, kwargs);
        __ss_float arg_4 = __ss_arg<__ss_float >("oneOverdX", 4, 0, 0, args, kwargs);

        return __to_py(((__ss_render_GradientsObject *)self)->__ss_object->CalcXStep(arg_0, arg_1, arg_2, arg_3, arg_4));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Gradients_CalcYStep(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        list<__ss_float> *arg_0 = __ss_arg<list<__ss_float> *>("values", 0, 0, 0, args, kwargs);
        Vertex *arg_1 = __ss_arg<Vertex *>("minYVert", 1, 0, 0, args, kwargs);
        Vertex *arg_2 = __ss_arg<Vertex *>("midYVert", 2, 0, 0, args, kwargs);
        Vertex *arg_3 = __ss_arg<Vertex *>("maxYVert", 3, 0, 0, args, kwargs);
        __ss_float arg_4 = __ss_arg<__ss_float >("oneOverdY", 4, 0, 0, args, kwargs);

        return __to_py(((__ss_render_GradientsObject *)self)->__ss_object->CalcYStep(arg_0, arg_1, arg_2, arg_3, arg_4));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_render_Gradients_as_number = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

PyObject *__ss_render_Gradients__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_render_Gradients__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_render_GradientsMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_render_Gradients__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_render_Gradients__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_render_Gradients___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"CalcXStep", (PyCFunction)__ss_render_Gradients_CalcXStep, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"CalcYStep", (PyCFunction)__ss_render_Gradients_CalcYStep, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_render_Gradients___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_render_Gradients___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_render_GradientsNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_render_GradientsObject *self = (__ss_render_GradientsObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __render__::Gradients();
    self->__ss_object->__class__ = __render__::cl_Gradients;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_render_GradientsDealloc(__ss_render_GradientsObject *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
    __ss_proxy->__delitem__(self->__ss_object);
}

PyObject *__ss_get___ss_render_Gradients_texCoordY(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->texCoordY);
}

int __ss_set___ss_render_Gradients_texCoordY(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->texCoordY = __to_ss<list<__ss_float> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_depth(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->depth);
}

int __ss_set___ss_render_Gradients_depth(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->depth = __to_ss<list<__ss_float> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_oneOverZYStep(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->oneOverZYStep);
}

int __ss_set___ss_render_Gradients_oneOverZYStep(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->oneOverZYStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_lightAmtXStep(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->lightAmtXStep);
}

int __ss_set___ss_render_Gradients_lightAmtXStep(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->lightAmtXStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_texCoordYYStep(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->texCoordYYStep);
}

int __ss_set___ss_render_Gradients_texCoordYYStep(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->texCoordYYStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_texCoordXYStep(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->texCoordXYStep);
}

int __ss_set___ss_render_Gradients_texCoordXYStep(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->texCoordXYStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_lightAmtYStep(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->lightAmtYStep);
}

int __ss_set___ss_render_Gradients_lightAmtYStep(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->lightAmtYStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_oneOverZ(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->oneOverZ);
}

int __ss_set___ss_render_Gradients_oneOverZ(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->oneOverZ = __to_ss<list<__ss_float> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_depthYStep(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->depthYStep);
}

int __ss_set___ss_render_Gradients_depthYStep(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->depthYStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_texCoordYXStep(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->texCoordYXStep);
}

int __ss_set___ss_render_Gradients_texCoordYXStep(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->texCoordYXStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_texCoordX(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->texCoordX);
}

int __ss_set___ss_render_Gradients_texCoordX(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->texCoordX = __to_ss<list<__ss_float> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_texCoordXXStep(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->texCoordXXStep);
}

int __ss_set___ss_render_Gradients_texCoordXXStep(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->texCoordXXStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_depthXStep(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->depthXStep);
}

int __ss_set___ss_render_Gradients_depthXStep(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->depthXStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_oneOverZXStep(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->oneOverZXStep);
}

int __ss_set___ss_render_Gradients_oneOverZXStep(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->oneOverZXStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Gradients_lightAmt(__ss_render_GradientsObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->lightAmt);
}

int __ss_set___ss_render_Gradients_lightAmt(__ss_render_GradientsObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->lightAmt = __to_ss<list<__ss_float> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_render_GradientsGetSet[] = {
    {(char *)"texCoordY", (getter)__ss_get___ss_render_Gradients_texCoordY, (setter)__ss_set___ss_render_Gradients_texCoordY, (char *)"", NULL},
    {(char *)"depth", (getter)__ss_get___ss_render_Gradients_depth, (setter)__ss_set___ss_render_Gradients_depth, (char *)"", NULL},
    {(char *)"oneOverZYStep", (getter)__ss_get___ss_render_Gradients_oneOverZYStep, (setter)__ss_set___ss_render_Gradients_oneOverZYStep, (char *)"", NULL},
    {(char *)"lightAmtXStep", (getter)__ss_get___ss_render_Gradients_lightAmtXStep, (setter)__ss_set___ss_render_Gradients_lightAmtXStep, (char *)"", NULL},
    {(char *)"texCoordYYStep", (getter)__ss_get___ss_render_Gradients_texCoordYYStep, (setter)__ss_set___ss_render_Gradients_texCoordYYStep, (char *)"", NULL},
    {(char *)"texCoordXYStep", (getter)__ss_get___ss_render_Gradients_texCoordXYStep, (setter)__ss_set___ss_render_Gradients_texCoordXYStep, (char *)"", NULL},
    {(char *)"lightAmtYStep", (getter)__ss_get___ss_render_Gradients_lightAmtYStep, (setter)__ss_set___ss_render_Gradients_lightAmtYStep, (char *)"", NULL},
    {(char *)"oneOverZ", (getter)__ss_get___ss_render_Gradients_oneOverZ, (setter)__ss_set___ss_render_Gradients_oneOverZ, (char *)"", NULL},
    {(char *)"depthYStep", (getter)__ss_get___ss_render_Gradients_depthYStep, (setter)__ss_set___ss_render_Gradients_depthYStep, (char *)"", NULL},
    {(char *)"texCoordYXStep", (getter)__ss_get___ss_render_Gradients_texCoordYXStep, (setter)__ss_set___ss_render_Gradients_texCoordYXStep, (char *)"", NULL},
    {(char *)"texCoordX", (getter)__ss_get___ss_render_Gradients_texCoordX, (setter)__ss_set___ss_render_Gradients_texCoordX, (char *)"", NULL},
    {(char *)"texCoordXXStep", (getter)__ss_get___ss_render_Gradients_texCoordXXStep, (setter)__ss_set___ss_render_Gradients_texCoordXXStep, (char *)"", NULL},
    {(char *)"depthXStep", (getter)__ss_get___ss_render_Gradients_depthXStep, (setter)__ss_set___ss_render_Gradients_depthXStep, (char *)"", NULL},
    {(char *)"oneOverZXStep", (getter)__ss_get___ss_render_Gradients_oneOverZXStep, (setter)__ss_set___ss_render_Gradients_oneOverZXStep, (char *)"", NULL},
    {(char *)"lightAmt", (getter)__ss_get___ss_render_Gradients_lightAmt, (setter)__ss_set___ss_render_Gradients_lightAmt, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_render_GradientsObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "render.Gradients",
    sizeof( __ss_render_GradientsObject),
    0,
    (destructor) __ss_render_GradientsDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_render_Gradients_as_number,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT,
    PyDoc_STR("Custom objects"),
    0,
    0,
    0,
    0,
    0,
    0,
    __ss_render_GradientsMethods,
    __ss_render_GradientsMembers,
    __ss_render_GradientsGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_render_Gradients___tpinit__,
    0,
    __ss_render_GradientsNew,
};

PyObject *__ss_render_Gradients__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_render, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_render_GradientsObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_render_GradientsObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyTuple_New(15);
    PyTuple_SetItem(b, 0, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->texCoordY));
    PyTuple_SetItem(b, 1, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->depth));
    PyTuple_SetItem(b, 2, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->oneOverZYStep));
    PyTuple_SetItem(b, 3, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->lightAmtXStep));
    PyTuple_SetItem(b, 4, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->texCoordYYStep));
    PyTuple_SetItem(b, 5, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->texCoordXYStep));
    PyTuple_SetItem(b, 6, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->lightAmtYStep));
    PyTuple_SetItem(b, 7, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->oneOverZ));
    PyTuple_SetItem(b, 8, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->depthYStep));
    PyTuple_SetItem(b, 9, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->texCoordYXStep));
    PyTuple_SetItem(b, 10, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->texCoordX));
    PyTuple_SetItem(b, 11, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->texCoordXXStep));
    PyTuple_SetItem(b, 12, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->depthXStep));
    PyTuple_SetItem(b, 13, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->oneOverZXStep));
    PyTuple_SetItem(b, 14, __to_py(((__ss_render_GradientsObject *)self)->__ss_object->lightAmt));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_render_Gradients__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    ((__ss_render_GradientsObject *)self)->__ss_object->texCoordY = __to_ss<list<__ss_float> *>(PyTuple_GetItem(state, 0));
    ((__ss_render_GradientsObject *)self)->__ss_object->depth = __to_ss<list<__ss_float> *>(PyTuple_GetItem(state, 1));
    ((__ss_render_GradientsObject *)self)->__ss_object->oneOverZYStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 2));
    ((__ss_render_GradientsObject *)self)->__ss_object->lightAmtXStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 3));
    ((__ss_render_GradientsObject *)self)->__ss_object->texCoordYYStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 4));
    ((__ss_render_GradientsObject *)self)->__ss_object->texCoordXYStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 5));
    ((__ss_render_GradientsObject *)self)->__ss_object->lightAmtYStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 6));
    ((__ss_render_GradientsObject *)self)->__ss_object->oneOverZ = __to_ss<list<__ss_float> *>(PyTuple_GetItem(state, 7));
    ((__ss_render_GradientsObject *)self)->__ss_object->depthYStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 8));
    ((__ss_render_GradientsObject *)self)->__ss_object->texCoordYXStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 9));
    ((__ss_render_GradientsObject *)self)->__ss_object->texCoordX = __to_ss<list<__ss_float> *>(PyTuple_GetItem(state, 10));
    ((__ss_render_GradientsObject *)self)->__ss_object->texCoordXXStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 11));
    ((__ss_render_GradientsObject *)self)->__ss_object->depthXStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 12));
    ((__ss_render_GradientsObject *)self)->__ss_object->oneOverZXStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 13));
    ((__ss_render_GradientsObject *)self)->__ss_object->lightAmt = __to_ss<list<__ss_float> *>(PyTuple_GetItem(state, 14));
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __render__

namespace __render__ { /* XXX */

/* class Edge */

typedef struct {
    PyObject_HEAD
    __render__::Edge *__ss_object;
} __ss_render_EdgeObject;

static PyMemberDef __ss_render_EdgeMembers[] = {
    {NULL}
};

PyObject *__ss_render_Edge___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Gradients *arg_0 = __ss_arg<Gradients *>("gradients", 0, 0, 0, args, kwargs);
        Vertex *arg_1 = __ss_arg<Vertex *>("minYVert", 1, 0, 0, args, kwargs);
        Vertex *arg_2 = __ss_arg<Vertex *>("maxYVert", 2, 0, 0, args, kwargs);
        __ss_int arg_3 = __ss_arg<__ss_int >("minYVertIndex", 3, 0, 0, args, kwargs);

        return __to_py(((__ss_render_EdgeObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2, arg_3));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_Edge_step(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_EdgeObject *)self)->__ss_object->step());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_render_Edge_as_number = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

PyObject *__ss_render_Edge__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_render_Edge__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_render_EdgeMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_render_Edge__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_render_Edge__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_render_Edge___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"step", (PyCFunction)__ss_render_Edge_step, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_render_Edge___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_render_Edge___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_render_EdgeNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_render_EdgeObject *self = (__ss_render_EdgeObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __render__::Edge();
    self->__ss_object->__class__ = __render__::cl_Edge;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_render_EdgeDealloc(__ss_render_EdgeObject *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
    __ss_proxy->__delitem__(self->__ss_object);
}

PyObject *__ss_get___ss_render_Edge_xStep(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->xStep);
}

int __ss_set___ss_render_Edge_xStep(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->xStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_yStart(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->yStart);
}

int __ss_set___ss_render_Edge_yStart(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->yStart = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_yEnd(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->yEnd);
}

int __ss_set___ss_render_Edge_yEnd(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->yEnd = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_x(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->x);
}

int __ss_set___ss_render_Edge_x(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->x = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_texCoordXStep(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->texCoordXStep);
}

int __ss_set___ss_render_Edge_texCoordXStep(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->texCoordXStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_depthStep(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->depthStep);
}

int __ss_set___ss_render_Edge_depthStep(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->depthStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_texCoordX(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->texCoordX);
}

int __ss_set___ss_render_Edge_texCoordX(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->texCoordX = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_lightAmtStep(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->lightAmtStep);
}

int __ss_set___ss_render_Edge_lightAmtStep(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->lightAmtStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_lightAmt(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->lightAmt);
}

int __ss_set___ss_render_Edge_lightAmt(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->lightAmt = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_texCoordY(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->texCoordY);
}

int __ss_set___ss_render_Edge_texCoordY(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->texCoordY = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_texCoordYStep(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->texCoordYStep);
}

int __ss_set___ss_render_Edge_texCoordYStep(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->texCoordYStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_oneOverZStep(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->oneOverZStep);
}

int __ss_set___ss_render_Edge_oneOverZStep(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->oneOverZStep = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_oneOverZ(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->oneOverZ);
}

int __ss_set___ss_render_Edge_oneOverZ(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->oneOverZ = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_Edge_depth(__ss_render_EdgeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->depth);
}

int __ss_set___ss_render_Edge_depth(__ss_render_EdgeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->depth = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_render_EdgeGetSet[] = {
    {(char *)"xStep", (getter)__ss_get___ss_render_Edge_xStep, (setter)__ss_set___ss_render_Edge_xStep, (char *)"", NULL},
    {(char *)"yStart", (getter)__ss_get___ss_render_Edge_yStart, (setter)__ss_set___ss_render_Edge_yStart, (char *)"", NULL},
    {(char *)"yEnd", (getter)__ss_get___ss_render_Edge_yEnd, (setter)__ss_set___ss_render_Edge_yEnd, (char *)"", NULL},
    {(char *)"x", (getter)__ss_get___ss_render_Edge_x, (setter)__ss_set___ss_render_Edge_x, (char *)"", NULL},
    {(char *)"texCoordXStep", (getter)__ss_get___ss_render_Edge_texCoordXStep, (setter)__ss_set___ss_render_Edge_texCoordXStep, (char *)"", NULL},
    {(char *)"depthStep", (getter)__ss_get___ss_render_Edge_depthStep, (setter)__ss_set___ss_render_Edge_depthStep, (char *)"", NULL},
    {(char *)"texCoordX", (getter)__ss_get___ss_render_Edge_texCoordX, (setter)__ss_set___ss_render_Edge_texCoordX, (char *)"", NULL},
    {(char *)"lightAmtStep", (getter)__ss_get___ss_render_Edge_lightAmtStep, (setter)__ss_set___ss_render_Edge_lightAmtStep, (char *)"", NULL},
    {(char *)"lightAmt", (getter)__ss_get___ss_render_Edge_lightAmt, (setter)__ss_set___ss_render_Edge_lightAmt, (char *)"", NULL},
    {(char *)"texCoordY", (getter)__ss_get___ss_render_Edge_texCoordY, (setter)__ss_set___ss_render_Edge_texCoordY, (char *)"", NULL},
    {(char *)"texCoordYStep", (getter)__ss_get___ss_render_Edge_texCoordYStep, (setter)__ss_set___ss_render_Edge_texCoordYStep, (char *)"", NULL},
    {(char *)"oneOverZStep", (getter)__ss_get___ss_render_Edge_oneOverZStep, (setter)__ss_set___ss_render_Edge_oneOverZStep, (char *)"", NULL},
    {(char *)"oneOverZ", (getter)__ss_get___ss_render_Edge_oneOverZ, (setter)__ss_set___ss_render_Edge_oneOverZ, (char *)"", NULL},
    {(char *)"depth", (getter)__ss_get___ss_render_Edge_depth, (setter)__ss_set___ss_render_Edge_depth, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_render_EdgeObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "render.Edge",
    sizeof( __ss_render_EdgeObject),
    0,
    (destructor) __ss_render_EdgeDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_render_Edge_as_number,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT,
    PyDoc_STR("Custom objects"),
    0,
    0,
    0,
    0,
    0,
    0,
    __ss_render_EdgeMethods,
    __ss_render_EdgeMembers,
    __ss_render_EdgeGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_render_Edge___tpinit__,
    0,
    __ss_render_EdgeNew,
};

PyObject *__ss_render_Edge__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_render, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_render_EdgeObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_render_EdgeObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyTuple_New(14);
    PyTuple_SetItem(b, 0, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->xStep));
    PyTuple_SetItem(b, 1, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->yStart));
    PyTuple_SetItem(b, 2, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->yEnd));
    PyTuple_SetItem(b, 3, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->x));
    PyTuple_SetItem(b, 4, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->texCoordXStep));
    PyTuple_SetItem(b, 5, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->depthStep));
    PyTuple_SetItem(b, 6, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->texCoordX));
    PyTuple_SetItem(b, 7, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->lightAmtStep));
    PyTuple_SetItem(b, 8, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->lightAmt));
    PyTuple_SetItem(b, 9, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->texCoordY));
    PyTuple_SetItem(b, 10, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->texCoordYStep));
    PyTuple_SetItem(b, 11, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->oneOverZStep));
    PyTuple_SetItem(b, 12, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->oneOverZ));
    PyTuple_SetItem(b, 13, __to_py(((__ss_render_EdgeObject *)self)->__ss_object->depth));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_render_Edge__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    ((__ss_render_EdgeObject *)self)->__ss_object->xStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 0));
    ((__ss_render_EdgeObject *)self)->__ss_object->yStart = __to_ss<__ss_int >(PyTuple_GetItem(state, 1));
    ((__ss_render_EdgeObject *)self)->__ss_object->yEnd = __to_ss<__ss_int >(PyTuple_GetItem(state, 2));
    ((__ss_render_EdgeObject *)self)->__ss_object->x = __to_ss<__ss_float >(PyTuple_GetItem(state, 3));
    ((__ss_render_EdgeObject *)self)->__ss_object->texCoordXStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 4));
    ((__ss_render_EdgeObject *)self)->__ss_object->depthStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 5));
    ((__ss_render_EdgeObject *)self)->__ss_object->texCoordX = __to_ss<__ss_float >(PyTuple_GetItem(state, 6));
    ((__ss_render_EdgeObject *)self)->__ss_object->lightAmtStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 7));
    ((__ss_render_EdgeObject *)self)->__ss_object->lightAmt = __to_ss<__ss_float >(PyTuple_GetItem(state, 8));
    ((__ss_render_EdgeObject *)self)->__ss_object->texCoordY = __to_ss<__ss_float >(PyTuple_GetItem(state, 9));
    ((__ss_render_EdgeObject *)self)->__ss_object->texCoordYStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 10));
    ((__ss_render_EdgeObject *)self)->__ss_object->oneOverZStep = __to_ss<__ss_float >(PyTuple_GetItem(state, 11));
    ((__ss_render_EdgeObject *)self)->__ss_object->oneOverZ = __to_ss<__ss_float >(PyTuple_GetItem(state, 12));
    ((__ss_render_EdgeObject *)self)->__ss_object->depth = __to_ss<__ss_float >(PyTuple_GetItem(state, 13));
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __render__

namespace __render__ { /* XXX */

/* class RenderContext */

typedef struct {
    PyObject_HEAD
    __render__::RenderContext *__ss_object;
} __ss_render_RenderContextObject;

static PyMemberDef __ss_render_RenderContextMembers[] = {
    {NULL}
};

PyObject *__ss_render_RenderContext___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_int arg_0 = __ss_arg<__ss_int >("width", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("height", 1, 0, 0, args, kwargs);

        return __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->__init__(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_RenderContext_clear(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->clear());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_RenderContext_clear_zbuffer(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->clear_zbuffer());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_RenderContext_draw_triangle(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vertex *arg_0 = __ss_arg<Vertex *>("v1", 0, 0, 0, args, kwargs);
        Vertex *arg_1 = __ss_arg<Vertex *>("v2", 1, 0, 0, args, kwargs);
        Vertex *arg_2 = __ss_arg<Vertex *>("v3", 2, 0, 0, args, kwargs);
        Bitmap *arg_3 = __ss_arg<Bitmap *>("texture", 3, 0, 0, args, kwargs);
        Vector4 *arg_4 = __ss_arg<Vector4 *>("lightDir", 4, 0, 0, args, kwargs);

        return __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->draw_triangle(arg_0, arg_1, arg_2, arg_3, arg_4));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_RenderContext_ClipPolygonAxis(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        list<Vertex *> *arg_0 = __ss_arg<list<Vertex *> *>("vertices", 0, 0, 0, args, kwargs);
        list<Vertex *> *arg_1 = __ss_arg<list<Vertex *> *>("auxillaryList", 1, 0, 0, args, kwargs);
        __ss_int arg_2 = __ss_arg<__ss_int >("componentIndex", 2, 0, 0, args, kwargs);

        return __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->ClipPolygonAxis(arg_0, arg_1, arg_2));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_RenderContext_ClipPolygonComponent(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        list<Vertex *> *arg_0 = __ss_arg<list<Vertex *> *>("vertices", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("componentIndex", 1, 0, 0, args, kwargs);
        __ss_float arg_2 = __ss_arg<__ss_float >("componentFactor", 2, 0, 0, args, kwargs);
        list<Vertex *> *arg_3 = __ss_arg<list<Vertex *> *>("result", 3, 0, 0, args, kwargs);

        return __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->ClipPolygonComponent(arg_0, arg_1, arg_2, arg_3));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_RenderContext_fill_triangle(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vertex *arg_0 = __ss_arg<Vertex *>("v1", 0, 0, 0, args, kwargs);
        Vertex *arg_1 = __ss_arg<Vertex *>("v2", 1, 0, 0, args, kwargs);
        Vertex *arg_2 = __ss_arg<Vertex *>("v3", 2, 0, 0, args, kwargs);
        Bitmap *arg_3 = __ss_arg<Bitmap *>("texture", 3, 0, 0, args, kwargs);
        Vector4 *arg_4 = __ss_arg<Vector4 *>("lightDir", 4, 0, 0, args, kwargs);

        return __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->fill_triangle(arg_0, arg_1, arg_2, arg_3, arg_4));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_RenderContext_scan_triangle(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vertex *arg_0 = __ss_arg<Vertex *>("minYVert", 0, 0, 0, args, kwargs);
        Vertex *arg_1 = __ss_arg<Vertex *>("midYVert", 1, 0, 0, args, kwargs);
        Vertex *arg_2 = __ss_arg<Vertex *>("maxYVert", 2, 0, 0, args, kwargs);
        __ss_bool arg_3 = __ss_arg<__ss_bool >("handedness", 3, 0, False, args, kwargs);
        Bitmap *arg_4 = __ss_arg<Bitmap *>("texture", 4, 0, 0, args, kwargs);
        Vector4 *arg_5 = __ss_arg<Vector4 *>("lightDir", 5, 0, 0, args, kwargs);

        return __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->scan_triangle(arg_0, arg_1, arg_2, arg_3, arg_4, arg_5));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_RenderContext_scan_edges(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Gradients *arg_0 = __ss_arg<Gradients *>("gradients", 0, 0, 0, args, kwargs);
        Edge *arg_1 = __ss_arg<Edge *>("a", 1, 0, 0, args, kwargs);
        Edge *arg_2 = __ss_arg<Edge *>("b", 2, 0, 0, args, kwargs);
        __ss_bool arg_3 = __ss_arg<__ss_bool >("handedness", 3, 0, False, args, kwargs);
        Bitmap *arg_4 = __ss_arg<Bitmap *>("texture", 4, 0, 0, args, kwargs);

        return __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->scan_edges(arg_0, arg_1, arg_2, arg_3, arg_4));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_RenderContext_draw_scanline(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Gradients *arg_0 = __ss_arg<Gradients *>("gradients", 0, 0, 0, args, kwargs);
        Edge *arg_1 = __ss_arg<Edge *>("left", 1, 0, 0, args, kwargs);
        Edge *arg_2 = __ss_arg<Edge *>("right", 2, 0, 0, args, kwargs);
        __ss_int arg_3 = __ss_arg<__ss_int >("j", 3, 0, 0, args, kwargs);
        Bitmap *arg_4 = __ss_arg<Bitmap *>("texture", 4, 0, 0, args, kwargs);

        return __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->draw_scanline(arg_0, arg_1, arg_2, arg_3, arg_4));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_render_RenderContext_copy_pixel(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_int arg_0 = __ss_arg<__ss_int >("destX", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("destY", 1, 0, 0, args, kwargs);
        __ss_int arg_2 = __ss_arg<__ss_int >("srcX", 2, 0, 0, args, kwargs);
        __ss_int arg_3 = __ss_arg<__ss_int >("srcY", 3, 0, 0, args, kwargs);
        Bitmap *arg_4 = __ss_arg<Bitmap *>("src", 4, 0, 0, args, kwargs);
        __ss_float arg_5 = __ss_arg<__ss_float >("lightAmt", 5, 0, 0, args, kwargs);

        return __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->copy_pixel(arg_0, arg_1, arg_2, arg_3, arg_4, arg_5));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_render_RenderContext_as_number = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

PyObject *__ss_render_RenderContext__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_render_RenderContext__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_render_RenderContextMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_render_RenderContext__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_render_RenderContext__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_render_RenderContext___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"clear", (PyCFunction)__ss_render_RenderContext_clear, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"clear_zbuffer", (PyCFunction)__ss_render_RenderContext_clear_zbuffer, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"draw_triangle", (PyCFunction)__ss_render_RenderContext_draw_triangle, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"ClipPolygonAxis", (PyCFunction)__ss_render_RenderContext_ClipPolygonAxis, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"ClipPolygonComponent", (PyCFunction)__ss_render_RenderContext_ClipPolygonComponent, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"fill_triangle", (PyCFunction)__ss_render_RenderContext_fill_triangle, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"scan_triangle", (PyCFunction)__ss_render_RenderContext_scan_triangle, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"scan_edges", (PyCFunction)__ss_render_RenderContext_scan_edges, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"draw_scanline", (PyCFunction)__ss_render_RenderContext_draw_scanline, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"copy_pixel", (PyCFunction)__ss_render_RenderContext_copy_pixel, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_render_RenderContext___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_render_RenderContext___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_render_RenderContextNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_render_RenderContextObject *self = (__ss_render_RenderContextObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __render__::RenderContext();
    self->__ss_object->__class__ = __render__::cl_RenderContext;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_render_RenderContextDealloc(__ss_render_RenderContextObject *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
    __ss_proxy->__delitem__(self->__ss_object);
}

PyObject *__ss_get___ss_render_RenderContext_width(__ss_render_RenderContextObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->width);
}

int __ss_set___ss_render_RenderContext_width(__ss_render_RenderContextObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->width = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_RenderContext_bitmap(__ss_render_RenderContextObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->bitmap);
}

int __ss_set___ss_render_RenderContext_bitmap(__ss_render_RenderContextObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->bitmap = __to_ss<Bitmap *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_RenderContext_height(__ss_render_RenderContextObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->height);
}

int __ss_set___ss_render_RenderContext_height(__ss_render_RenderContextObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->height = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_RenderContext_zbuffer(__ss_render_RenderContextObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->zbuffer);
}

int __ss_set___ss_render_RenderContext_zbuffer(__ss_render_RenderContextObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->zbuffer = __to_ss<list<__ss_float> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_RenderContext_zbuffer_reset(__ss_render_RenderContextObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->zbuffer_reset);
}

int __ss_set___ss_render_RenderContext_zbuffer_reset(__ss_render_RenderContextObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->zbuffer_reset = __to_ss<list<__ss_float> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_render_RenderContext_screenSpaceTransform(__ss_render_RenderContextObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->screenSpaceTransform);
}

int __ss_set___ss_render_RenderContext_screenSpaceTransform(__ss_render_RenderContextObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->screenSpaceTransform = __to_ss<Matrix4 *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_render_RenderContextGetSet[] = {
    {(char *)"width", (getter)__ss_get___ss_render_RenderContext_width, (setter)__ss_set___ss_render_RenderContext_width, (char *)"", NULL},
    {(char *)"bitmap", (getter)__ss_get___ss_render_RenderContext_bitmap, (setter)__ss_set___ss_render_RenderContext_bitmap, (char *)"", NULL},
    {(char *)"height", (getter)__ss_get___ss_render_RenderContext_height, (setter)__ss_set___ss_render_RenderContext_height, (char *)"", NULL},
    {(char *)"zbuffer", (getter)__ss_get___ss_render_RenderContext_zbuffer, (setter)__ss_set___ss_render_RenderContext_zbuffer, (char *)"", NULL},
    {(char *)"zbuffer_reset", (getter)__ss_get___ss_render_RenderContext_zbuffer_reset, (setter)__ss_set___ss_render_RenderContext_zbuffer_reset, (char *)"", NULL},
    {(char *)"screenSpaceTransform", (getter)__ss_get___ss_render_RenderContext_screenSpaceTransform, (setter)__ss_set___ss_render_RenderContext_screenSpaceTransform, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_render_RenderContextObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "render.RenderContext",
    sizeof( __ss_render_RenderContextObject),
    0,
    (destructor) __ss_render_RenderContextDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_render_RenderContext_as_number,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT,
    PyDoc_STR("Custom objects"),
    0,
    0,
    0,
    0,
    0,
    0,
    __ss_render_RenderContextMethods,
    __ss_render_RenderContextMembers,
    __ss_render_RenderContextGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_render_RenderContext___tpinit__,
    0,
    __ss_render_RenderContextNew,
};

PyObject *__ss_render_RenderContext__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_render, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_render_RenderContextObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_render_RenderContextObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyTuple_New(6);
    PyTuple_SetItem(b, 0, __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->width));
    PyTuple_SetItem(b, 1, __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->bitmap));
    PyTuple_SetItem(b, 2, __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->height));
    PyTuple_SetItem(b, 3, __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->zbuffer));
    PyTuple_SetItem(b, 4, __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->zbuffer_reset));
    PyTuple_SetItem(b, 5, __to_py(((__ss_render_RenderContextObject *)self)->__ss_object->screenSpaceTransform));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_render_RenderContext__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    ((__ss_render_RenderContextObject *)self)->__ss_object->width = __to_ss<__ss_int >(PyTuple_GetItem(state, 0));
    ((__ss_render_RenderContextObject *)self)->__ss_object->bitmap = __to_ss<Bitmap *>(PyTuple_GetItem(state, 1));
    ((__ss_render_RenderContextObject *)self)->__ss_object->height = __to_ss<__ss_int >(PyTuple_GetItem(state, 2));
    ((__ss_render_RenderContextObject *)self)->__ss_object->zbuffer = __to_ss<list<__ss_float> *>(PyTuple_GetItem(state, 3));
    ((__ss_render_RenderContextObject *)self)->__ss_object->zbuffer_reset = __to_ss<list<__ss_float> *>(PyTuple_GetItem(state, 4));
    ((__ss_render_RenderContextObject *)self)->__ss_object->screenSpaceTransform = __to_ss<Matrix4 *>(PyTuple_GetItem(state, 5));
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __render__

namespace __render__ { /* XXX */
PyObject *Global_render_saturate(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_float arg_0 = __ss_arg<__ss_float >("val", 0, 0, 0, args, kwargs);

        return __to_py(__render__::saturate(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *Global_render_quaternion_from_axis_angle(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vector4 *arg_0 = __ss_arg<Vector4 *>("axis", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("angle", 1, 0, 0, args, kwargs);

        return __to_py(__render__::quaternion_from_axis_angle(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods Global_render_as_number = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

static PyMethodDef Global_renderMethods[] = {
    {(char *)"__newobj__", (PyCFunction)__ss__newobj__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"saturate", (PyCFunction)Global_render_saturate, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"quaternion_from_axis_angle", (PyCFunction)Global_render_quaternion_from_axis_angle, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef Module_render = {
    PyModuleDef_HEAD_INIT,
    "render",   /* name of module */
    NULL,   /* module documentation, may be NULL */
    -1,     /* size of per-interpreter state of the module or -1 if the module keeps state in global variables. */
    Global_renderMethods
};

PyMODINIT_FUNC PyInit_render(void) {

    __shedskin__::__init();
    __math__::__init();
    __render__::__init();

    PyObject *m;

    if (PyType_Ready(&__ss_render_BitmapObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_render_Vector4ObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_render_Matrix4ObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_render_QuaternionObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_render_VertexObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_render_TransformObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_render_CameraObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_render_MeshObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_render_GradientsObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_render_EdgeObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_render_RenderContextObjectType) < 0)
        return NULL;

    // create extension module
    __ss_mod_render = m = PyModule_Create(&Module_render);
    if (m == NULL)
        return NULL;

    // add global variables
    PyModule_AddObject(m, (char *)"mesh", __to_py(__render__::mesh));
    PyModule_AddObject(m, (char *)"texture", __to_py(__render__::texture));
    PyModule_AddObject(m, (char *)"v", __to_py(__render__::v));
    PyModule_AddObject(m, (char *)"transform", __to_py(__render__::transform));
    PyModule_AddObject(m, (char *)"target", __to_py(__render__::target));
    PyModule_AddObject(m, (char *)"camera", __to_py(__render__::camera));

    // add type objects
    Py_INCREF(&__ss_render_BitmapObjectType);
    if (PyModule_AddObject(m, "Bitmap", (PyObject *) &__ss_render_BitmapObjectType) < 0) {
        Py_DECREF(&__ss_render_BitmapObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_render_Vector4ObjectType);
    if (PyModule_AddObject(m, "Vector4", (PyObject *) &__ss_render_Vector4ObjectType) < 0) {
        Py_DECREF(&__ss_render_Vector4ObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_render_Matrix4ObjectType);
    if (PyModule_AddObject(m, "Matrix4", (PyObject *) &__ss_render_Matrix4ObjectType) < 0) {
        Py_DECREF(&__ss_render_Matrix4ObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_render_QuaternionObjectType);
    if (PyModule_AddObject(m, "Quaternion", (PyObject *) &__ss_render_QuaternionObjectType) < 0) {
        Py_DECREF(&__ss_render_QuaternionObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_render_VertexObjectType);
    if (PyModule_AddObject(m, "Vertex", (PyObject *) &__ss_render_VertexObjectType) < 0) {
        Py_DECREF(&__ss_render_VertexObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_render_TransformObjectType);
    if (PyModule_AddObject(m, "Transform", (PyObject *) &__ss_render_TransformObjectType) < 0) {
        Py_DECREF(&__ss_render_TransformObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_render_CameraObjectType);
    if (PyModule_AddObject(m, "Camera", (PyObject *) &__ss_render_CameraObjectType) < 0) {
        Py_DECREF(&__ss_render_CameraObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_render_MeshObjectType);
    if (PyModule_AddObject(m, "Mesh", (PyObject *) &__ss_render_MeshObjectType) < 0) {
        Py_DECREF(&__ss_render_MeshObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_render_GradientsObjectType);
    if (PyModule_AddObject(m, "Gradients", (PyObject *) &__ss_render_GradientsObjectType) < 0) {
        Py_DECREF(&__ss_render_GradientsObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_render_EdgeObjectType);
    if (PyModule_AddObject(m, "Edge", (PyObject *) &__ss_render_EdgeObjectType) < 0) {
        Py_DECREF(&__ss_render_EdgeObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_render_RenderContextObjectType);
    if (PyModule_AddObject(m, "RenderContext", (PyObject *) &__ss_render_RenderContextObjectType) < 0) {
        Py_DECREF(&__ss_render_RenderContextObjectType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}


} // namespace __render__

} // extern "C"
namespace __render__ { /* XXX */

PyObject *Bitmap::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_render_BitmapObject *self = (__ss_render_BitmapObject *)(__ss_render_BitmapObjectType.tp_alloc(&__ss_render_BitmapObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ { /* XXX */

template<> __render__::Bitmap *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__render__::__ss_render_BitmapObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Bitmap expected)"));
    return ((__render__::__ss_render_BitmapObject *)p)->__ss_object;
}
}
namespace __render__ { /* XXX */

PyObject *Vector4::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_render_Vector4Object *self = (__ss_render_Vector4Object *)(__ss_render_Vector4ObjectType.tp_alloc(&__ss_render_Vector4ObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ { /* XXX */

template<> __render__::Vector4 *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__render__::__ss_render_Vector4ObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Vector4 expected)"));
    return ((__render__::__ss_render_Vector4Object *)p)->__ss_object;
}
}
namespace __render__ { /* XXX */

PyObject *Matrix4::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_render_Matrix4Object *self = (__ss_render_Matrix4Object *)(__ss_render_Matrix4ObjectType.tp_alloc(&__ss_render_Matrix4ObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ { /* XXX */

template<> __render__::Matrix4 *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__render__::__ss_render_Matrix4ObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Matrix4 expected)"));
    return ((__render__::__ss_render_Matrix4Object *)p)->__ss_object;
}
}
namespace __render__ { /* XXX */

PyObject *Quaternion::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_render_QuaternionObject *self = (__ss_render_QuaternionObject *)(__ss_render_QuaternionObjectType.tp_alloc(&__ss_render_QuaternionObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ { /* XXX */

template<> __render__::Quaternion *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__render__::__ss_render_QuaternionObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Quaternion expected)"));
    return ((__render__::__ss_render_QuaternionObject *)p)->__ss_object;
}
}
namespace __render__ { /* XXX */

PyObject *Vertex::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_render_VertexObject *self = (__ss_render_VertexObject *)(__ss_render_VertexObjectType.tp_alloc(&__ss_render_VertexObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ { /* XXX */

template<> __render__::Vertex *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__render__::__ss_render_VertexObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Vertex expected)"));
    return ((__render__::__ss_render_VertexObject *)p)->__ss_object;
}
}
namespace __render__ { /* XXX */

PyObject *Transform::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_render_TransformObject *self = (__ss_render_TransformObject *)(__ss_render_TransformObjectType.tp_alloc(&__ss_render_TransformObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ { /* XXX */

template<> __render__::Transform *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__render__::__ss_render_TransformObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Transform expected)"));
    return ((__render__::__ss_render_TransformObject *)p)->__ss_object;
}
}
namespace __render__ { /* XXX */

PyObject *Camera::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_render_CameraObject *self = (__ss_render_CameraObject *)(__ss_render_CameraObjectType.tp_alloc(&__ss_render_CameraObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ { /* XXX */

template<> __render__::Camera *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__render__::__ss_render_CameraObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Camera expected)"));
    return ((__render__::__ss_render_CameraObject *)p)->__ss_object;
}
}
namespace __render__ { /* XXX */

PyObject *Mesh::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_render_MeshObject *self = (__ss_render_MeshObject *)(__ss_render_MeshObjectType.tp_alloc(&__ss_render_MeshObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ { /* XXX */

template<> __render__::Mesh *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__render__::__ss_render_MeshObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Mesh expected)"));
    return ((__render__::__ss_render_MeshObject *)p)->__ss_object;
}
}
namespace __render__ { /* XXX */

PyObject *Gradients::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_render_GradientsObject *self = (__ss_render_GradientsObject *)(__ss_render_GradientsObjectType.tp_alloc(&__ss_render_GradientsObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ { /* XXX */

template<> __render__::Gradients *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__render__::__ss_render_GradientsObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Gradients expected)"));
    return ((__render__::__ss_render_GradientsObject *)p)->__ss_object;
}
}
namespace __render__ { /* XXX */

PyObject *Edge::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_render_EdgeObject *self = (__ss_render_EdgeObject *)(__ss_render_EdgeObjectType.tp_alloc(&__ss_render_EdgeObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ { /* XXX */

template<> __render__::Edge *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__render__::__ss_render_EdgeObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Edge expected)"));
    return ((__render__::__ss_render_EdgeObject *)p)->__ss_object;
}
}
namespace __render__ { /* XXX */

PyObject *RenderContext::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_render_RenderContextObject *self = (__ss_render_RenderContextObject *)(__ss_render_RenderContextObjectType.tp_alloc(&__ss_render_RenderContextObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ { /* XXX */

template<> __render__::RenderContext *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__render__::__ss_render_RenderContextObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (RenderContext expected)"));
    return ((__render__::__ss_render_RenderContextObject *)p)->__ss_object;
}
}
int main(int, char **) {
    __shedskin__::__init();
    __math__::__init();
    __shedskin__::__start(__render__::__init);
}
