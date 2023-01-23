/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __COLORSYS_HPP
#define __COLORSYS_HPP

using namespace __shedskin__;
namespace __colorsys__ {

extern __ss_float ONE_SIXTH, ONE_THIRD, TWO_THIRD;


tuple2<__ss_float, __ss_float> *rgb_to_yiq(__ss_float r, __ss_float g, __ss_float b);
tuple2<__ss_float, __ss_float> *yiq_to_rgb(__ss_float y, __ss_float i, __ss_float q);
tuple2<__ss_float, __ss_float> *rgb_to_hls(__ss_float r, __ss_float g, __ss_float b);
tuple2<__ss_float, __ss_float> *hls_to_rgb(__ss_float h, __ss_float l, __ss_float s);
__ss_float _v(__ss_float m1, __ss_float m2, __ss_float hue);
tuple2<__ss_float, __ss_float> *rgb_to_hsv(__ss_float r, __ss_float g, __ss_float b);
tuple2<__ss_float, __ss_float> *hsv_to_rgb(__ss_float h, __ss_float s, __ss_float v);

void __init();

} // module namespace
#endif
