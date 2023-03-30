/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifdef _MSC_VER
#define NOMINMAX
#endif

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstring>

#ifndef WIN32
#include <sys/mman.h>  // mmap, munmap, msync, mremap
#include <sys/types.h>
#include <sys/stat.h>  // fstat
#include <unistd.h>    // sysconf
#define MMAP_PUSH(constant) __##constant = (constant)
#define HAVE_MREMAP
#else /* WIN32 */
#include <io.h>        // lseek
#define MMAP_PUSH(constant) __##constant = -1
#endif /* WIN32 */

namespace __mmap__
{
enum
{
  MMAP_PUSH(PROT_READ),
  MMAP_PUSH(PROT_WRITE),
  MMAP_PUSH(PROT_EXEC),

  MMAP_PUSH(MAP_SHARED),
  MMAP_PUSH(MAP_PRIVATE),
  MMAP_PUSH(MAP_ANONYMOUS),
  MMAP_PUSH(MAP_ANON)
};
} // __mmap__ namespace

#undef MMAP_PUSH

#undef PROT_READ
#undef PROT_WRITE
#undef PROT_EXEC

#undef MAP_SHARED
#undef MAP_PRIVATE
#undef MAP_ANONYMOUS
#undef MAP_ANON

#include "mmap.hpp"

namespace __mmap__
{
#ifdef WIN32
const __ss_int PAGESIZE = 0x10000;
__ss_int ALLOCATIONGRANULARITY = PAGESIZE;
#else // UNIX
const __ss_int PAGESIZE = sysconf(_SC_PAGE_SIZE);
__ss_int ALLOCATIONGRANULARITY = PAGESIZE;
#endif
const __ss_int
    ACCESS_DEFAULT = 0,
    ACCESS_READ    = 1,
    ACCESS_WRITE   = 2,
    ACCESS_COPY    = 3,

    PROT_READ  = __PROT_READ,
    PROT_WRITE = __PROT_WRITE,
    PROT_EXEC  = __PROT_EXEC,

