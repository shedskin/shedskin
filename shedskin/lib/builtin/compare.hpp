
/* comparison */

template<class T> struct dereference {};
template<class T> struct dereference <T*> {
    typedef T type;
};

/* 
template<typename T, typename Sig>
struct has_cmp {
    template <typename U, U> struct type_check;
    template <typename V> static char (& chk(type_check<Sig, &V::__cmp__>*))[1];
    template <typename  > static char (& chk(...))[2];
    static bool const value = (sizeof(chk<T>(0)) == 1);
};

template<typename T, typename Sig>
struct has_eq {
    template <typename U, U> struct type_check;
    template <typename V> static char (& chk(type_check<Sig, &V::__eq__>*))[1];
    template <typename  > static char (& chk(...))[2];
    static bool const value = (sizeof(chk<T>(0)) == 1);
};

template<class T> inline __ss_int __cmp(T a, T b) {
    typedef typename dereference<T>::type T2;
    if (!a) return -1;
    if (has_cmp<T2, int (T2::*)(T)>::value)
        return a->__cmp__(b);
    else {
        if (has_eq<T2, __ss_bool (T2::*)(T)>::value and a->__eq__(b))
            return 0;
        if(a->__lt__(b))
            return -1;
        else
            return 1;
    }
    return 0;
}
*/

template<class T> inline __ss_int __cmp(T a, T b) {
    if (!a) return -1;
    return a->__cmp__(b);
}

#ifdef __SS_LONG
template<> inline __ss_int __cmp(__ss_int a, __ss_int b) {
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
}
#endif

template<> inline __ss_int __cmp(int a, int b) {
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
}

template<> inline __ss_int __cmp(__ss_bool a, __ss_bool b) {
    return __cmp(a.value, b.value); /* XXX */
}

template<> inline __ss_int __cmp(double a, double b) {
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
}
template<> inline __ss_int __cmp(void *a, void *b) {
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
}

template<class T> __ss_int cpp_cmp(T a, T b) {
    return __cmp(a, b) == -1;
}
template<class T> __ss_int cpp_cmp_rev(T a, T b) {
    return __cmp(a, b) == 1;
}
template<class T> class cpp_cmp_custom {
    typedef __ss_int (*hork)(T, T);
    hork cmp;
public:
    cpp_cmp_custom(hork a) { cmp = a; }
    __ss_int operator()(T a, T b) const { return cmp(a,b) == -1; }
};
template<class T> class cpp_cmp_custom_rev {
    typedef __ss_int (*hork)(T, T);
    hork cmp;
public:
    cpp_cmp_custom_rev(hork a) { cmp = a; }
    __ss_int operator()(T a, T b) const { return cmp(a,b) == 1; }
};
template<class T, class V> class cpp_cmp_key {
    typedef V (*hork)(T);
    hork key;
public:
    cpp_cmp_key(hork a) { key = a; }
    __ss_int operator()(T a, T b) const { return __cmp(key(a), key(b)) == -1; }
};
template<class T, class V> class cpp_cmp_key_rev {
    typedef V (*hork)(T);
    hork key;
public:
    cpp_cmp_key_rev(hork a) { key = a; }
    __ss_int operator()(T a, T b) const { return __cmp(key(a), key(b)) == 1; }
};
