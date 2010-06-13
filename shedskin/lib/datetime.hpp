#ifndef DATETIME_HPP
#define DATETIME_HPP

#include "builtin.hpp"
#include "time.hpp"
#include <ctime>
#if defined( _MSC_VER )
    #include <time.h>
#else
    #include <sys/time.h>
#endif
#ifdef WIN32
    #include <sys/timeb.h>
#endif
#include <assert.h>

using namespace __shedskin__;
namespace __datetime__ {

extern __ss_int MINYEAR, MAXYEAR;


void __init();

class date;
class tzinfo;
class datetime;
class timedelta;
class time;
class ZeroDivisionError : public Exception { public: ZeroDivisionError(str *msg=0) : Exception(msg) {} };
class OverflowError : public Exception { public: OverflowError(str *msg=0) : Exception(msg) {} };
class NotImplementedError : public Exception { public: NotImplementedError(str *msg=0) : Exception(msg) {} };

//todo:
//timedelta::timedelta() rounding problems
//check (unsigned) integer/long ranges (arguments as well)

//class date
extern class_ *cl_date;
class date : public pyobj {
public:
    __ss_int year;
    __ss_int month;
    __ss_int day;

    date(__ss_int year, __ss_int month, __ss_int day);
    date(date* d):year(d->year),month(d->month),day(d->day){__class__=cl_date;};
    static date *today();
    static date *fromtimestamp(__ss_int timestamp);
    static date *fromordinal(__ss_int o);                    //copied from cpython
    date *__add__(timedelta *other);
    date *__sub__(timedelta *other);
    timedelta *__sub__(date *other);

    date *replace(__ss_int year=0, __ss_int month=0, __ss_int day=0);  //ok (how to handle keyword variables?)
    __time__::struct_time *timetuple();                 //ok (depends on function from cpython)
    __ss_int toordinal();                                    //copied from cpython
    __ss_int weekday();                                      //copied from cpython
    __ss_int isoweekday();                                   //copied from cpython
    tuple2<__ss_int, __ss_int> *isocalendar();
    str *isoformat();
    str *__str__();
    str *ctime();
    str *strftime(str *format);

    __ss_int __cmp__(date *other);
    __ss_bool __eq__(date *other);
    __ss_bool __ne__(date *other);
    __ss_bool __gt__(date *other);
    __ss_bool __lt__(date *other);
    __ss_bool __ge__(date *other);
    __ss_bool __le__(date *other);
};


//class tzinfo
extern class_ *cl_tzinfo;
class tzinfo : public pyobj {
public:
    tzinfo(){__class__=cl_tzinfo;};
    virtual timedelta *utcoffset(datetime *dt) {throw new NotImplementedError(new str("a tzinfo subclass must implement utcoffset()"));};
    virtual timedelta *dst(datetime *dt) {throw new NotImplementedError(new str("a tzinfo subclass must implement dst()"));};
    virtual str *tzname(datetime *dt) {throw new NotImplementedError(new str("a tzinfo subclass must implement tzname()"));};
    virtual datetime *fromutc(datetime *dt);
	str *minutes_to_str(datetime *dt);
    __ss_int __init__() {};
};


//class datetime
extern class_ *cl_datetime;
class datetime : public date {
public:
    __ss_int hour, minute, second, microsecond;
    tzinfo *_tzinfo;

    datetime(datetime *d) : date(d),hour(d->hour),minute(d->minute),second(d->second),microsecond(d->microsecond),_tzinfo(d->_tzinfo)
                {__class__=cl_datetime;};
    datetime(__ss_int year, __ss_int month, __ss_int day, __ss_int hour=0, __ss_int minute=0, __ss_int second=0, __ss_int microsecond=0, tzinfo *tzinfo=NULL);

    static datetime *today();
    static datetime *now(tzinfo *tzinfo=NULL);
    static datetime *utcnow();

