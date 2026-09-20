/* Copyright 2005-2012 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __GC_HPP
#define __GC_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __gc__ {

extern __ss_int DEBUG_STATS, DEBUG_COLLECTABLE, DEBUG_UNCOLLECTABLE, DEBUG_SAVEALL, DEBUG_LEAK;

void __init();

void *enable();

void *disable();

__ss_bool isenabled();

__ss_int collect(__ss_int generation=2);

tuple<__ss_int> *get_count();

tuple<__ss_int> *get_threshold();

void *set_threshold(__ss_int threshold0, __ss_int threshold1=-1, __ss_int threshold2=-1);

__ss_int get_debug();
void *set_debug(__ss_int flags);

void *freeze();
void *unfreeze();
__ss_int get_freeze_count();

/* shedskin has no __del__ support, so no object is ever finalized */
template<class T> inline __ss_bool is_finalized(T) { return False; }

} // module namespace
#endif
