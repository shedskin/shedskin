#include "builtin.hpp"
#include "itertools.hpp"
#include "math/__init__.hpp"
#include "random.hpp"
#include "time.hpp"
#include "optimiserlib.hpp"

/**
Convert and optimise images for display in an Acorn Electron MODE 1 variant
with four colours per line but eight colours available for selection on each
line.
Copyright (C) 2015 Paul Boddie <paul@boddie.org.uk>
This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

namespace __optimiserlib__ {

str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_2, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;

using __random__::random;
using __random__::randrange;

UnicodeDecodeError *__exception3;
UnicodeEncodeError *__exception4;
file *__file;
__ss_int __void;
str *__name__;
list<tuple<__ss_int> *> *bases, *corners, *data;
__iter<tuple<__ss_float> *> *scaled_corners;
list<tuple2<tuple<__ss_int> *, tuple<__ss_float> *> *> *zipped_corners;
list<tuple<tuple<__ss_int> *> *> *base_complements;
tuple<__ss_int> *rgb;
SimpleImage *im, *im2;


list<tuple<__ss_int> *> * default_0;
list<tuple<__ss_int> *> * default_1;
static inline list<tuple2<tuple<__ss_int> *, __ss_float> *> *list_comp_0(list<tuple2<__ss_float, tuple<__ss_int> *> *> *d);
static inline list<tuple2<__ss_float, tuple<__ss_int> *> *> *list_comp_1(dict<tuple<__ss_int> *, __ss_float> *dd);
static inline list<tuple2<__ss_float, tuple<__ss_int> *> *> *list_comp_2(list<tuple<__ss_int> *> *chosen, tuple<__ss_int> *rgb);
static inline __ss_float  list_comp_3(list<tuple2<__ss_float, tuple<__ss_int> *> *> *l);
static inline list<tuple2<__ss_float, tuple<__ss_int> *> *> *list_comp_4(dict<tuple<__ss_int> *, __ss_float> *c, __ss_int width);
static inline list<tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *list_comp_5(list<tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *> *all);
static inline list<tuple<__ss_int> *> *list_comp_6(list<tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *> *suggestions);
static inline list<tuple<__ss_int> *> *list_comp_7(tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *l);
static inline __ss_int __lambda2__(__ss_float a);

static inline list<tuple2<tuple<__ss_int> *, __ss_float> *> *list_comp_0(list<tuple2<__ss_float, tuple<__ss_int> *> *> *d) {
    tuple2<__ss_float, tuple<__ss_int> *> *__10;
    __ss_float f;
    tuple<__ss_int> *value;
    list<tuple2<__ss_float, tuple<__ss_int> *> *> *__11;
    __iter<tuple2<__ss_float, tuple<__ss_int> *> *> *__12;
    __ss_int __13;
    list<tuple2<__ss_float, tuple<__ss_int> *> *>::for_in_loop __14;

    list<tuple2<tuple<__ss_int> *, __ss_float> *> *__ss_result = new list<tuple2<tuple<__ss_int> *, __ss_float> *>();

    __ss_result->resize(len(d));
    FOR_IN(__10,d,11,13,14)
        __10 = __10;
        __SS_UNPACK_CHECK(__10, 2);
        f = __10->__getfirst__();
        value = __10->__getsecond__();
        __ss_result->units[__13] = (__SS_NEW tuple2<tuple<__ss_int> *, __ss_float>(2,value,f));
    END_FOR

    return __ss_result;
}

static inline list<tuple2<__ss_float, tuple<__ss_int> *> *> *list_comp_1(dict<tuple<__ss_int> *, __ss_float> *dd) {
    tuple2<tuple<__ss_int> *, __ss_float> *__24;
    tuple<__ss_int> *value;
    __ss_float f;
    __iter<tuple2<tuple<__ss_int> *, __ss_float> *> *__25, *__26;
    __ss_int __27;
    __iter<tuple2<tuple<__ss_int> *, __ss_float> *>::for_in_loop __28;
    __GC_DICT<tuple<__ss_int> *, __ss_float>::iterator __29;
    dict<tuple<__ss_int> *, __ss_float> *__30;

    list<tuple2<__ss_float, tuple<__ss_int> *> *> *__ss_result = new list<tuple2<__ss_float, tuple<__ss_int> *> *>();

    FOR_IN_DICT(dd,30,29,27)
        value = (*__29).first;
        f = (*__29).second;
        __29++;
        __append_reserve(__ss_result, __30, len(__ss_result), 1);
        __ss_result->append((__SS_NEW tuple2<__ss_float, tuple<__ss_int> *>(2,f,value)));
    END_FOR

    return __ss_result;
}

static inline list<tuple2<__ss_float, tuple<__ss_int> *> *> *list_comp_2(list<tuple<__ss_int> *> *chosen, tuple<__ss_int> *rgb) {
    tuple2<__ss_float, tuple<__ss_int> *> *__42;
    __ss_float f;
    tuple<__ss_int> *value;
    list<tuple2<__ss_float, tuple<__ss_int> *> *> *__43;
    __iter<tuple2<__ss_float, tuple<__ss_int> *> *> *__44;
    __ss_int __45;
    list<tuple2<__ss_float, tuple<__ss_int> *> *>::for_in_loop __46;
    __ss_bool __47, __48;

    list<tuple2<__ss_float, tuple<__ss_int> *> *> *__ss_result = new list<tuple2<__ss_float, tuple<__ss_int> *> *>();

    __43 = combination(rgb);
    __ss_result->units.reserve(4);
    FOR_IN(__42,__43,43,45,46)
        __42 = __42;
        __SS_UNPACK_CHECK(__42, 2);
        f = __42->__getfirst__();
        value = __42->__getsecond__();
        if ((__NOT(___bool(chosen)) or (chosen)->__contains__(value))) {
            __ss_result->append((__SS_NEW tuple2<__ss_float, tuple<__ss_int> *>(2,f,value)));
        }
    END_FOR

    return __ss_result;
}

static inline __ss_float  list_comp_3(list<tuple2<__ss_float, tuple<__ss_int> *> *> *l) {
    tuple2<__ss_float, tuple<__ss_int> *> *__49;
    __ss_float f;
    tuple<__ss_int> *c;
    list<tuple2<__ss_float, tuple<__ss_int> *> *> *__50;
    __iter<tuple2<__ss_float, tuple<__ss_int> *> *> *__51;
    __ss_int __52;
    list<tuple2<__ss_float, tuple<__ss_int> *> *>::for_in_loop __53;

    __ss_float __ss_result = __zero<__ss_float >();

    FOR_IN(__49,l,50,52,53)
        __49 = __49;
        __SS_UNPACK_CHECK(__49, 2);
        f = __49->__getfirst__();
        c = __49->__getsecond__();
        __ss_result = __add(__ss_result, f);
    END_FOR

    return __ss_result;
}

static inline list<tuple2<__ss_float, tuple<__ss_int> *> *> *list_comp_4(dict<tuple<__ss_int> *, __ss_float> *c, __ss_int width) {
    tuple2<tuple<__ss_int> *, __ss_float> *__69;
    tuple<__ss_int> *value;
    __ss_float n;
    __iter<tuple2<tuple<__ss_int> *, __ss_float> *> *__70, *__71;
    __ss_int __72;
    __iter<tuple2<tuple<__ss_int> *, __ss_float> *>::for_in_loop __73;
    __GC_DICT<tuple<__ss_int> *, __ss_float>::iterator __74;
    dict<tuple<__ss_int> *, __ss_float> *__75;

    list<tuple2<__ss_float, tuple<__ss_int> *> *> *__ss_result = new list<tuple2<__ss_float, tuple<__ss_int> *> *>();

    FOR_IN_DICT(c,75,74,72)
        value = (*__74).first;
        n = (*__74).second;
        __74++;
        __append_reserve(__ss_result, __75, len(__ss_result), 1);
        __ss_result->append((__SS_NEW tuple2<__ss_float, tuple<__ss_int> *>(2,__divs(n, width),value)));
    END_FOR

    return __ss_result;
}

static inline list<tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *list_comp_5(list<tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *> *all) {
    tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *__87;
    __ss_float total;
    tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *l;
    list<tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *> *__88;
    __iter<tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *> *__89;
    __ss_int __90;
    list<tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *>::for_in_loop __91;

    list<tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *__ss_result = new list<tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *>();

    __ss_result->resize(len(all));
    FOR_IN(__87,all,88,90,91)
        __87 = __87;
        __SS_UNPACK_CHECK(__87, 2);
        total = __87->__getfirst__();
        l = __87->__getsecond__();
        __ss_result->units[__90] = l;
    END_FOR

    return __ss_result;
}

static inline list<tuple<__ss_int> *> *list_comp_6(list<tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *> *suggestions) {
    tuple2<__ss_float, tuple<__ss_int> *> *__116;
    __ss_float f;
    tuple<__ss_int> *value;
    tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *__117;
    __iter<tuple2<__ss_float, tuple<__ss_int> *> *> *__118;
    __ss_int __119;
    tuple<tuple2<__ss_float, tuple<__ss_int> *> *>::for_in_loop __120;

    list<tuple<__ss_int> *> *__ss_result = new list<tuple<__ss_int> *>();

    __117 = suggestions->__getfast__(__ss_int(0LL))->__getsecond__();
    __ss_result->resize(len(__117));
    FOR_IN(__116,__117,117,119,120)
        __116 = __116;
        __SS_UNPACK_CHECK(__116, 2);
        f = __116->__getfirst__();
        value = __116->__getsecond__();
        __ss_result->units[__119] = value;
    END_FOR

    return __ss_result;
}

static inline list<tuple<__ss_int> *> *list_comp_7(tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *l) {
    tuple2<__ss_float, tuple<__ss_int> *> *__121;
    __ss_float f;
    tuple<__ss_int> *value;
    tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *__122;
    __iter<tuple2<__ss_float, tuple<__ss_int> *> *> *__123;
    __ss_int __124;
    tuple<tuple2<__ss_float, tuple<__ss_int> *> *>::for_in_loop __125;

    list<tuple<__ss_int> *> *__ss_result = new list<tuple<__ss_int> *>();

    __ss_result->resize(len(l));
    FOR_IN(__121,l,122,124,125)
        __121 = __121;
        __SS_UNPACK_CHECK(__121, 2);
        f = __121->__getfirst__();
        value = __121->__getsecond__();
        __ss_result->units[__124] = value;
    END_FOR

    return __ss_result;
}

static inline __ss_int __lambda2__(__ss_float a) {
    return __int(a);
}

__ss_float within(__ss_float v, __ss_int lower, __ss_int upper) {
    return ___min(2, __ss_void, (__ss_float(__ss_int(0LL))), ___max(2, __ss_void, (__ss_float(__ss_int(0LL))), v, (__ss_float(lower))), (__ss_float(upper)));
}

__ss_int clip(__ss_float v) {
    return __int(within(v, __ss_int(0LL), __ss_int(255LL)));
}

__ss_float distance(tuple<__ss_int> *rgb1, tuple<__ss_int> *rgb2) {
    return __math__::sqrt(((__power(__abs((rgb1->__getitem__(__ss_int(0LL))-rgb2->__getitem__(__ss_int(0LL)))), __ss_int(2LL))+__power(__abs((rgb1->__getitem__(__ss_int(1LL))-rgb2->__getitem__(__ss_int(1LL)))), __ss_int(2LL)))+__power(__abs((rgb1->__getitem__(__ss_int(2LL))-rgb2->__getitem__(__ss_int(2LL)))), __ss_int(2LL))));
}

tuple<__ss_int> *restore(tuple<__ss_float> *srgb) {
    __ss_float b, g, r;
    tuple<__ss_float> *__0;

    __0 = srgb;
    __SS_UNPACK_CHECK(__0, 3);
    r = __0->__getitem__(0);
    g = __0->__getitem__(1);
    b = __0->__getitem__(2);
    return (__SS_NEW tuple<__ss_int>(3,__int((r*__ss_float(255.0))),__int((g*__ss_float(255.0))),__int((b*__ss_float(255.0)))));
}

tuple<__ss_float> *scale(tuple<__ss_int> *rgb) {
    __ss_int b, g, r;
    tuple<__ss_int> *__1;

    __1 = rgb;
    __SS_UNPACK_CHECK(__1, 3);
    r = __1->__getitem__(0);
    g = __1->__getitem__(1);
    b = __1->__getitem__(2);
    return (__SS_NEW tuple<__ss_float>(3,(r/__ss_float(255.0)),(g/__ss_float(255.0)),(b/__ss_float(255.0))));
}

tuple<__ss_float> *invert(tuple<__ss_float> *srgb) {
    __ss_float b, g, r;
    tuple<__ss_float> *__2;

    __2 = srgb;
    __SS_UNPACK_CHECK(__2, 3);
    r = __2->__getitem__(0);
    g = __2->__getitem__(1);
    b = __2->__getitem__(2);
    return (__SS_NEW tuple<__ss_float>(3,(__ss_float(1.0)-r),(__ss_float(1.0)-g),(__ss_float(1.0)-b)));
}

list<tuple2<__ss_float, tuple<__ss_int> *> *> *combination(tuple<__ss_int> *rgb) {
    /**
    Return the colour distribution for 'rgb'.
    */
    tuple<__ss_float> *__8, *rgbi, *scaled, *srgb;
    list<tuple<__ss_float> *> *pairs;
    list<tuple2<__ss_float, tuple<__ss_int> *> *> *d;
    tuple<__ss_int> *corner;
    __ss_float bs, gs, rs;
    tuple2<tuple<__ss_int> *, tuple<__ss_float> *> *__3;
    list<tuple2<tuple<__ss_int> *, tuple<__ss_float> *> *> *__4;
    __iter<tuple2<tuple<__ss_int> *, tuple<__ss_float> *> *> *__5;
    __ss_int __6;
    list<tuple2<tuple<__ss_int> *, tuple<__ss_float> *> *>::for_in_loop __7;

    srgb = scale(rgb);
    rgbi = invert(srgb);
    pairs = (__SS_NEW list<tuple<__ss_float> *>(__zip(2, False, rgbi, srgb)));
    d = (__ss_list<tuple2<__ss_float, tuple<__ss_int> *> *>());

    FOR_IN(__3,__optimiserlib__::zipped_corners,4,6,7)
        __3 = __3;
        __SS_UNPACK_CHECK(__3, 2);
        corner = __3->__getfirst__();
        scaled = __3->__getsecond__();
        __8 = scaled;
        __SS_UNPACK_CHECK(__8, 3);
        rs = __8->__getfast__(0);
        gs = __8->__getfast__(1);
        bs = __8->__getfast__(2);
        __append_reserve(d, __4, __6, 1);
        d->append((__SS_NEW tuple2<__ss_float, tuple<__ss_int> *>(2,(((pairs->__getfast__(__ss_int(0LL)))->__getitem__(__int(rs))*(pairs->__getfast__(__ss_int(1LL)))->__getitem__(__int(gs)))*(pairs->__getfast__(__ss_int(2LL)))->__getitem__(__int(bs))),corner)));
    END_FOR

    return balance(d);
}

