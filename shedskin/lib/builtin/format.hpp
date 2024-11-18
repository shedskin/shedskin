/* Copyright 2005-2023 Mark Dufour and contributors; License Expat (See LICENSE) */

/* printf-style string formatting */

#ifndef SS_FORMAT_HPP
#define SS_FORMAT_HPP

template <class T> void *__mod_dict_arg(T, str *) { return NULL; }
template <class V> V __mod_dict_arg(dict<str *, V> *d, str *name) {
    return d->__getitem__(name);
}
template <class V> V __mod_dict_arg(dict<bytes *, V> *d, str *name) {
    bytes *key = new bytes(); // optimize
    key->unit = name->unit;
    return d->__getitem__(key);
}

template <class T> void __mod_int(str *, size_t &, T, char, __ss_int, __ss_int, bool) {}
template<> inline void __mod_int(str *result, size_t &, __ss_int arg, char f_flag, __ss_int f_width, __ss_int f_precision, bool f_zero) {
    std::string sabs = std::to_string(__abs(arg));
    if (arg < 0)
        result->unit += "-";
    else if (f_flag == '+')
        result->unit += "+";
    else if (f_flag == ' ')
        result->unit += " ";
    if (f_precision != -1 && f_precision-((__ss_int)sabs.size()) > 0) {
        result->unit += std::string((size_t)f_precision-sabs.size(), '0');
    } else if (f_width != -1 && f_width-((__ss_int)sabs.size()) > 0) {
        result->unit += std::string((size_t)f_width-sabs.size(), f_zero? '0' : ' ');
    }
    result->unit += sabs;
}
template<> inline void __mod_int(str *result, size_t &pos, __ss_float arg, char f_flag, __ss_int f_width,__ss_int f_precision, bool f_zero) {
    __mod_int(result, pos, (__ss_int)arg, f_flag, f_width, f_precision, f_zero);
}

// TODO same as mod_int different base?
template <class T> void __mod_oct(str *, size_t &, T, char, __ss_int, __ss_int, bool) {}
template<> inline void __mod_oct(str *result, size_t &, __ss_int arg, char f_flag, __ss_int f_width, __ss_int f_precision, bool f_zero) {
    __GC_STRING sabs = __str(__abs(arg), (__ss_int)8)->unit;
    if (arg < 0)
        result->unit += "-";
    else if (f_flag == '+')
        result->unit += "+";
    else if (f_flag == ' ')
        result->unit += " ";
    if (f_precision != -1 && f_precision-((__ss_int)sabs.size()) > 0) {
        result->unit += std::string((size_t)f_precision-sabs.size(), '0');
    } else if (f_width != -1 && f_width-((__ss_int)sabs.size()) > 0) {
        result->unit += std::string((size_t)f_width-sabs.size(), f_zero? '0' : ' ');
    }
    result->unit += sabs;
}

// TODO same as mod_int different base? almost, upper/lower x different
template <class T> void __mod_hex(str *, size_t &, char, T, char, __ss_int, __ss_int, bool) {}
template<> inline void __mod_hex(str *result, size_t &, char c, __ss_int arg, char f_flag, __ss_int f_width, __ss_int f_precision, bool f_zero) {
    __GC_STRING sabs;
    if (c == 'x')
       sabs = __str(__abs(arg), (__ss_int)16)->unit;
    else
       sabs = __str(__abs(arg), (__ss_int)16)->upper()->unit;
    if (arg < 0)
        result->unit += "-";
    else if (f_flag == '+')
        result->unit += "+";
    else if (f_flag == ' ')
        result->unit += " ";

    if (f_precision != -1 && f_precision-((__ss_int)sabs.size()) > 0) {
        result->unit += std::string((size_t)f_precision-sabs.size(), '0');
    } else if (f_width != -1 && f_width-((__ss_int)sabs.size()) > 0) {
        result->unit += std::string((size_t)f_width-sabs.size(), f_zero? '0' : ' ');
    }
    result->unit += sabs;
}

