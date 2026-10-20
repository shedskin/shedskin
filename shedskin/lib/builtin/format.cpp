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

struct __fmt_spec {
    char type;   /* presentation type, 0 if omitted */
    char sign;   /* '+', '-' or ' ', 0 if omitted */
    char flag;   /* __SS_FMT_PLUS, __SS_FMT_SPACE and __SS_FMT_ALT, as for %-formatting */
    bool zero;   /* '0' */
    __ss_int width, precision; /* -1 if omitted */
};

/* the presentation type is checked by the caller (tname is for errors) */
static void __fmt_parse(str *spec, __fmt_spec &fs, const char *tname) {
    const __GC_STR &s = spec->unit;
    size_t n = s.size(), i = 0;
    fs.type = fs.sign = fs.flag = 0;
    fs.width = fs.precision = -1;
    fs.zero = false;

    /* sign ('-' is the default) */
    if (i < n && (s[i] == '+' || s[i] == '-' || s[i] == ' ')) {
        fs.sign = (char)s[i];
        if (s[i] == '+')
            fs.flag |= __SS_FMT_PLUS;
        else if (s[i] == ' ')
            fs.flag |= __SS_FMT_SPACE;
        i++;
    }
    if (i < n && s[i] == '#') {
        fs.flag |= __SS_FMT_ALT;
        i++;
    }
    /* '0': zero-padding between sign and digits, as for %-formatting */
    if (i < n && s[i] == '0') {
        fs.zero = true;
        i++;
    }
    for (; i < n && s[i] >= '0' && s[i] <= '9'; i++)
        fs.width = (fs.width == -1 ? 0 : 10*fs.width) + (__ss_int)(s[i] - '0');
    if (i < n && s[i] == '.') {
        i++;
        if (i == n || s[i] < '0' || s[i] > '9')
            throw new ValueError(new str("Format specifier missing precision"));
        for (fs.precision = 0; i < n && s[i] >= '0' && s[i] <= '9'; i++)
            fs.precision = 10*fs.precision + (__ss_int)(s[i] - '0');
    }
    if (i < n && s[i] > ' ' && s[i] < 127)
        fs.type = (char)s[i++];

    if (i != n)
        throw new ValueError(__add_strs(5, new str("Invalid format specifier '"), spec, new str("' for object of type '"), new str(tname), new str("'")));
}

static void __fmt_unknown(char type, const char *tname) {
    throw new ValueError(__add_strs(5, new str("Unknown format code '"), __char_str((__ss_char)type), new str("' for object of type '"), new str(tname), new str("'")));
}

/* like int.__format__ (for a non-empty spec) */
static str *__format_int(__ss_int arg, str *spec, const char *tname) {
    __fmt_spec fs;
    __fmt_parse(spec, fs, tname);
    str *result = new str();
    int base = 10;
    switch (fs.type) {
        case 'e': case 'E': case 'f': case 'F': case 'g': case 'G': case '%':
            __fmt_float(result, fs.type, (__ss_float)arg, fs.flag, fs.width, fs.precision, fs.zero);
            return result;
        case 0: case 'd': case 'c': break;
        case 'b': base = 2; break;
        case 'o': base = 8; break;
        case 'x': case 'X': base = 16; break;
        default:
            __fmt_unknown(fs.type, tname);
    }
    if (fs.precision != -1)
        throw new ValueError(new str("Precision not allowed in integer format specifier"));
    if (fs.type == 'c') {
        if (fs.sign)
            throw new ValueError(new str("Sign not allowed with integer format specifier 'c'"));
        if (fs.flag & __SS_FMT_ALT)
            throw new ValueError(new str("Alternate form (#) not allowed with integer format specifier 'c'"));
        __fmt_char(result, arg, fs.flag, fs.width, fs.zero);
    } else
        __mod_integer(result, arg, base, fs.type ? fs.type : 'd', fs.flag, fs.width, fs.precision, fs.zero);
    return result;
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
    __fmt_parse(spec, fs, "float");
    switch (fs.type) {
        case 0: case 'e': case 'E': case 'f': case 'F': case 'g': case 'G': case '%': break;
        default:
            __fmt_unknown(fs.type, "float");
    }
    str *result = new str();
    __fmt_float(result, fs.type, arg, fs.flag, fs.width, fs.precision, fs.zero);
    return result;
}

/* left-justified; '0' zero-fills, as in CPython 3.10 and later */
str *__format(str *arg, str *spec) {
    if (spec->unit.empty())
        return arg;
    __fmt_spec fs;
    __fmt_parse(spec, fs, "str");
    if (fs.type && fs.type != 's')
        __fmt_unknown(fs.type, "str");
    if (fs.sign)
        throw new ValueError(new str(fs.sign == ' ' ? "Space not allowed in string format specifier" : "Sign not allowed in string format specifier"));
    if (fs.flag & __SS_FMT_ALT)
        throw new ValueError(new str("Alternate form (#) not allowed in string format specifier"));
    size_t len = arg->unit.size();
    if (fs.precision != -1 && (size_t)fs.precision < len)
        len = (size_t)fs.precision;
    if (len == arg->unit.size() && (fs.width == -1 || (size_t)fs.width <= len))
        return arg;
    str *result = new str(arg->unit.substr(0, len));
    if (fs.width != -1 && (size_t)fs.width > len)
        result->unit.append((size_t)fs.width - len, fs.zero ? '0' : ' ');
    return result;
}
