/* Copyright 2005-2012 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __GC_HPP
#define __GC_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __gc__ {

void __init();

void *enable();

void *disable();

void *collect();

} // module namespace
#endif
