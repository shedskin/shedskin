#ifndef TIME_HPP
#define TIME_HPP

#include "builtin.hpp"
#include <ctime>
#include <sys/time.h>

#ifdef WIN32
#include <sys/timeb.h>
#endif

using namespace __shedskin__;
namespace __time__ {

#ifdef WIN32
struct  __ss_timezone {
    int     tz_minuteswest;
    int     tz_dsttime;
};

int gettimeofday (struct timeval *tv, struct __ss_timezone *tz);
#endif

extern int timezone;
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
    int tm_sec;
    int tm_hour;
    int tm_mday;
    int tm_isdst;
    int tm_year;
    int tm_mon;
    int tm_yday;
    int tm_wday;
    int tm_min;

    struct_time() {
        __class__ = cl_struct_time;
    }
    int __getitem__(int n);
    struct_time(tuple2<int, int> *_tuple);
    str *__repr__();
};


double mktime(struct_time *tuple);
double mktime(tuple2<int, int> *tuple);

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
str *strftime(str *format, tuple2<int, int> *tuple);

struct_time *strptime(str *string, str *format);
#ifdef WIN32
char *strptime(const char *, const char *, struct tm *);
#endif

void __init();

} // module namespace
#endif