template <class T> void __mod_float(str *, size_t &, char, T, char, __ss_int, __ss_int, bool) {}
template<> inline void __mod_float(str *result, size_t &, char c, __ss_float arg, char f_flag, __ss_int, __ss_int f_precision, bool) {
    std::stringstream t;
    if (arg > 0) {
        if (f_flag == '+')
            result->unit += "+";
        else if (f_flag == ' ')
            result->unit += " ";
    }
    if(c == 'f') {
        t.setf(std::ios::fixed);
        if (f_precision != -1)
            t.precision(f_precision);
        else
            t.precision(6);
        t << arg;
    } else if(c == 'g') {
        t.setf(std::ios::fixed);
        if (f_precision > 0)
            t.precision(f_precision-1);
        else
            t.precision(5);
        t << arg;
    } else if(c == 'e') {
        char num[64];
        snprintf(num, 64, "%.6e", arg); // TODO use f_precision without generating warnings..
        t << num;
    }
    result->unit += t.str();
}
template<> inline void __mod_float(str *result, size_t &pos, char c, __ss_int arg, char f_flag, __ss_int f_width, __ss_int f_precision, bool f_zero) {
    __mod_float(result, pos, c, (__ss_float)arg, f_flag, f_width, f_precision, f_zero);
}

template <class T> void __mod_str(str *result, size_t &, char c, T arg, __ss_int f_precision) {
    std::string s;
    if(c=='s')
        s = __str(arg)->unit;
    else
        s = repr(arg)->unit; // TODO escaping?

    if (f_precision == -1)
        result->unit += s;
    else
        result->unit += s.substr(0, (size_t)f_precision);
}
template<> inline void __mod_str(str *result, size_t &, char c, bytes *arg, __ss_int f_precision) {
    std::string s;
    if(c=='s')
        s = arg->unit;
    else
        s = repr(arg)->unit; // TODO escaping?

    if (f_precision == -1)
        result->unit += s;
    else
        result->unit += s.substr(0, (size_t)f_precision);
}

template <class T> void __mod_char(str *, size_t &, char, T) {}
template<> inline void __mod_char(str *result, size_t &, char, __ss_int arg) {
    if(arg < 0 || arg > 255)
        throw new OverflowError(new str("%c arg not in range(256)"));
    result->unit += (char)arg;
}
template<> inline void __mod_char(str *result, size_t &, char, str *arg) {
    if(arg->unit.size() != 1)
        throw new TypeError(new str("%c requires int or char"));
    result->unit += arg->unit[0];
}

template<class T> void __mod_one(str *fmt, size_t fmtlen, size_t &j, str *result, size_t &, T arg) {
    size_t namepos, startpos;
    str *name = NULL;
    std::string fmtchars = "0123456789# -+.*";

    for(; j<fmtlen;) {
        char c = fmt->unit[j++];
        if(c != '%') {
            result->unit += c;
            continue;
        }

        if(j >= fmtlen)
            throw new ValueError(new str("incomplete format"));

        /* %% */
        if(fmt->unit[j] == '%') {
            result->unit += '%';
            j++;
            continue;
        }

        /* %(name) */
        if(fmt->unit[j] == '(') {
            j++;
            namepos = j;
            while(fmt->unit[j++] != ')')
                ;
            name = new str(fmt->unit.c_str()+namepos, j-namepos-1);
        }
        else
            name = NULL;

        /* extract format string e.g. '%.2f' */
        startpos = j;
        size_t pos = fmt->unit.find_first_not_of(fmtchars, j);
        if(pos == std::string::npos)
            throw new ValueError(new str("incomplete format"));
        j += (size_t)(pos-startpos);

        c = fmt->unit[j++];

        std::string fstr = "%";
        fstr += fmt->unit.substr(startpos, j-startpos-1);
        if(fstr.find('*') != std::string::npos)
            throw new ValueError(new str("unsupported format character"));

        /* extract flags, width, precision */
        char f_flag = 'x';
        char d;
        __ss_int f_width = -1;
        __ss_int f_precision = -1;
        bool f_zero = false;
        bool dot = false;

        for(size_t k=1; k<fstr.size(); k++) {
            d = fstr[k];

            switch(d) {
                case '-':
                case '+':
                case ' ':
                    f_flag = d;
                    break;

                case '.':
                    dot = true;
                    break;

                case '0':
                case '1':
                case '2':
                case '3':
                case '4':
                case '5':
                case '6':
                case '7':
                case '8':
                case '9':
                    if (dot) {
                        if (f_precision == -1)
                            f_precision = (__ss_int)(d - '0');
                        else
                            f_precision = 10*f_precision + (__ss_int)(d - '0');
                    } else {
                        if (f_width == -1) {
                            if (d == '0')
                                f_zero = true;
                            f_width = (__ss_int)(d - '0');
                        } else
                            f_width = 10*f_width + (__ss_int)(d - '0');
                    }
                    break;
            }
        }

        /* check format flag */
        switch(c) {
            case 'd':
            case 'i':
            case 'u':
                if(name) {
                    __mod_int(result, pos, __mod_dict_arg(arg, name), f_flag, f_width, f_precision, f_zero);
                    break;
                } else {
                    __mod_int(result, pos, arg, f_flag, f_width, f_precision, f_zero);
                    return;
                }

            case 'o':
                if(name) {
                    __mod_oct(result, pos, __mod_dict_arg(arg, name), f_flag, f_width, f_precision, f_zero);
                    break;
                } else {
                    __mod_oct(result, pos, arg, f_flag, f_width, f_precision, f_zero);
                    return;
                }

            case 'x':
            case 'X':
                if(name) {
                    __mod_hex(result, pos, c, __mod_dict_arg(arg, name), f_flag, f_width, f_precision, f_zero);
                    break;
                } else {
                    __mod_hex(result, pos, c, arg, f_flag, f_width, f_precision, f_zero);
                    return;
                }

            case 'e':
            case 'E':
            case 'f':
            case 'F':
            case 'g':
            case 'G':
                if(name) {
                    __mod_float(result, pos, c, __mod_dict_arg(arg, name), f_flag, f_width, f_precision, f_zero);
                    break;
                } else {
                    __mod_float(result, pos, c, arg, f_flag, f_width, f_precision, f_zero);
                    return;
                }
                break;

            case 's':
            case 'r':
                if(name) {
                    __mod_str(result, pos, c, __mod_dict_arg(arg, name), f_precision);
                    break;
                } else {
                    __mod_str(result, pos, c, arg, f_precision);
                    return;
                }

            case 'c':
                if(name) {
                    __mod_char(result, pos, c, __mod_dict_arg(arg, name));
                    break;
                } else {
                    __mod_char(result, pos, c, arg);
                    return;
                }

            default:
                throw new ValueError(new str("unsupported format character"));
        }
    }
}

