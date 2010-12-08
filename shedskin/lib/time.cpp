#include "time.hpp"
#include "time.h"
#include <climits>

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
#ifdef WIN32
__ss_int gettimeofday (struct timeval *tv, struct __ss_timezone *tz)
{
   struct _timeb tb;

   if (!tv)
      return -1;

  _ftime (&tb);
  tv->tv_sec  = (long) tb.time;
  tv->tv_usec = tb.millitm * 1000 + 500;
  if (tz)
  {
    tz->tz_minuteswest = -60 * _timezone;
    tz->tz_dsttime = _daylight;
  }
  return 0;
}
#endif

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

    return __modct(const_1, 9, ___box(this->tm_year), ___box(this->tm_mon), ___box(this->tm_mday), ___box(this->tm_hour), ___box(this->tm_min), ___box(this->tm_sec), ___box(this->tm_wday), ___box(this->tm_yday), ___box(this->tm_isdst));
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
#else
// TOFIX
void *sleep(double s) {
    return NULL;
    }
#endif

double mktime(struct_time *tuple) {
    return (double)::mktime(tuple2tm(tuple));
}

double mktime(tuple2<__ss_int, __ss_int> *tuple) {
    struct_time *st;
    try {
        st = new struct_time(tuple);
    } catch(...) {
        throw;
    }
    return (double)::mktime(tuple2tm(st));
}

struct_time *localtime() {
    time_t time = ::time(NULL);
    return localtime((double)time);
}

struct_time *localtime(const double timep) {
    time_t timet = static_cast<time_t>(timep);
    tm *tm_time = ::localtime(&timet);
    return tm2tuple(tm_time);
}

