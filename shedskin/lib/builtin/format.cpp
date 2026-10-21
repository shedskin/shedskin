/* Copyright 2005-2023 Mark Dufour and contributors; License Expat (See LICENSE) */

/* TODO use in str/bytes __repr__ */
str *__escape_bytes(pyobj *p) {
    bytes *t = (bytes *)p;

    std::stringstream ss;
    __GC_STRING separator = "\\\n\r\t";
    __GC_STRING let = "\\nrt";

    size_t hasq = t->unit.find('\'');
    size_t hasd = t->unit.find('\"');

    if (hasq != std::string::npos && hasd != std::string::npos) {
        separator += "'"; let += "'";
    }

    for(size_t i=0; i<t->unit.size(); i++)
    {
        char c = t->unit[i];
        size_t k;

        if((k = separator.find_first_of(c)) != std::string::npos)
            ss << "\\" << let[k];
        else {
            int j = (int)((unsigned char)c);

            if(j<16)
                ss << "\\x0" << std::hex << j;
            else if(j>=' ' && j<='~')
                ss << (char)j;
            else
                ss << "\\x" << std::hex << j;
        }
    }

    return new str(ss.str().c_str());
}

/* format specs (f-strings and str.format) */

/* [[fill]align][sign][z][#][0][width][grouping][.precision][type] */
struct __fmt_spec {
    __ss_char fill;
    char align;     /* '<', '>', '=' or '^' */
    char sign;      /* '+', '-' or ' ', 0 if omitted */
    char flag;      /* __SS_FMT_PLUS, __SS_FMT_SPACE and __SS_FMT_ALT, as for %-formatting */
    bool no_neg_0;  /* 'z' */
    char grouping;  /* ',' or '_', 0 if omitted */
    int64_t width, precision; /* -1 if omitted (Py_ssize_t in CPython) */
    __ss_char type; /* presentation type */
};

/* a presentation type in errors, as CPython shows it */
static str *__fmt_type_str(__ss_char type) {
    if (type > 32 && type < 128)
        return __char_str(type);
    std::stringstream ss;
    ss << "\\x" << std::hex << (unsigned int)type;
    return new str(ss.str().c_str());
}

static inline bool __fmt_is_align(__ss_char c) {
    return c == '<' || c == '>' || c == '=' || c == '^';
}

/* a width or precision, as in CPython up to PY_SSIZE_T_MAX */
static int64_t __fmt_number(const __GC_STR &s, size_t &i) {
    int64_t value = 0;
    for (; i < s.size() && s[i] >= '0' && s[i] <= '9'; i++) {
        int d = (int)(s[i] - '0');
        if (value > (INT64_MAX - d) / 10)
            throw new ValueError(new str("Too many decimal digits in format string"));
        value = 10*value + d;
    }
    return value;
}

/* the presentation type is checked by the caller (tname is for errors), apart
   from whether it allows grouping */
