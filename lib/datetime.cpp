#include "datetime.hpp"
#include "time.hpp"
#include "string.hpp"
#include <iostream>

namespace __datetime__ {

str *date_format,*hour_format1,*hour_format2,*ctime_format;
str *one_day_string,*minus_one_day_string,*multiple_days_string,*point_string,*space_string,*none_string,*empty_string,*z_string,*Z_string;

int MINYEAR, MAXYEAR;

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


//class date        
date::date(int year, int month, int day){
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

date* date::fromtimestamp(int timestamp) {
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

date* date::fromordinal(int o) {
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

int date::__cmp__(date *other) {
	if(year==other->year && month==other->month && day==other->day)
		return 0;
    if (year*366+month*31+day > other->year*366+other->month*31+other->day)
        return 1;
    return -1;
}

int date::__eq__(date *other) { return __cmp__(other) == 0; }
int date::__ne__(date *other) { return __cmp__(other) != 0; }
int date::__gt__(date *other) { return __cmp__(other) == 1; }
int date::__lt__(date *other) { return __cmp__(other) == -1; }
int date::__ge__(date *other) { return __cmp__(other) != -1; }
int date::__le__(date *other) { return __cmp__(other) != 1; }

date *date::replace(int year, int month, int day) {
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
    return new __time__::struct_time(new tuple2<int, int>(9, 
    year,
    month,
    day,
    0,0,0,
    weekday(),
    days_before_month(year,month)+day,
    -1));
}

int date::toordinal() {
    return ymd_to_ord(year,month,day);
}

int date::weekday() {
    return (ymd_to_ord(year, month, day) + 6) % 7;
}

int date::isoweekday() {
    return (ymd_to_ord(year, month, day) + 6) % 7+1;
}

tuple2<int, int> *date::isocalendar() {
//modified from cpython
    int  week1_monday = iso_week1_monday(year);
    int  today        = ymd_to_ord(year, month, day);
    int  tmpyear      = year;
    int  tmpweek;
    int  tmpday;
    
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
    return new tuple2<int, int>(3, tmpyear, tmpweek+1, tmpday+1);
}

str *date::isoformat() {
    return __str__();
}

str *date::__str__() {
    return __mod(date_format, this->year, this->month, this->day);
}

str *date::ctime() {
    int wday = weekday();

    return __mod(ctime_format, DayNames->__getitem__(wday), MonthNames->__getitem__(month-1),
                        day, 0, 0, 0, year);
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
	return __mod(&f,offset->seconds/3600,(offset->seconds/60)%60);
}


//class datetime
datetime::datetime(int year, int month, int day, int hour, int minute, int second, int microsecond, tzinfo *tzinfo):date::date(year,month,day) {
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
	int us;

	timet = (time_t)timestamp;
	fraction = timestamp - (double)timet;
	if (fraction * 1e6 >= 0.0)
		us = (int)floor(fraction * 1e6 + 0.5);
	else
		us = (int)ceil(fraction * 1e6 - 0.5);

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
	return NULL;
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

datetime *datetime::fromordinal(int o) {
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
    int usec = this->microsecond + other->microseconds;
    int sec = this->second + other->seconds;
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
    int usec = this->microsecond - other->microseconds;
    int sec = this->second - other->seconds;
	int days = this->toordinal()-other->days +
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

int datetime::__cmp__(datetime *other) {
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

int datetime::__eq__(datetime *other) { return __cmp__(other) == 0; }
int datetime::__ne__(datetime *other) { return __cmp__(other) != 0; }
int datetime::__gt__(datetime *other) { return __cmp__(other) == 1; }
int datetime::__lt__(datetime *other) { return __cmp__(other) == -1; }
int datetime::__ge__(datetime *other) { return __cmp__(other) != -1; }
int datetime::__le__(datetime *other) { return __cmp__(other) != 1; }

date *datetime::_date() {
	return new date(year,month,day);
}

time *datetime::_time() {
	return new time(hour,minute,second,microsecond);
}

time *datetime::timetz() {
	return new time(hour,minute,second,microsecond,_tzinfo);
}

datetime *datetime::replace(int __args, int year,int month,int day,int hour,int minute,int second,int microsecond,tzinfo *tzinfo) {
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
        return NULL;
    else
		return _tzinfo->utcoffset(this);
}

timedelta *datetime::dst() {
    if(_tzinfo==NULL)
        return NULL;
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

    return new __time__::struct_time(new tuple2<int, int>(9, 
                                                        year,month,day,
                                                        hour,minute,second,
                                                        weekday(),
                                                        days_before_month(year,month)+day,
                                                        dst));
}

__time__::struct_time *datetime::utctimetuple() {
	datetime *tmp = this;
	timedelta *offset;
	if(_tzinfo!=NULL && NULL!=(offset=_tzinfo->utcoffset(this))) {
		tmp = this->__sub__(offset);
		delete offset;
	}
    return new __time__::struct_time(new tuple2<int, int>(9, 
                                                        tmp->year,tmp->month,tmp->day,
                                                        tmp->hour,tmp->minute,tmp->second,
                                                        tmp->weekday(),
                                                        days_before_month(tmp->year,tmp->month)+tmp->day,
                                                        0));
}



str *datetime::isoformat(str *sep) {
    if(sep->__len__()!=1) {
        throw new TypeError(new str("isoformat() argument 1 must be char, not str"));
    }
	str *r;
	r=__add_strs(3,date::__str__(),sep,__mod(hour_format2, hour, minute, second));
    if(microsecond!=0)
        r=__mod(new str("%s.%06d"),r, microsecond);
    if(this->_tzinfo!=NULL)
		return r->__add__(this->_tzinfo->minutes_to_str(this));
	return r;
}

str *datetime::__str__() {
    return isoformat(space_string);
}

str *datetime::ctime() {
    int wday = weekday();

    return __mod(ctime_format, DayNames->__getitem__(wday), MonthNames->__getitem__(month-1),
                        day, hour, minute, second, year);
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
time::time(int hour, int minute, int second, int microsecond, tzinfo *tzinfo) {
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

time *time::replace(int __args, int hour, int minute, int second, int microsecond, tzinfo *tzinfo) {
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
        s = __mod(hour_format2,hour, minute, second);
    else
        s = __mod(point_string,__mod(hour_format2,hour, minute, second),microsecond);
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
                                            new tuple2<int, int>(9,1900,1,1,//according to cpython implementation, but 0,0, according to description I found on the internet
                                                                 hour,minute,second,
                                                                 0,0,-1)));
	delete format;
	return tmp;
}

timedelta *time::utcoffset() {
    if(_tzinfo==NULL)
        return NULL;
    else
		return _tzinfo->utcoffset(NULL);
}

timedelta *time::dst() {
    if(_tzinfo==NULL)
        return NULL;
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

int time::__cmp__(time *other) {
    time *f = this;
	time_compare_check(f, other);

	if((f->hour*3600+f->minute*60+f->second)*1000000+f->microsecond == (other->hour*3600+other->minute*60+other->second)*1000000+other->microsecond)
        return 0;
	if((f->hour*3600+f->minute*60+f->second)*1000000+f->microsecond > (other->hour*3600+other->minute*60+other->second)*1000000+other->microsecond)
        return 1;
    return -1;
}

int time::__eq__(time *other) { return __cmp__(other) == 0; }
int time::__ne__(time *other) { return __cmp__(other) != 0; }
int time::__gt__(time *other) { return __cmp__(other) == 1; }
int time::__lt__(time *other) { return __cmp__(other) == -1; }
int time::__ge__(time *other) { return __cmp__(other) != -1; }
int time::__le__(time *other) { return __cmp__(other) != 1; }


//class timedelta
timedelta::timedelta(double days, double seconds, double microseconds, double milliseconds, double minutes, double hours, double weeks) {
    __class__=cl_timedelta;
//still some rounding errors
	//all little bits of hours and seconds added up
    double usec1 = milliseconds*1000 + microseconds + 
                        (((weeks*7 + days)*24*3600 + hours*3600 + minutes*60 + seconds)
						-(int)(hours*3600 + minutes*60 + seconds + (weeks*7 + days)*24*3600))*1000000;
    this->days = int(weeks*7 + days);
	this->seconds = (int)(hours*3600 + minutes*60 + seconds + (weeks*7 + days - int(weeks*7 + days))*24*3600);
    //rounding to nearest microsec
	if(usec1>=0.0)
		this->microseconds = (int)(floor(usec1+0.5));
	else
		this->microseconds = (int)(ceil(usec1-0.5));
    
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
        s=__mod(hour_format1,seconds/3600, (seconds%3600)/60, seconds%60);
    else if(days==1)
        s=__mod(one_day_string,seconds/3600, (seconds%3600)/60, seconds%60);
    else if(days==-1)
        s=__mod(minus_one_day_string,seconds/3600, (seconds%3600)/60, seconds%60);
    else
        s=__mod(multiple_days_string,days,seconds/3600, (seconds%3600)/60, seconds%60);
    if(microseconds==0)
        return s;
    else
        return __mod(point_string,s,microseconds);
}

timedelta *timedelta::__add__(timedelta *other) {
    return new timedelta(days+other->days, seconds+other->seconds, microseconds+other->microseconds,0,0,0,0);
}

timedelta *timedelta::__sub__(timedelta *other) {
    return new timedelta(days-other->days, seconds-other->seconds, microseconds-other->microseconds,0,0,0,0);
}

timedelta *timedelta::__mul__(int n) {
    return new timedelta(days*n, seconds*n, microseconds*n,0,0,0,0);
}

timedelta *timedelta::__div__(int n) {
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

timedelta *timedelta::__floordiv__(int n) {
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

int timedelta::__cmp__(timedelta *other) {
    if ((days == other->days) && (seconds == other->seconds) && (microseconds == other->microseconds)) 
        return 0;
    if (((days * 24 * 3600) + seconds) > ((other->days * 24 * 3600) + other->seconds)) 
        return 1;
    if ((((days * 24 * 3600) + seconds) == ((other->days * 24 * 3600) + other->seconds)) && (microseconds > other->microseconds)) 
        return 1;
    return -1;
}

int timedelta::__eq__(timedelta *other) { return __cmp__(other) == 0; }
int timedelta::__ne__(timedelta *other) { return __cmp__(other) != 0; }
int timedelta::__gt__(timedelta *other) { return __cmp__(other) == 1; }
int timedelta::__lt__(timedelta *other) { return __cmp__(other) == -1; }
int timedelta::__ge__(timedelta *other) { return __cmp__(other) != -1; }
int timedelta::__le__(timedelta *other) { return __cmp__(other) != 1; }


}
