#ifndef __DOOM_HPP
#define __DOOM_HPP

using namespace __shedskin__;
namespace __doom__ {

extern str *const_0, *const_1, *const_11, *const_13, *const_15, *const_17, *const_2, *const_26, *const_28, *const_29, *const_3, *const_30, *const_32, *const_34, *const_36, *const_38, *const_39, *const_4, *const_40, *const_5, *const_6;
extern bytes *const_10, *const_12, *const_14, *const_16, *const_18, *const_19, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_27, *const_31, *const_33, *const_35, *const_37, *const_7, *const_8, *const_9;

class Vertex;
class Sidedef;
class Linedef;
class Sector;
class SubSector;
class Seg;
class Flat;
class BSPNode;
class Thing;
class Player;
class Texture;
class Picture;
class Colormap;
class Vec2;
class Map;
class ClipBufferNode;


extern file *__file;
extern __ss_int HEIGHT, HEIGHT_2, WIDTH, WIDTH_2, __void;
extern str *__name__;
extern __ss_float HEIGHT_INV, TAN_45_DEG;
extern list<__ss_float> *CEIL_Y_INV, *FLOOR_Y_INV;
extern list<__ss_int> *OSCILLATION;
extern Map *map_;


extern class_ *cl_Vertex;
class Vertex : public pyobj {
public:
    __ss_int x;
    __ss_int y;

    Vertex() {}
    Vertex(__ss_int x, __ss_int y) {
        this->__class__ = cl_Vertex;
        __init__(x, y);
    }
    void *__init__(__ss_int x, __ss_int y);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Sidedef;
class Sidedef : public pyobj {
public:
    Texture *lower_texture;
    Texture *middle_texture;
    __ss_int offset_x;
    __ss_int offset_y;
    Sector *sector;
    __ss_bool skyhack;
    Texture *upper_texture;

    Sidedef() {}
    Sidedef(__ss_int offset_x, __ss_int offset_y, Texture *upper_texture, Texture *lower_texture, Texture *middle_texture, Sector *sector) {
        this->__class__ = cl_Sidedef;
        __init__(offset_x, offset_y, upper_texture, lower_texture, middle_texture, sector);
    }
    void *__init__(__ss_int offset_x, __ss_int offset_y, Texture *upper_texture, Texture *lower_texture, Texture *middle_texture, Sector *sector);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Linedef;
class Linedef : public pyobj {
public:
    Sidedef *sidedef_back;
    Sidedef *sidedef_front;
    __ss_int special_type;
    Vertex *vertex_end;
    Vertex *vertex_start;

    Linedef() {}
    Linedef(Vertex *vertex_start, Vertex *vertex_end, __ss_int special_type, Sidedef *sidedef_front, Sidedef *sidedef_back) {
        this->__class__ = cl_Linedef;
        __init__(vertex_start, vertex_end, special_type, sidedef_front, sidedef_back);
    }
    void *__init__(Vertex *vertex_start, Vertex *vertex_end, __ss_int special_type, Sidedef *sidedef_front, Sidedef *sidedef_back);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Sector;
class Sector : public pyobj {
public:
    Flat *ceil_flat;
    __ss_int ceil_h;
    Picture *ceil_pic;
    bytes *ceil_texture;
    Flat *floor_flat;
    __ss_int floor_h;
    bytes *floor_texture;
    __ss_int light_level;
    list<__ss_bool> *_random;
    __ss_int special_type;

    Sector() {}
    Sector(__ss_int floor_h, __ss_int ceil_h, bytes *floor_texture, bytes *ceil_texture, __ss_int light_level, __ss_int special_type, Flat *floor_flat, Flat *ceil_flat, Picture *ceil_pic) {
        this->__class__ = cl_Sector;
        __init__(floor_h, ceil_h, floor_texture, ceil_texture, light_level, special_type, floor_flat, ceil_flat, ceil_pic);
    }
    void *__init__(__ss_int floor_h, __ss_int ceil_h, bytes *floor_texture, bytes *ceil_texture, __ss_int light_level, __ss_int special_type, Flat *floor_flat, Flat *ceil_flat, Picture *ceil_pic);
    virtual PyObject *__to_py__();
};

extern class_ *cl_SubSector;
class SubSector : public pyobj {
public:
    list<Seg *> *segs;

    SubSector() {}
    SubSector(list<Seg *> *segs) {
        this->__class__ = cl_SubSector;
        __init__(segs);
    }
    void *__init__(list<Seg *> *segs);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Seg;
class Seg : public pyobj {
public:
    __ss_int angle;
    __ss_bool is_portal;
    __ss_float length;
    Linedef *linedef;
    __ss_int offset;
    Sector *sector_back;
    Sector *sector_front;
    Sidedef *sidedef_back;
    Sidedef *sidedef_front;
    Vertex *vertex_end;
    Vertex *vertex_start;

