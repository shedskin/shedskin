#include "datetime.hpp"
#include "time.hpp"
#include "string.hpp"
#include <iostream>

namespace __datetime__ {

str *date_format,*hour_format1,*hour_format2,*ctime_format;
str *one_day_string,*minus_one_day_string,*multiple_days_string,*point_string,*space_string,*none_string,*empty_string,*z_string,*Z_string;

__ss_int MINYEAR, MAXYEAR;

list<str *> *DayNames, *MonthNames;

class_ *cl_date, *cl_tzinfo, *cl_timedelta, *cl_time, *cl_datetime;

void __init() {
	cl_date = new class_("date", 34, 34);				//is this right?
	cl_tzinfo = new class_("tzinfo", 35, 35);
	cl_datetime = new class_("datetime", 36, 36);
	cl_time = new class_("time", 37, 37);
	cl_timedelta = new class_("timedelta", 38, 38);
	
    date_format = new str("%04d-%02d-%02d");
    hour_format1 = new str("%d:%02d:%02d");
    hour_format2 = new str("%02d:%02d:%02d");
    ctime_format = new str("%s %s %2d %02d:%02d:%02d %04d");
	
	one_day_string = new str("1 day, %d:%02d:%02d");
	minus_one_day_string = new str("-1 day, %d:%02d:%02d");
	multiple_days_string = new str("%d days, %d:%02d:%02d");
	point_string = new str("%s.%06d");
	space_string = new str(" ");
	none_string = new str("None");
	empty_string = new str("");
	z_string = new str("%z");
	Z_string = new str("%Z");

    MINYEAR = 1;
    MAXYEAR = 9999;

    DayNames = __string__::split(new str("Mon Tue Wed Thu Fri Sat Sun"));
    MonthNames = __string__::split(new str("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec"));
}

/* helper functions */

static __ss_int divmod(__ss_int x, __ss_int y, __ss_int *r);
static __ss_int is_leap(__ss_int year);
static __ss_int days_in_month(__ss_int year, __ss_int month);
static __ss_int days_before_month(__ss_int year, __ss_int month);
static __ss_int days_before_year(__ss_int year);
static void ord_to_ymd(__ss_int ordinal, __ss_int *year, __ss_int *month, __ss_int *day);
static __ss_int ymd_to_ord(__ss_int year, __ss_int month, __ss_int day);
static __ss_int iso_week1_monday(__ss_int year);

//class date
date::date(__ss_int year, __ss_int month, __ss_int day){
    __class__=cl_date;

    if(year<MINYEAR || year>MAXYEAR)    throw new ValueError(new str("year is out of range"));
    if(month<=0 || month>12)            throw new ValueError(new str("month must be in 1..12"));
    if(day<=0 || day>days_in_month(year,month)) throw new ValueError(new str("day is out of range for month"));

    this->year=year;
    this->month=month;
    this->day=day;
}

date *date::today() {
	//today's date using localtime
    time_t rawtime;
    struct tm * t;
    std::time( &rawtime );
    t = localtime( &rawtime );
    return new date(t->tm_year+1900,t->tm_mon+1,t->tm_mday);
}

date* date::fromtimestamp(__ss_int timestamp) {
	//date from timestamp using localtime
	struct tm *tm;
	time_t t = (time_t)timestamp;
	tm = localtime(&t);
	if (tm)
		return new date(tm->tm_year + 1900,
						tm->tm_mon + 1,
						tm->tm_mday);
	else
		throw new ValueError(new str("timestamp out of range for platform localtime() function"));
}

date* date::fromordinal(__ss_int o) {
	//OverflowError is raised if date2.year  would be smaller than MINYEAR or larger than MAXYEAR.
	 if(o<1)		//1 = date.min.toordinal()
		throw new OverflowError(new str("ordinal must be >= 1"));
	if(o>3652059)	//3652059 = date.max.toordinal()
		throw new OverflowError(new str("year is out of range"));
	
    date *r = new date(1,1,1);
    ord_to_ymd(o,&(r->year),&(r->month),&(r->day));
    return r;
}

date *date::__add__(timedelta *other) {
    return fromordinal(toordinal()+(other->days));
}

date *date::__sub__(timedelta *other) {
    return fromordinal(toordinal()-(other->days));
}

timedelta *date::__sub__(date *other) {
    return new timedelta(toordinal()-other->toordinal(), 0, 0, 0 ,0, 0, 0);
}

__ss_int date::__cmp__(date *other) {
	if(year==other->year && month==other->month && day==other->day)
		return 0;
    if (year*366+month*31+day > other->year*366+other->month*31+other->day)
        return 1;
    return -1;
}

__ss_bool date::__eq__(date *other) { return __mbool(__cmp__(other) == 0); }
__ss_bool date::__ne__(date *other) { return __mbool(__cmp__(other) != 0); }
__ss_bool date::__gt__(date *other) { return __mbool(__cmp__(other) == 1); }
__ss_bool date::__lt__(date *other) { return __mbool(__cmp__(other) == -1); }
__ss_bool date::__ge__(date *other) { return __mbool(__cmp__(other) != -1); }
__ss_bool date::__le__(date *other) { return __mbool(__cmp__(other) != 1); }

date *date::replace(__ss_int year, __ss_int month, __ss_int day) {
    date* t = new date(this);
    if(year!=0) {
        if(year<MINYEAR || year>MAXYEAR)    throw new ValueError(new str("year is out of range"));
        t->year=year;}
    if(month!=0) {
        if(month<=0 || month>12)            throw new ValueError(new str("month must be in 1..12"));
        t->month=month;}
    if(day!=0) {
        if(day<=0 || day>days_in_month(t->year,t->month)) throw new ValueError(new str("day is out of range for month"));
        t->day=day;}
    return t;
}

__time__::struct_time *date::timetuple() {
    return new __time__::struct_time(new tuple2<__ss_int, __ss_int>(9,
        (__ss_int)year, (__ss_int)month, (__ss_int)day,
        (__ss_int)0, (__ss_int)0, (__ss_int)0,
        (__ss_int)(weekday()),
        (__ss_int)(days_before_month(year,month)+day),
        (__ss_int)(-1)));
}

__ss_int date::toordinal() {
    return ymd_to_ord(year,month,day);
}

__ss_int date::weekday() {
    return (ymd_to_ord(year, month, day) + 6) % 7;
}

__ss_int date::isoweekday() {
    return (ymd_to_ord(year, month, day) + 6) % 7+1;
}

tuple2<__ss_int, __ss_int> *date::isocalendar() {
//modified from cpython
    __ss_int  week1_monday = iso_week1_monday(year);
    __ss_int  today        = ymd_to_ord(year, month, day);
    __ss_int  tmpyear      = year;
    __ss_int  tmpweek;
    __ss_int  tmpday;

    tmpweek = divmod(today - week1_monday, 7, &tmpday);
    if (tmpweek < 0) {
        --tmpyear;
        week1_monday = iso_week1_monday(tmpyear);
        tmpweek = divmod(today - week1_monday, 7, &tmpday);
    }
    else if (tmpweek >= 52 && today >= iso_week1_monday(tmpyear + 1)) {
        ++tmpyear;
        tmpweek = 0;
    }
    return new tuple2<__ss_int, __ss_int>(3, (__ss_int)tmpyear, (__ss_int)(tmpweek+1), (__ss_int)(tmpday+1));
}

str *date::isoformat() {
    return __str__();
}

str *date::__str__() {
    return __modct(date_format, 3, ___box(this->year), ___box(this->month), ___box(this->day));
}

str *date::ctime() {
    __ss_int wday = weekday();

    return __modct(ctime_format, 7, DayNames->__getitem__(wday), MonthNames->__getitem__(month-1),
                        ___box(day), ___box(0), ___box(0), ___box(0), ___box(year));
}

str *date::strftime(str *format) {
    return __time__::strftime(format,timetuple());
}


//class tzinfo
datetime *tzinfo::fromutc(datetime *dt) {
	if(dt->_tzinfo!=this)
		throw new ValueError(new str("fromutc: dt.tzinfo is not self"));
	timedelta *dtoff = utcoffset(dt);
	if(dtoff==NULL)
		throw new ValueError(new str("fromutc: non-None utcoffset() result required"));
	timedelta *dtdst = dst(dt);
	if(dtdst==NULL)
		throw new ValueError(new str("fromutc: non-None dst() result required"));
	timedelta *delta = dtoff->__sub__(dtdst);
	dt = dt->__add__(delta);
	dtdst = dst(dt);
	if(dtdst==NULL)
		throw new ValueError(new str("fromutc: non-None dst() result required"));
	dt = dt->__add__(dtdst);
	delete delta;
	delete dtoff;
	delete dtdst;
	return dt;
	/*    dtdst = dt.dst()
          # raise ValueError if dtoff is None or dtdst is None
          delta = dtoff - dtdst  # this is self's standard offset
          if delta:
              dt += delta   # convert to standard local time
              dtdst = dt.dst()
              # raise ValueError if dtdst is None
          if dtdst:
              return dt + dtdst
          else:
              return dt*/
}

str *tzinfo::minutes_to_str(datetime *dt) {
/*	timedelta *offset;
	str *f;
	offset = utcoffset(dt);
	if(offset==NULL)
		return new str("");
	if(offset->days<0) {
		offset = offset->__neg__();
		f = new str("-%02d:%02d");
	}
	else
		f = new str("+%02d:%02d");
	return __mod(f,offset->seconds/3600,(offset->seconds/60)%60);*/
	timedelta *offset;
	str f;
	offset = utcoffset(dt);
	if(offset==NULL)
		return empty_string;
	if(offset->days<0) {
		offset = offset->__neg__();
		f = str("-%02d:%02d");
	}
	else
		f = str("+%02d:%02d");
	return __modct(&f,2,___box(offset->seconds/3600),___box((offset->seconds/60)%60));
}


//class datetime
datetime::datetime(__ss_int year, __ss_int month, __ss_int day, __ss_int hour, __ss_int minute, __ss_int second, __ss_int microsecond, tzinfo *tzinfo) : date(year,month,day) {
    __class__=cl_datetime;

    if(hour>=24 || hour<0) throw new ValueError(new str("hour must be in 0..23"));
    if(minute>=60 || minute<0) throw new ValueError(new str("minute must be in 0..59"));
    if(second>=60 || second<0) throw new ValueError(new str("second must be in 0..59"));
    if(microsecond>=1000000 || microsecond<0) throw new ValueError(new str("microsecond must be in 0..999999"));

    this->hour = hour;
    this->minute = minute;
    this->second = second;
    this->microsecond = microsecond;
    this->_tzinfo = tzinfo;
}

datetime *datetime::today() {
    time_t rawtime;
    struct tm * t;
    std::time( &rawtime );
    t = localtime( &rawtime );

    struct timeval tv;
#ifdef WIN32
    __time__::gettimeofday(&tv, NULL);
#else
    gettimeofday(&tv, NULL);
#endif

    return new datetime(t->tm_year+1900,t->tm_mon+1,t->tm_mday,t->tm_hour,t->tm_min,t->tm_sec,tv.tv_usec);
}

datetime *datetime::now(tzinfo *tzinfo) {
    if(!tzinfo)
        return today();

    datetime *r = utcnow();
    r->_tzinfo = tzinfo;
	if(r->_tzinfo)
		try {
			return r->__add__(r->_tzinfo->utcoffset(r));
		} catch (Exception *e) {return r;}
	else
		return r;
}

datetime *datetime::utcnow() {
    time_t rawtime;
    struct tm * t;
    std::time( &rawtime );
    t = gmtime( &rawtime );

    struct timeval tv;
#ifdef WIN32
    __time__::gettimeofday(&tv, NULL);
#else
    gettimeofday(&tv, NULL);
#endif

    return new datetime(t->tm_year+1900,t->tm_mon+1,t->tm_mday,t->tm_hour,t->tm_min,t->tm_sec,tv.tv_usec);
}

datetime *datetime::from_timestamp(double timestamp, tzinfo *tzinfo, bool timefn) {
	//modified from cpython
	time_t timet;
	double fraction;
	__ss_int us;

	timet = (time_t)timestamp;
	fraction = timestamp - (double)timet;
	if (fraction * 1e6 >= 0.0)
		us = (__ss_int)floor(fraction * 1e6 + 0.5);
	else
		us = (__ss_int)ceil(fraction * 1e6 - 0.5);

	if (us < 0) {
		/* Truncation towards zero is not what we wanted
		   for negative numbers (Python's mod semantics) */
		timet -= 1;
		us += 1000000;
	}
	/* If timestamp is less than one microsecond smaller than a
	 * full second, round up. Otherwise, ValueErrors are raised
	 * for some floats. */
	if (us == 1000000) {
		timet += 1;
		us = 0;
	}
	
	struct tm *tm;

	if(timefn)
		tm = gmtime(&timet);
	else
		tm = localtime(&timet);

	if (tm) {
		/* The platform localtime/gmtime may insert leap seconds,
		 * indicated by tm->tm_sec > 59.  We don't care about them,
		 * except to the extent that passing them on to the datetime
		 * constructor would raise ValueError for a reason that
		 * made no sense to the user.
		 */
		if (tm->tm_sec > 59)
			tm->tm_sec = 59;
		return new datetime(tm->tm_year + 1900,
					       tm->tm_mon + 1,
					       tm->tm_mday,
					       tm->tm_hour,
					       tm->tm_min,
					       tm->tm_sec,
					       us,
					       tzinfo);
	}
	else
		throw new ValueError(new str("timestamp out of range for platform localtime()/gmtime() function"));
	return (datetime *)NULL;
}

datetime *datetime::utcfromtimestamp(double timestamp) {
	return from_timestamp(timestamp,NULL,true);	//true=gmtime
}

datetime *datetime::fromtimestamp(double timestamp, tzinfo *tzinfo) {
	datetime *tmp = from_timestamp(timestamp, tzinfo, (bool)tzinfo);
				// tzinfo == Py_None ? localtime : gmtime,
	if(tzinfo!=NULL)
		return tzinfo->fromutc(tmp);
	else
		return tmp;
}

datetime *datetime::fromordinal(__ss_int o) {
	if(o<1)		//1 = date.min.toordinal()
		throw new OverflowError(new str("ordinal must be >= 1"));
	if(o>3652059)	//3652059 = date.max.toordinal()
		throw new OverflowError(new str("year is out of range"));

    datetime *r = new datetime(1,1,1);
    ord_to_ymd(o,&(r->year),&(r->month),&(r->day));
    return r;
}

datetime *datetime::combine(date *d, time *t) {
    return new datetime(d->year,d->month,d->day,t->hour,t->minute,t->second,t->microsecond,t->_tzinfo);
}

datetime *datetime::strptime(str *date_string, str *format) {
	time_t rawtime;
	struct tm t = {0, 0, 0, 1, 0, 0, 0, 1, -1};
#ifdef WIN32
    char *e = __time__::strptime(date_string->unit.c_str(), format->unit.c_str(), &t);
#else
    char *e = ::strptime(date_string->unit.c_str(), format->unit.c_str(), &t);
#endif
    if(!e)
        throw new ValueError(new str("time data did not match format:  data="+date_string->unit+" fmt="+format->unit));
 	if((*e)!='\0')
        throw new ValueError((new str("ValueError: unconverted data remains: "))->__add__(new str(e)));
	return new datetime(t.tm_year + 1900,
        t.tm_mon + 1,
        t.tm_mday,
        t.tm_hour,
        t.tm_min,
        t.tm_sec);
}

datetime *datetime::__add__(timedelta *other) {
    __ss_int usec = this->microsecond + other->microseconds;
    __ss_int sec = this->second + other->seconds;
    datetime *r = datetime::fromordinal(this->toordinal()+other->days +
                                        (((usec/1000000 + sec)/60 +
                                        this->minute)/60 + this->hour)/24);
    r->microsecond = usec%1000000;
    r->second = (sec + usec/1000000)%(60);
    r->minute = (this->minute + (sec + usec/1000000)/60)%60;
    r->hour = (this->hour + (this->minute + (sec + usec/1000000)/60)/60)%24;
	r->_tzinfo = _tzinfo;
    return r;
}

datetime *datetime::__sub__(timedelta *other) {
    __ss_int usec = this->microsecond - other->microseconds;
    __ss_int sec = this->second - other->seconds;
	__ss_int days = this->toordinal()-other->days +
                                        (((usec/1000000 + sec)/60 +
                                        this->minute)/60 + this->hour)/24;
    datetime *r = datetime::fromordinal(days);
    r->microsecond = usec%1000000;
    r->second = (sec + usec/1000000)%(60);
    r->minute = (this->minute + (sec + usec/1000000)/60)%60;
    r->hour = (this->hour + (this->minute + (sec + usec/1000000)/60)/60)%24;
	r->_tzinfo = _tzinfo;
	
	//make positive
	if(r->microsecond<0) {
		r->second--;
		r->microsecond+=1000000;
	}
	if(r->second<0) {
		r->minute--;
		r->second+=60;
	}
	if(r->minute<0) {
		r->hour--;
		r->minute+=60;
	}
	if(r->hour<0) {
		r->hour+=24;
		date *tmp = date::fromordinal(days-1);
		r->year=tmp->year;
		r->month=tmp->month;
		r->day=tmp->day;
		delete tmp;
	}
    return r;
}

timedelta *datetime::__sub__(datetime *other) {
	timedelta *td = new timedelta(this->toordinal()-other->toordinal(),this->second-other->second,this->microsecond-other->microsecond,0,this->minute-other->minute,this->hour-other->hour);
	if(_tzinfo==NULL && other->_tzinfo==NULL)
		return td;
	if(_tzinfo!=NULL && other->_tzinfo!=NULL) {
		timedelta *offset1 = _tzinfo->utcoffset(this);
		timedelta *offset2 = other->_tzinfo->utcoffset(other);
		if(offset1!=NULL && offset2!=NULL) {
			timedelta *tmp = td->__sub__(offset1);
			delete td;
			delete offset1;
			td = tmp->__add__(offset2);
			delete tmp;
			delete offset2;
			return td;
		}
		if(offset1==NULL && offset2==NULL) {
			return td;
		}
	}
	throw new TypeError(new str("can't subtract offset-naive and offset-aware datetimes"));
}

void datetime_compare_check(datetime *&f, datetime *&s) {
	if((f->_tzinfo && !s->_tzinfo) || (s->_tzinfo && !f->_tzinfo))
		throw new TypeError(new str("can't compare offset-naive and offset-aware datetimes"));
	if(f->_tzinfo) {
		f = f->__sub__(f->_tzinfo->utcoffset(f));
		s = s->__sub__(s->_tzinfo->utcoffset(s));
	}
}

__ss_int datetime::__cmp__(datetime *other) {
    datetime *f = this;
	datetime_compare_check(f, other);

	if(f->year==other->year && f->month==other->month && f->day==other->day && f->hour==other->hour && f->minute==other->minute && f->second==other->second && f->microsecond==other->microsecond)
		return 0;
	if(f->year*366+f->month*31+f->day > other->year*366+other->month*31+other->day)
		return 1;
	if(f->year*366+f->month*31+f->day == other->year*366+other->month*31+other->day && (f->hour*3600+f->minute*60+f->second)*1000000+f->microsecond > (other->hour*3600+other->minute*60+other->second)*1000000+other->microsecond)
		return 1;
    return -1;
}

__ss_bool datetime::__eq__(datetime *other) { return __mbool(__cmp__(other) == 0); }
__ss_bool datetime::__ne__(datetime *other) { return __mbool(__cmp__(other) != 0); }
__ss_bool datetime::__gt__(datetime *other) { return __mbool(__cmp__(other) == 1); }
__ss_bool datetime::__lt__(datetime *other) { return __mbool(__cmp__(other) == -1); }
__ss_bool datetime::__ge__(datetime *other) { return __mbool(__cmp__(other) != -1); }
__ss_bool datetime::__le__(datetime *other) { return __mbool(__cmp__(other) != 1); }

date *datetime::_date() {
	return new date(year,month,day);
}

time *datetime::_time() {
	return new time(hour,minute,second,microsecond);
}

time *datetime::timetz() {
	return new time(hour,minute,second,microsecond,_tzinfo);
}

datetime *datetime::replace(__ss_int __args, __ss_int year, __ss_int month, __ss_int day, __ss_int hour, __ss_int minute, __ss_int second, __ss_int microsecond, tzinfo *tzinfo) {
    datetime *t = new datetime(this);

   if((__args & 1)==1) {
        if(year<MINYEAR || year>MAXYEAR)    throw new ValueError(new str("year is out of range"));
        t->year=year;}
    if((__args & 2)==2) {
        if(month<=0 || month>12)            throw new ValueError(new str("month must be in 1..12"));
        t->month=month;}
    if((__args & 4)==4) {
        if(day<=0 || day>days_in_month(t->year,t->month)) throw new ValueError(new str("day is out of range for month"));
        t->day=day;}
    if((__args & 8)==8) {
        if(hour<0 || hour>=24)              throw new ValueError(new str("hour must be in 0..23"));
        t->hour=hour;}
    if((__args & 16)==16) {
        if(minute<0 || minute>=60)          throw new ValueError(new str("minute must be in 0..59"));
        t->minute=minute;}
    if((__args & 32)==32) {
        if(second<0 || second>=60)          throw new ValueError(new str("second must be in 0..59"));
        t->second=second;}
    if((__args & 64)==64) {
        if(microsecond<0 || microsecond>=1000000)      throw new ValueError(new str("microsecond must be in 0..999999"));
        t->microsecond=microsecond;}
    if((__args & 128)==128)
        t->_tzinfo = tzinfo;
    return t;
}


datetime *datetime::astimezone(tzinfo *tzinfo) {
	if(this->_tzinfo == NULL)
		throw new ValueError(new str("astimezone() cannot be applied to a naive datetime"));
	if(this->_tzinfo == tzinfo)
		return this;
	datetime *utc = this->__sub__(this->utcoffset())->replace(128,-1,-1,-1,-1,-1,-1,-1,tzinfo);
	datetime *r = tzinfo->fromutc(utc);
	delete utc;
	return r;
/*def astimezone(self, tz):
      if self.tzinfo is tz:
          return self
      # Convert self to UTC, and attach the new time zone object.
      utc = (self - self.utcoffset()).replace(tzinfo=tz)
      # Convert from UTC to tz's local time.
      return tz.fromutc(utc)
*/
}


timedelta *datetime::utcoffset() {
    if(_tzinfo==NULL)
        return (timedelta *)NULL;
    else
		return _tzinfo->utcoffset(this);
}

timedelta *datetime::dst() {
    if(_tzinfo==NULL)
        return (timedelta *)NULL;
    else
		return _tzinfo->dst(this);
}

str *datetime::tzname() {
    if(_tzinfo==NULL)
        return none_string;
    else
		return _tzinfo->tzname(this);
}


__time__::struct_time *datetime::timetuple() {
    char dst=-1;
    if(_tzinfo) {
		timedelta *tmp = _tzinfo->dst(this);
		if(tmp->days==0 && tmp->seconds==0 && tmp->microseconds==0)
			dst=0;
		else
			dst=1;
        delete tmp;
	}

    return new __time__::struct_time(new tuple2<__ss_int, __ss_int>(9,
        (__ss_int)year,
        (__ss_int)month,
        (__ss_int)day,
        (__ss_int)hour,
        (__ss_int)minute,
        (__ss_int)second,
        (__ss_int)(weekday()),
        (__ss_int)(days_before_month(year,month)+day),
        (__ss_int)dst));
}

__time__::struct_time *datetime::utctimetuple() {
	datetime *tmp = this;
	timedelta *offset;
	if(_tzinfo!=NULL && NULL!=(offset=_tzinfo->utcoffset(this))) {
		tmp = this->__sub__(offset);
		delete offset;
	}
    return new __time__::struct_time(new tuple2<__ss_int, __ss_int>(9,
        (__ss_int)(tmp->year),
        (__ss_int)(tmp->month),
        (__ss_int)(tmp->day),
        (__ss_int)(tmp->hour),
        (__ss_int)(tmp->minute),
        (__ss_int)(tmp->second),
        (__ss_int)(tmp->weekday()),
        (__ss_int)(days_before_month(tmp->year,tmp->month)+tmp->day),
        (__ss_int)0));
}

str *datetime::isoformat(str *sep) {
    if(sep->__len__()!=1) {
        throw new TypeError(new str("isoformat() argument 1 must be char, not str"));
    }
	str *r;
	r=__add_strs(3,date::__str__(),sep,__modct(hour_format2, 3, ___box(hour), ___box(minute), ___box(second)));
    if(microsecond!=0)
        r=__modct(new str("%s.%06d"),2, r, ___box(microsecond));
    if(this->_tzinfo!=NULL)
		return r->__add__(this->_tzinfo->minutes_to_str(this));
	return r;
}

str *datetime::__str__() {
    return isoformat(space_string);
}

str *datetime::ctime() {
    __ss_int wday = weekday();

    return __modct(ctime_format, 7, DayNames->__getitem__(wday), MonthNames->__getitem__(month-1),
                        ___box(day), ___box(hour), ___box(minute), ___box(second), ___box(year));
}

str *datetime::strftime(str *format) {
	str *tmp;
	if(_tzinfo) {
		tmp = format->replace(z_string,_tzinfo->minutes_to_str(this)->__str__());
		format = tmp->replace(Z_string,_tzinfo->tzname(this));
	}
	else {
		tmp = format->replace(z_string,empty_string);
		format = tmp->replace(Z_string,empty_string);
	}
	delete tmp;
    tmp = __time__::strftime(format,timetuple());
	delete format;
	return tmp;
}

//class time
time::time(__ss_int hour, __ss_int minute, __ss_int second, __ss_int microsecond, tzinfo *tzinfo) {
    __class__=cl_time;

    if(hour>=24 || hour<0) throw new ValueError(new str("hour must be in 0..23"));
    if(minute>=60 || minute<0) throw new ValueError(new str("minute must be in 0..59"));
    if(second>=60 || second<0) throw new ValueError(new str("second must be in 0..59"));
    if(microsecond>=1000000 || microsecond<0) throw new ValueError(new str("microsecond must be in 0..999999"));

    this->hour = hour;
    this->minute = minute;
    this->second = second;
    this->microsecond = microsecond;
    this->_tzinfo = tzinfo;
}

time *time::replace(__ss_int __args, __ss_int hour, __ss_int minute, __ss_int second, __ss_int microsecond, tzinfo *tzinfo) {
    time *t = new time(this);
    if((__args & 1)==1) {
        if(hour<0 || hour>=24)          throw new ValueError(new str("hour must be in 0..23"));
        t->hour=hour;}
    if((__args & 2)==2) {
        if(minute<0 || minute>=60)      throw new ValueError(new str("minute must be in 0..59"));
        t->minute=minute;}
    if((__args & 4)==4) {
        if(second<0 || second>=60)      throw new ValueError(new str("second must be in 0..59"));
        t->second=second;}
    if((__args & 8)==8) {
        if(microsecond<0 || microsecond>=1000000)      throw new ValueError(new str("microsecond must be in 0..999999"));
        t->microsecond=microsecond;}
    if((__args & 16)==16)
        t->_tzinfo = tzinfo;
    return t;
}

str *time::isoformat() {
    return __str__();
}

str *time::__str__() {
    str * s;
    if(microsecond==0)
        s = __modct(hour_format2, 3, ___box(hour), ___box(minute), ___box(second));
    else
        s = __modct(point_string,2,__modct(hour_format2, 3,___box(hour), ___box(minute), ___box(second)),___box(microsecond));
    if(_tzinfo!=NULL)
		return s->__add__(_tzinfo->minutes_to_str(NULL));
	return s;
}

str *time::strftime(str* format) {
	str *tmp;
	if(_tzinfo) {
		tmp = format->replace(z_string,_tzinfo->minutes_to_str(NULL)->__str__());
		format = tmp->replace(Z_string,_tzinfo->tzname(NULL));
	}
	else {
		tmp = format->replace(z_string,empty_string);
		format = tmp->replace(Z_string,empty_string);
	}
	delete tmp;
    tmp = __time__::strftime(format, new __time__::struct_time(
        new tuple2<__ss_int, __ss_int>(9,
            (__ss_int)1900,
            (__ss_int)1,
            (__ss_int)1,//according to cpython implementation, but 0,0, according to description I found on the internet
            (__ss_int)hour,
            (__ss_int)minute,
            (__ss_int)second,
            (__ss_int)0,
            (__ss_int)0,
            (__ss_int)(-1))));
	delete format;
	return tmp;
}

timedelta *time::utcoffset() {
    if(_tzinfo==NULL)
        return (timedelta *)NULL;
    else
		return _tzinfo->utcoffset(NULL);
}

timedelta *time::dst() {
    if(_tzinfo==NULL)
        return (timedelta *)NULL;
    else
		return _tzinfo->dst(NULL);
}

str *time::tzname() {
    if(_tzinfo==NULL)
        return none_string;
    else
		return _tzinfo->tzname(NULL);
}

void time_compare_check(time *&f, time *&s) {
	if((f->_tzinfo && !s->_tzinfo) || (s->_tzinfo && !f->_tzinfo))
		throw new TypeError(new str("can't compare offset-naive and offset-aware datetimes"));
	if(f->_tzinfo) {
		timedelta *fdelta = f->_tzinfo->utcoffset(NULL), *sdelta = s->_tzinfo->utcoffset(NULL);
		time *ft = new time(), *st = new time();
		ft->hour = f->hour-fdelta->days*24;
		ft->minute = f->minute;
		ft->second = f->second - fdelta->seconds;
		ft->microsecond = f->microsecond - fdelta->microseconds;
		st->hour = s->hour-sdelta->days*24;
		st->minute = s->minute;
		st->second = s->second - sdelta->seconds;
		st->microsecond = s->microsecond - sdelta->microseconds;
		f = ft;
		s = st;
	}
}

__ss_int time::__cmp__(time *other) {
    time *f = this;
	time_compare_check(f, other);

	if((f->hour*3600+f->minute*60+f->second)*1000000+f->microsecond == (other->hour*3600+other->minute*60+other->second)*1000000+other->microsecond)
        return 0;
	if((f->hour*3600+f->minute*60+f->second)*1000000+f->microsecond > (other->hour*3600+other->minute*60+other->second)*1000000+other->microsecond)
        return 1;
    return -1;
}

__ss_bool time::__eq__(time *other) { return __mbool(__cmp__(other) == 0); }
__ss_bool time::__ne__(time *other) { return __mbool(__cmp__(other) != 0); }
__ss_bool time::__gt__(time *other) { return __mbool(__cmp__(other) == 1); }
__ss_bool time::__lt__(time *other) { return __mbool(__cmp__(other) == -1); }
__ss_bool time::__ge__(time *other) { return __mbool(__cmp__(other) != -1); }
__ss_bool time::__le__(time *other) { return __mbool(__cmp__(other) != 1); }


//class timedelta
timedelta::timedelta(double days, double seconds, double microseconds, double milliseconds, double minutes, double hours, double weeks) {
    __class__=cl_timedelta;
//still some rounding errors
	//all little bits of hours and seconds added up
    double usec1 = milliseconds*1000 + microseconds +
                        (((weeks*7 + days)*24*3600 + hours*3600 + minutes*60 + seconds)
						-(__ss_int)(hours*3600 + minutes*60 + seconds + (weeks*7 + days)*24*3600))*1000000;
    this->days = (__ss_int)(weeks*7 + days);
	this->seconds = (__ss_int)(hours*3600 + minutes*60 + seconds + (weeks*7 + days - (__ss_int)(weeks*7 + days))*24*3600);
    //rounding to nearest microsec
	if(usec1>=0.0)
		this->microseconds = (__ss_int)(floor(usec1+0.5));
	else
		this->microseconds = (__ss_int)(ceil(usec1-0.5));

    //move 1000000us to 1s
    this->seconds += this->microseconds/1000000;
    this->microseconds %= 1000000;
    //move 24*3600s to 1 day
    this->days += this->seconds/(24*3600);
    this->seconds %= 24*3600;
    //make positive (% doesn't do that in C++)
    if(this->microseconds<0) {
        this->microseconds+=1000000;
        this->seconds--;
    }
    if(this->seconds<0) {
        this->seconds+=24*3600;
        this->days--;
    }
    if(this->days>999999999 || this->days<(-999999999)) {
        throw new OverflowError();
    }
}

str *timedelta::__str__() {
    str *s;
    if(days==0)
        s=__modct(hour_format1, 3, ___box(seconds/3600), ___box((seconds%3600)/60), ___box(seconds%60));
    else if(days==1)
        s=__modct(one_day_string,3,___box(seconds/3600), ___box((seconds%3600)/60), ___box(seconds%60));
    else if(days==-1)
        s=__modct(minus_one_day_string,3,___box(seconds/3600), ___box((seconds%3600)/60), ___box(seconds%60));
    else
        s=__modct(multiple_days_string,4,___box(days),___box(seconds/3600), ___box((seconds%3600)/60), ___box(seconds%60));
    if(microseconds==0)
        return s;
    else
        return __modct(point_string,2,s,___box(microseconds));
}

timedelta *timedelta::__add__(timedelta *other) {
    return new timedelta(days+other->days, seconds+other->seconds, microseconds+other->microseconds,0,0,0,0);
}

timedelta *timedelta::__sub__(timedelta *other) {
    return new timedelta(days-other->days, seconds-other->seconds, microseconds-other->microseconds,0,0,0,0);
}

timedelta *timedelta::__mul__(__ss_int n) {
    return new timedelta(days*n, seconds*n, microseconds*n,0,0,0,0);
}

timedelta *timedelta::__div__(__ss_int n) {
    if(n==0) {
        throw new ZeroDivisionError(new str("integer division or modulo by zero"));
    }
	double d,s,us;
	d = double(days)/n;
	s = double(seconds)/n;
	std::cout<<(long)days*24*3600*1000000 + (long)seconds*1000000 + (long)microseconds<<std::endl;
	us = double(microseconds)/n+(((long double)(days)/n-double(days)/n)*24*3600+(long double)(seconds)/n-s)*1000000;
    return new timedelta(0,d*24*3600+s,us,0,0,0,0);
}

timedelta *timedelta::__neg__() {
    return new timedelta(-days, -seconds, -microseconds,0,0,0,0);
}

timedelta *timedelta::__floordiv__(__ss_int n) {
    if(n==0) {
       throw new ZeroDivisionError(new str("integer division or modulo by zero"));
    }
    return new timedelta(double(days)/n,double(seconds)/n,double(microseconds)/n,0,0,0,0);
}

timedelta *timedelta::__abs__() {
    if(days>=0)
        return new timedelta(this);
    else
        return __neg__();
}

__ss_int timedelta::__cmp__(timedelta *other) {
    if ((days == other->days) && (seconds == other->seconds) && (microseconds == other->microseconds))
        return 0;
    if (((days * 24 * 3600) + seconds) > ((other->days * 24 * 3600) + other->seconds))
        return 1;
    if ((((days * 24 * 3600) + seconds) == ((other->days * 24 * 3600) + other->seconds)) && (microseconds > other->microseconds))
        return 1;
    return -1;
}

__ss_bool timedelta::__eq__(timedelta *other) { return __mbool(__cmp__(other) == 0); }
__ss_bool timedelta::__ne__(timedelta *other) { return __mbool(__cmp__(other) != 0); }
__ss_bool timedelta::__gt__(timedelta *other) { return __mbool(__cmp__(other) == 1); }
__ss_bool timedelta::__lt__(timedelta *other) { return __mbool(__cmp__(other) == -1); }
__ss_bool timedelta::__ge__(timedelta *other) { return __mbool(__cmp__(other) != -1); }
__ss_bool timedelta::__le__(timedelta *other) { return __mbool(__cmp__(other) != 1); }


/*functions taken and modified from cpython, to be copied to datetime.cpp later*/

/* Compute Python divmod(x, y), returning the quotient and storing the
 * remainder into *r.  The quotient is the floor of x/y, and that's
 * the real point of this.  C will probably truncate instead (C99
 * requires truncation; C89 left it implementation-defined).
 * Simplification:  we *require* that y > 0 here.  That's appropriate
 * for all the uses made of it.  This simplifies the code and makes
 * the overflow case impossible (divmod(LONG_MIN, -1) is the only
 * overflow case).
 */
static __ss_int
divmod(__ss_int x, __ss_int y, __ss_int *r)
{
    __ss_int quo;

    assert(y > 0);
    quo = x / y;
    *r = x - quo * y;
    if (*r < 0) {
        --quo;
        *r += y;
    }
    assert(0 <= *r && *r < y);
    return quo;
}

/* ---------------------------------------------------------------------------
 * General calendrical helper functions
 */

/* For each month ordinal in 1..12, the number of days in that month,
 * and the number of days before that month in the same year.  These
 * are correct for non-leap years only.
 */
static __ss_int _days_in_month[] = {
    0, /* unused; this vector uses 1-based indexing */
    31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
};

static __ss_int _days_before_month[] = {
    0, /* unused; this vector uses 1-based indexing */
    0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334
};

/* year -> 1 if leap year, else 0. */
static __ss_int
is_leap(__ss_int year)
{
    /* Cast year to unsigned.  The result is the same either way, but
     * C can generate faster code for unsigned mod than for signed
     * mod (especially for % 4 -- a good compiler should just grab
     * the last 2 bits when the LHS is unsigned).
     */
    const unsigned int ayear = (unsigned int)year;
    return ayear % 4 == 0 && (ayear % 100 != 0 || ayear % 400 == 0);
}

/* year, month -> number of days in that month in that year */
static __ss_int
days_in_month(__ss_int year, __ss_int month)
{
    assert(month >= 1);
    assert(month <= 12);
    if (month == 2 && is_leap(year))
        return 29;
    else
        return _days_in_month[month];
}

/* year, month -> number of days in year preceeding first day of month */
static __ss_int
days_before_month(__ss_int year, __ss_int month)
{
    __ss_int days;

    assert(month >= 1);
    assert(month <= 12);
    days = _days_before_month[month];
    if (month > 2 && is_leap(year))
        ++days;
    return days;
}

/* year -> number of days before January 1st of year.  Remember that we
 * start with year 1, so days_before_year(1) == 0.
 */
static __ss_int
days_before_year(__ss_int year)
{
    __ss_int y = year - 1;
    /* This is incorrect if year <= 0; we really want the floor
     * here.  But so long as MINYEAR is 1, the smallest year this
     * can see is 0 (this can happen in some normalization endcases),
     * so we'll just special-case that.
     */
    assert (year >= 0);
    if (y >= 0)
        return y*365 + y/4 - y/100 + y/400;
    else {
        assert(y == -1);
        return -366;
    }
}

/* Number of days in 4, 100, and 400 year cycles.  That these have
 * the correct values is asserted in the module init function.
 */
#define DI4Y    1461    /* days_before_year(5); days in 4 years */
#define DI100Y    36524    /* days_before_year(101); days in 100 years */
#define DI400Y    146097    /* days_before_year(401); days in 400 years  */

/* ordinal -> year, month, day, considering 01-Jan-0001 as day 1. */
static void
ord_to_ymd(__ss_int ordinal, __ss_int *year, __ss_int *month, __ss_int *day)
{
    __ss_int n, n1, n4, n100, n400, leapyear, preceding;

    /* ordinal is a 1-based index, starting at 1-Jan-1.  The pattern of
     * leap years repeats exactly every 400 years.  The basic strategy is
     * to find the closest 400-year boundary at or before ordinal, then
     * work with the offset from that boundary to ordinal.  Life is much
     * clearer if we subtract 1 from ordinal first -- then the values
     * of ordinal at 400-year boundaries are exactly those divisible
     * by DI400Y:
     *
     *    D  M   Y            n              n-1
     *    -- --- ----        ----------     ----------------
     *    31 Dec -400        -DI400Y       -DI400Y -1
     *     1 Jan -399         -DI400Y +1   -DI400Y      400-year boundary
     *    ...
     *    30 Dec  000        -1             -2
     *    31 Dec  000         0             -1
     *     1 Jan  001         1              0          400-year boundary
     *     2 Jan  001         2              1
     *     3 Jan  001         3              2
     *    ...
     *    31 Dec  400         DI400Y        DI400Y -1
     *     1 Jan  401         DI400Y +1     DI400Y      400-year boundary
     */
    assert(ordinal >= 1);
    --ordinal;
    n400 = ordinal / DI400Y;
    n = ordinal % DI400Y;
    *year = n400 * 400 + 1;

    /* Now n is the (non-negative) offset, in days, from January 1 of
     * year, to the desired date.  Now compute how many 100-year cycles
     * precede n.
     * Note that it's possible for n100 to equal 4!  In that case 4 full
     * 100-year cycles precede the desired day, which implies the
     * desired day is December 31 at the end of a 400-year cycle.
     */
    n100 = n / DI100Y;
    n = n % DI100Y;

    /* Now compute how many 4-year cycles precede it. */
    n4 = n / DI4Y;
    n = n % DI4Y;

    /* And now how many single years.  Again n1 can be 4, and again
     * meaning that the desired day is December 31 at the end of the
     * 4-year cycle.
     */
    n1 = n / 365;
    n = n % 365;

    *year += n100 * 100 + n4 * 4 + n1;
    if (n1 == 4 || n100 == 4) {
        assert(n == 0);
        *year -= 1;
        *month = 12;
        *day = 31;
        return;
    }

    /* Now the year is correct, and n is the offset from January 1.  We
     * find the month via an estimate that's either exact or one too
     * large.
     */
    leapyear = n1 == 3 && (n4 != 24 || n100 == 3);
    assert(leapyear == is_leap(*year));
    *month = (n + 50) >> 5;
    preceding = (_days_before_month[*month] + (*month > 2 && leapyear));
    if (preceding > n) {
        /* estimate is too large */
        *month -= 1;
        preceding -= days_in_month(*year, *month);
    }
    n -= preceding;
    assert(0 <= n);
    assert(n < days_in_month(*year, *month));

    *day = n + 1;
}

/* year, month, day -> ordinal, considering 01-Jan-0001 as day 1. */
static __ss_int
ymd_to_ord(__ss_int year, __ss_int month, __ss_int day)
{
    return days_before_year(year) + days_before_month(year, month) + day;
}


static __ss_int
iso_week1_monday(__ss_int year)
{
    __ss_int first_day = ymd_to_ord(year, 1, 1);    /* ord of 1/1 */
    /* 0 if 1/1 is a Monday, 1 if a Tue, etc. */
    __ss_int first_weekday = (first_day + 6) % 7;
    /* ordinal of closest Monday at or before 1/1 */
    __ss_int week1_monday  = first_day - first_weekday;

    if (first_weekday > 3)    /* if 1/1 was Fri, Sat, Sun */
        week1_monday += 7;
    return week1_monday;
}

}
