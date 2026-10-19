/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* float.hex() and float.fromhex(), following CPython's float_hex and float_fromhex */

str *__ss_hex(__ss_float x) {
    if(std::isnan(x))
        return new str("nan");
    if(std::isinf(x))
        return new str(x < 0 ? "-inf" : "inf");
    if(x == 0.0)
        return new str(std::signbit(x) ? "-0x0.0p+0" : "0x0.0p+0");

    /* normalize so the leading digit is 1, except for subnormals */
    int e;
    double m = std::frexp(std::fabs(x), &e);
    int shift = 1 - std::max(DBL_MIN_EXP - e, 0);
    m = std::ldexp(m, shift);
    e -= shift;

    char digits[(DBL_MANT_DIG + 3) / 4 + 2];
    int si = 0;
    digits[si++] = "0123456789abcdef"[(int)m];
    m -= (int)m;
    digits[si++] = '.';
    for(int i = 0; i < (DBL_MANT_DIG - 1) / 4; i++) {
        m *= 16.0;
        digits[si++] = "0123456789abcdef"[(int)m];
        m -= (int)m;
    }
    digits[si] = '\0';

    char buf[64];
    std::snprintf(buf, sizeof(buf), "%s0x%sp%c%d", x < 0 ? "-" : "", digits, e < 0 ? '-' : '+', e < 0 ? -e : e);
    return new str(buf);
}

namespace __float___ {
    static inline bool __fromhex_space(char c) {
        return c == ' ' || c == '\t' || c == '\n' || c == '\v' || c == '\f' || c == '\r';
    }

    static inline int __fromhex_digit(char c) {
        return __ss_hexdigit[(unsigned char)c];
    }

    /* case-insensitive prefix match against a lowercase word */
    static inline bool __fromhex_word(const char *p, const char *end, const char *word) {
        for(; *word; p++, word++)
            if(p == end || std::tolower((unsigned char)*p) != *word)
                return false;
        return true;
    }

