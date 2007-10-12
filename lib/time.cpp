#include "time.hpp"

namespace __time__ {

clock_t start;

double clock() {
    return ((double) (std::clock()-start)) / CLOCKS_PER_SEC;
}

#ifdef WIN32
struct  timezone {
    int     tz_minuteswest;
    int     tz_dsttime;
};

static int gettimeofday (struct timeval *tv, struct timezone *tz)
{
   struct _timeb tb;

   if (!tv)
      return (-1);

  _ftime (&tb);
  tv->tv_sec  = tb.time;
  tv->tv_usec = tb.millitm * 1000 + 500;
  if (tz)
  {
    tz->tz_minuteswest = -60 * _timezone;
    tz->tz_dsttime = _daylight;
  }
  return (0);
}
#endif

double time() {
    timeval tim;
    gettimeofday(&tim, 0);
    return tim.tv_sec+tim.tv_usec/1000000.0;
}

void sleep(double s) {
    timeval tim;
    double t1, t2;

    gettimeofday(&tim, 0);
    t1=tim.tv_sec+(tim.tv_usec/1000000.0);
    do {
        gettimeofday(&tim, 0);
        t2=tim.tv_sec+(tim.tv_usec/1000000.0);
    } while (t2-t1 < s);

}

void __init() {
    start = std::clock();
}


} // module namespace