tuple<tuple<__ss_int> *> *complements(tuple<__ss_int> *rgb) {
    /**
    Return 'rgb' and its complement.
    */
    __ss_int b, g, r;
    tuple<__ss_int> *__9;

    __9 = rgb;
    __SS_UNPACK_CHECK(__9, 3);
    r = __9->__getfast__(0);
    g = __9->__getfast__(1);
    b = __9->__getfast__(2);
    return (__SS_NEW tuple<tuple<__ss_int> *>(2,rgb,restore(invert(scale(rgb)))));
}

list<tuple2<__ss_float, tuple<__ss_int> *> *> *balance(list<tuple2<__ss_float, tuple<__ss_int> *> *> *d) {
    /**
    Balance distribution 'd', cancelling opposing values and their complements
    and replacing their common contributions with black and white contributions.
    */
    dict<tuple<__ss_int> *, __ss_float> *__20, *__22, *dd;
    tuple<__ss_int> *__21, *__23, *primary, *secondary;
    __ss_float common;
    tuple<tuple<__ss_int> *> *__15;
    list<tuple<tuple<__ss_int> *> *> *__16;
    __iter<tuple<tuple<__ss_int> *> *> *__17;
    __ss_int __18;
    list<tuple<tuple<__ss_int> *> *>::for_in_loop __19;

    dd = (__SS_NEW dict<tuple<__ss_int> *, __ss_float>(list_comp_0(d)));

    FOR_IN(__15,__optimiserlib__::base_complements,16,18,19)
        __15 = __15;
        __SS_UNPACK_CHECK(__15, 2);
        primary = __15->__getfirst__();
        secondary = __15->__getsecond__();
        common = ___min(2, __ss_void, (__ss_float(__ss_int(0LL))), dd->__getitem__(primary), dd->__getitem__(secondary));
        __20 = dd;
        __21 = primary;
        __20->__setitem__(__21, (__20->__getitem__(__21)-common));
        __22 = dd;
        __23 = secondary;
        __22->__setitem__(__23, (__22->__getitem__(__23)-common));
    END_FOR

    return list_comp_1(dd);
}

