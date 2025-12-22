/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

#define __SS_MIN(a,b) ((a) < (b) ? (a) : (b))

/* iteration macros */

#define FAST_FOR(i, l, u, s, t1, t2) \
    if(s==0) \
        __throw_range_step_zero(); \
    for(__ ## t1 = l, __ ## t2 = u; ; __ ## t1 += s) { \
        if (s >= 0) { if (__ ## t1 >= __ ## t2) break; } \
        else { if (__ ## t1 <= __ ## t2) break; } \
        i=__ ## t1; \

#define FOR_IN(e, iter, temp, i, t) \
    __ ## temp = iter; \
    __ ## i = -1; \
    (void)__ ## i; \
    __ ## t = __ ## temp->for_in_init(); \
    while(__ ## temp->for_in_has_next(__ ## t)) \
    { \
        __ ## i ++; \
        e = __ ## temp->for_in_next(__ ## t);

#define FOR_IN_ZIP(a, b, k, l, t, u, n, m) \
    __ ## m = __SS_MIN(k->units.size(), l->units.size()); \
    __ ## t = k; \
    __ ## u = l; \
    for(__ ## n = 0; __ ## n < __ ## m; __ ## n ++) { \
        a = (__ ## t)->units[__ ## n]; \
        b = (__ ## u)->units[__ ## n];

#define FOR_IN_ENUMERATE(i, m, temp, n) \
    __ ## temp = m; \
    for(__ ## n = 0; (unsigned int)__ ## n < (__ ## temp)->units.size(); __ ## n ++) { \
        i = (__ ## temp)->units[__ ## n]; \

#define FOR_IN_ENUMERATE_STR(i, m, temp, n) \
    __ ## temp = m; \
    for(__ ## n = 0; (unsigned int)__ ## n < (__ ## temp)->unit.size(); __ ## n ++) { \
        i = (__ ## temp)->__getfast__(__ ## n); \

#define FOR_IN_LIST(e, m, temp) \
    __ ## temp = m; \
    for (auto __ ## iter = (__ ## temp)->units.begin(); __ ## iter != (__ ## temp)->units.end(); ) { \
        e = *(__ ## iter)++;

#define FOR_IN_DICT(m, temp, iter, pos) \
    __ ## temp = m; \
    __ ## iter = (__ ## temp)->gcd.begin(); \
    while (__ ## iter != (__ ## temp)->gcd.end() ) { \

#define FOR_IN_FILE(l, f, temp) \
    __ ## temp = f; \
    while (! __ ## temp->__eof()) { \
        l = __ ## temp->readline(); \
        if (__ ## temp->__eof() and len(l) == 0) \
            break;

#define END_FOR }

