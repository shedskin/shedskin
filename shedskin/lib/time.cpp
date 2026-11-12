/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "time.hpp"
#include "time.h"
#include <cerrno>
#include <climits>
#include <cmath>
#include <cstring>
#include <limits>
#include <algorithm>
#include <vector>

namespace __time__ {

clock_t start;
__ss_int timezone;
__ss_int altzone;
__ss_int daylight;
tuple2<str *, str *> *tzname;

__ss_int __ss_CLOCK_REALTIME;
__ss_int __ss_CLOCK_MONOTONIC;
__ss_int __ss_CLOCK_MONOTONIC_RAW;
__ss_int __ss_CLOCK_PROCESS_CPUTIME_ID;
__ss_int __ss_CLOCK_THREAD_CPUTIME_ID;
__ss_int __ss_CLOCK_BOOTTIME;
__ss_int __ss_CLOCK_TAI;
__ss_int __ss_CLOCK_UPTIME_RAW;

#ifdef _MSC_VER

#define DELTA_EPOCH_IN_100NS    INT64_C(116444736000000000)
#define POW10_7 10000000

static int __ss_realtime_gettime(struct timespec *tp)
{
    unsigned __int64 t;
    LARGE_INTEGER pf, pc;
    union {
        unsigned __int64 u64;
        FILETIME ft;
    } ct;

    GetSystemTimeAsFileTime(&ct.ft);

    t = ct.u64 - DELTA_EPOCH_IN_100NS;
    tp->tv_sec = t / POW10_7;
    tp->tv_nsec = ((int) (t % POW10_7)) * 100;

    return 0;
}

#undef DELTA_EPOCH_IN_100NS
#undef POW10_7

#endif

str *const_0, *const_1;

class_ *cl_struct_time;

/* as CPython: 9 to 11 items (tm_zone, tm_gmtoff), of which 9 are visible */
static tuple2<__ss_int, __ss_int> *__struct_time_items(tuple2<__ss_int, __ss_int> *t) {
    __ss_int n = len(t);
    if (n < 9)
        throw new TypeError(__add_strs(3, new str("time.struct_time() takes an at least 9-sequence ("), __str(n), new str("-sequence given)")));
    if (n > 11)
        throw new TypeError(__add_strs(3, new str("time.struct_time() takes an at most 11-sequence ("), __str(n), new str("-sequence given)")));
    return n == 9 ? t : t->__slice__(3, 0, 9, 0);
}

/* as CPython: a plain tuple argument must have exactly 9 items */
static tuple2<__ss_int, __ss_int> *__time_tuple_arg(tuple2<__ss_int, __ss_int> *t, const char *func) {
    if (len(t) != 9)
        throw new TypeError(__add_strs(2, new str(func), new str("(): illegal time tuple argument")));
    return t;
}

struct_time::struct_time(tuple2<__ss_int, __ss_int> *_tuple) : tuple2<__ss_int, __ss_int>(__struct_time_items(_tuple)) {
    this->__class__ = cl_struct_time;
    _tuple = __struct_time_items(_tuple);
    this->tm_year = _tuple->__getitem__(0);
    this->tm_mon = _tuple->__getitem__(1);
    this->tm_mday = _tuple->__getitem__(2);
    this->tm_hour = _tuple->__getitem__(3);
    this->tm_min = _tuple->__getitem__(4);
    this->tm_sec = _tuple->__getitem__(5);
    this->tm_wday = _tuple->__getitem__(6);
    this->tm_yday = _tuple->__getitem__(7);
    this->tm_isdst = _tuple->__getitem__(8);
}

str *struct_time::__repr__() {

    return __mod6(const_1, 9, this->tm_year, this->tm_mon, this->tm_mday, this->tm_hour, this->tm_min, this->tm_sec, this->tm_wday, this->tm_yday, this->tm_isdst);
}

/* like CPython's gettmarg(), which parses each field as a C int: raise
   OverflowError instead of silently truncating e.g. a year of 10**12 */
/* by value: a plain 'new tm' is malloc memory that was never freed. value-
   initialized, so platform-specific fields (tm_zone, tm_gmtoff) are not garbage */
tm tuple2tm(struct_time* tuple) {
    tm time_tuple = tm();

    int year = __ss_cint_i(tuple->tm_year);
    int mon = __ss_cint_i(tuple->tm_mon);
    int mday = __ss_cint_i(tuple->tm_mday);
    int hour = __ss_cint_i(tuple->tm_hour);
    int min = __ss_cint_i(tuple->tm_min);
    int sec = __ss_cint_i(tuple->tm_sec);
    int wday = __ss_cint_i(tuple->tm_wday);
    int yday = __ss_cint_i(tuple->tm_yday);
    int isdst = __ss_cint_i(tuple->tm_isdst);

    if (year < INT_MIN + 1900)
        throw new OverflowError(new str("year out of range"));

    time_tuple.tm_sec = sec;
    time_tuple.tm_min = min;
    time_tuple.tm_hour = hour;
    time_tuple.tm_mday = mday;
    time_tuple.tm_mon = (int)((__ss_int)mon - 1); /* (no int overflow) */
    time_tuple.tm_year = year - 1900;
    time_tuple.tm_wday = wday == 6 ? 0 : (int)((__ss_int)wday + 1);
    time_tuple.tm_yday = (int)((__ss_int)yday - 1);
    time_tuple.tm_isdst = isdst;
#ifndef WIN32
    time_tuple.tm_gmtoff = (long)tuple->tm_gmtoff;
    if (tuple->tm_zone)
        time_tuple.tm_zone = (char *)tuple->tm_zone->c_str();
#endif

    return time_tuple;
}

/* CPython's gettmarg()+checktm(), used by strftime() and asctime(): zero is
   accepted for tm_mon/tm_mday/tm_yday (meaning the lowest valid value),
   tm_wday is taken modulo 7, and anything else out of range raises
   ValueError instead of making libc index its name tables out of bounds
   (printing '?') or return NULL. */
tm tuple2tm_checked(struct_time* tuple) {
    tm time_tuple = tuple2tm(tuple);

    if (time_tuple.tm_mon == -1)
        time_tuple.tm_mon = 0;
    else if (time_tuple.tm_mon < 0 || time_tuple.tm_mon > 11)
        throw new ValueError(new str("month out of range"));
    if (time_tuple.tm_mday == 0)
        time_tuple.tm_mday = 1;
    else if (time_tuple.tm_mday < 0 || time_tuple.tm_mday > 31)
        throw new ValueError(new str("day of month out of range"));
    if (time_tuple.tm_hour < 0 || time_tuple.tm_hour > 23)
        throw new ValueError(new str("hour out of range"));
    if (time_tuple.tm_min < 0 || time_tuple.tm_min > 59)
        throw new ValueError(new str("minute out of range"));
    if (time_tuple.tm_sec < 0 || time_tuple.tm_sec > 61)
        throw new ValueError(new str("seconds out of range"));
    time_tuple.tm_wday = (int)((tuple->tm_wday + 1) % 7);
    if (time_tuple.tm_wday < 0)
        throw new ValueError(new str("day of week out of range"));
    if (time_tuple.tm_yday == -1)
        time_tuple.tm_yday = 0;
    else if (time_tuple.tm_yday < 0 || time_tuple.tm_yday > 365)
        throw new ValueError(new str("day of year out of range"));
    if (time_tuple.tm_isdst < -1)
        time_tuple.tm_isdst = -1;
    else if (time_tuple.tm_isdst > 1)
        time_tuple.tm_isdst = 1;

    return time_tuple;
}

struct_time *tm2tuple(tm* tm_time) {
    struct_time *time_tuple = new struct_time(new tuple2<__ss_int, __ss_int>(9,
        (__ss_int)(tm_time->tm_year + 1900),
        (__ss_int)(tm_time->tm_mon + 1),
        (__ss_int)(tm_time->tm_mday),
        (__ss_int)(tm_time->tm_hour),
        (__ss_int)(tm_time->tm_min),
        (__ss_int)(tm_time->tm_sec),
        (__ss_int)(tm_time->tm_wday == 0 ? 6 : tm_time->tm_wday - 1),
        (__ss_int)(tm_time->tm_yday + 1),
        (__ss_int)(tm_time->tm_isdst)));

    return time_tuple;
}

__ss_float time() {
    timespec ts { 0, 0 };
#ifdef _MSC_VER
    if (__ss_realtime_gettime(&ts) == -1)
#else
    if (::clock_gettime(CLOCK_REALTIME, &ts) == -1)
#endif
	    throw new Exception(new str("clock_gettime"));
    return (__ss_float)ts.tv_sec + (__ss_float)ts.tv_nsec/1000000000.0;
}

__ss_int time_ns() {
    timespec ts { 0, 0 };
#ifdef _MSC_VER
    if (__ss_realtime_gettime(&ts) == -1)
#else
    if (::clock_gettime(CLOCK_REALTIME, &ts) == -1)
#endif
	    throw new Exception(new str("clock_gettime"));
    return (__ss_int)((int64_t)ts.tv_sec * 1000000000 + (int64_t)ts.tv_nsec);
}

#ifdef WIN32
__ss_float perf_counter() {
    static LARGE_INTEGER frequency;
    static bool frequency_initialized = false;
    if (!frequency_initialized) {
        QueryPerformanceFrequency(&frequency);
        frequency_initialized = true;
    }
    LARGE_INTEGER counter;
    QueryPerformanceCounter(&counter);
    return (__ss_float)counter.QuadPart / (__ss_float)frequency.QuadPart;
}
__ss_float monotonic() {
    return perf_counter();
}
__ss_float process_time() {
    FILETIME creation, exit, kernel, user;
    GetProcessTimes(GetCurrentProcess(), &creation, &exit, &kernel, &user);
    ULARGE_INTEGER k, u;
    k.LowPart = kernel.dwLowDateTime;
    k.HighPart = kernel.dwHighDateTime;
    u.LowPart = user.dwLowDateTime;
    u.HighPart = user.dwHighDateTime;
    /* FILETIME units are 100ns */
    return (__ss_float)(k.QuadPart + u.QuadPart) / 10000000.0;
}
__ss_float thread_time() {
    FILETIME creation, exit, kernel, user;
    GetThreadTimes(GetCurrentThread(), &creation, &exit, &kernel, &user);
    ULARGE_INTEGER k, u;
    k.LowPart = kernel.dwLowDateTime;
    k.HighPart = kernel.dwHighDateTime;
    u.LowPart = user.dwLowDateTime;
    u.HighPart = user.dwHighDateTime;
    /* FILETIME units are 100ns */
    return (__ss_float)(k.QuadPart + u.QuadPart) / 10000000.0;
}
__ss_int perf_counter_ns() {
    static LARGE_INTEGER frequency;
    static bool frequency_initialized = false;
    if (!frequency_initialized) {
        QueryPerformanceFrequency(&frequency);
        frequency_initialized = true;
    }
    LARGE_INTEGER counter;
    QueryPerformanceCounter(&counter);
    /* Split into whole seconds and remainder before scaling to nanoseconds:
       counter.QuadPart counts ticks since boot, so multiplying it by 1e9 up
       front overflows int64 after a few minutes of uptime at a typical 10MHz
       QPC frequency. */
    int64_t q = counter.QuadPart, f = frequency.QuadPart;
    return (__ss_int)((q / f) * (int64_t)1000000000 + ((q % f) * (int64_t)1000000000) / f);
}
__ss_int monotonic_ns() {
    return perf_counter_ns();
}
__ss_int process_time_ns() {
    FILETIME creation, exit, kernel, user;
    GetProcessTimes(GetCurrentProcess(), &creation, &exit, &kernel, &user);
    ULARGE_INTEGER k, u;
    k.LowPart = kernel.dwLowDateTime;
    k.HighPart = kernel.dwHighDateTime;
    u.LowPart = user.dwLowDateTime;
    u.HighPart = user.dwHighDateTime;
    /* FILETIME units are 100ns */
    return (__ss_int)((k.QuadPart + u.QuadPart) * (int64_t)100);
}
__ss_int thread_time_ns() {
    FILETIME creation, exit, kernel, user;
    GetThreadTimes(GetCurrentThread(), &creation, &exit, &kernel, &user);
    ULARGE_INTEGER k, u;
    k.LowPart = kernel.dwLowDateTime;
    k.HighPart = kernel.dwHighDateTime;
    u.LowPart = user.dwLowDateTime;
    u.HighPart = user.dwHighDateTime;
    /* FILETIME units are 100ns */
    return (__ss_int)((k.QuadPart + u.QuadPart) * (int64_t)100);
}
#else
__ss_float perf_counter() {
    timespec ts { 0, 0 };
    if (::clock_gettime(CLOCK_MONOTONIC, &ts) == -1)
        throw new Exception(new str("clock_gettime"));
    return (__ss_float)ts.tv_sec + (__ss_float)ts.tv_nsec/1000000000.0;
}

__ss_float monotonic() {
    return perf_counter();
}

__ss_float process_time() {
    timespec ts { 0, 0 };
    if (::clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &ts) == -1)
        throw new Exception(new str("clock_gettime"));
    return (__ss_float)ts.tv_sec + (__ss_float)ts.tv_nsec/1000000000.0;
}