	static datetime *from_timestamp(double timestamp, tzinfo *tzinfo, bool timefn);
    static datetime *fromtimestamp(double timestamp, tzinfo *tzinfo=NULL);
    static datetime *utcfromtimestamp(double timestamp);
    static datetime *fromordinal(__ss_int o);
    static datetime *combine(date *d, time *t);
    static datetime *strptime(str *date_string, str *format);

    datetime *__add__(timedelta *other);
    datetime *__sub__(timedelta *other);
    timedelta *__sub__(datetime *other);

    date *_date();									//why is it exactly these two have a _?
    time *_time();
    time *timetz();
	
    datetime *replace(__ss_int __args, __ss_int year=-1, __ss_int month=-1, __ss_int day=-1, __ss_int hour=-1, __ss_int minute=-1, __ss_int second=-1, __ss_int microsecond=-1,tzinfo *tzinfo=NULL);
    datetime *astimezone(tzinfo *tzinfo);
    timedelta *utcoffset();
    timedelta *dst();
    str *tzname();

    __time__::struct_time *timetuple();
    __time__::struct_time *utctimetuple();

    str *isoformat(str *sep = new str("T"));
    str *__str__();
    str *ctime();
    str *strftime(str *format);

    __ss_int __cmp__(datetime *other);
    __ss_bool __eq__(datetime *other);
    __ss_bool __ne__(datetime *other);
    __ss_bool __gt__(datetime *other);
    __ss_bool __lt__(datetime *other);
    __ss_bool __ge__(datetime *other);
    __ss_bool __le__(datetime *other);
};


//class time
extern class_ *cl_time;
class time : public pyobj {
public:
    __ss_int hour, minute, second, microsecond;
    tzinfo *_tzinfo;

    time(time *t):hour(t->hour), minute(t->minute), second(t->second), microsecond(t->microsecond), _tzinfo(t->_tzinfo)
                {__class__=cl_time;};                                                       //copyconstructor
    time(__ss_int hour=0, __ss_int minute=0, __ss_int second=0, __ss_int microsecond=0, tzinfo *tzinfo=NULL);

    time *replace(__ss_int __args, __ss_int hour=-1, __ss_int minute=-1, __ss_int second=-1, __ss_int microsecond=-1, tzinfo *tzinfo=NULL);

    str *isoformat();
    str *__str__();
    str *strftime(str* format);
    timedelta *utcoffset();
    timedelta *dst();
    str *tzname();

    __ss_int __cmp__(time *other);
    __ss_bool __eq__(time *other);
    __ss_bool __ne__(time *other);
    __ss_bool __gt__(time *other);
    __ss_bool __lt__(time *other);
    __ss_bool __ge__(time *other);
    __ss_bool __le__(time *other);
};

//class timedelta
extern class_ *cl_timedelta;
class timedelta : public pyobj {
public:
    __ss_int days;
    __ss_int seconds;
    __ss_int microseconds;

    timedelta(double days=0., double seconds=0., double microseconds=0., double milliseconds=0., double minutes=0., double hours=0., double weeks=0.);
    timedelta(timedelta *c):days(c->days),seconds(c->seconds),microseconds(c->microseconds){__class__=cl_timedelta;}
    str *__str__();
    timedelta *__add__(timedelta *other);
    timedelta *__sub__(timedelta *other);
    timedelta *__mul__(__ss_int n);
    timedelta *__div__(__ss_int n);
    timedelta *__neg__();
    timedelta *__floordiv__(__ss_int n);                     //what's the difference between this and __div__?
    timedelta *__abs__();

    __ss_int __cmp__(timedelta *other);
    __ss_bool __eq__(timedelta *other);
    __ss_bool __ne__(timedelta *other);
    __ss_bool __gt__(timedelta *other);
    __ss_bool __lt__(timedelta *other);
    __ss_bool __ge__(timedelta *other);
    __ss_bool __le__(timedelta *other);
};


} // module namespace

#endif
