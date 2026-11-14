/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "datetime.hpp"
#include "time.hpp"
#include <iostream>
#include <time.h>
#include <cstdio>
#include <cctype>
#include <cstring>
#include <cmath>
#include <limits>
#include <cerrno>

#ifdef _MSC_VER

#define DELTA_EPOCH_IN_100NS    INT64_C(116444736000000000)
#define POW10_7 10000000

int clock_gettime(int, struct timespec *tp)
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

namespace __datetime__ {

str *date_format,*hour_format1,*hour_format2,*ctime_format;
str *one_day_string,*minus_one_day_string,*multiple_days_string,*point_string,*space_string,*empty_string,*t_string,*auto_string;

__ss_int MINYEAR, MAXYEAR;

date *date::min, *date::max;
timedelta *date::resolution;
datetime *datetime::min, *datetime::max;
timedelta *datetime::resolution;
time *time::min, *time::max;
timedelta *time::resolution;
timedelta *timedelta::min, *timedelta::max, *timedelta::resolution;

str *date_repr_format, *time_repr_format, *datetime_repr_format;
str *repr_arg_format, *repr_tzinfo_format, *repr_days_format, *repr_seconds_format, *repr_microseconds_format;
str *comma_space_string, *zero_string, *close_paren_string, *repr_fold_string;

list<str *> *DayNames, *MonthNames;

class_ *cl_date, *cl_tzinfo, *cl_timedelta, *cl_time, *cl_datetime, *cl___IsoCalendarDate;

void __init() {
	cl_date = new class_("date");
	cl___IsoCalendarDate = new class_("IsoCalendarDate");
	cl_tzinfo = new class_("tzinfo");
	cl_datetime = new class_("datetime");
	cl_time = new class_("time");
	cl_timedelta = new class_("timedelta");
	
    date_format = new str("%04d-%02d-%02d");
    hour_format1 = new str("%d:%02d:%02d");
    hour_format2 = new str("%02d:%02d:%02d");
    ctime_format = new str("%s %s %2d %02d:%02d:%02d %04d");
	
	one_day_string = new str("1 day, %d:%02d:%02d");
	minus_one_day_string = new str("-1 day, %d:%02d:%02d");
	multiple_days_string = new str("%d days, %d:%02d:%02d");
	point_string = new str("%s.%06d");
	space_string = new str(" ");
	t_string = new str("T");
	auto_string = new str("auto");
	empty_string = new str("");

    MINYEAR = 1;
    MAXYEAR = 9999;

    date_repr_format = new str("datetime.date(%d, %d, %d)");
    time_repr_format = new str("datetime.time(%d, %d");
    datetime_repr_format = new str("datetime.datetime(%d, %d, %d, %d, %d");
    repr_arg_format = new str(", %d");
    repr_tzinfo_format = new str(", tzinfo=%s");
    repr_days_format = new str("days=%d");
    repr_seconds_format = new str("seconds=%d");
    repr_microseconds_format = new str("microseconds=%d");
    comma_space_string = new str(", ");
    zero_string = new str("0");
    close_paren_string = new str(")");
    repr_fold_string = new str(", fold=1");

    date::min = new date(MINYEAR, 1, 1);
    date::max = new date(MAXYEAR, 12, 31);
    date::resolution = new timedelta(1);

    datetime::min = new datetime(MINYEAR, 1, 1);
    datetime::max = new datetime(MAXYEAR, 12, 31, 23, 59, 59, 999999);
    datetime::resolution = new timedelta(0, 0, 1);

    time::min = new time(0, 0, 0, 0);
    time::max = new time(23, 59, 59, 999999);
    time::resolution = new timedelta(0, 0, 1);

    timedelta::min = new timedelta(-999999999);
    timedelta::max = new timedelta(999999999, 59, 999999, 0, 59, 23);
    timedelta::resolution = new timedelta(0, 0, 1);

    DayNames = (new str("Mon Tue Wed Thu Fri Sat Sun"))->split();
    MonthNames = (new str("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec"))->split();
}

/* helper functions */

static __ss_int is_leap(__ss_int year);
static __ss_int days_in_month(__ss_int year, __ss_int month);

/* range errors, as CPython 3.15 words them */
static ValueError *__dt_range_error(const char *name, __ss_int lo, __ss_int hi, __ss_int v) {
    return new ValueError(__add_strs(6, new str(name), new str(" must be in "), __str(lo), new str(".."), __str(hi), __add_strs(2, new str(", not "), __str(v))));
}
static ValueError *__dt_day_error(__ss_int day, __ss_int month, __ss_int year) {
    return new ValueError(__add_strs(8, new str("day "), __str(day), new str(" must be in range 1.."), __str(days_in_month(year, month)), new str(" for month "), __str(month), new str(" in year "), __str(year)));
}
static __ss_int days_before_month(__ss_int year, __ss_int month);
static __ss_int days_before_year(__ss_int year);
static void ord_to_ymd(__ss_int ordinal, __ss_int *year, __ss_int *month, __ss_int *day);
static __ss_int ymd_to_ord(__ss_int year, __ss_int month, __ss_int day);
static __ss_int iso_week1_monday(__ss_int year);
static int64_t floordivmod(int64_t a, int64_t b, int64_t *r);

/* inverse of isocalendar(): ordinal of ISO (year, week, day), copied from
 * cpython's _isoweek_to_gregorian / iso_week1_monday logic */
static __ss_int isoweek_to_ord(__ss_int year, __ss_int week, __ss_int day) {
    if(year<MINYEAR || year>MAXYEAR)
        throw new ValueError(__mod6(new str("year must be in %d..%d, not %d"), 3, MINYEAR, MAXYEAR, year));
    if(week<=0 || week>=53) {
        bool out_of_range = true;
        if(week==53) {
            /* ISO years have 53 weeks when they start on a Thursday, or on a
             * Wednesday in a leap year */
            __ss_int first_weekday = ymd_to_ord(year, 1, 1) % 7;
            if(first_weekday==4 || (first_weekday==3 && is_leap(year)))
                out_of_range = false;
        }
        if(out_of_range)
            throw new ValueError(__mod6(new str("Invalid week: %d"), 1, week));
    }
    if(day<=0 || day>=8)
        throw new ValueError(__mod6(new str("Invalid weekday: %d (range is [1, 7])"), 1, day));
    return iso_week1_monday(year) + (week-1)*7 + (day-1);
}

/* 'HH:MM:SS[.ffffff]' according to isoformat()'s timespec argument */
static str *iso_time_string(__ss_int hour, __ss_int minute, __ss_int second, __ss_int microsecond, str *timespec) {
    const __GC_STR &ts = timespec->unit;
    if(ts == __gcs("auto")) {
        if(microsecond==0)
            return __mod6(hour_format2, 3, hour, minute, second);
        return __mod6(point_string, 2, __mod6(hour_format2, 3, hour, minute, second), microsecond);
    }
    if(ts == __gcs("hours"))
        return __mod6(new str("%02d"), 1, hour);
    if(ts == __gcs("minutes"))
        return __mod6(new str("%02d:%02d"), 2, hour, minute);
    if(ts == __gcs("seconds"))
        return __mod6(hour_format2, 3, hour, minute, second);
    if(ts == __gcs("milliseconds"))
        return __mod6(new str("%02d:%02d:%02d.%03d"), 4, hour, minute, second, microsecond/1000);
    if(ts == __gcs("microseconds"))
        return __mod6(point_string, 2, __mod6(hour_format2, 3, hour, minute, second), microsecond);
    throw new ValueError(new str("Unknown timespec value"));
}

/* fromisoformat parsing, following CPython's C implementation
 * (parse_isoformat_date, parse_hh_mm_ss_ff and
 * _find_isoformat_datetime_separator). the parsers return false where
 * CPython says "Invalid isoformat string"; values out of range are left to
 * the date and time constructors, which raise their own errors, as in
 * CPython. there is no datetime.timezone yet, so a string with a time zone
 * offset is rejected. */

static ValueError *iso_invalid(str *s) {
    return new ValueError(__add_strs(2, new str("Invalid isoformat string: "), repr(s)));
}

/* n ascii digits at pos */
static bool iso_digits(const __GC_STR &s, size_t pos, size_t n, __ss_int &v) {
    if (pos + n > s.size())
        return false;
    v = 0;
    for (size_t i = pos; i < pos + n; i++) {
        if (s[i] < '0' || s[i] > '9')
            return false;
        v = v * 10 + (__ss_int)(s[i] - '0');
    }
    return true;
}

/* YYYY-MM-DD, YYYYMMDD, YYYY-Www, YYYYWww, YYYY-Www-D or YYYYWwwD */
static bool iso_parse_date(const __GC_STR &s, __ss_int &year, __ss_int &month, __ss_int &day) {
    size_t n = s.size();
    if (!iso_digits(s, 0, 4, year))
        return false;
    bool sep = n > 4 && s[4] == '-';
    size_t pos = 4 + sep;
    if (pos < n && s[pos] == 'W') {
        __ss_int week, wday = 1;
        if (!iso_digits(s, pos + 1, 2, week))
            return false;
        pos += 3;
        if (pos < n) {
            if (sep && s[pos++] != '-')
                return false;
            if (!iso_digits(s, pos, 1, wday))
                return false;
        }
        /* as date.fromisocalendar(), but a week or weekday out of range
         * makes the string invalid */
        if (year < MINYEAR || year > MAXYEAR || week < 1 || week > 53 || wday < 1 || wday > 7)
            return false;
        if (week == 53) {
            __ss_int first_weekday = ymd_to_ord(year, 1, 1) % 7;
            if (!(first_weekday == 4 || (first_weekday == 3 && is_leap(year))))
                return false;
        }
        ord_to_ymd(iso_week1_monday(year) + (week - 1) * 7 + (wday - 1), &year, &month, &day);
        return true;
    }
    if (!iso_digits(s, pos, 2, month))
        return false;
    pos += 2;
    if (sep && (pos >= n || s[pos++] != '-'))
        return false;
    return iso_digits(s, pos, 2, day);
}

/* HH[:MM[:SS[{.,}fff[fff]]]] or HH[MM[SS[{.,}fff[fff]]]] */
static bool iso_parse_time(const __GC_STR &s, __ss_int *comps) {
    size_t n = s.size(), p = 0;
    comps[0] = comps[1] = comps[2] = comps[3] = 0;
    if (n < 2) /* "Isoformat time too short" */
        return false;
    for (size_t i = 0; i < n; i++) /* a time zone offset: +HH:MM, -HH:MM or Z */
        if (s[i] == '+' || s[i] == '-' || s[i] == 'Z')
            return false;
    bool sep = true;
    for (int i = 0; i < 3; i++) {
        if (!iso_digits(s, p, 2, comps[i]))
            return false;
        p += 2;
        __ss_char c = p < n ? s[p] : 0;
        p++;
        if (i == 0)
            sep = c == ':';
        if (p >= n)
            return c == 0;
        if (sep && c == ':')
            continue;
        if (c == '.' || c == ',')
            break;
        if (sep)
            return false; /* malformed time separator */
        p--;
    }
    /* the fraction; digits after the sixth are dropped */
    size_t digits = std::min(n - p, (size_t)6);
    if (!iso_digits(s, p, digits, comps[3]))
        return false;
    for (size_t i = digits; i < 6; i++)
        comps[3] *= 10;
    for (p += digits; p < n; p++)
        if (s[p] < '0' || s[p] > '9')
            return false;
    return true;
}

/* where the date ends in a datetime string of at least 7 characters */
static bool iso_datetime_separator(const __GC_STR &s, size_t &loc) {
    size_t n = s.size();
    if (n == 7)
        loc = 7;
    else if (s[4] == '-') {
        if (s[5] != 'W')
            loc = 10;                    /* YYYY-MM-DD */
        else if (n > 8 && s[8] == '-') { /* YYYY-Www-D */
            if (n == 9)
                return false;
            /* YYYY-Www-HH... rather than YYYY-Www-D, best effort */
            loc = (n > 10 && s[10] >= '0' && s[10] <= '9') ? 8 : 10;
        } else
            loc = 8;                     /* YYYY-Www */
    } else if (s[4] == 'W') {            /* YYYYWww or YYYYWwwD */
        size_t idx = 7;
        while (idx < n && s[idx] >= '0' && s[idx] <= '9')
            idx++;
        if (idx < 9)
            loc = idx;
        else
            loc = idx % 2 == 0 ? 7 : 8;  /* an even number of digits after Www: no D */
    } else
        loc = 8;                         /* YYYYMMDD */
    return true;
}

//class date
date::date(__ss_int year_, __ss_int month_, __ss_int day_){
    __class__ = cl_date;

    if(year_<MINYEAR || year_>MAXYEAR)    throw __dt_range_error("year", MINYEAR, MAXYEAR, year_);
    if(month_<=0 || month_>12)            throw __dt_range_error("month", 1, 12, month_);
    if(day_<=0 || day_>days_in_month(year_,month_)) throw __dt_day_error(day_, month_, year_);

    this->year=year_;
    this->month=month_;
    this->day=day_;
}

date *date::today() {
    //today's date using localtime
    time_t rawtime = ::time(nullptr);
    tm * t = localtime( &rawtime );
    return new date(t->tm_year+1900,t->tm_mon+1,t->tm_mday);
}

/* like cpython: ValueError for NaN, OverflowError if the (floored) timestamp
   does not fit in time_t (the cast would be undefined behaviour) */
static double __floor_timestamp(double timestamp) {
	if (std::isnan(timestamp))
		throw new ValueError(new str("Invalid value NaN (not a number)"));
	double f = std::floor(timestamp);
	const double lim = std::ldexp(1.0, (int)(sizeof(time_t) * 8 - 1));
	if (!(f >= -lim && f < lim))
		throw new OverflowError(new str("timestamp out of range for platform time_t"));
	return f;
}

/* int timestamps are converted exactly (via double, 2**63-1 would round up
   to 2**63 and overflow); only an --int128 value can be out of range */
static time_t __int_timestamp(__ss_int timestamp) {
	if (sizeof(__ss_int) > sizeof(time_t) &&
	    (timestamp < (__ss_int)std::numeric_limits<time_t>::min() ||
	     timestamp > (__ss_int)std::numeric_limits<time_t>::max()))
		throw new OverflowError(new str("timestamp out of range for platform time_t"));
	return (time_t)timestamp;
}

/* localtime()/gmtime() return NULL (errno EOVERFLOW) when the year does not
   fit in struct tm; cpython raises OSError there */
static tm *__timestamp_tm(time_t t, bool utc) {
	errno = 0;
	tm *tm = utc ? gmtime(&t) : localtime(&t);
	if (!tm) {
		if (errno == 0)
			errno = EINVAL;
		__throw_oserror();
	}
	return tm;
}

date* date::fromtimestamp(double timestamp) {
	//date from timestamp using localtime; like cpython, round down (so -0.5 is still 1969-12-31)
	tm *tm = __timestamp_tm(time_t(__floor_timestamp(timestamp)), false);

	return new date(tm->tm_year + 1900, tm->tm_mon + 1, tm->tm_mday);
}

date* date::fromtimestamp(__ss_int timestamp) {
	tm *tm = __timestamp_tm(__int_timestamp(timestamp), false);
	return new date(tm->tm_year + 1900, tm->tm_mon + 1, tm->tm_mday);
}

/* like CPython: ValueError (not OverflowError) for out-of-range ordinals */
static void check_ordinal(__ss_int o, __ss_int *year, __ss_int *month, __ss_int *day) {
    if(o<1)
        throw new ValueError(new str("ordinal must be >= 1"));
    ord_to_ymd(o, year, month, day);
    if(*year>MAXYEAR)
        throw __dt_range_error("year", MINYEAR, MAXYEAR, *year);
}

/* date/datetime arithmetic that leaves the supported year range raises
   OverflowError in CPython, unlike date.fromordinal() (ValueError) above */
static void check_ordinal_arith(__ss_int o, __ss_int *year, __ss_int *month, __ss_int *day) {
    if(o<1)
        throw new OverflowError(new str("date value out of range"));
    ord_to_ymd(o, year, month, day);
    if(*year>MAXYEAR)
        throw new OverflowError(new str("date value out of range"));
}

static date *__date_arith(__ss_int o) {
    __ss_int y, m, d;
    check_ordinal_arith(o, &y, &m, &d);
    return new date(y, m, d);
}

static datetime *__datetime_arith(__ss_int o) {
    __ss_int y, m, d;
    check_ordinal_arith(o, &y, &m, &d);
    return new datetime(y, m, d);
}

date* date::fromordinal(__ss_int o) {
    __ss_int y, m, d;
    check_ordinal(o, &y, &m, &d);
    return new date(y, m, d);
}

date *date::fromisocalendar(__ss_int year, __ss_int week, __ss_int day) {
    return fromordinal(isoweek_to_ord(year, week, day));
}

date *date::strptime(str *date_string, str *format) {
    /* like cpython's _strptime_datetime_date: parse as a datetime, keep the
     * date fields */
    datetime *dt = datetime::strptime(date_string, format);
    return new date(dt->year, dt->month, dt->day);
}

date *date::fromisoformat(str *date_string) {
    const __GC_STR &s = date_string->unit;
    __ss_int y, m, d;
    if ((s.size() != 7 && s.size() != 8 && s.size() != 10) || !iso_parse_date(s, y, m, d))
        throw iso_invalid(date_string);
    return new date(y, m, d);
}

date *date::__add__(timedelta *other) {
    return __date_arith(toordinal()+(other->days));
}

date *date::__sub__(timedelta *other) {
    return __date_arith(toordinal()-(other->days));
}

timedelta *date::__sub__(date *other) {
    return new timedelta((double)(toordinal()-other->toordinal()), 0, 0, 0 ,0, 0, 0);
}

__ss_int date::__cmp__(date *other) {
    if(year==other->year && month==other->month && day==other->day)
        return 0;
    if (toordinal() > other->toordinal())
        return 1;
    return -1;
}

__ss_bool date::__eq__(date *other) { return __mbool(__cmp__(other) == 0); }
__ss_bool date::__ne__(date *other) { return __mbool(__cmp__(other) != 0); }
__ss_bool date::__gt__(date *other) { return __mbool(__cmp__(other) == 1); }
__ss_bool date::__lt__(date *other) { return __mbool(__cmp__(other) == -1); }
__ss_bool date::__ge__(date *other) { return __mbool(__cmp__(other) != -1); }
__ss_bool date::__le__(date *other) { return __mbool(__cmp__(other) != 1); }

str *date::__repr__() {
    return __mod6(date_repr_format, 3, year, month, day);
}

__ss_int date::__hash__() {
    return hash_combine(hash_combine(year, month), day);
}

date *date::replace(__ss_int __args, __ss_int year_, __ss_int month_, __ss_int day_) {
    date* t = new date(this);

    if((__args & 1)==1) {
        if(year_<MINYEAR || year_>MAXYEAR)    throw __dt_range_error("year", MINYEAR, MAXYEAR, year_);
        t->year=year_;}
    if((__args & 2)==2) {
        if(month_<=0 || month_>12)            throw __dt_range_error("month", 1, 12, month_);
        t->month=month_;}
    if((__args & 4)==4) {
        if(day_<=0 || day_>days_in_month(t->year,t->month)) throw __dt_day_error(day_, t->month, t->year);
        t->day=day_;
    } else if(t->day>days_in_month(t->year,t->month)) {
        /* day itself was not replaced, but a new year/month can still make
         * the existing day invalid (e.g. Jan 31 -> April) */
        throw __dt_day_error(t->day, t->month, t->year);
    }
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

__IsoCalendarDate::__IsoCalendarDate(__ss_int year, __ss_int week, __ss_int weekday) : tuple2<__ss_int, __ss_int>(3, year, week, weekday) {
    this->__class__ = cl___IsoCalendarDate;
    this->year = year;
    this->week = week;
    this->weekday = weekday;
}

str *__IsoCalendarDate::__repr__() {
    return __mod6(new str("datetime.IsoCalendarDate(year=%d, week=%d, weekday=%d)"), 3, year, week, weekday);
}

__IsoCalendarDate *date::isocalendar() {
//modified from cpython
    __ss_int  week1_monday = iso_week1_monday(year);
    __ss_int  today        = ymd_to_ord(year, month, day);
    __ss_int  tmpyear      = year;
    int64_t   tmpweek;
    int64_t   tmpday;

    tmpweek = floordivmod(today - week1_monday, 7, &tmpday);
    if (tmpweek < 0) {
        --tmpyear;
        week1_monday = iso_week1_monday(tmpyear);
        tmpweek = floordivmod(today - week1_monday, 7, &tmpday);
    }
    else if (tmpweek >= 52 && today >= iso_week1_monday(tmpyear + 1)) {
        ++tmpyear;
        tmpweek = 0;
    }
    return new __IsoCalendarDate((__ss_int)tmpyear, (__ss_int)(tmpweek+1), (__ss_int)(tmpday+1));
}

str *date::isoformat() {
    return __str__();
}

str *date::__str__() {
    return __mod6(date_format, 3, this->year, this->month, this->day);
}

str *date::ctime() {
    __ss_int wday = weekday();

    return __mod6(ctime_format, 7, DayNames->__getitem__(wday), MonthNames->__getitem__(month-1),
                        day, (__ss_int)0, (__ss_int)0, (__ss_int)0, year);
}

/* expand the datetime-specific directives (%f, %z, %Z) ourselves and pass
   everything else on to time.strftime. '%%' is skipped over as a unit, so
   that e.g. '%%f' stays a literal '%f' */
static void __strftime_append_escaped(__GC_STR &out, str *s) {
    if(!s)
        return;
    for(size_t i=0; i<s->unit.size(); i++) {
        out += s->unit[i];
        if(s->unit[i] == U'%')
            out += U'%';
    }
}

static str *__strftime_preprocess(str *format, __ss_int microsecond, str *z, str *Z) {
    __GC_STR out;
    const __GC_STR &f = format->unit;
    size_t n = f.size();
    for(size_t i=0; i<n; i++) {
        __ss_char c = f[i];
        if(c != U'%' || i+1 == n) {
            out += c;
            continue;
        }
        __ss_char d = f[++i];
        if(d == U'f') {
            char buf[8];
            snprintf(buf, sizeof(buf), "%06d", (int)microsecond);
            for(int k=0; k<6; k++)
                out += (__ss_char)buf[k];
        } else if(d == U'z') {
            __strftime_append_escaped(out, z);
        } else if(d == U'Z') {
            __strftime_append_escaped(out, Z);
        } else {
            out += U'%';
            out += d;
        }
    }
    return new str(out);
}

str *date::strftime(str *format) {
    return __time__::strftime(__strftime_preprocess(format, 0, NULL, NULL), timetuple());
}

/* like CPython: an empty spec gives str(self), anything else is passed on
   to strftime (see __format in lib/builtin/format.hpp) */
str *date::__format__(str *format_spec) {
    if (format_spec->unit.empty())
        return __str__();
    return strftime(format_spec);
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
	return __mod6(&f,2,offset->seconds/3600,(offset->seconds/60)%60);
}


//class datetime
datetime::datetime(__ss_int year_, __ss_int month_, __ss_int day_, __ss_int hour_, __ss_int minute_, __ss_int second_, __ss_int microsecond_, tzinfo *tzinfo, __ss_int fold_) : date(year_,month_,day_) {
    __class__ = cl_datetime;

    if(hour_>=24 || hour_<0) throw __dt_range_error("hour", 0, 23, hour_);
    if(minute_>=60 || minute_<0) throw __dt_range_error("minute", 0, 59, minute_);
    if(second_>=60 || second_<0) throw __dt_range_error("second", 0, 59, second_);
    if(microsecond_>=1000000 || microsecond_<0) throw __dt_range_error("microsecond", 0, 999999, microsecond_);
    if(fold_!=0 && fold_!=1) throw new ValueError(__mod6(new str("fold must be either 0 or 1, not %d"), 1, fold_));

    this->hour = hour_;
    this->minute = minute_;
    this->second = second_;
    this->microsecond = microsecond_;
    this->_tzinfo = tzinfo;
    this->fold = fold_;
}

datetime *datetime::today() {
    timespec ts { 0, 0 };

#ifdef _MSC_VER
    if (clock_gettime(0, &ts) == -1)
#else
    if (clock_gettime(CLOCK_REALTIME, &ts) == -1)
#endif
        __throw_oserror();

    tm *t = localtime(&ts.tv_sec);

    return new datetime(t->tm_year+1900, t->tm_mon+1, t->tm_mday, t->tm_hour, t->tm_min, t->tm_sec, (__ss_int)ts.tv_nsec / 1000);
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
    timespec ts { 0, 0 };

#ifdef _MSC_VER
    if (clock_gettime(0, &ts) == -1)
#else
    if (clock_gettime(CLOCK_REALTIME, &ts) == -1)
#endif
        __throw_oserror();

    tm *t = gmtime(&ts.tv_sec);

    return new datetime(t->tm_year+1900, t->tm_mon+1, t->tm_mday, t->tm_hour, t->tm_min, t->tm_sec, (__ss_int)ts.tv_nsec / 1000);
}

datetime *datetime::from_timestamp(double timestamp, tzinfo *tzinfo, bool timefn) {
	//modified from cpython
	time_t timet;
	double fraction;
	__ss_int us;

	/* floor (Python's mod semantics), so fraction is in [0, 1) */
	double seconds = __floor_timestamp(timestamp);
	timet = (time_t)seconds;
	fraction = timestamp - seconds;
	/* round-half-to-even, like cpython (_PyTime_ROUND_HALF_EVEN) */
	us = ___round(fraction * 1e6);

	/* If timestamp is less than one microsecond smaller than a
	 * full second, round up. Otherwise, ValueErrors are raised
	 * for some floats. */
	if (us == 1000000) {
		timet += 1;
		us = 0;
	}

	return from_time_t(timet, us, tzinfo, timefn);
}

datetime *datetime::from_time_t(time_t timet, __ss_int us, tzinfo *tzinfo, bool timefn) {
	struct tm *tm = __timestamp_tm(timet, timefn);

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

datetime *datetime::utcfromtimestamp(double timestamp) {
    return from_timestamp(timestamp,NULL,true);	//true=gmtime
}

datetime *datetime::utcfromtimestamp(__ss_int timestamp) {
    return from_time_t(__int_timestamp(timestamp), 0, NULL, true);
}

datetime *datetime::fromtimestamp(double timestamp, tzinfo *tzinfo) {
	datetime *tmp = from_timestamp(timestamp, tzinfo, (bool)tzinfo);
				// tzinfo == Py_None ? localtime : gmtime,
	if(tzinfo!=NULL)
		return tzinfo->fromutc(tmp);
	else
		return tmp;
}

datetime *datetime::fromtimestamp(__ss_int timestamp, tzinfo *tzinfo) {
	datetime *tmp = from_time_t(__int_timestamp(timestamp), 0, tzinfo, (bool)tzinfo);
	if(tzinfo!=NULL)
		return tzinfo->fromutc(tmp);
	else
		return tmp;
}

datetime *datetime::fromordinal(__ss_int o) {
    __ss_int y, m, d;
    check_ordinal(o, &y, &m, &d);
    return new datetime(y, m, d);
}

datetime *datetime::fromisocalendar(__ss_int year, __ss_int week, __ss_int day) {
    return fromordinal(isoweek_to_ord(year, week, day));
}

datetime *datetime::combine(date *d, time *t) {
    return new datetime(d->year,d->month,d->day,t->hour,t->minute,t->second,t->microsecond,t->_tzinfo,t->fold);
}

datetime *datetime::strptime(str *date_string, str *format) {
    /* like cpython's _strptime_datetime. there is no datetime.timezone yet,
     * so a %z offset does not make the result aware */
    __time__::__ss_strptime_result r;
    __time__::__ss_strptime(date_string, format, r);
    return new datetime(r.year, r.month, r.day, r.hour, r.minute, r.second, r.microsecond);
}

datetime *datetime::fromisoformat(str *date_string) {
    const __GC_STR &s = date_string->unit;
    size_t loc;
    __ss_int y, m, d, t[4] = {0, 0, 0, 0};
    if (s.size() < 7 || !iso_datetime_separator(s, loc) || !iso_parse_date(s.substr(0, loc), y, m, d))
        throw iso_invalid(date_string);
    if (loc < s.size() && !iso_parse_time(s.substr(loc + 1), t))
        throw iso_invalid(date_string);
    return new datetime(y, m, d, t[0], t[1], t[2], t[3]);
}

datetime *datetime::__add__(timedelta *other) {
    __ss_int usec = this->microsecond + other->microseconds;
    __ss_int sec = this->second + other->seconds;
    datetime *r = __datetime_arith(this->toordinal()+other->days +
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
    datetime *r = __datetime_arith(days);
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
		date *tmp = __date_arith(days-1);
		r->year=tmp->year;
		r->month=tmp->month;
		r->day=tmp->day;
	}
    return r;
}

timedelta *datetime::__sub__(datetime *other) {
	timedelta *td = new timedelta((double)(this->toordinal()-other->toordinal()),(double)(this->second-other->second),(double)(this->microsecond-other->microsecond),0,(double)(this->minute-other->minute),(double)(this->hour-other->hour));
	if(_tzinfo==NULL && other->_tzinfo==NULL)
		return td;
	if(_tzinfo!=NULL && other->_tzinfo!=NULL) {
		timedelta *offset1 = _tzinfo->utcoffset(this);
		timedelta *offset2 = other->_tzinfo->utcoffset(other);
		if(offset1!=NULL && offset2!=NULL) {
			timedelta *tmp = td->__sub__(offset1);
			td = tmp->__add__(offset2);
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
	__ss_int ford = f->toordinal();
	__ss_int oord = other->toordinal();
	if(ford > oord)
		return 1;
	if(ford == oord && ((int64_t)f->hour*3600+f->minute*60+f->second)*1000000+f->microsecond > ((int64_t)other->hour*3600+other->minute*60+other->second)*1000000+other->microsecond)
		return 1;
    return -1;
}

__ss_bool datetime::__eq__(datetime *other) { return __mbool(__cmp__(other) == 0); }
__ss_bool datetime::__ne__(datetime *other) { return __mbool(__cmp__(other) != 0); }
__ss_bool datetime::__gt__(datetime *other) { return __mbool(__cmp__(other) == 1); }
__ss_bool datetime::__lt__(datetime *other) { return __mbool(__cmp__(other) == -1); }
__ss_bool datetime::__ge__(datetime *other) { return __mbool(__cmp__(other) != -1); }
__ss_bool datetime::__le__(datetime *other) { return __mbool(__cmp__(other) != 1); }

/* cpython omits trailing zero second/microsecond fields from the repr */
static str *time_repr_tail(__ss_int second, __ss_int microsecond, tzinfo *tz, __ss_int fold) {
    str *s = new str("");
    if(microsecond != 0)
        s = __add_strs(2, __mod6(repr_arg_format, 1, second), __mod6(repr_arg_format, 1, microsecond));
    else if(second != 0)
        s = __mod6(repr_arg_format, 1, second);
    if(tz)
        s = __add_strs(2, s, __mod6(repr_tzinfo_format, 1, repr(tz)));
    if(fold)
        s = __add_strs(2, s, repr_fold_string);
    return __add_strs(2, s, close_paren_string);
}

str *datetime::__repr__() {
    str *head = __mod6(datetime_repr_format, 5, year, month, day, hour, minute);
    return __add_strs(2, head, time_repr_tail(second, microsecond, _tzinfo, fold));
}

__ss_int datetime::__hash__() {
    /* consistent with __cmp__: aware datetimes hash by their utc equivalent */
    datetime *f = this;
    if(_tzinfo)
        f = __sub__(_tzinfo->utcoffset(this));
    __ss_int h = hash_combine(hash_combine(f->year, f->month), f->day);
    h = hash_combine(h, f->hour);
    h = hash_combine(h, f->minute);
    h = hash_combine(h, f->second);
    return hash_combine(h, f->microsecond);
}

date *datetime::_date() {
	return new date(year,month,day);
}

time *datetime::_time() {
	return new time(hour,minute,second,microsecond,NULL,fold);
}

time *datetime::timetz() {
	return new time(hour,minute,second,microsecond,_tzinfo,fold);
}

datetime *datetime::replace(__ss_int __args, __ss_int year_, __ss_int month_, __ss_int day_, __ss_int hour_, __ss_int minute_, __ss_int second_, __ss_int microsecond_, tzinfo *tzinfo, __ss_int fold_) {
    datetime *t = new datetime(this);

   if((__args & 1)==1) {
        if(year_<MINYEAR || year_>MAXYEAR)    throw __dt_range_error("year", MINYEAR, MAXYEAR, year_);
        t->year=year_;}
    if((__args & 2)==2) {
        if(month_<=0 || month_>12)            throw __dt_range_error("month", 1, 12, month_);
        t->month=month_;}
    if((__args & 4)==4) {
        if(day_<=0 || day_>days_in_month(t->year,t->month)) throw __dt_day_error(day_, t->month, t->year);
        t->day=day_;
    } else if(t->day>days_in_month(t->year,t->month)) {
        /* day itself was not replaced, but a new year/month can still make
         * the existing day invalid (e.g. Jan 31 -> April) */
        throw __dt_day_error(t->day, t->month, t->year);
    }
    if((__args & 8)==8) {
        if(hour_<0 || hour_>=24)              throw __dt_range_error("hour", 0, 23, hour_);
        t->hour=hour_;}
    if((__args & 16)==16) {
        if(minute_<0 || minute_>=60)          throw __dt_range_error("minute", 0, 59, minute_);
        t->minute=minute_;}
    if((__args & 32)==32) {
        if(second_<0 || second_>=60)          throw __dt_range_error("second", 0, 59, second_);
        t->second=second_;}
    if((__args & 64)==64) {
        if(microsecond_<0 || microsecond_>=1000000)      throw __dt_range_error("microsecond", 0, 999999, microsecond_);
        t->microsecond=microsecond_;}
    if((__args & 128)==128)
        t->_tzinfo = tzinfo;
    if((__args & 256)==256) {
        if(fold_!=0 && fold_!=1)              throw new ValueError(__mod6(new str("fold must be either 0 or 1, not %d"), 1, fold_));
        t->fold=fold_;}
    return t;
}


datetime *datetime::astimezone(tzinfo *tzinfo) {
	if(this->_tzinfo == NULL)
		throw new ValueError(new str("astimezone() cannot be applied to a naive datetime"));
	if(this->_tzinfo == tzinfo)
		return this;
	datetime *utc = this->__sub__(this->utcoffset())->replace(128,-1,-1,-1,-1,-1,-1,-1,tzinfo,-1);
	datetime *r = tzinfo->fromutc(utc);
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
    return _tzinfo ? _tzinfo->utcoffset(this) : nullptr;
}

timedelta *datetime::dst() {
    if(_tzinfo==NULL)
        return (timedelta *)NULL;
    else
		return _tzinfo->dst(this);
}

str *datetime::tzname() {
    if(_tzinfo==NULL)
        return NULL;
    else
		return _tzinfo->tzname(this);
}

__ss_float datetime::timestamp() {
	if(_tzinfo!=NULL) {
		/* aware: compute seconds since the Unix epoch (1970-01-01 UTC)
		 * directly from the calendar fields and subtract the utcoffset.
		 * This avoids mktime()/timegm() altogether, so the result does
		 * not depend on the platform (Windows/macOS/Linux) or on the
		 * process' local timezone setting. */
		static const __ss_int epoch_ordinal = 719163; //date(1970,1,1).toordinal()
		__ss_float secs = (__ss_float)(toordinal()-epoch_ordinal)*86400.0 +
			(__ss_float)hour*3600.0 + (__ss_float)minute*60.0 + (__ss_float)second + (__ss_float)microsecond/1e6;
		timedelta *off = utcoffset();
		if(off!=NULL)
			secs -= (__ss_float)off->days*86400.0 + (__ss_float)off->seconds + (__ss_float)off->microseconds/1e6;
		return secs;
	}
	else {
		/* naive: interpret the wall-clock fields as local time, same as
		 * cpython does (via mktime). tm_isdst=-1 lets the platform figure
		 * out DST; tm_wday is used to distinguish a genuine mktime()
		 * failure from a valid result that happens to encode as -1. */
		struct tm t;
		memset(&t, 0, sizeof(t));
		t.tm_year = (int)year-1900;
		t.tm_mon = (int)month-1;
		t.tm_mday = (int)day;
		t.tm_hour = (int)hour;
		t.tm_min = (int)minute;
		t.tm_sec = (int)second;
		t.tm_isdst = -1;
		t.tm_wday = -1;

		time_t timet = mktime(&t);
		if(timet==(time_t)(-1) && t.tm_wday==-1)
			throw new OverflowError(new str("timestamp out of range"));

		return (__ss_float)timet + (__ss_float)microsecond/1e6;
	}
}


__time__::struct_time *datetime::timetuple() {
    char dst=-1;
    if(_tzinfo) {
		timedelta *tmp = _tzinfo->dst(this);
		if(tmp->days==0 && tmp->seconds==0 && tmp->microseconds==0)
			dst=0;
		else
			dst=1;
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

str *datetime::isoformat(str *sep, str *timespec) {
    if(sep==NULL)
        sep = t_string;
    if(sep->__len__()!=1) {
        throw new TypeError(new str("isoformat() argument 1 must be char, not str"));
    }
    if(timespec==NULL)
        timespec = auto_string;
    str *r = __add_strs(3,date::__str__(),sep,iso_time_string(hour, minute, second, microsecond, timespec));
    if(this->_tzinfo!=NULL)
        return r->__add__(this->_tzinfo->minutes_to_str(this));
    return r;
}

str *datetime::__str__() {
    return isoformat(space_string, NULL);
}

str *datetime::ctime() {
    __ss_int wday = weekday();

    return __mod6(ctime_format, 7, DayNames->__getitem__(wday), MonthNames->__getitem__(month-1),
                        day, hour, minute, second, year);
}

str *datetime::strftime(str *format) {
    str *z = NULL, *Z = NULL;
    if(_tzinfo) {
        z = _tzinfo->minutes_to_str(this);
        Z = _tzinfo->tzname(this);
    }
    return __time__::strftime(__strftime_preprocess(format, microsecond, z, Z), timetuple());
}

str *datetime::__format__(str *format_spec) {
    if (format_spec->unit.empty())
        return __str__();
    return strftime(format_spec);
}

//class time
time::time(__ss_int hour_, __ss_int minute_, __ss_int second_, __ss_int microsecond_, tzinfo *tzinfo, __ss_int fold_) {
    __class__=cl_time;

    if(hour_>=24 || hour_<0) throw __dt_range_error("hour", 0, 23, hour_);
    if(minute_>=60 || minute_<0) throw __dt_range_error("minute", 0, 59, minute_);
    if(second_>=60 || second_<0) throw __dt_range_error("second", 0, 59, second_);
    if(microsecond_>=1000000 || microsecond_<0) throw __dt_range_error("microsecond", 0, 999999, microsecond_);
    if(fold_!=0 && fold_!=1) throw new ValueError(__mod6(new str("fold must be either 0 or 1, not %d"), 1, fold_));

    this->hour = hour_;
    this->minute = minute_;
    this->second = second_;
    this->microsecond = microsecond_;
    this->_tzinfo = tzinfo;
    this->fold = fold_;
}

time *time::strptime(str *time_string, str *format) {
    /* like cpython's _strptime_datetime_time: parse as a datetime, keep the
     * time fields */
    datetime *dt = datetime::strptime(time_string, format);
    return new time(dt->hour, dt->minute, dt->second, dt->microsecond);
}

time *time::fromisoformat(str *time_string) {
    const __GC_STR &s = time_string->unit;
    __ss_int t[4];
    /* the T of a time-only string is optional */
    if (!iso_parse_time(s.size() > 0 && s[0] == 'T' ? s.substr(1) : s, t))
        throw iso_invalid(time_string);
    return new time(t[0], t[1], t[2], t[3]);
}

time *time::replace(__ss_int __args, __ss_int hour_, __ss_int minute_, __ss_int second_, __ss_int microsecond_, tzinfo *tzinfo, __ss_int fold_) {
    time *t = new time(this);
    if((__args & 1)==1) {
        if(hour_<0 || hour_>=24)          throw __dt_range_error("hour", 0, 23, hour_);
        t->hour=hour_;}
    if((__args & 2)==2) {
        if(minute_<0 || minute_>=60)      throw __dt_range_error("minute", 0, 59, minute_);
        t->minute=minute_;}
    if((__args & 4)==4) {
        if(second_<0 || second_>=60)      throw __dt_range_error("second", 0, 59, second_);
        t->second=second_;}
    if((__args & 8)==8) {
        if(microsecond_<0 || microsecond_>=1000000)      throw __dt_range_error("microsecond", 0, 999999, microsecond_);
        t->microsecond=microsecond_;}
    if((__args & 16)==16)
        t->_tzinfo = tzinfo;
    if((__args & 32)==32) {
        if(fold_!=0 && fold_!=1)          throw new ValueError(__mod6(new str("fold must be either 0 or 1, not %d"), 1, fold_));
        t->fold=fold_;}
    return t;
}

str *time::isoformat(str *timespec) {
    if(timespec==NULL)
        timespec = auto_string;
    str *s = iso_time_string(hour, minute, second, microsecond, timespec);
    if(_tzinfo!=NULL)
        return s->__add__(_tzinfo->minutes_to_str(NULL));
    return s;
}

str *time::__str__() {
    return isoformat(NULL);
}

str *time::strftime(str* format) {
    str *z = NULL, *Z = NULL;
    if(_tzinfo) {
        z = _tzinfo->minutes_to_str(NULL);
        Z = _tzinfo->tzname(NULL);
    }
    return __time__::strftime(__strftime_preprocess(format, microsecond, z, Z),
        new __time__::struct_time(new tuple2<__ss_int, __ss_int>(9,
            (__ss_int)1900, (__ss_int)1, (__ss_int)1,
            (__ss_int)hour, (__ss_int)minute, (__ss_int)second,
            (__ss_int)0, (__ss_int)1, (__ss_int)(-1))));
}

str *time::__format__(str *format_spec) {
    if (format_spec->unit.empty())
        return __str__();
    return strftime(format_spec);
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
        return NULL;
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

    int64_t fus = ((int64_t)f->hour*3600+f->minute*60+f->second)*1000000+f->microsecond;
    int64_t ous = ((int64_t)other->hour*3600+other->minute*60+other->second)*1000000+other->microsecond;
    if(fus == ous)
        return 0;
    if(fus > ous)
        return 1;
    return -1;
}

__ss_bool time::__eq__(time *other) { return __mbool(__cmp__(other) == 0); }
__ss_bool time::__ne__(time *other) { return __mbool(__cmp__(other) != 0); }
__ss_bool time::__gt__(time *other) { return __mbool(__cmp__(other) == 1); }
__ss_bool time::__lt__(time *other) { return __mbool(__cmp__(other) == -1); }
__ss_bool time::__ge__(time *other) { return __mbool(__cmp__(other) != -1); }
__ss_bool time::__le__(time *other) { return __mbool(__cmp__(other) != 1); }

str *time::__repr__() {
    str *head = __mod6(time_repr_format, 2, hour, minute);
    return __add_strs(2, head, time_repr_tail(second, microsecond, _tzinfo, fold));
}

__ss_int time::__hash__() {
    __ss_int h = hash_combine(hour, minute);
    h = hash_combine(h, second);
    return hash_combine(h, microsecond);
}


//class timedelta

/* Bound on the whole days a single constructor argument may contribute. It is
 * far beyond the C int range that the result has to fit in, and small enough
 * that the seven contributions (and the carry from the microseconds) can be
 * summed in 64 bits. */
static const uint64_t TIMEDELTA_ACC_LIMIT = (uint64_t)1 << 56;

/* floor(w / per_day) and the matching remainder in [0, per_day), computed
 * exactly for an integer-valued double w. Scaling w to microseconds first does
 * not fit in 64 bits (timedelta(minutes=2**62) wrapped to 0:00:00, and the
 * valid range of timedelta goes up to about 8.64e19 microseconds), and casting
 * a double of 2**63 or more to int64_t is undefined. cpython uses python ints
 * here. Returns false if the quotient exceeds TIMEDELTA_ACC_LIMIT. */
static bool timedelta_split_days(double w, uint64_t per_day, int64_t *days, int64_t *rem) {
    double a = std::fabs(w);
    int e;
    std::frexp(a, &e); /* a < 2**e */
    int shift = e > 64 ? e - 64 : 0;
    /* a has a 53-bit mantissa, so a / 2**shift is still an integer, and it is
       below 2**64 */
    uint64_t m = (uint64_t)std::ldexp(a, -shift);
    uint64_t q = m / per_day, r = m % per_day;
    for(; shift > 0; shift--) { /* long division, one bit of a at a time */
        if(q > TIMEDELTA_ACC_LIMIT)
            return false;
        q *= 2;
        r *= 2;
        if(r >= per_day) {
            r -= per_day;
            q += 1;
        }
    }
    if(q > TIMEDELTA_ACC_LIMIT)
        return false;
    if(w < 0 && r != 0) { /* floor semantics */
        q += 1;
        r = per_day - r;
    }
    *days = w < 0 ? -(int64_t)q : (int64_t)q;
    *rem = (int64_t)r;
    return true;
}

/* Split one constructor argument into its whole and fractional parts, like
 * cpython's accum() in _datetimemodule.c: the whole part is added exactly to
 * the integer accumulators (as whole days, plus the remainder in
 * microseconds), the fractional part is scaled and carried along in a double
 * (in microseconds), to be rounded once at the very end. Handling every
 * argument separately keeps e.g. timedelta(hours=-55695256, seconds=-909.352)
 * exact, where combining the arguments into one double first would lose the
 * microseconds.
 *
 * per_day is the number of units in a day (1 for days and weeks), days_per_unit
 * the number of days in a unit (7 for weeks, else 1) and us_per_unit the number
 * of microseconds in a unit. *overflow is set if the argument alone is far too
 * large; as in cpython the OverflowError only comes after all the arguments
 * have been checked for NaN and infinity. (unlike cpython, two such arguments
 * that cancel out still overflow) */
static inline void timedelta_accum(timedelta_arg a, uint64_t per_day, int64_t days_per_unit, int64_t us_per_unit, int64_t *days_acc, int64_t *us_acc, double *leftover_us, bool *overflow) {
    if(a.is_int) { /* exact: no fraction, and no detour through a double */
        int64_t rem, d = floordivmod(a.i, (int64_t)per_day, &rem);
        if(d > (int64_t)TIMEDELTA_ACC_LIMIT || d < -(int64_t)TIMEDELTA_ACC_LIMIT) {
            *overflow = true;
            return;
        }
        *days_acc += d * days_per_unit;
        *us_acc += rem * us_per_unit;
        return;
    }
    double arg = a.f;
    if(std::isnan(arg))
        throw new ValueError(new str("cannot convert float NaN to integer"));
    if(std::isinf(arg))
        throw new OverflowError(new str("cannot convert float infinity to integer"));
    double whole;
    double frac = modf(arg, &whole);
    int64_t d, rem;
    if(!timedelta_split_days(whole, per_day, &d, &rem)) {
        *overflow = true;
        return;
    }
    *days_acc += d * days_per_unit;
    *us_acc += rem * us_per_unit; /* < one day */
    if (frac != 0.0) {
        /* scale the fraction to microseconds and again split off the whole
           microseconds, so that only the sub-microsecond remainder is carried
           in floating point (keeps it small, hence precise) */
        frac = modf(frac * (double)us_per_unit, &whole);
        *us_acc += (int64_t)whole;
        *leftover_us += frac;
    }
}

static void timedelta_check_days(int64_t days) {
    if(days>999999999 || days<(-999999999)) {
        char buf[64];
        snprintf(buf, sizeof(buf), "days=%lld; must have magnitude <= 999999999", (long long)days);
        throw new OverflowError(new str(buf));
    }
}

timedelta::timedelta(timedelta_arg days_, timedelta_arg seconds_, timedelta_arg microseconds_, timedelta_arg milliseconds, timedelta_arg minutes, timedelta_arg hours, timedelta_arg weeks) {
    __class__ = cl_timedelta;

    /* Same algorithm as cpython: whole parts of the arguments are accumulated
     * exactly in integer days and microseconds, fractional parts are
     * carried as leftover microseconds and converted with a single
     * round-half-to-even (___round, the builtin round() implementation). The
     * old implementation derived the microseconds from one combined float
     * total and the seconds from a separately truncated total; for negative
     * totals the two disagreed by a second (timedelta(days=-1, seconds=1.5)
     * came out as -1 day, 0:00:00.5), and it rounded ties away from zero. */
    const int64_t us_per_day = (int64_t)24 * 3600 * 1000000;
    int64_t d = 0, us = 0;
    double leftover_us = 0.0;
    bool overflow = false;

    /* same order as cpython's delta_new: the leftover is a floating point sum,
       so a different order can change the last bit and flip a tie */
    timedelta_accum(microseconds_, us_per_day, 1, 1, &d, &us, &leftover_us, &overflow);
    timedelta_accum(milliseconds, us_per_day / 1000, 1, 1000, &d, &us, &leftover_us, &overflow);
    timedelta_accum(seconds_, 24 * 3600, 1, 1000000, &d, &us, &leftover_us, &overflow);
    timedelta_accum(minutes, 24 * 60, 1, 60 * 1000000, &d, &us, &leftover_us, &overflow);
    timedelta_accum(hours, 24, 1, (int64_t)3600 * 1000000, &d, &us, &leftover_us, &overflow);
    timedelta_accum(days_, 1, 1, us_per_day, &d, &us, &leftover_us, &overflow);
    timedelta_accum(weeks, 1, 7, 7 * us_per_day, &d, &us, &leftover_us, &overflow);

    if(overflow)
        throw new OverflowError(new str("Python int too large to convert to C int"));

    if (leftover_us != 0.0) {
        /* round-half-to-even on the *total* number of microseconds (as
         * cpython does), not on the leftover alone: the parity of the total
         * is the parity of us, since the number of microseconds in a day is
         * even. Adding that parity before rounding and removing it afterwards
         * makes ___round's tie-breaking land the total on an even value. */
        int64_t odd = us & 1;
        us += ___round(leftover_us + (double)odd) - odd;
    }

    /* normalize with floor semantics: 0 <= microseconds < 1e6, 0 <= seconds < 86400 */
    int64_t rem;
    d += floordivmod(us, us_per_day, &rem);
    int64_t s = rem / 1000000;
    us = rem % 1000000;

    /* as cpython: days must fit a C int, and then the range is checked */
    if(d > std::numeric_limits<int>::max() || d < std::numeric_limits<int>::min())
        throw new OverflowError(new str("Python int too large to convert to C int"));
    timedelta_check_days(d);

    this->days = (__ss_int)d;
    this->seconds = (__ss_int)s;
    this->microseconds = (__ss_int)us;
}

__ss_bool timedelta::__bool__() {
    return __mbool(days != 0 || seconds != 0 || microseconds != 0);
}

str *timedelta::__str__() {
    str *s;
    if(days==0)
        s=__mod6(hour_format1, 3, seconds/3600, (seconds%3600)/60, seconds%60);
    else if(days==1)
        s=__mod6(one_day_string,3,seconds/3600, (seconds%3600)/60, seconds%60);
    else if(days==-1)
        s=__mod6(minus_one_day_string,3,seconds/3600, (seconds%3600)/60, seconds%60);
    else
        s=__mod6(multiple_days_string,4,days,seconds/3600, (seconds%3600)/60, seconds%60);
    if(microseconds==0)
        return s;
    else
        return __mod6(point_string,2,s,microseconds);
}

timedelta *timedelta::__add__(timedelta *other) {
    return new timedelta((double)(days+other->days), (double)(seconds+other->seconds), (double)(microseconds+other->microseconds),0,0,0,0);
}

timedelta *timedelta::__sub__(timedelta *other) {
    return new timedelta((double)(days-other->days), (double)(seconds-other->seconds), (double)(microseconds-other->microseconds),0,0,0,0);
}

/* cpython converts the float to an exact integer ratio first */
static void timedelta_check_ratio(__ss_float f) {
    if(std::isnan(f))
        throw new ValueError(new str("cannot convert NaN to integer ratio"));
    if(std::isinf(f))
        throw new OverflowError(new str("cannot convert Infinity to integer ratio"));
}


static int64_t floordivmod(int64_t a, int64_t b, int64_t *r) {
    int64_t q = a / b;
    int64_t rem = a - q * b;
    if (rem != 0 && ((rem < 0) != (b < 0))) {
        q -= 1;
        rem += b;
    }
    *r = rem;
    return q;
}

static bool timedelta_is_zero(timedelta *t) {
    return !t->days && !t->seconds && !t->microseconds;
}

/* exact arithmetic on timedeltas, without forming their microsecond counts
 * as single integers (these exceed 64 bits for large day counts). the
 * magnitudes are kept as (seconds, microseconds) pairs, which add, subtract
 * and double exactly, and are multiplied and divided in binary. */
struct timedelta_mag {
    long long s, us; /* 0 <= us < 1000000 */
};

static timedelta_mag timedelta_magnitude(timedelta *t, bool *neg) {
    timedelta_mag m = {(long long)t->days * 86400 + t->seconds, (long long)t->microseconds};
    *neg = m.s < 0;
    if(*neg) {
        if(m.us) {
            m.s += 1;
            m.us = 1000000 - m.us;
        }
        m.s = -m.s;
    }
    return m;
}

static bool timedelta_mag_lt(timedelta_mag a, timedelta_mag b) {
    return a.s < b.s || (a.s == b.s && a.us < b.us);
}

static timedelta_mag timedelta_mag_sub(timedelta_mag a, timedelta_mag b) {
    timedelta_mag m = {a.s - b.s, a.us - b.us};
    if(m.us < 0) {
        m.us += 1000000;
        m.s -= 1;
    }
    return m;
}

static timedelta_mag timedelta_mag_add(timedelta_mag a, timedelta_mag b) {
    timedelta_mag m = {a.s + b.s, a.us + b.us};
    if(m.us >= 1000000) {
        m.us -= 1000000;
        m.s += 1;
    }
    return m;
}

/* mult[i] = b * 2**i, up to the first mult[k] > a; returns k. |a| < 2**67
   microseconds and |b| >= 1, so at most 68 doublings */
static int timedelta_mag_multiples(timedelta_mag a, timedelta_mag b, timedelta_mag *mult) {
    int k = 0;
    mult[0] = b;
    while(!timedelta_mag_lt(a, mult[k])) {
        mult[k + 1] = timedelta_mag_add(mult[k], mult[k]);
        k++;
    }
    return k;
}

static timedelta *timedelta_from_magnitude(timedelta_mag m, bool neg) {
    if(neg) {
        if(m.us) {
            m.s += 1;
            m.us = 1000000 - m.us;
        }
        m.s = -m.s;
    }
    long long d = m.s / 86400, s = m.s % 86400;
    if(s < 0) {
        s += 86400;
        d -= 1;
    }
    timedelta *result = new timedelta(0.,0.,0.,0.,0.,0.,0.);
    result->days = (__ss_int)d;
    result->seconds = (__ss_int)s;
    result->microseconds = (__ss_int)m.us;
    return result;
}

/* *q is only computed if q is non-NULL (and raises OverflowError if it does not fit) */
static timedelta *timedelta_divmod(timedelta *a, timedelta *b, __ss_int *q) {
    if(timedelta_is_zero(b))
        throw new ZeroDivisionError(new str("integer division or modulo by zero"));
    bool aneg, bneg;
    timedelta_mag A = timedelta_magnitude(a, &aneg);
    timedelta_mag B = timedelta_magnitude(b, &bneg);
    timedelta_mag mult[70];
    int k = timedelta_mag_multiples(A, B, mult);
    unsigned long long q0 = 0;
    bool overflow = false;
    timedelta_mag R = A;
    for(int i = k - 1; i >= 0; i--) {
        if(!timedelta_mag_lt(R, mult[i])) {
            R = timedelta_mag_sub(R, mult[i]);
            if(i >= 63)
                overflow = true;
            else
                q0 |= 1ULL << i;
        }
    }

    /* python floor semantics: the remainder has the sign of b */
    bool rzero = (R.s == 0 && R.us == 0);
    if(aneg != bneg && !rzero) {
        R = timedelta_mag_sub(B, R);
        q0 += 1;
    }
    if(q) {
        if(overflow || q0 > (unsigned long long)std::numeric_limits<__ss_int>::max())
            throw new OverflowError(new str("Python int too large to convert to C int"));
        *q = (aneg != bneg) ? -(__ss_int)q0 : (__ss_int)q0;
    }
    return timedelta_from_magnitude(R, bneg);
}

/* correctly rounded t / u, like cpython's int / int on the microsecond
   counts: long division as above gives the first 62 significant bits of the
   quotient, and a sticky bit for any rest, so the conversion to double
   rounds only once */
__ss_float timedelta::__truediv__(timedelta *other) {
    if(timedelta_is_zero(other))
        throw new ZeroDivisionError(new str("division by zero"));
    bool aneg, bneg;
    timedelta_mag A = timedelta_magnitude(this, &aneg);
    timedelta_mag B = timedelta_magnitude(other, &bneg);
    long long q = 0;
    int bits = 0, i = -1;
    if(!timedelta_is_zero(this)) {
        timedelta_mag mult[70];
        i = timedelta_mag_multiples(A, B, mult) - 1;
        timedelta_mag R = A;
        for(; bits < 62; i--) {
            timedelta_mag D = mult[0];
            if(i >= 0)
                D = mult[i];
            else
                R = timedelta_mag_add(R, R); /* fractional bits: R < B */
            bool bit = !timedelta_mag_lt(R, D);
            if(bit)
                R = timedelta_mag_sub(R, D);
            if(bits || bit) {
                q = (q << 1) | bit;
                bits++;
            }
        }
        if(R.s || R.us)
            q |= 1;
    }
    __ss_float f = std::ldexp((__ss_float)q, i + 1);
    return (aneg != bneg) ? -f : f;
}

/* as cpython: the days of a product must fit a C int (also keeps the sums in range) */
static const long long timedelta_mul_limit = 2147483648LL * 86400;

static void timedelta_mul_check(timedelta_mag D) {
    if(D.s >= timedelta_mul_limit)
        throw new OverflowError(new str("Python int too large to convert to C int"));
}

/* Q = floor(D * 2**k / m), and *rem the remainder, for k >= 0 and
   1 <= m <= 2**63, by binary long division of the 128 bits of D * 2**k (as
   hi * 2**64 + lo). D < 2**68 microseconds, so this needs no wider type; the
   remainder stays below m, so doubling it does not overflow. */
static timedelta_mag timedelta_mag_div(timedelta_mag D, unsigned long long m, long k, unsigned long long *rem) {
    timedelta_mag Q = {0, 0};
    /* the bits of D = s * 1000000 + us (< 2**68), as hi * 2**64 + lo */
    unsigned long long s = (unsigned long long)D.s;
    unsigned long long lo = (s & 0xffffffffULL) * 1000000ULL + (unsigned long long)D.us;
    unsigned long long mid = (s >> 32) * 1000000ULL;
    unsigned long long lo2 = lo + (mid << 32);
    unsigned long long hi = (mid >> 32) + (lo2 < lo);
    lo = lo2;
    unsigned long long R = 0;
    long nbits = 128 + (k > 0 ? k : 0);
    for(long i = 0; i < nbits; i++) {
        unsigned long long bit = 0;
        if(i < 64)
            bit = (hi >> (63 - i)) & 1;
        else if(i < 128)
            bit = (lo >> (127 - i)) & 1;
        R = (R << 1) | bit;
        timedelta_mul_check(Q);
        Q = timedelta_mag_add(Q, Q);
        if(R >= m) {
            R -= m;
            timedelta_mag one = {0, 1};
            Q = timedelta_mag_add(Q, one);
        }
    }
    *rem = R;
    return Q;
}

/* t // n and t / n (rounded half to even), exact (for n that fits 64 bits) */
static timedelta *timedelta_div_int(timedelta *t, __ss_int n, bool round) {
    if(n == 0)
        throw new ZeroDivisionError(new str("integer division or modulo by zero"));
    bool neg;
    timedelta_mag D = timedelta_magnitude(t, &neg);
    unsigned long long m = n < 0 ? -(unsigned long long)n : (unsigned long long)n;
    if(n < 0)
        neg = !neg;
    unsigned long long R;
    timedelta_mag Q;
    if(m < (1ULL << 43)) { /* the common case: R * 1000000 + us fits 64 bits */
        unsigned long long s = (unsigned long long)D.s;
        unsigned long long x = (s % m) * 1000000 + (unsigned long long)D.us;
        Q.s = (long long)(s / m);
        Q.us = (long long)(x / m); /* < 1000000, as x < m * 1000000 */
        R = x % m;
    } else
        Q = timedelta_mag_div(D, m, 0, &R);
    /* R < m <= 2**63, so 2 * R does not overflow */
    if(round ? (2 * R > m || (2 * R == m && (Q.us & 1))) : (neg && R)) { /* floor of a negative quotient: away from zero */
        timedelta_mag one = {0, 1};
        Q = timedelta_mag_add(Q, one);
    }
    return timedelta_from_magnitude(Q, neg && (Q.s || Q.us));
}

timedelta *timedelta::__truediv__(__ss_int n) {
    return timedelta_div_int(this, n, true);
}

timedelta *timedelta::__floordiv__(__ss_int n) {
    return timedelta_div_int(this, n, false);
}

/* D * m, exact, by double-and-add (checked along the way) */
static timedelta_mag timedelta_mag_mul(timedelta_mag D, unsigned long long m) {
    timedelta_mag R = {0, 0};
    for(; m; m >>= 1) {
        timedelta_mul_check(D);
        if(m & 1)
            R = timedelta_mag_add(R, D);
        D = timedelta_mag_add(D, D);
    }
    timedelta_mul_check(R);
    return R;
}

timedelta *timedelta::__mul__(__ss_int n) {
    /* exact. as cpython: days must fit a C int, and then the timedelta range */
    bool neg;
    timedelta_mag D = timedelta_magnitude(this, &neg);
    unsigned long long m = n < 0 ? -(unsigned long long)n : (unsigned long long)n;
    if(n < 0)
        neg = !neg;
    timedelta *result = timedelta_from_magnitude(timedelta_mag_mul(D, m), neg);
    timedelta_check_days(result->days);
    return result;
}

/* f = m / 2**k, with m odd (f finite and non-zero) */
static unsigned long long timedelta_float_ratio(__ss_float f, int *k) {
    int e;
    unsigned long long m = (unsigned long long)std::ldexp(std::frexp(std::fabs(f), &e), 53);
    *k = 53 - e;
    for(; !(m & 1); m >>= 1)
        (*k)--;
    return m;
}

/* halve R n times, keeping the last bit halved off in *half, and whether any
   other (non-zero) bits were, in *sticky */
static timedelta_mag timedelta_mag_halve(timedelta_mag R, long n, bool *half, bool *sticky) {
    for(; n > 0; n--) {
        *sticky = *sticky || *half;
        if(!R.s && !R.us) { /* only zero bits are left */
            *half = false;
            break;
        }
        *half = R.us & 1; /* 1000000 is even */
        if(R.s & 1)
            R.us += 1000000;
        R.s >>= 1;
        R.us >>= 1;
    }
    return R;
}

static timedelta_mag timedelta_mag_round(timedelta_mag R, bool half, bool sticky) {
    if(half && (sticky || (R.us & 1))) {
        timedelta_mag one = {0, 1};
        R = timedelta_mag_add(R, one);
    }
    return R;
}

timedelta *timedelta::__mul__(__ss_float f) {
    /* exact, like cpython, which multiplies the microseconds by the integer
       ratio of f and rounds half to even. with f = m / 2**k, the integer part
       of m / 2**k is handled as above, and the fractional part bit by bit
       from the lowest bit, halving the accumulator each time (so it stays
       below the magnitude). as in long division, the last bit halved off,
       and whether any other bits were, decide the rounding. */
    timedelta_check_ratio(f);
    bool neg;
    timedelta_mag D = timedelta_magnitude(this, &neg);
    if(std::signbit(f))
        neg = !neg;
    timedelta_mag R = {0, 0};
    if(f != 0.0 && (D.s || D.us)) {
        int k;
        unsigned long long m = timedelta_float_ratio(f, &k);
        for(; k < 0; k++) { /* f is an integer >= 2**53 */
            timedelta_mul_check(D);
            D = timedelta_mag_add(D, D);
        }
        timedelta_mag acc = {0, 0};
        bool half = false, sticky = false;
        for(int i = 0; i < k && i < 53; i++) {
            if((m >> i) & 1)
                acc = timedelta_mag_add(acc, D);
            acc = timedelta_mag_halve(acc, 1, &half, &sticky);
        }
        if(k > 53)
            acc = timedelta_mag_halve(acc, k - 53, &half, &sticky);
        R = timedelta_mag_add(timedelta_mag_mul(D, k < 53 ? m >> k : 0), acc);
        R = timedelta_mag_round(R, half, sticky);
        timedelta_mul_check(R);
    }
    timedelta *result = timedelta_from_magnitude(R, neg && (R.s || R.us));
    timedelta_check_days(result->days);
    return result;
}

timedelta *timedelta::__truediv__(__ss_float f) {
    /* exact, like cpython, which multiplies the microseconds by the integer
       ratio of 1/f and rounds half to even. with f = m / 2**k, this is binary
       long division of D * 2**k by m, where the remainder stays below m (so
       below 2**53). for k < 0, the quotient is halved -k times afterwards. */
    timedelta_check_ratio(f);
    if(f == 0.0)
        throw new ZeroDivisionError(new str("integer division or modulo by zero"));
    bool neg;
    timedelta_mag D = timedelta_magnitude(this, &neg);
    if(std::signbit(f))
        neg = !neg;
    timedelta_mag Q = {0, 0};
    if(D.s || D.us) {
        int k;
        unsigned long long m = timedelta_float_ratio(f, &k);
        unsigned long long R;
        Q = timedelta_mag_div(D, m, k > 0 ? k : 0, &R);
        if(k >= 0) {
            if(2 * R > m) { /* m is odd, so there are no ties */
                timedelta_mag one = {0, 1};
                Q = timedelta_mag_add(Q, one);
            }
        } else {
            bool half = false, sticky = R != 0;
            Q = timedelta_mag_halve(Q, -(long)k, &half, &sticky);
            Q = timedelta_mag_round(Q, half, sticky);
        }
        timedelta_mul_check(Q);
    }
    timedelta *result = timedelta_from_magnitude(Q, neg && (Q.s || Q.us));
    timedelta_check_days(result->days);
    return result;
}

__ss_int timedelta::__floordiv__(timedelta *other) {
    __ss_int q;
    timedelta_divmod(this, other, &q);
    return q;
}

timedelta *timedelta::__mod__(timedelta *other) {
    if(timedelta_is_zero(other))
        throw new ZeroDivisionError(new str("integer modulo by zero"));
    return timedelta_divmod(this, other, NULL);
}

tuple2<__ss_int, timedelta *> *timedelta::__divmod__(timedelta *other) {
    __ss_int q;
    timedelta *r = timedelta_divmod(this, other, &q);
    return new tuple2<__ss_int, timedelta *>(2, q, r);
}

timedelta *timedelta::__neg__() {
    return new timedelta((double)-days, (double)-seconds, (double)-microseconds,0,0,0,0);
}

timedelta *timedelta::__pos__() {
    return new timedelta(this);
}

timedelta *timedelta::__abs__() {
    if(days>=0)
        return new timedelta(this);
    else
        return __neg__();
}

__ss_float timedelta::total_seconds() {
    /* as cpython, the microseconds divided by 10**6, correctly rounded: summing
       the parts in floating point cancels (timedelta(microseconds=-1) is
       -1 day, 86399.999999 seconds), and above 2**53 microseconds a double
       of the total would round twice */
    timedelta one_second(0, 1);
    return __truediv__(&one_second);
}

__ss_int timedelta::__cmp__(timedelta *other) {
    if ((days == other->days) && (seconds == other->seconds) && (microseconds == other->microseconds))
        return 0;
    int64_t s = (int64_t)days * 24 * 3600 + seconds;
    int64_t os = (int64_t)other->days * 24 * 3600 + other->seconds;
    if (s > os)
        return 1;
    if ((s == os) && (microseconds > other->microseconds))
        return 1;
    return -1;
}

__ss_bool timedelta::__eq__(timedelta *other) { return __mbool(__cmp__(other) == 0); }

str *timedelta::__repr__() {
    /* cpython (>= 3.7): keyword form, zero fields omitted, '0' if all zero */
    list<str *> *args = new list<str *>();
    if(days != 0)
        args->append(__mod6(repr_days_format, 1, days));
    if(seconds != 0)
        args->append(__mod6(repr_seconds_format, 1, seconds));
    if(microseconds != 0)
        args->append(__mod6(repr_microseconds_format, 1, microseconds));
    if(args->__len__() == 0)
        args->append(zero_string);
    return __add_strs(3, new str("datetime.timedelta("), comma_space_string->join(args), close_paren_string);
}

__ss_int timedelta::__hash__() {
    return hash_combine(hash_combine(days, seconds), microseconds);
}
__ss_bool timedelta::__ne__(timedelta *other) { return __mbool(__cmp__(other) != 0); }
__ss_bool timedelta::__gt__(timedelta *other) { return __mbool(__cmp__(other) == 1); }
__ss_bool timedelta::__lt__(timedelta *other) { return __mbool(__cmp__(other) == -1); }
__ss_bool timedelta::__ge__(timedelta *other) { return __mbool(__cmp__(other) != -1); }
__ss_bool timedelta::__le__(timedelta *other) { return __mbool(__cmp__(other) != 1); }


/*functions taken and modified from cpython, to be copied to datetime.cpp later*/


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