__ss_int perf_counter_ns() {
    timespec ts { 0, 0 };
    if (::clock_gettime(CLOCK_MONOTONIC, &ts) == -1)
        throw new Exception(new str("clock_gettime"));
    return (__ss_int)((int64_t)ts.tv_sec * 1000000000 + (int64_t)ts.tv_nsec);
}

__ss_int monotonic_ns() {
    return perf_counter_ns();
}

__ss_int process_time_ns() {
    timespec ts { 0, 0 };
    if (::clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &ts) == -1)
        throw new Exception(new str("clock_gettime"));
    return (__ss_int)((int64_t)ts.tv_sec * 1000000000 + (int64_t)ts.tv_nsec);
}

__ss_float thread_time() {
    timespec ts { 0, 0 };
    if (::clock_gettime(CLOCK_THREAD_CPUTIME_ID, &ts) == -1)
        throw new Exception(new str("clock_gettime"));
    return (__ss_float)ts.tv_sec + (__ss_float)ts.tv_nsec/1000000000.0;
}

__ss_int thread_time_ns() {
    timespec ts { 0, 0 };
    if (::clock_gettime(CLOCK_THREAD_CPUTIME_ID, &ts) == -1)
        throw new Exception(new str("clock_gettime"));
    return (__ss_int)((int64_t)ts.tv_sec * 1000000000 + (int64_t)ts.tv_nsec);
}
#endif

/* clock_gettime/clock_gettime_ns/clock_getres

   On POSIX these forward straight to the corresponding system calls. Windows
   has no clock_gettime at all, so there the CLOCK_* constants are synthetic
   ids (see __init) dispatched onto the Win32 clock APIs already used above,
   which keeps the Python-level API identical across platforms. Clock ids the
   platform does not provide are -1, which reaches the default branch below
   and raises OSError, mirroring the EINVAL a POSIX system would return. */

