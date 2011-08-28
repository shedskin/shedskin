/* Copyright 2005-2011 Mark Dufour and contributors; License MIT (See LICENSE) */

#ifndef __COLORSYS_HPP
#define __COLORSYS_HPP

using namespace __shedskin__;
namespace __colorsys__ {

extern double ONE_SIXTH, ONE_THIRD, TWO_THIRD;


tuple2<double, double> *rgb_to_yiq(double r, double g, double b);
tuple2<double, double> *yiq_to_rgb(double y, double i, double q);
tuple2<double, double> *rgb_to_hls(double r, double g, double b);
tuple2<double, double> *hls_to_rgb(double h, double l, double s);
double _v(double m1, double m2, double hue);
tuple2<double, double> *rgb_to_hsv(double r, double g, double b);
tuple2<double, double> *hsv_to_rgb(double h, double s, double v);

void __init();

} // module namespace
#endif
