/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include <algorithm>

#include "builtin.hpp"
#include "colorsys.hpp"

/**
Conversion functions between RGB and other color systems.

This modules provides two functions for each color system ABC:

  rgb_to_abc(r, g, b) --> a, b, c
  abc_to_rgb(a, b, c) --> r, g, b

All inputs and outputs are triples of floats in the range [0.0...1.0]
(with the exception of I and Q, which covers a slightly larger range).
Inputs outside the valid range may cause exceptions or invalid outputs.

Supported color systems:
RGB: Red, Green, Blue components
YIQ: Luminance, Chrominance (used by composite video signals)
HLS: Hue, Luminance, Saturation
HSV: Hue, Saturation, Value
*/

namespace __colorsys__ {

double ONE_SIXTH, ONE_THIRD, TWO_THIRD;

tuple2<double, double> *rgb_to_yiq(double r, double g, double b) {
    double y = (((0.3*r)+(0.59*g))+(0.11*b));
    double i = (((0.6*r)-(0.28*g))-(0.32*b));
    double q = (((0.21*r)-(0.52*g))+(0.31*b));

    return (new tuple2<double, double>(3,y,i,q));
}

tuple2<double, double> *yiq_to_rgb(double y, double i, double q) {
    double r = std::clamp((y+(0.948262*i))+(0.624013*q), 0., 1.);
    double g = std::clamp((y-(0.276066*i))-(0.63981*q), 0., 1.);
    double b = std::clamp((y-(1.10545*i))+(1.72986*q), 0., 1.);

    return (new tuple2<double, double>(3,r,g,b));
}

tuple2<double, double> *rgb_to_hls(double r, double g, double b) {
    double bc, gc, h, l, maxc, minc, rc, s;

    maxc = ___max(3, ((double)(0)), r, g, b);
    minc = ___min(3, ((double)(0)), r, g, b);
    l = ((minc+maxc)/2.0);
    if ((minc==maxc)) {
        return (new tuple2<double, double>(3,0.0,l,0.0));
    }
    if ((l<=0.5)) {
        s = ((maxc-minc)/(maxc+minc));
    }
    else {
        s = ((maxc-minc)/((2.0-maxc)-minc));
    }
    rc = ((maxc-r)/(maxc-minc));
    gc = ((maxc-g)/(maxc-minc));
    bc = ((maxc-b)/(maxc-minc));
    if ((r==maxc)) {
        h = (bc-gc);
    }
    else if ((g==maxc)) {
        h = ((2.0+rc)-bc);
    }
    else {
        h = ((4.0+gc)-rc);
    }
    h = __mods((h/6.0), 1.0);
    return (new tuple2<double, double>(3,h,l,s));
}

tuple2<double, double> *hls_to_rgb(double h, double l, double s) {
    double m1, m2;

    if ((s==0.0)) {
        return (new tuple2<double, double>(3,l,l,l));
    }
    if ((l<=0.5)) {
        m2 = (l*(1.0+s));
    }
    else {
        m2 = ((l+s)-(l*s));
    }
    m1 = ((2.0*l)-m2);
    return (new tuple2<double, double>(3,_v(m1, m2, (h+ONE_THIRD)),_v(m1, m2, h),_v(m1, m2, (h-ONE_THIRD))));
}

double _v(double m1, double m2, double hue) {
    
    hue = __mods(hue, 1.0);
    if ((hue<ONE_SIXTH)) {
        return (m1+(((m2-m1)*hue)*6.0));
    }
    if ((hue<0.5)) {
        return m2;
    }
    if ((hue<TWO_THIRD)) {
        return (m1+(((m2-m1)*(TWO_THIRD-hue))*6.0));
    }
    return m1;
}

tuple2<double, double> *rgb_to_hsv(double r, double g, double b) {
    double bc, gc, h, maxc, minc, rc, s, v;

    maxc = ___max(3, ((double)(0)), r, g, b);
    minc = ___min(3, ((double)(0)), r, g, b);
    v = maxc;
    if ((minc==maxc)) {
        return (new tuple2<double, double>(3,0.0,0.0,v));
    }
    s = ((maxc-minc)/maxc);
    rc = ((maxc-r)/(maxc-minc));
    gc = ((maxc-g)/(maxc-minc));
    bc = ((maxc-b)/(maxc-minc));
    if ((r==maxc)) {
        h = (bc-gc);
    }
    else if ((g==maxc)) {
        h = ((2.0+rc)-bc);
    }
    else {
        h = ((4.0+gc)-rc);
    }
    h = __mods((h/6.0), 1.0);
    return (new tuple2<double, double>(3,h,s,v));
}

tuple2<double, double> *hsv_to_rgb(double h, double s, double v) {
    double f, p, q, t;
    __ss_int i;

    if ((s==0.0)) {
        return (new tuple2<double, double>(3,v,v,v));
    }
    i = __int((h*6.0));
    f = ((h*6.0)-i);
    p = (v*(1.0-s));
    q = (v*(1.0-(s*f)));
    t = (v*(1.0-(s*(1.0-f))));
    i = __mods(i, (__ss_int)6);
    if ((i==0)) {
        return (new tuple2<double, double>(3,v,t,p));
    }
    if ((i==1)) {
        return (new tuple2<double, double>(3,q,v,p));
    }
    if ((i==2)) {
        return (new tuple2<double, double>(3,p,v,t));
    }
    if ((i==3)) {
        return (new tuple2<double, double>(3,p,q,v));
    }
    if ((i==4)) {
        return (new tuple2<double, double>(3,t,p,v));
    }
    if ((i==5)) {
        return (new tuple2<double, double>(3,v,p,q));
    }
    return 0;
}

void __init() {
    ONE_THIRD = (1.0/3.0);
    ONE_SIXTH = (1.0/6.0);
    TWO_THIRD = (2.0/3.0);
}

} // module namespace
