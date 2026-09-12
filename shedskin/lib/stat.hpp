/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __STAT_HPP
#define __STAT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __stat__ {

extern __ss_int __ss_S_IWRITE;
extern __ss_int __ss_ST_MTIME;
extern __ss_int __ss_S_IFLNK;
extern __ss_int __ss_ST_INO;
extern __ss_int __ss_S_IXOTH;
extern __ss_int __ss_ST_UID;
extern __ss_int __ss_S_IRGRP;
extern __ss_int __ss_S_IXUSR;
extern __ss_int __ss_S_IRUSR;
extern __ss_int __ss_ST_NLINK;
extern __ss_int __ss_S_IFBLK;
extern __ss_int __ss_S_IFDIR;
extern __ss_int __ss_ST_ATIME;
extern __ss_int __ss_S_ISUID;
extern __ss_int __ss_S_IRWXU;
extern __ss_int __ss_S_IFCHR;
extern __ss_int __ss_S_ISGID;
extern __ss_int __ss_S_IFREG;
extern __ss_int __ss_S_IREAD;
extern __ss_int __ss_S_IFIFO;
extern __ss_int __ss_S_IFSOCK;
extern __ss_int __ss_S_ISVTX;
extern __ss_int __ss_ST_MODE;
extern __ss_int __ss_S_ENFMT;
extern __ss_int __ss_S_IEXEC;
extern __ss_int __ss_ST_CTIME;
extern __ss_int __ss_S_IWOTH;
extern __ss_int __ss_S_IXGRP;
extern __ss_int __ss_S_IRWXG;
extern __ss_int __ss_S_IWUSR;
extern __ss_int __ss_ST_GID;
extern __ss_int __ss_S_IROTH;
extern __ss_int __ss_S_IWGRP;
extern __ss_int __ss_S_IRWXO;
extern __ss_int __ss_ST_DEV;
extern __ss_int __ss_ST_SIZE;

/* file types that only some platforms model (doors/event ports on
   solaris, whiteouts on bsd/macos), the BSD-style file flags used by
   os.chflags() and stat_result.st_flags, the windows
   st_file_attributes bits and the linux statx attribute bits. cpython
   exposes all of these from the stat module on every platform, falling
   back to fixed values where the system doesn't define them, so they
   are unconditionally available here too (see stat.cpp). */
extern __ss_int __ss_S_IFDOOR;
extern __ss_int __ss_S_IFPORT;
extern __ss_int __ss_S_IFWHT;
extern __ss_int __ss_UF_SETTABLE;
extern __ss_int __ss_UF_NODUMP;
extern __ss_int __ss_UF_IMMUTABLE;
extern __ss_int __ss_UF_APPEND;
extern __ss_int __ss_UF_OPAQUE;
extern __ss_int __ss_UF_NOUNLINK;
extern __ss_int __ss_UF_COMPRESSED;
extern __ss_int __ss_UF_TRACKED;
extern __ss_int __ss_UF_DATAVAULT;
extern __ss_int __ss_UF_HIDDEN;
extern __ss_int __ss_SF_SETTABLE;
extern __ss_int __ss_SF_ARCHIVED;
extern __ss_int __ss_SF_IMMUTABLE;
extern __ss_int __ss_SF_APPEND;
extern __ss_int __ss_SF_RESTRICTED;
extern __ss_int __ss_SF_NOUNLINK;
extern __ss_int __ss_SF_SNAPSHOT;
extern __ss_int __ss_SF_FIRMLINK;
extern __ss_int __ss_SF_DATALESS;
extern __ss_int __ss_FILE_ATTRIBUTE_ARCHIVE;
extern __ss_int __ss_FILE_ATTRIBUTE_COMPRESSED;
extern __ss_int __ss_FILE_ATTRIBUTE_DEVICE;
extern __ss_int __ss_FILE_ATTRIBUTE_DIRECTORY;
extern __ss_int __ss_FILE_ATTRIBUTE_ENCRYPTED;
extern __ss_int __ss_FILE_ATTRIBUTE_HIDDEN;
extern __ss_int __ss_FILE_ATTRIBUTE_INTEGRITY_STREAM;
extern __ss_int __ss_FILE_ATTRIBUTE_NORMAL;
extern __ss_int __ss_FILE_ATTRIBUTE_NOT_CONTENT_INDEXED;
extern __ss_int __ss_FILE_ATTRIBUTE_NO_SCRUB_DATA;
extern __ss_int __ss_FILE_ATTRIBUTE_OFFLINE;
extern __ss_int __ss_FILE_ATTRIBUTE_READONLY;
extern __ss_int __ss_FILE_ATTRIBUTE_REPARSE_POINT;
extern __ss_int __ss_FILE_ATTRIBUTE_SPARSE_FILE;
extern __ss_int __ss_FILE_ATTRIBUTE_SYSTEM;
extern __ss_int __ss_FILE_ATTRIBUTE_TEMPORARY;
extern __ss_int __ss_FILE_ATTRIBUTE_VIRTUAL;
extern __ss_int __ss_STATX_ATTR_COMPRESSED;
extern __ss_int __ss_STATX_ATTR_IMMUTABLE;
extern __ss_int __ss_STATX_ATTR_APPEND;
extern __ss_int __ss_STATX_ATTR_NODUMP;
extern __ss_int __ss_STATX_ATTR_ENCRYPTED;
extern __ss_int __ss_STATX_ATTR_AUTOMOUNT;
extern __ss_int __ss_STATX_ATTR_MOUNT_ROOT;
extern __ss_int __ss_STATX_ATTR_VERITY;
extern __ss_int __ss_STATX_ATTR_DAX;
extern __ss_int __ss_STATX_ATTR_WRITE_ATOMIC;

__ss_bool __ss_S_ISDIR(__ss_int mode);
__ss_bool __ss_S_ISREG(__ss_int mode);

str *filemode(__ss_int mode);

/* S_IMODE/S_IFMT/S_ISCHR/S_ISBLK/S_ISFIFO/S_ISLNK/S_ISSOCK use only
   literal bitmask constants (see stat.cpp), so they have no
   dependency on the POSIX S_IS.. / S_IF.. macros that MSVC's
   <sys/stat.h> lacks, and are available on every platform. */
__ss_int __ss_S_IMODE(__ss_int mode);
__ss_int __ss_S_IFMT(__ss_int mode);
__ss_bool __ss_S_ISCHR(__ss_int mode);
__ss_bool __ss_S_ISBLK(__ss_int mode);
__ss_bool __ss_S_ISFIFO(__ss_int mode);
__ss_bool __ss_S_ISLNK(__ss_int mode);
__ss_bool __ss_S_ISSOCK(__ss_int mode);
__ss_bool __ss_S_ISDOOR(__ss_int mode);
__ss_bool __ss_S_ISPORT(__ss_int mode);
__ss_bool __ss_S_ISWHT(__ss_int mode);

void __init();

} // module namespace
#endif
