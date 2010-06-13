#include "random.hpp"

/**
Random variable generators.

    integers
    --------
           uniform within range

    sequences
    ---------
           pick random element
           pick random sample
           generate random permutation

    distributions on the real line:
    ------------------------------
           uniform
           normal (Gaussian)
           lognormal
           negative exponential
           gamma
           beta
           pareto
           Weibull

    distributions on the circle (angles 0 to 2pi)
    ---------------------------------------------
           circular uniform
           von Mises

General notes on the underlying Mersenne Twister core generator:

* The period is 2**19937-1.
* It is one of the most extensively tested generators in existence
* Without a direct way to compute N steps forward, the
  semantics of jumpahead(n) are weakened to simply jump
  to another distant state and rely on the large period
  to avoid overlapping sequences.

Note: The jumpahead method is implemented for WichmannHill, but not yet for
Random (Mersenne Twister).
*/

namespace __random__ {

str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_2, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_26, *const_27, *const_28, *const_29, *const_3, *const_30, *const_31, *const_32, *const_33, *const_34, *const_35, *const_36, *const_4, *const_7, *const_8, *const_9;

list<str *> *__all__;
list<int> *mag01;
double LOG4, NV_MAGICCONST, SG_MAGICCONST;
int BPF, LOWER, M, MATRIX_A, MAXBITS, __ss_MAXINT, MAXWIDTH, N, UPPER;
str *__name__;
Random *_inst;

static inline list<double> *list_comp_0(list<int> *__108) {
    int s, __25;
    list<double> *result = new list<double>();

    result->resize(len(__108));
    FOR_IN_SEQ(s,__108,108,25)
        result->units[__25] = __float(s);
    END_FOR

    return result;
}

static inline list<int> *list_comp_1(list<double> *__108) {
    double s;
    list<int> *result = new list<int>();
    int __28;

    result->resize(len(__108));
    FOR_IN_SEQ(s,__108,108,28)
        result->units[__28] = __int(s);
    END_FOR

    return result;
}

/**
class Random
*/

class_ *cl_Random;

double Random::paretovariate(double alpha) {
    /**
    Pareto distribution.  alpha is the shape parameter.
    */
    double u;

    u = (1.0-this->random());
    return (1.0/__power(u, (1.0/alpha)));
}

int Random::randrange(int stop) {
    return this->randrange(0, stop, 1);
}
int Random::randrange(int start, int stop) {
    return this->randrange(start, stop, 1);
}
int Random::randrange(int start, int stop, int step) {
    /**
    Choose a random item from range(start, stop[, step]).

            This fixes the problem with randint() which includes the
            endpoint; in Python this is usually not what you want.
            Do not supply the 'int', 'default', and 'maxwidth' arguments.
    */
    int istart, istep, istop, n, width;

    istart = __int(start);
    if ((istart!=start)) {
        throw (new ValueError(const_0));
    }
    istop = __int(stop);
    if ((istop!=stop)) {
        throw (new ValueError(const_1));
    }
    width = (istop-istart);
    if (((step==1) && (width>0))) {
        return __int((istart+__int((this->random()*width))));
    }
    if ((step==1)) {
        throw (new ValueError(const_2));
    }
    istep = __int(step);
    if ((istep!=step)) {
        throw (new ValueError(const_3));
    }
    if ((istep>0)) {
        n = (((width+istep)-1)/istep);
    }
    else if ((istep<0)) {
        n = (((width+istep)+1)/istep);
    }
    else {
        throw (new ValueError(const_4));
    }
    if ((n<=0)) {
        throw (new ValueError(const_2));
    }
    return (istart+(istep*__int((this->random()*n))));
}

double Random::betavariate(double alpha, double beta) {
    /**
    Beta distribution.

            Conditions on the parameters are alpha > -1 and beta} > -1.
            Returned values range between 0 and 1.

    */
    double y;

    y = this->gammavariate(alpha, 1.0);
    if ((y==0)) {
        return 0.0;
    }
    else {
        return (y/(y+this->gammavariate(beta, 1.0)));
    }
    return 0;
}

double Random::random() {
    /**
    Generate a random number on [0,1)-real-interval.
    */

#ifdef __SS_FASTRANDOM
    return rand() / ((double)RAND_MAX+1);
#else
    return this->_genrand_res53();
#endif
}

double Random::normalvariate(double mu, double sigma) {
    /**
    Normal distribution.

            mu is the mean, and sigma is the standard deviation.

    */
    double u1, u2, z, zz;


    while(1) {
        u1 = this->random();
        u2 = (1.0-this->random());
        z = ((NV_MAGICCONST*(u1-0.5))/u2);
        zz = ((z*z)/4.0);
        if ((zz<=-__math__::log(u2))) {
            break;
        }
    }
    return (mu+(z*sigma));
}

double Random::_genrand_res53() {
    /**
    Generate a random number on [0,1) with 53-bit resolution.
    */
    int a, b;

    a = ((this->_genrand_int32()>>5)&~(-1<<(32-5)));
    b = ((this->_genrand_int32()>>6)&~(-1<<(32-6)));
//    return (((a*67108864.0)+b)*(1.0/9.00719925474e+15));

    return (((a*67108864.0)+b)*(1.0/9007199254740992.0));
    return 0;
}

double Random::weibullvariate(double alpha, double beta) {
    /**
    Weibull distribution.

            alpha is the scale parameter and beta is the shape parameter.

    */
    double u;

    u = (1.0-this->random());
    return (alpha*__power(-__math__::log(u), (1.0/beta)));
}

Random::Random() {
    this->__class__ = cl_Random;

    this->mt = ((new list<int>(1, 0)))->__mul__(N);
    this->mti = (N+1);
    this->gauss_next = 0.0;
    this->gauss_switch = 0;
    this->seed((void *)NULL);
    this->VERSION = 2;
}

Random::Random(int a) {
    /**
    Initialize an instance.

            Optional argument a controls seeding, as for Random.seed().
            The seed, a, must be an integer.
    */
    this->__class__ = cl_Random;

    this->mt = ((new list<int>(1, 0)))->__mul__(N);
    this->mti = (N+1);
    this->gauss_next = 0.0;
    this->gauss_switch = 0;
    this->seed(a);
    this->VERSION = 2;
}

int Random::_init_by_array(list<int> *init_key) {
    /**
    Seed the random number generator with a list of numbers.
    */
    list<int> *__14, *__15, *__16, *__19, *__20, *__21, *__22;
    int __12, __13, __17, __18, i, j, k, key_length;

    key_length = len(init_key);
    this->_init_genrand(19650218);
    i = 1;
    j = 0;
    k = ___max(2, 0, N, key_length);

    FAST_FOR_NEG(k,k,0,-1,12,13)
        __14 = this->mt;
        __14->__setitem__(i, (((this->mt)->__getfast__(i)^(((this->mt)->__getfast__((i-1))^(((this->mt)->__getfast__((i-1))>>30)&3))*1664525))+init_key->__getfast__(j))+j);
        __15 = this->mt;
        __15->__setitem__(i, __15->__getfast__(i) & 4294967295u);
        i += 1;
        j += 1;
        if ((i>=N)) {
            __16 = this->mt;
            __16->__setitem__(0, (this->mt)->__getfast__((N-1)));
            i = 1;
        }
        if ((j>=key_length)) {
            j = 0;
        }
    END_FOR


    FAST_FOR_NEG(k,(N-1),0,-1,17,18)
        __19 = this->mt;
        __19->__setitem__(i, (((this->mt)->__getfast__(i)^(((this->mt)->__getfast__((i-1))^(((this->mt)->__getfast__((i-1))>>30)&3))*1566083941))-i));
        __20 = this->mt;
        __20->__setitem__(i, __20->__getfast__(i) & 4294967295u);
        i += 1;
        if ((i>=N)) {
            __21 = this->mt;
            __21->__setitem__(0, (this->mt)->__getfast__((N-1)));
            i = 1;
        }
    END_FOR

    __22 = this->mt;
    __22->__setitem__(0, 2147483648u);
    return 0;
}

int Random::randint(int a, int b) {
    /**
    Return random integer in range [a, b], including both end points.
    */

    return this->randrange(a, (b+1), 1);
}

double Random::vonmisesvariate(double mu, double kappa) {
    /**
    Circular data distribution.

            mu is the mean angle, expressed in radians between 0 and 2*pi, and
            kappa is the concentration parameter, which must be greater than or
            equal to zero.  If kappa is equal to zero, this distribution reduces
            to a uniform random angle over the range 0 to 2*pi.

    */
    double a, b, c, f, r, theta, u1, u2, u3, z;

    if ((kappa<=1e-06)) {
        return ((2*__math__::pi)*this->random());
    }
    a = (1.0+__math__::sqrt((1.0+((4.0*kappa)*kappa))));
    b = ((a-__math__::sqrt((2.0*a)))/(2.0*kappa));
    r = ((1.0+(b*b))/(2.0*b));

    while(1) {
        u1 = this->random();
        z = __math__::cos((__math__::pi*u1));
        f = ((1.0+(r*z))/(r+z));
        c = (kappa*(r-f));
        u2 = this->random();
        if ((!((u2>=(c*(2.0-c))) && (u2>(c*__math__::exp((1.0-c))))))) {
            break;
        }
    }
    u3 = this->random();
    if ((u3>0.5)) {
        theta = (__math__::fmod(mu, (2*__math__::pi))+__math__::acos(f));
    }
    else {
        theta = (__math__::fmod(mu, (2*__math__::pi))-__math__::acos(f));
    }
    return theta;
}

double Random::gammavariate(double alpha, double beta) {
    /**
    Gamma distribution.  Not the gamma function!

            Conditions on the parameters are alpha > 0 and beta > 0.

    */
    double ainv, b, bbb, ccc, p, r, u, u1, u2, v, x, z;

    if (((alpha<=0.0) || (beta<=0.0))) {
        throw (new ValueError(const_7));
    }
    if ((alpha>1.0)) {
        ainv = __math__::sqrt(((2.0*alpha)-1.0));
        bbb = (alpha-LOG4);
        ccc = (alpha+ainv);

        while(1) {
            u1 = this->random();
            if ((!((1e-07<u1)&&(u1<0.9999999)))) {
                continue;
            }
            u2 = (1.0-this->random());
            v = (__math__::log((u1/(1.0-u1)))/ainv);
            x = (alpha*__math__::exp(v));
            z = ((u1*u1)*u2);
            r = ((bbb+(ccc*v))-x);
            if (((((r+SG_MAGICCONST)-(4.5*z))>=0.0) || (r>=__math__::log(z)))) {
                return (x*beta);
            }
        }
    }
    else if ((alpha==1.0)) {
        u = this->random();

        while((u<=1e-07)) {
            u = this->random();
        }
        return (-__math__::log(u)*beta);
    }
    else {

        while(1) {
            u = this->random();
            b = ((__math__::e+alpha)/__math__::e);
            p = (b*u);
            if ((p<=1.0)) {
                x = __power(p, (1.0/alpha));
            }
            else {
                x = -__math__::log(((b-p)/alpha));
            }
            u1 = this->random();
            if ((!(((p<=1.0) && (u1>__math__::exp(-x))) || ((p>1) && (u1>__power(x, (alpha-1.0))))))) {
                break;
            }
        }
        return (x*beta);
    }
    return 0;
}

double Random::uniform(double a, double b) {
    /**
    Get a random number in the range [a, b).
    */

    return (a+((b-a)*this->random()));
}

static inline double __triangular(double low, double high, double u, double c) {
    double __0, __1;
    if ((u>c)) {
        u = (1.0-u);
        c = (1.0-c);
        __0 = high;
        __1 = low;
        low = __0;
        high = __1;
    }
    return (low+((high-low)*__power((u*c), 0.5)));
}

double Random::triangular(double low, double high, double mode) {
    /**
    Triangular distribution.

    Continuous distribution bounded by given lower and upper limits,
    and having a given mode value in-between.

    http://en.wikipedia.org/wiki/Triangular_distribution

    */
    return __triangular(low, high, this->random(), ((mode-low)/(high-low)));
}

double Random::triangular(double low, double high, __ss_int mode) {
    return __triangular(low, high, this->random(), (double)mode);
}

double Random::triangular(double low, double high, void *) {
    return __triangular(low, high, this->random(), 0.5);
}

double Random::stdgamma(double alpha, double, double, double) {

    return this->gammavariate(alpha, 1.0);
}

double Random::expovariate(double lambd) {
    /**
    Exponential distribution.

            lambd is 1.0 divided by the desired mean.  (The parameter would be
            called "lambda", but that is a reserved word in Python.)  Returned
            values range from 0 to positive infinity.

    */
    double u;

    u = this->random();

    while((u<=1e-07)) {
        u = this->random();
    }
    return (-__math__::log(u)/lambd);
}

int Random::getrandbits(int k) {
    /**
    getrandbits(k) -> x.  Generates an int with k random bits.
    */

    if ((k<=0)) {
        throw (const_8);
    }
    if ((k>MAXBITS)) {
        throw (new ValueError(const_9));
    }
    return ((this->_genrand_int32()>>(32-k))&~(-1<<k));
}

void *Random::setstate(list<double> *state) {
    /**
    Restore internal state from object returned by getstate().
    */
    int version;

    version = __int(state->__getfast__(0));
    if ((version!=2)) {
        throw ((new ValueError(__modct(const_10, 2, ___box(version), ___box(this->VERSION)))));
    }
    this->mti = __int(state->__getfast__(1));
    this->gauss_switch = __int(state->__getfast__(2));
    this->mt = list_comp_1(state->__slice__(3, 3, -1, 0));
    this->gauss_next = state->__getfast__(-1);

    return NULL;
}

double Random::lognormvariate(double mu, double sigma) {
    /**
    Log normal distribution.

            If you take the natural logarithm of this distribution, you'll get a
            normal distribution with mean mu and standard deviation sigma.
            mu can have any value, and sigma must be greater than zero.

    */

    return __math__::exp(this->normalvariate(mu, sigma));
}

int Random::_init_genrand(int s) {
    /**
    Seed the random number generator.
    */
    list<int> *__10, *__11, *__7;
    int __8, __9;

    __7 = this->mt;
    __7->__setitem__(0, (s&4294967295u));

    FAST_FOR(this->mti,1,N,1,8,9)
        __10 = this->mt;
        __10->__setitem__(this->mti, ((1812433253*((this->mt)->__getfast__((this->mti-1))^(((this->mt)->__getfast__((this->mti-1))>>30)&3)))+this->mti));
        __11 = this->mt;
        __11->__setitem__(this->mti, __11->__getfast__(this->mti) & 4294967295u);
    END_FOR

    this->mti += 1;
    return 0;
}

double Random::gauss(double mu, double sigma) {
    /**
    Gaussian distribution.

            mu is the mean, and sigma is the standard deviation.  This is
            slightly faster than the normalvariate() function.

            Not thread-safe without a lock around calls.

    */
    double g2rad, x2pi, z;

    if ((this->gauss_switch==1)) {
        z = this->gauss_next;
        this->gauss_switch = 0;
    }
    else {
        x2pi = ((this->random()*2)*__math__::pi);
        g2rad = __math__::sqrt((-2.0*__math__::log((1.0-this->random()))));
        z = (__math__::cos(x2pi)*g2rad);
        this->gauss_next = (__math__::sin(x2pi)*g2rad);
        this->gauss_switch = 1;
    }
    return (mu+(z*sigma));
}

int Random::_genrand_int32() {
    /**
    Generate a random number on [0,0xffffffff]-interval.
    */
    list<int> *__2, *__5, *__6;
    int __0, __1, __3, __4, kk, y;

    if ((this->mti>=N)) {
        if ((this->mti==(N+1))) {
            this->_init_genrand(5489);
        }

        FAST_FOR(kk,0,(N-M),1,0,1)
            y = (((this->mt)->__getfast__(kk)&UPPER)|((this->mt)->__getfast__((kk+1))&LOWER));
            __2 = this->mt;
            __2->__setitem__(kk, ((this->mt)->__getfast__((kk+M))^(((y>>1)&LOWER)^mag01->__getfast__((y&1)))));
        END_FOR


        FAST_FOR(kk,(kk+1),(N-1),1,3,4)
            y = (((this->mt)->__getfast__(kk)&UPPER)|((this->mt)->__getfast__((kk+1))&LOWER));
            __5 = this->mt;
            __5->__setitem__(kk, ((this->mt)->__getfast__((kk+(M-N)))^(((y>>1)&LOWER)^mag01->__getfast__((y&1)))));
        END_FOR

        y = (((this->mt)->__getfast__((N-1))&UPPER)|((this->mt)->__getfast__(0)&LOWER));
        __6 = this->mt;
        __6->__setitem__(N-1, ((this->mt)->__getfast__((M-1))^(((y>>1)&LOWER)^mag01->__getfast__((y&1)))));
        this->mti = 0;
    }
    y = (this->mt)->__getfast__(this->mti);
    this->mti += 1;
    y ^= ((y>>11)&~(-1<<(32-11)));
    y ^= ((y<<7)&2636928640u);
    y ^= ((y<<15)&4022730752u);
    y ^= ((y>>18)&~(-1<<(32-18)));
    return y;
}

list<double> *Random::getstate() {
    /**
    Return internal state; can be passed to setstate() later.
    */
    list<double> *x;

    x = list_comp_0(__add((new list<int>(3, this->VERSION, this->mti, this->gauss_switch)), this->mt));
    return __add(x, (new list<double>(1, this->gauss_next)));
}

double Random::cunifvariate(double mean, double arc) {

    return __math__::fmod((mean+(arc*(this->random()-0.5))), __math__::pi);
}

/**
class WichmannHill
*/

class_ *cl_WichmannHill;

void *WichmannHill::__whseed(int x, int y, int z) {
    /**
    Set the Wichmann-Hill seed from (x, y, z).

            These must be integers in the range [0, 256).
    */
    tuple2<int, int> *__59, *__60, *__61;
    int __62, __63, __64, secs, t, usec;
    double hophop;

    if ((!(((0<=x)&&(x<256)) && ((0<=y)&&(y<256)) && ((0<=z)&&(z<256))))) {
        throw ((new ValueError(const_11)));
    }
    if (((0==x)&&(x==y)&&(y==z))) {
        hophop = __time__::time();
        secs = __int(hophop);
        usec = __int((1000000*(hophop-__int(hophop))));
        t = ((__mods(secs, (__ss_MAXINT/1000000))*1000000)|usec);
        __59 = divmod(t, 256);
        t = __59->__getfirst__();
        x = __59->__getsecond__();
        __60 = divmod(t, 256);
        t = __60->__getfirst__();
        y = __60->__getsecond__();
        __61 = divmod(t, 256);
        t = __61->__getfirst__();
        z = __61->__getsecond__();
    }
    if ((x==0)) {
        x = 1;
    }
    if ((y==0)) {
        y = 1;
    }
    if ((z==0)) {
        z = 1;
    }
    __62 = x;
    __63 = y;
    __64 = z;
    this->_seed = (new tuple2<int, int>(3, __62, __63, __64));
    this->gauss_next = 0.0;
    this->gauss_switch = 0;
    return NULL;
}

double WichmannHill::random() {
    /**
    Get the next random number in the range [0.0, 1.0).
    */
    tuple2<int, int> *__46;
    int __47, __48, __49, x, y, z;

    __46 = this->_seed;
    x = __46->__getfast__(0);
    y = __46->__getfast__(1);
    z = __46->__getfast__(2);
    x = __mods((171*x), 30269);
    y = __mods((172*y), 30307);
    z = __mods((170*z), 30323);
    __47 = x;
    __48 = y;
    __49 = z;
    this->_seed = (new tuple2<int, int>(3, __47, __48, __49));
    return __math__::fmod((((__float(x)/30269.0)+(__float(y)/30307.0))+(__float(z)/30323.0)), 1.0);
}

void *WichmannHill::seed() {
    return this->seed(-1);
}
void *WichmannHill::seed(int a) {
    /**
    Initialize internal state from hashable object.

            If provided, the seed, a, should be a non-negative integer.
            If no argument is provided, current time is used for seeding.

            Distinct values between 0 and 27814431486575L inclusive are guaranteed
            to yield distinct internal states (this guarantee is specific to the
            default Wichmann-Hill generator).
    */
    tuple2<int, int> *__40, *__41, *__42;
    int __43, __44, __45, secs, usec, x, y, z;
    double hophop;

    if ((a==-1)) {
        hophop = __time__::time();
        secs = __int(hophop);
        usec = __int((1000000*(hophop-__int(hophop))));
        a = ((__mods(secs, (__ss_MAXINT/1000000))*1000000)|usec);
    }
    __40 = divmod(a, 30268);
    a = __40->__getfirst__();
    x = __40->__getsecond__();
    __41 = divmod(a, 30306);
    a = __41->__getfirst__();
    y = __41->__getsecond__();
    __42 = divmod(a, 30322);
    a = __42->__getfirst__();
    z = __42->__getsecond__();
    __43 = (__int(x)+1);
    __44 = (__int(y)+1);
    __45 = (__int(z)+1);
    this->_seed = (new tuple2<int, int>(3, __43, __44, __45));
    this->gauss_next = 0.0;
    this->gauss_switch = 0;
    return NULL;
}

WichmannHill::WichmannHill() {
    this->__class__ = cl_WichmannHill;

    this->seed(-1);
    this->gauss_next = 0.0;
    this->gauss_switch = 0;
    this->VERSION = 1;
}

WichmannHill::WichmannHill(int a) {
    this->__class__ = cl_WichmannHill;

    this->seed(a);
    this->gauss_next = 0.0;
    this->gauss_switch = 0;
    this->VERSION = 1;
}

void *WichmannHill::whseed() {
    return this->whseed(-1);
}
void *WichmannHill::whseed(int a) {
    /**
    Seed from current time or non-negative integer argument.

            If no argument is provided, current time is used for seeding.

            This is obsolete, provided for compatibility with the seed routine
            used prior to Python 2.1.  Use the .seed() method instead.
    */
    tuple2<int, int> *__65, *__66, *__67;
    int x, y, z;

    if ((a==-1)) {
        this->__whseed(((int )(0)), ((int )(0)), ((int )(0)));
        return NULL;
    }
    __65 = divmod(a, 256);
    a = __65->__getfirst__();
    x = __65->__getsecond__();
    __66 = divmod(a, 256);
    a = __66->__getfirst__();
    y = __66->__getsecond__();
    __67 = divmod(a, 256);
    a = __67->__getfirst__();
    z = __67->__getsecond__();
    x = __mods((x+a), 256);
    y = __mods((y+a), 256);
    z = __mods((z+a), 256);
    if ((x==0)) {
        x = 1;
    }
    if ((y==0)) {
        y = 1;
    }
    if ((z==0)) {
        z = 1;
    }
    this->__whseed(x, y, z);
    return NULL;
}

void *WichmannHill::setstate(list<double> *state) {
    /**
    Restore internal state from object returned by getstate().
    */
    double xf, yf, zf;
    list<double> *__51;
    int __52, __53, __54, version;

    version = __int(state->__getfast__(0));
    if ((version==1)) {
        __51 = state->__slice__(3, 1, 4, 0);
        xf = __51->__getfast__(0);
        yf = __51->__getfast__(1);
        zf = __51->__getfast__(2);
        __52 = __int(xf);
        __53 = __int(yf);
        __54 = __int(zf);
        this->_seed = (new tuple2<int, int>(3, __52, __53, __54));
        this->gauss_switch = __int(state->__getfast__(4));
        this->gauss_next = state->__getfast__(5);
    }
    else {
        throw ((new ValueError(__modct(const_10, 2, ___box(version), ___box(this->VERSION)))));
    }
    return NULL;
}

int WichmannHill::jumpahead(int n) {
    /**
    Act as if n calls to random() were made, but quickly.

            n is an int, greater than or equal to 0.

            Example use:  If you have 2 threads and know that each will
            consume no more than a million random numbers, create two Random
            objects r1 and r2, then do
                r2.setstate(r1.getstate())
                r2.jumpahead(1000000)
            Then r1 and r2 will use guaranteed-disjoint segments of the full
            period.
    */
    tuple2<int, int> *__55;
    int __56, __57, __58, x, y, z;

    if ((!(n>=0))) {
        throw ((new ValueError(const_12)));
    }
    __55 = this->_seed;
    x = __55->__getfast__(0);
    y = __55->__getfast__(1);
    z = __55->__getfast__(2);
    x = __mods(__int((x*__power(171, n, 30269))), (__ss_int)30269);
    y = __mods(__int((y*__power(172, n, 30307))), (__ss_int)30307);
    z = __mods(__int((z*__power(170, n, 30323))), (__ss_int)30323);
    __56 = x;
    __57 = y;
    __58 = z;
    this->_seed = (new tuple2<int, int>(3, __56, __57, __58));
    return 0;
}

list<double> *WichmannHill::getstate() {
    /**
    Return internal state; can be passed to setstate() later.
    */
    tuple2<int, int> *__50;
    int x, y, z;

    __50 = this->_seed;
    x = __50->__getfast__(0);
    y = __50->__getfast__(1);
    z = __50->__getfast__(2);
    return (new list<double>(6, __float(this->VERSION), __float(x), __float(y), __float(z), __float(this->gauss_switch), this->gauss_next));
}

void __init() {
    const_0 = new str("non-integer arg 1 for randrange()");
    const_1 = new str("non-integer stop for randrange()");
    const_2 = new str("empty range for randrange()");
    const_3 = new str("non-integer step for randrange()");
    const_4 = new str("zero step for randrange()");
    const_7 = new str("gammavariate: alpha and beta must be > 0.0");
    const_8 = new str("number of bits must be greater than zero for getrandbits(k)");
    const_9 = new str("k exceeds size of int for getrandbits(k)");
    const_10 = new str("state with version %s passed to Random.setstate() of version %s");
    const_11 = new str("seeds must be in range(0, 256)");
    const_12 = new str("n must be >= 0");
    const_13 = new str("Random");
    const_14 = new str("seed");
    const_15 = new str("random");
    const_16 = new str("uniform");
    const_17 = new str("randint");
    const_18 = new str("choice");
    const_19 = new str("sample");
    const_20 = new str("randrange");
    const_21 = new str("shuffle");
    const_22 = new str("normalvariate");
    const_23 = new str("lognormvariate");
    const_24 = new str("cunifvariate");
    const_25 = new str("expovariate");
    const_26 = new str("vonmisesvariate");
    const_27 = new str("gammavariate");
    const_28 = new str("stdgamma");
    const_29 = new str("gauss");
    const_30 = new str("betavariate");
    const_31 = new str("paretovariate");
    const_32 = new str("weibullvariate");
    const_33 = new str("getstate");
    const_34 = new str("setstate");
    const_35 = new str("jumpahead");
    const_36 = new str("WichmannHill");

    __name__ = new str("random");

    cl_WichmannHill = new class_("WichmannHill", 14, 14);
    cl_Random = new class_("Random", 13, 14);

    /**
    =========================== Source Notes ==============================
    Translated by Guido van Rossum from C source provided by Adrian Baddeley.
    Adapted by Raymond Hettinger for use with the Mersenne Twister core generator.
    Adapted by Jeff Miller for compatibility with the Shed Skin Python-to-C++
    compiler.

    Mersenne Twister was converted to Python by Jeff Miller
    2007-02-03
    jwmillerusa (at) gmail (dot) com
    http://millerideas.com

    Below are the original comments from the authors' C source file.
    =======================================================================

       A C-program for MT19937, with initialization improved 2002/1/26.
       Coded by Takuji Nishimura and Makoto Matsumoto.

       Before using, initialize the state by using init_genrand(seed)
       or init_by_array(init_key, key_length).

       Copyright (C) 1997 - 2002, Makoto Matsumoto and Takuji Nishimura,
       All rights reserved.

       Redistribution and use in source and binary forms, with or without
       modification, are permitted provided that the following conditions
       are met:

         1. Redistributions of source code must retain the above copyright
            notice, this list of conditions and the following disclaimer.

         2. Redistributions in binary form must reproduce the above copyright
            notice, this list of conditions and the following disclaimer in the
            documentation and/or other materials provided with the distribution.

         3. The names of its contributors may not be used to endorse or promote
            products derived from this software without specific prior written
            permission.

       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
       AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
       IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
       ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
       LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
       CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
       SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
       INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
       CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
       ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
       POSSIBILITY OF SUCH DAMAGE.


       Any feedback is very welcome.
       http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/emt.html
       email: m-mat @ math.sci.hiroshima-u.ac.jp (remove space)
    */
    __all__ = (new list<str *>(24, const_13, const_14, const_15, const_16, const_17, const_18, const_19, const_20, const_21, const_22, const_23, const_24, const_25, const_26, const_27, const_28, const_29, const_30, const_31, const_32, const_33, const_34, const_35, const_36));
    NV_MAGICCONST = ((4*__math__::exp(-0.5))/__math__::sqrt(2.0));
    LOG4 = __math__::log(4.0);
    SG_MAGICCONST = (1.0+__math__::log(4.5));
    BPF = 53;
    MAXWIDTH = (1<<BPF);
    MAXBITS = 31;
    __ss_MAXINT = 2147483647;
    N = 624;
    M = 397;
    MATRIX_A = 2567483615u;
    UPPER = 2147483648u;
    LOWER = 2147483647;
    mag01 = (new list<int>(2, 0, MATRIX_A));
    _inst = (new Random());
}

double random() {

    return _inst->random();
}

list<double> *getstate() {

    return _inst->getstate();
}

void *setstate(list<double> *state) {

    return _inst->setstate(state);
}

int randrange(int stop) {

    return _inst->randrange(0, stop, 1);
}

int randrange(int start, int stop) {

    return _inst->randrange(start, stop, 1);
}

int randrange(int start, int stop, int step) {

    return _inst->randrange(start, stop, step);
}

int randint(int a, int b) {

    return _inst->randint(a, b);
}

double uniform(double a, double b) {

    return _inst->uniform(a, b);
}

double normalvariate(double mu, double sigma) {

    return _inst->normalvariate(mu, sigma);
}

double lognormvariate(double mu, double sigma) {

    return _inst->lognormvariate(mu, sigma);
}

double cunifvariate(double mean, double arc) {

    return _inst->cunifvariate(mean, arc);
}

double expovariate(double lambd) {

    return _inst->expovariate(lambd);
}

double vonmisesvariate(double mu, double kappa) {

    return _inst->vonmisesvariate(mu, kappa);
}

double gammavariate(double alpha, double beta) {

    return _inst->gammavariate(alpha, beta);
}

double stdgamma(double alpha, double ainv, double bbb, double ccc) {

    return _inst->stdgamma(alpha, ainv, bbb, ccc);
}

double gauss(double mu, double sigma) {

    return _inst->gauss(mu, sigma);
}

double betavariate(double alpha, double beta) {

    return _inst->betavariate(alpha, beta);
}

double paretovariate(double alpha) {

    return _inst->paretovariate(alpha);
}

double weibullvariate(double alpha, double beta) {

    return _inst->weibullvariate(alpha, beta);
}

int getrandbits(int k) {

    return _inst->getrandbits(k);
}

double triangular(double low, double high, double mode) {
    return _inst->triangular(low, high, mode);
}
double triangular(double low, double high, __ss_int mode) {
    return _inst->triangular(low, high, mode);
}
double triangular(double low, double high, void *mode) {
    return _inst->triangular(low, high, mode);
}

} // module namespace

