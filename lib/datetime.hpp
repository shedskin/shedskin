#ifndef DATETIME_HPP
#define DATETIME_HPP

#include "builtin.hpp"
#include "time.hpp"
#include <ctime>
#include <sys/time.h>
#include <assert.h>

#ifdef WIN32
#include <sys/timeb.h>
#endif

#include "datetime_cpython.hpp"

using namespace __shedskin__;
namespace __datetime__ {

extern int MINYEAR, MAXYEAR;


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
//check (unsinged) int/long ranges (arguments as well)

//class date
extern class_ *cl_date;
class date : public pyobj {
public:
    int year;
    int month;
    int day;

    date(int year, int month, int day);
    date(date* d):year(d->year),month(d->month),day(d->day){__class__=cl_date;};
    static date *today();
    static date *fromtimestamp(int timestamp);
    static date *fromordinal(int o);                    //copied from cpython
    date *__add__(timedelta *other);
    date *__sub__(timedelta *other);
    timedelta *__sub__(date *other);

    date *replace(int year=0, int month=0, int day=0);  //ok (how to handle keyword variables?)
    __time__::struct_time *timetuple();                 //ok (depends on function from cpython)
    int toordinal();                                    //copied from cpython
    int weekday();                                      //copied from cpython
    int isoweekday();                                   //copied from cpython
    tuple2<int, int> *isocalendar();
    str *isoformat();
    str *__str__();
    str *ctime();
    str *strftime(str *format);
};

bool __lt(date *f, date *s);
bool __gt(date *f, date *s);
bool __le(date *f, date *s);
bool __ge(date *f, date *s);
bool __eq(date *f, date *s);
bool __ne(date *f, date *s);


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
};


//class datetime
extern class_ *cl_datetime;
class datetime : public date {
public:
    int hour, minute, second, microsecond;
    tzinfo *_tzinfo;
    
    datetime(datetime *d):date::date(d),hour(d->hour),minute(d->minute),second(d->second),microsecond(d->microsecond),_tzinfo(d->_tzinfo)
                {__class__=cl_datetime;};
    datetime(int year, int month, int day, int hour=0, int minute=0, int second=0, int microsecond=0, tzinfo *tzinfo=NULL);
    
    static datetime *today();
    static datetime *now();
    static datetime *now(tzinfo *tzinfo);
    static datetime *utcnow();
    
	static datetime *from_timestamp(double timestamp, tzinfo *tzinfo, bool timefn);
    static datetime *fromtimestamp(double timestamp, tzinfo *tzinfo=NULL);
    static datetime *utcfromtimestamp(double timestamp);
    static datetime *fromordinal(int o);
    static datetime *combine(date *d, time *t);
    static datetime *strptime(str *date_string, str *format);
    
    datetime *__add__(timedelta *other);
    datetime *__sub__(timedelta *other);
    timedelta *__sub__(datetime *other);
    
    date *_date();									//why is it exactly these two have a _?
    time *_time();
    time *timetz();
	
    datetime *replace(int __args, int year=-1,int month=-1,int day=-1,int hour=-1,int minute=-1,int second=-1,int microsecond=-1,tzinfo *tzinfo=NULL);
    datetime *astimezone(tzinfo *tzinfo);
    timedelta *utcoffset();
    timedelta *dst();
    str *tzname();
    
    __time__::struct_time *timetuple();
    __time__::struct_time *utctimetuple();
    
    /*	//inherited from date
	int toordinal();
    int weekday();
    int isoweekday();
    tuple2<int, int> *isocalendar();*/
    
    str *isoformat(str *sep = new str("T"));
    str *__str__();
    str *ctime();
    str *strftime(str *format);
};

bool __lt(datetime *f, datetime *s);
bool __gt(datetime *f, datetime *s);
bool __le(datetime *f, datetime *s);
bool __ge(datetime *f, datetime *s);
bool __eq(datetime *f, datetime *s);
bool __ne(datetime *f, datetime *s);


//class time
extern class_ *cl_time;
class time : public pyobj {
public:
    int hour,minute,second,microsecond;
    tzinfo *_tzinfo;

    time(time *t):hour(t->hour), minute(t->minute), second(t->second), microsecond(t->microsecond), _tzinfo(t->_tzinfo)
                {__class__=cl_time;};                                                       //copyconstructor
    time(int hour=0, int minute=0, int second=0, int microsecond=0, tzinfo *tzinfo=NULL);

    time *replace(int __args, int hour=-1, int minute=-1, int second=-1, int microsecond=-1, tzinfo *tzinfo=NULL);

    str *isoformat();
    str *__str__();
    str *strftime(str* format);
    timedelta *utcoffset();
    timedelta *dst();
    str *tzname();
};

bool __lt(time *f, time *s);
bool __gt(time *f, time *s);
bool __le(time *f, time *s);
bool __ge(time *f, time *s);
bool __eq(time *f, time *s);
bool __ne(time *f, time *s);



//class timedelta
extern class_ *cl_timedelta;
class timedelta : public pyobj {
public:
    int days;
    int seconds;
    int microseconds;

    timedelta(double days=0., double seconds=0., double microseconds=0., double milliseconds=0., double minutes=0., double hours=0., double weeks=0.);
    timedelta(timedelta *c):days(c->days),seconds(c->seconds),microseconds(c->microseconds){__class__=cl_timedelta;}
    str *__str__();
    timedelta *__add__(timedelta *other);
    timedelta *__sub__(timedelta *other);
    timedelta *__mul__(int n);
    timedelta *__div__(int n);
    timedelta *__neg__();
    timedelta *__floordiv__(int n);                     //what's the difference between this and __div__?
    timedelta *__abs__();
};

} // module namespace

#endif
