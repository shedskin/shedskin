/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __GLOB_HPP
#define __GLOB_HPP

#include "builtin.hpp"
#include "os/path.hpp"
#include "fnmatch.hpp"
#include "re.hpp"
#include "os/__init__.hpp"

using namespace __shedskin__;
namespace __glob__ {

extern str *const_0, *const_2, *const_3, *const_4, *const_5, *const_6;

extern str *__name__;
extern __re__::Pattern *magic_check;
extern __re__::Pattern *magic_check_escape;

/* dir_fd: CPython's `dir_fd=None` arrives here as the default -1 (argument
   omitted) or as 0 (the compiler emits NULL for a literal None); neither is
   a plausible directory descriptor, so both mean "no dir_fd". Positive values
   are file descriptors of directories that relative paths (pattern and
   root_dir alike) are resolved against, as with the *at() system calls. Only
   supported on POSIX: like CPython, using it on Windows raises
   NotImplementedError. */
list<str *> *glob(str *pathname, __ss_bool recursive=False, __ss_bool include_hidden=False, str *root_dir=0, __ss_int dir_fd=-1);
__iter<str *> *iglob(str *pathname, __ss_bool recursive=False, __ss_bool include_hidden=False, str *root_dir=0, __ss_int dir_fd=-1);
__iter<str *> *_iglob(str *pathname, str *root_dir, __ss_int dir_fd, __ss_bool recursive, __ss_bool dironly, __ss_bool include_hidden);
__iter<str *> *_skip_empty(__iter<str *> *it);
list<str *> *_glob1(str *dirname, str *pattern, __ss_int dir_fd, __ss_bool dironly, __ss_bool include_hidden);
list<str *> *_glob0(str *dirname, str *basename, __ss_int dir_fd, __ss_bool dironly, __ss_bool include_hidden);
__iter<str *> *_glob2(str *dirname, str *pattern, __ss_int dir_fd, __ss_bool dironly, __ss_bool include_hidden);
list<str *> *_listdir(str *dirname, __ss_int dir_fd, __ss_bool dironly);
__iter<str *> *_rlistdir(str *dirname, __ss_int dir_fd, __ss_bool dironly, __ss_bool include_hidden);
__ss_bool _lexists(str *pathname, __ss_int dir_fd);
__ss_bool _isdir(str *pathname, __ss_int dir_fd);
__ss_bool _ishidden(str *path);
__ss_bool _isrecursive(str *pattern);
str *_join(str *dirname, str *basename);
__ss_bool has_magic(str *s);
str *escape(str *pathname);
str *translate(str *pat, __ss_bool recursive=False, __ss_bool include_hidden=False, str *seps=0);

void __init(void);

} // module namespace
#endif