    Seg() {}
    Seg(Vertex *vertex_start, Vertex *vertex_end, __ss_int angle, Linedef *linedef, Sidedef *sidedef_front, Sidedef *sidedef_back, __ss_bool is_portal, __ss_int offset, Sector *sector_front, Sector *sector_back) {
        this->__class__ = cl_Seg;
        __init__(vertex_start, vertex_end, angle, linedef, sidedef_front, sidedef_back, is_portal, offset, sector_front, sector_back);
    }
    void *__init__(Vertex *vertex_start, Vertex *vertex_end, __ss_int angle, Linedef *linedef, Sidedef *sidedef_front, Sidedef *sidedef_back, __ss_bool is_portal, __ss_int offset, Sector *sector_front, Sector *sector_back);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Flat;
class Flat : public pyobj {
public:
    list<list<list<__ss_int> *> *> *data;

    Flat() {}
    Flat(list<bytes *> *data) {
        this->__class__ = cl_Flat;
        __init__(data);
    }
    void *__init__(list<bytes *> *data);
    list<list<__ss_int> *> *get_data(__ss_int frame_count);
    virtual PyObject *__to_py__();
};

extern class_ *cl_BSPNode;
class BSPNode : public pyobj {
public:
    __ss_int change_partition_x;
    __ss_int change_partition_y;
    __ss_int lchild_id;
    __ss_int partition_x;
    __ss_int partition_y;
    __ss_int rchild_id;

    BSPNode() {}
    BSPNode(__ss_int partition_x, __ss_int partition_y, __ss_int change_partition_x, __ss_int change_partition_y, __ss_int rchild_id, __ss_int lchild_id) {
        this->__class__ = cl_BSPNode;
        __init__(partition_x, partition_y, change_partition_x, change_partition_y, rchild_id, lchild_id);
    }
    void *__init__(__ss_int partition_x, __ss_int partition_y, __ss_int change_partition_x, __ss_int change_partition_y, __ss_int rchild_id, __ss_int lchild_id);
    list<SubSector *> *visit(Map *map_, list<SubSector *> *subsectors);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Thing;
class Thing : public pyobj {
public:
    __ss_float angle;
    __ss_int type_;
    __ss_float x;
    __ss_float y;

    Thing() {}
    Thing(__ss_int x, __ss_int y, __ss_int angle, __ss_int type_) {
        this->__class__ = cl_Thing;
        __init__(x, y, angle, type_);
    }
    void *__init__(__ss_int x, __ss_int y, __ss_int angle, __ss_int type_);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Player;
class Player : public pyobj {
public:
    __ss_float angle;
    Vec2 *direction;
    __ss_float floor_h;
    __ss_float x;
    __ss_float y;
    __ss_float z;

    Player() {}
    Player(Thing *thing) {
        this->__class__ = cl_Player;
        __init__(thing);
    }
    void *__init__(Thing *thing);
    void *update();
    virtual PyObject *__to_py__();
};

extern class_ *cl_Texture;
class Texture : public pyobj {
public:
    list<list<__ss_int> *> *data;
    __ss_int height;
    bytes *name;
    __ss_int width;

    Texture() {}
    Texture(bytes *name, list<list<__ss_int> *> *data, __ss_int width, __ss_int height) {
        this->__class__ = cl_Texture;
        __init__(name, data, width, height);
    }
    void *__init__(bytes *name, list<list<__ss_int> *> *data, __ss_int width, __ss_int height);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Picture;
class Picture : public pyobj {
public:
    list<list<__ss_int> *> *data;
    __ss_int height;
    __ss_int width;

    Picture() {}
    Picture(bytes *data) {
        this->__class__ = cl_Picture;
        __init__(data);
    }
    void *__init__(bytes *data);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Colormap;
class Colormap : public pyobj {
public:
    list<__ss_int> *data;

    Colormap() {}
    Colormap(bytes *data) {
        this->__class__ = cl_Colormap;
        __init__(data);
    }
    void *__init__(bytes *data);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Vec2;
class Vec2 : public pyobj {
public:
    __ss_float x;
    __ss_float y;

    Vec2() {}
    Vec2(__ss_float x, __ss_float y) {
        this->__class__ = cl_Vec2;
        __init__(x, y);
    }
    void *__init__(__ss_float x, __ss_float y);
    __ss_float dot(Vec2 *v);
    virtual PyObject *__to_py__();
};

extern class_ *cl_Map;
class Map : public pyobj {
public:
    list<BSPNode *> *bspnodes;
    list<Colormap *> *colormaps;
    dict<bytes *, bytes *> *entry_data;
    list<Linedef *> *linedefs;
    list<tuple<__ss_int> *> *palette;
    list<Picture *> *patches;
    Player *player;
    list<Sector *> *sectors;
    list<Seg *> *segs;
    list<Sidedef *> *sidedefs;
    list<SubSector *> *subsectors;
    dict<bytes *, Texture *> *textures;
    list<Thing *> *things;
    list<Vertex *> *vertices;

