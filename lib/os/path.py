# copied from pypy:
# https://codespeak.net/viewvc/pypy/dist/lib-python/2.4.1/posixpath.py?revision=16842&view=markup

import os, stat

def split(p):
    return ('','')

#    """Split a pathname.  Returns tuple "(head, tail)" where "tail" is
#    everything after the final slash.  Either part may be empty."""
#    i = p.rfind('/') + 1
#    head, tail = p[:i], p[i:]
#    if head and head != '/'*len(head):
#        head = head.rstrip('/')
#    return head, tail

def splitext(p):
    return ('','')

#    """Split the extension from a pathname.  Extension is everything from the
#    last dot to the end.  Returns "(root, ext)", either part may be empty."""
#    i = p.rfind('.')
#    if i<=p.rfind('/'):
#        return p, ''
#    else:
#        return p[:i], p[i:]

def isdir(path):
    return False

#    """Test whether a path is a directory"""
#    try:
#        st = os.stat(path)
#    except OSError: #os.error:
#        return False
#    return stat.S_ISDIR(st.st_mode)

def exists(path):
    return False

#    """Test whether a path exists.  Returns False for broken symbolic links"""
#    try:
#        st = os.stat(path)
#    except OSError: #os.error:
#        return False
#    return True

def islink(path):
    return False

#    """Test whether a path is a symbolic link"""
#    try:
#        st = os.lstat(path)
#    except OSError: #(os.error, AttributeError):
#        return False
#    return stat.S_ISLNK(st.st_mode)

def isfile(path):
    return False

#    """Test whether a path is a regular file"""
#    try:
#        st = os.stat(path)
#    except OSError: #os.error:
#        return False
#    return stat.S_ISREG(st.st_mode)

