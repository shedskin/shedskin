/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef SS_SITESTATS_HPP
#define SS_SITESTATS_HPP

#include <algorithm>
#include <cstddef>

/* Per-call-site backing-buffer size class, adapted online from
 * list.append() grow events.
 *
 * current_class is the reserve() size handed to new lists created at
 * this site. Every __ss_site_window list instances constructed at
 * this site (one "sample" = one list instance, not one append()
 * call), we look at what fraction of them overflowed current_class
 * at least once ("sufficiency" = 1 - that fraction) and adjust:
 *
 *   - sufficiency < __ss_site_low_thresh  -> double the class
 *     (too many reallocations; react fast, this is the expensive
 *     direction to get wrong)
 *   - sufficiency > __ss_site_high_thresh -> attempt to halve the
 *     class (comfortably oversized; shrink cautiously -- this is a
 *     blind guess, since we have no signal on *how* oversized we
 *     are). Setting the threshold close to 1.0 only makes attempts
 *     rarer, not oscillation-free: a class sitting just above the
 *     site's actual maximum can read sufficiency == 1.0 indefinitely
 *     and still be the wrong class to halve down from, so on its own
 *     this threshold cannot prevent a halve/re-promote cycle from
 *     repeating forever. What actually damps that cycle is the
 *     exponential backoff below, not this threshold value.
 *   - otherwise leave current_class alone (dead zone between the
 *     two thresholds; this only helps when sufficiency is genuinely
 *     borderline near one of the two cutoffs -- it does nothing for
 *     the "confidently 100% sufficient but still the wrong class"
 *     case above, which is what the backoff is for)
 *
 * Note on what this converges to: because promotion targets driving
 * sufficiency toward ~100%, the class this settles on tracks the
 * *tail* of the site's size distribution (its practical maximum),
 * not a "typical" size such as the mean or median -- for a narrow,
 * sharply-bounded distribution the two can coincide, but for
 * anything with a long tail (e.g. a normal distribution) the class
 * ends up several standard deviations above the mean, comfortably
 * oversized for the common case.
 *
 * Only the *first* overflow of a given list instance is counted.
 * Once a list has grown past current_class once, std::vector's own
 * geometric growth takes over and keeps re-triggering the "size ==
 * capacity" check on every subsequent doubling -- that says something
 * about how large the list eventually got, not about whether our
 * class choice was right, so counting those further events would
 * mostly measure list size instead of class sufficiency and drown
 * out the signal we actually want. Each list instance therefore
 * contributes at most one grow event, gated by a per-instance flag.
 */
struct ListSiteStat {
    std::size_t current_class = 4;
    unsigned samples = 0;         // list instances constructed this window
    unsigned grow_events = 0;     // of those, how many overflowed current_class
    unsigned demote_backoff = 0;  // exponential backoff level for halving attempts
    unsigned demote_cooldown = 0; // windows left to wait before next halve attempt
    bool demote_pending = false;  // true right after a halve, until its outcome is known
};

constexpr std::size_t __ss_site_min_class = 4;
constexpr std::size_t __ss_site_max_class = std::size_t(1) << 24; // sanity ceiling

constexpr unsigned __ss_site_window = 1000; // list instances per decision window

constexpr double __ss_site_low_thresh = 0.80;  // sufficiency below this -> double
constexpr double __ss_site_high_thresh = 0.98; // sufficiency above this -> halve

/* Call once per list instance constructed at this site (after
 * reserve()'ing at the current class). Counts the sample and, every
 * __ss_site_window samples, reclassifies.
 *
 * Promotion is never blocked -- an insufficient class is expensive
 * (real reallocations happening right now), so react immediately.
 *
 * Demotion is protected by exponential backoff: a halve that gets
 * immediately reversed next window (sufficiency dropping below
 * __ss_site_low_thresh right away) means the site is genuinely near
 * its true size and "100% sufficient" was not a sign of waste --
 * so each such failure doubles how long we wait before trying to
 * halve again. A halve that survives a window (lands in the dead
 * zone) is treated as confirmed good and resets the backoff, so a
 * later shift in the workload can still shrink the class again. */
inline void __list_site_new(ListSiteStat &s) {
    s.samples++;

    if (s.samples < __ss_site_window) {
        return;
    }

    double sufficiency = 1.0 - (double)s.grow_events / (double)s.samples;

    if (sufficiency < __ss_site_low_thresh) {
        if (s.demote_pending) {
            // the halve we just tried was wrong; back off harder next time
            s.demote_backoff = (s.demote_backoff == 0) ? 1 : s.demote_backoff * 2;
            s.demote_pending = false;
        }
        s.current_class = std::min(s.current_class * 2, __ss_site_max_class);
    } else if (sufficiency > __ss_site_high_thresh && s.current_class > __ss_site_min_class) {
        if (s.demote_cooldown > 0) {
            s.demote_cooldown--;
        } else {
            s.current_class = std::max(s.current_class / 2, __ss_site_min_class);
            s.demote_pending = true;
            s.demote_cooldown = s.demote_backoff;
        }
    } else {
        // dead zone: any pending halve is confirmed good; reset backoff
        s.demote_pending = false;
        s.demote_backoff = 0;
        if (s.demote_cooldown > 0) {
            s.demote_cooldown--;
        }
    }

    s.samples = 0;
    s.grow_events = 0;
}

/* Call from append() the first time a given list instance overflows
 * its reserved capacity (guarded by the instance's own flag). */
inline void __list_site_grew(ListSiteStat &s) {
    s.grow_events++;
}

/* Reserve hint for a new list created at this site: just the site's
 * current size class. */
inline std::size_t __list_site_hint(ListSiteStat &s) {
    return s.current_class;
}

#endif