#ifdef WIN32

static __ss_int __ss_win_clock_ns(__ss_int clk_id) {
    if (clk_id == __ss_CLOCK_REALTIME) {
        FILETIME ft;
        ULARGE_INTEGER u;
        GetSystemTimeAsFileTime(&ft);
        u.LowPart = ft.dwLowDateTime;
        u.HighPart = ft.dwHighDateTime;
        /* FILETIME is 100ns units since 1601-01-01 */
        return (__ss_int)(((int64_t)u.QuadPart - (int64_t)116444736000000000LL) * 100);
    } else if (clk_id == __ss_CLOCK_MONOTONIC) {
        return monotonic_ns();
    } else if (clk_id == __ss_CLOCK_PROCESS_CPUTIME_ID) {
        return process_time_ns();
    } else if (clk_id == __ss_CLOCK_THREAD_CPUTIME_ID) {
        return thread_time_ns();
    }
    errno = EINVAL;
    __throw_oserror();
}

__ss_float clock_gettime(__ss_int clk_id) {
    return (__ss_float)__ss_win_clock_ns(clk_id) / 1000000000.0;
}

__ss_int clock_gettime_ns(__ss_int clk_id) {
    return __ss_win_clock_ns(clk_id);
}

__ss_float clock_getres(__ss_int clk_id) {
    if (clk_id == __ss_CLOCK_MONOTONIC) {
        LARGE_INTEGER frequency;
        QueryPerformanceFrequency(&frequency);
        return 1.0 / (__ss_float)frequency.QuadPart;
    } else if (clk_id == __ss_CLOCK_REALTIME ||
               clk_id == __ss_CLOCK_PROCESS_CPUTIME_ID ||
               clk_id == __ss_CLOCK_THREAD_CPUTIME_ID) {
        return 1e-7; /* FILETIME granularity: 100ns */
    }
    errno = EINVAL;
    __throw_oserror();
}

#else

/* reject -1 ("not available on this platform", see __init_clock_ids) up
   front: on FreeBSD, ids with the high bit set are valid cpu-time clocks
   (CPUCLOCK_BIT), so e.g. CLOCK_TAI would otherwise silently succeed */
static clockid_t __ss_clock_id(__ss_int clk_id) {
    if (clk_id == -1) {
        errno = EINVAL;
        __throw_oserror();
    }
    return (clockid_t)clk_id;
}

__ss_float clock_gettime(__ss_int clk_id) {
    timespec ts { 0, 0 };
    if (::clock_gettime(__ss_clock_id(clk_id), &ts) == -1)
        __throw_oserror();
    return (__ss_float)ts.tv_sec + (__ss_float)ts.tv_nsec/1000000000.0;
}

__ss_int clock_gettime_ns(__ss_int clk_id) {
    timespec ts { 0, 0 };
    if (::clock_gettime(__ss_clock_id(clk_id), &ts) == -1)
        __throw_oserror();
    return (__ss_int)((int64_t)ts.tv_sec * 1000000000 + (int64_t)ts.tv_nsec);
}

__ss_float clock_getres(__ss_int clk_id) {
    timespec ts { 0, 0 };
    if (::clock_getres(__ss_clock_id(clk_id), &ts) == -1)
        __throw_oserror();
    return (__ss_float)ts.tv_sec + (__ss_float)ts.tv_nsec/1000000000.0;
}

#endif

/* get_clock_info: describes the clocks exactly as implemented above (not
   necessarily as CPython implements them on the same platform, e.g. on macOS
   CPython uses mach_absolute_time() for monotonic/perf_counter). */

class_ *cl_clock_info;

__clock_info::__clock_info(str *implementation, __ss_bool monotonic, __ss_bool adjustable, __ss_float resolution) {
    this->__class__ = cl_clock_info;
    this->implementation = implementation;
    this->monotonic = monotonic;
    this->adjustable = adjustable;
    this->resolution = resolution;
}

str *__clock_info::__repr__() {
    return __mod6(new str("namespace(implementation=%s, monotonic=%s, adjustable=%s, resolution=%s)"), 4,
        repr(implementation), repr(monotonic), repr(adjustable), repr(resolution));
}

__clock_info *get_clock_info(str *name) {
    str *impl;
    __ss_bool mono = True, adjustable = False;
    __ss_float res;

#ifdef WIN32
    if (__eq(name, new str("time"))) {
#ifdef _MSC_VER
        impl = new str("GetSystemTimeAsFileTime()");
#else
        impl = new str("clock_gettime(CLOCK_REALTIME)");
#endif
        mono = False;
        adjustable = True;
        /* like CPython: the system clock tick, typically 15.625 ms */
        DWORD adj, inc;
        BOOL disabled;
        if (GetSystemTimeAdjustment(&adj, &inc, &disabled) && inc)
            res = (__ss_float)inc * 1e-7;
        else
            res = 1e-7;
    } else if (__eq(name, new str("monotonic")) || __eq(name, new str("perf_counter"))) {
        impl = new str("QueryPerformanceCounter()");
        LARGE_INTEGER frequency;
        QueryPerformanceFrequency(&frequency);
        res = 1.0 / (__ss_float)frequency.QuadPart;
    } else if (__eq(name, new str("process_time"))) {
        impl = new str("GetProcessTimes()");
        res = 1e-7;
    } else if (__eq(name, new str("thread_time"))) {
        impl = new str("GetThreadTimes()");
        res = 1e-7;
    } else
        throw new ValueError(new str("unknown clock"));
#else
    clockid_t clk;
    if (__eq(name, new str("time"))) {
        impl = new str("clock_gettime(CLOCK_REALTIME)");
        clk = CLOCK_REALTIME;
        mono = False;
        adjustable = True;
    } else if (__eq(name, new str("monotonic")) || __eq(name, new str("perf_counter"))) {
        impl = new str("clock_gettime(CLOCK_MONOTONIC)");
        clk = CLOCK_MONOTONIC;
    } else if (__eq(name, new str("process_time"))) {
        impl = new str("clock_gettime(CLOCK_PROCESS_CPUTIME_ID)");
        clk = CLOCK_PROCESS_CPUTIME_ID;
    } else if (__eq(name, new str("thread_time"))) {
        impl = new str("clock_gettime(CLOCK_THREAD_CPUTIME_ID)");
        clk = CLOCK_THREAD_CPUTIME_ID;
    } else
        throw new ValueError(new str("unknown clock"));

    timespec ts { 0, 0 };
    if (::clock_getres(clk, &ts) == 0 && (ts.tv_sec || ts.tv_nsec))
        res = (__ss_float)ts.tv_sec + (__ss_float)ts.tv_nsec/1000000000.0;
    else
        res = 1e-9;
#endif

    return new __clock_info(impl, mono, adjustable, res);
}

static void __ss_check_sleep(__ss_float s) {
    if (std::isnan(s))
        throw new ValueError(new str("Invalid value NaN (not a number)"));
    if (s < 0)
        throw new ValueError(new str("sleep length must be non-negative"));
    /* as CPython: in int64 nanoseconds (also: time_t(inf) is undefined) */
    if (!(s * 1e9 < 9223372036854775808.0))
        throw new OverflowError(new str("timestamp out of range for C PyTime_t"));
}

