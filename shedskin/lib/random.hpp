/* Copyright 2005-2025 Jeff Miller, Mark Dufour and other contributors */

#ifndef __RANDOM_HPP
#define __RANDOM_HPP

#include "builtin.hpp"
#include "math/__init__.hpp"
#include "time.hpp"

#include <random>
#include <vector>
#include <bit>

using namespace __shedskin__;
namespace __random__ {

void seed_xoshiro256(uint64_t initial_seed);

class Random;

extern class_ *cl_Random;
class Random : public pyobj {
/**
Random number generator base class used by bound module functions.

    Used to instantiate instances of Random to get generators that don't
    share state.  Especially useful for multi-threaded programs, creating
    a different instance of Random for each thread, and using the jumpahead()
    method to ensure that the generated sequences seen by each thread don't
    overlap.

    Class Random can also be subclassed if you want to use a different basic
    generator of your own devising: in that case, override the following
    methods:  random(), seed(), getstate(), setstate() and jumpahead().
*/
public:
    int gauss_switch;
    static constexpr __ss_int VERSION = 3; /* like cpython's Random.VERSION */
    __ss_float gauss_next;

    /* xoshiro256++ state, one copy per instance so that separate Random
       objects have independent streams (as the docstring above promises).
       Use _next_word()/_seed_state() rather than touching this directly. */
    uint64_t _s[4];

    /* The single source of randomness for random(), getrandbits() and
       randbytes(). SystemRandom overrides it to draw from the OS instead. */
    virtual uint64_t _next_word();
    void _seed_state(uint64_t initial_seed);

    /* Unbiased random integer in [0, n), n > 0, built from whole generator
       words (as CPython's _randbelow() does) instead of random()*n, which
       only carries 53 bits and so could never produce most values for
       n > 2**53. */
    uint64_t _randbelow(uint64_t n);
    std::vector<__ss_int> _sample_indices(__ss_int n, __ss_int k);