static void __fmt_parse(str *spec, __fmt_spec &fs, char default_type, char default_align, const char *tname) {
    const __GC_STR &s = spec->unit;
    size_t n = s.size(), i = 0;
    fs.fill = ' ';
    fs.align = default_align;
    fs.sign = fs.flag = fs.grouping = 0;
    fs.no_neg_0 = false;
    fs.width = fs.precision = -1;
    fs.type = (__ss_char)default_type;

    bool fill_given = false, align_given = false;
    if (n >= 2 && __fmt_is_align(s[1])) {
        fs.fill = s[0];
        fs.align = (char)s[1];
        fill_given = align_given = true;
        i = 2;
    } else if (n >= 1 && __fmt_is_align(s[0])) {
        fs.align = (char)s[0];
        align_given = true;
        i = 1;
    }
    /* sign ('-' is the default) */
    if (i < n && (s[i] == '+' || s[i] == '-' || s[i] == ' ')) {
        fs.sign = (char)s[i];
        if (s[i] == '+')
            fs.flag |= __SS_FMT_PLUS;
        else if (s[i] == ' ')
            fs.flag |= __SS_FMT_SPACE;
        i++;
    }
    if (i < n && s[i] == 'z') {
        fs.no_neg_0 = true;
        i++;
    }
    if (i < n && s[i] == '#') {
        fs.flag |= __SS_FMT_ALT;
        i++;
    }
    /* '0': fill with zeros, for numbers between sign and digits (unless an
       alignment is given) */
    if (!fill_given && i < n && s[i] == '0') {
        fs.fill = '0';
        if (!align_given && default_align == '>')
            fs.align = '=';
        i++;
    }
    if (i < n && s[i] >= '0' && s[i] <= '9')
        fs.width = __fmt_number(s, i);
    if (i < n && (s[i] == ',' || s[i] == '_')) {
        fs.grouping = (char)s[i++];
        if (i < n && (s[i] == ',' || s[i] == '_') && s[i] != (__ss_char)fs.grouping)
            throw new ValueError(new str("Cannot specify both ',' and '_'."));
    }
    if (i < n && s[i] == '.') {
        i++;
        if (i == n || s[i] < '0' || s[i] > '9')
            throw new ValueError(new str("Format specifier missing precision"));
        fs.precision = __fmt_number(s, i);
    }
    if (n - i > 1)
        throw new ValueError(__add_strs(5, new str("Invalid format specifier '"), spec, new str("' for object of type '"), new str(tname), new str("'")));
    if (i < n)
        fs.type = s[i];

    if (fs.grouping) {
        switch (fs.type) {
            case 0: case 'd': case 'e': case 'E': case 'f': case 'F': case 'g': case 'G': case '%':
                break;
            case 'b': case 'o': case 'x': case 'X': /* every four digits */
                if (fs.grouping == '_')
                    break;
                [[fallthrough]];
            default:
                throw new ValueError(__add_strs(5, new str("Cannot specify '"), __char_str((__ss_char)fs.grouping), new str("' with '"), __fmt_type_str(fs.type), new str("'.")));
        }
    }
}

static void __fmt_unknown(__ss_char type, const char *tname) {
    throw new ValueError(__add_strs(5, new str("Unknown format code '"), __fmt_type_str(type), new str("' for object of type '"), new str(tname), new str("'")));
}

/* group the first 'ndigits' of 'num' (per 'every' digits), and pad and align
   'pre' (sign and base prefix) and 'num'; zero-padding between them is
   grouped as well, as it is part of the number */
static str *__fmt_align(const __fmt_spec &fs, const __GC_STR &pre, const __GC_STR &num, size_t ndigits, size_t every) {
    size_t width = fs.width == -1 ? 0 : (size_t)fs.width;
    str *result = new str();
    __GC_STR grouped;
    const __GC_STR *body = &num;
    if (fs.grouping && ndigits) {
        size_t rest = num.size() - ndigits, need = 0;
        if (fs.fill == '0' && fs.align == '=' && width > pre.size() + rest)
            need = width - pre.size() - rest;
        for (size_t k = 0; k < ndigits || grouped.size() < need; k++) {
            if (k && k % every == 0)
                grouped += (__ss_char)fs.grouping;
            grouped += k < ndigits ? num[ndigits-1-k] : (__ss_char)'0';
        }
        std::reverse(grouped.begin(), grouped.end());
        grouped.append(num, ndigits, rest);
        body = &grouped;
    }

    size_t len = pre.size() + body->size();
    size_t pad = width > len ? width - len : 0, left = 0;
    if (fs.align == '>')
        left = pad;
    else if (fs.align == '^')
        left = pad / 2;
    result->unit.reserve(len + pad);
    if (fs.align == '=') {
        result->unit += pre;
        result->unit.append(pad, fs.fill);
    } else {
        result->unit.append(left, fs.fill);
        result->unit += pre;
    }
    result->unit += *body;
    if (fs.align != '=')
        result->unit.append(pad - left, fs.fill);
    return result;
}