template<class ... Args> str *__mod6(str *fmt, int, Args ... args) {
    str *result = new str();
    size_t pos = 0;
    size_t fmtlen = fmt->unit.size();
    size_t j = 0;

    (__mod_one(fmt, fmtlen, j, result, pos, args), ...);

    for(; j < fmtlen; j++) {
        char c = fmt->unit[j];
        result->unit += c;
        if(c=='%' and j+1<fmtlen and fmt->unit[j+1] == '%')
            j++;
    }

    return result;
}

template<class A, class B> str *__modtuple(str *fmt, tuple2<A,B> *t) {
    return __mod6(fmt, 2, t->__getfirst__(), t->__getsecond__());
}

template<class T> str *__modtuple(str *fmt, tuple2<T,T> *t) {
    str *result = new str();
    size_t pos = 0;
    size_t fmtlen = fmt->unit.size();
    size_t j = 0;

    size_t l = t->units.size();
    for(size_t i=0;i<l; i++)
        __mod_one(fmt, fmtlen, j, result, pos, t->units[i]);

    for(; j < fmtlen; j++) {
        char c = fmt->unit[j];
        result->unit += c;
        if(c=='%' and j+1<fmtlen and fmt->unit[j+1] == '%') // TODO incomplete format exception if % is last char
            j++;
    }

    return result;
}

/* TODO optimize bytes variants */

template<class ... Args> bytes *__mod6(bytes *fmt, int, Args ... args) {
    str *result = new str();
    bytes *r = new bytes();
    size_t pos = 0;
    size_t fmtlen = fmt->unit.size();
    size_t j = 0;
    str *sfmt = new str();
    sfmt->unit = fmt->unit;

    (__mod_one(sfmt, fmtlen, j, result, pos, args), ...);

    for(; j < fmtlen; j++) {
        char c = fmt->unit[j];
        result->unit += c;
        if(c=='%' and j+1<fmtlen and fmt->unit[j+1] == '%')
            j++;
    }

    r->unit = result->unit;
    return r;
}

template<class T> bytes *__modtuple(bytes *bfmt, tuple2<T,T> *t) {
    str *fmt = new str();
    fmt->unit = bfmt->unit;

    str *result = __modtuple(fmt, t);

    bytes *r = new bytes();
    r->unit = result->unit;
    return r;
}

template<class A, class B> bytes *__modtuple(bytes *fmt, tuple2<A,B> *t) {
    return __mod6(fmt, 2, t->__getfirst__(), t->__getsecond__());
}

#endif
