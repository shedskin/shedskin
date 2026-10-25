/*
 * Secret Labs' Regular Expression Engine
 *
 * regular expression matching engine
 *
 * partial history:
 * 1999-10-24 fl   created (based on existing template matcher code)
 * 2000-03-06 fl   first alpha, sort of
 * 2000-08-01 fl   fixes for 1.6b1
 * 2000-08-07 fl   use PyOS_CheckStack() if available
 * 2000-09-20 fl   added expand method
 * 2001-03-20 fl   lots of fixes for 2.1b2
 * 2001-04-15 fl   export copyright as Python attribute, not global
 * 2001-04-28 fl   added __copy__ methods (work in progress)
 * 2001-05-14 fl   fixes for 1.5.2 compatibility
 * 2001-07-01 fl   added BIGCHARSET support (from Martin von Loewis)
 * 2001-10-18 fl   fixed group reset issue (from Matthew Mueller)
 * 2001-10-20 fl   added split primitive; re-enable unicode for 1.6/2.0/2.1
 * 2001-10-21 fl   added sub/subn primitive
 * 2001-10-24 fl   added finditer primitive (for 2.2 only)
 * 2001-12-07 fl   fixed memory leak in sub/subn (Guido van Rossum)
 * 2002-11-09 fl   fixed empty sub/subn return type
 * 2003-04-18 mvl  fully support 4-byte codes
 * 2003-10-17 gn   implemented non recursive scheme
 * 2013-02-04 mrab added fullmatch primitive
 *
 * Copyright (c) 1997-2001 by Secret Labs AB.  All rights reserved.
 *
 * This version of the SRE library can be redistributed under CNRI's
 * Python 1.6 license.  For any other use, please contact Secret Labs
 * AB (info@pythonware.com).
 *
 * Portions of this engine have been developed in cooperation with
 * CNRI.  Hewlett-Packard provided funding for 1.6 integration and
 * other compatibility work.
 */

/* shedskin: the matching engine part of CPython 3.13's Modules/_sre/sre.c
   (see LICENSE in this directory), for 32-bit strings only. the Python
   object glue is left out; unicode character properties come from
   shedskin's own character database (builtin/unicode.hpp). */

#ifndef SRE_ENGINE_H
#define SRE_ENGINE_H

#include <ctype.h>                   // tolower(), toupper(), isalnum()
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

typedef uint32_t Py_UCS4;
typedef ptrdiff_t Py_ssize_t;
#ifndef PY_SSIZE_T_MAX /* already defined by Python.h, for extension modules */
#define PY_SSIZE_T_MAX PTRDIFF_MAX
#endif
#if SIZE_MAX > 0xFFFFFFFFu  /* no __SIZEOF_SIZE_T__/__SIZEOF_POINTER__ under msvc */
#define SIZEOF_SIZE_T 8
#else
#define SIZEOF_SIZE_T 4
#endif
#if UINTPTR_MAX > 0xFFFFFFFFu
#define SIZEOF_VOID_P 8
#else
#define SIZEOF_VOID_P 4
#endif
#ifndef Py_STRINGIFY
#define Py_STRINGIFY(x) #x
#endif
#define PyErr_CheckSignals() 0
#if defined(__GNUC__)
#define HAVE_COMPUTED_GOTOS 1
#endif

#include "sre.h"

