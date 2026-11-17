/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

#define __SS_MIN(a,b) ((a) < (b) ? (a) : (b))

/* iteration macros */

#define FAST_FOR(i, l, u, s, t1, t2) \
    if(s==0) \
        __throw_range_step_zero(); \
    for(__ ## t1 = l, __ ## t2 = u; ; __ ## t1 = __ss_range_next(__ ## t1, __ ## t2, s)) { \
        if (s >= 0) { if (__ ## t1 >= __ ## t2) break; } \
        else { if (__ ## t1 <= __ ## t2) break; } \
        i=__ ## t1; \

/* convert an element of another container (or iterable) to the element type
   of a container it is copied to, as in 'floats.extend(ints)'.

   elements of type 'void *' come from a container without an element type:
   nothing is ever added to it, or only None. they can be used as any pointer
   type, and do not occur where numbers are expected */

/* whether a value of type E can be used as a T without converting it, because
   it has the same representation: an instance of a subclass as one of a base
   class, and containers of those (at any depth), as in 'list<B *> *' for
   'list<A *> *' (but not 'list<int> *' for 'list<double> *') */

template<class E, class T> struct __ss_upcastable {
    static constexpr bool value = std::is_same_v<E, T> || (
        std::is_pointer_v<E> && std::is_pointer_v<T> &&
        std::is_class_v<std::remove_pointer_t<T>> &&
        std::is_base_of_v<std::remove_pointer_t<T>, std::remove_pointer_t<E>>);
};

template<class Es, class Ts> struct __ss_upcastable_args : std::false_type {};
template<class... Es, class... Ts> struct __ss_upcastable_args<std::tuple<Es...>, std::tuple<Ts...>> {
    static constexpr bool value = (__ss_upcastable<Es, Ts>::value && ...);
};

template<template<class...> class C, class... Es, class... Ts> struct __ss_upcastable<C<Es...> *, C<Ts...> *> {
    static constexpr bool value = std::is_same_v<C<Es...>, C<Ts...>> || [] {
        if constexpr (sizeof...(Es) == sizeof...(Ts))
            return __ss_upcastable_args<std::tuple<Es...>, std::tuple<Ts...>>::value;
        else
            return false;
    }();
};

template<class E, class T> inline constexpr bool __ss_upcastable_v = __ss_upcastable<E, T>::value;

/* elements of type E can be consumed as T without losing anything: the same type,
   none at all (an empty container), an instance of a subclass, or a widened number.
   used to reject e.g. floats into a set of ints, which would silently truncate */
template<class E, class T> inline constexpr bool __ss_widens_v =
    std::is_same_v<E, T> || std::is_same_v<E, void *> || __ss_upcastable_v<E, T> ||
    ((std::is_integral_v<E> || std::is_same_v<E, __ss_bool>) && std::is_floating_point_v<T>) ||
    (std::is_same_v<E, __ss_bool> && std::is_integral_v<T>);

/* the wider of two element types, which can hold the elements of both (e.g. floats for ints
   and floats), and whether there is one */
template<class A, class B> using __ss_wider_t = std::conditional_t<__ss_widens_v<A, B>, B, A>;
template<class A, class B> inline constexpr bool __ss_compatible_v = __ss_widens_v<A, B> || __ss_widens_v<B, A>;

/* the widest of any number of element types (e.g. for chain([1], [0.5])) */
template<class T, class ... Ts> struct __ss_widest { using type = T; };
template<class T, class U, class ... Ts> struct __ss_widest<T, U, Ts...> {
    using type = typename __ss_widest<__ss_wider_t<T, U>, Ts...>::type;
};
template<class ... Ts> using __ss_widest_t = typename __ss_widest<Ts...>::type;

/* a container as one with other element types (e.g. a list of ints as a list of floats):
   a converted copy, so only for reading (comparing, looking up, copying from) */
template<class W, class C> inline W *__ss_as(C *c) {
    if constexpr (std::is_same_v<W, C>)
        return c;
    else
        return c ? new W(c) : NULL;
}

/* a container looked up among containers with other element types (as in '(1, 2) in
   [(1.0, 2.0)]'): a converted copy. not the other way around, which would truncate */
template<class T, class U> inline T __ss_key(U a) {
    using TC = std::remove_pointer_t<T>;
    using UC = std::remove_pointer_t<U>;
    static_assert(__ss_widens_v<std::remove_cvref_t<typename UC::for_in_unit>, std::remove_cvref_t<typename TC::for_in_unit>>,
        "lookup: the elements of the key do not fit (e.g. a tuple of floats among tuples of ints)");
    return __ss_as<TC>(a);
}

template<class T, class E> inline T __ss_elem(E e) {
    if constexpr (std::is_same_v<E, void *> && !std::is_same_v<T, void *>) {
        if constexpr (std::is_pointer_v<T>)
            return (T)e;
        else
            return T();
    } else if constexpr (!std::is_convertible_v<E, T> && __ss_upcastable_v<E, T>)
        return reinterpret_cast<T>(e);
    else
        return e;
}

#define FOR_IN(e, iter, temp, i, t) \
    __ ## temp = iter; \
    (void)__ ## i; \
    __ ## t = __ ## temp->for_in_init(); \
    for(__ ## i = 0; __ ## temp->for_in_has_next(__ ## t); __ ## i ++) \
    { \
        e = __ss_elem<std::remove_cvref_t<decltype(e)>>(__ ## temp->for_in_next(__ ## t));

#define FOR_IN_ZIP(a, b, k, l, t, u, n, m) \
    __ ## t = k; \
    __ ## u = l; \
    __ ## m = __SS_MIN((__ ## t)->units.size(), (__ ## u)->units.size()); \
    for(__ ## n = 0; __ ## n < __ ## m; __ ## n ++) { \
        a = (__ ## t)->units[__ ## n]; \
        b = (__ ## u)->units[__ ## n];

#define FOR_IN_ENUMERATE(i, m, temp, n) \
    __ ## temp = m; \
    for(__ ## n = 0; (unsigned int)__ ## n < (__ ## temp)->units.size(); __ ## n ++) { \
        i = (__ ## temp)->units[__ ## n]; \

#define FOR_IN_ENUMERATE_STR(i, m, temp, n) \
    __ ## temp = m; \
    for(__ ## n = 0; (unsigned int)__ ## n < (__ ## temp)->unit.size(); __ ## n ++) { \
        i = (__ ## temp)->__getfast__(__ ## n); \

#define FOR_IN_DICT(m, temp, iter, pos) \
    __ ## temp = m; \
    __ ## iter = (__ ## temp)->gcd.begin(); \
    while (__ ## iter != (__ ## temp)->gcd.end() ) { \

#define FOR_IN_FILE(l, f, temp) \
    __ ## temp = f; \
    while (! __ ## temp->__eof()) { \
        l = __ ## temp->readline(); \
        if (__ ## temp->__eof() and len(l) == 0) \
            break;

#define END_FOR }

