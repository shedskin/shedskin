/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __MMAP_HPP
#define __MMAP_HPP

#ifdef WIN32
#include <windows.h>
#endif /* WIN32 */

#include "builtin.hpp"

using namespace __shedskin__;
/**
 * mmap module for Shed Skin.
 */
namespace __mmap__
{
extern __ss_int ALLOCATIONGRANULARITY;
extern const __ss_int
PAGESIZE,    /* 4096 bytes usually. */

/* Access */
ACCESS_READ,   /* Read-only memory.     */
ACCESS_WRITE,  /* Write-through memory. */
ACCESS_COPY,   /* Copy-on-write memory. */

/* Prot */
PROT_READ,     /* Page can be read.     */
PROT_WRITE,    /* Page can be written.  */
PROT_EXEC,     /* Page can be executed. */

/* Flags */
MAP_SHARED,    /* Share changes.        */
MAP_PRIVATE,   /* Changes are private.  */
MAP_ANONYMOUS, /* Don't use a file.     */
MAP_ANON;      /* Syn. MAP_ANONYMOUS.   */

extern str *__name__;
extern class_ *cl_mmap;

#ifndef WIN32 /* UNIX */
extern __ss_int default_0,
                default_1;
#else
extern str *default_2;
#endif /* WIN32 */

class __mmapiter;

/**
 * mmap class.
 * ref: http://docs.python.org/library/mmap.html
 */
class mmap: public pyobj
{
  public:
    typedef char* iterator;


    static const __ss_int all = -1;
    /**
      * Constructors.
      */
#ifndef WIN32
    mmap(int __ss_fileno,
         __ss_int length,
         __ss_int flags = MAP_SHARED,
         __ss_int prot  = PROT_READ | PROT_WRITE,
         __ss_int access = 0,
         __ss_int offset = 0) : closed(false), fd(-1)
    {
        this->__class__ = cl_mmap;
        __init__(__ss_fileno, length,
                 flags, prot, access, offset);
    }
    void *__init__(int __ss_fileno, __ss_int length,
                   __ss_int flags,  __ss_int prot,
                   __ss_int access, __ss_int offset);
#else /* WIN32 */
    mmap(int __ss_fileno,
         __ss_int length,
         str *tagname = 0,
         __ss_int access = 0,
         __ss_int offset = 0) : closed(false), file_handle(INVALID_HANDLE_VALUE)
    {
        this->__class__ = cl_mmap;
        __init__(__ss_fileno, length,
                 tagname, access, offset);
    }
    void *__init__(int __ss_fileno, __ss_int length,
                   str *tagname, __ss_int access,
                   __ss_int offset);
#endif /* WIN32 */
    // mmap
    void *   close();
    void     __enter__();
    void     __exit__();
    __ss_int flush(__ss_int offset=0, __ss_int size=-1);
    __ss_int find(bytes *s, __ss_int start=-1, __ss_int end=-1);
    void *   move(__ss_int destination, __ss_int source, __ss_int count);
    bytes *    read(__ss_int size=all);
    __ss_int   read_byte();
    bytes *    readline(__ss_int size=all, const char eol='\n');
    void *   resize(__ss_int newsize);
    __ss_int rfind(bytes *string, __ss_int start=-1, __ss_int end=-1);
    void *   seek(__ss_int offset, __ss_int whence=0);
    __ss_int size();
    __ss_int tell();
    void *   write(bytes *string);
    void *   write_byte(__ss_int vale);

    // pyraw
    __ss_int __len__();
    char * data() { return m_begin; }

    // pyiter
    __ss_bool __contains__(bytes *s);
    __iter<bytes *> *__iter__();

    // pyseq
    __ss_int __getitem__(__ss_int index);
    void *__setitem__(__ss_int index, __ss_int value);
    bytes *__slice__(__ss_int kind, __ss_int lower, __ss_int upper, __ss_int step);
    void *__setslice__(__ss_int kind, __ss_int lower, __ss_int upper, __ss_int step, bytes *sequence);

    // impl
    inline size_t __size()  const { return (m_end - m_begin); }
    inline bool   __eof()   const { return (m_position >= m_end); }

    typedef bytes * for_in_unit;
    typedef size_t for_in_loop;

    inline size_t for_in_init() { return 0; }
    inline bool for_in_has_next(size_t i) const { return i < __size(); }
    inline bytes *for_in_next(size_t &i) const { return new bytes(__char_cache[(unsigned char)(m_begin[i++])]->unit); }

  private:
    iterator m_begin;
    iterator m_end;
    iterator m_position;

    bool closed;
#ifndef WIN32
    int fd;
    __ss_int flags;
    __ss_int prot;
#else /* WIN32 */
    HANDLE map_handle;
    HANDLE file_handle;
    char * tagname;
    size_t offset;
#endif /* WIN32 */
    __ss_int access;

    void *__raise_if_closed();
    void *__raise_if_closed_or_not_readable();
    void *__raise_if_closed_or_not_writable();
    void *__seek_failed();

    inline size_t __subscript(__ss_int index, bool include_end=false) const;
    inline __ss_int __clamp(__ss_int index) const;
    inline size_t __tell() const { return (m_position - m_begin); }
    iterator __next_line(const char eol);
    __ss_int __find(const __GC_STRING& needle, __ss_int start, __ss_int end, bool reverse=false);
};

/**
 * mmap byte iterator.
 */
class __mmapiter : public __iter<bytes *>
{
  public:
    mmap *map;
    __mmapiter(mmap *map) : map(map) {}
    bytes *__next__();
};

void __init();

} // __mmap__ namespace

#endif // __MMAP_HPP