struct_time *gmtime() {
    time_t time = ::time(NULL);
    return gmtime((double)time);
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

#ifdef WIN32

/******************************************************************************
 * STRPTIME FOR WINDOWS
 *****************************************************************************/

/*	$NetBSD: strptime.c,v 1.35 2009/12/14 20:45:02 matt Exp $	*/

/*-
 * Copyright (c) 1997, 1998, 2005, 2008 The NetBSD Foundation, Inc.
 * All rights reserved.
 *
 * This code was contributed to The NetBSD Foundation by Klaus Klein.
 * Heavily optimised by David Laight
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE NETBSD FOUNDATION, INC. AND CONTRIBUTORS
 * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 * TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION OR CONTRIBUTORS
 * BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */
 
/* Original code modified to work with MSVC May 2010 with help from
 http://www.opensource.apple.com/source/gdb/gdb-282/src/tcl/compat/strftime.c
*/

#include <ctype.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

typedef struct {
    const char *abday[7];
    const char *day[7];
    const char *abmon[12];
    const char *mon[12];
    const char *am_pm[2];
    const char *d_t_fmt;
    const char *d_fmt;
    const char *t_fmt;
    const char *t_fmt_ampm;
} _TimeLocale;

/*
 * This is the C locale default.  On Windows, if we wanted to make this
 * localized, we would use GetLocaleInfo to get the correct values.
 * It may be acceptable to do localization of month/day names, as the
 * numerical values would be considered the locale-independent versions.
 */
static const _TimeLocale _DefaultTimeLocale =
{
    {
	"Sun","Mon","Tue","Wed","Thu","Fri","Sat",
    },
    {
	"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
	"Friday", "Saturday"
    },
    {
	"Jan", "Feb", "Mar", "Apr", "May", "Jun",
	"Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    },
    {
	"January", "February", "March", "April", "May", "June", "July",
	"August", "September", "October", "November", "December"
    },
    {
	"AM", "PM"
    },
    "%a %b %d %H:%M:%S %Y",
    "%m/%d/%y",
    "%H:%M:%S",
    "%I:%M:%S %p"
};

static const _TimeLocale *_CurrentTimeLocale = &_DefaultTimeLocale;
#define TM_YEAR_BASE   1900
#define IsLeapYear(x)   ((x % 4 == 0) && (x % 100 != 0 || x % 400 == 0))

#define	_ctloc(x)		(_CurrentTimeLocale->x)

#define u_char unsigned char
#define uint unsigned int
#define __UNCONST

/*
 * We do not implement alternate representations. However, we always
 * check whether a given modifier is allowed for a certain conversion.
 */
#define ALT_E			0x01
#define ALT_O			0x02
#define	LEGAL_ALT(x)		{ if (alt_format & ~(x)) return NULL; }

static char gmt[] = { "GMT" };
static char utc[] = { "UTC" };
/* RFC-822/RFC-2822 */
static const char * const nast[5] = {
       "EST",    "CST",    "MST",    "PST",    "\0\0\0"
};
static const char * const nadt[5] = {
       "EDT",    "CDT",    "MDT",    "PDT",    "\0\0\0"
};

static const u_char *conv_num(const unsigned char *, int *, uint, uint);
static const u_char *find_string(const u_char *, int *, const char * const *,
	const char * const *, int);


char *
strptime(const char *buf, const char *fmt, struct tm *tm)
{
	unsigned char c;
	const unsigned char *bp, *ep;
	int alt_format, i, split_year = 0, neg = 0, offs;
	const char *new_fmt;

	bp = (const u_char *)buf;

	while (bp != NULL && (c = *fmt++) != '\0') {
		/* Clear `alternate' modifier prior to new conversion. */
		alt_format = 0;
		i = 0;

		/* Eat up white-space. */
		if (isspace(c)) {
			while (isspace(*bp))
				bp++;
			continue;
		}

		if (c != '%')
			goto literal;


again:		switch (c = *fmt++) {
		case '%':	/* "%%" is converted to "%". */
literal:
			if (c != *bp++)
				return NULL;
			LEGAL_ALT(0);
			continue;

		/*
		 * "Alternative" modifiers. Just set the appropriate flag
		 * and start over again.
		 */
		case 'E':	/* "%E?" alternative conversion modifier. */
			LEGAL_ALT(0);
			alt_format |= ALT_E;
			goto again;

		case 'O':	/* "%O?" alternative conversion modifier. */
			LEGAL_ALT(0);
			alt_format |= ALT_O;
			goto again;

		/*
		 * "Complex" conversion rules, implemented through recursion.
		 */
		case 'c':	/* Date and time, using the locale's format. */
			new_fmt = _ctloc(d_t_fmt);
			goto recurse;

		case 'D':	/* The date as "%m/%d/%y". */
			new_fmt = "%m/%d/%y";
			LEGAL_ALT(0);
			goto recurse;

		case 'F':	/* The date as "%Y-%m-%d". */
			new_fmt = "%Y-%m-%d";
			LEGAL_ALT(0);
			goto recurse;

		case 'R':	/* The time as "%H:%M". */
			new_fmt = "%H:%M";
			LEGAL_ALT(0);
			goto recurse;

		case 'r':	/* The time in 12-hour clock representation. */
			new_fmt =_ctloc(t_fmt_ampm);
			LEGAL_ALT(0);
			goto recurse;

		case 'T':	/* The time as "%H:%M:%S". */
			new_fmt = "%H:%M:%S";
			LEGAL_ALT(0);
			goto recurse;

		case 'X':	/* The time, using the locale's format. */
			new_fmt =_ctloc(t_fmt);
			goto recurse;

		case 'x':	/* The date, using the locale's format. */
			new_fmt =_ctloc(d_fmt);
		    recurse:
			bp = (const u_char *)strptime((const char *)bp,
							    new_fmt, tm);
			LEGAL_ALT(ALT_E);
			continue;

		/*
		 * "Elementary" conversion rules.
		 */
		case 'A':	/* The day of week, using the locale's form. */
		case 'a':
			bp = find_string(bp, &tm->tm_wday, _ctloc(day),
					_ctloc(abday), 7);
			LEGAL_ALT(0);
			continue;

		case 'B':	/* The month, using the locale's form. */
		case 'b':
		case 'h':
			bp = find_string(bp, &tm->tm_mon, _ctloc(mon),
					_ctloc(abmon), 12);
			LEGAL_ALT(0);
			continue;

		case 'C':	/* The century number. */
			i = 20;
			bp = conv_num(bp, &i, 0, 99);

			i = i * 100 - TM_YEAR_BASE;
			if (split_year)
				i += tm->tm_year % 100;
			split_year = 1;
			tm->tm_year = i;
			LEGAL_ALT(ALT_E);
			continue;

		case 'd':	/* The day of month. */
		case 'e':
			bp = conv_num(bp, &tm->tm_mday, 1, 31);
			LEGAL_ALT(ALT_O);
			continue;

		case 'k':	/* The hour (24-hour clock representation). */
			LEGAL_ALT(0);
			/* FALLTHROUGH */
		case 'H':
			bp = conv_num(bp, &tm->tm_hour, 0, 23);
			LEGAL_ALT(ALT_O);
			continue;

		case 'l':	/* The hour (12-hour clock representation). */
			LEGAL_ALT(0);
			/* FALLTHROUGH */
		case 'I':
			bp = conv_num(bp, &tm->tm_hour, 1, 12);
			if (tm->tm_hour == 12)
				tm->tm_hour = 0;
			LEGAL_ALT(ALT_O);
			continue;

		case 'j':	/* The day of year. */
			i = 1;
			bp = conv_num(bp, &i, 1, 366);
			tm->tm_yday = i - 1;
			LEGAL_ALT(0);
			continue;

		case 'M':	/* The minute. */
			bp = conv_num(bp, &tm->tm_min, 0, 59);
			LEGAL_ALT(ALT_O);
			continue;

		case 'm':	/* The month. */
			i = 1;
			bp = conv_num(bp, &i, 1, 12);
			tm->tm_mon = i - 1;
			LEGAL_ALT(ALT_O);
			continue;

		case 'p':	/* The locale's equivalent of AM/PM. */
			bp = find_string(bp, &i, _ctloc(am_pm), NULL, 2);
			if (tm->tm_hour > 11)
				return NULL;
			tm->tm_hour += i * 12;
			LEGAL_ALT(0);
			continue;

		case 'S':	/* The seconds. */
			bp = conv_num(bp, &tm->tm_sec, 0, 61);
			LEGAL_ALT(ALT_O);
			continue;

		case 's':	/* seconds since the epoch */
			{
				time_t sse = 0;
				uint64_t rulim = LLONG_MAX;
                struct tm *tm2;

				if (*bp < '0' || *bp > '9') {
					bp = NULL;
					continue;
				}

				do {
					sse *= 10;
					sse += *bp++ - '0';
					rulim /= 10;
				} while ((sse * 10 <= LLONG_MAX) &&
					 rulim && *bp >= '0' && *bp <= '9');

				if (sse < 0 || (uint64_t)sse > LLONG_MAX) {
					bp = NULL;
					continue;
				}

				if ((tm2 = ::localtime(&sse)) == NULL)
					bp = NULL;
                else
                    *tm = *tm2;
			}
			continue;

		case 'U':	/* The week of year, beginning on sunday. */
		case 'W':	/* The week of year, beginning on monday. */
			/*
			 * XXX This is bogus, as we can not assume any valid
			 * information present in the tm structure at this
			 * point to calculate a real value, so just check the
			 * range for now.
			 */
			 bp = conv_num(bp, &i, 0, 53);
			 LEGAL_ALT(ALT_O);
			 continue;

		case 'w':	/* The day of week, beginning on sunday. */
			bp = conv_num(bp, &tm->tm_wday, 0, 6);
			LEGAL_ALT(ALT_O);
			continue;

		case 'u':	/* The day of week, monday = 1. */
			bp = conv_num(bp, &i, 1, 7);
			tm->tm_wday = i % 7;
			LEGAL_ALT(ALT_O);
			continue;

		case 'g':	/* The year corresponding to the ISO week
				 * number but without the century.
				 */
			bp = conv_num(bp, &i, 0, 99);
			continue;

		case 'G':	/* The year corresponding to the ISO week
				 * number with century.
				 */
			do
				bp++;
			while (isdigit(*bp));
			continue;

		case 'V':	/* The ISO 8601:1988 week number as decimal */
			bp = conv_num(bp, &i, 0, 53);
			continue;

		case 'Y':	/* The year. */
			i = TM_YEAR_BASE;	/* just for data sanity... */
			bp = conv_num(bp, &i, 0, 9999);
			tm->tm_year = i - TM_YEAR_BASE;
			LEGAL_ALT(ALT_E);
			continue;

		case 'y':	/* The year within 100 years of the epoch. */
			/* LEGAL_ALT(ALT_E | ALT_O); */
			bp = conv_num(bp, &i, 0, 99);

			if (split_year)
				/* preserve century */
				i += (tm->tm_year / 100) * 100;
			else {
				split_year = 1;
				if (i <= 68)
					i = i + 2000 - TM_YEAR_BASE;
				else
					i = i + 1900 - TM_YEAR_BASE;
			}
			tm->tm_year = i;
			continue;

		case 'Z':
			tzset();
			if (strncmp((const char *)bp, gmt, 3) == 0) {
				tm->tm_isdst = 0;
#ifdef TM_GMTOFF
				tm->TM_GMTOFF = 0;
#endif
#ifdef TM_ZONE
				tm->TM_ZONE = gmt;
#endif
				bp += 3;
			} else {
				ep = find_string(bp, &i,
					       	 (const char * const *)tzname,
					       	  NULL, 2);
				if (ep != NULL) {
					tm->tm_isdst = i;
#ifdef TM_GMTOFF
					tm->TM_GMTOFF = -(timezone);
#endif
#ifdef TM_ZONE
					tm->TM_ZONE = tzname[i];
#endif
				}
				bp = ep;
			}
			continue;

		case 'z':
			/*
			 * We recognize all ISO 8601 formats:
			 * Z	= Zulu time/UTC
			 * [+-]hhmm
			 * [+-]hh:mm
			 * [+-]hh
			 * We recognize all RFC-822/RFC-2822 formats:
			 * UT|GMT
			 *          North American : UTC offsets
			 * E[DS]T = Eastern : -4 | -5
			 * C[DS]T = Central : -5 | -6
			 * M[DS]T = Mountain: -6 | -7
			 * P[DS]T = Pacific : -7 | -8
			 *          Military
			 * [A-IL-M] = -1 ... -9 (J not used)
			 * [N-Y]  = +1 ... +12
			 */
			while (isspace(*bp))
				bp++;

			switch (*bp++) {
			case 'G':
				if (*bp++ != 'M')
					return NULL;
				/*FALLTHROUGH*/
			case 'U':
				if (*bp++ != 'T')
					return NULL;
				/*FALLTHROUGH*/
			case 'Z':
				tm->tm_isdst = 0;
#ifdef TM_GMTOFF
				tm->TM_GMTOFF = 0;
#endif
#ifdef TM_ZONE
				tm->TM_ZONE = utc;
#endif
				continue;
			case '+':
				neg = 0;
				break;
			case '-':
				neg = 1;
				break;
			default:
				--bp;
				ep = find_string(bp, &i, nast, NULL, 4);
				if (ep != NULL) {
#ifdef TM_GMTOFF
					tm->TM_GMTOFF = -5 - i;
#endif
#ifdef TM_ZONE
					tm->TM_ZONE = __UNCONST(nast[i]);
#endif
					bp = ep;
					continue;
				}
				ep = find_string(bp, &i, nadt, NULL, 4);
				if (ep != NULL) {
					tm->tm_isdst = 1;
#ifdef TM_GMTOFF
					tm->TM_GMTOFF = -4 - i;
#endif
#ifdef TM_ZONE
					tm->TM_ZONE = __UNCONST(nadt[i]);
#endif
					bp = ep;
					continue;
				}

				if ((*bp >= 'A' && *bp <= 'I') ||
				    (*bp >= 'L' && *bp <= 'Y')) {
#ifdef TM_GMTOFF
					/* Argh! No 'J'! */
					if (*bp >= 'A' && *bp <= 'I')
						tm->TM_GMTOFF =
						    ('A' - 1) - (int)*bp;
					else if (*bp >= 'L' && *bp <= 'M')
						tm->TM_GMTOFF = 'A' - (int)*bp;
					else if (*bp >= 'N' && *bp <= 'Y')
						tm->TM_GMTOFF = (int)*bp - 'M';
#endif
#ifdef TM_ZONE
					tm->TM_ZONE = NULL; /* XXX */
#endif
					bp++;
					continue;
				}
				return NULL;
			}
			offs = 0;
			for (i = 0; i < 4; ) {
				if (isdigit(*bp)) {
					offs = offs * 10 + (*bp++ - '0');
					i++;
					continue;
				}
				if (i == 2 && *bp == ':') {
					bp++;
					continue;
				}
				break;
			}
			switch (i) {
			case 2:
				offs *= 100;
				break;
			case 4:
				i = offs % 100;
				if (i >= 60)
					return NULL;
				/* Convert minutes into decimal */
				offs = (offs / 100) * 100 + (i * 50) / 30;
				break;
			default:
				return NULL;
			}
			if (neg)
				offs = -offs;
			tm->tm_isdst = 0;	/* XXX */
#ifdef TM_GMTOFF
			tm->TM_GMTOFF = offs;
#endif
#ifdef TM_ZONE
			tm->TM_ZONE = NULL;	/* XXX */
#endif
			continue;

		/*
		 * Miscellaneous conversions.
		 */
		case 'n':	/* Any kind of white-space. */
		case 't':
			while (isspace(*bp))
				bp++;
			LEGAL_ALT(0);
			continue;


		default:	/* Unknown/unsupported conversion. */
			return NULL;
		}
	}

	return (char *)(bp);
}


static const u_char *
conv_num(const unsigned char *buf, int *dest, uint llim, uint ulim)
{
	uint result = 0;
	unsigned char ch;

	/* The limit also determines the number of valid digits. */
	uint rulim = ulim;

	ch = *buf;
	if (ch < '0' || ch > '9')
		return NULL;

	do {
		result *= 10;
		result += ch - '0';
		rulim /= 10;
		ch = *++buf;
	} while ((result * 10 <= ulim) && rulim && ch >= '0' && ch <= '9');

	if (result < llim || result > ulim)
		return NULL;

	*dest = result;
	return buf;
}

int strncasecmp(char *s1, char *s2, size_t n)
{
    if (n == 0)
        return 0;

    while (n-- != 0 && tolower(*s1) == tolower(*s2))
    {
        if (n == 0 || *s1 == '\0' || *s2 == '\0')
            break;
        s1++;
        s2++;
    }

    return tolower(*(unsigned char *) s1) - tolower(*(unsigned char *) s2);
}

static const u_char *
find_string(const u_char *bp, int *tgt, const char * const *n1,
		const char * const *n2, int c)
{
	int i;
	unsigned int len;

	/* check full name - then abbreviated ones */
	for (; n1 != NULL; n1 = n2, n2 = NULL) {
		for (i = 0; i < c; i++, n1++) {
			len = strlen(*n1);
			if (strncasecmp((char *)*n1, (char *)bp, len) == 0) {
				*tgt = i;
				return bp + len;
			}
		}
	}

	/* Nothing matched */
	return NULL;
}

/******************************************************************************
 * END OF STRPTIME FOR WINDOWS
 *****************************************************************************/

#endif 

struct_time *strptime(str *string, str *format) {
    tm time_tuple = {0, 0, 0, 1, 0, 0, 0, 1, -1};
#ifdef WIN32
    /* XXX check if newer MinGW supports this */
    if(!strptime(string->unit.c_str(), format->unit.c_str(), &time_tuple))
        throw  new ValueError(new str("time data did not match format:  data="+string->unit+" fmt="+format->unit));
#else
    if(!::strptime(string->unit.c_str(), format->unit.c_str(), &time_tuple))
        throw  new ValueError(new str("time data did not match format:  data="+string->unit+" fmt="+format->unit));
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