tuple<__ss_int> *combine(list<tuple2<__ss_float, tuple<__ss_int> *> *> *d) {
    /**
    Combine distribution 'd' to get a colour value.
    */
    list<__ss_float> *__36, *__38, *__40, *out;
    __ss_float v;
    tuple<__ss_int> *rgb;
    tuple2<__ss_float, tuple<__ss_int> *> *__31;
    list<tuple2<__ss_float, tuple<__ss_int> *> *> *__32;
    __iter<tuple2<__ss_float, tuple<__ss_int> *> *> *__33;
    __ss_int __34, __37, __39, __41;
    list<tuple2<__ss_float, tuple<__ss_int> *> *>::for_in_loop __35;

    out = (__SS_NEW list<__ss_float>(3,((__ss_float)(__ss_int(0LL))),((__ss_float)(__ss_int(0LL))),((__ss_float)(__ss_int(0LL)))));

    FOR_IN(__31,d,32,34,35)
        __31 = __31;
        __SS_UNPACK_CHECK(__31, 2);
        v = __31->__getfirst__();
        rgb = __31->__getsecond__();
        __36 = out;
        __37 = __ss_int(0LL);
        __36->__setitem__(__37, (__36->__getfast__(__37)+(v*rgb->__getfast__(__ss_int(0LL)))));
        __38 = out;
        __39 = __ss_int(1LL);
        __38->__setitem__(__39, (__38->__getfast__(__39)+(v*rgb->__getfast__(__ss_int(1LL)))));
        __40 = out;
        __41 = __ss_int(2LL);
        __40->__setitem__(__41, (__40->__getfast__(__41)+(v*rgb->__getfast__(__ss_int(2LL)))));
    END_FOR

    return (__SS_NEW tuple<__ss_int>(map(1, False, __lambda2__, out)));
}

list<tuple2<__ss_float, tuple<__ss_int> *> *> *pattern(tuple<__ss_int> *rgb, list<tuple<__ss_int> *> *chosen) {
    /**
    Obtain a sorted colour distribution for 'rgb', optionally limited to any
    specified 'chosen' colours.
    */
    list<tuple2<__ss_float, tuple<__ss_int> *> *> *l;

    l = list_comp_2(chosen, rgb);
    l->sort(__ss_int(0LL), __ss_int(0LL), True);
    return l;
}

tuple<__ss_int> *get_value(tuple<__ss_int> *rgb, list<tuple<__ss_int> *> *chosen, __ss_bool fail) {
    /**
    Get an output colour for 'rgb', optionally limited to any specified 'chosen'
    colours. If 'fail' is set to a true value, return None if the colour cannot
    be expressed using any of the chosen colours.
    */
    list<tuple2<__ss_float, tuple<__ss_int> *> *> *__55, *l;
    __ss_float choose, f, limit, threshold;
    tuple<__ss_int> *c;
    tuple2<__ss_float, tuple<__ss_int> *> *__54;
    __iter<tuple2<__ss_float, tuple<__ss_int> *> *> *__56;
    __ss_int __57;
    list<tuple2<__ss_float, tuple<__ss_int> *> *>::for_in_loop __58;

    l = pattern(rgb, chosen);
    limit = list_comp_3(l);
    if (__NOT(___bool(limit))) {
        if (fail) {
            return NULL;
        }
        else {
            return l->__getfast__(randrange(__ss_int(0LL), len(l)))->__getsecond__();
        }
    }
    choose = (random()*limit);
    threshold = ((__ss_float)(__ss_int(0LL)));

    FOR_IN(__54,l,55,57,58)
        __54 = __54;
        __SS_UNPACK_CHECK(__54, 2);
        f = __54->__getfirst__();
        c = __54->__getsecond__();
        threshold = (threshold+f);
        if ((choose<threshold)) {
            return c;
        }
    END_FOR

    return c;
}

__ss_int sign(__ss_float x) {
    if ((x>=((__ss_float)(__ss_int(0LL))))) {
        return __ss_int(1LL);
    }
    else {
        return (-__ss_int(1LL));
    }
    return 0;
}

tuple<__ss_int> *saturate_rgb(tuple<__ss_int> *rgb, __ss_float exp) {
    __ss_int b, g, r;
    tuple<__ss_int> *__59;

    __59 = rgb;
    __SS_UNPACK_CHECK(__59, 3);
    r = __59->__getitem__(0);
    g = __59->__getitem__(1);
    b = __59->__getitem__(2);
    return (__SS_NEW tuple<__ss_int>(3,saturate_value(r, exp),saturate_value(g, exp),saturate_value(b, exp)));
}

__ss_int saturate_value(__ss_int x, __ss_float exp) {
    return __int((__ss_float(127.5)+((sign((x-__ss_float(127.5)))*__ss_float(127.5))*__power((__abs((x-__ss_float(127.5)))/__ss_float(127.5)), exp))));
}

tuple<__ss_int> *amplify_rgb(tuple<__ss_int> *rgb, __ss_float exp) {
    __ss_int b, g, r;
    tuple<__ss_int> *__60;

    __60 = rgb;
    __SS_UNPACK_CHECK(__60, 3);
    r = __60->__getitem__(0);
    g = __60->__getitem__(1);
    b = __60->__getitem__(2);
    return (__SS_NEW tuple<__ss_int>(3,amplify_value(r, exp),amplify_value(g, exp),amplify_value(b, exp)));
}

__ss_int amplify_value(__ss_int x, __ss_float exp) {
    return __int((__power((x/__ss_float(255.0)), exp)*__ss_float(255.0)));
}

list<tuple2<__ss_float, tuple<__ss_int> *> *> *get_colours(SimpleImage *im, __ss_int y) {
    /**
    Get a colour distribution from image 'im' for the row 'y'.
    */
    __ss_int __65, height, width, x;
    dict<tuple<__ss_int> *, __ss_float> *__67, *c;
    tuple<__ss_int> *__61, *__68, *rgb, *value;
    __ss_float f;
    list<tuple2<__ss_float, tuple<__ss_int> *> *> *__63, *d;
    tuple2<__ss_float, tuple<__ss_int> *> *__62;
    __iter<tuple2<__ss_float, tuple<__ss_int> *> *> *__64;
    list<tuple2<__ss_float, tuple<__ss_int> *> *>::for_in_loop __66;

    __61 = im->size;
    __SS_UNPACK_CHECK(__61, 2);
    width = __61->__getfirst__();
    height = __61->__getsecond__();
    c = (__SS_NEW dict<tuple<__ss_int> *, __ss_float>());
    x = __ss_int(0LL);

    while ((x<width)) {
        rgb = im->getpixel((__ss_tuple_int(2,x,y)));

        FOR_IN(__62,combination(rgb),63,65,66)
            __62 = __62;
            __SS_UNPACK_CHECK(__62, 2);
            f = __62->__getfirst__();
            value = __62->__getsecond__();
            if ((!(c)->__contains__(value))) {
                c->__setitem__(value, f);
            }
            else {
                c->__addtoitem__(value, f);
            }
        END_FOR

        x = (x+__ss_int(1LL));
    }
    d = list_comp_4(c, width);
    d->sort(__ss_int(0LL), __ss_int(0LL), True);
    return d;
}

