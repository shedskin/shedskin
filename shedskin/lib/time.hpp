/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef TIME_HPP
#define TIME_HPP

#include "builtin.hpp"
#include <ctime>
#ifdef WIN32
   #ifdef _MSC_VER
      #ifndef NOMINMAX
         #define NOMINMAX
      #endif
   #endif
   #include <windows.h>
   #include <time.h>
   #include <sys/timeb.h>
#else
   #include <sys/time.h>
#endif

using namespace __shedskin__;
namespace __time__ {
#ifdef WIN32
   struct  __ss_timezone {
       int     tz_minuteswest;
       int     tz_dsttime;
   };
   __ss_int gettimeofday (struct timeval *tv, struct __ss_timezone *tz);
#endif

extern __ss_int timezone;
extern __ss_int altzone;
extern __ss_int daylight;
extern tuple2<str *, str *> *tzname;

/* Clock identifiers for clock_gettime/clock_gettime_ns/clock_getres. These
   are filled in by __init() from the corresponding platform macros; a clock
   the platform does not provide is set to -1, so that passing it raises
   OSError (EINVAL) rather than silently selecting some other clock. */
extern __ss_int __ss_CLOCK_REALTIME;
extern __ss_int __ss_CLOCK_MONOTONIC;
extern __ss_int __ss_CLOCK_MONOTONIC_RAW;
extern __ss_int __ss_CLOCK_PROCESS_CPUTIME_ID;
extern __ss_int __ss_CLOCK_THREAD_CPUTIME_ID;
extern __ss_int __ss_CLOCK_BOOTTIME;
extern __ss_int __ss_CLOCK_TAI;
extern __ss_int __ss_CLOCK_UPTIME_RAW;

__ss_float time();
__ss_float perf_counter();
__ss_float monotonic();
__ss_float process_time();
__ss_float thread_time();
__ss_int time_ns();
__ss_int perf_counter_ns();
__ss_int monotonic_ns();
__ss_int process_time_ns();
__ss_int thread_time_ns();
__ss_float clock_gettime(__ss_int clk_id);
__ss_int clock_gettime_ns(__ss_int clk_id);
__ss_float clock_getres(__ss_int clk_id);
void *sleep(__ss_float s);

extern str *const_0, *const_1;

class struct_time;

extern str *__name__;

extern class_ *cl_struct_time;
class struct_time : public pyseq<__ss_int> {
public:
    __ss_int tm_sec;
    __ss_int tm_hour;
    __ss_int tm_mday;
    __ss_int tm_isdst;
    __ss_int tm_year;
    __ss_int tm_mon;
    __ss_int tm_yday;
    __ss_int tm_wday;
    __ss_int tm_min;

    struct_time() {
        __class__ = cl_struct_time;
    }
    __ss_int __getitem__(__ss_int n);
    struct_time(tuple2<__ss_int, __ss_int> *_tuple);
    str *__repr__();
    __ss_int __len__();
    __ss_bool __eq__(pyobj *p);
    __ss_int __cmp__(pyobj *p);
};


__ss_float mktime(struct_time *tuple);
__ss_float mktime(tuple2<__ss_int, __ss_int> *tuple);

struct_time *localtime();
struct_time *localtime(const __ss_float timep);

struct_time *gmtime();
struct_time *gmtime(const __ss_float seconds);

str *asctime();
str *asctime(struct_time *tuple);

str *ctime();
str *ctime(const __ss_float seconds);

str *strftime(str *format, struct_time* tuple);
str *strftime(str *format);
str *strftime(str *format, tuple2<__ss_int, __ss_int> *tuple);

struct_time *strptime(str *string, str *format);
#ifdef WIN32
char *strptime(const char *, const char *, struct tm *);
#endif

void __init();

} // module namespace
#endif