#ifndef WIN32
void *sleep(__ss_float s) {
    __ss_check_sleep(s);
    time_t seconds = time_t(s);
    __ss_float nanosecs = (s - (__ss_float)seconds) * 1000000000l;

    struct timespec time1, time2;
    time1.tv_sec = seconds;
    time1.tv_nsec = (long)nanosecs;

    int ret = -1;

    while((ret = nanosleep(&time1, &time2)) && errno == EINTR)
	    std::swap(time1, time2);

    if (ret == -1)
	    __throw_oserror();

    return NULL;
}
#else
void *sleep(__ss_float s) {
    __ss_check_sleep(s);
    /* (Sleep() takes a DWORD of milliseconds, and INFINITE is 0xffffffff:
       sleep longer ones in pieces) */
    double ms = s * 1000;
    while (ms > 0xfffffffe) {
        Sleep(0xfffffffe);
        ms -= 0xfffffffe;
    }
    Sleep((DWORD)ms); // TODO ms resolution..
    return NULL;
    }
#endif

__ss_float mktime(struct_time *tuple) {
    tm time_tuple = tuple2tm(tuple);
    /* as in CPython: -1 is only an error if mktime() left tm_wday untouched */
    time_tuple.tm_wday = -1;
    time_t tt = ::mktime(&time_tuple);
    if (tt == (time_t)(-1) && time_tuple.tm_wday == -1)
        throw new OverflowError(new str("mktime argument out of range"));
    return (__ss_float)tt;
}

__ss_float mktime(tuple2<__ss_int, __ss_int> *tuple) {
    return mktime(new struct_time(__time_tuple_arg(tuple, "mktime")));
}

/* CPython floors the seconds-since-epoch value before converting to an
   integer, so e.g. time.gmtime(-0.5) is 1969-12-31 23:59:59, one second
   *before* the epoch. A plain static_cast<time_t> truncates towards zero
   instead, which rounds negative fractional timestamps *up* to the wrong
   second (time.gmtime(-0.5) would incorrectly land on the epoch itself). */
static inline time_t __ss_seconds_to_time_t(const __ss_float seconds) {
    if (std::isnan(seconds))
        throw new ValueError(new str("Invalid value NaN (not a number)"));
    /* like CPython, refuse timestamps that do not fit in time_t (the cast
       would be undefined behaviour) */
    double f = std::floor((double)seconds);
    const double lim = std::ldexp(1.0, (int)(sizeof(time_t) * 8 - 1));
    if (!(f >= -lim && f < lim))
        throw new OverflowError(new str("timestamp out of range for platform time_t"));
    return static_cast<time_t>(f);
}

/* int seconds are converted exactly: via __ss_float, 2**63-1 would round up
   to 2**63 and overflow (CPython raises OSError for it, as for 2**62) */
static inline time_t __ss_seconds_to_time_t(const __ss_int seconds) {
    if (sizeof(__ss_int) > sizeof(time_t) &&
        (seconds < (__ss_int)std::numeric_limits<time_t>::min() ||
         seconds > (__ss_int)std::numeric_limits<time_t>::max()))
        throw new OverflowError(new str("timestamp out of range for platform time_t"));
    return static_cast<time_t>(seconds);
}

/* also keep the UTC offset and zone name of the result (see struct_time).
   windows has no tm_gmtoff/tm_zone, so derive them as CPython does there:
   "UTC" for gmtime(), else strftime('%Z') and the difference with timegm() */
static struct_time *__ss_tm2tuple_zone(tm *tm_time, time_t timet, bool utc) {
    struct_time *time_tuple = tm2tuple(tm_time);
#ifndef WIN32
    (void)timet;
    (void)utc;
    time_tuple->tm_gmtoff = (__ss_int)tm_time->tm_gmtoff;
    if (tm_time->tm_zone)
        time_tuple->tm_zone = new str(tm_time->tm_zone);
#else
    if (utc)
        time_tuple->tm_zone = new str("UTC");
    else {
        tm buf = *tm_time;
        char zone[100];
        size_t n = ::strftime(zone, sizeof(zone), "%Z", &buf);
        time_tuple->tm_zone = new str(zone, n);
        time_tuple->tm_gmtoff = (__ss_int)(::_mkgmtime(&buf) - timet);
    }
#endif
    return time_tuple;
}

/* ::localtime/::gmtime return NULL (errno EOVERFLOW) when the year does
   not fit in struct tm; CPython raises OSError there. */
static struct_time *__ss_localtime(time_t timet) {
    errno = 0;
    tm *tm_time = ::localtime(&timet);
    if (!tm_time) {
        if (errno == 0) errno = EINVAL;
        __throw_oserror();
    }
    return __ss_tm2tuple_zone(tm_time, timet, false);
}

static struct_time *__ss_gmtime(time_t timet) {
    errno = 0;
    tm *tm_time = ::gmtime(&timet);
    if (!tm_time) {
        if (errno == 0) errno = EINVAL;
        __throw_oserror();
    }
    return __ss_tm2tuple_zone(tm_time, timet, true);
}

/* the no-argument variants pass time_t straight through, rather than via
   __ss_float, which under --float32 would lose ~2 minutes of precision */
struct_time *localtime() {
    return __ss_localtime(::time(NULL));
}

struct_time *localtime(const __ss_float timep) {
    return __ss_localtime(__ss_seconds_to_time_t(timep));
}

struct_time *localtime(const __ss_int timep) {
    return __ss_localtime(__ss_seconds_to_time_t(timep));
}

struct_time *gmtime() {
    return __ss_gmtime(::time(NULL));
}

struct_time *gmtime(const __ss_float seconds) {
    return __ss_gmtime(__ss_seconds_to_time_t(seconds));
}

struct_time *gmtime(const __ss_int seconds) {
    return __ss_gmtime(__ss_seconds_to_time_t(seconds));
}

str *asctime() {
    struct_time *tuple = localtime();
    return asctime(tuple);
}

/* formatted by hand like CPython's _asctime(): libc asctime() differs for
   years beyond 4 digits (macOS pads them with spaces) */
str *asctime(struct_time *tuple) {
    static const char wday_name[7][4] = {
        "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"
    };
    static const char mon_name[12][4] = {
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    };
    tm time_tuple = tuple2tm_checked(tuple);
    char buf[64];
    int n = snprintf(buf, sizeof(buf), "%s %s%3d %.2d:%.2d:%.2d %lld",
        wday_name[time_tuple.tm_wday], mon_name[time_tuple.tm_mon],
        time_tuple.tm_mday, time_tuple.tm_hour, time_tuple.tm_min,
        time_tuple.tm_sec, 1900 + (long long)time_tuple.tm_year);
    return new str(buf, (size_t)n);
}

str *asctime(tuple2<__ss_int, __ss_int> *tuple) {
    return asctime(new struct_time(__time_tuple_arg(tuple, "asctime")));
}

str *ctime() {
    return asctime(localtime());
}

str *ctime(const __ss_float seconds) {
    return asctime(localtime(seconds));
}

str *ctime(const __ss_int seconds) {
    return asctime(localtime(seconds));
}

str *strftime(str *format, struct_time* tuple) {
    /* as CPython (3.13+): the parts around an embedded NUL are formatted
       separately, and the NUL is kept (C strftime() would stop there) */
    if (__ss_has_nul(format)) {
        list<str *> *parts = format->split(new str("", 1));
        list<str *> *out = new list<str *>();
        for (__ss_int i = 0; i < len(parts); i++)
            out->append(strftime(parts->__getfast__(i), tuple));
        return (new str("", 1))->join(out);
    }
    tm time_tuple = tuple2tm_checked(tuple);
#ifdef _MSC_VER
    /* as CPython: the MSVC strftime() aborts the process (0xc0000409) on
       years it does not support */
    if (time_tuple.tm_year + 1900 < 1 || 9999 < time_tuple.tm_year + 1900)
        throw new ValueError(new str("strftime() requires year in [1; 9999]"));
#endif
    size_t fmtlen = format->unit.size();
    size_t size = fmtlen;
    size_t n;
    std::vector<char> buf; /* (not 'new char[]': malloc memory, never freed) */
    if(size==0)
        return new str();
    /* as CPython: 0 may also mean an empty result, so give up at some point */
    do {
        size *= 2;
        buf.resize(size);
#if defined(__GNUC__) || defined(__clang__) /* (MSVC: C4068) */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wformat-nonliteral"
#endif
        n = ::strftime(buf.data(), size, format->c_str(), &time_tuple);
#if defined(__GNUC__) || defined(__clang__)
#pragma GCC diagnostic pop
#endif
    } while(n == 0 && size < 256 * fmtlen);
    return new str(buf.data(), n);
}