    void _init_instance();
    Random();
    template <class A> Random(A x) {
        /* x may be None (seed from entropy), an int, float, str or bytes,
           as for seed(). */
        this->__class__ = cl_Random;
        this->_init_instance();
        this->seed(x);
    }
    virtual __ss_float random();
    __ss_float paretovariate(__ss_float alpha);
    __ss_int randrange(__ss_int stop);
    __ss_int randrange(__ss_int start, __ss_int stop);
    __ss_int randrange(__ss_int start, __ss_int stop, __ss_int step);
    __ss_float betavariate(__ss_float alpha, __ss_float beta);
    __ss_float normalvariate(__ss_float mu, __ss_float sigma);
    template <class A> void *seed(A a, __ss_int version=2);
    __ss_float weibullvariate(__ss_float alpha, __ss_float beta);
    __ss_int binomialvariate(__ss_int n=1, __ss_float p=0.5);
    int _init_by_array(list<int> *init_key);
    __ss_int randint(__ss_int a, __ss_int b);
    __ss_float vonmisesvariate(__ss_float mu, __ss_float kappa);
    __ss_float gammavariate(__ss_float alpha, __ss_float beta);
    __ss_float uniform(__ss_float a, __ss_float b);
    __ss_float triangular(__ss_float low, __ss_float high, __ss_float mode); /* XXX template */
    __ss_float triangular(__ss_float low, __ss_float high, __ss_int mode);
    __ss_float triangular(__ss_float low, __ss_float high, void *mode);
    __ss_float stdgamma(__ss_float alpha, __ss_float ainv, __ss_float bbb, __ss_float ccc);
    __ss_float expovariate(__ss_float lambd);
    virtual __ss_int getrandbits(__ss_int k);
    virtual bytes *randbytes(__ss_int n);
    virtual void *setstate(bytes *state);
    __ss_float lognormvariate(__ss_float mu, __ss_float sigma);
    int _init_genrand(int s);
    __ss_float gauss(__ss_float mu, __ss_float sigma);
    template <class A> A choice(pyseq<A> *seq);
    template <class A, class W, class C> list<A> *choices(pyseq<A> *seq, W weights, C cum_weights, __ss_int k=1);
    template <class A> void *shuffle(list<A> *x);
    template <class A, class C> list<A> *sample(pyiter<A> *population, __ss_int k, C counts);
    template <class A, class C> list<A> *sample(pyseq<A> *population, __ss_int k, C counts);
    virtual bytes *getstate();
    __ss_float cunifvariate(__ss_float mean, __ss_float arc);
};

class SystemRandom;

extern class_ *cl_SystemRandom;
class SystemRandom : public Random {
/**
Alternate random number generator using sources provided by the operating
system (such as /dev/urandom on Unix or CryptGenRandom on Windows).

    Not available on all systems (see os.urandom() for details).
*/
public:
    SystemRandom();
    template <class A> SystemRandom(A) : SystemRandom() {
        /* the argument is ignored, as seed() is a no-op */
    }
    virtual uint64_t _next_word();
    virtual bytes *getstate();
    virtual void *setstate(bytes *state);
    template <class A> void *seed(A, __ss_int version=2) {
        /**
        Stub method.  Not used for a system random number generator.
        */
        return NULL;
    }
};

extern int  UPPER;
extern __ss_float  LOG4;
extern __ss_float  SG_MAGICCONST;
extern int  BPF;
extern Random * _inst;
extern int  MATRIX_A;
extern int  M;
extern int  LOWER;
extern int  N;
extern int  MAXWIDTH;
extern int  __ss_MAXINT;
extern str * __name__;
extern __ss_float  NV_MAGICCONST;
extern int  MAXBITS;
void __init();
__ss_float random();
bytes *getstate();
void *setstate(bytes *state);
__ss_int randrange(__ss_int stop);
__ss_int randrange(__ss_int start, __ss_int stop);
__ss_int randrange(__ss_int start, __ss_int stop, __ss_int step);
__ss_int randint(__ss_int a, __ss_int b);
__ss_float uniform(__ss_float a, __ss_float b);
__ss_float triangular(__ss_float low, __ss_float high, __ss_float mode);
__ss_float triangular(__ss_float low, __ss_float high, __ss_int mode);
__ss_float triangular(__ss_float low, __ss_float high, void *mode);
__ss_float normalvariate(__ss_float mu, __ss_float sigma);
__ss_float lognormvariate(__ss_float mu, __ss_float sigma);
__ss_float cunifvariate(__ss_float mean, __ss_float arc);
__ss_float expovariate(__ss_float lambd);
__ss_float vonmisesvariate(__ss_float mu, __ss_float kappa);
__ss_float gammavariate(__ss_float alpha, __ss_float beta);
__ss_float stdgamma(__ss_float alpha, __ss_float ainv, __ss_float bbb, __ss_float ccc);
__ss_float gauss(__ss_float mu, __ss_float sigma);
__ss_float betavariate(__ss_float alpha, __ss_float beta);
__ss_float paretovariate(__ss_float alpha);
__ss_float weibullvariate(__ss_float alpha, __ss_float beta);
__ss_int binomialvariate(__ss_int n=1, __ss_float p=0.5);
__ss_int getrandbits(__ss_int k);
bytes * randbytes(__ss_int n);

template <class A> A choice(pyseq<A> *seq) {

    return _inst->choice(seq);
}

template <class A, class W, class C> list<A> *choices(pyseq<A> *seq, W weights, C cum_weights, __ss_int k) {

    return _inst->choices(seq, weights, cum_weights, k);
}

template <class A> void *shuffle(list<A> *x) {

    return _inst->shuffle(x);
}

template <class A, class C> list<A> *sample(pyiter<A> *population, __ss_int k, C counts) {
    return _inst->sample(new list<A>(population), k, counts);
}

template <class A, class C> list<A> *sample(pyseq<A> *population, __ss_int k, C counts) {

    return _inst->sample(population, k, counts);
}

/* weights/cum_weights/counts helpers: None arrives as (void *)NULL */
template <class W> inline bool __random_values(pyiter<W> *w, std::vector<W> &out) {
    if (!w)
        return false;
    list<W> *l = new list<W>(w);
    out.assign(l->units.begin(), l->units.end());
    return true;
}
inline bool __random_values(void *, std::vector<__ss_int> &) { return false; }
inline bool __random_values(void *, std::vector<__ss_float> &) { return false; }

template <class W> inline std::vector<W> __random_elem_vector(pyiter<W> *) { return std::vector<W>(); }
inline std::vector<__ss_int> __random_elem_vector(void *) { return std::vector<__ss_int>(); }

extern str *const_choices_both, *const_choices_len, *const_choices_zero, *const_choices_finite;
extern str *const_sample_counts_len, *const_sample_counts_neg;

template <class A> void *Random::shuffle(list<A> *x) {
    /**
    x, random=random.random -> shuffle list x in place; return None.

            Note that for even rather small len(x), the total number of
            permutations of x is larger than the period of most random number
            generators; this implies that "most" permutations of a long
            sequence can never be generated.
    */
    for (__ss_int i = len(x)-1; i > 0; i--) {
        __ss_int j = (__ss_int)this->_randbelow((uint64_t)i+1);
        A tmp = x->units[(size_t)i];
        x->units[(size_t)i] = x->units[(size_t)j];
        x->units[(size_t)j] = tmp;
    }

    return NULL;
}

template <class A, class C> list<A> *Random::sample(pyiter<A> *population, __ss_int k, C counts) {
    return sample(new list<A>(population), k, counts);
}

template <class A, class C> list<A> *Random::sample(pyseq<A> *population, __ss_int k, C counts) {
    /**
    Chooses k unique random elements from a population sequence.

            Returns a new list containing elements from the population while
            leaving the original population unchanged.  The resulting list is
            in selection order so that all sub-slices will also be valid random
            samples.

            Repeated elements can be specified one at a time or with the
            optional counts parameter.
    */
    __ss_int n = len(population);
    list<A> *result = new list<A>();

    auto cum_counts = __random_elem_vector(counts);
    if (__random_values(counts, cum_counts)) {
        if ((__ss_int)cum_counts.size() != n)
            throw (new ValueError(const_sample_counts_len));
        __ss_int total = 0;
        for (size_t i = 0; i < cum_counts.size(); i++) {
            total += cum_counts[i];
            cum_counts[i] = total;
        }
        if (total < 0)
            throw (new ValueError(const_sample_counts_neg));
        std::vector<__ss_int> selections = this->_sample_indices(total, k);
        /* bisect_right over all but the last cumulative count
           (selections is empty when n == 0, since total is then 0) */
        for (__ss_int s : selections) {
            auto pos = std::upper_bound(cum_counts.begin(), cum_counts.end() - 1, s);
            result->append(population->__getitem__((__ss_int)(pos - cum_counts.begin())));
        }
        return result;
    }

    std::vector<__ss_int> selections = this->_sample_indices(n, k);
    for (__ss_int j : selections)
        result->append(population->__getitem__(j));
    return result;
}

template <class A> A Random::choice(pyseq<A> *seq) {
    /**
    Choose a random element from a non-empty sequence.
    */

    __ss_int n = len(seq);
    if (n == 0)
        throw new IndexError(new str("Cannot choose from an empty sequence"));
    return seq->__getitem__((__ss_int)this->_randbelow((uint64_t)n));
}

template <class A, class W, class C> list<A> *Random::choices(pyseq<A> *seq, W weights, C cum_weights, __ss_int k) {
    /**
    Return a k sized list of population elements chosen with replacement.

            If the relative weights or cumulative weights are not specified,
            the selections are made with equal probability.
    */
    __ss_int n = len(seq);
    list<A> *result = new list<A>();

    auto w = __random_elem_vector(weights);
    auto cw = __random_elem_vector(cum_weights);
    bool have_w = __random_values(weights, w);
    bool have_cw = __random_values(cum_weights, cw);

    if (!have_w && !have_cw) {
        __ss_float fn = (__ss_float)n;
        for (__ss_int i = 0; i < k; i++)
            result->append(seq->__getitem__((__ss_int)__math__::floor(this->random() * fn)));
        return result;
    }
    if (have_w && have_cw)
        throw (new TypeError(const_choices_both));

    std::vector<__ss_float> cum;
    if (have_w) {
        __ss_float acc = 0.0;
        for (auto x : w) {
            acc += (__ss_float)x;
            cum.push_back(acc);
        }
    } else {
        for (auto x : cw)
            cum.push_back((__ss_float)x);
    }

    if ((__ss_int)cum.size() != n)
        throw (new ValueError(const_choices_len));
    if (n == 0)
        throw (new IndexError(new str("list index out of range")));
    __ss_float total = cum.back() + 0.0;
    if (total <= 0.0)
        throw (new ValueError(const_choices_zero));
    if (!std::isfinite(total))
        throw (new ValueError(const_choices_finite));

    auto hi = cum.end() - 1;
    for (__ss_int i = 0; i < k; i++) {
        __ss_float r = this->random() * total;
        auto pos = std::upper_bound(cum.begin(), hi, r);
        result->append(seq->__getitem__((__ss_int)(pos - cum.begin())));
    }
    return result;
}

template<class T> inline int __is_none(T *t) { return !t; }
template<class T> inline int __is_none(T) { return 0; }

/* seed(a, version=1) hashes str/bytes seeds the way Python 3.1 did (as
   CPython still does for version=1); for every other type the version
   makes no difference. */
template<class T> inline uint64_t __seed_v1(T t) { return (uint64_t)hasher(t); }
uint64_t __seed_v1(str *s);
uint64_t __seed_v1(bytes *b);

template <class A> void *Random::seed(A a, __ss_int version) {
    /**
    Initialize the random number generator with a single seed number.

            If provided, the seed, a, must be an int, float, str or bytes.
            If no argument is provided, OS entropy is used for seeding.
    */

    if(__is_none(a)) {
        std::random_device rd;
        uint64_t hi = rd();
        this->_seed_state((hi << 32) | rd());
    } else if(version == 1) {
        this->_seed_state(__seed_v1(a));
    } else {
        this->_seed_state(hasher(a));
    }

    return NULL;
}

template <class A> void *seed(A a, __ss_int version=2) {
    return _inst->seed(a, version);
}

} // module namespace
#endif