    Map() {}
    Map(str *filepath, str *map_) {
        this->__class__ = cl_Map;
        __init__(filepath, map_);
    }
    void *__init__(str *filepath, str *map_);
    void *extract_entries(str *filepath, str *mapname);
    void *extract_vertices();
    void *extract_linedefs();
    void *extract_sidedefs();
    void *extract_sectors();
    void *extract_patches();
    void *extract_textures();
    void *extract_palette();
    void *extract_colormaps();
    void *extract_segs();
    void *extract_subsectors();
    void *extract_bspnodes();
    void *extract_things();
    virtual PyObject *__to_py__();
};

extern class_ *cl_ClipBufferNode;
class ClipBufferNode : public pyobj {
public:
    __ss_int end;
    ClipBufferNode *left;
    __ss_bool occluded;
    __ss_int partitionPoint;
    __ss_bool partitioned;
    ClipBufferNode *right;
    __ss_int start;

    ClipBufferNode() {}
    ClipBufferNode(__ss_int start, __ss_int end) {
        this->__class__ = cl_ClipBufferNode;
        __init__(start, end);
    }
    void *__init__(__ss_int start, __ss_int end);
    void *checkSpan(__ss_int start, __ss_int end, list<__ss_int> *result, __ss_bool add);
    virtual PyObject *__to_py__();
};

extern list<SubSector *> * default_0;
__ss_int get_special_light(Sector *sector, __ss_int frame_count);
Colormap *get_wall_colormap(list<Colormap *> *colormaps, __ss_float currentZ, Seg *seg, __ss_int frame_count);
Colormap *get_flat_colormap(list<Colormap *> *colormaps, __ss_float currentZ, Seg *seg, __ss_int frame_count);
void *draw_wall_col(bytes *drawsurf, __ss_int x, __ss_int middleMinY, __ss_int middleMaxY, Texture *wallTexture, __ss_float currentTextureX, __ss_float currentZ, __ss_float middleTextureY, __ss_float middleTextureYStep, Colormap *colormap);
void *draw_flat_col(bytes *drawsurf, __ss_int x, __ss_int ceilMin, __ss_int ceilMax, Seg *seg, Player *player, list<list<__ss_int> *> *flatTexture, __ss_int flat_h, list<__ss_float> *INV, __ss_int sign, list<Colormap *> *colormaps, __ss_int frame_count);
void *draw_sky_col(bytes *drawsurf, __ss_int x, __ss_int upperMinY, __ss_int upperMaxY, Seg *seg, Player *player);
void *draw_seg(Seg *seg, Map *map_, bytes *drawsurf, __ss_int scrXA, __ss_int scrXB, ClipBufferNode *cbuffer, __ss_float za, __ss_float zb, __ss_float textureX0, __ss_float textureX1, Sidedef *frontSidedef, list<__ss_int> *lowerOcclusion, list<__ss_int> *upperOcclusion, __ss_int frame_count);
bytes *render(Map *map_, __ss_int frame_count);

extern "C" {
PyMODINIT_FUNC PyInit_doom(void);

}
} // module namespace
extern "C" PyTypeObject __ss_doom_VertexObjectType;
extern "C" PyTypeObject __ss_doom_SidedefObjectType;
extern "C" PyTypeObject __ss_doom_LinedefObjectType;
extern "C" PyTypeObject __ss_doom_SectorObjectType;
extern "C" PyTypeObject __ss_doom_SubSectorObjectType;
extern "C" PyTypeObject __ss_doom_SegObjectType;
extern "C" PyTypeObject __ss_doom_FlatObjectType;
extern "C" PyTypeObject __ss_doom_BSPNodeObjectType;
extern "C" PyTypeObject __ss_doom_ThingObjectType;
extern "C" PyTypeObject __ss_doom_PlayerObjectType;
extern "C" PyTypeObject __ss_doom_TextureObjectType;
extern "C" PyTypeObject __ss_doom_PictureObjectType;
extern "C" PyTypeObject __ss_doom_ColormapObjectType;
extern "C" PyTypeObject __ss_doom_Vec2ObjectType;
extern "C" PyTypeObject __ss_doom_MapObjectType;
extern "C" PyTypeObject __ss_doom_ClipBufferNodeObjectType;
namespace __shedskin__ {

template<> __doom__::Vertex *__to_ss(PyObject *p);
template<> __doom__::Sidedef *__to_ss(PyObject *p);
template<> __doom__::Linedef *__to_ss(PyObject *p);
template<> __doom__::Sector *__to_ss(PyObject *p);
template<> __doom__::SubSector *__to_ss(PyObject *p);
template<> __doom__::Seg *__to_ss(PyObject *p);
template<> __doom__::Flat *__to_ss(PyObject *p);
template<> __doom__::BSPNode *__to_ss(PyObject *p);
template<> __doom__::Thing *__to_ss(PyObject *p);
template<> __doom__::Player *__to_ss(PyObject *p);
template<> __doom__::Texture *__to_ss(PyObject *p);
template<> __doom__::Picture *__to_ss(PyObject *p);
template<> __doom__::Colormap *__to_ss(PyObject *p);
template<> __doom__::Vec2 *__to_ss(PyObject *p);
template<> __doom__::Map *__to_ss(PyObject *p);
template<> __doom__::ClipBufferNode *__to_ss(PyObject *p);
}
#endif
