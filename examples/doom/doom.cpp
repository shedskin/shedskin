#include "builtin.hpp"
#include "math/__init__.hpp"
#include "random.hpp"
#include "struct.hpp"
#include "time.hpp"
#include "doom.hpp"

namespace __doom__ {

str *const_0, *const_1, *const_11, *const_13, *const_15, *const_17, *const_2, *const_26, *const_28, *const_29, *const_3, *const_30, *const_32, *const_34, *const_36, *const_38, *const_39, *const_4, *const_40, *const_5, *const_6;
bytes *const_10, *const_12, *const_14, *const_16, *const_18, *const_19, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_27, *const_31, *const_33, *const_35, *const_37, *const_7, *const_8, *const_9;

using __struct__::unpack_from;

file *__file;
__ss_int HEIGHT, HEIGHT_2, WIDTH, WIDTH_2, __void;
str *__name__;
__ss_float HEIGHT_INV, TAN_45_DEG;
list<__ss_float> *CEIL_Y_INV, *FLOOR_Y_INV;
list<__ss_int> *OSCILLATION;
Map *map_;


list<SubSector *> * default_0;
static inline list<__ss_float> *list_comp_0();
static inline list<__ss_float> *list_comp_1();
static inline list<__ss_int> *list_comp_2();
static inline list<__ss_bool> *list_comp_3();
static inline list<__ss_int> *list_comp_4(bytes *d, __ss_int x);
static inline list<list<__ss_int> *> *list_comp_5(bytes *d);
static inline list<list<list<__ss_int> *> *> *list_comp_6(list<bytes *> *data);
static inline list<__ss_int> *list_comp_7(__ss_int height);
static inline list<list<__ss_int> *> *list_comp_8(__ss_int height, __ss_int width);
static inline list<__ss_int> *list_comp_9(str *mapname);
static inline list<bytes *> *list_comp_10(list<bytes *> *names, Map *self);
static inline list<__ss_int> *list_comp_11(__ss_int height);
static inline list<list<__ss_int> *> *list_comp_12(__ss_int height, __ss_int width);

static inline list<__ss_float> *list_comp_0() {
    __ss_int __0, __1, y;

    list<__ss_float> *__ss_result = new list<__ss_float>();

    __SS_LIST_RESERVE(__ss_result, 4);
    FAST_FOR(y,0,__doom__::HEIGHT,1,0,1)
        __ss_result->append((((y>__doom__::HEIGHT_2))?(__divs(__ss_float(1.0), (y-__doom__::HEIGHT_2))):(__ss_float(0.0))));
    END_FOR

    return __ss_result;
}

static inline list<__ss_float> *list_comp_1() {
    __ss_int __2, __3, y;

    list<__ss_float> *__ss_result = new list<__ss_float>();

    __SS_LIST_RESERVE(__ss_result, 4);
    FAST_FOR(y,0,__doom__::HEIGHT,1,2,3)
        __ss_result->append((((y<__doom__::HEIGHT_2))?(__divs(__ss_float(1.0), (__doom__::HEIGHT_2-y))):(__ss_float(0.0))));
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_2() {
    __ss_int __4, __5, i;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(256);
    FAST_FOR(i,0,__ss_int(256LL),1,4,5)
        __ss_result->units[__4] = __int((__ss_int(13LL)+(__ss_int(13LL)*__math__::sin(((__ss_int(2LL)*__math__::pi)*__divs(i, __ss_int(255LL)))))));
    END_FOR

    return __ss_result;
}

static inline list<__ss_bool> *list_comp_3() {
    __ss_int __6, __7, i;

    list<__ss_bool> *__ss_result = new list<__ss_bool>();

    __ss_result->resize(256);
    FAST_FOR(i,0,__ss_int(256LL),1,6,7)
        __ss_result->units[__6] = ___bool((__random__::random()<__ss_float(0.5)));
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_4(bytes *d, __ss_int x) {
    __ss_int __14, __15, y;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(64);
    FAST_FOR(y,0,__ss_int(64LL),1,14,15)
        __ss_result->units[__14] = d->__getfast__(((__ss_int(64LL)*y)+x));
    END_FOR

    return __ss_result;
}

static inline list<list<__ss_int> *> *list_comp_5(bytes *d) {
    __ss_int __12, __13, x;

    list<list<__ss_int> *> *__ss_result = new list<list<__ss_int> *>();

    __ss_result->resize(64);
    FAST_FOR(x,0,__ss_int(64LL),1,12,13)
        __ss_result->units[__12] = list_comp_4(d, x);
    END_FOR

    return __ss_result;
}

static inline list<list<list<__ss_int> *> *> *list_comp_6(list<bytes *> *data) {
    bytes *d;
    list<bytes *> *__8;
    __iter<bytes *> *__9;
    __ss_int __10;
    list<bytes *>::for_in_loop __11;

    list<list<list<__ss_int> *> *> *__ss_result = new list<list<list<__ss_int> *> *>();

    __ss_result->resize(len(data));
    FOR_IN(d,data,8,10,11)
        __ss_result->units[__10] = list_comp_5(d);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_7(__ss_int height) {
    __ss_int __30, __31, k;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __SS_LIST_RESERVE(__ss_result, 4);
    FAST_FOR(k,0,height,1,30,31)
        __ss_result->append(__ss_int(0LL));
    END_FOR

    return __ss_result;
}

static inline list<list<__ss_int> *> *list_comp_8(__ss_int height, __ss_int width) {
    __ss_int __28, __29, j;

    list<list<__ss_int> *> *__ss_result = new list<list<__ss_int> *>();

    __SS_LIST_RESERVE(__ss_result, 4);
    FAST_FOR(j,0,width,1,28,29)
        __ss_result->append(list_comp_7(height));
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_9(str *mapname) {
    str *__47, *c;
    __iter<str *> *__48;
    __ss_int __49;
    str::for_in_loop __50;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(len(mapname));
    FOR_IN(c,mapname,47,49,50)
        __ss_result->units[__49] = ord(c);
    END_FOR

    return __ss_result;
}

static inline list<bytes *> *list_comp_10(list<bytes *> *names, Map *self) {
    bytes *name;
    list<bytes *> *__85;
    __iter<bytes *> *__86;
    __ss_int __87;
    list<bytes *>::for_in_loop __88;

    list<bytes *> *__ss_result = new list<bytes *>();

    __ss_result->resize(len(names));
    FOR_IN(name,names,85,87,88)
        __ss_result->units[__87] = (self->entry_data)->__getitem__(name);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_11(__ss_int height) {
    __ss_int __104, __105, k;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __SS_LIST_RESERVE(__ss_result, 4);
    FAST_FOR(k,0,height,1,104,105)
        __ss_result->append(__ss_int(0LL));
    END_FOR

    return __ss_result;
}

static inline list<list<__ss_int> *> *list_comp_12(__ss_int height, __ss_int width) {
    __ss_int __102, __103, j;

    list<list<__ss_int> *> *__ss_result = new list<list<__ss_int> *>();

    __SS_LIST_RESERVE(__ss_result, 4);
    FAST_FOR(j,0,width,1,102,103)
        __ss_result->append(list_comp_11(height));
    END_FOR

    return __ss_result;
}

/**
class Vertex
*/

class_ *cl_Vertex;

void *Vertex::__init__(__ss_int x, __ss_int y) {
    this->x = x;
    this->y = y;
    return NULL;
}

/**
class Sidedef
*/

class_ *cl_Sidedef;

void *Sidedef::__init__(__ss_int offset_x, __ss_int offset_y, Texture *upper_texture, Texture *lower_texture, Texture *middle_texture, Sector *sector) {
    this->offset_x = offset_x;
    this->offset_y = offset_y;
    this->upper_texture = upper_texture;
    this->lower_texture = lower_texture;
    this->middle_texture = middle_texture;
    this->sector = sector;
    this->skyhack = False;
    return NULL;
}

/**
class Linedef
*/

class_ *cl_Linedef;

void *Linedef::__init__(Vertex *vertex_start, Vertex *vertex_end, __ss_int special_type, Sidedef *sidedef_front, Sidedef *sidedef_back) {
    this->vertex_start = vertex_start;
    this->vertex_end = vertex_end;
    this->special_type = special_type;
    this->sidedef_front = sidedef_front;
    this->sidedef_back = sidedef_back;
    return NULL;
}

/**
class Sector
*/

class_ *cl_Sector;

void *Sector::__init__(__ss_int floor_h, __ss_int ceil_h, bytes *floor_texture, bytes *ceil_texture, __ss_int light_level, __ss_int special_type, Flat *floor_flat, Flat *ceil_flat, Picture *ceil_pic) {
    this->floor_h = floor_h;
    this->ceil_h = ceil_h;
    this->floor_texture = floor_texture;
    this->ceil_texture = ceil_texture;
    this->light_level = light_level;
    this->special_type = special_type;
    this->floor_flat = floor_flat;
    this->ceil_flat = ceil_flat;
    this->ceil_pic = ceil_pic;
    this->_random = list_comp_3();
    return NULL;
}

/**
class SubSector
*/

class_ *cl_SubSector;

void *SubSector::__init__(list<Seg *> *segs) {
    this->segs = segs;
    return NULL;
}

/**
class Seg
*/

class_ *cl_Seg;

void *Seg::__init__(Vertex *vertex_start, Vertex *vertex_end, __ss_int angle, Linedef *linedef, Sidedef *sidedef_front, Sidedef *sidedef_back, __ss_bool is_portal, __ss_int offset, Sector *sector_front, Sector *sector_back) {
    this->vertex_start = vertex_start;
    this->vertex_end = vertex_end;
    this->angle = angle;
    this->linedef = linedef;
    this->sidedef_front = sidedef_front;
    this->sidedef_back = sidedef_back;
    this->is_portal = is_portal;
    this->offset = offset;
    this->sector_front = sector_front;
    this->sector_back = sector_back;
    this->length = __math__::hypot(2, (vertex_end->x-vertex_start->x), (vertex_end->y-vertex_start->y));
    return NULL;
}

/**
class Flat
*/

class_ *cl_Flat;

void *Flat::__init__(list<bytes *> *data) {
    this->data = list_comp_6(data);
    return NULL;
}

list<list<__ss_int> *> *Flat::get_data(__ss_int frame_count) {
    return (this->data)->__getfast__(__mods((frame_count>>__ss_int(4LL)), len(this->data)));
}

/**
class BSPNode
*/

class_ *cl_BSPNode;

void *BSPNode::__init__(__ss_int partition_x, __ss_int partition_y, __ss_int change_partition_x, __ss_int change_partition_y, __ss_int rchild_id, __ss_int lchild_id) {
    this->partition_x = partition_x;
    this->partition_y = partition_y;
    this->change_partition_x = change_partition_x;
    this->change_partition_y = change_partition_y;
    this->rchild_id = rchild_id;
    this->lchild_id = lchild_id;
    return NULL;
}

list<SubSector *> *BSPNode::visit(Map *map_, list<SubSector *> *subsectors) {
    Player *player;
    __ss_float px, py;
    __ss_int __16, __17, __18, __19, __22, child_id, closest_id, farthest_id;
    tuple<__ss_int> *__20;
    __iter<__ss_int> *__21;
    tuple<__ss_int>::for_in_loop __23;

    if ((subsectors==NULL)) {
        subsectors = (__ss_list<SubSector *, 0>());
    }
    player = map_->player;
    px = (player->x-this->partition_x);
    py = (player->y-this->partition_y);
    __16 = this->lchild_id;
    __17 = this->rchild_id;
    closest_id = __16;
    farthest_id = __17;
    if (((py*this->change_partition_x)<=(px*this->change_partition_y))) {
        __18 = farthest_id;
        __19 = closest_id;
        closest_id = __18;
        farthest_id = __19;
    }

    for(__ss_int __20 : {closest_id,farthest_id}) {
        child_id = __20;
        if ((child_id<__ss_int(0LL))) {
            subsectors->append((map_->subsectors)->__getfast__(((child_id)&(__ss_int(32767LL)))));
        }
        else {
            ((map_->bspnodes)->__getfast__(child_id))->visit(map_, subsectors);
        }
    END_FOR

    return subsectors;
}

/**
class Thing
*/

class_ *cl_Thing;

void *Thing::__init__(__ss_int x, __ss_int y, __ss_int angle, __ss_int type_) {
    this->x = __float(x);
    this->y = __float(y);
    this->angle = __math__::radians(__ss_int(90LL));
    this->type_ = type_;
    return NULL;
}

/**
class Player
*/

class_ *cl_Player;

void *Player::__init__(Thing *thing) {
    this->x = thing->x;
    this->y = thing->y;
    this->z = __ss_float(0.0);
    this->angle = thing->angle;
    this->floor_h = __ss_float(48.0);
    this->direction = (new Vec2(__math__::cos(this->angle), __math__::sin(this->angle)));
    return NULL;
}

void *Player::update() {
    this->direction = (new Vec2(__math__::cos(this->angle), __math__::sin(this->angle)));
    return NULL;
}

/**
class Texture
*/

class_ *cl_Texture;

void *Texture::__init__(bytes *name, list<list<__ss_int> *> *data, __ss_int width, __ss_int height) {
    this->name = name;
    this->data = data;
    this->width = width;
    this->height = height;
    return NULL;
}

/**
class Picture
*/

class_ *cl_Picture;

void *Picture::__init__(bytes *data) {
    __ss_int _, __25, __26, __27, __32, __33, __35, __37, __39, __40, __41, col_offset, height, j, length, offset_x, offset_y, width, y, y_offset;
    bytes *__24, *__34, *__36, *__38;
    list<__ss_int> *__42;

    __24 = data;
    __25 = __wrap(__24, __ss_int(0LL));
    width = __struct__::unpack_int('<', 'H', 1, __24, &__25);
    height = __struct__::unpack_int('<', 'H', 1, __24, &__25);
    offset_x = __struct__::unpack_int('<', 'h', 1, __24, &__25);
    offset_y = __struct__::unpack_int('<', 'h', 1, __24, &__25);
    __26 = width;
    __27 = height;
    this->width = __26;
    this->height = __27;
    this->data = list_comp_8(height, width);

    FAST_FOR(j,0,width,1,32,33)
        __34 = data;
        __35 = __wrap(__34, (__ss_int(8LL)+(__ss_int(4LL)*j)));
        col_offset = __struct__::unpack_int('<', 'H', 1, __34, &__35);
        __36 = data;
        __37 = __wrap(__36, col_offset);
        y_offset = __struct__::unpack_int('<', 'B', 1, __36, &__37);
        __38 = data;
        __39 = __wrap(__38, (col_offset+__ss_int(1LL)));
        length = __struct__::unpack_int('<', 'B', 1, __38, &__39);
        _ = __struct__::unpack_int('<', 'B', 1, __38, &__39);

        FAST_FOR(y,0,length,1,40,41)
            (this->data)->__getfast__(j)->__setitem__((y+y_offset), data->__getfast__(((col_offset+__ss_int(3LL))+y)));
        END_FOR

    END_FOR

    return NULL;
}

/**
class Colormap
*/

class_ *cl_Colormap;

void *Colormap::__init__(bytes *data) {
    __ss_int __43, __44, i;

    this->data = (__ss_list<__ss_int, 1>());

    FAST_FOR(i,0,__ss_int(256LL),1,43,44)
        (this->data)->append(data->__getfast__(i));
    END_FOR

    return NULL;
}

/**
class Vec2
*/

class_ *cl_Vec2;

void *Vec2::__init__(__ss_float x, __ss_float y) {
    this->x = x;
    this->y = y;
    return NULL;
}

__ss_float Vec2::dot(Vec2 *v) {
    return ((this->x*v->x)+(this->y*v->y));
}

/**
class Map
*/

class_ *cl_Map;

void *Map::__init__(str *filepath, str *map_) {
    this->extract_entries(filepath, map_);
    this->extract_palette();
    this->extract_colormaps();
    this->extract_patches();
    this->extract_textures();
    this->extract_vertices();
    this->extract_sectors();
    this->extract_sidedefs();
    this->extract_linedefs();
    this->extract_segs();
    this->extract_subsectors();
    this->extract_bspnodes();
    this->extract_things();
    this->player = (new Player((this->things)->__getfast__(__ss_int(0LL))));
    return NULL;
}

void *Map::extract_entries(str *filepath, str *mapname) {
    bytes *__45, *__53, *__56, *bmapname, *data, *name;
    __ss_int __46, __51, __52, __54, dir_offset, i, length, nentries, offset;
    __ss_bool __55, __57, __58, __59, inmap;
    dict<bytes *, bytes *> *__60;

    data = (open_binary(filepath, const_4))->read();
    __45 = data;
    __46 = __wrap(__45, __ss_int(4LL));
    nentries = __struct__::unpack_int('<', 'I', 1, __45, &__46);
    dir_offset = __struct__::unpack_int('<', 'I', 1, __45, &__46);
    this->entry_data = (new dict<bytes *, bytes *>());
    inmap = False;
    bmapname = __bytes(list_comp_9(mapname));

    FAST_FOR(i,0,nentries,1,51,52)
        __53 = data;
        __54 = __wrap(__53, (dir_offset+(i*__ss_int(16LL))));
        offset = __struct__::unpack_int('<', 'I', 1, __53, &__54);
        length = __struct__::unpack_int('<', 'I', 1, __53, &__54);
        name = __struct__::unpack_bytes('<', 's', 8, __53, &__54);
        name = name->rstrip(const_7);
        if (__eq(name, bmapname)) {
            inmap = True;
        }
        else if (((inmap or (__eq(__56=name,const_8) || __eq(__56,const_9))) and (!(this->entry_data)->__contains__(name)))) {
            this->entry_data->__setitem__(name->upper(), data->__slice__(__ss_int(3LL), offset, (offset+length), __ss_int(0LL)));
        }
    END_FOR

    return NULL;
}

void *Map::extract_vertices() {
    bytes *__63, *data;
    __ss_int __61, __62, __64, j, x, y;

    this->vertices = (__ss_list<Vertex *, 2>());
    data = (this->entry_data)->__getitem__(const_10);

    FAST_FOR(j,0,__floordiv(len(data),__ss_int(4LL)),1,61,62)
        __63 = data;
        __64 = __wrap(__63, (j*__ss_int(4LL)));
        x = __struct__::unpack_int('<', 'h', 1, __63, &__64);
        y = __struct__::unpack_int('<', 'h', 1, __63, &__64);
        (this->vertices)->append((new Vertex(x, y)));
    END_FOR

    return NULL;
}

void *Map::extract_linedefs() {
    bytes *__67, *data;
    __ss_int _, __65, __66, __68, __71, j, sidedef_back, sidedef_front, special_type, vertex_end, vertex_start;
    Vertex *vertex_a, *vertex_b;
    Sidedef *sidedef_a, *sidedef_b;
    Linedef *linedef;
    list<Linedef *> *__69;
    __iter<Linedef *> *__70;
    list<Linedef *>::for_in_loop __72;
    __ss_bool __73, __74, __75, __76;

    this->linedefs = (__ss_list<Linedef *, 3>());
    data = (this->entry_data)->__getitem__(const_12);

    FAST_FOR(j,0,__floordiv(len(data),__ss_int(14LL)),1,65,66)
        __67 = data;
        __68 = __wrap(__67, (j*__ss_int(14LL)));
        vertex_start = __struct__::unpack_int('<', 'H', 1, __67, &__68);
        vertex_end = __struct__::unpack_int('<', 'H', 1, __67, &__68);
        _ = __struct__::unpack_int('<', 'H', 1, __67, &__68);
        special_type = __struct__::unpack_int('<', 'H', 1, __67, &__68);
        _ = __struct__::unpack_int('<', 'H', 1, __67, &__68);
        sidedef_front = __struct__::unpack_int('<', 'H', 1, __67, &__68);
        sidedef_back = __struct__::unpack_int('<', 'H', 1, __67, &__68);
        vertex_a = (this->vertices)->__getfast__(vertex_start);
        vertex_b = (this->vertices)->__getfast__(vertex_end);
        sidedef_a = (this->sidedefs)->__getfast__(sidedef_front);
        if ((sidedef_back!=__ss_int(65535LL))) {
            sidedef_b = (this->sidedefs)->__getfast__(sidedef_back);
        }
        else {
            sidedef_b = NULL;
        }
        linedef = (new Linedef(vertex_a, vertex_b, special_type, sidedef_a, sidedef_b));
        (this->linedefs)->append(linedef);
    END_FOR


    FOR_IN(linedef,this->linedefs,69,71,72)
        if (((linedef->sidedef_front!=NULL) and (((linedef->sidedef_front)->sector)->ceil_pic!=NULL) and (linedef->sidedef_back!=NULL) and (((linedef->sidedef_back)->sector)->ceil_pic!=NULL))) {
            linedef->sidedef_front->skyhack = True;
        }
    END_FOR

    return NULL;
}

void *Map::extract_sidedefs() {
    bytes *__79, *data, *lower_texture_name, *middle_texture_name, *upper_texture_name;
    __ss_int __77, __78, __80, j, offset_x, offset_y, sector_nr;
    Texture *lower_texture, *middle_texture, *upper_texture;
    Sector *sector;
    Sidedef *sidedef;

    this->sidedefs = (__ss_list<Sidedef *, 4>());
    data = (this->entry_data)->__getitem__(const_14);

    FAST_FOR(j,0,__floordiv(len(data),__ss_int(30LL)),1,77,78)
        __79 = data;
        __80 = __wrap(__79, (j*__ss_int(30LL)));
        offset_x = __struct__::unpack_int('<', 'H', 1, __79, &__80);
        offset_y = __struct__::unpack_int('<', 'H', 1, __79, &__80);
        upper_texture_name = __struct__::unpack_bytes('<', 's', 8, __79, &__80);
        lower_texture_name = __struct__::unpack_bytes('<', 's', 8, __79, &__80);
        middle_texture_name = __struct__::unpack_bytes('<', 's', 8, __79, &__80);
        sector_nr = __struct__::unpack_int('<', 'H', 1, __79, &__80);
        upper_texture = (this->textures)->get(upper_texture_name->rstrip(const_7));
        lower_texture = (this->textures)->get(lower_texture_name->rstrip(const_7));
        middle_texture = (this->textures)->get(middle_texture_name->rstrip(const_7));
        sector = (this->sectors)->__getfast__(sector_nr);
        sidedef = (new Sidedef(offset_x, offset_y, upper_texture, lower_texture, middle_texture, sector));
        (this->sidedefs)->append(sidedef);
    END_FOR

    return NULL;
}

void *Map::extract_sectors() {
    bytes *__83, *ceil_texture, *data, *floor_texture, *pic_data;
    __ss_int _, __81, __82, __84, ceil_h, floor_h, j, light_level, special_type;
    list<bytes *> *names;
    Flat *ceil_flat, *floor_flat;
    Picture *ceil_pic;
    Sector *sector;

    this->sectors = (__ss_list<Sector *, 5>());
    data = (this->entry_data)->__getitem__(const_16);

    FAST_FOR(j,0,__floordiv(len(data),__ss_int(26LL)),1,81,82)
        __83 = data;
        __84 = __wrap(__83, (j*__ss_int(26LL)));
        floor_h = __struct__::unpack_int('<', 'h', 1, __83, &__84);
        ceil_h = __struct__::unpack_int('<', 'h', 1, __83, &__84);
        floor_texture = __struct__::unpack_bytes('<', 's', 8, __83, &__84);
        ceil_texture = __struct__::unpack_bytes('<', 's', 8, __83, &__84);
        light_level = __struct__::unpack_int('<', 'H', 1, __83, &__84);
        special_type = __struct__::unpack_int('<', 'h', 1, __83, &__84);
        _ = __struct__::unpack_int('<', 'h', 1, __83, &__84);
        light_level = ((light_level)&(__ss_int(255LL)));
        floor_texture = floor_texture->rstrip(const_7);
        if (floor_texture->startswith(const_18)) {
            names = (new list<bytes *>(3,const_19,const_20,const_21));
            floor_flat = (new Flat(list_comp_10(names, this)));
        }
        else {
            floor_flat = (new Flat((new list<bytes *>(1,(this->entry_data)->__getitem__(floor_texture)))));
        }
        ceil_texture = ceil_texture->rstrip(const_7);
        ceil_flat = (new Flat((new list<bytes *>(1,(this->entry_data)->__getitem__(ceil_texture)))));
        ceil_pic = NULL;
        if ((ceil_texture)->__contains__(const_22)) {
            pic_data = (this->entry_data)->__getitem__(ceil_texture->replace(const_23, const_24));
            ceil_pic = (new Picture(pic_data));
        }
        sector = (new Sector(floor_h, ceil_h, floor_texture, ceil_texture, light_level, special_type, floor_flat, ceil_flat, ceil_pic));
        (this->sectors)->append(sector);
    END_FOR

    return NULL;
}

void *Map::extract_patches() {
    bytes *__89, *data, *patch_name;
    __ss_int __90, __91, __92, j, n_pnames;
    Picture *patch;

    this->patches = (__ss_list<Picture *, 6>());
    data = (this->entry_data)->__getitem__(const_25);
    __89 = data;
    __90 = __wrap(__89, __ss_int(0LL));
    n_pnames = __struct__::unpack_int('<', 'i', 1, __89, &__90);

    FAST_FOR(j,0,n_pnames,1,91,92)
        patch_name = ((data->__slice__(__ss_int(3LL), (__ss_int(4LL)+(j*__ss_int(8LL))), (__ss_int(4LL)+((j+__ss_int(1LL))*__ss_int(8LL))), __ss_int(0LL)))->rstrip(const_7))->upper();
        try {
            patch = (new Picture((this->entry_data)->__getitem__(patch_name)));
        } catch (KeyError *) {
            patch = NULL;
        }
        (this->patches)->append(patch);
    END_FOR

    return NULL;
}

void *Map::extract_textures() {
    bytes *__100, *__108, *__94, *__98, *data, *name;
    __ss_int _, __101, __106, __107, __109, __110, __111, __112, __113, __95, __96, __97, __99, height, j, k, m, n, n_patches, n_textures, offset, offset_x, offset_y, patch_index, width, x, y;
    list<list<__ss_int> *> *patch;
    Picture *pic;
    __ss_bool __114, __115;
    list<__ss_int> *__116;
    dict<bytes *, Texture *> *__117;

    this->textures = (new dict<bytes *, Texture *>());
    data = (this->entry_data)->__getitem__(const_27);
    __94 = data;
    __95 = __wrap(__94, __ss_int(0LL));
    n_textures = __struct__::unpack_int('<', 'i', 1, __94, &__95);

    FAST_FOR(j,0,n_textures,1,96,97)
        __98 = data;
        __99 = __wrap(__98, (__ss_int(4LL)+(j*__ss_int(4LL))));
        offset = __struct__::unpack_int('<', 'i', 1, __98, &__99);
        __100 = data;
        __101 = __wrap(__100, offset);
        name = __struct__::unpack_bytes('<', 's', 8, __100, &__101);
        _ = __struct__::unpack_int('<', 'I', 1, __100, &__101);
        width = __struct__::unpack_int('<', 'H', 1, __100, &__101);
        height = __struct__::unpack_int('<', 'H', 1, __100, &__101);
        _ = __struct__::unpack_int('<', 'I', 1, __100, &__101);
        n_patches = __struct__::unpack_int('<', 'H', 1, __100, &__101);
        name = name->rstrip(const_7);
        patch = list_comp_12(height, width);

        FAST_FOR(k,0,n_patches,1,106,107)
            __108 = data;
            __109 = __wrap(__108, ((offset+__ss_int(22LL))+(k*__ss_int(10LL))));
            offset_x = __struct__::unpack_int('<', 'h', 1, __108, &__109);
            offset_y = __struct__::unpack_int('<', 'h', 1, __108, &__109);
            patch_index = __struct__::unpack_int('<', 'h', 1, __108, &__109);
            _ = __struct__::unpack_int('<', 'h', 1, __108, &__109);
            _ = __struct__::unpack_int('<', 'h', 1, __108, &__109);
            pic = (this->patches)->__getfast__(patch_index);

            FAST_FOR(m,0,pic->width,1,110,111)

                FAST_FOR(n,0,pic->height,1,112,113)
                    x = (m+offset_x);
                    y = (n+offset_y);
                    if (((__ss_int(0LL)<=x)&&(x<width) and (__ss_int(0LL)<=y)&&(y<height))) {
                        patch->__getfast__(x)->__setitem__(y, ((pic->data)->__getfast__(m))->__getfast__(n));
                    }
                END_FOR

            END_FOR

        END_FOR

        this->textures->__setitem__(name, (new Texture(name, patch, width, height)));
    END_FOR

    return NULL;
}

void *Map::extract_palette() {
    bytes *__120, *data;
    __ss_int __118, __119, __121, b, g, j, r;

    this->palette = (__ss_list<tuple<__ss_int> *, 7>());
    data = (this->entry_data)->__getitem__(const_8);

    FAST_FOR(j,0,__ss_int(256LL),1,118,119)
        __120 = data;
        __121 = __wrap(__120, (__ss_int(3LL)*j));
        r = __struct__::unpack_int('<', 'B', 1, __120, &__121);
        g = __struct__::unpack_int('<', 'B', 1, __120, &__121);
        b = __struct__::unpack_int('<', 'B', 1, __120, &__121);
        (this->palette)->append((new tuple<__ss_int>(3,r,g,b)));
    END_FOR

    return NULL;
}

void *Map::extract_colormaps() {
    bytes *data;
    __ss_int __122, __123, j;

    this->colormaps = (__ss_list<Colormap *, 8>());
    data = (this->entry_data)->__getitem__(const_9);

    FAST_FOR(j,0,__ss_int(34LL),1,122,123)
        (this->colormaps)->append((new Colormap(data->__slice__(__ss_int(3LL), (__ss_int(256LL)*j), (__ss_int(256LL)*(j+__ss_int(1LL))), __ss_int(0LL)))));
    END_FOR

    return NULL;
}

void *Map::extract_segs() {
    bytes *__126, *data;
    __ss_int __124, __125, __127, angle, direction, j, linedef_nr, offset, vertex_end, vertex_start;
    Vertex *vertex_a, *vertex_b;
    Linedef *linedef;
    Sidedef *sidedef_back, *sidedef_front;
    __ss_bool is_portal;
    Sector *sector_back, *sector_front;

    this->segs = (__ss_list<Seg *, 9>());
    data = (this->entry_data)->__getitem__(const_31);

    FAST_FOR(j,0,__floordiv(len(data),__ss_int(12LL)),1,124,125)
        __126 = data;
        __127 = __wrap(__126, (j*__ss_int(12LL)));
        vertex_start = __struct__::unpack_int('<', 'H', 1, __126, &__127);
        vertex_end = __struct__::unpack_int('<', 'H', 1, __126, &__127);
        angle = __struct__::unpack_int('<', 'h', 1, __126, &__127);
        linedef_nr = __struct__::unpack_int('<', 'H', 1, __126, &__127);
        direction = __struct__::unpack_int('<', 'H', 1, __126, &__127);
        offset = __struct__::unpack_int('<', 'h', 1, __126, &__127);
        vertex_a = (this->vertices)->__getfast__(vertex_start);
        vertex_b = (this->vertices)->__getfast__(vertex_end);
        linedef = (this->linedefs)->__getfast__(linedef_nr);
        sidedef_back = NULL;
        is_portal = False;
        if ((direction==__ss_int(0LL))) {
            sidedef_front = linedef->sidedef_front;
            if ((linedef->sidedef_back!=NULL)) {
                sidedef_back = linedef->sidedef_back;
                is_portal = True;
            }
        }
        else {
            sidedef_front = linedef->sidedef_back;
            if ((linedef->sidedef_front!=NULL)) {
                sidedef_back = linedef->sidedef_front;
                is_portal = True;
            }
        }
        sector_front = sidedef_front->sector;
        if ((sidedef_back!=NULL)) {
            sector_back = sidedef_back->sector;
        }
        else {
            sector_back = NULL;
        }
        (this->segs)->append((new Seg(vertex_a, vertex_b, angle, linedef, sidedef_front, sidedef_back, is_portal, offset, sector_front, sector_back)));
    END_FOR

    return NULL;
}

void *Map::extract_subsectors() {
    bytes *__130, *data;
    __ss_int __128, __129, __131, first_seg, j, seg_count;
    list<Seg *> *segs;

    this->subsectors = (__ss_list<SubSector *, 10>());
    data = (this->entry_data)->__getitem__(const_33);

    FAST_FOR(j,0,__floordiv(len(data),__ss_int(4LL)),1,128,129)
        __130 = data;
        __131 = __wrap(__130, (j*__ss_int(4LL)));
        seg_count = __struct__::unpack_int('<', 'H', 1, __130, &__131);
        first_seg = __struct__::unpack_int('<', 'H', 1, __130, &__131);
        segs = (this->segs)->__slice__(__ss_int(3LL), first_seg, (first_seg+seg_count), __ss_int(0LL));
        (this->subsectors)->append((new SubSector(segs)));
    END_FOR

    return NULL;
}

void *Map::extract_bspnodes() {
    bytes *__134, *data;
    __ss_int _, __132, __133, __135, change_partition_x, change_partition_y, j, lchild_id, partition_x, partition_y, rchild_id;
    BSPNode *bspnode;

    this->bspnodes = (__ss_list<BSPNode *, 11>());
    data = (this->entry_data)->__getitem__(const_35);

    FAST_FOR(j,0,__floordiv(len(data),__ss_int(28LL)),1,132,133)
        __134 = data;
        __135 = __wrap(__134, (j*__ss_int(28LL)));
        partition_x = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        partition_y = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        change_partition_x = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        change_partition_y = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        _ = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        _ = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        _ = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        _ = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        _ = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        _ = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        _ = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        _ = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        rchild_id = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        lchild_id = __struct__::unpack_int('<', 'h', 1, __134, &__135);
        bspnode = (new BSPNode(partition_x, partition_y, change_partition_x, change_partition_y, rchild_id, lchild_id));
        (this->bspnodes)->append(bspnode);
    END_FOR

    return NULL;
}

void *Map::extract_things() {
    bytes *__138, *data;
    __ss_int _, __136, __137, __139, angle, j, type_, x, y;

    this->things = (__ss_list<Thing *, 12>());
    data = (this->entry_data)->__getitem__(const_37);

    FAST_FOR(j,0,__floordiv(len(data),__ss_int(10LL)),1,136,137)
        __138 = data;
        __139 = __wrap(__138, (j*__ss_int(10LL)));
        x = __struct__::unpack_int('<', 'h', 1, __138, &__139);
        y = __struct__::unpack_int('<', 'h', 1, __138, &__139);
        angle = __struct__::unpack_int('<', 'h', 1, __138, &__139);
        type_ = __struct__::unpack_int('<', 'h', 1, __138, &__139);
        _ = __struct__::unpack_int('<', 'h', 1, __138, &__139);
        (this->things)->append((new Thing(x, y, angle, type_)));
    END_FOR

    return NULL;
}

/**
class ClipBufferNode
*/

class_ *cl_ClipBufferNode;

void *ClipBufferNode::__init__(__ss_int start, __ss_int end) {
    this->start = start;
    this->end = end;
    this->occluded = False;
    this->left = NULL;
    this->right = NULL;
    this->partitioned = False;
    return NULL;
}

void *ClipBufferNode::checkSpan(__ss_int start, __ss_int end, list<__ss_int> *result, __ss_bool add) {
    __ss_bool __140, __141, __142, __143, __144, __145, __146, __147, __148, __149, __150, __151, __152, __153, __154, __155, __156, __157;

    if ((this->occluded and (start>=this->start) and (end<=this->end))) {
        return NULL;
    }
    if (((start>this->end) or (end<this->start))) {
        return NULL;
    }
    if ((start<=this->start)) {
        start = this->start;
    }
    if ((end>=this->end)) {
        end = this->end;
    }
    if (add) {
        if ((__NOT(this->occluded) and __NOT(this->partitioned) and (start<=this->start) and (end>=this->end))) {
            result->append(start);
            result->append(end);
            this->occluded = True;
            return NULL;
        }
        if (__NOT(this->partitioned)) {
            if ((start==this->start)) {
                this->partitionPoint = end;
            }
            else {
                this->partitionPoint = (start-__ss_int(1LL));
            }
            this->left = (new ClipBufferNode(this->start, this->partitionPoint));
            this->right = (new ClipBufferNode((this->partitionPoint+__ss_int(1LL)), this->end));
            this->partitioned = True;
        }
    }
    else if (__NOT(this->partitioned)) {
        result->append(start);
        result->append(end);
        return NULL;
    }
    if (((start<=this->partitionPoint) and (end<=this->partitionPoint))) {
        (this->left)->checkSpan(start, end, result, add);
    }
    else if (((start<=this->partitionPoint) and (end>this->partitionPoint))) {
        (this->left)->checkSpan(start, this->partitionPoint, result, add);
        (this->right)->checkSpan((this->partitionPoint+__ss_int(1LL)), end, result, add);
    }
    else if (((start>this->partitionPoint) and (end>this->partitionPoint))) {
        (this->right)->checkSpan(start, end, result, add);
    }
    if ((add and (this->left)->occluded and (this->right)->occluded)) {
        this->occluded = True;
    }
    return 0;
}

__ss_int get_special_light(Sector *sector, __ss_int frame_count) {
    __ss_int __158, __159, __160, special_type;

    special_type = sector->special_type;
    if ((__eq(__158=special_type,__ss_int(1LL)) || __eq(__158,__ss_int(17LL)))) {
        if ((sector->_random)->__getfast__((((frame_count)&(__ss_int(4080LL)))>>__ss_int(4LL)))) {
            return __ss_int(10LL);
        }
    }
    else if ((__eq(__159=special_type,__ss_int(2LL)) || __eq(__159,__ss_int(12LL)))) {
        if ((__mods(frame_count, __ss_int(120LL))<__ss_int(60LL))) {
            return __ss_int(10LL);
        }
    }
    else if ((__eq(__160=special_type,__ss_int(3LL)) || __eq(__160,__ss_int(13LL)))) {
        if ((__mods(frame_count, __ss_int(240LL))<__ss_int(120LL))) {
            return __ss_int(10LL);
        }
    }
    else if ((special_type==__ss_int(8LL))) {
        return __doom__::OSCILLATION->__getfast__(((frame_count)&(__ss_int(255LL))));
    }
    return __ss_int(0LL);
}

Colormap *get_wall_colormap(list<Colormap *> *colormaps, __ss_float currentZ, Seg *seg, __ss_int frame_count) {
    Sector *sector;
    __ss_int colorMapIndex;

    sector = seg->sector_front;
    colorMapIndex = __int(((currentZ-__ss_int(5LL))*__ss_float(0.05)));
    colorMapIndex = ___min(2, __ss_void, __ss_int(0LL), colorMapIndex, (__ss_int(32LL)-(sector->light_level>>__ss_int(3LL))));
    colorMapIndex = (colorMapIndex+__floordiv(((((((seg->angle+__ss_int(8192LL)))&(__ss_int(32767LL)))-__ss_int(16384LL)))&(__ss_int(32767LL))),__ss_int(3200LL)));
    colorMapIndex = (colorMapIndex+get_special_light(sector, frame_count));
    colorMapIndex = ___max(2, __ss_void, __ss_int(0LL), ___min(2, __ss_void, __ss_int(0LL), colorMapIndex, __ss_int(31LL)), __ss_int(0LL));
    return colormaps->__getfast__(colorMapIndex);
}

Colormap *get_flat_colormap(list<Colormap *> *colormaps, __ss_float currentZ, Seg *seg, __ss_int frame_count) {
    Sector *sector;
    __ss_int colorMapIndex;

    sector = seg->sector_front;
    colorMapIndex = __int(((currentZ-__ss_int(5LL))*__ss_float(0.05)));
    colorMapIndex = ___min(2, __ss_void, __ss_int(0LL), colorMapIndex, (__ss_int(32LL)-(sector->light_level>>__ss_int(3LL))));
    colorMapIndex = (colorMapIndex+get_special_light(sector, frame_count));
    colorMapIndex = ___max(2, __ss_void, __ss_int(0LL), ___min(2, __ss_void, __ss_int(0LL), colorMapIndex, __ss_int(31LL)), __ss_int(0LL));
    return colormaps->__getfast__(colorMapIndex);
}

void *draw_wall_col(bytes *drawsurf, __ss_int x, __ss_int middleMinY, __ss_int middleMaxY, Texture *wallTexture, __ss_float currentTextureX, __ss_float currentZ, __ss_float middleTextureY, __ss_float middleTextureYStep, Colormap *colormap) {
    __ss_int __161, __162, height, tx, ty, width, y;
    list<list<__ss_int> *> *wallTextureData;

    width = wallTexture->width;
    height = wallTexture->height;
    wallTextureData = wallTexture->data;
    tx = __mods(__int((currentTextureX*currentZ)), width);

    FAST_FOR(y,middleMinY,middleMaxY,1,161,162)
        ty = __mods(__int(middleTextureY), height);
        drawsurf->__setitem__(((y*__doom__::WIDTH)+x), (colormap->data)->__getfast__((wallTextureData->__getfast__(tx))->__getfast__(ty)));
        middleTextureY = (middleTextureY+middleTextureYStep);
    END_FOR

    return NULL;
}

void *draw_flat_col(bytes *drawsurf, __ss_int x, __ss_int ceilMin, __ss_int ceilMax, Seg *seg, Player *player, list<list<__ss_int> *> *flatTexture, __ss_int flat_h, list<__ss_float> *INV, __ss_int sign, list<Colormap *> *colormaps, __ss_int frame_count) {
    __ss_int __163, __164, tx, ty, y;
    __ss_float dx, dy, lateralLength, leftX, leftY, px, py, rightX, rightY, z;
    Colormap *colormap;
    Vec2 *playerDir;


    FAST_FOR(y,ceilMin,ceilMax,1,163,164)
        z = (((sign*__doom__::WIDTH_2)*((-flat_h)+player->z))*INV->__getfast__(y));
        colormap = get_flat_colormap(colormaps, z, seg, frame_count);
        playerDir = player->direction;
        px = ((playerDir->x*z)+player->x);
        py = ((playerDir->y*z)+player->y);
        lateralLength = (__doom__::TAN_45_DEG*z);
        leftX = (((-playerDir->y)*lateralLength)+px);
        leftY = ((playerDir->x*lateralLength)+py);
        rightX = ((playerDir->y*lateralLength)+px);
        rightY = (((-playerDir->x)*lateralLength)+py);
        dx = ((rightX-leftX)*__doom__::HEIGHT_INV);
        dy = ((rightY-leftY)*__doom__::HEIGHT_INV);
        tx = ((__int((leftX+(dx*x))))&(__ss_int(63LL)));
        ty = ((__int((leftY+(dy*x))))&(__ss_int(63LL)));
        drawsurf->__setitem__(((y*__doom__::WIDTH)+x), (colormap->data)->__getfast__((flatTexture->__getfast__(tx))->__getfast__(ty)));
    END_FOR

    return NULL;
}

void *draw_sky_col(bytes *drawsurf, __ss_int x, __ss_int upperMinY, __ss_int upperMaxY, Seg *seg, Player *player) {
    Picture *ceil_pic;
    __ss_int __165, __166, ceilingTextureHeight, ceilingTextureWidth, tx, ty, y;
    list<list<__ss_int> *> *ceilTextureData;
    __ss_float dx, dy, normPlayerAngle, textureOffsetX;

    ceil_pic = (seg->sector_front)->ceil_pic;
    ceilingTextureWidth = ceil_pic->width;
    ceilingTextureHeight = ceil_pic->height;
    ceilTextureData = ceil_pic->data;
    normPlayerAngle = __mods(player->angle, (__ss_int(2LL)*__math__::pi));
    if ((normPlayerAngle<((__ss_float)(__ss_int(0LL))))) {
        normPlayerAngle = (normPlayerAngle+(__ss_int(2LL)*__math__::pi));
    }
    textureOffsetX = (ceilingTextureWidth*__divs(normPlayerAngle, (__math__::pi*__ss_float(0.5))));
    dx = __divs(ceilingTextureWidth, __doom__::WIDTH);
    dy = __divs(ceilingTextureHeight, __floordiv(__doom__::WIDTH,__ss_int(2LL)));

    FAST_FOR(y,upperMinY,upperMaxY,1,165,166)
        tx = __mods(__int(((dx*x)-textureOffsetX)), ceilingTextureWidth);
        ty = __mods(__int((y*dy)), ceilingTextureHeight);
        drawsurf->__setitem__(((y*__doom__::WIDTH)+x), (ceilTextureData->__getfast__(tx))->__getfast__(ty));
    END_FOR

    return NULL;
}

void *draw_seg(Seg *seg, Map *map_, bytes *drawsurf, __ss_int scrXA, __ss_int scrXB, ClipBufferNode *cbuffer, __ss_float za, __ss_float zb, __ss_float textureX0, __ss_float textureX1, Sidedef *frontSidedef, list<__ss_int> *lowerOcclusion, list<__ss_int> *upperOcclusion, __ss_int frame_count) {
    list<__ss_int> *cbufferResult;
    Player *player;
    list<Colormap *> *colormaps;
    Sector *sector_back, *sector_front;
    __ss_float backCeil, backFloor, currentLowerCeil, currentLowerFloor, currentMiddleCeil, currentMiddleFloor, currentTextureX, currentUpperCeil, currentUpperFloor, currentZ, currentZInv, dxInv, frontCeil, frontFloor, lowerCeilStep, lowerTextureY, lowerTextureYStep, lowerfloorStep, middleCeilStep, middleTextureY, middleTextureYStep, middlefloorStep, scrYABackCeil, scrYABackFloor, scrYAFrontCeil, scrYAFrontFloor, scrYBBackCeil, scrYBBackFloor, scrYBFrontCeil, scrYBFrontFloor, textureXStep, upperCeilStep, upperFloorStep, upperTextureY, upperTextureYStep, zInvStep;
    __ss_bool __171, __172, __173, __174, hasLowerWall, hasUpperWall;
    __ss_int __167, __168, __169, __170, ceilMax, ceilMin, clip, clipLeft, clipRight, dif, lowerDy, lowerMaxY, lowerMinY, middleDy, middleMaxY, middleMinY, scrLeft, scrRight, upperDy, upperMaxY, upperMinY, x;
    Colormap *colormap;
    Texture *lower_texture, *middle_texture, *upper_texture;
    list<list<__ss_int> *> *ceil_flat, *floor_flat;

    cbufferResult = (__ss_list<__ss_int, 13>());
    cbuffer->checkSpan(scrXA, scrXB, cbufferResult, __NOT(seg->is_portal));
    if (__NOT(___bool(cbufferResult))) {
        return NULL;
    }
    player = map_->player;
    colormaps = map_->colormaps;
    sector_front = seg->sector_front;
    sector_back = seg->sector_back;
    frontCeil = (sector_front->ceil_h-player->z);
    frontFloor = (sector_front->floor_h-player->z);
    scrYAFrontCeil = ((__doom__::WIDTH_2*__divs(frontCeil, (-za)))+__doom__::HEIGHT_2);
    scrYAFrontFloor = ((__doom__::WIDTH_2*__divs(frontFloor, (-za)))+__doom__::HEIGHT_2);
    scrYBFrontCeil = ((__doom__::WIDTH_2*__divs(frontCeil, (-zb)))+__doom__::HEIGHT_2);
    scrYBFrontFloor = ((__doom__::WIDTH_2*__divs(frontFloor, (-zb)))+__doom__::HEIGHT_2);
    if (seg->is_portal) {
        backCeil = (sector_back->ceil_h-player->z);
        backFloor = (sector_back->floor_h-player->z);
        scrYABackCeil = ((__doom__::WIDTH_2*__divs(backCeil, (-za)))+__doom__::HEIGHT_2);
        scrYABackFloor = ((__doom__::WIDTH_2*__divs(backFloor, (-za)))+__doom__::HEIGHT_2);
        scrYBBackCeil = ((__doom__::WIDTH_2*__divs(backCeil, (-zb)))+__doom__::HEIGHT_2);
        scrYBBackFloor = ((__doom__::WIDTH_2*__divs(backFloor, (-zb)))+__doom__::HEIGHT_2);
        hasLowerWall = ___bool((backFloor>frontFloor));
        hasUpperWall = ___bool((backCeil<frontCeil));
    }
    else {
        backCeil = ((__ss_float)(__ss_int(0LL)));
        backFloor = ((__ss_float)(__ss_int(0LL)));
        scrYABackCeil = ((__ss_float)(__ss_int(0LL)));
        scrYABackFloor = ((__ss_float)(__ss_int(0LL)));
        scrYBBackCeil = ((__ss_float)(__ss_int(0LL)));
        scrYBBackFloor = ((__ss_float)(__ss_int(0LL)));
        hasLowerWall = False;
        hasUpperWall = False;
    }
    dxInv = __divs(__ss_float(1.0), (scrXB-scrXA));
    zInvStep = ((__divs(__ss_int(1LL), zb)-__divs(__ss_int(1LL), za))*dxInv);
    textureXStep = ((__divs(textureX1, zb)-__divs(textureX0, za))*dxInv);
    middleCeilStep = ((scrYBFrontCeil-scrYAFrontCeil)*dxInv);
    middlefloorStep = ((scrYBFrontFloor-scrYAFrontFloor)*dxInv);
    lowerCeilStep = ((scrYBBackFloor-scrYABackFloor)*dxInv);
    lowerfloorStep = ((scrYBFrontFloor-scrYAFrontFloor)*dxInv);
    upperCeilStep = ((scrYBFrontCeil-scrYAFrontCeil)*dxInv);
    upperFloorStep = ((scrYBBackCeil-scrYABackCeil)*dxInv);

    FAST_FOR(clip,__ss_int(0LL),len(cbufferResult),__ss_int(2LL),167,168)
        clipLeft = cbufferResult->__getfast__(clip);
        clipRight = cbufferResult->__getfast__((clip+__ss_int(1LL)));
        currentMiddleCeil = scrYAFrontCeil;
        currentMiddleFloor = scrYAFrontFloor;
        currentLowerCeil = scrYABackFloor;
        currentLowerFloor = scrYAFrontFloor;
        currentUpperCeil = scrYAFrontCeil;
        currentUpperFloor = scrYABackCeil;
        currentZInv = __divs(__ss_int(1LL), za);
        currentTextureX = __divs(textureX0, za);
        scrLeft = scrXA;
        scrRight = scrXB;
        if ((scrLeft<clipLeft)) {
            dif = (clipLeft-scrXA);
            currentTextureX = (currentTextureX+(dif*textureXStep));
            currentZInv = (currentZInv+(dif*zInvStep));
            currentMiddleCeil = (currentMiddleCeil+(dif*middleCeilStep));
            currentMiddleFloor = (currentMiddleFloor+(dif*middlefloorStep));
            if (hasLowerWall) {
                currentLowerCeil = (currentLowerCeil+(dif*lowerCeilStep));
                currentLowerFloor = (currentLowerFloor+(dif*lowerfloorStep));
            }
            if (hasUpperWall) {
                currentUpperCeil = (currentUpperCeil+(dif*upperCeilStep));
                currentUpperFloor = (currentUpperFloor+(dif*upperFloorStep));
            }
            scrLeft = clipLeft;
        }
        if ((scrRight>clipRight)) {
            scrRight = clipRight;
        }

        FAST_FOR(x,scrLeft,(scrRight+__ss_int(1LL)),1,169,170)
            currentZ = __divs(__ss_float(1.0), currentZInv);
            colormap = get_wall_colormap(colormaps, currentZ, seg, frame_count);
            middleMaxY = __int(currentMiddleFloor);
            middleMinY = __int(currentMiddleCeil);
            middleDy = (middleMaxY-middleMinY);
            if ((middleDy==__ss_int(0LL))) {
                middleTextureYStep = ((__ss_float)(__ss_int(0LL)));
            }
            else {
                middleTextureYStep = __divs((frontCeil-frontFloor), middleDy);
            }
            middleTextureY = ((__ss_float)(frontSidedef->offset_y));
            if ((middleMinY<lowerOcclusion->__getfast__(x))) {
                dif = (lowerOcclusion->__getfast__(x)-middleMinY);
                middleTextureY = ((dif*middleTextureYStep)+frontSidedef->offset_y);
                middleMinY = lowerOcclusion->__getfast__(x);
            }
            middleMaxY = ___min(2, __ss_void, __ss_int(0LL), middleMaxY, upperOcclusion->__getfast__(x));
            middle_texture = frontSidedef->middle_texture;
            if ((__NOT(seg->is_portal) and (middle_texture!=NULL))) {
                draw_wall_col(drawsurf, x, middleMinY, middleMaxY, middle_texture, currentTextureX, currentZ, middleTextureY, middleTextureYStep, colormap);
            }
            ceilMin = __int(___max(2, __ss_void, __ss_int(0LL), lowerOcclusion->__getfast__(x), middleMaxY));
            if ((ceilMin<upperOcclusion->__getfast__(x))) {
                floor_flat = (sector_front->floor_flat)->get_data(frame_count);
                draw_flat_col(drawsurf, x, ceilMin, upperOcclusion->__getfast__(x), seg, player, floor_flat, sector_front->floor_h, __doom__::FLOOR_Y_INV, __ss_int(1LL), colormaps, frame_count);
                upperOcclusion->__setitem__(x, ceilMin);
            }
            if (hasLowerWall) {
                lowerMaxY = __int(currentLowerFloor);
                lowerMinY = __int(currentLowerCeil);
                lowerDy = (lowerMaxY-lowerMinY);
                lowerTextureYStep = __divs((backFloor-frontFloor), lowerDy);
                lowerTextureY = ((__ss_float)(frontSidedef->offset_y));
                if ((lowerMinY<lowerOcclusion->__getfast__(x))) {
                    dif = (lowerOcclusion->__getfast__(x)-lowerMinY);
                    lowerTextureY = ((dif*lowerTextureYStep)+frontSidedef->offset_y);
                    lowerMinY = lowerOcclusion->__getfast__(x);
                }
                lowerMaxY = ___min(2, __ss_void, __ss_int(0LL), lowerMaxY, upperOcclusion->__getfast__(x));
                lower_texture = frontSidedef->lower_texture;
                if ((lower_texture!=NULL)) {
                    draw_wall_col(drawsurf, x, lowerMinY, lowerMaxY, lower_texture, currentTextureX, currentZ, lowerTextureY, lowerTextureYStep, colormap);
                }
                if ((lowerMinY<upperOcclusion->__getfast__(x))) {
                    upperOcclusion->__setitem__(x, lowerMinY);
                }
                currentLowerCeil = (currentLowerCeil+lowerCeilStep);
                currentLowerFloor = (currentLowerFloor+lowerfloorStep);
            }
            ceilMax = __int(___min(2, __ss_void, __ss_int(0LL), upperOcclusion->__getfast__(x), middleMinY));
            if ((ceilMax>lowerOcclusion->__getfast__(x))) {
                if ((sector_front->ceil_pic!=NULL)) {
                    draw_sky_col(drawsurf, x, lowerOcclusion->__getfast__(x), ceilMax, seg, player);
                }
                else {
                    ceil_flat = (sector_front->ceil_flat)->get_data(frame_count);
                    draw_flat_col(drawsurf, x, lowerOcclusion->__getfast__(x), ceilMax, seg, player, ceil_flat, sector_front->ceil_h, __doom__::CEIL_Y_INV, (-__ss_int(1LL)), colormaps, frame_count);
                }
                lowerOcclusion->__setitem__(x, middleMinY);
            }
            if (hasUpperWall) {
                upperMaxY = __int(currentUpperFloor);
                upperMinY = __int(currentUpperCeil);
                upperDy = (upperMaxY-upperMinY);
                upperTextureYStep = __divs((frontCeil-backCeil), upperDy);
                upperTextureY = ((__ss_float)(frontSidedef->offset_y));
                if ((upperMinY<lowerOcclusion->__getfast__(x))) {
                    dif = (lowerOcclusion->__getfast__(x)-upperMinY);
                    upperTextureY = ((dif*upperTextureYStep)+frontSidedef->offset_y);
                    upperMinY = lowerOcclusion->__getfast__(x);
                }
                upperMaxY = ___min(2, __ss_void, __ss_int(0LL), upperMaxY, upperOcclusion->__getfast__(x));
                upper_texture = frontSidedef->upper_texture;
                if ((frontSidedef->skyhack or (upper_texture==NULL))) {
                    if ((sector_front->ceil_pic!=NULL)) {
                        draw_sky_col(drawsurf, x, upperMinY, upperMaxY, seg, player);
                    }
                }
                else {
                    draw_wall_col(drawsurf, x, upperMinY, upperMaxY, upper_texture, currentTextureX, currentZ, upperTextureY, upperTextureYStep, colormap);
                }
                if ((upperMaxY>lowerOcclusion->__getfast__(x))) {
                    lowerOcclusion->__setitem__(x, upperMaxY);
                }
                currentUpperCeil = (currentUpperCeil+upperCeilStep);
                currentUpperFloor = (currentUpperFloor+upperFloorStep);
            }
            currentMiddleCeil = (currentMiddleCeil+middleCeilStep);
            currentMiddleFloor = (currentMiddleFloor+middlefloorStep);
            currentZInv = (currentZInv+zInvStep);
            currentTextureX = (currentTextureX+textureXStep);
        END_FOR

    END_FOR

    return 0;
}

bytes *render(Map *map_, __ss_int frame_count) {
    bytes *drawsurf;
    list<__ss_int> *lowerOcclusion, *upperOcclusion;
    ClipBufferNode *cbuffer;
    list<SubSector *> *__175, *subsectors;
    Player *player;
    SubSector *subsector;
    Seg *seg;
    Vertex *pa, *pb;
    Vec2 *v0, *v1, *v2, *v3;
    __ss_float p, textureX0, textureX1, xa, xb, za, zb;
    Sidedef *frontSidedef;
    __ss_int __177, __181, scrXA, scrXB;
    __iter<SubSector *> *__176;
    list<SubSector *>::for_in_loop __178;
    list<Seg *> *__179;
    __iter<Seg *> *__180;
    list<Seg *>::for_in_loop __182;
    __ss_bool __183, __184;

    drawsurf = __bytearray((__doom__::WIDTH*__doom__::HEIGHT));
    lowerOcclusion = __mul2(__doom__::WIDTH, (new list<__ss_int>(1,__ss_int(0LL))));
    upperOcclusion = __mul2(__doom__::WIDTH, (new list<__ss_int>(1,__doom__::HEIGHT)));
    cbuffer = (new ClipBufferNode(__ss_int(0LL), (__doom__::WIDTH-__ss_int(1LL))));
    subsectors = ((map_->bspnodes)->__getfast__((-__ss_int(1LL))))->visit(map_, NULL);
    player = map_->player;
    player->floor_h = ((__ss_float)(((((subsectors->__getfast__(__ss_int(0LL)))->segs)->__getfast__(__ss_int(0LL)))->sector_front)->floor_h));

    FOR_IN(subsector,subsectors,175,177,178)
        if (cbuffer->occluded) {
            break;
        }

        FOR_IN(seg,subsector->segs,179,181,182)
            if (cbuffer->occluded) {
                break;
            }
            pa = seg->vertex_start;
            pb = seg->vertex_end;
            v0 = (new Vec2((pa->x-player->x), (pa->y-player->y)));
            v1 = (new Vec2((pb->x-player->x), (pb->y-player->y)));
            v2 = (new Vec2((player->direction)->x, (player->direction)->y));
            za = v2->dot(v0);
            zb = v2->dot(v1);
            v3 = (new Vec2((-v2->y), v2->x));
            xa = v3->dot(v0);
            xb = v3->dot(v1);
            if (__NOT(((za<=__ss_float(0.1)) and (zb<=__ss_float(0.1))))) {
                frontSidedef = seg->sidedef_front;
                textureX0 = ((__ss_float)((seg->offset+frontSidedef->offset_x)));
                textureX1 = ((seg->offset+seg->length)+frontSidedef->offset_x);
                if ((za<=__ss_float(0.1))) {
                    p = __divs((zb-__ss_float(0.1)), (zb-za));
                    xa = (xb+(p*(xa-xb)));
                    textureX0 = (textureX1+(p*(textureX0-textureX1)));
                    za = __ss_float(0.1);
                }
                else if ((zb<=__ss_float(0.1))) {
                    p = __divs((za-__ss_float(0.1)), (za-zb));
                    xb = (xa+(p*(xb-xa)));
                    textureX1 = (textureX0+(p*(textureX1-textureX0)));
                    zb = __ss_float(0.1);
                }
                scrXA = (__int(__divs((__doom__::WIDTH_2*xa), (-za)))+__doom__::WIDTH_2);
                scrXB = (__int(__divs((__doom__::WIDTH_2*xb), (-zb)))+__doom__::WIDTH_2);
                if ((scrXA<scrXB)) {
                    draw_seg(seg, map_, drawsurf, scrXA, scrXB, cbuffer, za, zb, textureX0, textureX1, frontSidedef, lowerOcclusion, upperOcclusion, frame_count);
                }
            }
        END_FOR

    END_FOR

    return drawsurf;
}

void __init() {
    __name__ = new str("doom");

    const_0 = new str("<HHhh");
    const_1 = new str("<H");
    const_2 = new str("<B");
    const_3 = new str("<BB");
    const_4 = new str("rb");
    const_5 = new str("<II");
    const_6 = new str("<II8s");
    const_7 = __byte_cache[0];
    const_8 = new bytes("PLAYPAL");
    const_9 = new bytes("COLORMAP");
    const_10 = new bytes("VERTEXES");
    const_11 = new str("<hh");
    const_12 = new bytes("LINEDEFS");
    const_13 = new str("<HHHHHHH");
    const_14 = new bytes("SIDEDEFS");
    const_15 = new str("<HH8s8s8sH");
    const_16 = new bytes("SECTORS");
    const_17 = new str("<hh8s8sHhh");
    const_18 = new bytes("NUKAGE");
    const_19 = new bytes("NUKAGE1");
    const_20 = new bytes("NUKAGE2");
    const_21 = new bytes("NUKAGE3");
    const_22 = new bytes("F_SKY");
    const_23 = new bytes("F_");
    const_24 = new bytes("");
    const_25 = new bytes("PNAMES");
    const_26 = new str("<i");
    const_27 = new bytes("TEXTURE1");
    const_28 = new str("<8sIHHIH");
    const_29 = new str("<hhhhh");
    const_30 = new str("<BBB");
    const_31 = new bytes("SEGS");
    const_32 = new str("<HHhHHh");
    const_33 = new bytes("SSECTORS");
    const_34 = new str("<HH");
    const_35 = new bytes("NODES");
    const_36 = new str("<hhhhhhhhhhhhhh");
    const_37 = new bytes("THINGS");
    const_38 = new str("__main__");
    const_39 = new str("DOOM1.WAD");
    const_40 = new str("E1M1");

    WIDTH = __ss_int(800LL);
    HEIGHT = __ss_int(600LL);
    WIDTH_2 = __floordiv(__doom__::WIDTH,__ss_int(2LL));
    HEIGHT_2 = __floordiv(__doom__::HEIGHT,__ss_int(2LL));
    HEIGHT_INV = __divs(__ss_float(1.0), __doom__::WIDTH);
    TAN_45_DEG = __math__::tan(__math__::radians(__ss_int(45LL)));
    FLOOR_Y_INV = list_comp_0();
    CEIL_Y_INV = list_comp_1();
    OSCILLATION = list_comp_2();
    cl_Vertex = new class_("Vertex");
    cl_Sidedef = new class_("Sidedef");
    cl_Linedef = new class_("Linedef");
    cl_Sector = new class_("Sector");
    cl_SubSector = new class_("SubSector");
    cl_Seg = new class_("Seg");
    cl_Flat = new class_("Flat");
    default_0 = NULL;
    cl_BSPNode = new class_("BSPNode");
    cl_Thing = new class_("Thing");
    cl_Player = new class_("Player");
    cl_Texture = new class_("Texture");
    cl_Picture = new class_("Picture");
    cl_Colormap = new class_("Colormap");
    cl_Vec2 = new class_("Vec2");
    cl_Map = new class_("Map");
    cl_ClipBufferNode = new class_("ClipBufferNode");
    if (__eq(__doom__::__name__, const_38)) {
        map_ = (new Map(const_39, const_40));
        (__doom__::map_->player)->update();
        render(__doom__::map_, __ss_int(0LL));
    }
}

} // module namespace

/* extension module glue */

extern "C" {
#include <Python.h>
#include "math/__init__.hpp"
#include "random.hpp"
#include "struct.hpp"
#include "time.hpp"
#include "doom.hpp"
#include <structmember.h>
#include "math/__init__.hpp"
#include "random.hpp"
#include "struct.hpp"
#include "time.hpp"
#include "doom.hpp"

PyObject *__ss_mod_doom;

namespace __doom__ {

/* class Vertex */

typedef struct {
    PyObject_HEAD
    __doom__::Vertex *__ss_object;
} __ss_doom_VertexObject;

static PyMemberDef __ss_doom_VertexMembers[] = {
    {NULL}
};

PyObject *__ss_doom_Vertex___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_int arg_0 = __ss_arg<__ss_int >("x", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("y", 1, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_VertexObject *)self)->__ss_object->__init__(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Vertex_as_number = {
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

PyObject *__ss_doom_Vertex__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Vertex__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_VertexMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Vertex__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Vertex__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Vertex___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Vertex___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Vertex___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_VertexNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_VertexObject *self = (__ss_doom_VertexObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Vertex();
    self->__ss_object->__class__ = __doom__::cl_Vertex;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_VertexDealloc(__ss_doom_VertexObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Vertex_x(__ss_doom_VertexObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->x);
}

int __ss_set___ss_doom_Vertex_x(__ss_doom_VertexObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->x = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Vertex_y(__ss_doom_VertexObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->y);
}

int __ss_set___ss_doom_Vertex_y(__ss_doom_VertexObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->y = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_VertexGetSet[] = {
    {(char *)"x", (getter)__ss_get___ss_doom_Vertex_x, (setter)__ss_set___ss_doom_Vertex_x, (char *)"", NULL},
    {(char *)"y", (getter)__ss_get___ss_doom_Vertex_y, (setter)__ss_set___ss_doom_Vertex_y, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_VertexObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Vertex",
    sizeof( __ss_doom_VertexObject),
    0,
    (destructor) __ss_doom_VertexDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Vertex_as_number,
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
    __ss_doom_VertexMethods,
    __ss_doom_VertexMembers,
    __ss_doom_VertexGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Vertex___tpinit__,
    0,
    __ss_doom_VertexNew,
};

PyObject *__ss_doom_Vertex__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_VertexObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_VertexObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "x", __to_py(((__ss_doom_VertexObject *)self)->__ss_object->x));
    __ss_dict_steal(b, "y", __to_py(((__ss_doom_VertexObject *)self)->__ss_object->y));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Vertex__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "x");
    if (value) ((__ss_doom_VertexObject *)self)->__ss_object->x = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "y");
    if (value) ((__ss_doom_VertexObject *)self)->__ss_object->y = __to_ss<__ss_int >(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class Sidedef */

typedef struct {
    PyObject_HEAD
    __doom__::Sidedef *__ss_object;
} __ss_doom_SidedefObject;

static PyMemberDef __ss_doom_SidedefMembers[] = {
    {NULL}
};

PyObject *__ss_doom_Sidedef___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_int arg_0 = __ss_arg<__ss_int >("offset_x", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("offset_y", 1, 0, 0, args, kwargs);
        Texture *arg_2 = __ss_arg<Texture *>("upper_texture", 2, 0, 0, args, kwargs);
        Texture *arg_3 = __ss_arg<Texture *>("lower_texture", 3, 0, 0, args, kwargs);
        Texture *arg_4 = __ss_arg<Texture *>("middle_texture", 4, 0, 0, args, kwargs);
        Sector *arg_5 = __ss_arg<Sector *>("sector", 5, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_SidedefObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2, arg_3, arg_4, arg_5));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Sidedef_as_number = {
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

PyObject *__ss_doom_Sidedef__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Sidedef__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_SidedefMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Sidedef__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Sidedef__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Sidedef___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Sidedef___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Sidedef___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_SidedefNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_SidedefObject *self = (__ss_doom_SidedefObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Sidedef();
    self->__ss_object->__class__ = __doom__::cl_Sidedef;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_SidedefDealloc(__ss_doom_SidedefObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Sidedef_lower_texture(__ss_doom_SidedefObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->lower_texture);
}

int __ss_set___ss_doom_Sidedef_lower_texture(__ss_doom_SidedefObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->lower_texture = __to_ss<Texture *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sidedef_middle_texture(__ss_doom_SidedefObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->middle_texture);
}

int __ss_set___ss_doom_Sidedef_middle_texture(__ss_doom_SidedefObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->middle_texture = __to_ss<Texture *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sidedef_offset_x(__ss_doom_SidedefObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->offset_x);
}

int __ss_set___ss_doom_Sidedef_offset_x(__ss_doom_SidedefObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->offset_x = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sidedef_offset_y(__ss_doom_SidedefObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->offset_y);
}

int __ss_set___ss_doom_Sidedef_offset_y(__ss_doom_SidedefObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->offset_y = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sidedef_sector(__ss_doom_SidedefObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->sector);
}

int __ss_set___ss_doom_Sidedef_sector(__ss_doom_SidedefObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->sector = __to_ss<Sector *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sidedef_skyhack(__ss_doom_SidedefObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->skyhack);
}

int __ss_set___ss_doom_Sidedef_skyhack(__ss_doom_SidedefObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->skyhack = __to_ss<__ss_bool >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sidedef_upper_texture(__ss_doom_SidedefObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->upper_texture);
}

int __ss_set___ss_doom_Sidedef_upper_texture(__ss_doom_SidedefObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->upper_texture = __to_ss<Texture *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_SidedefGetSet[] = {
    {(char *)"lower_texture", (getter)__ss_get___ss_doom_Sidedef_lower_texture, (setter)__ss_set___ss_doom_Sidedef_lower_texture, (char *)"", NULL},
    {(char *)"middle_texture", (getter)__ss_get___ss_doom_Sidedef_middle_texture, (setter)__ss_set___ss_doom_Sidedef_middle_texture, (char *)"", NULL},
    {(char *)"offset_x", (getter)__ss_get___ss_doom_Sidedef_offset_x, (setter)__ss_set___ss_doom_Sidedef_offset_x, (char *)"", NULL},
    {(char *)"offset_y", (getter)__ss_get___ss_doom_Sidedef_offset_y, (setter)__ss_set___ss_doom_Sidedef_offset_y, (char *)"", NULL},
    {(char *)"sector", (getter)__ss_get___ss_doom_Sidedef_sector, (setter)__ss_set___ss_doom_Sidedef_sector, (char *)"", NULL},
    {(char *)"skyhack", (getter)__ss_get___ss_doom_Sidedef_skyhack, (setter)__ss_set___ss_doom_Sidedef_skyhack, (char *)"", NULL},
    {(char *)"upper_texture", (getter)__ss_get___ss_doom_Sidedef_upper_texture, (setter)__ss_set___ss_doom_Sidedef_upper_texture, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_SidedefObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Sidedef",
    sizeof( __ss_doom_SidedefObject),
    0,
    (destructor) __ss_doom_SidedefDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Sidedef_as_number,
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
    __ss_doom_SidedefMethods,
    __ss_doom_SidedefMembers,
    __ss_doom_SidedefGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Sidedef___tpinit__,
    0,
    __ss_doom_SidedefNew,
};

PyObject *__ss_doom_Sidedef__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_SidedefObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_SidedefObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "lower_texture", __to_py(((__ss_doom_SidedefObject *)self)->__ss_object->lower_texture));
    __ss_dict_steal(b, "middle_texture", __to_py(((__ss_doom_SidedefObject *)self)->__ss_object->middle_texture));
    __ss_dict_steal(b, "offset_x", __to_py(((__ss_doom_SidedefObject *)self)->__ss_object->offset_x));
    __ss_dict_steal(b, "offset_y", __to_py(((__ss_doom_SidedefObject *)self)->__ss_object->offset_y));
    __ss_dict_steal(b, "sector", __to_py(((__ss_doom_SidedefObject *)self)->__ss_object->sector));
    __ss_dict_steal(b, "skyhack", __to_py(((__ss_doom_SidedefObject *)self)->__ss_object->skyhack));
    __ss_dict_steal(b, "upper_texture", __to_py(((__ss_doom_SidedefObject *)self)->__ss_object->upper_texture));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Sidedef__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "lower_texture");
    if (value) ((__ss_doom_SidedefObject *)self)->__ss_object->lower_texture = __to_ss<Texture *>(value);
    value = __ss_dict_lookup(state, "middle_texture");
    if (value) ((__ss_doom_SidedefObject *)self)->__ss_object->middle_texture = __to_ss<Texture *>(value);
    value = __ss_dict_lookup(state, "offset_x");
    if (value) ((__ss_doom_SidedefObject *)self)->__ss_object->offset_x = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "offset_y");
    if (value) ((__ss_doom_SidedefObject *)self)->__ss_object->offset_y = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "sector");
    if (value) ((__ss_doom_SidedefObject *)self)->__ss_object->sector = __to_ss<Sector *>(value);
    value = __ss_dict_lookup(state, "skyhack");
    if (value) ((__ss_doom_SidedefObject *)self)->__ss_object->skyhack = __to_ss<__ss_bool >(value);
    value = __ss_dict_lookup(state, "upper_texture");
    if (value) ((__ss_doom_SidedefObject *)self)->__ss_object->upper_texture = __to_ss<Texture *>(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class Linedef */

typedef struct {
    PyObject_HEAD
    __doom__::Linedef *__ss_object;
} __ss_doom_LinedefObject;

static PyMemberDef __ss_doom_LinedefMembers[] = {
    {NULL}
};

PyObject *__ss_doom_Linedef___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vertex *arg_0 = __ss_arg<Vertex *>("vertex_start", 0, 0, 0, args, kwargs);
        Vertex *arg_1 = __ss_arg<Vertex *>("vertex_end", 1, 0, 0, args, kwargs);
        __ss_int arg_2 = __ss_arg<__ss_int >("special_type", 2, 0, 0, args, kwargs);
        Sidedef *arg_3 = __ss_arg<Sidedef *>("sidedef_front", 3, 0, 0, args, kwargs);
        Sidedef *arg_4 = __ss_arg<Sidedef *>("sidedef_back", 4, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_LinedefObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2, arg_3, arg_4));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Linedef_as_number = {
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

PyObject *__ss_doom_Linedef__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Linedef__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_LinedefMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Linedef__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Linedef__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Linedef___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Linedef___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Linedef___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_LinedefNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_LinedefObject *self = (__ss_doom_LinedefObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Linedef();
    self->__ss_object->__class__ = __doom__::cl_Linedef;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_LinedefDealloc(__ss_doom_LinedefObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Linedef_sidedef_back(__ss_doom_LinedefObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->sidedef_back);
}

int __ss_set___ss_doom_Linedef_sidedef_back(__ss_doom_LinedefObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->sidedef_back = __to_ss<Sidedef *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Linedef_sidedef_front(__ss_doom_LinedefObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->sidedef_front);
}

int __ss_set___ss_doom_Linedef_sidedef_front(__ss_doom_LinedefObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->sidedef_front = __to_ss<Sidedef *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Linedef_special_type(__ss_doom_LinedefObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->special_type);
}

int __ss_set___ss_doom_Linedef_special_type(__ss_doom_LinedefObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->special_type = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Linedef_vertex_end(__ss_doom_LinedefObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->vertex_end);
}

int __ss_set___ss_doom_Linedef_vertex_end(__ss_doom_LinedefObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->vertex_end = __to_ss<Vertex *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Linedef_vertex_start(__ss_doom_LinedefObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->vertex_start);
}

int __ss_set___ss_doom_Linedef_vertex_start(__ss_doom_LinedefObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->vertex_start = __to_ss<Vertex *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_LinedefGetSet[] = {
    {(char *)"sidedef_back", (getter)__ss_get___ss_doom_Linedef_sidedef_back, (setter)__ss_set___ss_doom_Linedef_sidedef_back, (char *)"", NULL},
    {(char *)"sidedef_front", (getter)__ss_get___ss_doom_Linedef_sidedef_front, (setter)__ss_set___ss_doom_Linedef_sidedef_front, (char *)"", NULL},
    {(char *)"special_type", (getter)__ss_get___ss_doom_Linedef_special_type, (setter)__ss_set___ss_doom_Linedef_special_type, (char *)"", NULL},
    {(char *)"vertex_end", (getter)__ss_get___ss_doom_Linedef_vertex_end, (setter)__ss_set___ss_doom_Linedef_vertex_end, (char *)"", NULL},
    {(char *)"vertex_start", (getter)__ss_get___ss_doom_Linedef_vertex_start, (setter)__ss_set___ss_doom_Linedef_vertex_start, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_LinedefObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Linedef",
    sizeof( __ss_doom_LinedefObject),
    0,
    (destructor) __ss_doom_LinedefDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Linedef_as_number,
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
    __ss_doom_LinedefMethods,
    __ss_doom_LinedefMembers,
    __ss_doom_LinedefGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Linedef___tpinit__,
    0,
    __ss_doom_LinedefNew,
};

PyObject *__ss_doom_Linedef__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_LinedefObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_LinedefObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "sidedef_back", __to_py(((__ss_doom_LinedefObject *)self)->__ss_object->sidedef_back));
    __ss_dict_steal(b, "sidedef_front", __to_py(((__ss_doom_LinedefObject *)self)->__ss_object->sidedef_front));
    __ss_dict_steal(b, "special_type", __to_py(((__ss_doom_LinedefObject *)self)->__ss_object->special_type));
    __ss_dict_steal(b, "vertex_end", __to_py(((__ss_doom_LinedefObject *)self)->__ss_object->vertex_end));
    __ss_dict_steal(b, "vertex_start", __to_py(((__ss_doom_LinedefObject *)self)->__ss_object->vertex_start));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Linedef__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "sidedef_back");
    if (value) ((__ss_doom_LinedefObject *)self)->__ss_object->sidedef_back = __to_ss<Sidedef *>(value);
    value = __ss_dict_lookup(state, "sidedef_front");
    if (value) ((__ss_doom_LinedefObject *)self)->__ss_object->sidedef_front = __to_ss<Sidedef *>(value);
    value = __ss_dict_lookup(state, "special_type");
    if (value) ((__ss_doom_LinedefObject *)self)->__ss_object->special_type = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "vertex_end");
    if (value) ((__ss_doom_LinedefObject *)self)->__ss_object->vertex_end = __to_ss<Vertex *>(value);
    value = __ss_dict_lookup(state, "vertex_start");
    if (value) ((__ss_doom_LinedefObject *)self)->__ss_object->vertex_start = __to_ss<Vertex *>(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class Sector */

typedef struct {
    PyObject_HEAD
    __doom__::Sector *__ss_object;
} __ss_doom_SectorObject;

static PyMemberDef __ss_doom_SectorMembers[] = {
    {NULL}
};

PyObject *__ss_doom_Sector___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_int arg_0 = __ss_arg<__ss_int >("floor_h", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("ceil_h", 1, 0, 0, args, kwargs);
        bytes *arg_2 = __ss_arg<bytes *>("floor_texture", 2, 0, 0, args, kwargs);
        bytes *arg_3 = __ss_arg<bytes *>("ceil_texture", 3, 0, 0, args, kwargs);
        __ss_int arg_4 = __ss_arg<__ss_int >("light_level", 4, 0, 0, args, kwargs);
        __ss_int arg_5 = __ss_arg<__ss_int >("special_type", 5, 0, 0, args, kwargs);
        Flat *arg_6 = __ss_arg<Flat *>("floor_flat", 6, 0, 0, args, kwargs);
        Flat *arg_7 = __ss_arg<Flat *>("ceil_flat", 7, 0, 0, args, kwargs);
        Picture *arg_8 = __ss_arg<Picture *>("ceil_pic", 8, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_SectorObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2, arg_3, arg_4, arg_5, arg_6, arg_7, arg_8));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Sector_as_number = {
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

PyObject *__ss_doom_Sector__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Sector__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_SectorMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Sector__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Sector__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Sector___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Sector___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Sector___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_SectorNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_SectorObject *self = (__ss_doom_SectorObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Sector();
    self->__ss_object->__class__ = __doom__::cl_Sector;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_SectorDealloc(__ss_doom_SectorObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Sector_ceil_flat(__ss_doom_SectorObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->ceil_flat);
}

int __ss_set___ss_doom_Sector_ceil_flat(__ss_doom_SectorObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->ceil_flat = __to_ss<Flat *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sector_ceil_h(__ss_doom_SectorObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->ceil_h);
}

int __ss_set___ss_doom_Sector_ceil_h(__ss_doom_SectorObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->ceil_h = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sector_ceil_pic(__ss_doom_SectorObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->ceil_pic);
}

int __ss_set___ss_doom_Sector_ceil_pic(__ss_doom_SectorObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->ceil_pic = __to_ss<Picture *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sector_ceil_texture(__ss_doom_SectorObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->ceil_texture);
}

int __ss_set___ss_doom_Sector_ceil_texture(__ss_doom_SectorObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->ceil_texture = __to_ss<bytes *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sector_floor_flat(__ss_doom_SectorObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->floor_flat);
}

int __ss_set___ss_doom_Sector_floor_flat(__ss_doom_SectorObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->floor_flat = __to_ss<Flat *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sector_floor_h(__ss_doom_SectorObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->floor_h);
}

int __ss_set___ss_doom_Sector_floor_h(__ss_doom_SectorObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->floor_h = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sector_floor_texture(__ss_doom_SectorObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->floor_texture);
}

int __ss_set___ss_doom_Sector_floor_texture(__ss_doom_SectorObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->floor_texture = __to_ss<bytes *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sector_light_level(__ss_doom_SectorObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->light_level);
}

int __ss_set___ss_doom_Sector_light_level(__ss_doom_SectorObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->light_level = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sector_random(__ss_doom_SectorObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->_random);
}

int __ss_set___ss_doom_Sector_random(__ss_doom_SectorObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->_random = __to_ss<list<__ss_bool> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Sector_special_type(__ss_doom_SectorObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->special_type);
}

int __ss_set___ss_doom_Sector_special_type(__ss_doom_SectorObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->special_type = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_SectorGetSet[] = {
    {(char *)"ceil_flat", (getter)__ss_get___ss_doom_Sector_ceil_flat, (setter)__ss_set___ss_doom_Sector_ceil_flat, (char *)"", NULL},
    {(char *)"ceil_h", (getter)__ss_get___ss_doom_Sector_ceil_h, (setter)__ss_set___ss_doom_Sector_ceil_h, (char *)"", NULL},
    {(char *)"ceil_pic", (getter)__ss_get___ss_doom_Sector_ceil_pic, (setter)__ss_set___ss_doom_Sector_ceil_pic, (char *)"", NULL},
    {(char *)"ceil_texture", (getter)__ss_get___ss_doom_Sector_ceil_texture, (setter)__ss_set___ss_doom_Sector_ceil_texture, (char *)"", NULL},
    {(char *)"floor_flat", (getter)__ss_get___ss_doom_Sector_floor_flat, (setter)__ss_set___ss_doom_Sector_floor_flat, (char *)"", NULL},
    {(char *)"floor_h", (getter)__ss_get___ss_doom_Sector_floor_h, (setter)__ss_set___ss_doom_Sector_floor_h, (char *)"", NULL},
    {(char *)"floor_texture", (getter)__ss_get___ss_doom_Sector_floor_texture, (setter)__ss_set___ss_doom_Sector_floor_texture, (char *)"", NULL},
    {(char *)"light_level", (getter)__ss_get___ss_doom_Sector_light_level, (setter)__ss_set___ss_doom_Sector_light_level, (char *)"", NULL},
    {(char *)"random", (getter)__ss_get___ss_doom_Sector_random, (setter)__ss_set___ss_doom_Sector_random, (char *)"", NULL},
    {(char *)"special_type", (getter)__ss_get___ss_doom_Sector_special_type, (setter)__ss_set___ss_doom_Sector_special_type, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_SectorObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Sector",
    sizeof( __ss_doom_SectorObject),
    0,
    (destructor) __ss_doom_SectorDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Sector_as_number,
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
    __ss_doom_SectorMethods,
    __ss_doom_SectorMembers,
    __ss_doom_SectorGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Sector___tpinit__,
    0,
    __ss_doom_SectorNew,
};

PyObject *__ss_doom_Sector__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_SectorObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_SectorObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "ceil_flat", __to_py(((__ss_doom_SectorObject *)self)->__ss_object->ceil_flat));
    __ss_dict_steal(b, "ceil_h", __to_py(((__ss_doom_SectorObject *)self)->__ss_object->ceil_h));
    __ss_dict_steal(b, "ceil_pic", __to_py(((__ss_doom_SectorObject *)self)->__ss_object->ceil_pic));
    __ss_dict_steal(b, "ceil_texture", __to_py(((__ss_doom_SectorObject *)self)->__ss_object->ceil_texture));
    __ss_dict_steal(b, "floor_flat", __to_py(((__ss_doom_SectorObject *)self)->__ss_object->floor_flat));
    __ss_dict_steal(b, "floor_h", __to_py(((__ss_doom_SectorObject *)self)->__ss_object->floor_h));
    __ss_dict_steal(b, "floor_texture", __to_py(((__ss_doom_SectorObject *)self)->__ss_object->floor_texture));
    __ss_dict_steal(b, "light_level", __to_py(((__ss_doom_SectorObject *)self)->__ss_object->light_level));
    __ss_dict_steal(b, "random", __to_py(((__ss_doom_SectorObject *)self)->__ss_object->_random));
    __ss_dict_steal(b, "special_type", __to_py(((__ss_doom_SectorObject *)self)->__ss_object->special_type));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Sector__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "ceil_flat");
    if (value) ((__ss_doom_SectorObject *)self)->__ss_object->ceil_flat = __to_ss<Flat *>(value);
    value = __ss_dict_lookup(state, "ceil_h");
    if (value) ((__ss_doom_SectorObject *)self)->__ss_object->ceil_h = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "ceil_pic");
    if (value) ((__ss_doom_SectorObject *)self)->__ss_object->ceil_pic = __to_ss<Picture *>(value);
    value = __ss_dict_lookup(state, "ceil_texture");
    if (value) ((__ss_doom_SectorObject *)self)->__ss_object->ceil_texture = __to_ss<bytes *>(value);
    value = __ss_dict_lookup(state, "floor_flat");
    if (value) ((__ss_doom_SectorObject *)self)->__ss_object->floor_flat = __to_ss<Flat *>(value);
    value = __ss_dict_lookup(state, "floor_h");
    if (value) ((__ss_doom_SectorObject *)self)->__ss_object->floor_h = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "floor_texture");
    if (value) ((__ss_doom_SectorObject *)self)->__ss_object->floor_texture = __to_ss<bytes *>(value);
    value = __ss_dict_lookup(state, "light_level");
    if (value) ((__ss_doom_SectorObject *)self)->__ss_object->light_level = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "random");
    if (value) ((__ss_doom_SectorObject *)self)->__ss_object->_random = __to_ss<list<__ss_bool> *>(value);
    value = __ss_dict_lookup(state, "special_type");
    if (value) ((__ss_doom_SectorObject *)self)->__ss_object->special_type = __to_ss<__ss_int >(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class SubSector */

typedef struct {
    PyObject_HEAD
    __doom__::SubSector *__ss_object;
} __ss_doom_SubSectorObject;

static PyMemberDef __ss_doom_SubSectorMembers[] = {
    {NULL}
};

PyObject *__ss_doom_SubSector___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        list<Seg *> *arg_0 = __ss_arg<list<Seg *> *>("segs", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_SubSectorObject *)self)->__ss_object->__init__(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_SubSector_as_number = {
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

PyObject *__ss_doom_SubSector__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_SubSector__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_SubSectorMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_SubSector__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_SubSector__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_SubSector___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_SubSector___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_SubSector___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_SubSectorNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_SubSectorObject *self = (__ss_doom_SubSectorObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::SubSector();
    self->__ss_object->__class__ = __doom__::cl_SubSector;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_SubSectorDealloc(__ss_doom_SubSectorObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_SubSector_segs(__ss_doom_SubSectorObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->segs);
}

int __ss_set___ss_doom_SubSector_segs(__ss_doom_SubSectorObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->segs = __to_ss<list<Seg *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_SubSectorGetSet[] = {
    {(char *)"segs", (getter)__ss_get___ss_doom_SubSector_segs, (setter)__ss_set___ss_doom_SubSector_segs, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_SubSectorObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.SubSector",
    sizeof( __ss_doom_SubSectorObject),
    0,
    (destructor) __ss_doom_SubSectorDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_SubSector_as_number,
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
    __ss_doom_SubSectorMethods,
    __ss_doom_SubSectorMembers,
    __ss_doom_SubSectorGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_SubSector___tpinit__,
    0,
    __ss_doom_SubSectorNew,
};

PyObject *__ss_doom_SubSector__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_SubSectorObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_SubSectorObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "segs", __to_py(((__ss_doom_SubSectorObject *)self)->__ss_object->segs));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_SubSector__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "segs");
    if (value) ((__ss_doom_SubSectorObject *)self)->__ss_object->segs = __to_ss<list<Seg *> *>(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class Seg */

typedef struct {
    PyObject_HEAD
    __doom__::Seg *__ss_object;
} __ss_doom_SegObject;

static PyMemberDef __ss_doom_SegMembers[] = {
    {NULL}
};

PyObject *__ss_doom_Seg___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vertex *arg_0 = __ss_arg<Vertex *>("vertex_start", 0, 0, 0, args, kwargs);
        Vertex *arg_1 = __ss_arg<Vertex *>("vertex_end", 1, 0, 0, args, kwargs);
        __ss_int arg_2 = __ss_arg<__ss_int >("angle", 2, 0, 0, args, kwargs);
        Linedef *arg_3 = __ss_arg<Linedef *>("linedef", 3, 0, 0, args, kwargs);
        Sidedef *arg_4 = __ss_arg<Sidedef *>("sidedef_front", 4, 0, 0, args, kwargs);
        Sidedef *arg_5 = __ss_arg<Sidedef *>("sidedef_back", 5, 0, 0, args, kwargs);
        __ss_bool arg_6 = __ss_arg<__ss_bool >("is_portal", 6, 0, False, args, kwargs);
        __ss_int arg_7 = __ss_arg<__ss_int >("offset", 7, 0, 0, args, kwargs);
        Sector *arg_8 = __ss_arg<Sector *>("sector_front", 8, 0, 0, args, kwargs);
        Sector *arg_9 = __ss_arg<Sector *>("sector_back", 9, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_SegObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2, arg_3, arg_4, arg_5, arg_6, arg_7, arg_8, arg_9));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Seg_as_number = {
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

PyObject *__ss_doom_Seg__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Seg__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_SegMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Seg__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Seg__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Seg___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Seg___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Seg___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_SegNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_SegObject *self = (__ss_doom_SegObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Seg();
    self->__ss_object->__class__ = __doom__::cl_Seg;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_SegDealloc(__ss_doom_SegObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Seg_angle(__ss_doom_SegObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->angle);
}

int __ss_set___ss_doom_Seg_angle(__ss_doom_SegObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->angle = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Seg_is_portal(__ss_doom_SegObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->is_portal);
}

int __ss_set___ss_doom_Seg_is_portal(__ss_doom_SegObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->is_portal = __to_ss<__ss_bool >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Seg_length(__ss_doom_SegObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->length);
}

int __ss_set___ss_doom_Seg_length(__ss_doom_SegObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->length = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Seg_linedef(__ss_doom_SegObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->linedef);
}

int __ss_set___ss_doom_Seg_linedef(__ss_doom_SegObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->linedef = __to_ss<Linedef *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Seg_offset(__ss_doom_SegObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->offset);
}

int __ss_set___ss_doom_Seg_offset(__ss_doom_SegObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->offset = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Seg_sector_back(__ss_doom_SegObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->sector_back);
}

int __ss_set___ss_doom_Seg_sector_back(__ss_doom_SegObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->sector_back = __to_ss<Sector *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Seg_sector_front(__ss_doom_SegObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->sector_front);
}

int __ss_set___ss_doom_Seg_sector_front(__ss_doom_SegObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->sector_front = __to_ss<Sector *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Seg_sidedef_back(__ss_doom_SegObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->sidedef_back);
}

int __ss_set___ss_doom_Seg_sidedef_back(__ss_doom_SegObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->sidedef_back = __to_ss<Sidedef *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Seg_sidedef_front(__ss_doom_SegObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->sidedef_front);
}

int __ss_set___ss_doom_Seg_sidedef_front(__ss_doom_SegObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->sidedef_front = __to_ss<Sidedef *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Seg_vertex_end(__ss_doom_SegObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->vertex_end);
}

int __ss_set___ss_doom_Seg_vertex_end(__ss_doom_SegObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->vertex_end = __to_ss<Vertex *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Seg_vertex_start(__ss_doom_SegObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->vertex_start);
}

int __ss_set___ss_doom_Seg_vertex_start(__ss_doom_SegObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->vertex_start = __to_ss<Vertex *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_SegGetSet[] = {
    {(char *)"angle", (getter)__ss_get___ss_doom_Seg_angle, (setter)__ss_set___ss_doom_Seg_angle, (char *)"", NULL},
    {(char *)"is_portal", (getter)__ss_get___ss_doom_Seg_is_portal, (setter)__ss_set___ss_doom_Seg_is_portal, (char *)"", NULL},
    {(char *)"length", (getter)__ss_get___ss_doom_Seg_length, (setter)__ss_set___ss_doom_Seg_length, (char *)"", NULL},
    {(char *)"linedef", (getter)__ss_get___ss_doom_Seg_linedef, (setter)__ss_set___ss_doom_Seg_linedef, (char *)"", NULL},
    {(char *)"offset", (getter)__ss_get___ss_doom_Seg_offset, (setter)__ss_set___ss_doom_Seg_offset, (char *)"", NULL},
    {(char *)"sector_back", (getter)__ss_get___ss_doom_Seg_sector_back, (setter)__ss_set___ss_doom_Seg_sector_back, (char *)"", NULL},
    {(char *)"sector_front", (getter)__ss_get___ss_doom_Seg_sector_front, (setter)__ss_set___ss_doom_Seg_sector_front, (char *)"", NULL},
    {(char *)"sidedef_back", (getter)__ss_get___ss_doom_Seg_sidedef_back, (setter)__ss_set___ss_doom_Seg_sidedef_back, (char *)"", NULL},
    {(char *)"sidedef_front", (getter)__ss_get___ss_doom_Seg_sidedef_front, (setter)__ss_set___ss_doom_Seg_sidedef_front, (char *)"", NULL},
    {(char *)"vertex_end", (getter)__ss_get___ss_doom_Seg_vertex_end, (setter)__ss_set___ss_doom_Seg_vertex_end, (char *)"", NULL},
    {(char *)"vertex_start", (getter)__ss_get___ss_doom_Seg_vertex_start, (setter)__ss_set___ss_doom_Seg_vertex_start, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_SegObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Seg",
    sizeof( __ss_doom_SegObject),
    0,
    (destructor) __ss_doom_SegDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Seg_as_number,
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
    __ss_doom_SegMethods,
    __ss_doom_SegMembers,
    __ss_doom_SegGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Seg___tpinit__,
    0,
    __ss_doom_SegNew,
};

PyObject *__ss_doom_Seg__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_SegObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_SegObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "angle", __to_py(((__ss_doom_SegObject *)self)->__ss_object->angle));
    __ss_dict_steal(b, "is_portal", __to_py(((__ss_doom_SegObject *)self)->__ss_object->is_portal));
    __ss_dict_steal(b, "length", __to_py(((__ss_doom_SegObject *)self)->__ss_object->length));
    __ss_dict_steal(b, "linedef", __to_py(((__ss_doom_SegObject *)self)->__ss_object->linedef));
    __ss_dict_steal(b, "offset", __to_py(((__ss_doom_SegObject *)self)->__ss_object->offset));
    __ss_dict_steal(b, "sector_back", __to_py(((__ss_doom_SegObject *)self)->__ss_object->sector_back));
    __ss_dict_steal(b, "sector_front", __to_py(((__ss_doom_SegObject *)self)->__ss_object->sector_front));
    __ss_dict_steal(b, "sidedef_back", __to_py(((__ss_doom_SegObject *)self)->__ss_object->sidedef_back));
    __ss_dict_steal(b, "sidedef_front", __to_py(((__ss_doom_SegObject *)self)->__ss_object->sidedef_front));
    __ss_dict_steal(b, "vertex_end", __to_py(((__ss_doom_SegObject *)self)->__ss_object->vertex_end));
    __ss_dict_steal(b, "vertex_start", __to_py(((__ss_doom_SegObject *)self)->__ss_object->vertex_start));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Seg__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "angle");
    if (value) ((__ss_doom_SegObject *)self)->__ss_object->angle = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "is_portal");
    if (value) ((__ss_doom_SegObject *)self)->__ss_object->is_portal = __to_ss<__ss_bool >(value);
    value = __ss_dict_lookup(state, "length");
    if (value) ((__ss_doom_SegObject *)self)->__ss_object->length = __to_ss<__ss_float >(value);
    value = __ss_dict_lookup(state, "linedef");
    if (value) ((__ss_doom_SegObject *)self)->__ss_object->linedef = __to_ss<Linedef *>(value);
    value = __ss_dict_lookup(state, "offset");
    if (value) ((__ss_doom_SegObject *)self)->__ss_object->offset = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "sector_back");
    if (value) ((__ss_doom_SegObject *)self)->__ss_object->sector_back = __to_ss<Sector *>(value);
    value = __ss_dict_lookup(state, "sector_front");
    if (value) ((__ss_doom_SegObject *)self)->__ss_object->sector_front = __to_ss<Sector *>(value);
    value = __ss_dict_lookup(state, "sidedef_back");
    if (value) ((__ss_doom_SegObject *)self)->__ss_object->sidedef_back = __to_ss<Sidedef *>(value);
    value = __ss_dict_lookup(state, "sidedef_front");
    if (value) ((__ss_doom_SegObject *)self)->__ss_object->sidedef_front = __to_ss<Sidedef *>(value);
    value = __ss_dict_lookup(state, "vertex_end");
    if (value) ((__ss_doom_SegObject *)self)->__ss_object->vertex_end = __to_ss<Vertex *>(value);
    value = __ss_dict_lookup(state, "vertex_start");
    if (value) ((__ss_doom_SegObject *)self)->__ss_object->vertex_start = __to_ss<Vertex *>(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class Flat */

typedef struct {
    PyObject_HEAD
    __doom__::Flat *__ss_object;
} __ss_doom_FlatObject;

static PyMemberDef __ss_doom_FlatMembers[] = {
    {NULL}
};

PyObject *__ss_doom_Flat___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        list<bytes *> *arg_0 = __ss_arg<list<bytes *> *>("data", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_FlatObject *)self)->__ss_object->__init__(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Flat_get_data(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_int arg_0 = __ss_arg<__ss_int >("frame_count", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_FlatObject *)self)->__ss_object->get_data(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Flat_as_number = {
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

PyObject *__ss_doom_Flat__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Flat__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_FlatMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Flat__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Flat__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Flat___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"get_data", (PyCFunction)__ss_doom_Flat_get_data, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Flat___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Flat___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_FlatNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_FlatObject *self = (__ss_doom_FlatObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Flat();
    self->__ss_object->__class__ = __doom__::cl_Flat;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_FlatDealloc(__ss_doom_FlatObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Flat_data(__ss_doom_FlatObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->data);
}

int __ss_set___ss_doom_Flat_data(__ss_doom_FlatObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->data = __to_ss<list<list<list<__ss_int> *> *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_FlatGetSet[] = {
    {(char *)"data", (getter)__ss_get___ss_doom_Flat_data, (setter)__ss_set___ss_doom_Flat_data, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_FlatObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Flat",
    sizeof( __ss_doom_FlatObject),
    0,
    (destructor) __ss_doom_FlatDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Flat_as_number,
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
    __ss_doom_FlatMethods,
    __ss_doom_FlatMembers,
    __ss_doom_FlatGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Flat___tpinit__,
    0,
    __ss_doom_FlatNew,
};

PyObject *__ss_doom_Flat__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_FlatObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_FlatObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "data", __to_py(((__ss_doom_FlatObject *)self)->__ss_object->data));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Flat__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "data");
    if (value) ((__ss_doom_FlatObject *)self)->__ss_object->data = __to_ss<list<list<list<__ss_int> *> *> *>(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class BSPNode */

typedef struct {
    PyObject_HEAD
    __doom__::BSPNode *__ss_object;
} __ss_doom_BSPNodeObject;

static PyMemberDef __ss_doom_BSPNodeMembers[] = {
    {NULL}
};

PyObject *__ss_doom_BSPNode___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_int arg_0 = __ss_arg<__ss_int >("partition_x", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("partition_y", 1, 0, 0, args, kwargs);
        __ss_int arg_2 = __ss_arg<__ss_int >("change_partition_x", 2, 0, 0, args, kwargs);
        __ss_int arg_3 = __ss_arg<__ss_int >("change_partition_y", 3, 0, 0, args, kwargs);
        __ss_int arg_4 = __ss_arg<__ss_int >("rchild_id", 4, 0, 0, args, kwargs);
        __ss_int arg_5 = __ss_arg<__ss_int >("lchild_id", 5, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_BSPNodeObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2, arg_3, arg_4, arg_5));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_BSPNode_visit(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Map *arg_0 = __ss_arg<Map *>("map_", 0, 0, 0, args, kwargs);
        list<SubSector *> *arg_1 = __ss_arg<list<SubSector *> *>("subsectors", 1, 1, 0, args, kwargs);

        return __to_py(((__ss_doom_BSPNodeObject *)self)->__ss_object->visit(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_BSPNode_as_number = {
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

PyObject *__ss_doom_BSPNode__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_BSPNode__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_BSPNodeMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_BSPNode__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_BSPNode__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_BSPNode___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"visit", (PyCFunction)__ss_doom_BSPNode_visit, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_BSPNode___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_BSPNode___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_BSPNodeNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_BSPNodeObject *self = (__ss_doom_BSPNodeObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::BSPNode();
    self->__ss_object->__class__ = __doom__::cl_BSPNode;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_BSPNodeDealloc(__ss_doom_BSPNodeObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_BSPNode_change_partition_x(__ss_doom_BSPNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->change_partition_x);
}

int __ss_set___ss_doom_BSPNode_change_partition_x(__ss_doom_BSPNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->change_partition_x = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_BSPNode_change_partition_y(__ss_doom_BSPNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->change_partition_y);
}

int __ss_set___ss_doom_BSPNode_change_partition_y(__ss_doom_BSPNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->change_partition_y = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_BSPNode_lchild_id(__ss_doom_BSPNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->lchild_id);
}

int __ss_set___ss_doom_BSPNode_lchild_id(__ss_doom_BSPNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->lchild_id = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_BSPNode_partition_x(__ss_doom_BSPNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->partition_x);
}

int __ss_set___ss_doom_BSPNode_partition_x(__ss_doom_BSPNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->partition_x = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_BSPNode_partition_y(__ss_doom_BSPNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->partition_y);
}

int __ss_set___ss_doom_BSPNode_partition_y(__ss_doom_BSPNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->partition_y = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_BSPNode_rchild_id(__ss_doom_BSPNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->rchild_id);
}

int __ss_set___ss_doom_BSPNode_rchild_id(__ss_doom_BSPNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->rchild_id = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_BSPNodeGetSet[] = {
    {(char *)"change_partition_x", (getter)__ss_get___ss_doom_BSPNode_change_partition_x, (setter)__ss_set___ss_doom_BSPNode_change_partition_x, (char *)"", NULL},
    {(char *)"change_partition_y", (getter)__ss_get___ss_doom_BSPNode_change_partition_y, (setter)__ss_set___ss_doom_BSPNode_change_partition_y, (char *)"", NULL},
    {(char *)"lchild_id", (getter)__ss_get___ss_doom_BSPNode_lchild_id, (setter)__ss_set___ss_doom_BSPNode_lchild_id, (char *)"", NULL},
    {(char *)"partition_x", (getter)__ss_get___ss_doom_BSPNode_partition_x, (setter)__ss_set___ss_doom_BSPNode_partition_x, (char *)"", NULL},
    {(char *)"partition_y", (getter)__ss_get___ss_doom_BSPNode_partition_y, (setter)__ss_set___ss_doom_BSPNode_partition_y, (char *)"", NULL},
    {(char *)"rchild_id", (getter)__ss_get___ss_doom_BSPNode_rchild_id, (setter)__ss_set___ss_doom_BSPNode_rchild_id, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_BSPNodeObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.BSPNode",
    sizeof( __ss_doom_BSPNodeObject),
    0,
    (destructor) __ss_doom_BSPNodeDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_BSPNode_as_number,
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
    __ss_doom_BSPNodeMethods,
    __ss_doom_BSPNodeMembers,
    __ss_doom_BSPNodeGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_BSPNode___tpinit__,
    0,
    __ss_doom_BSPNodeNew,
};

PyObject *__ss_doom_BSPNode__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_BSPNodeObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_BSPNodeObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "change_partition_x", __to_py(((__ss_doom_BSPNodeObject *)self)->__ss_object->change_partition_x));
    __ss_dict_steal(b, "change_partition_y", __to_py(((__ss_doom_BSPNodeObject *)self)->__ss_object->change_partition_y));
    __ss_dict_steal(b, "lchild_id", __to_py(((__ss_doom_BSPNodeObject *)self)->__ss_object->lchild_id));
    __ss_dict_steal(b, "partition_x", __to_py(((__ss_doom_BSPNodeObject *)self)->__ss_object->partition_x));
    __ss_dict_steal(b, "partition_y", __to_py(((__ss_doom_BSPNodeObject *)self)->__ss_object->partition_y));
    __ss_dict_steal(b, "rchild_id", __to_py(((__ss_doom_BSPNodeObject *)self)->__ss_object->rchild_id));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_BSPNode__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "change_partition_x");
    if (value) ((__ss_doom_BSPNodeObject *)self)->__ss_object->change_partition_x = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "change_partition_y");
    if (value) ((__ss_doom_BSPNodeObject *)self)->__ss_object->change_partition_y = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "lchild_id");
    if (value) ((__ss_doom_BSPNodeObject *)self)->__ss_object->lchild_id = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "partition_x");
    if (value) ((__ss_doom_BSPNodeObject *)self)->__ss_object->partition_x = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "partition_y");
    if (value) ((__ss_doom_BSPNodeObject *)self)->__ss_object->partition_y = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "rchild_id");
    if (value) ((__ss_doom_BSPNodeObject *)self)->__ss_object->rchild_id = __to_ss<__ss_int >(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class Thing */

typedef struct {
    PyObject_HEAD
    __doom__::Thing *__ss_object;
} __ss_doom_ThingObject;

static PyMemberDef __ss_doom_ThingMembers[] = {
    {NULL}
};

PyObject *__ss_doom_Thing___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_int arg_0 = __ss_arg<__ss_int >("x", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("y", 1, 0, 0, args, kwargs);
        __ss_int arg_2 = __ss_arg<__ss_int >("angle", 2, 0, 0, args, kwargs);
        __ss_int arg_3 = __ss_arg<__ss_int >("type_", 3, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_ThingObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2, arg_3));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Thing_as_number = {
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

PyObject *__ss_doom_Thing__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Thing__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_ThingMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Thing__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Thing__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Thing___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Thing___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Thing___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_ThingNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_ThingObject *self = (__ss_doom_ThingObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Thing();
    self->__ss_object->__class__ = __doom__::cl_Thing;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_ThingDealloc(__ss_doom_ThingObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Thing_angle(__ss_doom_ThingObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->angle);
}

int __ss_set___ss_doom_Thing_angle(__ss_doom_ThingObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->angle = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Thing_type_(__ss_doom_ThingObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->type_);
}

int __ss_set___ss_doom_Thing_type_(__ss_doom_ThingObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->type_ = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Thing_x(__ss_doom_ThingObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->x);
}

int __ss_set___ss_doom_Thing_x(__ss_doom_ThingObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->x = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Thing_y(__ss_doom_ThingObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->y);
}

int __ss_set___ss_doom_Thing_y(__ss_doom_ThingObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->y = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_ThingGetSet[] = {
    {(char *)"angle", (getter)__ss_get___ss_doom_Thing_angle, (setter)__ss_set___ss_doom_Thing_angle, (char *)"", NULL},
    {(char *)"type_", (getter)__ss_get___ss_doom_Thing_type_, (setter)__ss_set___ss_doom_Thing_type_, (char *)"", NULL},
    {(char *)"x", (getter)__ss_get___ss_doom_Thing_x, (setter)__ss_set___ss_doom_Thing_x, (char *)"", NULL},
    {(char *)"y", (getter)__ss_get___ss_doom_Thing_y, (setter)__ss_set___ss_doom_Thing_y, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_ThingObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Thing",
    sizeof( __ss_doom_ThingObject),
    0,
    (destructor) __ss_doom_ThingDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Thing_as_number,
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
    __ss_doom_ThingMethods,
    __ss_doom_ThingMembers,
    __ss_doom_ThingGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Thing___tpinit__,
    0,
    __ss_doom_ThingNew,
};

PyObject *__ss_doom_Thing__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_ThingObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_ThingObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "angle", __to_py(((__ss_doom_ThingObject *)self)->__ss_object->angle));
    __ss_dict_steal(b, "type_", __to_py(((__ss_doom_ThingObject *)self)->__ss_object->type_));
    __ss_dict_steal(b, "x", __to_py(((__ss_doom_ThingObject *)self)->__ss_object->x));
    __ss_dict_steal(b, "y", __to_py(((__ss_doom_ThingObject *)self)->__ss_object->y));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Thing__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "angle");
    if (value) ((__ss_doom_ThingObject *)self)->__ss_object->angle = __to_ss<__ss_float >(value);
    value = __ss_dict_lookup(state, "type_");
    if (value) ((__ss_doom_ThingObject *)self)->__ss_object->type_ = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "x");
    if (value) ((__ss_doom_ThingObject *)self)->__ss_object->x = __to_ss<__ss_float >(value);
    value = __ss_dict_lookup(state, "y");
    if (value) ((__ss_doom_ThingObject *)self)->__ss_object->y = __to_ss<__ss_float >(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class Player */

typedef struct {
    PyObject_HEAD
    __doom__::Player *__ss_object;
} __ss_doom_PlayerObject;

static PyMemberDef __ss_doom_PlayerMembers[] = {
    {NULL}
};

PyObject *__ss_doom_Player___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Thing *arg_0 = __ss_arg<Thing *>("thing", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_PlayerObject *)self)->__ss_object->__init__(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Player_update(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_PlayerObject *)self)->__ss_object->update());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Player_as_number = {
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

PyObject *__ss_doom_Player__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Player__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_PlayerMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Player__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Player__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Player___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"update", (PyCFunction)__ss_doom_Player_update, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Player___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Player___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_PlayerNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_PlayerObject *self = (__ss_doom_PlayerObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Player();
    self->__ss_object->__class__ = __doom__::cl_Player;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_PlayerDealloc(__ss_doom_PlayerObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Player_angle(__ss_doom_PlayerObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->angle);
}

int __ss_set___ss_doom_Player_angle(__ss_doom_PlayerObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->angle = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Player_direction(__ss_doom_PlayerObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->direction);
}

int __ss_set___ss_doom_Player_direction(__ss_doom_PlayerObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->direction = __to_ss<Vec2 *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Player_floor_h(__ss_doom_PlayerObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->floor_h);
}

int __ss_set___ss_doom_Player_floor_h(__ss_doom_PlayerObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->floor_h = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Player_x(__ss_doom_PlayerObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->x);
}

int __ss_set___ss_doom_Player_x(__ss_doom_PlayerObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->x = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Player_y(__ss_doom_PlayerObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->y);
}

int __ss_set___ss_doom_Player_y(__ss_doom_PlayerObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->y = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Player_z(__ss_doom_PlayerObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->z);
}

int __ss_set___ss_doom_Player_z(__ss_doom_PlayerObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->z = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_PlayerGetSet[] = {
    {(char *)"angle", (getter)__ss_get___ss_doom_Player_angle, (setter)__ss_set___ss_doom_Player_angle, (char *)"", NULL},
    {(char *)"direction", (getter)__ss_get___ss_doom_Player_direction, (setter)__ss_set___ss_doom_Player_direction, (char *)"", NULL},
    {(char *)"floor_h", (getter)__ss_get___ss_doom_Player_floor_h, (setter)__ss_set___ss_doom_Player_floor_h, (char *)"", NULL},
    {(char *)"x", (getter)__ss_get___ss_doom_Player_x, (setter)__ss_set___ss_doom_Player_x, (char *)"", NULL},
    {(char *)"y", (getter)__ss_get___ss_doom_Player_y, (setter)__ss_set___ss_doom_Player_y, (char *)"", NULL},
    {(char *)"z", (getter)__ss_get___ss_doom_Player_z, (setter)__ss_set___ss_doom_Player_z, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_PlayerObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Player",
    sizeof( __ss_doom_PlayerObject),
    0,
    (destructor) __ss_doom_PlayerDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Player_as_number,
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
    __ss_doom_PlayerMethods,
    __ss_doom_PlayerMembers,
    __ss_doom_PlayerGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Player___tpinit__,
    0,
    __ss_doom_PlayerNew,
};

PyObject *__ss_doom_Player__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_PlayerObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_PlayerObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "angle", __to_py(((__ss_doom_PlayerObject *)self)->__ss_object->angle));
    __ss_dict_steal(b, "direction", __to_py(((__ss_doom_PlayerObject *)self)->__ss_object->direction));
    __ss_dict_steal(b, "floor_h", __to_py(((__ss_doom_PlayerObject *)self)->__ss_object->floor_h));
    __ss_dict_steal(b, "x", __to_py(((__ss_doom_PlayerObject *)self)->__ss_object->x));
    __ss_dict_steal(b, "y", __to_py(((__ss_doom_PlayerObject *)self)->__ss_object->y));
    __ss_dict_steal(b, "z", __to_py(((__ss_doom_PlayerObject *)self)->__ss_object->z));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Player__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "angle");
    if (value) ((__ss_doom_PlayerObject *)self)->__ss_object->angle = __to_ss<__ss_float >(value);
    value = __ss_dict_lookup(state, "direction");
    if (value) ((__ss_doom_PlayerObject *)self)->__ss_object->direction = __to_ss<Vec2 *>(value);
    value = __ss_dict_lookup(state, "floor_h");
    if (value) ((__ss_doom_PlayerObject *)self)->__ss_object->floor_h = __to_ss<__ss_float >(value);
    value = __ss_dict_lookup(state, "x");
    if (value) ((__ss_doom_PlayerObject *)self)->__ss_object->x = __to_ss<__ss_float >(value);
    value = __ss_dict_lookup(state, "y");
    if (value) ((__ss_doom_PlayerObject *)self)->__ss_object->y = __to_ss<__ss_float >(value);
    value = __ss_dict_lookup(state, "z");
    if (value) ((__ss_doom_PlayerObject *)self)->__ss_object->z = __to_ss<__ss_float >(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class Texture */

typedef struct {
    PyObject_HEAD
    __doom__::Texture *__ss_object;
} __ss_doom_TextureObject;

static PyMemberDef __ss_doom_TextureMembers[] = {
    {NULL}
};

PyObject *__ss_doom_Texture___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        bytes *arg_0 = __ss_arg<bytes *>("name", 0, 0, 0, args, kwargs);
        list<list<__ss_int> *> *arg_1 = __ss_arg<list<list<__ss_int> *> *>("data", 1, 0, 0, args, kwargs);
        __ss_int arg_2 = __ss_arg<__ss_int >("width", 2, 0, 0, args, kwargs);
        __ss_int arg_3 = __ss_arg<__ss_int >("height", 3, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_TextureObject *)self)->__ss_object->__init__(arg_0, arg_1, arg_2, arg_3));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Texture_as_number = {
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

PyObject *__ss_doom_Texture__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Texture__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_TextureMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Texture__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Texture__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Texture___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Texture___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Texture___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_TextureNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_TextureObject *self = (__ss_doom_TextureObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Texture();
    self->__ss_object->__class__ = __doom__::cl_Texture;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_TextureDealloc(__ss_doom_TextureObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Texture_data(__ss_doom_TextureObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->data);
}

int __ss_set___ss_doom_Texture_data(__ss_doom_TextureObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->data = __to_ss<list<list<__ss_int> *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Texture_height(__ss_doom_TextureObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->height);
}

int __ss_set___ss_doom_Texture_height(__ss_doom_TextureObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->height = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Texture_name(__ss_doom_TextureObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->name);
}

int __ss_set___ss_doom_Texture_name(__ss_doom_TextureObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->name = __to_ss<bytes *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Texture_width(__ss_doom_TextureObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->width);
}

int __ss_set___ss_doom_Texture_width(__ss_doom_TextureObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->width = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_TextureGetSet[] = {
    {(char *)"data", (getter)__ss_get___ss_doom_Texture_data, (setter)__ss_set___ss_doom_Texture_data, (char *)"", NULL},
    {(char *)"height", (getter)__ss_get___ss_doom_Texture_height, (setter)__ss_set___ss_doom_Texture_height, (char *)"", NULL},
    {(char *)"name", (getter)__ss_get___ss_doom_Texture_name, (setter)__ss_set___ss_doom_Texture_name, (char *)"", NULL},
    {(char *)"width", (getter)__ss_get___ss_doom_Texture_width, (setter)__ss_set___ss_doom_Texture_width, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_TextureObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Texture",
    sizeof( __ss_doom_TextureObject),
    0,
    (destructor) __ss_doom_TextureDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Texture_as_number,
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
    __ss_doom_TextureMethods,
    __ss_doom_TextureMembers,
    __ss_doom_TextureGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Texture___tpinit__,
    0,
    __ss_doom_TextureNew,
};

PyObject *__ss_doom_Texture__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_TextureObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_TextureObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "data", __to_py(((__ss_doom_TextureObject *)self)->__ss_object->data));
    __ss_dict_steal(b, "height", __to_py(((__ss_doom_TextureObject *)self)->__ss_object->height));
    __ss_dict_steal(b, "name", __to_py(((__ss_doom_TextureObject *)self)->__ss_object->name));
    __ss_dict_steal(b, "width", __to_py(((__ss_doom_TextureObject *)self)->__ss_object->width));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Texture__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "data");
    if (value) ((__ss_doom_TextureObject *)self)->__ss_object->data = __to_ss<list<list<__ss_int> *> *>(value);
    value = __ss_dict_lookup(state, "height");
    if (value) ((__ss_doom_TextureObject *)self)->__ss_object->height = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "name");
    if (value) ((__ss_doom_TextureObject *)self)->__ss_object->name = __to_ss<bytes *>(value);
    value = __ss_dict_lookup(state, "width");
    if (value) ((__ss_doom_TextureObject *)self)->__ss_object->width = __to_ss<__ss_int >(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class Picture */

typedef struct {
    PyObject_HEAD
    __doom__::Picture *__ss_object;
} __ss_doom_PictureObject;

static PyMemberDef __ss_doom_PictureMembers[] = {
    {NULL}
};

PyObject *__ss_doom_Picture___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        bytes *arg_0 = __ss_arg<bytes *>("data", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_PictureObject *)self)->__ss_object->__init__(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Picture_as_number = {
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

PyObject *__ss_doom_Picture__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Picture__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_PictureMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Picture__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Picture__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Picture___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Picture___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Picture___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_PictureNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_PictureObject *self = (__ss_doom_PictureObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Picture();
    self->__ss_object->__class__ = __doom__::cl_Picture;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_PictureDealloc(__ss_doom_PictureObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Picture_data(__ss_doom_PictureObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->data);
}

int __ss_set___ss_doom_Picture_data(__ss_doom_PictureObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->data = __to_ss<list<list<__ss_int> *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Picture_height(__ss_doom_PictureObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->height);
}

int __ss_set___ss_doom_Picture_height(__ss_doom_PictureObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->height = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Picture_width(__ss_doom_PictureObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->width);
}

int __ss_set___ss_doom_Picture_width(__ss_doom_PictureObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->width = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_PictureGetSet[] = {
    {(char *)"data", (getter)__ss_get___ss_doom_Picture_data, (setter)__ss_set___ss_doom_Picture_data, (char *)"", NULL},
    {(char *)"height", (getter)__ss_get___ss_doom_Picture_height, (setter)__ss_set___ss_doom_Picture_height, (char *)"", NULL},
    {(char *)"width", (getter)__ss_get___ss_doom_Picture_width, (setter)__ss_set___ss_doom_Picture_width, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_PictureObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Picture",
    sizeof( __ss_doom_PictureObject),
    0,
    (destructor) __ss_doom_PictureDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Picture_as_number,
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
    __ss_doom_PictureMethods,
    __ss_doom_PictureMembers,
    __ss_doom_PictureGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Picture___tpinit__,
    0,
    __ss_doom_PictureNew,
};

PyObject *__ss_doom_Picture__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_PictureObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_PictureObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "data", __to_py(((__ss_doom_PictureObject *)self)->__ss_object->data));
    __ss_dict_steal(b, "height", __to_py(((__ss_doom_PictureObject *)self)->__ss_object->height));
    __ss_dict_steal(b, "width", __to_py(((__ss_doom_PictureObject *)self)->__ss_object->width));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Picture__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "data");
    if (value) ((__ss_doom_PictureObject *)self)->__ss_object->data = __to_ss<list<list<__ss_int> *> *>(value);
    value = __ss_dict_lookup(state, "height");
    if (value) ((__ss_doom_PictureObject *)self)->__ss_object->height = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "width");
    if (value) ((__ss_doom_PictureObject *)self)->__ss_object->width = __to_ss<__ss_int >(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class Colormap */

typedef struct {
    PyObject_HEAD
    __doom__::Colormap *__ss_object;
} __ss_doom_ColormapObject;

static PyMemberDef __ss_doom_ColormapMembers[] = {
    {NULL}
};

PyObject *__ss_doom_Colormap___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        bytes *arg_0 = __ss_arg<bytes *>("data", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_ColormapObject *)self)->__ss_object->__init__(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Colormap_as_number = {
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

PyObject *__ss_doom_Colormap__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Colormap__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_ColormapMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Colormap__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Colormap__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Colormap___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Colormap___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Colormap___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_ColormapNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_ColormapObject *self = (__ss_doom_ColormapObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Colormap();
    self->__ss_object->__class__ = __doom__::cl_Colormap;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_ColormapDealloc(__ss_doom_ColormapObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Colormap_data(__ss_doom_ColormapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->data);
}

int __ss_set___ss_doom_Colormap_data(__ss_doom_ColormapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->data = __to_ss<list<__ss_int> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_ColormapGetSet[] = {
    {(char *)"data", (getter)__ss_get___ss_doom_Colormap_data, (setter)__ss_set___ss_doom_Colormap_data, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_ColormapObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Colormap",
    sizeof( __ss_doom_ColormapObject),
    0,
    (destructor) __ss_doom_ColormapDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Colormap_as_number,
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
    __ss_doom_ColormapMethods,
    __ss_doom_ColormapMembers,
    __ss_doom_ColormapGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Colormap___tpinit__,
    0,
    __ss_doom_ColormapNew,
};

PyObject *__ss_doom_Colormap__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_ColormapObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_ColormapObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "data", __to_py(((__ss_doom_ColormapObject *)self)->__ss_object->data));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Colormap__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "data");
    if (value) ((__ss_doom_ColormapObject *)self)->__ss_object->data = __to_ss<list<__ss_int> *>(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class Vec2 */

typedef struct {
    PyObject_HEAD
    __doom__::Vec2 *__ss_object;
} __ss_doom_Vec2Object;

static PyMemberDef __ss_doom_Vec2Members[] = {
    {NULL}
};

PyObject *__ss_doom_Vec2___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_float arg_0 = __ss_arg<__ss_float >("x", 0, 1, __ss_float(0.0), args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("y", 1, 1, __ss_float(0.0), args, kwargs);

        return __to_py(((__ss_doom_Vec2Object *)self)->__ss_object->__init__(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Vec2_dot(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Vec2 *arg_0 = __ss_arg<Vec2 *>("v", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_Vec2Object *)self)->__ss_object->dot(arg_0));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Vec2_as_number = {
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

PyObject *__ss_doom_Vec2__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Vec2__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_Vec2Methods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Vec2__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Vec2__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Vec2___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"dot", (PyCFunction)__ss_doom_Vec2_dot, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Vec2___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Vec2___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_Vec2New(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_Vec2Object *self = (__ss_doom_Vec2Object *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Vec2();
    self->__ss_object->__class__ = __doom__::cl_Vec2;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_Vec2Dealloc(__ss_doom_Vec2Object *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Vec2_x(__ss_doom_Vec2Object *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->x);
}

int __ss_set___ss_doom_Vec2_x(__ss_doom_Vec2Object *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->x = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Vec2_y(__ss_doom_Vec2Object *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->y);
}

int __ss_set___ss_doom_Vec2_y(__ss_doom_Vec2Object *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->y = __to_ss<__ss_float >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_Vec2GetSet[] = {
    {(char *)"x", (getter)__ss_get___ss_doom_Vec2_x, (setter)__ss_set___ss_doom_Vec2_x, (char *)"", NULL},
    {(char *)"y", (getter)__ss_get___ss_doom_Vec2_y, (setter)__ss_set___ss_doom_Vec2_y, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_Vec2ObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Vec2",
    sizeof( __ss_doom_Vec2Object),
    0,
    (destructor) __ss_doom_Vec2Dealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Vec2_as_number,
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
    __ss_doom_Vec2Methods,
    __ss_doom_Vec2Members,
    __ss_doom_Vec2GetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Vec2___tpinit__,
    0,
    __ss_doom_Vec2New,
};

PyObject *__ss_doom_Vec2__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_Vec2ObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_Vec2ObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "x", __to_py(((__ss_doom_Vec2Object *)self)->__ss_object->x));
    __ss_dict_steal(b, "y", __to_py(((__ss_doom_Vec2Object *)self)->__ss_object->y));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Vec2__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "x");
    if (value) ((__ss_doom_Vec2Object *)self)->__ss_object->x = __to_ss<__ss_float >(value);
    value = __ss_dict_lookup(state, "y");
    if (value) ((__ss_doom_Vec2Object *)self)->__ss_object->y = __to_ss<__ss_float >(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class Map */

typedef struct {
    PyObject_HEAD
    __doom__::Map *__ss_object;
} __ss_doom_MapObject;

static PyMemberDef __ss_doom_MapMembers[] = {
    {NULL}
};

PyObject *__ss_doom_Map___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        str *arg_0 = __ss_arg<str *>("filepath", 0, 0, 0, args, kwargs);
        str *arg_1 = __ss_arg<str *>("map_", 1, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->__init__(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_entries(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        str *arg_0 = __ss_arg<str *>("filepath", 0, 0, 0, args, kwargs);
        str *arg_1 = __ss_arg<str *>("mapname", 1, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_entries(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_vertices(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_vertices());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_linedefs(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_linedefs());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_sidedefs(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_sidedefs());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_sectors(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_sectors());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_patches(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_patches());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_textures(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_textures());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_palette(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_palette());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_colormaps(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_colormaps());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_segs(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_segs());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_subsectors(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_subsectors());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_bspnodes(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_bspnodes());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_Map_extract_things(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {

        return __to_py(((__ss_doom_MapObject *)self)->__ss_object->extract_things());

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_Map_as_number = {
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

PyObject *__ss_doom_Map__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_Map__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_MapMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_Map__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_Map__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_Map___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_entries", (PyCFunction)__ss_doom_Map_extract_entries, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_vertices", (PyCFunction)__ss_doom_Map_extract_vertices, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_linedefs", (PyCFunction)__ss_doom_Map_extract_linedefs, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_sidedefs", (PyCFunction)__ss_doom_Map_extract_sidedefs, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_sectors", (PyCFunction)__ss_doom_Map_extract_sectors, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_patches", (PyCFunction)__ss_doom_Map_extract_patches, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_textures", (PyCFunction)__ss_doom_Map_extract_textures, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_palette", (PyCFunction)__ss_doom_Map_extract_palette, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_colormaps", (PyCFunction)__ss_doom_Map_extract_colormaps, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_segs", (PyCFunction)__ss_doom_Map_extract_segs, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_subsectors", (PyCFunction)__ss_doom_Map_extract_subsectors, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_bspnodes", (PyCFunction)__ss_doom_Map_extract_bspnodes, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"extract_things", (PyCFunction)__ss_doom_Map_extract_things, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_Map___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_Map___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_MapNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_MapObject *self = (__ss_doom_MapObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::Map();
    self->__ss_object->__class__ = __doom__::cl_Map;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_MapDealloc(__ss_doom_MapObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_Map_bspnodes(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->bspnodes);
}

int __ss_set___ss_doom_Map_bspnodes(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->bspnodes = __to_ss<list<BSPNode *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_colormaps(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->colormaps);
}

int __ss_set___ss_doom_Map_colormaps(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->colormaps = __to_ss<list<Colormap *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_entry_data(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->entry_data);
}

int __ss_set___ss_doom_Map_entry_data(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->entry_data = __to_ss<dict<bytes *, bytes *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_linedefs(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->linedefs);
}

int __ss_set___ss_doom_Map_linedefs(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->linedefs = __to_ss<list<Linedef *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_palette(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->palette);
}

int __ss_set___ss_doom_Map_palette(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->palette = __to_ss<list<tuple<__ss_int> *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_patches(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->patches);
}

int __ss_set___ss_doom_Map_patches(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->patches = __to_ss<list<Picture *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_player(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->player);
}

int __ss_set___ss_doom_Map_player(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->player = __to_ss<Player *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_sectors(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->sectors);
}

int __ss_set___ss_doom_Map_sectors(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->sectors = __to_ss<list<Sector *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_segs(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->segs);
}

int __ss_set___ss_doom_Map_segs(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->segs = __to_ss<list<Seg *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_sidedefs(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->sidedefs);
}

int __ss_set___ss_doom_Map_sidedefs(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->sidedefs = __to_ss<list<Sidedef *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_subsectors(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->subsectors);
}

int __ss_set___ss_doom_Map_subsectors(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->subsectors = __to_ss<list<SubSector *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_textures(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->textures);
}

int __ss_set___ss_doom_Map_textures(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->textures = __to_ss<dict<bytes *, Texture *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_things(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->things);
}

int __ss_set___ss_doom_Map_things(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->things = __to_ss<list<Thing *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_Map_vertices(__ss_doom_MapObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->vertices);
}

int __ss_set___ss_doom_Map_vertices(__ss_doom_MapObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->vertices = __to_ss<list<Vertex *> *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_MapGetSet[] = {
    {(char *)"bspnodes", (getter)__ss_get___ss_doom_Map_bspnodes, (setter)__ss_set___ss_doom_Map_bspnodes, (char *)"", NULL},
    {(char *)"colormaps", (getter)__ss_get___ss_doom_Map_colormaps, (setter)__ss_set___ss_doom_Map_colormaps, (char *)"", NULL},
    {(char *)"entry_data", (getter)__ss_get___ss_doom_Map_entry_data, (setter)__ss_set___ss_doom_Map_entry_data, (char *)"", NULL},
    {(char *)"linedefs", (getter)__ss_get___ss_doom_Map_linedefs, (setter)__ss_set___ss_doom_Map_linedefs, (char *)"", NULL},
    {(char *)"palette", (getter)__ss_get___ss_doom_Map_palette, (setter)__ss_set___ss_doom_Map_palette, (char *)"", NULL},
    {(char *)"patches", (getter)__ss_get___ss_doom_Map_patches, (setter)__ss_set___ss_doom_Map_patches, (char *)"", NULL},
    {(char *)"player", (getter)__ss_get___ss_doom_Map_player, (setter)__ss_set___ss_doom_Map_player, (char *)"", NULL},
    {(char *)"sectors", (getter)__ss_get___ss_doom_Map_sectors, (setter)__ss_set___ss_doom_Map_sectors, (char *)"", NULL},
    {(char *)"segs", (getter)__ss_get___ss_doom_Map_segs, (setter)__ss_set___ss_doom_Map_segs, (char *)"", NULL},
    {(char *)"sidedefs", (getter)__ss_get___ss_doom_Map_sidedefs, (setter)__ss_set___ss_doom_Map_sidedefs, (char *)"", NULL},
    {(char *)"subsectors", (getter)__ss_get___ss_doom_Map_subsectors, (setter)__ss_set___ss_doom_Map_subsectors, (char *)"", NULL},
    {(char *)"textures", (getter)__ss_get___ss_doom_Map_textures, (setter)__ss_set___ss_doom_Map_textures, (char *)"", NULL},
    {(char *)"things", (getter)__ss_get___ss_doom_Map_things, (setter)__ss_set___ss_doom_Map_things, (char *)"", NULL},
    {(char *)"vertices", (getter)__ss_get___ss_doom_Map_vertices, (setter)__ss_set___ss_doom_Map_vertices, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_MapObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.Map",
    sizeof( __ss_doom_MapObject),
    0,
    (destructor) __ss_doom_MapDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_Map_as_number,
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
    __ss_doom_MapMethods,
    __ss_doom_MapMembers,
    __ss_doom_MapGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_Map___tpinit__,
    0,
    __ss_doom_MapNew,
};

PyObject *__ss_doom_Map__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_MapObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_MapObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "bspnodes", __to_py(((__ss_doom_MapObject *)self)->__ss_object->bspnodes));
    __ss_dict_steal(b, "colormaps", __to_py(((__ss_doom_MapObject *)self)->__ss_object->colormaps));
    __ss_dict_steal(b, "entry_data", __to_py(((__ss_doom_MapObject *)self)->__ss_object->entry_data));
    __ss_dict_steal(b, "linedefs", __to_py(((__ss_doom_MapObject *)self)->__ss_object->linedefs));
    __ss_dict_steal(b, "palette", __to_py(((__ss_doom_MapObject *)self)->__ss_object->palette));
    __ss_dict_steal(b, "patches", __to_py(((__ss_doom_MapObject *)self)->__ss_object->patches));
    __ss_dict_steal(b, "player", __to_py(((__ss_doom_MapObject *)self)->__ss_object->player));
    __ss_dict_steal(b, "sectors", __to_py(((__ss_doom_MapObject *)self)->__ss_object->sectors));
    __ss_dict_steal(b, "segs", __to_py(((__ss_doom_MapObject *)self)->__ss_object->segs));
    __ss_dict_steal(b, "sidedefs", __to_py(((__ss_doom_MapObject *)self)->__ss_object->sidedefs));
    __ss_dict_steal(b, "subsectors", __to_py(((__ss_doom_MapObject *)self)->__ss_object->subsectors));
    __ss_dict_steal(b, "textures", __to_py(((__ss_doom_MapObject *)self)->__ss_object->textures));
    __ss_dict_steal(b, "things", __to_py(((__ss_doom_MapObject *)self)->__ss_object->things));
    __ss_dict_steal(b, "vertices", __to_py(((__ss_doom_MapObject *)self)->__ss_object->vertices));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_Map__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "bspnodes");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->bspnodes = __to_ss<list<BSPNode *> *>(value);
    value = __ss_dict_lookup(state, "colormaps");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->colormaps = __to_ss<list<Colormap *> *>(value);
    value = __ss_dict_lookup(state, "entry_data");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->entry_data = __to_ss<dict<bytes *, bytes *> *>(value);
    value = __ss_dict_lookup(state, "linedefs");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->linedefs = __to_ss<list<Linedef *> *>(value);
    value = __ss_dict_lookup(state, "palette");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->palette = __to_ss<list<tuple<__ss_int> *> *>(value);
    value = __ss_dict_lookup(state, "patches");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->patches = __to_ss<list<Picture *> *>(value);
    value = __ss_dict_lookup(state, "player");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->player = __to_ss<Player *>(value);
    value = __ss_dict_lookup(state, "sectors");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->sectors = __to_ss<list<Sector *> *>(value);
    value = __ss_dict_lookup(state, "segs");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->segs = __to_ss<list<Seg *> *>(value);
    value = __ss_dict_lookup(state, "sidedefs");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->sidedefs = __to_ss<list<Sidedef *> *>(value);
    value = __ss_dict_lookup(state, "subsectors");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->subsectors = __to_ss<list<SubSector *> *>(value);
    value = __ss_dict_lookup(state, "textures");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->textures = __to_ss<dict<bytes *, Texture *> *>(value);
    value = __ss_dict_lookup(state, "things");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->things = __to_ss<list<Thing *> *>(value);
    value = __ss_dict_lookup(state, "vertices");
    if (value) ((__ss_doom_MapObject *)self)->__ss_object->vertices = __to_ss<list<Vertex *> *>(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {

/* class ClipBufferNode */

typedef struct {
    PyObject_HEAD
    __doom__::ClipBufferNode *__ss_object;
} __ss_doom_ClipBufferNodeObject;

static PyMemberDef __ss_doom_ClipBufferNodeMembers[] = {
    {NULL}
};

PyObject *__ss_doom_ClipBufferNode___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_int arg_0 = __ss_arg<__ss_int >("start", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("end", 1, 0, 0, args, kwargs);

        return __to_py(((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->__init__(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *__ss_doom_ClipBufferNode_checkSpan(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_int arg_0 = __ss_arg<__ss_int >("start", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("end", 1, 0, 0, args, kwargs);
        list<__ss_int> *arg_2 = __ss_arg<list<__ss_int> *>("result", 2, 0, 0, args, kwargs);
        __ss_bool arg_3 = __ss_arg<__ss_bool >("add", 3, 0, False, args, kwargs);

        return __to_py(((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->checkSpan(arg_0, arg_1, arg_2, arg_3));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods __ss_doom_ClipBufferNode_as_number = {
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

PyObject *__ss_doom_ClipBufferNode__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_doom_ClipBufferNode__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_doom_ClipBufferNodeMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_doom_ClipBufferNode__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_doom_ClipBufferNode__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_doom_ClipBufferNode___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"checkSpan", (PyCFunction)__ss_doom_ClipBufferNode_checkSpan, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_doom_ClipBufferNode___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_doom_ClipBufferNode___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_doom_ClipBufferNodeNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_doom_ClipBufferNodeObject *self = (__ss_doom_ClipBufferNodeObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __doom__::ClipBufferNode();
    self->__ss_object->__class__ = __doom__::cl_ClipBufferNode;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_doom_ClipBufferNodeDealloc(__ss_doom_ClipBufferNodeObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_doom_ClipBufferNode_end(__ss_doom_ClipBufferNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->end);
}

int __ss_set___ss_doom_ClipBufferNode_end(__ss_doom_ClipBufferNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->end = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_ClipBufferNode_left(__ss_doom_ClipBufferNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->left);
}

int __ss_set___ss_doom_ClipBufferNode_left(__ss_doom_ClipBufferNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->left = __to_ss<ClipBufferNode *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_ClipBufferNode_occluded(__ss_doom_ClipBufferNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->occluded);
}

int __ss_set___ss_doom_ClipBufferNode_occluded(__ss_doom_ClipBufferNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->occluded = __to_ss<__ss_bool >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_ClipBufferNode_partitionPoint(__ss_doom_ClipBufferNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->partitionPoint);
}

int __ss_set___ss_doom_ClipBufferNode_partitionPoint(__ss_doom_ClipBufferNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->partitionPoint = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_ClipBufferNode_partitioned(__ss_doom_ClipBufferNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->partitioned);
}

int __ss_set___ss_doom_ClipBufferNode_partitioned(__ss_doom_ClipBufferNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->partitioned = __to_ss<__ss_bool >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_ClipBufferNode_right(__ss_doom_ClipBufferNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->right);
}

int __ss_set___ss_doom_ClipBufferNode_right(__ss_doom_ClipBufferNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->right = __to_ss<ClipBufferNode *>(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_doom_ClipBufferNode_start(__ss_doom_ClipBufferNodeObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->start);
}

int __ss_set___ss_doom_ClipBufferNode_start(__ss_doom_ClipBufferNodeObject *self, PyObject *value, void *closure) {
    (void)closure;
    try {
        self->__ss_object->start = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_doom_ClipBufferNodeGetSet[] = {
    {(char *)"end", (getter)__ss_get___ss_doom_ClipBufferNode_end, (setter)__ss_set___ss_doom_ClipBufferNode_end, (char *)"", NULL},
    {(char *)"left", (getter)__ss_get___ss_doom_ClipBufferNode_left, (setter)__ss_set___ss_doom_ClipBufferNode_left, (char *)"", NULL},
    {(char *)"occluded", (getter)__ss_get___ss_doom_ClipBufferNode_occluded, (setter)__ss_set___ss_doom_ClipBufferNode_occluded, (char *)"", NULL},
    {(char *)"partitionPoint", (getter)__ss_get___ss_doom_ClipBufferNode_partitionPoint, (setter)__ss_set___ss_doom_ClipBufferNode_partitionPoint, (char *)"", NULL},
    {(char *)"partitioned", (getter)__ss_get___ss_doom_ClipBufferNode_partitioned, (setter)__ss_set___ss_doom_ClipBufferNode_partitioned, (char *)"", NULL},
    {(char *)"right", (getter)__ss_get___ss_doom_ClipBufferNode_right, (setter)__ss_set___ss_doom_ClipBufferNode_right, (char *)"", NULL},
    {(char *)"start", (getter)__ss_get___ss_doom_ClipBufferNode_start, (setter)__ss_set___ss_doom_ClipBufferNode_start, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_doom_ClipBufferNodeObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "doom.ClipBufferNode",
    sizeof( __ss_doom_ClipBufferNodeObject),
    0,
    (destructor) __ss_doom_ClipBufferNodeDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_doom_ClipBufferNode_as_number,
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
    __ss_doom_ClipBufferNodeMethods,
    __ss_doom_ClipBufferNodeMembers,
    __ss_doom_ClipBufferNodeGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_doom_ClipBufferNode___tpinit__,
    0,
    __ss_doom_ClipBufferNodeNew,
};

PyObject *__ss_doom_ClipBufferNode__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_doom, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_doom_ClipBufferNodeObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_doom_ClipBufferNodeObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "end", __to_py(((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->end));
    __ss_dict_steal(b, "left", __to_py(((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->left));
    __ss_dict_steal(b, "occluded", __to_py(((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->occluded));
    __ss_dict_steal(b, "partitionPoint", __to_py(((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->partitionPoint));
    __ss_dict_steal(b, "partitioned", __to_py(((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->partitioned));
    __ss_dict_steal(b, "right", __to_py(((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->right));
    __ss_dict_steal(b, "start", __to_py(((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->start));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_doom_ClipBufferNode__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "end");
    if (value) ((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->end = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "left");
    if (value) ((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->left = __to_ss<ClipBufferNode *>(value);
    value = __ss_dict_lookup(state, "occluded");
    if (value) ((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->occluded = __to_ss<__ss_bool >(value);
    value = __ss_dict_lookup(state, "partitionPoint");
    if (value) ((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->partitionPoint = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "partitioned");
    if (value) ((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->partitioned = __to_ss<__ss_bool >(value);
    value = __ss_dict_lookup(state, "right");
    if (value) ((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->right = __to_ss<ClipBufferNode *>(value);
    value = __ss_dict_lookup(state, "start");
    if (value) ((__ss_doom_ClipBufferNodeObject *)self)->__ss_object->start = __to_ss<__ss_int >(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __doom__

namespace __doom__ {
PyObject *Global_doom_get_special_light(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Sector *arg_0 = __ss_arg<Sector *>("sector", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("frame_count", 1, 0, 0, args, kwargs);

        return __to_py(__doom__::get_special_light(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *Global_doom_get_wall_colormap(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        list<Colormap *> *arg_0 = __ss_arg<list<Colormap *> *>("colormaps", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("currentZ", 1, 0, 0, args, kwargs);
        Seg *arg_2 = __ss_arg<Seg *>("seg", 2, 0, 0, args, kwargs);
        __ss_int arg_3 = __ss_arg<__ss_int >("frame_count", 3, 0, 0, args, kwargs);

        return __to_py(__doom__::get_wall_colormap(arg_0, arg_1, arg_2, arg_3));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *Global_doom_get_flat_colormap(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        list<Colormap *> *arg_0 = __ss_arg<list<Colormap *> *>("colormaps", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("currentZ", 1, 0, 0, args, kwargs);
        Seg *arg_2 = __ss_arg<Seg *>("seg", 2, 0, 0, args, kwargs);
        __ss_int arg_3 = __ss_arg<__ss_int >("frame_count", 3, 0, 0, args, kwargs);

        return __to_py(__doom__::get_flat_colormap(arg_0, arg_1, arg_2, arg_3));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *Global_doom_draw_wall_col(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        bytes *arg_0 = __ss_arg<bytes *>("drawsurf", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("x", 1, 0, 0, args, kwargs);
        __ss_int arg_2 = __ss_arg<__ss_int >("middleMinY", 2, 0, 0, args, kwargs);
        __ss_int arg_3 = __ss_arg<__ss_int >("middleMaxY", 3, 0, 0, args, kwargs);
        Texture *arg_4 = __ss_arg<Texture *>("wallTexture", 4, 0, 0, args, kwargs);
        __ss_float arg_5 = __ss_arg<__ss_float >("currentTextureX", 5, 0, 0, args, kwargs);
        __ss_float arg_6 = __ss_arg<__ss_float >("currentZ", 6, 0, 0, args, kwargs);
        __ss_float arg_7 = __ss_arg<__ss_float >("middleTextureY", 7, 0, 0, args, kwargs);
        __ss_float arg_8 = __ss_arg<__ss_float >("middleTextureYStep", 8, 0, 0, args, kwargs);
        Colormap *arg_9 = __ss_arg<Colormap *>("colormap", 9, 0, 0, args, kwargs);

        return __to_py(__doom__::draw_wall_col(arg_0, arg_1, arg_2, arg_3, arg_4, arg_5, arg_6, arg_7, arg_8, arg_9));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *Global_doom_draw_flat_col(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        bytes *arg_0 = __ss_arg<bytes *>("drawsurf", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("x", 1, 0, 0, args, kwargs);
        __ss_int arg_2 = __ss_arg<__ss_int >("ceilMin", 2, 0, 0, args, kwargs);
        __ss_int arg_3 = __ss_arg<__ss_int >("ceilMax", 3, 0, 0, args, kwargs);
        Seg *arg_4 = __ss_arg<Seg *>("seg", 4, 0, 0, args, kwargs);
        Player *arg_5 = __ss_arg<Player *>("player", 5, 0, 0, args, kwargs);
        list<list<__ss_int> *> *arg_6 = __ss_arg<list<list<__ss_int> *> *>("flatTexture", 6, 0, 0, args, kwargs);
        __ss_int arg_7 = __ss_arg<__ss_int >("flat_h", 7, 0, 0, args, kwargs);
        list<__ss_float> *arg_8 = __ss_arg<list<__ss_float> *>("INV", 8, 0, 0, args, kwargs);
        __ss_int arg_9 = __ss_arg<__ss_int >("sign", 9, 0, 0, args, kwargs);
        list<Colormap *> *arg_10 = __ss_arg<list<Colormap *> *>("colormaps", 10, 0, 0, args, kwargs);
        __ss_int arg_11 = __ss_arg<__ss_int >("frame_count", 11, 0, 0, args, kwargs);

        return __to_py(__doom__::draw_flat_col(arg_0, arg_1, arg_2, arg_3, arg_4, arg_5, arg_6, arg_7, arg_8, arg_9, arg_10, arg_11));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *Global_doom_draw_sky_col(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        bytes *arg_0 = __ss_arg<bytes *>("drawsurf", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("x", 1, 0, 0, args, kwargs);
        __ss_int arg_2 = __ss_arg<__ss_int >("upperMinY", 2, 0, 0, args, kwargs);
        __ss_int arg_3 = __ss_arg<__ss_int >("upperMaxY", 3, 0, 0, args, kwargs);
        Seg *arg_4 = __ss_arg<Seg *>("seg", 4, 0, 0, args, kwargs);
        Player *arg_5 = __ss_arg<Player *>("player", 5, 0, 0, args, kwargs);

        return __to_py(__doom__::draw_sky_col(arg_0, arg_1, arg_2, arg_3, arg_4, arg_5));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *Global_doom_draw_seg(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Seg *arg_0 = __ss_arg<Seg *>("seg", 0, 0, 0, args, kwargs);
        Map *arg_1 = __ss_arg<Map *>("map_", 1, 0, 0, args, kwargs);
        bytes *arg_2 = __ss_arg<bytes *>("drawsurf", 2, 0, 0, args, kwargs);
        __ss_int arg_3 = __ss_arg<__ss_int >("scrXA", 3, 0, 0, args, kwargs);
        __ss_int arg_4 = __ss_arg<__ss_int >("scrXB", 4, 0, 0, args, kwargs);
        ClipBufferNode *arg_5 = __ss_arg<ClipBufferNode *>("cbuffer", 5, 0, 0, args, kwargs);
        __ss_float arg_6 = __ss_arg<__ss_float >("za", 6, 0, 0, args, kwargs);
        __ss_float arg_7 = __ss_arg<__ss_float >("zb", 7, 0, 0, args, kwargs);
        __ss_float arg_8 = __ss_arg<__ss_float >("textureX0", 8, 0, 0, args, kwargs);
        __ss_float arg_9 = __ss_arg<__ss_float >("textureX1", 9, 0, 0, args, kwargs);
        Sidedef *arg_10 = __ss_arg<Sidedef *>("frontSidedef", 10, 0, 0, args, kwargs);
        list<__ss_int> *arg_11 = __ss_arg<list<__ss_int> *>("lowerOcclusion", 11, 0, 0, args, kwargs);
        list<__ss_int> *arg_12 = __ss_arg<list<__ss_int> *>("upperOcclusion", 12, 0, 0, args, kwargs);
        __ss_int arg_13 = __ss_arg<__ss_int >("frame_count", 13, 0, 0, args, kwargs);

        return __to_py(__doom__::draw_seg(arg_0, arg_1, arg_2, arg_3, arg_4, arg_5, arg_6, arg_7, arg_8, arg_9, arg_10, arg_11, arg_12, arg_13));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

PyObject *Global_doom_render(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        Map *arg_0 = __ss_arg<Map *>("map_", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("frame_count", 1, 0, 0, args, kwargs);

        return __to_py(__doom__::render(arg_0, arg_1));

    } catch (Exception *e) {
        PyErr_SetString(__to_py(e), ((e->message)?(e->message->c_str()):""));
        return 0;
    }
}

static PyNumberMethods Global_doom_as_number = {
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

static PyMethodDef Global_doomMethods[] = {
    {(char *)"__newobj__", (PyCFunction)__ss__newobj__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"get_special_light", (PyCFunction)Global_doom_get_special_light, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"get_wall_colormap", (PyCFunction)Global_doom_get_wall_colormap, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"get_flat_colormap", (PyCFunction)Global_doom_get_flat_colormap, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"draw_wall_col", (PyCFunction)Global_doom_draw_wall_col, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"draw_flat_col", (PyCFunction)Global_doom_draw_flat_col, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"draw_sky_col", (PyCFunction)Global_doom_draw_sky_col, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"draw_seg", (PyCFunction)Global_doom_draw_seg, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"render", (PyCFunction)Global_doom_render, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef Module_doom = {
    PyModuleDef_HEAD_INIT,
    "doom",   /* name of module */
    NULL,   /* module documentation, may be NULL */
    -1,     /* size of per-interpreter state of the module or -1 if the module keeps state in global variables. */
    Global_doomMethods
};

PyMODINIT_FUNC PyInit_doom(void) {

    __shedskin__::__init();
    __math__::__init();
    __struct__::__init();
    __time__::__init();
    __random__::__init();
    __doom__::__init();

    PyObject *m;

    if (PyType_Ready(&__ss_doom_VertexObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_SidedefObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_LinedefObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_SectorObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_SubSectorObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_SegObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_FlatObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_BSPNodeObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_ThingObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_PlayerObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_TextureObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_PictureObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_ColormapObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_Vec2ObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_MapObjectType) < 0)
        return NULL;

    if (PyType_Ready(&__ss_doom_ClipBufferNodeObjectType) < 0)
        return NULL;

    // create extension module
    __ss_mod_doom = m = PyModule_Create(&Module_doom);
    if (m == NULL)
        return NULL;

    // add global variables
    if (PyModule_AddObject(m, (char *)"CEIL_Y_INV", __to_py(__doom__::CEIL_Y_INV)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"FLOOR_Y_INV", __to_py(__doom__::FLOOR_Y_INV)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"HEIGHT", __to_py(__doom__::HEIGHT)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"HEIGHT_2", __to_py(__doom__::HEIGHT_2)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"HEIGHT_INV", __to_py(__doom__::HEIGHT_INV)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"OSCILLATION", __to_py(__doom__::OSCILLATION)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"TAN_45_DEG", __to_py(__doom__::TAN_45_DEG)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"WIDTH", __to_py(__doom__::WIDTH)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"WIDTH_2", __to_py(__doom__::WIDTH_2)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"map_", __to_py(__doom__::map_)) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    // add type objects
    Py_INCREF(&__ss_doom_VertexObjectType);
    if (PyModule_AddObject(m, "Vertex", (PyObject *) &__ss_doom_VertexObjectType) < 0) {
        Py_DECREF(&__ss_doom_VertexObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_SidedefObjectType);
    if (PyModule_AddObject(m, "Sidedef", (PyObject *) &__ss_doom_SidedefObjectType) < 0) {
        Py_DECREF(&__ss_doom_SidedefObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_LinedefObjectType);
    if (PyModule_AddObject(m, "Linedef", (PyObject *) &__ss_doom_LinedefObjectType) < 0) {
        Py_DECREF(&__ss_doom_LinedefObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_SectorObjectType);
    if (PyModule_AddObject(m, "Sector", (PyObject *) &__ss_doom_SectorObjectType) < 0) {
        Py_DECREF(&__ss_doom_SectorObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_SubSectorObjectType);
    if (PyModule_AddObject(m, "SubSector", (PyObject *) &__ss_doom_SubSectorObjectType) < 0) {
        Py_DECREF(&__ss_doom_SubSectorObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_SegObjectType);
    if (PyModule_AddObject(m, "Seg", (PyObject *) &__ss_doom_SegObjectType) < 0) {
        Py_DECREF(&__ss_doom_SegObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_FlatObjectType);
    if (PyModule_AddObject(m, "Flat", (PyObject *) &__ss_doom_FlatObjectType) < 0) {
        Py_DECREF(&__ss_doom_FlatObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_BSPNodeObjectType);
    if (PyModule_AddObject(m, "BSPNode", (PyObject *) &__ss_doom_BSPNodeObjectType) < 0) {
        Py_DECREF(&__ss_doom_BSPNodeObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_ThingObjectType);
    if (PyModule_AddObject(m, "Thing", (PyObject *) &__ss_doom_ThingObjectType) < 0) {
        Py_DECREF(&__ss_doom_ThingObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_PlayerObjectType);
    if (PyModule_AddObject(m, "Player", (PyObject *) &__ss_doom_PlayerObjectType) < 0) {
        Py_DECREF(&__ss_doom_PlayerObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_TextureObjectType);
    if (PyModule_AddObject(m, "Texture", (PyObject *) &__ss_doom_TextureObjectType) < 0) {
        Py_DECREF(&__ss_doom_TextureObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_PictureObjectType);
    if (PyModule_AddObject(m, "Picture", (PyObject *) &__ss_doom_PictureObjectType) < 0) {
        Py_DECREF(&__ss_doom_PictureObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_ColormapObjectType);
    if (PyModule_AddObject(m, "Colormap", (PyObject *) &__ss_doom_ColormapObjectType) < 0) {
        Py_DECREF(&__ss_doom_ColormapObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_Vec2ObjectType);
    if (PyModule_AddObject(m, "Vec2", (PyObject *) &__ss_doom_Vec2ObjectType) < 0) {
        Py_DECREF(&__ss_doom_Vec2ObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_MapObjectType);
    if (PyModule_AddObject(m, "Map", (PyObject *) &__ss_doom_MapObjectType) < 0) {
        Py_DECREF(&__ss_doom_MapObjectType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&__ss_doom_ClipBufferNodeObjectType);
    if (PyModule_AddObject(m, "ClipBufferNode", (PyObject *) &__ss_doom_ClipBufferNodeObjectType) < 0) {
        Py_DECREF(&__ss_doom_ClipBufferNodeObjectType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}


} // namespace __doom__

} // extern "C"
namespace __doom__ {

PyObject *Vertex::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_VertexObject *self = (__ss_doom_VertexObject *)(__ss_doom_VertexObjectType.tp_alloc(&__ss_doom_VertexObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Vertex *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_VertexObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Vertex expected)"));
    return ((__doom__::__ss_doom_VertexObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *Sidedef::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_SidedefObject *self = (__ss_doom_SidedefObject *)(__ss_doom_SidedefObjectType.tp_alloc(&__ss_doom_SidedefObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Sidedef *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_SidedefObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Sidedef expected)"));
    return ((__doom__::__ss_doom_SidedefObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *Linedef::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_LinedefObject *self = (__ss_doom_LinedefObject *)(__ss_doom_LinedefObjectType.tp_alloc(&__ss_doom_LinedefObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Linedef *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_LinedefObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Linedef expected)"));
    return ((__doom__::__ss_doom_LinedefObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *Sector::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_SectorObject *self = (__ss_doom_SectorObject *)(__ss_doom_SectorObjectType.tp_alloc(&__ss_doom_SectorObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Sector *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_SectorObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Sector expected)"));
    return ((__doom__::__ss_doom_SectorObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *SubSector::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_SubSectorObject *self = (__ss_doom_SubSectorObject *)(__ss_doom_SubSectorObjectType.tp_alloc(&__ss_doom_SubSectorObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::SubSector *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_SubSectorObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (SubSector expected)"));
    return ((__doom__::__ss_doom_SubSectorObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *Seg::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_SegObject *self = (__ss_doom_SegObject *)(__ss_doom_SegObjectType.tp_alloc(&__ss_doom_SegObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Seg *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_SegObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Seg expected)"));
    return ((__doom__::__ss_doom_SegObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *Flat::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_FlatObject *self = (__ss_doom_FlatObject *)(__ss_doom_FlatObjectType.tp_alloc(&__ss_doom_FlatObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Flat *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_FlatObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Flat expected)"));
    return ((__doom__::__ss_doom_FlatObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *BSPNode::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_BSPNodeObject *self = (__ss_doom_BSPNodeObject *)(__ss_doom_BSPNodeObjectType.tp_alloc(&__ss_doom_BSPNodeObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::BSPNode *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_BSPNodeObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (BSPNode expected)"));
    return ((__doom__::__ss_doom_BSPNodeObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *Thing::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_ThingObject *self = (__ss_doom_ThingObject *)(__ss_doom_ThingObjectType.tp_alloc(&__ss_doom_ThingObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Thing *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_ThingObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Thing expected)"));
    return ((__doom__::__ss_doom_ThingObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *Player::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_PlayerObject *self = (__ss_doom_PlayerObject *)(__ss_doom_PlayerObjectType.tp_alloc(&__ss_doom_PlayerObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Player *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_PlayerObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Player expected)"));
    return ((__doom__::__ss_doom_PlayerObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *Texture::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_TextureObject *self = (__ss_doom_TextureObject *)(__ss_doom_TextureObjectType.tp_alloc(&__ss_doom_TextureObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Texture *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_TextureObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Texture expected)"));
    return ((__doom__::__ss_doom_TextureObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *Picture::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_PictureObject *self = (__ss_doom_PictureObject *)(__ss_doom_PictureObjectType.tp_alloc(&__ss_doom_PictureObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Picture *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_PictureObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Picture expected)"));
    return ((__doom__::__ss_doom_PictureObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *Colormap::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_ColormapObject *self = (__ss_doom_ColormapObject *)(__ss_doom_ColormapObjectType.tp_alloc(&__ss_doom_ColormapObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Colormap *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_ColormapObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Colormap expected)"));
    return ((__doom__::__ss_doom_ColormapObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *Vec2::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_Vec2Object *self = (__ss_doom_Vec2Object *)(__ss_doom_Vec2ObjectType.tp_alloc(&__ss_doom_Vec2ObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Vec2 *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_Vec2ObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Vec2 expected)"));
    return ((__doom__::__ss_doom_Vec2Object *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *Map::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_MapObject *self = (__ss_doom_MapObject *)(__ss_doom_MapObjectType.tp_alloc(&__ss_doom_MapObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::Map *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_MapObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (Map expected)"));
    return ((__doom__::__ss_doom_MapObject *)p)->__ss_object;
}
}
namespace __doom__ {

PyObject *ClipBufferNode::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_doom_ClipBufferNodeObject *self = (__ss_doom_ClipBufferNodeObject *)(__ss_doom_ClipBufferNodeObjectType.tp_alloc(&__ss_doom_ClipBufferNodeObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __doom__::ClipBufferNode *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__doom__::__ss_doom_ClipBufferNodeObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (ClipBufferNode expected)"));
    return ((__doom__::__ss_doom_ClipBufferNodeObject *)p)->__ss_object;
}
}
int main(int, char **) {
    __shedskin__::__init();
    __math__::__init();
    __struct__::__init();
    __time__::__init();
    __random__::__init();
    __shedskin__::__start(__doom__::__init);
}