    MAP_SHARED    = __MAP_SHARED,
    MAP_PRIVATE   = __MAP_PRIVATE,
    MAP_ANONYMOUS = __MAP_ANONYMOUS,
    MAP_ANON      = __MAP_ANON;

// Default parameters.
#ifndef WIN32 /* UNIX */
__ss_int default_0 = MAP_SHARED,
         default_1 = PROT_READ | PROT_WRITE;
#else
str *default_2;
#endif /* WIN32 */

// Error messages.
str *const_0, *const_1, *const_2, *const_3, *const_4, *const_5,
    *const_6, *const_8, *const_9, *const_10, *const_11, *const_12,
    *const_13, *const_14, *const_15, *const_16, *const_17;

str *__name__;
class_ *cl_mmap;

#ifndef WIN32
void *mmap::__init__(int __ss_fileno_, __ss_int length_, __ss_int flags_, __ss_int prot_, __ss_int access_, __ss_int offset_)
{
    if (length_ < 0)
    {
        throw new OverflowError(const_2);
    }
    if (offset_ < 0)
    {
        throw new OverflowError(const_3);
    }
    if ((access_ != ACCESS_DEFAULT and
            (flags_ != MAP_SHARED or
             (prot_ != (PROT_WRITE | PROT_READ)))))
    {
        throw new ValueError(const_4);
    }
    if (access_ == ACCESS_READ)
    {
        flags_ = MAP_SHARED;
        prot_ = PROT_READ;
    }
    else if (access_ == ACCESS_WRITE)
    {
        flags_ = MAP_SHARED;
        prot_ = (PROT_READ|PROT_WRITE);
    }
    else if (access_ == ACCESS_COPY)
    {
        flags_ = MAP_PRIVATE;
        prot_ = (PROT_READ | PROT_WRITE);
    }
    else if (access_ == ACCESS_DEFAULT)
    {
        /* Nothing */;
    }
    else
    {
        throw new ValueError(const_5);
    }
    if (prot_ == PROT_READ)
    {
        access_ = ACCESS_READ;
    }

    if (__ss_fileno_ == -1)
    {
        flags_ |= MAP_ANONYMOUS;
        assert(fd == -1);
    }
    else
    {
        fd = dup(__ss_fileno_);
        if (fd == -1)
        {
            throw new OSError();
        }
        if(length_ == 0)
        {
            struct stat buf;
            if (fstat(fd, &buf) == -1)
            {
                throw new OSError();
            }
            length_ = buf.st_size;
        }
    }

    void *temp = ::mmap(0, length_, prot_, flags_,
                                           fd, offset_);

    if (temp == MAP_FAILED)
    {
        throw OSError();
    }

    m_begin = static_cast<iterator>(temp);

    m_position = m_begin;
    m_end = m_begin + length_;

    flags = flags_;
    prot = prot_;
    access = access_;

    return NULL;
}

void *mmap::close()
{
    if (not closed)
    {
        if (fd >= 0)
            ::close(fd);

        ::msync(m_begin, __size(), MS_SYNC);
        ::munmap(m_begin, __size());
        closed = true;
    }
    return NULL;
}

__ss_int mmap::flush(__ss_int offset, __ss_int size)
{
    __raise_if_closed();
    if (::msync(m_begin + offset, __subscript(size), MS_SYNC) == -1)
    {
        throw new OSError();
    }
    return 0;
}

// since darwin doesn't have mremap
#ifdef __APPLE__
#undef HAVE_MREMAP
#endif

void *mmap::resize(__ss_int new_size)
{
    __raise_if_closed();
#ifdef HAVE_MREMAP
#if defined(__NetBSD__)
    void *temp = ::mremap(m_begin, __size(),
                                    m_begin, size_t(new_size), 0);
#else // !__NetBSD__
    void *temp = ::mremap(m_begin, __size(),
                                    size_t(new_size), 0);
#endif // __NetBSD__
    if (temp == MAP_FAILED)
    {
        throw new OSError();
    }
    m_begin = static_cast<iterator>(temp);
    m_end = m_begin + size_t(new_size);
    m_position = std::min(m_position, m_end);
#else // !HAVE_MREMAP
    throw new NotImplementedError(const_15);
#endif // HAVE_MREMAP
    return NULL;
}
#else /* WIN32*/
void *mmap::__init__(int __ss_fileno_, __ss_int length_, str *tagname_, __ss_int access_, __ss_int offset_)
{
    if (length_ < 0)
    {
        throw new OverflowError(const_2);
    }
    if (offset_ < 0)
    {
        throw new OverflowError(const_3);
    }
    // Taken from Python 2.7
    DWORD flProtect, dwDesiredAccess;
    DWORD off_hi;   /* upper 32 bits of offset */
    DWORD off_lo;   /* lower 32 bits of offset */
    DWORD size_hi;  /* upper 32 bits of size */
    DWORD size_lo;  /* lower 32 bits of size */
    DWORD dwErr = 0;
    HANDLE fh = 0;
    size_t size = 0;
    const char *tagname = tagname_ ? tagname_->c_str() : 0;
    switch (access_)
    {
    case ACCESS_READ:
        flProtect = PAGE_READONLY;
        dwDesiredAccess = FILE_MAP_READ;
        break;
    case ACCESS_DEFAULT:
    case ACCESS_WRITE:
        flProtect = PAGE_READWRITE;
        dwDesiredAccess = FILE_MAP_WRITE;
        break;
    case ACCESS_COPY:
        flProtect = PAGE_WRITECOPY;
        dwDesiredAccess = FILE_MAP_COPY;
        break;
    default:
        throw new ValueError(const_5);
    }

    if (__ss_fileno_ != -1 and __ss_fileno_ != 0)
    {
        fh = HANDLE(_get_osfhandle(__ss_fileno_));
        if (fh == HANDLE(-1))
        {
            throw new ValueError(const_16);
        }
        /* Win9x appears to need us seeked to zero */
        lseek(__ss_fileno_, 0, SEEK_SET);
    }

    if (fh == 0)
    {
        size = length_;
    }
    else
    {
        /* It is necessary to duplicate the handle, so the
           Python code can close it on us */
        if (!DuplicateHandle(
                    GetCurrentProcess(), /* source process handle */
                    fh, /* handle to be duplicated */
                    GetCurrentProcess(), /* target proc handle */
                    (LPHANDLE)&file_handle, /* result */
                    0, /* access - ignored due to options value */
                    FALSE, /* inherited by child processes? */
                    DUPLICATE_SAME_ACCESS))   /* options */
        {
            throw new OSError();
        }
        if (length_)
        {
            size = length_;
        }
        else
        {
            DWORD low, high;
            low = GetFileSize(fh, &high);
            /* low might just happen to have the value INVALID_FILE_SIZE;
               so we need to check the last error also. */
            if (low == INVALID_FILE_SIZE and
                    (dwErr = GetLastError()) != NO_ERROR)
            {
                throw new ValueError(const_17);
            }
#if SIZEOF_SIZE_T > 4
            size = (size_t(high)<<32) + low;
#else // SIZEOF_SIZE_T <= 4
            if (high)
                /* File is too large to map completely */
                size = size_t(-1);
            else
                size = low;
#endif // SIZEOF_SIZE_T > 4
        }
    }

    access = access_;
    /* DWORD is a 4-byte int.  If we're on a box where size_t consumes
     * more than 4 bytes, we need to break it apart.  Else (size_t
     * consumes 4 bytes), C doesn't define what happens if we shift
     * right by 32, so we need different code.
     */
#if SIZEOF_SIZE_T > 4
    size_hi = (DWORD)((offset_ + size) >> 32);
    size_lo = (DWORD)((offset_ + size) & 0xFFFFFFFF);
    off_hi = (DWORD)(offset_ >> 32);
    off_lo = (DWORD)(offset_ & 0xFFFFFFFF);
#else // SIZEOF_SIZE_T <= 4
    size_hi = 0;
    size_lo = (DWORD)(offset_ + size);
    off_hi = 0;
    off_lo = (DWORD)offset_;
#endif // SIZEOF_SIZE_T > 4
    /* For files, it would be sufficient to pass 0 as size.
       For anonymous maps, we have to pass the size explicitly. */
    map_handle = CreateFileMapping(file_handle,
                                   NULL,
                                   flProtect,
                                   size_hi,
                                   size_lo,
                                   tagname);
    if (map_handle == NULL)
    {
        throw new OSError();
    }

    m_begin = static_cast<iterator>(MapViewOfFile(map_handle,
                                    dwDesiredAccess,
                                    off_hi,
                                    off_lo,
                                    size));
    if (m_begin == NULL)
    {
        throw new OSError();
    }
    /* set the initial position */
    m_position = m_begin;
    m_end = m_begin + size_lo;
    offset = offset_;

    return NULL;
}

void *mmap::close()
{
    if (not closed)
    {
        UnmapViewOfFile (m_begin);
        CloseHandle (map_handle);
        if (file_handle != INVALID_HANDLE_VALUE)
            CloseHandle (file_handle);
        closed = true;
    }
    return NULL;
}

__ss_int mmap::flush(__ss_int offset, __ss_int size)
{
    __raise_if_closed();
    return __ss_int(FlushViewOfFile(m_begin + offset, __subscript(size)));
}

void *mmap::resize(__ss_int new_size)
{
    __raise_if_closed();
    DWORD dwErrCode = 0;
    DWORD off_hi, off_lo;
    LONG newSizeLow, newSizeHigh;
    /* First, unmap the file view */
    UnmapViewOfFile(m_begin);
    m_begin = NULL;
    /* Close the mapping object */
    CloseHandle(map_handle);
    map_handle = NULL;
    /* Move to the desired EOF position */
#if SIZEOF_SIZE_T > 4
    newSizeHigh = (DWORD)((offset + new_size) >> 32);
    newSizeLow = (DWORD)((offset + new_size) & 0xFFFFFFFF);
    off_hi = (DWORD)(offset >> 32);
    off_lo = (DWORD)(offset & 0xFFFFFFFF);
#else // SIZEOF_SIZE_T <= 4
    newSizeHigh = 0;
    newSizeLow = (DWORD)(offset + new_size);
    off_hi = 0;
    off_lo = (DWORD)offset;
#endif // SIZEOF_SIZE_T > 4
    SetFilePointer(file_handle,
                   newSizeLow, &newSizeHigh, FILE_BEGIN);
    /* Change the size of the file */
    SetEndOfFile(file_handle);
    /* Create another mapping object and remap the file view */
    map_handle = CreateFileMapping(
                     file_handle,
                     NULL,
                     PAGE_READWRITE,
                     0,
                     0,
                     tagname);
    if (map_handle != NULL)
    {
        throw new OSError();
    }

    m_begin = static_cast<iterator>(MapViewOfFile(map_handle,
                                    FILE_MAP_WRITE,
                                    off_hi,
                                    off_lo,
                                    new_size));
    if (m_begin == NULL)
    {
        CloseHandle(map_handle);
        throw new OSError();
    }
    m_end = m_begin + size_t(new_size);
    m_position = std::min(m_position, m_end);
    return NULL;
}
#endif /* WIN32 */

void mmap::__enter__() { }

void mmap::__exit__()
{
    close();
}

__ss_int mmap::find(bytes *needle, __ss_int start, __ss_int end)
{
    __raise_if_closed_or_not_readable();
    if (start == -1)
    {
        start = __tell();
    }
    if( end == -1)
    {
        end = __size();
    }
    return __find(needle->unit, start, end);
}

void *mmap::move(__ss_int destination, __ss_int source, __ss_int count)
{
    __raise_if_closed_or_not_readable();
    __ss_int length = size();

    // Taken from Python 2.7
    if (count < 0 or (count + destination) < count or
            (count + source) < count or source < 0 or
            source > length or (source + count) > length or
            destination < 0 or destination > length or
            (destination + count) > length)
    {
        throw new ValueError(const_1);
    }
    memmove(m_begin + destination, m_begin + source, count);
    return NULL;
}

bytes *mmap::read(__ss_int size)
{
    __raise_if_closed_or_not_readable();
    const iterator at = m_position;
    if (size == all)
    {
        m_position = m_end;
    }
    else
    {
        m_position += size;
        if (m_position < at)
        {
            throw new OverflowError(const_14);
        }
        if (m_position >= m_end)
        {
            m_position = m_end;
        }
    }
    bytes *b = new bytes(at, m_position - at);
    b->frozen = 1;
    return b;
}

__ss_int mmap::read_byte()
{
    __raise_if_closed_or_not_readable();
    if(m_position < m_end)
    {
        return *m_position++;
    }
    else
    {
        m_position = m_end;
        return 0; // XXX ???
    }
}

bytes *mmap::readline(__ss_int size, const char eol)
{
    __raise_if_closed_or_not_readable();
    const iterator at = m_position;
    m_position = __next_line(eol);
    if (m_position == 0)
    {
        m_position = m_end;
    }
    else // Line found.
    {
        ++m_position; // Include the newline
    }
    if (size != all and
            m_position > at + size)
    {
        m_position = at + size;
    }
    return new bytes(at, m_position - at);
}

__ss_int mmap::rfind(bytes *needle, __ss_int start, __ss_int end)
{
    __raise_if_closed_or_not_readable();
    if (start == -1)
    {
        start = __tell();
    }
    if( end == -1)
    {
        end = __size();
    }
    return __find(needle->unit, start, end, true);
}

void *mmap::seek(__ss_int offset, __ss_int whence)
{
    __raise_if_closed();
    const iterator restore = m_begin + tell();
    switch (whence)
    {
    case 0: /* SEEK_SET: relative to start.*/
        if (offset < 0L or size_t(offset) > __size())
        {
            __seek_failed();
        }
        m_position = m_begin + offset;
        break;
    case 1:  /* SEEK_CUR: relative to current position. */
        m_position += offset;
        if (m_position < m_begin or
                m_position > m_end)
        {
            m_position = restore;
            __seek_failed();
        }
        break;
    case 2: /* SEEK_END: relative to end */
        if (offset > 0L or offset < -int(__size()))
        {
            __seek_failed();
        }
        m_position = m_end + offset;
        break;
    default: // Error
        throw new ValueError(const_12);
    }
    return NULL;
}

__ss_int mmap::size()
{
    __raise_if_closed();
#ifdef WIN32
    if (file_handle != INVALID_HANDLE_VALUE) 
    {
        DWORD low, high;
        uint64_t size;
        low = GetFileSize(file_handle, &high);
        if (low == INVALID_FILE_SIZE)
        {
            /* It might be that the function appears to have failed,
               when indeed its size equals INVALID_FILE_SIZE */
            DWORD error = GetLastError();
            if (error != NO_ERROR)
                throw OSError();
        }
        size = (((uint64_t)high)<<32) + low;
        return __ss_int(size);
    }
    else 
    {
        return __size();
    }
#else /* UNIX */
    if(fd == -1 )
    {
        return __size();
    }
    else
    {
        struct stat buf;
        if (fstat(fd, &buf) == -1)
        {
            throw new OSError();
        }
        return buf.st_size;
    }
#endif /* WIN32 */
}

__ss_int mmap::tell()
{
    __raise_if_closed();
    return __tell();
}

void *mmap::write(bytes *string)
{
    __raise_if_closed_or_not_writable();
    size_t length = string->size();
    if (m_position + length > m_end)
    {
        throw new ValueError(const_14);
    }
    memcpy(m_position, string->unit.data(), length);
    m_position += length;

    return NULL;
}

void *mmap::write_byte(__ss_int value)
{
    __raise_if_closed_or_not_writable();
    if (m_position + 1 > m_end)
    {
        throw new ValueError(const_14);
    }
    *m_position++ = value;
    return NULL;
}

__ss_bool mmap::__contains__(bytes *string)
{
    __raise_if_closed_or_not_readable();
    if (string == 0 or string->size() != 1)
    {
        throw new ValueError(const_8);
    }
    return __mbool(find(string, 0) != -1);
}

__iter<bytes *> *mmap::__iter__()
{
    __raise_if_closed();	
    return new __mmapiter(this);
}

__ss_int mmap::__len__()
{
    return size();
}

__ss_int mmap::__getitem__(__ss_int index)
{
    __raise_if_closed_or_not_readable();
    return m_begin[__subscript(index)];
}

void *mmap::__setitem__(__ss_int index, __ss_int character)
{
    __raise_if_closed_or_not_writable();
    size_t id = __subscript(index);
    m_begin[id] = character;
    return NULL;
}

bytes *mmap::__slice__(__ss_int kind, __ss_int lower, __ss_int upper, __ss_int)
{
    __raise_if_closed_or_not_readable();

    lower = __clamp(lower);
    upper = __clamp(upper);

    iterator start = m_begin;
    size_t size = 0;
    switch (kind)
    {
    case 1: // step[x:]
        start = m_begin + __subscript(lower);
        size = m_end - start;
        break;
    case 2: // step[:x]
        start = m_begin;
        size = __subscript(upper);
        break;
    case 3: // step[x:y]
        start = m_begin + __subscript(lower);
        size = __subscript(upper) - __subscript(lower);
        break;
    default:
        assert(false);
    }
    bytes *b = new bytes(start, size);
    b->frozen = 1;
    return b;
}

void *mmap::__setslice__(__ss_int kind, __ss_int lower, __ss_int upper, __ss_int, bytes *sequence)
{
    __raise_if_closed_or_not_writable();
    iterator start = m_end;
    iterator finish = m_end;
    switch (kind)
    {
    case 1: // step[x:]
        start = m_begin + __subscript(lower, true);
        finish= m_end;
        break;
    case 2: // step[:x]
        start = m_begin;
        finish= m_begin + __subscript(upper, true);
        break;
    case 3: // step[x:y]
        start = m_begin + __subscript(lower, true);
        finish= m_begin + __subscript(upper, true);
        break;
    default:
        assert(false);
    }

    memcpy(start, sequence->unit.data(), finish - start);
    return NULL;
}

void *mmap::__raise_if_closed()
{
    if (closed)
    {
        throw new ValueError(const_11);
    }
    return NULL;
}

void *mmap::__raise_if_closed_or_not_readable()
{
    __raise_if_closed();
#ifndef WIN32
    if ((prot & PROT_READ) == 0)
#else /* WIN32 */
    if (access and access != ACCESS_READ)
#endif /* WIN32 */
    {
        throw new TypeError(const_0);
    }
    return NULL;
}

void *mmap::__raise_if_closed_or_not_writable()
{
    __raise_if_closed();
#ifndef WIN32
    if ((prot & PROT_WRITE) == 0)
#else /* WIN32 */
    if (access == ACCESS_READ)
#endif /* WIN32 */
    {
        throw new TypeError(const_9);
    }
    return NULL;
}

void *mmap::__seek_failed()
{
    throw new ValueError(const_14);
    return NULL;
}

size_t mmap::__subscript(__ss_int index, bool include_end) const
{
    if (index < 0)
    {
        index += __size();
    }
    if (index < 0 or size_t(index) >= __size())
    {
        if (not include_end or size_t(index) != __size())
        {
            throw new IndexError(const_13);
        }
    }
    return index;
}

__ss_int mmap::__clamp(__ss_int index) const
{
    __ss_int length = __size();
    return std::min(std::max(index, -length), length);
}

mmap::iterator mmap::__next_line(const char eol)
{
    return static_cast<const iterator>(
               memchr(m_position, eol, m_end - m_position));
}

__ss_int mmap::__find(const __GC_STRING& needle, __ss_int start, __ss_int end, bool reverse)
{
    if (end == 0)
    {
        end = __size();
    }
    size_t length = needle.size();
    // Taken from Python 3.2.
    const char *p, *start_p, *end_p;
    int sign = reverse ? -1 : 1;

    if (start < 0)
        start += __size();
    if (start < 0)
        start = 0;
    else if (size_t(start) > __size())
        start = __size();

    if (end < 0)
        end += __size();
    if (end < 0)
        end = 0;
    else if (size_t(end) > __size())
        end = __size();

    start_p = m_begin + start;
    end_p = m_begin + end;

    for (p = (reverse ? end_p - length : start_p);
            (p >= start_p) and (p + length <= end_p); p += sign)
    {
        size_t i;
        for (i = 0; i < length and needle[i] == p[i]; ++i)
        {
            /* Nothing */;
        }

        if (i == length)
        {
            return (p - m_begin);
        }
    }
    return -1;
}

bytes *__mmapiter::__next__()
{
    if (map->__eof())
        throw new StopIteration();
    bytes* byte = new bytes(__char_cache[(unsigned char)(map->read_byte())]->unit);
    if (map->__eof())
        throw new StopIteration();
    return byte;
}

void __init()
{
    static bool __initialized = false;

    if(not __initialized)
    {
#ifdef WIN32
        SYSTEM_INFO si;
        GetSystemInfo(&si);
        ALLOCATIONGRANULARITY = si.dwAllocationGranularity;

        default_2 = new str("");
#endif /* WIN32 */
        const_0  = new str("mmap object is not open for reading");
        const_1  = new str("source, destination, or count out of range");
        const_2  = new str("memory mapped size must be positive");
        const_3  = new str("memory mapped offset must be positive");
        const_4  = new str("mmap can't specify both access and flags, prot");
        const_5  = new str("mmap invalid access parameter");
        const_8  = new str("mmap assignment must be single-character string");
        const_9  = new str("mmap object is not open for writing");
        const_10 = new str("mmap slice assignment is wrong size");
        const_11 = new str("mmap closed or invalid");
        const_12 = new str("unknown seek type");
        const_13 = new str("mmap index out of range");
        const_14 = new str("data out of range");
        const_15 = new str("mmap: resizing not available--no mremap()");
        const_16 = new str("mmap invalid file handle");
        const_17 = new str("mmap invalid file size");

        __name__ = new str("mmap");

        cl_mmap = new class_("mmap");

        __initialized = true;
    }
} // __init

} // __mmap__ namespace
