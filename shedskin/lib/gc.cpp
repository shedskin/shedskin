/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "gc.hpp"

namespace __gc__ {

/* Boehm GC is neither generational nor reference-counted, so CPython's
 * generation bookkeeping has no equivalent here. The thresholds below are
 * CPython's defaults; they are stored and handed back unchanged, so that
 * save/tweak/restore patterns keep working, but they do not influence
 * collection. get_count() likewise always reports zero objects per
 * generation. Sentinel -1 means "leave this threshold alone", matching
 * CPython, where omitted arguments keep their previous value. */

#ifdef __SS_NOGC
/* --nogc: there is no collector at all, so only the flag is tracked, keeping
 * enable/disable/isenabled coherent for user code. */
static bool __enabled = true;
#endif

static __ss_int __threshold0 = 700;
static __ss_int __threshold1 = 10;
static __ss_int __threshold2 = 10;

void __init() {

}

void *enable() {
#ifndef __SS_NOGC
    /* CPython's gc.enable()/gc.disable() are idempotent flags, while Boehm's
     * are a nesting counter (GC_disable increments, GC_enable decrements).
     * Only act on an actual transition, so that an unbalanced enable() cannot
     * push the counter below zero -- which would silently turn a later
     * disable() into a no-op. */
    if (GC_is_disabled())
        GC_enable();
#else
    __enabled = true;
#endif

    return NULL;
}

void *disable() {
#ifndef __SS_NOGC
    if (!GC_is_disabled())
        GC_disable();
#else
    __enabled = false;
#endif

    return NULL;
}

__ss_bool isenabled() {
#ifndef __SS_NOGC
    return __mbool(!GC_is_disabled());
#else
    return __mbool(__enabled);
#endif
}

__ss_int collect() {
#ifndef __SS_NOGC
    GC_gcollect();
#endif

    /* CPython returns the number of unreachable objects found; Boehm does not
     * report this, so always return zero. */
    return 0;
}

tuple<__ss_int> *get_count() {
    return new tuple<__ss_int>(3, (__ss_int)0, (__ss_int)0, (__ss_int)0);
}

tuple<__ss_int> *get_threshold() {
    return new tuple<__ss_int>(3, __threshold0, __threshold1, __threshold2);
}

void *set_threshold(__ss_int threshold0, __ss_int threshold1, __ss_int threshold2) {
    __threshold0 = threshold0;

    if (threshold1 != -1)
        __threshold1 = threshold1;

    if (threshold2 != -1)
        __threshold2 = threshold2;

    return NULL;
}

} // module namespace

