/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef SS_FILE_HPP
#define SS_FILE_HPP

struct __file_options {
    char lastchar;
    int space;
    bool universal_mode;
    bool cr;
    __file_options() : lastchar('\n'), space(0), universal_mode(false), cr(false) {}
};

class file_binary;

class file : public __iter<str *> {
public:
    str *name;
    str *mode;

    FILE *f;
    file_binary *buffer;

    __ss_int closed;
    __file_options options;
    __GC_VECTOR(char) __read_cache;

    file(FILE *g=0) : f(g) {}
    file(str *name, str *mode=0);

    virtual void * close();
    virtual void * flush();
    virtual int  __ss_fileno();
    virtual __ss_bool isatty();
    virtual str *  read(int n=-1);
    virtual str *  readline(int n=-1);
    list<str *> *  readlines(__ss_int size_hint=-1);
    virtual void * seek(__ss_int i, __ss_int w=0);
    virtual __ss_int tell();
    virtual void * truncate(int size);
    virtual void * write(str *s);
    virtual void * writelines(pyiter<str *> *iter);
    __iter<str *> *xreadlines();
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
};

/* TODO file<bytes *> template? */

class file_binary : public __iter<bytes *> {
public:
    str *name;
    str *mode;

    FILE *f;
    __ss_int closed;
    __file_options options;
    __GC_VECTOR(char) __read_cache;

    file_binary(FILE *g=0) : f(g) {}
    file_binary(str *name, str *mode=0);

    virtual void * close();
    virtual void * flush();
    virtual int  __ss_fileno();
    virtual __ss_bool isatty();
    virtual bytes *  read(int n=-1);
    virtual bytes *  readline(int n=-1);
    list<bytes *> *  readlines(__ss_int size_hint=-1);
    virtual void * seek(__ss_int i, __ss_int w=0);
    virtual __ss_int tell();
    virtual void * truncate(int size);
    virtual void * write(bytes *b);
    virtual void *writelines(pyiter<bytes *> *iter);
    __iter<bytes *> *xreadlines();
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

file *open(str *name, str *flags = 0);
file *open(bytes *name, str *flags = 0);
file_binary *open_binary(str *name, str *flags = 0);
file_binary *open_binary(bytes *name, str *flags = 0); /* ugly duplication.. use str/byte template? */

extern file *__ss_stdin, *__ss_stdout, *__ss_stderr;

#endif