/* like float.__format__ (for a checked presentation type) */
static str *__format_float(__ss_float arg, const __fmt_spec &fs) {
    if (fs.precision > __SS_FMT_MAX_PRECISION)
        throw new ValueError(new str("precision too big"));
    char type = fs.type == 'n' ? 'g' : (char)fs.type; /* 'n' is 'g' in the C locale */
    str tmp;
    __fmt_float(&tmp, type, arg, fs.flag, -1, fs.precision, false);
    const __GC_STR &s = tmp.unit;
    size_t p = (s[0] == '-' || s[0] == '+' || s[0] == ' ') ? 1 : 0;
    __GC_STR pre(s, 0, p), num(s, p);
    size_t ndigits = 0; /* before the decimal point (none for inf/nan) */
    while (ndigits < num.size() && num[ndigits] >= '0' && num[ndigits] <= '9')
        ndigits++;
    /* 'z': negative zero (after rounding) becomes positive zero */
    if (fs.no_neg_0 && p && s[0] == '-' && ndigits) {
        size_t i = 0;
        for (; i < num.size() && (num[i] == '0' || num[i] == '.'); i++);
        if (i == num.size() || num[i] == 'e' || num[i] == 'E' || num[i] == '%')
            pre = __gcs(__mod_sign(false, fs.flag));
    }
    return __fmt_align(fs, pre, num, ndigits, 3);
}

/* like int.__format__ */
static str *__format_int(__ss_int arg, str *spec, const char *tname) {
    __fmt_spec fs;
    __fmt_parse(spec, fs, 'd', '>', tname);
    int base = 10;
    switch (fs.type) {
        case 'e': case 'E': case 'f': case 'F': case 'g': case 'G': case '%':
            return __format_float((__ss_float)arg, fs);
        case 'd': case 'n': case 'c': break; /* 'n' is 'd' in the C locale */
        case 'b': base = 2; break;
        case 'o': base = 8; break;
        case 'x': case 'X': base = 16; break;
        default:
            __fmt_unknown(fs.type, tname);
    }
    if (fs.precision != -1)
        throw new ValueError(new str("Precision not allowed in integer format specifier"));
    if (fs.no_neg_0)
        throw new ValueError(new str("Negative zero coercion (z) not allowed in integer format specifier"));
    if (fs.type == 'c') {
        if (fs.sign)
            throw new ValueError(new str("Sign not allowed with integer format specifier 'c'"));
        if (fs.flag & __SS_FMT_ALT)
            throw new ValueError(new str("Alternate form (#) not allowed with integer format specifier 'c'"));
        if (arg < 0 || arg > 0x10ffff)
            throw new OverflowError(new str("%c arg not in range(0x110000)"));
        return __fmt_align(fs, __GC_STR(), __GC_STR(1, (__ss_char)arg), 0, 3);
    }
    str tmp;
    __mod_integer(&tmp, arg, base, fs.type == 'n' ? 'd' : (char)fs.type, fs.flag, -1, -1, false);
    const __GC_STR &s = tmp.unit;
    size_t p = (s[0] == '-' || s[0] == '+' || s[0] == ' ') ? 1 : 0;
    if ((fs.flag & __SS_FMT_ALT) && base != 10)
        p += 2; /* 0b, 0o, 0x or 0X */
    __GC_STR num(s, p);
    return __fmt_align(fs, __GC_STR(s, 0, p), num, num.size(), base == 10 ? 3 : 4);
}

str *__format(__ss_int arg, str *spec) {
    return __format_int(arg, spec, "int");
}

str *__format(__ss_bool arg, str *spec) {
    if (spec->unit.empty())
        return __str(arg);
    return __format_int((__ss_int)arg.value, spec, "bool");
}