list<tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *get_combinations(list<tuple2<__ss_float, tuple<__ss_int> *> *> *c, __ss_int n) {
    /**
    Get combinations of colours from 'c' of size 'n' in decreasing order of
    probability.
    */
    list<tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *> *all;
    tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *__83, *l;
    __ss_float f, total;
    tuple<__ss_int> *value;
    __iter<tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *__76, *__77;
    __ss_int __78, __85;
    __iter<tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *>::for_in_loop __79;
    void *__80, *__81;
    tuple2<__ss_float, tuple<__ss_int> *> *__82;
    __iter<tuple2<__ss_float, tuple<__ss_int> *> *> *__84;
    tuple<tuple2<__ss_float, tuple<__ss_int> *> *>::for_in_loop __86;

    all = (__ss_list<tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *>());

    FOR_IN(l,__itertools__::combinations(c, n),76,78,79)
        total = ((__ss_float)(__ss_int(0LL)));

        FOR_IN(__82,l,83,85,86)
            __82 = __82;
            __SS_UNPACK_CHECK(__82, 2);
            f = __82->__getfirst__();
            value = __82->__getsecond__();
            total = (total+f);
        END_FOR

        all->append((__SS_NEW tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *>(2,total,l)));
    END_FOR

    all->sort(__ss_int(0LL), __ss_int(0LL), True);
    return list_comp_5(all);
}

tuple2<__ss_int, set<tuple<__ss_int> *> *> *count_colours(SimpleImage *im, __ss_int colours) {
    /**
    Count colours on each row of image 'im', returning a tuple indicating the
    first row with more than the given number of 'colours' together with the
    found colours; otherwise returning None.
    */
    __ss_int height, width, x, y;
    set<tuple<__ss_int> *> *l;
    tuple<__ss_int> *__92;

    __92 = im->size;
    __SS_UNPACK_CHECK(__92, 2);
    width = __92->__getfirst__();
    height = __92->__getsecond__();
    y = __ss_int(0LL);

    while ((y<height)) {
        l = (__SS_NEW set<tuple<__ss_int> *>());
        x = __ss_int(0LL);

        while ((x<width)) {
            l->add(im->getpixel((__ss_tuple_int(2,x,y))));
            x = (x+__ss_int(1LL));
        }
        if ((len(l)>colours)) {
            return (__SS_NEW tuple2<__ss_int, set<tuple<__ss_int> *> *>(2,y,l));
        }
        y = (y+__ss_int(1LL));
    }
    return NULL;
}

void *process_image(SimpleImage *im, __ss_float saturate, __ss_float desaturate, __ss_float darken, __ss_float brighten) {
    /**
    Process image 'im' using the given options: 'saturate', 'desaturate',
    'darken', 'brighten'.
    */
    __ss_int height, width, x, y;
    tuple<__ss_int> *__93, *rgb;
    __ss_float __100, __101, __102, __103, __104, __105, __106, __107, __108, __109, __94, __95, __96, __97, __98, __99;

    __93 = im->size;
    __SS_UNPACK_CHECK(__93, 2);
    width = __93->__getfirst__();
    height = __93->__getsecond__();
    if ((___bool(saturate) or ___bool(desaturate) or ___bool(darken) or ___bool(brighten))) {
        y = __ss_int(0LL);

        while ((y<height)) {
            x = __ss_int(0LL);

            while ((x<width)) {
                rgb = im->getpixel((__ss_tuple_int(2,x,y)));
                if ((___bool(saturate) or ___bool(desaturate))) {
                    rgb = saturate_rgb(rgb, __OR(__AND(saturate, __divs(__ss_float(0.5), saturate), 100), (__ss_float(2.0)*desaturate), 102));
                }
                if ((___bool(darken) or ___bool(brighten))) {
                    rgb = amplify_rgb(rgb, __OR(__AND(brighten, __divs(__ss_float(0.5), brighten), 106), (__ss_float(2.0)*darken), 108));
                }
                im->putpixel((__ss_tuple_int(2,x,y)), rgb);
                x = (x+__ss_int(1LL));
            }
            y = (y+__ss_int(1LL));
        }
    }
    return NULL;
}

void *convert_image(SimpleImage *im, __ss_int colours, __ss_bool least_error) {
    /**
    Convert image 'im' to an appropriate output representation.
    */
    __ss_int __113, __115, height, width, x, y;
    list<tuple2<__ss_float, tuple<__ss_int> *> *> *c;
    list<tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *> *suggestions;
    tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *l;
    list<tuple<__ss_int> *> *most;
    __ss_float error;
    tuple<__ss_int> *__110, *rgb, *rgbn, *value;
    list<tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *__111;
    __iter<tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *__112;
    list<tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *>::for_in_loop __114;
    __ss_bool __126, __127;

    __110 = im->size;
    __SS_UNPACK_CHECK(__110, 2);
    width = __110->__getfirst__();
    height = __110->__getsecond__();
    y = __ss_int(0LL);

    while ((y<height)) {
        c = get_colours(im, y);
        suggestions = (__ss_list<tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *> *>());

        __115 = 0;
        FOR_IN(l,get_combinations(c, colours),111,113,114)
            most = list_comp_7(l);
            error = ((__ss_float)(__ss_int(0LL)));
            x = __ss_int(0LL);

            while ((x<width)) {
                rgb = im->getpixel((__ss_tuple_int(2,x,y)));
                value = get_value(rgb, most, False);
                if (least_error) {
                    error = (error+distance(value, rgb));
                }
                else if ((value==NULL)) {
                    error = (error+__ss_int(1LL));
                }
                x = (x+__ss_int(1LL));
            }
            if ((__NOT(least_error) and __NOT(___bool(error)))) {
                __115 = 1;
                break;
            }
            suggestions->append((__SS_NEW tuple2<__ss_float, tuple<tuple2<__ss_float, tuple<__ss_int> *> *> *>(2,error,l)));
        END_FOR
        if (!__115) {
            suggestions->sort(__ss_int(0LL), __ss_int(0LL), __ss_int(0LL));
            most = list_comp_6(suggestions);
        }

        x = __ss_int(0LL);

        while ((x<width)) {
            rgb = im->getpixel((__ss_tuple_int(2,x,y)));
            value = get_value(rgb, most, False);
            im->putpixel((__ss_tuple_int(2,x,y)), value);
            if ((x<(width-__ss_int(1LL)))) {
                rgbn = im->getpixel((__ss_tuple_int(2,(x+__ss_int(1LL)),y)));
                rgbn = (__SS_NEW tuple<__ss_int>(3,clip((rgbn->__getitem__(__ss_int(0LL))+((rgb->__getitem__(__ss_int(0LL))-value->__getitem__(__ss_int(0LL)))/__ss_float(4.0)))),clip((rgbn->__getitem__(__ss_int(1LL))+((rgb->__getitem__(__ss_int(1LL))-value->__getitem__(__ss_int(1LL)))/__ss_float(4.0)))),clip((rgbn->__getitem__(__ss_int(2LL))+((rgb->__getitem__(__ss_int(2LL))-value->__getitem__(__ss_int(2LL)))/__ss_float(4.0))))));
                im->putpixel((__ss_tuple_int(2,(x+__ss_int(1LL)),y)), rgbn);
            }
            if ((y<(height-__ss_int(1LL)))) {
                rgbn = im->getpixel((__ss_tuple_int(2,x,(y+__ss_int(1LL)))));
                rgbn = (__SS_NEW tuple<__ss_int>(3,clip((rgbn->__getitem__(__ss_int(0LL))+((rgb->__getitem__(__ss_int(0LL))-value->__getitem__(__ss_int(0LL)))/__ss_float(2.0)))),clip((rgbn->__getitem__(__ss_int(1LL))+((rgb->__getitem__(__ss_int(1LL))-value->__getitem__(__ss_int(1LL)))/__ss_float(2.0)))),clip((rgbn->__getitem__(__ss_int(2LL))+((rgb->__getitem__(__ss_int(2LL))-value->__getitem__(__ss_int(2LL)))/__ss_float(2.0))))));
                im->putpixel((__ss_tuple_int(2,x,(y+__ss_int(1LL)))), rgbn);
            }
            x = (x+__ss_int(1LL));
        }
        y = (y+__ss_int(1LL));
    }
    return NULL;
}

