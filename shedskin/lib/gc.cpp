/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "gc.hpp"

namespace __gc__ {

void __init() {

}

void *enable() {
    GC_enable();

    return NULL;
}

void *disable() {
    GC_disable();

    return NULL;
}

void *collect() {
    GC_gcollect();

    return NULL;
}

} // module namespace

