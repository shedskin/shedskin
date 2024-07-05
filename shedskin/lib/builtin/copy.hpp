/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef SS_COPY_HPP
#define SS_COPY_HPP

template<class T> T __copy(T t) {
    if(!t)
        return (T)NULL;
    return (T)(t->__copy__());
}

#ifdef __SS_LONG
template<> inline __ss_int __copy(__ss_int i) { return i; }
#endif
template<> inline int __copy(int i) { return i; }
template<> inline __ss_bool __copy(__ss_bool b) { return b; }
template<> inline __ss_float __copy(__ss_float d) { return d; }
template<> inline void *__copy(void *p) { return p; }

template<class T> T __deepcopy(T t, dict<void *, pyobj *> *memo=0) {
    if(!t)
        return (T)NULL;

    if(!memo)
        memo = new dict<void *, pyobj *>();
    T u = (T)(memo->get(t, 0));
    if(u)
       return u;

    return (T)(t->__deepcopy__(memo));
}

#ifdef __SS_LONG
template<> inline __ss_int __deepcopy(__ss_int i, dict<void *, pyobj *> *) { return i; }
#endif
template<> inline int __deepcopy(int i, dict<void *, pyobj *> *) { return i; }
template<> inline __ss_bool __deepcopy(__ss_bool b, dict<void *, pyobj *> *) { return b; }
template<> inline __ss_float __deepcopy(__ss_float d, dict<void *, pyobj *> *) { return d; }
template<> inline void *__deepcopy(void *p, dict<void *, pyobj *> *) { return p; }

#endif
