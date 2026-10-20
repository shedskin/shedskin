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

void __fmt_parse_float(str *spec, char &c, char &f_flag, __ss_int &f_width, __ss_int &f_precision, bool &f_zero) {
    const __GC_STR &s = spec->unit;
    size_t n = s.size(), i = 0;
    f_flag = 0;
    f_width = f_precision = -1;
    f_zero = false;

    /* sign ('-' is the default) */
    if (i < n && (s[i] == '+' || s[i] == '-' || s[i] == ' ')) {
        if (s[i] == '+')
            f_flag |= __SS_FMT_PLUS;
        else if (s[i] == ' ')
            f_flag |= __SS_FMT_SPACE;
        i++;
    }
    if (i < n && s[i] == '#') {
        f_flag |= __SS_FMT_ALT;
        i++;
    }
    /* '0': zero-padding between sign and digits, as for %-formatting */
    if (i < n && s[i] == '0') {
        f_zero = true;
        i++;
    }
    for (; i < n && s[i] >= '0' && s[i] <= '9'; i++)
        f_width = (f_width == -1 ? 0 : 10*f_width) + (__ss_int)(s[i] - '0');
    if (i < n && s[i] == '.') {
        i++;
        if (i == n || s[i] < '0' || s[i] > '9')
            throw new ValueError(new str("Format specifier missing precision"));
        for (f_precision = 0; i < n && s[i] >= '0' && s[i] <= '9'; i++)
            f_precision = 10*f_precision + (__ss_int)(s[i] - '0');
    }

    if (i+1 != n || (s[i] != 'f' && s[i] != 'F'))
        throw new ValueError(__add_strs(3, new str("Invalid format specifier '"), spec, new str("' for object of type 'float'")));
    c = (char)s[i];
}