    __ss_float fromhex(void *, str *str_) {
        __GC_BYTES b = __to_utf8(str_->unit);
        const char *s = b.data();
        const char *s_end = s + b.size();
        const char *coeff_start, *coeff_end, *s_store;
        double x = 0.0;
        long exp, top_exp, lsb, key_digit, ndigits, fdigits, i;
        int half_eps, digit;
        bool negate = false, round_up;

        /* leading whitespace */
        while(s < s_end && __fromhex_space(*s))
            s++;

        /* infinities and nans (with optional sign) */
        {
            const char *p = s;
            bool neg = false;
            if(p < s_end && (*p == '-' || *p == '+')) {
                neg = (*p == '-');
                p++;
            }
            if(__fromhex_word(p, s_end, "inf")) {
                p += 3;
                if(__fromhex_word(p, s_end, "inity"))
                    p += 5;
                x = neg ? -INFINITY : INFINITY;
                s = p;
                goto finished;
            }
            if(__fromhex_word(p, s_end, "nan")) {
                x = NAN;
                s = p + 3;
                goto finished;
            }
        }

        /* optional sign */
        if(s < s_end && *s == '-') {
            s++;
            negate = true;
        }
        else if(s < s_end && *s == '+')
            s++;

        /* [0x] */
        s_store = s;
        if(s < s_end && *s == '0') {
            s++;
            if(s < s_end && (*s == 'x' || *s == 'X'))
                s++;
            else
                s = s_store;
        }

        /* coefficient: <integer> [. <fraction>] */
        coeff_start = s;
        while(s < s_end && __fromhex_digit(*s) >= 0)
            s++;
        s_store = s;
        if(s < s_end && *s == '.') {
            s++;
            while(s < s_end && __fromhex_digit(*s) >= 0)
                s++;
            coeff_end = s - 1;
        }
        else
            coeff_end = s;

        /* ndigits = total # of hex digits; fdigits = # after point */
        ndigits = (long)(coeff_end - coeff_start);
        fdigits = (long)(coeff_end - s_store);
        if(ndigits == 0)
            throw new ValueError(new str("invalid hexadecimal floating-point string"));
        if(ndigits > std::min(DBL_MIN_EXP - DBL_MANT_DIG - LONG_MIN/2, LONG_MAX/2 + 1 - DBL_MAX_EXP) / 4)
            throw new ValueError(new str("hexadecimal string too long to convert"));

        /* [p <exponent>] */
        if(s < s_end && (*s == 'p' || *s == 'P')) {
            s++;
            const char *exp_start = s;
            if(s < s_end && (*s == '-' || *s == '+'))
                s++;
            if(!(s < s_end && '0' <= *s && *s <= '9'))
                throw new ValueError(new str("invalid hexadecimal floating-point string"));
            s++;
            while(s < s_end && '0' <= *s && *s <= '9')
                s++;
            exp = std::strtol(__GC_STRING(exp_start, s).c_str(), NULL, 10);
        }
        else
            exp = 0;

        /* for 0 <= j < ndigits, HEX_DIGIT(j) gives the jth most significant digit */
#define HEX_DIGIT(j) __fromhex_digit(*((j) < fdigits ? coeff_end-(j) : coeff_end-1-(j)))

        /* discard leading zeros, and catch extreme overflow and underflow */
        while(ndigits > 0 && HEX_DIGIT(ndigits-1) == 0)
            ndigits--;
        if(ndigits == 0 || exp < LONG_MIN/2) {
            x = 0.0;
            goto finished;
        }
        if(exp > LONG_MAX/2)
            goto overflow_error;

        /* adjust exponent for fractional part */
        exp = exp - 4*fdigits;

        /* top_exp = 1 more than exponent of most sig. bit of coefficient */
        top_exp = exp + 4*(ndigits - 1);
        for(digit = HEX_DIGIT(ndigits-1); digit != 0; digit /= 2)
            top_exp++;

        /* catch almost all nonextreme cases of overflow and underflow here */
        if(top_exp < DBL_MIN_EXP - DBL_MANT_DIG) {
            x = 0.0;
            goto finished;
        }
        if(top_exp > DBL_MAX_EXP)
            goto overflow_error;

        /* lsb = exponent of least significant bit of the *rounded* value */
        lsb = std::max(top_exp, (long)DBL_MIN_EXP) - DBL_MANT_DIG;

        x = 0.0;
        if(exp >= lsb) {
            /* no rounding required */
            for(i = ndigits-1; i >= 0; i--)
                x = 16.0*x + HEX_DIGIT(i);
            x = std::ldexp(x, (int)exp);
            goto finished;
        }

        /* rounding required; key_digit is the index of the hex digit containing the first bit to be rounded away */
        half_eps = 1 << (int)((lsb - exp - 1) % 4);
        key_digit = (lsb - exp - 1) / 4;
        for(i = ndigits-1; i > key_digit; i--)
            x = 16.0*x + HEX_DIGIT(i);
        digit = HEX_DIGIT(key_digit);
        x = 16.0*x + (double)(digit & (16-2*half_eps));

        /* round-half-even */
        if((digit & half_eps) != 0) {
            round_up = false;
            if((digit & (3*half_eps-1)) != 0 || (half_eps == 8 && key_digit+1 < ndigits && (HEX_DIGIT(key_digit+1) & 1) != 0))
                round_up = true;
            else
                for(i = key_digit-1; i >= 0; i--)
                    if(HEX_DIGIT(i) != 0) {
                        round_up = true;
                        break;
                    }
            if(round_up) {
                x += 2*half_eps;
                if(top_exp == DBL_MAX_EXP && x == std::ldexp((double)(2*half_eps), DBL_MANT_DIG))
                    goto overflow_error;
            }
        }
        x = std::ldexp(x, (int)(exp + 4*key_digit));
#undef HEX_DIGIT

      finished:
        /* optional trailing whitespace leading to the end of the string */
        while(s < s_end && __fromhex_space(*s))
            s++;
        if(s != s_end)
            throw new ValueError(new str("invalid hexadecimal floating-point string"));
        return negate ? -x : x;

      overflow_error:
        throw new OverflowError(new str("hexadecimal value too large to represent as a float"));
    }
}