str *strftime(str *format) {
    return strftime(format, localtime());
}

str *strftime(str *format, tuple2<__ss_int, __ss_int> *tuple) {
    struct_time *st = new struct_time(__time_tuple_arg(tuple, "strftime"));

    return strftime(format, st);
}

/******************************************************************************
 * STRPTIME
 *
 * a port of CPython's _strptime for the C locale, used on every platform, so
 * that results no longer depend on the system libc (glibc for example skips
 * %G/%V/%u without using them, and nothing knows %f). the format is matched
 * the way the regex CPython builds from it would match: each directive tries
 * the alternatives of its regex in the same order, backtracking when the rest
 * of the format does not match, literals and names ignore case, and white-
 * space in the format matches one or more white-space characters. the
 * fields found are then combined as in CPython's _strptime().
 *****************************************************************************/

static const char *__ss_sp_day_abbr[7] = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"};
static const char *__ss_sp_day_name[7] = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"};
static const char *__ss_sp_month_abbr[12] = {"jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"};
static const char *__ss_sp_month_name[12] = {"january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"};
static const char *__ss_sp_am_pm[2] = {"am", "pm"};

/* the C locale's %c, %x, %X and %r, as CPython's LocaleTime finds them */
static const char *__ss_sp_composite(__ss_char d) {
    switch (d) {
        case 'c': return "%a %b %d %H:%M:%S %Y";
        case 'x': return "%m/%d/%y";
        case 'X': return "%H:%M:%S";
        case 'r': return "%I:%M:%S %p";
        case 'R': return "%H:%M";
        case 'T': return "%H:%M:%S";
    }
    return NULL;
}

/* the regex group a directive fills in ('\0' for %%) */
static char __ss_sp_group(__ss_char d) {
    switch (d) {
        case 'e': return 'd';
        case 'k': return 'H';
        case 'l': return 'I';
        case 'P': return 'p';
        case '%': return '\0';
    }
    return (char)d;
}

static inline __ss_char __ss_sp_lower(__ss_char c) {
    if (c < 0x80)
        return (c >= 'A' && c <= 'Z') ? c + 32 : c;
    const __ss_char_record *r = __ss_char_rec(c);
    if (r->flags & __SS_CHAR_EXTENDED_CASE)
        return c;
    return (__ss_char)((int)c + r->map[__SS_CHAR_LOWER_MAP]);
}

/* the value of a decimal digit of any script, as \d and int() see it */
static inline int __ss_sp_digit(__ss_char c) {
    if (c < 0x80)
        return (c >= '0' && c <= '9') ? (int)(c - '0') : -1;
    return __ss_char_rec(c)->decimal;
}

struct __ss_sp_token {
    char kind;   /* 'l' literal, 's' white-space, 'd' directive */
    __ss_char c; /* the literal, or the directive */
    bool alt;    /* %O form */
};

static ValueError *__ss_sp_bad_directive(__GC_STR d, str *format) {
    return new ValueError(__add_strs(5, new str("'"), new str(d), new str("' is a bad directive in format '"), format, new str("'")));
}

/* split a format into tokens, as CPython's TimeRE.pattern(), checking the
   directives (before any data is looked at, as CPython does when compiling
   the regex) */
static void __ss_sp_compile(const __GC_STR &fmt, str *format, std::vector<__ss_sp_token> &out, std::string &groups) {
    size_t i = 0, n = fmt.size();
    while (i < n) {
        __ss_char c = fmt[i];
        if (__ss_char_space(c)) {
            while (i < n && __ss_char_space(fmt[i]))
                i++;
            out.push_back({'s', ' ', false});
            continue;
        }
        if (c != '%') {
            out.push_back({'l', c, false});
            i++;
            continue;
        }
        i++;
        /* flags and a width, which CPython accepts and ignores */
        while (i < n && fmt[i] < 0x80 && strchr("-_0^#", (char)fmt[i]))
            i++;
        while (i < n && fmt[i] >= '0' && fmt[i] <= '9')
            i++;
        __ss_char alt = 0;
        if (i < n && (fmt[i] == 'O' || fmt[i] == 'E'))
            alt = fmt[i++];
        if (i == n || __ss_char_space(fmt[i])) {
            if (!alt)
                throw new ValueError(__add_strs(3, new str("stray % in format '"), format, new str("'")));
            throw __ss_sp_bad_directive(__GC_STR(1, alt), format);
        }
        __ss_char d = fmt[i++];
        const char *valid = alt == 'O' ? "dmyCHIMSwep" : (alt ? "" : "dfHkIlGjmMSUwuVyYzAaBbpZ%ePWTRrXxc");
        if (d >= 0x80 || !*valid || !strchr(valid, (char)d))
            throw __ss_sp_bad_directive(alt ? __GC_STR({alt, d}) : __GC_STR(1, d), format);
        if (!alt && __ss_sp_composite(d)) {
            __GC_STR sub;
            for (const char *p = __ss_sp_composite(d); *p; p++)
                sub += (__ss_char)*p;
            __ss_sp_compile(sub, format, out, groups);
            continue;
        }
        char g = __ss_sp_group(d);
        if (g) {
            if (groups.find(g) != std::string::npos) /* re.error in CPython */
                throw new ValueError(__add_strs(3, new str("redefinition of group name '"), new str(__GC_STR(1, (__ss_char)g)), new str("'")));
            groups += g;
        }
        out.push_back({'d', d, alt == 'O' && d != 'p'}); /* %Op is %p */
    }
}

struct __ss_sp_found {
    char group;
    int val;          /* the number, or the index of the name */
    size_t pos, len;  /* where in the data */
};

struct __ss_sp_matcher {
    const std::vector<__ss_sp_token> *toks;
    const __ss_char *s, *e;
    std::vector<__ss_sp_found> found;
    std::vector<__GC_STR> zones; /* %Z names, longest first */
};

static const __ss_char *__ss_sp_match(__ss_sp_matcher &m, size_t ti, const __ss_char *p);

static const __ss_char *__ss_sp_try(__ss_sp_matcher &m, size_t ti, const __ss_char *p, const __ss_char *q, char group, int val) {
    m.found.push_back({group, val, (size_t)(p - m.s), (size_t)(q - p)});
    const __ss_char *r = __ss_sp_match(m, ti + 1, q);
    if (!r)
        m.found.pop_back();
    return r;
}

/* the digits of a number of the given width at p, or -1 */
static int __ss_sp_number(const __ss_sp_matcher &m, const __ss_char *p, int width) {
    if (m.e - p < width)
        return -1;
    int v = 0;
    for (int k = 0; k < width; k++) {
        int dg = __ss_sp_digit(p[k]);
        if (dg < 0)
            return -1;
        v = v * 10 + dg;
    }
    return v;
}

