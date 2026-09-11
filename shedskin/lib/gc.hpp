/* Copyright 2005-2012 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __GC_HPP
#define __GC_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __gc__ {

void __init();

void *enable();

void *disable();

__ss_bool isenabled();

__ss_int collect();

tuple<__ss_int> *get_count();

tuple<__ss_int> *get_threshold();

void *set_threshold(__ss_int threshold0, __ss_int threshold1=-1, __ss_int threshold2=-1);

} // module namespace
#endif
