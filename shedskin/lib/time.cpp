#include "time.hpp"
#include "time.h"

namespace __time__ {

clock_t start;
__ss_int timezone;
tuple2<str *, str *> *tzname;

#ifdef WIN32

//#include <windows.h>

double clock()
{
    return ((double) (std::clock()-start)) / CLOCKS_PER_SEC;

/*       static LARGE_INTEGER ctrStart;
       static double divisor = 0.0;
       LARGE_INTEGER now;
       double diff;

       if (divisor == 0.0) {
               LARGE_INTEGER freq;
               QueryPerformanceCounter(&ctrStart);
               if (!QueryPerformanceFrequency(&freq) || freq.QuadPart == 0) {
                       // Unlikely to happen - this works on all intel
                       //     machines at least!  Revert to clock()
                       return ((double) (std::clock()-start)) / CLOCKS_PER_SEC;
               }
               divisor = (double)freq.QuadPart;
       }
       QueryPerformanceCounter(&now);
       diff = (double)(now.QuadPart - ctrStart.QuadPart);
       return diff / divisor; */
}

__ss_int gettimeofday (struct timeval *tv, struct __ss_timezone *tz)
{
   struct _timeb tb;

   if (!tv)
      return -1;

  _ftime (&tb);
  tv->tv_sec  = tb.time;
  tv->tv_usec = tb.millitm * 1000 + 500;
  if (tz)
  {
    tz->tz_minuteswest = -60 * _timezone;
    tz->tz_dsttime = _daylight;
  }
  return 0;
}
#else

double clock() {
    return ((double) (std::clock()-start)) / CLOCKS_PER_SEC;
}

#endif

str *const_0, *const_1;

class_ *cl_struct_time;

__ss_int struct_time::__getitem__(__ss_int n) {

    return ((new tuple2<__ss_int, __ss_int>(9,
        this->tm_year, this->tm_mon,
        this->tm_mday, this->tm_hour, this->tm_min, this->tm_sec,
        this->tm_wday, this->tm_yday,
        this->tm_isdst)))->__getitem__(n);
}

struct_time::struct_time(tuple2<__ss_int, __ss_int> *_tuple) {
    this->__class__ = cl_struct_time;

    if ((len(_tuple)!=9)) {
        throw ((new TypeError(const_0)));
    }
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

    return __modct(const_1, 9, __box(this->tm_year), __box(this->tm_mon), __box(this->tm_mday), __box(this->tm_hour), __box(this->tm_min), __box(this->tm_sec), __box(this->tm_wday), __box(this->tm_yday), __box(this->tm_isdst));
}

tm* tuple2tm(struct_time* tuple) {
    tm *time_tuple = new tm;

    time_tuple->tm_sec = tuple->tm_sec;
    time_tuple->tm_min = tuple->tm_min;
    time_tuple->tm_hour = tuple->tm_hour;
    time_tuple->tm_mday = tuple->tm_mday;
    time_tuple->tm_mon = tuple->tm_mon - 1;
    time_tuple->tm_year = tuple->tm_year - 1900;
    time_tuple->tm_wday = tuple->tm_wday == 6 ? 0 : tuple->tm_wday + 1;
    time_tuple->tm_yday = tuple->tm_yday - 1 ;
    time_tuple->tm_isdst = tuple->tm_isdst;

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

double time() {
    timeval tim;
    gettimeofday(&tim, 0);
    return tim.tv_sec+tim.tv_usec/1000000.0;
}

#ifndef WIN32
void *sleep(double s) {
    struct timespec time;
    time_t seconds = (int) s;
    long nanosecs = (double)(s - seconds)*1000000000;
    time.tv_sec = seconds;
    time.tv_nsec = nanosecs;

    nanosleep(&time, NULL);

    return NULL;
}
#endif

double mktime(struct_time *tuple) {
    return ::mktime(tuple2tm(tuple));
}

double mktime(tuple2<__ss_int, __ss_int> *tuple) {
    struct_time *st;
    try {
        st = new struct_time(tuple);
    } catch(...) {
        throw;
    }
    return ::mktime(tuple2tm(st));
}

struct_time *localtime() {
    time_t time = ::time(NULL);
    return localtime(time);
}

struct_time *localtime(const double timep) {
    time_t timet = static_cast<time_t>(timep);
    tm *tm_time = ::localtime(&timet);
    return tm2tuple(tm_time);
}

struct_time *gmtime() {
    time_t time = ::time(NULL);
    return gmtime(time);
}

struct_time *gmtime(const double seconds) {
    time_t timet = static_cast<time_t>(seconds);
    tm *tm_time = ::gmtime(&timet);
    return tm2tuple(tm_time);
}

str *asctime() {
    struct_time *tuple = localtime();
    return asctime(tuple);
}

str *asctime(struct_time *tuple) {
    return (new str(::asctime(tuple2tm(tuple))))->__slice__(2, 0, -1, 0);
}

str *ctime() {
    return asctime(localtime());
}

str *ctime(const double seconds) {
    return asctime(localtime(seconds));
}

str *strftime(str *format, struct_time* tuple) {
    tm *time_tuple = tuple2tm(tuple);
    unsigned int size = format->__len__();
    unsigned int n;
    char *buf;
	if(size==0)
		return new str();
    do {
        size *= 2;
        buf = new char[size];
        n = ::strftime(buf, size, format->unit.c_str(), time_tuple);
    } while(n == 0);
    return new str(buf);
}

str *strftime(str *format) {
    return strftime(format, localtime());
}

str *strftime(str *format, tuple2<__ss_int, __ss_int> *tuple) {
    struct_time *st;
    try {
        st = new struct_time(tuple);
    } catch (...) {
        throw;
    }
    return strftime(format, st);
}

/******************************************************************************
 * STRPTIME FOR WINDOWS
 *****************************************************************************/
#ifdef WIN32

/*
removed because of licensing issues. we might want to use this instead:
http://cvsweb.netbsd.org/bsdweb.cgi/src/lib/libc/time/strptime.c?rev=HEAD
*/

#endif

/******************************************************************************
 * END OF STRPTIME FOR WINDOWS
 *****************************************************************************/

struct_time *strptime(str *string, str *format) {
    tm time_tuple = {0, 0, 0, 1, 0, 0, 0, 1, -1};
#ifndef WIN32
    if (!::strptime(string->unit.c_str(), format->unit.c_str(), &time_tuple)) {
        throw  new ValueError(new str("time data did not match format:  data="+string->unit+" fmt="+format->unit));
    }
#else
    if (!strptime(string->unit.c_str(), format->unit.c_str(), &time_tuple)) {
        throw  new ValueError(new str("time data did not match format:  data="+string->unit+" fmt="+format->unit));
    }
#endif
    return tm2tuple(&time_tuple);
}


void __init() {
    start = std::clock();
    const_0 = new str("time.struct_time() takes a 9-sequence");
    const_1 = new str("time.struct_time(tm_year=%d, tm_mon=%d, tm_mday=%d, tm_hour=%d, tm_min=%d, tm_sec=%d, tm_wday=%d, tm_yday=%d, tm_isdst=%d)");
    struct_time* gmt = gmtime();
    struct_time* localt = localtime();
    __ss_int gmt_hour = gmt->tm_hour;
    __ss_int localt_hour = localt->tm_hour;
    if (gmt->tm_mday > localt->tm_mday) {
        localt_hour -= 24;
    } else if (gmt->tm_mday < localt->tm_mday) {
        localt_hour += 24;
    }
    timezone = (gmt_hour - localt_hour) * 3600;
    tzname = new tuple2<str *, str *>(2, new str(::tzname[0]), new str(::tzname[1]));
}


} // module namespace
