/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef SS_SITESTATS_HPP
#define SS_SITESTATS_HPP

#include <algorithm>
#include <cmath>
#include <cstddef>

/* Running (sum, n) average of observed sizes at a call site, plus an
 * online (Welford/West) weighted variance accumulator (mean, m2).
 * The variance fields are updated alongside sum/n but not yet consulted
 * by __list_site_hint() below -- this is purely to measure whether
 * maintaining them costs anything before we start using them. */
struct ListSiteStat {
    double sum = 0.0; // TODO move to double, or start losing precision
    double n = 0.0;
    double mean = 0.0;
    double m2 = 0.0;   // sum of weighted squared deviations from mean
};

inline void __list_site_update(ListSiteStat &s, double x, double y=1.0) {
//    printf("list update x=%f, y=%f\n", x, y);

    double weight = (s.n == 0.0) ? 1.0 : y;

    s.sum += x;
    s.n += weight;

    // Welford/West online update of (mean, m2); variance == m2 / n.
    double delta = x - s.mean;
    s.mean += delta * weight / s.n;
    s.m2 += weight * delta * (x - s.mean);
//    printf("update sum=%f, n=%f, mean=%f, m2=%f\n", s.sum, s.n, s.mean, s.m2);
}

constexpr double __ss_site_cushion = 6.0;

inline std::size_t __list_site_hint(ListSiteStat &s) {
    if (s.n <= 0.0) {
//        printf("hint %d\n", __ss_site_cushion);
        return (std::size_t)__ss_site_cushion;
    }
    double avg = s.sum / s.n;
    double dev = std::sqrt(s.m2 / s.n);
//    printf("stddev %f\n", dev);
//    printf("hint %d\n", (std::size_t)std::max(0.0, avg - dev));
    return (std::size_t)std::max(0.0, avg - dev);
}

#endif
