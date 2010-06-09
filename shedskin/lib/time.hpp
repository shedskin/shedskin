#ifndef TIME_HPP
#define TIME_HPP

#include "builtin.hpp"
#include <ctime>
#if defined( _MSC_VER )
   #include <windows.h>
   #include <time.h>
   #include <sys/timeb.h>
#else
   #include <sys/time.h>
#endif

using namespace __shedskin__;
namespace __time__ {
#if defined( _MSC_VER )
   struct  __ss_timezone {
       int     tz_minuteswest;
       int     tz_dsttime;
   };
   __ss_int gettimeofday (struct timeval *tv, struct __ss_timezone *tz);
#endif

extern __ss_int timezone;
extern tuple2<str *, str *> *tzname;

double clock();
double time();
void *sleep(double s);

extern str *const_0, *const_1;

class struct_time;

extern str *__name__;

extern class_ *cl_struct_time;
class struct_time : public pyobj {
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
};


double mktime(struct_time *tuple);
double mktime(tuple2<__ss_int, __ss_int> *tuple);

struct_time *localtime();
struct_time *localtime(const double timep);

struct_time *gmtime();
struct_time *gmtime(const double seconds);

str *asctime();
str *asctime(struct_time *tuple);

str *ctime();
str *ctime(const double seconds);

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