/* does a lower case name start at p, ignoring case */
template<class T> static bool __ss_sp_name_at(const __ss_sp_matcher &m, const __ss_char *p, const T *name, size_t len) {
    if ((size_t)(m.e - p) < len)
        return false;
    for (size_t k = 0; k < len; k++)
        if (__ss_sp_lower(p[k]) != (__ss_char)name[k])
            return false;
    return true;
}

static const __ss_char *__ss_sp_names(__ss_sp_matcher &m, size_t ti, const __ss_char *p, char group, const char **names, int count, int base) {
    /* no C locale name is a prefix of another in the same list, so at most
       one matches */
    for (int k = 0; k < count; k++)
        if (__ss_sp_name_at(m, p, names[k], strlen(names[k])))
            return __ss_sp_try(m, ti, p, p + strlen(names[k]), group, k + base);
    return NULL;
}

/* %z: [+-]\d\d:?[0-5]\d(:?[0-5]\d(\.\d{1,6})?)?|Z */
static const __ss_char *__ss_sp_zone(__ss_sp_matcher &m, size_t ti, const __ss_char *p) {
    if (p < m.e && *p == 'Z') /* case-sensitive, even with IGNORECASE */
        return __ss_sp_try(m, ti, p, p + 1, 'z', 0);
    if (p == m.e || (*p != '+' && *p != '-') || __ss_sp_number(m, p + 1, 2) < 0)
        return NULL;
    const __ss_char *q = p + 3;
    if (q < m.e && *q == ':')
        q++;
    if (q + 1 >= m.e || *q < '0' || *q > '5' || __ss_sp_digit(q[1]) < 0)
        return NULL;
    q += 2;
    const __ss_char *ends[8];
    int nends = 0;
    const __ss_char *t = q;
    if (t < m.e && *t == ':')
        t++;
    if (t + 1 < m.e && *t >= '0' && *t <= '5' && __ss_sp_digit(t[1]) >= 0) {
        t += 2;
        if (t < m.e && *t == '.') {
            int digits = 0;
            while (digits < 6 && t + 1 + digits < m.e && __ss_sp_digit(t[1 + digits]) >= 0)
                digits++;
            for (; digits > 0; digits--)
                ends[nends++] = t + 1 + digits;
        }
        ends[nends++] = t;
    }
    ends[nends++] = q;
    for (int k = 0; k < nends; k++) {
        const __ss_char *r = __ss_sp_try(m, ti, p, ends[k], 'z', 0);
        if (r)
            return r;
    }
    return NULL;
}

static const __ss_char *__ss_sp_match(__ss_sp_matcher &m, size_t ti, const __ss_char *p) {
    if (ti == m.toks->size())
        return p;
    const __ss_sp_token &tok = (*m.toks)[ti];

    if (tok.kind == 'l' || (tok.kind == 'd' && tok.c == '%')) {
        if (p == m.e)
            return NULL;
        if (tok.c == '\'' ? (*p != '\'' && *p != 0x2bc) : __ss_sp_lower(*p) != __ss_sp_lower(tok.c))
            return NULL;
        return __ss_sp_match(m, ti + 1, p + 1);
    }
    if (tok.kind == 's') { /* \s+, greedy */
        const __ss_char *q = p;
        while (q < m.e && __ss_char_space(*q))
            q++;
        for (; q > p; q--) {
            const __ss_char *r = __ss_sp_match(m, ti + 1, q);
            if (r)
                return r;
        }
        return NULL;
    }

    char g = __ss_sp_group(tok.c);
    if (tok.alt) {
        /* the %O forms of the C locale: \d\d|\d| \d (%Ow: \d) */
        int maxw = tok.c == 'w' ? 1 : 2;
        for (int w = maxw; w > 0; w--) {
            int v = __ss_sp_number(m, p, w);
            if (v >= 0) {
                const __ss_char *r = __ss_sp_try(m, ti, p, p + w, g, v);
                if (r)
                    return r;
            }
        }
        if (maxw == 2 && p < m.e && *p == ' ') {
            int v = __ss_sp_number(m, p + 1, 1);
            if (v >= 0)
                return __ss_sp_try(m, ti, p, p + 2, g, v);
        }
        return NULL;
    }

    /* numbers: the widest alternative first, the lowest value allowed for
       more than one digit and for one digit, the highest, and whether the
       regex also takes a space and one digit */
    int maxw = 2, minw = 1, lo = 0, lo1 = 0, hi = 0;
    bool space = false;
    switch (tok.c) {
        case 'd': case 'e': lo = lo1 = 1; hi = 31; space = true; break;
        case 'H': case 'k': hi = 23; space = true; break;
        case 'I': case 'l': lo = lo1 = 1; hi = 12; space = true; break;
        case 'j': maxw = 3; lo = lo1 = 1; hi = 366; break;
        case 'm': lo = lo1 = 1; hi = 12; break;
        case 'M': hi = 59; break;
        case 'S': hi = 61; break;
        case 'U': case 'W': hi = 53; break;
        case 'V': lo = 1; hi = 53; break;
        case 'w': maxw = 1; hi = 6; break;
        case 'u': maxw = 1; lo1 = 1; hi = 7; break;
        case 'y': minw = 2; hi = 99; break;
        case 'Y': case 'G': maxw = minw = 4; hi = 9999; break;
        case 'f': maxw = 6; hi = 999999; break;
        case 'a': return __ss_sp_names(m, ti, p, 'a', __ss_sp_day_abbr, 7, 0);
        case 'A': return __ss_sp_names(m, ti, p, 'A', __ss_sp_day_name, 7, 0);
        case 'b': return __ss_sp_names(m, ti, p, 'b', __ss_sp_month_abbr, 12, 1);
        case 'B': return __ss_sp_names(m, ti, p, 'B', __ss_sp_month_name, 12, 1);
        case 'p': case 'P': return __ss_sp_names(m, ti, p, 'p', __ss_sp_am_pm, 2, 0);
        case 'z': return __ss_sp_zone(m, ti, p);
        case 'Z':
            for (size_t k = 0; k < m.zones.size(); k++)
                if (__ss_sp_name_at(m, p, m.zones[k].data(), m.zones[k].size())) {
                    const __ss_char *r = __ss_sp_try(m, ti, p, p + m.zones[k].size(), 'Z', 0);
                    if (r)
                        return r;
                }
            return NULL;
    }
    for (int w = maxw; w >= minw; w--) {
        int v = __ss_sp_number(m, p, w);
        if (v < 0 || v < (w > 1 ? lo : lo1) || v > hi)
            continue;
        if (tok.c == 'f')
            for (int k = w; k < 6; k++)
                v *= 10;
        const __ss_char *r = __ss_sp_try(m, ti, p, p + w, g, v);
        if (r)
            return r;
    }
    if (space && p < m.e && *p == ' ') {
        int v = __ss_sp_number(m, p + 1, 1);
        if (v >= lo1)
            return __ss_sp_try(m, ti, p, p + 2, g, v);
    }
    return NULL;
}

/* proleptic gregorian calendar helpers, as in CPython's datetime */
static inline bool __ss_isleap(int year) {
    return (year % 4 == 0) && (year % 100 != 0 || year % 400 == 0);
}

