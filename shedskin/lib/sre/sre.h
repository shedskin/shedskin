/*
 * Secret Labs' Regular Expression Engine
 *
 * regular expression matching engine
 *
 * Copyright (c) 1997-2001 by Secret Labs AB.  All rights reserved.
 *
 * See the sre.c file for information on usage and redistribution.
 */

/* shedskin: vendored from CPython 3.13 (Modules/_sre/sre.h), with the
   Python object types and object fields of SRE_STATE removed */

#ifndef SRE_INCLUDED
#define SRE_INCLUDED

#include "sre_constants.h"

/* size of a code word (must be unsigned short or larger, and
   large enough to hold a UCS4 character) */
#define SRE_CODE Py_UCS4
#if SIZEOF_SIZE_T > 4
# define SRE_MAXREPEAT (~(SRE_CODE)0)
# define SRE_MAXGROUPS ((SRE_CODE)INT32_MAX / 2)
#else
# define SRE_MAXREPEAT ((SRE_CODE)PY_SSIZE_T_MAX)
# define SRE_MAXGROUPS ((SRE_CODE)PY_SSIZE_T_MAX / SIZEOF_VOID_P / 2)
#endif

typedef struct SRE_REPEAT_T {
    Py_ssize_t count;
    const SRE_CODE* pattern; /* points to REPEAT operator arguments */
    const void* last_ptr; /* helper to check for infinite loops */
    struct SRE_REPEAT_T *prev; /* points to previous repeat context */
    /* for SRE_REPEAT pool */
    struct SRE_REPEAT_T *pool_prev;
    struct SRE_REPEAT_T *pool_next;
} SRE_REPEAT;

typedef struct {
    /* string pointers */
    const void* ptr; /* current position (also end of current slice) */
    const void* beginning; /* start of original string */
    const void* start; /* start of current slice */
    const void* end; /* end of original string */
    /* attributes for the match object */
    Py_ssize_t pos, endpos;
    int isbytes;
    int charsize; /* character size */
    int match_all;
    int must_advance;
    int debug;
    /* marks */
    int lastmark;
    int lastindex;
    const void** mark;
    /* dynamically allocated stuff */
    char* data_stack;
    size_t data_stack_size;
    size_t data_stack_base;
    /* current repeat context */
    SRE_REPEAT *repeat;
    /* SRE_REPEAT pool */
    SRE_REPEAT *repeat_pool_used;
    SRE_REPEAT *repeat_pool_unused;
    unsigned int sigcount;
} SRE_STATE;

#endif