str *__format(__ss_float arg, str *spec) {
    __fmt_spec fs;
    __fmt_parse(spec, fs, 0, '>', "float");
    switch (fs.type) {
        case 0: case 'e': case 'E': case 'f': case 'F': case 'g': case 'G': case 'n': case '%': break;
        default:
            __fmt_unknown(fs.type, "float");
    }
    return __format_float(arg, fs);
}

/* left-justified by default; '0' fills with zeros, as in CPython 3.10 and later */
str *__format(str *arg, str *spec) {
    if (spec->unit.empty())
        return arg;
    __fmt_spec fs;
    __fmt_parse(spec, fs, 's', '<', "str");
    if (fs.type != 's')
        __fmt_unknown(fs.type, "str");
    if (fs.sign)
        throw new ValueError(new str(fs.sign == ' ' ? "Space not allowed in string format specifier" : "Sign not allowed in string format specifier"));
    if (fs.no_neg_0)
        throw new ValueError(new str("Negative zero coercion (z) not allowed in string format specifier"));
    if (fs.flag & __SS_FMT_ALT)
        throw new ValueError(new str("Alternate form (#) not allowed in string format specifier"));
    if (fs.align == '=')
        throw new ValueError(new str("'=' alignment not allowed in string format specifier"));
    size_t len = arg->unit.size();
    if (fs.precision != -1 && (size_t)fs.precision < len)
        len = (size_t)fs.precision;
    if (len == arg->unit.size() && (fs.width == -1 || (size_t)fs.width <= len))
        return arg;
    return __fmt_align(fs, __GC_STR(), arg->unit.substr(0, len), 0, 3);
}

/* a part of a complex number, as for float.__format__ except that 'repr'
   omits the '.0' of an integral value (no Py_DTSF_ADD_DOT_0 in CPython) */
static __GC_STR __fmt_complex_part(__ss_float arg, const __fmt_spec &fs, bool repr) {
    __GC_STR s = __format_float(arg, fs)->unit;
    size_t n = s.size();
    if (repr && n >= 2 && s[n-2] == '.' && s[n-1] == '0')
        s.erase(n - ((fs.flag & __SS_FMT_ALT) ? 1 : 2));
    return s;
}

/* like complex.__format__, which is also repr() for an empty spec */
str *__format(complex arg, str *spec) {
    __fmt_spec fs;
    __fmt_parse(spec, fs, 0, '>', "complex");
    switch (fs.type) {
        case 0: case 'e': case 'E': case 'f': case 'F': case 'g': case 'G': case 'n': break;
        default:
            __fmt_unknown(fs.type, "complex");
    }
    if (fs.precision > __SS_FMT_MAX_PRECISION)
        throw new ValueError(new str("precision too big"));
    if (fs.fill == '0')
        throw new ValueError(new str("Zero padding is not allowed in complex format specifier"));
    if (fs.align == '=')
        throw new ValueError(new str("'=' alignment flag is not allowed in complex format specifier"));

    /* no presentation type: like str(), so a positive zero real part is
       omitted, and else there are parentheses */
    bool repr = false, skip_re = false, parens = false;
    if (fs.type == 0) {
        skip_re = arg.real == 0 && !std::signbit(arg.real);
        parens = !skip_re;
        if (fs.precision == -1)
            repr = true;
        else
            fs.type = 'g';
    }

    /* the parts without padding, the imaginary part always with a sign
       (unless it is on its own) */
    __fmt_spec part = fs;
    part.fill = ' ';
    part.align = '<';
    part.width = -1;
    __GC_STR num;
    if (!skip_re) {
        num += __fmt_complex_part(arg.real, part, repr);
        part.sign = '+';
        part.flag |= __SS_FMT_PLUS;
    }
    num += __fmt_complex_part(arg.imag, part, repr);
    num += 'j';
    if (parens) {
        num.insert(num.begin(), '(');
        num += ')';
    }
    fs.grouping = 0; /* done for each part */
    return __fmt_align(fs, __GC_STR(), num, 0, 3);
}