namespace __re__ {

#define SRE_CODE_BITS (8 * sizeof(SRE_CODE))

static int sre_isalnum(unsigned int ch) {
    return (unsigned int)isalnum((int)ch);
}

static unsigned int sre_tolower(unsigned int ch) {
    return (unsigned int)tolower((int)ch);
}

static unsigned int sre_toupper(unsigned int ch) {
    return (unsigned int)toupper((int)ch);
}


/* -------------------------------------------------------------------- */

#define LOCAL(type) static inline type

/* error codes */
#define SRE_ERROR_ILLEGAL -1 /* illegal opcode */
#define SRE_ERROR_STATE -2 /* illegal state */
#define SRE_ERROR_RECURSION_LIMIT -3 /* runaway recursion */
#define SRE_ERROR_MEMORY -9 /* out of memory */
#define SRE_ERROR_INTERRUPTED -10 /* signal handler raised exception */

#  define INIT_TRACE(state)
#  define DO_TRACE 0
#  define TRACE(v)

/* -------------------------------------------------------------------- */
/* search engine state */

/* shedskin: ascii-only versions of CPython's Py_ISDIGIT etc. (replacing
   the Python.h ones, for extension modules) */
#undef Py_ISDIGIT
#undef Py_ISSPACE
#undef Py_ISALNUM
#undef Py_TOLOWER
#define Py_ISDIGIT(ch) ((ch) >= '0' && (ch) <= '9')
#define Py_ISSPACE(ch) ((ch) == ' ' || ((ch) >= '\t' && (ch) <= '\r'))
#define Py_ISALNUM(ch) (Py_ISDIGIT(ch) || ((ch) >= 'a' && (ch) <= 'z') || ((ch) >= 'A' && (ch) <= 'Z'))
#define Py_TOLOWER(ch) (((ch) >= 'A' && (ch) <= 'Z') ? (ch) + 32 : (ch))

#define SRE_IS_DIGIT(ch)\
    ((ch) <= '9' && Py_ISDIGIT(ch))
#define SRE_IS_SPACE(ch)\
    ((ch) <= ' ' && Py_ISSPACE(ch))
#define SRE_IS_LINEBREAK(ch)\
    ((ch) == '\n')
#define SRE_IS_WORD(ch)\
    ((ch) <= 'z' && (Py_ISALNUM(ch) || (ch) == '_'))

static unsigned int sre_lower_ascii(unsigned int ch)
{
    return ((ch) < 128 ? Py_TOLOWER(ch) : ch);
}

/* locale-specific character predicates */
/* !(c & ~N) == (c < N+1) for any unsigned c, this avoids
 * warnings when c's type supports only numbers < N+1 */
#define SRE_LOC_IS_ALNUM(ch) (!((ch) & ~255) ? sre_isalnum((ch)) : 0)
#define SRE_LOC_IS_WORD(ch) (SRE_LOC_IS_ALNUM((ch)) || (ch) == '_')

static unsigned int sre_lower_locale(unsigned int ch)
{
    return ((ch) < 256 ? (unsigned int)sre_tolower((ch)) : ch);
}

static unsigned int sre_upper_locale(unsigned int ch)
{
    return ((ch) < 256 ? (unsigned int)sre_toupper((ch)) : ch);
}

/* unicode-specific character predicates */

/* shedskin: CPython's simple case mappings (Py_UNICODE_TOLOWER/TOUPPER)
   are the first character of the full ones */
static inline unsigned int __sre_case(unsigned int ch, int which)
{
    const __shedskin__::__ss_char_record *r = __shedskin__::__ss_char_rec(ch);
    int v = r->map[which];
    if (!(r->flags & __SS_CHAR_EXTENDED_CASE))
        return (unsigned int)((int)ch + v);
    return __shedskin__::__ss_char_ext_case[v & 0xffffff];
}

static inline int __sre_linebreak(unsigned int ch)
{
    switch (ch) {
    case 0x0a: case 0x0b: case 0x0c: case 0x0d: case 0x1c: case 0x1d:
    case 0x1e: case 0x85: case 0x2028: case 0x2029:
        return 1;
    }
    return 0;
}

#define SRE_UNI_IS_DIGIT(ch) __shedskin__::__ss_char_has((ch), __SS_CHAR_DECIMAL)
#define SRE_UNI_IS_SPACE(ch) __shedskin__::__ss_char_space(ch)
#define SRE_UNI_IS_LINEBREAK(ch) __sre_linebreak(ch)
#define SRE_UNI_IS_ALNUM(ch) __shedskin__::__ss_char_has((ch), __SS_CHAR_ALPHA|__SS_CHAR_DECIMAL|__SS_CHAR_DIGIT|__SS_CHAR_NUMERIC)
#define SRE_UNI_IS_WORD(ch) (SRE_UNI_IS_ALNUM(ch) || (ch) == '_')

static unsigned int sre_lower_unicode(unsigned int ch)
{
    return __sre_case(ch, __shedskin__::__SS_CHAR_LOWER_MAP);
}

static unsigned int sre_upper_unicode(unsigned int ch)
{
    return __sre_case(ch, __shedskin__::__SS_CHAR_UPPER_MAP);
}

LOCAL(int)
sre_category(SRE_CODE category, unsigned int ch)
{
    switch (category) {

    case SRE_CATEGORY_DIGIT:
        return SRE_IS_DIGIT(ch);
    case SRE_CATEGORY_NOT_DIGIT:
        return !SRE_IS_DIGIT(ch);
    case SRE_CATEGORY_SPACE:
        return SRE_IS_SPACE(ch);
    case SRE_CATEGORY_NOT_SPACE:
        return !SRE_IS_SPACE(ch);
    case SRE_CATEGORY_WORD:
        return SRE_IS_WORD(ch);
    case SRE_CATEGORY_NOT_WORD:
        return !SRE_IS_WORD(ch);
    case SRE_CATEGORY_LINEBREAK:
        return SRE_IS_LINEBREAK(ch);
    case SRE_CATEGORY_NOT_LINEBREAK:
        return !SRE_IS_LINEBREAK(ch);

    case SRE_CATEGORY_LOC_WORD:
        return SRE_LOC_IS_WORD(ch);
    case SRE_CATEGORY_LOC_NOT_WORD:
        return !SRE_LOC_IS_WORD(ch);

    case SRE_CATEGORY_UNI_DIGIT:
        return SRE_UNI_IS_DIGIT(ch);
    case SRE_CATEGORY_UNI_NOT_DIGIT:
        return !SRE_UNI_IS_DIGIT(ch);
    case SRE_CATEGORY_UNI_SPACE:
        return SRE_UNI_IS_SPACE(ch);
    case SRE_CATEGORY_UNI_NOT_SPACE:
        return !SRE_UNI_IS_SPACE(ch);
    case SRE_CATEGORY_UNI_WORD:
        return SRE_UNI_IS_WORD(ch);
    case SRE_CATEGORY_UNI_NOT_WORD:
        return !SRE_UNI_IS_WORD(ch);
    case SRE_CATEGORY_UNI_LINEBREAK:
        return SRE_UNI_IS_LINEBREAK(ch);
    case SRE_CATEGORY_UNI_NOT_LINEBREAK:
        return !SRE_UNI_IS_LINEBREAK(ch);
    }
    return 0;
}

LOCAL(int)
char_loc_ignore(SRE_CODE pattern, SRE_CODE ch)
{
    return ch == pattern
        || (SRE_CODE) sre_lower_locale(ch) == pattern
        || (SRE_CODE) sre_upper_locale(ch) == pattern;
}


/* helpers */

static void
data_stack_dealloc(SRE_STATE* state)
{
    if (state->data_stack) {
        free(state->data_stack);
        state->data_stack = NULL;
    }
    state->data_stack_size = state->data_stack_base = 0;
}

static int
data_stack_grow(SRE_STATE* state, Py_ssize_t size)
{
    INIT_TRACE(state);
    Py_ssize_t minsize, cursize;
    minsize = state->data_stack_base+size;
    cursize = state->data_stack_size;
    if (cursize < minsize) {
        void* stack;
        cursize = minsize+minsize/4+1024;
        TRACE(("allocate/grow stack %zd\n", cursize));
        stack = realloc(state->data_stack, cursize);
        if (!stack) {
            data_stack_dealloc(state);
            return SRE_ERROR_MEMORY;
        }
        state->data_stack = (char *)stack;
        state->data_stack_size = cursize;
    }
    return 0;
}

/* memory pool functions for SRE_REPEAT, this can avoid memory
   leak when SRE(match) function terminates abruptly.
   state->repeat_pool_used is a doubly-linked list, so that we
   can remove a SRE_REPEAT node from it.
   state->repeat_pool_unused is a singly-linked list, we put/get
   node at the head. */
static SRE_REPEAT *
repeat_pool_malloc(SRE_STATE *state)
{
    SRE_REPEAT *repeat;

    if (state->repeat_pool_unused) {
        /* remove from unused pool (singly-linked list) */
        repeat = state->repeat_pool_unused;
        state->repeat_pool_unused = repeat->pool_next;
    }
    else {
        repeat = (SRE_REPEAT *)malloc(sizeof(SRE_REPEAT));
        if (!repeat) {
            return NULL;
        }
    }

    /* add to used pool (doubly-linked list) */
    SRE_REPEAT *temp = state->repeat_pool_used;
    if (temp) {
        temp->pool_prev = repeat;
    }
    repeat->pool_prev = NULL;
    repeat->pool_next = temp;
    state->repeat_pool_used = repeat;

    return repeat;
}

static void
repeat_pool_free(SRE_STATE *state, SRE_REPEAT *repeat)
{
    SRE_REPEAT *prev = repeat->pool_prev;
    SRE_REPEAT *next = repeat->pool_next;

    /* remove from used pool (doubly-linked list) */
    if (prev) {
        prev->pool_next = next;
    }
    else {
        state->repeat_pool_used = next;
    }
    if (next) {
        next->pool_prev = prev;
    }

    /* add to unused pool (singly-linked list) */
    repeat->pool_next = state->repeat_pool_unused;
    state->repeat_pool_unused = repeat;
}

static void
repeat_pool_clear(SRE_STATE *state)
{
    /* clear used pool */
    SRE_REPEAT *next = state->repeat_pool_used;
    state->repeat_pool_used = NULL;
    while (next) {
        SRE_REPEAT *temp = next;
        next = temp->pool_next;
        free(temp);
    }

    /* clear unused pool */
    next = state->repeat_pool_unused;
    state->repeat_pool_unused = NULL;
    while (next) {
        SRE_REPEAT *temp = next;
        next = temp->pool_next;
        free(temp);
    }
}

/* generate 32-bit unicode version */

/* sre_lib.h dispatches on opcodes using computed gotos, a GNU extension */
#if defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpedantic"
#endif

#define SRE_CHAR Py_UCS4
#define SIZEOF_SRE_CHAR 4
#define SRE(F) sre_ucs4_##F
#include "sre_lib.h"

#if defined(__GNUC__)
#pragma GCC diagnostic pop
#endif

/* -------------------------------------------------------------------- */
/* state handling (shedskin: simplified versions of sre.c's state_init,
   state_reset and state_fini, for a 32-bit string) */

LOCAL(void)
state_reset(SRE_STATE* state)
{
    /* state->mark will be set to 0 in SRE_OP_MARK dynamically. */
    /*memset(state->mark, 0, sizeof(*state->mark) * SRE_MARK_SIZE);*/

    state->lastmark = -1;
    state->lastindex = -1;

    state->repeat = NULL;

    data_stack_dealloc(state);
}

LOCAL(void)
state_init(SRE_STATE* state, Py_ssize_t groups, const Py_UCS4* ptr,
           Py_ssize_t length, Py_ssize_t start, Py_ssize_t end)
{
    memset(state, 0, sizeof(SRE_STATE));

    state->mark = (const void **)malloc(sizeof(void *) * (groups * 2 + 1));
    state->lastmark = -1;
    state->lastindex = -1;

    /* adjust boundaries */
    if (start < 0)
        start = 0;
    else if (start > length)
        start = length;

    if (end < 0)
        end = 0;
    else if (end > length)
        end = length;

    state->charsize = 4;

    state->beginning = ptr;

    state->start = (const void*) (ptr + start);
    state->end = (const void*) (ptr + end);

    state->pos = start;
    state->endpos = end;
}

LOCAL(void)
state_fini(SRE_STATE* state)
{
    data_stack_dealloc(state);
    free((void*) state->mark);
    state->mark = NULL;
    /* SRE_REPEAT pool */
    repeat_pool_clear(state);
}

/* calculate offset from start of string */
#define STATE_OFFSET(state, member)\
    (((char*)(member) - (char*)(state)->beginning) / (state)->charsize)

} // namespace __re__

#endif
