/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef SS_FILE_HPP
#define SS_FILE_HPP

struct __file_options {
    char lastchar;
    int space;
    bool universal_mode;
    bool cr;
    bool split_cr; /* newline='': lines also end at '\r' and '\r\n', untranslated */
    __file_options() : lastchar('\n'), space(0), universal_mode(false), cr(false), split_cr(false) {}
};

class file_binary;

class file : public __iter<str *> {
public:
    str *name;
    str *mode;

    FILE *f;
    file_binary *buffer;

    __ss_bool closed = False; /* (also for the constructors that open by name, without gc zeroing) */
    __file_options options;
    __GC_VECTOR(char) __read_cache;

    /* text encoding: open() defaults to utf-8/strict (as CPython 3.15, where
       utf-8 mode is the default); the standard streams use surrogateescape */
    __ss_encoding __encoding = __SS_ENC_UTF8;
    __ss_errors __errors = __SS_ERR_SURROGATEESCAPE;
    bool __bom_pending = false; /* utf-8-sig: write a bom on the first write */

    file(FILE *g=0) : f(g), closed(False) {}
    file(str *name, str *mode=0, str *encoding=0, str *errors=0, str *newline=0);

    virtual void * close();
    virtual void * flush();
    virtual __ss_int  __ss_fileno();
    virtual __ss_bool isatty();
    virtual str *  read(__ss_int n=-1);
    virtual str *  readline(__ss_int n=-1);
    virtual list<str *> *  readlines(__ss_int size_hint=-1);
    virtual __ss_int seek(__ss_int i, __ss_int w=0);
    virtual __ss_int tell();
    virtual __ss_int truncate(__ss_int size);
    virtual __ss_int  write(str *s);
    virtual void * writelines(pyiter<str *> *iter);
    virtual void __enter__();
    virtual void __exit__();

    virtual __iter<str *> *__iter__();
    virtual str *  __next__();

    virtual str *__repr__();

    virtual bool __eof();
    virtual bool __error();

    inline void __check_closed() {
        if(closed)
            throw new ValueError(new str("I/O operation on closed file"));
    }

    str *__decode_cache();
};

/* TODO file<bytes *> template? */

class file_binary : public __iter<bytes *> {
public:
    str *name;
    str *mode;

    FILE *f;
    __ss_bool closed = False; /* (also for the constructors that open by name, without gc zeroing) */
    __file_options options;
    __GC_VECTOR(char) __read_cache;

    file_binary(FILE *g=0) : f(g), closed(False) {}
    file_binary(str *name, str *mode=0);

    virtual void * close();
    virtual void * flush();
    virtual __ss_int  __ss_fileno();
    virtual __ss_bool isatty();
    virtual bytes *  read(__ss_int n=-1);
    virtual bytes *  readline(__ss_int n=-1);
    list<bytes *> *  readlines(__ss_int size_hint=-1);
    virtual __ss_int seek(__ss_int i, __ss_int w=0);
    virtual __ss_int tell();
    virtual __ss_int truncate(__ss_int size);
    virtual __ss_int  write(bytes *b);
    virtual void *writelines(pyiter<bytes *> *iter);
    virtual void __enter__();
    virtual void __exit__();
    virtual str *__repr__();

    virtual __iter<bytes *> *__iter__();
    virtual bytes *  __next__();

    virtual bool __eof();
    virtual bool __error();

    inline void __check_closed() {
        if(closed)
            throw new ValueError(new str("I/O operation on closed file"));
    }
};

#ifdef WIN32
/* file names on Windows: utf-16 for the wide apis (the narrow ones go
   through the lossy ansi code page), lone surrogates kept as in CPython */
inline std::wstring __ss_wpath(str *s) { return __to_utf16<wchar_t>(s->unit); }
#endif

file *open(str *name, str *flags = 0, str *encoding = 0, str *errors = 0, str *newline = 0);
file *open(bytes *name, str *flags = 0, str *encoding = 0, str *errors = 0, str *newline = 0);
file_binary *open_binary(str *name, str *flags = 0, str *encoding = 0, str *errors = 0, str *newline = 0);
file_binary *open_binary(bytes *name, str *flags = 0, str *encoding = 0, str *errors = 0, str *newline = 0); /* ugly duplication.. use str/byte template? */

extern file *__ss_stdin, *__ss_stdout, *__ss_stderr;

#endif