static int __ss_sp_days_in_month(int year, int month) {
    static const int mdays[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    return mdays[month - 1] + (month == 2 && __ss_isleap(year));
}

static int __ss_sp_ordinal(int year, int month, int day) {
    /* like datetime.date(year, month, day).toordinal() */
    if (year < 1 || year > 9999)
        throw new ValueError(__add_strs(3, new str("year "), __str((__ss_int)year), new str(" is out of range")));
    if (month < 1 || month > 12)
        throw new ValueError(new str("month must be in 1..12"));
    if (day < 1 || day > __ss_sp_days_in_month(year, month))
        throw new ValueError(new str("day is out of range for month"));
    int y = year - 1;
    int ord = y * 365 + y / 4 - y / 100 + y / 400 + day;
    for (int m = 1; m < month; m++)
        ord += __ss_sp_days_in_month(year, m);
    return ord;
}

static void __ss_sp_from_ordinal(int ord, int &year, int &month, int &day) {
    /* like datetime.date.fromordinal(ord) */
    if (ord < 1)
        throw new ValueError(new str("ordinal must be >= 1"));
    int n = ord - 1;
    int n400 = n / 146097; n %= 146097;
    int n100 = n / 36524; n %= 36524;
    int n4 = n / 1461; n %= 1461;
    int n1 = n / 365; n %= 365;
    year = n400 * 400 + n100 * 100 + n4 * 4 + n1 + 1;
    if (n1 == 4 || n100 == 4) {
        year--;
        month = 12;
        day = 31;
    } else {
        month = 1;
        while (n >= __ss_sp_days_in_month(year, month))
            n -= __ss_sp_days_in_month(year, month++);
        day = n + 1;
    }
    if (year > 9999)
        throw new ValueError(__add_strs(3, new str("year "), __str((__ss_int)year), new str(" is out of range")));
}

static void __ss_sp_from_isocalendar(int year, int week, int day, int &y, int &m, int &d) {
    /* like datetime.date.fromisocalendar() */
    if (year < 1 || year > 9999)
        throw new ValueError(__add_strs(2, new str("year must be in 1..9999, not "), __str((__ss_int)year)));
    int first = __ss_sp_ordinal(year, 1, 1);
    if (week <= 0 || week >= 53) {
        int first_weekday = first % 7; /* sunday == 0 */
        if (week != 53 || !(first_weekday == 4 || (first_weekday == 3 && __ss_isleap(year))))
            throw new ValueError(__add_strs(2, new str("Invalid week: "), __str((__ss_int)week)));
    }
    if (day <= 0 || day >= 8)
        throw new ValueError(__add_strs(3, new str("Invalid weekday: "), __str((__ss_int)day), new str(" (range is [1, 7])")));
    /* the monday of week 1 */
    int monday = first - ((first + 6) % 7);
    if ((first + 6) % 7 > 3)
        monday += 7;
    __ss_sp_from_ordinal(monday + (week - 1) * 7 + (day - 1), y, m, d);
}

void __ss_strptime(str *string, str *format, __ss_strptime_result &res) {
    std::vector<__ss_sp_token> toks;
    std::string groups;
    __ss_sp_compile(format->unit, format, toks, groups);

    __ss_sp_matcher m;
    m.toks = &toks;
    m.s = string->unit.data();
    m.e = m.s + string->unit.size();
    if (groups.find('Z') != std::string::npos) {
        /* CPython's LocaleTime.timezone: utc, gmt and tzname[0], then
           tzname[1] when there is daylight saving time */
        m.zones = {(new str("utc"))->unit, (new str("gmt"))->unit, tzname->__getfirst__()->lower()->unit};
        if (daylight)
            m.zones.push_back(tzname->__getsecond__()->lower()->unit);
        std::stable_sort(m.zones.begin(), m.zones.end(), [](const __GC_STR &a, const __GC_STR &b) { return a.size() > b.size(); });
    }

    const __ss_char *end = __ss_sp_match(m, 0, m.s);
    if (!end)
        throw new ValueError(__add_strs(4, new str("time data "), repr(string), new str(" does not match format "), repr(format)));
    if (end != m.e)
        throw new ValueError(__add_strs(2, new str("unconverted data remains: "), new str(__GC_STR(end, m.e))));

    int iso_year = -1, year = -1, month = 1, day = 1;
    int hour = 0, minute = 0, second = 0, fraction = 0;
    int tz = -1, gmtoff = 0, gmtoff_fraction = 0;
    bool has_gmtoff = false;
    int iso_week = -1, week_of_year = -1, weekday = -1, julian = -1;
    bool week_starts_mon = false;
    str *zone = NULL;

    int century = -1, ampm = -1;
    for (const __ss_sp_found &f : m.found) {
        if (f.group == 'C')
            century = f.val;
        else if (f.group == 'p')
            ampm = f.val;
    }

    for (const __ss_sp_found &f : m.found) {
        switch (f.group) {
            case 'y':
                year = f.val;
                if (century != -1)
                    year += century * 100;
                else
                    year += year <= 68 ? 2000 : 1900;
                break;
            case 'Y': year = f.val; break;
            case 'G': iso_year = f.val; break;
            case 'm': case 'b': case 'B': month = f.val; break;
            case 'd': day = f.val; break;
            case 'H': hour = f.val; break;
            case 'I':
                hour = f.val;
                if (ampm == 1) {
                    if (hour != 12)
                        hour += 12;
                } else if (hour == 12)
                    hour = 0;
                break;
            case 'M': minute = f.val; break;
            case 'S': second = f.val; break;
            case 'f': fraction = f.val; break;
            case 'a': case 'A': weekday = f.val; break;
            case 'w': weekday = f.val == 0 ? 6 : f.val - 1; break;
            case 'u': weekday = f.val - 1; break;
            case 'j': julian = f.val; break;
            case 'U': case 'W':
                week_of_year = f.val;
                week_starts_mon = f.group == 'W';
                break;
            case 'V': iso_week = f.val; break;
            case 'z': {
                std::string z;
                for (size_t k = 0; k < f.len; k++) {
                    __ss_char c = m.s[f.pos + k];
                    int dg = __ss_sp_digit(c);
                    z += dg >= 0 ? (char)('0' + dg) : (char)c;
                }
                has_gmtoff = true;
                if (z == "Z") {
                    gmtoff = 0;
                    break;
                }
                if (z[3] == ':') {
                    z.erase(3, 1);
                    if (z.size() > 5) {
                        if (z[5] != ':')
                            throw new ValueError(__add_strs(2, new str("Inconsistent use of : in "), new str(__GC_STR(m.s + f.pos, f.len))));
                        z.erase(5, 1);
                    }
                }
                if (z.size() > 5 && z[5] == ':') /* int(':3') in CPython */
                    throw new ValueError(__add_strs(3, new str("invalid literal for int() with base 10: '"), new str(z.substr(5, 2).c_str()), new str("'")));
                int secs = z.size() > 5 ? atoi(z.substr(5, 2).c_str()) : 0;
                gmtoff = atoi(z.substr(1, 2).c_str()) * 3600 + atoi(z.substr(3, 2).c_str()) * 60 + secs;
                if (z.size() > 8) {
                    std::string rem = z.substr(8);
                    rem.append(6 - rem.size(), '0');
                    gmtoff_fraction = atoi(rem.c_str());
                }
                if (z[0] == '-') {
                    gmtoff = -gmtoff;
                    gmtoff_fraction = -gmtoff_fraction;
                }
                break;
            }
            case 'Z': {
                zone = new str(__GC_STR(m.s + f.pos, f.len));
                __GC_STR found = zone->lower()->unit;
                bool utc = found == (new str("utc"))->unit || found == (new str("gmt"))->unit;
                int value = -1;
                if (utc || found == tzname->__getfirst__()->lower()->unit)
                    value = 0;
                else if (daylight && found == tzname->__getsecond__()->lower()->unit)
                    value = 1;
                /* too ambiguous when both names are the same */
                if (value != -1 && !(tzname->__getfirst__()->unit == tzname->__getsecond__()->unit && daylight && !utc))
                    tz = value;
                break;
            }
        }
    }

    /* the ISO week directives need each other and a weekday */
    if (iso_year != -1) {
        if (julian != -1)
            throw new ValueError(new str("Day of the year directive '%j' is not compatible with ISO year directive '%G'. Use '%Y' instead."));
        if (iso_week == -1 || weekday == -1)
            throw new ValueError(new str("ISO year directive '%G' must be used with the ISO week directive '%V' and a weekday directive ('%A', '%a', '%w', or '%u')."));
    } else if (iso_week != -1) {
        if (year == -1 || weekday == -1)
            throw new ValueError(new str("ISO week directive '%V' must be used with the ISO year directive '%G' and a weekday directive ('%A', '%a', '%w', or '%u')."));
        throw new ValueError(new str("ISO week directive '%V' is incompatible with the year directive '%Y'. Use the ISO year '%G' instead."));
    }

    bool leap_year_fix = false;
    if (year == -1) {
        if (month == 2 && day == 29) {
            year = 1904; /* the first leap year of the 20th century */
            leap_year_fix = true;
        } else
            year = 1900;
    }

    if (julian == -1 && weekday != -1) {
        if (week_of_year != -1) {
            /* the day of the year from %U or %W and the weekday */
            int first_weekday = (__ss_sp_ordinal(year, 1, 1) + 6) % 7;
            int dow = weekday;
            if (!week_starts_mon) {
                first_weekday = (first_weekday + 1) % 7;
                dow = (dow + 1) % 7;
            }
            if (week_of_year == 0)
                julian = 1 + dow - first_weekday;
            else
                julian = 1 + (7 - first_weekday) % 7 + 7 * (week_of_year - 1) + dow;
        } else if (iso_year != -1 && iso_week != -1)
            __ss_sp_from_isocalendar(iso_year, iso_week, weekday + 1, year, month, day);
        if (julian != -1 && julian <= 0) {
            year--;
            julian += 365 + __ss_isleap(year);
        }
    }

    if (julian == -1)
        julian = __ss_sp_ordinal(year, month, day) - __ss_sp_ordinal(year, 1, 1) + 1;
    else
        __ss_sp_from_ordinal(julian - 1 + __ss_sp_ordinal(year, 1, 1), year, month, day);
    if (weekday == -1)
        weekday = (__ss_sp_ordinal(year, month, day) + 6) % 7;

    if (leap_year_fix) /* no year was given, but february 29th was */
        year = 1900;

    res.year = year;
    res.month = month;
    res.day = day;
    res.hour = hour;
    res.minute = minute;
    res.second = second;
    res.weekday = weekday;
    res.julian = julian;
    res.isdst = tz;
    res.microsecond = fraction;
    res.has_gmtoff = has_gmtoff;
    res.gmtoff = gmtoff;
    res.gmtoff_fraction = gmtoff_fraction;
    res.zone = zone;
}

struct_time *strptime(str *string, str *format) {
    __ss_strptime_result r;
    __ss_strptime(string, format, r);
    struct_time *st = new struct_time(new tuple2<__ss_int, __ss_int>(9,
        (__ss_int)r.year, (__ss_int)r.month, (__ss_int)r.day,
        (__ss_int)r.hour, (__ss_int)r.minute, (__ss_int)r.second,
        (__ss_int)r.weekday, (__ss_int)r.julian, (__ss_int)r.isdst));
    if (r.has_gmtoff)
        st->tm_gmtoff = r.gmtoff;
    st->tm_zone = r.zone;
    return st;
}

void __init_clock_ids() {
    /* -1 means "not available on this platform"; passing it to
       clock_gettime/clock_getres raises OSError. */
    __ss_CLOCK_REALTIME = -1;
    __ss_CLOCK_MONOTONIC = -1;
    __ss_CLOCK_MONOTONIC_RAW = -1;
    __ss_CLOCK_PROCESS_CPUTIME_ID = -1;
    __ss_CLOCK_THREAD_CPUTIME_ID = -1;
    __ss_CLOCK_BOOTTIME = -1;
    __ss_CLOCK_TAI = -1;
    __ss_CLOCK_UPTIME_RAW = -1;
#ifdef WIN32
    /* synthetic ids, dispatched by __ss_win_clock_ns/clock_getres */
    __ss_CLOCK_REALTIME = 0;
    __ss_CLOCK_MONOTONIC = 1;
    __ss_CLOCK_PROCESS_CPUTIME_ID = 2;
    __ss_CLOCK_THREAD_CPUTIME_ID = 3;
#else
#ifdef CLOCK_REALTIME
    __ss_CLOCK_REALTIME = CLOCK_REALTIME;
#endif
#ifdef CLOCK_MONOTONIC
    __ss_CLOCK_MONOTONIC = CLOCK_MONOTONIC;
#endif
#ifdef CLOCK_MONOTONIC_RAW
    __ss_CLOCK_MONOTONIC_RAW = CLOCK_MONOTONIC_RAW;
#endif
#ifdef CLOCK_PROCESS_CPUTIME_ID
    __ss_CLOCK_PROCESS_CPUTIME_ID = CLOCK_PROCESS_CPUTIME_ID;
#endif
#ifdef CLOCK_THREAD_CPUTIME_ID
    __ss_CLOCK_THREAD_CPUTIME_ID = CLOCK_THREAD_CPUTIME_ID;
#endif
#ifdef CLOCK_BOOTTIME
    __ss_CLOCK_BOOTTIME = CLOCK_BOOTTIME;
#endif
#ifdef CLOCK_TAI
    __ss_CLOCK_TAI = CLOCK_TAI;
#endif
#ifdef CLOCK_UPTIME_RAW
    __ss_CLOCK_UPTIME_RAW = CLOCK_UPTIME_RAW;
#endif
#endif
}

void __init() {
    start = std::clock();
    __init_clock_ids();
    cl_clock_info = new class_("SimpleNamespace");
    const_1 = new str("time.struct_time(tm_year=%d, tm_mon=%d, tm_mday=%d, tm_hour=%d, tm_min=%d, tm_sec=%d, tm_wday=%d, tm_yday=%d, tm_isdst=%d)");
#ifdef WIN32
    /* as CPython: the CRT globals */
    _tzset();
    long tz = 0;
    _get_timezone(&tz);
    timezone = (__ss_int)tz;
    tzname = new tuple2<str *, str *>(2, new str(_tzname[0]), new str(_tzname[1]));
    daylight = _daylight;
    altzone = timezone - 3600;
#else
    /* as CPython (glibc, and where tm_gmtoff exists): the utc offsets of
       january and july of this year, which also handles half-hour zones,
       DST in effect at startup and the southern hemisphere */
    tzset();
    const time_t YEAR = (365 * 24 + 6) * 3600;
    time_t t = (::time(NULL) / YEAR) * YEAR;
    struct tm tm_;
    ::localtime_r(&t, &tm_);
    __ss_int janzone = -(__ss_int)tm_.tm_gmtoff;
    t += YEAR / 2;
    ::localtime_r(&t, &tm_);
    __ss_int julyzone = -(__ss_int)tm_.tm_gmtoff;
    if (janzone < julyzone) { /* DST is reversed in the southern hemisphere */
        timezone = julyzone;
        altzone = janzone;
    } else {
        timezone = janzone;
        altzone = julyzone;
    }
    daylight = janzone != julyzone;
    tzname = new tuple2<str *, str *>(2, new str(::tzname[0]), new str(::tzname[1]));
#endif
}


} // module namespace