/**
class SimpleImage
*/

class_ *cl_SimpleImage;

void *SimpleImage::__init__(list<tuple<__ss_int> *> *data, tuple<__ss_int> *size) {
    tuple<__ss_int> *__128, *__129;

    this->_data = data;
    __129 = size;
    __128 = size;
    this->width = __128->__getfirst__();
    this->height = __128->__getsecond__();
    this->size = __129;
    return NULL;
}

SimpleImage *SimpleImage::copy() {
    return (__SS_NEW SimpleImage((this->_data)->__slice__(__ss_int(0LL), __ss_int(0LL), __ss_int(0LL), __ss_int(0LL)), this->size));
}

tuple<__ss_int> *SimpleImage::getpixel(tuple<__ss_int> *xy) {
    __ss_int x, y;
    tuple<__ss_int> *__130;

    __130 = xy;
    __SS_UNPACK_CHECK(__130, 2);
    x = __130->__getfirst__();
    y = __130->__getsecond__();
    return (this->_data)->__getfast__(((y*this->width)+x));
}

void *SimpleImage::putpixel(tuple<__ss_int> *xy, tuple<__ss_int> *value) {
    __ss_int x, y;
    tuple<__ss_int> *__131;
    list<tuple<__ss_int> *> *__132;

    __131 = xy;
    __SS_UNPACK_CHECK(__131, 2);
    x = __131->__getfirst__();
    y = __131->__getsecond__();
    this->_data->__setitem__(((y*this->width)+x), value);
    return NULL;
}

list<tuple<__ss_int> *> *SimpleImage::getdata() {
    return this->_data;
}

void SimpleImage::__static__() {
}

__SS_INIT_ATTR void __init() {
    __name__ = new str("optimiserlib");

    const_0 = new str("\012Convert and optimise images for display in an Acorn Electron MODE 1 variant\012with four colours per line but eight colours available for selection on each\012line.\012\012Copyright (C) 2015 Paul Boddie <paul@boddie.org.uk>\012\012This program is free software; you can redistribute it and/or modify it under\012the terms of the GNU General Public License as published by the Free Software\012Foundation; either version 3 of the License, or (at your option) any later\012version.\012\012This program is distributed in the hope that it will be useful, but WITHOUT ANY\012WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A\012PARTICULAR PURPOSE.  See the GNU General Public License for more details.\012\012You should have received a copy of the GNU General Public License along\012with this program.  If not, see <http://www.gnu.org/licenses/>.\012");
    const_1 = new str("Return the colour distribution for 'rgb'.");
    const_2 = new str("Return 'rgb' and its complement.");
    const_3 = new str("\012    Balance distribution 'd', cancelling opposing values and their complements\012    and replacing their common contributions with black and white contributions.\012    ");
    const_4 = new str("Combine distribution 'd' to get a colour value.");
    const_5 = new str("\012    Obtain a sorted colour distribution for 'rgb', optionally limited to any\012    specified 'chosen' colours.\012    ");
    const_6 = new str("\012    Get an output colour for 'rgb', optionally limited to any specified 'chosen'\012    colours. If 'fail' is set to a true value, return None if the colour cannot\012    be expressed using any of the chosen colours.\012    ");
    const_7 = new str("Get a colour distribution from image 'im' for the row 'y'.");
    const_8 = new str("\012    Get combinations of colours from 'c' of size 'n' in decreasing order of\012    probability.\012    ");
    const_9 = new str("\012    Count colours on each row of image 'im', returning a tuple indicating the\012    first row with more than the given number of 'colours' together with the\012    found colours; otherwise returning None.\012    ");
    const_10 = new str("\012    Process image 'im' using the given options: 'saturate', 'desaturate',\012    'darken', 'brighten'.\012    ");
    const_11 = new str("Convert image 'im' to an appropriate output representation.");
    const_12 = new str("An image behaving like PIL.Image.");
    const_13 = new str("__main__");

    corners = (__SS_NEW list<tuple<__ss_int> *>(8,(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(0LL),__ss_int(0LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(0LL),__ss_int(0LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(255LL),__ss_int(0LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(255LL),__ss_int(0LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(0LL),__ss_int(255LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(0LL),__ss_int(255LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(255LL),__ss_int(255LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(255LL),__ss_int(255LL)))));
    scaled_corners = map(1, False, scale, __optimiserlib__::corners);
    zipped_corners = (__SS_NEW list<tuple2<tuple<__ss_int> *, tuple<__ss_float> *> *>(__zip(2, False, __optimiserlib__::corners, __optimiserlib__::scaled_corners)));
    bases = (__SS_NEW list<tuple<__ss_int> *>(4,(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(0LL),__ss_int(0LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(0LL),__ss_int(0LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(255LL),__ss_int(0LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(0LL),__ss_int(255LL)))));
    base_complements = (__SS_NEW list<tuple<tuple<__ss_int> *> *>(map(1, False, complements, __optimiserlib__::bases)));
    default_0 = NULL;
    default_1 = NULL;
    cl_SimpleImage = new class_("SimpleImage");
    SimpleImage::__static__();
    if (__eq(__optimiserlib__::__name__, const_13)) {
        rgb = (__SS_NEW tuple<__ss_int>(3,__ss_int(200LL),__ss_int(100LL),__ss_int(50LL)));
        saturate_rgb(__optimiserlib__::rgb, __ss_float(1.0));
        amplify_rgb(__optimiserlib__::rgb, __ss_float(1.0));
        get_value(__optimiserlib__::rgb, NULL, False);
        get_value(__optimiserlib__::rgb, (__SS_NEW list<tuple<__ss_int> *>(4,(__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(255LL),__ss_int(255LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(0LL),__ss_int(0LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(255LL),__ss_int(0LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(0LL),__ss_int(0LL))))), False);
        combine((__SS_NEW list<tuple2<__ss_float, tuple<__ss_int> *> *>(2,(__SS_NEW tuple2<__ss_float, tuple<__ss_int> *>(2,__ss_float(1.0),(__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(0LL),__ss_int(0LL))))),(__SS_NEW tuple2<__ss_float, tuple<__ss_int> *>(2,__ss_float(0.0),(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(0LL),__ss_int(0LL))))))));
        clip(__ss_float(200.0));
        get_combinations((__SS_NEW list<tuple2<__ss_float, tuple<__ss_int> *> *>(3,(__SS_NEW tuple2<__ss_float, tuple<__ss_int> *>(2,__ss_float(0.5),(__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(0LL),__ss_int(0LL))))),(__SS_NEW tuple2<__ss_float, tuple<__ss_int> *>(2,__ss_float(0.25),(__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(255LL),__ss_int(0LL))))),(__SS_NEW tuple2<__ss_float, tuple<__ss_int> *>(2,__ss_float(0.25),(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(0LL),__ss_int(0LL))))))), __ss_int(2LL));
        data = (__SS_NEW list<tuple<__ss_int> *>(2,(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(0LL),__ss_int(0LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(0LL),__ss_int(0LL)))));
        im = (__SS_NEW SimpleImage(__optimiserlib__::data, (__ss_tuple_int(2,__ss_int(2LL),__ss_int(1LL)))));
        im2 = __optimiserlib__::im->copy();
        ___bool(__eq(__optimiserlib__::im2->getpixel((__ss_tuple_int(2,__ss_int(0LL),__ss_int(0LL)))), (__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(0LL),__ss_int(0LL)))));
        __optimiserlib__::im2->putpixel((__ss_tuple_int(2,__ss_int(0LL),__ss_int(0LL))), (__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(255LL),__ss_int(255LL))));
        ___bool(__eq(__optimiserlib__::im2->getdata(), (__SS_NEW list<tuple<__ss_int> *>(2,(__SS_NEW tuple<__ss_int>(3,__ss_int(255LL),__ss_int(255LL),__ss_int(255LL))),(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(0LL),__ss_int(0LL)))))));
        ___bool(__eq(get_colours(__optimiserlib__::im, __ss_int(0LL)), (__SS_NEW list<tuple2<__ss_float, tuple<__ss_int> *> *>(1,(__SS_NEW tuple2<__ss_float, tuple<__ss_int> *>(2,__ss_float(1.0),(__SS_NEW tuple<__ss_int>(3,__ss_int(0LL),__ss_int(0LL),__ss_int(0LL)))))))));
        count_colours(__optimiserlib__::im, __ss_int(4LL));
        process_image(__optimiserlib__::im, __ss_float(1.0), __ss_float(0.0), __ss_float(1.0), __ss_float(0.0));
        convert_image(__optimiserlib__::im, __ss_int(4LL), True);
    }
}

} // module namespace

/* extension module glue */

extern "C" {
#include <Python.h>
#include "itertools.hpp"
#include "math/__init__.hpp"
#include "random.hpp"
#include "time.hpp"
#include "optimiserlib.hpp"
#include <structmember.h>
#include "itertools.hpp"
#include "math/__init__.hpp"
#include "random.hpp"
#include "time.hpp"
#include "optimiserlib.hpp"

PyObject *__ss_mod_optimiserlib;

namespace __optimiserlib__ {

/* class SimpleImage */

typedef struct {
    PyObject_HEAD
    __optimiserlib__::SimpleImage *__ss_object;
} __ss_optimiserlib_SimpleImageObject;

static PyMemberDef __ss_optimiserlib_SimpleImageMembers[] = {
    {NULL}
};

PyObject *__ss_optimiserlib_SimpleImage___init__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"data", "size"};
        __ss_check_args("SimpleImage.__init__", 1, 2, 2, __ss_names, args, kwargs);
        list<tuple<__ss_int> *> *arg_0 = __ss_arg<list<tuple<__ss_int> *> *>("data", 0, 0, 0, args, kwargs);
        tuple<__ss_int> *arg_1 = __ss_arg<tuple<__ss_int> *>("size", 1, 0, 0, args, kwargs);

        return __to_py(((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->__init__(arg_0, arg_1));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *__ss_optimiserlib_SimpleImage_copy(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_check_args("SimpleImage.copy", 1, 0, 0, NULL, args, kwargs);

        return __to_py(((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->copy());

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *__ss_optimiserlib_SimpleImage_getpixel(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"xy"};
        __ss_check_args("SimpleImage.getpixel", 1, 1, 1, __ss_names, args, kwargs);
        tuple<__ss_int> *arg_0 = __ss_arg<tuple<__ss_int> *>("xy", 0, 0, 0, args, kwargs);

        return __to_py(((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->getpixel(arg_0));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *__ss_optimiserlib_SimpleImage_putpixel(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"xy", "value"};
        __ss_check_args("SimpleImage.putpixel", 1, 2, 2, __ss_names, args, kwargs);
        tuple<__ss_int> *arg_0 = __ss_arg<tuple<__ss_int> *>("xy", 0, 0, 0, args, kwargs);
        tuple<__ss_int> *arg_1 = __ss_arg<tuple<__ss_int> *>("value", 1, 0, 0, args, kwargs);

        return __to_py(((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->putpixel(arg_0, arg_1));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *__ss_optimiserlib_SimpleImage_getdata(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        __ss_check_args("SimpleImage.getdata", 1, 0, 0, NULL, args, kwargs);

        return __to_py(((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->getdata());

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

static PyNumberMethods __ss_optimiserlib_SimpleImage_as_number = {
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

PyObject *__ss_optimiserlib_SimpleImage__reduce__(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *__ss_optimiserlib_SimpleImage__setstate__(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef __ss_optimiserlib_SimpleImageMethods[] = {
    {(char *)"__reduce__", (PyCFunction)__ss_optimiserlib_SimpleImage__reduce__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__setstate__", (PyCFunction)__ss_optimiserlib_SimpleImage__setstate__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"__init__", (PyCFunction)__ss_optimiserlib_SimpleImage___init__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"copy", (PyCFunction)__ss_optimiserlib_SimpleImage_copy, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"getpixel", (PyCFunction)__ss_optimiserlib_SimpleImage_getpixel, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"putpixel", (PyCFunction)__ss_optimiserlib_SimpleImage_putpixel, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"getdata", (PyCFunction)__ss_optimiserlib_SimpleImage_getdata, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

int __ss_optimiserlib_SimpleImage___tpinit__(PyObject *self, PyObject *args, PyObject *kwargs) {
    if(!__ss_optimiserlib_SimpleImage___init__(self, args, kwargs))
        return -1;
    return 0;
}

PyObject *__ss_optimiserlib_SimpleImageNew(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    __ss_optimiserlib_SimpleImageObject *self = (__ss_optimiserlib_SimpleImageObject *)type->tp_alloc(type, 0);
    self->__ss_object = new __optimiserlib__::SimpleImage();
    self->__ss_object->__class__ = __optimiserlib__::cl_SimpleImage;
    __ss_proxy->__setitem__(self->__ss_object, self);
    return (PyObject *)self;
}

void __ss_optimiserlib_SimpleImageDealloc(__ss_optimiserlib_SimpleImageObject *self) {
    __ss_proxy->__delitem__(self->__ss_object);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *__ss_get___ss_optimiserlib_SimpleImage_data(__ss_optimiserlib_SimpleImageObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->_data);
}

int __ss_set___ss_optimiserlib_SimpleImage_data(__ss_optimiserlib_SimpleImageObject *self, PyObject *value, void *closure) {
    (void)closure;
    if(value == NULL) {
        PyErr_SetString(PyExc_AttributeError, "attribute 'data' of 'optimiserlib.SimpleImage' objects cannot be deleted");
        return -1;
    }
    try {
        self->__ss_object->_data = __to_ss<list<tuple<__ss_int> *> *>(value);
    } catch (Exception *e) {
        __ss_raise_py(e);
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_optimiserlib_SimpleImage_height(__ss_optimiserlib_SimpleImageObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->height);
}

int __ss_set___ss_optimiserlib_SimpleImage_height(__ss_optimiserlib_SimpleImageObject *self, PyObject *value, void *closure) {
    (void)closure;
    if(value == NULL) {
        PyErr_SetString(PyExc_AttributeError, "attribute 'height' of 'optimiserlib.SimpleImage' objects cannot be deleted");
        return -1;
    }
    try {
        self->__ss_object->height = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        __ss_raise_py(e);
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_optimiserlib_SimpleImage_size(__ss_optimiserlib_SimpleImageObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->size);
}

int __ss_set___ss_optimiserlib_SimpleImage_size(__ss_optimiserlib_SimpleImageObject *self, PyObject *value, void *closure) {
    (void)closure;
    if(value == NULL) {
        PyErr_SetString(PyExc_AttributeError, "attribute 'size' of 'optimiserlib.SimpleImage' objects cannot be deleted");
        return -1;
    }
    try {
        self->__ss_object->size = __to_ss<tuple<__ss_int> *>(value);
    } catch (Exception *e) {
        __ss_raise_py(e);
        return -1;
    }
    return 0;
}

PyObject *__ss_get___ss_optimiserlib_SimpleImage_width(__ss_optimiserlib_SimpleImageObject *self, void *closure) {
    (void)closure;
    return __to_py(self->__ss_object->width);
}

int __ss_set___ss_optimiserlib_SimpleImage_width(__ss_optimiserlib_SimpleImageObject *self, PyObject *value, void *closure) {
    (void)closure;
    if(value == NULL) {
        PyErr_SetString(PyExc_AttributeError, "attribute 'width' of 'optimiserlib.SimpleImage' objects cannot be deleted");
        return -1;
    }
    try {
        self->__ss_object->width = __to_ss<__ss_int >(value);
    } catch (Exception *e) {
        __ss_raise_py(e);
        return -1;
    }
    return 0;
}

PyGetSetDef __ss_optimiserlib_SimpleImageGetSet[] = {
    {(char *)"data", (getter)__ss_get___ss_optimiserlib_SimpleImage_data, (setter)__ss_set___ss_optimiserlib_SimpleImage_data, (char *)"", NULL},
    {(char *)"height", (getter)__ss_get___ss_optimiserlib_SimpleImage_height, (setter)__ss_set___ss_optimiserlib_SimpleImage_height, (char *)"", NULL},
    {(char *)"size", (getter)__ss_get___ss_optimiserlib_SimpleImage_size, (setter)__ss_set___ss_optimiserlib_SimpleImage_size, (char *)"", NULL},
    {(char *)"width", (getter)__ss_get___ss_optimiserlib_SimpleImage_width, (setter)__ss_set___ss_optimiserlib_SimpleImage_width, (char *)"", NULL},
    {NULL}
};

PyTypeObject __ss_optimiserlib_SimpleImageObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "optimiserlib.SimpleImage",
    sizeof( __ss_optimiserlib_SimpleImageObject),
    0,
    (destructor) __ss_optimiserlib_SimpleImageDealloc,
    0,
    0,
    0,
    0,
    0,
    &__ss_optimiserlib_SimpleImage_as_number,
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
    __ss_optimiserlib_SimpleImageMethods,
    __ss_optimiserlib_SimpleImageMembers,
    __ss_optimiserlib_SimpleImageGetSet,
    0, 
    0, 
    0, 
    0, 
    0, 
    (initproc) __ss_optimiserlib_SimpleImage___tpinit__,
    0,
    __ss_optimiserlib_SimpleImageNew,
};

PyObject *__ss_optimiserlib_SimpleImage__reduce__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)args; (void)kwargs;
    PyObject *t = PyTuple_New(3);
    PyTuple_SetItem(t, 0, PyObject_GetAttrString(__ss_mod_optimiserlib, "__newobj__"));
    PyObject *a = PyTuple_New(1);
    Py_INCREF((PyObject *)&__ss_optimiserlib_SimpleImageObjectType);
    PyTuple_SetItem(a, 0, (PyObject *)&__ss_optimiserlib_SimpleImageObjectType);
    PyTuple_SetItem(t, 1, a);
    PyObject *b = PyDict_New();
    __ss_dict_steal(b, "data", __to_py(((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->_data));
    __ss_dict_steal(b, "height", __to_py(((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->height));
    __ss_dict_steal(b, "size", __to_py(((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->size));
    __ss_dict_steal(b, "width", __to_py(((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->width));
    PyTuple_SetItem(t, 2, b);
    return t;
}

PyObject *__ss_optimiserlib_SimpleImage__setstate__(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *state = PyTuple_GetItem(args, 0);
    PyObject *value;
    value = __ss_dict_lookup(state, "data");
    if (value) ((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->_data = __to_ss<list<tuple<__ss_int> *> *>(value);
    value = __ss_dict_lookup(state, "height");
    if (value) ((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->height = __to_ss<__ss_int >(value);
    value = __ss_dict_lookup(state, "size");
    if (value) ((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->size = __to_ss<tuple<__ss_int> *>(value);
    value = __ss_dict_lookup(state, "width");
    if (value) ((__ss_optimiserlib_SimpleImageObject *)self)->__ss_object->width = __to_ss<__ss_int >(value);
    Py_INCREF(Py_None);
    return Py_None;
}

} // namespace __optimiserlib__

namespace __optimiserlib__ {
PyObject *Global_optimiserlib_within(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"v", "lower", "upper"};
        __ss_check_args("within", 0, 3, 3, __ss_names, args, kwargs);
        __ss_float arg_0 = __ss_arg<__ss_float >("v", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("lower", 1, 0, 0, args, kwargs);
        __ss_int arg_2 = __ss_arg<__ss_int >("upper", 2, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::within(arg_0, arg_1, arg_2));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_clip(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"v"};
        __ss_check_args("clip", 0, 1, 1, __ss_names, args, kwargs);
        __ss_float arg_0 = __ss_arg<__ss_float >("v", 0, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::clip(arg_0));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_distance(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"rgb1", "rgb2"};
        __ss_check_args("distance", 0, 2, 2, __ss_names, args, kwargs);
        tuple<__ss_int> *arg_0 = __ss_arg<tuple<__ss_int> *>("rgb1", 0, 0, 0, args, kwargs);
        tuple<__ss_int> *arg_1 = __ss_arg<tuple<__ss_int> *>("rgb2", 1, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::distance(arg_0, arg_1));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_restore(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"srgb"};
        __ss_check_args("restore", 0, 1, 1, __ss_names, args, kwargs);
        tuple<__ss_float> *arg_0 = __ss_arg<tuple<__ss_float> *>("srgb", 0, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::restore(arg_0));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_scale(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"rgb"};
        __ss_check_args("scale", 0, 1, 1, __ss_names, args, kwargs);
        tuple<__ss_int> *arg_0 = __ss_arg<tuple<__ss_int> *>("rgb", 0, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::scale(arg_0));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_invert(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"srgb"};
        __ss_check_args("invert", 0, 1, 1, __ss_names, args, kwargs);
        tuple<__ss_float> *arg_0 = __ss_arg<tuple<__ss_float> *>("srgb", 0, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::invert(arg_0));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_combination(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"rgb"};
        __ss_check_args("combination", 0, 1, 1, __ss_names, args, kwargs);
        tuple<__ss_int> *arg_0 = __ss_arg<tuple<__ss_int> *>("rgb", 0, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::combination(arg_0));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_complements(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"rgb"};
        __ss_check_args("complements", 0, 1, 1, __ss_names, args, kwargs);
        tuple<__ss_int> *arg_0 = __ss_arg<tuple<__ss_int> *>("rgb", 0, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::complements(arg_0));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_balance(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"d"};
        __ss_check_args("balance", 0, 1, 1, __ss_names, args, kwargs);
        list<tuple2<__ss_float, tuple<__ss_int> *> *> *arg_0 = __ss_arg<list<tuple2<__ss_float, tuple<__ss_int> *> *> *>("d", 0, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::balance(arg_0));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_combine(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"d"};
        __ss_check_args("combine", 0, 1, 1, __ss_names, args, kwargs);
        list<tuple2<__ss_float, tuple<__ss_int> *> *> *arg_0 = __ss_arg<list<tuple2<__ss_float, tuple<__ss_int> *> *> *>("d", 0, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::combine(arg_0));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_pattern(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"rgb", "chosen"};
        __ss_check_args("pattern", 0, 2, 1, __ss_names, args, kwargs);
        tuple<__ss_int> *arg_0 = __ss_arg<tuple<__ss_int> *>("rgb", 0, 0, 0, args, kwargs);
        list<tuple<__ss_int> *> *arg_1 = __ss_arg<list<tuple<__ss_int> *> *>("chosen", 1, 1, 0, args, kwargs);

        return __to_py(__optimiserlib__::pattern(arg_0, arg_1));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_get_value(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"rgb", "chosen", "fail"};
        __ss_check_args("get_value", 0, 3, 1, __ss_names, args, kwargs);
        tuple<__ss_int> *arg_0 = __ss_arg<tuple<__ss_int> *>("rgb", 0, 0, 0, args, kwargs);
        list<tuple<__ss_int> *> *arg_1 = __ss_arg<list<tuple<__ss_int> *> *>("chosen", 1, 1, 0, args, kwargs);
        __ss_bool arg_2 = __ss_arg<__ss_bool >("fail", 2, 1, False, args, kwargs);

        return __to_py(__optimiserlib__::get_value(arg_0, arg_1, arg_2));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_sign(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"x"};
        __ss_check_args("sign", 0, 1, 1, __ss_names, args, kwargs);
        __ss_float arg_0 = __ss_arg<__ss_float >("x", 0, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::sign(arg_0));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_saturate_rgb(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"rgb", "exp"};
        __ss_check_args("saturate_rgb", 0, 2, 2, __ss_names, args, kwargs);
        tuple<__ss_int> *arg_0 = __ss_arg<tuple<__ss_int> *>("rgb", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("exp", 1, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::saturate_rgb(arg_0, arg_1));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_saturate_value(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"x", "exp"};
        __ss_check_args("saturate_value", 0, 2, 2, __ss_names, args, kwargs);
        __ss_int arg_0 = __ss_arg<__ss_int >("x", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("exp", 1, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::saturate_value(arg_0, arg_1));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_amplify_rgb(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"rgb", "exp"};
        __ss_check_args("amplify_rgb", 0, 2, 2, __ss_names, args, kwargs);
        tuple<__ss_int> *arg_0 = __ss_arg<tuple<__ss_int> *>("rgb", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("exp", 1, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::amplify_rgb(arg_0, arg_1));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_amplify_value(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"x", "exp"};
        __ss_check_args("amplify_value", 0, 2, 2, __ss_names, args, kwargs);
        __ss_int arg_0 = __ss_arg<__ss_int >("x", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("exp", 1, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::amplify_value(arg_0, arg_1));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_get_colours(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"im", "y"};
        __ss_check_args("get_colours", 0, 2, 2, __ss_names, args, kwargs);
        SimpleImage *arg_0 = __ss_arg<SimpleImage *>("im", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("y", 1, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::get_colours(arg_0, arg_1));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_get_combinations(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"c", "n"};
        __ss_check_args("get_combinations", 0, 2, 2, __ss_names, args, kwargs);
        list<tuple2<__ss_float, tuple<__ss_int> *> *> *arg_0 = __ss_arg<list<tuple2<__ss_float, tuple<__ss_int> *> *> *>("c", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("n", 1, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::get_combinations(arg_0, arg_1));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_count_colours(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"im", "colours"};
        __ss_check_args("count_colours", 0, 2, 2, __ss_names, args, kwargs);
        SimpleImage *arg_0 = __ss_arg<SimpleImage *>("im", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("colours", 1, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::count_colours(arg_0, arg_1));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_process_image(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"im", "saturate", "desaturate", "darken", "brighten"};
        __ss_check_args("process_image", 0, 5, 5, __ss_names, args, kwargs);
        SimpleImage *arg_0 = __ss_arg<SimpleImage *>("im", 0, 0, 0, args, kwargs);
        __ss_float arg_1 = __ss_arg<__ss_float >("saturate", 1, 0, 0, args, kwargs);
        __ss_float arg_2 = __ss_arg<__ss_float >("desaturate", 2, 0, 0, args, kwargs);
        __ss_float arg_3 = __ss_arg<__ss_float >("darken", 3, 0, 0, args, kwargs);
        __ss_float arg_4 = __ss_arg<__ss_float >("brighten", 4, 0, 0, args, kwargs);

        return __to_py(__optimiserlib__::process_image(arg_0, arg_1, arg_2, arg_3, arg_4));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

PyObject *Global_optimiserlib_convert_image(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self; (void)args; (void)kwargs;
    try {
        static const char *const __ss_names[] = {"im", "colours", "least_error"};
        __ss_check_args("convert_image", 0, 3, 2, __ss_names, args, kwargs);
        SimpleImage *arg_0 = __ss_arg<SimpleImage *>("im", 0, 0, 0, args, kwargs);
        __ss_int arg_1 = __ss_arg<__ss_int >("colours", 1, 0, 0, args, kwargs);
        __ss_bool arg_2 = __ss_arg<__ss_bool >("least_error", 2, 1, False, args, kwargs);

        return __to_py(__optimiserlib__::convert_image(arg_0, arg_1, arg_2));

    } catch (Exception *e) {
        __ss_raise_py(e);
        return 0;
    }
}

static PyNumberMethods Global_optimiserlib_as_number = {
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

static PyMethodDef Global_optimiserlibMethods[] = {
    {(char *)"__newobj__", (PyCFunction)__ss__newobj__, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"within", (PyCFunction)Global_optimiserlib_within, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"clip", (PyCFunction)Global_optimiserlib_clip, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"distance", (PyCFunction)Global_optimiserlib_distance, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"restore", (PyCFunction)Global_optimiserlib_restore, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"scale", (PyCFunction)Global_optimiserlib_scale, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"invert", (PyCFunction)Global_optimiserlib_invert, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"combination", (PyCFunction)Global_optimiserlib_combination, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"complements", (PyCFunction)Global_optimiserlib_complements, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"balance", (PyCFunction)Global_optimiserlib_balance, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"combine", (PyCFunction)Global_optimiserlib_combine, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"pattern", (PyCFunction)Global_optimiserlib_pattern, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"get_value", (PyCFunction)Global_optimiserlib_get_value, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"sign", (PyCFunction)Global_optimiserlib_sign, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"saturate_rgb", (PyCFunction)Global_optimiserlib_saturate_rgb, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"saturate_value", (PyCFunction)Global_optimiserlib_saturate_value, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"amplify_rgb", (PyCFunction)Global_optimiserlib_amplify_rgb, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"amplify_value", (PyCFunction)Global_optimiserlib_amplify_value, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"get_colours", (PyCFunction)Global_optimiserlib_get_colours, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"get_combinations", (PyCFunction)Global_optimiserlib_get_combinations, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"count_colours", (PyCFunction)Global_optimiserlib_count_colours, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"process_image", (PyCFunction)Global_optimiserlib_process_image, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {(char *)"convert_image", (PyCFunction)Global_optimiserlib_convert_image, METH_VARARGS | METH_KEYWORDS, (char *)""},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef Module_optimiserlib = {
    PyModuleDef_HEAD_INIT,
    "optimiserlib",   /* name of module */
    NULL,   /* module documentation, may be NULL */
    -1,     /* size of per-interpreter state of the module or -1 if the module keeps state in global variables. */
    Global_optimiserlibMethods
};

PyMODINIT_FUNC PyInit_optimiserlib(void) {

    __shedskin__::__init();
    __math__::__init();
    __time__::__init();
    __random__::__init();
    __itertools__::__init();
    __optimiserlib__::__init();

    PyObject *m;

    if (PyType_Ready(&__ss_optimiserlib_SimpleImageObjectType) < 0)
        return NULL;

    // create extension module
    __ss_mod_optimiserlib = m = PyModule_Create(&Module_optimiserlib);
    if (m == NULL)
        return NULL;

    // add global variables
    if (PyModule_AddObject(m, (char *)"base_complements", __to_py(__optimiserlib__::base_complements)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"bases", __to_py(__optimiserlib__::bases)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"corners", __to_py(__optimiserlib__::corners)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"data", __to_py(__optimiserlib__::data)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"im", __to_py(__optimiserlib__::im)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"im2", __to_py(__optimiserlib__::im2)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"rgb", __to_py(__optimiserlib__::rgb)) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, (char *)"zipped_corners", __to_py(__optimiserlib__::zipped_corners)) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    // add type objects
    Py_INCREF(&__ss_optimiserlib_SimpleImageObjectType);
    if (PyModule_AddObject(m, "SimpleImage", (PyObject *) &__ss_optimiserlib_SimpleImageObjectType) < 0) {
        Py_DECREF(&__ss_optimiserlib_SimpleImageObjectType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}


} // namespace __optimiserlib__

} // extern "C"
namespace __optimiserlib__ {

PyObject *SimpleImage::__to_py__() {
    PyObject *p;
    if(__ss_proxy->has_key(this)) {
        p = (PyObject *)(__ss_proxy->__getitem__(this));
        Py_INCREF(p);
    } else {
        __ss_optimiserlib_SimpleImageObject *self = (__ss_optimiserlib_SimpleImageObject *)(__ss_optimiserlib_SimpleImageObjectType.tp_alloc(&__ss_optimiserlib_SimpleImageObjectType, 0));
        self->__ss_object = this;
        __ss_proxy->__setitem__(self->__ss_object, self);
        p = (PyObject *)self;
    }
    return p;
}

} // module namespace

namespace __shedskin__ {

template<> __optimiserlib__::SimpleImage *__to_ss(PyObject *p) {
    if(p == Py_None) return NULL;
    if(PyObject_IsInstance(p, (PyObject *)&__optimiserlib__::__ss_optimiserlib_SimpleImageObjectType)!=1)
        throw new TypeError(new str("error in conversion to Shed Skin (SimpleImage expected)"));
    return ((__optimiserlib__::__ss_optimiserlib_SimpleImageObject *)p)->__ss_object;
}
}
int main(int, char **) {
    __shedskin__::__init();
    __math__::__init();
    __time__::__init();
    __random__::__init();
    __itertools__::__init();
    __shedskin__::__start(__optimiserlib__::__init);
}
